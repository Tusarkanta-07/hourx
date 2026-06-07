from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import BarterRequest
from skills.models import Skill
from . import services

@login_required
def create_request(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    if request.user == skill.user:
        messages.error(request, "You cannot request your own skill.")
        return redirect('skill_detail', pk=skill_id)

    if request.method == 'POST':
        try:
            hours = int(request.POST.get('hours', 1))
        except ValueError:
            hours = 1
            
        if hours <= 0:
            messages.error(request, "Hours must be greater than zero.")
            return redirect('skill_detail', pk=skill_id)
            
        message = request.POST.get('message', '')
        # Check if sender has enough balance
        if request.user.time_balance < hours:
            messages.error(request, "Insufficient time balance.")
            return redirect('skill_detail', pk=skill_id)
            
        BarterRequest.objects.create(
            sender=request.user,
            receiver=skill.user,
            skill=skill,
            hours=hours,
            message=message
        )
        messages.success(request, "Request sent successfully!")
        return redirect('sent_requests')
    
    return render(request, 'barter/create_request.html', {'skill': skill})

@login_required
def received_requests(request):
    requests = BarterRequest.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'barter/received_requests.html', {'requests': requests})

@login_required
def sent_requests(request):
    requests = BarterRequest.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, 'barter/sent_requests.html', {'requests': requests})

@login_required
@require_POST
def accept_request(request, request_id):
    barter_req = get_object_or_404(BarterRequest, id=request_id, receiver=request.user)
    try:
        services.lock_escrow(request_id)
        messages.success(request, "Request accepted. Hours locked in escrow.")
    except Exception as e:
        messages.error(request, str(e))
    return redirect('received_requests')

@login_required
@require_POST
def complete_request(request, request_id):
    # Usually completion is confirmed by the sender (who received the service)?
    # Or receiver marks as done and sender confirms?
    # Logic: "Barter Requests -> Escrow releasing".
    # If sender (the one who payed hours) confirms completion, funds go to receiver.
    # If receiver marks complete, maybe sender needs to approve.
    # For simplicity: Sender confirms completion to release funds.
    barter_req = get_object_or_404(BarterRequest, id=request_id, sender=request.user)
    try:
        services.release_escrow(request_id)
        messages.success(request, "Transaction completed. Hours released to receiver.")
    except Exception as e:
        messages.error(request, str(e))
    return redirect('sent_requests')

@login_required
@require_POST
def reject_request(request, request_id):
    barter_req = get_object_or_404(BarterRequest, id=request_id, receiver=request.user)
    try:
        services.reject_request(request_id)
        messages.success(request, "Request rejected.")
    except Exception as e:
        messages.error(request, str(e))
    return redirect('received_requests')

@login_required
@require_POST
def cancel_request(request, request_id):
    # Depending on business logic, maybe only sender can cancel
    barter_req = get_object_or_404(BarterRequest, id=request_id, sender=request.user)
    try:
        services.cancel_request(request_id)
        messages.success(request, "Request canceled.")
    except Exception as e:
        messages.error(request, str(e))
    return redirect('sent_requests')

@login_required
def join_meeting(request, request_id):
    # Ensure only sender or receiver of the accepted request can join
    barter_req = get_object_or_404(BarterRequest, id=request_id)
    
    if request.user != barter_req.sender and request.user != barter_req.receiver:
        messages.error(request, "You do not have permission to join this meeting.")
        return redirect('skill_list')

    if barter_req.status not in ['ACCEPTED', 'COMPLETED']:
        messages.error(request, "Meeting is only available for accepted or completed requests.")
        return redirect('skill_list')

    # Generate a unique and private meeting room name
    # Using the request ID and the skill title stripped of non-alphanumeric characters
    import re
    clean_title = re.sub(r'\W+', '', barter_req.skill.title)
    meeting_room_name = f"HOURX_Meeting_{request_id}_{clean_title}_SecureRoom"

    return render(request, 'barter/meeting.html', {
        'request_obj': barter_req,
        'meeting_room_name': meeting_room_name
    })

