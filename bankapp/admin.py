from django.contrib import admin

# Register your models here.
admin.site.site_header = 'Sendesta | Admin'
admin.site.index_title = 'Sendesta'
admin.site.site_title = 'Admin'
from .models import Plan ,StripeCustomer, CanDownloadReport, SavedReport, Report

admin.site.register(Plan)
admin.site.register(StripeCustomer)
admin.site.register(CanDownloadReport)
admin.site.register(SavedReport)
admin.site.register(Report)