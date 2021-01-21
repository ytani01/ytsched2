#!/usr/bin/env python3
#
# (c) Yoichi Tanibayashi
#
'''
YTスケジューラ
'''
__author__  = 'Yoichi Tanibayashi'
__date__    = '2021/01'

import time
import os
import shutil
import re
import datetime
from .my_logger import get_logger


def htmlstr2text(intext: str) -> str:
    """
    Parameters
    ----------
    intext: str

    Returns
    -------
    outtext: str
    """
    outtext = intext
    # outtext = html2text.html2text(intext)
    outtext = outtext.replace('&amp;', '&')
    outtext = outtext.replace('&nbsp;', ' ')
    outtext = outtext.replace('&#160;', ' ')
    outtext = re.sub(r'<BR */*>', '\n', outtext, flags=re.IGNORECASE)
    return outtext


def text2htmlstr(intext: str) -> str:
    """
    Parameters
    ----------
    intext: str
        normal text string

    Returns
    -------
    outtext: str
        HTML text
    """
    outtext = intext.rstrip('\n')
    outtext = outtext.replace('&', '&amp;')
    outtext = outtext.replace(' ', '&nbsp;')
    outtext = outtext.replace('\n', '<br />')
    return outtext


class SchedDataEnt:
    '''
    スケジュール・データ・エンティティ
    '''
    TIME_NULL = ':-:'
    TYPE_PREFIX_TODO = '□'
    TYPE_HOLYDAY = ['休日', '祝日']
    TITLE_PREFIX_IMPORTANT = ['★', '☆']
    TITLE_PREFIX_CANCELED = ['(キャンセル', '(欠', '(中止', '(休']

    _log = get_logger(__name__, False)

    def __init__(self, id='',
                 date: datetime.date = datetime.date.today(),
                 time_start: datetime.time = '',
                 time_end: datetime.time = '',
                 sde_type='', title='', place='', text='',
                 debug=False):
        self.debug = debug
        self.__class__._log = get_logger(self.__class__.__name__,
                                         self.debug)
        self._log.debug('(%s)%s %s-%s [%s] %s @%s: %s.',
                        id, date, time_start, time_end,
                        sde_type, title, place, text)

        self.id = id
        self.date = date
        self.time_start = time_start
        self.time_end = time_end
        self.type = sde_type
        self.title = title
        self.place = place
        self.text = htmlstr2text(text)

        if self.id == '':
            self.id = SchedDataEnt.new_id()

    def __str__(self):
        """ str(self) """
        out_str = '(%s) ' % (self.id)
        out_str += self.date.strftime('%Y/%m/%d ')

        if self.time_start:
            out_str += self.time_start.strftime('%H:%M-')
        else:
            out_str += ':-'

        if self.time_end:
            out_str += self.time_end.strftime('%H:%M ')
        else:
            out_str += ': '

        out_str += '[%s]' % (htmlstr2text(self.type))
        out_str += '%s' % (htmlstr2text(self.title))
        out_str += '@%s: ' % (htmlstr2text(self.place))
        out_str += htmlstr2text(self.text)

        return out_str

    def mk_dataline(self):
        """
        ファイル保存用の文字列を生成
        """
        date_str = self.date.strftime('%Y/%m/%d')

        time_start_str = ':'
        if self.time_start:
            time_start_str = self.time_start.strftime('%H:%M')

        time_end_str = ':'
        if self.time_end:
            time_end_str = self.time_end.strftime('%H:%M')

        time_str = time_start_str + '-' + time_end_str

        return '\t'.join((self.id, date_str, time_str,
                          self.type, self.title, self.place,
                          text2htmlstr(self.text)))

    @classmethod
    def new_id(cls):
        id = str(time.time()).replace('.', '-')
        cls._log.debug('id=%s', id)
        return id

    def is_todo(self):
        self._log.debug('')
        if self.type == '':
            return False
        return self.type.startswith(self.TYPE_PREFIX_TODO)

    def is_holiday(self):
        self._log.debug('')
        if self.type == '':
            return False
        return self.type in self.TYPE_HOLYDAY

    def is_important(self):
        if self.title == '':
            return False
        for start_str in self.TITLE_PREFIX_IMPORTANT:
            if self.title.lower().startswith(start_str):
                return True

        return False

    def is_canceled(self):
        if self.title == '':
            return False

        for start_str in self.TITLE_PREFIX_CANCELED:
            if self.title.lower().startswith(start_str):
                return True

        return False

    def get_date(self):
        '''
        Returns
        -------
        (year, month, day)
        '''
        self._log.debug('')
        return (self.date.year, self.date.month, self.date.day)

    def set_date(self, d: datetime.date = None):
        '''
        Parameters
        ----------
        d: datetime.date

        '''
        self._log.debug('d=%s', d)

        if d is None:
            self.date = datetime.date.today()
            return

        self.date = d

    def get_timestr(self) -> str:
        '''
        Returns
        -------
        'HH:MM-HH:MM' : str
        ':-:', ':-HH:MM', 'HH:MM-'

        '''
        time_start_str = ':'
        if self.time_start:
            time_start_str = self.time_start.strftime('%H:%M')

        time_end_str = ':'
        if self.time_end:
            time_end_str = self.time_end.strftime('%H:%M')

        time_str = '%s-%s' % (time_start_str, time_end_str)

        self._log.debug('time_str=%s', time_str)
        return time_str

    def set_time(self, t1=None, t2=None):
        '''
        Parameters
        ----------
        t1: (hour1, minute1)
        t2: (hour2, minute2)
        '''
        self._log.debug('t1=%s, t2=%s', t1, t2)

        if t1 is None or len(t1) < 2:
            h1 = ''
            m1 = ''
        else:
            h1 = '02d' % t1[0]
            m1 = '02d' % t1[1]

        if t2 is None or len(t2) < 2:
            h2 = ''
            m2 = ''
        else:
            h2 = '02d' % t2[0]
            m2 = '02d' % t2[1]

        self.time = '%s:%s-%s:%s' % (h1, m1, h2, m2)


class SchedDataFile:
    '''
    スケジュール・データ・ファイル
    '''
    DEF_TOP_DIR = '/home/ytani/ytsched/data'
    PATH_FORMAT = '%s/%04s/%02s/%02s.cgi'
    BACKUP_EXT = '.bak'
    ENCODE = ['utf-8', 'euc_jp']

    def __init__(self, date: datetime.date = None, topdir=DEF_TOP_DIR,
                 debug=False):
        """
        date: datetime.date

        topdir: str

        """
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('date=%s, topdir=%s', date, topdir)

        self.date = date
        self.topdir = topdir

        self.pathname = self.date2path(self.date, self.topdir)

        pl = self.pathname.split('/')
        self.filename = pl.pop()
        self.dirname  = '/'.join(pl)

        self.sde = self.load()

    def date2path(self,
                  date: datetime.date = None,
                  topdir: str = DEF_TOP_DIR) -> str:
        """
        Parameters
        ----------
        date: datetime.date

        Returns
        -------
        path: str

        """
        self._log.debug('date=%s, topdir=%s', date, topdir)

        pathname = self.PATH_FORMAT % (topdir,
                                       date.strftime('%Y'),
                                       date.strftime('%m'),
                                       date.strftime('%d'))
                                   
        return pathname

    def load(self):
        '''
        データファイルの読み込み

        Notes
        -----
        初期化時に自動的に実行される
        '''
        self._log.debug('')

        ok = False
        for e in self.ENCODE:
            self._log.debug('e=%s', e)
            try:
                with open(self.pathname, encoding=e) as f:
                    lines = f.readlines()
                    ok = True
                    break
            except FileNotFoundError:
                self._log.debug('%s: not found', self.pathname)
                return []
            except UnicodeDecodeError:
                self._log.debug('%s: decode error .. try next ..', e)

        if not ok:
            self._log.warning('%s: invalid encoding', self.pathname)
            return []

        out = []
        for l in lines:
            d = [htmlstr2text(d1) for d1 in l.split('\t')]

            date1 = d[1].split('/')
            date2 = datetime.date(int(date1[0]),
                                  int(date1[1]),
                                  int(date1[2]))

            time1 = d[2].split('-')

            time_start1 = time1[0].split(':')
            self._log.debug('time_start1=%s', time_start1)

            time_end1 = time1[1].split(':')
            self._log.debug('time_end1=%s', time_end1)

            if time_start1[0]:
                time_start2 = datetime.time(
                    int(time_start1[0]) % 24, int(time_start1[1]) % 60)
            else:
                time_start2 = ''

            if time_end1[0]:
                time_end2 = datetime.time(
                    int(time_end1[0]) % 24, int(time_end1[1]) % 60)
            else:
                time_end2 = ''

            sde = SchedDataEnt(d[0], date2, time_start2, time_end2,
                               d[3], d[4], d[5], d[6], debug=self._dbg)
            out.append(sde)

        out2 = sorted(out, key=lambda x: x.get_timestr())
        return out2

    def save(self):
        '''
        データファイルへ保存

        Notes
        -----
        全て上書きされる。
        ファイルが存在する場合は、バックアップされる。
        '''
        self._log.debug('')

        if os.path.exists(self.pathname):
            backup_pathname = self.pathname + self.BACKUP_EXT
            shutil.move(self.pathname, backup_pathname)

        with open(self.pathname, mode='w') as f:
            for sde in self.list:
                line = self.mk_dataline(sde)
                f.write(line)

    def get_sde(self, sde_id: str = None) -> SchedDataEnt:
        """
        Parameters
        ----------
        sde_id: str

        Returns
        -------
        sde: SchedDataEnt
        
        """
        self._log.debug('sde_id=%s', sde_id)

        for sde in self.sde:
            if sde_id == sde.id:
                return sde

        return None
