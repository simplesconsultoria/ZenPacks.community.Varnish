# -*- coding:utf-8 -*-
import sys
import re
import urllib2
import os

from optparse import OptionParser

class ZenossVarnishPlugin:
    def __init__(self, hostname, port, ipAddress, url, useSsl, authentication):
        self.hostname = hostname
        self.port = str(port) or '80'
        self.ipAddress = ipAddress
        self.url = url
        self.useSsl = useSsl
        self.protocol = useSsl and 'https' or 'http'
        self.authentication = authentication
        self._pattern = '(\S*)\s*(\S*)\s*(\S*)\s(.*)\n'
    
    def formatNagios(self,value):
        """HTTP OK HTTP/1.1 200 OK - 30737 bytes in 0.815 seconds |time=0.814667s;;;0.000000 size=30737B;;;0"""
        base = 'Ok |'
        for line in value:
            tmpStr = '%s=%s;;;0 ' % (line['key'],line['persec'],)
            base += tmpStr
        return base
        
    def run(self):
        headerLine = ['key','raw','persec','explain']
        headers = [('User-agent', 'Zenoss')]
        if self.hostname and self.ipAddress:
            headers.append(('Host',self.hostname))
            address = '%s://%s:%s%s' % (self.protocol,self.ipAddress,self.port,self.url)
        else:
            address = '%s://%s:%s%s' % (self.protocol,self.hostname,self.port,self.url)
        if self.authentication:
            username, passwd = self.authentication.split(':')
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, address, username, password)
            authhandler = urllib2.HTTPBasicAuthHandler(passman)
            opener = urllib2.build_opener(authhandler)
        else:
            opener = urllib2.build_opener()
        
        opener.addheaders = headers
        f = opener.open(address)
        data = f.read()
        data = data +'\n'
        response = []
        lines = re.findall(self._pattern,data)
        for line in lines:
            response.append(dict(zip(headerLine,line)))
        response = self.formatNagios(response)
        return response


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-H', '--hostname', dest='hostname',
                      help='Hostname of http server containing Varnish stat data')
    parser.add_option('-p', '--port', dest='port', default=80, type='int',
                      help='Port of http server')
    parser.add_option('-i', '--ipAddress', dest='ipAddress', 
                      help='IP Address http server')
    parser.add_option('-U', '--url', dest='url', default='/status/varnish.txt',
                      help='Path to Varnish Stats')
    parser.add_option('-s', '--useSsl', dest='useSsl', default=False,
                      help='Use SSL?')
    parser.add_option('-a', '--authentication', dest='authentication', 
                      help='Authentication')
    options, args = parser.parse_args()

    if not options.hostname:
        print "You must specify the hostname parameter."
        sys.exit(1)

    cmd = ZenossVarnishPlugin(options.hostname, options.port, 
                              options.ipAddress, options.url, 
                              options.useSsl, options.authentication,)

    result = cmd.run()
    sys.exit(result)