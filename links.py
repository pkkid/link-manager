#!/usr/bin/env python3
# encoding: utf-8
import argparse, json, os, shutil

HOME = os.path.expanduser('~')
CONFIG = os.path.join(HOME, '.config/linkmanager.json')
IGNORES = ['LINKROOT', 'README', '*_Conflict*']
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


def _validate_linkroot(linkroot):
    """ Check the specified linkroot is valid and save it to the config. """
    if not os.path.isdir(linkroot):
        raise SystemExit(f'The specified linkroot does not exist: {linkroot}')
    if not os.listdir(linkroot):
        return _save_config('linkroot', linkroot)
    if not os.path.isfile(os.path.join(linkroot, 'LINKROOT')):
        raise SystemExit(f'The specified path does not appear to be a valid linkroot: {linkroot}'
            '\nIf you are sure this is the valid linkroot path, you can specify so by creating a'
            '\nfile in the directory named LINKROOT. BEWARE: If you specify the wrong path, bad'
            '\nthings can happen.')
    return _save_config('linkroot', linkroot)


def mklink(opts, config):
    """ Create a new entry in LINKROOT to sync. """
    dest = opts.path.replace(HOME, config.linkroot)
    if os.path.exists(dest):
        print(f'Link already exists {_(dest)}')
    elif os.path.isfile(opts.path):
        print(f'Copying File {_(opts.path)} to {_(dest)}')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(opts.path, dest)
    elif os.path.isdir(opts.path):
        print(f'Copying Dir {_(opts.path)} to {_(dest)}')
        shutil.copytree(opts.path, dest)
        open(os.path.join(dest, 'LINKDIR'), 'a').close()
    cplinks(opts, config)


def cplinks(opts, config):
    """ Symlink synced files and dirs to home directory. """
    pass


def rmlink(opts, config):
    """ Remove an entry from LINKROOT. """
    pass


if __name__ == '__main__':
    # Command line arguments
    parser = argparse.ArgumentParser(description='Manage links in shared directory.')
    parser.set_defaults(callback=None)
    parser.add_argument('--root', required=False, help='Path to ROOT (will be saved to config)')
    commands = parser.add_subparsers(help='command help')
    commands_mklink = commands.add_parser('mklink', help='Create a new entry in LINKROOT to sync.')
    commands_mklink.set_defaults(callback=mklink)
    commands_mklink.add_argument('path', nargs='+', help='Path to file or directory to be created.')
    commands_cplinks = commands.add_parser('cplinks', help='Symlink synced files and dirs to home directory.')
    commands_mklink.set_defaults(callback=cplinks)
    commands_rmlink = commands.add_parser('rmlink')
    commands_rmlink.add_argument('path', nargs='+', help='Remove an entry from LINKROOT.')
    commands_rmlink.set_defaults(callback=rmlink)
    # Perform specified tasks
    opts = parser.parse_args()
    config = _validate_linkroot(opts.root) if opts.root else _get_config()
    if not config.linkroot:
        raise SystemExit('No ROOT specified, please run: links.py --root=<ROOT>')
    if opts.callback:
        opts.callback(opts, config)



# def _ignored(filepath):
#     """ Return true if filepath matches an ignore pattern. """
#     path = filepath.replace(LINKS, '').lstrip('/')
#     for ignore in IGNORES:
#         if fnmatch.fnmatch(path, ignore):
#             return True
#     return False


# def create_symlink(filepath, dryrun=False, verbose=False):
#     """ Create the specified symlink. """
#     # Get the source and destination paths
#     if os.path.islink(filepath):
#         source = filepath.replace(LINKS, HOME)
#         filepath = os.readlink(filepath)
#     elif os.path.isfile(filepath):
#         source = filepath.replace(LINKS, HOME)
#     elif os.path.isdir(filepath):
#         source = filepath.replace(LINKS, HOME)
#     # Check the source file or directory already exists and delete it
#     ftype = 'Dir' if os.path.isdir(source) else 'File'
#     if os.path.exists(source) or os.path.islink(source):
#         if os.path.islink(source) and os.readlink(source) == filepath:
#             if verbose:
#                 print(f'Completed {ftype}: {_(source)}')
#             return None
#         print(f'Deleting {ftype}: {_(source)}')
#         if (os.path.isfile(source) or os.path.islink(source)) and not dryrun:
#             os.remove(source)
#         elif os.path.isdir(source) and not dryrun:
#             shutil.rmtree(source)
#     # Create the new symlink!
#     print(f'Creating {ftype}: {_(source)}')
#     if not dryrun:
#         os.makedirs(os.path.dirname(source), exist_ok=True)
#         os.symlink(filepath, source)


# def copy_links(dirpath, dryrun=False, verbose=False):
#     for filename in os.listdir(dirpath):
#         filepath = os.path.join(dirpath, filename)
#         if not _ignored(filepath):
#             if os.path.islink(filepath) or os.path.isfile(filepath):
#                 create_symlink(filepath, dryrun, verbose)
#                 continue
#             if os.path.exists(os.path.join(filepath, 'LINKDIR')):
#                 create_symlink(filepath, dryrun, verbose)
#                 continue
#             if os.path.isdir(filepath):
#                 copy_links(filepath, dryrun, verbose)

# ----------------------

# def _safe_unlink(path):
#     try:
#         os.unlink(path)
#     except Exception:
#         pass


# def rmlink(path):
#     """ Create file in LINKS to be linked in place. """
#     source = path.replace(cplinks.HOME, cplinks.LINKS)
#     if not os.path.exists(source):
#         print(f'Link does not exist {_(source)}')
#     elif os.path.islink(path) and os.path.isfile(path):
#         print(f'Unlinking File {_(path)}')
#         _safe_unlink(path)
#         os.rename(source, path)
#     elif os.path.islink(path) and os.path.isdir(path):
#         print(f'Unlinking Dir {_(path)}')
#         _safe_unlink(path)
#         shutil.move(source, path)
#         _safe_unlink(os.path.join(path, 'LINKDIR'))
