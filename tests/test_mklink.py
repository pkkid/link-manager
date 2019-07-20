# -*- coding: utf-8 -*-
# py.test -rxXs --tb=native --verbose --log-cli-level=INFO ~/Projects/link-manager/tests/test_mklink.py
import os
import pytest
from .conftest import HOME, SYNC, File, Link
from .conftest import create, check
from .conftest import clear_contents, list_contents
from linkmanager import LINKDIR
from linkmanager import mklink

setup_function = clear_contents
teardown_function = list_contents


def test_basic_files(opts):
    """ Basic filepaths should just work. """
    opts.paths = create([
        File(f'{HOME}/test1.tmp'),  # File at root
        File(f'{HOME}/subdir/test2.tmp'),  # File in subdir
        File(f'{HOME}/สวัสดีครับ - 🦊🐵🐸.tmp'),  # Unicode
    ])
    mklink.run_command(opts)
    check([
        Link(f'{HOME}/test1.tmp', to=f'{SYNC}/test1.tmp'),
        Link(f'{HOME}/subdir/test2.tmp', to=f'{SYNC}/subdir/test2.tmp'),
        Link(f'{HOME}/สวัสดีครับ - 🦊🐵🐸.tmp', to=f'{SYNC}/สวัสดีครับ - 🦊🐵🐸.tmp'),
        File(f'{SYNC}/test1.tmp', data='test1.tmp'),
        File(f'{SYNC}/subdir/test2.tmp', data='test2.tmp'),
        File(f'{SYNC}/สวัสดีครับ - 🦊🐵🐸.tmp', data='สวัสดีครับ - 🦊🐵🐸.tmp'),
    ])


def test_already_exists(opts):
    """ mklink with an existing file in syncdir should fail. """
    paths = create([
        File(f'{HOME}/existing1.tmp'),
        File(f'{SYNC}/existing1.tmp'),
    ])
    opts.paths = [p for p in paths if p.startswith(HOME)]
    mklink.run_command(opts)
    check([
        Link(f'{HOME}/existing1.tmp', to=f'{SYNC}/existing1.tmp'),
        File(f'{SYNC}/existing1.tmp', data='existing1.tmp'),
    ])


def test_outside_home(opts):
    """ Test file outside home directory should fail. """
    parent = os.path.dirname(HOME)
    opts.paths = create([File(f'{parent}/outside.tmp')])
    with pytest.raises(SystemExit):
        mklink.run_command(opts)


def test_inside_linkroot(opts):
    """ Test file inside sync dir should fail. """
    opts.paths = create([File(f'{SYNC}/inside.tmp')])
    with pytest.raises(SystemExit):
        mklink.run_command(opts)


def test_dir(opts):
    """ Test syncing a directory. """
    create([
        File(f'{HOME}/mydir/test1.tmp'),
        File(f'{HOME}/mydir/test2.tmp')])
    opts.paths = [f'{HOME}/mydir']
    mklink.run_command(opts)
    check([
        Link(f'{HOME}/mydir', to=f'{SYNC}/mydir'),
        File(f'{SYNC}/mydir/{LINKDIR}', data=''),
        File(f'{SYNC}/mydir/test1.tmp', data='test1.tmp'),
        File(f'{SYNC}/mydir/test2.tmp', data='test2.tmp'),
    ])


def test_symlink(opts):
    create([
        File(f'{HOME}/mydir/testfile.tmp'),
        Link(f'{HOME}/mydir/testlink.lnk', to=f'{HOME}/mydir/testfile.tmp')])
    opts.paths = [f'{HOME}/mydir/testlink.lnk']
    mklink.run_command(opts)
    check([
        File(f'{HOME}/mydir/testfile.tmp', data='testfile.tmp'),
        Link(f'{HOME}/mydir/testlink.lnk', to=f'{HOME}/mydir/testfile.tmp'),
        Link(f'{SYNC}/mydir/testlink.lnk', to=f'{HOME}/mydir/testfile.tmp'),
    ])
