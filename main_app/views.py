from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView
from .models import GameInstance, Photo
import uuid
import boto3


# ----------------------CONSTANTS-------------------------- #


S3_BASE_URL = 'https://s3.us-east-2.amazonaws.com/'
BUCKET = 'wheredis'


# -----------------------GENERAL--------------------------- #


def home(request):
    return render(request, 'home.html')


def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('home')
    else:
      error_message = 'Something went wrong! :( Give it another shot'
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)


# ------------------------GAMES---------------------------- #

class GameList(ListView):
  model = GameInstance
  

# THIS IS THE BIG FUNCTION
# MAKE SURE WE SEND THE DATA WE NEED TO THE GAME DETAIL VIEW 
def game_detail(request, game_id):
  game_from_db = GameInstance.objects.get(id=game_id)
  return render(request, 'game/detail.html', {
    'game': game_from_db
  })

# def game_map(request):
#     mapbox_access_token = ''
#     return render(request, 'map.html', { 'mapbox_access_token': mapbox_access_token })

def game_map(request, game_id):
    context = {'mapbox_access_token': ''}
    
    return redirect('game_detail', context, game_id=game_id)



# ------------------------PHOTOS---------------------------- #


def upload_photo(request, game_id, user_id): # DOUBLE-CHECK GAME ID AND MULTIPLE KWARGS
  photo_file = request.FILES.get('photo-file', None)
  if photo_file:
    s3 = boto3.client('s3')
    key = uuid.uuid4() + photo_file.name[photo_file.name.rfind('.'):]
    
    try:
      s3.upload_fileobj(photo_file, BUCKET, key)
      url = f'{S3_BASE_URL}{BUCKET}/{key}'
      photo = Photo(url=url, game_instance_id=game_id, user_id=user_id) # DOUBLE-CHECK HERE TOO
      photo.save()
    except:
      print('There has been an error uploading to S3')
  return redirect('game_detail', game_id=game_id)