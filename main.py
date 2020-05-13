# todo; optimize program by looking only at flights within a certain timeframe
# todo; update mass flow
# todo; update velocity approach
# todo; update separation times
# todo; model verification
# todo; model sensitivity analysis
# todo; optional; add departure-departure, arrival-departure, departure-arrival dependencies (easier than it sounds)
# todo; optional; add more runways

import pandas as pd
import numpy as np


""" VARIABLES """
# airport
approach_left_distance = 10000                  # m
approach_right_distance = 20000                 # m

runway_list = ['l', 'r']

# aircraft
aircraft_list = ['H', 'N', 'M', 'L']
mass_flow_list = [3, 2.5, 2, 1]                 # kg/s
velocity_approach_list = [82, 78, 72, 63]       # m/s

separation_H_H = 113                            # s
separation_H_N = 131                            # s
separation_H_M = 181                            # s
separation_H_L = 202                            # s
separation_N_H = 97                             # s
separation_N_N = 103                            # s
separation_N_M = 110                            # s
separation_N_L = 130                            # s
separation_M_H = 87                             # s
separation_M_N = 93                             # s
separation_M_M = 100                            # s
separation_M_L = 120                            # s
separation_L_H = 75                             # s
separation_L_N = 82                             # s
separation_L_M = 92                             # s
separation_L_L = 98                             # s

separation_matrix = [[separation_H_H, separation_H_N, separation_H_M, separation_H_L],
                     [separation_N_H, separation_N_N, separation_N_M, separation_N_L],
                     [separation_M_H, separation_M_N, separation_M_M, separation_M_L],
                     [separation_L_H, separation_L_N, separation_L_M, separation_L_L]]

noise_left_list = [90, 85, 80, 75]              # dBA
noise_right_list = [100, 95, 90, 85]            # dBA

# time vector
time_resolution = 20                            # s
max_time_slot_shift = 5000                      # -

# input data
flights_input = pd.read_csv('Flightschedule.csv')
file = open('ifrum.lp', 'w')


""" TOOLS """
assert len(aircraft_list) == len(mass_flow_list)
assert len(aircraft_list) == len(velocity_approach_list)
assert len(aircraft_list) == len(noise_left_list)
assert len(aircraft_list) == len(noise_right_list)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def find_idx(input_string):
    return aircraft_list.index(input_string)


""" OBJECTIVE FUNCTION """
# variables
optimization_function = 'total_fuel_burned + total_noise'

# write
file.write('Minimize\n')
file.write('  ' + optimization_function+'\n')
file.write('\n')
file.write('Subject To\n')


""" FUEL """
# variables
total_fuel_burned_left_list = []
total_fuel_burned_right_list = []
for i in range(len(mass_flow_list)):
    total_fuel_burned_left_list.append(mass_flow_list[i] * approach_left_distance / velocity_approach_list[i])
    total_fuel_burned_right_list.append(mass_flow_list[i] * approach_right_distance / velocity_approach_list[i])

# write
file.write('  fuel: -total_fuel_burned ')
for i in range(len(flights_input.index)):
    weight_class = flights_input['Weight class'] .iloc[i]
    index = find_idx(weight_class)
    file.write('+ ' + str(mass_flow_list[index]) + ' delay_' + str(i+1) + ' + tfb_' + str(i+1) + ' ')
file.write('= 0\n')

for lead_idx in range(len(flights_input.index)):
    time_original = flights_input['Time'].iloc[lead_idx]
    file.write('  tfb' + str(lead_idx) + ': ')
    for j in range(max_time_slot_shift):
        for runway in runway_list:
            time_slot = time_original + j * time_resolution
            weight_class = flights_input['Weight class'].iloc[lead_idx]
            index = find_idx(weight_class)
            tfb = 0
            if runway == 'l':
                tfb = total_fuel_burned_left_list[index]
            elif runway == 'r':
                tfb = total_fuel_burned_right_list[index]
            file.write('+ ' + str(tfb) + ' x_' + str(lead_idx + 1) + '_' + runway + '_' + str(time_slot) + ' ')
    file.write(' - tfb_' + str(lead_idx+1) + ' = ' + str(time_original) + '\n')

for lead_idx in range(len(flights_input.index)):
    time_original = flights_input['Time'].iloc[lead_idx]
    file.write('  delaye_' + str(lead_idx) + ': ')
    for j in range(max_time_slot_shift):
        for runway in runway_list:
            time_slot = time_original + j * time_resolution
            file.write(' + ' + str(time_slot) + ' x_' + str(lead_idx + 1) + '_' + runway + '_' + str(time_slot))
    file.write(' - delay_' + str(lead_idx+1) + ' = ' + str(time_original) + '\n')


""" NOISE """
file.write('  noise_total: -total_noise ')
for i in range(len(flights_input.index)):
    for runway in runway_list:
        file.write('+ ' + 'noise_' + runway + '_' + str(i+1)  + ' ')
file.write('= 0\n')

for runway in runway_list:
    for lead_idx in range(len(flights_input.index)):
        time_original = flights_input['Time'].iloc[lead_idx]
        file.write('  noise' + str(lead_idx) + runway + ': ')
        for j in range(max_time_slot_shift):
            time_slot = time_original + j * time_resolution
            weight_class = flights_input['Weight class'].iloc[lead_idx]
            index = find_idx(weight_class)
            noise = 0
            if runway == 'l':
                noise = noise_left_list[index]
            elif runway == 'r':
                noise = noise_right_list[index]
            file.write('+ ' + str(noise) + ' x_' + str(lead_idx + 1) + '_' + runway + '_' + str(time_slot) + ' ')
        file.write(' - noise_' + runway + '_' + str(lead_idx+1) + ' = ' + str(0) + '\n')


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

print('""" FLIGHT ASSIGNMENT DONE """')


""" RUNWAY OCCUPATION """
# generate dependency matrices
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
                        index_lead = find_idx(lead_class)
                        index_follow = find_idx(follow_class)
                        if separation < separation_matrix[index_lead][index_follow]:
                            dependency = True
                    dependency_matrix[i][j] = dependency
        lead_matrix.append(dependency_matrix)
    dependency_tensor.append(lead_matrix)

    print(' -> LEAD IDX ' + str(lead_idx) + ' DEPENDENCY DONE')

print('""" DEPENDENCY MATRIX DONE """')

# write constraints
for runway in runway_list:
    for lead_idx in range(len(flights_input.index)):
        time_original = flights_input['Time'].iloc[lead_idx]
        for j in range(max_time_slot_shift):
            time_slot = time_original + j * time_resolution
            file.write('  occupation_' + str(lead_idx + 1) + '_' + str(time_slot) + '_' + runway + ': x_' +
                       str(lead_idx + 1) + '_' + runway + '_' + str(time_slot))
            for follow_idx in range(len(flights_input.index)):
                if follow_idx is not lead_idx:
                    for k in range(max_time_slot_shift):
                        if dependency_tensor[lead_idx][follow_idx][j][k]:
                            follow_time_slot = flights_input['Time'].iloc[follow_idx] + k * time_resolution
                            # if follow_time_slot >= time_slot:
                            file.write(' + x_' + str(follow_idx+1) + '_' + runway + '_' + str(follow_time_slot))
            file.write(' <= 1\n')

print('""" RUNWAY OCCUPATION CONSTRAINTS DONE """')


""" DEFINE VARIABLES """
file.write('\nBinary\n')
for runway in runway_list:
    for lead_idx in range(len(flights_input.index)):
        time_original = flights_input['Time'].iloc[lead_idx]
        for j in range(max_time_slot_shift):
            time_slot = time_original + j * time_resolution
            file.write('x_' + str(lead_idx + 1) + '_' + runway + '_' + str(time_slot) + ' ')
file.write('\nEnd')

print('""" READY FOR OPTIMIZATION """')

if flights_input['Time'] .iloc[-1] > time_resolution * max_time_slot_shift - 300:
    print(f"{bcolors.FAIL}WARNING: POTENTIALLY INSUFFICIENTLY LARGE TIME VECTOR {bcolors.ENDC}")
    print('--> Time vector is length ', time_resolution * max_time_slot_shift)
    print('--> While latest arrival is at ', flights_input['Time'] .iloc[-1])
    print('--> It is highly recommended to extend your time vector to accommodate for delays')
