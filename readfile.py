# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 19:58:33 2020

@author: lrfoo
"""

import matplotlib.pyplot as plt
import csv 

with open('model.sol', newline='\n') as csvfile:
    reader = csv.reader((line.replace('  ', ' ') for line in csvfile), delimiter=' ')
    next(reader)  # skip header
    sol = {}
    for var, value in reader:
        sol[var] = float(value)
    print(sol)


## Variables & plotting
fuel_level = sol["total_fuel_burned"]
noise_level = sol["total_noise"]     
left_runway = sol["noise_r_94"]

foodict = {k: v for k, v in sol.items() if k.startswith('noise_l')}
runway_left=len({x:y for x,y in foodict.items() if y!=0})
runway_right=len(foodict)-runway_left

fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.set_ylabel('Number of aircraft')
ax.set_title('Runway usage by aircraft number')
runways = ['Left runway', 'Right runway']
numbers= [runway_left,runway_right]
ax.bar(runways,numbers)
plt.show()



