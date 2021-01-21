#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Web Interface
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import os
import tornado.ioloop
import tornado.httpserver
import tornado.web
from .main_handler import MainHandler
from .edit_handler import EditHandler
from .my_logger import get_logger


class WebServer:
    """
    Web application server
    """
    URL_PREFIX = '/ytsched'

    DEF_PORT = 10085
    DEF_WEBROOT = './webroot/'
    DEF_WORKDIR = '~/ytsched'
    DEF_DATADIR = DEF_WORKDIR + '/data'

    CONF_FNAME = 'Conf.cgi'

    DEF_SIZE_LIMIT = 100*1024*1024  # 100MB

    def __init__(self, port: int = DEF_PORT,
                 webroot: str = DEF_WEBROOT,
                 datadir: str = DEF_DATADIR,
                 days: int = MainHandler.DEF_DAYS,
                 size_limit: int = DEF_SIZE_LIMIT,
                 version: str = '(cur)',
                 debug: bool = False):
        """ Constructor

        Parameters
        ----------
        port: int
            port number
        webroot: str

        datadir: str

        days: int

        size_limit: int
            max upload size
        version: str
            version string
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.info('port=%s, webroot=%s, datadir=%s, days=%s',
                       port, webroot, datadir, days)
        self._log.info('size_limit=%s', size_limit)
        self._log.info('version=%s', version)

        self._port = port
        self._webroot = os.path.expanduser(webroot)
        self._datadir = os.path.expanduser(datadir)
        self._days = days
        self._size_limit = size_limit
        self._version = version

        try:
            os.makedirs(self._datadir, exist_ok=True)
        except Exception as ex:
            raise ex

        self._app = tornado.web.Application(
            [
                (r'/', MainHandler),
                (r'%s' % self.URL_PREFIX, MainHandler),
                (r'%s/' % self.URL_PREFIX, MainHandler),

                (r'%s/edit' % self.URL_PREFIX, EditHandler),
                (r'%s/edit/' % self.URL_PREFIX, EditHandler),
            ],
            static_path=os.path.join(self._webroot, "static"),
            static_url_prefix=self.URL_PREFIX + '/static/',
            template_path=os.path.join(self._webroot, "templates"),

            autoreload=True,
            # xsrf_cookies=False,

            url_prefix=self.URL_PREFIX + '/',

            datadir=self._datadir,
            conffname=self.CONF_FNAME,
            webroot=self._webroot,
            days=self._days,
            size_limit=self._size_limit,
            version=self._version,
            debug=self._dbg
        )
        self._log.debug('app=%s', self._app.__dict__)

        self._svr = tornado.httpserver.HTTPServer(
            self._app, max_buffer_size=self._size_limit)
        self._log.debug('svr=%s', self._svr.__dict__)

    def main(self):
        """ main """
        self._log.debug('')

        self._svr.listen(self._port)
        self._log.info('start server: run forever ..')

        tornado.ioloop.IOLoop.current().start()

        self._log.debug('done')
