Dir=$PWD
rm $Dir"/BIGMIX_cplexTestResults/BIGMIX_cplex.tar"
rm $Dir"/BIGMIX_gurobiTestResults/BIGMIX_gurobi.tar"
rm $Dir"/BIGMIX_lpsolveTestResults/BIGMIX_lpsolve.tar"
rm $Dir"/BIGMIX_scipTestResults/BIGMIX_scip.tar"
rm $Dir"/CORLAT_cplexTestResults/CORLAT_cplex.tar"
rm $Dir"/CORLAT_gurobiTestResults/CORLAT_gurobi.tar"
rm $Dir"/CORLAT_lpsolveTestResults/CORLAT_lpsolve.tar"
rm $Dir"/CORLAT_scipTestResults/CORLAT_scip.tar"
rm $Dir"/HAND_minisatTestResults/HAND_minisat.tar"
rm $Dir"/INDU-HAND-RAND_minisatTestResults/INDU-HAND-RAND_minisat.tar"
rm $Dir"/INDU_minisatTestResults/INDU_minisat.tar"
rm $Dir"/RAND_minisatTestResults/RAND_minisat.tar"

for a in `find  -not -type d -name *.tar`; do tar -xf $a; done

Dir=$PWD
rm -r $Dir"/BIGMIX_cplexTestResults/"
rm -r $Dir"/BIGMIX_gurobiTestResults/"
rm -r $Dir"/BIGMIX_lpsolveTestResults/"
rm -r $Dir"/BIGMIX_scipTestResults/"
rm -r $Dir"/CORLAT_cplexTestResults/"
rm -r $Dir"/CORLAT_gurobiTestResults/"
rm -r $Dir"/CORLAT_lpsolveTestResults/"
rm -r $Dir"/CORLAT_scipTestResults/"
rm -r $Dir"/HAND_minisatTestResults/"
rm -r $Dir"/INDU-HAND-RAND_minisatTestResults/"
rm -r $Dir"/INDU_minisatTestResults/"
rm -r $Dir"/RAND_minisatTestResults/"
