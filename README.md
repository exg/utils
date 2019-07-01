# Overview

Collection of miscellaneous utilities

* `apt-dump`: list the available debian packages in a one-per-line format
* `b64decode`: decode a Base64 encoded sequence
* `battery`: show the battery status
* `browser`: open a URL in a new browser window
* `count-words`: list the words contained in a file, sorted by frequency
* `cvs-ls`: list the files tracked by a CVS checkout
* `deckdiff`: diff Hearthstone decks
* `git-sync-fork`: sync a git fork with the upstream repository
* `ld-grep`: grep dependencies of executable files
* `matrix`: process a matrix
* `md2mbox`: convert a maildir mailbox to an mbox mailbox
* `mirror`: synchronize two directories using rsync, with support for
inode-based file rename detection
* `mp3sum`: compute the SHA256 hash of a MP3 file excluding ID3 tags, if any
* `mutt-open`: mutt mailcap helper to open attachments in the background
* `pastebin`: upload a file to a pastebin
* `pconfig`: configure an autoconf-based source directory
* `pwd-tool`: manage mail passwords in the system keychain
* `rename-symbol`: rename a symbol using rtags
* `setdiff`: diff files as sets
* `tabulate`: convert a matrix to a latex table
* `tar-dump`: list the content of a TAR archive
* `urldecode`: decode a percent encoded sequence
* `vcard2mutt`: convert a vcard file to a mutt alias file
* `verify-bom`: verify the integrity of the files indexed by a BOM file
* `vsort`: sort version numbers


# Installation

1. `python3 setup.py sdist`
2. `pip install --user dist/exg-utils-1.0.tar.gz`
