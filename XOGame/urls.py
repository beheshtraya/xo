from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import login, logout
from xo_app.views import index


urlpatterns = [
    url(r'^$', index),
    url(r'^accounts/', include('user_app.urls')),
    url(r'^admin/', admin.site.urls),
]
