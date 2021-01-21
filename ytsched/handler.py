#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
HandlerBase
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import tornado.web
from .my_logger import get_logger


class HandlerBase(tornado.web.RequestHandler):
    """ HandlerBase """
    def __init__(self, app, req):
        """ Constructor """
        self._dbg = app.settings.get('debug')
        self._mylog = get_logger(self.__class__.__name__, self._dbg)
        self._mylog.debug('debug=%s', self._dbg)
        self._mylog.debug('app=%s', app)
        self._mylog.debug('req=%s', req)

        self._app = app
        self._req = req

        self._url_prefix = app.settings.get('url_prefix')
        self._mylog.debug('url_prefix=%s', self._url_prefix)

        self._datadir = app.settings.get('datadir')
        self._mylog.debug('datadir=%s', self._datadir)

        self._webroot = app.settings.get('webroot')
        self._mylog.debug('webroot=%s', self._webroot)

        self._days = app.settings.get('days')
        self._mylog.debug('days=%s', self._days)

        self._version = app.settings.get('version')
        self._mylog.debug('version=%s', self._version)

        super().__init__(app, req)
