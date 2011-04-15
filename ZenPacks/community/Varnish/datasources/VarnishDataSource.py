# -*- coding:utf-8 -*-

__doc__='''VarnishDataSource.py

Defines datasource for Varnish
'''

import Products.ZenModel.RRDDataSource as RRDDataSource
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence
from AccessControl import ClassSecurityInfo, Permissions
from Products.ZenUtils.ZenTales import talesCompile, getEngine
from Products.ZenUtils.Utils import binPath

DATAPOINTS = ['client_conn','client_drop','client_req','cache_hit',
              'cache_hitpass','cache_miss','backend_conn','backend_unhealthy',
              'backend_busy','backend_fail','backend_reuse','backend_toolate',
              'backend_recycle','backend_unused','fetch_head','fetch_length',
              'fetch_chunked','fetch_eof','fetch_bad','fetch_close',
              'fetch_oldhttp','fetch_zero','fetch_failed','n_sess_mem','n_sess',
              'n_object','n_vampireobject','n_objectcore','n_objecthead',
              'n_smf','n_smf_frag','n_smf_large','n_vbe_conn','n_wrk',
              'n_wrk_create','n_wrk_failed','n_wrk_max','n_wrk_queue',
              'n_wrk_overflow','n_wrk_drop','n_backend','n_expired',
              'n_lru_nuked','n_lru_saved','n_lru_moved','n_deathrow',
              'losthdr','n_objsendfile','n_objwrite','n_objoverflow','s_sess',
              's_req','s_pipe','s_pass','s_fetch','s_hdrbytes','s_bodybytes',
              'sess_closed','sess_pipeline','sess_readahead','sess_linger',
              'sess_herd','shm_records','shm_writes','shm_flushes','shm_cont',
              'shm_cycles','sm_nreq','sm_nobj','sm_balloc','sm_bfree',
              'sma_nreq','sma_nobj','sma_nbytes','sma_balloc','sma_bfree',
              'sms_nreq','sms_nobj','sms_nbytes','sms_balloc','sms_bfree',
              'backend_req','n_vcl','n_vcl_avail','n_vcl_discard','n_purge',
              'n_purge_add','n_purge_retire','n_purge_obj_test',
              'n_purge_re_test','n_purge_dups','hcb_nolock','hcb_lock',
              'hcb_insert','esi_parse','esi_errors','accept_fail',
              'client_drop_late','uptime','backend_retry','dir_dns_lookups',
              'dir_dns_failed','dir_dns_hit','dir_dns_cache_full']

class VarnishDataSource(ZenPackPersistence, RRDDataSource.RRDDataSource):
    
    HTTP_MONITOR = 'Varnish'
    
    ZENPACKID = 'ZenPacks.community.Varnish'
    
    sourcetypes = (HTTP_MONITOR,)
    sourcetype = HTTP_MONITOR

    timeout = 60
    eventClass = '/Status/Web'
        
    hostname = '${dev/id}'
    ipAddress = '${dev/manageIp}'
    port = 80
    useSsl= False
    url = '/'
    basicAuthUser = ''
    basicAuthPass = ''

    _properties = RRDDataSource.RRDDataSource._properties + (
        {'id':'hostname', 'type':'string', 'mode':'w'},
        {'id':'ipAddress', 'type':'string', 'mode':'w'},
        {'id':'port', 'type':'int', 'mode':'w'},
        {'id':'useSsl', 'type':'boolean', 'mode':'w'},
        {'id':'url', 'type':'string', 'mode':'w'},
        {'id':'basicAuthUser', 'type':'string', 'mode':'w'},
        {'id':'basicAuthPass', 'type':'string', 'mode':'w'},
        {'id':'timeout', 'type':'int', 'mode':'w'},
        )
        
    _relations = RRDDataSource.RRDDataSource._relations + (
        )


    factory_type_information = ( 
    { 
        'immediate_view' : 'editVarnishDataSource',
        'actions'        :
        ( 
            { 'id'            : 'edit',
              'name'          : 'Data Source',
              'action'        : 'editVarnishDataSource',
              'permissions'   : ( Permissions.view, ),
            },
        )
    },
    )

    security = ClassSecurityInfo()


    def __init__(self, id, title=None, buildRelations=True):
        RRDDataSource.RRDDataSource.__init__(self, id, title, buildRelations)
        #self.addDataPoints()


    def getDescription(self):
        if self.sourcetype == self.HTTP_MONITOR:
            return self.ipAddress + self.url
        return RRDDataSource.RRDDataSource.getDescription(self)


    def useZenCommand(self):
        return True


    def getCommand(self, context):
        parts = [binPath('check_varnish')]
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
        datapoints = DATAPOINTS
        for dp in datapoints:
            if not self.datapoints._getOb(dp, None):
                self.manage_addRRDDataPoint(dp)


    def zmanage_editProperties(self, REQUEST=None):
        '''validation, etc'''
        if REQUEST:
            # ensure default datapoint didn't go away
            self.addDataPoints()
            # and eventClass
            if not REQUEST.form.get('eventClass', None):
                REQUEST.form['eventClass'] = self.__class__.eventClass
        return RRDDataSource.RRDDataSource.zmanage_editProperties(self, REQUEST)


