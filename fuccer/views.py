import random
from contextlib import nullcontext

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from fuccer.models import User, BoardModel, Profile, BoardParticipant

@login_required
def home(request):
    # ユーザ名取得
    print(f"Current user: {request.user.username}")
    # 全ユーザ情報取得
    for attr in dir(request.user):
        try:
            print(f"{attr}: {getattr(request.user, attr)}")
        except AttributeError:
            print(f"{attr}: [アクセス不可]")
    # HTML
    return render(request, 'home.html')


@login_required
def test_page(request):
    # ユーザ名取得
    print(f"Current user: {request.user.username}")
    return render(request, 'test_page.html')

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
               return render(request, 'registration/login.html')
           if user.password == password:
               request.session['userid'] = user.userid
           else:
               messages.error(request, 'ユーザIDもしくはパスワードが違います')
               return render(request, 'registration/login.html')
           boards = BoardModel.objects.all()
           return render(request, 'board/board_list.html', {'boards': boards})
       return render(request, 'registration/login.html')
   return render(request, 'registration/login.html')

def board_list(request):
    # BoardModelテーブルの全レコードを取得
    boards = BoardModel.objects.all()
    # HTMLテンプレートにデータを渡す
    return render(request, 'board/board_list.html', {'boards': boards})


def logout(request):
   logout(request)
   return render(request, 'registration/login.html')

def board_kensaku(request):
    query = request.GET.get('query')
    if query:
        board = BoardModel.objects.objects.filter

def create_board(request):
    if request.method == "POST":
        title = request.POST.get('title')
        participant_limit = request.POST.get('participant_limit')
        description = request.POST.get('description')
        creator_id = request.session.get('userid')  # 現在ログイン中のユーザーを取得

        if not title or not description:
            messages.error(request, 'タイトルまたは説明が空です。')
            return render(request, 'board/board_create.html')

        # BoardModelのインスタンスを作成して保存
        board = BoardModel(
            title=title,
            participant_limit=participant_limit,
            description=description,
            creator_id=creator_id,
            created_at=timezone.now(),
        )
        board.save()

        messages.success(request, 'ボードが作成されました。')
        boards = BoardModel.objects.all()
        return render(request, 'board/board_list.html', {'boards':boards})  # 適切なURL名に変更

    return render(request, 'board/board_create.html')

def board_description(request, board_id):
        board = BoardModel.objects.get(board_id=board_id)
        return render(request, 'board/board_description.html', {'board':board})

def board_sanka(request, board_id):
    board = get_object_or_404(BoardModel, board_id=board_id)
    user = User.objects.get(userid=request.session.get('userid'))

    # 既に参加しているか確認
    if BoardParticipant.objects.filter(board=board, user=user).exists():
        return HttpResponse("You have already joined this board.")

    # 参加上限のチェック
    if board.participants >= board.participant_limit:
        return HttpResponse("This board has reached the participant limit.")

    # 参加登録処理
    BoardParticipant.objects.create(board=board, user=user)
    board.participants += 1
    board.save()

    boards = BoardModel.objects.all()
    return render(request, 'board/board_list.html', {'boards': boards})


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

