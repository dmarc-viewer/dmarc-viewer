from django.conf.urls import url

import views

urlpatterns = [
    url(r'edit/$', views.edit, name='edit'),
    url(r'edit/(?P<view_id>[0-9]+)/$', views.edit, name='edit'),
    url(r'deep-analysis/$', views.deep_analysis, name='deep_analysis'),
    url(r'deep-analysis/(?P<view_id>[0-9]+)/$', views.deep_analysis, name='deep_analysis'),
    url(r'^$', views.index, name='index')
]