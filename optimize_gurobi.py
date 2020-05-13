import sys
import gurobipy as gp
from gurobipy import GRB

# if len(sys.argv) < 2:
#     print('Usage: lp.py filename')
#     quit()

# Read and solve model

model = gp.read('ifrum.lp')
model.optimize()

if model.status == GRB.INF_OR_UNBD:
    # Turn presolve off to determine whether model is infeasible
    # or unbounded
    model.setParam(GRB.Param.Presolve, 0)
    model.optimize()

if model.status == GRB.OPTIMAL:
    print('Optimal objective: %g' % model.objVal)
    model.write('model.sol')
    sys.exit(0)
elif model.status != GRB.INFEASIBLE:
    print('Optimization was stopped with status %d' % model.status)
    sys.exit(0)


# Model is infeasible - compute an Irreducible Inconsistent Subsystem (IIS)

print('')
print('Model is infeasible')
model.computeIIS()
model.write("model.ilp")
print("IIS written to file 'model.ilp'")