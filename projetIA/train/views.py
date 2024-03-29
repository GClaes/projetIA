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
from AI.train import *
from django.db import transaction
import time


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
    setup_training(ia1.ai_id, ia2.ai_id)
    chronos = []
    for i in range(nb_games):
        print("Game "+str(i+1)+" en cours")
        debut_game = time.time()
        play(ia1, ia2)
        fin_game = time.time()
        duree_game = fin_game - debut_game
        chronos.append(duree_game)
        print(str(duree_game)+" secondes")
        print("Game "+str(i+1)+" terminée")
    print("Les variables globales ont été nettoyées")
    temps_total = reduce(lambda x,y: x+y,chronos)
    print("Les "+str(nb_games)+" parties ont pris "+str(round(temps_total,2))+" secondes à se réaliser, soit "+str(round(temps_total/nb_games,2))+" secondes par partie en moyenne.")    

def play(u1, u2):
    """
    SETUP DE LA GAME
    """
    #board = [[1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,2]]
    board = [[1,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,2]]
    game_state_data = Game_State(current_player=1, board=board)
    game_state_data.save()
    #game_player1 = Game_Player(user=u1, game_state=game_state_data, pos=[0,0])
    #game_player2 = Game_Player(user=u2, game_state=game_state_data, pos=[7,7])
    game_player1 = Game_Player(user=u1,game_state=game_state_data, pos=[0,0])
    game_player2 = Game_Player(user=u2,game_state=game_state_data, pos=[3,3])
    game_player1.user.ai_id.nb_games_training+=1
    game_player1.user.ai_id.save()
    game_player2.user.ai_id.nb_games_training+=1
    game_player2.user.ai_id.save()
    current_player = None
    u1.ai_id.epsilon = epsilon_greedy_training(u1.ai_id)
    u2.ai_id.epsilon = epsilon_greedy_training(u2.ai_id)
    game_players = [game_player1, game_player2]
    indice=0
    game_state = build_game_state(game_state_data, [game_player1, game_player2], game_player1.auto_increment_id,0)  
    """
    DEBUT DE LA PARTIE
    """
    direction = None
    while is_current_player_ai(game_players[indice]) and not end_of_game(game_state_data.board):
        user = get_user_from_player(u1, u2, game_players[indice])
        movement, direction = do_play(board, game_players,indice, user, direction)
        game_state_data = move_pos(game_players[indice], movement, game_state_data, game_players)
        indice = switch_player(indice)
        game_state = build_game_state(game_state_data, [game_player1, game_player2], game_player2.auto_increment_id,0)
        if end_of_game(game_state_data.board):
            """
            FIN DE LA PARTIE
            """
            game_state = build_game_state(game_state_data, game_players, current_player, 0)
            winner_id, nb_cell_winner, tie = define_winner(game_state.get("board"))
            data_winner = {"name": game_players[winner_id-1].user.username, "nb_cell": nb_cell_winner, "tie":tie}
            game_state["winner"] =  data_winner
            game_players[winner_id-1].user.ai_id.nb_games_training_wins+=1
            game_players[winner_id-1].user.ai_id.save()
            save_data_from_training()
            clear_data()
            with open("log.txt", "a") as f:
                f.write("Tie\n"if game_state.get("winner").get("tie") else ""+ game_state.get("winner").get("name")+" with "+str(game_state.get("winner").get("nb_cell"))+" cells.\n")

def switch_player(indice):
    return 1 if indice == 0 else 0
    
def do_play(board, game_players, indice, user, direction):
    if indice == 1:
        i_o = 0
    else:
        i_o = 1
    direction_board, direction =training_play(board,game_players[indice].pos,game_players[i_o].pos,game_players[indice],indice, user.ai_id, direction)
    movement = direction_board[0]
    game_players[indice].previous_state_ai = direction_board[1]
    return movement, direction


def get_user_from_player(u1,u2, game_player):
    return u1 if game_player.user.username == u1.username else u2

"""
Difference between Atomic Transaction and Bulk create:
For 50000 saves
Atomic Transaction takes: 27s
Bulk create takes: 3.5s
https://pmbaumgartner.github.io/blog/the-fastest-way-to-load-data-django-postgresql/
"""

@transaction.atomic 
def save_data_from_training():
    ai_s, states = get_data_from_training()
    for ai in ai_s:
        ai.save()
    for state in states:
        state.save()
    print(str(len(states))+" nouveaux états créés")


"""
The problem with the bulk_create method is that it doesn't do update.
It only does create statement, which is a problem because we often update State.
If we decide to fix this with conditions, we will probably be slower than with an atomic transaction due to conditions.
"""
"""
def save_data_from_training():
    ai_s, states = get_data_from_training()
    states_list = []
    for ai in ai_s:
        ai.save()
    for state in states:
        states_list.append(state)
    State.manager.bulk_create(states_list)
    print(str(len(states_list))+" nouveaux états créés")
   """ 
