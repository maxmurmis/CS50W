from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

class User(AbstractUser):
    pass

class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(default="No description provided.")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.TextField(default="No image provided.")
    timestamp = models.DateTimeField(default=now)
    category = models.CharField(default="No category provided.", max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=1, related_name="user")
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="winner")
    closed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title}, created by {self.user}'

class Comment(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    commentary = models.CharField(max_length=140)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.user} left a new comment on {self.auction}'

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bidder")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user} bid ${self.amount} for {self.auction}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    auction = models.ForeignKey('Auction', on_delete=models.CASCADE, related_name="watchlist_items")

    def __str__(self):
        return f"{self.user.username}'s watchlist item: {self.auction.title}"
