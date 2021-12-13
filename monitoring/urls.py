from django.conf.urls import url, include
from . import views
from django.contrib.auth.decorators import login_required
from django.views import View


urlpatterns = [
    url(r'^$', login_required(views.index.as_view()), name='index_monitoring'),
    url(r'^graph/(?P<zGraphID>\S+)$', login_required(views.get_zGraph.as_view()), name='getzgraph'),

    url(r'^dashboard/$', login_required(views.dashboard.as_view()), name='dashboard_monitoring'),
    url(r'^events/$', login_required(views.events.as_view()), name='events_monitoring'),
    url(r'^network/$', login_required(views.network.as_view()), name='network_monitoring'),

]
