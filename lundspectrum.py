import numpy as np
from astropy.io import fits
from matplotlib import pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib


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

#plt.plot(spectra)
#plt.plot(continuum)
#plt.plot(cont_poly)

#plt.show()


fig = matplotlib.figure.Figure(figsize=(8, 5))
fig.add_subplot(111).plot(spectra)
#fig.add_subplot(111).plot(continuum)
#fig.add_subplot(111).plot(cont_poly)

matplotlib.use("TkAgg")

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

# Define the window layout
layout = [
    [sg.Text("Plot test")],
    [sg.Canvas(key="-CANVAS-")],
    [sg.Button("Ok")],
    [sg.Button("PP")],
]

# Create the form and show it without the plot
window = sg.Window(
    "Matplotlib Single Graph",
    layout,
    location=(0, 0),
    finalize=True,
    element_justification="center",
    font="Helvetica 18",
)

# Add the plot to the window


while True:
    draw_figure(window["-CANVAS-"].TKCanvas, fig)

    event, values = window.read()


    if event == "PP":
        fig = matplotlib.figure.Figure(figsize=(8, 5))
        fig.add_subplot(111).plot(spectra)
        fig.add_subplot(111).plot(cont_poly)
        draw_figure(window["-CANVAS-"].TKCanvas, fig)

    elif event == "Ok" or event == sg.WIN_CLOSED:
        break



window.close()