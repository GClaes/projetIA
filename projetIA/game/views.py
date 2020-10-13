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

    random_board = [[random.randint(0,2) for i in range(8)]for i in range(8)]
    random_pos1= [random.randint(0,7),random.randint(0,7)]
    random_pos2= [random.randint(0,7),random.randint(0,7)]


    game_state = {
        "game_id" : 11,
        "board" : random_board,
        "players" : [{
                "id" :  10,
                "name" : "Alice",
                "color" : "cyan",
                "position" : random_pos1

            },{
                "id" :  20,
                "name" : "Bob",
                "color" : "orange",
                "position" : random_pos2

            }],
        "current_player" : 1,
        "code" : 0
    }
    return JsonResponse(game_state)