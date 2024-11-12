from django.shortcuts import render , redirect
from django.contrib import messages
from users.models import UserProfile
from django.contrib.auth.decorators import login_required
from .models import (CompanyInformation,
  YourBusinessRecommendation,
  YourCurrentTradelines,
  SendestaScore,
  BusinessReports,
  UpdateYourCompanyInformation,
  Dispute
)
from users.forms import UpdateProfileForm, UpdateUserForm
# Create your views here.
import stripe
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site


from django.http import JsonResponse
from .models import UserResponse, Question, Option
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.serializers import serialize
from .serializers import QuestionSerializer, OptionSerializer, CompanyInformationSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from bankapp.models import CanDownloadReport
from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd
from rest_framework.response import Response
from rest_framework import status

@login_required
def index(request):
  score = SendestaScore.objects.filter(user=request.user).first()
  recommendation = YourBusinessRecommendation.objects.filter(user=request.user)
  context = {}
  context['score'] = score
  context['recommendation'] = recommendation
  return render(request, 'dashboard/index.html',context)

@login_required
def ManageSubscription(request):
  stripe.api_key = settings.STRIPE_SECRET_KEY
  current_site = get_current_site(request)
  current_domain = f"{request.scheme}://{current_site.domain}"

  # Construct the URL for the /dashboard path
  return_url = f"{current_domain}/dashboard"
  print('return_url')
  print(return_url)
  response = stripe.billing_portal.Session.create(
  customer=request.user.userstripe.stripeCustomerId,
  return_url=return_url,
  ) 
  return redirect(response['url'])
  

@login_required
def Inbox(request):
  context = {}
  return render(request, 'dashboard/inbox.html',context)

@login_required
def Profile(request):
  context = {}
  user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
  
  context['form'] = UpdateUserForm(instance=request.user)
  context['profile_form'] = UpdateProfileForm(
        instance=request.user.userprofile)
  if request.method == 'POST':
      form = UpdateUserForm(request.POST, instance=request.user)
      profile_form = UpdateProfileForm(
            request.POST, instance=request.user.userprofile)
      if form.is_valid() and profile_form.is_valid():
          form.save()
          profile_form.save()
          messages.success(request, 'Your profile has been updated.')
          return redirect('profile')
      return redirect('profile')
  return render(request, 'dashboard/userprofile.html',context)

@login_required
def YourBusinessReport(request):
  context = {}
  reports = BusinessReports.objects.filter(user=request.user)
  context['reports'] = reports
  return render(request, 'dashboard/businessreports.html',context)

@login_required
def BusinessCreditReports(request):
  reports = BusinessReports.objects.filter(user=request.user)
  context = {}
  context['reports'] = reports
  score = SendestaScore.objects.filter(user=request.user).first()
  context['score'] = score
  company = CompanyInformation.objects.filter(user=request.user).first()
  context['company'] = company
  tradelines = YourCurrentTradelines.objects.filter(user=request.user)
  context['tradelines'] = tradelines
  return render(request, 'dashboard/yourbusinesscreditreport.html',context)

@login_required
def YourCompanyInformation(request):
  company = CompanyInformation.objects.filter(user=request.user).first()
  context = {}
  context['company'] = company
  return render(request, 'dashboard/yourcompanyinformation.html',context)

@login_required
def YourBusinessTradelines(request):
  tradelines = YourCurrentTradelines.objects.filter(user=request.user)
  context = {}
  context['tradelines'] = tradelines
  return render(request, 'dashboard/yourcurrentbusinesstradelines.html',context)

@login_required
def AddBusinessTradelines(request):
  tradelines = YourCurrentTradelines.objects.filter(user=request.user)
  context = {}
  context['tradelines'] = tradelines
  return render(request, 'dashboard/addbusinesstradelines.html',context)

@login_required
def DisputeView(request):
  context = {}
  if request.method == 'POST':
    business_name = request.POST.get('business_name')
    business_email = request.POST.get('business_email')
    business_phone = request.POST.get('business_phone')
    reason_of_dispute = request.POST.get('reason_of_dispute')
    Dispute.objects.create(
      business_name = business_name,
      business_email = business_email,
      business_phone = business_phone,
      reason_of_dispute = reason_of_dispute)
  tradelines = YourCurrentTradelines.objects.filter(user=request.user)
  context['tradelines'] = tradelines
  return render(request, 'dashboard/dispute.html',context)

@login_required
def UpdateCompanyInformation(request):
  context = {}
  company  = UpdateYourCompanyInformation.objects.filter(user=request.user).first()
  questions = Question.objects.all()
  total_questions = questions.count()

  serialized_questions = [
        {
            'question_text': question.question_text,
            'options': list(question.options.values('option_text')),
            # 'options': list(question.options.values('option_text'))
        }

        
        for question in questions
    ]
  
  context = {
        'company': company,
        'questions': json.dumps(serialized_questions),  # Pass the questions to the template
        'total_questions': total_questions,
    }
  return render(request, 'dashboard/updatecompanyinformation.html',context)


@login_required
def CurrentBusinessTradelines(request):
  context = {}
  tradelines = YourCurrentTradelines.objects.filter(user=request.user)
  context['tradelines'] = tradelines
  return render(request, 'dashboard/yourcurrentbusinesstradelines.html',context)

@login_required
def CancelMembership(request):
  request.user.userprofile.paid = False
  request.user.userprofile.save()
  return redirect('/dashboard/')

@login_required
def UpgradeMembership(request):
  return redirect('/')

def survey_view(request):
    return render(request, 'updatecompanyinformation.html', {'questions': questions})

@csrf_exempt
def save_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        question_index = data.get('question_index')
        response = data.get('response')

        UserResponse.objects.create(
            user_id=user_id,
            question_index=question_index,
            response=response
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)


# api for Question and it's option

class QuestionListCreateAPIView(APIView):
    """
    List all questions or create a new question.
    """
    def get(self, request, format=None):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionDetailAPIView(APIView):
    """
    Retrieve, update or delete a question instance.
    """
    def get_object(self, pk):
        try:
            return Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        question = self.get_object(pk)
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        question = self.get_object(pk)
        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        question = self.get_object(pk)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OptionListCreateAPIView(APIView):
    """
    List all options or create a new option for a question.
    """
    def get(self, request, format=None):
        options = Option.objects.all()
        serializer = OptionSerializer(options, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = OptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OptionDetailAPIView(APIView):
    """
    Retrieve, update or delete an option instance.
    """
    def get_object(self, pk):
        try:
            return Option.objects.get(pk=pk)
        except Option.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        option = self.get_object(pk)
        serializer = OptionSerializer(option)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        option = self.get_object(pk)
        serializer = OptionSerializer(option, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        option = self.get_object(pk)
        option.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

@login_required
def SearchReport(request):
  return render(request, 'dashboard/search_reports.html')
  

class UploadExcelView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file)
            records = df.to_dict(orient='records')
            for record in records:
                serializer = CompanyInformationSerializer(data=record)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)