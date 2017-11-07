#!bin/bash
function createImages {
	dirName=""
    cd $1
	python ViewResultsNew.py
}


Dir=$PWD
cp $Dir"/ViewResultsNew.py" $Dir"/BIGMIX_cplex/QueuingModels/ViewResultsNew.py"
cp $Dir"/ViewResultsNew.py" $Dir"/BIGMIX_gurobi/QueuingModels/ViewResultsNew.py"
cp $Dir"/ViewResultsNew.py" $Dir"/BIGMIX_lpsolve/QueuingModels/ViewResultsNew.py"
cp $Dir"/ViewResultsNew.py" $Dir"/BIGMIX_scip/QueuingModels/ViewResultsNew.py"
cp $Dir"/ViewResultsNew.py" $Dir"/CORLAT_cplex/QueuingModels/ViewResultsNew.py"
cp $Dir"/ViewResultsNew.py" $Dir"/CORLAT_gurobi/QueuingModels/ViewResultsNew.py"
cp $Dir"/ViewResultsNew.py" $Dir"/CORLAT_lpsolve/QueuingModels/ViewResultsNew.py"
cp $Dir"/ViewResultsNew.py" $Dir"/CORLAT_scip/QueuingModels/ViewResultsNew.py"
cp $Dir"/ViewResultsNew.py" $Dir"/HAND_minisat/QueuingModels/ViewResultsNew.py"
cp $Dir"/ViewResultsNew.py" $Dir"/INDU-HAND-RAND_minisat/QueuingModels/ViewResultsNew.py"
cp $Dir"/ViewResultsNew.py" $Dir"/INDU_minisat/QueuingModels/ViewResultsNew.py"
cp $Dir"/ViewResultsNew.py" $Dir"/RAND_minisat/QueuingModels/ViewResultsNew.py"


Dir=$PWD
createImages $Dir"/BIGMIX_cplex/QueuingModels/"
createImages $Dir"/BIGMIX_gurobi/QueuingModels/"
createImages $Dir"/BIGMIX_lpsolve/QueuingModels/"
createImages $Dir"/BIGMIX_scip/QueuingModels/"
createImages $Dir"/CORLAT_cplex/QueuingModels/"
createImages $Dir"/CORLAT_gurobi/QueuingModels/"
createImages $Dir"/CORLAT_lpsolve/QueuingModels/"
createImages $Dir"/CORLAT_scip/QueuingModels/"
createImages $Dir"/HAND_minisat/QueuingModels/"
createImages $Dir"/INDU-HAND-RAND_minisat/QueuingModels/"
createImages $Dir"/INDU_minisat/QueuingModels/"
createImages $Dir"/RAND_minisat/QueuingModels/"



