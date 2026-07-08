from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.db.models import Q
from .models import *

def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user: login(request, user); return redirect('home')
    return render(request, 'registration/login.html')

def register_view(request):
    if request.method == 'POST':
        user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['password'])
        login(request, user); return redirect('home')
    return render(request, 'registration/register.html')

def logout_view(request): logout(request); return redirect('login')

@login_required
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    stories = Story.objects.all().order_by('-created_at')[:8]
    return render(request, 'posts/home.html', {'posts': posts, 'stories': stories})

@login_required
def create_post(request):
    if request.method == 'POST':
        Post.objects.create(user=request.user, content=request.POST['content'], image=request.FILES.get('image'))
    return redirect('home')

@login_required
def profile_view(request, username):
    u = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=u).order_by('-created_at')
    is_friend = u in request.user.profile.friends.all()
    return render(request, 'posts/profile.html', {'profile_user': u, 'posts': posts, 'is_friend': is_friend})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        request.user.profile.bio = request.POST['bio']
        request.user.profile.location = request.POST['location']
        if request.FILES.get('avatar'): request.user.profile.avatar = request.FILES['avatar']
        request.user.profile.save()
        return redirect('profile', username=request.user.username)
    return render(request, 'posts/edit_profile.html')

@login_required
def follow_user(request, username):
    u = get_object_or_404(User, username=username)
    request.user.profile.friends.add(u)
    u.profile.friends.add(request.user)
    Notification.objects.create(user=u, message=f'{request.user.username} est devenu votre ami', link=f'/profile/{request.user.username}/')
    return redirect('profile', username=username)

@login_required
def discover(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'posts/discover.html', {'users': users})

@login_required
def friends_list(request): 
    return render(request, 'posts/friends.html', {'friends': request.user.profile.friends.all()})

@login_required
def send_friend_request(request, username): 
    to_user = User.objects.get(username=username)
    FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    Notification.objects.create(user=to_user, message=f'{request.user.username} vous a envoyé une demande d\'ami', link='/notifications/')
    return redirect('discover')

@login_required
def accept_friend_request(request, request_id): 
    fr = get_object_or_404(FriendRequest, id=request_id)
    fr.to_user.profile.friends.add(fr.from_user)
    fr.from_user.profile.friends.add(fr.to_user)
    fr.delete()
    return redirect('notifications')

@login_required
def decline_friend_request(request, request_id): 
    get_object_or_404(FriendRequest, id=request_id).delete()
    return redirect('notifications')

@login_required
def cancel_friend_request(request, request_id): 
    get_object_or_404(FriendRequest, id=request_id).delete()
    return redirect('discover')

@login_required
def groups_list(request): 
    return render(request, 'posts/groups.html', {'groups': Group.objects.all()})

@login_required
def create_group(request):
    if request.method == 'POST': 
        g = Group.objects.create(name=request.POST['name'], description=request.POST['desc'], creator=request.user)
        g.members.add(request.user)
        return redirect('groups_list')
    return render(request, 'posts/create_group.html')

@login_required
def join_group(request, group_id):
    g = get_object_or_404(Group, id=group_id)
    g.members.add(request.user)
    return redirect('group_chat', group_id=group_id)

@login_required
def group_chat(request, group_id):
    g = get_object_or_404(Group, id=group_id)
    if request.method == 'POST': 
        GroupMessage.objects.create(group=g, sender=request.user, content=request.POST.get('content'))
        return redirect('group_chat', group_id)
    return render(request, 'posts/group_chat.html', {'group': g, 'messages': g.messages.all().order_by('created_at')})

@login_required
def notifications(request): 
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'posts/notifications.html', {'notifications': notifs})

@login_required
def menu(request): 
    return render(request, 'posts/menu.html')

@login_required
def messages(request): 
    chats = User.objects.filter(Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)).distinct()
    return render(request, 'posts/messages.html', {'chats': chats})

@login_required
def chat_view(request, username): 
    other = User.objects.get(username=username)
    msgs = Message.objects.filter(Q(sender=request.user, receiver=other) | Q(sender=other, receiver=request.user)).order_by('created_at')
    Message.objects.filter(sender=other, receiver=request.user, is_read=False).update(is_read=True)
    if request.method == 'POST': 
        Message.objects.create(sender=request.user, receiver=other, content=request.POST['content'])
        return redirect('chat', username)
    return render(request, 'posts/chat.html', {'other': other, 'messages': msgs})

@login_required  
def create_story(request):
    if request.method == 'POST': 
        Story.objects.create(user=request.user, text=request.POST.get('text'), image=request.FILES.get('image'))
        return redirect('home')
    return render(request, 'posts/create_story.html')

@login_required
def view_story(request, story_id): 
    return render(request, 'posts/view_story.html', {'story': get_object_or_404(Story, id=story_id)})

@login_required
def post_detail(request, post_id): 
    return render(request, 'posts/post_detail.html', {'post': get_object_or_404(Post, id=post_id)})

@login_required
def like_post(request, post_id):
    p = get_object_or_404(Post, id=post_id)
    if request.user in p.likes.all(): p.likes.remove(request.user)
    else: 
        p.likes.add(request.user)
        if p.user != request.user:
            Notification.objects.create(user=p.user, message=f'{request.user.username} a aimé votre publication', link=f'/post/{p.id}/')
    return redirect('home')

@login_required
def add_comment(request, post_id):
    if request.method == 'POST': 
        post = get_object_or_404(Post, id=post_id)
        Comment.objects.create(post=post, user=request.user, text=request.POST['text'])
    return redirect('post_detail', post_id)

@login_required
def share_post(request, post_id):
    original = get_object_or_404(Post, id=post_id)
    Post.objects.create(user=request.user, content=f"A partagé: {original.content}", image=original.image)
    Notification.objects.create(user=original.user, message=f'{request.user.username} a partagé votre publication', link=f'/post/{original.id}/')
    return redirect('home')

@login_required
def reels(request):
    reels = Reel.objects.all().order_by('-created_at')
    return render(request, 'posts/reels.html', {'reels': reels})

@login_required
def upload_reel(request):
    if request.method == 'POST':
        Reel.objects.create(user=request.user, video=request.FILES['video'], description=request.POST['desc'])
        return redirect('reels')
    return render(request, 'posts/upload_reel.html')

@login_required
def marketplace(request):
    items = MarketplaceItem.objects.all().order_by('-created_at')
    return render(request, 'posts/marketplace.html', {'items': items})

@login_required
def pages_list(request):
    pages = Page.objects.all()
    return render(request, 'posts/pages.html', {'pages': pages})

@login_required
def page_view(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    return render(request, 'posts/page.html', {'page': page})

@login_required
def reply_comment(request, comment_id):
    parent = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        Comment.objects.create(post=parent.post, user=request.user, text=request.POST['text'], parent=parent)
    return redirect('post_detail', parent.post.id)

@login_required
def save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    SavedPost.objects.get_or_create(user=request.user, post=post)
    return redirect('home')

@login_required
def search(request):
    q = request.GET.get('q')
    users = User.objects.filter(username__icontains=q)
    posts = Post.objects.filter(content__icontains=q)
    return render(request, 'posts/search.html', {'users': users, 'posts': posts, 'q': q})

@login_required
def go_live(request):
    return render(request, 'posts/live.html')
from django.utils import timezone
from datetime import timedelta

@login_required
def home(request):
    Story.objects.filter(created_at__lt=timezone.now()-timedelta(hours=24)).delete() # SUPPRIME STORIES >24H
    posts = Post.objects.all().order_by('-created_at')
    stories = Story.objects.all().order_by('-created_at')[:8]
    return render(request, 'posts/home.html', {'posts': posts, 'stories': stories})
