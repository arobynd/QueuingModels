#from SimulatorSources.plotResults import *
#from SimulatorSources.CalculateSATfeatureOverhead import *
import numpy as np
import pandas as pd
import os

def appendAllTests(Test):
  d1="Results_K4_R0_H2,4,6,8,16/"+Test
  d2="Results_K4_R1-2-3-4_H2/"+Test
  d3="Results_K6-8_R0_H2/"+Test
  d4="CompleteDataAllTests/AllTests/"
  file1 = pd.read_csv(d1+"AllTestResults_TestHeuristic.csv", index_col=0)
  file2 = pd.read_csv(d2+"AllTestResults_TestHeuristic.csv", index_col=0)
  file3 = pd.read_csv(d3+"AllTestResults_TestHeuristic.csv", index_col=0)
  finalA=file1.append(file2, ignore_index=True)
  finalB=finalA.append(file3, ignore_index=True)
  finalB["TestID"]=finalB["VM"].map(str)+"_"+finalB["Features"].map(str)+"_"+finalB["WTlower"].map(str)+"_"+finalB["WTupper"].map(str)+"_"+finalB["AvgRunTDiv"].map(str)+"_"+finalB["InterArr"].map(str)+"_"+finalB["Heuristic"].map(str)+"_"+finalB["KqueueSize"].map(str)
  #acomodar el testID
  a=Test.split("/")
  finalB.to_csv(d4+a[0]+".csv")
  print "OK "+Test


#appendAllTests( "BIGMIX_cplex/QueuingModels/")
#appendAllTests( "BIGMIX_gurobi/QueuingModels/")
#appendAllTests( "BIGMIX_lpsolve/QueuingModels/")
#appendAllTests( "BIGMIX_scip/QueuingModels/")
#appendAllTests( "CORLAT_cplex/QueuingModels/")
##appendAllTests( "CORLAT_gurobi/QueuingModels/")
#appendAllTests( "CORLAT_lpsolve/QueuingModels/")
#appendAllTests( "CORLAT_scip/QueuingModels/")
#appendAllTests( "HAND_minisat/QueuingModels/")
#appendAllTests( "INDU-HAND-RAND_minisat/QueuingModels/")
#appendAllTests( "INDU_minisat/QueuingModels/")
#appendAllTests( "RAND_minisat/QueuingModels/")


#####################################################

def test1Data(Test):
  d1="CompleteDataAllTests/AllTests/"+Test
  d2="CompleteDataAllTests/Test1/"+Test
  f = pd.read_csv(d1, index_col=0)
  x = f[(f.KqueueSize == 4) & (f.Rand == 0)]
  x.to_csv(d2)
  print "OK "+Test


#test1Data( "BIGMIX_cplex.csv")
#test1Data( "BIGMIX_gurobi.csv")
#test1Data( "BIGMIX_lpsolve.csv")
#test1Data( "BIGMIX_scip.csv")
#test1Data( "CORLAT_cplex.csv")
##test1Data( "CORLAT_gurobi.csv")
#test1Data( "CORLAT_lpsolve.csv")
#test1Data( "CORLAT_scip.csv")
#test1Data( "HAND_minisat.csv")
#test1Data( "INDU-HAND-RAND_minisat.csv")
#test1Data( "INDU_minisat.csv")
#test1Data( "RAND_minisat.csv")


#####################################################


def test2Data(Test):
  d1="CompleteDataAllTests/AllTests/"+Test
  d2="CompleteDataAllTests/Test2/"+Test
  f = pd.read_csv(d1, index_col=0)
  x = f[(f.Heuristic == 2) & (f.KqueueSize == 4)]
  x.to_csv(d2)
  print "OK "+Test

#test2Data( "BIGMIX_cplex.csv")
#test2Data( "BIGMIX_gurobi.csv")
#test2Data( "BIGMIX_lpsolve.csv")
#test2Data( "BIGMIX_scip.csv")
#test2Data( "CORLAT_cplex.csv")
##test2Data( "CORLAT_gurobi.csv")
#test2Data( "CORLAT_lpsolve.csv")
#test2Data( "CORLAT_scip.csv")
#test2Data( "HAND_minisat.csv")
#test2Data( "INDU-HAND-RAND_minisat.csv")
#test2Data( "INDU_minisat.csv")
#test2Data( "RAND_minisat.csv")


#####################################################


def test3Data(Test):
  d1="CompleteDataAllTests/AllTests/"+Test
  d2="CompleteDataAllTests/Test3/"+Test
  f = pd.read_csv(d1, index_col=0)
  x = f[(f.Rand == 0) & (f.Heuristic == 2)]
  x.to_csv(d2)
  print "OK "+Test

test3Data( "BIGMIX_cplex.csv")
test3Data( "BIGMIX_gurobi.csv")
test3Data( "BIGMIX_lpsolve.csv")
test3Data( "BIGMIX_scip.csv")
test3Data( "CORLAT_cplex.csv")
##test3Data( "CORLAT_gurobi.csv")
test3Data( "CORLAT_lpsolve.csv")
test3Data( "CORLAT_scip.csv")
test3Data( "HAND_minisat.csv")
test3Data( "INDU-HAND-RAND_minisat.csv")
test3Data( "INDU_minisat.csv")
test3Data( "RAND_minisat.csv")
