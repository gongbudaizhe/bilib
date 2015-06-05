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
    ############################################################################
    # Load words
    ############################################################################
    wordfile = sys.argv[1]
    words = []
    with open(wordfile) as f:
        for line in f:
            line = line.decode('utf-8')
            line = line.strip()
            words.append(line)
    sys.stderr.write("len(words): " + str(len(words)) + "\n")
    n_words = len(words)

    word_ref = {}
    word_len = len(words[0])

    ############################################################################
    # Create word reference
    ############################################################################
    for word in words:
        for i in xrange(word_len):
            char = word[i]
            if char not in word_ref:
                word_ref[char] = [set() for j in xrange(word_len)]
            word_ref[char][i].add(word)
    sys.stderr.write("Word Reference Made...\n")

    ############################################################################
    # Stage machine
    ############################################################################
    stages = word_len + 1
    stage = 0
    matrix = [None for i in xrange(stages)]
    iters = [None for i in xrange(stages)]
    progress = 0
    while True:
        if stage == 0:
            # stage one: choose any word as the first row word,
            #            denote this word as word_1
            if not iters[stage]:
                iters[stage] = iter(words)

            # Get word and update matrix
            try:
                # Show progress
                progress += 1
                sys.stderr.write("Progress: %d/%d\r" % (progress, n_words))
                sys.stderr.flush()

                word = iters[stage].next()
                matrix[stage] = word
            except StopIteration as e:
                break

            stage += 1

        for i in xrange(1, stages-1):
            if stage == i:
                # stage two: choose any word except word_1 such that it has
                #            the same first char as the word_1,
                #            denoted as word_2

                char = matrix[0][i-1]
                if not iters[stage]:
                    iters[stage] = iter(word_ref[char][0])

                # Get word and update matrix
                try:
                    word = iters[stage].next()
                    matrix[stage] = word
                except StopIteration as e:
                    matrix[stage] = None
                    iters[stage] = None
                    stage -= 1
                    # You can "break" the for loop, since there is no point
                    # to try bigger stages.
                    # Here we use "continue" for consistency
                    continue

                stage += 1

        if stage == stages - 1:
            # final stage: this is where we have most constraints
            char = matrix[0][stage-1]
            if not iters[stage]:
                iters[stage] = iter(word_ref[char][0])

            # Get word and update matrix
            try:
                word = iters[stage].next()
                matrix[stage] = word
            except StopIteration as e:
                matrix[stage] = None
                iters[stage] = None
                stage -= 1
                # You can "break" the for loop, since there is no point
                # to try bigger stages.
                # Here we use "continue" for consistency
                continue

            # constraints
            satisfied = True
            for i in xrange(1, word_len):
                word_t = "".join([w[i] for w in matrix[1:]])
                if word_t not in word_ref[matrix[-1][i]][word_len-1]:
                    satisfied = False
                    break
            if satisfied:
                # print the matrix
                sys.stdout.write(":".join([x.encode('utf-8') for x in matrix]))
                sys.stdout.write("\n")
