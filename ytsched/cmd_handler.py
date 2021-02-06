#!/usr/bin/env python3
#
# (c) 2021 Yoichi Tanibayashi
#
"""
cmd_handler.py
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/02'

from .handler import HandlerBase


class CmdHandler(HandlerBase):
    """
    """
    URL_PATH = 'cmd'

    def get(self):
        """ GET """
        self._mylog.debug('request=%s', self.request.__dict__)

        for k in self.request.__dict__:
            self._mylog.debug('%s:%s.',
                              k, self.request.__dict__[k])

        self._mylog.debug('body_arguments=%s',
                          self.request.body_arguments)

        self._cmd = self.get_argument('cmd')
        self._mylog.debug('cmd=%s', self._cmd)

        self._cmdfunc = {
            'add': self.cmd_add,
            'fix': self.cmd_fix,
            'update': self.cmd_update,
            'del': self.cmd_del
        }

        try:
            self._cmdfunc[self._cmd]()
        except KeyError as ex:
            self._mylog.error('%s:%s:cmd=%s', type(ex).__name__, ex,
                              self._cmd)

    def post(self):
        """ POST """
        self._mylog.debug('request.body_arguments=%s',
                          self.request.body_arguments)
        self.get()
    
    def cmd_add(self):
        self._mylog.debug('')
        
    def cmd_fix(self):
        self._mylog.debug('')
    
    def cmd_update(self):
        self._mylog.debug('')
    
    def cmd_del(self):
        self._mylog.debug('')
