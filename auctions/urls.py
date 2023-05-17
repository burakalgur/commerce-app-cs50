from django.urls import path

from . import views

app_name = "au"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("closedListings", views.closedListings, name="closedListings"),
    path("create", views.create_listing_view, name="create_listing_view"),
    path("auction/<int:id>", views.auction, name="auction"),
    path("auction/<int:auction_id>/addToWatchlist", views.addToWatchlist, name="addToWatchlist"),
    path("auction/<int:auction_id>/closeAuction", views.closeAuction, name="closeAuction"),
    path("auction/<int:auction_id>/bid", views.bid, name="bid"),
    path("auction/<int:auction_id>/comment", views.comment, name="comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category_name>", views.category, name="category"),
]
