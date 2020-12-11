from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from django import forms
import random
from game.models import Game_Player, Game_State
from connection.models import User
import ast
from game.business import *
from game.services import *
from game.exceptions import *
from AI.models import AI
from AI.views import play_ai

 

class NewGameForm(forms.Form):
    player1 = forms.CharField(label="Player 1")
    is_ai1 = forms.BooleanField(label="Is player 1 an AI", required=False)
    player2 = forms.CharField(label="Player 2")
    is_ai2 = forms.BooleanField(label="Is player 2 an AI", required=False)


def index(request):
    if request.method == "GET":
        form = NewGameForm(auto_id='id_for_%s')
        return render(request, "game/index.html", { "form": form })

    if request.method == "POST": 
        form = NewGameForm(request.POST)
        if form.is_valid():
            #[[1,0,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,1],[1,1,1,1,1,1,1,2]]
            #[[1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,2]]
            #[[1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,2]]
            board = [[1,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,2]]
            game_state_data = Game_State(current_player=1, board=board)
            game_state_data.save()

            username1 = form.cleaned_data.get("player1")
            username2 = form.cleaned_data.get("player2")
            
            u1 = User.manager.get(username = username1)
            u2 = User.manager.get(username = username2)
            colors = build_colors([u1,u2])
            
            game_player1 = get_game_player(username1, form.cleaned_data.get("is_ai1"), game_state_data, [0,0],colors[0])
            game_player2 = get_game_player(username2, form.cleaned_data.get("is_ai2"), game_state_data, [3,3],colors[1])


            game_state = build_game_state(game_state_data, [game_player1, game_player2], game_player1.auto_increment_id,0)  

            if form.cleaned_data.get("is_ai1"):
                game_state["AI_1"]= 1
            if form.cleaned_data.get("is_ai2"):
                game_state["AI_2"]= 1
            
            return render(request, 'game/new_game.html', game_state)

        return HttpResponse("KO")


def get_game_player(username, is_ai, game_state_data, pos,col):
    u = User.manager.get(username = username)
    game_player = Game_Player(user=u, game_state=game_state_data, pos=pos , color = col)
    if is_ai:
        game_player.is_ai = True
    else:
        game_player.is_ai = False
    game_player.save()

    return game_player


def apply_move(request) :

    rcontent = json.loads(request.body.decode())
    #movement = rcontent.get("move")
    p_player = rcontent.get("player_id")
    game_id = rcontent.get("game_id")


    #Recupérer le game_state en DB
    game_state_data = get_gamestate_data(game_id)
    game_state_data.board = string_to_list(game_state_data.board)
    game_players = get_all_player_from_gamestate(game_state_data)
    game_players = listing_game_players(game_players)

   
    
    
    #Construire le game_state
    indice = index_player(int(p_player), game_players)
    curr_player = p_player
   
    try:
        if game_players[indice].is_ai:
            if indice == 1:
                indice_oppo = 0
            else:
                indice_oppo = 1
            ai = AI.manager.get(username=game_players[indice].user.username)
            direction_board = play_ai(game_state_data.board,game_players[indice].pos,game_players[indice_oppo].pos,ai,game_players[indice],indice)
            movement = direction_board[0]
            print(movement)
        else:
            
            movement = rcontent.get("move")
            

    
        #COndition is_ai
        
        game_state_data = move_pos(game_players[indice], movement, game_state_data, game_players)
    except OufOfBoardError as e:
        game_state = build_game_state(game_state_data, game_players, curr_player, 1)
    except NotEmptyCellError as e:
        game_state = build_game_state(game_state_data, game_players, curr_player, 2)
    else:
        if end_of_game(game_state_data.board):
            game_state = build_game_state(game_state_data, game_players, curr_player, 0)
            winner_id, nb_cell_winner, tie = define_winner(game_state.get("board"))

            data_winner = {"name": game_players[winner_id-1].user.username, "nb_cell": nb_cell_winner, "tie":tie}
            game_state["winner"] =  data_winner
        else:
            curr_player = change_player(game_players, p_player)
            game_state = build_game_state(game_state_data, game_players, curr_player, 0)

    game_state_data.current_player = game_state.get("current_player")

    #Persister les données
    if game_players[indice].is_ai:
        game_players[indice].preview_state_ai = direction_board[1]
    save_data(game_state_data)
    for game_player in game_players:
        save_data(game_player)


    return JsonResponse(game_state)