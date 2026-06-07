from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from barter.models import BarterRequest

User = get_user_model()

@login_required
def add_review(request, user_id):
    reviewee = get_object_or_404(User, pk=user_id)
    if request.user == reviewee:
        messages.error(request, "You cannot review yourself.")
        return redirect('dashboard') 

    # Verify that the users have at least one completed transaction together
    has_completed_txn = BarterRequest.objects.filter(
        Q(sender=request.user, receiver=reviewee, status='COMPLETED') |
        Q(sender=reviewee, receiver=request.user, status='COMPLETED')
    ).exists()

    if not has_completed_txn:
        messages.error(request, "You can only review users you have successfully bartered with.")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating', 5))
        except ValueError:
            rating = 5
            
        if rating < 1 or rating > 5:
            messages.error(request, "Rating must be between 1 and 5.")
            return render(request, 'reviews/add.html', {'reviewee': reviewee})
            
        comment = request.POST.get('comment', '').strip()
        if not comment:
            messages.error(request, "Please provide a comment for your review.")
            return render(request, 'reviews/add.html', {'reviewee': reviewee})
        
        with transaction.atomic():
            Review.objects.create(
                reviewer=request.user,
                reviewee=reviewee,
                rating=rating,
                comment=comment
            )
        messages.success(request, f"Review added for {reviewee.username}.")
        return redirect('dashboard') 
    
    return render(request, 'reviews/add.html', {'reviewee': reviewee})
