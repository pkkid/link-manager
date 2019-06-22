# encoding: utf-8
import os, shutil
from linkmanager import HOME
from linkmanager import LINKROOT, LINKDIR
from linkmanager import log, utils
from linkmanager import cplinks
_ = utils.short_home


def get_options(parser):
    """ Command line options for mklink. """
    options = parser.add_parser('mklink', help=f'create a new entry in {LINKROOT} to sync')
    options.add_argument('paths', nargs='+', help='path to file or directory to be created')
    return options


def run_command(opts):
    """ Create a new entry in LINKROOT to sync. """
    utils.validate_paths(opts.paths, opts.linkroot)
    for path in opts.paths:
        dest = path.replace(HOME, opts.linkroot)
        if os.path.exists(dest):
            log.info(f'Link already exists {_(dest)}')
        elif os.path.isfile(path):
            log.info(f'Copying File {_(path)} to {_(dest)}')
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(path, dest)
        elif os.path.isdir(path):
            log.info(f'Copying Dir {_(path)} to {_(dest)}')
            shutil.copytree(path, dest)
            open(os.path.join(dest, LINKDIR), 'a').close()
    cplinks.run_command(opts)
