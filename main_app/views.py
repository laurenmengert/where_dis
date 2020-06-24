from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse
from .models import GameInstance, Photo
import uuid
import boto3
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import copy


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
      return redirect('game_list')
    else:
      error_message = 'Something went wrong! :( Give it another shot'
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)


# ------------------------GAMES---------------------------- #

class GameList(ListView):
  model = GameInstance
  
  
class GameCreate(CreateView):
  model = GameInstance
  fields = ['name', 'details']
  
  def form_valid(self, form):
    form.instance.host = self.request.user
    return super().form_valid(form)
  
  def get_success_url(self):
    print(self.object.id, '<====================================================self.object.id')
    print(type(self.object.id), '<====================================================type(self.object.id)')
    return reverse('game_ref_photo_form', kwargs={'game_id':self.object.id})
  

# THIS IS THE BIG FUNCTION
# MAKE SURE WE SEND THE DATA WE NEED TO THE GAME DETAIL VIEW 
def game_detail(request, game_id):
  game_from_db = GameInstance.objects.get(id=game_id)
  # PASS RELEVANT REFERENCE PHOTO
  # PASS WINNING LAT/LONG (DONE BY PASSING GAME)
  ref_photo = Photo.objects.filter(game_instance=game_from_db, is_reference=True)[0]
  print(ref_photo, '<=======================our photo')
  return render(request, 'game/detail.html', {
    'game': game_from_db,
    'ref_photo': ref_photo
  })

# def game_map(request):
#     mapbox_access_token = ''
#     return render(request, 'map.html', { 'mapbox_access_token': mapbox_access_token })

def game_map(request, game_id):
  # NEED TO PASS CENTER OF MAP DATA HERE
  context = {'mapbox_access_token': ''}
  
  return redirect('game_detail', context, game_id=game_id)



# ------------------------PHOTOS---------------------------- #


# Helper function for converting type of extracted lat and long
def get_decimal_coordinates(info):
  for key in ['Latitude', 'Longitude']:
      if 'GPS'+key in info and 'GPS'+key+'Ref' in info:
          e = info['GPS'+key]
          ref = info['GPS'+key+'Ref']
          info[key] = ( e[0][0]/e[0][1] +
                        e[1][0]/e[1][1] / 60 +
                        e[2][0]/e[2][1] / 3600
                      ) * (-1 if ref in ['S','W'] else 1)

  if 'Latitude' in info and 'Longitude' in info:
      return [info['Latitude'], info['Longitude']]


def game_ref_photo_form(request, game_id):
  context = {'game_id':game_id}
  return render(request, 'game/ref_photo_form.html', context)


def upload_ref_photo_function(request, game_id):
  photo_file = request.FILES.get('photo-file', None)
  game = GameInstance.objects.get(id=game_id)
  
  #--------------------------INSIDE IF---------------------------
  photo_copy = copy.deepcopy(photo_file)
  exif = Image.open(photo_copy)._getexif()
  print(exif is not None)
  if exif is not None:
      for key, value in exif.items():
          name = TAGS.get(key, key)
          exif[name] = exif.pop(key)

      if 'GPSInfo' in exif:
          for key in exif['GPSInfo'].keys():
              name = GPSTAGS.get(key,key)
              exif['GPSInfo'][name] = exif['GPSInfo'].pop(key)
              
  print(exif, 'EXIFFFFFFFF')
  decimals = get_decimal_coordinates(exif['GPSInfo'])
  print(decimals)
  
  lat = decimals[0]
  lng = decimals[1]
  
  game.reference_lat = lat
  game.reference_lng = lng
  game.save()
  #-----------------------------INSIDE IF--------------------------
  
  if photo_file:
    s3 = boto3.client('s3')
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    
    try:
      print('TRY step 1')
      s3.upload_fileobj(photo_file, BUCKET, key)
      print('TRY step 2')
      url = f'{S3_BASE_URL}{BUCKET}/{key}'
      # photo_obj = gpsphoto.getGPSData(f'{url}')
      # print('photo_obj:', photo_obj)
      print(f'TRY step 3 url = {url}')
      photo = Photo(url=url, game_instance_id=game_id, user=request.user, lat=lat, lng=lng, is_reference=True) # DOUBLE-CHECK HERE TOO
      print(f'TRY step 4 photo = {photo}')
      photo.save()
      print('TRY step 5')
      # photo_obj = gpsphoto.getGPSData(f'{url}')
      # print('photo_obj:', photo_obj)
    except:
      print('There has been an error uploading to S3')
  return redirect('game_detail', game_id=game_id)



    

# def save_picture(form_picture):
#     # this function has to do with the module Pillow
#     # PIL
#     # purpose is to save the image as a static asset
#     # 1. generate a random name
#     random_hex = uuid.uuid4().hex[:8]# generates a random integer
#     # grabbing the ext , jpeg, jpg
    
#     print(form_picture, '<=====form_picture')
#     f_name, f_ext = os.path.splitext(form_picture.name)
#     # => ['jimProfile', 'png']
#     # create the random picture name with the correct extension
#     picture_name = random_hex + f_ext
#     # create the file_path
#     file_path = os.path.join(os.getcwd(), 'main_app/tmp/' + picture_name)
#     print(file_path, '<=======================file_path')
    
#     # file_path = os.path.join(os.getcwd(), 'main_app/tmp' + picture_name) # print this
#     # Pillow code stars
#     # output_size = (125, 175) # set the size of picture, as tuple
#     # open the file sent from the client
#     i = Image.open(form_picture)
#     # exif = i._exif._loaded_exif
#     # print( i.gps_latitude, 'latitude')
    
#     exif_dict = piexif.load(i.info["exif"])
#     exif_bytes = piexif.dump(exif_dict)
    
#     print(exif_bytes, '<=======exif_bytes')
    
#     # print(exif, 'exifffffffffffffffffffffffffffff')
    
#     # i.thumbnail(output_size) # set the size accepts a tuple with dimensions
#     i.save(file_path) # save it to file path we created
#     return file_path  #RETURN FILEPATH
  
  
# # CREATE HELPER FUNCTION TO DELETE


def upload_photo(request, game_id): # DOUBLE-CHECK GAME ID AND MULTIPLE KWARGS
  photo_file = request.FILES.get('photo-file', None)
  
  #--------------------------INSIDE IF---------------------------
  photo_copy = copy.deepcopy(photo_file)
  exif = Image.open(photo_copy)._getexif()
  print(exif is not None)
  if exif is not None:
      for key, value in exif.items():
          name = TAGS.get(key, key)
          exif[name] = exif.pop(key)

      if 'GPSInfo' in exif:
          for key in exif['GPSInfo'].keys():
              name = GPSTAGS.get(key,key)
              exif['GPSInfo'][name] = exif['GPSInfo'].pop(key)
              
  print(exif, 'EXIFFFFFFFF')
  decimals = get_decimal_coordinates(exif['GPSInfo'])
  print(decimals)
  
  lat = decimals[0]
  lng = decimals[1]
  #-----------------------------INSIDE IF--------------------------
  
  if photo_file:
    s3 = boto3.client('s3')
    key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
    
    try:
      print('TRY step 1')
      s3.upload_fileobj(photo_file, BUCKET, key)
      print('TRY step 2')
      url = f'{S3_BASE_URL}{BUCKET}/{key}'
      # photo_obj = gpsphoto.getGPSData(f'{url}')
      # print('photo_obj:', photo_obj)
      print(f'TRY step 3 url = {url}')
      photo = Photo(url=url, game_instance_id=game_id, user=request.user, lat=lat, lng=lng) # DOUBLE-CHECK HERE TOO
      print(f'TRY step 4 photo = {photo}')
      photo.save()
      print('TRY step 5')
      # photo_obj = gpsphoto.getGPSData(f'{url}')
      # print('photo_obj:', photo_obj)
    except:
      print('There has been an error uploading to S3')
  return redirect('game_detail', game_id=game_id)
