# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404,redirect

from django.views.decorators.csrf import csrf_exempt
from samlsp import samuelSP
import urllib
from django.contrib.auth import authenticate,login
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import logout as django_logout
import ast
from django.contrib.auth.models import Group,User

from django.contrib.auth.models import Permission


# Create your views here.

try:
    urlencoder = urllib.urlencode
except:
    urlencoder = urllib.parse.urlencode


sp = samuelSP(settings.CERTPEM,settings.LOGIN_IDP_ENDPOINT,settings.LOGIN_PROVIDER,settings.LOGIN_ISSUER)

def auth(request):

    if request.user.is_anonymous():
        params = {"SAMLRequest": sp.genAuthnRequest(settings.LOGIN_ACS_URL)}
        return redirect(settings.LOGIN_IDP_ENDPOINT + '?' + urllib.urlencode(params))
    return redirect(settings.LOGIN_REDIRECT_URL)


def login_sp(request):
    if settings.DEBUG:
#        user = User.objects.get(username='aaron.navarro')
        user = User.objects.get(username='yroll.macalino')
        auths = authenticate(user)
        login(request, auths)


        request.session['permissions'] = [x.codename for x in Permission.objects.filter(user=request.user)]

        for i in request.user.groups.all():
            [request.session['permissions'].append(perm.codename) if perm.codename not in request.session[
                'permissions'] else False for perm in i.permissions.all()]

            if not 'groups' in request.session:
                request.session['groups'] = []
            request.session['groups'].append(i.name)

        request.session.modified = True

    if not request.user.is_authenticated():
        return render(request,'login.html')
    return redirect(settings.LOGIN_REDIRECT_URL)


def logout(request):
    django_logout(request)
    return redirect(settings.LOGIN_URL)

@csrf_exempt
def acs(request):

    if request.method =='POST':
        samlResponse = request.POST.get('SAMLResponse')
        response = sp.decodeAndValidate(samlResponse)
        if response is not None:
            user = sp.getName(response)
            attr = sp.getAttributeList(response)

            if user is not None:
                auths = authenticate(user)
                if auths is not None:
                    login(request,auths)
                    if attr:
                        request.session['attr'] = attr
                        request.session['attr']['dept']=ast.literal_eval(attr['dept'])
                        #### NEW IMPLEMENTATION REMOVE THE 2 PRECEDING LINES AFTER THIS IS OK

                        request.session['permissions'] = [x.codename for x in Permission.objects.filter(user=request.user)]
                        ### IF NEW USER ADD USER TO GROUP
                        for i in request.session['attr']['dept']:
                            try:
                                grp = '{0}-GROUP'.format(i.upper())
                                group = Group.objects.get(name=grp)
                                if grp not in [i.name for i in request.user.groups.all()]:
                                    group.user_set.add(request.user)
                            except Exception as e:
                                print e


                        for i in request.user.groups.all():
                            [request.session['permissions'].append(perm.codename) if perm.codename not in request.session['permissions'] else False for perm in i.permissions.all()]

                            if not 'groups' in request.session:
                                request.session['groups']=[]
                            request.session['groups'].append(i.name)

                        request.session.modified=True


                    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    return redirect('auth')
