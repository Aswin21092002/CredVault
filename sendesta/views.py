# sendesta/views.py

from rest_framework import viewsets
from bankapp.models import Plan, StripeCustomer, CanDownloadReport
from .serializers import PlanSerializer, StripeCustomerSerializer, CanDownloadReportSerializer

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

class StripeCustomerViewSet(viewsets.ModelViewSet):
    queryset = StripeCustomer.objects.all()
    serializer_class = StripeCustomerSerializer

class CanDownloadReportViewSet(viewsets.ModelViewSet):
    queryset = CanDownloadReport.objects.all()
    serializer_class = CanDownloadReportSerializer
