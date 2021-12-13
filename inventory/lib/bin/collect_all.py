import json
import os
from inventory.lib.asset_processor import asset_details
from inventory.lib.host_processor import physical_host_details,cloud_host_details
from pprint import pprint


MAIN_DIR = '/home/aaron/PycharmProjects/argus/testinventory'
ASSET_DIR = '/assets/'
HOST_DIR = '/hosts/'
CLOUD_HOST_DIR = '/cloud_hosts/'

asset_files = os.listdir(MAIN_DIR+ASSET_DIR)
host_files = os.listdir(MAIN_DIR+HOST_DIR)
cloud_host_files = os.listdir(MAIN_DIR+CLOUD_HOST_DIR)


assets_obj_dict = {}
hosts_obj_dict = {}
cloud_hosts_obj_dict = {}


def parse():
    for asset in asset_files:
        f = open(MAIN_DIR+ASSET_DIR+asset)
        asset_dict = json.loads(f.read())
        f.close()

        asset_obj = asset_details(asset_dict)
        assets_obj_dict[asset_obj.serial] = asset_obj

    for host in host_files:
        f = open(MAIN_DIR + HOST_DIR + host)
        host_dict = json.loads(f.read())
        f.close()

        host_obj = physical_host_details(host_dict)
        hosts_obj_dict[host_obj.serial] = host_obj

    for cloud_host in cloud_host_files:
        f = open(MAIN_DIR + CLOUD_HOST_DIR + cloud_host)
        cloud_host_dict = json.loads(f.read())
        f.close()

        cloud_host_obj = cloud_host_details(cloud_host,cloud_host_dict)
        cloud_hosts_obj_dict[cloud_host_obj.ip] = cloud_host_obj


    return assets_obj_dict, hosts_obj_dict,cloud_hosts_obj_dict


def save():
    for k, asset_obj in assets_obj_dict:
        asset_obj.save_to_db()

    for k, host_obj in hosts_obj_dict:
        host_obj.save_to_db()
