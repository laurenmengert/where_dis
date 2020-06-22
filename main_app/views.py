from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView
from .models import GameInstance


# Create your views here.

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

def game_map(request):
    mapbox_access_token = 'pk.eyJ1IjoidGF3bHVyIiwiYSI6ImNrYmp5MmZlaTA3YXEyc2x4dGZua2EyeHEifQ.gHRUEAc8Bs48FURFPwxvZg'
    return render(request, 'map.html', { 'mapbox_access_token': mapbox_access_token })

# def game_map(request, game_id):
#     return redirect('game_detail', game_id=game_id)

# ------------------------PHOTOS---------------------------- #