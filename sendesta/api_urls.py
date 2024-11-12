# sendesta/api_urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlanViewSet, StripeCustomerViewSet, CanDownloadReportViewSet

router = DefaultRouter()
router.register(r'plans', PlanViewSet)
router.register(r'stripe-customers', StripeCustomerViewSet)
router.register(r'can-download-reports', CanDoping ec2-54-88-157-171.compute-1.amazonaws.com
wnloadReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
