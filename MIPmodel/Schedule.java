
//Model1: Model with disjunction constraints and with maximum expected waiting times (Regressions)
//PARAMETERS:
//a[i]...arrival time of instance i
//rt[i]...execution time of instance i (It may be an estimation or the real value)
//ewt[i]...maximum expected waiting time of instance i. If an instance waiting time is greater than this value,
//then it is not Attended
//VARIABLES:
//ST[i]...Start time of instance i (These are the decision variables)
//ET[i]...End time of instance i (These variables depend on the value of ST[i] and rt[i])
//WT[i]...Wait time of instance i (These variables depend on the value of ST[i] and a[i])
//Attended[i]...boolean variables used to determine whether an instance is Attended before the maximum waiting time or not
//
//CONSTRAINTS:
//ST[i] >= a[i]  forall i
//ET[i] = ST[i] + (rt[i]*Attended[i])  forall i
//WT[i] = ST[i] - a[i]  forall i
//Attended[i] = (WT[i] <= ewt[i])
//( ET[j] <= ST[i]-1  or  ST[j] >= ET[i]+1 )  forall i, i   if i!=j....This disjunction constraints avoids overlapping
//
//OBJECTIVE FUNCTION:
//minimize(C*sum(1 - Attended[i]) + sum(WT[i]) )
//
//C is the cost of solving an instance...If C is greater than instances cap time, then the function gives priority
//to maximize the number of Attended instances and then to minimize the waiting times.

//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//Model2: Model with disjunction constraints and with maximum expected waiting times (Perfect Classification and Perfect Regressions)
//PARAMETERS:
//a[i]...arrival time of instance i
//rt[i]...execution time of instance i (It may be an estimation or the real value)
//ewt[i]...maximum expected waiting time of instance i. If an instance waiting time is greater than this value,
//then it is not Attended
//solvable[i]...array indicating if an instance is solvable or not (0,1)

//VARIABLES:
//ST[i]...Start time of instance i (These are the decision variables)
//ET[i]...End time of instance i (These variables depend on the value of ST[i] and rt[i])
//WT[i]...Wait time of instance i (These variables depend on the value of ST[i] and a[i])
//Attended[i]...boolean variables used to determine whether an instance is Attended before the maximum waiting time or not
//
//CONSTRAINTS:
//ST[i] >= a[i]  forall i
//ET[i] = ST[i] + (rt[i] * solvable[i] * Attended[i])  forall i
//WT[i] = ST[i] - a[i]  forall i
//Attended[i] = ((WT[i] <= ewt[i]) * solvable[i])

//( ET[j] <= ST[i]-1  or  ST[j] >= ET[i]+1 )  forall i, i   if i!=j....This disjunction constraints avoids overlapping

//
//OBJECTIVE FUNCTION:
//maximize(C*sum(Attended[i]*solvable[i]) -WT[i] )
//Maximize attended instances that are solvable.

//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//Model3: Model with disjunction constraints and with maximum expected waiting times  for multiple machines
//PARAMETERS:
//a[i]...arrival time of instance i
//e[i]...execution time of instance i (It may be an estimation or the real value)
//ewt[i]...maximum expected waiting time of instance i. If an instance waiting time is greater than this value,
//then it is not Attended
//m...number of machines
//nextEndTime[k]...estimated time when machines become available

//VARIABLES:
//ST[i]...Start time of instance i (These are the decision variables)
//ET[i]...End time of instance i (These variables depend on the value of ST[i] and e[i])
//WT[i]...Wait time of instance i (These variables depend on the value of ST[i] and a[i])
//Attended[i]...boolean variables used to determine whether an instance is Attended before the maximum waiting time or not
//x[i][k]...binary array per instance i. This array represents if instance i is assigned to machine k.
//
//CONSTRAINTS:
//ST[i] >= a[i]  forall i
//ET[i] = ST[i] + (e[i]*Attended[i])  forall i
//WT[i] = ST[i] - a[i]  forall i
//Attended[i] = (WT[i] <= ewt[i])

//If instance i is assigned to machine k, it has to start after the machine becomes available
//ST[i] * X[i][k]  >= (nextEndTime[k] + 1 ) * X[i][k]

//Disjunctions to avoid overlapping in each machine k
//ET[j] * x[i][k] * x[j][k] <= (ST[i] -1) * x[i][k] * x[j][k])
//or
//ST[j] * x[i][k] * x[j][k] >= (ET[i] +1) * x[i][k] * x[j][k]

//(The end time of instance j has to be smaller than the start time of instance i...if they are both assigned to machine k)
//or
//(The start time of instance j has to be greater than the end time of instance i...if they are both assigned to machine k)

//
//OBJECTIVE FUNCTION:
//minimize(C*sum(1 - Attended[i]) + sum(WT[i]) )

//minimize(C*sum(1 - Attended[i]) + sum(WT[i])*(1 - Attended[i]) ) #Maximize attended instances and Minimize instances that waited but were not attended

//It can also be written as: minimize(-C*sum(Attended[1]) + sum(WT[i]) )
//
//C is the cost of solving an instance...If C is greater than instances cap time, then the function gives priority
//to maximize the number of Attended instances and then to minimize the waiting times.


//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////
//Model4: Model with with maximum expected waiting times for multiple machines and Solvable constraints
//PARAMETERS:
//a[i]...arrival time of instance i
//e[i]...execution time of instance i (It may be an estimation or the real value)
//ewt[i]...maximum expected waiting time of instance i. If an instance waiting time is greater than this value,
//then it is not Attended
//m...number of machines
//solvable[i]...array indicating if an instance is solvable or not (0,1)
//nextEndTime[k]...estimated time when machines become available

//VARIABLES:
//ST[i]...Start time of instance i (These are the decision variables)
//ET[i]...End time of instance i (These variables depend on the value of ST[i] and e[i])
//WT[i]...Wait time of instance i (These variables depend on the value of ST[i] and a[i])
//Attended[i]...boolean variables used to determine whether an instance is Attended before the maximum waiting time or not
//X[i][k]...binary array per instance i and machine k. This array represents if instance i is assigned to machine k.
//
//CONSTRAINTS:
//ST[i] >= a[i]  forall i
//ET[i] = ST[i] + (e[i]*Attended[i])  forall i
//WT[i] = ST[i] - a[i]  forall i
//Attended[i] = (WT[i] <= ewt[i])

//If instance i is assigned to machine k, it has to start after the machine becomes available
//ST[i] * X[i][k]  >= (nextEndTime[k] + 1 ) * X[i][k]

//Disjunctions to avoid overlapping in each machine k
//ET[j] * X[i][k] * X[j][k] <= (ST[i] -1) * X[i][k] * X[j][k])
//or
//ST[j] * X[i][k] * X[j][k] >= (ET[i] +1) * X[i][k] * X[j][k]

//(The end time of instance j has to be smaller than the start time of instance i...if they are both assigned to machine k)
//or
//(The start time of instance j has to be greater than the end time of instance i...if they are both assigned to machine k)

//
//OBJECTIVE FUNCTION:
//maximize(C*sum(Attended[i]*solvable[i]) -WT[i] )
//Maximize attended instances that are solvable.






import ilog.concert.IloException;
import ilog.concert.IloIntExpr;
import ilog.concert.IloIntVar;
import ilog.concert.IloLinearNumExpr;
import ilog.concert.IloNumVar;
import ilog.cplex.IloCplex;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

public class Schedule {

	public static void main(String[] args){

		if(args.length != 11)
	    {
	        System.out.println("Proper Usage is: java program instanceArrivalTimesCSV instanceRunTimesCSV instanceMaximumExpectedWaitingTimeCSV C searchTime searchGap nextEndTimeCSV instanceSolvableCSV option fileName machines");
	        System.out.println("-The first three parameters must be comma separated values. e.g., \"10,130,513,1060\" ");
	        System.out.println("-C must be an integer value");
	        System.out.println("-searchTime must be given in seconds (use searchTime=0 to disable this parameter)");
	        System.out.println("-searchGap must be a number from 0 to 1 (use searchGap=0 to disable this parameter)");
	        System.out.println("-nextEndTimeCSV represents the when machines become available, no instance should begin before this time in a machine k");
	        System.out.println("-instanceSolvableCSV represents if an instance is thought to be solvable or not. It must be comma separated values. e.g., \"1,0,1,1\"  (use instanceSolvableCSV=0 to disable this parameter)");
	        System.out.println("-option is either the word \"predictions\" or \"real\", in order to select appropriate constraints according to the type of data");
	        System.out.println("-fileName represents the name of the output files)");
	        System.out.println("-machines represents the number of machines)");

	        System.exit(0);
	    }

		String instanceArrivalTimesCSV=args[0];
		String instanceRunTimesCSV=args[1];
		String instanceMaximumExpectedWaitingTimeCSV=args[2];
		int C=Integer.parseInt(args[3]);
		int searchTime=Integer.parseInt(args[4]);
		double searchGap=Double.parseDouble(args[5]);
		String nextEndTimeCSV=args[6];
		String instanceSolvableCSV=args[7];
		String option=args[8];
		String fileName=args[9];
		int m=Integer.parseInt(args[10]);

		int[] nextEndTime= stringToArray(nextEndTimeCSV);
		int[] a= stringToArray(instanceArrivalTimesCSV);
		int[] rt= stringToArray(instanceRunTimesCSV);
		int[] ewt= stringToArray(instanceMaximumExpectedWaitingTimeCSV);
		int[] solvable= stringToArray(instanceSolvableCSV);

		System.out.println("instanceArrivalTimesCSV: "+instanceArrivalTimesCSV);
		System.out.println("instanceRunTimesCSV: "+instanceRunTimesCSV);
		System.out.println("instanceMaximumExpectedWaitingTimeCSV: "+instanceMaximumExpectedWaitingTimeCSV);
		System.out.println("nextEndTimeCSV: "+nextEndTimeCSV);
		System.out.println("machines: "+m);


			if(a.length != rt.length){
		        System.out.println("The number of instance arrivals does not match the number of runtimes");
		        System.exit(0);
		    }else if( a.length != ewt.length ){
		    	System.out.println("The number of instance arrivals does not match the number of expected waiting times");
		    	System.exit(0);
		    }else if(searchGap > 1){
		    	System.out.println("The searchGap must be a number from 0 to 1 (use searchGap=0 to disable this parameter)");
		        System.exit(0);
		    }else if(searchTime < 0){
		    	System.out.println("The searchTime must be given in seconds (use searchTime=0 to disable this parameter)");
		        System.exit(0);
		    }else if(C < 0){
		    	System.out.println("C must be an integer value");
		        System.exit(0);
		    }else{
		    	if(option.equals("model1")){
		    		Model1(a, rt, ewt, C, searchTime, searchGap, fileName, nextEndTime);//Model for a single machine (Regression estimations)
		    	}else if(option.equals("model2")){
		    		Model2(a, rt, ewt, C, searchTime, searchGap, fileName, nextEndTime, solvable);//Model for a single machine (Regression/classification estimations)
		    	}else if(option.equals("model3")){
		    		Model3(a, rt, ewt, C, searchTime, searchGap, fileName, nextEndTime, m);//Model for m machines (Regression estimations)
		    	}else if(option.equals("model4")){
		    		Model4(a, rt, ewt, C, searchTime, searchGap, fileName, nextEndTime, m, solvable);//Model for m machines (Regression/classification estimations)
		    	}else{
		    		System.out.println("Unknown model");
		    	}
			}

	}

////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////


public static void Model1(int []a, int []rt, int []ewt, int C, int searchTime, double searchGap, String fileName, int[] nextEndTime){
	System.out.println("Model 1");
	try{
		int n=a.length;
		IloCplex cplex=new IloCplex();
		//ST[i] represent the starting time of instance i
		IloNumVar[]ST=new IloNumVar[n];
		//ET[i] represent the end time of instance i
		IloNumVar[]ET=new IloNumVar[n];
		//ST[i] represent the waiting time of instance i
		IloNumVar[]WT=new IloNumVar[n];
		//Attended[i] checks if an instance is Attended or not
		IloIntVar[]Attended=cplex.boolVarArray(n);

		for(int i=0;i<n;i++) {
			ST[i]=cplex.intVar(0, Integer.MAX_VALUE , "StartTime("+i+")");
			ET[i]=cplex.intVar(0, Integer.MAX_VALUE , "EndTime("+i+")");
			WT[i]=cplex.intVar(0, Integer.MAX_VALUE , "WaitTime("+i+")");
			Attended[i]=cplex.boolVar("Attended("+i+")");

			cplex.addGe( ST[i], a[i] );
			cplex.addGe( ST[i], nextEndTime[0]+1 );
			cplex.addEq( ET[i], cplex.sum(ST[i],cplex.prod(rt[i],Attended[i])));
			cplex.addEq( WT[i], cplex.sum(ST[i], -1*a[i]));
			cplex.addEq( Attended[i], cplex.le(WT[i],ewt[i]));
		}

		for(int i=0;i<n;i++) {
			for(int j=0;j<n;j++) {
				if(i!=j){
					cplex.addEq(1, cplex.or(cplex.le(ET[j], cplex.sum(ST[i],-1) ), cplex.ge(ST[j], cplex.sum(ET[i],1))));
				}
			}
		}


		IloLinearNumExpr Addition = cplex.linearNumExpr();


		for(int i=0;i<n;i++) {
			Addition.addTerm(C, Attended[i]);
			Addition.addTerm(-rt[i], Attended[i]);
		}

		cplex.addMaximize(Addition);


		if(searchTime!=0){ cplex.setParam(IloCplex.DoubleParam.TiLim, searchTime);}
		if(searchGap!=0){ cplex.setParam(IloCplex.DoubleParam.EpGap, searchGap); }
		cplex.setParam(IloCplex.IntParam.Threads, 1);//Run in a single thread

		if(cplex.solve()){
			showResults(a, rt, cplex, ST, ET, WT, Attended, null, 1);
			createCSV(a, rt, cplex, ST, ET, WT, Attended, fileName, null, 1);
		}else{

			System.out.println("Model not solved..."+cplex.getStatus());
		}
		cplex.end();
	}catch(IloException exc){
		exc.printStackTrace();
	}
}
////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////


public static void Model2(int []a, int []rt, int []ewt, int C, int searchTime, double searchGap, String fileName, int[] nextEndTime, int []solvable){
	System.out.println("Model 2");
	try{
		int n=a.length;
		IloCplex cplex=new IloCplex();
		//ST[i] represent the starting time of instance i
		IloNumVar[]ST=new IloNumVar[n];
		//ET[i] represent the end time of instance i
		IloNumVar[]ET=new IloNumVar[n];
		//ST[i] represent the waiting time of instance i
		IloNumVar[]WT=new IloNumVar[n];
		//Attended[i] checks if an instance is Attended or not
		IloIntVar[]Attended=cplex.boolVarArray(n);


		for(int i=0;i<n;i++) {
			ST[i]=cplex.intVar(0, Integer.MAX_VALUE , "StartTime("+i+")");
			ET[i]=cplex.intVar(0, Integer.MAX_VALUE , "EndTime("+i+")");
			WT[i]=cplex.intVar(0, Integer.MAX_VALUE , "WaitTime("+i+")");
			Attended[i]=cplex.boolVar("Attended("+i+")");

			cplex.addGe( ST[i], a[i] );
			cplex.addGe( ST[i], nextEndTime[0]+1 );
			cplex.addEq( ET[i], cplex.sum(ST[i],cplex.prod(rt[i],Attended[i])));
			cplex.addEq( WT[i], cplex.sum(ST[i], -1*a[i]));
			cplex.addEq( Attended[i], cplex.le(WT[i],ewt[i]));


			cplex.addGe( ST[i], a[i] );
			cplex.addGe( ST[i], nextEndTime[0]+1 );
			cplex.addEq( ET[i], cplex.sum(ST[i],cplex.prod(rt[i]*solvable[i],Attended[i])));//If we have perfect estimations
			cplex.addEq( WT[i], cplex.sum(ST[i], -1*a[i]));
			cplex.addEq( Attended[i], cplex.prod(solvable[i],cplex.le(WT[i],ewt[i])));//If we have perfect estimations
		}

		for(int i=0;i<n;i++) {
			for(int j=0;j<n;j++) {
				if(i!=j){
					cplex.addEq(1, cplex.or(cplex.le(ET[j], cplex.sum(ST[i],-1) ), cplex.ge(ST[j], cplex.sum(ET[i],1))));
				}
			}
		}

		IloLinearNumExpr Addition = cplex.linearNumExpr();

		for(int i=0;i<n;i++) {
			Addition.addTerm(C, Attended[i]);
			Addition.addTerm(-rt[i], Attended[i]);
		}

		cplex.addMaximize(Addition);

		if(searchTime!=0){ cplex.setParam(IloCplex.DoubleParam.TiLim, searchTime);}
		if(searchGap!=0){ cplex.setParam(IloCplex.DoubleParam.EpGap, searchGap); }
		cplex.setParam(IloCplex.IntParam.Threads, 1);//Run in a single thread

		if(cplex.solve()){
			showResults(a, rt, cplex, ST, ET, WT, Attended, null, 1);
			createCSV(a, rt, cplex, ST, ET, WT, Attended, fileName, null, 1);
		}else{

			System.out.println("Model not solved..."+cplex.getStatus());
		}
		cplex.end();
	}catch(IloException exc){
		exc.printStackTrace();
	}
}



////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////

public static void Model3(int []a, int []e, int []ewt, int C, int searchTime, double searchGap, String fileName, int []nextEndTime, int m){
	System.out.println("Model 3");
	try{
		int n=a.length;
		IloCplex cplex=new IloCplex();
		//ST[i] represent the starting time of instance i
		IloNumVar[]ST=new IloNumVar[n];
		//ET[i] represent the end time of instance i
		IloNumVar[]ET=new IloNumVar[n];
		//ST[i] represent the waiting time of instance i
		IloNumVar[]WT=new IloNumVar[n];
		//Attended[i] checks if an instance is Attended or not
		IloIntVar[]Attended=cplex.boolVarArray(n);
		//X[i][k] represent if an instance i is assigned to a machine k
		IloNumVar[][]X=new IloNumVar[n][];

		/////////////////////////////////////////////////////////////////////
		//Start time (ST) and end time (ET) constraints
		/////////////////////////////////////////////////////////////////////
		for(int i=0;i<n;i++) {
			ST[i]=cplex.intVar(0, Integer.MAX_VALUE , "StartTime("+i+")");
			ET[i]=cplex.intVar(0, Integer.MAX_VALUE , "EndTime("+i+")");
			WT[i]=cplex.intVar(0, Integer.MAX_VALUE , "WaitTime("+i+")");
			Attended[i]=cplex.boolVar("Attended("+i+")");
			X[i] = cplex.boolVarArray(m);

			cplex.addGe( ST[i], a[i] );
			//cplex.addGe( ST[i], nextEndTime[0]+1 );
			cplex.addEq( ET[i], cplex.sum(ST[i],cplex.prod(e[i],Attended[i])));
			cplex.addEq( WT[i], cplex.sum(ST[i], -1*a[i]));
			cplex.addEq( Attended[i], cplex.le(WT[i],ewt[i]));

			int UpperBound=Max(nextEndTime)*10;//This is an estimated upper bound for the constraints. Its 10 times bigger than the maximum end time.

			IloLinearNumExpr OnlyOneMachinePerInstance = cplex.linearNumExpr();
			for(int k=0;k<m;k++){

				//To represent a multiplication xy, where x is binary and y is a variable:
				//z<= Ux
				//z>= Lx
				//z<= y - L(1-x)
				//z>= y - U(1-x)


				//ST[i] * X[i][k]  >= (nextEndTime[k] + 1 ) * X[i][k]

				//ST[i] * X[i][k]
				IloNumVar auxst1=cplex.intVar(0, UpperBound );
				cplex.addLe(auxst1,  cplex.prod(UpperBound , X[i][k]));
				cplex.addGe(auxst1,  cplex.prod(a[i] , X[i][k]));
				cplex.addLe(auxst1,  cplex.sum(ST[i], cplex.prod(-a[i], cplex.sum(1, cplex.negative(X[i][k])))));
				cplex.addGe(auxst1,  cplex.sum(ST[i], cplex.prod(-UpperBound, cplex.sum(1, cplex.negative(X[i][k])))));

				//(nextEndTime[k] + 1 ) * X[i][k]
				IloNumVar auxst2=cplex.intVar(0, UpperBound );
				cplex.addLe(auxst2,  cplex.prod(UpperBound , X[i][k]));
				cplex.addGe(auxst2,  cplex.prod(nextEndTime[k] + 1 , X[i][k]));
				cplex.addLe(auxst2,  cplex.sum((nextEndTime[k] + 1), cplex.prod(- (nextEndTime[k]+1) , cplex.sum(1, cplex.negative(X[i][k])))));
				cplex.addGe(auxst2,  cplex.sum((nextEndTime[k] + 1), cplex.prod(-UpperBound, cplex.sum(1, cplex.negative(X[i][k])))));

				cplex.addGe(auxst1, auxst2);



				OnlyOneMachinePerInstance.addTerm(1, X[i][k]);
			}
			cplex.addEq(OnlyOneMachinePerInstance, 1);




		}


		for(int k=0;k<m;k++){
			for(int i=0;i<n;i++) {
				for(int j=0;j<n;j++) {
					if(i!=j){

						//To represent a multiplication xy, where x is binary and y is a variable:
						//z<= Ux
						//z>= Lx
						//z<= y - L(1-x)
						//z>= y - U(1-x)


						//ET[j] * x[i][k] * x[j][k] <= (ST[i] -1) * x[i][k] * x[j][k])
						//or
						//ST[j] * x[i][k] * x[j][k] >= (ET[i] +1) * x[i][k] * x[j][k]

						IloNumVar auxProd=cplex.boolVar();
						cplex.addEq(auxProd, cplex.and( cplex.eq(X[i][k],1), cplex.eq(X[j][k],1)));

						int UpperBound=Max(nextEndTime)*10;//This is an estimated upper bound for the constraints. Its 10 times bigger than the maximum end time.


						//ET[j] * auxProd
						IloNumVar aux1=cplex.intVar(0, UpperBound );
						cplex.addLe(aux1,  cplex.prod(UpperBound , auxProd));
						cplex.addGe(aux1,  cplex.prod(1 , auxProd));
						cplex.addLe(aux1,  cplex.sum(ET[j], cplex.prod(-1, cplex.sum(1, cplex.negative(auxProd)))));
						cplex.addGe(aux1,  cplex.sum(ET[j], cplex.prod(-UpperBound, cplex.sum(1, cplex.negative(auxProd)))));


						//(ST[i] -1) * auxProd
						IloNumVar aux2=cplex.intVar(0, UpperBound );
						cplex.addLe(aux2,  cplex.prod(UpperBound , auxProd));
						cplex.addGe(aux2,  cplex.prod(1 , auxProd));
						cplex.addLe(aux2,  cplex.sum(cplex.sum(ST[i],-1), cplex.prod(-1, cplex.sum(1, cplex.negative(auxProd)))));
						cplex.addGe(aux2,  cplex.sum(cplex.sum(ST[i],-1), cplex.prod(-UpperBound, cplex.sum(1, cplex.negative(auxProd)))));



						//ST[j] * auxProd
						IloNumVar aux3=cplex.intVar(0,UpperBound);
						cplex.addLe(aux3,  cplex.prod(UpperBound , auxProd));
						cplex.addGe(aux3,  cplex.prod(1 , auxProd));
						cplex.addLe(aux3,  cplex.sum(ST[j], cplex.prod(-1, cplex.sum(1, cplex.negative(auxProd)))));
						cplex.addGe(aux3,  cplex.sum(ST[j], cplex.prod(-UpperBound, cplex.sum(1, cplex.negative(auxProd)))));


						//(ET[i] +1) * auxProd
						IloNumVar aux4=cplex.intVar(0, UpperBound );
						cplex.addLe(aux4,  cplex.prod(UpperBound , auxProd));
						cplex.addGe(aux4,  cplex.prod(1 , auxProd));
						cplex.addLe(aux4,  cplex.sum(cplex.sum(ET[i],1), cplex.prod(-1, cplex.sum(1, cplex.negative(auxProd)))));
						cplex.addGe(aux4,  cplex.sum(cplex.sum(ET[i],1), cplex.prod(-UpperBound, cplex.sum(1, cplex.negative(auxProd)))));


						cplex.addEq(1,
								cplex.or(

										cplex.le(
												aux1 ,
												aux2
												),
												cplex.ge(
														aux3,
														aux4
														)
										)
								);


					}
				}
			}
		}


		//Minimize the addition of waiting times
		////* minimize(-C*sum(Attended[i]) + sum(WT[i]) )
		IloLinearNumExpr Addition = cplex.linearNumExpr();

		for(int i=0;i<n;i++) {
			Addition.addTerm(C, Attended[i]);
			Addition.addTerm(-e[i], Attended[i]);
		}

		cplex.addMaximize(Addition);

		if(searchTime!=0){ cplex.setParam(IloCplex.DoubleParam.TiLim, searchTime);}
		if(searchGap!=0){ cplex.setParam(IloCplex.DoubleParam.EpGap, searchGap); }
		cplex.setParam(IloCplex.IntParam.Threads, 1);//Run in a single thread

		if(cplex.solve()){
			showResults(a, e, cplex, ST, ET, WT, Attended, X,  m);
			createCSV(a, e, cplex, ST, ET, WT, Attended, fileName, X,  m);
		}else{

			System.out.println("Model not solved..."+cplex.getStatus());
		}
		cplex.end();
	}catch(IloException exc){
		exc.printStackTrace();
	}
}


////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////

public static void Model4(int []a, int []e, int []ewt, int C, int searchTime, double searchGap, String fileName, int []nextEndTime, int m, int []solvable){
	System.out.println("Model 4");
	try{
		int n=a.length;
		IloCplex cplex=new IloCplex();
		//ST[i] represent the starting time of instance i
		IloNumVar[]ST=new IloNumVar[n];
		//ET[i] represent the end time of instance i
		IloNumVar[]ET=new IloNumVar[n];
		//ST[i] represent the waiting time of instance i
		IloNumVar[]WT=new IloNumVar[n];
		//Attended[i] checks if an instance is Attended or not
		IloIntVar[]Attended=cplex.boolVarArray(n);
		//X[i][k] represent if an instance i is assigned to a machine k
		IloNumVar[][]X=new IloNumVar[n][];

		/////////////////////////////////////////////////////////////////////
		//Start time (ST) and end time (ET) constraints
		/////////////////////////////////////////////////////////////////////
		for(int i=0;i<n;i++) {
			ST[i]=cplex.intVar(0, Integer.MAX_VALUE , "StartTime("+i+")");
			ET[i]=cplex.intVar(0, Integer.MAX_VALUE , "EndTime("+i+")");
			WT[i]=cplex.intVar(0, Integer.MAX_VALUE , "WaitTime("+i+")");
			Attended[i]=cplex.boolVar("Attended("+i+")");
			X[i] = cplex.boolVarArray(m);

			cplex.addGe( ST[i], a[i] );
			//cplex.addGe( ST[i], nextEndTime[0]+1 );
			//cplex.addEq( ET[i], cplex.sum(ST[i],cplex.prod(e[i],Attended[i])));
			cplex.addEq( ET[i], cplex.sum(ST[i],cplex.prod(e[i]*solvable[i],Attended[i])));//If we have perfect estimations
			cplex.addEq( WT[i], cplex.sum(ST[i], -1*a[i]));
			//cplex.addEq( Attended[i], cplex.le(WT[i],ewt[i]));
			cplex.addEq( Attended[i], cplex.prod(solvable[i],cplex.le(WT[i],ewt[i])));//If we have perfect estimations


			int UpperBound=Max(nextEndTime)*10;//This is an estimated upper bound for the constraints. Its 10 times bigger than the maximum end time.

			IloLinearNumExpr OnlyOneMachinePerInstance = cplex.linearNumExpr();
			for(int k=0;k<m;k++){

				//To represent a multiplication xy, where x is binary and y is a variable:
				//z<= Ux
				//z>= Lx
				//z<= y - L(1-x)
				//z>= y - U(1-x)


				//ST[i] * X[i][k]  >= (nextEndTime[k] + 1 ) * X[i][k]

				//ST[i] * X[i][k]
				IloNumVar auxst1=cplex.intVar(0, UpperBound );
				cplex.addLe(auxst1,  cplex.prod(UpperBound , X[i][k]));
				cplex.addGe(auxst1,  cplex.prod(a[i] , X[i][k]));
				cplex.addLe(auxst1,  cplex.sum(ST[i], cplex.prod(-a[i], cplex.sum(1, cplex.negative(X[i][k])))));
				cplex.addGe(auxst1,  cplex.sum(ST[i], cplex.prod(-UpperBound, cplex.sum(1, cplex.negative(X[i][k])))));

				//(nextEndTime[k] + 1 ) * X[i][k]
				IloNumVar auxst2=cplex.intVar(0, UpperBound );
				cplex.addLe(auxst2,  cplex.prod(UpperBound , X[i][k]));
				cplex.addGe(auxst2,  cplex.prod(nextEndTime[k] + 1 , X[i][k]));
				cplex.addLe(auxst2,  cplex.sum((nextEndTime[k] + 1), cplex.prod(- (nextEndTime[k]+1) , cplex.sum(1, cplex.negative(X[i][k])))));
				cplex.addGe(auxst2,  cplex.sum((nextEndTime[k] + 1), cplex.prod(-UpperBound, cplex.sum(1, cplex.negative(X[i][k])))));

				cplex.addGe(auxst1, auxst2);


				OnlyOneMachinePerInstance.addTerm(1, X[i][k]);
			}
			cplex.addEq(OnlyOneMachinePerInstance, 1);

		}


		for(int k=0;k<m;k++){
			for(int i=0;i<n;i++) {
				for(int j=0;j<n;j++) {
					if(i!=j){

						//To represent a multiplication xy, where x is binary and y is a variable:
						//z<= Ux
						//z>= Lx
						//z<= y - L(1-x)
						//z>= y - U(1-x)


						//ET[j] * x[i][k] * x[j][k] <= (ST[i] -1) * x[i][k] * x[j][k])
						//or
						//ST[j] * x[i][k] * x[j][k] >= (ET[i] +1) * x[i][k] * x[j][k]

						IloNumVar auxProd=cplex.boolVar();
						cplex.addEq(auxProd, cplex.and( cplex.eq(X[i][k],1), cplex.eq(X[j][k],1)));

						int UpperBound=Max(nextEndTime)*10;//This is an estimated upper bound for the constraints. Its 10 times bigger than the maximum end time.


						//ET[j] * auxProd
						IloNumVar aux1=cplex.intVar(0, UpperBound );
						cplex.addLe(aux1,  cplex.prod(UpperBound , auxProd));
						cplex.addGe(aux1,  cplex.prod(1 , auxProd));
						cplex.addLe(aux1,  cplex.sum(ET[j], cplex.prod(-1, cplex.sum(1, cplex.negative(auxProd)))));
						cplex.addGe(aux1,  cplex.sum(ET[j], cplex.prod(-UpperBound, cplex.sum(1, cplex.negative(auxProd)))));


						//(ST[i] -1) * auxProd
						IloNumVar aux2=cplex.intVar(0, UpperBound );
						cplex.addLe(aux2,  cplex.prod(UpperBound , auxProd));
						cplex.addGe(aux2,  cplex.prod(1 , auxProd));
						cplex.addLe(aux2,  cplex.sum(cplex.sum(ST[i],-1), cplex.prod(-1, cplex.sum(1, cplex.negative(auxProd)))));
						cplex.addGe(aux2,  cplex.sum(cplex.sum(ST[i],-1), cplex.prod(-UpperBound, cplex.sum(1, cplex.negative(auxProd)))));



						//ST[j] * auxProd
						IloNumVar aux3=cplex.intVar(0,UpperBound);
						cplex.addLe(aux3,  cplex.prod(UpperBound , auxProd));
						cplex.addGe(aux3,  cplex.prod(1 , auxProd));
						cplex.addLe(aux3,  cplex.sum(ST[j], cplex.prod(-1, cplex.sum(1, cplex.negative(auxProd)))));
						cplex.addGe(aux3,  cplex.sum(ST[j], cplex.prod(-UpperBound, cplex.sum(1, cplex.negative(auxProd)))));


						//(ET[i] +1) * auxProd
						IloNumVar aux4=cplex.intVar(0, UpperBound );
						cplex.addLe(aux4,  cplex.prod(UpperBound , auxProd));
						cplex.addGe(aux4,  cplex.prod(1 , auxProd));
						cplex.addLe(aux4,  cplex.sum(cplex.sum(ET[i],1), cplex.prod(-1, cplex.sum(1, cplex.negative(auxProd)))));
						cplex.addGe(aux4,  cplex.sum(cplex.sum(ET[i],1), cplex.prod(-UpperBound, cplex.sum(1, cplex.negative(auxProd)))));


						cplex.addEq(1,
								cplex.or(

										cplex.le(
												aux1 ,
												aux2
												),
												cplex.ge(
														aux3,
														aux4
														)
										)
								);


					}
				}
			}
		}

		//Minimize the addition of waiting times
		//maximize(sum(Attended[i]*solvable[i])
		IloLinearNumExpr Addition = cplex.linearNumExpr();

		for(int i=0;i<n;i++) {
			Addition.addTerm(C, Attended[i]);
			Addition.addTerm(-e[i], Attended[i]);
		}

		cplex.addMaximize(Addition);

		if(searchTime!=0){ cplex.setParam(IloCplex.DoubleParam.TiLim, searchTime);}
		if(searchGap!=0){ cplex.setParam(IloCplex.DoubleParam.EpGap, searchGap); }
		cplex.setParam(IloCplex.IntParam.Threads, 1);//Run in a single thread

		if(cplex.solve()){
			showResults(a, e, cplex, ST, ET, WT, Attended, X,  m);
			createCSV(a, e, cplex, ST, ET, WT, Attended, fileName, X,  m);
		}else{
			System.out.println("Model not solved..."+cplex.getStatus());
		}
		cplex.end();
	}catch(IloException exc){
		exc.printStackTrace();
	}
}

////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
public static int Max(int []array){

	int m=0;
	for (int i=0; i < array.length; i++) {
		if (array[i]>m){
			m=array[i];
		}
	}
	return m;
}
////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
	public static int [] stringToArray(String s){
		String[] aux= s.split(",");
		int[] auxArray = new int[aux.length];
		for (int i=0; i < aux.length; i++) {
	        auxArray[i] = Integer.parseInt(aux[i]);
	    }
		return auxArray;
	}

/*
	public static int [] stringToArray(String s){
		String[] aux= s.split(",");
		int tam = aux.length;
		k = 4;
		if (tam > k){ tam = k; }
		int[] auxArray = new int[tam];
		for (int i=0; i < tam; i++) {
	            auxArray[i] = Integer.parseInt(aux[i]);
	    }
		return auxArray;
	}

	*/
////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
	public static void showResults(int []a, int []rt, IloCplex cplex, IloNumVar[]ST, IloNumVar[]ET, IloNumVar[]WT, IloIntVar[]Attended, IloNumVar[][]X, int m){
		try{
			System.out.println("");
			System.out.println("Obj="+cplex.getObjValue());
			System.out.println("Best Relaxation Obj="+cplex.getBestObjValue());
			System.out.println("GAP="+((cplex.getObjValue()-cplex.getBestObjValue())/cplex.getObjValue()));
			System.out.println("");

			System.out.println("PredictedServiceTime,ArrivalTime,MIPPredictedTimeServiceBegins,MIPPredictedTimeServiceEnds,MIPWaitingTimeInQueue,MIPAttended,MIPVM");


			for(int i=0;i<a.length;i++) {
				System.out.print(rt[i]+",");
				System.out.print(a[i]+",");
				System.out.print(Math.round(cplex.getValue(ST[i]))+",");
				System.out.print(Math.round(cplex.getValue(ET[i]))+",");
				System.out.print(Math.round(cplex.getValue(WT[i]))+",");
				System.out.print(Math.round(cplex.getValue(Attended[i]))+",");

				if (m > 1){
					for(int k=0;k<m;k++){
					   if( Math.round(cplex.getValue(X[i][k])) == 1){
						   System.out.print(k);

					   }
					}
				}else{
					System.out.print("1");
				}

				System.out.println("");
			}

		}catch(IloException exc){
			exc.printStackTrace();
		}
	}






////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////
	public static void createCSV(int []a, int []e, IloCplex cplex, IloNumVar[]ST, IloNumVar[]ET, IloNumVar[]WT, IloIntVar[]Attended, String fileName, IloNumVar[][]X, int m){
		try {
			////////////////////////////////////////////////////////////////////////////////////////////////
			////////////////////////////////////////////////////////////////////////////////////////////////
			//PrintWriter pw = new PrintWriter(new File(fileName+"_Obj.csv"));
			//PrintWriter pw = new PrintWriter(new File(fileName+"_Obj.csv"));
			FileWriter pw;
			StringBuilder sb = new StringBuilder();


			pw = new FileWriter(fileName+"_Obj.csv", true);//True allows appending
			sb.append("ObjectiveValue,BestRelaxation,Gap\n");


			sb.append(cplex.getObjValue());
			sb.append(',');
			sb.append(cplex.getBestObjValue());
			sb.append(',');
			if (cplex.getObjValue()!=0){
				sb.append(((cplex.getObjValue()-cplex.getBestObjValue())/cplex.getObjValue()));
			}else{ sb.append("0"); }
			sb.append('\n');

			pw.write(sb.toString());
			pw.close();
			////////////////////////////////////////////////////////////////////////////////////////////////
			////////////////////////////////////////////////////////////////////////////////////////////////
			//PrintWriter pw2 = new PrintWriter(new File(fileName+"_testResults.csv"));
			FileWriter pw2;
			StringBuilder sb2 = new StringBuilder();


			pw2 = new FileWriter(fileName+"_scheduleResults.csv", true);//True allows appending
			sb2.append("PredictedServiceTime,ArrivalTime,MIPPredictedTimeServiceBegins,MIPPredictedTimeServiceEnds,MIPWaitingTimeInQueue,MIPAttended,MIPVM\n");


			for(int i=0;i<a.length;i++) {
				sb2.append(e[i]);
				sb2.append(',');
				sb2.append(a[i]);
				sb2.append(',');
				sb2.append(Math.round(cplex.getValue(ST[i])));
				sb2.append(',');
				sb2.append(Math.round(cplex.getValue(ET[i])));
				sb2.append(',');
				sb2.append(Math.round(cplex.getValue(WT[i])));
				sb2.append(',');
				sb2.append(Math.round(cplex.getValue(Attended[i])));
				sb2.append(',');
				if (m > 1){
					for(int k=0;k<m;k++){

					   if( Math.round(cplex.getValue(X[i][k])) == 1){
						   sb2.append(k);

					   }
					}
				}else{
					sb2.append(1);
				}

				sb2.append('\n');
			}
			pw2.write(sb2.toString());
			pw2.close();

            //Temporal file
			FileWriter pw3;
			StringBuilder sb3 = new StringBuilder();
			pw3 = new FileWriter(fileName+"_Temp.csv");
			sb3.append("PredictedServiceTime,ArrivalTime,MIPPredictedTimeServiceBegins,MIPPredictedTimeServiceEnds,MIPWaitingTimeInQueue,MIPAttended,MIPVM\n");
			for(int i=0;i<a.length;i++) {
				sb3.append(e[i]);
				sb3.append(',');
				sb3.append(a[i]);
				sb3.append(',');
				sb3.append(Math.round(cplex.getValue(ST[i])));
				sb3.append(',');
				sb3.append(Math.round(cplex.getValue(ET[i])));
				sb3.append(',');
				sb3.append(Math.round(cplex.getValue(WT[i])));
				sb3.append(',');
				sb3.append(Math.round(cplex.getValue(Attended[i])));
				sb3.append(',');
				if (m > 1){
					for(int k=0;k<m;k++){

					   if( Math.round(cplex.getValue(X[i][k])) == 1){
						   sb3.append(k);

					   }
					}
				}else{
					sb3.append(1);
				}

				sb3.append('\n');
			}
			pw3.write(sb3.toString());
			pw3.close();
			////////////////////////////////////////////////////////////////////////////////////////////////
			////////////////////////////////////////////////////////////////////////////////////////////////

		} catch (FileNotFoundException excp) {
			excp.printStackTrace();
		}catch(IloException exc){
			exc.printStackTrace();
		} catch (IOException e1) {
			e1.printStackTrace();
		}
	}

}

