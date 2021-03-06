from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from home.views import home_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    url(r'^$', home_view, name = 'home'),

    url(r'^home/', include('home.urls', namespace="home")),

    url(r'^photo/', include('photo.urls', namespace="photo")),

    url(r'^contest/', include('contest.urls')),

    url(r'^user/', include('user.urls')),

    url(r'^admin/', admin.site.urls),

    path('api/report-photo/', include('reportedPhotos.api.urls', namespace='reportedPhotos_api')),
    path('api/photo/', include('photo.api.urls', namespace='photo_api')),
    path('api/user/', include('user.api.urls', namespace='user_api')),
    path('api/contest/', include('contest.api.urls', namespace='contest_api')),

    path('oauth/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
