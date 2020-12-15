# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 12:25:15 2020

@title: Utilities
@author: Philip Bretz
"""

import matplotlib.pyplot as plt
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
def clean(times, d_min, w2_max, tol=0.001):
    time_prev = 'Initial'
    ret = [times[0]]
    for t in times[1:(len(times)-1)]:
        keep = keep_conditions(t, time_prev, d_min, w2_max, tol)
        if keep:
            ret.append(t)
            time_prev = t
    ret.append(times[-1])
    return ret

# Remove times that do not have a peak between them,
# are too large, or are too close together
def keep_conditions(t, time_prev, d_min, w2_max, tol):
    keep = True
    if time_prev == 'Initial':
        if W2B0[t] > w2_max:
            keep = False
    else:
        peak = max(W2B0[time_prev:t])
        if peak-W2B0[time_prev] < tol  or peak-W2B0[t] < tol:
            keep = False
        elif W2B0[t] > w2_max:
            keep = False
        elif t-time_prev < d_min:
            keep = False
    return keep

def print_run_time(init, final):
    run_time = round((final-init)/500, 0)
    text = 'Estimated time: ' + str(run_time) + ' minutes\n\n'
    sys.stdout.write(text)
    sys.stdout.flush()

# Plot marked changepoints on W2 curve
def changepoint_plot(times, interval):
    left, right = interval[0], interval[1]
    fig = plt.figure(figsize=(8, 6))
    plt.plot(range(left, right), W2B0[left:right])
    plt.xlabel('Time')
    plt.ylabel('W2 (filtered)')
    plt.title('Detected Regime Change(s)')
    if len(times) > 2:
        for t in times[1:(len(times)-1)]:
            if t <= right and t >= left:
                plt.axvline(x=t, color='Blue', ls='--')
    plt.show()
    return fig