import django.contrib.auth.views
from django.http.response import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.conf import settings
from .models import (
    Plan,
    StripeCustomer,
    CanDownloadReport,
    CompanyInformation,
    SavedReport,
)
from users.models import UserProfile
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from dashboard.models import CompanyInformation
from django.shortcuts import get_object_or_404
import json
import stripe
from fuzzywuzzy import process
from django.core.serializers import serialize
import os
from .models import Report

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your views here.
def generate_a_checkout_to_download_this_report(request, company_info):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    # domain_url = 'https://sendesta.com/'
    domain_url = "http://localhost:8001/"
    try:
        # Create a PaymentIntent with the amount and currency
        checkout_session = stripe.checkout.Session.create(
            customer=(
                request.user.userstripe.stripeCustomerId
                if request.user.is_authenticated
                else None
            ),
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Report on {company_info.business_name}",
                        },
                        "unit_amount": 4900,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            metadata={"company_info_obj_id": company_info.id},
            success_url=domain_url
            + f"download-report/{company_info.id}"
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url,
        )
        return redirect(checkout_session.url)
    except Exception as e:
        return JsonResponse({"error": str(e)})


def get_user_requested_report(request, user, company_id):
    context = {}
    company_id = int(company_id)
    company_info = CompanyInformation.objects.get(id=company_id)
    if request.user.is_authenticated:
        can_download_report = CanDownloadReport.objects.filter(
            user=user, company_information=company_info
        )
        if can_download_report:
            return redirect(f"/download-report/{company_info.id}")
        else:
            if request.user.userprofile.total_reports == 0:
                return generate_a_checkout_to_download_this_report(
                    request, company_info
                )
            else:
                request.user.userprofile.total_reports -= 1
                request.user.userprofile.save()
                CanDownloadReport.objects.get_or_create(
                    user=request.user, company_information=company_info
                )
                return redirect(f"/download-report/{company_info.id}")

    else:
        return generate_a_checkout_to_download_this_report(request, company_info)


def Index(request):
    context = {}
    basic = Plan.objects.filter(plan_name="basic")
    pro = Plan.objects.filter(plan_name="professional")
    context["title"] = "Home"
    context["basic"] = basic
    context["pro"] = pro
    context["API_KEY"] = settings.STRIPE_SECRET_KEY
    if request.method == "GET":
        try:
            company_info = list(request.user.business_info.all())[-1]
            context["business_name"] = company_info.business_name
        except Exception as e:
            print("Error while getting the user company: ", e)
        return render(request, "index.html", context)


def MakePaymentBuyReport(request, company_id):
    res = get_user_requested_report(request, request.user, company_id)
    return res


def GetRelevantCompanies(request):
    context = {}
    data = request.POST
    country = data.get("country", "")
    company = data.get("company", "")

    if request.method == "POST":
        try:
            personal_or_other = int(data.get("personal_or_other"))

            if personal_or_other == 0:
                company_info = CompanyInformation.objects.filter(
                    user=request.user
                ).first()
                if company_info:
                    CanDownloadReport.objects.get_or_create(
                        user=request.user, company_information=company_info
                    )
                    return redirect(f"/download-report/{company_info.id}")
                else:
                    context["no_company"] = True
                    return render(request, "company-search-results.html", context)
        except:
            pass

        if not company:
            context["no_company"] = True
            return render(request, "company-search-results.html", context)

        all_companies = CompanyInformation.objects.all().order_by("-id")

        try:
            # Use fuzzy matching to find similar countrys and business names
            country_results = process.extract(
                country, [company for company in all_companies], limit=5
            )
            companies_name_results = process.extract(
                company, [company for company in all_companies], limit=5
            )
        except:
            context["no_company"] = True
            return render(request, "company-search-results.html", context)

        # Create a list of matched objects
        matched_objects = []
        for (country, country_score), (company_name, company_name_score) in zip(
            country_results, companies_name_results
        ):
            # Customize the matching threshold as per your requirements
            if company_name_score > 39:
                matched_objects.append(company_name)
                if country.id == company_name.id:
                    continue

            if country_score > 39:
                matched_objects.append(country)

        context["companies"] = matched_objects
        return render(request, "company-search-results.html", context)

    elif request.method == "GET" and request.is_ajax():
        query = request.GET.get("query", "")
        suggestions = []

        if query:
            company_results = CompanyInformation.objects.filter(
                business_name__icontains=query
            ).values_list("business_name", flat=True)[:5]
            city_results = CompanyInformation.objects.filter(
                city__icontains=query
            ).values_list("city", flat=True)[:5]
            suggestions = list(company_results) + list(city_results)

        return JsonResponse({"suggestions": suggestions})

    return render(request, "company-search.html", context)


# def GetRelevantCompanies(request):
#     context = {}
#     data = request.POST
#     country = data.get("country")
#     company = data.get("company")
#     try:
#         personal_or_other = int(data.get("personal_or_other"))

#         if personal_or_other == 0:
#             company_info = CompanyInformation.objects.filter(user=request.user)[0]
#             if company_info:
#                 CanDownloadReport.objects.get_or_create(
#                     user=request.user, company_information=company_info
#                 )
#                 return redirect(f"/download-report/{company_info.id}")
#             else:
#                 context["no_company"] = True
#                 return render(request, "company-search-results.html", context)
#     except:
#         pass

#     if company == "":
#         context["no_company"] = True
#         return render(request, "company-search-results.html", context)

#     all_companies = CompanyInformation.objects.all().order_by("-id")
#     try:
#         # Use fuzzy matching to find similar countrys and business names
#         country_results = process.extract(
#             country, [company for company in all_companies], limit=5
#         )
#         companies_name_results = process.extract(
#             company, [company for company in all_companies], limit=5
#         )
#     except:
#         context["no_company"] = True
#         return render(request, "company-search-results.html", context)

#     # Create a list of matched objects
#     matched_objects = []
#     for (country, country_score), (company_name, company_name_score) in zip(
#         country_results, companies_name_results
#     ):
#         # Customize the matching threshold as per your requirements
#         if company_name_score > 39:
#             matched_objects.append(company_name)
#             if country.id == company_name.id:
#                 continue

#         if country_score > 39:
#             matched_objects.append(country)

#     context["companies"] = matched_objects
#     return render(request, "company-search-results.html", context)


# def DownloadReport(request, id):
#     stripe.api_key = settings.STRIPE_SECRET_KEY

#     context = {}
#     company_information = CompanyInformation.objects.get(id=id)

#     can_download_report = False
#     if request.user.is_authenticated:
#         can_download_report = CanDownloadReport.objects.filter(
#             user=request.user, company_information=company_information
#         )

#     try:
#         session_id = request.GET.get("session_id")
#         session = stripe.checkout.Session.retrieve(session_id)
#     except:
#         session = {}
#         session['payment_status'] = "not_valid"


#     if can_download_report or session.payment_status == "paid":
#         context = {}
#         context["report"] = model_to_dict(company_information)
#         context["trade_lines"] = []
#         context["maximum_credit_recommendations"] = []

#         all_trade_lines = company_information.user.current_tradelines.all()
#         all_maximum_credit_recommendation = (
#             company_information.user.maximum_credit_recommendation.all()
#         )
#         for trade_line in all_trade_lines:
#             trade_line_obj = {}
#             trade_line_obj["business_name"] = trade_line.business_name
#             trade_line_obj["email"] = trade_line.email
#             trade_line_obj["phone"] = trade_line.phone
#             trade_line_obj["tradeline_age"] = trade_line.tradeline_age
#             trade_line_obj["tradeline_date"] = trade_line.tradeline_date
#             trade_line_obj["tradeline_amount"] = trade_line.tradeline_amount
#             trade_line_obj["status"] = trade_line.status

#             context["trade_lines"].append(trade_line_obj)

#         for maximum_credit_recommendation in all_maximum_credit_recommendation:
#             maximum_credit_recommendation_obj = {}
#             maximum_credit_recommendation_obj[
#                 "score"
#             ] = maximum_credit_recommendation.score
#             maximum_credit_recommendation_obj[
#                 "maximum_credit_recommendation"
#             ] = maximum_credit_recommendation.maximum_credit_recommendation

#             context["maximum_credit_recommendations"].append(
#                 maximum_credit_recommendation_obj
#             )

#     else:
#         context["report"] = None
#     return render(request, "download_report.html", context)


def DownloadReport(request, id):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    context = {}
    company_information = CompanyInformation.objects.get(id=id)

    can_download_report = False
    if request.user.is_authenticated:
        can_download_report = CanDownloadReport.objects.filter(
            user=request.user, company_information=company_information
        ).exists()

    try:
        session_id = request.GET.get("session_id")
        session = stripe.checkout.Session.retrieve(session_id)
    except:
        session = {}
        session["payment_status"] = "not_valid"

    if can_download_report or session.get("payment_status") == "paid":
        context = {
            "report": model_to_dict(company_information),
            "trade_lines": [],
            "maximum_credit_recommendations": [],
        }

        all_trade_lines = company_information.user.current_tradelines.all()
        all_maximum_credit_recommendation = (
            company_information.user.maximum_credit_recommendation.all()
        )

        for trade_line in all_trade_lines:
            trade_line_obj = {
                "business_name": trade_line.business_name,
                "email": trade_line.email,
                "phone": trade_line.phone,
                "tradeline_age": trade_line.tradeline_age,
                "tradeline_date": trade_line.tradeline_date,
                "tradeline_amount": trade_line.tradeline_amount,
                "status": trade_line.status,
            }
            context["trade_lines"].append(trade_line_obj)

        for maximum_credit_recommendation in all_maximum_credit_recommendation:
            maximum_credit_recommendation_obj = {
                "score": maximum_credit_recommendation.score,
                "maximum_credit_recommendation": maximum_credit_recommendation.maximum_credit_recommendation,
            }
            context["maximum_credit_recommendations"].append(
                maximum_credit_recommendation_obj
            )
    else:
        context["report"] = None

    return render(request, "download_report.html", context)


def saved_reports(request):
    if request.user.is_authenticated:
        user_reports = Report.objects.filter(user=request.user)
    else:
        user_reports = []

    return render(request, "dashboard/saved_report.html", {"reports": user_reports})


def Products(request):
    context = {}
    context["title"] = "Products"
    return render(request, "Products.html", context)


def Legal(request):
    context = {}
    context["title"] = "Legal"
    return render(request, "legal.html", context)


def BusinessServices(request):
    context = {}
    context["title"] = "Business Services"
    return render(request, "businessservices.html", context)


def Contact(request):
    context = {}
    context["title"] = "Contact"
    return render(request, "contact.html", context)


def About(request):
    return render(request, "about.html", {})


def Account(request):
    if request.user.is_authenticated:
        messages.info(request, "You have been already logged in")
        return redirect("dashboard")
    if request.method == "GET":
        global nxt
        nxt = request.GET.get("next")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                if nxt:
                    return redirect(nxt)
                else:
                    return redirect("/")
            except:
                return redirect("/")
        else:
            messages.error(request, "Username or maybe Password is incorrect")
    return render(request, "account.html", {})


@csrf_exempt
def AccountWithPay(request, id):
    plan = Plan.objects.get(id=id)
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        data = data.get("data")
        user_created = User.objects.create(
            username=data.get("username"),
            password=data.get("password"),
            email=data.get("email"),
            first_name=data.get("name"),
        )
        user_profile, _ = UserProfile.objects.get_or_create(user=user_created)
        user_profile.gender = data.get("gender")
        user_profile.city = data.get("city")
        user_profile.address = data.get("address")
        user_profile.country = data.get("country")
        user_profile.save()
        print("[start] creating and now redirecting")

        login(request, user_created)
        print("[end] creating and now redirecting")
        return redirect(reverse("index"))
    else:
        return render(request, "accountwithpay.html", {"plan": plan})


@csrf_exempt
def stripe_config(request):
    if request.method == "GET":
        stripe_config = {"publicKey": settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


# @login_required
# def MakePayment(request, id):
#     if request.method == "GET":
#         plan = Plan.objects.get(id=id)
#         # domain_url = "https://sendesta.com/"
#         domain_url = "http://localhost:8001/"
#         stripe.api_key = settings.STRIPE_SECRET_KEY
#         try:
#             checkout_session = stripe.checkout.Session.create(
#                 customer=request.user.userstripe.stripeCustomerId
#                 if request.user.is_authenticated
#                 else None,
#                 success_url='http://localhost:8001/' + "success/?session_id={CHECKOUT_SESSION_ID}",
#                 cancel_url=domain_url,
#                 payment_method_types=["card"],
#                 mode="subscription",
#                 metadata={
#                     "total_reports": plan.total_reports,
#                     "total_tradelines": plan.total_tradelines,
#                 },
#                 line_items=[
#                     {
#                         "price": plan.stripe_id,
#                         "quantity": 1,
#                     }
#                 ],
#             )
#             return JsonResponse({"sessionId": checkout_session["id"]})
#         except Exception as e:
#             return JsonResponse({"error": str(e)})


@login_required
def MakePayment(request, id):
    if request.method == "GET":
        plan = Plan.objects.get(id=id)
        domain_url = "https://sendesta.com/"  # Use your production URL
        if settings.DEBUG:
            domain_url = "http://localhost:8001/"  # Use localhost for development

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                customer=(
                    request.user.userstripe.stripeCustomerId
                    if request.user.is_authenticated
                    else None
                ),
                success_url=domain_url
                + f"download-report/{id}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=domain_url,
                payment_method_types=["card"],
                mode="subscription",
                metadata={
                    "total_reports": plan.total_reports,
                    "total_tradelines": plan.total_tradelines,
                },
                line_items=[
                    {
                        "price": plan.stripe_id,
                        "quantity": 1,
                    }
                ],
            )
            return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            return JsonResponse({"error": str(e)})


def MakePaymentView(request, id):
    plan = Plan.objects.get(id=id)
    context = {}
    context["plan"] = plan
    return render(request, "checkout-session.html", context)


def Success(request):
    request.user.userprofile.paid = True
    request.user.userprofile.save()
    return redirect("dashboard")


# stripe.exe listen --forward-to https://sendesta.com/stripe_webhook
# stripe.exe listen --forward-to http://localhost:8000/stripe_webhook
@require_POST
@csrf_exempt
def stripe_webhook(request):
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        session = event["data"]["object"]
        try:
            # Handle the checkout.session.completed event
            if (
                event["type"] == "checkout.session.completed"
                or event["type"] == "customer.subscription.created"
            ):
                # Fetch all the required data from session
                try:
                    metadata = session["metadata"]
                    stripe_customer_id = session.get("customer")
                    stripe_customer = StripeCustomer.objects.get(
                        stripeCustomerId=stripe_customer_id
                    )
                    if "company_info_obj_id" in metadata:
                        company_info_obj = CompanyInformation.objects.get(
                            id=int(metadata["company_info_obj_id"])
                        )
                        CanDownloadReport.objects.get_or_create(
                            user=stripe_customer.user,
                            company_information=company_info_obj,
                        )
                    else:
                        stripe_subscription_id = session.get("subscription")

                        stripe_customer.stripeSubscriptionId = stripe_subscription_id
                        stripe_customer.user.userprofile.paid = True
                        stripe_customer.user.userprofile.total_reports += int(
                            metadata["total_reports"]
                        )

                        # -1 means unlimited
                        if int(metadata["total_tradelines"]) == -1:
                            stripe_customer.user.userprofile.total_tradelines = -1
                        else:
                            stripe_customer.user.userprofile.total_tradelines += int(
                                metadata["total_tradelines"]
                            )

                        stripe_customer.user.userprofile.save()
                        stripe_customer.save()
                except:
                    pass

            if event["type"] == "invoice.payment_failed":
                return redirect("https://sendesta.com/payment/failure")

            if event["type"] == "customer.subscription.trial_will_end":
                # send an email
                pass

            if event["type"] == "customer.subscription.deleted":
                stripe_customer_id = session.get("customer")
                stripe_customer = StripeCustomer.objects.get(
                    stripeCustomerId=stripe_customer_id
                )
                stripe_customer.stripeSubscriptionId = None
                stripe_customer.user.userprofile.paid = False
                stripe_customer.user.userprofile.save()
                stripe_customer.save()

            if event["type"] == "customer.subscription.updated":
                stripe_subscription_id = session["id"]
                new_target_price_id = session["items"]["data"][0]["price"]["id"]
                is_cancelled = session["cancellation_details"]["reason"]
                was_subscription_already_active = session["status"]
                subscription_ = stripe.Subscription.retrieve(stripe_subscription_id)
                # Retrieve the price_id from the items associated with the subscription
                price_id = subscription_["items"]["data"][0]["price"]["id"]
                plan = False
                try:
                    plan = Plan.objects.get(stripe_id=price_id)
                except Exception as e:
                    print(f"No plan found with the id: {price_id}")

                stripe_customer_id = session.get("customer")
                stripe_customer = StripeCustomer.objects.get(
                    stripeCustomerId=stripe_customer_id
                )
                stripe_customer.stripeSubscriptionId = stripe_subscription_id

                stripe_customer.user.userprofile.paid = True
                print(session)
                if (
                    plan
                    and is_cancelled == None
                    and (
                        was_subscription_already_active != "active"
                        or was_subscription_already_active != "canceled"
                        or was_subscription_already_active != "past_due"
                    )
                ) or (plan and price_id != new_target_price_id):
                    stripe_customer.user.userprofile.total_reports += plan.total_reports
                    # -1 means unlimited
                    if plan.total_tradelines == -1:
                        stripe_customer.user.userprofile.total_tradelines = -1
                    else:
                        stripe_customer.user.userprofile.total_tradelines += (
                            plan.total_tradelines
                        )

                stripe_customer.user.userprofile.save()

                stripe_customer.save()

        except Exception as e:
            print(f"Error while managing subscription before ending function: {str(e)}")

        print("webhook completed")
        return HttpResponse(status=200)
    except Exception as e:
        print(f"Error while managing subscription: {str(e)}")


def SaveReport(request):
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf_file = request.FILES["pdf"]

        # Check if a report already exists for the current user
        existing_report = Report.objects.filter(user=request.user).exists()

        if not existing_report:
            # Save the PDF file to the database
            report = Report()
            report.user = request.user  # Associate the report with the current user
            report.file.save(pdf_file.name, pdf_file)
            report.save()

            return JsonResponse({"success": True})

        return JsonResponse(
            {"success": False, "message": "Report already exists for this user."}
        )

    return JsonResponse({"success": False, "message": "No file found in the request."})


@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        # Assuming you want to create a transaction for the logged-in user
        user = request.user

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": "price_1PdYG7Ro60QijuQn0v0awnDt",  # Use the Price ID from Stripe Dashboard
                    "quantity": 1,
                }
            ],
            mode="payment",
            # test
            success_url="http://127.0.0.1:8001/download-report/<int:id>/",
            cancel_url="http://127.0.0.1:8001/dashboard/",
            # #live
            # success_url='https://www.sendesta.com/download-report/<int:id>/',
            # cancel_url='https://www.sendesta.com/dashboard/',
        )

        return JsonResponse({"id": session.id})


# @csrf_exempt
# def SaveReport(request):
#     if request.method == 'POST' and request.FILES.get('pdf'):
#         pdf_file = request.FILES['pdf']

#         # Save the PDF file to the database
#         report = Report()
#         report.user = request.user  # Associate the report with the current user
#         report.file.save(pdf_file.name, pdf_file)
#         report.save()

#         return JsonResponse({'success': True})

#     return JsonResponse({'success': False})
