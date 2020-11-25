from django.shortcuts import render
from game import *
from State.models import State
from AI.models import AI
import random
from random import randint

# Create your views here.
def play_ai(board,pos,ai):
    #recherche/creation du board
    board_db = verify_board(board,pos,ai)
    #calcul epsilon
    eps = epsilon_greedy(10,ai)
    #deplacement(renvoie le deplacement dans Game)
    return move(eps,board_db.q_table,board_db.position)


def epsilon_greedy(rapidite,ai): 
    ai=AI.manager.get(id=ai)
    E=ai.epsilon
    i_partie=ai.nb_games
    if i_partie % rapidite == 0:
        E = (E /100) * 95
    if E < 5: return 5
    ai.epsilon=E
    ai.save()
    return E

'''def eps_calc():
    E = 99
    nb_exploit = 0
    nb_explor = 0

    for i in range(100):
        E = epsilon_greedy(E, i, 2)
        x = random.randint(0, 100)
        if x > E:
            nb_exploit += 1
        else:
            nb_explor += 1
        if i %100==0:
            print(E)
            
    print("Exploitation: ",nb_exploit)
    print("Exploration: ",nb_explor)
    return E'''
    

def move(eps,q_table,position):
    #attention aux murs (et a la mousse)
    #ajouter un 'convertisseur' pour la direction (0,1,2,3 = haut,bas,gauche,droite)
    if random.uniform(0, 1) < eps:
        direction = randint(0, 3)
    else:
        direction = q_table.index(max(q_table))
    
    return direction

def verify_board(searched_board,searched_position,ai):

    board_db = State.manager.get(board = searched_board, position = searched_position,ai_id=ai)
    if board_db == None:
        board_db = register_board(searched_board,searched_position,ai)
    return board_db

def register_board(board,position,ai):
    grid_point = transform_board(board)
    state = State(board = board, position = position,q_table = [0,0,0,0], grid_point_db = grid_point,ai_id = ai)
    state.save()
    return state
def save_move(searched_board, searched_position,direction,ai):
    board_db = verify_board(searched_board,searched_position,ai)
    recompense=board_db.grid_point_db[searched_position[0]][searched_position[1]]
    directionp1 = move(0,board_db.q_table,board_db.position)
    board_db.q_table[direction] = board_db.q_table[direction] + 0.1*(recompense + 0.9*board_db.q_table[directionp1]- board_db.q_table[direction])
    board_db.save()
    ai=AI.manager.get(id=ai)
    ai.nb_games+=1
    ai.save()

def transform_board(board):
    #pourquoi le board est en charfield dans la db ??
    grid_point = board
    for line in grid_point:
        for elem in line:
            if elem == 0:
                elem = 1
            elif elem == 2:
                elem = -1
            else:
                elem = 9

    return grid_point