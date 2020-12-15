# changepoint
Detect changepoints in W_2 distances.

The program applies a Bayesian approach to changepoint detection. By examining, for each frame, the posterior probability of the length of the current regime, the algorithm marks frames when the highest probability run length is 0. I.e., it locates frames that have a high likelihood of being the beginning of a new regime; the changepoint frames.

The changepoint.py code is made to be fairly flexible. Different priors can be added when looking at different data and various parameters can be altered. However, the main.py code is tailored to the W_2 distances. Specifically, we look for changes in the variance of the first difference of the logarithm of the W_2 curve. The first difference of the logarithm of the W_2 curve is roughly normally distributed around 0 with major changes in variance that precede slip events.

To run the program, save all the files to a single folder and just run main.py. The program has limited user interaction, allowing you to specify which frames from the W_2 file you want to run the changepoint detection on. It also allows you to save the detected changepoints to a text file for later examination (since the program takes about 2 minutes per 1000 frames).
