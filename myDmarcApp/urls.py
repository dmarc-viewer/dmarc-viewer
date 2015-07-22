from django.conf.urls import url

import views

urlpatterns = [
    url(r'edit/$', views.edit, name='edit'),
    url(r'^$', views.index, name='index')
]