# -*- coding:utf-8 -*-
import Products.ZenModel.RRDDataSource as RRDDataSource
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence
from AccessControl import ClassSecurityInfo, Permissions
from Products.ZenUtils.Utils import binPath


class VarnishDataSource(ZenPackPersistence, RRDDataSource.RRDDataSource):

    HTTP_MONITOR = 'Varnish'

    ZENPACKID = 'ZenPacks.community.Varnish'

    sourcetypes = (HTTP_MONITOR, )
    sourcetype = HTTP_MONITOR

    timeout = 60
    eventClass = '/Status/Web'

    hostname = '${dev/id}'
    ipAddress = '${dev/manageIp}'
    port = 80
    useSsl= False
    url = '/status/varnish.txt'
    basicAuthUser = ''
    basicAuthPass = ''

    _properties = RRDDataSource.RRDDataSource._properties + (
        {'id': 'hostname', 'type': 'string', 'mode': 'w'},
        {'id': 'ipAddress', 'type': 'string', 'mode': 'w'},
        {'id': 'port', 'type': 'int', 'mode': 'w'},
        {'id': 'useSsl', 'type': 'boolean', 'mode': 'w'},
        {'id': 'url', 'type': 'string', 'mode': 'w'},
        {'id': 'basicAuthUser', 'type': 'string', 'mode': 'w'},
        {'id': 'basicAuthPass', 'type': 'string', 'mode': 'w'},
        {'id': 'timeout', 'type': 'int', 'mode': 'w'},
        )

    _relations = RRDDataSource.RRDDataSource._relations + (
        )


    factory_type_information = (
    {
        'immediate_view': 'editVarnishDataSource',
        'actions':
        (
            {'id': 'edit',
             'name': 'Data Source',
             'action': 'editVarnishDataSource',
             'permissions': (Permissions.view, ),
            },
        )
    },
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title=None, buildRelations=True):
        RRDDataSource.RRDDataSource.__init__(self, id, title, buildRelations)

    def getDescription(self):
        if self.sourcetype == self.HTTP_MONITOR:
            return self.ipAddress + self.url
        return RRDDataSource.RRDDataSource.getDescription(self)

    def useZenCommand(self):
        return True

    def getCommand(self, context):
        parts = [binPath('check_http')]
        if self.hostname:
            parts.append('-H %s' % self.hostname)
        if self.ipAddress:
            parts.append('-I %s' % self.ipAddress)
        if self.port:
            parts.append('-p %s' % self.port)
        if self.timeout:
            parts.append('-t %s' % self.timeout)
        if self.useSsl:
            parts.append('-S')
        if self.url:
            parts.append('-u %s' % self.url)
        if self.basicAuthUser or self.basicAuthPass:
            parts.append('-a %s:%s' % (self.basicAuthUser, self.basicAuthPass))
        cmd = ' '.join(parts)
        cmd = RRDDataSource.RRDDataSource.getCommand(self, context, cmd)
        return cmd

    def checkCommandPrefix(self, context, cmd):
        return cmd

    def addDataPoints(self):
        if not self.datapoints._getOb('time', None):
            self.manage_addRRDDataPoint('time')
        if not self.datapoints._getOb('size', None):
            self.manage_addRRDDataPoint('size')

    def zmanage_editProperties(self, REQUEST=None):
        '''validation, etc'''
        if REQUEST:
            # ensure default datapoint didn't go away
            self.addDataPoints()
            # and eventClass
            if not REQUEST.form.get('eventClass', None):
                REQUEST.form['eventClass'] = self.__class__.eventClass
        return RRDDataSource.RRDDataSource.zmanage_editProperties(self,
                                                                  REQUEST)
