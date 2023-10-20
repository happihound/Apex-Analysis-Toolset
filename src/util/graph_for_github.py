import matplotlib.pyplot as plt
import csv
import numpy as np
from scipy.signal import savgol_filter

from src.playerKillTracker import KillTracker

# Use the dark background style
plt.style.use('dark_background')

x = []
y = []
headers = []
filename = 'zone timer.csv'
with open('outputData/'+filename, 'r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    # get the first line of the csv file, which is the headers
    headers = next(plots)
    for row in plots:
        x.append(int(float(row[0]))*1.58)
        y.append(int(float(row[1])))

# Plot with a specific line color and style for better visibility
plt.plot(x, y, color='cyan', linestyle='-', linewidth=2)
plt.xlabel("Time (seconds)", color='white')
plt.ylabel(headers[1], color='white')
plt.xticks(np.arange(0, max(x), max(x)/10, dtype=int), color='white')
plt.xlim([0, max(x)])
plt.yticks(np.arange(0, max(y), max(y)*0.1, dtype=int), color='white')

# Add a grid for better readability
plt.grid(color='gray', linestyle='--', linewidth=0.5)
plt.title(filename, color='white')
plt.show()
plt.pause(99999)
