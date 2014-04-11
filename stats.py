"""
The statistics running module.
Currently can run only one type of statistics.
In general- for every statistic you run, you create
an urllib2 opener suited to the protocol, and ask for
a valid page (currently, only google).
@author: tmrlvi
"""

import socket
if not hasattr(socket, "_orig_socket"):
    socket._orig_socket = socket.socket

import urllib2
import socks
import time
import csv
import argparse

# ==================== Connection Managing ===================
        
def get_urllib2_proxy_opener_function(type):
    """
    A decorator used to create the opener functions for protocols that
    work under urllib2
    """
    def __wrapper__(proxy, port):
        # Make sure you use the original socket
        socket.socket = socket._orig_socket
        # The scheme in the url of the proxy doesn't seem to matter
        full_url = "http://%s:%d" % (proxy, port)
        proxy_support = urllib2.ProxyHandler({type : full_url})
        opener = urllib2.build_opener(proxy_support)
        return opener
    __wrapper__.__name__ = "get_%s_proxy_opener" % type
    return __wrapper__
    
def get_socks_proxy_opener_function(type):
    """
    A decorator used to create the opener functions for protocols that
    work under SocksiPy
    """
    def __wrapper__(proxy, port):
        # Use SocksiPy socket
        socks.setdefaultproxy(type, proxy, port)
        socket.socket = socks.socksocket
        opener = urllib2.build_opener()
        return opener
    __wrapper__.__name__ = "get_socks%d_proxy_opener" % (type + 3)
    return __wrapper__
    

openers_getters = {
    "http"   : get_urllib_proxy_opener_function("http"),
    "https"  : get_urllib_proxy_opener_function("https"),
    "socks5" : get_socks_proxy_opener_function(socks.PROXY_TYPE_SOCKS5),
    "socks4" : get_socks_proxy_opener_function(socks.PROXY_TYPE_SOCKS4),
}

# urls to check for each protocol
urls = {
    "http"   : "http://www.google.com",
    "https"  : "https://www.google.com",
    "socks5" : "http://www.google.com",
    "socks4" : "http://www.google.com",
    
}

        
# ================== Statistics gathering ================

def get_stats(type, proxy, port):
    """
    Gather statistics about the proxy. Tries to connect the a web page
    20 time, and report the rate of the success and the average speed.
    """
    success_counter = 0.0
    counter = 0
    speed_sum = 0.0
    errors = {}
    opener = openers_getters[type](proxy, port)       
    
    print "Checking", "%s:%d" % (proxy, (port or -1)), "for", type, "..."
    for i in xrange(20):
        try:
            begin_time = time.time()
            opener.open(urls[type])
            success_counter += 1
            speed_sum += time.time() - begin_time
        except Exception, e:
            errors[str(e)] = errors.get(str(e), 0) + 1
        counter += 1
    
    # Caculate the statistics
    success_rate = success_counter/counter
    if success_counter == 0:
        average_speed = 0
    else:
        average_speed = speed_sum / success_counter
    # Get the most common error
    error_count = 0
    error_desc = ""
    for desc in errors:
        if errors[desc] > error_count:
            error_count = errors[desc]
            error_desc = desc
    print type, "->", "%s:%d" % (proxy, (port or -1)), ":", success_rate, "(", error_desc, ")"
    return success_rate, average_speed, error_desc
