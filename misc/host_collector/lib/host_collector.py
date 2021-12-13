import re
import dockersession
import hashlib
from dbconn import conn
import traceback
re_publicip = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))(?<!127)(?<!^10)(?<!^0)\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!192\.168)(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!\.255$))$'

DB = conn()

class base_host(object):
    def to_dict(self):
        return {
            'hostname': self.hostname,
            'hosttype': self.hosttype,
            'location': self.location,
            'network': self.network,
            'memory': self.network,
            'disk': self.disk,
            'children': self.children
        }

class docker_container(base_host):
    def __init__(self, hostip, container_name):
        self.__hue = dockersession.dockerSession("http://%s:2375" % hostip);
        self.__dSpecs = self.__hue.getContainerSpecifications(container_name);
        self._ip = hostip;
        self._container_name = container_name

    @property
    def uuid(self):
        return hashlib.md5('{0}{1}'.format(self.container_id, self._ip)).hexdigest()

    @property
    def hostname(self):
        return self.__dSpecs['name'];

    @property
    def ip_address(self):
        sample_network = self.__dSpecs['networks'].keys()[0]
        return self.__dSpecs['networks'][sample_network]['ip'];

    @property
    def mac_address(self):
        sample_network = self.__dSpecs['networks'].keys()[0]
        return self.__dSpecs['networks'][sample_network]['mac'];

    @property
    def port_bindings(self):
        return " ".join(self.__dSpecs['ports']).replace('/tcp','') if self.__dSpecs['ports'] else 'N/A'

    @property
    def disk(self):
        return 0;

    @property
    def cpu_count(self):
        return int(self.__dSpecs['cpu_count'])

    @property
    def memory(self):
        return self.__dSpecs['memory']

    @property
    def image_id(self):
        return self.__dSpecs['image_id'];

    @property
    def container_id(self):
        return self.__dSpecs['id']

    @property
    def creation_date(self):
        return self.__dSpecs['creation_date'].split('.')[0].replace('T', ' ')

    def save_to_db(self):
        row={
            'uuid': self.uuid,
            'ctid': self.container_id,
            'container_name': self._container_name,
            'image_id':self.image_id,
            'memory': self.memory,
            'ip_address': self.ip_address,
            'mac_address': self.mac_address,
            'port_bindings': self.port_bindings,
            'cpu_count': self.cpu_count,
            'host_ip': self._ip,
        }
        DB.insert_into_docker_container(row)
        print '{0} DOCKER CONTAINER {1} saved'.format(self._ip,self._container_name)

class openvz_container(base_host):
    def __init__(self, ctid, details,host_ip):
        self._ctid = ctid
        self._details = details
        self._ip = host_ip

    @property
    def ctid(self):
        return self._ctid

    @property
    def disks(self):
        return self._details['disks']

    @property
    def ip_address(self):
        return self._details['ip_address']

    @property
    def memory(self):
        return self._details['mem_size']

    @property
    def hostname(self):
        return self._details['vm_name']

    def save_to_db(self):
        row={
            'host_ip': self._ip,
            'ctid': self._ctid,
            'disks': self.disks,
            'ip_address': self.ip_address,
            'memory': self.memory,
            'hostname':self.hostname,
        }
        print '{0} OPENVZ CONTAINER {1} saved'.format(self._ip,self._ctid)
        DB.insert_into_openvz_container(row)

class xen_virtual_machine(base_host):
    def __init__(self, uuid, details,host_ip):
        self._uuid = uuid
        self._details = details
        self._ip = host_ip

    @property
    def uuid(self):
        return self._uuid

    @property
    def host_ip(self):
        return self._ip

    @property
    def disks(self):
        return self._details['disks']

    @property
    def cpu_count(self):
        return self._details['cpu_count']

    @property
    def ip_address(self):
        return self._details['ip_address']

    @property
    def memory(self):
        return self._details['mem_size']

    @property
    def hostname(self):
        return self._details['vm_name']

    def save_to_db(self):
        row={
            'host_ip': self._ip,
            'uuid': self._uuid,
            'disks': self.disks,
            'cpu_count': self.cpu_count,
            'ip_address': self.ip_address,
            'memory': self.memory,
            'hostname': self.hostname

        }
        print '{0} XEN VM {1} saved'.format(self._ip,self.ip_address)
        DB.insert_into_xen_vm(row)

class physical_host(base_host):
    def __init__(self, ip, hostdict):
        self._raw = hostdict
        self._ip = ip

    @property
    def hosttype(self):
        if 'virtual_machine' in self._raw['ansible_local'] and self._raw['ansible_local']['virtual_machine']:
            for i in self._raw['ansible_local']['virtual_machine']:
                return i
        else:
            return 'Unspecified'
        #return self._raw['ansible_virtualization_type']

    @property
    def hostname(self):
        return self._raw['ansible_hostname']

    @property
    def location(self):
        if re.match(re_publicip, self._ip):
            return 'CLOUD'
        elif '10.168' in self._ip:
            return 'GDC'
        elif '10.167' in self._ip:
            return 'HK'
        else:
            return 'Unknown'

    @property
    def network(self):
        return self._raw['ansible_default_ipv4']

    @property
    def disk(self):
        rVal = {}
        for i in self._raw['ansible_devices']:
            if i.startswith('sd'):
                rVal[i] = self._raw['ansible_devices'][i]['size']
        return rVal

    @property
    def memory(self):
        rVal = {
            'real': self._raw['ansible_memory_mb']['real']['total'],
            'swap': self._raw['ansible_memory_mb']['swap']['total'],
        }
        return rVal

    def save_to_db(self):
        row = {
            'host_ip': self._ip,
            'memory': self.memory['real'],
            'swap': self.memory['real'],
            'hostname': self.hostname,
            'mac': self.network['macaddress'],
            'interface': self.network['interface'],
            'host_type': self.hosttype,
            'location': self.location

        }

        DB.insert_into_physical_host(row)
        DB.delete_disk(self._ip)

        for disk in self.disk:
            row = {
                'disk_name':disk,
                'disk_size':self.disk[disk],
                'host_ip':self._ip
            }
            print row
            DB.insert_into_disk(row)


class docker_host(physical_host):
    @property
    def children(self):
        rVal = []
        for k, container_name in self._raw['ansible_local']['virtual_machine']['docker'].items():
            rVal.append(docker_container(self._ip, container_name['vm_name']))
        return rVal

    def save_to_db(self):
        super(docker_host,self).save_to_db()
        print 'DOCKER HOST {0} saved'.format(self._ip)

        DB.delete_docker_container(self._ip)
        print 'DOCKER HOST {0} Containers deleted'.format(self._ip)
        try:
            for vm in self.children:
                vm.save_to_db()
        except Exception as e:
            print traceback.format_exc()
            print "DOCKER - Error Creating Object {0} ERROR: {1}".format(self._ip,e)

class xen_host(physical_host):
    @property
    def children(self):
        try:
            rVal = []
            for uuid, details in self._raw['ansible_local']['virtual_machine']['xen'].items():
                rVal.append(xen_virtual_machine(uuid, details,self._ip))
            return rVal
        except Exception as e:
            print traceback.format_exc()
            print "XEN - Error Creating Object {0} ERROR: {1}".format(self._ip,e)

    def save_to_db(self):
        super(xen_host,self).save_to_db()
        print 'XEN HOST {0} saved'.format(self._ip)

        DB.delete_xen_vm(self._ip)
        print 'XEN HOST {0} Virtual Machines deleted'.format(self._ip)
        try:
            for vm in self.children:
                vm.save_to_db()
        except Exception as e:
            print traceback.format_exc()
            print e

class openvz_host(physical_host):
    @property
    def children(self):
        try:
            rVal = []
            for ctid, details in self._raw['ansible_local']['virtual_machine']['openvz'].items():
                rVal.append(openvz_container(ctid, details, self._ip))
            return rVal
        except Exception as e:
            print traceback.format_exc()
            print "OPENVZ - Error Creating Object {0} ERROR: {1}".format(self._ip, e)

    def save_to_db(self):
        super(openvz_host, self).save_to_db()
        print 'OPENVZ HOST {0} saved'.format(self._ip)

        DB.delete_openvz_container(self._ip)
        print 'OPENVZ HOST {0} Containers deleted'.format(self._ip)
        try:
            for vm in self.children:
                vm.save_to_db()
        except Exception as e:
            print traceback.format_exc()
            print e



class server_details(object):
    def __init__(self, ip, serverdict):
        self._raw = serverdict
        self._ip = ip

    @property
    def serial(self):
        if 'chassis' in self._raw and 'SerialNumber' in self._raw['chassis']:
            return self._raw['chassis']['SerialNumber']

    @property
    def server_model(self):
        if 'system_information' in self._raw and 'ProductName' in self._raw['system_information']:
            return self._raw['system_information']['ProductName']

    @property
    def idrac_ip(self):
        if 'ipmi_info' in self._raw and 'IDRAC_IP' in self._raw['ipmi_info']:
            return self._raw['ipmi_info']['IDRAC_IP']

    @property
    def psu_count(self):
        if 'ipmi_info' in self._raw and 'PSU_Count' in self._raw['ipmi_info']:
            return self._raw['ipmi_info']['PSU_Count']

    @property
    def chassis_height(self):
        if 'chassis' in self._raw and 'Height' in self._raw['chassis']:
            return self._raw['chassis']['Height']

    @property
    def date_acquired(self):
        if 'shipping_date' in self._raw:
            date = self._raw['shipping_date'].split('/')
            return '{0}-{1}-{2}'.format(date[2],date[0],date[1])

    @property
    def physical_disk(self):
        rVal = {}
        if 'physical_disks' in self._raw:
            for disk in self._raw['physical_disks']:
                rVal[disk['Serial']] = {
                    'size': disk['Capacity'],
                    'model': disk['Model'],
                    'type': 'HDD' if disk['IsRotational'] else 'SSD',
                    'protocol': disk['SMART_ATTR'][
                        'TransportProtocol'] if 'SMART_ATTR' in disk and 'TransportProtocol' in disk[
                        'SMART_ATTR'] else 'UNKNOWN'
                }
        return rVal

    @property
    def physical_memory(self):
        rVal={}
        if 'physical_dimms' in self._raw:
            for dimm_slot,details in self._raw['physical_dimms'].items():
                if details['Size'] != 'No Module Installed':
                    rVal[dimm_slot] = {
                        'size': details['Size'],
                        'serial':details['SerialNumber'],
                        'type':details['Type'],
                        'speed':details['Speed'],
                        'model': details['PartNumber'],
                        'manufacturer':details['Manufacturer']
                    }
        return rVal

    @property
    def physical_cpu(self):
        rVal={}

        if 'physical_processor' in self._raw:
            for cpu,details in self._raw['physical_processor'].items():
                rVal[cpu] = {
                    'core_count': int(details['CoreCount']),
                    'socket_type':details['SocketType'],
                    'thread_count':int(details['ThreadCount']),
                    'max_frequency': details['MaxFrequency'],
                    'model':details['Model']
                }
        return rVal
    
    def save_to_db(self):
        pass
        '''row = {
            'serial':self.serial,
            'host_ip': self._ip,
            'idrac_ip': self.idrac_ip,
            'server_model': self.server_model,
            'psu_count': self.psu_count,
            'chassis_height': self.chassis_height,
            'date_acquired':self.date_acquired
            
        }

        DB.insert_into_server_details(row)
        
         
        DB.delete_server_disk(self._ip)

        for disk in self.physical_disk:
            row = {
                'serial':disk,
                'size': self.physical_disk[disk]['size'],
                'model': self.physical_disk[disk]['model'],
                'type': self.physical_disk[disk]['type'],
                'protocol': self.physical_disk[disk]['protocol']
            }
            print row
            DB.insert_into_server_disk(row)

        DB.delete_server_server_memory(self._ip)

        for dimm_slot in self.physical_memory:
            row = {
                'dimm_slot': dimm_slot,
                'size': self.physical_memory[dimm_slot]['size'],
                'serial': self.physical_memory[dimm_slot]['serial'],
                'type': self.physical_memory[dimm_slot]['type'],
                'speed': self.physical_memory[dimm_slot]['speed'],
                'model': self.physical_memory[dimm_slot]['model'],
                'manufacturer': self.physical_memory[dimm_slot]['manufacturer']
            }
            print row
            DB.insert_into_server_memory(row)'''























