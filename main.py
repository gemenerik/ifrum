# todo; model verification ## moet nog uitgewerkt worden ##
# todo; model sensitivity analysis
# todo; optional; add departure-departure, arrival-departure, departure-arrival dependencies (easier than it sounds)
# todo; optional; add more runways
# todo; add lead idx for last idx, because it is not necessarily last

import pandas as pd
import scipy.sparse as sps
import numpy as np


""" VARIABLES """
# airport
#approach_left_distance = 10000                  # m
approach_left_distance = 100000
approach_right_distance = 10000                 # m

runway_list = ['l', 'r']
Left = 0
Right = 0

# aircraft
aircraft_list = ['H', 'N', 'M', 'L']
mass_flow_list = [1.7, 0.7, 0.5, 0.2]           # kg/s
velocity_approach_list = [77, 72, 66, 46]       # m/s

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

#noise_left_list = [1000, 1000, 1000, 1000]              # dBA
noise_left_list = [100, 95, 90, 85]   
noise_right_list = [100, 95, 90, 85]            # dBA

# time vector
time_resolution = 20                            # s
number_of_timeslots = 4500                      # -
max_timeslot_shift = 30                         # -
time_vector = range(0, time_resolution * number_of_timeslots, time_resolution)

dependency_forward = 10
dependency_backward = -5

# input data
flights_input = pd.read_csv('Flightschedule.csv')
file = open('ifrum.lp', 'w')

fuel_weight = 1
noise_weight = 1

sumtfbLeft = 0
sumtfbRight = 0


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


def get_range(lead_index):
    low_index = lead_index + dependency_backward
    high_index = lead_index + dependency_forward
    if low_index < 0:
        low_index = 0
    if high_index > len(flights_input.index):
        high_index = len(flights_input.index)
    return low_index, high_index


def get_time_idxs(lead_time_idx):
    bottom = lead_time_idx - max_timeslot_shift
    if bottom < 0:
        bottom = 0
    top = lead_time_idx + max_timeslot_shift
    if top > len(time_vector):
        top = len(time_vector)
    return bottom, top


""" OBJECTIVE FUNCTION """
# variables
optimization_function = str(fuel_weight) + ' total_fuel_burned + ' + str(noise_weight) + ' total_noise'

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
    for j in range(0, max_timeslot_shift):      # range from 0 so that aircraft cannot arrive earlier than they do
        for runway in runway_list:
            time_slot = time_original + j * time_resolution
            weight_class = flights_input['Weight class'].iloc[lead_idx]
            index = find_idx(weight_class)
            tfb = 0    
            tfbLeft = 0
            tfbRight = 0
            if runway == 'l':
                tfb = total_fuel_burned_left_list[index]
                tfbLeft = total_fuel_burned_left_list[index]
                sumtfbLeft = sumtfbLeft + tfbLeft
            elif runway == 'r':
                tfb = total_fuel_burned_right_list[index]
                tfbRight = total_fuel_burned_right_list[index]
                sumtfbRight = sumtfbRight + tfbRight
            file.write('+ ' + str(tfb) + ' x_' + str(lead_idx + 1) + '_' + runway + '_' + str(time_slot) + ' ')
    file.write(' - tfb_' + str(lead_idx + 1) + ' = 0\n')

for lead_idx in range(len(flights_input.index)):
    time_original = flights_input['Time'].iloc[lead_idx]
    file.write('  delaye_' + str(lead_idx) + ': ')
    for j in range(0, max_timeslot_shift):
        for runway in runway_list:
            time_slot = time_original + j * time_resolution
            file.write(' + ' + str(time_slot - time_original) + ' x_' + str(lead_idx + 1) + '_' + runway + '_' + str(time_slot))
    file.write(' - delay_' + str(lead_idx + 1) + ' = 0\n')


""" NOISE """
file.write('  noise_total: -total_noise ')
for i in range(len(flights_input.index)):
    for runway in runway_list:
        file.write('+ ' + 'noise_' + runway + '_' + str(i+1)  + ' ')
file.write('= 0\n')
sumnoiseLeft = 0
sumnoiseRight = 0
runwayLeft = 0
runwayRight = 0

for runway in runway_list:
    for lead_idx in range(len(flights_input.index)):
        time_original = flights_input['Time'].iloc[lead_idx]
        file.write('  noise' + str(lead_idx) + runway + ': ')
        for j in range(0, max_timeslot_shift):
            time_slot = time_original + j * time_resolution
            weight_class = flights_input['Weight class'].iloc[lead_idx]
            index = find_idx(weight_class)
            noiseLeft = 0
            noiseRight = 0
            if runway == 'l':
                noise = noise_left_list[index]
                #noiseLeft = noise_left_list[index]
                #sumnoiseLeft = sumnoiseLeft + noiseLeft
            elif runway == 'r':
                noise = noise_right_list[index]
                #noiseRight = noise_right_list[index]
                #sumnoiseRight = sumnoiseRight + noiseRight
            file.write('+ ' + str(noise) + ' x_' + str(lead_idx + 1) + '_' + runway + '_' + str(time_slot) + ' ')
        file.write(' - noise_' + runway + '_' + str(lead_idx+1) + ' = ' + str(0) + '\n')
        #if runway == 'l':
        #    runwayLeft = runwayLeft + 1
        #else:
        #    runwayRight = runwayRight + 1

""" FLIGHT ASSIGNMENT """
# write
for i in range(len(flights_input.index)):
    file.write('  assignment_' + str(i+1) + ': ')
    time_original = flights_input['Time'] .iloc[i]
    flag = True
    for runway in runway_list:
        for time_slot in range(time_original, time_original + max_timeslot_shift * time_resolution, time_resolution):
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
# dependency_tensor_entry = sps.coo_matrix((len(time_vector),len(time_vector)))
# import numpy as np
# print(len(flights_input.index))
# print(len(time_vector))
# test = np.zeros((len(flights_input.index),len(flights_input.index),len(time_vector),len(time_vector)), dtype=bool)
for lead_idx in range(len(flights_input.index)):
    lead_class = flights_input['Weight class'] .iloc[lead_idx]
    lead_time_original = flights_input['Time'].iloc[lead_idx]
    lead_time_idx = time_vector.index(lead_time_original)
    bottom_range, top_range = get_range(lead_idx)
    dependency_follower_tensor = []
    for follow_idx in range(len(flights_input.index)):
        if follow_idx in range(bottom_range, top_range):
            if follow_idx is not lead_idx:
                follow_class = flights_input['Weight class'].iloc[follow_idx]
                follow_time_original = flights_input['Time'].iloc[follow_idx]
                follow_time_idx = time_vector.index(follow_time_original)
                bottom, top = get_time_idxs(lead_time_idx)
                row = []
                col = []
                data = []
                for i in range(lead_time_idx, lead_time_idx + max_timeslot_shift):
                    for j in range(follow_time_idx, follow_time_idx + max_timeslot_shift):
                        dependency = False
                        lead_time_slot =  i * time_resolution
                        follow_time_slot =  j * time_resolution
                        separation = follow_time_slot - lead_time_slot
                        index_lead = find_idx(lead_class)
                        index_follow = find_idx(follow_class)
                        if separation >= 0:
                            if separation < separation_matrix[index_lead][index_follow]:
                                dependency = True
                        elif separation < 0:
                            if abs(separation) < separation_matrix[index_follow][index_lead]:
                                dependency = True
                        # dependency_tensor[lead_idx][follow_idx][i][j] = dependency
                        if dependency:
                            row.append(i)
                            col.append(j)
                            data.append(int(dependency))
                full_coo = sps.coo_matrix((data, (row, col)), shape=(len(time_vector), len(time_vector)))
                dependency_follower_tensor.append(full_coo.tocsr())
            else:
                empty_coo = sps.coo_matrix((len(time_vector), len(time_vector)))
                dependency_follower_tensor.append(empty_coo.tocsr())
        else:
            empty_coo = sps.coo_matrix((len(time_vector), len(time_vector)))
            dependency_follower_tensor.append(empty_coo.tocsr())
            # dependency_follower_tensor.append(sps.coo_matrix((len(time_vector), len(time_vector)))
            # make empty matrix
    dependency_tensor.append(dependency_follower_tensor)
    print(' -> LEAD IDX ' + str(lead_idx) + ' DEPENDENCY DONE')
print('""" DEPENDENCY MATRIX DONE """')

# import sys
# import numpy as np
# np.set_printoptions(threshold=sys.maxsize)
# print(np.shape(dependency_tensor))

# write constraints
for runway in runway_list:
    for lead_idx in range(len(flights_input.index)):
        time_original = flights_input['Time'].iloc[lead_idx]
        lead_time_idx = time_vector.index(time_original)
        for j in range(lead_time_idx, lead_time_idx + max_timeslot_shift):
            if j < len(time_vector):
                time_slot = j * time_resolution
                bottom_range, top_range = get_range(lead_idx)
                for follow_idx in range(bottom_range, top_range):
                    if follow_idx is not lead_idx:
                        follow_time_original = flights_input['Time'].iloc[follow_idx]
                        follow_time_idx = time_vector.index(follow_time_original)
                        file.write('  occupation_' + str(lead_idx + 1) + '_' + str(follow_idx+1) + '_' + str(time_slot) + '_' + runway + ': x_' +
                                   str(lead_idx + 1) + '_' + runway + '_' + str(time_slot))
                        for k in range(follow_time_idx, follow_time_idx + max_timeslot_shift):
                            if k < len(time_vector):
                                array = dependency_tensor[lead_idx][follow_idx] # this is too slow
                                if array[j, k]:
                                    follow_time_slot = k * time_resolution
                                    file.write(' + x_' + str(follow_idx+1) + '_' + runway + '_' + str(follow_time_slot))
                        file.write(' <= 1\n')
        print(' -> LEAD IDX ' + str(lead_idx) + ', RUNWAY ' + runway + ' OCCUPATION CONSTRAINTS WRITTEN')

print('""" RUNWAY OCCUPATION CONSTRAINTS DONE """')


""" DEFINE VARIABLES """
file.write('\nBinary\n')
for runway in runway_list:
    for lead_idx in range(len(flights_input.index)):
        time_original = flights_input['Time'].iloc[lead_idx]
        lead_time_idx = time_vector.index(time_original)
        for j in range(lead_time_idx, lead_time_idx + max_timeslot_shift):
            if j < len(time_vector):
                time_slot = j * time_resolution
                file.write('x_' + str(lead_idx + 1) + '_' + runway + '_' + str(time_slot) + ' ')
file.write('\nEnd')

print('""" READY FOR OPTIMIZATION """')

if flights_input['Time'] .iloc[-1] > time_resolution * number_of_timeslots - 300:
    print(f"{bcolors.FAIL}WARNING: POTENTIALLY INSUFFICIENTLY LARGE TIME VECTOR {bcolors.ENDC}")
    print('--> Time vector is length ', time_resolution * number_of_timeslots)
    print('--> While latest arrival is at ', flights_input['Time'] .iloc[-1])
    print('--> It is highly recommended to extend your time vector to accommodate for delays')
