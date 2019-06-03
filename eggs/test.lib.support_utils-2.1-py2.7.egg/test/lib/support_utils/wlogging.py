#!/usr/bin/env python

'''
wlogging.py - logging facility
'''

from test.lib.support_utils.patterns import Singleton

import logging
import logging.handlers
import logging.config
import os
import sys
import signal

# Defaults
LOG_LEVEL = 'logging.INFO'
LOG_DIR = 'var/log'
LOG_MAXBYTE = 500000
LOG_BACKUP_COUNT = 20
LOG_FORMAT = 'DLOGGER: %(asctime)s %(levelname)-5.5s ' \
                    '[%(name)s][%(threadName)s][PID:%(process)d] %(message)s'

LOGGING_DEFAULTS= \
{
    'version': 1,              
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': LOG_FORMAT
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'level' : 'INFO',    
            'class' : 'logging.handlers.RotatingFileHandler',
            'filename' : os.path.join(LOG_DIR,'default.log'),
            'mode': 'a',
            'formatter' : 'standard',
            'maxBytes' : LOG_MAXBYTE,
            'backupCount' : LOG_BACKUP_COUNT
        },  
    },
    'loggers': {
        '': {                  
            'handlers': ['console', 'file',],        
            'level': 'INFO',  
            'propagate': True  
        },
    }
}
## Defaults ends

class LogFactory(Singleton):

    def init_loggers(self, configObj=None, defaults=LOGGING_DEFAULTS, 
                                            disable_existing_loggers=True):
        """
        Set up logging via the logging module's by using ``ConfigObj`` from 
        wconfig as input. ``defaults`` and ``disable_existing_loggers`` are passed
        straight to logging.config.fileConfig.
        """
        if configObj and configObj.type != 'yaml':
            raise Exception("Log factory only accepts config objects of type yaml.")
        else:
            self.configObj = configObj

        if self.configObj:
            return logging.config.dictConfig(self.configObj.config_dict)
        else:
            return logging.config.dictConfig(defaults)


class BufferingSMTPHandler(logging.handlers.SMTPHandler):
    """
BufferingSMTPHandler works like SMTPHandler log handler except that it
buffers log messages for the ``interval``(secs) or until buffer size reaches
or exceeds the specified capacity at which point it will then send everything
that was buffered up until that point in one email message. Alternatively, if 
any log record messages ends with '##', it will trigger the flush. Everytime
the buffer is flushed the timer for the ``interval`` is reset.
Contrast this with SMTPHandler which sends one email per log message received.
"""
    
    def __init__(self, mailhost, fromaddr, toaddrs, subject, credentials=None,
                 secure=None, interval= 300, capacity=1024):
        logging.handlers.SMTPHandler.__init__(self, mailhost, fromaddr,
                                              toaddrs, subject,
                                              credentials, secure)
        
        self.capacity = capacity
        self.interval = interval
        self.buffer = []
        self._timeout = 1
        if credentials is None:
            self.username = None
            self.password = None
        if secure is None:
            self.secure = None
        if self.interval > 0:
            self.clock()

    def emit(self, record):
        try:
            try:
                self.acquire()
                self.buffer.append(record)
            finally:
                self.release()
            if self.shouldFlush(record):
                self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
            
    def shouldFlush(self, record):
        """
        Should the handler flush its buffer?

        Returns true if the buffer is up to capacity or the record ends with
        double hashes ('##').
        """
        return (len(self.buffer) >= self.capacity) or record.msg.endswith('##')
    
    def signalHandler(self, signum, frame):
        # By passing shouldFlush if interval is passed
        self.flush()
        
    def clock(self):
        """ 
        Keep track of time
        """
        signal.signal(signal.SIGALRM, self.signalHandler)
        signal.alarm(self.interval)

    def sendmail(self, host, port, msg, fromaddr, toaddrs, timeout, username=None, 
                                                password=None, secure = None):
        # Don't remove this!
        import smtplib
        smtp= smtplib.SMTP(host, port, timeout)
        if username:
            if secure is not None:
                smtp.ehlo()
                smtp.starttls(*secure)
                smtp.ehlo()
            smtp.login(username, password)
        smtp.sendmail(fromaddr, toaddrs, msg)
        smtp.quit()
        
    def flush(self):
        # Resetting timer
        import signal
        signal.alarm(self.interval)
        # buffer on termination may be empty if capacity is an exact multiple of
        # lines that were logged--thus we need to check for empty buffer
        if not self.buffer:
            return

        try:
            from email.utils import formatdate
            from smtplib import SMTP_PORT
            port = self.mailport
            if not port:
                port = SMTP_PORT
            msg = ""
            for record in self.buffer:
                msg = msg + self.format(record) + "\r\n"
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                            self.fromaddr,
                            ",".join(self.toaddrs),
                            self.getSubject(self.buffer[0]),
                            formatdate(), msg)
            # Sending email here
            self.sendmail(self.mailhost, port, msg, self.fromaddr, self.toaddrs, \
                            self._timeout, self.username, self.password, self.secure)
            self.acquire()
            try:
                self.buffer = []
            finally:
                self.release()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(self.buffer[0])
            
    def close(self):
        """
        Close the handler.

        This version just flushes and chains to the parent class' close().
        """
        import logging
        self.flush()
        logging.handlers.SMTPHandler.close(self)


class TagFilter(object):
    """
    Standard log filter that filters messages based on their tags
    ``tag``s look like "[1,system]" (an array in a string format with comma
    seperated tags). The filter will pass the record if ANY of the tags
    listed found at the begging of the message. Thus "[system] Kernel fault."
    as log massage will pass through the example filter.
    ``name`` is standard logger name and will additionaly filter based on that
    if provided.
    """

    def __init__(self, tag, name=''):
        """
        Initialize a filter.

        Initialize with the name of the logger which, together with its
        children, will have its events allowed through the filter. If no
        name is specified, allow every event.
        """
        self.name = name
        self.nlen = len(name)
        self.tag = tag
    
    def filter(self, record):
        """
        Determine if the specified record is to be logged.

        Each record MUST start with a tag like [tag1,tag2,...]
        if any of the tags in the filter matches them the log will
        be accepted by the filter.

        """
        f_accept = True
        if self.nlen == 0:
            f_accept = f_accept and True
        elif self.name == record.name:
            f_accept = f_accept and True
        elif record.name.find(self.name, 0, self.nlen) != 0:
            f_accept = f_accept and False
        elif  (record.name[self.nlen] == "."):
            f_accept = f_accept and True
        else:
            f_accept = f_accept and False
        # We check if any of the tags are found in the tag section of the
        # LogRecord.msg
        try:
            if record.msg.startswith('['):
                record_tags = record.msg[1:record.msg.find(']')].strip().split(',')
                filter_tags = str(self.tag).strip()[1:-1].split(',')
                if any([y for y in filter_tags if y in record_tags]):
                    f_accept = f_accept and True
                else:
                    f_accept = f_accept and False
            else:
                f_accept = f_accept and False
        except Exception as e:
            print str(e)
            f_accept = False

        return f_accept



def test():
    MAILHOST = '127.0.0.1'
    FROM = 'Whomever'
    TO = 'Whomever'
    SUBJECT = 'TEST'
    logger = logging.getLogger("")
    logger.setLevel(logging.DEBUG)
    logger.addFilter(TagFilter("[2,avid]"))
    logger.addHandler(BufferingSMTPHandler(MAILHOST, FROM, TO, SUBJECT, interval=30, capacity=10 ))
    logger.addHandler(logging.StreamHandler(sys.stderr))
    for i in xrange(2):
       logger.info("Info index = %d", i)
    logger.info("hello")
    logging.shutdown()

if __name__=='__main__':
    test()      
