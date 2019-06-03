#!/usr/bin/env python

'''
patterns.py - A collection of usable design patters

'''


class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance
    
    @classmethod
    def is_initialized(cls):
        return False if cls._instance is None else True
