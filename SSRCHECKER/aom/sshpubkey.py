#!/usr/bin/python3
#created by: Yroll Jay-R Macalino
from subprocess import *
from enterpassword import *
from py_config import colordesign
import os, sys, json, shutil, requests

class Collect():
	def __init__(self):
		#variables
		with open('info.json') as f_object:
			location = json.load(f_object)
		self.ansibleportask = colordesign("ccyan") + "Enter Ansible Port. \n"	+ colordesign("cnormal")
		self.ansibleportask += colordesign("cyellow") + "\t1.)" + colordesign("cnormal") + " 2556\n"
		self.ansibleportask += colordesign("cyellow") + "\t2.)" + colordesign("cnormal") + " 28038"
		self.ansibleuserask = colordesign("ccyan") + "Enter Ansible User. \n"	+ colordesign("cnormal")
		self.ansibleuserask += colordesign("cyellow") + "\t1.)" + colordesign("cnormal") + " snadmin\n"
		self.ansibleuserask += colordesign("cyellow") + "\t2.)" + colordesign("cnormal") + " ommgr"
		self.ssrportS0 = colordesign("cwhite") + "Port: "	+ colordesign("cnormal") 
		self.ssruserS = colordesign("cwhite") + "User: "	+ colordesign("cnormal") 
		self.sshaskS = colordesign("ccyan") + "Have you added IP? [y/n]? "	+ colordesign("cnormal")
		self.d1_location = location["directory1_location"]
		self.ssrhostfileyml = self.d1_location + "sshpubkey.yml"
		self.ssrhostfile = self.d1_location + "ssrhost"
		self.ssrhostfile1 = self.ssrhostfile + ".bak"
		self.ssrhostsList = []
		self.configfile = "ls " + self.d1_location
		with os.popen(self.configfile) as configfilelocation:
			self.configfileL = configfilelocation.read()
	def sshpubkey(self):
		#office settings password
#		storepass = enterpassword()
		#question for port
		print(self.ansibleportask)
		self.ssrportask = input(self.ssrportS0)
		if self.ssrportask == '1':
			self.ssrportask = "2556"
		elif self.ssrportask == '2':
			self.ssrportask = "28032"
		#question for username
		print(self.ansibleuserask)
		self.ssruserask = input(self.ssruserS)
		if self.ssruserask == '1':
			self.ssruserask = "snadmin"
		elif self.ssruserask == '2':
			self.ssruserask = "ommgr"
		#setting up ssrhost
		self.sshask = input(self.sshaskS)
		self.ansibleuser = "ansible_ssh_user=" + self.ssruserask
		self.ansibleport = "ansible_ssh_port=" + self.ssrportask 
		self.ansiblevars = "[ssr" + self.ssrportask + ":vars]"
		self.ssrportS = "[ssr" + self.ssrportask + "]"
		self.ssrportS1 = "ssr" + self.ssrportask
		self.ssrlists = ["[multi:children]", self.ssrportS1, self.ansiblevars, self.ansibleuser, self.ansibleport, "AUTH_BASIC_ENABLED=False", "host_key_checking=False"]
		ssrDic = { 'python_host': self.ssrportS1, 'python_username': self.ssruserask }
#		ssrDic = {'python_host': self.ssrportS1}
		def replacefile(changed1, changed2):
			#setting host and password on yml file
			with open(self.ssrhostfileyml, 'r') as replaceyml:
				ymlfile = replaceyml.read()
			replacenow = ymlfile.replace(changed1, changed2) 
			with open(self.ssrhostfileyml, 'w') as replaceyml1:
				replaced = replaceyml1.write(replacenow)
			return replaced
		def terminalmode(ssrhostfile):
			#checking the password
#			while True:
#				officeset_url = "http://" + "omadmin:" + str(storepass) + "@" + "office.pc-setting.info/cyrus/"
#				y_request = requests.get(officeset_url)
#				if y_request.status_code == 200:
#					break
#				elif y_request.status_code != 200:
#					print("\033[1;31mIncorrect password!\033[1;0m")
#					storepass = enterpassword()
#					ssrDic['secret_pass'] = storepass
			for key, value in ssrDic.items():
				replacefile(key, value)
			#executing ansible playbook
			call(["export", "ANSIBLE_HOST_KEY_CHECKING=False"], stdout=PIPE, shell=True)
			call(["ansible-playbook", "-i", ssrhostfile, self.ssrhostfileyml, "--ssh-common-args='-o StrictHostKeyChecking=no'", "-K", "--become-method=su"])
			for key, value in ssrDic.items():
				replacefile(value, key)
		if self.sshask.lower() == 'n' or len(self.sshask) == 0:
			#copying files and create an empty file
			if "ssrhost" not in self.configfileL:
				open(self.ssrhostfile, 'w').close()
			elif "ssrhost.bak" not in self.configfileL:
				open(self.ssrhostfile1, 'w').close()
			shutil.copyfile(self.ssrhostfile, self.ssrhostfile1)
			open(self.ssrhostfile, 'w').close()
			#adding your list of IP's
			your_input = colordesign('cwhite') + "---" + colordesign('cyellow') + " Start Adding. To quit type " + colordesign('cred') + ":q " + colordesign('cwhite') + "---" + colordesign('cgreen')
			print(your_input)
			self.ssrhostsList.insert(1, self.ssrportS)
			while True:
				question = input()
				if question == ':q':
					call("clear")
					print(colordesign('cnormal'))
					break
				elif len(question) > 3:
					self.ssrhostsList.insert(2,question.strip())
					self.ssrhostsList.insert(3,"")
			for ssrlist1 in self.ssrlists:
				self.ssrhostsList.insert(-1, ssrlist1)
			for ssrhostList in self.ssrhostsList:
				with open(self.ssrhostfile, 'a') as ssrlist:
					ssrlist.write(ssrhostList)
					ssrlist.write('\n')
			#calling ansible playbook
			terminalmode(self.ssrhostfile)
		elif self.sshask.lower() == 'y':
			call("clear")
			shutil.copyfile(self.ssrhostfile, self.ssrhostfile1)
			terminalmode(self.ssrhostfile1)
