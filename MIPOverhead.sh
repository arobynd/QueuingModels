#!/bin/bash


#Perfect Estimations
Dir="SimulationResults/30_70/"
File="MIP1_stops_RealServiceTime_G1_Simulation.csv_SolutionsLog.txt"


Test="VM_1_WaitingTime_1_3600_interArrival_3600_#2017_05_01_12_13_04_onlysolvable=False_completeTest/"
grep "(root+branch&cut)" $Dir""$Test""$File >> xxx.csv	
Test="VM_1_WaitingTime_1_300_interArrival_300_#2017_04_30_22_40_52_onlysolvable=False_completeTest/"
grep "(root+branch&cut)" $Dir""$Test""$File >> xxx.csv	
Test="VM_1_WaitingTime_1_500_interArrival_1000_#2017_05_01_00_35_46_onlysolvable=False_completeTest/"
grep "(root+branch&cut)" $Dir""$Test""$File >> xxx.csv	
Test="VM_1_WaitingTime_1_600_interArrival_300_#2017_05_01_01_22_36_onlysolvable=False_completeTest/"
grep "(root+branch&cut)" $Dir""$Test""$File >> xxx.csv	
Test="VM_1_WaitingTime_1_1000_interArrival_300_#2017_05_01_09_37_41_onlysolvable=False_completeTest/"
grep "(root+branch&cut)" $Dir""$Test""$File >> xxx.csv	
Test="VM_1_WaitingTime_1_1500_interArrival_3600_#2017_05_01_11_50_54_onlysolvable=False_completeTest/"
grep "(root+branch&cut)" $Dir""$Test""$File >> xxx.csv	
Test="VM_1_WaitingTime_1_3600_interArrival_3600_#2017_05_01_12_13_04_onlysolvable=False_completeTest/"
grep "(root+branch&cut)" $Dir""$Test""$File >> xxx.csv	
Test="VM_1_WaitingTime_1000_3000_interArrival_300_#2017_04_30_15_29_28/"
grep "(root+branch&cut)" $Dir""$Test""$File >> xxx.csv	
Test="VM_1_WaitingTime_1000_3000_interArrival_400_#2017_05_04_23_43_42/"
grep "(root+branch&cut)" $Dir""$Test""$File >> xxx.csv	
Test="VM_1_WaitingTime_1000_3000_interArrival_500_#2017_05_01_12_39_26/"
grep "(root+branch&cut)" $Dir""$Test""$File >> xxx.csv	
Test="VM_1_WaitingTime_1000_3000_interArrival_1000_#2017_04_30_19_35_48/"
grep "(root+branch&cut)" $Dir""$Test""$File >> xxx.csv	


