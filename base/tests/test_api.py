from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from base.models import USER_TYPE_CHOICES
from base.tests.factories import UserFactory, Post, PostFactory

PASSWORD = 'TESTPASSWORD'


class TestUserAPI(APITestCase):

    def setUp(self):
        self.user = UserFactory(password=PASSWORD)
        self.token = Token.objects.first()

    def test_obtain_auth_token(self):
        data = {
            'email': self.user.email,
            'password': PASSWORD
        }
        url = reverse('base:get_auth_token')
        request = self.client.post(url, data, format='json')
        self.assertEqual(request.data.get('token'), self.token.key)

    def test_not_auth_get_user(self):
        """
        Test unauthorized user permissions
        """
        request = self.client.get(reverse('base:users-list'))
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_profile(self):
        data = {
            'email': self.user.email,
            'password': PASSWORD
        }
        request = self.client.post(reverse('rest_login'), data=data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + request.data.get('key'))
        self.assertEqual(self.user.is_authenticated, True)

        request = self.client.get(reverse('base:users-profile'), format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_get_profile_detail_from_token(self):
        data = {
            'email': self.user.email,
            'password': PASSWORD
        }
        request = self.client.post(reverse('rest_login'), data=data, format='json')
        token_key = request.data.get('key')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token_key)
        self.assertEqual(self.user.is_authenticated, True)

        request = self.client.get(
            reverse('base:token-user-detail', kwargs={'token': token_key}), data=data, format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)


class TestPostAPI(APITestCase):

    def setUp(self):
        self.user = UserFactory(password=PASSWORD, type=USER_TYPE_CHOICES.journalist)
        self.token = Token.objects.first()

    def test_not_auth_user_cannot_create_post(self):
        url = reverse('base:posts-list')
        data = {
            'title': 'Title',
            'body': 'boooooddyyyyy'
        }

        request = self.client.post(url, data, format='json')
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_authed_user_success_create_post(self):
        data = {
            'email': self.user.email,
            'password': PASSWORD
        }
        request = self.client.post(reverse('rest_login'), data=data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + request.data.get('key'))
        self.assertEqual(self.user.is_authenticated, True)

        self.assertEqual(Post.objects.count(), 0)

        data = {
            'title': 'Title',
            'body': 'boooooddyyyyy',
        }

        request = self.client.post(reverse('base:posts-list'), data=data, format='json')
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.first().approved, False)

    def test_redactor_approve_post(self):
        redactor = UserFactory(type=USER_TYPE_CHOICES.redactor, password=PASSWORD)
        token = Token.objects.get(user=redactor)
        data = {
            'email': redactor.email,
            'password': PASSWORD
        }

        request = self.client.post(reverse('rest_login'), data=data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        post = PostFactory(author=self.user, approved=False)
        self.assertEqual(post.approved, False)

        request = self.client.patch(reverse('base:posts-approve', kwargs={'pk': post.pk}))
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        post = Post.objects.first()
        self.assertEqual(post.approved, True)

    def test_author_cant_approve_post(self):
        data = {
            'email': self.user.email,
            'password': PASSWORD
        }

        request = self.client.post(reverse('rest_login'), data=data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        post = PostFactory(author=self.user)
        self.assertEqual(post.approved, False)

        request = self.client.patch(reverse('base:posts-approve', kwargs={'pk': post.pk}))
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Post.objects.first().approved, False)

    def test_find_posts_by_text(self):
        data = {
            'email': self.user.email,
            'password': PASSWORD
        }

        request = self.client.post(reverse('rest_login'), data=data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        post1 = PostFactory(author=self.user, body='test1', title='title1', approved=True)
        post2 = PostFactory(author=self.user, body='SomeBody', title='SomeTitle', approved=True)
        post3 = PostFactory(author=self.user, body='SomeBody', title='SomeTitle', approved=True)

        request = self.client.get(reverse('base:posts-find-posts'), {'text': 'test1'}, format='json')
        self.assertEqual(len(request.data), 1)
        self.assertEqual(request.data[0]['id'], post1.id)

        request = self.client.get(reverse('base:posts-find-posts'), {'text': 'SomeBody'}, format='json')
        self.assertEqual(len(request.data), 2)
        self.assertEqual(request.data[0]['id'], post2.id)
        self.assertEqual(request.data[1]['id'], post3.id)

    def test_find_posts_by_user(self):
        user2 = UserFactory()
        data = {
            'email': self.user.email,
            'password': PASSWORD
        }

        request = self.client.post(reverse('rest_login'), data=data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        post1 = PostFactory(author=self.user, body='test1', title='title1', approved=True)
        post2 = PostFactory(author=user2, body='SomeBody', title='SomeTitle', approved=True)
        post3 = PostFactory(author=user2, body='SomeBody1', title='SomeTitle2', approved=True)

        request = self.client.get(reverse('base:posts-find-posts'), {'user_id': self.user.id}, format='json')
        self.assertEqual(len(request.data), 1)
        self.assertEqual(request.data[0]['id'], post1.id)

        request = self.client.get(reverse('base:posts-find-posts'), {'user_id': user2.id}, format='json')
        self.assertEqual(len(request.data), 2)
        self.assertEqual(request.data[0]['id'], post2.id)
        self.assertEqual(request.data[1]['id'], post3.id)

    def test_not_approved_posts_not_in_search(self):
        user2 = UserFactory()
        data = {
            'email': self.user.email,
            'password': PASSWORD
        }

        request = self.client.post(reverse('rest_login'), data=data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        post1 = PostFactory(author=user2, body='test1', title='title1', approved=False)
        post2 = PostFactory(author=user2, body='SomeBody', title='SomeTitle', approved=True)
        post3 = PostFactory(author=user2, body='SomeBody', title='SomeTitle', approved=False)

        request = self.client.get(reverse('base:posts-find-posts'), {'text': 'test1'}, format='json')
        self.assertEqual(len(request.data), 0)

        request = self.client.get(reverse('base:posts-find-posts'), {'text': 'SomeBody'}, format='json')
        self.assertEqual(len(request.data), 1)
        self.assertEqual(request.data[0]['id'], post2.id)
