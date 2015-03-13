from pulp import *
prob = LpProblem('lptest', LpMaximize)

x = LpVariable('x', lowBound = 0)
y = LpVariable('y', lowBound = 0)
z = LpVariable('z', lowBound = 0)

w = [LpVariable('w%d' % i, lowBound=0) for i in range(3)]

prob += w[0]+w[1]+w[2] == 1
prob += w[0]*3+w[1]*2+w[2]*0.5 <= 2

prob.writeLP("problem.lp")

print prob

GLPK().solve(prob)
# status = prob.solve(GLPK(msg = 0))

for v in prob.variables():
    print v.name, '=', v.varValue

# print 'objective =', value(prob.objective)
