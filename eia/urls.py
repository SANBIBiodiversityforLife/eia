"""eia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from core import views, spreadsheet_creation
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django allauth
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/$', login_required(views.TemplateView.as_view(template_name='account/profile.html')), name='profile_detail'),
    url(r'^accounts/profile/(?P<pk>[0-9]+)$', login_required(views.TemplateView.as_view(template_name='account/profile.html')), name='profile_detail'),
    url(r'^accounts/profile/edit$', login_required(views.ProfileUpdate.as_view()), name='profile_update'),
    url(r'^accounts/profile/request_status/(?P<status>request_(trusted|contributor))/$', login_required(views.request_status), name='request_status'),

    # Admin section
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/reset_taxonomy/$', login_required(spreadsheet_creation.reset_taxa_tree), name='admin_reset_taxa_tree'),

    # Front page
    url(r'^$', views.index, name='index'),

    #url(r'^projects/(?P<developer>[\w-]+)/$', login_required(views.ProjectList.as_view()), name='project_list'),
    url(r'^projects/$', login_required(views.project_list), name='projects_list'),
    url(r'^projects-map/$', login_required(views.projects_map), name='projects_map'),

    # Project related URLs
    #url(r'^project/(?P<pk>[0-9]+)/$', views.ProjectDetail.as_view(), name='project_detail'),
    url(r'^project/(?P<pk>[0-9]+)/$', login_required(views.project_detail), name='project_detail'),
    url(r'^project/create/$', login_required(views.ProjectCreate.as_view()), name='project_create'),
    url(r'^project/update/(?P<pk>[0-9]+)/$', login_required(views.ProjectUpdate.as_view()), name='project_update'),
    url(r'^project/update-operational/(?P<pk>[0-9]+)/$', login_required(views.ProjectUpdateOperationalInfo.as_view()), name='project_update_operational_info'),

    # Data view URLS
    url(r'^project/(?P<pk>[0-9]+)/population_data/$', login_required(views.population_data), name='population_data'),
    url(r'^project/(?P<pk>[0-9]+)/population_data/(?P<metadata_pk>[0-9]+)$', login_required(views.population_data), name='population_data'),
    url(r'^project/(?P<pk>[0-9]+)/focal_site_data/$', login_required(views.focal_site_data), name='focal_site_data'),
    url(r'^project/(?P<pk>[0-9]+)/focal_site_data/(?P<focal_site_pk>[0-9]+)/$', login_required(views.focal_site_data), name='focal_site_data'),
    url(r'^project/(?P<pk>[0-9]+)/focal_site_data/(?P<focal_site_pk>[0-9]+)/(?P<metadata_pk>[0-9]+)$', login_required(views.focal_site_data), name='focal_site_data'),
    url(r'^project/(?P<pk>[0-9]+)/fatality_data/$', login_required(views.fatality_data), name='fatality_data'),
    url(r'^project/(?P<pk>[0-9]+)/fatality_data/(?P<metadata_pk>[0-9]+)$', login_required(views.fatality_data), name='fatality_data'),

    # Flag for removal
    url(r'^project/(?P<pk>[0-9]+)/(?P<metadata_pk>[0-9]+)/flag_for_removal$', login_required(views.flag_for_removal), name='flag_for_removal'),

    # Add a document
    url(r'^project/(?P<pk>[0-9]+)/(?P<metadata_pk>[0-9]+)/add_metadata_document$', login_required(views.add_metadata_document), name='add_metadata_document'),

    # Developer
    url(r'^developer/create/$', login_required(views.DeveloperCreate.as_view()), name='developer_create'),
    url(r'^developer/(?P<pk>[0-9]+)/$', login_required(views.DeveloperDetail.as_view()), name='developer_detail'),

    # Turbine
    url(r'^equipment/create/$', login_required(views.EquipmentMakeCreate.as_view()), name='equipment_make_create'),

    # Focal site
    url(r'^project/(?P<project_pk>[0-9]+)/focal_site_data/focal_site/create/$',
        login_required(views.FocalSiteCreate.as_view()), name='focal_site_create'),

    # Data add URLs
    url(r'^project/(?P<project_pk>[0-9]+)/population_data/create/',
        login_required(views.population_data_create),
        name='population_data_create'),
    #url(r'^project/(?P<project_pk>[0-9]+)/population_data/create/',
    #    login_required(views.PopulationDataCreateView.as_view()),
    #    name='population_data_create'),
    url(r'^project/(?P<project_pk>[0-9]+)/focal_site_data/focal_site/(?P<focal_site_pk>[0-9]+)/create/',
        login_required(views.focal_site_data_create),
        name='focal_site_data_create'),
    url(r'^project/(?P<project_pk>[0-9]+)/fatality_data/create/',
        login_required(views.fatality_data_create),
        name='fatality_data_create'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
