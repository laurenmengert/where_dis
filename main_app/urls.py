from django.urls import path
from django.conf.urls import url                                                                                                                              
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('games/', views.GameList.as_view(), name='game_list'),
    path('games/<int:game_id>/', views.game_detail, name='game_detail'),
    # path('games/<int:game_id>/game_map', views.game_map, name='game_map'),
    url(r'map/', views.game_map, name="game_map"),
]