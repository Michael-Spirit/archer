from django.conf.urls import url

from base.api import RegisterView, UserAPI, ObtainAuthToken, PostAPI, ObtainUserByToken
from rest_framework import routers

app_name = 'base'

router = routers.DefaultRouter()
router.register(r'users', UserAPI, base_name='users')
router.register(r'user_from_token', ObtainUserByToken, base_name='token-user')
router.register(r'posts', PostAPI, base_name='posts')

urlpatterns = [
    url(r'^auth/registration/', RegisterView.as_view(), name='register'),
    url(r'^get_auth_token/$', ObtainAuthToken.as_view(), name='get_auth_token'),
]

urlpatterns += router.urls
