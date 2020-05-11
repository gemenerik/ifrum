# complete revision of linear programming model, more true to paper
# largest change is removal of an optimal ordering system, this is not explicitly implemented in the paper, although
# the author mentions that it is implicit in the objective function.

import pandas as pd
import numpy as np


flights_input = pd.read_csv('flights_input.csv')

""" OBJECTIVE FUNCTION """
# variables
optimization_function = 'total_fuel_burned'

# write
file = open('ifrum.lp', 'w')
file.write('Minimize\n')
file.write('  ' + optimization_function+'\n')
file.write('\n')
file.write('Subject To\n')


""" FUEL """
# variables
approach_left_distance = 10000      # m
approach_right_distance = 20000     # m

mass_flow_medium = 2
mass_flow_heavy = 3

velocity_approach_medium = 72       # m/s
velocity_approach_heavy = 82        # m/s

time_resolution = 10
max_time_slot_shift = 500
runway_list = ['l', 'r']

total_fuel_burned_left_medium = mass_flow_medium * approach_left_distance / velocity_approach_medium
total_fuel_burned_left_heavy = mass_flow_heavy * approach_left_distance / velocity_approach_heavy
total_fuel_burned_right_medium = mass_flow_medium * approach_right_distance / velocity_approach_medium
total_fuel_burned_right_heavy = mass_flow_heavy * approach_right_distance / velocity_approach_heavy

# write
file.write('  fuel: -total_fuel_burned ')
for i in range(len(flights_input.index)):
    if flights_input['Weight class'] .iloc[i] == 'H':
        file.write('+ ' + str(mass_flow_heavy) + ' delay_' + str(i+1) + ' ')
    elif flights_input['Weight class'] .iloc[i] == 'M':
        file.write('+ ' + str(mass_flow_medium) + ' delay_' + str(i+1) + ' ')
    else:
        print('Error - aircraft class not found')
file.write('= 0\n')

for lead_idx in range(len(flights_input.index)):
    time_original = flights_input['Time'].iloc[lead_idx]
    file.write('  delayerino_' + str(lead_idx) + ': ')
    for j in range(max_time_slot_shift):
        for runway in runway_list:
            time_slot = time_original + j * time_resolution
            file.write(' + ' + str(time_slot) + ' x_' + str(lead_idx + 1) + '_' + runway + '_' + str(time_slot))
    file.write(' - delay_' + str(lead_idx+1) + ' = ' + str(time_original) + '\n')


""" FLIGHT ASSIGNMENT """
# write
for i in range(len(flights_input.index)):
    file.write('  assignment_' + str(i+1) + ': ')
    time_original = flights_input['Time'] .iloc[i]
    flag = True
    for runway in runway_list:
        for time_slot in range(time_original, time_original + max_time_slot_shift * time_resolution, time_resolution):
            if flag:
                file.write('x_' + str(i+1) + '_' + runway + '_' + str(time_slot))
            else:
                file.write(' + x_' + str(i + 1) + '_' + runway + '_' + str(time_slot))
            flag = False
    file.write(' = 1\n')


""" RUNWAY OCCUPATION """
# dependency matrices
separation_heavy_heavy = 113
separation_heavy_medium = 181
separation_medium_heavy = 87
separation_medium_medium = 100

dependency_tensor = []
for lead_idx in range(len(flights_input.index)):
    lead_class = flights_input['Weight class'] .iloc[lead_idx]
    lead_time_original = flights_input['Time'].iloc[lead_idx]
    lead_matrix = []
    for follow_idx in range(len(flights_input.index)):      # todo; to optimize performance, section 4.4; i-10,i+30
        dependency_matrix = np.zeros((max_time_slot_shift, max_time_slot_shift))
        if follow_idx is not lead_idx:
            follow_class = flights_input['Weight class'].iloc[follow_idx]
            follow_time_original = flights_input['Time'].iloc[follow_idx]
            for i in range(max_time_slot_shift):
                for j in range(max_time_slot_shift):
                    dependency = False
                    lead_time_slot = flights_input['Time'].iloc[lead_idx] + i * time_resolution
                    follow_time_slot = flights_input['Time'].iloc[follow_idx] + j * time_resolution
                    if follow_time_slot >= lead_time_slot: # todo; check if follower HAS to be after leader
                        separation = follow_time_slot - lead_time_slot
                        if lead_class == 'H':
                            if follow_class == 'H':
                                if separation < separation_heavy_heavy:
                                    dependency = True
                            elif follow_class == 'M':
                                if separation < separation_heavy_medium:
                                    dependency = True
                        elif lead_class == 'M':
                            if follow_class == 'H':
                                if separation < separation_medium_heavy:
                                    dependency = True
                            elif follow_class == 'M':
                                if separation < separation_medium_medium:
                                    dependency = True
                    dependency_matrix[i][j] = dependency
        lead_matrix.append(dependency_matrix)
    dependency_tensor.append(lead_matrix)

# write
for runway in runway_list:
    for lead_idx in range(len(flights_input.index)):
        time_original = flights_input['Time'].iloc[lead_idx]
        for j in range(max_time_slot_shift):
            time_slot = time_original + j * time_resolution
            file.write('  occupation_' + str(lead_idx + 1) + '_' + str(time_slot) + '_' + runway + ': x_' + str(lead_idx + 1) + '_' + runway + '_' + str(time_slot))
            for follow_idx in range(len(flights_input.index)):
                if follow_idx is not lead_idx:
                    for k in range(max_time_slot_shift):
                        if dependency_tensor[lead_idx][follow_idx][j][k]:
                            follow_time_slot = flights_input['Time'].iloc[follow_idx] + k * time_resolution
                            # if follow_time_slot >= time_slot:
                            file.write(' + x_' + str(follow_idx+1) + '_' + runway + '_' + str(follow_time_slot))
            file.write(' <= 1\n')


""" DEFINE VARIABLES """
file.write('\nBinary\n')
for runway in runway_list:
    for lead_idx in range(len(flights_input.index)):
        time_original = flights_input['Time'].iloc[lead_idx]
        for j in range(max_time_slot_shift):
            time_slot = time_original + j * time_resolution
            file.write('x_' + str(lead_idx + 1) + '_' + runway + '_' + str(time_slot) + ' ')
file.write('\nEnd')