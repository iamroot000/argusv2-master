#!/usr/bin/python3
#created by: Yroll Jay-R Macalino
from subprocess import *
from py_config import colordesign
import os, shutil, getpass, json, run, yaml, sys
class Collect():
    def __init__(self):
        # variables
        with open('info.json') as f_object:
            location = json.load(f_object)
        self.d1_location = location["directory1_location"]
        self.ansible_loc = self.d1_location + "ansible/"
        self.ansible_hosts_f = self.ansible_loc + "hosts"
        self.ansible_main = self.ansible_loc + "main.yml"
        self.ansible_hosts = self.ansible_loc + "hosts"
        self.ansible_hosts1 = self.ansible_hosts + ".bak"
        self.ansible_ssr_config_vars = self.ansible_loc + "roles/p.ssr_config/vars/main.yml"
        self.ansible_ssr_init_vars = self.ansible_loc + "roles/p.ssr_init/vars/main.yml"
        self.ansible_ssr_port_print =  colordesign("cwhite") + "Press " + colordesign("cred") + "Enter"	+ colordesign("cwhite") + " to use default port " + colordesign("cred") + "3389" + colordesign("cnormal")
        self.num3 = colordesign('cred') + "[+] " + colordesign("cwhite") + "SSR Initialization and Configuration\n"
        self.init_ask = colordesign("cred") + "\t1.)" + colordesign("cnormal") + " SSR Initialization\n"
        self.config_ask = colordesign("cred") + "\t2.)" + colordesign("cnormal") + " SSR Configuration\n"
        self.ssr_choose = "Num]: " + colordesign("cred")
        self.ip_ask = colordesign("ccyan") + "Have you added IP? [y/n]? " + colordesign("cnormal")
        self.ip_add = colordesign('cwhite') + "---" + colordesign('cyellow') + " Start Adding. To set password " + colordesign('cred') + ":p " + colordesign('cyellow') + " or to save and quit " + colordesign('cred') + ":q " + colordesign('cwhite') + "---" + colordesign('cgreen')
        self.ip_add2 = colordesign('cwhite') + "---" + colordesign('cyellow') + " Start Adding. To save and quit " + colordesign('cred') + ":q " + colordesign('cwhite') + "---" + colordesign('cgreen')
        self.ip_pass = colordesign('cwhite') + "---" + colordesign('cyellow') + " Password: "
        self.ansible_pass = { "ansible_ssh_pass": "centos7" }
        self.ansible_conf = { "ansible_ssh_user": "root", "ansible_ssh_port": "22"}
        self.hosts_ssr_init = [ "[ssr_init]" ]
        self.hosts_ssr_config = [ "[ssr_config]" ]
        self.hosts_config = [ "[multi:children]", "ssr_init", "ssr_config", "[multi:vars]", str(self.ansible_conf).replace(': ', '=').replace('{', '').replace('}', '').replace("'", "").replace(', ', '\n'),  "AUTH_BASIC_ENABLED=False", "HOST_KEY_CHECKING=False", "ANSIBLE_HOST_KEY_CHECKING=False" ]
        self.show = [ self.num3, self.init_ask, self.config_ask ]
        self.configfile = "ls " + self.d1_location
        self.invalid_input = colordesign('cred') + "Invalid Input!" + colordesign('cnormal')
        self.ip_lists = []
        with open(self.ansible_ssr_config_vars) as f_object:
            self.vars_yml = yaml.load(f_object)
        with open(self.ansible_ssr_init_vars) as f_object2:
            self.vars_yml2 = yaml.load(f_object2)
        with os.popen(self.configfile) as configfilelocation:
            self.configfileL = configfilelocation.read()
    def SSR_init(self):
        def ssrportdefault(portset):
            self.vars_yml['ssr_port'] = portset
            with open(self.ansible_ssr_config_vars, 'w') as f_object:
                yaml.dump(self.vars_yml, f_object, default_flow_style=False, explicit_start=True)
        def replacefile(changed1, changed2):
            # setting host and password on yml file
            with open(self.ansible_hosts_f, 'r') as replace_hosts:
                hosts_file = replace_hosts.read()
            replacenow = hosts_file.replace(changed1, changed2)
            with open(self.ansible_hosts_f, 'w') as replace_hosts2:
                replaced_hosts = replace_hosts2.write(replacenow)
            return replaced_hosts
        def invalid(adding_msg):
            print(colordesign('cnormal') + "#####################")
            print(self.invalid_input)
            print(colordesign('cnormal') + "#####################")
            print(adding_msg)
        def configfile(banner):
            shutil.copyfile(self.ansible_hosts, self.ansible_hosts1)
            open(self.ansible_hosts, 'w').close()
            print(banner)
        def hostsconfig():
            while True:
                ip_addr = input()
                if len(ip_addr) > 7:
                    ip_addr_check = ip_addr.strip()
                    self.ip_lists.append(ip_addr_check)
                elif ip_addr == ':p':
                    ip_pass = getpass.getpass(self.ip_pass)
                    self.ansible_pass['ansible_ssh_pass'] = ip_pass
                    for ip_list in self.ip_lists:
                        ip_addr_with_pass = ip_list + " ansible_ssh_pass=" + self.ansible_pass['ansible_ssh_pass']
                        self.hosts_ssr_init.insert(1, ip_addr_with_pass.strip())
                        self.hosts_ssr_config.insert(1, ip_addr_with_pass.strip())
                    del self.ip_lists[0:]
                    print(self.ip_add)
                elif ip_addr == ':q':
                    call("clear")
                    print(colordesign('cnormal'))
                    print()
                    break
                else:
                    invalid(self.ip_add)
        def hostsconfig2():
            while True:
                ip_addr = input()
                if len(ip_addr) > 7:
                    ip_addr_check = ip_addr.strip()
                    self.ip_lists.append(ip_addr_check)
                    for ip_list in self.ip_lists:
                        ip_addr_with_pass = ip_list
                        self.hosts_ssr_init.insert(1, ip_addr_with_pass.strip())
                        self.hosts_ssr_config.insert(1, ip_addr_with_pass.strip())
                elif ip_addr == ':q':
                    call("clear")
                    print(colordesign('cnormal'))
                    break
                else:
                    invalid(self.ip_add2)
        def hostsall_func():
            hosts_all = self.hosts_ssr_init + self.hosts_ssr_config + self.hosts_config
            for hosts_all_l in hosts_all:
                with open(self.ansible_hosts, 'a') as hosts_file:
                    hosts_file.write(hosts_all_l)
                    hosts_file.write('\n')
        def printing():
            call("clear")
            call(["pyfiglet", "-j", "center", "--color=RED", "AOM Tools"])
            for ssr_show in self.show:
                print(ssr_show)
        def terminalmode(ansiblehosts, limit, tags):
            call(["ansible-playbook", "-i", ansiblehosts, self.ansible_main, "--ssh-common-args='-o StrictHostKeyChecking=no'", "--limit", limit, "--tags", tags])
        def terminalmode2(ansiblehosts, limit, tags):
            ansible_su_password = "ansible_become_pass=" + self.vars_yml2['ssr_password']
            call(["ansible-playbook", "-i", ansiblehosts, self.ansible_main, "--ssh-common-args='-o StrictHostKeyChecking=no'", "--limit", limit, "--tags", tags, "--extra-vars", ansible_su_password, '--become-method=su'])
        printing()
        choose = input(self.ssr_choose)
        if int(choose) == 1:
            ip_ask_input = input(self.ip_ask)
            if str(ip_ask_input).lower() == 'n' or len(ip_ask_input) == 0:
                configfile(self.ip_add)
                hostsconfig()
                hostsall_func()
                terminalmode(self.ansible_hosts, "ssr_init,ssr_config", "initialization_ssr,config_ssr")
            elif str(ip_ask_input).lower() == 'y':
                shutil.copyfile(self.ansible_hosts, self.ansible_hosts1)
                terminalmode(self.ansible_hosts1, "ssr_init,ssr_config", "initialization_ssr,config_ssr")
        elif int(choose) == 2:
            ip_ask_input = input(self.ip_ask)
            if str(ip_ask_input).lower() == 'n' or len(ip_ask_input) == 0:
                configfile(self.ip_add2)
                hostsconfig2()
                print(self.ansible_ssr_port_print)
                ssr_port_q = 'SSR PORT: ' + colordesign('cred')
                port_ssr = input(ssr_port_q)
                print(colordesign('cnormal'))
                try:
                    if len(port_ssr) == 0:
                        ssrportdefault('3389')
                    elif int(port_ssr) >= 1 and int(port_ssr) <= 65535:
                        ssrportdefault(port_ssr)
                    else:
                        print(colordesign('cred') + "Port should be in range of 1 to 65535." + colordesign('cnormal'))
                        sys.exit(1)
                except ValueError:
                    print(colordesign('cred') + "Port should be numbers!" + colordesign('cnormal'))
                    sys.exit(1)
                hostsall_func()
                replacefile('ansible_ssh_user=root', 'ansible_ssh_user=ommgr')
                replacefile('ansible_ssh_port=22', 'ansible_ssh_port=28032')
                terminalmode2(self.ansible_hosts, "ssr_config", "config_ssr")
            elif str(ip_ask_input).lower() == 'y':
                shutil.copyfile(self.ansible_hosts, self.ansible_hosts1)
                ssrportdefault('3389')
                replacefile('ansible_ssh_user=root', 'ansible_ssh_user=ommgr')
                replacefile('ansible_ssh_port=22', 'ansible_ssh_port=28032')
                terminalmode2(self.ansible_hosts, "ssr_config", "config_ssr")




