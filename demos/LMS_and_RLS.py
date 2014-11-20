#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2014 bily     Huazhong University of Science and Technology
#
# Distributed under terms of the MIT license.

"""
This is a simple demo of LMS and RLS adaptive filter algorithm
"""

import numpy as np
import matplotlib.pyplot as plt
from numpy import dot, prod


def LMS(n_input, X, D, miu):
    """LMS algorithm

    :n_input: the dimension of the input vector
    :X: all the samples
    :D: all the ground truth
    :miu: the learning rate
    :returns: the history of weight W

    """
    n_samples = prod(X.shape)

    # parameter initialization
    W = np.zeros((n_input, 1)) # W(0)
    W_all = np.copy(W) # we should use the copy method to get another instance
                       # of matrix W. Normal assignment like W_all = W will just
                       # create a reference to W
    assert prod(D.shape) == n_samples - n_input,"{0}!={1}".format(prod(D.shape), 
                                                    n_samples - n_input)
    for i in range(n_samples - n_input):
        x = X[i:i+n_input] # x(i)
        d = D[i] # d(i)
        y = dot(W.T, x) # y(i)
        e = d - y # e(i) = d(i) - y(i)
        W += 2 * miu * e * x # gradient decent get W(i+1)
        W_all = np.c_[W_all, W]
    return W_all


def RLS(n_input, X, D, lamda, t):
    """RLS algorithm

    :n_input: the dimension of the input vector
    :X: all the samples
    :D: all the ground truth
    :lamda: the decaying factor
    :t: the initialization factor of T(-1)
    :returns: the history of weight W

    """
    n_samples = prod(X.shape)
    assert prod(D.shape) == n_samples - n_input,"{0}!={1}".format(prod(D.shape), 
                                                    n_samples - n_input)

    # parameter initialization
    W = np.zeros((n_input, 1)) # W(-1)
    W_all = np.copy(W)
    T = t * np.diag(np.ones(n_input)) # T is initialized as a diagnoal matrix

    for i in range(n_samples - n_input):
        x = X[i:i+n_input] # x(i)
        T = ((T - dot(dot(T, x), dot(x.T, T)) / (lamda + dot(dot(x.T, T), x))) 
                / lamda) # T(i)
        d = D[i] # d(i)
        y = dot(W.T, x) # y(i|i-1) 
        e = d - y # e(i|i-1)
        W += dot(T, x) * e # gradient decent get W(i)
        W_all = np.c_[W_all, W]
    return W_all


if __name__ == "__main__":

    # Set fixed seed to get the same result every time
    np.random.seed(0)

    miu = 0.002
    lambda1 = 1
    lambda2 = 0.98
    t = 10

    n_samples = 600
    n_input = 2 # the input dimension of the LMS filter

    # the model is: a0*x(n) + a1*x(n-1) + a2*x(n-2) = e(n)
    A = np.array([[-0.8], [1.6]])
    assert A.shape[0] == n_input, \
           "the number of input must equal to the number of model coefficients"

    # Generate noise which is white noise with zero mean and unit standard
    # deviation
    n = np.random.normal(0.0, 1.0, n_samples)[:, np.newaxis]
    x = np.zeros((2,1)) # x(-2), x(-1)
    for i in range(n_samples):
        X = x[i:i+n_input]
        x = np.r_[x, dot(A.T, X) + n[i]]

    W_LMS = LMS(n_input, x, x[n_input:], miu)
    W_RLS1 = RLS(n_input, x, x[n_input:], lambda1, t)
    W_RLS2 = RLS(n_input, x, x[n_input:], lambda2, t)

    #################
    # Plot 
    #################

    # vertical bar 
    bar = -A[1] * np.ones((n_samples))

    plt.figure()
    plt.plot(-W_LMS[1,:], label="LMS")
    plt.plot(-W_RLS1[1,:], label="RLS")
    plt.plot(bar, "--")

    locs, labels = plt.yticks()
    plt.yticks(np.concatenate((locs, -A[1])))
    plt.legend()
    plt.xlabel("n")
    plt.ylabel(r"$a_1(n)$")
    plt.title("LMS vs RLS")
    
    plt.figure()
    plt.plot(-W_RLS1[1,:], label=r"$\lambda=" + str(lambda1) +"$")
    plt.plot(-W_RLS2[1,:], label=r"$\lambda=" + str(lambda2) +"$")
    plt.plot(bar, "--")

    locs, labels = plt.yticks()
    plt.yticks(np.concatenate((locs, -A[1])))
    plt.legend()
    plt.xlabel("n")
    plt.ylabel(r"$a_1(n)$")
    plt.title("RLS with different decaying factor")

    # Show all plots
    plt.show()
