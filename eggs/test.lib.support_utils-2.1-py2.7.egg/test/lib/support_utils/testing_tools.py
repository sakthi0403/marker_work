#!/usr/bin/env python

'''
testing_tools.py - General testing and mocking utilities that are useful to write unit tests.

'''
import urllib2
from StringIO import StringIO


class TestHTTPHandler(urllib2.HTTPHandler):
    res_dict = dict()
        
    def http_open(self, req):
        return self.mock_response(req)
    
    @classmethod
    def set_responses(cls, res_dict):
        cls.res_dict = res_dict
    
    def mock_response(self, req):
        if req.get_full_url() in self.res_dict.keys():
            metadata = self.res_dict[req.get_full_url()]
            data = metadata['data']
            headers = metadata['headers']
            res_code = metadata['res_code']
            res_msg = metadata['res_msg']
            resp = urllib2.addinfourl(StringIO(data), headers, req.get_full_url())
            resp.code = res_code
            resp.msg = res_msg
            return resp
        else:
            resp = urllib2.addinfourl(StringIO("The url was not found in my dictionary!"),
                                       "mock message", req.get_full_url())
            resp.code = 404
            resp.msg = "Error"
            return resp
        
def test_TestHTTPHandler():
    '''
    >>> TestHTTPHandler.set_responses({'http://localhost' : { 'data' : 'test', 'headers' : 'mock', 'res_code' : 200, 'res_msg' : 'Ok'}})
    >>> myopen = urllib2.build_opener(TestHTTPHandler)                             
    >>> urllib2.install_opener(myopen)                                                                                                                                                                                                                                           
    >>> response=urllib2.urlopen('http://localhost')                               
    >>> print response.read()
    test
    >>> print response.code
    200
    >>> print response.msg
    Ok
    '''
    pass
