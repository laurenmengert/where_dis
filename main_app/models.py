from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from exiffield.fields import ExifField
from GPSPhoto import gpsphoto
import datetime


class GameInstance(models.Model):
    name = models.CharField(max_length=50)
    details = models.TextField(
        max_length=500,
        null=True,
        blank=True
    )
    
    start_time = models.TimeField(
        auto_now_add=True,  # automatically sets to the time when the object is created
    )
    
    host = models.ForeignKey(
        User, 
        editable=False,            
        on_delete=models.CASCADE    
    )  
    
    winner = models.ForeignKey(
        User, 
        null=True,                  # Allows nulls in DB
        blank=True,                 # Allows blank values, UPDATE to user with first winning photo
        related_name='winner',     
        on_delete=models.CASCADE    
    ) 
    
    reference_lat = models.DecimalField(decimal_places=8, max_digits=11, null=True, blank=True) # Blanks b/c game created before photo
    reference_lng = models.DecimalField(decimal_places=8, max_digits=12, null=True, blank=True) 

    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('game_detail', kwargs={"pk": self.id})
    
    
class Photo(models.Model):
    url = models.CharField(max_length=200)
    game_instance = models.ForeignKey(GameInstance, on_delete=models.CASCADE)
    is_reference = models.BooleanField(default=False)           # True indicates the 'goalpost' photo
    user = models.ForeignKey(User, on_delete=models.CASCADE)   
    lat = models.DecimalField(decimal_places=8, max_digits=11)  
    lng = models.DecimalField(decimal_places=8, max_digits=12)
    
    def __str__(self):

        return f'Photo for game_id: {self.game_instance.id} user {self.user_id} @{self.url}'  

