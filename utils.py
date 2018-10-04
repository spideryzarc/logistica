import numpy as np

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

def dist(pts):
    mat = np.zeros((len(pts),len(pts)))
    for i in range(len(pts)):
        xi = pts[i][0]
        yi = pts[i][1]
        for j in range(i):
            xj = pts[j][0]
            yj = pts[j][1]
            mat[i][j] = mat[j][i] = np.sqrt((xi-xj)**2+(yi-yj)**2)
    return mat