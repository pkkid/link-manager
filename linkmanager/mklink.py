# encoding: utf-8
import os, shutil
from linkmanager import LINKROOT, LINKDIR
from linkmanager import utils
from linkmanager import cplinks
cyan = utils.cyan


def get_options(parser):
    """ Command line options for mklink. """
    options = parser.add_parser('mklink', help=f'create a new entry in {LINKROOT} to sync')
    options.add_argument('paths', nargs='+', help='path to file or directory to be created')
    return options


def run_command(opts):
    """ Create a new entry in linkroot to sync. """
    homepaths = utils.validate_paths(opts.paths, opts.home, opts.linkroot)
    for homepath in homepaths:
        syncpath = homepath.replace(opts.home, opts.linkroot)
        # If syncpath already exists, break out early.
        # TODO: We should prompt to overwrite here.
        if utils.exists(syncpath):
            print(f'Destination already exists {syncpath}')
            continue
        # Copy homepath to the linkroot
        ftype = utils.get_ftype(homepath)
        print(f'Copying {ftype} {cyan(homepath)} to {cyan(syncpath)}')
        if not opts.dryrun:
            os.makedirs(os.path.dirname(syncpath), exist_ok=True)
            if utils.is_link(homepath):
                os.symlink(os.readlink(homepath), syncpath)
            elif utils.is_file(homepath):
                shutil.copyfile(homepath, syncpath)
            elif utils.is_dir(homepath):
                shutil.copytree(homepath, syncpath)
                open(os.path.join(syncpath, LINKDIR), 'a').close()
        # Create the symlink
        cplinks.create_symlink(syncpath, opts.home, opts.linkroot, opts.dryrun, force='yes')
