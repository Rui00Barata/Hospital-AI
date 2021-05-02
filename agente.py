"""
agente.py

41308, Ruben Santos
41872, Rui Barata

"""
import time
import math
import networkx as nx
import numpy as np
import scipy.optimize as sp
# import matplotlib.pyplot as plt
import warnings as war

#-----------------------------VARÁVEIS GLOBAIS--------------------------------

vel = -1                # velocidade aproximada do robo 
velT = -1               # }
velX = -1               # } variaveis auxiliares da velocidade
velY = -1               # }
people = []             # lista de pessoas que foram vistas durante a execução do programa
objects = []            # lista de objetos que foram vistos durante a execução do programa
posicaoX = 0            # coordenada X do robo
posicaoY = 0            # coordenada Y do robo
bat = 0                 # bateria do robo
obj = []                # lista de objetos/pessoas que o robo esta perto

batDataX = []           # dados da percentagem de bateria
batDataY = []           # dados do tempo da bateria
Taux = -1               # }
batAux = -1             # } variaveis auxiliares da bateria


#-----------------------------GERAL--------------------------------

#funções
def check_distance(x1, y1, x2, y2): # funcao que calcula a distancia de dois pontos
    return math.sqrt(((x2-x1) ** 2) + ((y2-y1) ** 2))

def update_Lists(obj, x, y): #funcao que adiciona objetos e pessoas as listas certas

    l = obj.split("_")[0]

    switcher2 = {
        'doente': True,
        'medico': True,
        'enfermeiro': True,
        'cama': False,
        'livro': False,
        'cadeira': False,
        'mesa': False,
    }

    #remover objectos das listas se ja estiverem presentes para a memoria não dar overflow
    if switcher2[l]:
        try:
            people.remove(obj)
        except:
            pass
    else:
        try:
            objects.remove(obj)
        except:
            pass

    switcher1 = {
        'doente': people.insert,
        'medico': people.insert,
        'enfermeiro': people.insert,
        'cama': objects.insert,
        'livro': objects.insert,
        'cadeira': objects.insert,
        'mesa': objects.insert
    }

    switcher1[l](0,obj)
    r = check_room(x,y)

    if(rooms[r][l].count(obj) == 0):
        rooms[r][l].append(obj)

    if(not (switcher2[l])):
        update_room_type(r)

    if (l == 'medico'):
        addMedico(obj) 

#----------------------------GRAFOS-------------------------------
init_FLAG = True            # flag que permite inicializar grafo na primeira execucao
nodo_atual = "-1"           # representa o nodo em que o robo esat atualmente
roomGraph = nx.Graph()      # grafo 

# dicionarios
nodeBorders = { # bordas dos nodos
    "0": [(30,30), (245, 89)],
    "1_1": [(86,90), (245, 135)],
    "1_2": [(246,30), (395, 135)],
    "1_3": [(396,30), (564, 135)],
    "2_1": [(30,90), (85, 170)],
    "2_2": [(30,171), (85, 329)],
    "3_1": [(565,30), (635, 85)],
    "3_2": [(565,86), (635, 329)],
    "4_1": [(30,330), (85, 410)],
    "4_2": [(86,330), (245, 410)],
    "4_3": [(246,330), (395, 410)],
    "4_4": [(396,330), (580, 410)],
    "4_5": [(581,330), (770, 410)],
    "5": [(86,136), (245,329)],
    "6": [(246,136), (395,329)],
    "7": [(396,136), (564,329)],
    "8": [(636,30), (770,85)],
    "9": [(636,86), (770,185)],
    "10": [(636,186), (770,329)],
    "11": [(30,411), (245,570)],
    "12": [(246,411), (395,570)],
    "13": [(396,411), (580,570)],
    "14": [(581,411), (770,570)]
}

medicList = { # coordenadas dos medicos que estão em cada nodo
    "0": {},
    "1_1": {},
    "1_2": {},
    "1_3": {},
    "2_1": {},
    "2_2": {},
    "3_1": {},
    "3_2": {},
    "4_1": {},
    "4_2": {},
    "4_3": {},
    "4_4": {},
    "4_5": {},
    "5": {},
    "6": {},
    "7": {},
    "8": {},
    "9": {},
    "10": {},
    "11": {},
    "12": {},
    "13": {},
    "14": {},
}

#funções
def getNodeCenter(id): # calcula o centro de cada nodo usando o dicionario "nodeBorders"
    (x1, y1) = nodeBorders[id][0]
    (x2, y2) = nodeBorders[id][1]

    return (x1 + (x2 - x1)/2, y1 + (y2 - y1)/2)

def findActualNode(x, y):   # devolve o nodo que o robo esta atualmente
    for (index, ((x1,y1), (x2,y2))) in nodeBorders.items():
        if((x1 <= x <= x2) and (y1 <= y <= y2)):
            return index
    return -1

def initGraph():    # funcao que inicializa o grafo 
    global roomGraph
    global init_FLAG
    global nodo_atual
    
    init_FLAG = False

    for i in nodeBorders.keys(): # adiconar todos os nodos no dicionario
        roomGraph.add_node(i)   

    # adicionar edges entre os corredores (pois estas conexoes existem sempre)
    roomGraph.add_edge("0", "1_1", weight=59.9416)      #1
    roomGraph.add_edge("1_1", "0", weight=59.9416)
    roomGraph.add_edge("0", "1_2", weight=184.4397)     #2
    roomGraph.add_edge("1_2", "0", weight=184.4397)
    roomGraph.add_edge("1_1", "1_2", weight=157.8765)   #3
    roomGraph.add_edge("1_2", "1_1", weight=157.8765)
    roomGraph.add_edge("1_2", "1_3", weight=159.5)      #4 
    roomGraph.add_edge("1_3", "1_2", weight=159.5)
    roomGraph.add_edge("1_3", "3_1", weight=122.5765)   #5
    roomGraph.add_edge("3_1", "1_3", weight=122.5765)
    roomGraph.add_edge("3_1", "3_2", weight=150.0)      #6
    roomGraph.add_edge("3_2", "3_1", weight=150.0)
    roomGraph.add_edge("3_2", "4_5", weight=179.1829)   #7
    roomGraph.add_edge("4_5", "3_2", weight=179.1829)
    roomGraph.add_edge("4_5", "4_4", weight=187.5)      #8
    roomGraph.add_edge("4_4", "4_5", weight=187.5)
    roomGraph.add_edge("3_2", "4_4", weight=197.3582)   #9
    roomGraph.add_edge("4_4", "3_2", weight=197.3582)
    roomGraph.add_edge("4_3", "4_4", weight=167.5)      #10
    roomGraph.add_edge("4_4", "4_3", weight=167.5)
    roomGraph.add_edge("4_1", "4_2", weight=108.0)      #11
    roomGraph.add_edge("4_2", "4_1", weight=108.0)
    roomGraph.add_edge("4_2", "4_3", weight=155.0)      #12
    roomGraph.add_edge("4_3", "4_2", weight=155.0)
    roomGraph.add_edge("4_1", "2_2", weight=120.0)      #13
    roomGraph.add_edge("2_2", "4_1", weight=120.0)
    roomGraph.add_edge("2_1", "2_2", weight=120.0)      #14
    roomGraph.add_edge("2_2", "2_1", weight=120.0) 
    roomGraph.add_edge("2_1", "1_1", weight=109.4086)   #15
    roomGraph.add_edge("1_1", "2_1", weight=109.4086)

    #inicializar nodo atual
    nodo_atual = findActualNode(posicaoX, posicaoY)

def getPathCost(l):     # funcao que calcula o custo de um dado caminho
    
    aux = l.pop(0)


    if (len(l) > 0):
        (x2, y2) = getNodeCenter(l[0])
        sum = check_distance(posicaoX, posicaoY, x2, y2)
    else:
        sum = 0

    
    
    for i in range((len(l)-1)):
        sum += roomGraph[l[i]][l[i+1]]['weight']

    l.insert(0, aux)

    return sum

#----------------------------SALAS-------------------------------
# dicionarios
roomsBorders = {    # dicinario que tem as fronteiras de cada divisao/corredor
    0: [(30,30), (85,89)],
    1: [(86,30), (564,135)],
    2: [(30,90), (85,329)],
    3: [(565,30), (635,329)],
    4: [(30,330), (770,410)],
    5: [(86,136), (245,329)],
    6: [(246,136), (395,329)],
    7: [(396,136), (564,329)],
    8: [(636,30), (770,85)],
    9: [(636,86), (770,185)],
    10: [(636,186), (770,329)],
    11: [(30,411), (245,570)],
    12: [(246,411), (395,570)],
    13: [(396,411), (580,570)],
    14: [(581,411), (770,570)]
}

rooms = {   # dicionario que contem os objetos presentes em cada quarto e outras informacoes sobre cada sala
    1: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': 0},
    2: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': 0},
    3: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': 0},
    4: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': 0},
    5: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': (-1)},
    6: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': (-1)},
    7: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': (-1)},
    8: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': (-1)},
    9: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': (-1)},
    10: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': (-1)},
    11: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': (-1)},
    12: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': (-1)},
    13: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': (-1)},
    14: {'doente': [], 'medico': [], 'enfermeiro': [], 'cama': [], 'livro': [], 'cadeira': [], 'mesa': [], 'type': (-1)},
} # tipo de divisão: 0 -> corredor || 1 -> quarto || 2 -> sala de enfermeiros || 3 -> sala de espera || -1 -> unknown

# funcoes
def check_room(x, y):       # funcao que devolve a divisao/corredor em que estou
    for (index, ((x1,y1), (x2,y2))) in roomsBorders.items():
        if((x1 <= x <= x2) and (y1 <= y <= y2)):
            return index
    return -1

def update_room_type(r):    # atualiza o tipo da divisao, chamada sempre que encontro um objeto num quarto

    if (len(rooms[r]['cama']) != 0):                                            #quarto
        rooms[r]['type'] = 1
    elif ((len(rooms[r]['mesa']) != 0) and (len(rooms[r]['cadeira']) != 0)):    #sala de enfermeiros
        rooms[r]['type'] = 2
    elif (len(rooms[r]['cadeira']) > 2):                                        #sala de espera
        rooms[r]['type'] = 3

def getRoomCenter(id):      # funcao que devolve o centro de uma divisao/corredor
    (x1, y1) = roomsBorders[id][0]
    (x2, y2) = roomsBorders[id][1]

    return ((x2 - x1)/2, (y2 - y1)/2)

#----------------------------ONE-TIME-USE-------------------------------
def printPath(l): # resp3() - imprime no ecra o caminho dado

    for i in range(len(l)):
        aux = l.pop(0)
        aux = aux.split('_')[0]
        l.append(aux)

    l = list(dict.fromkeys(l))
    for i in range(len(l)-1):
        print(l[i] ,end=" -> ")

    print(l[len(l)-1])

def addMedico(obj): # resp4() - adciona um medico ao nodo atual

    n = findActualNode(posicaoX, posicaoY)

    aux = (posicaoX, posicaoY)

    medicList[n][obj] = aux

def bat_estimation(bat, time): # resp6() - calcula o tempo que falta de bateria
    return (((100-bat) * time) / bat)

def expo(x, a, b): # função que estima o gasto da bateria
    return np.exp(a + b * x)
#--------------------------------MAIN-----------------------------------
def work(posicao, bateria, objetos):
    global vel
    global velT
    global velX
    global velY
    global batAux
    global Taux
    global nodo_atual
    global posicaoX
    global posicaoY
    global bat
    global obj    

    war.filterwarnings("ignore")

    posicaoX = posicao[0]
    posicaoY = posicao[1]
    bat = bateria
    obj = objetos
    # posicao = a posição atual do agente, uma lista [X,Y]
    # bateria = valor de energia na bateria, um número inteiro >= 0
    # objetos = o nome do(s) objeto(s) próximos do agente, uma string
    # podem achar o tempo atual usando, p.ex.
    # time.time()

    if (init_FLAG == True): # so entra a primeira vez que a funcao loop e executada
        initGraph()
    
    aux = findActualNode(posicaoX, posicaoY)


    if(aux != nodo_atual): # cria edges entre os corredores e divisoes
        l = list(roomGraph.edges())
        if(l.count((nodo_atual, aux)) == 0 and l.count((aux, nodo_atual)) == 0):

            (x1, y1) = getNodeCenter(nodo_atual)
            (x2, y2) = getNodeCenter(aux)

            roomGraph.add_edge(nodo_atual, aux, weight=check_distance(x1, y1, x2, y2))
            roomGraph.add_edge(aux, nodo_atual, weight=check_distance(x1, y1, x2, y2))
    
    nodo_atual = aux    # atualiza nodo atual


    
    for i in objetos: # trata de todos os objetos que ve no momento
        update_Lists(i, posicaoX, posicaoY)


    if (vel == -1): # mede a velocidade
        if(velX == -1):
            velX = posicaoX
            velY = posicaoY

        if (velX == posicaoX and velY == posicaoY):
            velT = time.time()
        else:
            vel = 5/(time.time()-velT)


    if (batAux == -1 or bat == 100):
        batAux = bat
        Taux = time.time()

    if (batAux > int(bat)):

        if (batAux <= 99):
            batDataX.append(batAux)
            batDataY.append(float("{:.3f}".format(time.time()-Taux)))

        batAux = int(bat)
    
def resp1():
    if len(people) < 2: # quando ainda so viu 1 ou 0 pessoas
        print("Ainda não vi mais do que uma pessoa")
    else:
        print(people[1])

def resp2():

    r = check_room(posicaoX,posicaoY)

    # ve em que tipo de divisao esta
    if (0<=r<=4):                                                               #corredor
        print("Esta divisão é um corredor")
    elif (len(rooms[r]['cama']) != 0):                                          #quarto
        print("Esta divisão é um quarto")
    elif ((len(rooms[r]['mesa']) != 0) and (len(rooms[r]['cadeira']) != 0)):    #sala de enfermeiros
        print("Esta divisão é uma sala de enfermeiros")
    elif (len(rooms[r]['cadeira']) > 2):                                        #sala de espera
        print("Esta divisão é uma sala de espera")
    else:
        print("Ainda não tenho informação suficiente")              

def resp3():

    if(rooms[check_room(posicaoX, posicaoY)]['type'] == 2): # ve se a sala atual ja e uma sala de enfermeiros
        print("Já me encontro numa sala de enfermeiros")
    else:
        
        minDistance = 100000
        minRoom = -1
        path = []

        n_atual = findActualNode(posicaoX, posicaoY)

        for (r, dic) in rooms.items(): # vai comparar todos os caminhos para todas as salas de enfermeiros e escolhe o mais pequeno
            if (dic['type'] == 2):
                l = nx.shortest_path(roomGraph, n_atual, str(r), "weight")
                aux = getPathCost(l)
                
                if (minDistance > aux):
                    minDistance = aux
                    minRoom = r
                    path = l


        if (minRoom == -1): # se nao encontrar nenhum caminho e porque ainda nao conhece nenhuma sala de enfermeiros
            print("Ainda não encontrei nenhuma sala de enfermeiros")
        else:   # se encontrar imprime o melhor
            printPath(path)

def resp4():
    
    minDistance = 100000
    minRoom = -1
    path = []

    n_atual = findActualNode(posicaoX, posicaoY)

    for (r, med) in medicList.items():  # encontra caminho para o nodo mais proximo com medicos presentes
        if (len(med) > 0):

            path = nx.shortest_path(roomGraph, n_atual, r, "weight")
            aux = getPathCost(path)
            
            if (minDistance > aux):
                    minDistance = aux
                    minRoom = r

    minDis = 100000

    if(minRoom == -1):
        print("Ainda nao encontrei nenhum medico")
        return

    for (x2, y2) in medicList[minRoom].values():    # encontra o medico mais proximo nesse nodo

        if (n_atual == minRoom):    # se for no mesmo nodo em que o robo esta entao ve a distancia de todos os medicos presentes no nodo ate ao robo e escolhe o mais proximo

            aux = check_distance(posicaoX, posicaoY, x2, y2)

            if (minDis > aux):
                minDis = aux

        else:   # ve a distancia desde o penultimo nodo do caminho ate ao medico mais proximo desse nodo
            
            path.reverse()
            
            (cx, cy) = getNodeCenter(path[1])
            (minRoomx, minRoomy) = getNodeCenter(path[0])

            aux = check_distance(cx, cy, x2, y2) - check_distance(cx, cy, minRoomx, minRoomy)

            if (minDis > aux):
                minDis = aux
         
    minDistance += minDis

    print(minDistance)

def resp5(): 
    
    # calcula uma aproximacao do tempo que demora usando o custo do caminho calculado a dividir pela a aproximacao da velocidade do robo

    if (vel == -1):
        print("Ainda nao tenho informacao suficiente para responder")
        return

    n_atual = findActualNode(posicaoX, posicaoY)

    l = nx.shortest_path(roomGraph, n_atual, "0", "weight")

    t = getPathCost(l) / vel

    print("Devo chegar as escadas em {:.2f}s".format(t)) 

def resp6():

    try:
        (a, b),_ = sp.curve_fit(expo, batDataX, batDataY)
        print("{:.2f}s".format((expo(0, a, b) - expo(bat, a, b))))
    except:
        print("Ainda nao tenho informacao suficiente para responder")
    
    """ x = np.linspace(-1, 100, 202)
    y = expo(x, a, b)
    plt.plot(batDataX, batDataY, "r.")
    plt.plot(x, y, "b-")
    plt.xlabel("Percentagem de bateria")
    plt.ylabel("Tempo que demorou a ser gasta")
    plt.show() """
    
def resp7():

    # calcula a probabilidade condicionada de encontrar um livro sabendo que encontrou uma cadeira

    #C: probabilidade de encontrar cadeira
    cfC = 0
    #P(L ^ C)
    cfLC = 0

    for (r, obj) in rooms.items():
        if(r>4):
            if (len(obj['cadeira']) > 0 and len(obj['livro']) > 0):
                cfLC += 1
            if (len(obj['cadeira']) > 0):
                cfC += 1

    if (cfC != 0):
        print("{:d}%".format(int((cfLC / cfC)*100)))
    else:
        print("{:d}%".format(cfC))

def resp8():
    
    
    # calcula a probabilidade condicionada de encontrar um doente sabendo que encontrou um enfermeiro

    #C: probabilidade de encontrar cadeira
    cfE = 0
    #P(L ^ C)
    cfDE = 0

    for (r, obj) in rooms.items():
        if(r>4):
            if (len(obj['doente']) > 0 and len(obj['enfermeiro']) > 0):
                cfDE += 1
            if (len(obj['enfermeiro']) > 0):
                cfE += 1

    if (cfE != 0):
        print("{:d}%".format(int((cfDE / cfE)*100)))
    else:
        print("{:d}%".format(cfE))
