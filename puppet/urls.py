from django.conf.urls import url,include
from . import views
from django.contrib.auth.decorators import login_required
from django.views import View


urlpatterns = [
    url(r'^$', login_required(views.index.as_view()), name='index_puppet'),
    url(r'^history$', login_required(views.history.as_view()), name='history'),
    url(r'^reload', login_required(views.reload.as_view()), name='reload'),
    url(r'^deploy/$', login_required(views.deploy.as_view()), name='deploy'),

    url(r'^(?P<hostgroup>\S+)/generate/$', login_required(views.generate.as_view()), name='generate'),
    url(r'^(?P<hostgroup>\S+)/sync/$', login_required(views.sync.as_view()), name='sync'),
    url(r'^(?P<hostgroup>\S+)/$', login_required(views.hostgroup_index.as_view()), name='hostgroup_index'),

]
