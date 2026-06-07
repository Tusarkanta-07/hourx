from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .models import User
from barter.models import BarterRequest
from skills.models import Skill
from reviews.models import Review
from django.db.models import Q, Sum, Avg, Count

@login_required
def profile(request):
    if request.method == 'POST':
        from django.contrib import messages
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'profiles/profile.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user

    # Active requests (pending + accepted)
    active_requests = BarterRequest.objects.filter(
        Q(sender=user) | Q(receiver=user),
        status__in=['PENDING', 'ACCEPTED']
    ).select_related('skill', 'sender', 'receiver').order_by('-updated_at')[:5]

    # All recent requests for full history
    all_requests = BarterRequest.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).select_related('skill', 'sender', 'receiver').order_by('-updated_at')[:10]

    # Counts by status
    received_pending = BarterRequest.objects.filter(receiver=user, status='PENDING').count()
    sent_pending = BarterRequest.objects.filter(sender=user, status='PENDING').count()

    completed_as_provider = BarterRequest.objects.filter(receiver=user, status='COMPLETED')
    completed_as_requester = BarterRequest.objects.filter(sender=user, status='COMPLETED')
    total_completed = completed_as_provider.count() + completed_as_requester.count()

    # Hours traded
    hours_earned = completed_as_provider.aggregate(total=Sum('hours'))['total'] or 0
    hours_spent = completed_as_requester.aggregate(total=Sum('hours'))['total'] or 0
    hours_in_escrow = BarterRequest.objects.filter(
        Q(sender=user) | Q(receiver=user),
        status='ACCEPTED', is_escrowed=True
    ).aggregate(total=Sum('hours'))['total'] or 0

    # Reviews
    reviews_received = Review.objects.filter(reviewee=user).select_related('reviewer').order_by('-created_at')[:3]
    reviews_given_count = Review.objects.filter(reviewer=user).count()
    avg_rating = Review.objects.filter(reviewee=user).aggregate(avg=Avg('rating'))['avg']

    # My skills
    my_skills = Skill.objects.filter(user=user).order_by('-created_at')[:6]

    # Completion rate
    total_received = BarterRequest.objects.filter(receiver=user).exclude(status='PENDING').count()
    completion_rate = round((completed_as_provider.count() / total_received * 100)) if total_received > 0 else 0

    return render(request, 'dashboard/index.html', {
        'user': user,
        'balance': user.time_balance,
        'active_requests': active_requests,
        'all_requests': all_requests,
        'received_pending': received_pending,
        'sent_pending': sent_pending,
        'total_completed': total_completed,
        'hours_earned': hours_earned,
        'hours_spent': hours_spent,
        'hours_in_escrow': hours_in_escrow,
        'reviews_received': reviews_received,
        'reviews_given_count': reviews_given_count,
        'avg_rating': avg_rating,
        'my_skills': my_skills,
        'completion_rate': completion_rate,
    })

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')

def terms_page(request):
    return render(request, 'pages/terms.html')

def privacy_page(request):
    return render(request, 'pages/privacy.html')

def support_page(request):
    return render(request, 'pages/support.html')

def guidelines_page(request):
    return render(request, 'pages/guidelines.html')
