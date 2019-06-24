# encoding: utf-8
import fnmatch, json, os
from linkmanager import FILE, DIR
from linkmanager import HOME, CONFIG
from linkmanager import LINKROOT, LINKDIR
from linkmanager import log

BYTES = ((2**30,'G'), (2**20,'M'), (2**10,'K'), (1,''))
DELETED = '[DELETED]'
IGNORES = [
    'LINKROOT',             # LINKROOT flag
    '*_Conflict*',          # Synology conflict file
    '*conflicted copy*'     # Dropbox conflict file
    '*[Conflict]*'          # Google Drive conflict file
]


class Bunch(dict):
    def __getattr__(self, item):
        return self.__getitem__(item)

    def __setattr__(self, item, value):
        return self.__setitem__(item, value)


def get_config():
    """ Read and return all the configuration object. """
    try:
        with open(CONFIG) as handle:
            return Bunch(json.load(handle))
    except FileNotFoundError:
        return Bunch()


def get_fsize(path):
    """ Return size of directory or file as an integer. """
    total = 0
    if os.path.isfile(path) or os.path.islink(path):
        return os.path.getsize(path)
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_fsize(entry.path)
    return total


def is_deleted(filepath):
    """ Return True iof the filepath has been deleted. """
    return filepath.endswith(DELETED)


def is_ignored(filepath):
    """ Return true if filepath matches an ignore pattern. """
    filename = os.path.basename(filepath)
    for ignore in IGNORES:
        if fnmatch.fnmatch(filename, ignore):
            return True
    return False


def iter_linkroot(linkroot):
    """ Iterate all items in linkroot. """
    for filename in sorted(os.listdir(linkroot)):
        filepath = os.path.join(linkroot, filename)
        if not is_ignored(filepath):
            if os.path.islink(filepath) or os.path.isfile(filepath):
                yield FILE, filepath
            elif os.path.exists(os.path.join(filepath, LINKDIR)):
                yield DIR, filepath
            elif os.path.isdir(filepath):
                for item in iter_linkroot(filepath):
                    yield item


def safe_fsize(path):
    """ Safely get the filesize of a directory or file. """
    try:
        fsize = get_fsize(path)
        return value_to_str(fsize, 1).replace('.0', '')
    except FileNotFoundError:
        return 'Error'


def safe_unlink(path):
    """ Safley delete a file. """
    try:
        os.unlink(path)
    except Exception:
        pass


def save_config(key, value):
    """ Save a new configuration option. """
    log.info(f'Saving configuration value {key}={value} to {CONFIG}')
    config = get_config()
    config.update({key:value})
    with open(CONFIG, 'w') as handle:
        json.dump(config, handle)
    return config


def short_home(path):
    """ replace /home/user with ~. """
    return path.replace(HOME, '~')


def value_to_str(value, places=0):
    """ Pretty print the specified value. """
    if not isinstance(value, (int, float)):
        return value or ''
    for div, unit in BYTES:
        if value >= div:
            conversion = round(value/div, int(places)) if places else int(value/div)
            return f'{conversion}{unit}'
    return f'0{unit}'


def validate_linkroot(linkroot):
    """ Check the specified linkroot is valid and save it to the config. """
    linkroot = linkroot.rstrip('/')
    if not linkroot:
        raise SystemExit('You must specify a linkroot directory in order to use these'
            '\ntools. You can configure this setting by running the following command:'
            '\n> links.py setconfig --linkroot=LINKROOT')
    if not os.path.isdir(linkroot):
        raise SystemExit(f'The specified linkroot does not exist: {linkroot}')
    if not os.path.isfile(os.path.join(linkroot, LINKROOT)):
        raise SystemExit(f'The specified path does not appear to be a valid linkroot: {linkroot}'
            '\nIf you are sure this is the valid linkroot path, you can specify so by creating a'
            '\nfile in the directory named LINKROOT. BEWARE: If you specify the wrong path, bad'
            '\nthings can happen.')
    return linkroot


def validate_paths(paths, linkroot):
    """ Validate the specified path is appropriate. """
    paths = [os.path.abspath(path) for path in paths]
    for path in paths:
        if not os.path.exists(path):
            raise SystemExit(f'The specified path does not exist: {path}')
        if not path.startswith(HOME):
            raise SystemExit(f'Specified path must exist in your home directory.')
        if path.startswith(linkroot):
            raise SystemExit(f'Specified path must not be in the LINKROOT directory.')
    return paths
