from django.urls import path
from . import views


urlpatterns = [
   path('', views.home, name='home'),
   path('home/', views.home, name='home'),
   path('test_page', views.test_page, name='test_page'),
   path('board/create', views.create_board, name='board_create'),
   path('boards/', views.board_list, name='board_list'),
   path('board/description/<uuid:board_id>/', views.board_description, name='board_description'),
   path('board/board_kensaku/', views.board_kensaku, name='board_kensaku'),
   path('board/board_sanka/<uuid:board_id>/', views.board_sanka, name='board_sanka'),
   path('profile/create/', views.create_profile, name='profile_create'),
   path('profile/list/', views.profile_list, name='profile_list'),
path('profiles/<uuid:Profile_id>/', views.profile_detail, name='profile_detail'),



]
