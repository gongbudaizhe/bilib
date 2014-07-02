#! /usr/bin/env python
# -*- coding: utf-8 -*-
# get_common.py
#
# Copyright © 2014 bily <bily.HUST@gmail.com>
#
# distribution is not allowed without author's approval

#import sys
#sys.path.append("") # your library directory

"""

"""
import sys
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('ref', help = 'reference file')
    parser.add_argument('test', help = 'comparison file')
    parser.add_argument('--col', type = int, help = 'compare the #col column of two file\ncompare the whole line if not set',default=-1)
    args = parser.parse_args()

    ref_path = args.ref
    test_path = args.test
    col = args.col

    with open(ref_path) as f_ref:
        with open(test_path) as f_test:
            lines_ref = f_ref.readlines()
            lines_test = f_test.readlines()
            
            if col >= 0:
                ref = []
                test = []
                for line in lines_ref:
                    ref.append(line.split(" ")[col])
                ref = set(ref)
            else:
                ref = set(lines_ref)
            
            common = []
            uncommon = []
            for line in lines_test:
                if col >= 0:
                    key = line.split(" ")[col]
                else:
                    key = line

                if key in ref:
                    common.append(line)
                else:
                    uncommon.append(line + "\n")
            sys.stdout.writelines(common) 
            #with open("uncommon", "w") as f_out:
                #f_out.writelines(uncommon)
            #print len(common)
