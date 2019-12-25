import numpy as np
from psopy import _minimize_pso
from psopy import init_feasible, gen_confunc


fun = lambda x: (x[0] - 1)**2 + (x[1] - 2.5)**2
fun_ = lambda x: np.apply_along_axis(fun, 1, x)

cons = ({'type': 'ineq', 'fun': lambda x:  x[0] - 2 * x[1] + 2},
        {'type': 'ineq', 'fun': lambda x: -x[0] - 2 * x[1] + 6},
        {'type': 'ineq', 'fun': lambda x: -x[0] + 2 * x[1] + 2},
        {'type': 'ineq', 'fun': lambda x: x[0]},
        {'type': 'ineq', 'fun': lambda x: x[1]})

x0 = init_feasible(cons, low=0., high=2., shape=(1000, 2))
confunc = gen_confunc(cons)

options={'g_rate': 1., 'l_rate': 1., 'max_velocity': 4., 'stable_iter': 50}
res = _minimize_pso(fun_, x0, confunc=confunc, **options)

print(res.x)