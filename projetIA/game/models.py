from django.db import models
from connection.models import User


# Create your models here.
class Game_State(models.Model):
    auto_increment_id=models.AutoField(primary_key=True)
    current_player=models.IntegerField()
    board=models.CharField(max_length=146)
    manager = models.Manager()

class Game_Player(models.Model):
    auto_increment_id=models.AutoField(primary_key=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    game_state=models.ForeignKey(Game_State,on_delete=models.CASCADE)
    pos=models.CharField(max_length=5)
    manager = models.Manager()
   

