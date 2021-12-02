# encoding: utf-8
import os
import shutil
from linkmanager import DELETED, LINKROOT, LINKDIR
from linkmanager import log, utils
cyan = utils.cyan


def get_options(parser):
    """ Command line options for rmlink. """
    options = parser.add_parser('rmlink', help=f'remove an entry from {LINKROOT}')
    options.add_argument('paths', nargs='+', help='path to file or directory to be removed')
    return options


def remove_syncpath(syncpath, home, linkroot, dryrun=False, force=None):
    """ Cleanup a removed syncpath. Copy original contents back into place.
        1. Make sure homepath is a symlink pointing to syncpath.
        2. Make sure homepath is pointing to a non-existing file.
        3. Make sure syncpath exists.
        4. Delete homepath & copy syncpath to its location!
    """
    _syncpath, _ = utils.get_syncflag(syncpath)
    homepath = _syncpath.replace(linkroot, home)
    # Make sure homepath is a symlink pointing to syncpath.
    if utils.linkpath(homepath) != _syncpath:
        log.debug(f'DISABLED - {cyan(homepath)}')
        return 0
    # Make sure homepath is pointing to a non-existing file.
    if utils.exists(utils.linkpath(homepath)):
        log.debug(f'Syncing appears valid for {cyan(homepath)}')
        return 0
    # Make sure syncpath exists
    if not utils.exists(syncpath):
        log.debug(f'MISSING  - {cyan(syncpath)}')
        return 0
    # Delete homepath & copy syncpath to its location!
    ftype = utils.get_ftype(syncpath)
    log.info(f'Removing sync for {ftype} {cyan(homepath)}')
    if not dryrun:
        if utils.is_link(syncpath):
            utils.safe_unlink(homepath)
            os.symlink(os.readlink(syncpath), homepath)
            return 1
        elif utils.is_file(syncpath):
            utils.safe_unlink(homepath)
            shutil.copyfile(syncpath, homepath)
            return 1
        elif utils.is_dir(syncpath):
            utils.safe_unlink(homepath)
            shutil.copytree(syncpath, homepath)
            utils.safe_unlink(os.path.join(homepath, LINKDIR))
            return 1
    return 0


def run_command(opts):
    """ Remove an entry from LINKROOT. """
    actions = 0
    homepaths = utils.validate_paths(opts.paths, opts.home, opts.linkroot)
    for homepath in homepaths:
        syncpath = homepath.replace(opts.home, opts.linkroot)
        actions += remove_syncpath(syncpath, opts.home, opts.linkroot, opts.dryrun, opts.force)
        os.rename(syncpath, f'{syncpath}[{DELETED}]')
    return actions
