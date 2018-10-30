from utils import *
import pyomo.environ as env
import random as rd
import matplotlib.pyplot as plt
import numpy as np
from transporte import createPyomoModel as transModel
rd.seed(7)

def creatRandomInst(nClients, nFacilidades, capMin=20, capMax=60,demMin=5, demMax=15):
    cli_x = [rd.randint(0,1000) for i in range(nClients)]
    cli_y = [rd.randint(0, 1000) for i in range(nClients)]
    cli_d = [rd.randint(demMin, demMax) for i in range(nClients)]
    fac_x = [rd.randint(0, 1000) for i in range(nFacilidades)]
    fac_y = [rd.randint(0, 1000) for i in range(nFacilidades)]
    fac_c = [rd.randint(capMin, capMax) for i in range(nFacilidades)]
    fac_f = [rd.randint(1, demMax*1000/nFacilidades) for i in range(nFacilidades)]
    return cli_x,cli_y,cli_d,fac_x,fac_y,fac_c,fac_f


def plotPLF(cli_x,cli_y,fac_x,fac_y, model = None):
    plt.close()
    plt.plot(cli_x,cli_y,'ro')
    plt.plot(fac_x,fac_y, 'bx')
    if(model != None):
        n = len(cli_x)
        m = len(fac_x)

        for j in range(m):
            x = []
            y = []
            for i in range(n):
                if(model.x[j,i].value>.0001):
                    # print j,i
                    x.append(fac_x[j])
                    x.append(cli_x[i])
                    x.append(fac_x[j])
                    y.append(fac_y[j])
                    y.append(cli_y[i])
                    y.append(fac_y[j])
            plt.plot(x, y, '-')

    plt.show()

def plotPLFSol(cli_x,cli_y,fac_x,fac_y, sol):
    plt.close()
    plt.plot(cli_x,cli_y,'ro')
    plt.plot(fac_x,fac_y, 'bx')

    n = len(cli_x)
    m = len(fac_x)

    for j in range(m):
        x = []
        y = []
        for i in range(n):
            if(sol[j][i]>.0001):
                # print j,i
                x.append(fac_x[j])
                x.append(cli_x[i])
                x.append(fac_x[j])
                y.append(fac_y[j])
                y.append(cli_y[i])
                y.append(fac_y[j])
        plt.plot(x, y, '-')

    plt.show()

def matrizDist(cli_x,cli_y,fac_x,fac_y):
    n = len(cli_x)
    m = len(fac_x)
    md = np.zeros([m,n])
    for i in range(n):
        for j in range(m):
            md[j][i] = np.sqrt((cli_x[i]-fac_x[j])**2 + (cli_y[i]-fac_y[j])**2)
    return md


def createPyomoModel(cli_d,fac_c,fac_f,md):
    #numero de facilidades
    N = len(fac_c)
    #numero de clientes
    M = len(cli_d)

    capDic = vectorToDic(fac_c)
    demDic = vectorToDic(cli_d)
    costDic = matrixToDic(md)

    model = env.ConcreteModel()

    #conjuntos
    model.I = env.Set(initialize=capDic.keys(),doc='Conjunto de facilidades')
    model.J = env.Set(initialize=demDic.keys(), doc='Conjunto de consumidores')
    #dados
    model.a = env.Param(model.I,initialize=capDic,doc='Capacidade de cada facilidades')
    model.b = env.Param(model.J, initialize=demDic, doc='Demanda de cada consumidor')
    model.C = env.Param(model.I,model.J,initialize=costDic,doc='Custo de transporte unitario')
    #variaveis
    model.x = env.Var(model.I,model.J,bounds=(0,None),doc='quantidade transportada de i a j')
    model.z = env.Var(model.I,within=env.Binary, doc='se facilidade i sera aberta ou nao')
    #funcao objetivo
    model.objective = env.Objective(rule=lambda model: sum(model.x[i,j]*model.C[i,j] for i in model.I for j in model.J)
                                                       +sum(model.z[i]*fac_f[i] for i in model.I),sense=env.minimize)
    #restricoes

    #capacidade
    model.cap = env.Constraint(model.I,rule=lambda model,i: sum(model.x[i,j] for j in model.J) <= model.a[i]*model.z[i])

    # demanda
    model.dem = env.Constraint(model.J, rule=lambda model, j: sum(model.x[i, j] for i in model.I) == model.b[j])

    return model


#heuristica
def custo(sol,cli_d, fac_f,md):
    c = 0;
    for i in range(len(fac_f)):
        for j in range(len(cli_d)):
            c+= md[i][j]*cli_d[j]

    for i in range(len(fac_f)):
        if sum(sol[i]) >.0001:
            c+= fac_f[i]
    return c


def greedySol(cli_d,fac_c,fac_f,md):
    sol = np.zeros((len(fac_c),len(cli_d)))
    idxFac = [i for i in range(len(fac_c))]
    rd.shuffle(idxFac)
    dtotal = sum(cli_d)
    openFac = []
    cap = 0
    i = 0
    while cap < dtotal and i < len(idxFac):
        openFac.append(idxFac[i])
        cap+= fac_c[idxFac[i]]
        i+=1
    if cap < dtotal:
        print 'instancia nao viavel'
        exit(1)
    openFac_c = [fac_c[i] for i in openFac]
    openMD = md[openFac]
    model = transModel(openFac_c, cli_d, openMD)
    result = solveWithGLPK(model)
    for i in range(len(openFac)):
        for j in range(len(cli_d)):
            sol[openFac[i]][j] = model.x[i,j].value

    return sol


cli_x,cli_y,cli_d,fac_x,fac_y,fac_c,fac_f = creatRandomInst(100,50,capMin=200, capMax=250)
# plotPLF(cli_x,cli_y,fac_x,fac_y)
md = matrizDist(cli_x,cli_y,fac_x,fac_y)

min = np.inf
for i in range(100):
    sol = greedySol(cli_d,fac_c,fac_f,md)
    d =  custo(sol,cli_d,fac_f,md)
    if d < min:
        min = d
        print min

# plotPLFSol(cli_x,cli_y,fac_x,fac_y,sol)
# model = createPyomoModel(cli_d,fac_c,fac_f,md)
# result = solveWithGLPK(model)
# model.display()
# plotPLF(cli_x,cli_y,fac_x,fac_y,model)