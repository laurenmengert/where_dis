from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from exiffield.fields import ExifField
from GPSPhoto import gpsphoto
import datetime

# Create your models here.
class GameInstance(models.Model):
    name = models.CharField(max_length=50)
    start_time = models.TimeField(
        auto_now_add=True,  # automatically sets to the time when the object is created
    )
    # HOST FOREIGN KEY FOREIGN KEY
    # WINNER FOREIGN KEY  NULL=TRUE
    # WINNING LOCATION FROM METADATA FIELD
    host = models.ForeignKey(
        User, 
        editable=False,             # We shouldn't be able to change the host, select User at creation
        on_delete=models.CASCADE    # Reconsider? Do we want games to disappear if accounts are deleted
    )  
    winner = models.ForeignKey(
        User, 
        null=True,                  # Allows nulls in DB
        blank=True,                 # Allows blank values, UPDATE to user with first winning photo
        related_name='winner',      # Needed to override conflict with host model, both would have same Django-created name for queries
        on_delete=models.CASCADE    # Reconsider? Do we want games to disappear if accounts are deleted
    ) 
    
    reference_lat = models.DecimalField(decimal_places=8, max_digits=11, null=True, blank=True) # Blanks b/c game created before photo
    reference_lng = models.DecimalField(decimal_places=8, max_digits=12, null=True, blank=True)
    
    
    
    #---------------ICEBOX-----------------#
    # ENDTIME TO TRACK HOW FAST EACH GAME IS WON
    # PLAYERS FIELD MANY TO MANY FOR PRIVATE GAMES
    # DIFFICULTY SETTING FIELD
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('game_detail', kwargs={"pk": self.id})
    
    
# PHOTO MODEL
    # GAME_INSTANCE_ID FOREIGN KEY FIELD
    # LOCATION METADATA FIELD
    # USER_ID FOREIGN KEY FIELD
    
class Photo(models.Model):
    url = models.CharField(max_length=200)
    game_instance = models.ForeignKey(GameInstance, on_delete=models.CASCADE)
    is_reference = models.BooleanField(default=False)           # True indicates the 'goalpost' photo
    user = models.ForeignKey(User, on_delete=models.CASCADE)    # MAY WANT TO RECONSIDER CASCADE HERE. CAN USERS BE DELETED?
    lat = models.DecimalField(decimal_places=8, max_digits=11)  # Do we need some sort of error handling here in the long term?
    lng = models.DecimalField(decimal_places=8, max_digits=12)
    
    def __str__(self):
        return f'Photo for game_id: {self.game_instance.id} user {self.user_id} @{self.url}'
    

# USER_INFO MODEL
    # USER_ID FOREIGN KEY FIELD
    # IS_HOST BOOLEAN FIELD  -----------  MIGHT BELONG ON GAME MODEL
    # ROUNDS_WON INTEGER FIELD
    
    