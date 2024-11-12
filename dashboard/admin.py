from django.contrib import admin
from .models import (CompanyInformation
,YourBusinessRecommendation
,YourCurrentTradelines
,SendestaScore
,BusinessReports
,UpdateYourCompanyInformation
,Dispute
,UserResponse
,Question
,Option)
# Register your models here.
from import_export.admin import ImportExportModelAdmin
from import_export import resources

#This will create an import and export option 
@admin.register(CompanyInformation)
class CompanyInformationAdmin(ImportExportModelAdmin):
    pass

admin.site.register(YourBusinessRecommendation)
admin.site.register(YourCurrentTradelines)
admin.site.register(SendestaScore)
admin.site.register(BusinessReports)
admin.site.register(UpdateYourCompanyInformation)
admin.site.register(Dispute)
admin.site.register(UserResponse)
admin.site.register(Question)
admin.site.register(Option)
