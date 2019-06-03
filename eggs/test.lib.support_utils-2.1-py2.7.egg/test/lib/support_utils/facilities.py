#!/usr/bin/env python

'''
facilities.py - Bunch of facility functions to make simple
setup and usage of underlying functions easier for most of
the ordinary usages. Developers may call underlying 
functions directly if they intend to have more flexibility
rather than convenience.

The standard extensions are .cfg for config files and .log
for log files.

'''
from wconfig import ConfigFactory
from wlogging import LogFactory

def setup_app(app_name):
    '''
    This is a general purpose factory
    to configure an application. It loads up the configuration files
    and then setup logging.
    @return: ConfigFactory object loaded with configs
    '''
    cf = ConfigFactory()
    # Check if we already have set it up
    if app_name in cf.pool and app_name + '-logging.yaml' in cf.pool:
        return cf
    # Not there so we need to set it up
    else:
        get_config(app_name)
        cfg = cf.init_config(app_name + '-logging.yaml')
        lf = LogFactory()
        lf.init_loggers(cfg)
        return cf

def get_config(conf_name):
    '''
    returns a Config instance
    '''
    cf = ConfigFactory()
    if conf_name.endswith('.ini'):
        return cf.init_config(conf_name)
    elif conf_name.endswith('.yaml'):
        return cf.init_config(conf_name)
    else:
        return cf.init_config(conf_name + '.yaml')

def get_default_config():
    '''
    Returns the first config file in the factory if it exist
    otherwise it returns None
    '''
    cf = ConfigFactory()
    return cf.get_config()

def get_buildout_path():
    '''
    returns the best guess buildout path
    '''
    cf = ConfigFactory()
    return cf.get_buildout_path()
