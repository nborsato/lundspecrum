import numpy as np
from astropy.io import fits
from matplotlib import pyplot as plt


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


plt.plot(spectra)

continuum = spectra
continuum[spectra>7] = np.max(spectra[spectra<7])
x_vals = np.linspace(np.min(continuum), np.max(continuum), len(continuum))

cont_poly = poly_mask(x_vals, continuum, 3)


plt.plot(continuum)
plt.plot(cont_poly)

plt.show()