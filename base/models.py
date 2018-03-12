from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from model_utils import Choices


USER_TYPE_CHOICES = Choices(
    ('journalist', 'journalist', _('journalist')),
    ('redactor', 'redactor', _('redactor')),
    ('default', 'default', _('default')))


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    password = models.CharField(_('password'), max_length=128, null=True, blank=True)
    full_name = models.CharField(_('full name'), max_length=30)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active status'), default=False)
    type = models.CharField(
        _("Account type"),
        choices=USER_TYPE_CHOICES,
        default=USER_TYPE_CHOICES.default,
        max_length=11,
        null=True,
        blank=True)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return f'{self.full_name}'

    def get_short_name(self):
        return self.get_full_name()

    @property
    def token(self):
        """
        Returns token API key.

        :rtype: str
        """
        return Token.objects.get(user=self).key


class Post(models.Model):
    author = models.ForeignKey(
        "base.User",
        verbose_name=_('Journalist post'),
        related_name='posts',
        on_delete=models.CASCADE
    )
    title = models.CharField(verbose_name=_('Post title'), max_length=256)
    body = models.TextField(verbose_name=_('Post body'))
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
