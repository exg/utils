# Overview

Collection of miscellaneous utilities

* `apt-dump`: list the available debian packages in a one-per-line format
* `b64decode`: decode a Base64 encoded sequence
* `count-words`: list the words contained in a file, sorted by frequency
* `cvs-ls`: list the files tracked by a CVS checkout
* `get-access-token`: obtain an OAuth 2.0 access token
* `ld-grep`: grep dependencies of executable files
* `matrix`: process a matrix
* `md2mbox`: convert a maildir mailbox to an mbox mailbox
* `mirror`: synchronize two directories using rsync, with support for
inode-based file rename detection
* `mp3sum`: compute the SHA256 hash of a MP3 file excluding ID3 tags, if any
* `pastebin`: upload a file to a pastebin
* `pconfig`: configure a source directory build
* `proc-size`: show the amount of unique and total memory used by a process tree
* `pwd-tool`: manage mail passwords in the system keychain
* `setdiff`: diff files as sets
* `tabulate`: convert a matrix to a latex table
* `tar-dump`: list the content of a TAR archive
* `tar-size`: show the content size in bytes of a TAR archive
* `urldecode`: decode a percent encoded sequence
* `vcard2mutt`: convert a vcard file to a mutt alias file
* `verify-bom`: verify the integrity of the files indexed by a BOM file
* `vsort`: sort version numbers
* `yaml2json`: convert a YAML document to a JSON document


# Installation

```
python3 setup.py sdist
pip install dist/exg.utils-1.0.tar.gz
```
