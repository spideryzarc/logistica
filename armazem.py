import turtle as tt
import numpy as np
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
            tt.goto(x+w/2, y+h/2)
            tt.write(str(cont))
            lista.append(Baia(x, y, lin, col, 1, cont))
            cont += 1
            lin += 1
        col += 1
    tt.color('black')
    return lista


def manhatan(x1, y1, x2, y2):
    return abs(x1 - x2) +abs(y1 - y2)


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
        d = abs(a.y-y) + abs(b.y-y)
        if d < min:
            min = d
    return min+abs(a.x-b.x)




l = drawArmazem(400, 500)
print dist(l[8],l[78],[offSetY,offSetY+500])
input()
