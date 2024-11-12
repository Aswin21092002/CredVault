# signals.py in your app

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from users.models import UserProfile
from .models import StripeCustomer
from django.conf import settings
import stripe

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_user_account = stripe.Customer.create(
            email=instance.email,
            name=f"{instance.username}"
        )
        stripe_user_account_id = stripe_user_account["id"]
        StripeCustomer.objects.create(user=instance, stripeCustomerId=stripe_user_account_id)
        UserProfile.objects.create(user=instance)
