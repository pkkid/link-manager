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


def _add_global_options(command):
    """ Global command line options. """
    command.add_argument('--home', default=HOME, help='set home to a dir other than $HOME')
    command.add_argument('--linkroot', help='set the the linkroot directory')
    command.add_argument('--dryrun', action='store_true', default=False, help='dryrun, do not perform any actions')
    command.add_argument('--loglevel', default='INFO', help='sets the python log level')


if __name__ == '__main__':
    # Build the command line arguments
    parser = argparse.ArgumentParser(description='Manage links in shared directory.')
    commands = parser.add_subparsers(dest='command')
    for module in MODULES:
        command = module.get_options(commands)
        _add_global_options(command)
    # Read options and configuration
    opts = utils.Bunch(utils.get_config())
    opts.update(vars(parser.parse_args()))
    log.setLevel(opts.loglevel)
    # Run the specified command
    utils.validate_linkroot(opts.linkroot)
    callback = globals().get(opts.command).run_command(opts)
