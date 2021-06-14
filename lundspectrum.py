import numpy as np
from astropy.io import fits
import PySimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def poly_mask(x_vals, y_vals, degree):
    """This is a polynomial fitter, its flexible now to take any order one might like.
    This code is vectorised so you just need to input the columns you want to fit."""

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


file = "/Users/nicholasborsato/Documents/Lund_Files/Teaching/Labs/ASTA33/spectrum_33229.fits"

hdul = fits.open(file)
spectra = hdul[0].data
spectra = spectra[0][0]


continuum = spectra.copy()
continuum[spectra>7] = np.max(spectra[spectra<7])
x_vals = np.linspace(np.min(continuum), np.max(continuum), len(continuum))

cont_poly = poly_mask(x_vals, continuum, 3)


# VARS CONSTS:
# Upgraded dataSize to global...
_VARS = {'window': False,
         'fig_agg': False,
         'pltFig': False,
         'dataSize': 60}


plt.style.use('Solarize_Light2')

# Helper Functions

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


# \\  -------- PYSIMPLEGUI -------- //

AppFont = 'Any 16'
SliderFont = 'Any 14'
sg.theme('black')

# New layout with slider and padding

layout = [[sg.Canvas(key='figCanvas', background_color='#FDF6E3')],
          [sg.Text(text="Random sample size :",
                   font=SliderFont,
                   background_color='#FDF6E3',
                   pad=((0, 0), (10, 0)),
                   text_color='Black'),
           sg.Slider(range=(0, 10), orientation='h', size=(34, 20),
                     default_value=_VARS['dataSize'],
                     background_color='#FDF6E3',
                     text_color='Black',
                     key='-Slider-',
                     enable_events=True),
           sg.Button('Resample',
                     font=AppFont,
                     pad=((4, 0), (10, 0)))],
          # pad ((left, right), (top, bottom))
          [sg.Button('Exit', font=AppFont, pad=((540, 0), (0, 0)))],
          [sg.Button("Remove Continuum")]]

_VARS['window'] = sg.Window('Random Samples',
                            layout,
                            finalize=True,
                            resizable=True,
                            location=(100, 100),
                            element_justification="center",
                            background_color='#FDF6E3')

# \\  -------- PYSIMPLEGUI -------- //


# \\  -------- PYPLOT -------- //


def makeSynthData():
    xData = np.random.randint(100, size=_VARS['dataSize'])
    yData = np.linspace(0, _VARS['dataSize'],
                        num=_VARS['dataSize'], dtype=int)
    return (xData, yData)


def drawChart(spectra):
    _VARS['pltFig'] = plt.figure()
    #dataXY = makeSynthData()
    plt.clf()
    plt.plot(spectra, 'k')
    _VARS['fig_agg'] = draw_figure(
        _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])


def updateChart(spectra,continuum_removal="False"):
    _VARS['fig_agg'].get_tk_widget().forget()
    #dataXY = makeSynthData()
    # plt.cla()
    plt.clf()
    plt.plot(spectra, 'k')
    plt.plot(poly_mask(x_vals, continuum, _VARS['dataSize']))
    _VARS['fig_agg'] = draw_figure(
        _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])

    if continuum_removal == "True":
        spectra = spectra - poly_mask(x_vals, continuum, _VARS['dataSize'])
        plt.plot(spectra)


def updateData(val):
    _VARS['dataSize'] = val
    updateChart(spectra)

# \\  -------- PYPLOT -------- //


drawChart(spectra)

# MAIN LOOP
while True:
    event, values = _VARS['window'].read(timeout=200)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == 'Resample':
        updateChart(spectra)
    elif event == '-Slider-':
        updateData(int(values['-Slider-']))
    elif event == 'Remove Continuum':
        updateChart(spectra,"True")

_VARS['window'].close()