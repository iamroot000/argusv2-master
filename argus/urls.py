"""argus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views
from django.contrib.auth.decorators import login_required
from django.views import View



admin.autodiscover()
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.slash, name="rootredir"),
    url(r'^', include('PySAMLSP.urls')),
    url(r'^', include('core.urls')),
    #url(r'^nrmt/', include('nrmt.urls')),
    url(r'domains/', include('domains.urls')),

    url(r'fwdcontrol/', include('fwdcontrol.urls')),
    url(r'LEManager/', include('LEManager.urls')),
    url(r'esync/', include('esync.urls')),
    url(r'puppet/', include('puppet.urls')),
    url(r'smsalerts/', include('smsalerts.urls')),
    url(r'inventory/', include('inventory.urls')),
    url(r'monitoring/', include('monitoring.urls')),
    #url(r'services/', include('services.urls')),

    #url(r'vergil/', include('vergil.urls')),
    url(r'core/', include('core.urls')),

    url(r'proxycontroller/', include('proxycontroller.urls')),

    url(r'^dashboard/$', login_required(views.dashboard.as_view()), name='dashboard'),
    #url(r'^dashboard/geteyestats', login_required(views.geteyestats.as_view()), name='geteyestats'),
    #url(r'^dashboard/getvergilstats', login_required(views.getvergilstats.as_view()), name='getvergilstats'),
    #url(r'^dashboard/tester', login_required(views.tester.as_view()), name='tester'),

    url(r'vpn-manager/', include('SSRCHECKER.urls')),
    url(r'ssl-checker/', include('SSLDOMAINS.urls')),
    url(r'cdn-checker/', include('cdn.urls')),
    url(r'domainexpiry/', include('domainexpiry.urls')),

]

'''
import urls

def show_urls(urllist, depth=0):
    for entry in urllist:
        print "  " * depth, entry.regex.pattern
        if hasattr(entry, 'url_patterns'):
            show_urls(entry.url_patterns, depth + 1)

show_urls(urls.urlpatterns)

'''

from django.conf.urls import (
handler400, handler403, handler404, handler500
)

handler400 = 'argus.views.bad_request'
handler403 = 'argus.views.permission_denied'
handler404 = 'argus.views.page_not_found'
handler500 = 'argus.views.server_error'

