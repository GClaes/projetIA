from AI.models import *
from game.business import *
import random
from random import randint
from functools import reduce
from AI.views import *
import time

up = [-1,0]
down = [1,0]
right = [0,1]
left=[0,-1]
tab_direction=[up,down,right,left]
global Epsilon
Epsilon= []
global States
States = []

def setup_training(ai1, ai2):
    Epsilon.append(ai1)
    Epsilon.append(ai2)

def get_limit():
    return len(States)

def get_data_from_training():
    return Epsilon, States

def clear_data():
    global States
    States = []
    Epsilon = []

def training_play (board, pos1, pos2, game_player, curr_player, ai):
    eps = ai.epsilon
    board_db = verify_board_training(board,pos1,pos2,ai)
    direction = move(eps,board_db.q_table,board_db.position)
    while not verify_direction(direction,board,pos1,curr_player):
        direction = move(eps,board_db.q_table,board_db.position)
    if game_player.previous_state_ai:
        update_q_table_training(board,board_db,pos1,pos2,ai,game_player,direction)
    direction_board = [tab_direction[direction],board_db]
    return direction_board

def epsilon_greedy_training(ai): 
    i_partie=ai.nb_games_training 
    E,i = find_epsilon(ai)
    if i_partie % ai.speed_learning == 0:
        E = (E /100) * 95
    if E < 5: 
        E = 5
    Epsilon[i].epsilon = E
    return E

def find_epsilon(ai):
    for ia in Epsilon:
        if ia.id == ai.id:
            return ia.epsilon, Epsilon.index(ia)
    return 0


def verify_board_training(searched_board,searched_position1,searched_position2,ai):
    board=str(searched_board)
    pos1=str(searched_position1)
    pos2=str(searched_position2)
    board_db,i = find_state(board, pos1, pos2, ai)
    if i == 0: #Stocké en interne
        States.append(State(board = board, position = pos1,position2 = pos2 ,q_table = "[0,0,0,0]",ai_id = ai))
        board_db = States[-1]
    elif i == -1: #Stocké en DB
        States.append(State(id = board_db.id, board = board, position = pos1,position2 = pos2 ,q_table = board_db.q_table,ai_id = ai))
    return board_db

def find_state(board, pos1, pos2, ai):
    for state in States:
        if state.ai_id == ai and state.board == board and state.position == pos1 and state.position2 == pos2:
            return state, States.index(state)
    try:
        state = State.manager.get(board = board, position = pos1,position2 = pos2,ai_id=ai)
        return state,-1
    except Exception as e:
        return 0,0

   

def update_q_table_training(board,board_db,pos1,pos2,ai,game_player,direction):
    old_q = string_to_list(game_player.previous_state_ai.q_table)
    q_table_list = string_to_list(board_db.q_table)
    max_q = max(q_table_list)
    recompense=calculate_reward(board,pos1,pos2,game_player)
    old_q[direction] = old_q[direction] + ai.learning_rate*(recompense+max_q-old_q[direction])
    state = game_player.previous_state_ai    
    s, i = find_state(state.board, state.position, state.position2, state.ai_id)
    States[i].q_table = old_q
