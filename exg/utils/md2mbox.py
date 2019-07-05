#!/usr/bin/env python3

import argparse
import mailbox


def maildir_to_mbox(src: str, dst: str) -> None:
    md = mailbox.Maildir(src)
    mbox = mailbox.mbox(dst)

    for msg in md.itervalues():
        mbox.add(mailbox.mboxMessage(msg))
    mbox.close()
    md.close()


def main() -> None:
    """
    Convert a maildir mailbox to an mbox mailbox.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("src")
    parser.add_argument("dst")
    args = parser.parse_args()
    maildir_to_mbox(args.src, args.dst)


if __name__ == "__main__":
    main()
