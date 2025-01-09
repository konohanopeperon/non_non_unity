from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from fuccer.models import BoardModel, Profile, BoardParticipant, Tag, UserFavorite, ChatRoom, Message, Report
from django.contrib.auth import get_user_model, logout
from django.shortcuts import render, redirect
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
User = get_user_model()

# 管理者チェック
def admin_check(user):
    return user.is_staff  # 管理者のみアクセス可能

@user_passes_test(admin_check)
def admin_dashboard(request):
    # 統計情報を収集
    user_count = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    board_count = BoardModel.objects.count()
    chat_count = ChatRoom.objects.count()
    message_count = Message.objects.count()
    favorite_count = UserFavorite.objects.count()

    context = {
        'user_count': user_count,
        'active_users': active_users,
        'board_count': board_count,
        'chat_count': chat_count,
        'message_count': message_count,
        'favorite_count': favorite_count,
    }
    return render(request, 'admin/admin.html', context)

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
        # ログインユーザがスーパーユーザかどうかをチェック
    if request.user.is_superuser:
        # スーパーユーザなら管理者用の処理
        return render(request, 'admin/admin.html')
    else:
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return render(request, 'profile/profile_create.html')
        boards = BoardModel.objects.filter(is_active=True).exclude(creator=request.user)
        return render(request, 'board/board_list.html', {'boards': boards, 'profile':profile})


@login_required
def test_page(request):
    # ユーザ名取得
    print(f"Current user: {request.user.username}")
    return render(request, 'test_page.html')

def board_list(request):
    # BoardModelテーブルの全レコードを取得
    boards = BoardModel.objects.filter(is_active=True).exclude(creator=request.user)
    # HTMLテンプレートにデータを渡す
    return render(request, 'board/board_list.html', {'boards': boards})


def user_logout(request):
   logout(request)
   return render(request, 'registration/login.html')

def board_kensaku(request):
    query = request.GET.get('query')
    k = request.GET.get('k')

    if not query:
        boards = BoardModel.objects.filter(is_active=True).exclude(creator=request.user)
        return render(request, 'board/board_list.html', {'boards': boards})

    if not k:
        messages.error(request, 'タイトルかタグか指定してください')
        boards = BoardModel.objects.filter(is_active=True).exclude(creator=request.user)  # リストが空の場合にも全て表示
        return render(request, 'board/board_list.html', {'boards': boards})

    try:
        k = int(k)
    except ValueError:
        messages.error(request, '無効な検索オプションです')
        boards = BoardModel.objects.filter(is_active=True).exclude(creator=request.user)
        return render(request, 'board/board_list.html', {'boards': boards})

    if k == 1:
        boards = BoardModel.objects.filter(is_active=1,title__icontains=query)
    elif k == 2:
        boards = BoardModel.objects.filter(is_active=1,tags__name__icontains=query)  # タグがManyToManyの場合
    else:
        messages.error(request, '無効な検索オプションです')
        boards = BoardModel.objects.all()

    return render(request, 'board/board_list.html', {'boards': boards})


@login_required
def create_board(request):
    if request.method == "POST":
        title = request.POST.get('title')
        participant_limit = request.POST.get('participant_limit', 0)
        description = request.POST.get('description')
        scheduled_date = request.POST.get('scheduled_date')
        tags_input = request.POST.get('tags')
        creator = request.user

        if not title or not description:
            messages.error(request, 'タイトルまたは説明が空です。')
            return render(request, 'board/board_create.html')

        try:
            participant_limit = int(participant_limit)
            if participant_limit <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, '参加上限は正の整数で指定してください。')
            return render(request, 'board/board_create.html')

        board = BoardModel.objects.create(
            title=title,
            participant_limit=participant_limit,
            description=description,
            creator=creator,
            scheduled_date=scheduled_date,
        )

        if tags_input:
            tag_names = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                board.tags.add(tag)

        messages.success(request, 'ボードが作成されました。')
        return redirect('board_list')

    return render(request, 'board/board_create.html')

def board_description(request, board_id):
        board = BoardModel.objects.get(board_id=board_id)
        return render(request, 'board/board_description.html', {'board':board})


def my_board_description(request, board_id):
    board = BoardModel.objects.get(board_id=board_id)
    return render(request, 'board/my_board_description.html', {'board': board})


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

    boards = BoardModel.objects.filter(is_active=True).exclude(creator=request.user)
    return render(request, 'board/board_list.html', {'boards': boards, 'profile': profile})

@login_required
def edit_board(request, board_id):
    board = get_object_or_404(BoardModel, board_id=board_id, creator=request.user)

    if request.method == 'POST':
        # POSTデータを受け取ってフォームデータを反映
        board.title = request.POST.get('title')
        board.description = request.POST.get('description')
        board.participant_limit = request.POST.get('participant_limit')
        board.scheduled_date = request.POST.get('scheduled_date') or None
        board.save()
        return redirect('my_keijiban')  # 保存後詳細ページへ

    return render(request, 'board/board_edit.html', {'board': board})

@login_required
def profile_list(request):
    query = request.GET.get('query', '')

    # ログインユーザー以外をフィルタ
    profiles = Profile.objects.exclude(user=request.user)


    # 検索条件がある場合、さらにフィルタ
    if query:
        profiles = profiles.filter(nickname__icontains=query)

    return render(request, 'profile/profile_list.html', {'profiles': profiles})
@login_required
def profile_detail(request, Profile_id):
    profile = get_object_or_404(Profile, Profile_id=Profile_id)

    # 現在のユーザーが登録したお気に入りリスト
    user_favorites = request.user.favorites.values_list('favorite_user_id',
                                                        flat=True) if request.user.is_authenticated else []

    return render(request, 'profile/profile_detail.html', {
        'profile': profile,
        'user_favorites': user_favorites,
    })

@login_required
def profile_detail_favorite(request, id):
    profile = get_object_or_404(Profile, user_id=id)  # Profile_idで検索
    user = profile.user  # Profileから関連するUserを取得
    return render(request, 'profile/profile_detail_favorite.html', {'user': user, 'profile': profile})

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
        boards = BoardModel.objects.filter(is_active=True).exclude(creator=request.user)
        return render(request, 'board/board_list.html', {'boards': boards, 'profile': profile})

    return render(request, 'profile/profile_create.html')


@login_required
def profile_edit(request, Profile_id):
    # Profileオブジェクトを取得
    profile = get_object_or_404(Profile, Profile_id=Profile_id)

    if request.method == 'POST':
        # フォームデータを取得
        nickname = request.POST.get('nickname', profile.nickname)
        sex = request.POST.get('sex', profile.sex)
        bio = request.POST.get('bio', profile.bio)
        hobby = request.POST.get('hobby', profile.hobby)

        # オブジェクトを更新
        profile.nickname = nickname
        profile.sex = sex
        profile.bio = bio
        profile.hobby = hobby
        profile.save()

        return redirect('my_profile')  # 適切なリダイレクト先を設定

    return render(request, 'profile/profile_edit.html', {'profile': profile})
@login_required
def add_favorite(request, Profile_id):
    user = request.user
    favorite_profile = get_object_or_404(Profile, Profile_id=Profile_id)

    if user.id == favorite_profile.user.id:
        messages.error(request, "自分自身をお気に入りに登録することはできません。")
        return redirect('profile_detail', Profile_id=Profile_id)

    favorite_user = favorite_profile.user
    favorite, created = UserFavorite.objects.get_or_create(
        user=user,
        favorite_user=favorite_user,
    )

    if created:
        messages.success(request, f"{favorite_profile.nickname}をお気に入りに登録しました！")
    else:
        messages.info(request, f"{favorite_profile.nickname}は既にお気に入りに登録されています。")

    return redirect('profile_detail', Profile_id=Profile_id)


@login_required
def remove_favorite(request, Profile_id):
    user = request.user
    favorite_profile = get_object_or_404(Profile, Profile_id=Profile_id)

    favorite_user = favorite_profile.user
    favorite = UserFavorite.objects.filter(user=user, favorite_user=favorite_user).first()

    if favorite:
        favorite.delete()
        messages.success(request, f"{favorite_profile.nickname}をお気に入りから解除しました。")
    else:
        messages.info(request, f"{favorite_profile.nickname}はお気に入りに登録されていません。")

    return redirect('profile_detail', Profile_id=Profile_id)


@login_required
def favorite_list(request):
    favorites = UserFavorite.objects.filter(user=request.user).select_related('favorite_user')
    return render(request, 'profile/favorite_list.html', {'favorites': favorites})


def join_chat_room(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(ChatRoom, room_id=room_id)
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        if user not in room.participants.all():
            room.participants.add(user)
        return redirect('chat_room', room_id=room_id)


def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, room_id=room_id)
    messages = Message.objects.filter(room=room).order_by('timestamp')
    available_users = User.objects.exclude(id__in=room.participants.values_list('id', flat=True)).filter(is_superuser=False)
    if request.method == 'POST' and 'content' in request.POST:
        content = request.POST.get('content')
        Message.objects.create(room=room, sender=request.user, content=content)
        return redirect('chat_room', room_id=room_id)
    return render(request, 'chat/chat_room.html', {'room': room, 'messages': messages, 'available_users': available_users})

def create_chat_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('name')
        if room_name:
            # チャットルームの作成
            room = ChatRoom.objects.create(name=room_name)
            room.participants.add(request.user)  # ルーム作成者が自動で参加
            return redirect('chat_room', room_id=room.room_id)
    return render(request, 'chat/create_chat_room.html')

def my_chat_rooms(request):
    # ログインユーザーが参加しているチャットルームを取得
    chat_rooms = ChatRoom.objects.filter(participants=request.user)
    if not chat_rooms:
        return redirect('create_chat_room')
    return render(request, 'chat/my_chat_rooms.html', {'chat_rooms': chat_rooms})

def chat_menu(request):
    return render(request,'chat/chat_menu.html')

@login_required
def my_profile(request):
    # ログイン中のユーザーに関連するプロフィールを取得
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'profile/my_profile.html', {'profile': profile})

@login_required
def submit_report(request):
    if request.method == 'POST':
        reported_user_id = request.POST.get('reported_user')
        reported_board_id = request.POST.get('reported_board')
        report_reason = request.POST.get('report_reason')
        details = request.POST.get('details')

        if not report_reason:
            messages.error(request, "通報理由を選択してください。")
            return redirect('submit_report')

        report = Report(
            reporter=request.user,
            report_reason=report_reason,
            details=details
        )

        # 通報対象のユーザーを設定
        if reported_user_id:
            try:
                report.reported_user = User.objects.get(id=reported_user_id)
            except User.DoesNotExist:
                messages.error(request, "選択されたユーザーが見つかりません。")
                return redirect('submit_report')

        # 通報対象の掲示板を設定
        if reported_board_id:
            try:
                report.reported_board = BoardModel.objects.get(board_id=reported_board_id)
            except BoardModel.DoesNotExist:
                messages.error(request, "選択された掲示板が見つかりません。")
                return redirect('submit_report')

        report.save()
        messages.success(request, "通報が送信されました。")
        return redirect('board_list')

    # ユーザーと掲示板リストをテンプレートに渡す
    users = User.objects.all()
    boards = BoardModel.objects.all()
    return render(request, 'report/submit_report.html', {'users': users, 'boards': boards})


@login_required
def submit_report(request):
    if request.method == 'POST':
        reported_user_id = request.POST.get('reported_user_id')
        report_type = request.POST.get('report_type')
        description = request.POST.get('description', '')

        reported_user = get_object_or_404(User, id=reported_user_id)

        # 通報の作成
        report = Report.objects.create(
            reporter=request.user,
            reported_user=reported_user,
            report_type=report_type,
            description=description
        )

        messages.success(request, '通報が送信されました。管理者が確認します。')
        return redirect('home')

    # 通報対象ユーザーを選択するためのフォーム表示
    profiles = Profile.objects.exclude(user=request.user)  # 自分以外のプロフィールをリスト
    return render(request, 'report/submit_report.html', {'profiles': profiles})

def report_list(request):
    reports = Report.objects.all()
    return render(request, 'admin/report_list.html', {'reports': reports})

def manage_users(request):
    users = User.objects.filter(is_superuser=0)
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")
        user = User.objects.get(id=user_id)
        if action == "deactivate":
            user.is_active = False
            profile = Profile.objects.get(user=user)
            profile.is_active = False
            profile.save()
            messages.success(request, f"ユーザ {user.email} を利用停止にしました。")
        elif action == "activate":
            user.is_active = True
            profile = Profile.objects.get(user=user)
            profile.is_active = True
            profile.save()
            messages.success(request, f"ユーザ {user.email} を利用可能にしました。")
        user.save()
        return redirect("manage_users")

    return render(request, "admin/manage_users.html", {"users": users})

def manage_boards(request):
    boards = BoardModel.objects.all()
    if request.method == "POST":
        board_id = request.POST.get("board_id")
        action = request.POST.get("action")
        board = BoardModel.objects.get(board_id=board_id)
        if action == "deactivate":
            board.is_active = False
            messages.success(request, f"掲示板 {board.title} を非表示にしました。")
        elif action == "activate":
            board.is_active = True
            messages.success(request, f"掲示板 {board.title} を表示可能にしました。")
        board.save()
        return redirect("manage_boards")

    return render(request, "admin/manage_boards.html", {"boards": boards})

def my_keijiban(request):
    boards = BoardModel.objects.filter(creator=request.user)
    return render(request,'board/my_boards.html', {"boards":boards})

def admin_menu(request):
    return render(request, 'admin/admin.html')

def manage_kensaku(request):
    query = request.GET.get('search', '')  # 検索クエリを取得
    if query:
        # last_nameまたはfirst_nameに部分一致するユーザを検索
        users = User.objects.filter(Q(last_name__icontains=query) | Q(first_name__icontains=query))
    else:
        users = User.objects.all()  # 検索がなければ全て表示
    return render(request, 'admin/manage_users.html', {'users': users, 'query': query})


def keiji_kensaku(request):
    query = request.GET.get('search', '')  # 検索クエリを取得
    if query:
        # last_nameまたはfirst_nameに部分一致するユーザを検索
        boards = BoardModel.objects.filter(title__icontains=query)
    else:
        boards = BoardModel.objects.all()  # 検索がなければ全て表示
    return render(request, 'admin/manage_boards.html', {'boards': boards, 'query': query})

def create_google_meet_event(request):
    social = request.user.social_auth.get(provider='google-oauth2')
    creds = Credentials(
        token=social.extra_data['access_token'],
        refresh_token=social.extra_data.get('refresh_token'),
        client_id='104966677750-o7nbpejt3mckq6omegkk1llasp1llj67.apps.googleusercontent.com',
        client_secret='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',
        token_uri='https://oauth2.googleapis.com/token',
    )

    service = build('calendar', 'v3', credentials=creds)
    event = {
        'summary': 'Google Meet Meeting',
        'start': {
            'dateTime': (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).isoformat() + 'Z',
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (datetime.datetime.utcnow() + datetime.timedelta(minutes=40)).isoformat() + 'Z',
            'timeZone': 'UTC',
        },
        'conferenceData': {
            'createRequest': {
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                'requestId': 'sample123',
            }
        },
    }

    try:
        created_event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        # Google Meet URLを取得
        meet_url = created_event['conferenceData']['entryPoints'][0]['uri']

        # リンクをテンプレートに渡す
        return render(request, 'meet_created.html', {'meet_url': meet_url})

    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})
