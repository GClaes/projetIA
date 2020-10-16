from django.db import models

# Create your models here.
class User_data(models.Model):
    auto_increment_id = models.AutoField(primary_key = True)
    password=models.CharField(max_length=25)


class User(models.Model):
    username=models.CharField(max_length=25).primary_key=True
    user_data=models.ForeignKey(User_data,on_delete=models.CASCADE)
    color1=models.IntegerField()
    color2=models.IntegerField()
    


