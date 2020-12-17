from django.shortcuts import render
from game import *
from AI.models import *
from game.models import *
from game.business import *
import random
from random import randint
from functools import reduce


def play_ai(board,pos1,pos2,user,game_player,curr_player):
    ai = AI.manager.get(id = user.ai_id.id)
    up = [-1,0]
    down = [1,0]
    right = [0,1]
    left=[0,-1]
    tab_direction=[up,down,right,left]

    eps = epsilon_greedy(ai,user)
    board_db = verify_board(board,pos1,pos2,ai)
    direction = move(eps,board_db.q_table,board_db.position)
    while not verify_direction(direction,board,pos1,curr_player):
        direction = move(eps,board_db.q_table,board_db.position)
    if game_player.previous_state_ai:
        update_q_table(board,board_db,pos1,pos2,user.ai_id,game_player,direction)
    direction_board = [tab_direction[direction],board_db]
    return direction_board

def epsilon_greedy(ai,user): 
    print(ai.epsilon)
    E=ai.epsilon
    i_partie=user.nb_games
    if i_partie % ai.speed_learning == 0:
        E = (E /100) * 95
    if E < 5: return 5
    ai.epsilon=E
    ai.save()
    return E

def move(eps,q_table,position):
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
    up = [-1,0]
    down = [1,0]
    right = [0,1]
    left=[0,-1]
    tab_direction=[up,down,right,left]
    x=pos[0]+tab_direction[direction][0]
    y=pos[1]+tab_direction[direction][1]
   
    if x < 0 or x > 3 or y < 0 or y > 3: 
        return False
    else:
        return board[x][y] ==curr_player+1 or board[x][y] == 0

def verify_board(searched_board,searched_position1,searched_position2,ai):
    board=str(searched_board)
    pos1=str(searched_position1)
    pos2=str(searched_position2)

    try:
        board_db = State.manager.get(board = board, position = pos1,position2 = pos2,ai_id=ai)
        print("state connu = " ,board_db.board)

    except Exception as e:
        board_db = register_board(board,pos1,pos2,ai)
        print("-")
    return board_db

def register_board(board,position,position2,ai):
    state = State(board = board, position = position,position2 = position2 ,q_table = "[0,0,0,0]",ai_id = ai)
    state.save()
    return state

def update_q_table(board,board_db,pos1,pos2,ai,game_player,direction):
    old_q = string_to_list(game_player.previous_state_ai.q_table)
    q_table_list = string_to_list(board_db.q_table)
    max_q = max(q_table_list)
    recompense=calculate_reward(board,pos1,pos2,game_player)
    old_q[direction] = old_q[direction] + ai.learning_rate*(recompense+max_q-old_q[direction])
    state=game_player.previous_state_ai
    state.q_table=old_q
    state.save()
    game_player.previous_state_ai.q_table=old_q
    game_player.save()
    board_db.save()
    ai.save()

def count_boxes(board,num_player):
    return reduce(lambda x,y: x+y, board).count(num_player)

def best_reward_and_position(pos,previous_board,num_player,old_pos):
    
    up = [-1,0]
    down = [1,0]
    right = [0,1]
    left=[0,-1]
    tab_direction=[up,down,right,left]
    
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
    
    