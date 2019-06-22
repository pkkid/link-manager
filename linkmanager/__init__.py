# encoding: utf-8
import logging, os, sys

FILE, DIR = 'file', 'dir'
LINKROOT, LINKDIR = 'LINKROOT', 'LINKDIR'
HOME = os.path.expanduser('~')
CONFIG = os.path.join(HOME, '.config/linkmanager.json')

log = logging.getLogger('linkmanager')
streamhandler = logging.StreamHandler(sys.stdout)
streamhandler.setFormatter(logging.Formatter('%(message)s'))
log.addHandler(streamhandler)
