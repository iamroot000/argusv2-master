from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required
from django.views import View


urlpatterns = [
    url(r'^overview/$', login_required(views.overview.as_view()), name='LE_overview'),
    #url(r'^data/', login_required(views.data.as_view()), name='data'),
    url(r'^history/(?P<CN>\S+)$',login_required(views.history.as_view()), name='history'),

    url(r'^renew$',login_required(views.renew.as_view()), name='renew'),
    url(r'^update$',login_required(views.update.as_view()), name='update'),
    url(r'^create', login_required(views.create.as_view()), name='create'),
    url(r'^bulkcreate', login_required(views.bulkcreate.as_view()), name='bulk'),
    url(r'^data/', login_required(views.data.as_view()), name='data'),

    url(r'^tester/', login_required(views.tester.as_view()), name='tester'),

    #url(r'^data/listdomains/', login_required(views.listdomains.as_view()), name='listdomains'),
]

