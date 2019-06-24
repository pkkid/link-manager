# encoding: utf-8
import os, shutil
from linkmanager import HOME
from linkmanager import log, utils
from linkmanager import rmlink
_ = utils.short_home


def get_options(parser):
    """ Command line options for cplinks. """
    options = parser.add_parser('cplinks', help='symlink synced files and dirs to home directory')
    return options


def create_symlink(syncpath, linkroot, dryrun=False):
    """ Create a symlink for the specified syncpath. """
    homepath = syncpath.replace(linkroot, HOME)
    # If syncpath is a link, resolve the new path
    if os.path.islink(syncpath):
        syncpath = os.readlink(syncpath)
    # Check the homepath file or directory already exists and delete it
    if os.path.exists(homepath) or os.path.islink(homepath):
        if os.path.islink(homepath) and os.readlink(homepath) == syncpath:
            return log.debug(f'Existing link: {_(homepath)}')
        log.info(f'Deleting: {_(homepath)}')
        if (os.path.isfile(homepath) or os.path.islink(homepath)) and not dryrun:
            os.remove(homepath)
        elif os.path.isdir(homepath) and not dryrun:
            shutil.rmtree(homepath)
    # Create the new symlink!
    log.info(f'Syncing: {_(homepath)}')
    if not dryrun:
        os.makedirs(os.path.dirname(homepath), exist_ok=True)
        os.symlink(syncpath, homepath)


def run_command(opts):
    """ Symlink synced files and dirs to home directory. """
    for ftype, syncpath in utils.iter_linkroot(opts.linkroot):
        if utils.is_deleted(syncpath):
            rmlink.remove_syncpath(syncpath, opts.linkroot, opts.dryrun)
            continue
        create_symlink(syncpath, opts.linkroot, opts.dryrun)
