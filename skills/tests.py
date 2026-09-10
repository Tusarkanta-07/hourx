from django.test import TestCase
from django.contrib.auth import get_user_model
from reviews.models import Review
from barter.models import BarterRequest
from .models import Skill

User = get_user_model()

class SkillMarketplaceTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='expert_dev', password='password123', time_balance=10.0)
        self.user2 = User.objects.create_user(username='novice_dev', password='password123', time_balance=10.0)
        self.reviewer = User.objects.create_user(username='client_reviewer', password='password123', time_balance=10.0)

        # Create transactions and reviews
        # User 1 has 5-star review
        req1 = BarterRequest.objects.create(
            sender=self.reviewer, receiver=self.user1,
            skill=Skill.objects.create(user=self.user1, title='Django Architecture', description='Deep Django', category='Development'),
            hours=2, status='COMPLETED'
        )
        Review.objects.create(barter_request=req1, reviewer=self.reviewer, reviewee=self.user1, rating=5, comment='Superb!')

        # User 2 has 2-star review
        req2 = BarterRequest.objects.create(
            sender=self.reviewer, receiver=self.user2,
            skill=Skill.objects.create(user=self.user2, title='Basic HTML', description='HTML basics', category='Development'),
            hours=1, status='COMPLETED'
        )
        Review.objects.create(barter_request=req2, reviewer=self.reviewer, reviewee=self.user2, rating=2, comment='Needs work')

    def test_rating_filtering(self):
        # Filter min_rating = 4.0: only user1's skill should appear
        res = self.client.get('/skills/?min_rating=4.0')
        self.assertEqual(res.status_code, 200)
        skills = res.context['skills'].object_list
        titles = [s.title for s in skills]
        self.assertIn('Django Architecture', titles)
        self.assertNotIn('Basic HTML', titles)

        # Filter min_rating = 2.0: both skills should appear
        res2 = self.client.get('/skills/?min_rating=2.0')
        self.assertEqual(res2.status_code, 200)
        titles2 = [s.title for s in res2.context['skills'].object_list]
        self.assertIn('Django Architecture', titles2)
        self.assertIn('Basic HTML', titles2)

    def test_category_and_search_filtering(self):
        Skill.objects.create(user=self.user1, title='Logo Illustration', description='Vector art', category='Design')
        
        # Category filter
        res_cat = self.client.get('/skills/?category=Design')
        self.assertEqual(res_cat.status_code, 200)
        titles = [s.title for s in res_cat.context['skills'].object_list]
        self.assertIn('Logo Illustration', titles)
        self.assertNotIn('Django Architecture', titles)

        # Search query
        res_search = self.client.get('/skills/?q=Illustration')
        self.assertEqual(res_search.status_code, 200)
        search_titles = [s.title for s in res_search.context['skills'].object_list]
        self.assertIn('Logo Illustration', search_titles)
        self.assertNotIn('Django Architecture', search_titles)

    def test_marketplace_pagination(self):
        # Create 12 more skills to test pagination (total will be 14 skills)
        for i in range(12):
            Skill.objects.create(user=self.user1, title=f'Extra Skill {i}', description='Desc', category='Writing')

        # Page 1 should contain 9 skills
        res_p1 = self.client.get('/skills/?page=1')
        self.assertEqual(res_p1.status_code, 200)
        self.assertEqual(len(res_p1.context['skills']), 9)
        self.assertTrue(res_p1.context['skills'].has_next())
        self.assertFalse(res_p1.context['skills'].has_previous())

        # Page 2 should contain remaining 5 skills (14 total)
        res_p2 = self.client.get('/skills/?page=2')
        self.assertEqual(res_p2.status_code, 200)
        self.assertEqual(len(res_p2.context['skills']), 5)
        self.assertTrue(res_p2.context['skills'].has_previous())
        self.assertFalse(res_p2.context['skills'].has_next())

        # Non-integer page returns page 1
        res_invalid = self.client.get('/skills/?page=invalid')
        self.assertEqual(res_invalid.context['skills'].number, 1)

        # Out-of-bounds page returns last page (page 2)
        res_oob = self.client.get('/skills/?page=999')
        self.assertEqual(res_oob.context['skills'].number, 2)


class SkillCRUDTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='author', password='password123', time_balance=10.0)
        self.other_user = User.objects.create_user(username='stranger', password='password123', time_balance=10.0)
        self.skill = Skill.objects.create(user=self.user, title='My Skill', description='Original Desc', category='Music')

    def test_skill_create_authenticated(self):
        self.client.login(username='author', password='password123')
        res = self.client.post('/skills/add/', {
            'title': 'New Guitar Lessons',
            'description': 'Acoustic and electric guitar lessons',
            'category': 'Music'
        })
        self.assertRedirects(res, '/skills/')
        self.assertTrue(Skill.objects.filter(title='New Guitar Lessons').exists())

    def test_skill_edit_own(self):
        self.client.login(username='author', password='password123')
        res = self.client.post(f'/skills/{self.skill.pk}/edit/', {
            'title': 'My Skill Updated',
            'description': 'Updated Desc',
            'category': 'Music'
        })
        self.assertRedirects(res, f'/skills/{self.skill.pk}/')
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.title, 'My Skill Updated')

    def test_skill_delete_own(self):
        self.client.login(username='author', password='password123')
        res = self.client.post(f'/skills/{self.skill.pk}/delete/')
        self.assertRedirects(res, '/skills/')
        self.assertFalse(Skill.objects.filter(pk=self.skill.pk).exists())

    def test_skill_detail(self):
        res = self.client.get(f'/skills/{self.skill.pk}/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'My Skill')

