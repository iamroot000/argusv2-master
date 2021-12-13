from django.conf.urls import url
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # SSR servers
    url(r'^$', SSRhome, name='SSR_home'),
    url(r'^SSRcheck/(?P<SSRID>[0-9]+)/$', SSRcheck, name='SSR_check'),
    url(r'^SSRhomedelete/(?P<SSRID>[0-9]+)/$', SSRhomedelete, name='SSR_homedelete'),
    url(r'^SSRhomeadd/$', SSRhomeadd, name='SSR_homeadd'),
    url(r'^SSRhomehistory/$', SSRhomehistory, name='SSR_homehistory'),
    # SSR initialization
    url(r'^initialization/$', SSRinitialization, name='SSR_initialization'),
    url(r'^initialization/SSRhistory/(?P<IPID>[0-9]+)/$', SSRhistorylogs, name='SSR_history'),
    url(r'^initialization/SSRinitlogs/$', SSRinitlogs, name='SSR_initlogs'),
    url(r'^initialization/SSRdel/(?P<SSRID>[0-9]+)/$', SSRdelete, name='SSR_delete'),
    url(r'^initialization/SSRinit/$', SSRinit, name='SSR_init'),
    # SSR port config
    url(r'^configuration/$', SSRconfig, name='SSR_config'),
    url(r'^configuration/SSRconfigrestart/$', SSRconfigrestart, name='SSR_configrestart'),
    url(r'^configuration/SSRconfighistory/(?P<IPID>[0-9]+)/$', SSRconfighistorylogs, name='SSR_confighistory'),
    url(r'^configuration/SSRconfdel/(?P<SSRID>[0-9]+)/$', SSRconfigdelete, name='SSR_configdelete'),
    url(r'^configuration/SSRIDCcheck/(?P<IPsummary>.*)/$', SSRIDCcheck, name='SSR_IDCcheck'),
    url(r'^configuration/SSRconfiglogs/$', SSRconfiglogs, name='SSR_configlogs'),
    # SSR file config
    url(r'^file-configuration/$', SSRfileconfig, name='SSR_fileconfig'),
    url(r'^file-configuration/SSRfileedit/$', SSRfileedit, name='SSR_fileedit'),
    url(r'^file-configuration/SSRfilesave/$', SSRfilsave, name='SSR_filesave'),
    url(r'^file-configuration/SSRfilelogs/(?P<IPID>[0-9]+)/$', SSRfilelogs, name='SSR_filelogs'),
    url(r'^file-configuration/SSRfileupdate/(?P<IPID>[0-9]+)/$', SSRfileupdate, name='SSR_fileupdate'),
    url(r'^file-configuration/SSRfileprevious/(?P<IPID>[0-9]+)/$', SSRfileprevious, name='SSR_fileprevious'),
    url(r'^file-configuration/SSRfileprocesslogs/$', SSRfileprocesslogs, name='SSR_fileprocesslogs'),
    url(r'^file-configuration/SSRfileconfigsync/$', SSRfilesync, name='SSR_filesync'),

]
