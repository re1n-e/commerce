from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Max


from .models import User, Category_name, Listing, Bid , Comment


def index(request):
    return render(request, "auctions/index.html")


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


def create_Listing(request):
    if request.method == "GET":
        return render(
            request,
            "auctions/createListing.html",
            {"categories": Category_name.objects.all()},
        )
    elif request.method == "POST":
        title = request.POST.get(
            "title"
        )  
        description = request.POST.get(
            "description"
        ) 
        category_id = request.POST.get(
            "category"
        )  
        imageurl = request.POST.get(
            "imageurl"
        )  
        price = request.POST.get(
            "price"
        )  

        if not title:
            return render(
                request,
                "auctions/createListing.html",
                {"message": "Title can't be empty"},
            )
        if not description:
            return render(
                request,
                "auctions/createListing.html",
                {"message": "Description can't be empty"},
            )
        if not price:
            return render(
                request,
                "auctions/createListing.html",
                {"message": "Price can't be empty"},
            )
        try:
            price = float(price)
            if price < 0:
                return render(
                    request,
                    "auctions/createListing.html",
                    {"message": "Price can't be negative"},
                )
        except ValueError:
            return render(
                request,
                "auctions/createListing.html",
                {"message": "Price must be a valid number"},
            )

        category = Category_name.objects.get(pk=category_id)

        listing = Listing(
            Title=title,
            Description=description,
            Price=price,
            Active=True,
            user=request.user,
            Category=category,
            Image_url=imageurl,
        )
        listing.save()
        return HttpResponseRedirect(reverse("index"))


def get_is_watched(request, listing_id):
    if listing_id:
        try:
            listing = Listing.objects.get(pk=listing_id)
            return request.user in listing.watchlist.all()
        except Listing.DoesNotExist:
            return False
    else:
        return False


def view_listing(request, listing_id=None):
    if listing_id:
        is_watched = get_is_watched(request, listing_id)
        try:
            listing = Listing.objects.get(pk=listing_id)
            comments = Comment.objects.filter(item=listing)
            bids = Bid.objects.filter(item=listing).order_by("-bid_number")[
                :1
            ]  
            return render(
                request,
                "auctions/ListingPage.html",
                {
                    "listing": listing,
                    "is_watched": is_watched,
                    "comments": comments,
                    "msg_less": listing.msg_bid,
                    "bids": bids,
                    "winner": Bid.objects.filter(item=listing, user=request.user.id)
                    .order_by("-bid_number")
                    .first(),
                },
            )
        except Listing.DoesNotExist:
            return HttpResponse("Listing not found", status=404)
    else:
        if request.method == "GET":
            listing_id = request.GET.get("listing_id")
            if listing_id:
                return view_listing(request, listing_id)
            else:
                return HttpResponse("Listing ID not provided in GET data", status=400)
        else:
            return HttpResponseNotAllowed(["GET"])


def index(request):
    if request.method == "GET":
        is_valid_items = Listing.objects.filter(Active=True)
        return render(request, "auctions/index.html", {"Listings": is_valid_items})
    else:
        return redirect("")


def addwatchlist(request, id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=id)
        user = request.user
        listing.watchlist.add(user)
        return redirect(reverse("view_listing", kwargs={"listing_id": id}))
    else:
        return HttpResponse("Invalid request", status=400)


def removewatchlist(request, id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=id)
        user = request.user
        listing.watchlist.remove(user)
        return redirect(reverse("view_listing", kwargs={"listing_id": id}))
    else:
        return HttpResponse("Invalid request", status=400)


def watchlist(request):
    if request.user.is_authenticated:
        user = request.user
        watchlist_items = Listing.objects.filter(watchlist=user)
        return render(
            request, "auctions/watchlist.html", {"watchlist": watchlist_items}
        )
    else:
        return HttpResponse("You need to be logged in to view your watchlist.")


def categories(request):
    if request.method == "POST":
        category_id = request.POST.get("cat_id")
        if category_id:
            try:
                category = Category_name.objects.get(pk=category_id)
                listings = Listing.objects.filter(Category=category)
                return render(request, "auctions/show.html", {"listings": listings})
            except Category_name.DoesNotExist:
                return HttpResponse("Category not found", status=404)
        else:
            return HttpResponse("Category ID not provided in POST data", status=400)
    else:
        categories = Category_name.objects.all()
        return render(request, "auctions/categories.html", {"cat": categories})


def bid(request, id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=id)
        user1 = request.user
        try:
            user_bid = float(request.POST.get("Bid_id"))
        except (TypeError, ValueError):
            return HttpResponseRedirect(
                reverse(
                    "view_listing",
                    kwargs={"listing_id": id},
                )
            )

        highest_bid = (
            Bid.objects.filter(item=listing).aggregate(Max("bidding"))["bidding__max"]
            or 0
        )

        if user_bid > listing.Price:
            if user_bid > highest_bid:
                a = Bid(
                    user=user1,
                    item=listing,
                    bidding=user_bid,
                )
                a.save()
                listing.msg_bid = "Congrats! Your bid is made"
                listing.save()
                return HttpResponseRedirect(
                    reverse("view_listing", kwargs={"listing_id": id})
                )
            else:
                listing.msg_bid = (
                    "The current bid should be greater than the highest bid"
                )
                listing.save()
                return HttpResponseRedirect(
                    reverse(
                        "view_listing",
                        kwargs={
                            "listing_id": id,
                        },
                    )
                )
        else:
            listing.msg_bid = "The bid should be greater than the listed price!"
            listing.save()
            return HttpResponseRedirect(
                reverse(
                    "view_listing",
                    kwargs={
                        "listing_id": id,
                    },
                )
            )


def comment(request, id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=id)
        user1 = request.user
        user_comment = request.POST["addcomment"]

        new_comment = Comment(
            user=user1,
            item=listing,
            comment=user_comment,
        )
        new_comment.save()
    return redirect(reverse("view_listing", kwargs={"listing_id": id}))

def close_listing(request, id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=id)
        listing.Active = False
        listing.save()
    return redirect(reverse("view_listing", kwargs={"listing_id": id}))
