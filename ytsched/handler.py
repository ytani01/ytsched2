#!/usr/bin/env python3
#
# (c) 2021 Yoichi Tanibayashi
#
"""
Handler
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import os
import datetime
import tornado.web
from . import SchedDataEnt, SchedDataFile
from .my_logger import get_logger


class Handler(tornado.web.RequestHandler):
    """
    Web request handler
    """
    HTML_FILE = 'main.html'

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

    def get(self, date_from=None, days=90):
        """
        GET method and rendering
        """
        self._mylog.debug('request=%s', self.request)

        delta_day1 = datetime.timedelta(1)

        sde_data = []

        if not date_from:
            date_from_value = self.get_argument('date_from', None)
            if date_from_value:
                (year, month, day) = date_from_value.split('-')
                date_from = datetime.date(int(year), int(month), int(day))

        if not date_from:
            year = self.get_argument('year', None)
            month = self.get_argument('month', None)
            day = self.get_argument('day', None)

            if year and month and day:
                date_from = datetime.date(int(year), int(month), int(day))

        if not date_from:
            date_from = datetime.date.today()

        self._mylog.debug('date_from=%s', date_from)

        for d in range(days):
            date = date_from + delta_day1 * d
            sdf = SchedDataFile(date, self._datadir, debug=self._dbg)
            sde_data.append({'date': date, 'sde': sdf.sde})

        if self._dbg:
            for dent in sde_data:
                self._mylog.debug('date:%s', dent['date'])
                for sde in dent['sde']:
                    self._mylog.debug('%s', sde)
                
        """
        elif self.request.uri != self._url_prefix:
            self._mylog.warning('redirect: %s', self._url_prefix)
            self.redirect(self._url_prefix)
            return
        """
        self.render(self.HTML_FILE,
                    title="ytsched",
                    author=__author__,
                    url_prefix=self._url_prefix,
                    year=year,
                    month=month,
                    today=datetime.date.today(),
                    delta_day1=datetime.timedelta(1),
                    date_from=date_from,
                    data=sde_data,
                    version=self._version)

    async def post(self):
        """
        POST method
        """
        self._mylog.debug('request=%s', self.request.__dict__)
        self._mylog.debug('request.files[\'file1\']=%s',
                          self.request.files['file1'])
        self._mylog.debug('request.body_arguments=%s',
                          self.request.body_arguments)

        self.get()
