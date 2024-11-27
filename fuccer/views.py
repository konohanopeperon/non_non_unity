from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from fuccer.models import User, BoardModel, Profile, BoardParticipant, Tag


@login_required
def home(request):
    # ユーザ名取得
    print(f"Current user: {request.user.username}")
    request.session['id'] = f'{request.user.id}'
    # 全ユーザ情報取得
    for attr in dir(request.user):
        try:
            print(f"{attr}: {getattr(request.user, attr)}")
        except AttributeError:
            print(f"{attr}: [アクセス不可]")

    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return render(request, 'profile/profile_create.html')
    boards = BoardModel.objects.all()
    return render(request, 'board/board_list.html', {'boards': boards, 'profile':profile})


@login_required
def test_page(request):
    # ユーザ名取得
    print(f"Current user: {request.user.username}")
    return render(request, 'test_page.html')

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
    k = request.GET.get('k')

    if not query:
        boards = BoardModel.objects.all()
        return render(request, 'board/board_list.html', {'boards': boards})

    if not k:
        messages.error(request, 'タイトルかタグか指定してください')
        boards = BoardModel.objects.all()  # リストが空の場合にも全て表示
        return render(request, 'board/board_list.html', {'boards': boards})

    try:
        k = int(k)
    except ValueError:
        messages.error(request, '無効な検索オプションです')
        boards = BoardModel.objects.all()
        return render(request, 'board/board_list.html', {'boards': boards})

    if k == 1:
        boards = BoardModel.objects.filter(title__icontains=query)
    elif k == 2:
        boards = BoardModel.objects.filter(tags__name__icontains=query)  # タグがManyToManyの場合
    else:
        messages.error(request, '無効な検索オプションです')
        boards = BoardModel.objects.all()

    return render(request, 'board/board_list.html', {'boards': boards})
    

def create_board(request):
    if request.method == "POST":
        title = request.POST.get('title')
        participant_limit = request.POST.get('participant_limit')
        description = request.POST.get('description')
        tags_input = request.POST.get('tags')  # ハッシュタグフィールドを取得
        creator = request.user

        # 必須フィールドのバリデーション
        if not title or not description:
            messages.error(request, 'タイトルまたは説明が空です。')
            return render(request, 'board/board_create.html')

        # BoardModelのインスタンスを作成して保存
        board = BoardModel(
            title=title,
            participant_limit=participant_limit,
            description=description,
            creator=creator,
            created_at=timezone.now(),
        )
        board.save()

        # ハッシュタグの処理
        if tags_input:
            tag_names = [tag.strip() for tag in tags_input.split(',')]
            for name in tag_names:
                if name:  # 空文字を無視
                    tag, created = Tag.objects.get_or_create(name=name)
                    board.tags.add(tag)

        messages.success(request, 'ボードが作成されました。')
        boards = BoardModel.objects.all()
        return render(request, 'board/board_list.html', {'boards': boards})  # 適切なテンプレート名に変更

    return render(request, 'board/board_create.html')

def board_description(request, board_id):
        board = BoardModel.objects.get(board_id=board_id)
        return render(request, 'board/board_description.html', {'board':board})


def board_sanka(request, board_id):
    board = get_object_or_404(BoardModel, board_id=board_id)

    user = request.user

    # ユーザーに関連するプロフィールがあるかを確認
    profile = Profile.objects.filter(user=user).first()
    if not profile:
        return HttpResponse("参加するには自分のプロフィールを作成する必要があります")

    # 既に参加しているか確認
    if BoardParticipant.objects.filter(board=board, user=user).exists():
        return HttpResponse("すでにこの掲示板に参加しています")

    # 参加上限のチェック
    if board.participants >= board.participant_limit:
        return HttpResponse("この掲示板はすでに参加可能人数に達しています")

    # 参加登録処理
    BoardParticipant.objects.create(board=board, user=user)
    board.participants += 1
    board.save()

    boards = BoardModel.objects.all()
    return render(request, 'board/board_list.html', {'boards': boards, 'profile': profile})


@login_required
def profile_list(request):
    query = request.GET.get('query', '')

    if query:
        profiles = Profile.objects.filter(nickname__icontains=query)
    else:
        profiles = Profile.objects.all()

    return render(request, 'profile/profile_list.html', {'profiles': profiles})

@login_required
def profile_detail(request, Profile_id):
    profile = get_object_or_404(Profile, Profile_id=Profile_id)
    return render(request, 'profile/profile_detail.html', {'profile': profile})

@login_required
def create_profile(request):
    if request.method == 'POST':
        user = request.user  # Google認証でログインしているユーザーを取得
        nickname = request.POST.get('nickname', None)
        sex = request.POST.get('sex', None)
        bio = request.POST.get('bio', None)
        hobby = request.POST.get('hobby', None)

        # プロファイルの作成
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'nickname': nickname,
                'sex': sex,
                'bio': bio,
                'hobby': hobby
            }
        )

        # 既にプロファイルがある場合は、更新
        if not created:
            profile.nickname = nickname or profile.nickname
            profile.sex = sex or profile.sex
            profile.bio = bio or profile.bio
            profile.hobby = hobby or profile.hobby
            profile.save()

        profile = Profile.objects.get(user=request.user)
        boards = BoardModel.objects.all()
        return render(request, 'board/board_list.html', {'boards': boards, 'profile': profile})

    return render(request, 'profile/profile_create.html')


@login_required
def edit_profile(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        profile.nickname = request.POST.get('nickname', profile.nickname)
        profile.sex = request.POST.get('sex', profile.sex)
        profile.bio = request.POST.get('bio', profile.bio)
        profile.hobby = request.POST.get('hobby', profile.hobby)
        profile.save()

        return render(request, 'profile/profile_edit.html', {'profile': profile})

    return render(request, 'profile/profile_edit.html', {'profile': profile})

