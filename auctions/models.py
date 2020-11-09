from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.IntegerField()
    image = models.URLField(blank=True)
    category = models.CharField(max_length=64, blank=True)
    listedby = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings") 
    date = models.DateTimeField(auto_now_add=True, auto_now=False, null=True, blank=True)
    startbid = models.IntegerField()
    winner = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    status = models.CharField(max_length=64, blank=True)


class Watchlist(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watching_listing")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watching_user")

class Bid(models.Model):
    bid = models.IntegerField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

class Comment(models.Model):
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_user")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment_listing")
    date = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)