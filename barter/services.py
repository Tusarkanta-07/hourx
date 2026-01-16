from django.db import transaction
from django.core.exceptions import ValidationError
from .models import BarterRequest

def lock_escrow(request_id):
    """
    Locks the hours from sender's account when request is accepted.
    """
    with transaction.atomic():
        barter_request = BarterRequest.objects.select_for_update().get(id=request_id)
        
        if barter_request.status != 'PENDING':
             raise ValidationError("Request must be pending to accept.")
        
        sender = barter_request.sender
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
        receiver = barter_request.receiver
        receiver.time_balance += barter_request.hours
        receiver.save()
        
        barter_request.status = 'COMPLETED'
        barter_request.is_escrowed = False # Funds moved out of escrow
        barter_request.save()
        return barter_request
