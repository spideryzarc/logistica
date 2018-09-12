import random as rd
import matplotlib.pyplot as plt
import numpy as np
rd.seed(7)

def createRandomInstance(n, max=100):
    return [(rd.random()*max,rd.random()*max) for i in range(n)]

def plot(pts, sol = None):
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

def randomSearch(sol,c, ite = 100000, pts = None):
    bestCost = custoSol(sol,c)
    bestSol = list(sol)
    for i in range(ite):
        rd.shuffle(sol)
        cost = custoSol(sol,c)
        if cost < bestCost:
            bestCost =cost
            bestSol = list(sol)
            print cost
            if pts != None:
                plot(pts,sol)
    return bestSol


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





pts = createRandomInstance(1000)
c = dist(pts)
bestCost = np.inf
bestSol = None
for i in range(len(pts)):
    sol = nearestNeighbor(c,i)
    custo = custoSol(sol,c)
    if(bestCost > custo):
        bestCost = custo
        bestSol = list(sol)
        print bestCost
plot(pts,bestSol)
print bestSol