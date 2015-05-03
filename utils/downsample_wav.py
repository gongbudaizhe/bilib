#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 bily.lee@qq.com Huazhong University of Science and Technology
#
# Distributed under terms of the MIT license.

from scipy.io import wavfile
import sys

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "Usage: {0} input_wav downsample_rate " \
              "output_wav".format(sys.argv[0])
        exit(1)

    wavname = sys.argv[1]
    downsample_rate = int(sys.argv[2])
    out_wav = sys.argv[3]
    rate, data = wavfile.read(wavname)

    wavfile.write(out_wav, rate/downsample_rate, data[::downsample_rate])