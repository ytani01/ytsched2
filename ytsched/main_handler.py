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

    DEF_DAYS = 45
    SEARCH_MODE_DAYS = 365

    TODO_DAYS = {'off': 0,
                 '1W': 7,
                 '1M': 30,
                 '3M': 93,
                 '1Y': 365,
                 '10Y': 365 * 10 + 2,
                 'all': 365 * 100
                 }
    DEF_TODO_DAYS = 365

    COOKIE_TODO_DAYS = "todo_days"

    def get(self, date=None):
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
        cur_day = datetime.date.today()
        cur_day_str = self.get_argument('cur_day', None)
        self._mylog.debug('cur_day_str=%s', cur_day_str)
        if cur_day_str:
            cur_day = datetime.date.fromisoformat(cur_day_str)
        self._mylog.debug('cur_day=%s', cur_day)
        
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
            date = cur_day

        self._mylog.debug('date=%s', date)

        #
        # todo_days_value
        #
        todo_days_value0 = self.get_conf(self.CONF_KEY_TODO_DAYS)
        self._mylog.debug('todo_days_value0=%s', todo_days_value0)

        todo_days_value = self.get_argument('todo_days', None)
        self._mylog.debug('todo_days_value=%s', todo_days_value)

        if todo_days_value:
            if todo_days_value != todo_days_value0:
                self.set_conf(self.CONF_KEY_TODO_DAYS, todo_days_value)
            else:
                pass

        elif todo_days_value0:
            todo_days_value = todo_days_value0
        else:
            todo_days_value = self.DEF_TODO_DAYS

        todo_days_value = int(todo_days_value)
        self._mylog.debug('todo_days_value=%a', todo_days_value)

        #
        # filter_str
        #
        filter_str0 = self.get_conf(self.CONF_KEY_FILTER_STR)
        filter_str = self.get_argument('filter_str', None)

        if filter_str is not None:
            if filter_str != filter_str0:
                self.set_conf(self.CONF_KEY_FILTER_STR, filter_str)
            else:
                pass

        elif filter_str0:
            filter_str = filter_str0
        else:
            filter_str = ''

        self._mylog.debug('filter_str=\'%s\'', filter_str)
        
        #
        # search_str
        #
        search_str0 = self.get_conf(self.CONF_KEY_SEARCH_STR)
        search_str = self.get_argument('search_str', None)
        if search_str is not None:
            if search_str != search_str0:
                self.set_conf(self.CONF_KEY_SEARCH_STR, search_str)
            else:
                pass
            
        elif search_str0:
            search_str = search_str0
        else:
            search_str = ''

        self._mylog.debug('search_str=\'%s\'', search_str)

        #
        # top_bottom
        #
        top_bottom = self.get_argument('top_bottom', None)
        self._mylog.debug('top_bottom=%s', top_bottom)

        #
        # load ToDo
        #
        todo_sdf = SchedDataFile(None, self._datadir, debug=self._dbg)
        todo_sde = []
        for sde in todo_sdf.sde:
            if filter_str.startswith('!'):
                if filter_str[1:] in sde.search_str():
                    continue
            else:
                if filter_str not in sde.search_str():
                    continue

            if search_str:
                if search_str not in sde.search_str():
                    continue

            todo_sde.append(sde)

        #
        # load schedule data
        #
        sched = []
        delta_day1 = datetime.timedelta(1)
        date_from = date - delta_day1 * self._days
        date_to = date + delta_day1 * (self._days - 1)

        if search_str:
            date_from = date - delta_day1 * self.SEARCH_MODE_DAYS
            date_to = date + delta_day1 * self.SEARCH_MODE_DAYS

        date1 = date_from - delta_day1
        while date1 < date_to:
            date1 += delta_day1
            self._mylog.debug('date1=%s', date1)
            
            sdf = SchedDataFile(date1, self._datadir, debug=self._dbg)
#            self._mylog.debug('sdf=%s', sdf)

            out_sde = []
            for sde in sdf.sde:
                if filter_str.startswith('!'):
                    if filter_str[1:] in sde.search_str():
                        continue
                else:
                    if filter_str not in sde.search_str():
                        continue

                if search_str:
                    if search_str not in sde.search_str():
                        continue

                out_sde.append(sde)

            # ToDo
            for sde in todo_sde:
                if sde.date == date1 and date1 != datetime.date.today():
                    out_sde.append(sde)

            if search_str and not out_sde:
                continue

            sched.append({
                'date': date1,
                'is_holiday': sdf.is_holiday,
                'sde': out_sde
            })

        #
        # render
        #
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
                    todo=todo_sde,
                    todo_days_list=self.TODO_DAYS,
                    todo_days_value=todo_days_value,
                    filter_str=filter_str,
                    search_str=search_str,
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
        orig_date = None
        orig_date_str = self.get_argument('orig_date', None)
        if orig_date_str:
            orig_date = datetime.date.fromisoformat(orig_date_str)

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
