#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 bily <bily@mclab>
#
# Distributed under terms of the MIT license.

"""
This is a python implementation of the bash 'cat' functionality.
You can learn how to use argparse and fileinput module together to
achieve a better argument parsing mechanism.
"""

import sys
import fileinput
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs = '*', help = 'specify input files')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-o', '--output', 
                    help = 'specify the output file. The default is stdout')
    group.add_argument('-i', '--inplace', action = 'store_true',
                    help = 'modify files inplace')
    args = parser.parse_args()

    if args.output and args.output != '-':
        output_file = open(args.output, 'w')
    else:
        output_file = sys.stdout

    # write lines 
    for line in fileinput.input(args.files, inplace=args.inplace):
        output_file.write(line)
    
    # close file explicitely
    if args.output and args.output != '-':
        output_file.close()


