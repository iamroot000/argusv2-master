from django.conf import settings
from .models import *
import os, paramiko, yaml, json, time, base64, socket


class SSRsetup():
    def __init__(self):
        self.ansiblefile = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/ansible.cfg')
        self.hostsfile = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/hosts')
        self.ansible_conf = {
            'inventory' : os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/hosts'),
            'library' : os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/my_modules'),
            'local_tmp' : os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/tmp'),
            'roles_path' : os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/roles'),
            'host_key_checking' : False,
            'deprecation_warnings' : False,
            'command_warnings' : False
        }

    def ansibleConf(self):
        open(self.ansiblefile, 'w').close()
        open(self.ansiblefile, 'a').write('[defaults]\n')
        for key, value in self.ansible_conf.items():
            open(self.ansiblefile, 'a').write('{} = {}\n'.format(key, value))


    def ansibleHosts(self, ssrrestart=False):
        open(self.hostsfile, 'w').close()
	ssr_hosts = ['[ssr_init]\n', '[ssr_config]\n', '[ssr_fileconfig]\n']
        ssr_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/roles/p.ssr_init/vars/main.yml')
        ssr_file2 = open(ssr_file, 'r').read()
        ssr_port = yaml.safe_load(ssr_file2)['ssr_port']
        ssr_user = yaml.safe_load(ssr_file2)['ssr_user']
        for ssr_host in ssr_hosts:
            open(self.hostsfile, 'a').write(ssr_host)
            if ssrrestart is True:
                for data in SSRconfigsummaryModel.objects.all():
                    open(self.hostsfile, 'a').write(
                        '{} ansible_ssh_port={} ansible_ssh_user={}\n'.format(data.IP, ssr_port, ssr_user))
            else:
                for data in SSRinitModel.objects.all():
                    open(self.hostsfile, 'a').write('{} ansible_ssh_port={} ansible_ssh_user={} ansible_ssh_pass={}\n'.format(data.IP, data.PORT, data.USER, data.PASSWORD))
        open(self.hostsfile, 'a').write('[multi:children]\nssr_init\nssr_config\nssr_fileconfig\n[multi:vars]\nAUTH_BASIC_ENABLED=False\nHOST_KEY_CHECKING=False\nANSIBLE_HOST_KEY_CHECKING=False\n')

    def ansibleExecute(self, ssrrestart=False):
        ansiblehosts = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/hosts')
        ansible_main = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/main.yml')
        ssr_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/roles/p.ssr_init/vars/main.yml')
        ssr_file2 = open(ssr_file, 'r').read()
        ssr_password = yaml.safe_load(ssr_file2)['ssr_password']
        limit = 'ssr_init,ssr_config'
        limit2 = 'ssr_config'
        tags = 'initialization_ssr,config_ssr'
        tags2 = 'config_ssr'
        if ssrrestart is True:
            try:
                for port in SSRconfigsummaryModel.objects.all():
                    ssrport = port.PORT
                ssr_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/roles/p.ssr_config/vars/main.yml')
                ssr_file2 = open(ssr_file, 'r').read()
                ssr_portprev = yaml.safe_load(ssr_file2)
                ssr_portprev['ssr_port'] = str(ssrport)
                ssr_file2 = open(ssr_file, 'w')
                yaml.safe_dump(ssr_portprev, ssr_file2, default_flow_style=False, explicit_start=True)
            except:
                pass

            os.system(
                "ansible-playbook -i {} {} --ssh-common-args='-o StrictHostKeyChecking=no' --limit {} --tags {} --extra-vars ansible_become_pass={} --become-method=su -T 30 > {} &".format(
                    ansiblehosts, ansible_main, limit2, tags2, ssr_password,
                    os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/logs')))
        else:
            os.system(
                "ansible-playbook -i {} {} --ssh-common-args='-o StrictHostKeyChecking=no' --limit {} --tags {} > {} -T 30 &".format(
                    ansiblehosts, ansible_main, limit, tags,
                    os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/logs')))

    def ansiblerecap(self):
        logs = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/logs'), 'r').read()
        # logs = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/testlogs'), 'r').read()
        if "PLAY RECAP" in logs.strip('\n'):
            ssr_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/roles/p.ssr_config/vars/main.yml')
            ssr_file2 = open(ssr_file, 'r').read()
            ssr_portprev = yaml.safe_load(ssr_file2)
            ssr_portprev['ssr_port'] = '3389'
            ssr_file2 = open(ssr_file, 'w')
            yaml.safe_dump(ssr_portprev, ssr_file2, default_flow_style=False, explicit_start=True)
            return True

class SSRsave():
    def ssrcheck(self, ssrip, ssrport):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        result = sock.connect_ex((str(ssrip), int(ssrport)))
        try:
            if result == 0:
                return 'OK'
            else:
                return 'DOWN'
        except Exception as e:
            # print("ssrcheck exception" + str(e))
            return 'TIMEOUT'
            # return e


    def ssrinfo(self, IPok, SSRerror='TIMEOUT', SSRstatus=True, SSRrestart=False):
        ssr_passfile = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/roles/p.ssr_init/vars/main.yml')
        ssr_passfile2 = open(ssr_passfile, 'r').read()
        ssr_password = yaml.safe_load(ssr_passfile2)['ssr_password']
        ssr_user = yaml.safe_load(ssr_passfile2)['ssr_user']
        ssr_port = yaml.safe_load(ssr_passfile2)['ssr_port']
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('{}'.format(IPok), username=ssr_user, port=ssr_port, timeout=15)
            console = ssh.invoke_shell()
            console.keep_this = ssh
            # print('try connect ssh')
            if SSRrestart is True:
                try:
                    stdin, stdout, stderr = ssh.exec_command('su root -c "service ssr restart"')
                    # time.sleep(5)
                    # print(stdout.read())
                    stdin.write('{}\n'.format(ssr_password))
                    # print('password write2')
                    # time.sleep(10)
                except:
                    pass
		restartyrm = os.path.join(settings.BASE_DIR,'SSRCHECKER/aom/ansible/restart.yml')
                hostsfile = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/hosts_file_config')
                open(hostsfile, 'w').close()
                ssr_hosts = ['[ssr_init]\n', '[ssr_config]\n', '[ssr_fileconfig]\n']
                for ssr_host in ssr_hosts:
                    open(hostsfile, 'a').write(ssr_host)
                    for data in (IPok,):
                            open(hostsfile, 'a').write(
                                '{} ansible_ssh_port={} ansible_ssh_user={}\n'.format(data, ssr_port, ssr_user))
                open(hostsfile, 'a').write(
                    '[multi:children]\nssr_init\nssr_config\nssr_fileconfig\n[multi:vars]\nAUTH_BASIC_ENABLED=False\nHOST_KEY_CHECKING=False\nANSIBLE_HOST_KEY_CHECKING=False\n')
                os.system("ansible-playbook -i {} {} --ssh-common-args='-o StrictHostKeyChecking=no' --extra-vars ansible_become_pass={} --become-method=su".format(hostsfile,restartyrm, ssr_password))
            # print('processing')
            stdin, stdout, stderr = ssh.exec_command('cat /etc/shadowsocksr/user-config.json')
            ssrdata = stdout.read().decode('utf-8')
            ssrdata = json.loads(ssrdata)
            ip = IPok
            # ip = requests.get('http://ipinfo.io/ip').text
            password64 = base64.b64encode(ssrdata["password"].encode("utf-8")).decode("utf-8")
            SS_url = '{}:{}@{}:{}'.format(ssrdata["method"], ssrdata["password"], str(ip), ssrdata["server_port"])
            SSR_url = '{}:{}:{}:{}:{}:{}'.format(str(ip), ssrdata["server_port"],
                                                 ssrdata["protocol"].replace('_compatible', ''), ssrdata["method"],
                                                 ssrdata["obfs"],
                                                 str(password64).replace('=', '').replace('+', '-').replace('/', '_'))
            SS_url64 = base64.b64encode(str(SS_url).encode("utf-8")).decode("utf-8")
            SSR_url64 = base64.b64encode(str(SSR_url).encode("utf-8")).decode("utf-8")
            # print(SSR_url64)
            ssh.close()
            # time.sleep(10)
            # print('ssh closed')
            if SSRstatus is True:
                ssrstatus = self.ssrcheck(ssrip=str(IPok), ssrport=ssrdata["server_port"])
                # print("SSR status check "+ ssrstatus)
                return {'ssr_link': 'ssr://{}'.format(SSR_url64.replace('+', '-').replace('/', '_').replace('=', '')),
                        'ssr_code': 'http://doub.pw/qr/qr.php?text=ssr://{}'.format(
                            SSR_url64.replace('+', '-').replace('/', '_').replace('=', '')),
                        'ss_link': 'ss://{}'.format(SS_url64.replace('+', '-').replace('/', '_').replace('=', '')),
                        'ss_code': 'http://doub.pw/qr/qr.php?text=ss://{}'.format(
                            SS_url64.replace('+', '-').replace('/', '_').replace('=', '')),
                        'ssr_status': ssrstatus,
                        'ssr_port': int(ssrdata["server_port"]),
                        }
            else:
                return {'ssr_link': 'ssr://{}'.format(SSR_url64.replace('+', '-').replace('/', '_').replace('=', '')),
                        'ssr_code': 'http://doub.pw/qr/qr.php?text=ssr://{}'.format(
                            SSR_url64.replace('+', '-').replace('/', '_').replace('=', '')),
                        'ss_link': 'ss://{}'.format(SS_url64.replace('+', '-').replace('/', '_').replace('=', '')),
                        'ss_code': 'http://doub.pw/qr/qr.php?text=ss://{}'.format(
                            SS_url64.replace('+', '-').replace('/', '_').replace('=', '')),
                        }
        except Exception as e:
            # print("ssrinfo exception " + str(e))
            return SSRerror
            # return e


    def ssrlogs(self, username, restartssr=False):
        logs = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/logs'), 'r').read()
        IPS = {}
        final = []
        ipinfo = {}
        if restartssr is True:
            for ip in SSRconfigsummaryModel.objects.all():
                IPS[ip.IP] = ip.PORT
        else:
            for ip in SSRinitModel.objects.all():
                IPS[ip.IP] = ip.IDC

        for i, value in IPS.items():
            for i2 in logs.split('PLAY RECAP')[-1].split('\n'):
                if i in i2:
                    final.append(i2)

        ssr_dataall = {}
        ssr_summaryidc = {}
        for iplist in SSRinitdataModel.objects.all():
            ssr_dataall.update({iplist.IP: iplist.IDC})

        for idclist in SSRconfigsummaryModel.objects.all():
            ssr_summaryidc.update({idclist.IP: idclist.IDC})

        for key, value in ssr_summaryidc.items():
            if key in ssr_dataall.keys():
                ssr_summaryidc[key] = ssr_dataall[key]


        for i in final:
            ipinfo[i.split(':')[0].strip()] = i.split(':')[-1].strip().split()

        if "PLAY RECAP" in logs:
            for key, value in ipinfo.items():
                if "unreachable=1" in value:
                    # ssrinfo = self.ssrinfo(key)
                    try:
                        if restartssr is True:
                            data = SSRconfighistoryModel.objects.get(IP=key)
                            data.STATUS = 'UNREACHABLE'
                            data.LOGS = logs
                            data.PORT = IPS[key]
                            data.USERNAME = username
                            data.CREATED = datetime.datetime.now()
                            data.save()
                        else:
                            data = SSRinithistoryModel.objects.get(IP=key)
                            data.STATUS='UNREACHABLE'
                            data.LOGS=logs
                            data.IDC=IPS[key]
                            data.USERNAME=username
                            data.CREATED=datetime.datetime.now()
                            data.save()
                    except:
                    # except Exception as e:
                    #     print('unreachable exception ' + str(e))
                        if restartssr is True:
                            SSRconfighistoryModel.objects.create(
                                IP=key,
                                STATUS='UNREACHABLE',
                                LOGS=logs,
                                PORT=IPS[key],
                                USERNAME=username,
                                DATE=datetime.datetime.now()
                                )
                        else:
                            SSRinithistoryModel.objects.create(
                                IP=key,
                                STATUS='UNREACHABLE',
                                LOGS=logs,
                                IDC=IPS[key],
                                USERNAME=username,
                                CREATED=datetime.datetime.now()
                                )
                    if restartssr is True:
                        SSRconfigsummaryModel.objects.all().delete()
                    else:
                        SSRinitModel.objects.all().delete()
                elif "failed=1" in value:
                    #ssrinfo = self.ssrinfo(key,SSRerror='FAILED')
                    try:
                        if restartssr is True:
                            data = SSRconfighistoryModel.objects.get(IP=key)
                            data.STATUS='FAILED'
                            data.LOGS=logs
                            data.PORT = IPS[key]
                            data.USERNAME=username
                            data.DATE=datetime.datetime.now()
                            data.save()
                        else:
                            data = SSRinithistoryModel.objects.get(IP=key)
                            data.STATUS = 'FAILED'
                            data.LOGS = logs
                            data.IDC = IPS[key]
                            data.USERNAME = username
                            data.CREATED = datetime.datetime.now()
                            data.save()
                    except:
                    # except Exception as e:
                    #     print('failed exception ' + str(e))
                        if restartssr is True:
                            SSRconfighistoryModel.objects.create(
                                IP=key,
                                STATUS='FAILED',
                                LOGS=logs,
                                PORT=IPS[key],
                                USERNAME=username,
                                DATE=datetime.datetime.now()
                                )
                        else:
                            SSRinithistoryModel.objects.create(
                                IP=key,
                                STATUS='FAILED',
                                LOGS=logs,
                                IDC=IPS[key],
                                USERNAME=username,
                                CREATED=datetime.datetime.now()
                            )
                    if restartssr is True:
                        SSRconfigsummaryModel.objects.all().delete()
                    else:
                        SSRinitModel.objects.all().delete()
                else:
                    ssrinfo = self.ssrinfo(str(key))
                    try:
                        if restartssr is True:
                            data = SSRconfighistoryModel.objects.get(IP=key)
                            data.STATUS='COMPLETED'
                            data.LOGS=logs
                            data.PORT=IPS[key]
                            data.USERNAME=username
                            data.DATE=datetime.datetime.now()
                            data.save()
                        else:
                            data = SSRinithistoryModel.objects.get(IP=key)
                            data.STATUS = 'COMPLETED'
                            data.LOGS = logs
                            data.IDC = IPS[key]
                            data.USERNAME = username
                            data.CREATED = datetime.datetime.now()
                            data.save()
                    except:
                    # except Exception as e:
                    #     print('success exception ' + str(e))
                        if restartssr is True:
                            SSRconfighistoryModel.objects.create(
                                IP=key,
                                STATUS='COMPLETED',
                                LOGS=logs,
                                PORT=IPS[key],
                                USERNAME=username,
                                DATE=datetime.datetime.now()
                                )
                        else:
                            SSRinithistoryModel.objects.create(
                                IP=key,
                                STATUS='COMPLETED',
                                LOGS=logs,
                                IDC=IPS[key],
                                USERNAME=username,
                                CREATED=datetime.datetime.now()
                            )
                    try:
                        data = SSRinitdataModel.objects.get(IP=key)
                        data.IP=key
                        data.PORT=ssrinfo['ssr_port']
                        data.STATUS=ssrinfo['ssr_status']
                        data.SSR_LINK=ssrinfo['ssr_link']
                        data.SSR_CODE=ssrinfo['ssr_code']
                        data.IDC=ssr_summaryidc[key]
                        data.SS_CODE=ssrinfo['ssr_code']
                        data.SS_LINK=ssrinfo['ssr_link']
                        data.LAST_CHECK=datetime.datetime.now()
                        data.save()
                    except:
                    # except Exception as e:
                    #     print('success 2 exception ' + str(e))
                        if restartssr is True:
                            SSRinitdataModel.objects.create(
                                IP=key,
                                PORT=ssrinfo['ssr_port'],
                                STATUS=ssrinfo['ssr_status'],
                                SSR_LINK=ssrinfo['ssr_link'],
                                SSR_CODE=ssrinfo['ssr_code'],
                                IDC=ssr_summaryidc[key],
                                SS_CODE=ssrinfo['ssr_code'],
                                SS_LINK=ssrinfo['ssr_link'],
                                LAST_CHECK=datetime.datetime.now()
                                )
                        else:
                            SSRinitdataModel.objects.create(
                                IP=key,
                                PORT=ssrinfo['ssr_port'],
                                STATUS=ssrinfo['ssr_status'],
                                SSR_LINK=ssrinfo['ssr_link'],
                                SSR_CODE=ssrinfo['ssr_code'],
                                IDC=IPS[key],
                                SS_CODE=ssrinfo['ssr_code'],
                                SS_LINK=ssrinfo['ssr_link'],
                                LAST_CHECK=datetime.datetime.now()
                                )
                    if restartssr is True:
                        SSRconfigsummaryModel.objects.all().delete()
                    else:
                        SSRinitModel.objects.all().delete()

    def ssrping(self, IPadd):
        response = os.system("ping -c 3 " + IPadd)
        if response == 0:
            return "OK"
        else:
            return "UNREACHABLE"


class SSRfileconfigprocess():
    def __init__(self):
        self.config = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/config.json')
        self.hostsfile = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/hosts')

    def SSRfileyml(self):
        config_file_template = os.path.join(settings.BASE_DIR,
                                            'SSRCHECKER/aom/ansible/roles/p.ssr_fileconfig/tasks/template.yml')
        ssr_filetemplate = open(config_file_template, 'r').read()
        ssr_filetemplate = yaml.safe_load(ssr_filetemplate)
        config_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/config.json')
        config_file = open(config_file, 'r')
        config_file_data = json.load(config_file)
        config_yamldata = []
        config_yamldata2 = [config_file_data["configfiledest"]["IPTABLES"], '/etc/init.d/iptables save']
        for key in config_file_data["configfile"].keys():
            if config_file_data["configfile"][key] != config_file_data["configfiledest"][key]:
                config_yamldata.append({'src': os.path.join(settings.BASE_DIR,
                                                            'SSRCHECKER/aom/ansible/{}'.format(
                                                                config_file_data["configfile"][key])),
                                        'dest': config_file_data["configfiledest"][key]})
        ssr_filetemplate[1]["with_items"] = config_yamldata
        ssr_filetemplate[2]["with_items"] = config_yamldata2
        config_file_template = open(config_file_template, 'w')
        yaml.safe_dump(ssr_filetemplate, config_file_template, default_flow_style=False, explicit_start=True)

    def SSRfilesave(self,fileusername=None, filelatest=None, filename=None):
        config_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/config.json')
        config_read = open(config_file, 'r').read()
        condigdata = json.loads(config_read)
        filenames = condigdata["configfile"]
        fileopen = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/{}'.format(filenames[filename])), 'r').read()
        filesave = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/{}'.format(filenames[filename])), 'w')
        masterconfig = SSRmasterconfighistoryModel()
        masterconfig.USERNAME = fileusername
        masterconfig.IP = 'SAVED'
        masterconfig.FILE = filenames[filename]
        masterconfig.CHANGED_ADDED = filelatest
        masterconfig.PREVIOUS = fileopen
        masterconfig.DATE = datetime.datetime.now()
        masterconfig.save()
        filesave.write(filelatest)

    def SSRfilehosts(self):
        open(self.hostsfile, 'w').close()
        ssr_hosts = ['[ssr_init]\n', '[ssr_config]\n', '[ssr_fileconfig]\n']
        ssr_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/roles/p.ssr_init/vars/main.yml')
        ssr_file2 = open(ssr_file, 'r').read()
        ssr_port = yaml.safe_load(ssr_file2)['ssr_port']
        ssr_user = yaml.safe_load(ssr_file2)['ssr_user']
        for ssr_host in ssr_hosts:
            open(self.hostsfile, 'a').write(ssr_host)
            for data in SSRinitdataModel.objects.filter(STATUS='OK'):
                open(self.hostsfile, 'a').write(
                '{} ansible_ssh_port={} ansible_ssh_user={}\n'.format(data, ssr_port, ssr_user))
        open(self.hostsfile, 'a').write('[multi:children]\nssr_init\nssr_config\nssr_fileconfig\n[multi:vars]\nAUTH_BASIC_ENABLED=False\nHOST_KEY_CHECKING=False\nANSIBLE_HOST_KEY_CHECKING=False\n')

    def SSRfileexecute(self):
        ansiblehosts = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/hosts')
        ansible_main = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/main.yml')
        ssr_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/roles/p.ssr_init/vars/main.yml')
        ssr_file2 = open(ssr_file, 'r').read()
        ssr_password = yaml.safe_load(ssr_file2)['ssr_password']
        limit2 = 'ssr_fileconfig'
        tags2 = 'fileconfig_ssr'
        os.system(
            "ansible-playbook -i {} {} --ssh-common-args='-o StrictHostKeyChecking=no' --limit {} --tags {} --extra-vars ansible_become_pass={} --become-method=su -T 30 > {} &".format(
                ansiblehosts, ansible_main, limit2, tags2, ssr_password,
                os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/logs')))


    def SSRfilesyncsave(self, fileusername=None, filelogs='SAVED'):
        logs = open(os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/logs/logs'), 'r').read()
        config_file = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/config.json')
        config_file = open(config_file, 'r')
        config_file_data = json.load(config_file)

        for key, value in config_file_data['configfile'].items():
            fileopen = open(os.path.join(settings.BASE_DIR,
                                         'SSRCHECKER/aom/ansible/{}'.format(config_file_data['configfile'][key])),
                            'r').read()
            if "PLAY RECAP" in logs:
                if config_file_data["configfile"][key] != config_file_data["configfiledest"][key]:
                    try:
                        dataid = SSRmasterconfighistoryModel.objects.filter(FILE=value).latest('id').id
                        datahistory = SSRmasterconfighistoryModel.objects.get(id=dataid)
                        datahistory.IP = filelogs
                        datahistory.DATE = datetime.datetime.now()
                    except:
                        datahistory = SSRmasterconfighistoryModel.objects.create(
                            USERNAME=fileusername,
                            IP=filelogs,
                            FILE=value,
                            CHANGED_ADDED=fileopen,
                            PREVIOUS=fileopen,
                            DATE=datetime.datetime.now()
                        )
                datahistory.save()

