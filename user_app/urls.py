from django.conf.urls import url
import user_app.views

urlpatterns = [
    url(r'^login/$', user_app.views.login, name='login'),
    url(r'^logout/$', user_app.views.logout, name='logout'),
    url(r'^register/$', user_app.views.register, name='register'),
]
