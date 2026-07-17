from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("story/create/", views.create_story, name="create_story"),
    path("story/view/", views.view_story, name="view_story"),
]
