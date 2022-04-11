from django.urls import path
from.import views
urlpatterns = [
path('v1/health/', views.health, name='health'),
path('v2/patches/', views.patches, name='patches'),
path('v2/players/<int:playerid>/game_exp/', views.game_exp, name = 'game_exp'),
path('v2/players/<int:playerid>/game_objectives/', views.game_objectives, name = 'game_objectives'),
path('v2/players/<int:playerid>/abilities/', views.abilities, name = 'abilities'),
path('v3/matches/<int:matchid>/top_purchases/', views.purchases, name = 'purchases'),
path('', views.index, name = 'index'),
]
