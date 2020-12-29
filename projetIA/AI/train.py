from AI.models import *
from game.business import *
import random
from random import randint
from functools import reduce

global up
up = [-1,0]
global down
down = [1,0]
global right
right = [0,1]
global left
left=[0,-1]
global tab_direction
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
    States = []
    Epsilon = []

def training_play (board, pos1, pos2, game_player, curr_player, ai):
    #eps = epsilon_greedy(ai)
    eps = ai.epsilon
    board_db = verify_board(board,pos1,pos2,ai)
    direction = move(eps,board_db.q_table,board_db.position)
    while not verify_direction(direction,board,pos1,curr_player):
        direction = move(eps,board_db.q_table,board_db.position)
    if game_player.previous_state_ai:
        update_q_table(board,board_db,pos1,pos2,ai,game_player,direction)
    direction_board = [tab_direction[direction],board_db]
    return direction_board

def epsilon_greedy(ai): 
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


def verify_board(searched_board,searched_position1,searched_position2,ai):
    board=str(searched_board)
    pos1=str(searched_position1)
    pos2=str(searched_position2)
    board_db, i = find_state(board, pos1, pos2, ai)
    if board_db == 0:
        States.append(State(board = board, position = pos1,position2 = pos2 ,q_table = "[0,0,0,0]",ai_id = ai))
        board_db = States[-1]
    return board_db

def find_state(board, pos1, pos2, ai):
    for state in States:
        if state.ai_id == ai and state.board == board and state.position == pos1 and state.position2 == pos2:
            return state, States.index(state)
    return 0,0

def move(eps,q_table,position):
    a = "abc"
    if type(q_table)== type(a):
        q_table=string_to_list(q_table)
    r=random.randint(0, 100)
    
    if qtable_count_value(q_table) == 0 or r < eps:
        direction = randint(0, 3)
    else:
        direction = q_table.index(max(q_table))
    return direction

def qtable_count_value(q_table):
    return reduce(lambda x,y: x+y, q_table)


def verify_direction(direction,board,pos,curr_player):
    x=pos[0]+tab_direction[direction][0]
    y=pos[1]+tab_direction[direction][1]
   
    if x < 0 or x > 7 or y < 0 or y > 7: 
        return False
    else:
        return board[x][y] ==curr_player+1 or board[x][y] == 0


def update_q_table(board,board_db,pos1,pos2,ai,game_player,direction):
    a="abc"
    if type(game_player.previous_state_ai.q_table)== type(a):
        old_q = string_to_list(game_player.previous_state_ai.q_table)
    else:
        old_q = game_player.previous_state_ai.q_table
    if type(board_db.q_table)== type(a):
        q_table_list = string_to_list(board_db.q_table)
    else:
        q_table_list = board_db.q_table
    max_q = max(q_table_list)
    recompense=calculate_reward(board,pos1,pos2,game_player)
    old_q[direction] = old_q[direction] + ai.learning_rate*(recompense+max_q-old_q[direction])
    state = game_player.previous_state_ai    
    s, i = find_state(state.board, state.position, state.position2, state.ai_id)
    States[i].q_table = old_q


def calculate_reward(board,ai_position,opp_position,gameplayer): 
    previous_state = gameplayer.previous_state_ai
    try:
        pos_ai = string_to_list( previous_state.position)
    except Exception as e:
        pos_ai =previous_state.position
    pos = opp_position
    try:
        previous_board = string_to_list(previous_state.board)
    except Exception as e:
        previous_board = previous_state.board

    try:
        previous_opp_pos = string_to_list(previous_state.position2)
    except Exception as e:
        previous_opp_pos = previous_state.position2
    num_opp = board[pos[0]][pos[1]]
    num_player = board[ai_position[0]][ai_position[1]]
    
    best_points_opp,best_position_opp = best_reward_and_position(pos,previous_board,num_opp,previous_opp_pos)
    best_points_ai,best_position_ai = best_reward_and_position(ai_position,previous_board,num_player,pos_ai)

    
    if ai_position == best_position_opp:
        if best_points_opp > best_points_ai:
            return best_points_opp
        else:
            return 1
    else:
        return count_cells(previous_board,board,num_player)

def count_cells(old_board, new_board, num_player):
    old_nb_boxes = count_boxes(old_board,num_player)
    new_nb_boxes = count_boxes(new_board,num_player)

    return new_nb_boxes - old_nb_boxes


def best_reward_and_position(pos,previous_board,num_player,old_pos):    
    best_points = 0
    best_position = [pos[0]+tab_direction[0][0],pos[1]+tab_direction[0][1]]

    for i in tab_direction:
        pos[0]+=i[0]
        pos[1]+=i[1]
        complete_boxes(previous_board,num_player,old_pos)
        previous_points = count_boxes(previous_board,num_player)
        new_points = count_boxes(previous_board,num_player)
        reward = new_points - previous_points
        if reward > best_points:
            best_points = reward
            best_position = pos

    return best_points,best_position

def count_boxes(board,num_player):
    return reduce(lambda x,y: x+y, board).count(num_player)
