from django.conf.urls import url, include
from . import views
from django.contrib.auth.decorators import login_required
from django.views import View


urlpatterns = [
    url(r'^$', login_required(views.index.as_view()), name='index_inventory'),
    url(r'^data/$', login_required(views.data.as_view()), name='data_inventory'),

    url(r'^sync/$', login_required(views.sync.as_view()), name='sync_inventory'),

]
