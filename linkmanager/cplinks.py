# encoding: utf-8
import os, shutil
from linkmanager import log, utils
from linkmanager import rmlink


def get_options(parser):
    """ Command line options for cplinks. """
    options = parser.add_parser('cplinks', help='symlink synced files and dirs to home directory')
    return options


def create_symlink(syncpath, home, linkroot, dryrun=False):
    """ Create a symlink for the specified syncpath. """
    homepath = syncpath.replace(linkroot, home)
    # if syncpath is a link, resolve its destination
    if os.path.islink(syncpath):
        syncpath = os.readlink(syncpath)
    # check the homepath file or dir already exists and delete it
    # TODO: we should prompt before deleting anything here
    if os.path.exists(homepath) or os.path.islink(homepath):
        if os.path.islink(homepath) and os.readlink(homepath) == syncpath:
            log.debug(f'Existing link: {homepath}')
            return
        log.info(f'Deleting: {homepath}')
        if (os.path.isfile(homepath) or os.path.islink(homepath)) and not dryrun:
            os.remove(homepath)
        elif os.path.isdir(homepath) and not dryrun:
            shutil.rmtree(homepath)
    # make sure home dirs exiist and create the new symlink
    log.info(f'Syncing: {homepath}')
    if not dryrun:
        os.makedirs(os.path.dirname(homepath), exist_ok=True)
        os.symlink(syncpath, homepath)


def run_command(opts):
    """ Symlink synced files and dirs to home directory. """
    for ftype, syncpath in utils.iter_linkroot(opts.linkroot):
        if utils.is_deleted(syncpath):
            rmlink.remove_syncpath(syncpath, opts.linkroot, opts.dryrun)
            continue
        create_symlink(syncpath, opts.home, opts.linkroot, opts.dryrun)
