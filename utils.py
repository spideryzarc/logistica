def vectorToDic(v):
    return {i:v[i] for i in range(len(v))}

def matrixToDic(m):
    return {(i,j):m[i][j] for i in range(len(m)) for j in range(len(m[i]))}

def solveWithGurobi(model):
    from pyomo.environ import SolverFactory
    opt = SolverFactory("gurobi")
    results = opt.solve(model)
    return results


def solveWithGLPK(model):
    from pyomo.environ import SolverFactory
    opt = SolverFactory("glpk")
    results = opt.solve(model)
    return results
