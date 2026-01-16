from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Review
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

@login_required
def add_review(request, user_id):
    reviewee = get_object_or_404(User, pk=user_id)
    if request.user == reviewee:
        return redirect('profile') # Cannot review self

    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        
        with transaction.atomic():
            Review.objects.create(
                reviewer=request.user,
                reviewee=reviewee,
                rating=rating,
                comment=comment
            )
        return redirect('profile') # Ideally redirect to reviewee's profile or dashboard
    
    return render(request, 'reviews/add.html', {'reviewee': reviewee})
