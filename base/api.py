from rest_auth.registration.urls import RegisterView as BaseRegisterView
from rest_framework import generics, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken as BaseObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.viewsets import GenericViewSet

from django.db.models import Q

from base.serializers import RegisterSerializer, UserSerializer, AuthTokenSerializer, PostSerializer
from base.models import Post, User, USER_TYPE_CHOICES


class RegisterView(BaseRegisterView):
    """
    API call to register new client

    Required fields: email, password

    Not req field: type (journalist, redactor or default)
    """
    serializer_class = RegisterSerializer


class UserAPI(viewsets.ModelViewSet):
    """
        API call to register new client

        Required fields:
            email, password

        Not req field:
            type (journalist, redactor or default)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @list_route(methods=['get', 'patch'])
    def profile(self, request, **kwargs):
        if self.request.method == 'GET':
            user = self.request.user
            serializer = self.get_serializer(instance=user)
            return Response(serializer.data)

        else:
            user = self.request.user
            serializer = self.get_serializer(instance=user, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainUserByToken(generics.RetrieveAPIView, GenericViewSet):
    lookup_field = 'token'
    serializer_class = UserSerializer

    def get_object(self):
        return Token.objects.get(key=self.kwargs.get('token')).user


class ObtainAuthToken(BaseObtainAuthToken):
    """
        API call to obtain user token

        Required fields: email, password
    """
    serializer_class = AuthTokenSerializer


class PostAPI(viewsets.ModelViewSet):
    """
    API call for posts

    Required fields:
        id

    additional routes:

        unapproved_posts/ - search posts with approve=False (for redactors only)
        approve/ - approve post by id (for redactors only)
        find_posts/ - find posts by author_id OR by text in post.body or post.title

    """
    serializer_class = PostSerializer
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        if self.request.user.type == USER_TYPE_CHOICES.redactor:
            queryset = Post.objects.all()
        elif self.request.user.type == USER_TYPE_CHOICES.journalist:
            queryset = Post.objects.filter(Q(approved=True) | Q(author=self.request.user))
        else:
            queryset = Post.objects.filter(approved=True)

        if self.action == 'find_posts':
            text = self.request.GET.get('text')
            user_id = self.request.GET.get('user_id')
            if text:
                queryset = queryset.filter(Q(body__icontains=text) | Q(title__icontains=text))
            if user_id:
                queryset = queryset.filter(author_id=user_id)

        return queryset

    @list_route(methods=['get'])
    def unapproved_posts(self, request, **kwargs):
        if self.request.user.type != USER_TYPE_CHOICES.redactor:
            raise PermissionDenied()

        serializer = self.get_serializer(Post.objects.filter(approved=False), many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def find_posts(self, request, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @detail_route(methods=['patch'])
    def approve(self, request, **kwargs):
        if self.request.user.type != USER_TYPE_CHOICES.redactor:
            raise PermissionDenied()

        serializer = self.get_serializer(instance=self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.approve()
        return Response(data=serializer.data)
