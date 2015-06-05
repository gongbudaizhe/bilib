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

    ############################################################################
    # Create word reference
    ############################################################################
    word_ref = {}
    word_len = len(words[0])

    for word in words:
        for i in xrange(word_len):
            char = word[i]
            if char not in word_ref:
                word_ref[char] = [set() for j in xrange(word_len)]
            word_ref[char][i].add(word)
    sys.stderr.write("Word Reference Made...\n")

    len_ref = {}
    for (key, value) in word_ref.iteritems():
        len_ref[key] = [len(ws) for ws in value]

    ############################################################################
    # Stage machine
    ############################################################################
    stages = word_len + 1
    stage = 0
    progress = 0
    matrix = [None for i in xrange(stages)]
    iters = [None for i in xrange(stages)]

    first_sucess_words = {}
    for word in words:
        first_sucess_words[word] = None

    while True:
        if stage == 0:
            # stage one: choose any word as the first row word,
            #            denote this word as word_1
            if not iters[stage]:
                iters[stage] = iter(words)

            # Get word
            try:
                # Show progress
                progress += 1
                sys.stderr.write("Progress: %d/%d\r" % (progress, n_words))
                sys.stderr.flush()

                word = iters[stage].next()

                last_word = matrix[stage]
                if last_word and not first_sucess_words[last_word]:
                    first_sucess_words[last_word] = False
            except StopIteration as e:
                break

            # Constraint
            # each char of the choosen word must apears
            # in the first position of at least one word
            for i in xrange(word_len):
                if len_ref[word[i]][0] == 0:
                    continue

            matrix[stage] = word
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
                except StopIteration as e:
                    matrix[stage] = None
                    iters[stage] = None
                    stage -= 1
                    # You can "break" the for loop, since there is no point
                    # to try bigger stages.
                    # Here we use "continue" for consistency
                    continue

                # Constraint
                # If the word never succeeds as word_1, it won't succeeds as
                # word_2 either.
                if stage == 1:
                    if first_sucess_words[word] is not None:
                        continue
                # we don't want repetition
                if word in matrix:
                    continue
                # each char of the choosen word must apears
                # in the (stage)th position of at least one word
                for j in xrange(word_len):
                    if len_ref[word[j]][stage-1] == 0:
                        continue

                matrix[stage] = word
                stage += 1

        if stage == stages - 1:
            # final stage: this is where we have most constraints
            char = matrix[0][stage-1]
            if not iters[stage]:
                iters[stage] = iter(word_ref[char][0])

            # Get word and update matrix
            try:
                word = iters[stage].next()
            except StopIteration as e:
                matrix[stage] = None
                iters[stage] = None
                stage -= 1
                # You can "break" the for loop, since there is no point
                # to try bigger stages.
                # Here we use "continue" for consistency
                continue

            if word in matrix:
                continue
            for j in xrange(word_len):
                if len_ref[word[j]][stage-1] == 0:
                    continue

            matrix[stage] = word

            # constraints
            satisfied = True
            for i in xrange(1, word_len):
                word_t = "".join([w[i] for w in matrix[1:]])
                if word_t in matrix or \
                        word_t not in word_ref[matrix[-1][i]][word_len-1]:
                    satisfied = False
                    break
            if satisfied:
                first_sucess_words[matrix[0]] = True
                # print the matrix
                sys.stdout.write(":".join([x.encode('utf-8') for x in matrix]))
                sys.stdout.write("\n")
