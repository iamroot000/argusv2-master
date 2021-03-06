# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views import View
from argus.mixins import GENERIC_PERMISSION_MIXIN
from django.http import Http404, HttpResponse, HttpResponseForbidden
from argus.celery import app
import json
import traceback
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from argus.log import log
from lib.nginx_processor import *
from lib.settings import STANDARD_DIRS,OTHER_DIRS

import glob
import os
import time
import threading
from admin import ESYNC_GLOBAL_RESOURCE


from esync.lib.esync_logger import nonstandard_esync_log,standard_esync_log,command_logger
from global_objects.GLOBAL_OBJECTS import ZABBIX

from esync.models import SERVICE_PROVIDERS
from inventory.models import CLOUD_HOST

def check_perm(request,hostgroup):
    access_levels = ESYNC_GLOBAL_RESOURCE.get_access_levels()
    if access_levels[hostgroup]['access_level'] == 'OPEN':
        print 'OPEN'
        return True
    if 'can_use_ESYNC_advanced' in request.session['permissions']:
        return True
    return False

class tester(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_ESYNC'

    ### PUT IN CONFIG FILE

    template_name = 'esync/index.html'
    def get(self,request):
        context={'test': check_perm(request,'Aaron-TEST__NginxForward')}

        return HttpResponse(json.dumps(context), content_type='application/json')

class reload(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_ESYNC'

    ### PUT IN CONFIG FILE

    @staticmethod
    def generate_hostgroups(to_dict=False):
        hostgroups={}
        rVal = ''
        #db_data = list(cloud_host.objects.filter().values('host_ip','fqdn'))
        db_data = ZABBIX.get_all_hosts(filter='Cloud Hosts')
        pprint(db_data)
        for row in db_data:
            match = re.match(r'(\S+)-([a-zA-Z_]+[a-zA-Z_0-9]+[a-zA-Z_]+)(\d+)\.(\S+)\.(\S+)\.(monaco1\.me)', row['hostname'])
            if match:
                hg = '{0}-{1}'.format(match.group(1), match.group(2))

                if hg not in hostgroups:
                    hostgroups[hg]=[]
                hostgroups[hg].append('{0} #{1}'.format(row['ip'],row['hostname']))
            else:
                print row['hostname']
        for hg in hostgroups:
            rVal +='\n[{0}]\n'.format(hg)
            for ip in hostgroups[hg]:
                rVal += '{0}\n'.format(ip)
        if to_dict:
            return hostgroups

        return rVal

    @staticmethod
    def load_all():
        service_providers = list(CLOUD_HOST.objects.values('service_provider').distinct())
        for i in service_providers:
            try:
                newObj = SERVICE_PROVIDERS.objects.get(service_provider=i['service_provider'])
            except:
                newObj = SERVICE_PROVIDERS(service_provider=i['service_provider'])
                newObj.save()
        rVal = {
            'config': ESYNC_GLOBAL_RESOURCE.load_config_list(),
            'access': ESYNC_GLOBAL_RESOURCE.load_access_levels(),
            'hosts': app.send_task(
                'esync_worker.write_ansible_hosts',
                args=(reload.generate_hostgroups(),),
                queue='qesync_agent'
            ).get()
        }
        return rVal

    def get(self, request):
        return HttpResponse(json.dumps(reload.load_all()), content_type='application/json')

class hostgroup_index(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_ESYNC'

    ### PUT IN CONFIG FILE

    template_name = 'esync/index.html'
    def get(self,request,hostgroup):
        context = {}
        directory  = request.GET.get("dir", None)
        filename = request.GET.get("file", None)
        search = request.GET.get("search", None)
        getfilelist = request.GET.get("getfilelist", None)
        dom = request.GET.get("dom", None)
        certstore = request.GET.get("certstore", None)
        sha1 = request.GET.get("sha1", None)

        routine_key = request.GET.get("r", None)
        routine_from = request.GET.get("rf", None)
        routine_to = request.GET.get("rt", None)

        hg = ESYNC_GLOBAL_RESOURCE.get_config_list(hostgroup=hostgroup)
        access_levels = ESYNC_GLOBAL_RESOURCE.get_access_levels()

        if not hg or access_levels[hostgroup]['access_level'] == 'SPECIFIC' and request.user.username not in \
                access_levels[hostgroup]['users']:
            raise Http404

        print 1
        if dom:
            print "SSL"
            context['data']=app.send_task(
                                'esync_worker.find_ssl_keypair',
                                 args=(hostgroup,dom,),
                                 queue='qesync_agent'
                             ).get()
            return HttpResponse(json.dumps(context), content_type='application/json')

        if filename and directory:
            fullpath = directory + '/' + filename
            if sha1:
                result = app.send_task(
                        'esync_filewatcher.getsha1', 
                        args=(hostgroup,fullpath,),
                        #args=(fullpath,),
                        queue='qesync_filewatcher'
                    )
                context['hash'] = result.get()
                return HttpResponse(json.dumps(context), content_type='application/json')
  
            print 11
            context['content'] = app.send_task(
                                    'esync_worker.get_config', 
                                    args=(hostgroup,fullpath,), 
                                    queue='qesync_agent'
                                ).get()

            print 111
            context['hash'] = app.send_task(
                                'esync_filewatcher.getsha1',
                                 args=(hostgroup,fullpath,),
                                 #args=(fullpath,),
                                 queue='qesync_filewatcher'
                             ).get()

            if directory in STANDARD_DIRS:
                context['keys'] = parse_standard_config(context['content'])
            return HttpResponse(json.dumps(context), content_type='application/json')

        elif search:
            context['data']=app.send_task(
                                'esync_worker.search', 
                                args=(hostgroup, search),
                                queue='qesync_agent'
                            ).get()

            print 1111
            return HttpResponse(json.dumps(context), content_type='application/json')

        elif getfilelist:
            context['FILES'] =  app.send_task(
                                'esync_worker.get_file_list', 
                                args=(hostgroup,),
                                queue='qesync_agent'
                            ).get()
            context['W'] = check_perm(request,hostgroup)

            return HttpResponse(json.dumps(context), content_type='application/json')

        elif certstore:
            context['certstore'] = app.send_task(
                                        'esync_worker.get_certstore_list',
                                        queue='qesync_agent'
                                    ).get()
            print 11231
            return HttpResponse(json.dumps(context), content_type='application/json')

        if routine_key:
            context = None
            RETRY = 0
          
            #print ESYNC_GLOBAL_RESOURCE.resource_manager.get_routine_line('57bd6010ee81efeb20c95dd168f61cc63ba480cd', 0, -1)
            
            while not context:
                print 'try,',RETRY
                context = ESYNC_GLOBAL_RESOURCE.resource_manager.get_routine_line(routine_key, routine_from, routine_to)
                time.sleep(.3)
                RETRY +=1

                if RETRY == 200:
                    context = 'MAX RETRIES EXECUTED, COMMAND NOT RESPONDING'
                    log.info(context)
                    break

            return HttpResponse(context,content_type='text/html')


        return render(request, self.template_name, context)


@method_decorator(csrf_exempt, name='dispatch')
class generate(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_ESYNC'

    def post(self,request,hostgroup):
        context = {
            'code':{},
            'status':True
        }
        create = request.GET.get("create", None)
        body = json.loads(request.body)
        hg = ESYNC_GLOBAL_RESOURCE.get_config_list(hostgroup=hostgroup)
        access_levels = ESYNC_GLOBAL_RESOURCE.get_access_levels()
        if not hg or access_levels[hostgroup]['access_level'] == 'SPECIFIC' and request.user.username not in \
                access_levels[hostgroup]['users']:
            raise Http404


        if body['dir'] in OTHER_DIRS:
            for i in body['conf']:
                for k,v in i.items():

                    if not check_perm(request,hostgroup):
                        context = {
                            'message': 'You do not have privileges to create non-standard configuration, Ask our manager for a Career promotion or level-up.\n',
                            'status': False
                        }
                        log.info('{0} - Denied creation, nonstandard configuration'.format(request.user.username))
                        return HttpResponse(json.dumps(context), content_type='application/json')

                    if body['dir'] == 'include':
                        if not k.endswith('.include') or len(k)>50:
                            context = {
                                'message': "Invalid Filename, must end with .include",
                                'status': False
                            }
                            return HttpResponse(json.dumps(context), content_type='application/json')
                    elif body['dir'] in ['default','global','other']:
                        if not k.endswith('.conf') or len(k)>50:
                            context = {
                                'message': "Invalid Filename, must end with .conf",
                                'status': False
                            }
                            return HttpResponse(json.dumps(context), content_type='application/json')


                    destpath = body['dir']+'/'+k

                    if 'edit' not in body:
                        ##### IF FILE EXISTS, DENY
                        result = app.send_task('esync_worker.get_config', args=(hostgroup,destpath),queue='qesync_agent')
                        result = result.get()
                        if result is not False:
                            context = {
                                'message': "The file {0}/{1} exists, please edit the file directly.".format(body['dir'],k),
                                'status': False
                            }
                            return HttpResponse(json.dumps(context), content_type='application/json')


                    result = app.send_task('esync_worker.write_file',args=(hostgroup, destpath, v),queue='qesync_agent')
                    result = result.get()
                    log.info('{0} - FILE CREATION - {1} - esync_worker.write_file - {2}'.format(request.user.username,destpath,result[0]))

                    nonstandard_esync_log(hostgroup, request.user.username, [result[1]],activity_type='CREATE')

        elif body['dir'] in STANDARD_DIRS:


            if body['dir'] == '80':
                listen = '80'

            elif body['dir'] == '443':
                listen = '443'

            elif body['dir'] == '80-443':
                listen = ['80', '443']

            certificate = None
            privkey = None

            for i in body['conf']:
                dom_list = i['http_host'].split('.')
                root_dom = dom_list[-2] + '.' + dom_list[-1]
                h = root_dom + ' '+i['http_host'] if i['http_host'].startswith('www.') else i['http_host']
                i['http_host'] = i['http_host'].strip()

                if '443' in listen:
                    result = app.send_task('esync_worker.find_ssl_keypair',
                                           args=(hostgroup, root_dom,),kwargs={'checkcertstore':True},queue='qesync_agent')
                    files = result.get()
                    if files == False:
                        context = {
                            'message':'No SSL Keypair found for the HTTP Host! Link the directory first',
                            'status' : False
                        }
                        log.info('{0} - FIND SSL KEYPAIR - {1} - esync_worker.find_ssl_keypair - {2}'.format(request.user.username,root_dom,files))

                        return HttpResponse(json.dumps(context), content_type='application/json')

                    for k,v in files.items():
                        fl = files[k].split('/')
                        files[k]='ssl/{0}/{1}'.format(fl[-2],fl[-1])

                    certificate = files['cert']
                    privkey = files['privkey']

                path = body['dir'] + '/' + root_dom + '.conf'
                if not path in context['code']:
                    context['code'][path]={
                        'add':'',
                        'remove':'',
                        'remain':''
                    }

                if isinstance(listen, list):
                    for o in listen:
                        ### if has sub domain, no change, else redirect to www
                        p_http_host = i['http_host'] + ' www.' + i['http_host'] if len(dom_list) <= 2 else i['http_host']

                        ### if port 80, no include else add include
                        p_include = None if o == '80' else i['include_file']

                        if o == '80' and len(dom_list) <= 2:
                            p_redirect_http_host = 'www.'+i['http_host']
                        elif o == '443' and len(dom_list) <= 2:
                            p_redirect_http_host = 'www'
                        elif o == '443' and len(dom_list) > 2:
                            p_redirect_http_host = None
                        ## else if have subdomain
                        else:
                            p_redirect_http_host = i['http_host']

                        if o == '80':
                            p_certificate = None
                            p_privkey = None
                        else:
                            p_certificate = certificate
                            p_privkey = privkey

                        context['code'][path]['add'] += create_standard_config(o,
                                                    p_http_host,
                                                    p_include,
                                                    redirect_http_host= p_redirect_http_host,
                                                    redirect_to=True,
                                                    certificate=p_certificate,
                                                    privkey=p_privkey,
                                                    redirect_scheme='https')

                else:
                    context['code'][path]['add'] += create_standard_config(listen,
                                                   h,
                                                   i['include_file'],
                                                   redirect_http_host='www' if i['http_host'].startswith('www.') else None,
                                                   redirect_to=None,
                                                   certificate=certificate,
                                                   privkey=privkey,
                                                   redirect_scheme='http' if listen == '80' else 'https')

                search_res = []

                for host in h.split(' '):
                    tempd =  host.split('.')
                    result = app.send_task('esync_worker.search',
                                           args=(hostgroup, tempd[-2]+'.'+tempd[-1]),
                                           queue='qesync_agent')
                    for res in result.get():
                        if res not in search_res:
                            search_res.append(res)
                if search_res:
                    conflicts = {}
                    ret = None
                    for search in search_res:
                        searchpath = search['dir'] + '/' + search['file']
                        result = app.send_task('esync_worker.get_config',
                                               args=(hostgroup,searchpath,),queue='qesync_agent')
                        result = result.get()
                        if check_server_block(result, h.split(' '),listen):
                            conflicts[search['dir'] + '/' + search['file']] = result

                        if path == search['dir'] + '/' + search['file']:
                            ret = result

                    if not conflicts and ret is not None:
                        context['code'][path]['remain']=ret

                    else:


                        for c_dir, c_conf in conflicts.items():
                            if not check_perm(request,hostgroup):
                                context = {
                                    'message': 'Existing configuration(s) found, you have insufficient privileges to override:\n',
                                    'status': False
                                }
                                log.info(
                                    '{0} - Create Configuration - {1} - {2}'.format(request.user.username, root_dom,
                                                                                    context['message']))
                                context['message'] += '\n' + c_dir
                                return HttpResponse(json.dumps(context), content_type='application/json')

                            if c_dir not in context['code']:
                                context['code'][c_dir] = {
                                    'add':'',
                                    'remove':'',
                                    'remain':''
                                }
                            test = rewrite_server_block(c_conf,h.split(' '),listen)

                            context['code'][c_dir]['remove'] = test[0]
                            context['code'][c_dir]['remain'] = test[1]

            if bool(create) == True:
                try:
                    for k,v in context['code'].items():
                        destpath = k
                        content = context['code'][k]['add'] + context['code'][k]['remain']
                        result = app.send_task('esync_worker.write_file',args=(hostgroup,destpath, content),queue='qesync_agent')
                        result = result.get()
                        log.info('{0} - FILE CREATION - {1} - esync_worker.write_file - {2}'.format(request.user.username, destpath, result))

                    standard_esync_log(hostgroup,request.user.username,context,activity_type='CREATE')


                except Exception as e:
                    context = {
                        'message':str(e),
                        'status':False
                    }
                    log.error(traceback.print_exc())

        else:
            raise Http404

        return HttpResponse(json.dumps(context), content_type='application/json')

@method_decorator(csrf_exempt, name='dispatch')
class link(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_ESYNC'

    def post(self,request,hostgroup):
        context = {
            'status':False
        }
        body = json.loads(request.body)

        hg = ESYNC_GLOBAL_RESOURCE.get_config_list(hostgroup=hostgroup)

        access_levels = ESYNC_GLOBAL_RESOURCE.get_access_levels()
        if not hg or access_levels[hostgroup]['access_level'] == 'SPECIFIC' and request.user.username not in \
                access_levels[hostgroup]['users']:
            raise Http404

        rem = request.GET.get("remove", None)

        if rem:
            loc = body['source']
            result = app.send_task('esync_worker.unlink_ssl', args=(hostgroup,loc,),queue='qesync_agent')
            context['status'] = result.get()
            log.info('{0} - UNLINK SSL - {1} - esync_worker.unlink_ssl - {2}'.format(request.user.username,body['source'],result))
        else:
            result = app.send_task('esync_worker.link_ssl', args=(hostgroup,body['source']),queue='qesync_agent')
            context['status'] = result.get()
            log.info('{0} - LINK SSL - {1} - esync_worker.link_ssl - {2}'.format(request.user.username,body['source'],result))

        return HttpResponse(json.dumps(context), content_type='application/json')


class check(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_ESYNC'
    def get(self,request,hostgroup):
        hg = ESYNC_GLOBAL_RESOURCE.get_config_list(hostgroup=hostgroup)
        access_levels = ESYNC_GLOBAL_RESOURCE.get_access_levels()
        if not hg or access_levels[hostgroup]['access_level'] == 'SPECIFIC' and request.user.username not in \
                access_levels[hostgroup]['users']:
            raise Http404

        result = app.send_task('esync_worker.test_nginx_config', args=(hostgroup,),queue='qesync_agent')
        result = result.get()
        log.info('{0} - TEST NGINX - {1} - esync_worker.test_nginx_config - {2}'.format(request.user.username,hostgroup , result[1]))

        context = {
            'status': result[0],
            'message':result[1]
        }

        return HttpResponse(json.dumps(context), content_type='application/json')



class sync(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_ESYNC'

    def get(self,request,hostgroup):

        hg = ESYNC_GLOBAL_RESOURCE.get_config_list(hostgroup=hostgroup)
        execute = request.GET.get("execute", None)

        access_levels = ESYNC_GLOBAL_RESOURCE.get_access_levels()
        if not hg or access_levels[hostgroup]['access_level'] == 'SPECIFIC' and request.user.username not in \
                access_levels[hostgroup]['users']:
            raise Http404
        if execute:
            print 123123
            result = app.send_task('esync_worker.sync_nginx_config', args=(hostgroup,),
                                   kwargs={'user': request.user.username},queue='qesync_agent')
            result = result.get()
            print 17623678123
            log.info('{0} - SYNC - {1} - esync_worker.sync_nginx_config'.format(request.user.username,hostgroup))

            context = {
                'status': result[0],
                'key': result[1]
            }

            threading.Thread(target=command_logger,
                             args=(hostgroup, request.user.username, context['key'], ESYNC_GLOBAL_RESOURCE.resource_manager),
                             kwargs={'etype': 'SYNC'}
                             ).start()

            return HttpResponse(json.dumps(context), content_type='application/json')



class clear_cache(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_ESYNC'

    def get(self,request,hostgroup):

        hg = ESYNC_GLOBAL_RESOURCE.get_config_list(hostgroup=hostgroup)
        execute = request.GET.get("execute", None)

        access_levels = ESYNC_GLOBAL_RESOURCE.get_access_levels()
        if not hg or access_levels[hostgroup]['access_level'] == 'SPECIFIC' and request.user.username not in \
                access_levels[hostgroup]['users']:
            raise Http404

        if execute:
            result = app.send_task('esync_worker.clear_nginx_cache', args=(hostgroup,),
                                   kwargs={'user': request.user.username},queue='qesync_agent')
            result = result.get()

            log.info('{0} - CLEAR NGINX CACHE - {1} - esync_worker.clear_nginx_cache'.format(request.user.username,hostgroup))

            context = {
                'status': result[0],
                'key': result[1]
            }

            threading.Thread(target=command_logger,
                             args=(hostgroup, request.user.username, context['key'], ESYNC_GLOBAL_RESOURCE.resource_manager),
                             kwargs={'etype':'CLEAR'}
                             ).start()

            return HttpResponse(json.dumps(context), content_type='application/json')

@method_decorator(csrf_exempt, name='dispatch')
class delete(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_ESYNC'

    def post(self,request,hostgroup):
        hg = ESYNC_GLOBAL_RESOURCE.get_config_list(hostgroup=hostgroup)
        access_levels = ESYNC_GLOBAL_RESOURCE.get_access_levels()
        if not hg or access_levels[hostgroup]['access_level'] == 'SPECIFIC' and request.user.username not in \
                access_levels[hostgroup]['users']:
            raise Http404

        if not check_perm(request,hostgroup):
            return HttpResponseForbidden()

        body = json.loads(request.body)

        pprint(body)
        if not body['dir'] or not body['file']:
            log.info('{0} - EMPTY DIR/EMPTY FILE {1}'.format(request.user.username,body))

            context = {
                'status': True,
                'message': 'Don\'t do it :)'
            }

        elif body['dir'] not in STANDARD_DIRS and body['dir'] not in OTHER_DIRS:
            log.info('{0} - ATTEMPTED TO DELETE A DIFFERENT DIRECTORY'.format(request.user.username))

            context = {
                'status': False,
                'message': 'Don\'t do it :)'
            }
        else:
            fullpath = body['dir']+'/'+body['file']

            result = app.send_task('esync_worker.delete_file', args=(hostgroup,fullpath, ),queue='qesync_agent')
            result = result.get()

            if result:
                context = {
                    'status':result,
                    'message':'File: '+body['file']+' Deleted'
                }

                log.info('{0} - FILE DELETION - {1} - esync_worker.delete_file'.format(request.user.username, fullpath))
                nonstandard_esync_log(hostgroup, request.user.username, context['message'],activity_type='DELETE')

        return HttpResponse(json.dumps(context), content_type='application/json')



class history(GENERIC_PERMISSION_MIXIN,View):
    permission_required = 'can_use_ESYNC'
    def get(self,request):
        context = {
            'data':[]
        }

        file  = request.GET.get("file", None)


        if file:
            if '~' in file or '..' in file or '&' in file:
                raise Http404

            try:
                f = open('logs/esync_logger/'+file)
                context = f.read()
                f.close()
                return HttpResponse(context, content_type='text')
            except:
                raise Http404


        files = glob.glob('logs/esync_logger/*/*')
        files.sort(key=os.path.getmtime,reverse=True)
        c = 0
        while c <100:
            try:
                _file = files[c].split('/')
                context['data'].append(_file[-2] + '/' + _file[-1])
                c +=1
            except IndexError:
                break

        return HttpResponse(json.dumps(context), content_type='application/json')


@method_decorator(csrf_exempt, name='dispatch')
class index(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_ESYNC'
    template_name = 'esync/index2.html'

    def get(self,request):
        context = {}

        entitylist = request.GET.get("entitylist", None)
        hg = ESYNC_GLOBAL_RESOURCE.get_config_list()
        access_levels = ESYNC_GLOBAL_RESOURCE.get_access_levels()
        if not hg:
            log.info("ESYNC Config List Not Found")
            raise Exception("ESYNC Config List Not Found")

        if entitylist:
            context['ENTITYLIST'] = ESYNC_GLOBAL_RESOURCE.get_entity_list(request.user.username)
            pprint(context['ENTITYLIST']['bbetasia'])
            return HttpResponse(json.dumps(context), content_type='application/json')

        context['DIRLIST']=[i for i in hg]

        return render(request, self.template_name, context)


@method_decorator(csrf_exempt, name='dispatch')
class deploy(GENERIC_PERMISSION_MIXIN, View):
    permission_required = 'can_use_ESYNC_deploy'
    template_name = 'esync/deploy.html'

    def __get_deployable(self):
        t = app.send_task(
            'esync_worker-CLOUD.get_deployable_hosts',
            queue='qesync_agent'
        )
        res = t.get()
        t.forget()
        return sorted(res)


    def get(self,request):
        context = {
            'deployable':self.__get_deployable()
        }
        return render(request, self.template_name,context)

    def post(self,request):
        context = {'result':None}
        context['reload'] = reload.load_all()
        body = json.loads(request.body)
        t = app.send_task(
            'esync_worker.deploy_hostgroup',
            args=(body['hostgroup'],),
            queue='qesync_agent'
        )
        res = t.get()
        t.forget()
        log.info("DEPLOY NGINX: {0} - {1}".format(request.user.username,res[1]))
        context['result'] = res[1]


        return HttpResponse(json.dumps(context), content_type='application/json')



