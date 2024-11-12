from django.urls import path
from . import views
from .views import create_checkout_session

urlpatterns = [
  path('',views.Index,name='index'),
  path('get-relevant-companies/',views.GetRelevantCompanies,name='get_relevant_companies'),
  # path('create-checkout-session-buy-report/<int:company_id>/', views.MakePaymentBuyReport),
  # path('create-checkout-session-buy-report/<int:company_id>/', views.MakePaymentBuyReport, name='create-checkout-session-buy-report'),
  path('create-checkout-session-buy-report/<int:company_id>/', views.MakePaymentBuyReport, name='create-checkout-session-buy-report'),
  path('config/', views.stripe_config, name='stripe_config'),

  path('download-report/<int:id>/',views.DownloadReport,name='download_report'),
  path('saved-reports/', views.saved_reports, name='saved-reports'),
  path('business/',views.BusinessServices,name='business'),
  path('legal/',views.Legal,name='legal'),
  path('contact/',views.Contact,name='contact'),
  path('about/',views.About,name='about'),
  path('account',views.Account,name='account'),
  path('register/<int:id>/',views.AccountWithPay,name='register'),
  path('make_payment/<int:id>/',views.MakePaymentView,name='make_payment'),
  path('config/', views.stripe_config),
  path('success/', views.Success),
  path('create-checkout-session/<int:id>/', views.MakePayment),

  path('save-report/', views.SaveReport, name='save_report'),
  path('create-checkout-session/', create_checkout_session, name='create-checkout-session'),

]
