# encoding: utf-8
import os
from linkmanager import LINKROOT
from linkmanager import utils

DRYRUN_CHOICES = [True, False]
FORCE_CHOICES = ['yes', 'no']
LOGLEVEL_CHOICES = ['debug', 'info', 'error']


def get_options(parser):
    """ Command line options for setconfig. """
    options = parser.add_parser('setconfig', help='save a new configuration value')
    options.add_argument('name', help='name of the config to be set')
    options.add_argument('value', help='value of the config to be set')
    return options


def save_config(name, value, choices=None, cast=None):
    """ Save the specified value if it matches one of the choices. """
    value = cast(value) if cast else value
    if not choices or value in choices:
        return utils.save_config('name', value)
    raise SystemExit(f'Error saving {name}: Unknown value {value}')


def _bool(value): return True if value.lower() == 'true' else False  # noqa
def _lower(value): return value.lower()  # noqa


def _linkroot(value):
    linkroot = value.rstrip('/')
    utils.validate_linkroot(linkroot)
    open(os.path.join(linkroot, LINKROOT), 'a').close()
    return linkroot


def run_command(opts):
    """ Save a new configuration value. """
    name, value = opts.name.lower(), opts.value
    if name == 'dryrun':
        save_config('dryrun', value, DRYRUN_CHOICES, _bool)
    if name == 'force':
        save_config('force', value, FORCE_CHOICES, _lower)
    if name == 'linkroot':
        save_config('linkroot', value, None, _linkroot)
    if name == 'loglevel':
        save_config('loglevel', value, LOGLEVEL_CHOICES, _lower)
