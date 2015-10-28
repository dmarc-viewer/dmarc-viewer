from django.conf.urls import url
from django.views.generic import RedirectView

import views

urlpatterns = [
    url(r'add-view/$', views.edit, name='add_view'),
    url(r'edit-view/(?P<view_id>[0-9]+)/$', views.edit, name='edit_view'),
    url(r'clone-view/(?P<view_id>[0-9]+)/$', views.clone, name='clone_view'),
    url(r'delete-view/(?P<view_id>[0-9]+)/$', views.delete, name='delete_view'),
    url(r'get-table/(?P<view_id>[0-9]+)/$', views.get_table, name='get_table'),
    url(r'export-svg/(?P<view_id>[0-9]+)/$', views.export_svg, name='export_svg'),
    url(r'export-csv/(?P<view_id>[0-9]+)/$', views.export_csv, name='export_csv'),
    url(r'order-views/$', views.order, name='order_views'),
    url(r'deep-analysis/$', views.deep_analysis, name='deep_analysis'),
    url(r'deep-analysis/(?P<view_id>[0-9]+)/$', views.deep_analysis, name='deep_analysis'),
    url(r'view-management/$', views.view_management, name='view_management'),
    url(r'help/$', views.help, name='help'),
    url(r'overview/$', views.overview, name='overview'),
    url(r'^$', RedirectView.as_view(pattern_name='overview'))
]