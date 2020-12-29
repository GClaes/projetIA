from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django import forms
from connection.models import User, User_data


class StatForm(forms.Form):
    player = forms.CharField(label="Player username")

    def clean(self):
        cd = self.cleaned_data
        c_username = cd.get("player")
        try:
            p1 = User.manager.get(username = c_username)
        except User.DoesNotExist:
            raise forms.ValidationError("This player doesn't exist")
        return cd




def index(request):
    if request.method == "GET":
        form = StatForm(auto_id='id_for_%s')
        return render(request, "stats/index.html", {"form": form})

    if request.method == "POST": 
        form = StatForm(request.POST)
        if form.is_valid():
            u = User.manager.get(username = form.cleaned_data.get("player")) 
            return printData(u, request)
        return render(request, "stats/index.html", {"form": form })

def printData(user, request):
    data = get_data(user)
    return render(request, "stats/data.html", {"data":data})

def get_data(user):
    data = {}
    data["user"]=user
    data["prc"] = user.nb_games_wins / user.nb_games * 100 if user.nb_games != 0 else 0
    if user.ai_id:
        data["ai"]=user.ai_id
        data["prc2"] = user.ai_id.nb_games_training_wins / user.ai_id.nb_games_training * 100 if user.ai_id.nb_games_training != 0 else 0 
    return data