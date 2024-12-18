from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:title>", views.entry, name="entry"),
    path("search/", views.search, name="search"),
    path("create/", views.create, name="create"),
    path("new/", views.new, name="new" ),
    path("<str:title>/edit/", views.edit, name="edit"),
    path("random/", views.random, name="random")
]
