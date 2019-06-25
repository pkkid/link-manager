# -*- coding: utf-8 -*-
# py.test -rxXs --tb=native --verbose tests; ll /tmp/linkmanager/*/*
import os, pytest
from .conftest import HOME, LINKROOT
from .conftest import content_ok
from .conftest import touch_filepaths
from linkmanager import LINKDIR
from linkmanager import cplinks


def test_file(opts):
    syncpaths = [os.path.join(LINKROOT, 'test1.tmp')]
    homepaths = [p.replace(LINKROOT, HOME) for p in syncpaths]
    touch_filepaths(syncpaths)
    cplinks.run_command(opts)
    for i in range(len(homepaths)):
        assert os.path.isfile(homepaths[i]), "Path is a file"
        assert os.path.islink(homepaths[i]), "Symlink was not created"
        assert content_ok(homepaths[i]), "Contents are not accurate"


def test_subfile(opts):
    syncpaths = [os.path.join(LINKROOT, 'subdirA/test1.tmp')]
    homepaths = [p.replace(LINKROOT, HOME) for p in syncpaths]
    touch_filepaths(syncpaths)
    cplinks.run_command(opts)
    for i in range(len(homepaths)):
        assert os.path.isfile(homepaths[i]), "Path is a file"
        assert os.path.islink(homepaths[i]), "Symlink was not created"
        assert content_ok(homepaths[i]), "Contents are not accurate"


def test_unicode_file(opts):
    syncpaths = [os.path.join(LINKROOT, 'สวัสดีครับ - 🦊🐵🐸.tmp')]
    homepaths = [p.replace(LINKROOT, HOME) for p in syncpaths]
    touch_filepaths(syncpaths)
    cplinks.run_command(opts)
    for i in range(len(homepaths)):
        assert os.path.isfile(homepaths[i]), "Path is a file"
        assert os.path.islink(homepaths[i]), "Symlink was not created"
        assert content_ok(homepaths[i]), "Contents are not accurate"


def test_dir(opts):
    linkdir = os.path.join(LINKROOT, 'mydir')
    syncpaths = [
        os.path.join(linkdir, 'test1.tmp'),
        os.path.join(linkdir, 'test2.tmp'),
        os.path.join(linkdir, LINKDIR)]
    homedir = linkdir.replace(LINKROOT, HOME)
    homepaths = [p.replace(LINKROOT, HOME) for p in syncpaths][:-1]
    touch_filepaths(syncpaths)
    cplinks.run_command(opts)
    for i in range(len(homepaths)):
        assert os.path.isfile(homepaths[i]), "Path is not a file"
        assert not os.path.islink(homepaths[i]), "Subfile is a link!"
        assert content_ok(homepaths[i]), "Contents are not accurate"
    assert os.path.isdir(homedir), "Homedir is not a dir"
    assert os.path.islink(homedir), "Homedir is not a link"


def test_symlink(opts):
    testfile = os.path.join(HOME, 'testfile.tmp')
    syncpath = os.path.join(LINKROOT, 'testlink.lnk')
    testlink = syncpath.replace(LINKROOT, HOME)
    touch_filepaths([testfile])
    os.symlink(testfile, syncpath)
    cplinks.run_command(opts)
    assert os.path.isfile(testfile), "Testfile is not a file"
    assert os.path.isfile(testlink), "Testlink is not a file"
    assert os.path.islink(testlink), "Testlink is not a link"
    assert os.readlink(testlink) == testfile, "Testlink not pointing to correct location"
    assert os.path.isfile(syncpath), "Syncpath is not a file"
    assert os.path.islink(syncpath), "Syncpath is not a link"
    assert os.readlink(syncpath) == testfile, "Syncpath not pointing to correct location"
