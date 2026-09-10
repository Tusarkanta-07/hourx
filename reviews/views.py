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
def add_review(request, request_id):
    barter_req = get_object_or_404(BarterRequest, pk=request_id)
    
    # Only transaction participants can submit a review
    if request.user not in [barter_req.sender, barter_req.receiver]:
        messages.error(request, "You can only review exchanges you participated in.")
        return redirect('dashboard')
        
    # Transaction must be COMPLETED
    if barter_req.status != 'COMPLETED':
        messages.error(request, "You can only review completed barter exchanges.")
        return redirect('dashboard')
        
    # Determine reviewee (the other participant)
    reviewee = barter_req.receiver if request.user == barter_req.sender else barter_req.sender
    if request.user == reviewee:
        messages.error(request, "You cannot review yourself.")
        return redirect('dashboard')

    # Prevent duplicate reviews on the same barter exchange (OneToOne binding)
    if hasattr(barter_req, 'review') and barter_req.review is not None:
        messages.error(request, "This exchange has already been reviewed.")
        return redirect('sent_requests' if request.user == barter_req.sender else 'received_requests')

    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating', 5))
        except ValueError:
            rating = 5
            
        if rating < 1 or rating > 5:
            messages.error(request, "Rating must be between 1 and 5.")
            return render(request, 'reviews/add.html', {'reviewee': reviewee, 'barter_request': barter_req})
            
        comment = request.POST.get('comment', '').strip()
        if not comment:
            messages.error(request, "Please provide a comment for your review.")
            return render(request, 'reviews/add.html', {'reviewee': reviewee, 'barter_request': barter_req})
        
        try:
            with transaction.atomic():
                Review.objects.create(
                    barter_request=barter_req,
                    reviewer=request.user,
                    reviewee=reviewee,
                    rating=rating,
                    comment=comment
                )
            messages.success(request, f"Review submitted for {reviewee.username}.")
        except Exception as e:
            messages.error(request, "This exchange has already been reviewed.")

        return redirect('sent_requests' if request.user == barter_req.sender else 'received_requests')
    
    return render(request, 'reviews/add.html', {'reviewee': reviewee, 'barter_request': barter_req})
