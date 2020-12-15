# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 16:23:34 2020

@title: Main Script for Changepoint Detection
@author: Philip Bretz
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import changepoint as cp
import sys
import time

# Read in data
W2B0 = np.loadtxt('C:/Users/Owner/OneDrive/Documents/Research/Slip Analysis/Data/W2B0_Filter.txt')

# Get the first difference of desired time interval
def my_diffs(init, final):
    log_period = pd.Series(np.log((W2B0[init:final])))
    diff = log_period.diff()
    diff = diff.drop(0)
    return diff

# Clean up the times that are too close, etc.
def clean(times, tol=0.001):
    time_prev = times[1]
    ret = []
    for t in times[2:len(times)]:
        peak = max(W2B0[time_prev:t])
        keep = True
        if peak-W2B0[time_prev] < tol  or peak-W2B0[t] < tol:
            keep = False
        elif W2B0[t] > 0.02:
            keep = False
        elif t-time_prev < 15:
            keep = False
        if keep:
            ret.append(t)
            time_prev = t
        return ret

text = 'This is my program for changepoint detection '
text += 'along the filtered W_2 curve.\n'
text += 'Note: the program takes about 2 min. per 1000 frames.\n'
sys.stdout.write(text)
sys.stdout.flush()

active = True
while active:
    init = int(input('Input the initial time: '))
    if init < 0 or init > len(W2B0):
        sys.stdout.write('Invalid initial time. Exiting program.')
        break
    final = int(input('Input the final time: '))
    if final <= init or final > len(W2B0):
        sys.stdout.write('Invalid final time. Exiting program.')
        break
    run_time = round((final-init)/500, 0)
    text = 'Estimated time: ' + str(run_time) + ' minutes\n\n'
    sys.stdout.write(text)
    sys.stdout.flush()
    # Running the algorithm
    first_diff = my_diffs(init, final)
    prior = cp.Prior('Scaled Inverse Chi Squared', [10, 0.2])
    model = cp.Model(prior, '1/100')
    times = cp.changepoint(first_diff.to_numpy(),
                           model, 
                           300, 
                           init)
    # Cleaning up the extraneous times
    #times = clean(times)
    # Plotting the changepoints
    plot = input('View plot with marked changepoints? Y/N: ')
    if plot == 'Y':
        fig = plt.figure(figsize=(8, 6))
        plt.plot(range(init, final), W2B0[init:final])
        plt.xlabel('Time')
        plt.ylabel('W2 (filtered)')
        plt.title('Detected Regime Change(s)')
        if times:
            for t in times:
                plt.axvline(x=t, color='Blue', ls='--')
        plt.show()
        save = input('Save plot? Y/N: ')
        if save == 'Y':
            filename = input('Enter filename for saving plot: ')
            fig.savefig(filename)
    # Save times to text file
    save = input('Save changepoint times? Y/N: ')
    if save == 'Y':
        with open('regime_times.txt', 'w') as filehandle:
            for listitem in times:
                filehandle.write('%s\n' % listitem)
    # Repeat or break
    again = input('Perform changepoint detection again with different times? Y/N: ')
    if again != 'Y':
        sys.stdout.write('Program exiting.')
        break