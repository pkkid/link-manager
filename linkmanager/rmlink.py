# encoding: utf-8
import os, shutil
from linkmanager import DELETED, LINKROOT, LINKDIR
from linkmanager import log, utils


def get_options(parser):
    """ Command line options for rmlink. """
    options = parser.add_parser('rmlink', help=f'remove an entry from {LINKROOT}')
    options.add_argument('paths', nargs='+', help='path to file or directory to be removed')
    return options


def remove_syncpath(syncpath, home, linkroot, dryrun=False):
    """ Cleanup a removed syncpath. Copy original contents back into place. """
    # TODO: Does this work for symlinks?
    homepath = syncpath.replace(linkroot, home).replace(f'[{DELETED}]', '')
    if os.path.islink(homepath) and os.path.isfile(syncpath):
        log.info(f'Unlinking file {homepath}')
        if not dryrun:
            utils.safe_unlink(homepath)
            shutil.copyfile(syncpath, homepath)
    elif os.path.islink(homepath) and os.path.isdir(syncpath):
        log.info(f'Unlinking dir {homepath}')
        if not dryrun:
            utils.safe_unlink(homepath)
            shutil.copytree(syncpath, homepath)
            utils.safe_unlink(os.path.join(homepath, LINKDIR))


def run_command(opts):
    """ Remove an entry from LINKROOT. """
    homepaths = utils.validate_paths(opts.paths, opts.linkroot)
    for homepath in homepaths:
        syncpath = homepath.replace(opts.home, opts.linkroot)
        if not os.path.exists(syncpath):
            log.info(f'Link does not exist {syncpath}')
        remove_syncpath(syncpath, opts.home, opts.linkroot, opts.dryrun)
        os.rename(syncpath, f'{syncpath}[{DELETED}]')
