from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='swagger')

prefix = r'^api/v1/'


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^docs/', schema_view, name='swagger'),

    url(prefix, include([
        url(r'^rest-auth/', include('rest_auth.urls')),
        url(r'^accounts/', include('allauth.urls')),
        url(r'^', include("base.urls", namespace="base")),
    ])),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
