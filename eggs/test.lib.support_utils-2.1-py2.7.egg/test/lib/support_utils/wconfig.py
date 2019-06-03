#!/usr/bin/env python

'''
wconfig.py - config parser

'''

import os
import sys
import yaml
from ConfigParser import SafeConfigParser
from collections import OrderedDict
from patterns import Singleton

BUILDOUT_EGGS_DIR = '/eggs/'


class ConfigFactory(Singleton):
    '''
    Multiton Config Factory
    '''
    
    pool = OrderedDict()
    
    def __init__(self):
        pass
        
    def init_config(self, name, dir_path = None):
        '''
        Initializes or returns a config file by instantiating 
        a Config object.
        
        @var name: configuration file name like blah.ini
        @type name: string
        @var dir_path: folder location of config file if not
                       specified it tries to find buildout
                       etc dir.
        @type dir_path: string
          
        @return: Config instance
        @rtype: Config  
        '''
        
        file_path =  os.path.join(dir_path, name) if dir_path else \
                    os.path.join(self.get_buildout_path(), 'etc', name)
        if name not in self.pool:
            self.pool[name] = Config(file_path)
        return self.pool[name]
    
    def get_config(self, name = None):
        ''' 
        Returns an instantiated named config or returns the first
        in the list as the default. If not initialized
        return None.
        
        @var name: configuration file name
        @type name: string
        @return: Config instance
        @rtype: Config 
        '''
        
        if name in self.pool:
            return self.pool[name]
        elif name is None and self.pool:
            return self.pool.itervalues().next()
        else:
            # We don't raise exceptions to tests don't complain
            return None
        
    def get_buildout_path(self):
        '''
        @return: buildout directory
        @rtype: string
        ''' 
        for path in sys.path:
            if BUILDOUT_EGGS_DIR in path:
                return path.split(BUILDOUT_EGGS_DIR)[0]
        return None
    

class Config(object):
    '''
    Simple wrapper around ConfigParser, if no file path
    is given, it tries to find the buildout folder and use
    that.
    '''

    def __init__(self, file_path):
        self.file_path =  file_path
                    
        if not os.access(self.file_path, os.R_OK):     # W_OK is for writing, R_OK
            raise IOError("File %s can't be accessed or not readable." % self.file_path)
        if self.file_path.endswith('.yml') or self.file_path.endswith('.yaml'):
            self.type = 'yaml'
            self.parser = None
            with open(file_path) as fh:
                self.config_dict = yaml.load(fh)
        else:
            self.type = 'ini'
            self.parser = SafeConfigParser()
            self.parser.read(self.file_path)

    def __repr__(self):
        return "Config<type: %s file_path: %s>" % (self.type, self.file_path)
        
    def get_conf_file(self):
        return self.file_path
    
    def get_parser(self):
        return self.parser






