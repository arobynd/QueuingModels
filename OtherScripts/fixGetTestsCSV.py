#from SimulatorSources.plotResults import *
#from SimulatorSources.CalculateSATfeatureOverhead import *
import numpy as np
import pandas as pd
import os



AllTestResults_TestHeuristic = pd.read_csv("AllTestResults_TestHeuristic.csv", index_col=0)
AllTestResults_TestHeuristic.insert(9, "KqueueSize", 4)
AllTestResults_TestHeuristic.insert(10, "Rand", 0)
AllTestResults_TestHeuristic .to_csv("AllTestResults_TestHeuristic.csv")
print "OK"
