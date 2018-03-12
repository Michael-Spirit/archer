from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer as DefaultRegisterSerializer
from rest_framework.compat import authenticate

from base.models import User, USER_TYPE_CHOICES, Post


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    is_staff = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    token = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'email', 'token', 'full_name', 'type', 'is_staff', 'is_active')


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    approved = serializers.BooleanField(required=False)
    title = serializers.CharField(required=False)
    body = serializers.CharField(required=False)

    class Meta:
        model = Post
        fields = ('id', 'author', 'approved', 'title', 'body', 'created_at')

    def create(self, validated_data):
        return Post.objects.create(author=self.context['request'].user, **validated_data)

    def approve(self):
        self.instance.approved = True
        self.instance.save()
        return self.instance


class RegisterSerializer(DefaultRegisterSerializer):
    type = serializers.CharField(required=False)

    def validate_type(self, type):
        if type not in USER_TYPE_CHOICES:
            raise serializers.ValidationError(_("User type error"))
        return type
