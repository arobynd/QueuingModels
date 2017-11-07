#!bin/bash
function addK4_R0 {
	dirName=""
    cd $1
	for D in ./*; do
		if [ -d "$D" ]; then
			dirName="$D"
			mv $dirName $dirName"_K_4_Rand_0"
			#dir=${dirName/_#*/}
			#mkdir $dir
		    #cd "$D"
		    #cp *.csv ../$dir
		    #cp *.txt ../$dir
		    #cd ..
		fi
	done
}

Dir=$PWD
addK4_R0 $Dir"/BIGMIX_cplex/QueuingModels/SimulationResults/30_70/"
addK4_R0 $Dir"/BIGMIX_gurobi/QueuingModels/SimulationResults/30_70/"
addK4_R0 $Dir"/BIGMIX_lpsolve/QueuingModels/SimulationResults/30_70/"
addK4_R0 $Dir"/BIGMIX_scip/QueuingModels/SimulationResults/30_70/"
addK4_R0 $Dir"/CORLAT_cplex/QueuingModels/SimulationResults/30_70/"
#addK4_R0 $Dir"/CORLAT_gurobi/QueuingModels/SimulationResults/30_70/"
addK4_R0 $Dir"/CORLAT_lpsolve/QueuingModels/SimulationResults/30_70/"
addK4_R0 $Dir"/CORLAT_scip/QueuingModels/SimulationResults/30_70/"
addK4_R0 $Dir"/HAND_minisat/QueuingModels/SimulationResults/30_70/"
addK4_R0 $Dir"/INDU-HAND-RAND_minisat/QueuingModels/SimulationResults/30_70/"
addK4_R0 $Dir"/INDU_minisat/QueuingModels/SimulationResults/30_70/"
addK4_R0 $Dir"/RAND_minisat/QueuingModels/SimulationResults/30_70/"



