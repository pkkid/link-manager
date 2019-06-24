# encoding: utf-8
import os, shutil
from linkmanager import LINKROOT, LINKDIR
from linkmanager import log, utils
from linkmanager import cplinks


def get_options(parser):
    """ Command line options for mklink. """
    options = parser.add_parser('mklink', help=f'create a new entry in {LINKROOT} to sync')
    options.add_argument('paths', nargs='+', help='path to file or directory to be created')
    return options


def run_command(opts):
    """ Create a new entry in LINKROOT to sync. """
    paths = utils.validate_paths(opts.paths, opts.home, opts.linkroot)
    for path in paths:
        dest = path.replace(opts.home, opts.linkroot)
        if os.path.exists(dest):
            log.info(f'Link already exists {dest}')
        elif os.path.isfile(path):
            log.info(f'Copying File {path} to {dest}')
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(path, dest)
        elif os.path.isdir(path):
            log.info(f'Copying Dir {path} to {dest}')
            shutil.copytree(path, dest)
            open(os.path.join(dest, LINKDIR), 'a').close()
    cplinks.run_command(opts)
