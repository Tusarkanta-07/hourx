from django.test import TestCase
from accounts.models import User
from skills.models import Skill
from .models import BarterRequest
from . import services
from django.core.exceptions import ValidationError

class BarterServicesTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='pwd', time_balance=10.0)
        self.receiver = User.objects.create_user(username='receiver', password='pwd', time_balance=5.0)
        self.skill = Skill.objects.create(user=self.receiver, title='Cooking', description='I can cook')
        
        self.request = BarterRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            skill=self.skill,
            hours=2,
            message='Teach me to cook',
            status='PENDING'
        )

    def test_lock_escrow_success(self):
        # Sender has 10, hours is 2
        services.lock_escrow(self.request.id)
        
        self.sender.refresh_from_db()
        self.request.refresh_from_db()
        
        self.assertEqual(self.sender.time_balance, 8.0)
        self.assertEqual(self.request.status, 'ACCEPTED')
        self.assertTrue(self.request.is_escrowed)

    def test_lock_escrow_insufficient_funds(self):
        # Change sender balance
        self.sender.time_balance = 1.0
        self.sender.save()
        
        with self.assertRaises(ValidationError):
            services.lock_escrow(self.request.id)

    def test_release_escrow(self):
        services.lock_escrow(self.request.id) # Setup accepted state
        
        services.release_escrow(self.request.id)
        
        self.receiver.refresh_from_db()
        self.request.refresh_from_db()
        
        self.assertEqual(self.receiver.time_balance, 7.0) # 5 + 2
        self.assertEqual(self.request.status, 'COMPLETED')
        self.assertFalse(self.request.is_escrowed)

    def test_reject_request(self):
        services.reject_request(self.request.id)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'REJECTED')

    def test_cancel_pending_request(self):
        # Cancel while pending: no funds refunded because they weren't taken
        services.cancel_request(self.request.id)
        self.sender.refresh_from_db()
        self.request.refresh_from_db()
        self.assertEqual(self.sender.time_balance, 10.0)
        self.assertEqual(self.request.status, 'CANCELED')

    def test_cancel_accepted_request(self):
        # Accept the request first to lock escrow
        services.lock_escrow(self.request.id)
        self.sender.refresh_from_db()
        self.assertEqual(self.sender.time_balance, 8.0)
        
        # Now cancel, should refund
        services.cancel_request(self.request.id)
        self.sender.refresh_from_db()
        self.request.refresh_from_db()
        
        self.assertEqual(self.sender.time_balance, 10.0) # Refunded
        self.assertEqual(self.request.status, 'CANCELED')
        self.assertFalse(self.request.is_escrowed)
