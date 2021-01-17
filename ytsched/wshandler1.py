#!/usr/bin/env python3
#
# (c) 2021 Yoichi Tanibayashi
#
"""
Websocket Handler1
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import os
import time
import tornado.websocket
from .my_logger import get_logger


class WsHandler1(tornado.websocket.WebSocketHandler):
    """
    Websocket handler1
    """
    MSG_FILE = 'msg.txt'

    Client = set()

    def __init__(self, app, req):
        """ Constructor """
        self._dbg = app.settings.get('debug')
        self._mylog = get_logger(self.__class__.__name__, self._dbg)
        self._mylog.debug('app=%s', app)
        self._mylog.debug('req=%s', req)

        self._req = req

        self._workdir = app.settings.get('workdir')
        self._msg_file = os.path.join(self._workdir, self.MSG_FILE)
        self._mylog.debug('msg_file=%s', self._msg_file)

        super().__init__(app, self._req)

    def open(self):
        """ open """
        if self not in self.Client:
            self.Client.add(self)

        self._mylog.debug('Client=%s', self.Client)

        msg_text = ''
        try:
            with open(self._msg_file) as f:
                msg_text = f.readlines()
        except FileNotFoundError:
            with open(self._msg_file, mode='w') as f:
                pass

        for txt in msg_text:
            txt.rstrip('\n')
            self._mylog.debug('txt=%s', txt)
            self.write_message(txt)

    def on_message(self, msg):
        """ on_message """
        self._mylog.debug('msg=%s', msg)

        msg = '\n[%s %s]\n%s' % (
            time.strftime('%F %T'), self._req.remote_ip, msg)
        self._mylog.debug('msg=%s', msg)

        with open(self._msg_file, mode='a') as f:
            f.write(msg)

        for cl in self.Client:
            cl.write_message(msg)

    def on_close(self):
        """ on_close """
        if self in self.Client:
            self.Client.remove(self)

        self._mylog.debug('client=%s', self.Client)
