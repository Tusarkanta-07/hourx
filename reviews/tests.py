from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from skills.models import Skill
from barter.models import BarterRequest
from barter import services as barter_services
from .models import Review

User = get_user_model()

class ReviewModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='reviewer_user', password='password123', time_balance=10.0)
        self.receiver = User.objects.create_user(username='provider_user', password='password123', time_balance=5.0)
        self.skill = Skill.objects.create(user=self.receiver, title='Logo Design', description='Design logos')
        self.request = BarterRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            skill=self.skill,
            hours=2,
            status='COMPLETED'
        )

    def test_review_creation_bound_to_transaction(self):
        review = Review.objects.create(
            barter_request=self.request,
            reviewer=self.sender,
            reviewee=self.receiver,
            rating=5,
            comment='Outstanding design service!'
        )
        self.assertEqual(review.barter_request, self.request)
        self.assertEqual(self.request.review, review)
        self.assertIn("5 stars", str(review))
        self.assertIn(str(self.request.id), str(review))

    def test_duplicate_review_on_same_transaction_raises_integrity_error(self):
        Review.objects.create(
            barter_request=self.request,
            reviewer=self.sender,
            reviewee=self.receiver,
            rating=5,
            comment='First review'
        )
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                barter_request=self.request,
                reviewer=self.sender,
                reviewee=self.receiver,
                rating=4,
                comment='Duplicate review spam attempt'
            )


class ReviewViewsTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='client', password='password123', time_balance=10.0)
        self.receiver = User.objects.create_user(username='expert', password='password123', time_balance=5.0)
        self.skill = Skill.objects.create(user=self.receiver, title='Python Mentoring', description='Python coaching')
        
        self.request = BarterRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            skill=self.skill,
            hours=2,
            status='COMPLETED'
        )

    def test_add_review_success(self):
        self.client.login(username='client', password='password123')
        response = self.client.post(f'/reviews/add/{self.request.id}/', {
            'rating': 5,
            'comment': 'Terrific mentor, highly recommend!'
        }, follow=True)
        self.assertRedirects(response, '/barter/sent/')
        
        # Verify review created and bound
        review = Review.objects.get(barter_request=self.request)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.reviewer, self.sender)
        self.assertEqual(review.reviewee, self.receiver)
        self.assertEqual(review.comment, 'Terrific mentor, highly recommend!')

    def test_prevent_review_spam_on_same_transaction(self):
        # Create initial review
        Review.objects.create(
            barter_request=self.request,
            reviewer=self.sender,
            reviewee=self.receiver,
            rating=5,
            comment='Legitimate review'
        )

        self.client.login(username='client', password='password123')
        # Attempt second review on same transaction
        response = self.client.post(f'/reviews/add/{self.request.id}/', {
            'rating': 1,
            'comment': 'Malicious duplicate spam'
        }, follow=True)
        self.assertRedirects(response, '/barter/sent/')
        
        messages = list(response.context['messages'])
        self.assertTrue(any("already been reviewed" in m.message for m in messages))
        self.assertEqual(Review.objects.filter(barter_request=self.request).count(), 1)
        self.assertEqual(Review.objects.get(barter_request=self.request).rating, 5)

    def test_cannot_review_uncompleted_transaction(self):
        pending_req = BarterRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            skill=self.skill,
            hours=1,
            status='PENDING'
        )
        self.client.login(username='client', password='password123')
        response = self.client.post(f'/reviews/add/{pending_req.id}/', {
            'rating': 5,
            'comment': 'Premature review'
        }, follow=True)
        self.assertRedirects(response, '/dashboard/')
        self.assertFalse(Review.objects.filter(barter_request=pending_req).exists())

    def test_non_participant_cannot_review(self):
        intruder = User.objects.create_user(username='intruder', password='password123', time_balance=0.0)
        self.client.login(username='intruder', password='password123')
        response = self.client.post(f'/reviews/add/{self.request.id}/', {
            'rating': 1,
            'comment': 'Intruder review'
        }, follow=True)
        self.assertRedirects(response, '/dashboard/')
        self.assertFalse(Review.objects.filter(reviewer=intruder).exists())

    def test_invalid_rating_rejected(self):
        self.client.login(username='client', password='password123')
        response = self.client.post(f'/reviews/add/{self.request.id}/', {
            'rating': 10,
            'comment': 'Invalid rating score'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.filter(barter_request=self.request).exists())

