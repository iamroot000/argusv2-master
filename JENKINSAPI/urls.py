from django.conf.urls import url, include
from JENKINSAPI.views import *
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^jenkins-home/$', login_required(JenkinsHome.as_view()), name="jenkins_home"),
    url(r'^jenkins-build/$', login_required(JenkinsbuildCrumb.as_view()), name="jenkins_build"),
    url(r'^jenkins-verify/jenkins-approve/$', login_required(JenkinsApprove.as_view()), name="jenkins_approve"),
    url(r'^jenkins-verify/jenkins-reject/$', login_required(JenkinsReject.as_view()), name="jenkins_reject"),
    url(r'^jenkinsdelete/$', login_required(JenkinsDelete.as_view()), name="jenkins_delete"),
#    url(r'^jenkinsupdate/(?P<UPDATE>[-\w]+)/$', JenkinsInfoList2.as_view()),
    url(r'^jenkinsupdate/(?P<JOBNUMBER>[-\w]+)/$', JenkinsInfoList2.as_view()),
    url(r'^jenkinscreate/$', JenkinsInfoList.as_view())
]
