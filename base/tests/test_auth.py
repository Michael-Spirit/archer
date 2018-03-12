from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from base.tests.factories import UserFactory

PASSWORD = 'TESTPASSWORD'


class UserAuthTestCase(APITestCase):

    def test_successful_register(self):
        data = {
            'full_name': 'Michael Spirit',
            'email': 'user@example.com',
            'password1': PASSWORD,
            'password2': PASSWORD
        }

        url = reverse('base:register')
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, 201)

    def test_register_with_unexisted_user_type(self):
        data = {
            'full_name': 'Michael Spirit',
            'email': 'user@example.com',
            'password1': PASSWORD,
            'password2': PASSWORD,
            'type': 'STOOPID'
        }

        url = reverse('base:register')
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get('type')[0], 'User type error')

    def test_register_with_existed_user_type(self):
        data = {
            'full_name': 'Michael Spirit',
            'email': 'user@example.com',
            'password1': PASSWORD,
            'password2': PASSWORD,
            'type': 'redactor'
        }

        url = reverse('base:register')
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, 201)

    def test_email_not_unique_register(self):
        data = {
            'full_name': 'Michael Spirit',
            'email': 'user@example.com',
            'password1': PASSWORD,
            'password2': PASSWORD
        }
        data2 = {
            'full_name': 'John Doe',
            'email': 'user@example.com',
            'password1': PASSWORD,
            'password2': PASSWORD
        }

        url = reverse('base:register')
        self.client.post(url, data=data, format='json')
        response = self.client.post(url, data=data2, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['email'],
            ['A user is already registered with this e-mail address.'])

    def test_successful_login(self):
        user = UserFactory(password=PASSWORD)

        url = reverse('rest_login')
        data = {
            'email': user.email,
            'password': PASSWORD
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_fail_login(self):
        user = UserFactory(password=PASSWORD)

        url = reverse('rest_login')
        data = {
            'email': user.email,
            'password': 'NOT_MY_PASSWORD'
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_get_token_after_login(self):
        user = UserFactory(password=PASSWORD)

        url = reverse('rest_login')
        data = {
            'email': user.email,
            'password': PASSWORD
        }

        token = Token.objects.get(user=user)

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.data.get('key'), token.key)
        self.assertEqual(response.status_code, 200)

    def test_token_user_is_correct_user(self):
        user = UserFactory(password=PASSWORD)

        url = reverse('rest_login')
        data = {
            'email': user.email,
            'password': PASSWORD
        }

        response = self.client.post(url, data=data, format='json')

        response_token = Token.objects.get(key=response.data.get('key'))
        token = Token.objects.get(user=user)

        self.assertEqual(response_token, token)
