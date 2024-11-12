# sendesta/serializers.py

from rest_framework import serializers
from bankapp.models import Plan, StripeCustomer, CanDownloadReport

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class StripeCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeCustomer
        fields = '__all__'

class CanDownloadReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CanDownloadReport
        fields = '__all__'
