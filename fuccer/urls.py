from django.urls import path
from . import views


urlpatterns = [
   path('', views.login, name='login'),
   path('board/create', views.create_board, name='board_create'),
   path('boards/', views.board_list, name='board_list'),
   path('board/description/<int:board_id>/', views.board_description, name='board_description'),



]
