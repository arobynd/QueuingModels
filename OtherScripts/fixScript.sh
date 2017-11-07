#!bin/bash
function fix {
	dirName=""
    cd $1
	for D in ./*; do
		if [ -d "$D" ]; then
			dirName="$D"
			dir=${dirName/_K_0_/_K_4_}
            #echo $dir"..."$dirName
            #echo $D
		    cd "$D"
		    mv *.csv ../$dir
		    mv *.txt ../$dir
		    cd ..
		fi
	done
	rm -r *_K_0_*
}

#bash untarAll.sh

Dir=$PWD
#oneDir $Dir"/BIGMIX_cplex/QueuingModels/SimulationResults/30_70/"
#oneDir $Dir"/BIGMIX_gurobi/QueuingModels/SimulationResults/30_70/"
#oneDir $Dir"/BIGMIX_lpsolve/QueuingModels/SimulationResults/30_70/"
#oneDir $Dir"/BIGMIX_scip/QueuingModels/SimulationResults/30_70/"
#oneDir $Dir"/CORLAT_cplex/QueuingModels/SimulationResults/30_70/"
#oneDir $Dir"/CORLAT_gurobi/QueuingModels/SimulationResults/30_70/"
#oneDir $Dir"/CORLAT_lpsolve/QueuingModels/SimulationResults/30_70/"
#oneDir $Dir"/CORLAT_scip/QueuingModels/SimulationResults/30_70/"
fix $Dir"/HAND_minisat/QueuingModels/SimulationResults/30_70/"
#oneDir $Dir"/INDU-HAND-RAND_minisat/QueuingModels/SimulationResults/30_70/"
#fix $Dir"/INDU_minisat/QueuingModels/SimulationResults/30_70/"
#fix $Dir"/RAND_minisat/QueuingModels/SimulationResults/30_70/"

