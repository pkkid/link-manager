# encoding: utf-8
import os
from linkmanager import DELETED
from linkmanager import log, utils


def get_options(parser):
    """ Command line options for inventory. """
    options = parser.add_parser('purge', help='purge all deleted symlinks from LINKROOT')
    return options


def purge_syncpath(syncpath, dryrun=False):
    """ Purge the specified syncpath. """
    if not utils.is_deleted(syncpath):
        syncpath = f'{syncpath}{DELETED}'
    if os.path.exists(syncpath):
        log.info(f'Purging {syncpath}')
        if not dryrun:
            utils.safe_unlink(syncpath)
        return 1
    return 0


def run_command(opts):
    """ List the inventory of links in LINKROOT. """
    actions = 0
    for ftype, syncpath in utils.iter_linkroot(opts.linkroot):
        if utils.is_deleted(syncpath):
            actions += purge_syncpath(syncpath, opts.dryrun)
    return actions
