from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from decimal import Decimal, InvalidOperation
from .models import User, Auction, Bid, Comment, Watchlist

categories = ["Fashion", "Beauty", "Toys", "Electronics", "Home", "Sports", "Vehicles", "Groceries"]

@login_required
def new_bid(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    current_price = auction.price

    if request.method == "POST":
        bid_amount_str = request.POST.get("bid_amount", "").strip()

        try:
            bid_amount = Decimal(bid_amount_str)
            if bid_amount <= current_price:
                return render(request, "auctions/entry.html", {
                    "auction": auction,
                    "error": "Your bid must be higher than the current price."
                })
            
        except (InvalidOperation, ValueError):
            return render(request, "auctions/entry.html", {
                "auction": auction,
                "error": "Please enter a valid bid amount."
            })

        auction.price = bid_amount
        auction.save()

        Bid.objects.create(auction=auction, amount=bid_amount, user=request.user)
        
        return render(request, "auctions/entry.html", {
            "auction": auction,
            "message": "Your bid has been placed. You currently hold the highest bid "
        })
        
def entry(request, auction_id):
    
    auction = Auction.objects.get(pk=auction_id)
    comments =  Comment.objects.filter(auction=auction)
    return render(request, "auctions/entry.html", {
        "auction" : auction,
        "comments": comments,
        "message_closed": "The auction is closed"        
    })

@login_required
def get_watchlist(request):
    watchlist_items = Watchlist.objects.filter(user=request.user)
    auctions = [watchlist_item.auction for watchlist_item in watchlist_items]

    return render(request, "auctions/watchlist.html", {
        "watchlist": auctions
    })

@login_required
def add_watchlist(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)

    if Watchlist.objects.filter(user=request.user, auction=auction).exists():
        # Redirect back to the entry page with an error message
        return render(request, "auctions/entry.html", {
            "auction": auction,
            "error": "This item is already in your watchlist."
        })
    else:
        Watchlist.objects.create(user=request.user, auction=auction)

    return redirect("get_watchlist")

@login_required
def remove_watchlist(request, auction_id):
    if not request.user.is_authenticated:
        return redirect('login')

    auction = Auction.objects.get(pk=auction_id)
    Watchlist.objects.filter(user=request.user, auction=auction).delete()
    return redirect("get_watchlist")

@login_required
def new(request):
    return render(request, "auctions/new.html", {
        "categories": categories
    })

@login_required
def create(request):
    if request.method == "POST":
        form = Auction(request.POST)
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '').strip()
        category = request.POST.get('category', '').strip()
        image= request.POST.get('image', '').strip()
        user= request.user

        if not title or not description or not price:
            return render(request, "encyclopedia/new.html", {
                "error": "Complete all required fields!",
                "title": title,
                "description": description,
                "price": price,
                "image": image
            })

        auction = Auction(
            title=title,
            description=description,
            price=price,
            category=category,
            image=image,
            user=user
        )
        auction.save()
        
        return redirect("index")
    
    return render(request, "auctions/new.html", {
        "categories": categories
    })

@login_required
def close(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    if request.method == "POST":
        highest_bid = auction.bidder.all().order_by('-amount').first()
        if highest_bid:
            auction.winner = highest_bid.user  
            auction.price = highest_bid.amount  
            auction.closed = True  
            auction.save()


            message_closed = "The auction is closed"
            message_winner = f'The winner of this auction is {auction.winner.username} with a bid of ${auction.price}.'
        else:
            message_winner = 'No bids were placed on this auction.'

        return render(request, "auctions/entry.html", {
            "auction": auction,
            "message_closed": message_closed,
            "message_winner": message_winner  
        })


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Auction.objects.all()
    })


@login_required
def comment(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)

    if request.method == "POST":
        commentary = request.POST.get('comment', '').strip()
        if commentary:
            Comment.objects.create(auction=auction, commentary=commentary, user=request.user)
            return redirect('entry', auction_id=auction.id)

        return render(request, "auctions/entry.html", {
            "auction": auction,
            "comments": Comment.objects.filter(auction=auction),
            "error": "Comment cannot be empty."
        })

    return render(request, "auctions/entry.html", {
        "auction": auction,
        "comments": Comment.objects.filter(auction=auction),
    })

def category(request):
    return render (request, "auctions/category.html", {
        "categories": categories
    })

def category_listings(request, category):
    listings= Auction.objects.filter(category=category)
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
