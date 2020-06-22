from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('games/', views.GameList.as_view(), name='game_list'),
    path('games/<int:game_id>/', views.game_detail, name='game_detail'),
]