Dir=$PWD

cd $Dir"/BIGMIX_cplex/QueuingModels/"
python $Dir"/BIGMIX_cplex/QueuingModels/getTestsCSVNew.py"

cd $Dir"/BIGMIX_gurobi/QueuingModels/"
python $Dir"/BIGMIX_gurobi/QueuingModels/getTestsCSVNew.py"

cd $Dir"/BIGMIX_lpsolve/QueuingModels/"
python $Dir"/BIGMIX_lpsolve/QueuingModels/getTestsCSVNew.py"

cd $Dir"/BIGMIX_scip/QueuingModels/"
python $Dir"/BIGMIX_scip/QueuingModels/getTestsCSVNew.py"

cd $Dir"/CORLAT_cplex/QueuingModels/"
python $Dir"/CORLAT_cplex/QueuingModels/getTestsCSVNew.py"

cd $Dir"/CORLAT_gurobi/QueuingModels/"
python $Dir"/CORLAT_gurobi/QueuingModels/getTestsCSVNew.py"

cd $Dir"/CORLAT_lpsolve/QueuingModels/"
python $Dir"/CORLAT_lpsolve/QueuingModels/getTestsCSVNew.py"

cd $Dir"/CORLAT_scip/QueuingModels/"
python $Dir"/CORLAT_scip/QueuingModels/getTestsCSVNew.py"

cd $Dir"/HAND_minisat/QueuingModels/"
python $Dir"/HAND_minisat/QueuingModels/getTestsCSVNew.py"

cd $Dir"/INDU-HAND-RAND_minisat/QueuingModels/"
python $Dir"/INDU-HAND-RAND_minisat/QueuingModels/getTestsCSVNew.py"

cd $Dir"/INDU_minisat/QueuingModels/"
python $Dir"/INDU_minisat/QueuingModels/getTestsCSVNew.py"

cd $Dir"/RAND_minisat/QueuingModels/"
python $Dir"/RAND_minisat/QueuingModels/getTestsCSVNew.py"
