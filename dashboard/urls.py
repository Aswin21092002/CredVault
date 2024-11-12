from django.urls import path
from . import views
from .views import survey_view

urlpatterns = [
    path("", views.index, name="dashboard"),
    path("manage-subscription/", views.ManageSubscription, name="manage-subscription"),
    path("inbox", views.Inbox, name="inbox"),
    path("profile", views.Profile, name="profile"),
    path('update-company-address/', views.UpdateYourCompanyInformation, name='update-company-address'),

    path("cancel-membership", views.CancelMembership, name="cancel-membership"),
    path("upgrade-membership", views.UpgradeMembership, name="upgrade-membership"),
    path("your-business-report", views.YourBusinessReport, name="your-business-report"),
    path(
        "your-company-information",
        views.YourCompanyInformation,
        name="your-company-information",
    ),
    path(
        "your-business-tradelines",
        views.YourBusinessTradelines,
        name="your-business-tradelines",
    ),
    path(
        "add-business-tradelines",
        views.AddBusinessTradelines,
        name="add-business-tradelines",
    ),
    path("dispute", views.DisputeView, name="dispute"),
    path(
        "update-company-information",
        views.UpdateCompanyInformation,
        name="update-company-information",
    ),
    path(
        "business-credit-reports",
        views.BusinessCreditReports,
        name="business-credit-reports",
    ),
    path(
        "current-business-tradelines",
        views.CurrentBusinessTradelines,
        name="current-business-tradelines",
    ),

    path('survey/', survey_view, name='survey'),

    path('questions/', views.QuestionListCreateAPIView.as_view(), name='question-list'),
    path('questions/<int:pk>/', views.QuestionDetailAPIView.as_view(), name='question-detail'),
    path('options/', views.OptionListCreateAPIView.as_view(), name='option-list'),
    path('options/<int:pk>/', views.OptionDetailAPIView.as_view(), name='option-detail'),

    path('search-report/', views.SearchReport, name='search-report'),
    path('upload-excel/', views.UploadExcelView.as_view(), name='upload-excel'),

]
