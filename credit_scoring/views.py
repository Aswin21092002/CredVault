from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Business
import json

def dashboard_view(request):
    business = get_object_or_404(Business, id=1)
    context = {'business': business,
               'sendesta_score': business.sendesta_score }
    return render(request, 'index.html', context)
    
def generate_report_view(request):
    business = get_object_or_404(Business, id=1) #assuming you are getting a specific business
    
    report_data = {
        'sendesta_score' : business.sendesta_score,
        'business_name' : business.name,
        'company_age' : business.company_age,
        'num_employees' : business.num_employees,
        'industry_risk' : business.industry_risk,
        'profit_loss_ratio' : business.profit_loss_ratio,
        'on_time_payments' : business.on_time_payments,
    }
    #return the report as a downloadable file (e.g., JSON or PDF)
    response = HttpResponse(json.dumps(report_data), 
                            content_type = 'application/json')
    response['Content-Disposition'] = 'attachment; filename=business_credit_report.json'
    return response