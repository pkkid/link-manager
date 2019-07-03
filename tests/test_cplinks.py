# -*- coding: utf-8 -*-
# py.test -rxXs --tb=native --verbose --log-cli-level=INFO ~/Projects/link-manager/tests/test_cplinks.py
from .conftest import HOME, SYNC, File, Link
from .conftest import create, check
from .conftest import clear_contents, list_contents
from linkmanager import DELETED, LINKDIR
from linkmanager import cplinks

setup_function = clear_contents
teardown_function = list_contents


def test_file(opts):
    """ Basic filepaths should just work. """
    create([
        File(f'{SYNC}/test1.tmp'),  # File at root
        File(f'{SYNC}/subdir/test2.tmp'),  # File in subdir
        File(f'{SYNC}/สวัสดีครับ - 🦊🐵🐸.tmp'),  # Unicode
    ])
    cplinks.run_command(opts)
    check([
        Link(f'{HOME}/test1.tmp', to=f'{SYNC}/test1.tmp'),
        Link(f'{HOME}/subdir/test2.tmp', to=f'{SYNC}/subdir/test2.tmp'),
        Link(f'{HOME}/สวัสดีครับ - 🦊🐵🐸.tmp', to=f'{SYNC}/สวัสดีครับ - 🦊🐵🐸.tmp'),
        File(f'{SYNC}/test1.tmp', data='test1.tmp'),
        File(f'{SYNC}/subdir/test2.tmp', data='test2.tmp'),
        File(f'{SYNC}/สวัสดีครับ - 🦊🐵🐸.tmp', data='สวัสดีครับ - 🦊🐵🐸.tmp'),
    ])


def test_dir(opts):
    """ Test linking a dirtectory. """
    create([
        File(f'{SYNC}/mydir/test1.tmp'),
        File(f'{SYNC}/mydir/test2.tmp'),
        File(f'{SYNC}/mydir/{LINKDIR}', data=''),
    ])
    cplinks.run_command(opts)
    check([
        Link(f'{HOME}/mydir', to=f'{SYNC}/mydir'),
        File(f'{SYNC}/mydir/test1.tmp', data='test1.tmp'),
        File(f'{SYNC}/mydir/test2.tmp', data='test2.tmp'),
        File(f'{SYNC}/mydir/{LINKDIR}', data=''),
    ])


def test_symlink(opts):
    """ Symlink should be a copy of the file. """
    create([
        File(f'{HOME}/testfile.tmp'),
        Link(f'{SYNC}/testlink.lnk', to=f'{HOME}/testfile.tmp'),
    ])
    cplinks.run_command(opts)
    check([
        File(f'{HOME}/testfile.tmp', data='testfile.tmp'),
        Link(f'{HOME}/testlink.lnk', to=f'{HOME}/testfile.tmp'),
        Link(f'{SYNC}/testlink.lnk', to=f'{HOME}/testfile.tmp'),
    ])


def test_deleted(opts):
    """ Deleted file should replace linked file. """
    create([
        Link(f'{HOME}/testfile.tmp', to=f'{SYNC}/testfile.tmp'),
        File(f'{SYNC}/testfile.tmp[{DELETED}]', data='deleted'),
    ])
    cplinks.run_command(opts)
    check([
        File(f'{HOME}/testfile.tmp', data='deleted'),
        File(f'{SYNC}/testfile.tmp[{DELETED}]', data='deleted'),
    ])


def test_sync_disabled(opts):
    """ File shuold remain untouched as its was never being synced. """
    create([
        File(f'{HOME}/testfile.tmp'),
        File(f'{SYNC}/testfile.tmp[{DELETED}]', data='deleted'),
    ])
    cplinks.run_command(opts)
    check([
        File(f'{HOME}/testfile.tmp', data='testfile.tmp'),
        File(f'{SYNC}/testfile.tmp[{DELETED}]', data='deleted'),
    ])


def test_deleted_symlink(opts):
    """ Deleted symlink should replace broken symlink. """
    create([
        Link(f'{HOME}/testfile.tmp', to=f'{SYNC}/testfile.tmp'),
        Link(f'{SYNC}/testfile.tmp[{DELETED}]', to=f'{SYNC}/somefile.tmp'),
    ])
    cplinks.run_command(opts)
    check([
        Link(f'{HOME}/testfile.tmp', to=f'{SYNC}/somefile.tmp'),
        Link(f'{SYNC}/testfile.tmp[{DELETED}]', to=f'{SYNC}/somefile.tmp'),
    ])


# def test_deleted_dir(opts):
#     pass


# def test_deleted_notdeleted_file(opts):
#     pass


# def test_deleted_notdeleted_symlink(opts):
#     pass


# def test_deleted_notdeleted_dir(opts):
#     pass


# def test_hostname(opts):
#     pass


# def test_deleted_hostname(opts):
#     pass
