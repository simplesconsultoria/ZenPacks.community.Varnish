#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import re
import urllib2

from optparse import OptionParser

PATTERN = r"([^\ ]*)[^\d]*(\d*)\ *([^\ ]*)\ *([^\n]*)\n"

STATS = {
        'uptime': ('raw', 's', 0),
        'n_backend': ('raw', '', 0),
        'cache_hit': ('persec', '', 0.000000),
        'cache_miss': ('persec', '', 0.000000),
        'n_expired': ('raw', '', 0),
        'n_wrk': ('raw', '', 0),
        'n_wrk_failed': ('raw', '', 0),
        'n_wrk_max': ('raw', '', 0),
        'n_wrk_overflow': ('raw', '', 0),
        'n_wrk_drop': ('raw', '', 0),
        'n_object': ('raw', '', 0),
        'n_lru_nuked': ('raw', '', 0),
}


class ZenossVarnishPlugin:

    def __init__(self, hostname, port, ipAddress, url, useSsl, authentication):
        self.hostname = hostname
        self.port = str(port) or '80'
        self.ipAddress = ipAddress
        self.url = url
        self.useSsl = useSsl
        self.protocol = useSsl and 'https' or 'http'
        self.authentication = authentication
        self._pattern = PATTERN

    def hit_rate(self, value):
        ''' cache_hit / client_req '''
        cache_hit = float(value.get('cache_hit', {}).get('raw', 0))
        client_req = float(value.get('client_req', {}).get('raw', 0))
        return '%.2f' % ((cache_hit / client_req) * 100)

    def formatNagios(self, value):
        """OK|foo=0.814667s;;;0.000000 bar=30737B;;;0"""
        base = 'OK |'
        for key in STATS:
            line = value.get(key, None)
            if not line:
                continue
            stat = STATS[key]
            stat_value = line[stat[0]]
            stat_unit = stat[1]
            stat_max = stat[2]
            tmpStr = '%s=%s%s;;;%s ' % (key,
                                        stat_value,
                                        stat_unit,
                                        str(stat_max))
            base += tmpStr
        base += 'hit_rate=%s%s;;;0 ' % (self.hit_rate(value), '%')
        return base

    def run(self):
        headerLine = ['key', 'raw', 'persec', 'explain']
        headers = [('User-agent', 'Zenoss')]
        if self.hostname and self.ipAddress:
            headers.append(('Host', self.hostname))
            address = '%s://%s:%s%s' % (self.protocol,
                                        self.ipAddress,
                                        self.port,
                                        self.url)
        else:
            address = '%s://%s:%s%s' % (self.protocol,
                                        self.hostname,
                                        self.port,
                                        self.url)
        if self.authentication:
            username, passwd = self.authentication.split(':')
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, address, username, passwd)
            authhandler = urllib2.HTTPBasicAuthHandler(passman)
            opener = urllib2.build_opener(authhandler)
        else:
            opener = urllib2.build_opener()

        opener.addheaders = headers
        f = opener.open(address)
        data = f.read()
        data = data +'\n'
        response = []
        lines = re.findall(self._pattern, data)
        for line in lines:
            response.append((line[0], dict(zip(headerLine, line))))
        response = dict(response)
        response = self.formatNagios(response)
        return response


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-H', '--hostname', dest='hostname',
                 help='Hostname of http server containing Varnish stat data')
    parser.add_option('-p', '--port', dest='port', default=80, type='int',
                 help='Port of http server')
    parser.add_option('-I', '--ipAddress', dest='ipAddress',
                 help='IP Address http server')
    parser.add_option('-U', '--url', dest='url', default='/status/varnish.txt',
                 help='Path to Varnish Stats')
    parser.add_option('-s', '--useSsl', dest='useSsl', default=False,
                 help='Use SSL?')
    parser.add_option('-t', '--timeout', dest='timeout',
                 help='Timeout')
    parser.add_option('-a', '--authentication', dest='authentication',
                 help='Authentication')
    options, args = parser.parse_args()

    if not options.hostname:
        print "You must specify the hostname parameter."
        sys.exit(1)

    cmd = ZenossVarnishPlugin(options.hostname, options.port,
                              options.ipAddress, options.url,
                              options.useSsl, options.authentication)

    try:
        result = cmd.run()
    except urllib2.HTTPError:
        print 'HTTP Error'
        sys.exit(1)

    if result:
        print result
        sys.exit(0)
    else:
        sys.exit(1)
