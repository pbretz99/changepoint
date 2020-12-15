# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 12:19:31 2020

@title: Changepoint Detection
@author: Philip Bretz
"""

'''Note: the code, especially the methods for Prior,
are designed for numpy arrays. I.e., the input of 
changepoint() needs to be a numpy array.'''

import numpy as np
from scipy.stats import t

##################
# Useful classes #
##################

# Create class for a few different priors
# Methods for updating and predictive evaluation
class Prior:
    def __init__(self, kind, params):
        self.kind = kind
        self.params = params
        
    def update(self, x):
        if x.size == 0:
            return self.params
        if self.kind == 'Inverse Gamma':
            sumsq = sum(map(lambda i : i * i, x))
            a_new = self.params[0] + len(x)/2
            b_new = self.params[1] + sumsq/2
            return [a_new, b_new]
        elif self.kind == 'Scaled Inverse Chi Squared':
            sumsq = sum(map(lambda i : i * i, x))
            nu_new = self.params[0] + len(x)
            s2_new = (self.params[1]*self.params[1] + sumsq)/(self.params[0] + len(x))
            return [nu_new, s2_new]
        else:
            print('Prior has not been assigned a valid kind.')
            return 0
    
    def predictive(self, x_new, x=np.empty(shape=(0,0))):
        params = self.update(x)
        if self.kind == 'Inverse Gamma':
            pred = t.pdf(x_new, 2*params[0], 0, (params[1]/params[0]) ** 0.5)
        if self.kind == 'Scaled Inverse Chi Squared':
            pred = t.pdf(x_new, params[0], 0, params[1] ** 0.5)
        return pred

# Create class for model
class Model:
    def __init__(self, prior, hazard):
        self.prior = prior
        self.hazard = hazard
    
    def evaluate(self, x):
        return 1/100
    '''For a more complete program, I would have
    the option for an actual hazard function, or 
    at least allow the memoryless parameter to be
    chosen by the user.'''

#######################################
# The changepoint detection algorithm #
#######################################
def changepoint(x, model, cap, shift):
    # Initialize
    times = [shift]
    prev_run_probs = [0]*(cap+1)
    prev_run_probs[0] = 1
    for i in range(1, len(x)):
        new_run_probs = [0]*(cap+1)
        max_time = min(i, cap-2)
        min_time = max(0, i-cap)
        # Evaluate predictive probabilities
        pred = predictive(x[min_time:(i+1)], model)
        # Calculate changepoint probability
        new_run_probs[0] = cp_prob(max_time, prev_run_probs, pred, model)
        # Calculate growth probabilities
        for s in range(1,max_time+2):
            new_run_probs[s] = growth_prob(s, prev_run_probs[s-1], pred[s-1], model)
        # Truncate very small probabilities and re-normalize
        new_run_probs = truncate(new_run_probs)
        # Run changepoint detection
        new_time = detect(i,
                          new_run_probs,
                          prev_run_probs, 
                          times,
                          cap,
                          shift)
        if new_time:
            # Ignore when 'detected' changepoint is an artifact of hitting the cap
            if new_time == 'Reset':
                new_run_probs = [0]*(cap+1)
                new_run_probs[0] = 1
            # Otherwise, record time of changepoint
            else:
                times.append(new_time)
        # Reset run probabilities
        prev_run_probs = new_run_probs
    return times

# Predictive evaluation function
# Takes in data and returns predictive evaluation for each run length
# index i of output corresponds to run length of i
def predictive(x, model):
    pred = []
    pred.append(model.prior.predictive(x[-1]))
    if len(x) == 1:
        return pred
    for i in range(2,len(x)+1):
        p = model.prior.predictive(x[-1], x[-i:-1])
        pred.append(p)
    return pred

# Changepoint probability function
def cp_prob(max_time, prev_probs, pred, model):
    cp = 0
    for i in range(max_time):
        cp += prev_probs[i] * pred[i] * model.evaluate(i)
    return cp

# Growth probabilities function
def growth_prob(t, prob, pred, model):
    gp = prob * pred * (1-model.evaluate(t))
    return gp

# Remove small probabilities and re-normalize
def truncate(probs, tol=0.00001):
    ret = []
    for prob in probs:
        if prob < tol:
            ret.append(0)
        else:
            ret.append(prob)
    ret = ret/sum(ret)
    return ret

'''Detect changepoints given array of run probabilities
Location of maximum probability density during a given regime
should increase by 1 every time step; detect when this does not
occur (with a given tolerance). Additionally, to make sure
it only finds new runs, look for new most likely run time 
less than buffer. Also, when spurious changepoints are located
when the run hits the cap, mark for reset.'''

def detect(i, new_probs, prev_probs, times, cap, shift=0, tol=5, buffer=10):
    new_time = []
    #current_max_loc = new_probs.index(max(new_probs))
    #prev_max_loc = prev_probs.index(max(prev_probs))
    current_max_loc = np.argmax(new_probs)
    prev_max_loc = np.argmax(prev_probs)
    if cap-prev_max_loc < 3:
        return 'Reset'
    diff = abs(prev_max_loc-(current_max_loc-1))
    true_location = i-current_max_loc+shift
    new = True
    for time in times:
        if abs(true_location-time) < tol:
            new = False
    if diff > tol and current_max_loc < buffer and new:
        new_time = true_location
    return new_time