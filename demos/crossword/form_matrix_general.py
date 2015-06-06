#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2015 bily     Huazhong University of Science and Technology
#
# Distributed under terms of the MIT license.

"""
Forming a Crossword puzzle
note that you need stackless python to save the state since we need to pickle
iterators
"""

import sys
import pickle
import argparse
import signal

class State:
    def __init__(self):
        pass
s = State()

def sigint_handler(signum, frame):
    sys.stderr.write("Storing state in state.pickle...")
    with open('state.pickle', 'w') as f:
        pickle.dump(s, f)
    exit(0)

signal.signal(signal.SIGINT, sigint_handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # positional argument
    parser.add_argument('words', help='specify words file')
    # optional argument
    parser.add_argument('-s', '--state', help='specify state file')
    args = parser.parse_args()

    ############################################################################
    # Load words
    ############################################################################
    wordfile = args.words
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

    # Store len so that we don't have to compute it every time
    len_ref = {}
    for (key, value) in word_ref.iteritems():
        len_ref[key] = [len(ws) for ws in value]

    ############################################################################
    # Stage machine
    ############################################################################
    if args.state:
        with open(args.state) as f:
            s = pickle.load(f)
    else:
        s.stages = word_len + 1
        s.stage = 0
        s.progress = 0
        s.matrix = [None for i in xrange(s.stages)]
        s.iters = [None for i in xrange(s.stages)]
        s.sucess_matrixs = []
        first_sucess_words = {}
        for word in words:
            first_sucess_words[word] = None
        s.first_sucess_words = first_sucess_words

    while True:

        if s.stage == 0:
            # stage one: choose any word as the first row word,
            #            denote this word as word_1
            if not s.iters[s.stage]:
                s.iters[s.stage] = iter(words)

            # Get word
            try:
                # Show progress
                s.progress += 1
                sys.stderr.write("Progress: %d/%d\r" % (s.progress, n_words))
                sys.stderr.flush()

                word = s.iters[s.stage].next()

                last_word = s.matrix[s.stage]
                if last_word and not s.first_sucess_words[last_word]:
                    s.first_sucess_words[last_word] = False
            except StopIteration as e:
                break

            # Constraint
            # each char of the choosen word must apears
            # in the first position of at least one word
            for i in xrange(word_len):
                if len_ref[word[i]][0] == 0:
                    continue

            s.matrix[s.stage] = word
            s.stage += 1

        for i in xrange(1, s.stages-1):
            if s.stage == i:
                # stage two: choose any word except word_1 such that it has
                #            the same first char as the word_1,
                #            denoted as word_2

                char = s.matrix[0][i-1]
                if not s.iters[s.stage]:
                    s.iters[s.stage] = iter(word_ref[char][0])

                # Get word and update matrix
                try:
                    word = s.iters[s.stage].next()
                except StopIteration as e:
                    s.matrix[s.stage] = None
                    s.iters[s.stage] = None
                    s.stage -= 1
                    # You can "break" the for loop, since there is no point
                    # to try bigger stages.
                    # Here we use "continue" for consistency
                    continue

                # Constraint
                # If the word never succeeds as word_1, it won't succeeds as
                # word_2 either.
                if s.stage == 1:
                    if s.first_sucess_words[word] is not None:
                        continue
                # we don't want repetition
                if word in s.matrix:
                    continue
                # each char of the choosen word must apears
                # in the (stage)th position of at least one word
                for j in xrange(word_len):
                    if len_ref[word[j]][s.stage-1] == 0:
                        continue

                s.matrix[s.stage] = word
                s.stage += 1

        if s.stage == s.stages - 1:
            # final stage: this is where we have most constraints
            char = s.matrix[0][s.stage-1]
            if not s.iters[s.stage]:
                s.iters[s.stage] = iter(word_ref[char][0])

            # Get word and update matrix
            try:
                word = s.iters[s.stage].next()
            except StopIteration as e:
                s.matrix[s.stage] = None
                s.iters[s.stage] = None
                s.stage -= 1
                # You can "break" the for loop, since there is no point
                # to try bigger stages.
                # Here we use "continue" for consistency
                continue

            if word in s.matrix:
                continue
            for j in xrange(word_len):
                if len_ref[word[j]][s.stage-1] == 0:
                    continue

            s.matrix[s.stage] = word

            # constraints
            satisfied = True
            for i in xrange(1, word_len):
                word_t = "".join([w[i] for w in s.matrix[1:]])
                if word_t in s.matrix or \
                        word_t not in word_ref[s.matrix[-1][i]][word_len-1]:
                    satisfied = False
                    break
            if satisfied:
                s.first_sucess_words[s.matrix[0]] = True
                # print the matrix
                s.sucess_matrixs.append(s.matrix)
                sys.stdout.write(":".join([x.encode('utf-8') for x in s.matrix]))
                sys.stdout.write("\n")
