#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 bily <bily@mclab>
#
# Distributed under terms of the MIT license.

"""

"""

import sys
import argparse

#sys.path.append(your_library_here)

def convert_string_to_number(string):
    try:
        return int(string)
    except ValueError:
        return float(string)

def parse_columns_input(columns,col_num):
    parts = columns.split(":")
    if len(parts) > 3:
        raise Exception("wrong column syntax")
    elif len(parts) == 3:
        start = convert_string_to_number(parts[0])
        step = convert_string_to_number(parts[1])
        stop = min(convert_string_to_number(parts[2]), col_num)
        return range(start, stop, step)
    elif len(parts) == 2:
        if parts[0]:
            start = convert_string_to_number(parts[0])
        else:
            start = 0
        if parts[1]:
            stop = min(convert_string_to_number(parts[1]), col_num)
        else:
            stop = col_num
        return range(start, stop)
    elif len(parts) == 1:
        pos = convert_string_to_number(parts[0])
        if col_num  > pos:
            return [pos]
        else:
            return []
    else:
        raise Exception("Empty columns")


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help = 'specify input file')
    parser.add_argument('columns', help = 'the columns needed')
    parser.add_argument('-s', '--separator', help = "column separator", default=" ")
    args = parser.parse_args()

    filename = args.filename
    columns = args.columns
    separator = args.separator
    if filename == "-":
        file_input = sys.stdin
    else:
        file_input = open(filename)

    lines = file_input.readlines()

    
    new_lines = []
    for line in lines:
        line = line.strip()
        line_parts = line.split(separator)

        COL_NUM = len(line_parts) 
        column_index = parse_columns_input(columns, COL_NUM)

        new_line = ''
        for pos in column_index:
            new_line += (line_parts[pos] + separator)
        new_line += "\n"
        new_lines.append(new_line)

    sys.stdout.writelines(new_lines)

    if filename != "-":
        file_input.close()
        
