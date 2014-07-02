#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 bily     Huazhong University of Science and Technology
#
# Distributed under terms of the MIT license.

"""
A simple timer demo
"""
import argparse
import os
from threading import Timer

def notify(string):
    os.system("notify-send " + string)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", type = float, help = "work time(by minutes, default = 120)", default = 120)
    parser.add_argument("-r", type = float, help = "relax time(by minutes), default = 15", default = 15)
    args = parser.parse_args()

    work_time = args.w * 60.0
    relax_time = args.r * 60.0
    
    while True:
        t = Timer(work_time, notify, ['"Relax time!!!"'])
        t.start()
        t.join()
        t = Timer(relax_time, notify, ['"Start working..."'])
        t.start()
        t.join()
