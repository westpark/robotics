#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse

shells = {}
from . import text
shells['text'] = text
try:
    from . import snes
except ImportError:
    shells['snes'] = None
else:
    shells['snes'] = snes

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--shell", default="text")
    args = parser.parse_args()

    shell = shells.get(args.shell)
    if shell:
        shell.start()
    else:
        raise RuntimeError("Invalid shell: %s" % args.shell)
