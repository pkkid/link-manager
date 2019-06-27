# encoding: utf-8
import os
from linkmanager import LINKROOT
from linkmanager import utils

DRYRUN_CHOICES = ['true', 'false']
LOGLEVEL_CHOICES = ['DEBUG', 'INFO', 'ERROR']


def get_options(parser):
    """ Command line options for setconfig. """
    options = parser.add_parser('setconfig', help=f'save a new configuration value')
    options.add_argument('name', help='name of the config to be set')
    options.add_argument('value', help='value of the config to be set')
    return options


def run_command(opts):
    """ Save a new configuration value. """
    # dryrun
    if opts.name.lower() == 'dryrun':
        dryrun = opts.value.lower()
        if dryrun in DRYRUN_CHOICES:
            dryrun = True if opts.value.lower() == 'true' else False
            utils.save_config('dryrun', dryrun)
    # linkroot
    if opts.name.lower() == 'linkroot':
        linkroot = opts.value.rstrip('/')
        utils.validate_linkroot(linkroot)
        open(os.path.join(linkroot, LINKROOT), 'a').close()
        utils.save_config('linkroot', linkroot)
    # loglevel
    if opts.name.lower() == 'loglevel':
        loglevel = opts.value.upper()
        if loglevel in LOGLEVEL_CHOICES:
            utils.save_config('loglevel', loglevel)
