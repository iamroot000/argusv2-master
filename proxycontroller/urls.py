from django.conf.urls import url,include
from . import views
from django.contrib.auth.decorators import login_required
from django.views import View


urlpatterns = [
    url(r'^$', login_required(views.index.as_view()), name='index_proxycontroller'),


    url(r'^servers/(?P<server>\S+)/', login_required(views.server.as_view()), name='domainprocess'),

    url(r'^servers/$', login_required(views.servers.as_view()), name='servers_proxycontroller'),

    url(r'^dashboard/$', login_required(views.dashboard.as_view()), name='dashboard_proxycontroller'),

    url(r'^process/$', login_required(views.process.as_view()), name='serverprocess'),

]
