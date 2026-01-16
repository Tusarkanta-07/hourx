from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ProfileForm
from .models import User

from django.db import transaction

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'profiles/profile.html', {'form': form})

@login_required
def dashboard(request):
    # This view will aggregate data from other apps later
    return render(request, 'dashboard/index.html', {
        'user': request.user,
        'balance': request.user.time_balance
    })

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

# -- Password Reset via OTP --
import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        
        if user:
            # Generate 6-digit OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            user.reset_otp = otp
            user.reset_otp_expiry = timezone.now() + timedelta(minutes=10) # Valid for 10 mins
            user.save()
            
            # Send Email
            send_mail(
                'Password Reset OTP',
                f'Your password reset code is: {otp}',
                'noreply@hourx.com',
                [email],
                fail_silently=False,
            )
            
            # Store email in session to use in next step
            request.session['reset_email'] = email
            return redirect('password_reset_verify_otp')
        else:
            # For security, you might want to show same message even if email not found
            # But for good UX in this phase, we'll just error
            messages.error(request, 'User with this email does not exist.')
            
    return render(request, 'auth/password_reset.html')

def password_reset_verify_otp(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('password_reset')
        
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user = User.objects.filter(email=email).first()
        
        if user and user.reset_otp == otp and user.reset_otp_expiry > timezone.now():
            # OTP Verified
            request.session['reset_verified'] = True
            return redirect('password_reset_new_password')
        else:
            messages.error(request, 'Invalid or expired OTP.')
            
    return render(request, 'auth/password_reset_verify.html')

def password_reset_new_password(request):
    email = request.session.get('reset_email')
    verified = request.session.get('reset_verified')
    
    if not email or not verified:
        return redirect('password_reset')
        
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password == confirm_password:
            user = User.objects.filter(email=email).first()
            if user:
                user.set_password(password)
                user.reset_otp = None # Clear OTP
                user.reset_otp_expiry = None
                user.save()
                
                # Cleanup session
                del request.session['reset_email']
                del request.session['reset_verified']
                
                messages.success(request, 'Password reset successful. Please login.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
            
    return render(request, 'auth/password_reset_confirm.html')
