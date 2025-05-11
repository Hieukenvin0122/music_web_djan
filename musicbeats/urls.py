from django.urls import path
from . import views

urlpatterns = [
    path('songs/', views.songs, name='songs'),
    path('songs/<int:id>', views.songpost, name ='songpost'),
    path('login', views.login, name ='login'),
    path('signup', views.signup, name ='signup'),
    path('logout_user', views.logout_user, name = 'logout_user'),
    path('watchlater', views.watchlater, name = 'watchlater'),
    path('watchlater/remove/<int:song_id>/', views.remove_watchlater, name='remove_watchlater'),
    path('history', views.history, name = 'history'),
    path('c/<str:channel>', views.channel, name = 'channel'),
    path('upload', views.upload, name = 'upload'),
    path('search', views.search, name = 'search'),
    path('favourite', views.favourite, name='favourite'),
    path('favourite/remove/<int:song_id>/', views.remove_favourite, name='remove_favourite'),
    path('songs/<int:song_id>/info/', views.song_info, name='song_info'),
]