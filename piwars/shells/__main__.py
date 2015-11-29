#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import importlib

name = __name__.split(".")[-1]
if name == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--shell", default="text")
    args = parser.parse_args()

    try:
        module = importlib.import_module(".%s" % args.shell, "piwars.shells")
    except ImportError:
        raise RuntimeError("Invalid shell: %s" % args.shell)
    else:
        shell = module.Shell()
    
    shell.start()
