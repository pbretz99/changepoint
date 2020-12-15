# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 16:23:34 2020

@title: Main Script for Changepoint Detection
@author: Philip Bretz
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import changepoint as cp
import utilities as ut
import sys

# Read in data
#W2B0 = np.loadtxt('C:/Users/Owner/OneDrive/Documents/Research/Slip Analysis/Data/W2B0_Filter.txt')
W2B0 = np.loadtxt('W2B0_Filter.txt')

text = 'This is my program for changepoint detection '
text += 'along the filtered W_2 curve.\n'
text += 'Note: the program takes about 2 min. per 1000 frames.\n'
sys.stdout.write(text)
sys.stdout.flush()

active = True
first_iter = True
while active:
    if first_iter:
        previous_record = input('Examine previous results? Y/N: ')
        examine_previous = False
        if previous_record == 'Y':
            if os.path.exists('regime_times.txt'):
                with open('regime_times.txt', 'r') as filehandle:
                    times = [int(current_time.rstrip()) for current_time in filehandle.readlines()]
            else:
                sys.stdout.write('No saved previous results exist. Exiting program.')
                break
            init = times[0]
            if len(times) > 1:
                final = times[-1] + 10
            else:
                final = init + 100
            final = min(final, len(W2B0))
            examine_previous = True
        else:
            init = int(input('Input the initial time: '))
            if init < 0 or init > len(W2B0):
                sys.stdout.write('Invalid initial time. Exiting program.')
                break
            final = int(input('Input the final time: '))
            if final <= init or final > len(W2B0):
                sys.stdout.write('Invalid final time. Exiting program.')
                break
            ut.print_run_time(init, final)
    else:
        init = int(input('Input the initial time: '))
        if init < 0 or init > len(W2B0):
            sys.stdout.write('Invalid initial time. Exiting program.')
            break
        final = int(input('Input the final time: '))
        if final <= init or final > len(W2B0):
            sys.stdout.write('Invalid final time. Exiting program.')
            break
        ut.print_run_time(init, final)
    # Running the algorithm
    first_diff = ut.my_diffs(init, final)
    if not examine_previous or not first_iter:
        prior = cp.Prior('Scaled Inverse Chi Squared', [10, 0.2])
        model = cp.Model(prior, '1/100')
        times = cp.changepoint(first_diff.to_numpy(),
                               model, 
                               300, 
                               init)
    # Cleaning up the extraneous times
    clean_times = input('Clean up extraneous times? Y/N: ')
    if clean_times == 'Y':
        times = ut.clean(times)
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
    first_iter = False