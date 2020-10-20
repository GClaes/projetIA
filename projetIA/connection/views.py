from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from connection.models import User, User_data

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

    def clean (self):
        cd=self.cleaned_data

        c_username = cd.get("username")
        password = cd.get("password")
        cpassword = cd.get("confirm_password")

        if password != cpassword:
            raise forms.ValidationError("Passwords did not match")

        #Rechercher si username existant
        try:
            user = User.manager.get(username = c_username)
        except User.DoesNotExist: #Aucune idée de pourquoi c'est souligné en rouge alors que c'est bon ?
            return cd
        raise forms.ValidationError("User does already exist")
        



def index(request):
    if request.method == "GET": # get connection page
        #Login de Test
        ud = User_data(password = "test")
        ud.save()
        u = User(username = "Test", user_data = ud, color1 = "R", color2="B")
        u.save()
        #
        form = ConnectionForm() # empty form
        return render(request, "connection/index.html", { "form": form })

    if request.method == "POST": # post a connection
        form = ConnectionForm(request.POST) #auto fill form with info in POST
        
        if form.is_valid():
            return HttpResponse("OK")
        
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
            ud = User_data(password=cd_password)
            ud.save()
            u = User(username=cd_username, user_data = ud, color1="R", color2="B")
            u.save()


            #Permet de vérifier que ça a bien enregistré et de récupérer le compte
            user = User.manager.get(username = cd_username)
            return HttpResponse("You are correctly signed up "+user.username+"//"+user.user_data.password)

        return render(request, "connection/signup.html", { "form": form })
