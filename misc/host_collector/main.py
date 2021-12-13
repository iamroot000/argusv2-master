import sys
import argparse

def log():
    from lib import log
    log.flush = sys.stdout.flush
    log.write = log.info
    sys.stdout = log;

log()

from lib.host_collector import docker_host, xen_host, openvz_host, physical_host
import os
import json


def main(floc):

    hosts = {}

    FACT_LOCATION = floc

    for host in os.listdir(FACT_LOCATION):
        f = open('{0}/{1}'.format(FACT_LOCATION,host))
        raw = f.read()
        f.close()
        print 'Parsing json hostfile {0}/{1}'.format(FACT_LOCATION,host)
        try:
            hostdict = json.loads(raw)
            if 'virtual_machine' in hostdict['ansible_local'] and hostdict['ansible_local']['virtual_machine']:
                if 'docker' in hostdict['ansible_local']['virtual_machine']:
                    print 'DOCKER_HOST',host
                    hosts[host] = docker_host(host, hostdict)
                elif 'xen' in hostdict['ansible_local']['virtual_machine']:
                    print  'XEN HOST',host
                    hosts[host] = xen_host(host, hostdict)
                elif 'openvz' in hostdict['ansible_local']['virtual_machine']:
                    print host, 'OPENVZ HOST',host
                    hosts[host] = openvz_host(host, hostdict)
            else:
                print host,'PHYSICAL HOST',host
                hosts[host] = physical_host(host, hostdict)
        except Exception as e:
            print 'Error parsing json hostfile {0}/{1} Error: {2}'.format(FACT_LOCATION,host,e)

    for host in hosts:
        hosts[host].save_to_db()


if __name__ == '__main__':
    parser = argparse.ArgumentParser();
    parser.add_argument('--fact-dir',help='Absolute path to Host facts directory');
    args = parser.parse_args();

    if args.fact_dir:
        main(args.fact_dir)
    else:
        print 'Please add the absolute path to the host facts directory'

'''for host in hosts:
    hosts[host].save_to_db()

for host in hosts:
    try:
        print '{0}\t{1}'.format(hosts[host].network['macaddress'], hosts[host].network['interface'])
    except Exception as e:
        print host, e

for host in hosts:
    try:
        print '{0}\t{1}\t{3}'.format(hosts[host].product_details['product_name'],
                                     hosts[host].product_details['product_serial'],
                                     hosts[host].product_details['product_date_bought'])
    except Exception as e:
        print host, e

for host in hosts:
    print '{0}\t{1}\t{2}\t{3}'.format(hosts[host].cpu_info['processor_count'], hosts[host].cpu_info['processor_vcpus'],
                                      hosts[host].cpu_info['processor_cores'],
                                      hosts[host].cpu_info['processor_threads_per_core'])

for host in hosts:
    print '{0}\t{1}'.format(hosts[host].memory['module_count'], hosts[host].memory['memory_per_module'])

for host in hosts:
    try:
        print '{0}\t{1}\t{2}\t{3}'.format(hosts[host].memory['real'], hosts[host].memory['swap'],
                                          hosts[host].memory['physical']['mem_count'],
                                          hosts[host].memory['physical']['mem_size_per_stick'])
    except:
        print host, 'ERROR'

for host in hosts:
    print hosts[host].product_details['product_date_bought']

for host in hosts:
    print '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}\t{11}\t{12}\t{13}\t{14}\t{15}\t{16}'.format(
        host,
        hosts[host].product_details['product_name'],
        hosts[host].product_details['product_serial'],
        hosts[host].product_details['product_date_bought'],
        hosts[host].cpu_info['processor_count'],
        hosts[host].cpu_info['processor_vcpus'],
        hosts[host].cpu_info['processor_cores'],
        hosts[host].cpu_info['processor_vcpus'],
        hosts[host].cpu_info['processor_name'],
        hosts[host].memory['real'],
        hosts[host].memory['swap'],
        hosts[host].memory['physical']['mem_count'],
        hosts[host].memory['physical']['mem_size_per_stick'],
        hosts[host].hostname,
        hosts[host].network['macaddress'],
        hosts[host].network['interface'],
        hosts[host].hosttype
    )

for i in hosts:
    if hosts[i].hosttype == 'xen':
        for vm in hosts[i].children:
            print '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}'.format(
                vm.ip_address,
                i,
                vm.uuid,
                vm.cpu_count,
                vm.disks,
                vm.memory,
                vm._details['vm_name']
            )

for i in hosts:
    if hosts[i].hosttype == 'openvz':
        for vm in hosts[i].children:
            print '{0}\t{1}\t{2}\t{3}\t{4}\t{5}'.format(
                vm.ip_address,
                i,
                vm.ctid,
                vm.disks,
                vm.memory,
                vm._details['vm_name']
            )

for i in hosts:
    if hosts[i].hosttype == 'kvm':
        try:
            for vm in hosts[i].children:
                print '{0}\t{1}\t{2}\t{3}'.format(
                    vm._container_name,
                    i,
                    vm.memory,
                    vm.port_bindings
                )
        except Exception as e:
            print 'ERROR',e'''