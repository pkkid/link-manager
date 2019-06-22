# Link Manager
Allows you to easily sync specific configuration files across all your Linux
computers with the assistance of another third-party service such as Dropbox,
Google Drive, or Synology Drive. This tool makes it easy to copy a file into your
sync location and create the corresponding symlink to it's original location. It
provides the following core commands:

* **`mklink <PATH>`** - Copy a file to the sync location and replace the original
     file with a symlink pointing to the now synced file.
* **`cplinks`** - Iterate all files in the sync location and replace the original
     files with symlinks pointing to them.
* **`rmlink PATH`** - The opposite of mklink. Copies the synced file back to it's
     original location to no longer by synced.

## Example Usage
Let's assume my Dropbox folder is syncing to `~/Dropbox` and I decide I want to
store my configuration files in `~/Dropbox/Config`. The following examples explain
what is happening behind the scenes when running these commands.

```bash
# Update config to know where synced files go. We only need to call this once.
links.py setconfig --linkroot ~/Dropbox/Config

# After the above setup step, we're good to go. Let's say you want to make sure
# the local file ~/.flake8 is in sync across all your Linux installations. We
# can simply run the following command to start syncing it. This command will
# copy ~/.flake8 to ~/Dropbox/Config/.flake8 then create a symlink from
# ~/.flake8 -> ~/Dropbox/Config/.flake8.
links.py mklink ~/.flake8

# To make sure this file is also in sync on the second computer, we can symply
# run the following command (on the second comuter). This command will iterate
# all files in ~/Dropbox/Config and setup the corresponding symlink for every
# file or directory present.
links.py cplinks
```

## Documentation
#### setconfig \<key\>=\<value\>
Saves the specified key value pair to the configuration file. The configuration
file is located at `~/.config/linkmanager.json` and currently the only supported
configuration option is `linkroot`.

#### mklink \<path\>
Copies the specified file or directory to the synced location and created a
coresponding symlink pointing to the synced file. If the path is a directry, the
full direcotry will be copied to the synced location and a single symlink created
pointing to the synced directory. - *Under the covers this command will also add
a single blank file `LINKDIR` to the root of the directory so these tools
understand to create a single symlink for the full directory and not individual
symlinks for each file.*

#### cplinks
Recursley iterates all files in the sync location and created cooresponding
symlinks in your home directory to these synced files. This command is used
update or initially setup all synced files into place. *Under the covers it
follows the ruleset below while iterating the sync location: 1. Sync every file
to its cooresponding location in your home dir. 2. If a dir contains the file
LINKDIR, symlink the directory, not the individual files. 3. If a symlink is
found, just copy it into place.*

#### rmlink \<path\>
The opposite of mklink. This will copy the file from the sync location back to
it's cooresponding location in your home directory. The file will no longer be
syncing across your computers.

#### inventory
Displays an simple inventory of all files items in the sync location.



## Installation
Presumably, you are already using a sync service such as Dropbox, Google Drive or
Synology Drive. This project uses no third party requirements. So simply cloning
the repo is enough to get yourself going. Optionally, you may want to add a few
aliases to your `.bash_profile` to make running the commands a little easier.

```bash
alias mklink="links.py mklink"
alias cplinks="links.py cplinks"
alias rmlink="links.py rmlink"
```

Don't forget the one time setup step to tell Link Manager where to sync files:

```bash
links.py setconfig --linkroot ~/Dropbox/Config
```
