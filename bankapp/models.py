from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import stripe
from django.utils import timezone

# Create your models here.

class CompanyInformation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="company_info")
    business_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.business_name
    
class Plan(models.Model):
    plan_name = models.CharField(max_length=100)
    stripe_id = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    total_reports = models.IntegerField(default=10)
    total_tradelines = models.IntegerField(default=12)
    time = models.CharField(max_length=100, default="month")
    valid = models.CharField(max_length=100, default="monthly")

    def __str__(self):
        return self.plan_name


class StripeCustomer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="userstripe"
    )
    stripeCustomerId = models.CharField(max_length=255)
    stripeSubscriptionId = models.CharField(
        max_length=255, default=None, null=True, blank=True
    )

    def __str__(self):
        return self.user.username
    
    def parse_date(self, date):
        dt_object = datetime.utcfromtimestamp(date)
        parsed_date = dt_object.strftime("%m/%d/%y")
        return parsed_date


    def get_user_subscription_details(self):
        try:
            # Retrieve the subscription & product
            stripe.api_key = settings.STRIPE_SECRET_KEY
            subscription = stripe.Subscription.retrieve(self.stripeSubscriptionId)
            subscription_data = {}
            subscription_data['status'] = subscription['status']
            subscription_data['current_period_start'] = self.parse_date(subscription['current_period_start'])
            subscription_data['current_period_end'] = self.parse_date(subscription['current_period_end'])

            return [subscription_data]
        except:
            return []


class CanDownloadReport(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="can_download"
    )
    company_information = models.ForeignKey(
        "dashboard.companyinformation",
        on_delete=models.CASCADE,
        related_name="can_download",
    )

    def __str__(self):
        return f"{self.user.username} - {self.company_information.business_name}"


class SavedReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    download_date = models.DateTimeField(default=timezone.now)
    company_information = models.ForeignKey(CompanyInformation, on_delete=models.CASCADE)

    def __str__(self):
        return self.report_name
    

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='reports/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.user.username} on {self.created_at}"