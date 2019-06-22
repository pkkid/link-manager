# encoding: utf-8
import os, shutil
from linkmanager import HOME
from linkmanager import LINKROOT, LINKDIR
from linkmanager import log, utils
_ = utils.short_home


def get_options(parser):
    """ Command line options for rmlink. """
    options = parser.add_parser('rmlink', help=f'remove an entry from {LINKROOT}')
    options.add_argument('paths', nargs='+', help='path to file or directory to be removed')
    return options


def run_command(opts):
    """ Remove an entry from LINKROOT. """
    utils.validate_paths(opts.paths, opts.linkroot)
    for path in opts.paths:
        source = path.replace(HOME, opts.linkroot)
        if not os.path.exists(source):
            log.info(f'Link does not exist {_(source)}')
        elif os.path.islink(path) and os.path.isfile(path):
            log.info(f'Unlinking File {_(path)}')
            if not opts.dryrun:
                utils.safe_unlink(path)
                os.rename(source, path)
        elif os.path.islink(path) and os.path.isdir(path):
            log.info(f'Unlinking Dir {_(path)}')
            if not opts.dryrun:
                utils.safe_unlink(path)
                shutil.move(source, path)
                utils.safe_unlink(os.path.join(path, LINKDIR))
