# -*- coding: utf-8 -*-
# py.test -rxXs --tb=native --verbose tests; ll /tmp/linkmanager/*/*
import os, pytest
from .conftest import HOME, LINKROOT
from .conftest import content_ok
from .conftest import touch_filepaths
from linkmanager import LINKDIR
from linkmanager import mklink


def test_file(opts):
    opts.paths = [os.path.join(HOME, 'test1.tmp')]
    syncpaths = [p.replace(HOME, LINKROOT) for p in opts.paths]
    touch_filepaths(opts.paths)
    mklink.run_command(opts)
    for i in range(len(opts.paths)):
        assert os.path.isfile(opts.paths[i]), "Path is a file"
        assert os.path.islink(opts.paths[i]), "Symlink was not created"
        assert os.path.isfile(syncpaths[i]), "Sync file was not created"
        assert content_ok(opts.paths[i]), "Contents are not accurate"


def test_subfile(opts):
    opts.paths = [os.path.join(HOME, 'subdirA/test1.tmp')]
    syncpaths = [p.replace(HOME, LINKROOT) for p in opts.paths]
    touch_filepaths(opts.paths)
    mklink.run_command(opts)
    for i in range(len(opts.paths)):
        assert os.path.isfile(opts.paths[i]), "Path is a file"
        assert os.path.islink(opts.paths[i]), "Symlink was not created"
        assert os.path.isfile(syncpaths[i]), "Sync file was not created"
        assert content_ok(opts.paths[i]), "Contents are not accurate"


def test_unicode_file(opts):
    opts.paths = [os.path.join(HOME, 'สวัสดีครับ - 🦊🐵🐸.tmp')]
    syncpaths = [p.replace(HOME, LINKROOT) for p in opts.paths]
    touch_filepaths(opts.paths)
    mklink.run_command(opts)
    for i in range(len(opts.paths)):
        assert os.path.isfile(opts.paths[i]), "Path is a file"
        assert os.path.islink(opts.paths[i]), "Symlink was not created"
        assert os.path.isfile(syncpaths[i]), "Sync file was not created"
        assert content_ok(opts.paths[i]), "Contents are not accurate"


def test_already_exists(opts):
    opts.paths = [os.path.join(HOME, 'existing.tmp')]
    syncpaths = [p.replace(HOME, LINKROOT) for p in opts.paths]
    touch_filepaths(opts.paths)
    touch_filepaths(syncpaths)
    mklink.run_command(opts)
    for i in range(len(opts.paths)):
        assert os.path.isfile(opts.paths[i]), "Path is a file"
        assert not os.path.islink(opts.paths[i]), "Path is a link!"
        assert os.path.isfile(syncpaths[i]), "Sync file was not created"


def test_outside_home(opts):
    parent = os.path.dirname(HOME)
    opts.paths = [os.path.join(parent, '/tmp/outside.tmp')]
    with pytest.raises(SystemExit):
        mklink.run_command(opts)


def test_inside_linkroot(opts):
    opts.paths = [os.path.join(LINKROOT, 'foo/outside.tmp')]
    with pytest.raises(SystemExit):
        mklink.run_command(opts)


def test_dir(opts):
    subfiles = [
        os.path.join(HOME, 'mydir/test1.tmp'),
        os.path.join(HOME, 'mydir/test2.tmp')]
    opts.paths = [os.path.join(HOME, 'mydir')]
    syncpaths = [p.replace(HOME, LINKROOT) for p in opts.paths]
    touch_filepaths(subfiles)
    mklink.run_command(opts)
    for i in range(len(opts.paths)):
        assert os.path.isfile(os.path.join(opts.paths[i], LINKDIR)), "LINKDIR does not exist"
        assert os.path.isdir(opts.paths[i]), "Path is a dir"
        assert os.path.islink(opts.paths[i]), "Symlink was not created"
        assert os.path.isdir(syncpaths[i]), "Sync file was not created"
    for subfile in subfiles:
        assert content_ok(subfile), "Contents are not accurate"


def test_symlink(opts):
    testfile = os.path.join(HOME, 'testfile.tmp')
    testlink = os.path.join(HOME, 'testlink.lnk')
    touch_filepaths([testfile])
    os.symlink(testfile, testlink)
    opts.paths = [testlink]
    mklink.run_command(opts)
    syncpath = testlink.replace(HOME, LINKROOT)
    assert os.path.isfile(testfile), "Testfile is not a file"
    assert os.path.isfile(testlink), "Testlink is not a file"
    assert os.path.islink(testlink), "Testlink is not a link"
    assert os.readlink(testlink) == testfile, "Testlink not pointing to correct location"
    assert os.path.isfile(syncpath), "Syncpath is not a file"
    assert os.path.islink(syncpath), "Syncpath is not a link"
    assert os.readlink(syncpath) == testfile, "Syncpath not pointing to correct location"
