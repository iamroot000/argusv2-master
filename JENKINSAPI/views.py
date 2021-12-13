from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponseForbidden, Http404, HttpResponse
from django.contrib import messages
from JENKINSAPI.models import *
from JENKINSAPI.forms import *
from JENKINSAPI.serializers import *
from rest_framework import generics
from argus.mixins import GENERIC_PERMISSION_MIXIN
from django.views import View
from JENKINSAPI.apps import *
import json, os





# Create your views here.
class JenkinsInfoList(generics.ListCreateAPIView):
    lookup_field = "pk"
    serializer_class = JenkinsSerializer


    def get_queryset(self):
        return JenkinsModel.objects.all()


class JenkinsInfoList2(generics.RetrieveUpdateDestroyAPIView):
#    lookup_field = "UPDATE"
    lookup_field = "JOBNUMBER"
    serializer_class = JenkinsSerializerUpdate

    def get_queryset(self):
        return JenkinsModel.objects.all()


class JenkinsHome(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_jenkins'
    template_name = 'JENKINSAPI/index.html'

    def get(self, request):
        jenkins_file = open(os.path.join(settings.BASE_DIR, '{}/jenkins.conf'.format(JenkinsapiConfig.name)), 'r')
        jenkins_conf = json.load(jenkins_file)
        jenkins_conf['jenkins_home'] = request.path
        jenkins_file = open(os.path.join(settings.BASE_DIR, '{}/jenkins.conf'.format(JenkinsapiConfig.name)), 'w')
        json.dump(jenkins_conf, jenkins_file)
        v_astatus = "APPROVED"
        v_rstatus = "REJECTED"
        jenkinspending = JenkinsModel.objects.filter(BUILD_STATUS__in=['PENDING', 'INPROGRESS']).exclude(APPROVER_STATUS=v_rstatus)
        jenkinstobuild = JenkinsModel.objects.filter(APPROVER_STATUS=v_astatus, BUILD_STATUS__in=['PENDING','INPROGRESS'])
        jenkinsbuilt = JenkinsModel.objects.filter(APPROVER_STATUS__in=['REJECTED', 'APPROVED']).exclude(BUILD_STATUS__in=['PENDING', 'INPROGRESS'])
        context = {'jenkinspending': jenkinspending,
                   'jenkinstobuild': jenkinstobuild,
                   'jenkinsbuilt': jenkinsbuilt
                   }
        return render(request, self.template_name, context)



class JenkinsbuildCrumb(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_jenkins_user_om'

    def post(self, request):
        jenkins_file = open(os.path.join(settings.BASE_DIR, '{}/jenkins.conf'.format(JenkinsapiConfig.name)), 'r')
        jenkins_conf = json.load(jenkins_file)
        for argususer in JenkinsUserKeyModel.objects.all():
            if argususer.APPROVER == "argus":
                j_user = argususer.APPROVER
                j_password = argususer.APIKEY
        # j_user = "argus"
        # j_password = "1105f7735b8cd24cf2c01ef9c8b00de44a"
        j_username = request.user.username.replace('.', '_')
        jenkinsid = request.POST['getjenkinsid']
        jenkinsurl = request.POST['getjenkinsurl']
        jenkinsdir = jenkinsurl.split('/')[-2]
        jenkinsname = request.POST['getjenkinsname']
        jenkinsnumber = request.POST['getjenkinsnumber']
        data = JenkinsModel.objects.get(id=jenkinsid)
        data.BUILD_STATUS = "INPROGRESS"
        data.ARGUS_USER = request.user.username
        data.save()

        crumb = requests.get('http://10.167.11.251:8080/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,":",//crumb)', auth=(j_user, j_password)).text
        requests.post('http://jenkins252.sinonet.me/job/{}/job/{}/{}/input/20/proceedEmpty'.format(jenkinsdir, jenkinsname, jenkinsnumber), headers={str(crumb).split(':')[0]:str(crumb).split(':')[1]}, auth=(j_user, j_password))

        return redirect(jenkins_conf['jenkins_home'])



class JenkinsApprove(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_jenkins_user'

    def post(self, request):
        jenkins_file = open(os.path.join(settings.BASE_DIR, '{}/jenkins.conf'.format(JenkinsapiConfig.name)), 'r')
        jenkins_conf = json.load(jenkins_file)
        jenkinsid = request.POST['getjenkinsid']
        v_approver = request.user.username
        v_status = "APPROVED"
        data = JenkinsModel.objects.filter(id=jenkinsid)
        data.update(APPROVER=v_approver, APPROVER_STATUS=v_status)
        return redirect(jenkins_conf['jenkins_home'])



class JenkinsReject(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_jenkins_user'

    def post(self, request):
        jenkins_file = open(os.path.join(settings.BASE_DIR, '{}/jenkins.conf'.format(JenkinsapiConfig.name)), 'r')
        jenkins_conf = json.load(jenkins_file)
        jenkinsid = request.POST['getjenkinsid']
        v_approver = request.user.username
        v_status = "REJECTED"
        data = JenkinsModel.objects.filter(id=jenkinsid)
        data.update(APPROVER=v_approver, APPROVER_STATUS=v_status, BUILD_STATUS=v_status)
        return redirect(jenkins_conf['jenkins_home'])



class JenkinsDelete(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_jenkins_user_om'

    def post(self, request):
        jenkins_file = open(os.path.join(settings.BASE_DIR, '{}/jenkins.conf'.format(JenkinsapiConfig.name)), 'r')
        jenkins_conf = json.load(jenkins_file)
        jenkinsid = request.POST['jenkinsid']
        to_delete = JenkinsModel.objects.get(id=jenkinsid)
        to_delete.delete()
        return redirect(jenkins_conf['jenkins_home'])

