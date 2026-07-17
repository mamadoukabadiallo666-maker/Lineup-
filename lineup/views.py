from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from posts.models import Post, Story, User, Comment, FriendRequest, Notification, Message, Profile, Transaction

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
    return render(request, "posts/login.html")

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "posts/register.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

def home(request):
    posts = Post.objects.all().order_by("-created_at")
    stories = Story.objects.filter(expires_at__gt=timezone.now()).order_by("-created_at")[:10]
    return render(request, "posts/home.html", {"posts": posts, "stories": stories})

@login_required
def story_view(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    return render(request, "posts/story_view.html", {"story": story})

@login_required
def create_story(request):
    if request.method == "POST":
        image = request.FILES.get("image")
        if image:
            expires = timezone.now() + timedelta(hours=24)
            Story.objects.create(user=request.user, image=image, expires_at=expires)
            return redirect("home")
    return render(request, "posts/create_story.html")

@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST.get("content")
        image = request.FILES.get("image")
        if content or image:
            Post.objects.create(user=request.user, content=content, image=image)
            return redirect("home")
    return render(request, "posts/create_post.html")

@login_required
def friends(request):
    friends = User.objects.filter(
        Q(sent_requests__to_user=request.user, sent_requests__status="accepted") |
        Q(received_requests__from_user=request.user, received_requests__status="accepted")
    ).distinct()
    requests_received = FriendRequest.objects.filter(to_user=request.user, status="pending")
    requests_sent = FriendRequest.objects.filter(from_user=request.user, status="pending")
    all_users = User.objects.exclude(id=request.user.id)
    suggestions = []
    for u in all_users:
        if u not in friends and u not in [r.to_user for r in requests_sent]:
            suggestions.append(u)
    suggestions = suggestions[:20]
    return render(request, "posts/friends.html", {"friends": friends, "suggestions": suggestions, "requests": requests_received, "sent": requests_sent})

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    req, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    if created:
        Notification.objects.create(to_user=to_user, from_user=request.user, notification_type="friend")
    return redirect("friends")

@login_required
def cancel_friend_request(request, user_id):
    FriendRequest.objects.filter(from_user=request.user, to_user_id=user_id).delete()
    return redirect("friends")

@login_required
def accept_friend_request(request, req_id):
    req = get_object_or_404(FriendRequest, id=req_id, to_user=request.user)
    req.status = "accepted"
    req.save()
    Notification.objects.create(to_user=req.from_user, from_user=request.user, notification_type="accept")
    return redirect("friends")

@login_required
def decline_friend_request(request, req_id):
    req = get_object_or_404(FriendRequest, id=req_id, to_user=request.user)
    req.delete()
    return redirect("friends")

@login_required
def messages(request):
    friends = User.objects.filter(
        Q(sent_requests__to_user=request.user, sent_requests__status="accepted") |
        Q(received_requests__from_user=request.user, received_requests__status="accepted")
    ).distinct()
    others = User.objects.filter(
        Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
    ).distinct().exclude(id=request.user.id).exclude(id__in=[u.id for u in friends])[:20]
    return render(request, "posts/messages.html", {"friends": friends, "others": others})

@login_required
def chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user)
    ).order_by("created_at")
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(sender=request.user, receiver=other_user, content=content)
            return redirect("chat", user_id=user_id)
    return render(request, "posts/chat.html", {"other_user": other_user, "messages": messages})

@login_required
def videos_redirect(request):
    videos = Post.objects.filter(user=request.user).exclude(image="").filter(image__endswith=".mp4").order_by("-created_at")
    return render(request, "posts/videos.html", {"videos": videos})

@login_required
def all_videos(request):
    videos = Post.objects.exclude(image="").filter(image__endswith=".mp4").order_by("-created_at")
    return render(request, "posts/videos.html", {"videos": videos})

@login_required
def notifications(request):
    notifs = Notification.objects.filter(to_user=request.user).order_by("-created_at")[:20]
    Notification.objects.filter(to_user=request.user, is_read=False).update(is_read=True)
    return render(request, "posts/notifications.html", {"notifications": notifs})

@login_required
def profile_redirect(request):
    user_id = request.GET.get("user")
    if user_id:
        profile_user = get_object_or_404(User, id=user_id)
    else:
        profile_user = request.user
    profile = Profile.objects.get_or_create(user=profile_user)[0]
    posts = Post.objects.filter(user=profile_user).order_by("-created_at")
    if request.method == "POST" and profile_user == request.user:
        avatar = request.FILES.get("avatar")
        bio = request.POST.get("bio")
        if avatar:
            profile.avatar = avatar
        if bio is not None:
            profile.bio = bio
        profile.save()
        return redirect("profile_redirect")
    return render(request, "posts/profile.html", {"profile_user": profile_user, "profile": profile, "posts": posts})

def groups(request):
    return render(request, "posts/coming_soon.html", {"title": "Groupes"})

def marketplace(request):
    return render(request, "posts/coming_soon.html", {"title": "Marketplace"})

@login_required
def settings(request):
    return render(request, "posts/settings.html")

@login_required
def wallet(request):
    profile = Profile.objects.get_or_create(user=request.user)[0]
    transactions = Transaction.objects.filter(user=request.user).order_by("-created_at")[:10]
    if request.method == "POST":
        amount = Decimal(request.POST.get("amount", 0))
        if amount > 0:
            profile.balance += amount
            profile.save()
            Transaction.objects.create(user=request.user, amount=amount, type="deposit", description="Rechargement")
            return redirect("wallet")
    return render(request, "posts/wallet.html", {"profile": profile, "transactions": transactions})

@login_required
def search(request):
    q = request.GET.get("q", "")
    users = User.objects.filter(username__icontains=q) if q else []
    posts = Post.objects.filter(content__icontains=q) if q else []
    return render(request, "posts/search.html", {"users": users, "posts": posts, "q": q})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by("-created_at")
    return render(request, "posts/post_detail.html", {"post": post, "comments": comments})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        if post.user!= request.user:
            Notification.objects.create(to_user=post.user, from_user=request.user, notification_type="like", post=post)
    return redirect(request.META.get("HTTP_REFERER", "home"))

@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("content")
        if content:
            Comment.objects.create(user=request.user, post=post, content=content)
            if post.user!= request.user:
                Notification.objects.create(to_user=post.user, from_user=request.user, notification_type="comment", post=post)
    return redirect(request.META.get("HTTP_REFERER", "home"))

def share_post(request, post_id):
    return redirect("home")

