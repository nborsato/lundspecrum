"""Disclaimer to anyone looking at this code. I sincerly apologise for the copy pasting if I haven't fixed it already"""

import os
from os import mkdir
import subprocess
import sys
import imp
import warnings
warnings.filterwarnings("ignore")


packages = ["PySimpleGUI", "numpy", "matplotlib", "astropy","scipy"]

def install(package):
    try:
        imp.find_module(package)
        found = True
    except ImportError:
        found = False
    if found == False:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_packages(packages):
    for package in packages:
        install(package)


check_packages(packages)

import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from astropy.io import ascii
from scipy import optimize


def output_gen():
    """Creates the output directory on the first run through"""

    directory = os.listdir()#Calls list of the directory

    #Searchs if the directory "output" is in the file. If not it will make it.
    test_element = "output"

    check_for_output = np.isin(test_element,directory)

    if check_for_output == False:
        mkdir("output")


def poly_mask(x_vals, y_vals, degree):
    """This is a polynomial fitter, its flexible now to take any order one might like.
    This code is vectorised so you just need to input the columns you want to fit.
        args:
            x_vals: the x-axis of the fitted data
            y_vals: the y-axis of the fitted data

        returns:
            polymask: the polynomial values along the xvalues fitted
    """

    # This code fits another polynomial and shifts it again so it sin't wobbly
    coeffs = np.polyfit(x_vals, y_vals, deg=degree)

    # Flips the coefficents so x^0, is the first coefficient making it correspond to i = 0
    coeffs = np.flip(coeffs)

    # Caculates the sum of all the polynomial values
    poly_vals = []
    for i in range(0, len(coeffs)):
        # Takes the coefficient of the fitted polynomial and multiples the parameter by
        ##the correct power.
        poly_val = list(coeffs[i] * np.power(x_vals, i))
        poly_vals.append(poly_val)

    # Sums all the values along the row to get the desired polynomial fit
    poly_mask = np.sum(poly_vals, axis=0)

    return poly_mask

def salsa_data_reader(file):
    """This function reads in the text files saved by the salsa instrument.
        Function prints out the header information in the terminal.
        args:
            file: the txt file for the data

        returns:
            data: an astropy table with the LSR, and Temp data
    """
    data = ascii.read(file, names =("LSR", "Temp"))

    with open(file) as f:
        lines = f.readlines()

    for i in range(0,8):
        print(lines[i])

    return data


# Helper Functions
#The Figure below draws the plotting area. This function was pulled from another tutorial
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


# \\  -------- PYPLOT -------- //


def drawChart(data):
    """This function plots the initial figure, taking the data as an argument."""

    _VARS['pltFig'] = plt.figure()

    continuum = data["Temp"].copy()
    continuum[data["Temp"] > _VARS['continuum_height']] = np.max(data["Temp"][data["Temp"] < _VARS['continuum_height']])

    plt.clf()
    plt.plot(data["LSR"],data["Temp"], 'k', label = "data") #Plots the raw data from the file
    #Plotting inital height of the continuum that can be canged
    plt.plot([data["LSR"][0],data["LSR"][-1]], [_VARS['continuum_height']]*2, linestyle = "--", color = 'k',
             label = "continuum")
    plt.plot(data["LSR"], poly_mask(data["LSR"], continuum, _VARS['polydegree']), label="polynomial fit")
    plt.legend()
    plt.xlabel("LSR")
    plt.ylabel("Temperature")
    plt.xticks(np.arange(-300, 300, step = 50))
    _VARS['fig_agg'] = draw_figure(_VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])#Draws the figure.


def removecontinuum(data, continuum_removal="False"):
    """This function updates the plotted chart in the loop."""

    _VARS['fig_agg'].get_tk_widget().forget()
    plt.clf()
    _VARS['fig_agg'] = draw_figure(_VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])

    continuum = data["Temp"].copy() #Creates a copy of the temperature info

    #This line removes any data above the continuum line
    continuum[data["Temp"] > _VARS['continuum_height']] = np.max(data["Temp"][data["Temp"] < _VARS['continuum_height']])

    if continuum_removal=="False": #If the user has not clicked continuum
        plt.plot([data["LSR"][0],data["LSR"][-1]], [_VARS['continuum_height']]*2, linestyle = "--", color = 'k',
                 label = "continuum")
        plt.plot(data["LSR"],data["Temp"], 'k', label = "data")
        plt.plot(data["LSR"],poly_mask(data["LSR"], continuum, _VARS['polydegree']), label = "polynomial fit")
        plt.legend()
        plt.xlabel("LSR")
        plt.ylabel("Temperature")
        plt.xticks(np.arange(-300, 300, step=50))

    elif continuum_removal=="True": #Once user clicks continuum remval
        data["Temp"] = data["Temp"] - poly_mask(data["LSR"], continuum, _VARS['polydegree'])
        plt.plot(data["LSR"],data["Temp"], color = 'k')
        plt.xlabel("LSR")
        plt.ylabel("Temperature")
        plt.xticks(np.arange(-300, 300, step=50))

def gaussian(x, height, center, width, offset):
    return height*np.exp(-(x - center)**2/(2*width**2)) + offset

def two_gaussians(x, h1, c1, w1, h2, c2, w2, offset):
    return three_gaussians(x, h1, c1, w1, h2, c2, w2, 0,0,1, offset)

def three_gaussians(x, h1, c1, w1, h2, c2, w2, h3, c3, w3, offset):
    return (gaussian(x, h1, c1, w1, offset=0) +
        gaussian(x, h2, c2, w2, offset=0) +
        gaussian(x, h3, c3, w3, offset=0) + offset)

def four_gaussians(x, h1, c1, w1, h2, c2, w2, h3, c3, w3, h4, c4, w4, offset):
    return (gaussian(x, h1, c1, w1, offset=0) +
            gaussian(x, h2, c2, w2, offset=0) +
            gaussian(x, h3, c3, w3, offset=0) +
            gaussian(x, h4, c4, w4, offset=0) + offset)

def five_gaussians(x, h1, c1, w1, h2, c2, w2, h3, c3, w3, h4, c4, w4, h5, c5, w5, offset):
    return (gaussian(x, h1, c1, w1, offset=0) +
            gaussian(x, h2, c2, w2, offset=0) +
            gaussian(x, h3, c3, w3, offset=0) +
            gaussian(x, h4, c4, w4, offset=0) +
            gaussian(x, h5, c5, w5, offset=0) + offset)




def gauss_plot(data, gauss_params = []):

    _VARS['fig_agg'].get_tk_widget().forget()
    plt.clf()
    _VARS['fig_agg'] = draw_figure(_VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])
    plt.plot(data["LSR"], data["Temp"], color='k')

    print("-----Peaks Estimates-----")
    print()
    print()

    if gauss_params[0] is None:
        print("Program has closed")

    elif len(gauss_params)/3 == 1:
        errfunc1 = lambda p, x, y: (gaussian(x, *p) - y) ** 2
        guess1 = [float(gauss_params[0]), float(gauss_params[1]), float(gauss_params[2]), 0]
        optim1, success = optimize.leastsq(errfunc1, guess1[:], args=(data['LSR'], data['Temp']))

        max_vr = optim1[1] + 3 * optim1[2]

        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim1[0]), float(optim1[1]), float(optim1[2]), 0), label="peak 1")
        plt.scatter(max_vr, gaussian(max_vr,optim1[0],optim1[1],optim1[2],0),facecolors='none',edgecolors='r',label="maxV_r"
                                    ,s=60)
        plt.legend()
        plt.xlabel("LSR")
        plt.ylabel("Temperature")
        plt.xticks(np.arange(-300, 300, step=50))

        print("Estimated height for peak 1 = " + str(optim1[0]))
        print("Estimated centre for peak 1 = " + str(optim1[1]))
        print("Estimated std for peak 1 = " + str(optim1[2]))
        print("-------------------------------------------------")
        print("Maximum Probable Velocity = " + str(max_vr))

    elif len(gauss_params)/3 == 2:
        errfunc2 = lambda p, x, y: (two_gaussians(x, *p) - y) ** 2
        guess2 = [float(gauss_params[0]), float(gauss_params[1]), float(gauss_params[2]),
                  float(gauss_params[3]), float(gauss_params[4]), float(gauss_params[5]), 0]
        optim2, success = optimize.leastsq(errfunc2, guess2[:], args=(data['LSR'], data['Temp']))

        variable_array = np.array([[float(optim2[0]),float(optim2[3])],
                                   [float(optim2[1]),float(optim2[4])],
                                   [float(optim2[2]),float(optim2[5])]])

        max_index = np.where(variable_array[1] == np.max(variable_array[1]))
        max_vr = variable_array[2][max_index] * 3 + variable_array[1][max_index]

        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim2[0]), float(optim2[1]), float(optim2[2]), 0), label="peak 1")
        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim2[3]), float(optim2[4]), float(optim2[5]), 0), label="peak 2")

        plt.scatter(max_vr, gaussian(max_vr, variable_array[0][max_index], variable_array[1][max_index],
                                     variable_array[2][max_index], 0), facecolors='none', edgecolors='r', label="maxV_r"
                                    ,s = 60)

        plt.legend()
        plt.xlabel("LSR")
        plt.ylabel("Temperature")
        plt.xticks(np.arange(-300, 300, step=50))

        print("Estimated height for peak 1 = " + str(optim2[0]))
        print("Estimated centre for peak 1 = " + str(optim2[1]))
        print("Estimated std for peak 1 = " + str(optim2[2]))
        print("-------------------------------------------------")
        print("Estimated height for peak 2 = " + str(optim2[3]))
        print("Estimated centre for peak 2 = " + str(optim2[4]))
        print("Estimated std for peak 2 = " + str(optim2[5]))
        print("-------------------------------------------------")
        print("Maximum Probable Velocity = " + str(max_vr[0]))

    elif len(gauss_params)/3 == 3:
        errfunc3 = lambda p, x, y: (three_gaussians(x, *p) - y) ** 2
        guess3 = [float(gauss_params[0]), float(gauss_params[1]), float(gauss_params[2]),
                  float(gauss_params[3]), float(gauss_params[4]), float(gauss_params[5]),
                  float(gauss_params[6]), float(gauss_params[7]), float(gauss_params[8]), 0]
        optim3, success = optimize.leastsq(errfunc3, guess3[:], args=(data['LSR'], data['Temp']))

        variable_array = np.array([[float(optim3[0]), float(optim3[3]), float(optim3[6])],
                                   [float(optim3[1]), float(optim3[4]), float(optim3[7])],
                                   [float(optim3[2]), float(optim3[5]), float(optim3[8])]])

        print(variable_array)
        max_index = np.where(variable_array[1] == np.max(variable_array[1]))
        max_vr = variable_array[2][max_index] * 3 + variable_array[1][max_index]

        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim3[0]), float(optim3[1]), float(optim3[2]), 0), label="peak 1")
        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim3[3]), float(optim3[4]), float(optim3[5]), 0), label="peak 2")
        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim3[6]), float(optim3[7]), float(optim3[8]), 0), label="peak 3")
        plt.scatter(max_vr, gaussian(max_vr, variable_array[0][max_index], variable_array[1][max_index],
                                     variable_array[2][max_index], 0), facecolors='none', edgecolors='r', label="maxV_r"
                                    ,s=60)
        plt.legend()
        plt.xlabel("LSR")
        plt.ylabel("Temperature")
        plt.xticks(np.arange(-300, 300, step=50))

        print("Estimated height for peak 1 = " + str(optim3[0]))
        print("Estimated centre for peak 1 = " + str(optim3[1]))
        print("Estimated std for peak 1 = " + str(optim3[2]))
        print("-------------------------------------------------")
        print("Estimated height for peak 2 = " + str(optim3[3]))
        print("Estimated centre for peak 2 = " + str(optim3[4]))
        print("Estimated std for peak 2 = " + str(optim3[5]))
        print("-------------------------------------------------")
        print("Estimated height for peak 3 = " + str(optim3[6]))
        print("Estimated centre for peak 3 = " + str(optim3[7]))
        print("Estimated std for peak 3 = " + str(optim3[8]))
        print("-------------------------------------------------")
        print("Maximum Probable Velocity = " + str(max_vr[0]))

    elif len(gauss_params)/3 == 4:
        errfunc4 = lambda p, x, y: (four_gaussians(x, *p) - y) ** 2
        guess4 = [float(gauss_params[0]), float(gauss_params[1]), float(gauss_params[2]),
                  float(gauss_params[3]), float(gauss_params[4]), float(gauss_params[5]),
                  float(gauss_params[6]), float(gauss_params[7]), float(gauss_params[8]),
                  float(gauss_params[9]), float(gauss_params[10]), float(gauss_params[11]), 0]
        optim4, success = optimize.leastsq(errfunc4, guess4[:], args=(data['LSR'], data['Temp']))

        variable_array = np.array([[float(optim4[0]), float(optim4[3]), float(optim4[6]), float(optim4[9])],
                                   [float(optim4[1]), float(optim4[4]), float(optim4[7]), float(optim4[10])],
                                   [float(optim4[2]), float(optim4[5]), float(optim4[8]), float(optim4[11])]])

        max_index = np.where(variable_array[1] == np.max(variable_array[1]))
        max_vr = variable_array[2][max_index] * 3 + variable_array[1][max_index]

        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim4[0]), float(optim4[1]), float(optim4[2]), 0), label="peak 1")
        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim4[3]), float(optim4[4]), float(optim4[5]), 0), label="peak 2")
        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim4[6]), float(optim4[7]), float(optim4[8]), 0), label="peak 3")
        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim4[6]), float(optim4[7]), float(optim4[8]), 0), label="peak 4")
        plt.scatter(max_vr, gaussian(max_vr, variable_array[0][max_index], variable_array[1][max_index],
                                     variable_array[2][max_index], 0), facecolors='none', edgecolors='r', label="maxV_r"
                                    ,s=60)
        plt.legend()
        plt.xlabel("LSR")
        plt.ylabel("Temperature")
        plt.xticks(np.arange(-300, 300, step=50))

        print("Estimated height for peak 1 = " + str(optim4[0]))
        print("Estimated centre for peak 1 = " + str(optim4[1]))
        print("Estimated std for peak 1 = " + str(optim4[2]))
        print("-------------------------------------------------")
        print("Estimated height for peak 2 = " + str(optim4[3]))
        print("Estimated centre for peak 2 = " + str(optim4[4]))
        print("Estimated std for peak 2 = " + str(optim4[5]))
        print("-------------------------------------------------")
        print("Estimated height for peak 3 = " + str(optim4[6]))
        print("Estimated centre for peak 3 = " + str(optim4[7]))
        print("Estimated std for peak 3 = " + str(optim4[8]))
        print("-------------------------------------------------")
        print("Estimated height for peak 4 = " + str(optim4[9]))
        print("Estimated centre for peak 4 = " + str(optim4[10]))
        print("Estimated std for peak 4 = " + str(optim4[11]))
        print("-------------------------------------------------")
        print("Maximum Probable Velocity = " + str(max_vr[0]))

    elif len(gauss_params)/3 == 5:
        errfunc5 = lambda p, x, y: (five_gaussians(x, *p) - y) ** 2
        guess5 = [float(gauss_params[0]), float(gauss_params[1]), float(gauss_params[2]),
                  float(gauss_params[3]), float(gauss_params[4]), float(gauss_params[5]),
                  float(gauss_params[6]), float(gauss_params[7]), float(gauss_params[8]),
                  float(gauss_params[9]), float(gauss_params[10]), float(gauss_params[11]),
                  float(gauss_params[12]), float(gauss_params[13]), float(gauss_params[14]), 0]

        optim5, success = optimize.leastsq(errfunc5, guess5[:], args=(data['LSR'], data['Temp']))

        variable_array = np.array([[float(optim5[0]), float(optim5[3]), float(optim5[6]), float(optim5[9]), float(optim5[12])],
                                   [float(optim5[1]), float(optim5[4]), float(optim5[7]), float(optim5[10]), float(optim5[13])],
                                   [float(optim5[2]), float(optim5[5]), float(optim5[8]), float(optim5[11]), float(optim5[14])]])

        max_index = np.where(variable_array[1] == np.max(variable_array[1]))
        max_vr = variable_array[2][max_index] * 3 + variable_array[1][max_index]


        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim5[0]), float(optim5[1]), float(optim5[2]), 0), label="peak 1")
        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim5[3]), float(optim5[4]), float(optim5[5]), 0), label="peak 2")
        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim5[6]), float(optim5[7]), float(optim5[8]), 0), label="peak 3")
        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim5[6]), float(optim5[7]), float(optim5[8]), 0), label="peak 4")
        plt.plot(data["LSR"],gaussian(data["LSR"], float(optim5[9]), float(optim5[10]), float(optim5[11]), 0),label="peak 5")
        plt.scatter(max_vr, gaussian(max_vr, variable_array[0][max_index], variable_array[1][max_index],
                                     variable_array[2][max_index], 0), facecolors='none', edgecolors='r', label="maxV_r"
                                    ,s=60)

        plt.legend()
        plt.xlabel("LSR")
        plt.ylabel("Temperature")
        plt.xticks(np.arange(-300, 300, step=50))

        print("Estimated height for peak 1 = " + str(optim5[0]))
        print("Estimated centre for peak 1 = " + str(optim5[1]))
        print("Estimated std for peak 1 = " + str(optim5[2]))
        print("-------------------------------------------------")
        print("Estimated height for peak 2 = " + str(optim5[3]))
        print("Estimated centre for peak 2 = " + str(optim5[4]))
        print("Estimated std for peak 2 = " + str(optim5[5]))
        print("-------------------------------------------------")
        print("Estimated height for peak 3 = " + str(optim5[6]))
        print("Estimated centre for peak 3 = " + str(optim5[7]))
        print("Estimated std for peak 3 = " + str(optim5[8]))
        print("-------------------------------------------------")
        print("Estimated height for peak 4 = " + str(optim5[9]))
        print("Estimated centre for peak 4 = " + str(optim5[10]))
        print("Estimated std for peak 4 = " + str(optim5[11]))
        print("-------------------------------------------------")
        print("Estimated height for peak 5 = " + str(optim5[12]))
        print("Estimated centre for peak 5 = " + str(optim5[13]))
        print("Estimated std for peak 5 = " + str(optim5[14]))
        print("-------------------------------------------------")
        print("Maximum Probable Velocity = " + str(max_vr[0]))

def gaussian_fit():
    layout = [[sg.Text("Number of Peaks", key="Peak_Num"), sg.InputText()],
              [sg.Submit()]]

    window = sg.Window("Gaussian Fit", layout, modal=True)
    choice = None
    event, values = window.read()
    peak_number = int(values[0])
    count = 0 #making the window only update once
    window.close()
    while True:
        event, values = window.read()

        if peak_number == 1:
            layout = [[sg.Text('Height 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Submit()]]

        elif peak_number == 2:
            layout = [[sg.Text('Height 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Text('Height 2', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 2', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 2', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Submit()]]

        elif peak_number == 3:
            layout = [[sg.Text('Height 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Text('Height 2', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 2', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 2', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Text('Height 3', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 3', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 3', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Submit()]]

        elif peak_number == 4:
            layout = [[sg.Text('Height 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Text('Height 2', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 2', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 2', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Text('Height 3', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 3', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 3', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Text('Height 4', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 4', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 4', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Submit()]]

        elif peak_number == 5:
            layout = [[sg.Text('Height 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 1', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Text('Height 2', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 2', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 2', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Text('Height 3', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 3', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 3', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Text('Height 4', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 4', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 4', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Text('Height 5', size=(10, 1)), sg.InputText()],
                      [sg.Text('Center 5', size=(10, 1)), sg.InputText()],
                      [sg.Text('Width 5', size=(10, 1)), sg.InputText()],
                      [sg.Text('--------------------------------------')],
                      [sg.Submit()]]

        if count == 0:
            window = sg.Window("Gaussian Fit", layout, modal=True)
        count = 1

        event, values = window.read()

        if values == None:
            save_vals = save_vals

        else:
            save_vals = list(values.values())

        gauss_plot(data, save_vals)


        if event == sg.WIN_CLOSED:
            break

    window.close()


def updateData(val):
    #If the polynomial slider is changed this will update the value
    _VARS['polydegree'] = val
    removecontinuum(data)

def updateContinuum(val):
    #If the continuum hieght is changed this will update the value
    _VARS["continuum_height"] = val
    removecontinuum(data)


def save_files(data):
    layout = [[sg.Text("New Window", key="new")],
              [sg.Text('Name of the data and image file.')],
              [sg.Text('File Name:', size =(15, 1)), sg.InputText()],
              [sg.Submit()]]
    window = sg.Window("Save Window", layout, modal=True)
    choice = None
    while True:
        event, values = window.read()

        if values != None:
            output_gen() #Will create the output file if it does not exist.
            file_name = "output/" + values[0] + ".csv"
            print(file_name)
            plt.savefig("output/" + values[0])
            ascii.write(data,"output/" + values[0] + ".csv",overwrite=True)

            break

        if event == "Exit" or event == sg.WIN_CLOSED:
            break

    window.close()



def file_selector():
    """Function enables the user to select the txt files that they have downloaded.

        returns:
            """

    layout = [[sg.Text("Choose a file: "),sg.Input(key="-IN2-" ,change_submits=True), sg.FileBrowse(key="-IN-")],
              [sg.Button("Submit")]]

    window = sg.Window("File Window", layout, modal=True)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == "Submit":
            file = values["-IN-"]
            break
    window.close()

    return file

# \\  -------- PYPLOT -------- //


# \\  -------- PYSIMPLEGUI -------- //
#Current file being used need to write code so the user can input their own
data = salsa_data_reader(file_selector())

""" Below are the global variable that the GUI controls. Main ones to consider are polydegree and continuum_height."""
# VARS CONSTS:
_VARS = {'window': False,
         'fig_agg': False,
         'pltFig': False,
         'polydegree': 10,
         'continuum_height': int(np.median(data["Temp"]))}


plt.style.use('Solarize_Light2')


#Setting font parameters
AppFont = 'Any 16'
SliderFont = 'Any 14'
sg.theme('black')

#Layout features contain all the elements in thee GUI
"""At the moment the gui creates a plot of the data, the height of the continuum, and the polynomial fit of the
continuum that needs to be subtracted. Buttons control wether or not the continuum is removed"""

layout = [[sg.Canvas(key='figCanvas', background_color='#FDF6E3')],
          [sg.Text(text="Polynomial Order :",
                   font=SliderFont,
                   background_color='#FDF6E3',
                   pad=((0, 0), (10, 0)),
                   text_color='Black'),
           sg.Slider(range=(0, 20), orientation='h', size=(34, 20),
                     default_value=_VARS['polydegree'],
                     background_color='#FDF6E3',
                     text_color='Black',
                     key='-Slider-',
                     enable_events=True),
           sg.Button('Remove Continuum',
                     font=AppFont,
                     pad=((4, 0), (10, 0)))],
          # pad ((left, right), (top, bottom))

          [sg.Text(text="Continuum Height :",
                   font=SliderFont,
                   background_color='#FDF6E3',
                   pad=((0, 0), (10, 0)),
                   text_color='Black'),
           sg.Slider(range=(int(np.min(data["Temp"])), int(np.max(data["Temp"]))), orientation='h', size=(34, 20),
                     default_value=_VARS['continuum_height'],
                     background_color='#FDF6E3',
                     text_color='Black',
                     key='-Contfit-',
                     enable_events=True),
           sg.Text(text="                               ------      ",
                   font=SliderFont,
                   background_color='#FDF6E3',
                   pad=((0, 0), (10, 0)),
                   text_color='Black')
           ],
          [sg.Button("Fit Gaussians",font=AppFont, key="gauss_fit")],
          [sg.Button("Save Image and Data", font=AppFont, key="save_data", pad=((0, 0), (0, 0)))]]

_VARS['window'] = sg.Window('Lund Spectrum',
                            layout,
                            finalize=True,
                            resizable=True,
                            location=(100, 100),
                            element_justification="center",
                            background_color='#FDF6E3')

# \\  -------- PYSIMPLEGUI -------- //

drawChart(data)

while True:
    event, values = _VARS['window'].read(timeout=200)
    if event == sg.WIN_CLOSED:
        break
    elif event == 'Resample':
        removecontinuum(data)
    elif event == '-Slider-':
        updateData(int(values['-Slider-']))
    elif event == '-Contfit-':
        updateContinuum(int(values['-Contfit-']))
    elif event == 'Remove Continuum':
        removecontinuum(data, "True")
    elif event == "save_data":
        save_files(data)
    elif event == "gauss_fit":
        gaussian_fit()

_VARS['window'].close()


