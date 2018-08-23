#!/usr/bin/env python
import os
import sys
import tarfile


def internal_tar(root_path, arc_name=None):
    _, source_name = os.path.split(root_path)
    with tarfile.open(fileobj=sys.stdout.buffer, mode='w|') as tf:
        tf.add(root_path, arcname=arc_name or source_name)


def main():
    if len(sys.argv) < 2:
        sys.stderr.write('tar.py path\n')
        sys.exit(-1)
    root_path = os.path.abspath(sys.argv[1])
    arc_name = None if len(sys.argv) < 3 else sys.argv[2]

    # call tar to pack files
    internal_tar(root_path, arc_name)


if __name__ == '__main__':
    main()
