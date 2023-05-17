from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django import forms
from .models import Auction, User, Category, Bid, Comment
from .forms import CreateListingForm, BidForm, CommentForm
from django.db.models import Max


def index(request):
    auctions = Auction.objects.filter(isActive =True)
    return render(request, "auctions/index.html", {"auctions":auctions, "title":"Active Listings"})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("au:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("au:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("au:index"))
    else:
        return render(request, "auctions/register.html")

def closedListings(request):
    auctions = Auction.objects.filter(isActive =False)
    return render(request, "auctions/index.html", {"auctions":auctions, "title":"Closed Listings"})    

@login_required
@csrf_protect
def create_listing_view(request):
    form = CreateListingForm()
    categories = Category.objects.all()

    
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.creator = request.user
            auction.save()
            
            bid_price = form.cleaned_data["price"]
            bid = Bid.objects.create(bid=bid_price, user=request.user, auction=auction)
            return HttpResponseRedirect(reverse("au:index"))

    return render(request, "auctions/create.html", {'form': form, 'categories': categories})

@login_required
@csrf_protect
def auction(request, id):
    commentForm = CommentForm()
    auction = Auction.objects.get(id=id)
    user = User.objects.get(pk=int(request.user.id))
    is_creator = auction.creator == user
    is_watching = auction.users.filter(pk=user.pk).exists()
    is_winner = False
    
    highest_bid = auction.auction_bid.aggregate(Max('bid'))
    max_bid = highest_bid['bid__max']
    
    if max_bid is not None:
        highest_bid_obj = Bid.objects.filter(auction=auction, bid=max_bid).first()
        if highest_bid_obj:
            highest_bid_username = highest_bid_obj.user.username
            if (not(auction.isActive) and highest_bid_username == user.username):
                is_winner = True
    
    bids = Bid.objects.filter(auction=auction)
    comments = Comment.objects.filter(auction=auction)  

    return render(request, "auctions/auction.html", 
        {
            "auction":auction, "is_watching":is_watching, "bids":bids, 
            "is_creator":is_creator, "is_winner": is_winner, "commentForm": commentForm,
            "comments":comments
    })

@login_required
@csrf_protect
def addToWatchlist(request, auction_id):
    if request.method == "POST":
        auction = Auction.objects.get(id=auction_id)
        user = User.objects.get(pk=int(request.user.id))
        is_watching = auction.users.filter(pk=user.pk).exists()
        
        if is_watching:
            auction.users.remove(user)
        else:
            auction.users.add(user)
            auction.save()
            

        return HttpResponseRedirect(reverse("au:auction", kwargs={'id':auction_id}))

@login_required
@csrf_protect
def closeAuction(request, auction_id):
    if request.method == "POST":
        auction = Auction.objects.get(id=auction_id)
        user = User.objects.get(pk=int(request.user.id))
        is_creator = auction.creator == user
        
        if is_creator:
            auction.isActive = False
            auction.save()

        return HttpResponseRedirect(reverse("au:auction", kwargs={'id':auction_id}))

@login_required
@csrf_protect
def bid(request, auction_id):
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            auction = Auction.objects.get(id=auction_id)
            user = User.objects.get(pk=int(request.user.id))
            new_price = float(request.POST["offer"])
            # Daha önce teklif yapılmışsa
            if auction.auction_bid.exists():
                highest_bid = auction.auction_bid.aggregate(Max('bid'))['bid__max']
                if new_price > highest_bid:
                    bid = Bid.objects.create(bid=new_price, user=user, auction=auction)
                    auction.price = new_price
                    auction.save()
                else:
                    return render(request, "auctions/error.html")
            # Daha önce teklif yapılmamışsa
            else:
                if new_price > auction.price:
                    bid = Bid.objects.create(bid=new_price, user=user, auction=auction)
                    auction.price = new_price
                    auction.save()
                else:
                    return render(request, "auctions/error.html")
        else:
            form = BidForm()
    
    return HttpResponseRedirect(reverse("au:auction", kwargs={'id': auction_id}))

@login_required
@csrf_protect
def comment(request, auction_id):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            auction = Auction.objects.get(id=auction_id)
            user = User.objects.get(pk=int(request.user.id))
            comment = request.POST["comment"]
            comment = Comment.objects.create(comment=comment, user=user, auction=auction)
            comment.save()
            
    return HttpResponseRedirect(reverse("au:auction", kwargs={'id': auction_id}))

@login_required
@csrf_protect
def watchlist(request):
    auctions = Auction.objects.all()
    
    user_auction = []
    
    for auction in auctions:
        user = User.objects.get(pk=int(request.user.id))
        is_watching = auction.users.filter(pk=user.pk).exists()
        if is_watching:
            user_auction.append(auction)
            
    return render(request, "auctions/watchlist.html", {"user_auction": user_auction})

@login_required
@csrf_protect
def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {"categories": categories})

@login_required
@csrf_protect
def category(request, category_name):
    category_obj = get_object_or_404(Category, name=category_name)
    category_items = Auction.objects.filter(category=category_obj)
    return render(request, "auctions/category.html", {"category_items": category_items, "category_name":category_name})

    