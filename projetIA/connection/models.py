from django.db import models

# Create your models here.
class User_data(models.Model):
    password=models.CharField(max_length=25)


class Player(models.Model):
    user=models.ForeignKey(User_data,on_delete=models.CASCADE)
    username=models.CharField(max_length=25).primary_key=True
    color1=models.IntegerField()
    color2=models.IntegerField()
    


