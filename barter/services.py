from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import BarterRequest

User = get_user_model()

def lock_escrow(request_id):
    """
    Locks the hours from sender's account when request is accepted.
    """
    with transaction.atomic():
        barter_request = BarterRequest.objects.select_for_update().get(id=request_id)
        
        if barter_request.status != 'PENDING':
             raise ValidationError("Request must be pending to accept.")
        
        sender = User.objects.select_for_update().get(id=barter_request.sender_id)
        if sender.time_balance < barter_request.hours:
            raise ValidationError("Sender does not have enough time balance.")
            
        # Deduct from sender
        sender.time_balance -= barter_request.hours
        sender.save()
        
        barter_request.is_escrowed = True
        barter_request.status = 'ACCEPTED'
        barter_request.save()
        return barter_request

def release_escrow(request_id):
    """
    Releases the hours to receiver's account when job is completed.
    """
    with transaction.atomic():
        barter_request = BarterRequest.objects.select_for_update().get(id=request_id)
        
        if barter_request.status != 'ACCEPTED':
            raise ValidationError("Request must be accepted (active) to complete.")
            
        if not barter_request.is_escrowed:
             raise ValidationError("No funds in escrow.")

        # Credit receiver
        receiver = User.objects.select_for_update().get(id=barter_request.receiver_id)
        receiver.time_balance += barter_request.hours
        receiver.save()
        
        barter_request.status = 'COMPLETED'
        barter_request.is_escrowed = False # Funds moved out of escrow
        barter_request.cancellation_requested_by = None
        barter_request.cancellation_reason = ""
        barter_request.save()
        return barter_request

def reject_request(request_id):
    """
    Rejects a pending request. No escrow involved yet.
    """
    with transaction.atomic():
        barter_request = BarterRequest.objects.select_for_update().get(id=request_id)
        if barter_request.status != 'PENDING':
            raise ValidationError("Only pending requests can be rejected.")
        
        barter_request.status = 'REJECTED'
        barter_request.save()
        return barter_request

def cancel_request(request_id, user=None):
    """
    Cancels a request.
    - If PENDING: sender can cancel immediately with no escrow refund needed.
    - If ACCEPTED: unilateral cancellation by sender is prohibited. Requires receiver consent
      (receiver directly canceling or mutual confirmation via confirm_cancellation).
    """
    with transaction.atomic():
        barter_request = BarterRequest.objects.select_for_update().get(id=request_id)
        
        if barter_request.status not in ['PENDING', 'ACCEPTED']:
            raise ValidationError("Only pending or accepted requests can be canceled.")
            
        if barter_request.status == 'PENDING':
            barter_request.status = 'CANCELED'
            barter_request.cancellation_requested_by = None
            barter_request.cancellation_reason = ""
            barter_request.save()
            return barter_request

        # Request is ACCEPTED
        if user is None or user == barter_request.sender:
            raise ValidationError(
                "Accepted requests cannot be unilaterally canceled by the sender. "
                "Receiver consent or mutual confirmation is required."
            )
        elif user == barter_request.receiver:
            # Receiver consent is granted directly: refund sender and cancel
            if barter_request.is_escrowed:
                sender = User.objects.select_for_update().get(id=barter_request.sender_id)
                sender.time_balance += barter_request.hours
                sender.save()
                barter_request.is_escrowed = False

            barter_request.status = 'CANCELED'
            barter_request.cancellation_requested_by = None
            barter_request.cancellation_reason = ""
            barter_request.save()
            return barter_request
        else:
            raise ValidationError("Unauthorized to cancel this exchange.")

def request_cancellation(request_id, user, reason=""):
    """
    Initiates a cancellation request on an accepted barter exchange.
    Requires the other party's confirmation/consent to finalize.
    """
    with transaction.atomic():
        barter_request = BarterRequest.objects.select_for_update().get(id=request_id)
        
        if barter_request.status != 'ACCEPTED':
            raise ValidationError("Cancellation can only be requested for accepted exchanges.")
            
        if not barter_request.is_escrowed:
            raise ValidationError("No active escrow found for this request.")
            
        if user not in [barter_request.sender, barter_request.receiver]:
            raise ValidationError("You are not authorized to request cancellation for this exchange.")
            
        if barter_request.cancellation_requested_by:
            if barter_request.cancellation_requested_by == user:
                raise ValidationError("You have already submitted a cancellation request for this exchange.")
            else:
                raise ValidationError("The other party has already requested cancellation. Please confirm their request.")

        barter_request.cancellation_requested_by = user
        barter_request.cancellation_reason = (reason or "").strip()
        barter_request.save()
        return barter_request

def confirm_cancellation(request_id, user):
    """
    Confirms an existing cancellation request, fulfilling mutual confirmation / receiver consent.
    Refunds escrowed hours to the sender and marks the request as CANCELED.
    """
    with transaction.atomic():
        barter_request = BarterRequest.objects.select_for_update().get(id=request_id)
        
        if barter_request.status != 'ACCEPTED':
            raise ValidationError("Request must be in accepted status to confirm cancellation.")
            
        if not barter_request.cancellation_requested_by:
            raise ValidationError("No cancellation request is pending for this exchange.")
            
        if user not in [barter_request.sender, barter_request.receiver]:
            raise ValidationError("You are not authorized to confirm cancellation for this exchange.")
            
        if user == barter_request.cancellation_requested_by:
            raise ValidationError("You cannot confirm your own cancellation request.")

        if barter_request.is_escrowed:
            sender = User.objects.select_for_update().get(id=barter_request.sender_id)
            sender.time_balance += barter_request.hours
            sender.save()
            barter_request.is_escrowed = False

        barter_request.status = 'CANCELED'
        barter_request.cancellation_requested_by = None
        barter_request.cancellation_reason = ""
        barter_request.save()
        return barter_request

def withdraw_cancellation(request_id, user):
    """
    Withdraws or declines an active cancellation request, returning the exchange to normal accepted status.
    - The initiator can withdraw their request.
    - The recipient can decline the cancellation request.
    """
    with transaction.atomic():
        barter_request = BarterRequest.objects.select_for_update().get(id=request_id)
        
        if barter_request.status != 'ACCEPTED':
            raise ValidationError("Request must be in accepted status.")
            
        if not barter_request.cancellation_requested_by:
            raise ValidationError("No cancellation request is pending.")
            
        if user not in [barter_request.sender, barter_request.receiver]:
            raise ValidationError("You are not authorized to modify this cancellation request.")

        barter_request.cancellation_requested_by = None
        barter_request.cancellation_reason = ""
        barter_request.save()
        return barter_request
