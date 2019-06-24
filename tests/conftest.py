# -*- coding: utf-8 -*-
import os, pytest, shutil
from linkmanager import utils

HOME = '/tmp/linkmanager/homedir'
LINKROOT = '/tmp/linkmanager/linkroot'


def content_ok(filepath):
    print(f'reading file: {filepath}')
    with open(filepath, 'r') as handle:
        data = handle.read().strip()
    return data == os.path.basename(filepath)


def touch_filepaths(filepaths):
    for path in filepaths:
        print(f'touching file: {path}')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as handle:
            handle.write(f'{os.path.basename(path)}\n')


@pytest.fixture()
def opts():
    for path in (HOME, LINKROOT):
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path, exist_ok=True)
    return utils.Bunch({
        'home': HOME,
        'linkroot': LINKROOT,
        'dryrun': False,
    })
