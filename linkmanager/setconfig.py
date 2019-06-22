# encoding: utf-8
import os
from linkmanager import LINKROOT
from linkmanager import utils


def get_options(parser):
    """ Command line options for setconfig. """
    options = parser.add_parser('setconfig', help=f'save a new configuration value')
    options.add_argument('--linkroot', help='path to your synced linkroot directory')
    return options


def run_command(opts):
    """ Save a new configuration value. """
    if opts.linkroot:
        linkroot = opts.linkroot.rstrip('/')                 # remove trailing slash
        utils.validate_linkroot(linkroot)                    # validate the specified path
        open(os.path.join(linkroot, LINKROOT), 'a').close()  # touch the linkroot/LINKROOT file
        utils.save_config('linkroot', linkroot)              # save the configuration
