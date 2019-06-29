# encoding: utf-8
import os, shutil
from linkmanager import HOSTNAME
from linkmanager import log, utils
from linkmanager import rmlink


def get_options(parser):
    """ Command line options for cplinks. """
    options = parser.add_parser('cplinks', help='symlink synced files and dirs to home directory')
    return options


def create_symlink(syncpath, home, linkroot, dryrun=False):
    """ Create a symlink for the specified syncpath. """
    # check syncpath is flagged for a specific hostname or deleted
    _syncpath, syncflag = utils.get_syncflag(syncpath)
    if syncflag is not None and syncflag != HOSTNAME:
        return rmlink.remove_syncpath(syncpath, home, linkroot, dryrun)
    # check the homepath file or dir already exists and delete it
    # TODO: we should prompt before deleting anything here
    # WARNING: Do not put homepath before syncpath in the below code!
    homepath = _syncpath.replace(linkroot, home)
    syncpath = os.readlink(syncpath) if os.path.islink(syncpath) else syncpath
    if os.path.exists(homepath) or os.path.islink(homepath):
        if os.path.islink(homepath) and os.readlink(homepath) == syncpath:
            log.info(f'Existing link: {homepath}')
            return
        log.debug(f'Deleting: {homepath}')
        if (os.path.isfile(homepath) or os.path.islink(homepath)) and not dryrun:
            os.remove(homepath)
        elif os.path.isdir(homepath) and not dryrun:
            shutil.rmtree(homepath)
    # make sure home dirs exiist and create the new symlink
    log.info(f'Syncing: {homepath} -> {syncpath}')
    if not dryrun:
        os.makedirs(os.path.dirname(homepath), exist_ok=True)
        os.symlink(syncpath, homepath)


def run_command(opts):
    """ Symlink synced files and dirs to home directory. """
    for ftype, syncpath in utils.iter_linkroot(opts.linkroot):
        create_symlink(syncpath, opts.home, opts.linkroot, opts.dryrun)
