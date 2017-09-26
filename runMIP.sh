#!/bin/bash

instanceArrivalTimesCSV=$1
instanceRunTimesCSV=$2
instanceMaximumExpectedWaitingTimeCSV=$3
C=$4
searchTime=$5
searchGap=$6
lastEndTime=$7
instanceSolvableCSV=$8
option=$9
fileName=${10}
machines=${11}


cd "MIPmodel/"
bash runTest.sh $instanceArrivalTimesCSV $instanceRunTimesCSV $instanceMaximumExpectedWaitingTimeCSV $C $searchTime $searchGap $lastEndTime $instanceSolvableCSV $option $fileName $machines
cd ..