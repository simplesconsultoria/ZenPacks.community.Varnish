# -*- coding:utf-8 -*-
import os

from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenUtils.Utils import zenPath
from Products.CMFCore.DirectoryView import registerDirectory


class ZenPack(ZenPackBase):
    """
    ZenPack class to add new zProperties and perform other installation and
    removal tasks.
    """

    def install(self, app):
        super(ZenPack, self).install(app)
        self.symlinkPlugin()

    def remove(self, app, leaveObjects=False):
        if not leaveObjects:
            self.removePluginSymlink()

        super(ZenPack, self).remove(app, leaveObjects=leaveObjects)

    def symlinkPlugin(self):
        os.system('ln -sf %s/check_varnish.py %s/' %
            (self.path('libexec'), zenPath('libexec')))

    def removePluginSymlink(self):
        os.system('rm -f %s/check_varnish.py' % (zenPath('libexec')))


skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())
