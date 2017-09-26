import pandas as pd

def calculateAllFeaturesOverhead(DirData):
    ##  Calculate FeatureOverhead_All for All features testing data
    print "Calculating feature overhead for All features in testing data: " + DirData
    Data = pd.read_csv(DirData)
    n = Data.ix[:,126:138]
    FeatureOverhead_All=0;
    for i in range(n.shape[0]):
        for j in range(n.shape[1]):
          temp = n.ix[i,j]
          if temp >= 0:
              FeatureOverhead_All += temp;
    return FeatureOverhead_All


def calculateCheapFeaturesOverhead(DirData):
    ##  Calculate FeatureOverhead_Cheap for Cheap features testing data
    print "Calculating feature overhead for Cheap features in testing data: " + DirData
    Data = pd.read_csv(DirData)
    m = Data.ix[:,60:65]
    FeatureOverhead_Cheap=0;
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
          temp = m.ix[i,j]
          if temp >= 0:
              FeatureOverhead_Cheap += temp;
    return FeatureOverhead_Cheap


def calculateTrivialFeaturesOverhead(DirData):
    print "Calculating feature overhead for Trivial features in testing data: " + DirData
    return 0


def SATfeatureOverhead(DataSet):
    if (DataSet.lower().find("all")!=-1):
        return round(calculateAllFeaturesOverhead(DataSet))
    elif (DataSet.lower().find("trivial")!=-1):
        return round(calculateTrivialFeaturesOverhead(DataSet))
    elif (DataSet.lower().find("cheap")!=-1):
        return round(calculateCheapFeaturesOverhead(DataSet))
    else:
        return 20
