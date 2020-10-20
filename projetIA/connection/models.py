from django.db import models

class User_data(models.Model):
    auto_increment_id = models.AutoField(primary_key = True)
    password=models.CharField(max_length=25)


class User(models.Model):
    username=models.CharField(max_length=25,primary_key=True)
    user_data=models.ForeignKey(User_data,on_delete=models.CASCADE)

    colors = (
        ('R', 'Red'),
        ('B', 'Blue'),
        ('Y', 'Yellow'),
        ('G', 'Green'),
    )

    color1=models.CharField(max_length=1, choices=colors)
    color2=models.CharField(max_length=1, choices=colors)

    manager = models.Manager()
    


