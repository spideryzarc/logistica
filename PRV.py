import random as rd
import matplotlib.pyplot as plt
import numpy as np
from utils import *
import pyomo.environ as env
from PCV import custoSol, VND


rd.seed(123)

def createRandomInstance(n, max=100, cap = 100):
    return [(rd.random()*max,rd.random()*max,rd.randint(1,cap)) for i in range(n)]

def createPyomoModel(pts,cap):
    #preparacao dos dados
    C = dist(pts)
    Cdic = matrixToDic(C)
    demTotal = sum(pts[i][2] for i in range(1, len(pts)))
    dem = [pts[j][2] for j in range(len(pts))]

    model = env.ConcreteModel()
    model.pts = pts
    model.name = 'PCV'
    #criacao dos conjuntos
    model.V = env.Set(initialize=range(len(pts)),doc='conjunto dos vertices')
    model.Vs0= env.Set(initialize=range(1,len(pts)), doc='conjunto dos vertices sem a origem')
    model.x = env.Var(model.V,model.V,within=env.Binary,doc='se o arco (i,j) eh usado ou nao')
    model.c = env.Param(model.V,model.V,initialize=Cdic,doc='custo do arco (i,j)')
    #funcao objetvo
    model.objective = env.Objective(rule=lambda model: sum(model.x[i,j]*model.c[i,j]
                                                           for i in model.V for j in model.V if i!=j)
                                     ,sense=env.minimize)

    #restricoes de designacao / assingment
    model.leaving = env.Constraint(model.Vs0,
                                   rule=lambda model,i:sum(model.x[i,j] for j in model.V if i!=j) ==1)
    model.incoming = env.Constraint(model.Vs0,
                                    rule=lambda model, j: sum(model.x[i,j] for i in model.V if i != j) == 1)

    #remocao dos subcirclos e limitacao da capacidade
    model.y = env.Var(model.V, model.V, within=env.NonNegativeIntegers, doc='qtd. de comodities trans. de (i,j)')
    model.c1 = env.Constraint(expr=sum(model.y[0,i] for i in model.V) == demTotal, doc='todal da demanda de comodities saindo da origem')
    model.c2 = env.Constraint(expr=sum(model.y[i,0] for i in model.V) == 0, doc='zero comodite volta para a origem')
    model.c3 = env.Constraint(model.V,model.V,rule=lambda model,i,j:model.y[i,j]<=demTotal*model.x[i,j])
    model.c4 = env.Constraint(model.Vs0,
                              rule=lambda model,j:sum(model.y[i,j] for i in model.V if (i!=j))
                                                  - sum(model.y[j,i] for i in model.V if (i!=j))
                                                  == dem[j],
                              doc='cada cliente absorve sua demanda de comodite')
    model.c5 = env.Constraint(model.V, rule=lambda model, i: model.y[0, i] <= cap,
                              doc='cada rota nao pode fornecer mais do que a capacidade')
    return model

def plotModel(model):
    pts = model.pts
    x = [p[0] for p in pts]
    y = [p[1] for p in pts]
    plt.close()
    plt.plot(x, y, 'ro')
    for i in range(len(pts)):
        for j in range(len(pts)):
            if model.x[i,j].value >= 1:
                plt.plot([x[i],x[j]], [y[i],y[j]], '-')
                if(i!= 0):
                    plt.annotate(model.pts[i][2], xy=(x[i], y[i]), xycoords='data')
    plt.show()


### heuristica
def custo(rotas,md):
    c = 0
    for r in rotas:
        c+= custoSol(r,md)
    return c

def randomPart(pts,cap):
    load = []
    rotas = []
    idx = [i for i in range(1,len(pts))]
    rd.shuffle(idx)
    rotaCont = 0
    for i in idx:
        if len(load) == 0 or load[rotaCont-1]+pts[i][2] > cap:
            load.append(pts[i][2])
            rotas.append([0,i])
            rotaCont+=1
        else:
            load[rotaCont-1]+=pts[i][2]
            rotas[rotaCont-1].append(i)
    # print load, rotas

    return load,rotas

def plotSol(pts, rotas = None):
    plt.close()
    for sol in rotas:
        x = [p[0] for p in pts]
        y = [p[1] for p in pts]
        plt.plot(x,y,'ro')
        if sol != None:
            x = [pts[p][0] for p in sol]
            y = [pts[p][1] for p in sol]
            x.append(pts[sol[0]][0])
            y.append(pts[sol[0]][1])
            plt.plot(x, y, '-')
    plt.show()

def melhoraRota(rotas,md):
    for r in rotas:
        VND(r,md)

cap = 100
pts = createRandomInstance(20,cap=15)


# model = createPyomoModel(pts,cap)
# solveWithGLPK(model)
# print 'solucao otima ', model.objective()
# plotModel(model)

md = dist(pts)
bestcost = np.inf
best = None
for i in range(1000):
    load,rotas = randomPart(pts,cap)
    melhoraRota(rotas,md)
    c = custo(rotas, md)
    if c < bestcost:
        bestcost = c
        best = rotas
        print c

plotSol(pts,best)


