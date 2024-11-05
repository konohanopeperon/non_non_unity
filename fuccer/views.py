import random
from contextlib import nullcontext

from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone


from fuccer.models import User, BoardModel, Profile

def login(request):
   if request.method == 'POST':
       userid = request.POST.get('userid')
       password = request.POST.get('password')
       if not userid or not password:
           messages.error(request, '空欄があります')
       else:
           try:
               user = User.objects.get(userid=userid)
           except User.DoesNotExist:
               messages.error(request, "ユーザIDもしくはパスワードが違います")
               return render(request, 'login.html')
           if user.password == password:
               request.session['userid'] = user.userid
           else:
               messages.error(request, 'ユーザIDもしくはパスワードが違います')
               return render(request, 'login.html')
           boards = BoardModel.objects.all()
           return render(request, 'board/board_list.html', {'boards': boards})
       return render(request, 'login.html')
   return render(request, 'login.html')

def board_list(request):
    # BoardModelテーブルの全レコードを取得
    boards = BoardModel.objects.all()
    # HTMLテンプレートにデータを渡す
    return render(request, 'board/board_list.html', {'boards': boards})


def logout(request):
   logout(request)
   return render(request, 'login.html')


def create_board(request):
    if request.method == "POST":
        title = request.POST.get('title')
        participants = request.POST.get('participants')
        description = request.POST.get('description')
        creator_id = request.session.get('userid')  # 現在ログイン中のユーザーを取得

        if not title or not description:
            messages.error(request, 'タイトルまたは説明が空です。')
            return render(request, 'board/board_create.html')

        # BoardModelのインスタンスを作成して保存
        board = BoardModel(
            title=title,
            participants=participants,
            description=description,
            creator_id=creator_id,
            created_at=timezone.now()
        )
        board.save()

        messages.success(request, 'ボードが作成されました。')
        boards = BoardModel.objects.all()
        return render(request, 'board/board_list.html', {'boards':boards})  # 適切なURL名に変更

    return render(request, 'board/board_create.html')

def board_description(request):
    if request.method == "GET":
        board = BoardModel.objects.get(board_id=request.GET)
        return render(request, 'board/board_description.html', {'board':board})


def create_profile(request):
   if request.method == 'POST':
       user = request.session.get('userid')
       nickname = request.POST.get('nickname')
       sex = request.POST.get('sex')
       bio = request.POST.get('bio')
       hobby = request.POST.get('hobby')

       if not nickname:
           nickname = None
       if not sex:
           sex = None
       if not bio:
           bio = None
       if not hobby:
           hobby = None

       profile = Profile(
           user=user,
           nickname=nickname,
           sex=sex,
           bio=bio,
           hobby=hobby,
       )
       profile.save()
       return render(request, 'profile/profile_create.html')

   return render(request, 'profile/profile_create.html')

