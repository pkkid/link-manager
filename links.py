#!/usr/bin/env python3
# encoding: utf-8
import argparse, os, sys

# Add linkmanager to sys.path if not already there. Useful when
# running this application without officially installing it.
projectroot = os.path.dirname(__file__)
if projectroot not in sys.path:
    sys.path.append(projectroot)

from linkmanager import HOME  # noqa
from linkmanager import setconfig, inventory  # noqa
from linkmanager import mklink, cplinks, rmlink, purge  # noqa
from linkmanager import log, utils  # noqa

MODULES = [setconfig, inventory, mklink, cplinks, rmlink, purge]
OPTIONS = utils.Bunch(utils.get_config())


def _add_global_options(command):
    """ Global command line options. """
    command.add_argument('--home', default=HOME, help=f'set home to a dir other than $HOME (default: {HOME})')  # noqa
    command.add_argument('--linkroot', default=OPTIONS.get('linkroot'), help='set the the linkroot directory')  # noqa
    command.add_argument('--dryrun', default=OPTIONS.get('dryrun', False), action='store_true', help='dryrun, do not perform any actions')  # noqa
    command.add_argument('--loglevel',default=OPTIONS.get('loglevel', 'INFO'), help='sets the python log level')  # noqa


if __name__ == '__main__':
    # Build the command line arguments
    parser = argparse.ArgumentParser(description='Manage links in shared directory.')
    commands = parser.add_subparsers(dest='command')
    for module in MODULES:
        command = module.get_options(commands)
        _add_global_options(command)
    # Read options and configuration
    opts = utils.Bunch(vars(parser.parse_args()))
    log.setLevel(opts.loglevel)
    # Run the specified command
    opts.linkroot = utils.validate_linkroot(opts.linkroot)
    callback = globals().get(opts.command).run_command(opts)
