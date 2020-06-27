from django.urls import path
from django.conf.urls import url                                                                                                                              
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('games/', views.GameList.as_view(), name='game_list'),
    path('games/create/', views.GameCreate.as_view(), name='game_create'),
    path('games/<int:game_id>/ref_photo_form', views.game_ref_photo_form, name='game_ref_photo_form'),
    path('games/<int:game_id>/upload_ref_photo_url', views.upload_ref_photo_function, name='upload_ref_photo_nickname'),
    path('games/<int:game_id>/', views.game_detail, name='game_detail'),
    path('games/<int:game_id>/upload_photo/', views.upload_photo, name='upload_photo'),
    path('games/<int:game_id>/game_map/', views.game_map, name='game_map'),
    path('games/<int:pk>/game_delete/', views.GameDelete.as_view(), name='game_delete'),
]