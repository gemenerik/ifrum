# writes .lp file for optimization
# idx 1 corresponds to flight 1 in csv, idx 0 corresponds to 'start', idx n to 'end'
# todo; add multiple runways, add maximum delay

import pandas as pd


runway_list = ['l', 'r']
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


""" FUEL & DELAY """
# variables
approach_left_distance = 10000      # m
approach_right_distance = 20000     # m

mass_flow_medium = 2
mass_flow_heavy = 3

velocity_approach_medium = 72       # m/s
velocity_approach_heavy = 82        # m/s


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

for i in range(len(flights_input.index)):
    file.write('  delay_maximum_' + str(i+1) + ': delay_maximum - delay_' + str(i+1) + ' >= 0\n')

for i in range(len(flights_input.index)):
    file.write('  time_maximum' + str(i+1) + ': time_maximum - time_' + str(i+1) + ' >= 0\n')


""" SCHEDULING """
# write
for i in range(len(flights_input.index)):
    arrival_time = flights_input['Time'].iloc[i]
    file.write('  delay_' + str(i+1) + ': time_' + str(i+1) + ' - delay_' + str(i+1) + ' = ' + str(arrival_time) + '\n')


""" SEPARATION """
separation_heavy_heavy = -1687      # 113
separation_heavy_medium = -1619     # 181
separation_medium_heavy = -1713     # 87
separation_medium_medium = -1700    # 100

for i in range(len(flights_input.index)):
    for j in range(len(flights_input.index)):
        if i is not j:
            for k in runway_list:
                file.write('  separation_' + str(i+1) + '_' + str(j+1) + '_' + k + ': time_' + str(j+1) + ' - time_' + str(i+1) +
                           ' - 1800 order_' + str(i+1) + '_' + str(j+1) + '_' + k + ' >= ')
                if flights_input['Weight class'] .iloc[i] == 'H':
                    if flights_input['Weight class'] .iloc[j] == 'H':
                        # heavy - heavy
                        file.write(str(separation_heavy_heavy))
                        file.write('\n')
                    elif flights_input['Weight class'] .iloc[j] == 'M':
                        # heavy - medium
                        file.write(str(separation_heavy_medium))
                        file.write('\n')
                    else:
                        print('Error - aircraft class not found')
                elif flights_input['Weight class'] .iloc[i] == 'M':
                    if flights_input['Weight class'].iloc[j] == 'H':
                        # medium - heavy
                        file.write(str(separation_medium_heavy))
                        file.write('\n')
                    elif flights_input['Weight class'] .iloc[j] == 'M':
                        # medium - medium
                        file.write(str(separation_medium_medium))
                        file.write('\n')
                    else:
                        print('Error - aircraft class not found')
                else:
                    print('Error - aircraft class not found')


""" ORDER """
# ascertain that from order i_j and j_i, maximum one can be True.
for i in range(len(flights_input.index)):
    for j in range(len(flights_input.index)):
        if i < j:
            file.write('  o_' + str(i + 1) + '_' + str(j + 1) + ':')
            flag = True
            print(i,j)
            for k in runway_list:
                if flag:
                    file.write(' order_' + str(j+1) + '_' + str(i+1) + '_' + k + ' + order_' + str(i+1) + '_' + str(j+1) + '_' + k)
                if not flag:
                    file.write(' + order_' + str(j + 1) + '_' + str(i + 1) + '_' + k + ' + order_' + str(i + 1) + '_' + str(j + 1) + '_' + k)
                flag = False
            file.write(' <= 1\n')
# ascertain that from order i_n for n = 1, 2, 3 ... but not i; maximum one can be true
# this ensures that only one flight can be directly AFTER flight i
for i in range(len(flights_input.index)+1):
    file.write('  after' + str(i) + ':')
    flag = True
    for j in range(1, len(flights_input.index)+2):
        if i is not j:
            for k in runway_list:
                if flag:
                    file.write(' order_' + str(i) + '_' + str(j) + '_' + k)
                if not flag:
                    file.write(' + order_' + str(i) + '_' + str(j) + '_' + k)
                flag = False
    file.write(' = 1\n')

# ascertain that from order n_i for n = 1, 2, 3 ... but not i; maximum one can be true
# this ensures that only one flight can be directly BEFORE flight i
for i in range(1, len(flights_input.index)+2):
    file.write('  before' + str(i) + ':')
    flag = True
    for j in range(len(flights_input.index)+1):
        if i is not j:
            for k in runway_list:
                if flag:
                    file.write(' order_' + str(j) + '_' + str(i) + '_' + k)
                if not flag:
                    file.write(' + order_' + str(j) + '_' + str(i) + '_' + k)
                flag = False
    file.write(' = 1\n')


""" NOISE """
# variables
noise_left_medium = 65      # dB
noise_left_heavy = 70       # dB
noise_right_medium = 70     # dB
noise_right_heavy = 75      # dB


""" DEFINE VARIABLES """
file.write('\nBinary\n')
for i in range(len(flights_input.index)+2):
    for j in range(len(flights_input.index)+1):
        if i is not j:
            for k in runway_list:
                file.write('order_' + str(j) + '_' + str(i) + '_' + k + ' ')
file.write('\nEnd')