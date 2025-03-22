from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel  # Import the models for car make and car model

from .populate import initiate

from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    data = {"userName":""}
    return JsonResponse(data)

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    context = {}

    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        User.objects.get(username=username)
        username_exist = True
    except:
        logger.debug("{} is new user".format(username))

    if not username_exist:
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        data = {"userName": username, "error": "Already Registered"}
        return JsonResponse(data)

# Add the `get_cars` view here
def get_cars(request):
    # Count the number of car makes
    count = CarMake.objects.filter().count()
    print(count)
    
    # If no car makes exist, initiate 
    if(count == 0):
        initiate()  # Define the initiate function if needed
    
    # Fetch car models and use select_related for better performance
    car_models = CarModel.objects.select_related('car_make')
    
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    
    return JsonResponse({"CarModels": cars})

# # Update the `get_dealerships` view to render the index page with a list of dealerships
#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})

# Create a `get_dealer_reviews` view to render the reviews of a dealer

def get_dealer_reviews(request, dealer_id):
    """Fetch dealer reviews, analyze sentiments, and return JSON response."""
    url = f"https://your-api-endpoint.com/fetchReviews/dealer/{dealer_id}"  # Replace with the actual API URL
    reviews = get_request(url)  # Fetch reviews from the microservice

    review_list = []
    if reviews and "reviews" in reviews:
        for review in reviews["reviews"]:
            sentiment = analyze_review_sentiments(review["review"])  # Analyze sentiment
            review_detail = {
                "id": review.get("id"),
                "name": review.get("name"),
                "review": review.get("review"),
                "sentiment": sentiment  # Add sentiment analysis result
            }
            review_list.append(review_detail)

    return JsonResponse({"dealer_id": dealer_id, "reviews": review_list}, safe=False)

# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

# Create a `add_review` view to submit a review
def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})
