# encoding: utf-8
import os, shutil
from linkmanager import HOME
from linkmanager import log, utils
_ = utils.short_home


def get_options(parser):
    """ Command line options for cplinks. """
    options = parser.add_parser('cplinks', help='symlink synced files and dirs to home directory')
    return options


def run_command(opts):
    """ Symlink synced files and dirs to home directory. """
    for ftype, filepath in utils.iter_linkroot(opts.linkroot):
        # Get the source and destination paths
        if os.path.islink(filepath):
            source = filepath.replace(opts.linkroot, HOME)
            filepath = os.readlink(filepath)
        elif os.path.isfile(filepath):
            source = filepath.replace(opts.linkroot, HOME)
        elif os.path.isdir(filepath):
            source = filepath.replace(opts.linkroot, HOME)
        # Check the source file or directory already exists and delete it
        if os.path.exists(source) or os.path.islink(source):
            if os.path.islink(source) and os.readlink(source) == filepath:
                log.debug(f'Existing {ftype}: {_(source)}')
                continue
            log.info(f'Deleting {ftype}: {_(source)}')
            if (os.path.isfile(source) or os.path.islink(source)) and not opts.dryrun:
                os.remove(source)
            elif os.path.isdir(source) and not opts.dryrun:
                shutil.rmtree(source)
        # Create the new symlink!
        log.info(f'Creating {ftype}: {_(source)}')
        if not opts.dryrun:
            os.makedirs(os.path.dirname(source), exist_ok=True)
            os.symlink(filepath, source)
