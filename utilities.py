# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 12:25:15 2020

@title: Utilities
@author: Philip Bretz
"""

import numpy as np
import pandas as pd
import sys

# Read in data
#W2B0 = np.loadtxt('C:/Users/Owner/OneDrive/Documents/Research/Slip Analysis/Data/W2B0_Filter.txt')
W2B0 = np.loadtxt('W2B0_Filter.txt')

# Get the first difference of desired time interval
def my_diffs(init, final):
    log_period = pd.Series(np.log((W2B0[init:final])))
    diff = log_period.diff()
    diff = diff.drop(0)
    return diff

# Clean up the times that are too close, etc.
def clean(times, tol=0.001):
    time_prev = 'Initial'
    ret = []
    for t in times[1:len(times)]:
        keep = keep_conditions(t, time_prev, tol)
        if keep:
            ret.append(t)
            time_prev = t
    return ret

def keep_conditions(t, time_prev, tol):
    keep = True
    if time_prev == 'Initial':
        if W2B0[t] > 0.02:
            keep = False
    else:
        peak = max(W2B0[time_prev:t])
        if peak-W2B0[time_prev] < tol  or peak-W2B0[t] < tol:
            keep = False
        elif W2B0[t] > 0.02:
            keep = False
        elif t-time_prev < 15:
            keep = False
    return keep

def print_run_time(init, final):
    run_time = round((final-init)/500, 0)
    text = 'Estimated time: ' + str(run_time) + ' minutes\n\n'
    sys.stdout.write(text)
    sys.stdout.flush()