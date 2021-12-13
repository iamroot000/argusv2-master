from inventory.models import asset, physical_server, physical_memory, physical_disk, physical_cpu, physical_storage_controller
import hashlib
import datetime

from django.utils import timezone


def generate_asset_id(v1, v2, asset_type):
    return '{0}-{1}'.format(asset_type, hashlib.md5(v1 + v2).hexdigest()[:7])


class asset_details(object):

    def __init__(self, serverdict):
        self._raw = serverdict

    @property
    def serial(self):
        if 'chassis' in self._raw and 'SerialNumber' in self._raw['chassis']:
            return self._raw['chassis']['SerialNumber']

    @property
    def server_model(self):
        if 'system_information' in self._raw and 'ProductName' in self._raw['system_information']:
            return self._raw['system_information']['ProductName']
        return 'SERVER N/A'

    @property
    def idrac_ip(self):
        if 'ipmi_info' in self._raw and 'IDRAC_IP' in self._raw['ipmi_info']:
            return self._raw['ipmi_info']['IDRAC_IP']

    @property
    def psu_count(self):
        if 'ipmi_info' in self._raw and 'PSU_Count' in self._raw['ipmi_info']:
            return self._raw['ipmi_info']['PSU_Count']
        else:
            return 0
    @property
    def chassis_height(self):
        if 'chassis' in self._raw and 'Height' in self._raw['chassis']:
            return self._raw['chassis']['Height']

    @property
    def date_acquired(self):
        if 'shipping_date' in self._raw:
            try:
                print self._raw['shipping_date']
                return datetime.datetime.strptime(self._raw['shipping_date'], '%m/%d/%Y')
            except:
                print self._raw['shipping_date']
                return None

    @property
    def physical_disk(self):
        rVal = {}
        if 'physical_disks' in self._raw and not 'error' in self._raw['physical_disks']:
            for disk in self._raw['physical_disks']:
                rVal[disk['Serial']] = {
                    'size': disk['Capacity'] if 'Capacity' in disk else 'NA',
                    'model': disk['Model'],
                    'type': 'HDD' if disk['IsRotational'] else 'SSD',
                    'protocol': disk['TransportProtocol'] if 'TransportProtocol' in disk else 'UNKNOWN'
                }
        return rVal

    @property
    def physical_memory(self):
        rVal = {}
        if 'physical_dimms' in self._raw:
            for dimm_slot, details in self._raw['physical_dimms'].items():
                if details['Size'] != 'No Module Installed':
                    rVal[dimm_slot] = {
                        'size': details['Size'],
                        'serial': details['SerialNumber'],
                        'type': details['Type'],
                        'speed': details['Speed'],
                        'model': details['PartNumber'],
                        'manufacturer': details['Manufacturer']
                    }
        return rVal

    @property
    def physical_cpu(self):
        rVal = {}

        if 'physical_processors' in self._raw:
            for cpu, details in self._raw['physical_processors'].items():
                rVal[cpu] = {
                    'core_count': int(details['CoreCount']),
                    'socket_type': details['SocketType'],
                    'thread_count': int(details['ThreadCount']),
                    'max_frequency': details['MaxFrequency'],
                    'model': details['Model']
                }
        return rVal

    @property
    def physical_storage_controller(self):
        if not 'storage_controller' in self._raw:
            print self.serial,'NOT FOUND'
            return None

        rVal={
            self._raw['storage_controller']['Model']:{
                "capacity":None,
                'drive_count':None,
                'primary_raid_level':None,
                'secondary_raid_level':None,
                'span_count':None,
                'span_depth':None
            }
        }

        if 'RaidInformation' in self._raw['storage_controller']:
            if 'Capacity' in self._raw['storage_controller']['RaidInformation'] and self._raw['storage_controller']['RaidInformation']['Capacity']:
                rVal[self._raw['storage_controller']['Model']]['capacity'] = self._raw['storage_controller']['RaidInformation']['Capacity'] 
            if 'DriveCount' in self._raw['storage_controller']['RaidInformation'] and self._raw['storage_controller']['RaidInformation']['DriveCount']:
                rVal[self._raw['storage_controller']['Model']]['drive_count'] = int(self._raw['storage_controller']['RaidInformation']['DriveCount'])
            if 'RaidLevel' in self._raw['storage_controller']['RaidInformation'] and self._raw['storage_controller']['RaidInformation']['RaidLevel']:
                for i in self._raw['storage_controller']['RaidInformation']['RaidLevel']:
                    rVal[self._raw['storage_controller']['Model']]['{0}_raid_level'.format(i.lower())]=int(self._raw['storage_controller']['RaidInformation']['RaidLevel'][i])
                rVal[self._raw['storage_controller']['Model']]['span_count'] = int(self._raw['storage_controller']['RaidInformation']['SpanCount'])
                rVal[self._raw['storage_controller']['Model']]['span_depth'] = int(self._raw['storage_controller']['RaidInformation']['SpanDepth'])

        return rVal
    

    def save_to_db(self):
        now = timezone.now()
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
            idrac_ip=self.idrac_ip,
            psu_count=self.psu_count,
            chassis_height=self.chassis_height,
            date_acquired=self.date_acquired,
            last_updated=now
        )
        PHYSICAL_SERVER.save()

        for cpu, details in self.physical_cpu.items():
            CPU_ASSET = asset(
                asset_id=generate_asset_id(cpu, self.serial, 'PROCESSOR'),
                asset_type='PROCESSOR',
                entity='PHYSICAL',
                last_updated=now
            )
            CPU_ASSET.save()
            CPU = physical_cpu(
                serial='N/A',
                asset=CPU_ASSET,
                parent_server=PHYSICAL_SERVER,
                cpu_slot=cpu,
                core_count=details['core_count'],
                thread_count=details['thread_count'],
                max_frequency=details['max_frequency'],
                cpu_model=details['model'],
                last_updated=now
            )
            CPU.save()

        for module, details in self.physical_memory.items():
            MEMORY_ASSET = asset(
                asset_id=generate_asset_id(module, self.serial, 'RAM'),
                asset_type='RAM',
                entity='PHYSICAL',
                last_updated=now
            )
            MEMORY_ASSET.save()
            MEMORY = physical_memory(
                serial=details['serial'],
                asset=MEMORY_ASSET,
                parent_server=PHYSICAL_SERVER,
                dimm_slot=module,
                dimm_size=details['size'],
                dimm_type=details['type'],
                dimm_speed=details['speed'],
                dimm_model=details['model'],
                manufacturer=details['manufacturer'],
                last_updated=now
            )
            MEMORY.save()

        for disk, details in self.physical_disk.items():
            DISK_ASSET = asset(
                asset_id=generate_asset_id(
                    disk+details['model'], self.serial, 'DISK'),
                asset_type='DISK',
                entity='PHYSICAL',
                last_updated=now
            )
            DISK_ASSET.save()
            DISK = physical_disk(
                serial=disk,
                asset=DISK_ASSET,
                parent_server=PHYSICAL_SERVER,
                capacity=details['size'],
                disk_model=details['model'],
                disk_type=details['type'],
                disk_protocol=details['protocol'],
                last_updated=now

            )
            DISK.save()


        for model, details in self.physical_storage_controller.items():
            STORAGE_CONTROLLER_ASSET = asset(
                asset_id=generate_asset_id(
                    model, self.serial, 'STORAGE_CONTROLLER'),
                asset_type='STORAGE_CONTROLLER',
                entity='PHYSICAL',
                last_updated=now
            )
            STORAGE_CONTROLLER_ASSET.save()
            STORAGE_CONTROLLER = physical_storage_controller(
                asset=STORAGE_CONTROLLER_ASSET,
                parent_server=PHYSICAL_SERVER,
                model = model,
                capacity = details['capacity'],
                primary_level = details['primary_raid_level'],
                secondary_level = details['secondary_raid_level'],
                drive_count = details['drive_count'],
                span_depth = details['span_depth'],
                span_count = details['span_count'],
                last_updated=now

            )
            STORAGE_CONTROLLER.save()
