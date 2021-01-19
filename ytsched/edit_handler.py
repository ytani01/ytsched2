#!/usr/bin/env python3
#
# (c) 2021 Yoichi Tanibayashi
#
"""
EditHandler
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import os
import datetime
import tornado.web
from . import SchedDataEnt, SchedDataFile
from .my_logger import get_logger


class EditHandler(tornado.web.RequestHandler):
    """
    Web request handler
    """
    HTML_FILE = 'edit.html'

    def __init__(self, app, req):
        """ Constructor """
        self._dbg = app.settings.get('debug')
        self._mylog = get_logger(self.__class__.__name__, self._dbg)
        self._mylog.debug('debug=%s', self._dbg)
        self._mylog.debug('app=%s', app)
        self._mylog.debug('req=%s', req)

        self._url_prefix = app.settings.get('url_prefix')
        self._mylog.debug('url_prefix=%s', self._url_prefix)

        self._datadir = app.settings.get('datadir')
        self._mylog.debug('datadir=%s', self._datadir)

        self._webroot = app.settings.get('webroot')
        self._mylog.debug('webroot=%s', self._webroot)

        self._version = app.settings.get('version')
        self._mylog.debug('version=%s', self._version)

        super().__init__(app, req)


    def get(self, date=None, sde_id=None):
        """
        ``date``の優先順位
          1. Parameter
          2. getargument('date')
          3. today()

        ``sde_id``の優先順位
          1. Parameter
          2. getargument('sde_id')
          3. SchedDataEnt.new_id()

        Parameters
        ----------
        date: datetime.date

        sde_id: str

        """
        self._mylog.debug('date=%s, sde_id=%s', date, sde_id)

        if not date:
            date_str = self.get_argument('date', None)
            self._mylog.debug('date_str=%s', date_str)

            if date_str:
                date = datetime.date.fromisoformat(date_str)
                
        if not date:
            date = datetime.date.today()

        self._mylog.debug('date=%s', date)

        if not sde_id:
            sde_id = self.get_argument('sde_id', None)

        if sde_id:
            sdf = SchedDataFile(date, topdir=self._datadir,
                                debug=self._dbg)
            sde = sdf.get_sde(sde_id)

        else:
            sde = SchedDataEnt('', date, debug=self._dbg)
            sde_id = sde.id

        self.render(self.HTML_FILE,
                    title="ytsched",
                    author=__author__,
                    url_prefix=self._url_prefix,
                    date=date,
                    sde=sde,
                    sde_id=sde_id,
                    today=datetime.date.today(),
                    delta_day1=datetime.timedelta(1),
                    version=self._version)
