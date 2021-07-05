#import numpy as np
#from astropy.io import fits
import os

import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from astropy.io import ascii
from os import listdir, mkdir, path
from scipy import optimize

file = "/Users/nicholasborsato/lundspectrum/output/test.csv"

data = ascii.read(file, names =("LSR", "Temp"))
#plt.plot(data['LSR'], data['Temp'])
#plt.show()

def gaussian(x, height, center, width, offset):
    return height*np.exp(-(x - center)**2/(2*width**2)) + offset
def three_gaussians(x, h1, c1, w1, h2, c2, w2, h3, c3, w3, offset):
    return (gaussian(x, h1, c1, w1, offset=0) +
        gaussian(x, h2, c2, w2, offset=0) +
        gaussian(x, h3, c3, w3, offset=0) + offset)

def two_gaussians(x, h1, c1, w1, h2, c2, w2, offset):
    return three_gaussians(x, h1, c1, w1, h2, c2, w2, 0,0,1, offset)

errfunc3 = lambda p, x, y: (three_gaussians(x, *p) - y)**2
errfunc2 = lambda p, x, y: (two_gaussians(x, *p) - y)**2

guess3 = [15, 0, 20, 0.6, 0.61, 0.01, 1, 0.64, 0.01, 0]  # I guess there are 3 peaks, 2 are clear, but between them there seems to be another one, based on the change in slope smoothness there
guess2 = [0.49, 0.55, 0.01, 1, 0.64, 0.01, 0]  # I removed the peak I'm not too sure about
optim3, success = optimize.leastsq(errfunc3, guess3[:], args=(data["LSR"], data["Temp"]))
optim2, success = optimize.leastsq(errfunc2, guess2[:], args=(data["LSR"], data["Temp"]))
optim3

plt.plot(data["LSR"], data["Temp"], lw=1, label='measurement')
plt.plot(data["LSR"], three_gaussians(data["LSR"], *optim3),
    lw=3, c='b', label='fit of 3 Gaussians')
plt.plot(data["LSR"], two_gaussians(data["LSR"], *optim2),
    lw=1, c='r', ls='--', label='fit of 2 Gaussians')
plt.legend(loc='best')
plt.show()

#print(data)