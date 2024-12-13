import consumers
from django.urls import path
from . import views

urlpatterns = [
path('submit-report/', views.submit_report, name='submit_report'),
   path('', views.home, name='home'),
   path('logout/', views.logout, name='logout'),
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
path('profile/<int:id>/', views.profile_detail_favorite, name='profile_detail_favorite'),  # プロフィールページ
path('profile/<uuid:Profile_id>/add_favorite/', views.add_favorite, name='add_favorite'),
    path('profile/<uuid:Profile_id>/remove_favorite/', views.remove_favorite, name='remove_favorite'),
path('profile/edit/<uuid:Profile_id>/', views.profile_edit, name='profile_edit'),
    path('favorites/', views.favorite_list, name='favorite_list'),
path('my_chat_rooms/', views.my_chat_rooms, name='my_chat_rooms'),
   path('chat/create/', views.create_chat_room, name='create_chat_room'),
   path('chat/<uuid:room_id>/', views.chat_room, name='chat_room'),
path('join/<uuid:room_id>/', views.join_chat_room, name='join_chat_room'),
   path('chat/nenu/', views.chat_menu, name='chat_menu'),
path('profile/', views.my_profile, name='my_profile'),  # 自分のプロフィールページ
path('admin/reports/', views.report_list, name='admin_report_list'),
path("admin/manage_users/", views.manage_users, name="manage_users"),
   path("admin/manage_users/kensaku/", views.manage_kensaku, name="manage_kensaku"),
    path("admin/manage_boards/", views.manage_boards, name="manage_boards"),
   path("admin/", views.admin_menu, name='admin_menu'),
   path("admin/manage_boards/kensaku/", views.keiji_kensaku, name="keiji_kensaku")
]
