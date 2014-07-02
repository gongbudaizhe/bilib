#!/usr/bin/python
# transform PCM format to wav format and write to stdout
# bily 
# TODO:
# 1.DONE parse argument
# 2. set data endian(little?big?)

import sys
import argparse
from struct import *

#---------------------------------------------------------------------
#----------------------- parse argument ------------------------------
#---------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("raw_file", help = "the raw file's path")
parser.add_argument("-nchannels",type = int, help = "number of channels", default = 1)
parser.add_argument("-samprate",type = int, help = "sampling rate(Hz)",default= 16000)
parser.add_argument("-sampwidth", type = int, help = "number of bytes per sample",default = 2)
args = parser.parse_args()

# header
nchannels = args.nchannels 
sampwidth = args.sampwidth # n bytes per sample
framerate = args.samprate # sampling rate
byterate = framerate * nchannels * sampwidth 
blockalign = nchannels * sampwidth

# read PCM data
with open(sys.argv[1], 'rb') as pcmfile:
    pcm = pcmfile.read()
    pcm_size = len(pcm)
    chunk_size = pcm_size + 36
    # convert PCM to wav, all we need is just a header
    wav = ''
    wav += pack('>cccc', 'R','I','F','F') # ChunkID, contains the
                                          # letters "RIFF" in ASCII
                                          # form(0x52494646 big-endian)
    wav += pack('<I', chunk_size) # ChunkSize, this is the size of the
                                  # rest of the chunk following this number

    wav += pack('>cccc', 'W','A','V','E') # Format, contains the
                                          # letters "WAVE"(0x57415645 big-endian)

#--------------------------------------------------------------------
    wav += pack('>cccc', 'f','m','t',' ') # Subchunk1ID, contains the 
                                          # letters "fmt "(0x666d7420 big-endian)
    wav += pack('<I', 16) # Subchunk1ISize, 16 for PCM
    wav += pack('<H', 1) # AudioFormat, PCM = 1, values other than 1 indicate some form of compression
    wav += pack('<H', nchannels) # NumChannels, mono = 1, stereo = 2, etc
    wav += pack('<I', framerate) # 8000, 44100, etc
    wav += pack('<I', byterate) # samplerate * numchannels * bitspersample / 8
    wav += pack('<H', blockalign) # numchannels * bitspersample / 8
    wav += pack('<H', sampwidth * 8) # bitspersample

#--------------------------------------------------------------------
    wav += pack('>cccc','d','a','t','a') # Subchunk2ID, contains the letters "data"(0x64617461 big-endian)
    wav += pack('<I', pcm_size) # number of bytes in the data
    wav += pcm # this is the data(little-endian)
    sys.stdout.write(wav)

