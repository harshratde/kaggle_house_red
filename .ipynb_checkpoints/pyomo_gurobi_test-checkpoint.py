
#import pyomo.environ as pyo
#from pyomo.opt import SolverFactory

from pyomo.environ import *
import pyomo
import pyomo.opt
import pyomo.environ as pe

solver_name = 'gurobi'
#solverpath_exe='/home/ec2-user/optimization/baron-lin64/baron'


model = ConcreteModel()
model.nVars = Param(initialize=4)
model.N = RangeSet(model.nVars)
model.x = Var(model.N, within=Binary)
model.obj = Objective(expr=summation(model.x))
model.cuts = ConstraintList()

#opt1 = SolverFactory(solver_name, executable=solverpath_exe)

#opt = SolverFactory(solver_name, executable=solverpath_exe)
opt = SolverFactory(solver_name)
opt.solve(model) 

# Iterate, adding a cut to exclude the previously found solution
for i in range(5):
    expr = 0
    for j in model.x:
        if value(model.x[j]) < 0.5:
            expr += model.x[j]
        else:
            expr += (1 - model.x[j])
    model.cuts.add( expr >= 1 )
    results = opt.solve(model)
    print ("\n===== iteration",i)
    model.display() 
    
#=============================================================================================    
from sklearn.linear_model import LinearRegression
lm=LinearRegression()
lm
reg_df =  pd.DataFrame({'col1':[1,2,3,4,5,6,7]
                             ,'col2':[12,23,34,54,65,96,47]})   
lm.fit(reg_df[['col1']],reg_df[['col2']])

#=============================================================================================
    
    
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

m.Y     = pe.Var(m.input_df, domain=pe.NonNegativeIntegers, bounds=(0,50),initialize=1)

def predict_ada_3(a,b):
    pred_df = pd.DataFrame({'tv_grp':[a,b]
                           , 'filter': [0,1] })
    
    pred_df['extra'] = pred_df['tv_grp'].apply(lambda x : x+1)
    pred_df['tv_grp_cum'] = pred_df['tv_grp'].cumsum()
    
    out_set = pred_df[pred_df['filter']==1]
    df_eval = out_set[['tv_grp_cum']].head(1)
    
    if value(a) <=2:
#        df_eval['out'] = df_eval['tv_grp_cum'].apply(lambda x: lm.intercept_[0]+x*lm.coef_[0]) 
        #df_eval['out'] = df_eval['tv_grp_cum'].apply(lambda x: 7+x*10) 
        
        #out = df_eval['out'][0]
        out = [7+i*10 for i in df_eval['tv_grp_cum'].tolist()][0]
    else:
        out = 20
    #pred_val = regr.predict(pred_df[['tv_grp']])
#    output_val = create_model_predict(pred_df)
    #return value(input_num)+1
    
#    if value(input_num) >= 25:
#        return 10
#    else:
#        return 5
    return out

def obj_rule(m):
    
    return (20+sum([m.Y[e]  for e in tm_key_set]) - predict_ada_3(m.Y['a'],m.Y['b'] )-40)
m.OBJ = pe.Objective(rule=obj_rule, sense=pe.maximize)


def impact_push_show_u(m):
    show_outly = (20-sum([m.Y[e]  for e in tm_key_set]) - predict_ada_3(m.Y['a'],m.Y['b'] ))
    return show_outly >= 0
m.impact_push_show_cu = pe.Constraint(rule = impact_push_show_u)


def prc_cntrl1(m,k):
    return m.Y[k] <= 5
m.prcBound1 = pe.Constraint(m.input_df,rule=prc_cntrl1)


solver = SolverFactory(solver_name)#, executable=solverpath_exe)


results = solver.solve(m,keepfiles=True,tee=True)
import datetime
end_tm_cmpt = datetime.datetime.now()

print('\n-------------------')
#print(end_tm_cmpt - strt_tm_cmpt)
print('-------------------\n')

print(results.solver.status)
print(results.solver.termination_condition)
import logging

if (results.solver.status != pyomo.opt.SolverStatus.ok):
    logging.warning('Check solver not ok?')
if (results.solver.termination_condition != pyomo.opt.TerminationCondition.optimal):    
    logging.warning('Check solver optimality?') 

#============================================================================================

master_key = 'col2'

if str(results.solver.termination_condition) != 'infeasible':
    

    dec_var = [str(v) for v in m.component_objects(Var,active=True)]
    print(dec_var)
        
    for v in dec_var:
        #if str(v) == 'Y':
        varobject = getattr(m, str(v))
        print(v)
        print(varobject)
            
        opt_out = {}    
        key_id = list(tm_key_set.names)
        
        for id_num in range(0,len(key_id)):
            globals()['key_list_{}'.format(id_num)] =[]
        value_list = []
        
        for index in varobject:
            for id_num in range(0,len(key_id)):
                globals()['key_list_{}'.format(id_num)].append(index[id_num])
                
            value_list.append(varobject[index].value)
        
        for id_num in range(0,len(key_id)):            
            opt_out[key_id[id_num]] = globals()['key_list_{}'.format(id_num)]
    
        opt_out['value'] = value_list
        
        globals()['opt_out_df_'+v] = pd.DataFrame(opt_out)
        globals()['opt_out_df_'+v].set_index(master_key, inplace=True)
        globals()['opt_out_df_'+v].sort_index(inplace=True)
    
print(globals()['opt_out_df_'+v])
