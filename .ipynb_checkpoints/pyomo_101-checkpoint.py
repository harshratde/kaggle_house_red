#import pyomo.environ as pyo
#from pyomo.opt import SolverFactory

from pyomo.environ import *
import pyomo
import pyomo.opt
import pyomo.environ as pe

solver_name = 'gplk'
solverpath_exe='D:\\DS\\PROJECTS\\gplk\\glpk-4.65\\w64\\glpsol'


model = pyo.ConcreteModel()
model.nVars = pyo.Param(initialize=4)
model.N = pyo.RangeSet(model.nVars)
model.x = pyo.Var(model.N, within=pyo.Binary)
model.obj = pyo.Objective(expr=pyo.summation(model.x))
model.cuts = pyo.ConstraintList()

#opt1 = SolverFactory(solver_name, executable=solverpath_exe)


opt = SolverFactory('gurobi')
result = opt.solve(model) 

# Iterate, adding a cut to exclude the previously found solution
for i in range(5):
    expr = 0
    for j in model.x:
        if pyo.value(model.x[j]) < 0.5:
            expr += model.x[j]
        else:
            expr += (1 - model.x[j])
    model.cuts.add( expr >= 1 )
    results = opt.solve(model)
    print ("\n===== iteration",i)
    model.display() 
    
    
    
    
    
import pandas as pd

opt_feed_fnl =  pd.DataFrame({'col1':[1,2,3,4,5,6,7]
                             ,'col2':['a','a','b','c','d','e','f']})    
opt_feed_fnl.set_index(['col2'], inplace=True)

tm_key_set           = opt_feed_fnl.index.unique()
    
#input_df =  opt_feed_fnl.copy()
#threads_input = 40
#prime_increment = 0.2
m = pe.ConcreteModel() 

# Create sets
m.input_df      = pe.Set(initialize = tm_key_set , dimen = len(['col2']))

#m.price_buck_set = pe.Set(initialize=price_buck)

m.Y     = pe.Var(m.input_df, domain=pe.NonNegativeIntegers)

def obj_rule(m):
return (sum([m.Y[e]*(input_df.loc[e, 'Floor Price'] - m.RCP[e])  for e in tm_key_set])+sum([m.Y[e]*(input_df.loc[e, 'TVR_chan'])  for e in tm_key_set]))/(sum([m.Y[e]*m.RCP[e]  for e in tm_key_set]))

m.OBJ = pe.Objective(rule=obj_rule, sense=pe.minimize)



solver = pyomo.opt.SolverFactory('baron')
#        solver.options['AllowFilterSD'] = 1
#        solver.options['BoxTol'] = 0.1
#        solver.options['DeltaTerm'] = 1
#        solver.options['CutOff'] = 1
solver.options['MaxTime'] = 1800
solver.options['threads'] = threads_input
solver.options['epsr'] = 0.01
solver.options['DoLocal'] = 0



#        solver = pyomo.opt.SolverFactory('gurobi')
#        solver.options['PSDTol'] = 1.1
#        solver.options['DualReductions'] = 0
#        solver.options['outlev'] = 1    # tell gurobi to find an iis table for the infeasible model
#        solver.options['iisfind'] = 1   # tell gurobi to be verbose with output

results = solver.solve(m,keepfiles=True,tee=True)
end_tm_cmpt = datetime.datetime.now()

print('\n-------------------')
print(end_tm_cmpt - strt_tm_cmpt)
print('-------------------\n')

print(results.solver.status)
print(results.solver.termination_condition)


if (results.solver.status != pyomo.opt.SolverStatus.ok):
logging.warning('Check solver not ok?')
if (results.solver.termination_condition != pyomo.opt.TerminationCondition.optimal):    
logging.warning('Check solver optimality?') 
