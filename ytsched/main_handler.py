#!/usr/bin/env python3
#
# (c) 2021 Yoichi Tanibayashi
#
"""
MainHandler
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import datetime
import tornado.web
from .ytsched import SchedDataFile
from .my_logger import get_logger


class MainHandler(tornado.web.RequestHandler):
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

    def get(self, date=None, days=30):
        """
        GET method and rendering

        date priority
        1. parameter
        2. get_argument('date')
        3. get_argument('year', 'month', 'day')
        4. today

        Parameters
        ----------
        date: str

        days: int
            +/- days
        """
        self._mylog.debug('request=%s', self.request)

        if not date:
            date_str = self.get_argument('date', None)
            if date_str:
                date = datetime.date.fromisoformat(date_str)

        if not date:
            year = self.get_argument('year', None)
            month = self.get_argument('month', None)
            day = self.get_argument('day', None)

            if year and month and day:
                date = datetime.date(int(year), int(month), int(day))

        if not date:
            date = datetime.date.today()

        self._mylog.debug('date=%s', date)

        sched = []
        delta_day1 = datetime.timedelta(1)

        date_from = date - delta_day1 * days
        date_to = date + delta_day1 * (days - 1)

        for d in range(-days, days):
            date1 = date + delta_day1 * d
            self._mylog.debug('date1=%s', date)
            sdf = SchedDataFile(date1, self._datadir, debug=self._dbg)
            self._mylog.debug('sdf=%s', sdf)
            sched.append({'date': date1, 'sde': sdf.sde})

        top_bottom = self.get_argument('top_bottom', None)

        if self._dbg:
            for dent in sched:
                self._mylog.debug('date:%s', dent['date'])
                for sde in dent['sde']:
                    self._mylog.debug('%s', sde)

        elif self.request.uri != self._url_prefix:
            self._mylog.warning('redirect: %s', self._url_prefix)
            self.redirect(self._url_prefix)
            return

        self.render(self.HTML_FILE,
                    title="ytsched",
                    author=__author__,
                    url_prefix=self._url_prefix,
                    today=datetime.date.today(),
                    delta_day1=delta_day1,
                    date=date,
                    date_from=date_from,
                    date_to=date_to,
                    sched=sched,
                    top_bottom=top_bottom,
                    version=self._version)

    def post(self):
        """ POST """
        self._mylog.debug('request=%s', self.request.__dict__)
        self._mylog.debug('request.body_arguments=%s',
                          self.request.body_arguments)

        date_str = self.get_argument('date', None)
        if date_str:
            date = datetime.date.fromisoformat(date_str)

        if not date:
            year = self.get_argument('year', None)
            month = self.get_argument('month', None)
            day = self.get_argument('day', None)

            if year and month and day:
                date = datetime.date(int(year), int(month), int(day))

        if not date:
            date = datetime.date.today()

        self._mylog.debug('date=%s', date)

        self.get(date, days=30)
