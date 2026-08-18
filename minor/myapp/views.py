from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, EmailAuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
import time
from .ml_service import ml_service
from .models import Subscription, Invoice
import uuid
from django.utils import timezone

# Create your views here.
def home(request):
    return render(request, 'home.html')

def appointment(request):
    return render(request, 'appointment.html')

def disease_info(request):
    return render(request,'disease_info.html')

def page1(request):
    return render(request, 'page1.html')

def page2(request):
    return render(request, 'page2.html')

def page3(request):
    return render(request, 'page3.html')

def page4(request):
    return render(request, 'page4.html')

def page5(request):
    return render(request, 'page5.html')

def page6(request):
    return render(request, 'page6.html')

def page7(request):
    return render(request, 'page7.html')

def page8(request):
    return render(request, 'page8.html')

def page9(request):
    return render(request, 'page9.html')

def page10(request):
    return render(request, 'page10.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='myapp.backends.EmailBackend')
            messages.success(request, 'Registration successful. Welcome!')
            return redirect('login')
        else:
            messages.error(request, 'Unsuccessful registration. Invalid information.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user, backend='myapp.backends.EmailBackend')
                request.session['last_activity'] = time.time()
                messages.info(request, f"You are now logged in. Your session will expire in 30 minutes.")
                return redirect('predict')
            else:
                messages.error(request, "Invalid Gmail or password.")
        else:
            messages.error(request, "Invalid Gmail or password.")
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

def check_plan(user):
    """Helper to check if user has access to premium features"""
    subscription = getattr(user, 'subscription', None)
    return subscription and subscription.is_active and subscription.plan_name in ['Starter', 'Pro']

@login_required(login_url='login')
def predict(request):
    request.session['last_activity'] = time.time()
    if not check_plan(request.user):
        messages.warning(request, "The AI Prediction Tool requires a Starter or Pro plan. Please upgrade to continue.")
        return redirect('pricing')
    return render(request, 'predict.html')

@login_required(login_url='login')
def camera_capture(request):
    request.session['last_activity'] = time.time()
    if not check_plan(request.user):
        messages.warning(request, "Camera Capture requires a Starter or Pro plan. Please upgrade to continue.")
        return redirect('pricing')
    return render(request, 'camera_capture.html')

@csrf_exempt
@login_required(login_url='login')
def predict_api(request):
    if request.method == 'POST':
        try:
            request.session['last_activity'] = time.time()
            if not check_plan(request.user):
                return JsonResponse({'error': 'Subscription required for this feature'}, status=403)
            
            if 'file' not in request.FILES:
                return JsonResponse({'error': 'No file uploaded'}, status=400)
            
            file = request.FILES['file']
            if not file.content_type.startswith('image/'):
                return JsonResponse({'error': 'File must be an image'}, status=400)
            
            symptom_start_date = request.POST.get('symptom_start_date')
            result = ml_service.predict(file, symptom_start_date)
            
            if 'error' in result:
                return JsonResponse(result, status=500)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required(login_url='login')
def result(request):
    request.session['last_activity'] = time.time()
    return render(request, 'result.html')

def check_auth_status(request):
    """Simple endpoint to check if user is authenticated and their plan"""
    if request.user.is_authenticated:
        subscription = getattr(request.user, 'subscription', None)
        plan = subscription.plan_name if subscription else 'Free'
        return JsonResponse({
            'authenticated': True,
            'username': request.user.username,
            'plan': plan
        })
    return JsonResponse({'authenticated': False})

@login_required(login_url='login')
def profile_view(request):
    request.session['last_activity'] = time.time()
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        user = request.user
        user.username = username
        user.email = email
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    return render(request, 'profile.html')

def pricing(request):
    return render(request, 'pricing.html')

@csrf_exempt
@login_required(login_url='login')
def activate_plan(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan_name = data.get('plan_name')
            price = data.get('price')
            
            if not plan_name:
                return JsonResponse({'success': False, 'error': 'Plan name is missing'})
            
            subscription, created = Subscription.objects.update_or_create(
                user=request.user,
                defaults={
                    'plan_name': plan_name,
                    'price': price,
                    'is_active': True,
                    'activated_at': timezone.now()
                }
            )
            
            Invoice.objects.create(
                user=request.user,
                subscription=subscription,
                invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
                amount=price
            )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
