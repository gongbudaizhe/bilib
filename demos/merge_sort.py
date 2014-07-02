#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 bily <bily@mclab>
#
# Distributed under terms of the MIT license.

"""
merge sort demo
algorithm:
    1. split list into two list equally
    2. recursively merge sort two list
    3. merge two list 

"""

def compare(a, b):
    if a < b:
        return True
    else:
        return False

def split(list_):
    break_point = len(list_) / 2 
    list_a = list_[:break_point]
    list_b = list_[break_point:]
    return list_a,list_b

def merge(list_a, list_b, compare):
    i = 0
    j = 0
    list_ = []
    while True:
        if compare(list_a[i] , list_b[j]):
            list_.append(list_a[i])
            i += 1
        else:
            list_.append(list_b[j])
            j += 1

        # now check if it's the end
        if i >= len(list_a):
            for x in list_b[j:]:
                list_.append(x)
            break
        elif j >= len(list_b):
            for x in list_a[i:]:
                list_.append(x)
            break

    return list_
                

def merge_sort(list_, compare):
    if(len(list_) in [0, 1]):
        return list_
    list_a, list_b = split(list_)
    list_a = merge_sort(list_a, compare)
    list_b = merge_sort(list_b, compare)

    return merge(list_a, list_b, compare)

def test_merge_sort():
    test_list = [7, 4, 3, 4, 2, 9]
    print merge_sort(test_list, compare)

if __name__ == "__main__":
    test_merge_sort()
