from django.conf.urls import url

import views

urlpatterns = [
    url(r'add-view/$', views.edit, name='add_view'),
    url(r'edit-view/(?P<view_id>[0-9]+)/$', views.edit, name='edit_view'),
    url(r'clone-view/(?P<view_id>[0-9]+)/$', views.edit, {'clone': True}, name='clone_view'),
    url(r'delete-view/(?P<view_id>[0-9]+)/$', views.delete_view, name='delete_view'),
    url(r'deep-analysis/$', views.deep_analysis, name='deep_analysis'),
    url(r'deep-analysis/(?P<view_id>[0-9]+)/$', views.deep_analysis, name='deep_analysis'),
    url(r'view-management/$', views.view_management, name='view_management'),
    url(r'help/$', views.help, name='help'),
    url(r'^$', views.index, name='index')
]