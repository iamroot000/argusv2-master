from django.conf.urls import url,include
from . import views
from django.contrib.auth.decorators import login_required
from django.views import View


'''urlpatterns = [
    #url(r'^nginx/data/$', login_required(views.data_nginx.as_view()), name='data-nginx'),

    url(r'^nginx/<type>/$', login_required(views.nginx.as_view()), name='nginx'),
    url(r'^nginx/(?P<hostgroup>\S+)/create/$', login_required(views.createfile.as_view()), name='createfile'),


]'''



urlpatterns = [
    url(r'^(?P<hostgroup>\S+)/create/$', login_required(views.createfile.as_view()), name='create'),
    url(r'^(?P<hostgroup>\S+)/$', login_required(views.nginx.as_view()), name='overview'),

  #  url(r'^httpsdomains/$', login_required(views.https_domains.as_view()), name='httpsdomains'),





]
