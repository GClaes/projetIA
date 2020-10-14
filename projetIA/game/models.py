from django.db import models
from models import Player


# Create your models here.
class Game_State(models.Model):
    id=models.AutoField(primary_key=True)
    current_player=models.IntegerField()
    bord=models.CharField(max_length=146)
class Game_Player(models.Model):
    user_username=models.ForeignKey(Player,on_delete=models.CASCADE)
    game_state_id=models.ForeignKey(Game_State,on_delete=models.CASCADE)
    id=models.AutoField(primary_key=True)
    pos=models.CharField(max_length=5)
   

