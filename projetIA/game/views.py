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
 

class NewGameForm(forms.Form):
    player1 = forms.CharField(label="Player 1")
    player2 = forms.CharField(label="Player 2")


def index(request):
    if request.method == "GET":
        form = NewGameForm(auto_id='id_for_%s')
        return render(request, "game/index.html", { "form": form })

    if request.method == "POST": 
        form = NewGameForm(request.POST)
        if form.is_valid():
            board = [[1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,2]]
            game_state_data = Game_State(current_player=1, board=board)
            game_state_data.save()

            username1 = form.cleaned_data.get("player1")
            username2 = form.cleaned_data.get("player2")
            u1 = User.manager.get(username = username1)
            u2 = User.manager.get(username = username2)
            game_player1 = Game_Player(user=u1, game_state=game_state_data, pos=[0,0])
            game_player1.save()
            game_player2 = Game_Player(user=u2, game_state=game_state_data, pos=[7,7])
            game_player2.save()

            
            game_state = build_game_state(game_state_data, [game_player1, game_player2])

            return render(request, 'game/new_game.html', game_state)

        return HttpResponse("KO")

def apply_move(request) :
    rcontent = json.loads(request.body.decode())
    movement = rcontent.get("move")
    p_player = rcontent.get("player_id")
    game_id = rcontent.get("game_id")

    #Recupérer le game_state en DB
    game_state_data = get_gamestate_data(game_id)
    game_state_data.board = string_to_list(game_state_data.board)
    game_players = get_all_player_from_gamestate(game_state_data)
    game_players = listing_game_players(game_players)

    #Changer
    game_player1 = game_players[0]
    game_player2 = game_players[1]
    #
    
    game_state_data = move_pos(game_player1, movement, game_state_data, game_players)
    game_state = build_game_state(game_state_data, game_players)



    #Persister les données
    save_data(game_state_data)
    save_data(game_player1)


    return JsonResponse(game_state)