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
from .handler import HandlerBase
from .ytsched import SchedDataFile, SchedDataEnt


class MainHandler(HandlerBase):
    """
    Web request handler
    """
    HTML_FILE = 'main.html'

    DEF_DAYS = 30

    def get(self, date=None, days=DEF_DAYS):
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

        self.exec_cmd()

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
                    self._mylog.debug('\'%s\'', sde)

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

    def exec_cmd(self):
        """
        """
        self._mylog.debug('')

        cmd = self.get_argument('cmd', None)
        if not cmd:
            return

        orig_date_str = self.get_argument('orig_date', None)
        if orig_date_str:
            orig_date = datetime.date.fromisoformat(orig_date_str)
        else:
            orig_date = datetime.date.today()

        self._mylog.debug('orig_date=%s', orig_date)

        date_str = self.get_argument('date', None)
        if date_str:
            date = datetime.date.fromisoformat(date_str)
        else:
            date = datetime.date.today()

        self._mylog.debug('date=%s', date)

        time_start_str = self.get_argument('time_start', None)
        if time_start_str:
            time_start = datetime.time.fromisoformat(time_start_str)
        else:
            time_start = None

        time_end_str = self.get_argument('time_end', None)
        if time_end_str:
            time_end = datetime.time.fromisoformat(time_end_str)
        else:
            time_end = None

        self._mylog.debug('time_start, time_end: %s-%s',
                          time_start, time_end)

        sde_type = self.get_argument('sde_type', '')
        title = self.get_argument('title', '')
        place = self.get_argument('place', '')
        self._mylog.debug('[%s]%s@%s', sde_type, title, place)

        text = self.get_argument('text', '')
        self._mylog.debug('test:\'%s\'', text)
        
        sde_id = self.get_argument('sde_id')
        self._mylog.debug('sde_id=%s', sde_id)

        if cmd == 'add':
            self._mylog.debug('EXEC [%s]', cmd)

            sde_id = SchedDataEnt.new_id()

            sdf = SchedDataFile(date, topdir=self._datadir,
                                debug=self._dbg)
            sdf.add_sde(sde_id, date, time_start, time_end,
                        sde_type, title, place, text)
            sdf.save()

        if cmd == 'del':
            self._mylog.debug('EXEC [%s]', cmd)

            orig_sdf = SchedDataFile(orig_date, topdir=self._datadir,
                                     debug=self._dbg)
            orig_sdf.del_sde(sde_id)
            orig_sdf.save()

        if cmd == 'fix':
            self._mylog.debug('EXEC [%s]', cmd)

            orig_sdf = SchedDataFile(orig_date, topdir=self._datadir,
                                     debug=self._dbg)
            orig_sdf.del_sde(sde_id)
            orig_sdf.save()
            
            sdf = SchedDataFile(date, topdir=self._datadir,
                                debug=self._dbg)
            sdf.add_sde(sde_id, date, time_start, time_end,
                        sde_type, title, place, text)
            sdf.save()
