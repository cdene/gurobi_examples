# Facility location: a company currently ships its product from 5 plants
# to 4 warehouses. It is considering closing some plants to reduce
# costs. What plant(s) should the company close, in order to minimize
# transportation and fixed costs?

# Based on an example from Gurobi https://www.gurobi.com/documentation/9.0/examples/facility_py.html
# see original example http://www.solver.com/disfacility.htm

import os

import gurobipy as gp
import pandas as pd
from gurobipy import GRB

dir_path = os.path.dirname(os.path.realpath(__file__))

# read data from csv
plants_data = pd.read_csv(f"{dir_path}/plants.csv", index_col=0)
warehouses_data = pd.read_csv(f"{dir_path}/warehouses.csv", index_col=0)
transCosts_data = pd.read_csv(f"{dir_path}/transportation_costs.csv", index_col=0)

# Warehouse demand in thousands of units
warehouses = warehouses_data.index.values
demand = warehouses_data['demand']

plants = plants_data.index.values
# Plant capacity in thousands of units
capacity = plants_data['capacity']
# Fixed costs for each plant
fixedCosts = plants_data['cost']

transCosts = transCosts_data.values

# Model
m = gp.Model("facility")

# Plant open decision variables: open[p] == 1 if plant p is open.
open = m.addVars(plants,
                 vtype=GRB.BINARY,
                 obj=fixedCosts,
                 name="open")

# Transportation decision variables: transport[w,p] captures the
# optimal quantity to transport to warehouse w from plant p
transport = m.addVars(warehouses, plants, obj=transCosts, name="trans")

# The objective is to minimize the total fixed and variable costs
m.modelSense = GRB.MINIMIZE

# Production constraints
# Note that the right-hand limit sets the production to zero if the plant
# is closed
m.addConstrs((transport.sum('*', p) <= capacity[p] * open[p] for p in plants), "Capacity")

# Demand constraints
m.addConstrs((transport.sum(w) == demand[w] for w in warehouses), "Demand")

# Save model
m.write('facilityPY.lp')

# Guess at the starting point: close the plant with the highest fixed costs;
# open all others

# First open all plants
for p in plants:
    open[p].start = 1.0

# Now close the plant with the highest fixed cost
print('Initial guess:')
maxFixed = max(fixedCosts)
for p in plants:
    if fixedCosts[p] == maxFixed:
        open[p].start = 0.0
        print('Closing plant %s' % p)
        break
print('')

# Use barrier to solve root relaxation
m.Params.method = 2

# Solve
m.optimize()

# Print solution
print('\nTOTAL COSTS: %g' % m.objVal)
print('SOLUTION:')
for p in plants:
    if open[p].x > 0.99:
        print('Plant %s open' % p)
        for w in warehouses:
            if transport[w, p].x > 0:
                print('  Transport %g units to warehouse %s' %
                      (transport[w, p].x, w))
    else:
        print('Plant %s closed!' % p)
