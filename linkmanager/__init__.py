# encoding: utf-8
import os, socket

FILE, DIR, LINK = 'file', 'dir', 'link'
DELETED = 'DELETED'
LINKROOT, LINKDIR = 'LINKROOT', 'LINKDIR'

HOME = os.path.expanduser('~')
HOSTNAME = socket.gethostname()
CONFIG = os.path.join(HOME, '.config/linkmanager.json')
