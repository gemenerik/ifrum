Minimize
  total_fuel_burned

Subject To
  fuel: -total_fuel_burned + 3 delay_1 + 3 delay_2 + 2 delay_3 + 2 delay_4 + 3 delay_5 = 0
  delay_maximum_1: delay_maximum - delay_1 >= 0
  delay_maximum_2: delay_maximum - delay_2 >= 0
  delay_maximum_3: delay_maximum - delay_3 >= 0
  delay_maximum_4: delay_maximum - delay_4 >= 0
  delay_maximum_5: delay_maximum - delay_5 >= 0
  time_maximum1: time_maximum - time_1 >= 0
  time_maximum2: time_maximum - time_2 >= 0
  time_maximum3: time_maximum - time_3 >= 0
  time_maximum4: time_maximum - time_4 >= 0
  time_maximum5: time_maximum - time_5 >= 0
  delay_1: time_1 - delay_1 = 0
  delay_2: time_2 - delay_2 = 100
  delay_3: time_3 - delay_3 = 120
  delay_4: time_4 - delay_4 = 600
  delay_5: time_5 - delay_5 = 800
  separation_1_2: time_2 - time_1 - 1800 order_1_2 >= -1687
  separation_1_3: time_3 - time_1 - 1800 order_1_3 >= -1619
  separation_1_4: time_4 - time_1 - 1800 order_1_4 >= -1619
  separation_1_5: time_5 - time_1 - 1800 order_1_5 >= -1687
  separation_2_1: time_1 - time_2 - 1800 order_2_1 >= -1687
  separation_2_3: time_3 - time_2 - 1800 order_2_3 >= -1619
  separation_2_4: time_4 - time_2 - 1800 order_2_4 >= -1619
  separation_2_5: time_5 - time_2 - 1800 order_2_5 >= -1687
  separation_3_1: time_1 - time_3 - 1800 order_3_1 >= -1713
  separation_3_2: time_2 - time_3 - 1800 order_3_2 >= -1713
  separation_3_4: time_4 - time_3 - 1800 order_3_4 >= -1700
  separation_3_5: time_5 - time_3 - 1800 order_3_5 >= -1713
  separation_4_1: time_1 - time_4 - 1800 order_4_1 >= -1713
  separation_4_2: time_2 - time_4 - 1800 order_4_2 >= -1713
  separation_4_3: time_3 - time_4 - 1800 order_4_3 >= -1700
  separation_4_5: time_5 - time_4 - 1800 order_4_5 >= -1713
  separation_5_1: time_1 - time_5 - 1800 order_5_1 >= -1687
  separation_5_2: time_2 - time_5 - 1800 order_5_2 >= -1687
  separation_5_3: time_3 - time_5 - 1800 order_5_3 >= -1619
  separation_5_4: time_4 - time_5 - 1800 order_5_4 >= -1619
  o_1_2: order_2_1 + order_1_2 <= 1
  o_1_3: order_3_1 + order_1_3 <= 1
  o_1_4: order_4_1 + order_1_4 <= 1
  o_1_5: order_5_1 + order_1_5 <= 1
  o_2_3: order_3_2 + order_2_3 <= 1
  o_2_4: order_4_2 + order_2_4 <= 1
  o_2_5: order_5_2 + order_2_5 <= 1
  o_3_4: order_4_3 + order_3_4 <= 1
  o_3_5: order_5_3 + order_3_5 <= 1
  o_4_5: order_5_4 + order_4_5 <= 1
  after0: order_0_1 + order_0_2 + order_0_3 + order_0_4 + order_0_5 + order_0_6 = 1
  after1: order_1_0 + order_1_2 + order_1_3 + order_1_4 + order_1_5 + order_1_6 = 1
  after2: order_2_0 + order_2_1 + order_2_3 + order_2_4 + order_2_5 + order_2_6 = 1
  after3: order_3_0 + order_3_1 + order_3_2 + order_3_4 + order_3_5 + order_3_6 = 1
  after4: order_4_0 + order_4_1 + order_4_2 + order_4_3 + order_4_5 + order_4_6 = 1
  after5: order_5_0 + order_5_1 + order_5_2 + order_5_3 + order_5_4 + order_5_6 = 1
  before1: order_0_1 + order_2_1 + order_3_1 + order_4_1 + order_5_1 = 1
  before2: order_0_2 + order_1_2 + order_3_2 + order_4_2 + order_5_2 = 1
  before3: order_0_3 + order_1_3 + order_2_3 + order_4_3 + order_5_3 = 1
  before4: order_0_4 + order_1_4 + order_2_4 + order_3_4 + order_5_4 = 1
  before5: order_0_5 + order_1_5 + order_2_5 + order_3_5 + order_4_5 = 1
  before6: order_0_6 + order_1_6 + order_2_6 + order_3_6 + order_4_6 + order_5_6 = 1

Binary
order_1_0 order_2_0 order_3_0 order_4_0 order_5_0 order_6_0 order_0_1 order_2_1 order_3_1 order_4_1 order_5_1 order_6_1 order_0_2 order_1_2 order_3_2 order_4_2 order_5_2 order_6_2 order_0_3 order_1_3 order_2_3 order_4_3 order_5_3 order_6_3 order_0_4 order_1_4 order_2_4 order_3_4 order_5_4 order_6_4 order_0_5 order_1_5 order_2_5 order_3_5 order_4_5 order_6_5 order_0_6 order_1_6 order_2_6 order_3_6 order_4_6 order_5_6 
End