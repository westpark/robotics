#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

from . import text
from . import snes

shells = {
    "snes" : snes,
    "text" : text
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--shell", default="text")
    args = parser.parse_args()

    if args.shell not in shells:
        raise RuntimeError("Invalid shell: %s" % args.shell)
    else:
        shell = shells[args.shell]
        shell.start()
