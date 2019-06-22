# links
Easily create symbolic links to Dropbox or any other file sync service to keep
settings synchronized across your PCs.

Configuration files can be copied to the home directory by running
~/Sync/Scripts/copy-links.py. The following rules will be applied.

* Ignore any non-hidden items linked to $HOME.
* If a dir contains the file LINKDIR, link the dir (not the files).
* If a symlink is found, just copy it into place.
* Create a symlink from relative dir in $HOME to all other files.
