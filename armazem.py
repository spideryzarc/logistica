import turtle as tt
import numpy as np
import random as rd
from PCV import nearestNeighbor, VND, custoSol

offSetX = -200
offSetY = -200


class Baia:
    def __init__(self, x, y, lin, col, lado, id):
        self.x = x
        self.y = y
        self.lin = lin
        self.col = col
        self.lado = lado
        self.id = id

    def __repr__(self):
        return '(%d %d %d)' % (self.lin, self.col, self.lado)


def drawRec(x, y, w, h):
    tt.penup()
    tt.goto(x, y)
    tt.pendown()
    tt.goto(x + w, y)
    tt.goto(x + w, y + h)
    tt.goto(x, y + h)
    tt.goto(x, y)
    tt.penup()


def drawArmazem(W, H, cor=30, w=20, h=30):
    drawRec(offSetX, offSetY, W, H)
    tt.speed(0)
    tt.color('blue')
    lista = []
    col = 0

    cont = 0
    for x in range(offSetX + cor, W + offSetX - cor - w, 2 * w + cor):
        lin = 0
        for y in range(offSetY + cor, H + offSetY - cor - h, h):
            drawRec(x, y, w, h)
            tt.goto(x + w / 2, y + h / 2)
            tt.write(str(cont))
            lista.append(Baia(x, y, lin, col, 0, cont))

            cont += 1
            lin += 1
        col += 1

    col = 0
    for x in range(offSetX + cor + w, W + offSetX - cor - w, 2 * w + cor):
        lin = 0
        for y in range(offSetY + cor, H + offSetY - cor - h, h):
            drawRec(x, y, w, h)
            tt.goto(x + w / 2, y + h / 2)
            tt.write(str(cont))
            lista.append(Baia(x, y, lin, col, 1, cont))
            cont += 1
            lin += 1
        col += 1
    tt.color('black')
    return lista


def manhatan(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


def dist(a, b, cory):
    if a.col == b.col and a.lado == b.lado:
        return abs(a.y - b.y)
    if a.lado != b.lado and abs(a.col - b.col) == 1:
        if a.col < b.col and a.lado == 1:
            return manhatan(a.x, a.y, b.x, b.y)
        if a.col > b.col and a.lado == 0:
            return manhatan(a.x, a.y, b.x, b.y)
    min = np.inf
    for y in cory:
        d = abs(a.y - y) + abs(b.y - y)
        if d < min:
            min = d
    return min + abs(a.x - b.x)


def custo(pedidos, W, local):
    centroX = W / 2 + offSetX
    custo = 0;
    for p in pedidos:
        n = len(p) + 1
        mat = np.zeros((n, n))

        for i in range(1, n):
            mat[0][i] = mat[i][0] = abs(local[p[i - 1]].x - centroX) + abs(local[p[i - 1]].y - offSetY)
        for i in range(len(p)):
            for j in range(i):
                mat[i + 1][j + 1] = mat[j + 1][i + 1] = dist(local[p[i]], local[p[j]], cory)
        sol = nearestNeighbor(mat)
        VND(sol, mat)
        custo += custoSol(sol, mat)
    return custo


def drawLocal(pedidos, local, W, H, w=20, h=30):
    tt.clear()
    tt.color('black')
    drawRec(offSetX, offSetY, W, H)

    tt.color('red')
    list = []
    for p in pedidos:
        for prod in p:
            if prod not in list:
                drawRec(local[prod].x, local[prod].y, w, h)
                tt.write(str(prod))
                list.append(prod)


W = 600
H = 400
l = drawArmazem(W, H)
cory = [offSetY, offSetY + H]
prods = range(len(l))
pedidos = []
for i in range(10):
    pedidos.append(rd.sample(prods, rd.randint(2, 20)))

min = np.inf
for i in range(1000):
    rd.shuffle(prods)
    localRandom = {i: l[prods[i]] for i in range(len(prods))}

    d = custo(pedidos, W, localRandom)
    if (d < min):
        min = d;
        print min;
        # drawLocal(pedidos, localRandom, W, H)
