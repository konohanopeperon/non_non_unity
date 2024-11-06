from django.urls import path
from . import views


urlpatterns = [
   path('', views.login, name='login'),
   path('board/create', views.create_board, name='board_create'),
   path('boards/', views.board_list, name='board_list'),
   path('board/description/<uuid:board_id>/', views.board_description, name='board_description'),
   path('board/board_kensaku/', views.board_kensaku, name='board_kensaku'),
   path('board/board_sanka/<uuid:board_id>/', views.board_sanka, name='board_sanka'),



]
