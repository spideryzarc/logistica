import random as rd
import matplotlib.pyplot as plt
import numpy as np
from utils import *
import pyomo.environ as env

rd.seed(123)

def createRandomInstance(n, max=100):
    return [(rd.random()*max,rd.random()*max) for i in range(n)]

def plotSol(pts, sol = None):
    x = [p[0] for p in pts]
    y = [p[1] for p in pts]
    plt.close()
    plt.plot(x,y,'ro')
    if sol != None:
        x = [pts[p][0] for p in sol]
        y = [pts[p][1] for p in sol]
        x.append(pts[sol[0]][0])
        y.append(pts[sol[0]][1])
        plt.plot(x, y, '-')
    plt.show()

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

def custoSol(sol,c):
    s = 0
    for i in range(1,len(sol)):
        s+= c[sol[i-1]][sol[i]]
    s+= c[sol[len(sol)-1]][sol[0]]
    return s




def createPyomoModel(pts):
    C = dist(pts)
    Cdic = matrixToDic(C)
    model = env.ConcreteModel()
    model.pts = pts
    model.name = 'PCV'
    model.V = env.Set(initialize=range(len(pts)),doc='conjunto dos vertices')
    model.Vs0= env.Set(initialize=range(1,len(pts)), doc='conjunto dos vertices sem a origem')
    model.x = env.Var(model.V,model.V,within=env.Binary,doc='se o arco (i,j) eh usado ou nao')
    model.c = env.Param(model.V,model.V,initialize=Cdic,doc='custo do arco (i,j)')

    model.objective = env.Objective(rule=lambda model: sum(model.x[i,j]*model.c[i,j]
                                                           for i in model.V for j in model.V if i!=j)
                                     ,sense=env.minimize)

    model.leaving = env.Constraint(model.Vs0,
                                   rule=lambda model,i:sum(model.x[i,j] for j in model.V if i!=j) ==1)
    model.incoming = env.Constraint(model.Vs0,
                                    rule=lambda model, j: sum(model.x[i,j] for i in model.V if i != j) == 1)

    #remocao dos subcirclos
    model.y = env.Var(model.V, model.V, within=env.NonNegativeIntegers, doc='qtd. de comodities trans. de (i,j)')
    N = len(pts)
    model.c1 = env.Constraint(expr=sum(model.y[0,i] for i in model.V) == N, doc='N comodities saindo da origem')
    model.c2 = env.Constraint(expr=sum(model.y[i,0] for i in model.V) == 1, doc='1 comodite volta para a origem')
    model.c3 = env.Constraint(model.V,model.V,rule=lambda model,i,j:model.y[i,j]<=N*model.x[i,j])

    model.c4 = env.Constraint(model.Vs0,
                              rule=lambda model,j:sum(model.y[i,j] for i in model.V if (i!=j))
                                                  - sum(model.y[j,i] for i in model.V if (i!=j)) == 1 )
    #model.c5 = env.Constraint(model.V, rule=lambda model, i: model.y[0, i] <= 3)
    return model


# def plot(model):
#     pts = model.pts
#     x = [p[0] for p in pts]
#     y = [p[1] for p in pts]
#     plt.close()
#     plt.plot(x, y, 'ro')
#     for i in range(len(pts)):
#         for j in range(len(pts)):
#             if model.x[i,j].value >= 1:
#                 plt.plot([x[i],x[j]], [y[i],y[j]], '-')
#     plt.show()

def getSol(model):
    solveWithGLPK(model)
    sol = [0]
    while len(sol) < len(model.pts):
        for i in range(1,len(model.pts)):
            if model.x[sol[-1],i] == 1:
                sol.append(i)
                break
    return sol

#HEURISTICAS

#testa ite permutacoes aleatorias e retorna a de menor custo
def randomSearch(sol,c, ite = 10000, pts = None):
    bestCost = custoSol(sol,c)
    bestSol = list(sol)
    for i in range(ite):
        rd.shuffle(sol)
        cost = custoSol(sol,c)
        if cost < bestCost:
            bestCost =cost
            bestSol = list(sol)
            # print cost
            if pts != None:
                plotSol(pts,sol)
    return bestSol

#
def nearestNeighbor(c, first = 0):
    sol = [first]
    nv = [i for i in range(len(c)) if i != first]
    nvsize = len(nv)
    for i in range(1,len(c)):
        min = np.inf
        arg = -1
        pivot = sol[i-1]
        for j in range(nvsize):
            if min > c[pivot][nv[j]]:
                min = c[pivot][nv[j]]
                arg = j
        sol.append(nv[arg])
        nv[arg] = nv[nvsize-1]
        nvsize-=1
    return sol

def shiftRight(sol, c,pts):
    for i in range(1,len(sol)-1):
        remDelta = c[sol[i-1]][sol[i+1]]\
                   -c[sol[i-1]][sol[i]]\
                   -c[sol[i]][sol[i+1]]
        for j in range(i+2,len(sol)-1):
                addDelta = c[sol[j]][sol[i]]\
                           +c[sol[i]][sol[j+1]]\
                           -c[sol[j]][sol[j+1]]
                if remDelta+addDelta < -.001:
                    # print 'shift',i,j, remDelta+addDelta
                    # print custoSol(sol,c)+remDelta+addDelta,sol
                    # plotSol(pts,sol)
                    tmp = sol[i]
                    for k in range(i,j):
                        sol[k] = sol[k+1]
                    sol[j] =tmp
                    # print custoSol(sol, c), sol
                    # plotSol(pts, sol)
                    return True
    return False
# model = createPyomoModel(createRandomInstance(10))
# sol = getSol(model)
# # plotSol(model.pts,sol)
# print model.objective.expr()


pts = createRandomInstance(100)
sol = [i for i in range(len(pts))]
c = dist(pts)
sol = randomSearch(sol,c)
print 'tentativas aleatorias ', custoSol(sol,c)
# plotSol(pts,sol)
while shiftRight(sol, c,pts):
    pass
print 'tentativas aleatorias + melhoramentos ', custoSol(sol,c)

sol = nearestNeighbor(c)
print 'vizinho mais proximo ',custoSol(sol,c)
plotSol(pts,sol)
while shiftRight(sol, c,pts):
    pass
print 'vizinho mais proximo + melhoramentos ', custoSol(sol,c)

