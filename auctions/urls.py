from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createListing", views.create_Listing, name="createListing"),
    path("view_listing/<int:listing_id>/", views.view_listing, name="view_listing"),
    path("categories", views.categories, name="categories"),
    path("addwatchlist/<int:id>", views.addwatchlist, name="addwatchlist"),
    path("removewatchlist/<int:id>", views.removewatchlist, name="removewatchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("comment/<int:id>", views.comment, name="comment"),
    path("bid/<int:id>/", views.bid, name="bid"),
    path("close_listing/<int:id>", views.close_listing, name="close_listing"),
]
