from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView
from .models import GameInstance, Photo
from GPSPhoto import gpsphoto
import uuid
import boto3
import os, sys
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import copy
import piexif


# ----------------------CONSTANTS-------------------------- #


S3_BASE_URL = 'https://s3.us-east-2.amazonaws.com/'
BUCKET = 'wheredis'



# -----------------------GENERAL--------------------------- #


def home(request):
  photo_obj = gpsphoto.getGPSData('/Users/Shawn/code/where_dis/main_app/wireframe.jpg')
  print('photo_obj:', photo_obj)
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
  # NEED TO PASS CENTER OF MAP DATA HERE
  context = {'mapbox_access_token': ''}
  
  return redirect('game_detail', context, game_id=game_id)



# ------------------------PHOTOS---------------------------- #


def save_picture(form_picture):
    # this function has to do with the module Pillow
    # PIL
    # purpose is to save the image as a static asset
    # 1. generate a random name
    random_hex = uuid.uuid4().hex[:8]# generates a random integer
    # grabbing the ext , jpeg, jpg
    
    print(form_picture, '<=====form_picture')
    f_name, f_ext = os.path.splitext(form_picture.name)
    # => ['jimProfile', 'png']
    # create the random picture name with the correct extension
    picture_name = random_hex + f_ext
    # create the file_path
    file_path = os.path.join(os.getcwd(), 'main_app/tmp/' + picture_name)
    print(file_path, '<=======================file_path')
    
    # file_path = os.path.join(os.getcwd(), 'main_app/tmp' + picture_name) # print this
    # Pillow code stars
    # output_size = (125, 175) # set the size of picture, as tuple
    # open the file sent from the client
    i = Image.open(form_picture)
    # exif = i._exif._loaded_exif
    # print( i.gps_latitude, 'latitude')
    
    exif_dict = piexif.load(i.info["exif"])
    exif_bytes = piexif.dump(exif_dict)
    
    print(exif_bytes, '<=======exif_bytes')
    
    # print(exif, 'exifffffffffffffffffffffffffffff')
    
    # i.thumbnail(output_size) # set the size accepts a tuple with dimensions
    i.save(file_path) # save it to file path we created
    return file_path  #RETURN FILEPATH
  
  
# CREATE HELPER FUNCTION TO DELETE


def upload_photo(request, game_id): # DOUBLE-CHECK GAME ID AND MULTIPLE KWARGS
  photo_file = request.FILES.get('photo-file', None)
  print( type(photo_file), 'photo_file type')
  # print(request.user.id)
  if photo_file:
    # photo_obj = gpsphoto.getGPSData('/Users/Shawn/code/where_dis/photo_file')
    
    # photo_file_copy = dict(photo_file)
    photo_file_copy = copy.deepcopy(photo_file)
    # img_path = save_picture(temp_photo)
    
    
    img = Image.open(photo_file)
    # img = img.load()
    
    # photo_obj = gpsphoto.getGPSData(img_path)
    # print('photo_obj:', photo_obj)
    
    exif_data = img._getexif()
    # gps_dict = {}
    print(exif_data, '<=========exif_data')
    
    if exif_data is not None:
      for key, value in exif_data.items():
        name = TAGS.get(key, key)
        exif_data[name] = exif_data.pop(key)
        # print(name, '<=====name')
      
      if 'GPSInfo' in exif_data:
        for key in exif_data['GPSInfo'].keys():
          name = GPSTAGS.get(key,key)
          exif_data['GPSInfo'][name] = exif_data['GPSInfo'].pop(key)
    
    # print( exif_data['GPSInfo'] )
    print( exif_data, '<============exif_data' )
    print( 'GPS Latitude: ', exif_data['GPSInfo']['GPSLatitude'])
    print( 'GPS Longitude: ', exif_data['GPSInfo']['GPSLongitude'])
    
    
    # print(dir(photo_file))
    # photo_obj = gpsphoto.getGPSData(f'{sys.path.append(os.path.realpath("photo_file"))}')
    # print( os.path.abspath("photo_file") )   # /Users/Shawn/code/where_dis/photo_file
    # print('photo_obj:', photo_obj)
    s3 = boto3.client('s3')
    key = uuid.uuid4().hex[:6] + photo_file_copy.name[photo_file_copy.name.rfind('.'):]
    
    try:
      print('TRY step 1')
      s3.upload_fileobj(photo_file_copy, BUCKET, key)
      print('TRY step 2')
      url = f'{S3_BASE_URL}{BUCKET}/{key}'
      # photo_obj = gpsphoto.getGPSData(f'{url}')
      # print('photo_obj:', photo_obj)
      print(f'TRY step 3 url = {url}')
      photo = Photo(url=url, game_instance_id=game_id, user=request.user) # DOUBLE-CHECK HERE TOO
      print(f'TRY step 4 photo = {photo}')
      photo.save()
      print('TRY step 5')
      # photo_obj = gpsphoto.getGPSData(f'{url}')
      # print('photo_obj:', photo_obj)
    except:
      print('There has been an error uploading to S3')
  return redirect('game_detail', game_id=game_id)






# 34853 in exifdata references a dictionary of coordinates