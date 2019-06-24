# encoding: utf-8
import os, shutil
from linkmanager import HOME, LINKROOT, LINKDIR
from linkmanager import log, utils
from linkmanager import cplinks, purge
_ = utils.short_home


def get_options(parser):
    """ Command line options for mklink. """
    options = parser.add_parser('mklink', help=f'create a new entry in {LINKROOT} to sync')
    options.add_argument('paths', nargs='+', help='path to file or directory to be created')
    return options


def run_command(opts):
    """ Create a new entry in linkroot to sync. """
    homepaths = utils.validate_paths(opts.paths, opts.linkroot)
    for homepath in homepaths:
        syncpath = homepath.replace(HOME, opts.linkroot)
        if os.path.exists(syncpath):
            log.info(f'Link already exists {_(syncpath)}')
        elif os.path.isfile(homepath):
            log.info(f'Copying file {_(homepath)} to {_(syncpath)}')
            os.makedirs(os.path.dirname(syncpath), exist_ok=True)
            shutil.copyfile(homepath, syncpath)
        elif os.path.isdir(homepath):
            log.info(f'Copying dir {_(homepath)} to {_(syncpath)}')
            shutil.copytree(homepath, syncpath)
            open(os.path.join(syncpath, LINKDIR), 'a').close()
        # Make sure there is no deleted entry in linkroot and
        # run cplink against this syncpath
        purge.purge_syncpath(syncpath)
        cplinks.create_symlink(syncpath, opts.linkroot, opts.dryrun)
