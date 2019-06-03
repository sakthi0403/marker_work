#!/usr/bin/env python

'''
tools.py are a bunch of utility tools and routines that help achieve
 a specific purpose that has a commone use.
'''

def arguments():
    '''
    Returns tuple containing dictionary of calling function's
        named arguments and a list of calling function's unnamed
        positional arguments.
    '''
    from inspect import getargvalues, stack
    posname, kwname, args = getargvalues(stack()[1][0])[-3:]
    posargs = args.pop(posname, [])
    args.update(args.pop(kwname, []))
    return args, posargs
