#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 bily     Huazhong University of Science and Technology
#
# Distributed under terms of the MIT license.

"""

TODO:
    * I used batch_num = 100 here to deal with large files but it may cause problems when file line number is less than batch_num
    * In random mode, we won't get output that follows the original file's order
    * add more selection mode
"""

import sys
import argparse

def readline(file_, num, lines):
    for i in range(num):
        lines.append(file_.readline())

    return len(lines[-1])

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help = 'specify input file')
    parser.add_argument('-r', type = float,  help = 'ratio', default = 0.1)
    parser.add_argument('-t', type = int, help = "selection mode(0:random)", default = 0)
    parser.add_argument('-c', help = "complementary filepath", default = '')
    args = parser.parse_args()

    filename = args.filename
    ratio = args.r
    mode = args.t
    
    complementary_file = args.c
    if complementary_file:
        com_file = open(complementary_file, 'w')

    if filename == "-":
        input_file = sys.stdin
    else:
        input_file = open(filename)

    batch_num = 100
    break_point = int(batch_num * ratio)

    # process code here 
    if mode == 0:
        import random
        while True:
            lines = [] 
            status = readline(input_file, batch_num, lines)

            index = range(batch_num)
            random.shuffle(index)
            for pos in index[0:break_point]:
                sys.stdout.write(lines[pos])
            if complementary_file:
                for pos in index[break_point:]:
                    com_file.write(lines[pos])

            if status == 0:
                break
    else:
        # TODO: add other mode
        pass

    if filename != "-":
        input_file.close()
    if complementary_file:
        com_file.close()



