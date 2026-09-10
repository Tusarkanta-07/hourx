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
        services.cancel_request(self.request.id, user=self.sender)
        self.sender.refresh_from_db()
        self.request.refresh_from_db()
        self.assertEqual(self.sender.time_balance, 10.0)
        self.assertEqual(self.request.status, 'CANCELED')

    def test_prevent_unilateral_sender_cancellation_when_accepted(self):
        # Accept the request first to lock escrow
        services.lock_escrow(self.request.id)
        self.sender.refresh_from_db()
        self.assertEqual(self.sender.time_balance, 8.0)
        
        # Unilateral cancellation by sender MUST be prevented (raises ValidationError)
        with self.assertRaises(ValidationError) as ctx:
            services.cancel_request(self.request.id, user=self.sender)
        self.assertIn("cannot be unilaterally canceled by the sender", str(ctx.exception))
        
        # Escrow must remain intact
        self.sender.refresh_from_db()
        self.request.refresh_from_db()
        self.assertEqual(self.sender.time_balance, 8.0)
        self.assertEqual(self.request.status, 'ACCEPTED')
        self.assertTrue(self.request.is_escrowed)

    def test_mutual_cancellation_flow(self):
        # Accept the request to lock escrow
        services.lock_escrow(self.request.id)
        self.sender.refresh_from_db()
        self.assertEqual(self.sender.time_balance, 8.0)

        # Sender requests cancellation
        services.request_cancellation(self.request.id, user=self.sender, reason="Cannot make it")
        self.request.refresh_from_db()
        self.assertEqual(self.request.cancellation_requested_by, self.sender)
        self.assertEqual(self.request.cancellation_reason, "Cannot make it")
        self.assertTrue(self.request.is_cancellation_pending)
        self.assertEqual(self.request.status, 'ACCEPTED')
        self.assertTrue(self.request.is_escrowed)

        # Sender cannot confirm their own cancellation request
        with self.assertRaises(ValidationError):
            services.confirm_cancellation(self.request.id, user=self.sender)

        # Receiver consents and confirms cancellation
        services.confirm_cancellation(self.request.id, user=self.receiver)
        self.sender.refresh_from_db()
        self.request.refresh_from_db()

        # Sender is refunded, status is CANCELED, escrow released
        self.assertEqual(self.sender.time_balance, 10.0)
        self.assertEqual(self.request.status, 'CANCELED')
        self.assertFalse(self.request.is_escrowed)
        self.assertIsNone(self.request.cancellation_requested_by)
        self.assertFalse(self.request.is_cancellation_pending)

    def test_receiver_declines_cancellation_request(self):
        services.lock_escrow(self.request.id)
        services.request_cancellation(self.request.id, user=self.sender, reason="Emergency")
        self.request.refresh_from_db()
        self.assertTrue(self.request.is_cancellation_pending)

        # Receiver declines cancellation
        services.withdraw_cancellation(self.request.id, user=self.receiver)
        self.request.refresh_from_db()
        self.sender.refresh_from_db()

        # Exchange remains accepted, funds remain in escrow
        self.assertFalse(self.request.is_cancellation_pending)
        self.assertEqual(self.request.status, 'ACCEPTED')
        self.assertTrue(self.request.is_escrowed)
        self.assertEqual(self.sender.time_balance, 8.0)

    def test_sender_withdraws_cancellation_request(self):
        services.lock_escrow(self.request.id)
        services.request_cancellation(self.request.id, user=self.sender)
        self.request.refresh_from_db()
        self.assertTrue(self.request.is_cancellation_pending)

        # Sender withdraws their own cancellation request
        services.withdraw_cancellation(self.request.id, user=self.sender)
        self.request.refresh_from_db()
        self.assertFalse(self.request.is_cancellation_pending)
        self.assertEqual(self.request.status, 'ACCEPTED')

    def test_receiver_direct_cancel_accepted_request(self):
        # If receiver (provider) cancels, receiver consent is inherently granted
        services.lock_escrow(self.request.id)
        services.cancel_request(self.request.id, user=self.receiver)

        self.sender.refresh_from_db()
        self.request.refresh_from_db()
        self.assertEqual(self.sender.time_balance, 10.0) # Refunded to sender
        self.assertEqual(self.request.status, 'CANCELED')
        self.assertFalse(self.request.is_escrowed)

    def test_unauthorized_user_cancellation_attempt(self):
        services.lock_escrow(self.request.id)
        third_party = User.objects.create_user(username='intruder', password='pwd', time_balance=0.0)
        
        with self.assertRaises(ValidationError):
            services.request_cancellation(self.request.id, user=third_party)

        with self.assertRaises(ValidationError):
            services.cancel_request(self.request.id, user=third_party)


class BarterViewsTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender_user', password='password123', time_balance=10.0)
        self.receiver = User.objects.create_user(username='receiver_user', password='password123', time_balance=5.0)
        self.skill = Skill.objects.create(user=self.receiver, title='Web Dev', description='Django web app')
        
        self.request = BarterRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            skill=self.skill,
            hours=3,
            status='PENDING'
        )

    def test_view_cancel_pending_request(self):
        self.client.login(username='sender_user', password='password123')
        response = self.client.post(f'/barter/cancel/{self.request.id}/')
        self.assertRedirects(response, '/barter/sent/')
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'CANCELED')

    def test_view_unilateral_cancel_accepted_blocked(self):
        # Accept request
        services.lock_escrow(self.request.id)
        
        self.client.login(username='sender_user', password='password123')
        response = self.client.post(f'/barter/cancel/{self.request.id}/', follow=True)
        self.assertRedirects(response, '/barter/sent/')
        
        # Verify error message present and status NOT canceled
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'ACCEPTED')
        self.assertTrue(self.request.is_escrowed)
        messages = list(response.context['messages'])
        self.assertTrue(any("cannot be unilaterally canceled" in m.message for m in messages))

    def test_view_request_and_confirm_cancellation(self):
        services.lock_escrow(self.request.id)

        # Sender requests cancellation
        self.client.login(username='sender_user', password='password123')
        res = self.client.post(f'/barter/request-cancellation/{self.request.id}/', {'cancellation_reason': 'Need to reschedule'}, follow=True)
        self.assertRedirects(res, '/barter/sent/')
        self.request.refresh_from_db()
        self.assertEqual(self.request.cancellation_requested_by, self.sender)
        self.assertEqual(self.request.cancellation_reason, 'Need to reschedule')

        # Receiver confirms cancellation
        self.client.login(username='receiver_user', password='password123')
        res = self.client.post(f'/barter/confirm-cancellation/{self.request.id}/', follow=True)
        self.assertRedirects(res, '/barter/received/')

        self.request.refresh_from_db()
        self.sender.refresh_from_db()
        self.assertEqual(self.request.status, 'CANCELED')
        self.assertFalse(self.request.is_escrowed)
        self.assertEqual(self.sender.time_balance, 10.0)

    def test_view_withdraw_cancellation(self):
        services.lock_escrow(self.request.id)
        services.request_cancellation(self.request.id, user=self.sender)

        self.client.login(username='sender_user', password='password123')
        res = self.client.post(f'/barter/withdraw-cancellation/{self.request.id}/', follow=True)
        self.assertRedirects(res, '/barter/sent/')

        self.request.refresh_from_db()
        self.assertFalse(self.request.is_cancellation_pending)
        self.assertEqual(self.request.status, 'ACCEPTED')

