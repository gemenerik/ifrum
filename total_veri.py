# -*- coding: utf-8 -*-
"""
Created on Sat May 30 15:14:27 2020

@author: lrfoo
"""


import matplotlib.pyplot as plt
import csv
import numpy as np


with open('veri1.csv', newline='') as f:
    reader = csv.reader(f)
    total_optimize = list(reader)
    
data = total_optimize
rR = np.zeros(len(data))


# runway count

for i in range(len(data)):
    rR[i] = sum((itm.count("noise_r_") for itm in data[i]))

runwayRight = sum(rR)
runwayLeft = 100-runwayRight


fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.set_ylabel('Number of aircraft')
ax.set_title('Runway usage by aircraft number')
runways = ['Left runway', 'Right runway']
numbers= [runwayLeft,runwayRight]
ax.bar(runways,numbers)
plt.show()