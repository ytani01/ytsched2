#
# (c) 2020 Yoichi Tanibayashi
#
"""
main for musicbox package
"""
import click
from . import SchedDataEnt, SchedDataFile
from . import WebServer, __prog_name__
from .my_logger import get_logger

__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'


class DataFileApp:
    def __init__(self, yyyy, mm, dd, topdir='', debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('')

        self.sdf = SchedDataFile(yyyy, mm, dd, topdir=topdir,
                                 debug=self._dbg)

    def main(self):
        self._log.debug('')

        if self.sdf.sde_list == []:
            print('===== No data =====')

        else:
            for sde in self.sdf.sde_list:
                sde.print1()

    def end(self):
        self._log.debug('')


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(invoke_without_command=True,
             context_settings=CONTEXT_SETTINGS, help="""
sample package
""")
@click.pass_context
def cli(ctx):
    """ command group """
    subcmd = ctx.invoked_subcommand

    if subcmd is None:
        print(ctx.get_help())


@cli.command(help="""
test """)
@click.argument('year', type=int, default=2021)
@click.argument('month', type=int, default=1)
@click.argument('day', type=int, default=1)
@click.option('--datadir', '--data', 'datadir',
              type=click.Path(exists=True), default='',
              help='data directory')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def data(year, month, day, datadir, debug):
    """ data  """
    log = get_logger(__name__, debug)

    app = DataFileApp(year, month, day, datadir, debug)
    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('end')


@cli.command(help="""
Web server""")
@click.option('--port', '-p', 'port', type=int,
              default=WebServer.DEF_PORT,
              help='port number')
@click.option('--webroot', '-r', 'webroot', type=click.Path(exists=True),
              default=WebServer.DEF_WEBROOT,
              help='Web root directory')
@click.option('--workdir', '-w', 'workdir', type=click.Path(),
              default=WebServer.DEF_WORKDIR,
              help='work directory')
@click.option('--size_limit', '-l', 'size_limit', type=int,
              default=100*1024*1024,
              help='upload size limit, default=%s' % (
                  WebServer.DEF_SIZE_LIMIT))
@click.option('--version', 'version', type=str, default='<current>',
              help='version string')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def webapp(port, webroot, workdir, size_limit, version, debug):
    """ cmd1  """
    log = get_logger(__name__, debug)

    app = WebServer(port, webroot, workdir, size_limit, version,
                    debug=debug)
    try:
        app.main()
    finally:
        log.info('end')


if __name__ == '__main__':
    cli(prog_name=__prog_name__)
