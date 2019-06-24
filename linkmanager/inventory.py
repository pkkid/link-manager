# encoding: utf-8
import os
from linkmanager import HOME
from linkmanager import log, utils
_ = utils.short_home


def get_options(parser):
    """ Command line options for inventory. """
    options = parser.add_parser('inventory', help='list the inventory of links in LINKROOT')
    return options


def run_command(opts):
    """ List the inventory of links in LINKROOT. """
    for ftype, syncpath in utils.iter_linkroot(opts.linkroot):
        ftype = 'link' if os.path.islink(syncpath) else ftype
        fsize = utils.safe_fsize(syncpath)
        syncpath = syncpath.replace(opts.linkroot, HOME)
        log.info(f' {ftype:5}  {fsize:6}  {_(syncpath)}')
