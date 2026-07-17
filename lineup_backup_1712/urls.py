from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from lineup import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("create/", views.create_post, name="create_post"),
    path("story/create/", views.create_story, name="create_story"),
    path("story/<int:story_id>/", views.story_view, name="story_view"),
    path("friends/", views.friends, name="friends"),
    path("friends/add/<int:user_id>/", views.send_friend_request, name="send_request"),
    path("friends/cancel/<int:user_id>/", views.cancel_friend_request, name="cancel_request"),
    path("friends/accept/<int:req_id>/", views.accept_friend_request, name="accept_request"),
    path("friends/decline/<int:req_id>/", views.decline_friend_request, name="decline_request"),
    path("messages/", views.messages, name="messages"),
    path("messages/<int:user_id>/", views.chat, name="chat"),
    path("videos/", views.videos_redirect, name="videos_redirect"),
    path("videos/all/", views.all_videos, name="all_videos"),
    path("notifications/", views.notifications, name="notifications"),
    path("profile/", views.profile_redirect, name="profile_redirect"),
    path("settings/", views.settings, name="settings"),
    path("groups/", views.groups, name="groups"),
    path("marketplace/", views.marketplace, name="marketplace"),
    path("wallet/", views.wallet, name="wallet"),
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("post/<int:post_id>/like/", views.like_post, name="like_post"),
    path("post/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("post/<int:post_id>/share/", views.share_post, name="share_post"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
