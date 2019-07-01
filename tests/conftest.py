# -*- coding: utf-8 -*-
import os, pytest, shutil
from linkmanager import utils
from collections import namedtuple

HOME = '/tmp/linkmanager/home'
SYNC = '/tmp/linkmanager/sync'
IGNORE = '.pytest_cache'
File = namedtuple('File', ['path', 'data'], defaults=[None])
Link = namedtuple('Link', ['path', 'to'])
cyan = utils.cyan


@pytest.fixture()
def opts():
    return utils.Bunch({
        'home': HOME,
        'linkroot': SYNC,
        'dryrun': False,
        'force': 'no'
    })


def data(filepath):
    """ Return the data of the specified file. """
    try:
        with open(filepath, 'r') as handle:
            return handle.read().strip()
    except Exception:
        return None


def clear_contents():
    """ Clear contents of the home and sync dirs. """
    rootdir = os.path.dirname(HOME)
    for path in os.listdir(rootdir):
        filepath = os.path.join(rootdir, path)
        if IGNORE in filepath: continue
        if os.path.isdir(filepath):
            shutil.rmtree(filepath, ignore_errors=True)
        elif os.path.isfile(filepath):
            os.unlink(filepath)
    os.makedirs(HOME, exist_ok=True)
    os.makedirs(SYNC, exist_ok=True)
    

def list_contents():
    """ List all contents in test directory. """
    for dirpath, dirnames, filenames in os.walk(os.path.dirname(HOME)):
        if IGNORE in dirpath: continue
        for dirname in sorted(dirnames):
            dirpath = os.path.join(dirpath, dirname)
            if utils.is_link(dirpath):
                print(f'link {cyan(dirpath)} -> {os.readlink(dirpath)}')
        for filename in sorted(filenames):
            filepath = os.path.join(dirpath, filename)
            if utils.is_link(filepath):
                print(f'link {cyan(filepath)} -> {os.readlink(filepath)}')
            elif utils.is_file(filepath):
                print(f'file {cyan(filepath)} :: {data(filepath)}')


def create(manifest):
    """ Create the specified manifest. """
    for item in manifest:
        os.makedirs(os.path.dirname(item.path), exist_ok=True)
        if isinstance(item, File):
            print(f'Creating file {cyan(item.path)}')
            with open(item.path, 'w') as handle:
                data = os.path.basename(item.path) if item.data is None else item.data
                handle.write(f'{data}\n')
        elif isinstance(item, Link):
            print(f'Creating link {cyan(item.path)} -> {cyan(item.to)}')
            os.symlink(item.to, item.path)
    return [item.path for item in manifest]


def check(manifest):
    """ Check the specified manifest. """
    # PASS 1: Check everything in the manifest is accurate
    allpaths = set()
    for item in manifest:
        allpaths.add(item.path)
        # Check the manifest file..
        if isinstance(item, File):
            print(f'Checking file {cyan(item.path)}')
            if not utils.is_file(item.path):
                raise Exception(f'File does not exist {cyan(item.path)}')
            if not data(item.path) == item.data:
                raise Exception(f'File {cyan(item.path)} data != "{item.data}"')
        # Check the manifest link..
        elif isinstance(item, Link):
            if not utils.is_link(item.path):
                raise Exception(f'Path {cyan(item.path)} is not a link.')
            if not os.readlink(item.path) == item.to:
                raise Exception(f'File {cyan(item.path)} not -> {cyan(item.to)}')
    # PASS 2: Make sure there are no extra files or directories
    for dirpath, dirnames, filenames in os.walk(os.path.dirname(HOME)):
        if IGNORE in dirpath: continue
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if filepath not in allpaths:
                raise Exception(f'Filepath {cyan(filepath)} not in the manifest.')
        if not dirnames and not filenames and dirpath not in [HOME, SYNC]:
            raise Exception(f'Found empty directory {cyan(dirpath)}.')
