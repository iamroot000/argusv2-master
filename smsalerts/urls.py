from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^$', login_required(views.index.as_view()), name='index_smsalerts'),
    url(r'^ajax/contacts$', login_required(views.ajaxContacts.as_view()), name='contacts endpoint'),
    url(r'^ajax/announcers$', login_required(views.ajaxAnnouncers.as_view()), name='announcers endpoint'),
    url(r'^ajax/groups$', login_required(views.ajaxGroups.as_view()), name='groups endpoint'),
]
