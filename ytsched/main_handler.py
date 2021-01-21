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

    TODO_DAYS = {'off': 0,
                 '1w': 7,
                 '1mo': 30,
                 '1yr': 365,
                 '10yrs': 365 * 10 + 2,
                 'all': 365 * 100
                 }
    DEF_TODO_DAYS = 365

    COOKIE_TODO_DAYS = "todo_days"

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

        if self.request.uri != self._url_prefix:
            self._mylog.warning('redirect: %s', self._url_prefix)
            self.redirect(self._url_prefix)
            return

        todo_flag = False

        #
        # exec command (add/fix/del)
        #
        cmd = self.get_argument('cmd', None)

        if cmd in ['add', 'fix', 'del']:
            todo_flag = self.exec_update(cmd)

        #
        # set Date
        #
        if todo_flag:
            date = datetime.date.today()

        if not date:
            date_str = self.get_argument('date', None)
            self._mylog.debug('date_str=%s', date_str)
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

        #
        # load schedule data
        #
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

        #
        # load ToDo
        #
        todo_sdf = SchedDataFile(None, self._datadir, debug=self._dbg)

        #
        # todo_days_value
        #
        
        todo_days_value0 = self.get_cookie(self.COOKIE_TODO_DAYS)
        self._mylog.debug('todo_days_value0=%s', todo_days_value0)
        todo_days_value = self.get_argument('todo_days', None)
        self._mylog.debug('todo_days_value=%s', todo_days_value)
        if todo_days_value:
            if todo_days_value != todo_days_value0:
                self.set_cookie(self.COOKIE_TODO_DAYS, todo_days_value)
            else:
                pass

        elif todo_days_value0:
            todo_days_value = todo_days_value0
        else:
            todo_days_value = self.DEF_TODO_DAYS

        todo_days_value = int(todo_days_value)
        self._mylog.debug('todo_days_value=%a', todo_days_value)

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
                    todo=todo_sdf.sde,
                    todo_days_list=self.TODO_DAYS,
                    todo_days_value=todo_days_value,
                    top_bottom=top_bottom,
                    version=self._version)

    def post(self):
        """ POST """
        self._mylog.debug('request=%s', self.request.__dict__)
        self._mylog.debug('request.body_arguments=%s',
                          self.request.body_arguments)

        self.get()

    def exec_update(self, cmd: str) -> bool:
        """
        Parameters
        ----------
        cmd: str

        Returns
        -------
        todo_flag: bool

        """
        self._mylog.debug('')

        todo_flag = False

        #
        # get orig_date
        #
        orig_date_str = self.get_argument('orig_date', None)
        if orig_date_str:
            orig_date = datetime.date.fromisoformat(orig_date_str)
        else:
            orig_date = datetime.date.today()

        self._mylog.debug('orig_date=%s', orig_date)

        #
        # get (new) date
        #
        date_str = self.get_argument('date', None)
        if date_str:
            date = datetime.date.fromisoformat(date_str)
        else:
            date = datetime.date.today()

        self._mylog.debug('date=%s', date)

        #
        # get times
        #
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

        #
        # get sde_type
        #
        sde_type = self.get_argument('sde_type', '')
        if SchedDataEnt.type_is_todo(sde_type):
            orig_date = None
            todo_flag = True

        #
        # title & place
        #
        title = self.get_argument('title', '')
        place = self.get_argument('place', '')
        self._mylog.debug('[%s]%s@%s', sde_type, title, place)

        #
        # text
        #
        text = self.get_argument('text', '')
        self._mylog.debug('test:\'%s\'', text)

        #
        # sde_id
        #
        sde_id = self.get_argument('sde_id')
        self._mylog.debug('sde_id=%s', sde_id)

        #
        # exec cmd
        #
        if cmd == 'add':
            self.cmd_add(None, date, time_start, time_end,
                         sde_type, title, place, text)

        if cmd == 'del':
            self.cmd_del(sde_id, orig_date)

        if cmd == 'fix':
            self._mylog.debug('EXEC [%s]', cmd)
            self.cmd_del(sde_id, orig_date)
            self.cmd_add(sde_id, date, time_start, time_end,
                         sde_type, title, place, text)

        return todo_flag

    def cmd_add(self, sde_id, date, time_start, time_end,
                sde_type, title, place, text):
        """
        Parameters
        ----------

        """
        self._mylog.debug('sde_id=%s, date=%s', sde_id, date)

        new_sde = SchedDataEnt(sde_id, date, time_start, time_end,
                               sde_type, title, place, text,
                               debug=self._dbg)
        if new_sde.is_todo():
            sdf = SchedDataFile(None, topdir=self._datadir,
                                debug=self._dbg)
        else:
            sdf = SchedDataFile(date, topdir=self._datadir,
                                debug=self._dbg)

        sdf.add_sde(new_sde)
        sdf.save()

    def cmd_del(self, sde_id, date):
        """
        Parameters
        ----------
        sde_id: str

        date:

        """
        self._mylog.debug('sde_id=%s, date=%s', sde_id, date)

        sdf = SchedDataFile(date, topdir=self._datadir, debug=self._dbg)
        sdf.del_sde(sde_id)
        sdf.save()
