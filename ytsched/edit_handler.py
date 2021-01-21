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
        # sde_id
        #
        if not sde_id:
            sde_id = self.get_argument('sde_id', None)

        if sde_id:
            sdf = SchedDataFile(date, topdir=self._datadir,
                                debug=self._dbg)
            sde = sdf.get_sde(sde_id)

        else:
            sde = SchedDataEnt('', date, debug=self._dbg)

        self._mylog.debug('date=%s, sde.id=%s', date, sde.id)

        self.render(self.HTML_FILE,
                    title="ytsched",
                    author=__author__,
                    url_prefix=self._url_prefix,
                    date=date,
                    sde=sde,
                    version=self._version)

    def post(self):
        """
        """
        self._mylog.debug('request.body_arguments=%s',
                          self.request.body_arguments)
        self._mylog.debug('request=%s', self.request)

        date = None
        date_str = self.get_argument('date', None)

        if date_str:
            date = datetime.date.fromisoformat(date_str)

        sde_id = self.get_argument('sde_id', None)

        self._mylog.debug('date=%s, sde_id=%s', date, sde_id)

        self.get(date, sde_id)
