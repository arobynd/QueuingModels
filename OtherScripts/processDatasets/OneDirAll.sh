#!bin/bash
function oneDir {
	dirName=""
    cd $1
	for D in ./*; do
		if [ -d "$D" ]; then
			dirName="$D"
			dir=${dirName/_#*/}
			mkdir $dir
		    cd "$D"
		    cp *.csv ../$dir
		    cp *.txt ../$dir
		    cd ..
		fi
	done
	rm -r *_#*
}

bash untarAll.sh

Dir=$PWD
oneDir $Dir"/BIGMIX_cplex/QueuingModels/SimulationResults/30_70/"
oneDir $Dir"/BIGMIX_gurobi/QueuingModels/SimulationResults/30_70/"
oneDir $Dir"/BIGMIX_lpsolve/QueuingModels/SimulationResults/30_70/"
oneDir $Dir"/BIGMIX_scip/QueuingModels/SimulationResults/30_70/"
oneDir $Dir"/CORLAT_cplex/QueuingModels/SimulationResults/30_70/"
oneDir $Dir"/CORLAT_gurobi/QueuingModels/SimulationResults/30_70/"
oneDir $Dir"/CORLAT_lpsolve/QueuingModels/SimulationResults/30_70/"
oneDir $Dir"/CORLAT_scip/QueuingModels/SimulationResults/30_70/"
oneDir $Dir"/HAND_minisat/QueuingModels/SimulationResults/30_70/"
oneDir $Dir"/INDU-HAND-RAND_minisat/QueuingModels/SimulationResults/30_70/"
oneDir $Dir"/INDU_minisat/QueuingModels/SimulationResults/30_70/"
oneDir $Dir"/RAND_minisat/QueuingModels/SimulationResults/30_70/"



