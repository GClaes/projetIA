from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from django import forms
import random
from game.models import Game_Player, Game_State
from connection.models import User
import ast
 

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
            game_state1 = Game_State(current_player=1, board=board)
            game_state1.save()

            username1 = form.cleaned_data.get("player1")
            username2 = form.cleaned_data.get("player2")
            u1 = User.manager.get(username = username1)
            u2 = User.manager.get(username = username2)
            game_player1 = Game_Player(user=u1, game_state=game_state1, pos=[0,0])
            game_player1.save()
            game_player2 = Game_Player(user=u2, game_state=game_state1, pos=[7,7])
            game_player2.save()


            game_state = {
                "game_id" : game_state1.auto_increment_id,
                "board" : game_state1.board,
                "players" : [{
                        "id" :  game_player1.auto_increment_id,
                        "name" : game_player1.user.username,
                        "color" : "cyan",
                        "position" : game_player1.pos
                    },{
                        "id" :  game_player2.auto_increment_id,
                        "name" : game_player2.user.username,
                        "color" : "orange",
                        "position" : game_player2.pos
                    }],
                "current_player" : 0,
                "code" : 0,
            }

            return render(request, 'game/new_game.html', game_state)

        return HttpResponse("KO")

def apply_move(request) :
    rcontent = json.loads(request.body.decode())
    movement = rcontent.get("move")
    p_player = rcontent.get("player_id")
    game_id = rcontent.get("game_id")

    #Recupérer le game_state en DB
    game_state_data = Game_State.manager.get(auto_increment_id=game_id)
    game_state_data.board = ast.literal_eval(game_state_data.board)
    game_players = Game_Player.manager.all().filter(game_state = game_state_data)
    game_player1 = game_players[0]
    print(game_player1.auto_increment_id)
    print(game_player1.pos)
    game_player1.pos = ast.literal_eval(game_player1.pos)
    game_player2 = game_players[1]
 


    game_state = {
        "game_id" : game_state_data.auto_increment_id,
        "board" : game_state_data.board,
        "players" : [{
                "id" :  game_player1.auto_increment_id,
                "name" : game_player1.user.username,
                "color" : game_player1.user.color1,
                "position" : game_player1.pos

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
    game_player1.pos = pos

    board = game_state.get("board")
    players = game_state.get("players")
    board = update_board_content(board, player1, players.index(player1))
    game_state["board"]=board

    #Sauver le game_state en DB
    game_state_data.save()
    game_player1.save()


    return JsonResponse(game_state)







    #Changer Current_player
    """
    for player in game_players:
        if player.auto_increment_id == p_player:
            curr_player = game_players.index(player)
    """


    
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