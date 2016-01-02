#!/usr/bin/env python
import argparse
import os


def is_existing_dir(arg):
    if not os.path.isdir(arg):
        parser.error('Given path %s does not point to an existing directory. Exiting.')
    return arg


def is_not_existing_path(arg):
    if os.path.exists(arg):
        parser.error('Given path %s points to an existing path. Exiting.')
    return arg


__author__ = 'Alexander Junge (alexander.junge@gmail.com)'

parser = argparse.ArgumentParser(description='''TODO''')
args = parser.parse_args()