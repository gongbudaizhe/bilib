#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2015 bily     Huazhong University of Science and Technology
#
# Distributed under terms of the MIT license.

"""

"""

import sys

if __name__ == "__main__":
    with open('dict.txt') as dict_file:
        for line in dict_file:
            line = line.decode('utf-8')
            parts = line.split(' ')
            if len(parts[0]) == 4:
                sys.stdout.write(parts[0].encode('utf-8') + '\n')
