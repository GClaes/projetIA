from django.shortcuts import render
from django.http import HttpResponse
from django import forms

class ConnectionForm (forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())



class SignupForm (forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput())

    def clean (self):
        #Définir condition
        cd=self.cleaned_data

        #username = cd.get("username")
        password = cd.get("password")
        cpassword = cd.get("confirm_password")

        if password != cpassword:
            raise forms.ValidationError("Passwords did not match")

        #Rechercher si username existant
        #raise forms.ValidationError("User does already exist")

        return cd
        




def index(request):
    if request.method == "GET": # get connection page
        form = ConnectionForm() # empty form
        return render(request, "connection/index.html", { "form": form })

    if request.method == "POST": # post a connection
        form = ConnectionForm(request.POST) #auto fill form with info in POST
        
        if form.is_valid():
            # Check credentials
            return HttpResponse("OK")
        return HttpResponse("KO")


def signup(request):
    if request.method == "GET":
        form = SignupForm()
        return render(request, "connection/signup.html", { "form": form })
    if request.method == "POST":
        form = SignupForm(request.POST) #auto fill form with info in POST
        if form.is_valid():
            #Enregister en base de données
            username = form.cleaned_data.get("username") #Permet d'accéder aux champs
            password = form.cleaned_data.get("password")
            cpassword = form.cleaned_data.get("confirm_password")
            return HttpResponse("You are correctly signed up "+username+"//"+password+"//"+cpassword)

        return render(request, "connection/signup.html", { "form": form })
