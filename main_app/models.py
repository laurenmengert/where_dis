from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import datetime

# Create your models here.
class GameInstance(models.Model):
    name = models.CharField(max_length=50)
    start_time = models.TimeField(
        auto_now_add=True,  # automatically sets to the time when the object is created
        )
    # WINNING LOCATION FROM METADATA FIELD
    # PLAYERS FIELD MANY TO MANY 
    # HOST FOREIGN KEY FOREIGN KEY
    # WINNER FOREIGN KEY  NULL=TRUE
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)    # MAY WANT TO RECONSIDER CASCADE HERE. CAN USERS BE DELETED?
    # lat = models.DecimalField()
    # lng = models.DecimalField()
    
    
    def __str__(self):
        return f'Photo for game_id: {self.game_instance.id} user {self.user_id} @{self.url}'
    

# USER_INFO MODEL
    # USER_ID FOREIGN KEY FIELD
    # IS_HOST BOOLEAN FIELD  -----------  MIGHT BELONG ON GAME MODEL
    # ROUNDS_WON INTEGER FIELD
    
    