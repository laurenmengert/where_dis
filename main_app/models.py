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
    # USER_ID FOREIGN KEY FIELD
    # DIFFICULTY SETTING FIELD
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('game_detail', kwargs={"pk": self.id})
    
    
# PHOTO MODEL
    # GAME_INSTANCE_ID FOREIGN KEY FIELD
    # LOCATION METADATA FIELD
    # USER_ID FOREIGN KEY FIELD
    

# USER_INFO MODEL
    # USER_ID FOREIGN KEY FIELD
    # IS_HOST BOOLEAN FIELD  -----------  MIGHT BELONG ON GAME MODEL
    # ROUNDS_WON INTEGER FIELD
    
    