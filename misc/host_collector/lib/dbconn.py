INSERT_INTO_physical_host='''INSERT INTO physical_host (host_ip,product_name,product_serial,product_date_bought,cpu_count,vcpu_count,core_count,cpu_name,threads_per_core,memory,swap,module_count,memory_per_module,hostname,mac,interface,host_type,location,last_updated)
VALUES ( "%s","%s","%s","%s",%s,%s,%s,"%s",%s,"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")'''

ON_DUPLICATE_physical_host='''ON DUPLICATE KEY UPDATE
`host_ip`=VALUES(`host_ip`),
`product_name`=VALUES(`product_name`),
`product_serial`=VALUES(`product_serial`),
`product_date_bought`=VALUES(`product_date_bought`),
`cpu_count`=VALUES(`cpu_count`),
`vcpu_count`=VALUES(`vcpu_count`),
`core_count`=VALUES(`core_count`),
`cpu_name`=VALUES(`cpu_name`),
`threads_per_core`=VALUES(`threads_per_core`),
`memory`=VALUES(`memory`),
`swap`=VALUES(`swap`),
`module_count`=VALUES(`module_count`),
`memory_per_module`=VALUES(`memory_per_module`),
`hostname`=VALUES(`hostname`),
`mac`=VALUES(`mac`),
`interface`=VALUES(`interface`),
`host_type`=VALUES(`host_type`),
`location`=VALUES(`location`),
`last_updated`=VALUES(`last_updated`)
'''

INSERT_INTO_xen_vm='''INSERT INTO xen_vm (uuid,disk,memory,cpu_count,ip_address,host_ip,hostname,last_updated)
VALUES ( "%s","%s","%s",%s,"%s","%s","%s","%s")'''

ON_DUPLICATE_xen_vm='''ON DUPLICATE KEY UPDATE
`uuid`=VALUES(`uuid`),
`disk`=VALUES(`disk`),
`memory`=VALUES(`memory`),
`cpu_count`=VALUES(`cpu_count`),
`ip_address`=VALUES(`ip_address`),
`host_ip`=VALUES(`host_ip`),
`hostname`=VALUES(`hostname`),
`last_updated`=VALUES(`last_updated`)
'''


INSERT_INTO_openvz_container='''INSERT INTO openvz_container (ctid,disk,memory,ip_address,host_ip,hostname,last_updated)
VALUES ( "%s","%s","%s","%s","%s","%s","%s")'''

ON_DUPLICATE_openvz_container='''ON DUPLICATE KEY UPDATE
`ctid`=VALUES(`ctid`),
`disk`=VALUES(`disk`),
`memory`=VALUES(`memory`),
`ip_address`=VALUES(`ip_address`),
`host_ip`=VALUES(`host_ip`),
`hostname`=VALUES(`hostname`),
`last_updated`=VALUES(`last_updated`)
'''

INSERT_INTO_docker_container='''INSERT INTO docker_container (uuid,ctid,container_name,image_id,memory,ip_address,mac_address,port_bindings,cpu_count,host_ip,last_updated)
VALUES ( "%s","%s","%s","%s","%s","%s","%s","%s",%s,"%s","%s")'''

ON_DUPLICATE_docker_container='''ON DUPLICATE KEY UPDATE
`uuid`=VALUES(`uuid`),
`ctid`=VALUES(`ctid`),
`container_name`=VALUES(`container_name`),
`image_id`=VALUES(`image_id`),
`memory`=VALUES(`memory`),
`ip_address`=VALUES(`ip_address`),
`mac_address`=VALUES(`mac_address`),
`port_bindings`=VALUES(`port_bindings`),
`cpu_count`=VALUES(`cpu_count`),
`host_ip`=VALUES(`host_ip`),
`last_updated`=VALUES(`last_updated`)
'''

DELETE_docker_container='''DELETE FROM docker_container
WHERE host_ip="%s"
'''

DELETE_xen_vm='''DELETE FROM xen_vm
WHERE host_ip="%s"
'''

DELETE_openvz_container='''DELETE FROM openvz_container
WHERE host_ip="%s"
'''

INSERT_INTO_disk='''INSERT INTO disk (id_disk_name,id_host_ip,disk_size,last_updated)
VALUES ( "%s","%s","%s","%s" )'''

INSERT_INTO_physical_disk='''INSERT INTO physical_disk (disk_model,host_ip,disk_size,disk_type,serial,last_updated)
VALUES ( "%s","%s","%s","%s","%s","%s" )'''


DELETE_disk='''DELETE FROM disk
WHERE id_host_ip="%s"
'''
DELETE_physical_disk='''DELETE FROM physical_disk
WHERE host_ip="%s"
'''
import mysql.connector
import datetime

server_inventory_DB = {
        "host": '10.168.11.216',
        "database": 'server_inventory',
        "user": 'siuser',
        "password": 'Ad@sn1407',
        "charset": "utf8",
    }


class conn(object):
    def __init__(self):
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    def insert_into_physical_disk(self,row):
        conn = mysql.connector.connect(**server_inventory_DB);
        c = conn.cursor();
        q = INSERT_INTO_physical_disk % (
            row['disk_model'],
            row['host_ip'],
            row['disk_size'],
            row['disk_type'],
            row['serial'],
            self.timestamp
        )

        c.execute(q);
        conn.commit()
        conn.close();

        return True;

    def delete_physical_disk(self,host_ip):
        conn = mysql.connector.connect(**server_inventory_DB);
        c = conn.cursor();

        q = DELETE_physical_disk % (host_ip,)
        c.execute(q);
        conn.commit()
        conn.close();

        return True;
    def insert_into_disk(self,row):
        conn = mysql.connector.connect(**server_inventory_DB);
        c = conn.cursor();
        q = INSERT_INTO_disk % (
            row['disk_name'],
            row['host_ip'],
            row['disk_size'],
            self.timestamp
        )

        c.execute(q);
        conn.commit()
        conn.close();

        return True;

    def delete_disk(self,host_ip):
        conn = mysql.connector.connect(**server_inventory_DB);
        c = conn.cursor();

        q = DELETE_disk % (host_ip,)
        c.execute(q);
        conn.commit()
        conn.close();

        return True;

    def insert_into_physical_host(self,row):
        conn = mysql.connector.connect(**server_inventory_DB);
        c = conn.cursor();
        q = INSERT_INTO_physical_host % (
            row['host_ip'],
            row['product_name'],
            row['product_serial'],
            row['product_date_bought'],
            row['cpu_count'],
            row['vcpu_count'],
            row['core_count'],
            row['cpu_name'],
            row['threads_per_core'],
            row['memory'],
            row['swap'],
            row['module_count'],
            row['memory_per_module'],
            row['hostname'],
            row['mac'],
            row['interface'],
            row['host_type'],
            row['location'],
            self.timestamp
        ) + ON_DUPLICATE_physical_host

        c.execute(q);
        conn.commit()
        conn.close();

        return True;

    def insert_into_xen_vm(self,row):
        conn = mysql.connector.connect(**server_inventory_DB);
        c = conn.cursor();

        q = INSERT_INTO_xen_vm % (
            row['uuid'],
            row['disks'],
            row['memory'],
            row['cpu_count'],
            row['ip_address'],
            row['host_ip'],
            row['hostname'],
            self.timestamp
        ) + ON_DUPLICATE_xen_vm

        c.execute(q);
        conn.commit()
        conn.close();

        return True;

    def insert_into_openvz_container(self,row):
        conn = mysql.connector.connect(**server_inventory_DB);
        c = conn.cursor();

        q = INSERT_INTO_openvz_container % (
            row['ctid'],
            row['disks'],
            row['memory'],
            row['ip_address'],
            row['host_ip'],
            row['hostname'],
            self.timestamp
        ) + ON_DUPLICATE_openvz_container

        c.execute(q);
        conn.commit()
        conn.close();

        return True;

    def insert_into_docker_container(self,row):
        conn = mysql.connector.connect(**server_inventory_DB);
        c = conn.cursor();

        q = INSERT_INTO_docker_container % (
            row['uuid'],
            row['ctid'],
            row['container_name'],
            row['image_id'],
            row['memory'],
            row['ip_address'],
            row['mac_address'],
            row['port_bindings'],
            row['cpu_count'],
            row['host_ip'],
            self.timestamp
        ) + ON_DUPLICATE_docker_container
        c.execute(q);
        conn.commit()
        conn.close();

        return True;

    def delete_docker_container(self, host_ip):
        conn = mysql.connector.connect(**server_inventory_DB);
        c = conn.cursor();

        q = DELETE_docker_container % (host_ip,)
        c.execute(q);
        conn.commit()
        conn.close();

        return True;

    def delete_xen_vm(self, host_ip):
        conn = mysql.connector.connect(**server_inventory_DB);
        c = conn.cursor();

        q = DELETE_xen_vm % (host_ip,)
        c.execute(q);
        conn.commit()
        conn.close();

        return True;

    def delete_openvz_container(self, host_ip):
        conn = mysql.connector.connect(**server_inventory_DB);
        c = conn.cursor();

        q = DELETE_openvz_container % (host_ip,)
        c.execute(q);
        conn.commit()
        conn.close();

        return True;


'''
CREATE TABLE `physical_host` ( 
    `host_ip` VARCHAR(15) NOT NULL, 
    `product_name` VARCHAR(50) NOT NULL, 
    `product_serial` VARCHAR(50) NOT NULL, 
    `product_date_bought` DATE, 
    `cpu_count` INT(2) NOT NULL, 
    `vcpu_count` INT(2) NOT NULL, 
    `core_count` INT(2) NOT NULL, 
    `cpu_name` VARCHAR(50) NOT NULL, 
    `threads_per_core` INT(2) NOT NULL, 
    `memory` VARCHAR(20) NOT NULL, 
    `swap` VARCHAR(20) NOT NULL, 
    `module_count` VARCHAR(20) NOT NULL, 
    `memory_per_module` VARCHAR(20) NOT NULL, 
    `hostname` VARCHAR(50) NOT NULL, 
    `mac` VARCHAR(50) NOT NULL, 
    `interface` VARCHAR(20) NOT NULL, 
    `host_type` VARCHAR(20) NOT NULL, 
    `location` VARCHAR(20) NOT NULL, 
    PRIMARY KEY (`host_ip`),	
    `last_updated` DATETIME NOT NULL
) ENGINE=InnoDB;

CREATE TABLE `xen_vm` (
	`uuid` VARCHAR(50) NOT NULL,
	`disk` VARCHAR(20) NOT NULL,
	`memory` VARCHAR(30),
	`cpu_count` INT(2),
	`ip_address` VARCHAR(50),
	`last_updated` DATETIME NOT NULL,
	`host_ip` VARCHAR(50) NOT NULL,
	`hostname` VARCHAR(50) NOT NULL, 
    FOREIGN KEY (`host_ip`) REFERENCES physical_host(`host_ip`),
	PRIMARY KEY (`uuid`)
) ENGINE=InnoDB;


CREATE TABLE `openvz_container` (
	`ctid` VARCHAR(50) NOT NULL,
	`disk` VARCHAR(20) NOT NULL,
	`memory` VARCHAR(30),
	`ip_address` VARCHAR(50),
	`last_updated` DATETIME NOT NULL,
	`host_ip` VARCHAR(50) NOT NULL,
	`hostname` VARCHAR(50) NOT NULL, 
    FOREIGN KEY (`host_ip`) REFERENCES physical_host(`host_ip`),
	PRIMARY KEY (`ctid`)
) ENGINE=InnoDB;

CREATE TABLE `docker_container` (
	`uuid` VARCHAR(50) NOT NULL,
	`ctid` VARCHAR(128) NOT NULL,
	`container_name` VARCHAR(50) NOT NULL,
	`image_id` VARCHAR(128),
	`memory` VARCHAR(30),
	`ip_address` VARCHAR(50),
	`mac_address` VARCHAR(50),
	`port_bindings` VARCHAR(128),
	`cpu_count` INT(2),
	`last_updated` DATETIME NOT NULL,
	`host_ip` VARCHAR(50) NOT NULL,
    FOREIGN KEY (`host_ip`) REFERENCES physical_host(`host_ip`),
	PRIMARY KEY (`uuid`)
) ENGINE=InnoDB;


CREATE TABLE `disk` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_disk_name` VARCHAR(10) NOT NULL,
  `id_host_ip` VARCHAR(50) NOT NULL,
  `disk_size` VARCHAR(20) NOT NULL,
  `last_updated` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_disk_name` (`id_disk_name`,`id_host_ip`)
) ENGINE=InnoDB;

CREATE TABLE `physical_disk` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `disk_model` VARCHAR(128) NOT NULL,
  `host_ip` VARCHAR(50) NOT NULL,
  `disk_size` VARCHAR(128) NOT NULL,
  `disk_type` VARCHAR(20),
  `serial` VARCHAR(20),
  `last_updated` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`host_ip`) REFERENCES physical_host(`host_ip`)
) ENGINE=InnoDB;
'''


###NEW SHIT
'''
CREATE TABLE `asset` (
  `asset_id` VARCHAR(128) NOT NULL,
  `asset_type` VARCHAR(50) NOT NULL,
  `last_updated` DATETIME NOT NULL,
  PRIMARY KEY (`asset_id`)
) ENGINE=InnoDB;


CREATE TABLE `physical_server` ( 
    `serial` VARCHAR(15) NOT NULL,
    `asset_id` VARCHAR(128) NOT NULL,
    `host_ip` VARCHAR(15) NOT NULL, 
    `psu_count` INT(2), 
    `chassis_height` VARCHAR(10), 
    `date_acquired` DATE, 
    `last_updated` DATETIME NOT NULL,
    FOREIGN KEY (`asset_id`) REFERENCES asset(`asset_id`),
    PRIMARY KEY (`serial`)
) ENGINE=InnoDB;


CREATE TABLE `physical_disk` ( 
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `asset_id` VARCHAR(128) NOT NULL,
    `host_ip` VARCHAR(15) NOT NULL, 
    `serial` VARCHAR(15),
    `capacity` VARCHAR(15) NOT NULL, 
    `model` VARCHAR(50), 
    `type` VARCHAR(5) NOT NULL, 
    `protocol` VARCHAR(10), 
    `last_updated` DATETIME NOT NULL,
    FOREIGN KEY (`asset_id`) REFERENCES asset(`asset_id`),
    FOREIGN KEY (`host_ip`) REFERENCES physical_server(`host_ip`),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB;


CREATE TABLE `physical_memory` ( 
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `asset_id` VARCHAR(128) NOT NULL,
    `host_ip` VARCHAR(15) NOT NULL, 
    `serial` VARCHAR(15),
    `dimm_slot` VARCHAR(15) NOT NULL, 
    `size` VARCHAR(15) NOT NULL, 
    `type` VARCHAR(5) NOT NULL, 
    `speed` VARCHAR(5) NOT NULL, 
    `model` VARCHAR(50),
    `manufacturer` VARCHAR(50), 
    `last_updated` DATETIME NOT NULL,
    FOREIGN KEY (`asset_id`) REFERENCES asset(`asset_id`),
    FOREIGN KEY (`host_ip`) REFERENCES physical_server(`host_ip`),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB;

                
CREATE TABLE `physical_cpu` ( 
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `asset_id` VARCHAR(128) NOT NULL,
    `host_ip` VARCHAR(15) NOT NULL, 
    `cpu_slot` VARCHAR(15) NOT NULL, 
    `core_count` int(5) NOT NULL, 
    `thread_count` int(5) NOT NULL, 
    `max_frequency` VARCHAR(15) NOT NULL, 
    `model` VARCHAR(50) NOT NULL, 
    `last_updated` DATETIME NOT NULL,
    FOREIGN KEY (`asset_id`) REFERENCES asset(`asset_id`),
    FOREIGN KEY (`host_ip`) REFERENCES physical_server(`host_ip`),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB;

'''



INSERT_INTO_asset='''
    INSERT INTO asset (asset_id,asset_type,last_updated)
    VALUES ( "%s","%s","%s")
    ON DUPLICATE KEY UPDATE
    `last_updated`=VALUES(`last_updated`)
'''

INSERT_INTO_PHYSICAL_SERVER='''
    INSERT INTO physical_server (serial,asset_id ,host_ip ,psu_count ,chassis_height,date_acquired,last_updated)
    VALUES ("%s","%s","%s",%s,"%s","%s","%s")
    ON DUPLICATE KEY UPDATE
    `serial`=VALUES(`serial`),
    `asset_id`=VALUES(`asset_id`),
    `host_ip`=VALUES(`host_ip`),
    `psu_count`=VALUES(`psu_count`),
    `chassis_height`=VALUES(`chassis_height`),
    `date_acquired`=VALUES(`date_acquired`),
    `last_updated`=VALUES(`last_updated`)
'''

INSERT_INTO_PHYSICAL_DISK='''
    INSERT INTO physical_disk (asset_id,host_ip,serial,capacity,model,type,protocol,last_updated)
    VALUES ("%s","%s","%s",%s,"%s","%s","%s","%s")
    ON DUPLICATE KEY UPDATE
    `asset_id`=VALUES(`asset_id`),
    `host_ip`=VALUES(`host_ip`),
    `serial`=VALUES(`serial`),
    `capacity`=VALUES(`capacity`),
    `model`=VALUES(`model`),
    `type`=VALUES(`type`),
    `protocol`=VALUES(`protocol`),
    `last_updated`=VALUES(`last_updated`)
'''














