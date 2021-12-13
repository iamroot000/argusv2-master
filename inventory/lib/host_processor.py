from inventory.lib import dockersession
from inventory.models import asset, physical_server
from inventory.models import physical_host, host_mount_points, docker_container, xen_vm, openvz_container,cloud_host
import hashlib
import datetime


from django.utils import timezone


def generate_asset_id(v1, v2, asset_type):
    return '{0}-{1}'.format(asset_type, hashlib.md5(v1 + v2).hexdigest()[:7])


class physical_host_details(object):
    def __init__(self, hostdict):
        self._raw = hostdict

    @property
    def host_type(self):
        if 'virtual_machine' in self._raw['ansible_local'] and self._raw['ansible_local']['virtual_machine'] and not 'error' in self._raw['ansible_local']['virtual_machine']:
            for i in self._raw['ansible_local']['virtual_machine']:
                return i
        else:
            return 'N/A'

    @property
    def host_name(self):
        return self._raw['ansible_hostname']

    @property
    def fqdn(self):
        return self._raw['ansible_fqdn']

    @property
    def network_interface(self):
        if 'ansible_default_ipv4' in self._raw and 'interface' in self._raw['ansible_default_ipv4']:
            return self._raw['ansible_default_ipv4']['interface']
        return 'N/A'

    @property
    def ip(self):
        if 'ansible_default_ipv4' in self._raw and 'address' in self._raw['ansible_default_ipv4']:
            return self._raw['ansible_default_ipv4']['address']
        return 'N/A'

    @property
    def mac(self):
        if 'ansible_default_ipv4' in self._raw and 'macaddress' in self._raw['ansible_default_ipv4']:
            return self._raw['ansible_default_ipv4']['macaddress']
        return 'N/A'
    @property
    def disk_mounts(self):
        rVal = {}
        exclude =['dev','run','docker','boot','sys','boot','sys','devicemapper','mnt','xen']


        for i in self._raw['ansible_mounts']:
            flag = False
            for x in exclude:
                if x in i['mount']:
                    flag = True
            if not flag:
                rVal[i['device']] = {
                    'capacity':float(i['size_total'])/1048576,
                    'mount_point':i['mount']
                }
        return rVal

    @property
    def memory(self):
        return int(self._raw['ansible_memory_mb']['real']['total'])

    @property
    def guest_hosts(self):
        rVal = []
        if self.host_type == 'xen':
            for uuid, details in self._raw['ansible_local']['virtual_machine'][self.host_type].items():
                rVal.append(xen_virtual_machine_details(
                    uuid, details, self.ip))
                print 'XEN VM {0} - {1}'.format(self.ip, uuid)
        elif self.host_type == 'docker':
            for container_id, container_name in self._raw['ansible_local']['virtual_machine'][self.host_type].items():
                try:
                    rVal.append(docker_container_details(
                        self.ip, container_name['vm_name']))
                    print 'DOCKER CONTAINER {0} - {1}'.format(self.ip, container_name['vm_name'])
                except Exception as e:
                    print 'ERROR DOCKER CONTAINER - {0} - {1} - {2}'.format(self.ip, container_name['vm_name'], e)
        elif self.host_type == 'openvz':
            for ctid, details in self._raw['ansible_local']['virtual_machine'][self.host_type].items():
                rVal.append(openvz_container_details(ctid, details, self.ip))
                print 'OPENVZ CONTAINER {0} - {1}'.format(self.ip, ctid)
        else:
            return None
        return rVal

    @property
    def serial(self):
        if 'ansible_product_serial' in self._raw:
            return self._raw['ansible_product_serial']
        return 'N/A'

    @property
    def server_model(self):
        if 'ansible_product_name' in self._raw:
            return self._raw['ansible_product_name']
        return 'N/A'

    def save_to_db(self):
        now = timezone.now()

        try:
            PHYSICAL_SERVER = physical_server.objects.get(serial=self.serial)
        except:
            PHYSICAL_SERVER_ASSET = asset(
                asset_id=generate_asset_id(self.serial, self.serial, 'SERVER'),
                asset_type='SERVER',
                entity='PHYSICAL',
                last_updated=now
            )
            PHYSICAL_SERVER_ASSET.save()
            PHYSICAL_SERVER = physical_server(
                server_model=self.server_model,
                serial=self.serial,
                asset=PHYSICAL_SERVER_ASSET,
                idrac_ip='N/A',
                psu_count=0,
                chassis_height='N/A',
                last_updated=now
            )
            PHYSICAL_SERVER.save()

        PHYSICAL_HOST_ASSET = asset(
            asset_id=generate_asset_id(
                self.mac, self.mac, 'PHYSICAL_HOST'),
            asset_type='PHYSICAL_HOST',
            entity='VIRTUAL',
            last_updated=now
        )
        PHYSICAL_HOST_ASSET.save()

        PHYSICAL_HOST = physical_host(
            asset=PHYSICAL_HOST_ASSET,
            parent_server=PHYSICAL_SERVER,
            host_name=self.host_name,
            fqdn=self.fqdn,
            host_type=self.host_type,
            host_ip=self.ip,
            memory=self.memory,
            network_interface=self.network_interface,
            mac=self.mac,
            last_updated=now
        )
        PHYSICAL_HOST.save()

        MOUNTS = host_mount_points.objects.filter(host=PHYSICAL_HOST_ASSET.asset_id)



        if MOUNTS:
            for mount_obj in MOUNTS:
                mount_obj.delete()

        for mount,det in self.disk_mounts.items():
            MOUNT_POINT = host_mount_points(
                host=PHYSICAL_HOST_ASSET,
                capacity = det['capacity'],
                mount_point = det['mount_point'],
                device= mount,
                last_updated=now
            )
            MOUNT_POINT.save()


        if self.guest_hosts is not None:
            for guest_obj in self.guest_hosts:
                guest_obj.save_to_db()


class docker_container_details(object):
    def __init__(self, hostip, container_name):
        self.__hue = dockersession.dockerSession("http://%s:2375" % hostip)
        self.__dSpecs = self.__hue.getContainerSpecifications(container_name)
        self._ip = hostip
        self._container_name = container_name

    @property
    def hostname(self):
        return self.__dSpecs['name']

    @property
    def container_ip(self):
        sample_network = self.__dSpecs['networks'].keys()[0]
        return self.__dSpecs['networks'][sample_network]['ip']

    @property
    def mac_address(self):
        sample_network = self.__dSpecs['networks'].keys()[0]
        return self.__dSpecs['networks'][sample_network]['mac']

    @property
    def port_bindings(self):
        return " ".join(self.__dSpecs['ports']).replace('/tcp', '') if self.__dSpecs['ports'] else 'N/A'

    @property
    def disk(self):
        return 0

    @property
    def cpu_count(self):
        return int(self.__dSpecs['cpu_count'])

    @property
    def memory(self):
        return int(self.__dSpecs['memory']) / 1048576

    @property
    def image_id(self):
        return self.__dSpecs['image_id']

    @property
    def container_id(self):
        return self.__dSpecs['id']

    @property
    def creation_date(self):
        return self.__dSpecs['creation_date'].split('.')[0].replace('T', ' ')

    def save_to_db(self):
        now = timezone.now()
        PHYSICAL_HOST = physical_host.objects.get(host_ip=self._ip)

        DOCKER_CONTAINER_ASSET = asset(
            asset_id=generate_asset_id(
                self._container_name, self._ip, 'DOCKER_CONTAINER'),
            asset_type='DOCKER_CONTAINER',
            entity='VIRTUAL',
            last_updated=now
        )
        DOCKER_CONTAINER_ASSET.save()

        DOCKER_CONTAINER = docker_container(
            asset=DOCKER_CONTAINER_ASSET,
            host=PHYSICAL_HOST,
            container_id=self._container_name,
            image_id=self.image_id,
            memory=self.memory,
            container_ip=self.container_ip,
            port_bindings=self.port_bindings,
            cpu_count=self.cpu_count,
            last_updated=now
        )
        DOCKER_CONTAINER.save()


class xen_virtual_machine_details(object):
    def __init__(self, uuid, details, host_ip):
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
    def disk(self):
        return int(self._details['disks'].split()[0])*1024

    @property
    def cpu_count(self):
        return self._details['cpu_count']

    @property
    def vm_ip(self):
        return self._details['ip_address']

    @property
    def memory(self):
        return int(self._details['mem_size'].split()[0])

    @property
    def host_name(self):
        return self._details['vm_name']

    def save_to_db(self):
        now = timezone.now()
        PHYSICAL_HOST = physical_host.objects.get(host_ip=self._ip)

        XEN_VM_ASSET = asset(
            asset_id=generate_asset_id(self._uuid, self._ip, 'XEN_VM'),
            asset_type='XEN_VM',
            entity='VIRTUAL',
            last_updated=now
        )
        XEN_VM_ASSET.save()

        XEN_VM = xen_vm(
            asset=XEN_VM_ASSET,
            host=PHYSICAL_HOST,
            uuid=self.uuid,
            memory=self.memory,
            disk=self.disk,
            cpu_count=self.cpu_count,
            vm_ip=self.vm_ip,
            host_name=self.host_name,
            last_updated=now
        )
        XEN_VM.save()


class openvz_container_details(object):
    def __init__(self, ctid, details, host_ip):
        self._ctid = ctid
        self._details = details
        self._ip = host_ip

    @property
    def ctid(self):
        return self._ctid

    @property
    def host_ip(self):
        return self._ip

    @property
    def disk(self):
        return int(self._details['disks'].split()[0])

    @property
    def container_ip(self):
        return self._details['ip_address']

    @property
    def memory(self):
        return int(self._details['mem_size'].split()[0])

    @property
    def host_name(self):
        return self._details['vm_name']

    def save_to_db(self):
        now = timezone.now()
        PHYSICAL_HOST = physical_host.objects.get(host_ip=self._ip)

        OPENVZ_CONTAINER_ASSET = asset(
            asset_id=generate_asset_id(
                self._ctid, self._ip, 'OPENVZ_CONTAINER'),
            asset_type='OPENVZ_CONTAINER',
            entity='VIRTUAL',
            last_updated=now
        )
        OPENVZ_CONTAINER_ASSET.save()

        OPENVZ_CONTAINER = openvz_container(
            asset=OPENVZ_CONTAINER_ASSET,
            host=PHYSICAL_HOST,
            ctid=self.ctid,
            memory=self.memory,
            disk=self.disk,
            container_ip=self.container_ip,
            host_name=self.host_name,
            last_updated=now
        )
        OPENVZ_CONTAINER.save()




class cloud_host_details(object):
    def __init__(self, ip, hostdict):
        self._raw = hostdict
        self._ip = ip

    @property
    def host_name(self):
        return self._raw['ansible_hostname']

    @property
    def fqdn(self):
        return self._raw['ansible_fqdn']

    @property
    def ip(self):
        return self._ip

    @property
    def disk_mounts(self):
        rVal = {}
        exclude =['dev','run','docker','boot','sys','boot','sys','devicemapper','mnt','xen']


        for i in self._raw['ansible_mounts']:
            flag = False
            for x in exclude:
                if x in i['mount']:
                    flag = True
            if not flag:
                rVal[i['device']] = {
                    'capacity':float(i['size_total'])/1048576,
                    'mount_point':i['mount']
                }
        return rVal

    @property
    def memory(self):
        return int(self._raw['ansible_memory_mb']['real']['total'])


    @property
    def serial(self):
        return hashlib.md5(self.ip).hexdigest()[:7]


    def save_to_db(self):
        now = timezone.now()

        CLOUD_HOST_ASSET = asset(
            asset_id=generate_asset_id(self.ip, self.serial, 'CLOUD_HOST'),
            asset_type='CLOUD_HOST',
            entity='VIRTUAL',
            last_updated=now
        )

        CLOUD_HOST_ASSET.save()

        CLOUD_HOST = cloud_host(
            serial=self.serial,
            asset=CLOUD_HOST_ASSET,
            memory=self.memory,
            host_ip=self.ip,
            fqdn=self.fqdn,
            last_updated=now
        )
        CLOUD_HOST.save()

        MOUNTS = host_mount_points.objects.filter(host=CLOUD_HOST_ASSET.asset_id)

        if MOUNTS:
            for mount_obj in MOUNTS:
                mount_obj.delete()

        for mount,det in self.disk_mounts.items():
            MOUNT_POINT = host_mount_points(
                host=CLOUD_HOST_ASSET,
                capacity = det['capacity'],
                mount_point = det['mount_point'],
                device= mount,
                last_updated=now
            )
            MOUNT_POINT.save()


