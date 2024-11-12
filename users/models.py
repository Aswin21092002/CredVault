from django.db import models
from django.contrib.auth.models import User

# Create your models here.
COUNTRY_CHOICES = (
    ("London", "London"),
    ("Brazil", "Brazil"),
    ("USA", "USA"),
    ("Canada", "Canada"),
    ("Thailand", "Thailand"),
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="userprofile"
    )
    phone = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(
        max_length=100, choices=COUNTRY_CHOICES, null=True, blank=True
    )
    gender = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    paid = models.BooleanField(default=False)
    total_reports = models.IntegerField(default=0)
    total_tradelines = models.IntegerField(default=0)
    def __str__(self):
        return self.user.username
