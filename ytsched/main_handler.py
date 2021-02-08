#!/usr/bin/env python3
#
# (c) 2021 Yoichi Tanibayashi
#
"""
MainHandler
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import re
import math
import datetime
from .handler import HandlerBase
from .ytsched import SchedDataEnt


def days2y_offset(days: int) -> int:
    """
    Parameters
    ----------
    days: int

    Returns
    -------
    offset: int

    """
    dd = 0.8
    a = 70
    b = 0

    if days == 0:
        return 0

    offset = round(math.log10(abs(days + dd) * a) * b)
    if days < 0:
        return -offset
    return offset


GAGE = [
    {'label': '-10Y', 'y_offset': days2y_offset(-3650)},
    {'label':  '-5Y', 'y_offset': days2y_offset(-1826)},
    {'label':  '-2Y', 'y_offset': days2y_offset( -730)},
    {'label':  '-1Y', 'y_offset': days2y_offset( -365)},
    {'label':  '-6M', 'y_offset': days2y_offset( -183)},
    {'label':  '-2M', 'y_offset': days2y_offset(  -61)},
    {'label':  '-1M', 'y_offset': days2y_offset(  -30)},
    {'label':  '-2w', 'y_offset': days2y_offset(  -14)},
    {'label':  '-1w', 'y_offset': days2y_offset(   -7)},
    {'label':  '-3d', 'y_offset': days2y_offset(   -3)},
    {'label':  '-1d', 'y_offset': days2y_offset(   -1)},
    {'label':  '+1d', 'y_offset': days2y_offset(   +1)},
    {'label':  '+3d', 'y_offset': days2y_offset(   +3)},
    {'label':  '+1w', 'y_offset': days2y_offset(   +7)},
    {'label':  '+2w', 'y_offset': days2y_offset(  +14)},
    {'label':  '+1M', 'y_offset': days2y_offset(  +30)},
    {'label':  '+2M', 'y_offset': days2y_offset(  +61)},
    {'label':  '+6M', 'y_offset': days2y_offset( +183)},
    {'label':  '+1Y', 'y_offset': days2y_offset( +365)},
    {'label':  '+2Y', 'y_offset': days2y_offset( +730)},
    {'label':  '+5Y', 'y_offset': days2y_offset(+1826)},
    {'label': '+10Y', 'y_offset': days2y_offset(+3650)},
]


class MainHandler(HandlerBase):
    """
    Web request handler
    """
    DEF_DAYS = 50
    SEARCH_MODE_MAX_DAYS = 365 * 5
    SEARCH_MODE_DAYS = 365
    DEF_SEARCH_N = 5

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

    def post(self):
        """ POST """
        self._mylog.debug('request=%s', self.request.__dict__)
        self._mylog.debug('request.body_arguments=%s',
                          self.request.body_arguments)

        self.get()

    def get(self):
        """
        GET method and rendering

        date priority
        1. get_argument('date')
        2. get_argument('year', 'month', 'day')
        3. today

        Parameters
        ----------
        date: str

        days: int
            +/- days
        """
        self._mylog.debug('request=%s', self.request)
        self._mylog.debug('request.path=%s', self.request.path)

        if self.request.uri != self._url_prefix:
            self._mylog.warning('redirect: %s', self._url_prefix)
            self.redirect(self._url_prefix)
            return

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
        # command (add/fix/del)
        #
        cmd = self.get_argument('cmd', None)

        if cmd in ['add', 'fix', 'update', 'del']:
            date, sde_id = self.exec_update(cmd)

            if cmd in ['update']:
                sdf = self._sd.get_sdf(date)
                sde = sdf.get_sde(sde_id)
                date = sde.date
                todo_flag = sde.is_todo()

                self.render(self.HTML_EDIT,
                            title=self._title,
                            author=self._author,
                            version=self._version,

                            url_prefix=self._url_prefix,
                            post_url=self._url_prefix,
                            date=date,
                            sde=sde,
                            new_flag=False,
                            todo_flag=todo_flag,
                            search_str=search_str,
                            )
                return

        #
        # set Date
        #
        date = None

        cur_day = datetime.date.today()
        cur_day_str = self.get_argument('cur_day', None)
        self._mylog.debug('cur_day_str=%s', cur_day_str)
        if cur_day_str:
            cur_day = datetime.date.fromisoformat(cur_day_str)
        self._mylog.debug('cur_day=%s', cur_day)

        date_str = self.get_argument('date', None)
        self._mylog.debug('date_str=%s', date_str)
        if date_str:
            date = datetime.date.fromisoformat(date_str)

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
        # sde_align
        #
        sde_align = self.get_argument('sde_align', None)
        self._mylog.debug('sde_align=%s', sde_align)
        if not sde_align:
            sde_align = "top"
            self._mylog.debug('[fix]sde_align=%s', sde_align)

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
        # search_n
        #
        search_n_str0 = self.get_conf(self.CONF_KEY_SEARCH_N)
        search_n_str = self.get_argument('search_n', None)
        if search_n_str is not None:
            if search_n_str != search_n_str0:
                self.set_conf(self.CONF_KEY_SEARCH_N, search_n_str)
            else:
                pass

        elif search_n_str0:
            search_n_str = search_n_str0
        else:
            search_n_str = str(self.DEF_SEARCH_N)

        search_n = int(search_n_str)
        self._mylog.debug('search_n=%s', search_n)

        #
        # load ToDo
        #
        todo_sdf = self._sd.get_sdf(None)
        todo_sde = []
        for sde in todo_sdf.sde:
            if filter_str.startswith('!'):
                try:
                    if re.search(filter_str[1:],
                                  sde.search_str()):
                        continue
                except re.error as ex:
                    self._mylog.warning(
                        '%s:%s:%s:%s',
                        type(ex).__name__, ex,
                        filter_str, sde.search_str())
                    continue
            else:
                try:
                    if not re.search(filter_str, sde.search_str()):
                        continue
                except re.error as ex:
                    self._mylog.warning(
                        '%s:%s:%s:%s',
                        type(ex).__name__, ex,
                        filter_str, sde.search_str())
                    continue

            if search_str:
                try:
                    if not re.search(search_str, sde.search_str()):
                        continue
                except re.error as ex:
                    self._mylog.warning(
                        '%s:%s:%s:%s',
                        type(ex).__name__, ex,
                        search_str, sde.search_str())
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
            date_from = date - delta_day1 * self.SEARCH_MODE_MAX_DAYS
            date_from1 = date - delta_day1 * self.SEARCH_MODE_DAYS
            date_to = date

        search_count = 0
        date1 = date_to + delta_day1
        while date1 > date_from:
            if search_str and search_count > 0:
                if search_count >= search_n:
                    date_from = date1
                    break

                if date1 <= date_from1:
                    date_from = date1
                    break

            date1 -= delta_day1
            # self._mylog.debug('date1=%s', date1)

            sdf = self._sd.get_sdf(date1)
            # self._mylog.debug('sdf=%s', sdf)

            out_sde = []
            for sde in sdf.sde:
                # self._mylog.debug('sde=%s', sde)
                if filter_str.startswith('!'):
                    try:
                        if re.search(filter_str[1:],
                                      sde.search_str()):
                            continue
                    except re.error as ex:
                        self._mylog.warning(
                            '%s:%s:%s:%s',
                            type(ex).__name__, ex,
                            filter_str, sde.search_str())
                        continue
                else:
                    try:
                        if not re.search(filter_str, sde.search_str()):
                            continue
                    except re.error as ex:
                        self._mylog.warning(
                            '%s:%s:%s:%s',
                            type(ex).__name__, ex,
                            filter_str, sde.search_str())
                        continue

                if search_str:
                    try:
                        if not re.search(search_str, sde.search_str()):
                            continue
                    except re.error as ex:
                        self._mylog.warning(
                            '%s:%s:%s:%s',
                            type(ex).__name__, ex,
                            search_str, sde.search_str())
                        continue

                out_sde.append(sde)
                search_count += 1

            # ToDo
            for sde in todo_sde:
                # self._mylog.debug('sde=%s', sde)
                if search_str:
                    if not re.search(search_str, sde.search_str()):
                        continue

                if sde.date == date1:
                    out_sde.append(sde)
                    if sde.date == datetime.date.today():
                        todo_sde.remove(sde)

            if search_str and not out_sde:
                continue

            sched.append({
                'date': date1,
                'is_holiday': sdf.is_holiday,
                'sde': out_sde
            })

        sched = sched[::-1]

        #
        # render
        #
        self.render(self.HTML_MAIN,
                    title=self._title,
                    author=self._author,
                    version=self._version,

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
                    search_n=search_n,
                    sde_align=sde_align,
                    sd=self._sd,
                    gage=GAGE,
                    )

    def exec_update(self, cmd: str) -> datetime.date:
        """
        Parameters
        ----------
        cmd: str

        Returns
        -------
        date: datetime.date

        sde_id: str

        """
        self._mylog.debug('')

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
#        if SchedDataEnt.type_is_todo(sde_type):
#            date = datetime.date.today()

        #
        # title & place
        #
        title = self.get_argument('title', '')
        place = self.get_argument('place', '')
        self._mylog.debug('[%s]%s@%s', sde_type, title, place)

        #
        # detail
        #
        detail = self.get_argument('detail', '')
        self._mylog.debug('detail:\'%s\'', detail)

        #
        # deadlines
        #
        deadline_date = self.get_argument('deadline_date', None)
        deadline_time_start = self.get_argument('deadline_time_start',
                                                None)
        deadline_time_end = self.get_argument('deadline_time_end', None)

        if deadline_date and not SchedDataEnt.type_is_todo(sde_type):
            date = datetime.date.today()
            time_start, time_end = None, None
            detail = '〆%s %s-%s\n%s' % (
                deadline_date.replace('-', '/'),
                deadline_time_start, deadline_time_end,
                detail)
            self._mylog.debug('[fix] date=%s', date)
            self._mylog.debug('[fix] detail=%s', detail)
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
                         sde_type, title, place, detail)

        if cmd == 'del':
            self.cmd_del(sde_id, orig_date)
            date = orig_date

        if cmd == 'fix':
            self._mylog.debug('EXEC [%s]', cmd)
            self.cmd_del(sde_id, orig_date)
            self.cmd_add(sde_id, date, time_start, time_end,
                                sde_type, title, place, detail)

        if cmd == 'update':
            self._mylog.debug('EXEC [%s]', cmd)
            self.cmd_del(sde_id, orig_date)
            new_sde = self.cmd_add(sde_id, date, time_start, time_end,
                                   sde_type, title, place, detail)
            if new_sde.is_todo():
                date = None
                sde_id = new_sde.id

        self._mylog.debug('date=%s, sde_id=%s', date, sde_id)
        return date, sde_id

    def cmd_add(self, sde_id, date, time_start, time_end,
                sde_type, title, place, detail):
        """
        Parameters
        ----------
        sde_id: str
        date: datetime.date
        time_start, time_end:
        sde_type: str
        title: str
        place: str
        detail: str

        Returns
        -------
        new_sde: SchedDataEnt

        """
        self._mylog.debug('sde_id=%s, date=%s', sde_id, date)

        new_sde = SchedDataEnt(sde_id, date, time_start, time_end,
                               sde_type, title, place, detail,
                               debug=self._dbg)
        if new_sde.is_todo():
            self._sd.add_sde(None, new_sde)
        else:
            self._sd.add_sde(date, new_sde)

        return new_sde

    def cmd_del(self, sde_id, date):
        """
        Parameters
        ----------
        sde_id: str

        date:

        """
        self._mylog.debug('sde_id=%s, date=%s', sde_id, date)

        self._sd.del_sde(date, sde_id)
