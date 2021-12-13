from django.conf import settings
from .models import *
import os, paramiko, yaml, json, time, base64, socket




class v2raysave():
    def v2raycheck(self, ssrip, ssrport):
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


    def v2rayinfo(self, IPok, IPIDC=None, SSRerror='TIMEOUT', SSRstatus=True, SSRrestart=False):
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
            if SSRrestart is True:
                try:
                    stdin, stdout, stderr = ssh.exec_command('su root -c "service v2ray restart"')
                    # stdin, stdout, stderr = ssh.exec_command('cat /bak/bin/iptables.sh')
                    # time.sleep(5)
                    # print(stdout.read())
                    stdin.write('{}\n'.format(ssr_password))
                    # time.sleep(10)
                except Exception as e:
                    pass
                restartyrm = os.path.join(settings.BASE_DIR,'SSRCHECKER/aom/ansible/restart.yml')
                hostsfile = os.path.join(settings.BASE_DIR, 'SSRCHECKER/aom/ansible/hosts_v2ray_restart')
                open(hostsfile, 'w').close()
                ssr_hosts = ['[v2ray_init]\n', '[v2ray_config]\n', '[v2ray_fileconfig]\n']
                for ssr_host in ssr_hosts:
                    open(hostsfile, 'a').write(ssr_host)
                    for data in (IPok,):
                            open(hostsfile, 'a').write(
                                '{} ansible_ssh_port={} ansible_ssh_user={}\n'.format(data, ssr_port, ssr_user))
                open(hostsfile, 'a').write(
                    '[multi:children]\nv2ray_init\nv2ray_config\nv2ray_fileconfig\n[multi:vars]\nAUTH_BASIC_ENABLED=False\nHOST_KEY_CHECKING=False\nANSIBLE_HOST_KEY_CHECKING=False\n')
                os.system("ansible-playbook -i {} {} --ssh-common-args='-o StrictHostKeyChecking=no' --extra-vars ansible_become_pass={} --become-method=su --limit v2ray_config 2>/dev/null".format(hostsfile,restartyrm, ssr_password))
            # print('processing')
            stdin, stdout, stderr = ssh.exec_command('cat /etc/v2ray/233blog_v2ray_config.json')
            if stderr.read():
                return {
                    "V2RAY_PORT": 23456,
                    "V2RAY_STATUS": "NO V2RAY INSTALLED",
                    "V2RAY_URL": None,
                    "V2RAY_DOMAIN": None,
                    "V2RAY_PATH": None
                }
            ssrdata = stdout.read().decode('utf-8')
            stdin, stdout, stderr = ssh.exec_command('cat /etc/v2ray/config.json')
            ws_settings = stdout.read().decode('utf-8')
            ssrdata = json.loads(ssrdata)
            if IPIDC is None:
                data_db = SSRinitdataModel.objects.get(IP=IPok)
                datadb = data_db.IDC
                print(data_db.IDC)
            else:
                datadb = IPIDC
            # datadb = 'tencent_cloud'
            print("THIS is the IDC {}".format(datadb))
            stdin, stdout, stderr = ssh.exec_command('grep -ril {} /etc/nginx/conf.d/'.format("server"))
            # if stdout.read() is None:
            #     return {
            #         "V2RAY_PORT": 23456,
            #         "V2RAY_STATUS": "NO V2RAY INSTALLED",
            #         "V2RAY_URL": None,
            #         "V2RAY_DOMAIN": None,
            #         "V2RAY_PATH": None
            #     }
            maindom = stdout.read().decode('utf-8').strip().split('.')
            print(maindom)
            v2raydomain = "{}.{}".format(maindom[2], maindom[3])
            print(v2raydomain)
            print(maindom)
            v2ray_dom = "https://{}.{}".format(maindom[1].split('/')[-1], v2raydomain)
            for ws_set in ws_settings.split('\n'):
                if "wsSettings" in ws_set:
                    web_socket = ws_set.split("path")[-1].split("/")[-1].replace('"}', '')
                    break
                else:
                    web_socket = ""
            v2ray_url_data = {

                            "v": "2",

                            "ps": "233v2.com_{}".format(ssrdata["outbounds"][0]["settings"]["vnext"][0]["address"]),

                            "add": "{}".format(ssrdata["outbounds"][0]["settings"]["vnext"][0]["address"]),

                            "port": "{}".format(ssrdata["outbounds"][0]["settings"]["vnext"][0]["port"]),

                            "id": "{}".format(ssrdata["outbounds"][0]["settings"]["vnext"][0]["users"][0]['id']),

                            "aid": "{}".format(ssrdata["outbounds"][0]["settings"]["vnext"][0]["users"][0]['alterId']),

                            "net": "{}".format(ssrdata["outbounds"][0]["streamSettings"]["network"]),

                            "type": "none",

                            "host": v2ray_dom,

                            "path": web_socket,

                            "tls": ""

                            }
            ip = IPok
            # ip = requests.get('http://ipinfo.io/ip').text
            V2RAY_URL =  base64.b64encode(json.dumps(v2ray_url_data, indent=4).encode('ascii'))
            # print(SSR_url64)
            ssh.close()
            # time.sleep(10)
            if SSRstatus is True:
                ssrstatus = self.v2raycheck(ssrip=str(IPok), ssrport=ssrdata["outbounds"][0]["settings"]["vnext"][0]["port"])
                return {
                    "V2RAY_PORT":  ssrdata["outbounds"][0]["settings"]["vnext"][0]["port"],
                    "V2RAY_STATUS": ssrstatus,
                    "V2RAY_URL": "vmess://{}".format(V2RAY_URL.decode('utf-8')),
                    "V2RAY_DOMAIN": v2ray_dom,
                    "V2RAY_PATH": web_socket
                }
            else:
                return {
                    "V2RAY_URL": "vmess://{}".format(V2RAY_URL.decode('utf-8')),
                    "V2RAY_DOMAIN": v2ray_dom,
                    "V2RAY_PATH": web_socket
                }
        except Exception as e:
            print("ssrinfo exception " + str(e))
            return SSRerror
            # return str('This is the error for v2ray process {}'.format(e))

