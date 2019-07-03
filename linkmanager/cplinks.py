# encoding: utf-8
import os, shutil
from linkmanager import HOSTNAME
from linkmanager import log, utils, rmlink
cyan = utils.cyan


def get_options(parser):
    """ Command line options for cplinks. """
    options = parser.add_parser('cplinks', help='symlink synced files and dirs to home directory')
    return options


def _promt_to_overwrite(homepath, dryrun=False, force=None):
    """ Remove the specified mfile, dir or link. Prompt the user before deleting
        anything if the file is not a broken link.
    """
    if not utils.exists(homepath):
        return None
    if utils.is_broken_link(homepath):
        return os.remove(homepath)
    ftype = utils.get_ftype(homepath)
    if not dryrun and force not in 'yesno':
        question = f'Would you like overwrite {ftype} {cyan(homepath)}? [y/n]'
        response = utils.get_input(None, question, choices=['y','n'])
    if dryrun or force == 'yes' or (force is None and response == 'y'):
        log.info(f'Deleting {ftype} {cyan(homepath)}')
        if (utils.is_file(homepath) or utils.is_link(homepath)) and not dryrun:
            os.remove(homepath)
        elif utils.is_dir(homepath) and not dryrun:
            shutil.rmtree(homepath)


def create_symlink(syncpath, home, linkroot, dryrun=False, force=None):
    """ Create a symlink for the specified syncpath. Rules to creating a symlink..
        1. If syncflag is set and not equal to pcname, remove the syncpath.
        2. If homepath is already a link pointing to the correct file, return.
        3. Prompt to remove the homepath if it exists.
        4. Create the symlink!
    """
    # If syncflag is set and not equal to pcname, remove the syncpath.
    _syncpath, syncflag = utils.get_syncflag(syncpath)
    if syncflag is not None and syncflag != HOSTNAME:
        return rmlink.remove_syncpath(syncpath, home, linkroot, dryrun)
    # If the homepath exists and is a broken link, delete it.
    homepath = _syncpath.replace(linkroot, home)
    syncpath = os.readlink(syncpath) if os.path.islink(syncpath) else syncpath
    if utils.linkpath(homepath) == syncpath:
        log.debug(f'Syncing already setup for {cyan(homepath)}')
        return
    # Prompt to remove the homepath if it exists.
    _promt_to_overwrite(homepath, dryrun, force)
    # Create the symlink!
    if not utils.exists(homepath):
        log.info(f'Syncing {cyan(homepath)} -> {cyan(syncpath)}')
        if not dryrun:
            os.makedirs(os.path.dirname(homepath), exist_ok=True)
            os.symlink(syncpath, homepath)


def run_command(opts):
    """ Symlink synced files and dirs to home directory. """
    for ftype, syncpath in utils.iter_linkroot(opts.linkroot):
        create_symlink(syncpath, opts.home, opts.linkroot, opts.dryrun, opts.force)
