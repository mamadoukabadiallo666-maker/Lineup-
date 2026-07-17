from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import *

def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user: login(request, user); return redirect('home')
    return render(request, 'registration/login.html')

def logout_view(request): 
    logout(request)
    return redirect('login')

@login_required
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    stories = Story.objects.filter(expires_at__gt=timezone.now()).order_by('-created_at')[:8]
    return render(request, 'posts/home.html', {'posts': posts, 'stories': stories})

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user).order_by('-created_at')
    return render(request, 'profile.html', {'profile_user': user, 'posts': posts})

@login_required
def profile_redirect(request): 
    return redirect('profile', username=request.user.username)

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all(): post.likes.remove(request.user)
    else: post.likes.add(request.user)
    return redirect('home')

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        Comment.objects.create(post=post, user=request.user, content=request.POST['content'])
    return redirect('home')

# PAGES SIMPLES
@login_required
def friends(request): return render(request, 'friends.html')
@login_required  
def groups(request): return render(request, 'groups.html')
@login_required
def messages(request): return render(request, 'messages.html')
@login_required
def notifications(request): return render(request, 'notifications.html')
@login_required
def reels(request): return render(request, 'reels.html')
@login_required
def marketplace(request): return render(request, 'marketplace.html')
@login_required
def wallet_view(request): return render(request, 'wallet.html')
@login_required
def live(request): return render(request, 'live.html')

# FONCTIONS Bouchon pour éviter les erreurs
@login_required
def post_detail(request, post_id): return redirect('home')
@login_required
def share_post(request, post_id): return redirect('home')
@login_required
def save_post(request, post_id): return redirect('home')
@login_required
def send_friend_request(request, username): return redirect('friends')
@login_required
def accept_friend_request(request, request_id): return redirect('friends')
@login_required
def decline_friend_request(request, request_id): return redirect('friends')
@login_required
def cancel_friend_request(request, request_id): return redirect('friends')
@login_required
def create_group(request): return redirect('groups')
@login_required
def pages_list(request): return render(request, 'pages.html')
@login_required
def page_view(request, page_id): return render(request, 'page.html')
@login_required
def search(request): return render(request, 'search.html')
@login_required
def go_live(request): return render(request, 'live.html')
@login_required
def watch_live(request, username): return render(request, 'live.html', {'streamer': username})
@login_required
def stop_live(request): return redirect('home')
@login_required
def settings_view(request): return render(request, 'settings.html')
@login_required
def withdraw_view(request): return render(request, 'withdraw.html')
@login_required
def upload_reel(request): return redirect('reels')
@login_required
def reply_comment(request, comment_id): return redirect('home')
@login_required
def create_redirect(request): return redirect('home')
@login_required
def videos_redirect(request): return render(request, 'videos.html')
@login_required
def discover(request): return render(request, 'discover.html')
@login_required
def chat_view(request, username): return render(request, 'chat.html', {'username': username})
@login_required
def menu(request): return render(request, 'menu.html')

@login_required
def create_post(request): return redirect('home')
@login_required
def create_story(request): return redirect('home')
def create_post(request):
    if request.method == 'POST':
        # Ici on va gérer l'upload plus tard
        return redirect('home')
    return render(request, 'posts/create_post.html')

def create_post(request):
    if request.method == 'POST':
        return redirect('home')
    return render(request, 'posts/create_post.html')
def create_story(request):
def story_view(request, story_id):
def create_story(request):
def story_view(request, story_id):
