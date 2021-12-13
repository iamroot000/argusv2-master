from django.conf.urls import url,include
from . import views
from . import viewsv2
from . import views_initializer

from django.contrib.auth.decorators import login_required
from django.views import View


urlpatterns = [

    ###NEWSHIT
    #url(r'^(?P<host>\S+)/(?P<application>\S+)/(?P<hostgroup>\S+)/ssl/link', login_required(viewsv2.link.as_view()),name='esync_ssl_link'),
    #url(r'^(?P<host>\S+)/(?P<application>\S+)/(?P<hostgroup>\S+)/ssl/unlink', login_required(viewsv2.unlink.as_view()),name='esync_ssl_unlink'),
    #url(r'^(?P<host>\S+)/(?P<application>\S+)/(?P<hostgroup>\S+)/$', login_required(viewsv2.control.as_view()), name='esync_filecontrol'),
    #url(r'^templates/(?P<application>\S+)', login_required(viewsv2.templates.as_view()),name='esync_templates'),
    #url(r'^homeshit/$', login_required(viewsv2.index.as_view()),name='esync_index'),


    ###INITIALIZER
    url(r'^initiald/start$', login_required(views_initializer.start_init.as_view()), name='esync_start_init'),
    url(r'^initiald/$', login_required(views_initializer.index.as_view()), name='esync_initializer'),

    ###OLDSHIT
    url(r'^$', login_required(views.index.as_view()), name='index_esync'),
    url(r'^history$', login_required(views.history.as_view()), name='history'),
    url(r'^tester', login_required(views.tester.as_view()), name='tester'),
    url(r'^reload', login_required(views.reload.as_view()), name='reload'),

    url(r'^deploy/$', login_required(views.deploy.as_view()), name='deploy'),

    url(r'^(?P<hostgroup>\S+)/generate/$', login_required(views.generate.as_view()), name='generate'),
    url(r'^(?P<hostgroup>\S+)/delete/$', login_required(views.delete.as_view()), name='delete'),
    url(r'^(?P<hostgroup>\S+)/link/$', login_required(views.link.as_view()), name='link'),
    #url(r'^(?P<hostgroup>\S+)/api/$', views.api, name='mynigga'),
    url(r'^(?P<hostgroup>\S+)/check/$', login_required(views.check.as_view()), name='check'),
    url(r'^(?P<hostgroup>\S+)/sync/$', login_required(views.sync.as_view()), name='sync'),
    url(r'^(?P<hostgroup>\S+)/clear/$', login_required(views.clear_cache.as_view()), name='clear'),
    url(r'^(?P<hostgroup>\S+)/$', login_required(views.hostgroup_index.as_view()), name='hostgroup_index'),

]
