#!/usr/bin/python

import subprocess, shlex, os
from distutils.dir_util import copy_tree
import re

GITUSER = "om:sPCJ-015"
TEMPLATENAME = 'hosttemplate'

"""
Make sure there is no directory for the hostgroup, and there 
is an UNINITIALIZED GIT repository for the hostgroup or the
script will fail.

Nginx: /ansible/nginx/hostgroups/
Puppet: /puppet/

No need to redelete the container, since this is docker-compose.

Inheritance Tree
                        baseHostgroup
                        //         \\
                       //           \\
              nginxHostgroup     puppetHostgroupo

"""


class baseHostGroup(object):
    HOSTGROUP_RE = '^(\S+)-([a-zA-Z_]+[a-zA-Z_0-9]+[a-zA-Z_]+)$'

    def __init__(self, hostgroup):
        self.hostgroup = hostgroup
        self.gitURI = "http://{0}@git.neweb.me/".format(GITUSER)
        self._hostgroupPath = ''
        self._hostgroupDirs = ''

        if not self.correctFormat:
            raise Exception("Wrong Hostgroup Format")

    @property
    def exists(self):
        return os.path.isdir(self._hostgroupPath)

    @property
    def correctFormat(self):
        if re.match(self.HOSTGROUP_RE, self.hostgroup):
            return True
        return False

    def _osCall(self, cmd, cwd=None):
        process = subprocess.Popen(shlex.split(cmd),
                                   shell=False,
                                   bufsize=1,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   cwd=cwd)
        out, err = process.communicate()
        print out
        return out

    def initGit(self):
        rVal = ''
        if self._hostgroupPath:
            steps = [
                'git init',
                'git remote add origin {0}'.format(self.gitURI),
                'git add .',
                'git commit -m "Initial commit"',
                'git push -u origin master',
            ]
            for command in steps:
                rVal += self._osCall(command, cwd=self._hostgroupPath)

            return rVal

    def _createDirectories(self):
        if not self.exists and self._hostgroupPath and self._hostgroupDirs:
            copy_tree(self._hostgroupDirs + TEMPLATENAME, self._hostgroupPath)
            return True

    def generate(self):
        raise NotImplementedError


class nginxHostgroup(baseHostGroup):

    def __init__(self, hostgroup):
        super(nginxHostgroup, self).__init__(hostgroup)
        self.gitURI += "nginx_cloud/{0}.git".format(self.hostgroup)
        self.__composeConfPath = '/opt/compose-conf/nginx/new/'
        self._hostgroupDirs = '/ansible/nginx/hostgroups/'
        self._hostgroupPath = self._hostgroupDirs + self.hostgroup
        self.__composeConfTemplate = '''############
version: '2'
services:
 {0}:
  image: omdockerhub.neweb.me:5000/jinsheng_tianhe_standard
  container_name: {0}
  volumes:
    - /etc/localtime:/etc/localtime:ro
    - /ansible/nginx/hostgroups/{0}/nginx/conf.d/:/usr/local/nginx/conf.d/
    - /ansible/nginx/hostgroups/{0}/nginx/conf/:/usr/local/nginx/conf/
    - /ansible/nginx/hostgroups/{0}/nginx/data/:/usr/local/nginx/data/
    - /app/certstore/:/app/certstore/
  hostname: {0}
  read_only: false
  restart: always
  command: /bin/bash
  stdin_open: true
  tty: true
        '''

        if self.exists:
            raise Exception("Hostgroup Exists, Delete directory, yml, container first")

    def __createComposeFile(self):
        if not self.exists:
            with open(self.__composeConfPath + "{0}.yml".format(self.hostgroup), 'w') as f:
                f.write(self.__composeConfTemplate.format(self.hostgroup))
            return True

    def __composeContainer(self):
        cmd = "docker-compose -f {0}.yml up -d".format(self.hostgroup)
        self._osCall(cmd, cwd=self.__composeConfPath)
        return True

    def generate(self):
        rVal = ''
        if not self.exists:
            print "Deploy Start"
            rVal += "Deploy Start\n"
            if self.__createComposeFile():
                print "Compose File Created {0}".format(self.__composeConfPath + "{0}.yml".format(self.hostgroup))
                rVal += "Compose File Created {0}\n".format(self.__composeConfPath + "{0}.yml".format(self.hostgroup))
                if self._createDirectories():
                    print "Files Created {0}".format(self._hostgroupPath)
                    rVal += "Files Created {0}\n".format(self._hostgroupPath)
                    if self.__composeContainer():
                        print "Container Ready {0}".format(self.hostgroup)
                        rVal += "Container Ready {0}\n".format(self.hostgroup)
                        rVal += self.initGit()
                        print "Git REPO Ready {0}".format(self.gitURI)
                        rVal += "Git REPO Ready {0}\n".format(self.gitURI)
                        return (True, rVal)

        print "Error Creating, Delete directory, yml, container first then retry"
        rVal += "Error Creating, Delete directory, yml, container first then retry\n"
        return (False, rVal)


class puppetHostgroup(baseHostGroup):

    def __init__(self, hostgroup):
        super(puppetHostgroup, self).__init__(hostgroup)
        self.gitURI += "puppet_cloud/{0}.git".format(self.hostgroup)
        self._hostgroupDirs = '/puppet/'
        self._hostgroupPath = self._hostgroupDirs + self.hostgroup

        if self.exists:
            raise Exception("Hostgroup Exists, Delete directory first")

    def generate(self):
        rVal = ''
        if not self.exists:
            print "Deploy Start"
            rVal += "Deploy Start\n"
            if self._createDirectories():
                print "Files Created {0}".format(self._hostgroupPath)
                rVal += "Files Created {0}\n".format(self._hostgroupPath)
                self._hostgroupPath += '/templates'
                rVal += self.initGit()
                print "Git REPO Ready"
                rVal += "Git REPO Ready"
                return (True, rVal)

        rVal += "Error Creating, Delete directory, first then retry"
        return (False, rVal)


if __name__ == '__main__':
    import sys

    if sys.argv[1] == 'nginx':
        x = nginxHostgroup(sys.argv[2])
        x.generate()
    elif sys.argv[1] == 'puppet':
        x = puppetHostgroup(sys.argv[2])
        x.generate()
    else:
        print """Incorrect arguments 
        arg1 should be 'nginx' or 'puppet'
        arg2 should be hostgroup name
        """


