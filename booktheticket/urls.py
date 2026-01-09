from django.contrib import admin
from django.urls import path, include
from movies.views import movie_list
from django.conf import settings
from django.conf.urls.static import static
from users.views import home

urlpatterns = [

    path('', home, name='home'),
    path('movies/', include('movies.urls')),
    path('users/', include('users.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
