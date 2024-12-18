from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path("admin", admin.site.urls),
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new, name="new"),
    path("create", views.create, name="create"),
    path("close/<int:auction_id>", views.close, name="close"),
    path("<int:auction_id>", views.entry, name="entry"),
    path("watchlist/", views.get_watchlist, name="get_watchlist"),
    path("watchlist/add/<int:auction_id>/", views.add_watchlist, name="add_watchlist"),
    path("watchlist/remove/<int:auction_id>/", views.remove_watchlist, name="remove_watchlist"),
    path("new_bid/<int:auction_id>/", views.new_bid, name="new_bid"),
    path("auction/<int:auction_id>/comment", views.comment, name="comment"),
    path("category", views.category, name="category"),
    path("category/<str:category>", views.category_listings, name="category_listings")
]
