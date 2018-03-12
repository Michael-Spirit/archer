import factory
from factory.fuzzy import FuzzyChoice

from base.models import User, Post, USER_TYPE_CHOICES

TEST_PASSWORD = 'password'


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: 'user%s@example.com' % n)
    password = factory.PostGenerationMethodCall('set_password', TEST_PASSWORD)
    full_name = factory.Faker('name')
    is_staff = False
    is_active = True
    type = FuzzyChoice([type[0] for type in USER_TYPE_CHOICES])

    class Meta:
        model = User
        django_get_or_create = ('email',)


class PostFactory(factory.django.DjangoModelFactory):
    author = UserFactory()
    body = factory.Faker('text')
    title = factory.Faker('text')
    approved = FuzzyChoice([True, False])

    class Meta:
        model = Post
