#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 bily     Huazhong University of Science and Technology
#
# Distributed under terms of the MIT license.

"""

"""
import sys
#sys.path.append(your_library_here)
def readline(file_, num, lines):
    for i in range(num):
        lines.append(file_.readline())
    
    return len(lines[-1]) > 0

def process(line):
    return line

def parse_input(in_filename, out_filename):
    input_is_file = False
    output_is_file = False
    if in_filename and out_filename:
        input_file = open(in_filename)
        output_file = open(out_filename, 'w')
        input_is_file = True
        output_is_file = True

    if in_filename and not out_filename:
        if not sys.stdin.isatty():
            # we have pipe input
            input_file = sys.stdin
            output_file = open(in_filename, 'w')
            output_is_file = True
        else:
            input_file = open(in_filename)
            input_is_file = True
            output_file = sys.stdout

    if not in_filename and not out_filename:
        input_file = sys.stdin
        output_file = sys.stdout
    return input_file, output_file, input_is_file, output_is_file

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SOME FUNCTION")
    parser.add_argument('inputfile', nargs='?', help = 'input file')
    parser.add_argument('outputfile', nargs='?', help = 'output file')
    args = parser.parse_args()

    in_filename = args.inputfile
    out_filename = args.outputfile
    input_file, output_file, input_is_file, output_is_file = parse_input(in_filename, out_filename)

    batch_num = 100
    while True:
        lines = []
        status = readline(input_file, 100, lines)
        for line in lines:
            if len(line) > 0:
                # PROCESS CODE HERE
                new_line = process(line)
                output_file.write(new_line)

        # remember to jump out the while loop
        if not status:
            break

    if input_is_file:
        input_file.close()
    if output_is_file:
        output_file.close()


