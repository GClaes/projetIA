from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json

from django import forms
import random
 

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
            game_state = {
                "game_id" : 11,
                "board" : [[1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,2]],
                "players" : [{
                        "id" :  10,
                        "name" : form.cleaned_data.get("player1"),
                        "color" : "cyan",
                        "position" : [2,2]
                    },{
                        "id" :  20,
                        "name" : form.cleaned_data.get("player2"),
                        "color" : "orange",
                        "position" : [4,5]
                    }],
                "current_player" : 1,
                "code" : 0
            }
            return render(request, 'game/new_game.html', game_state)

        return HttpResponse("KO")

def apply_move(request) :
    rcontent = json.loads(request.body.decode())
    movement = rcontent.get("move")
    p_player = rcontent.get("player_id")

    #Recupérer le game_state en DB

    #Game_state doit être supp pour utiliser la DB
    game_state = {
        "game_id" : 11,
        "board" : [[1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,2]],
        "players" : [{
                "id" :  10,
                "name" : "Alice",
                "color" : "cyan",
                "position" : [0,0]

            },{
                "id" :  20,
                "name" : "Bob",
                "color" : "orange",
                "position" : [7,7]

            }],
        "current_player" : 1,
        "code" : 0, 
    }


    #Le code sera à modifier pour le rendre plus fonctionnel paradigment parlant
    #+Encore données brutes
    player1 = game_state.get("players")[0]
    pos_player1 = player1.get("position")
    pos = calculate_position(pos_player1, movement)
    game_state["players"][0]["position"] = pos

    board = game_state.get("board")
    players = game_state.get("players")
    board = update_board_content(board, player1, players.index(player1))
    game_state["board"]=board

    #Sauver le game_state en DB

    return JsonResponse(game_state)

#Rendre plus fonctionnel
def calculate_position(player_pos, movement):
    position =  [player_pos[0]+movement[0], player_pos[1]+movement[1]]
    for pos in position:
        if pos < 0 or pos > 7:
            #Raise error
            return player_pos

    return position

def update_board_content(board, player, index):
    position = player.get("position")
    board[position[0]][position[1]] = index+1
    return board