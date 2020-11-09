from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from .models import User, Listing, Watchlist, Bid, Comment
from .forms import ListingForm
from . import util


def index(request):
    listings = Listing.objects.filter(status="active")
    return render(request, "auctions/index.html", {
        "listings": listings,
        "watchlistcount": util.watchlist_total(request)
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

@login_required
def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            user = User.objects.get(pk=request.user.id)
            listing = Listing(
                title= form.cleaned_data['title'],
                description = form.cleaned_data['description'],
                image = form.cleaned_data['image'],
                price = form.cleaned_data['bid'],
                startbid = form.cleaned_data['bid'],
                category = form.cleaned_data['category'],
                listedby = user,
                status = 'active'
            )
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = ListingForm()    
        
    return render(request, "auctions/create.html", {
        "form": form,
        "watchlistcount": util.watchlist_total(request)
    })

def listing(request, listing_id):

    if request.method == "POST":
        watchbtnClicked = request.POST.get('watchlist', 'not')
        newbid = request.POST.get('newbid', '')
        bidbtnClicked = request.POST.get('bidbutton', 'not')
        postbtnClicked = request.POST.get('postcomment', 'not')
        closebtnClicked = request.POST.get('closelisting', 'not')

        if watchbtnClicked != 'not':
            listing = Listing.objects.get(pk=listing_id)
            user = User.objects.get(pk=request.user.id)
            if user.watching_user.filter(listing=listing).count() > 0:
                user.watching_user.filter(listing=listing).delete()
            else:
                watchlist = Watchlist(
                    user = User.objects.get(pk=request.user.id),
                    listing = Listing.objects.get(pk=listing_id)
                )
                watchlist.save()
        elif postbtnClicked != 'not':
            listing = Listing.objects.get(pk=listing_id)
            user = User.objects.get(pk=request.user.id)
            text = request.POST.get('comment', '')
            comment = Comment(listing=listing, user=user, comment=text)
            comment.save()   
        elif closebtnClicked != 'not':
            listing = Listing.objects.get(pk=listing_id)
            listing.status = "closed"
            listing.winner = listing.bids.order_by("-bid").first().user
            listing.save()
        elif bidbtnClicked != 'not':
            listing = Listing.objects.get(pk=listing_id)
            bid = Bid(
                user = User.objects.get(pk=request.user.id),
                bid = newbid,
                listing = listing
            )
            bid.save()
            listing.price = bid.bid
            listing.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
        
    listing = Listing.objects.get(pk=listing_id)
    comments = listing.comment_listing.all()
    bids = listing.bids.count()
    user = User.objects.get(pk=request.user.id)
    currentbid = listing.bids.order_by("-bid").first()

    if Watchlist.objects.filter(user=user, listing=listing).count() > 0:
        watching = True
    else:
        watching = False

    if currentbid is not None and currentbid.user.id == request.user.id:
        yoursbid = True
    else: 
        yoursbid = False

    if currentbid is not None:
        newprice = currentbid.bid + 1
    else:
        newprice = listing.price + 1

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlistcount": util.watchlist_total(request),
        "comments": comments,
        "bids": bids,
        "watching": watching,
        "yoursbid": yoursbid,
        "newprice": newprice,
        "lastbid": currentbid
    })

def categories(request):
    categories = Listing.objects.values("category").annotate(count=Count('category'))

    return render(request, "auctions/categories.html", {
        "categories": categories,
        "watchlistcount": util.watchlist_total(request)
    })

def category(request, category):
    if category == 'none':
        category = ''
    listings = Listing.objects.filter(category=category)
    if category == '':
        category = 'No Category'
    return render(request, "auctions/category.html", {
        "category": category,
        "listings": listings,
        'watchlistcount': util.watchlist_total(request)
    })

def watchlist(request):
    user = User.objects.get(pk=request.user.id)
    watchlist = user.watching_user.all()
    listings = []
    for watched in watchlist:
        listings.append(watched.listing)

    return render(request, "auctions/watchlist.html", {
        "listings": listings,
        "watchlistcount": util.watchlist_total(request)
    })

def winner(request):
    user = User.objects.get(pk=request.user.id)
    activeListings = Listing.objects.filter(listedby=user).filter(status="active")
    closedListings = Listing.objects.filter(listedby=user).filter(status="closed")
    wonListings = Listing.objects.filter(winner=user).filter(status="closed")

    return render(request, "auctions/winner.html", {
        'activeListings': activeListings,
        "closedListings": closedListings,
        'wonListings': wonListings,
        'watchlistcount': util.watchlist_total(request)
    })