#from SimulatorSources.plotResults import *
#from SimulatorSources.CalculateSATfeatureOverhead import *
import numpy as np
import pandas as pd


def fixColumns(Arg):
  AllTestResults_TestHeuristic = pd.read_csv(Arg+"AllTestResults_TestHeuristic.csv", index_col=0)
  AllTestResults_TestHeuristic.insert(9, "KqueueSize", 4)
  AllTestResults_TestHeuristic.insert(10, "Rand", 0)
  AllTestResults_TestHeuristic .to_csv(Arg+"AllTestResults_TestHeuristic.csv")
  print "OK"
  


#fixColumns( "Results_K4_R0_H2,4,6,8,16/BIGMIX_cplex/QueuingModels/")
#fixColumns( "Results_K4_R0_H2,4,6,8,16/BIGMIX_gurobi/QueuingModels/")
#fixColumns( "Results_K4_R0_H2,4,6,8,16/BIGMIX_lpsolve/QueuingModels/")
#fixColumns( "Results_K4_R0_H2,4,6,8,16/BIGMIX_scip/QueuingModels/")
#fixColumns( "Results_K4_R0_H2,4,6,8,16/CORLAT_cplex/QueuingModels/")
#fixColumns( "Results_K4_R0_H2,4,6,8,16/CORLAT_gurobi/QueuingModels/")
#fixColumns( "Results_K4_R0_H2,4,6,8,16/CORLAT_lpsolve/QueuingModels/")
#fixColumns( "Results_K4_R0_H2,4,6,8,16/CORLAT_scip/QueuingModels/")
#fixColumns( "Results_K4_R0_H2,4,6,8,16/HAND_minisat/QueuingModels/")
#fixColumns( "Results_K4_R0_H2,4,6,8,16/INDU-HAND-RAND_minisat/QueuingModels/")
#fixColumns( "Results_K4_R0_H2,4,6,8,16/INDU_minisat/QueuingModels/")
#fixColumns( "Results_K4_R0_H2,4,6,8,16/RAND_minisat/QueuingModels/")
