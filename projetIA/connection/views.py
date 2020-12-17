from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from connection.models import User, User_data
from AI.models import AI
from game.views import NewGameForm

class ConnectionForm (forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def clean(self):
        cd = self.cleaned_data

        c_password = cd.get("password")
        c_username = cd.get("username")

        try:
            user = User.manager.get(username = c_username)
        except User.DoesNotExist: #Aucune idée de pourquoi c'est souligné en rouge alors que c'est bon ?
            raise forms.ValidationError("User doesn't exist")

        if(user.user_data.password != c_password):
            raise forms.ValidationError("Incorrect password")
        return cd



class SignupForm (forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput())

    COLOR_CHOICES = [
            ('blue', 'blue'),
            ('darkBlue', 'darkBlue'),
            ('cyan', 'cyan'),
            ('darkCyan', 'darkCyan'),
            ('green', 'green'),
            ('darkGreen', 'darkGreen'),
            ('yellow', 'yellow'),
            ('orange', 'orange'),
            ('darkOrange', 'darkOrange'),
            ('red', 'red'),
            ('darkRed', 'darkRed'),
            ('purple', 'purple'),
            ('black', 'black'),
        ]

    fav_color1 = forms.MultipleChoiceField(
        label = 'Color 1',
        required=False,
        choices= COLOR_CHOICES,
    )
    fav_color2 = forms.MultipleChoiceField(
        label = 'Color 2',
        required=False,
        choices= COLOR_CHOICES,
    )


    def clean (self):
        cd=self.cleaned_data

        c_username = cd.get("username")
        password = cd.get("password")
        cpassword = cd.get("confirm_password")

        color1 = cd.get("fav_color1")
        if len(color1) > 1:
            raise forms.ValidationError("Choose only one color for Color 1")
        if len(color1) < 1:
            raise forms.ValidationError("Choose one color for Color 1")

        color2 = cd.get("fav_color2")
        if len(color2) > 1:
            raise forms.ValidationError("Choose only one color for Color 2")
        if len(color2) < 1:
            raise forms.ValidationError("Choose one color for Color 2")
        
        colors = []
        colors.append(color1[0])
        colors.append(color2[0])

        if password != cpassword:
            raise forms.ValidationError("Passwords did not match")

        #Rechercher si username existant
        try:
            user = User.manager.get(username = c_username)
        except User.DoesNotExist:
            return cd
        raise forms.ValidationError("User does already exist")

class AIForm(forms.Form):
    ai_name = forms.CharField(label="AI Name")
    epsilon = forms.IntegerField(label="Epsilon (0-100)")
    learning_rate = forms.FloatField(label ="Learning rate (0-1)")
    speed_learning = forms.IntegerField(label=" Speed (>0)")

    COLOR_CHOICES = [
            ('blue', 'blue'),
            ('darkBlue', 'darkBlue'),
            ('cyan', 'cyan'),
            ('darkCyan', 'darkCyan'),
            ('green', 'green'),
            ('darkGreen', 'darkGreen'),
            ('yellow', 'yellow'),
            ('orange', 'orange'),
            ('darkOrange', 'darkOrange'),
            ('red', 'red'),
            ('darkRed', 'darkRed'),
            ('purple', 'purple'),
            ('black', 'black'),
        ]   

    fav_color1 = forms.MultipleChoiceField(
        label = 'Color 1',
        required=False,
        choices= COLOR_CHOICES,
    )
    fav_color2 = forms.MultipleChoiceField(
        label = 'Color 2',
        required=False,
        choices= COLOR_CHOICES,
    )



    def clean(self):
        cd= self.cleaned_data
        c_ai_name = cd.get("ai_name")

        color1 = cd.get("fav_color1")
        if len(color1) > 1:
            raise forms.ValidationError("Choose only one color for Color 1")
        if len(color1) < 1:
            raise forms.ValidationError("Choose one color for Color 1")

        color2 = cd.get("fav_color2")
        if len(color2) > 1:
            raise forms.ValidationError("Choose only one color for Color 2")
        if len(color2) < 1:
            raise forms.ValidationError("Choose one color for Color 2")
        
        colors = []
        colors.append(color1[0])
        colors.append(color2[0])

        c_epsilon =  cd.get("epsilon")
        c_learning_rate = cd.get("learning_rate")
        c_speed_learning = cd.get("speed_learning")

        if c_epsilon > 100 or c_epsilon < 0:
            raise forms.ValidationError("Epsilon value is not correct")
        if c_learning_rate > 1 or c_learning_rate < 0:
            raise forms.ValidationError("Learning rate value is not correct")
        if c_speed_learning < 1:
            raise forms.ValidationError("Speed value is not correct")

        try:
            ai = AI.manager.get(username = c_ai_name)
        except AI.DoesNotExist:
            return cd
        raise forms.ValidationError("AI with this name does already exist")
        



def index(request):
    if request.method == "GET": # get connection page
        #Login de Test
        ud = User_data(password = "test")
        ud.save()
        u = User(username = "Test", user_data = ud, color1 = "R", color2="B",nb_games_wins = 0,nb_games = 0)
        u.save()
        #
        form = ConnectionForm() # empty form
        return render(request, "connection/index.html", { "form": form })

    if request.method == "POST": # post a connection
        form = ConnectionForm(request.POST) #auto fill form with info in POST
        
        if form.is_valid():
            return render(request, "game/index.html", { "form": form })
        
        return render(request, "connection/index.html", { "form": form })

def signup(request):
    if request.method == "GET":
        form = SignupForm()
        return render(request, "connection/signup.html", { "form": form })
    if request.method == "POST":
        form = SignupForm(request.POST) #auto fill form with info in POST
        if form.is_valid():
            #Enregister en base de données
            cd_username = form.cleaned_data.get("username") #Permet d'accéder aux champs
            cd_password = form.cleaned_data.get("password")

            cd_colors = []
            color1 = form.cleaned_data.get("fav_color1")
            color2 = form.cleaned_data.get("fav_color2")
            cd_colors.append(color1[0])
            cd_colors.append(color2[0])

            ud = User_data(password=cd_password)
            ud.save()
            u = User(username=cd_username, user_data = ud, color1=cd_colors[0], color2=cd_colors[1],nb_games=0,nb_games_wins = 0)
            u.save()


            #Permet de vérifier que ça a bien enregistré et de récupérer le compte
            user = User.manager.get(username = cd_username)
            #return HttpResponse("You are correctly signed up "+user.username+"//"+user.user_data.password+"//"+user.color1+"//"+user.color2)
            form = ConnectionForm(request.POST)
            return render(request, "connection/index.html", { "form": form })

        return render(request, "connection/signup.html", { "form": form })

def signup_ai(request):
    if request.method == "GET":
        form = AIForm()
        return render(request, "connection/signup_ai.html", {"form": form})
    if request.method == "POST":
        form = AIForm(request.POST)
        if form.is_valid():
            c_ai_name = form.cleaned_data.get("ai_name")
            c_epsilon = form.cleaned_data.get("epsilon")
            c_learning_rate = form.cleaned_data.get("learning_rate")
            c_speed_learning = form.cleaned_data.get("speed_learning")

            cd_colors = []
            color1 = form.cleaned_data.get("fav_color1")
            color2 = form.cleaned_data.get("fav_color2")
            cd_colors.append(color1[0])
            cd_colors.append(color2[0])

            ai = AI(username = c_ai_name, epsilon= c_epsilon, nb_games=0, user_data = None, color1=cd_colors[0], color2=cd_colors[1],learning_rate = c_learning_rate, nb_games_wins = 0,speed_learning = c_speed_learning)
            ai.save()

            ai = AI.manager.get(username = c_ai_name)

            form = ConnectionForm(request.POST)
            return render(request, "connection/index.html", { "form": form })

            return HttpResponse("You are correctly signed up "+ai.username)

        return render(request, "connection/signup_ai.html", {"form": form})

