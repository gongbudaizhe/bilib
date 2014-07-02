#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 bily     Huazhong University of Science and Technology
#
# Distributed under terms of the MIT license.

"""
convert file's encoding to utf8

note:
    1. it's recommended to convert a file into utf8 instead of a single sentence
    or a single word, since chardet won't work well without enough text material

TODO:
    1. convert_tree_to_utf8 can be really slow, try to use multiprocessing
    2. convert_tree_to_utf8's handling directory name doesn't work correctlly
    3. convert_tree_to_utf8 handle suffix
    4. argparse add more options
    DONE! for large files, it can consume a lot of memory(for 2.5G file, you need a machine with memory larger than 6G), I shall figure out a way to solve this.

"""

import sys
import os

def readline(file_, num, lines):
    for i in range(num):
        lines.append(file_.readline())
    
    return len(lines[-1]) > 0
 
def mkdir_p(path):
    """functions like mkdir -p in bash"""

    import errno
    try:
        os.makedirs(path)
    except OSError as exc: # Python > 2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def get_available_encodings():
    """get all available encodings in python"""

    import pkgutil
    import encodings

    false_positives = set(["aliases"])

    found = set(name for imp, name, ispkg in pkgutil.iter_modules(encodings.__path__) if not ispkg)
    found.difference_update(false_positives)

    return found
    
#available_encodings = get_available_encodings()

def convert_tree_to_utf8(dirname, autodetect = True, first_try_cp = None):
    """convert a whole tree to utf8"""

    new_top_dir = dirname + ".utf8"
    mkdir_p(new_top_dir)
    for dirpath, dirnames,filenames in os.walk(dirname):
        new_dirpath = new_top_dir + "/" + '/'.join(dirpath.split('/')[1:])
        for dir_ in dirnames:
            mkdir_p(os.path.join(new_dirpath, dir_))
        for name in filenames:
            old_file = os.path.join(dirpath, name)
            new_file = os.path.join(new_dirpath, name)
            with open(old_file) as f_in:
                with open(new_file, "w") as f_out:
                    f_out.write(convert_to_utf8(f_in.read(), autodetect, first_try_cp))

def find_encoding(string, autodetect = True, first_try_cp = None):
    """find encodings for any string"""

    string_partial = string[:8000] # we don't need all of the string to find the encoding
    code_page_found = False
    encoding = None
    if first_try_cp:
        try:
            string_decode = string_partial.decode(first_try_cp)
            code_page_found = True
            encoding = first_try_cp
        except UnicodeDecodeError as e:
            pass

    if not code_page_found and autodetect:
        import chardet    
        detected_encoding = (chardet.detect(string[:8000]))['encoding']
        try:
            string_decode = string_partial.decode(detected_encoding)
            code_page_found = True
            encoding = detected_encoding
        except:
            pass

    if not code_page_found:
        source_encoding = ["gbk" 
                           ,"gb2312" 
                           ,"gb18030" 
                           ,"big5" 
                           ,"shift_jis" 
                           ,"iso2022_kr" 
                           ,"iso2022_jp" 
                           ,"ascii"] 
        for x in source_encoding:
            try:
                string_decode = string_partial.decode(x)  
                code_page_found = True
                encoding = x
            except UnicodeDecodeError:
                continue 

    return encoding


def convert_to_utf8(string, autodetect = True, first_try_cp = None):
    """convert string from all kinds of encoding to UTF-8"""

    code_page_found = False
    if first_try_cp:
        try:
            string_decode = string.decode(first_try_cp)
            code_page_found = True
        except UnicodeDecodeError as e:
            pass

    if autodetect:
        import chardet    
        detected_encoding = (chardet.detect(string[:8000]))['encoding']
        try:
            string_decode = string.decode(detected_encoding[:5000])
            code_page_found = True
        except:
            pass

    if not code_page_found:
        source_encoding = ["gbk" 
                           ,"gb2312" 
                           ,"gb18030" 
                           ,"big5" 
                           ,"shift_jis" 
                           ,"iso2022_kr" 
                           ,"iso2022_jp" 
                           ,"ascii"] 
        for encoding in source_encoding:
            try:
                string_decode = string.decode(encoding)  
            except UnicodeDecodeError:
                continue 

    string_encode = string_decode.encode('utf-8')
    return string_encode

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help = 'specify input file')
    args = parser.parse_args()

    filename = args.filename
    if filename == "-":
        input_file = sys.stdin
    else:
        input_file = open(filename)

    batch_num = 100

    # find the encoding
    lines = []
    status = readline(input_file, 100, lines)
    lines_connected = "".join(lines)
    encoding = find_encoding(lines_connected)
    line = lines_connected.decode(encoding)
    sys.stdout.write(line.encode('utf-8'))

    if encoding:
        while True:
            lines = []
            status = readline(input_file, 100, lines)

            for line in lines:
                if len(line) > 0:
                    line = line.decode(encoding)
                    new_line = line.encode("utf-8")
                    sys.stdout.write(new_line)

            # remember to jump out the while loop
            if not status:
                break
    else:
        sys.stderr.write("Sorry, I can't find the encoding of input file...")

    if filename != "-":
        input_file.close()
