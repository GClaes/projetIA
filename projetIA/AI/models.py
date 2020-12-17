from django.db import models
from connection.models import User

# Create your models here.
class AI(User):
    id = models.AutoField(primary_key = True)
    epsilon = models.FloatField()
    speed_learning = models.IntegerField()
    learning_rate = models.FloatField()
    manager = models.Manager()



class State(models.Model):
    id = models.AutoField(primary_key = True)
    board=models.CharField(max_length=146)
    position = models.CharField(max_length=2)
    position2 = models.CharField(max_length=2)
    q_table = models.CharField(max_length=100)
    ai_id=models.ForeignKey(AI,on_delete=models.CASCADE)

    manager = models.Manager()


