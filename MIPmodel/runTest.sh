#!/bin/bash

#Compile the solver

javac -classpath cplex.jar -encoding UTF-8 *.java

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

java -cp  cplex.jar:. -Djava.library.path=./x86-64_linux/:. Schedule $instanceArrivalTimesCSV $instanceRunTimesCSV $instanceMaximumExpectedWaitingTimeCSV $C $searchTime $searchGap $lastEndTime $instanceSolvableCSV $option $fileName $machines

