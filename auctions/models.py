from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.CharField(max_length=64, unique=True)
    email = models.EmailField(max_length=64, unique=True)
    password = models.CharField(max_length=64)
    
    def __str__(self):
        return f"{self.username} : {self.email}"
    
class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Auction(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auction_creator')
    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=128, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.URLField(max_length = 200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    isActive = models.BooleanField(default = True)
    users = models.ManyToManyField(User, blank=True, related_name="watchlist")

    def __str__(self):
        return f"{self.name} : {self.price}"

class Bid(models.Model):
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name="user_bid")
    auction = models.ForeignKey(Auction, on_delete = models.CASCADE, related_name="auction_bid")


class Comment(models.Model):
    comment = models.CharField(max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comment")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="auction_comment")
    