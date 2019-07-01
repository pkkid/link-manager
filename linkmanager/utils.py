# encoding: utf-8
import fnmatch, json, os
import re, subprocess
from shlex import split
from linkmanager import FILE, DIR, LINK, CONFIG
from linkmanager import HOME, LINKROOT, LINKDIR

try:
    from termcolor import colored, cprint
except ImportError:
    colored = lambda msg, color: msg
    cprint = lambda msg, color: print(msg)

cyan = lambda msg: colored(msg, 'cyan')
BYTES = ((2**30,'G'), (2**20,'M'), (2**10,'K'), (1,''))
HOSTNAME_REGEX = r'^(.+?)\[([\w\-]+?)\]$'
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


def exists(path):
    """ Return true if the path exists as a file, dir, link, or broken link. """
    return os.path.exists(path) or os.path.islink(path)


def find_linkroot(maxdepth=3):
    """ Attempt to find linkroot in the homr directory. """
    # I suppose I could have written this in Python, but I assume calling find
    # here is probably a much faster implementation that I would come up with
    result = subprocess.check_output(split(f'find {HOME} -maxdepth {maxdepth} -name {LINKROOT}'))
    if result:
        linkroot = os.path.dirname(result.decode('utf8').strip())
        print('Linkroot is not specified in your configuration.')
        question = f'Would you like to set it to {cyan(linkroot)}? [y/n]'
        response = get_input(None, question, choices=['y','n'])
        if response == 'y':
            save_config('linkroot', linkroot)
            return linkroot
    return None


def get_config():
    """ Read and return all the configuration object. """
    try:
        with open(CONFIG) as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {}


def get_syncflag(syncpath):
    """ Return the flag portion of a syncpath file. For example, if the syncpath filename
        is "hello-world.py[flag]", the return value of this function will be a tuple
        containing (homepath, syncflag).
    """
    matches = re.findall(HOSTNAME_REGEX, syncpath)
    if len(matches) == 1:
        syncpath, syncflag = matches[0]
        return syncpath, syncflag
    return syncpath, None


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


def get_ftype(path):
    """ Return file, dir, or link. """
    if is_link(path): return LINK
    if is_file(path): return FILE
    if is_dir(path): return DIR


def get_input(result, msg, default=None, choices=None):
    msg = '%s [%s]: ' % (msg, default) if default else '%s: ' % msg
    while choices and result not in choices:
        result = input(msg) or default
    if choices is None or '' not in choices:
        while not result:
            result = input(msg) or default
    return result


def is_broken_link(path):
    """ Return true if path is a link and the path is broken. """
    if is_link(path):
        linkpath = os.readlink(path)
        if not os.path.exists(linkpath):
            return True
    return False


def is_dir(path):
    """ Return true if dir is a file and not a link. """
    return os.path.isdir(path) and not os.path.islink(path)


def is_file(path):
    """ Return true if path is a file and not a link. """
    return os.path.isfile(path) and not os.path.islink(path)


def is_link(path):
    """ Return true if the path is a link. """
    return os.path.islink(path)


def is_ignored(filepath):
    """ Return true if filepath matches an ignore pattern. """
    filename = os.path.basename(filepath)
    for ignore in IGNORES:
        if fnmatch.fnmatch(filename, ignore):
            return True
    return False


def is_working_link(filepath):
    """ Return true if the filepath is a link and not broken. """
    if os.path.islink(filepath):
        linkpath = os.readlink(filepath)
        if os.path.exists(linkpath):
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


def linkpath(filepath):
    """ Return the linkpath of the specified link. """
    if os.path.islink(filepath):
        return os.readlink(filepath)
    return None


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
    print(f'Saving configuration value {key}={value} to {CONFIG}')
    config = get_config()
    config.update({key:value})
    with open(CONFIG, 'w') as handle:
        json.dump(config, handle)
    return config


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
    if not linkroot:
        linkroot = find_linkroot()
        if not linkroot:
            msg = 'You must specify a linkroot directory in order to use these tools.'
            msg += '\nYou can configure this setting by running the following command:'
            msg += cyan('\n> links.py setconfig linkroot <LINKROOT>')
            raise SystemExit(msg)
    linkroot = linkroot.rstrip('/')
    if not os.path.isdir(linkroot):
        raise SystemExit(f'The specified linkroot does not exist: {cyan(linkroot)}')
    if not os.path.isfile(os.path.join(linkroot, LINKROOT)):
        msg = f'The specified path does not appear to be a valid linkroot: {cyan(linkroot)}'
        msg += '\nIf you are sure this is the valid linkroot path, you can specify so by creating a file in'
        msg += '\nthe directory named LINKROOT. BEWARE: Bad things can happen if you specify the wrong path.'
        raise SystemExit(msg)
    return linkroot


def validate_paths(paths, home, linkroot):
    """ Validate the specified paths are appropriate. """
    paths = [os.path.abspath(path) for path in paths]
    for path in paths:
        if not exists(path):
            raise SystemExit(f'The specified path does not exist: {cyan(path)}')
        if not path.startswith(home):
            raise SystemExit(f'Specified path must exist in your home directory.')
        if path.startswith(linkroot):
            raise SystemExit(f'Specified path must not be in the LINKROOT directory.')
    return paths
