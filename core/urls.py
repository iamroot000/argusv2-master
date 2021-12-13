from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required
from django.views import View


urlpatterns = [
    url(r'^redisconfig/', login_required(views.redisconfig.as_view()), name='redisconfig'),
]

