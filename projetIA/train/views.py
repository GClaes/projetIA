from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from django import forms
from connection.models import User, User_data
from game.models import Game_Player, Game_State
from game.business import *
from game.services import *
from game.exceptions import *
from AI.models import AI
from AI.views import play_ai



class NewGameForm(forms.Form):
    ia1 = forms.CharField(label="IA 1")
    ia2 = forms.CharField(label="IA 2")
    nb_games = forms.IntegerField(label="Number of games")

    def clean(self):
        cd = self.cleaned_data

        c_ia1 = cd.get("ia1")
        c_ia2 = cd.get("ia2")
        c_nb_games = cd.get("nb_games")


        try:
            ia1 = User.manager.get(username = c_ia1)
        except User.DoesNotExist:
            raise forms.ValidationError("IA1 doesn't exist")

        try:
            ia2 = User.manager.get(username = c_ia2)
        except User.DoesNotExist:
            raise forms.ValidationError("IA2 doesn't exist")

        if c_nb_games < 1:
            raise forms.ValidationError("The number of games must be more than 0")

        return cd


def index(request):
    if request.method == "GET":
        form = NewGameForm(auto_id='id_for_%s')
        return render(request, "train/index.html", { "form": form })

    if request.method == "POST": 
        form = NewGameForm(request.POST)
        if form.is_valid():
            nb_games = form.cleaned_data.get("nb_games")
            ia1 = User.manager.get(username=form.cleaned_data.get("ia1"))
            ia2 = User.manager.get(username=form.cleaned_data.get("ia2"))
            setup_games(ia1, ia2, nb_games)
            return HttpResponse("Training done, check the log file for more data.")

        return render(request, "train/index.html", { "form": form })
def setup_games(ia1, ia2, nb_games):
    for i in range(nb_games):
        print("Game "+str(i+1)+" en cours")
        play(ia1, ia2)
        print("Game "+str(i+1)+" terminée")





def play(u1, u2):
    board = [[1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,2]]
    game_state_data = Game_State(current_player=1, board=board)
    game_state_data.save()
    colors = build_colors([u1,u2])
    game_player1 = get_game_player(u1.username,game_state_data, [0,0],colors[0])
    game_player2 = get_game_player(u2.username,game_state_data, [7,7],colors[1])
    game_players = [game_player1, game_player2]
    indice=0
    game_state = build_game_state(game_state_data, [game_player1, game_player2], game_player1.auto_increment_id,0)  
    while is_current_player_ai(game_players[indice]) and not end_of_game(game_state_data.board):
        movement = do_play(board, game_players,indice)
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
            with open("log.txt", "a") as f:
                f.write("Tie\n"if game_state.get("winner").get("tie") else ""+ game_state.get("winner").get("name")+" with "+str(game_state.get("winner").get("nb_cell"))+" cells.\n")



def do_play(board, game_players, indice):
    if indice == 1:
        i_o = 0
    else:
        i_o = 1
    user = User.manager.get(username=game_players[indice].user.username)
    direction_board =play_ai(board,game_players[indice].pos,game_players[i_o].pos,user,game_players[indice],indice)
    movement = direction_board[0]
    game_players[indice].previous_state_ai = direction_board[1]
    return movement 





