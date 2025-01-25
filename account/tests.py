from django.test import TestCase
from account.models import User

class UserModelTest(TestCase):
    def setUp(self):
        # Set up test data
        self.user_data = {
            'username': 'Geobellz22',
            'email': 'st377126@gmail.com',
            'password': '97160929Hj',
            'name': 'Saheed',
        }

    def test_user_creation(self):
        # Create a user
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            name=self.user_data['name'],
        )
        
        # Assert the user was created with correct details
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertEqual(user.name, self.user_data['name'])

        # Assert default field values
        self.assertTrue(user.is_user)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_verified)

    def test_user_creation_invalid_email(self):
        # Attempt to create a user without an email
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username='InvalidUser',
                email='',
                password='testpassword123',
                name='Invalid User',
            )
