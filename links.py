#!/usr/bin/env python3
# encoding: utf-8
import json, os, shutil, sys
import argparse, fnmatch, logging

log = logging.getLogger('linkmanager')
streamhandler = logging.StreamHandler(sys.stdout)
streamhandler.setFormatter(logging.Formatter('%(message)s'))
log.addHandler(streamhandler)

FILE, DIR = 'file', 'dir'
LINKROOT, LINKDIR = 'LINKROOT', 'LINKDIR'
BYTES = ((2**30,'G'), (2**20,'M'), (2**10,'K'), (1,''))
HOME = os.path.expanduser('~')
CONFIG = os.path.join(HOME, '.config/linkmanager.json')
IGNORES = [
    'LINKROOT',             # LINKROOT flag
    '*_Conflict*',          # Synology conflict file
    '*conflicted copy*'     # Dropbox conflict file
    '*[Conflict]*'          # Google Drive conflict file
]
_ = lambda path: path.replace(HOME, '~')


class Bunch(dict):
    def __getattr__(self, item): return self.__getitem__(item)  # noqa
    def __setattr__(self, item, value): return self.__setitem__(item, value)  # noqa


def _get_config():
    """ Read and return all the configuration object. """
    try:
        with open(CONFIG) as handle:
            return Bunch(json.load(handle))
    except FileNotFoundError:
        return Bunch()


def _save_config(key, value):
    """ Save a new configuration option. """
    config = _get_config()
    config.update({key:value})
    with open(CONFIG, 'w') as handle:
        json.dump(config, handle)
    return config


def _get_fsize(path):
    """ Return size of directory or file as an integer. """
    total = 0
    if os.path.isfile(path) or os.path.islink(path):
        return os.path.getsize(path)
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += _get_fsize(entry.path)
    return total


def _ignored(filepath):
    """ Return true if filepath matches an ignore pattern. """
    filename = os.path.basename(filepath)
    for ignore in IGNORES:
        if fnmatch.fnmatch(filename, ignore):
            return True
    return False


def _iter_linkroot(linkroot):
    """ Iterate all items in linkroot. """
    for filename in sorted(os.listdir(linkroot)):
        filepath = os.path.join(linkroot, filename)
        if not _ignored(filepath):
            if os.path.islink(filepath) or os.path.isfile(filepath):
                yield FILE, filepath
            elif os.path.exists(os.path.join(filepath, LINKDIR)):
                yield DIR, filepath
            elif os.path.isdir(filepath):
                for item in _iter_linkroot(filepath):
                    yield item


def _safe_fsize(path):
    """ Safely get the filesize of a directory or file. """
    try:
        fsize = _get_fsize(path)
        return _value_to_str(fsize, 1).replace('.0', '')
    except FileNotFoundError:
        return 'Error'


def _safe_unlink(path):
    """ Safley delete a file. """
    try:
        os.unlink(path)
    except Exception:
        pass


def _value_to_str(value, places=0):
    """ Pretty print the specified value. """
    if not isinstance(value, (int, float)):
        return value or ''
    for div, unit in BYTES:
        if value >= div:
            conversion = round(value/div, int(places)) if places else int(value/div)
            return f'{conversion}{unit}'
    return f'0{unit}'


def _validate_linkroot(linkroot):
    """ Check the specified linkroot is valid and save it to the config. """
    if not os.path.isdir(linkroot):
        raise SystemExit(f'The specified linkroot does not exist: {linkroot}')
    if not os.listdir(linkroot):
        open(os.path.join(linkroot, LINKROOT), 'a').close()
        return _save_config('linkroot', linkroot)
    if not os.path.isfile(os.path.join(linkroot, LINKROOT)):
        raise SystemExit(f'The specified path does not appear to be a valid linkroot: {linkroot}'
            '\nIf you are sure this is the valid linkroot path, you can specify so by creating a'
            '\nfile in the directory named LINKROOT. BEWARE: If you specify the wrong path, bad'
            '\nthings can happen.')
    return _save_config('linkroot', linkroot.rstrip('/'))


def _validate_paths(paths, linkroot):
    """ Validate the specified path is appropriate. """
    for path in paths:
        if not os.path.exists(path):
            raise SystemExit(f'The specified path does not exist: {path}')
        if not path.startswith(HOME):
            raise SystemExit(f'Specified path must exist in your home directory.')
        if path.startswith(linkroot):
            raise SystemExit(f'Specified path must not be in the LINKROOT directory.')


def mklink(opts):
    """ Create a new entry in LINKROOT to sync. """
    _validate_paths(opts.paths, opts.linkroot)
    for path in opts.paths:
        dest = path.replace(HOME, opts.linkroot)
        if os.path.exists(dest):
            log.info(f'Link already exists {_(dest)}')
        elif os.path.isfile(path):
            log.info(f'Copying File {_(path)} to {_(dest)}')
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(path, dest)
        elif os.path.isdir(path):
            log.info(f'Copying Dir {_(path)} to {_(dest)}')
            shutil.copytree(path, dest)
            open(os.path.join(dest, LINKDIR), 'a').close()
    cplinks(opts)


def cplinks(opts):
    """ Symlink synced files and dirs to home directory. """
    for ftype, filepath in _iter_linkroot(opts.linkroot):
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


def rmlink(opts):
    """ Remove an entry from LINKROOT. """
    _validate_paths(opts.paths, opts.linkroot)
    for path in opts.paths:
        source = path.replace(HOME, opts.linkroot)
        if not os.path.exists(source):
            log.info(f'Link does not exist {_(source)}')
        elif os.path.islink(path) and os.path.isfile(path):
            log.info(f'Unlinking File {_(path)}')
            if not opts.dryrun:
                _safe_unlink(path)
                os.rename(source, path)
        elif os.path.islink(path) and os.path.isdir(path):
            log.info(f'Unlinking Dir {_(path)}')
            if not opts.dryrun:
                _safe_unlink(path)
                shutil.move(source, path)
                _safe_unlink(os.path.join(path, LINKDIR))


def inventory(opts):
    """ List the inventory of links in LINKROOT. """
    for ftype, filepath in _iter_linkroot(opts.linkroot):
        fsize = _safe_fsize(filepath)
        filepath = filepath.replace(opts.linkroot, HOME)
        log.info(f' {ftype:5}  {fsize:6}  {_(filepath)}')


if __name__ == '__main__':
    # Command line arguments
    parser = argparse.ArgumentParser(description='Manage links in shared directory.')
    parser.set_defaults(callback=None)
    parser.add_argument('--root', required=False, help=f'path to {LINKROOT} (will be saved to config)')
    parser.add_argument('--dryrun', action='store_true', default=False, help=f'dryrun, do not perform any actions')
    parser.add_argument('--loglevel', default='INFO', help=f'sets the python log level')
    commands = parser.add_subparsers(dest='command', required=True)
    commands_mklink = commands.add_parser('mklink', help=f'create a new entry in {LINKROOT} to sync')
    commands_mklink.add_argument('paths', nargs='+', help='path to file or directory to be created')
    commands_cplinks = commands.add_parser('cplinks', help='symlink synced files and dirs to home directory')
    commands_rmlink = commands.add_parser('rmlink', help=f'remove an entry from {LINKROOT}')
    commands_rmlink.add_argument('paths', nargs='+', help='path to file or directory to be removed')
    commands_inventory = commands.add_parser('inventory', help='list the inventory of links in LINKROOT')
    # Perform specified tasks
    opts = Bunch(vars(parser.parse_args()))
    log.setLevel(opts.loglevel)
    opts.update(_validate_linkroot(opts.root) if opts.root else _get_config())
    if not opts.linkroot:
        raise SystemExit('No ROOT specified, please run: links.py --root=<ROOT>')
    callback = globals().get(opts.command)
    if callback:
        callback(opts)
