"""domainchecker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', domainlist, name='domlist'),
    url(r'^(?P<domainid>[0-9]+)/$', forcecheck, name='fc_id'),
    url(r'^update/$', updatedata, name='update_data'),
    url(r'^add_data/$', addingData, name='adddata'),
    url(r'^delete_data/(?P<domainid>[0-9]+)/$', deleteData, name='deletedata'),
    url(r'^clear_data/(?P<domainid>[0-9]+)/$', clearData, name='cleardata'),

]
