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
from core import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Django allauth
    url(r'^accounts/', include('allauth.urls')),

    # Admin section
    url(r'^admin/', include(admin.site.urls)),

    # Front page
    url(r'^$', views.index, name='index'),

    #url(r'^projects/(?P<developer>[\w-]+)/$', login_required(views.ProjectList.as_view()), name='project_list'),
    url(r'^projects$', login_required(views.project_list), name='project_list'),

    # Project related URLs
    #url(r'^project/(?P<pk>[0-9]+)/$', views.ProjectDetail.as_view(), name='project_detail'),
    url(r'^project/(?P<pk>[0-9]+)/$', views.project_detail, name='project_detail'),
    url(r'^project/create/$', login_required(views.ProjectCreate.as_view()), name='project_create'),
    url(r'^project/update/(?P<pk>[0-9]+)/$', login_required(views.ProjectUpdate.as_view()), name='project_update'),
    url(r'^project_delete/(?P<pk>[0-9]+)/$', login_required(views.ProjectDelete.as_view()), name='project_delete'),

    # Developer
    url(r'^developer/create/$', login_required(views.DeveloperCreate.as_view()), name='developer_create'),

    # Data related URLs
    url(r'^project/(?P<project_pk>[0-9]+)/data/', login_required(views.DataList.as_view()), name='data_list'),
    url(r'^project/(?P<project_pk>[0-9]+)/population_data/create/',
        login_required(views.PopulationDataCreateView.as_view()),
        name='population_data_create'),
    #url(r'^project/(?P<project_pk>[0-9]+)/population_data/create/', views.create_population_data, name='population_data_create'),

    url(r'^focal_site/create/$', login_required(views.FocalSiteCreate.as_view()), name='focal_site_create'),
    url(r'^focal_site_data/create/$', login_required(views.FocalSiteDataCreate.as_view()), name='focal_site_data_create'),
]
