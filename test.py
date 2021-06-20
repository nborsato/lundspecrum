from astropy.io import ascii
import matplotlib.pyplot as plt

table = "/Users/nicholasborsato/Documents/Lund_Files/Teaching/Labs/ASTA33/Radio lab/Test/Test_Data_2020/Obs_1.txt"

def salsa_data_reader(file):

    data = ascii.read(table, names =("LSR", "Temp"))

    #print(data.description)

    with open(table) as f:
        lines = f.readlines()

    for i in range(0,8):
        print(lines[i])

    return data

data = salsa_data_reader(table)
plt.plot(data["LSR"], data["Temp"])
plt.show()