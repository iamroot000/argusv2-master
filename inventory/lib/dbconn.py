from argus.defs.datasources import SERVER_INVENTORY_DB
import datetime
import mysql.connector
SELECT_FROM_PHYSICAL_HOSTS = '''SELECT host_ip,hostname,product_name,product_date_bought,product_serial,memory,mac,host_type,location
FROM physical_host
ORDER BY host_ip DESC
'''

SELECT_ALL_FROM_PHYSICAL_HOSTS_BY_IP = '''SELECT host_ip, product_name, product_serial, product_date_bought, cpu_count, vcpu_count, core_count, cpu_name, threads_per_core, memory, swap, module_count, memory_per_module, hostname, mac, interface, host_type, location, last_updated
FROM physical_host
where host_ip=%s
'''

SELECT_FROM_DOCKER_CONTAINER = '''SELECT host_ip,container_name,port_bindings,last_updated
FROM docker_container
ORDER BY container_name DESC
'''

SELECT_FROM_DOCKER_CONTAINER_BY_HOST_IP = '''SELECT host_ip, uuid, ctid, container_name, image_id, memory, ip_address, mac_address, port_bindings, cpu_count, last_updated
FROM docker_container
where host_ip=%s
'''

SELECT_FROM_DOCKER_CONTAINER_BY_CONTAINER_NAME = '''SELECT host_ip, uuid, ctid, container_name, image_id, memory, ip_address, mac_address, port_bindings, cpu_count, last_updated
FROM docker_container
where container_name=%s
'''

SELECT_FROM_OPENVZ_CONTAINER = '''SELECT host_ip,ip_address,ctid,disk,memory,hostname,last_updated
FROM openvz_container
ORDER BY ip_address DESC
'''

SELECT_FROM_OPENVZ_CONTAINER_BY_HOST_IP = '''SELECT host_ip,ip_address,ctid,disk,memory,hostname,last_updated
FROM openvz_container
where host_ip=%s
'''

SELECT_FROM_OPENVZ_CONTAINER_BY_CTID = '''SELECT host_ip,ip_address,ctid,disk,memory,hostname,last_updated
FROM openvz_container
where ctid=%s
'''

SELECT_FROM_XEN_VM = '''SELECT host_ip,ip_address,uuid,disk,memory,cpu_count,hostname,last_updated
FROM xen_vm
ORDER BY ip_address DESC
'''

SELECT_FROM_XEN_VM_BY_HOST_IP = '''SELECT host_ip,ip_address,uuid,disk,memory,cpu_count,hostname,last_updated
FROM xen_vm
where host_ip=%s
'''
SELECT_FROM_XEN_VM_BY_UUID = '''SELECT host_ip,ip_address,uuid,disk,memory,cpu_count,hostname,last_updated
FROM xen_vm
where uuid=%s
'''

SELECT_FROM_DISK_BY_HOST_IP = '''SELECT id_disk_name,id_host_ip,disk_size
FROM disk
where id_host_ip=%s
'''


SELECT_FROM_PHYSICAL_DISK_BY_HOST_IP = '''SELECT disk_model,host_ip,disk_size,disk_type,serial,last_updated
FROM physical_disk
where host_ip=%s
'''


class conn(object):
    def __init__(self):
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def select_from_physical_host(self, host_ip=None):
        conn = mysql.connector.connect(**SERVER_INVENTORY_DB)
        c = conn.cursor()

        if host_ip is not None:
            q = SELECT_ALL_FROM_PHYSICAL_HOSTS_BY_IP
            c.execute(q, (host_ip,))

            res = c.fetchone()
            conn.commit()
            conn.close()
            rVal = {
                'host_ip': res[0],
                'product_name': res[1],
                'product_serial': res[2],
                'product_date_bought': res[3].strftime("%Y-%m-%d"),
                'cpu_count': res[4],
                'vcpu_count': res[5],
                'core_count': res[6],
                'cpu_name': res[7],
                'threads_per_core': res[8],
                'memory': res[9],
                'swap': res[10],
                'module_count': res[11],
                'memory_per_module': res[12],
                'hostname': res[13],
                'mac': res[14],
                'interface': res[15],
                'host_type': res[16],
                'location': res[17],
                'last_updated': res[18].strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            q = SELECT_FROM_PHYSICAL_HOSTS
            c.execute(q)
            res = c.fetchall()
            conn.commit()
            conn.close()
            rVal = []
            for i in res:
                row = {
                    'host_ip': i[0],
                    'hostname': i[1],
                    'product_name': i[2],
                    'product_date_bought': i[3].strftime("%Y-%m-%d"),
                    'product_serial': i[4],
                    'memory': i[5],
                    'mac': i[6],
                    'host_type': i[7],
                    'idc': i[8]

                }
                rVal.append(row)
        return rVal

    def select_from_docker_container(self, host_ip=None, container_name=None):
        conn = mysql.connector.connect(**SERVER_INVENTORY_DB)
        c = conn.cursor()
        rVal = []

        if host_ip is not None or container_name is not None:
            if host_ip:
                q = SELECT_FROM_DOCKER_CONTAINER_BY_HOST_IP
                filter = host_ip
            if container_name:
                q = SELECT_FROM_DOCKER_CONTAINER_BY_CONTAINER_NAME
                filter = container_name

            c.execute(q, (filter,))
            res = c.fetchall()

            conn.commit()
            conn.close()
            for i in res:
                row = {
                    'host_ip': i[0],
                    'uuid': i[1],
                    'ctid': i[2],
                    'container_name': i[3],
                    'image_id': i[4],
                    'memory': i[5],
                    'ip_address': i[6],
                    'mac_address': i[7],
                    'port_bindings': i[8],
                    'cpu_count': i[9],
                    'last_updated': i[10].strftime("%Y-%m-%d %H:%M:%S")
                }
                rVal.append(row)

        else:
            q = SELECT_FROM_DOCKER_CONTAINER
            c.execute(q)
            res = c.fetchall()
            conn.commit()
            conn.close()
            for i in res:
                row = {
                    'host_ip': i[0],
                    'container_name': i[1],
                    'port_bindings': i[2],
                    'last_updated': i[3].strftime("%Y-%m-%d %H:%M:%S"),
                }
                rVal.append(row)
        return rVal

    def select_from_openvz_container(self, host_ip=None, ctid=None):
        conn = mysql.connector.connect(**SERVER_INVENTORY_DB)
        c = conn.cursor()
        rVal = []

        if host_ip is not None or ctid is not None:
            if host_ip:
                q = SELECT_FROM_OPENVZ_CONTAINER_BY_HOST_IP
                filter = host_ip
            if ctid:
                q = SELECT_FROM_OPENVZ_CONTAINER_BY_CTID
                filter = ctid

            c.execute(q, (filter,))
            res = c.fetchall()
            conn.commit()
            conn.close()
            for i in res:
                row = {
                    'host_ip': i[0],
                    'ip_address': i[1],
                    'ctid': i[2],
                    'disk': i[3],
                    'memory': i[4],
                    'hostname': i[5],
                    'last_updated': i[6].strftime("%Y-%m-%d %H:%M:%S"),
                }
                rVal.append(row)
        else:
            q = SELECT_FROM_OPENVZ_CONTAINER
            c.execute(q)
            res = c.fetchall()
            conn.commit()
            conn.close()
            for i in res:
                row = {
                    'host_ip': i[0],
                    'ip_address': i[1],
                    'ctid': i[2],
                    'disk': i[3],
                    'memory': i[4],
                    'hostname': i[5],
                    'last_updated': i[6].strftime("%Y-%m-%d %H:%M:%S"),
                }
                rVal.append(row)
        return rVal

    def select_from_xen_vm(self, host_ip=None, uuid=None):
        conn = mysql.connector.connect(**SERVER_INVENTORY_DB)
        c = conn.cursor()
        rVal = []

        if host_ip is not None or uuid is not None:

            if host_ip:
                q = SELECT_FROM_XEN_VM_BY_HOST_IP
                filter = host_ip
            if uuid:
                q = SELECT_FROM_XEN_VM_BY_UUID
                filter = uuid

            c.execute(q, (filter,))
            res = c.fetchall()
            conn.commit()
            conn.close()
            for i in res:
                row = {
                    'host_ip': i[0],
                    'ip_address': i[1],
                    'uuid': i[2],
                    'disk': i[3],
                    'memory': i[4],
                    'cpu_count': i[5],
                    'hostname': i[6],
                    'last_updated': i[7].strftime("%Y-%m-%d %H:%M:%S"),
                }
                rVal.append(row)
        else:
            q = SELECT_FROM_XEN_VM
            c.execute(q)
            res = c.fetchall()
            conn.commit()
            conn.close()
            for i in res:
                row = {
                    'host_ip': i[0],
                    'ip_address': i[1],
                    'uuid': i[2],
                    'disk': i[3],
                    'memory': i[4],
                    'cpu_count': i[5],
                    'hostname': i[6],
                    'last_updated': i[7].strftime("%Y-%m-%d %H:%M:%S"),
                }
                rVal.append(row)
        return rVal

    def select_from_disk(self, host_ip=None):
        conn = mysql.connector.connect(**SERVER_INVENTORY_DB)
        c = conn.cursor()
        rVal = []

        if host_ip is not None:
            q = SELECT_FROM_DISK_BY_HOST_IP
            filter = host_ip

            c.execute(q, (filter,))
            res = c.fetchall()
            conn.commit()
            conn.close()
            for i in res:
                row = {
                    'id_disk_name': i[0],
                    'id_host_ip': i[1],
                    'disk_size': i[2],
                }
                rVal.append(row)

        return rVal

    def select_from_physical_disk(self, host_ip=None):
        conn = mysql.connector.connect(**SERVER_INVENTORY_DB)
        c = conn.cursor()
        rVal = []
        if host_ip is not None:
            q = SELECT_FROM_PHYSICAL_DISK_BY_HOST_IP
            filter = host_ip

            c.execute(q, (filter,))
            res = c.fetchall()
            conn.commit()
            conn.close()
            for i in res:
                row = {
                    'disk_model': i[0],
                    'host_ip': i[1],
                    'disk_size': i[2],
                    'disk_type': i[3],
                    'serial': i[4]
                }
                rVal.append(row)

        return rVal
