# encoding: utf-8
import logging
import os
import socket
import sys

FILE, DIR, LINK = 'file', 'dir', 'link'
DELETED = 'DELETED'
LINKROOT, LINKDIR = 'LINKROOT', 'LINKDIR'

HOME = os.path.expanduser('~')
HOSTNAME = socket.gethostname()
CONFIG = os.path.join(HOME, '.config/linkmanager.json')

log = logging.getLogger('linkmanager')
streamhandler = logging.StreamHandler(sys.stdout)
streamhandler.setFormatter(logging.Formatter('%(message)s'))
log.addHandler(streamhandler)
