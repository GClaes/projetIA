from django.shortcuts import render
from game import *
from AI.models import *
from game.models import *
from game.business import *
import random
from random import randint

# Create your views here.
def play_ai(board,pos1,pos2,ai,game_player,curr_player):
    up = [-1,0]
    down = [1,0]
    right = [0,1]
    left=[0,-1]
    tab_direction=[up,down,right,left]

    eps = epsilon_greedy(1,ai)
    board_db = verify_board(board,pos1,pos2,ai)
    direction = move(eps,board_db.q_table,board_db.position)
    while not verify_direction(direction,board,pos1,curr_player):
        direction = move(eps,board_db.q_table,board_db.position)
    if game_player.preview_state_ai is not None:
        update_q_table(board,board_db,pos1,pos2,ai,game_player,direction)
    direction_board = [tab_direction[direction],board_db]
    
    return direction_board

def epsilon_greedy(rapidite,ai): 
    E=ai.epsilon
    i_partie=ai.nb_games
    if i_partie % rapidite == 0:
        E = (E /100) * 95
    if E < 5: return 5
    ai.epsilon=E
    ai.save()
    return E

def move(eps,q_table,position):
    #attention aux murs (et a la mousse)
    #ajouter un 'convertisseur' pour la direction (0,1,2,3 = haut,bas,gauche,droite)
    q_table=string_to_list(q_table)
    
    r=random.randint(0, 100)
    print("r=",r)
    print("epsilon= ",eps)
    print("q_table=",q_table)
    print("qtable is null=",qtable_is_null(q_table))
    
    if qtable_is_null(q_table) == 0 or r < eps:
        direction = randint(0, 3)
        print("random")    
    else:
        direction = q_table.index(max(q_table))
        print("qtble= ",q_table)
        print("exploitation")
    return direction

def qtable_is_null(q_table):
    sum = 0
    for i in q_table:
        sum+=i
    return sum

def verify_direction(direction,board,pos1,curr_player):
    
    pos=pos1
    up = [-1,0]
    down = [1,0]
    right = [0,1]
    left=[0,-1]
    tab_direction=[up,down,right,left]

    move = tab_direction[direction]
    x=pos[0]+move[0]
    y=pos[1]+move[1]
    
   
    if x < 0 or x > 3 or y < 0 or y > 3: #virer hardcoding
        return False
    else:
        if board[x][y] ==curr_player+1 or board[x][y] == 0:
            return True
        else:
            return False

def verify_board(searched_board,searched_position1,searched_position2,ai):
    board=str(searched_board)
    pos1=str(searched_position1)
    pos2=str(searched_position2)
    try:
        board_db = State.manager.get(board = board, position = pos1,position2 = pos2,ai_id=ai.id)
        print("state= " ,board_db)
    except Exception as e:
        board_db = register_board(searched_board,searched_position1,searched_position2,ai)
    return board_db
#ICI
def register_board(board,position,position2,ai):
    state = State(board = board, position = position,position2 = position2 ,q_table = "[0,0,0,0]",ai_id = ai)
    state.save()
    return state

def update_q_table(board,board_db,pos1,pos2,ai,game_player,direction):
    #board_db = verify_board(board,pos1,ai)
    old_q = string_to_list(game_player.preview_state_ai.q_table)
    q_table_list = string_to_list(board_db.q_table)
    max_q = max(q_table_list)
    #a refaire
    recompense=calculate_reward(board,pos1,pos2,game_player)

    #directionp1 = move(0,board_db.q_table,board_db.position)
    #modif en fct de (fct dans business)
    #print(type(max_q))
    #print(type(old_q))
    print('recompense= ',recompense)
    old_q[direction] = old_q[direction] + 0.9*(recompense+max_q-old_q[direction])
    state=game_player.preview_state_ai
    print("old_q",old_q)
    state.q_table=old_q
    state.save()
    game_player.preview_state_ai.q_table=old_q
    game_player.save()
    
    #mettre le state actuel dans le gameplayer
    #game_player.preview_state_ai = ai.
    board_db.save()
    ai.save()

def count_boxes(board,num_player):
    nb_cases = 0
    for line in board:
        for cell in line:
            if cell == num_player:
                nb_cases +=1
    
    return nb_cases

def best_reward_and_position(pos,preview_board,num_player,old_pos):
    
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
        #print(preview_board)
        #print(pos)
        complete_boxes(preview_board,num_player,old_pos)
        preview_points = count_boxes(preview_board,num_player)
        new_points = count_boxes(preview_board,num_player)
        reward = new_points - preview_points
        if reward > best_points:
            best_points = reward
            best_position = pos

    return best_points,best_position

def calculate_reward(board,ai_position,opp_position,gameplayer): 
    preview_state = gameplayer.preview_state_ai
    pos_ai = string_to_list( preview_state.position)
    pos = opp_position
    preview_board = string_to_list(preview_state.board)
    preview_opp_pos = string_to_list(preview_state.position2)
    num_opp = board[pos[0]][pos[1]]
    num_player = board[ai_position[0]][ai_position[1]]
    
    best_points_opp,best_position_opp = best_reward_and_position(pos,preview_board,num_opp,preview_opp_pos)
    best_points_ai,best_position_ai = best_reward_and_position(ai_position,preview_board,num_player,pos_ai)

    
    if ai_position == best_position_opp:
        if best_points_opp > best_points_ai:
            return best_points_opp
        else:
            return 1
    else:
        return count_cells(preview_board,board,num_player)


def count_cells(old_board, new_board, num_player):
    old_nb_boxes = count_boxes(old_board,num_player)
    new_nb_boxes = count_boxes(new_board,num_player)

    return new_nb_boxes - old_nb_boxes
    
    
    


'''def best_direction(num_player,direction,position,board)
    
    nb_cell_max = 0
    nb_old_cell = 0
    for line in board:
            for cell in line:
                if cell == num_player:
                    nb_old_cell+=1

    for dir in direction:
        nb_cell = 0
        new_board = board
        new_pos = [position[0]+dir[0],position[1]+dir[1]]
        complete_boxes(new_board,num_player,new_pos)
        for line in new_board:
            for cell in line:
                if cell == num_player:
                    nb_cell+=1
        if nb_cell >= nb_cell_max:
            nb_cell_max = nb_cell
            best_dir = dir
        
    return nb_cell_max-nb_old_cell,best_dir'''