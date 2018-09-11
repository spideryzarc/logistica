from utils import *
import pyomo.environ as env
def createPyomoModel(capacity,demand,cost):
    N = len(capacity)
    M = len(demand)

    capDic = vectorToDic(capacity)
    demDic = vectorToDic(demand)
    costDic = matrixToDic(cost)

    model = env.ConcreteModel()

    #conjuntos
    model.I = env.Set(initialize=capDic.keys(),doc='Conjunto de fornecedores')
    model.J = env.Set(initialize=demDic.keys(), doc='Conjunto de consumidores')
    #dados
    model.a = env.Param(model.I,initialize=capDic,doc='Capacidade de cada fornecedor')
    model.b = env.Param(model.J, initialize=demDic, doc='Demanda de cada fornecedor')
    model.C = env.Param(model.I,model.J,initialize=costDic,doc='Custo de transporte unitario')
    #variaveis
    model.x = env.Var(model.I,model.J,bounds=(0,None),doc='quantidade transportada de i a j')
    #funcao objetivo
    model.objective = env.Objective(rule=lambda model: sum(model.x[i,j]*model.C[i,j] for i in model.I for j in model.J),sense=env.minimize)
    #restricoes

    #capacidade
    model.cap = env.Constraint(model.I,rule=lambda model,i: sum(model.x[i,j] for j in model.J) <= model.a[i])

    # demanda
    model.dem = env.Constraint(model.J, rule=lambda model, j: sum(model.x[i, j] for i in model.I) == model.b[j])


    return model



model = createPyomoModel([1,1],[1,1],[[21,22],[23,24]])
result = solveWithGurobi(model)
model.display()
print result