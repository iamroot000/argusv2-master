from django.conf.urls import url,include
from . import views
from django.contrib.auth.decorators import login_required
from django.views import View


urlpatterns = [
    url(r'^ssladded$', views.add_sslchecker, name="addSSLChecker"),
	
    url(r'^$', login_required(views.index.as_view()), name='index_domains'),

    url(r'^eye/$', login_required(views.eye_index.as_view()), name='eye'),
    url(r'^search/(?P<domain>\S+)$', login_required(views.search.as_view()), name='search'),

    url(r'^eye/(?P<business_unit>\S+)', login_required(views.eye_data.as_view()), name='eye_BU'),

    url(r'^bulkprocess/$', login_required(views.bulkProcess.as_view()), name='bulkdomainprocess'),

    url(r'^(?P<domain>\S+)/process', login_required(views.process.as_view()), name='domainprocess'),

    url(r'^(?P<domain>\S+)$', login_required(views.domaininfo.as_view()), name='domaininfo'),
]

