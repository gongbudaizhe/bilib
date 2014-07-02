#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 bily <bily@mclab>
#

"""
utils
"""
import os
import errno
import shutil

def get_suffix_file(dirname, suffix):
    """get all files in a dir recursively with specific suffix"""

    files = []
    for dirpath,dirnames,filenames in os.walk(dirname):
        for name in filenames:
            filename, file_extension = os.path.splitext(name)
            if file_extension == suffix:
                files.append(os.path.join(dirpath, name))
    return files

def copy(src, dest, force_create = False):
    """copy file from src to dest"""
    
    if force_create:
        head,tail = os.path.split(dest)
        mkdir_p(head)
        shutil.copyfile(src, dest)
    else:
        shutil.copyfile(src, dest)

def mkdir_p(path):
    '''
        functions like mkdir -p in bash
    '''
    try:
        os.makedirs(path)
    except OSError as exc: # Python > 2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

if __name__ == "__main__":
    pass
