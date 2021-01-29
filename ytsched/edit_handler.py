#!/usr/bin/env python3
#
# (c) 2021 Yoichi Tanibayashi
#
"""
EditHandler
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import datetime
from .handler import HandlerBase
from .ytsched import SchedDataEnt, SchedDataFile


class EditHandler(HandlerBase):
    """
    Web request handler
    """
    HTML_FILE = 'edit.html'

    def get(self, date=None, sde_id=None, todo_flag=False):
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

        todo_flag: bool

        """
        self._mylog.debug('date=%s, sde_id=%s, todo_flag=%s',
                          date, sde_id, todo_flag)
        self._mylog.debug('request=%s', self.request)

        #
        # date
        #
        if not date:
            date_str = self.get_argument('date', None)

            if date_str:
                date = datetime.date.fromisoformat(date_str)

        if not date:
            date = datetime.date.today()

        #
        # search_str
        #
        search_str = self.get_argument('search_str', None)
        self._mylog.debug('search_str=%s', search_str)

        #
        # sde_id
        #
        if not sde_id:
            sde_id = self.get_argument('sde_id', None)

        #
        # todo_flag
        #
        todo_flag = self.get_argument('todo_flag', False)
        if todo_flag == 'true':
            todo_flag = True
        else:
            todo_flag = False

        self._mylog.debug('date=%s, sde_id=%s, todo_flag=%s',
                          date, sde_id, todo_flag)

        #
        # sde
        #
        if sde_id:
            if todo_flag:
                sdf = SchedDataFile(None, topdir=self._datadir,
                                    debug=self._dbg)
            else:
                sdf = SchedDataFile(date, topdir=self._datadir,
                                    debug=self._dbg)

            sde = sdf.get_sde(sde_id)

        else:
            sde = SchedDataEnt('', date, debug=self._dbg)

        self.render(self.HTML_FILE,
                    title="ytsched",
                    author=__author__,
                    url_prefix=self._url_prefix,
                    date=date,
                    sde=sde,
                    todo_flag=todo_flag,
                    search_str=search_str,
                    version=self._version)

    def post(self):
        """
        """
        self._mylog.debug('request.body_arguments=%s',
                          self.request.body_arguments)
        self.get()
