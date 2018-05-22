"""
<Program Name>
    urls.py

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    Jul 22, 2015

<Copyright>
    See LICENSE for licensing information.

<Purpose>
    Website (app) URL dispatcher. Defines routes for all dmarc_viewer views

"""

from django.conf.urls import url
from django.views.generic import RedirectView

import views

urlpatterns = [
    # Index, Overview
    url(r'^$', RedirectView.as_view(pattern_name='overview', permanent=False)),
    url(r'overview/$', views.overview, name='overview'),
    url(r'overview-async/$', views.overview_async, name='overview_async'),

    # Analysis, Data, Export
    url(r'deep-analysis/$', views.deep_analysis_first,
            name='deep_analysis_first'),
    url(r'deep-analysis/(?P<view_id>[0-9]+)/$', views.deep_analysis,
            name='deep_analysis'),
    url(r'map-async/(?P<view_id>[0-9]+)/$', views.map_async, name='map_async'),
    url(r'line-async/(?P<view_id>[0-9]+)/$', views.line_async,
            name='line_async'),
    url(r'table-async/(?P<view_id>[0-9]+)/$', views.table_async,
            name='table_async'),
    url(r'export-svg/(?P<view_id>[0-9]+)/$', views.export_svg,
            name='export_svg'),
    url(r'export-csv/(?P<view_id>[0-9]+)/$', views.export_csv,
            name='export_csv'),

    # View Management, View Editor
    url(r'add-view/$', views.edit, name='add_view'),
    url(r'edit-view/(?P<view_id>[0-9]+)/$', views.edit,name='edit_view'),
    url(r'clone-view/(?P<view_id>[0-9]+)/$', views.clone, name='clone_view'),
    url(r'delete-view/(?P<view_id>[0-9]+)/$', views.delete,
            name='delete_view'),
    url(r'order-views/$', views.order, name='order_views'),
    url(r'view-management/$', views.view_management, name='view_management'),
    url(r'delete-view/(?P<view_id>[0-9]+)/$', views.delete,
            name='delete_view'),
    url(r'choices-async/$', views.choices_async, name='choices_async'),

    #Help, FAQ
    url(r'help/$', views.help_page, name='help')
]
