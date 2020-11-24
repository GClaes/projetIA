from django.db import models

# Create your models here.
class AI(models.Model):
    ai_name = models.CharField(max_length=25,primary_key=True)
    nb_games = models.IntegerField()
    epsilon = models.FloatField()


class State(models.Model):
    id = models.AutoField(primary_key = True)
    board=models.CharField(max_length=146)
    grid_point_db = models.CharField(max_length=146)
    position = models.CharField(max_length=2)
    q_table = models.FloatField()
    ai_id=models.ForeignKey(AI,on_delete=models.CASCADE)

    manager = models.Manager()


