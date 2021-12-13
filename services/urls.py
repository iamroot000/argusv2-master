from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^$', login_required(views.index.as_view()), name='index_services'),
  ]
