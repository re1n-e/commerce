from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category_name(models.Model):
    CategoryName = models.CharField(max_length=80)

    def __str__(self):
        return self.CategoryName


class Listing(models.Model):
    Title = models.CharField(max_length=80)
    Description = models.CharField(max_length=1000)
    Price = models.FloatField()
    Active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    msg_bid = models.CharField(max_length=50)
    Category = models.ForeignKey(
        Category_name,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="listings",
    )
    Image_url = models.CharField(max_length=500)
    watchlist = models.ManyToManyField(
        User,
        blank=True,
        related_name="Watchlist",
    )
    def __str__(self):
        return self.Title


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_user")
    bidding = models.FloatField(default=0)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid_item")
    response = models.CharField(max_length=250)
    bid_number = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            latest_bid = Bid.objects.all().order_by("-bid_number").first()
            if latest_bid:
                self.bid_number = latest_bid.bid_number + 1
            else:
                self.bid_number = 1
        super().save(*args, **kwargs)


class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE, 
        related_name="comment"
        )
    item = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="commentitem"
    )
    comment = models.CharField(max_length=300)
    def __str__(self):
        return f"{self.user} commented on {self.item}"
