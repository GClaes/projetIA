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
from AI.views import play_ai,epsilon_greedy

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
            u1.nb_games+=1
            u1.save()
            u2 = User.manager.get(username = username2)
            u2.nb_games+=1
            u2.save()
            colors = build_colors([u1,u2])
            game_player1 = get_game_player(username1,game_state_data, [0,0],colors[0])
            game_player2 = get_game_player(username2,game_state_data, [7,7],colors[1])
            game_players = [game_player1, game_player2]

            for player in game_players:
                if is_current_player_ai(player):
                    player.user.ai_id.epsilon = epsilon_greedy(player.user)
                    player.user.ai_id.save()

            indice=0
            game_state = build_game_state(game_state_data, [game_player1, game_player2], game_player1.auto_increment_id,0)

            #2 IA jouent ensemble  
            while is_current_player_ai(game_players[indice]) and not end_of_game(game_state_data.board):
                movement = play(board, game_players,indice)
                game_state_data = move_pos(game_players[indice], movement, game_state_data, game_players)
                current_player = change_player(game_players, indice)
                game_state_data.current_player = current_player
                save_data(game_state_data)
                for game_player in game_players:
                    save_data(game_player)
                game_state = build_game_state(game_state_data, [game_player1, game_player2], game_player2.auto_increment_id,0)
                indice = index_player(current_player, game_players)
                if end_of_game(game_state_data.board):
                    game_state = build_game_state(game_state_data, game_players, current_player, 0)
                    winner_id, nb_cell_winner, tie = define_winner(game_state.get("board"))
                    game_players[winner_id-1].user.nb_games_wins+=1
                    game_players[winner_id-1].user.save()
                    data_winner = {"name": game_players[winner_id-1].user.username, "nb_cell": nb_cell_winner, "tie":tie}
                    game_state["winner"] =  data_winner
                    if(game_state.get("winner").get("tie")):
                        text = "Egalité avec "+str(game_state.get("winner").get("nb_cell"))
                    else:
                        text = "Resultat: "+game_state.get("winner").get("name")+" avec "+str(game_state.get("winner").get("nb_cell"))
                    return HttpResponse(text)
            return render(request, 'game/new_game.html', game_state)
        return HttpResponse("KO")

def apply_move(request) :
    rcontent = json.loads(request.body.decode())
    p_player = rcontent.get("player_id")
    game_id = rcontent.get("game_id")
    game_state_data = get_gamestate_data(game_id)
    game_state_data.board = string_to_list(game_state_data.board)
    game_players = get_all_player_from_gamestate(game_state_data)
    game_players = listing_game_players(game_players)
    indice = index_player(int(p_player), game_players)
    curr_player = p_player 
    try:
        movement = rcontent.get("move")
        game_state_data = move_pos(game_players[indice], movement, game_state_data, game_players)
        game_state = build_game_state(game_state_data, game_players, curr_player, 0)
    except OufOfBoardError as e:
        game_state = build_game_state(game_state_data, game_players, curr_player, 1)
    except NotEmptyCellError as e:
        game_state = build_game_state(game_state_data, game_players, curr_player, 2)
    else:
        if end_of_game(game_state_data.board):
            winner_id, nb_cell_winner, tie = define_winner(game_state.get("board"))
            game_players[winner_id-1].user.nb_games_wins+=1
            game_players[winner_id-1].user.save()
            game_state = print_winner(game_state, game_players[winner_id-1])
            return JsonResponse(game_state)
        else:
            curr_player = change_player(game_players, indice)
            game_state = build_game_state(game_state_data, game_players, curr_player, 0)

    game_state_data.current_player = game_state.get("current_player")
    save_game_turn(game_state_data, game_players)
    
    #Verifier si c'est au tour d'une IA de jouer
    indice = index_player(int(curr_player), game_players)
    if is_current_player_ai(game_players[indice]):
        game_state = ai_play(curr_player, game_players, game_state_data, indice)
        if end_of_game(game_state["board"]):
            winner_id, nb_cell_winner, tie = define_winner(game_state.get("board"))
            game_players[winner_id-1].user.nb_games_wins+=1
            game_players[winner_id-1].user.save()
            game_state = print_winner(game_state, game_players[winner_id-1])
    return JsonResponse(game_state)

def ai_play(curr_player, game_players, game_state_data, indice):
    movement = play(game_state_data.board, game_players,indice)
    game_state_data = move_pos(game_players[indice], movement, game_state_data, game_players)
    curr_player = change_player(game_players, indice)
    game_state_data.current_player = curr_player
    save_game_turn(game_state_data, game_players)
    return build_game_state(game_state_data, game_players, curr_player,0)

def play(board, game_players, indice):
    if indice == 1:
        i_o = 0
    else:
        i_o = 1
    user = User.manager.get(username=game_players[indice].user.username)
    direction_board =play_ai(board,game_players[indice].pos,game_players[i_o].pos,user,game_players[indice],indice)
    movement = direction_board[0]
    save_data(game_players[indice])
    return movement 