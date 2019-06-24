# -*- coding: utf-8 -*-
import os
from . import conftest
from linkmanager import mklink


def _call_mklink(opts, filepaths):
    # Setup the scenario
    homepaths = [os.path.join(conftest.HOME, p) for p in filepaths]
    syncpaths = [os.path.join(conftest.LINKROOT, p) for p in filepaths]
    # Run the command
    opts.paths = homepaths
    for path in opts.paths:
        conftest.touch(path)
    mklink.run_command(opts)
    # Check everything
    for i in range(len(homepaths)):
        assert os.path.isfile(syncpaths[i]), "Sync file was not created"
        assert os.path.islink(homepaths[i]), "Symlink was not created"
        assert conftest.content_ok(homepaths[i]), "Contents are not accurate"


def test_mklink_file(opts):
    filepath = ['test1.tmp', 'test2.tmp']
    _call_mklink(opts, filepath)


def test_mklink_subdir_file(opts):
    filepath = ['subdirA/test1.tmp', 'subdirB/test2.tmp']
    _call_mklink(opts, filepath)


def test_mklink_unicode(opts):
    filepath = ['สวัสดีครับ.tmp', '🦊🐵🐸.tmp']
    _call_mklink(opts, filepath)
