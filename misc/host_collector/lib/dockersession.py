#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@author: Nico
'''
import collections

import datetime
from docker import Client


dict = collections.OrderedDict


class dockerSession(object):

    def __init__(self,url,user=None,password=None):
        self.__conn = Client(base_url=url);
        self.__CREDENTIALS = {"username":user, "password":password};


    def removeContainer(self,containerName):
        try:
            self.__conn.stop(containerName); #hope that cadvisor doesnt fuck up and get the container stuck
            self.__conn.remove_container(containerName,force=True);
        except Exception as exception:
            return False;
        return True;


    def getContainerPort(self,containerName):
        '''
        Get the ports, mapped outside, of a container
        :param containerName: container name
        :return: list of forwarded ports
        '''
        client = self.__conn;
        rVal = [];
        for i in client.containers():
            if containerName in i['Names'] or ("/" + containerName in i['Names']):
                for j in i['Ports']:
                    if 'PublicPort' in j:
                        rVal.append(j['PublicPort']);
        return rVal;


    def getDockerContainerNames(self):
        '''
        Gets all attributes of all container names
        :return: list of attributes return by the docker-api
        '''
        client = self.__conn;
        rVal = [];
        for i in client.containers():
            for j in i:
                rVal.append(j);
        return rVal;

    def isContainerRunning(self,containerName):
        '''
        Checks if a container is running
        :param containerName: container name
        :return: True if active, False otherwise
        '''
        client = self.__conn;
        for i in client.containers():
            if containerName in i['Names'] or ("/" + containerName in i['Names']):
                if i['State'] == 'running':
                    return True;
                break;
        return False;

    def dockerExec(self,containerName,command):
        '''
        Execute a command on a container
        :param containerName: container name
        :param command: command
        :return: Output of command
        '''
        client = self.__conn;

        #110 broken. very weird fix
        try:
            execCrResult = client.exec_create(containerName,command);
        except:
            execCrResult = client.exec_create(containerName,command);
        try:
            return client.exec_start(execCrResult['Id']);
        except:
            return client.exec_start(execCrResult['Id']);


    def downloadLatestImage(self,reponimage):
        print("Getting latest image of %s.." % reponimage);
        try:
            self.__conn.pull(reponimage, LATEST_TAG, auth_config=self.__CREDENTIALS);
        except Exception as exception:
            print("Failure on retrieving image..\n%s" % str(exception));
            return False;
        return True;


    def pullImage(self,reponimage,tag):
        '''
        Pull the specified image+tag
        :param reponimage: repo and image
        :param tag: tag
        :return: True on successful pull
        '''
        print("Getting image of %s:%s.." % (reponimage,tag));
        try:
            self.__conn.pull(reponimage, tag, auth_config=self.__CREDENTIALS);
        except Exception as exception:
            print("Failure on retrieving image..\n%s" % str(exception));
            return False;
        return True;

    def backupCurrentContainerImage(self,containerName,reponimage):
        '''
        Backup the current specified container to the specified repository/image
        :param containerName: container name
        :param reponimage: repository+image to commit to(ex. omdockerhub.neweb.me:5000/tomcat-blb-mobile-redis)
        :return: True on successful creation
        '''
        print("Creating backup image for %s to %s.." % (containerName,reponimage));
        try:
            backuptag = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S");
            self.__conn.commit(
                containerName,
                reponimage,
                backuptag,
                changes='Cmd ["/opt/tomcat/bin/startup.sh"]'
            );
            self.__conn.push(reponimage,backuptag,auth_config=self.__CREDENTIALS);
        except Exception as exception:
            print("Failed creating backup image..\n%s" % str(exception));
            return False;
        return True;



    def pushContainerToLatest(self,containerName,reponimage=None):
        '''
        Push image to the repository. Equivalent of sync-to-real
        :param containerName: container name
        :param reponimage: repository+image (ex. omdockerhub.neweb.me:5000/tomcat-blb-mobile-redis)
        :return: True on successful creation
        '''
        if not reponimage:
            reponimage = self.getImageFromContainer(containerName)[0];
        try:
            print("Creating backup image.. %s" % reponimage);
            backuptag = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S");
            #imageid = self.getImageFromContainer(containerName)[0]
            #self.__conn.tag(imageid,reponimage,backuptag);
            self.__conn.commit(
                containerName,
                reponimage,
                backuptag,
                #changes='Cmd ["/opt/tomcat/bin/startup.sh"]'
            );
            self.__conn.push(reponimage,backuptag,auth_config=self.__CREDENTIALS);

            print("Pushing current image as latest..");
            self.__conn.commit(
                containerName,
                reponimage,
                LATEST_TAG,
                #changes='Cmd ["/opt/tomcat/bin/startup.sh"]'
            );
            self.__conn.push(reponimage,LATEST_TAG,auth_config=self.__CREDENTIALS);
        except Exception as exception:
            print("Failure..\n%s" % str(exception));
        return True;


    def removeImage(self,image,tag):
        '''
        Equivalent of docker rmi
        :param image: image name
        :param tag: tag
        :return: True on successful execution, Exception otherwise
        '''
        print("Removing image: %s:%s" % (image,tag));
        self.__conn.remove_image(image + ":" + tag);
        return True;

    def getImageNameList(self,imagename):
        '''
        Returns a list of all names of images+tags of a given image name
        :param imagename: image name
        :return: list
        '''
        images = self.__conn.images();
        #import json
        #print json.dumps(images,indent=4)
        #rVal = [];
        rVal = dict()#dict();
        for i in images:
            if i['RepoTags']:
                #print i
                for j in i['RepoTags']:
                    if imagename in j.lower():
                        rVal[j] = i['Id'].split(':')[1][:12];
                        #rVal.append(j);

                        #break;
        return rVal;


    def getImageFromContainer(self,containerName):
        '''
        UNRELIABLE. Returns the current image being used by a container
        :param containerName: container name
        :return: tuple of (imagename,imageid)
        '''
        containers = self.__conn.containers();
        for i in containers:
            if '/' + containerName in i['Names']:
                #print i
                return i['Image'],i['ImageID'].split(':')[1][:12];
        return None;

    def getImageFromContainerz(self,containerName):
        '''
        Returns the current image being used by a container
        :param containerName: container name
        :return: tuple of (imagename,imageid)
        '''
        containers = self.__conn.containers();
        for i in containers:
            if '/' + containerName in i['Names']:
                #print i
                Id = i['ImageID'];
                images = self.__conn.images({"since" : Id})
                for j in images:
                    if j['Id'] == Id:
                        return j['RepoTags'][0],Id.split(':')[1][:12];
                #return i['Image'],i['ImageID'].split(':')[1][:12];
        return None;
    def getLatestImageTag(self,imagename):
        '''
        Returns the tag before the latest one
        :param imagename:
        :return: string of the tag
        '''
        imageNamesList = self.getImageNameList(imagename);
        try:
            return datetime.datetime.strptime(imageNamesList[1].split(":")[-1],"%Y-%m-%d-%H-%M-%S").strftime("%Y-%m-%d %H:%M");
        except Exception as exception:
            print("failed to get image tag for %s\n%s" % (imagename,str(exception)));
            return None;

    def getAllActiveImageNames(self):
        '''
        Returns the list of container names and their associated image ID's
        :return: dictinary {container_name: image_id }
        '''
        containers = self.__conn.containers();
        return {i['Names'][0][1:]:i['ImageID'] for i in containers};

    def getAllContainerSpecifications(self):
        containerlist = self.getAllActiveImageNames();
        rVal = dict();
        for i in containerlist:
            rVal[i] = self.getContainerSpecifications(i);
        return rVal;

    def getContainerSpecifications(self,container_name):
        rVal = dict();
        profile = self.__conn.inspect_container(container_name);
        config = profile['Config'];
        hostconfig = profile['HostConfig'];
        network = profile['NetworkSettings'];
        state = profile['State'];
        rVal['cpu_count'] = hostconfig['CpuCount'];
        rVal['cpu_quota'] = hostconfig['CpuQuota'];
        rVal['memory'] = hostconfig['Memory'];
        rVal['memory_swap'] = hostconfig['MemorySwap'];
        rVal['image'] = config['Image'];
        rVal['image_id'] = profile['Image'];
        rVal['id'] = profile['Id'];
        rVal['ports'] = hostconfig['PortBindings'].keys();
        rVal['networks'] = {k:{'ip' : v['IPAddress'], 'mac' : v['MacAddress'], 'gateway' : v['Gateway']} for k,v in network['Networks'].iteritems()};
        rVal['status'] = state['Status'];
        rVal['creation_date'] = profile['Created'];
        rVal['name'] = profile['Name'];
        return rVal;


