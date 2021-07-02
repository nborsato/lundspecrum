#import numpy as np
#from astropy.io import fits
import os

import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from astropy.io import ascii
from os import listdir, mkdir, path


import warnings
warnings.filterwarnings("ignore")

def output_gen():
    """Creates the output directory on the first run through>"""

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
    _VARS['fig_agg'] = draw_figure(
        _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])#Draws the figure.


def removecontinuum(data, continuum_removal="False"):
    """This function updates the plotted chart in the loop."""

    _VARS['fig_agg'].get_tk_widget().forget()
    plt.clf()
    _VARS['fig_agg'] = draw_figure(
        _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])

    continuum = data["Temp"].copy() #Creates a copy of the temperature info

    #This line removes any data above the continuum line
    continuum[data["Temp"] > _VARS['continuum_height']] = np.max(data["Temp"][data["Temp"] < _VARS['continuum_height']])

    if continuum_removal=="False": #If the user has not clicked continuum
        plt.plot([data["LSR"][0],data["LSR"][-1]], [_VARS['continuum_height']]*2, linestyle = "--", color = 'k',
                 label = "continuum")
        plt.plot(data["LSR"],data["Temp"], 'k', label = "data")
        plt.plot(data["LSR"],poly_mask(data["LSR"], continuum, _VARS['polydegree']), label = "polynomial fit")
        plt.legend()

    elif continuum_removal=="True": #Once user clicks continuum remval
        data["Temp"] = data["Temp"] - poly_mask(data["LSR"], continuum, _VARS['polydegree'])
        plt.plot(data["LSR"],data["Temp"], color = 'k')


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
    window = sg.Window("Second Window", layout, modal=True)
    choice = None
    while True:
        event, values = window.read()

        if values != None:
            output_gen() #Will create the output file if it does not exist.
            file_name = "output/" + values[0] + ".csv"
            print(file_name)
            plt.savefig("output/" + values[0])
            ascii.write(data,"output/" + values[0] + ".csv",overwrite=True)


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
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event == "Submit":
            file = values["-IN-"]
            break
    return file

    #while True:
        #event, values = window.read()

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
          [sg.Button("Open Window", key="open")],
          [sg.Button('Exit', font=AppFont, pad=((540, 0), (0, 0)))]]

_VARS['window'] = sg.Window('Random Samples',
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
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == 'Resample':
        removecontinuum(data)
    elif event == '-Slider-':
        updateData(int(values['-Slider-']))
    elif event == '-Contfit-':
        updateContinuum(int(values['-Contfit-']))
    elif event == 'Remove Continuum':
        removecontinuum(data, "True")
    elif event == "open":
        save_files(data)

_VARS['window'].close()


