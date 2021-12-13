#!/usr/bin/python3
#created by: Yroll Jay-R Macalino
from subprocess import *
from py_config import colordesign
import os, sys, json, shutil

class Collect():
	def __init__(self):
		#variables
		with open('info.json') as self.f_obj:
			location = json.load(self.f_obj)
		self.d1_location = location["directory1_location"]
		self.filename_domainyml = self.d1_location +'domainchecking.yml'
		self.filename_domainlist = self.d1_location +'domainchecking.list'
		self.filename_domainyml1 = self.d1_location +'domainchecking.bak.yml'
		self.question = colordesign("ccyan") + "Have you added Domain? [y/n]? "	+ colordesign("cnormal")
		self.domain_files = [ self.filename_domainlist, self.filename_domainyml ]
		self.ymlconfigs = [ "#created by: Yroll Jay-R Macalino", "---", "- hosts: 127.0.0.1", "  gather_facts: no",  "  tasks:", "  - name: Check that you can connect (GET) to a page and it returns a status 200", "    uri:", "     url: http://{{ item }}", "    with_items:", "\n" ]
		self.ymlconfigs1 = [ "  - name: A record (IPV4 address) lookup", "    debug: msg='{{ lookup('dig', '{{ item }}')}}'", "    with_items:" ]
		self.domainlists0 = []
		self.configfile = "ls " + self.d1_location
		with os.popen(self.configfile) as configfilelocation:
			self.configfileL = configfilelocation.read()
	def domain(self):
		#setting up yml
		self.question1 = input(self.question)
		if self.question1.lower() == 'n' or len(self.question1) == 0:
			if "domainchecking.yml" not in self.configfileL:
				open(self.filename_domainyml, 'w').close()
			elif "domainchecking.bak.yml" not in self.configfileL:
				open(self.filename_domainyml1, 'w').close()
			shutil.copyfile(self.filename_domainyml, self.filename_domainyml1)
			open(self.filename_domainyml, 'w').close()
			for domain_file in self.domain_files:
				open(domain_file, 'w').close()
			your_input = colordesign('cwhite') + "---" + colordesign('cyellow') + " Start Adding. To quit type " + colordesign('cred') + ":q " + colordesign('cwhite') + "---" + colordesign('cgreen') 
			print(your_input)
			while True:
				question = input()
				if question == ':q':
					call("clear")
					print(colordesign('cnormal'))
					break
				else:
					self.domainlists0.append(question)
			for domainlist in self.domainlists0:
				with open(self.filename_domainlist, 'a') as domainalllist:
					domainalllist.write(domainlist)
					domainalllist.write('\n')
			with open(self.filename_domainlist) as f_domain:
				reads_l = f_domain.readlines()
			def appendall(position):
				for read_l in reads_l:
					if len(read_l) > 4:
						domainlist = "      - " + str(read_l.strip())
						self.ymlconfigs.insert(position, domainlist)
				self.ymlconfigs.insert(position, "    ignore_errors: yes")
			appendall(-1)
			for ymlconfig1 in self.ymlconfigs1:
				self.ymlconfigs.insert(-1, ymlconfig1)
			appendall(-1)		
			with open(self.filename_domainyml, 'a') as file_save:
				for self.ymlconfig in self.ymlconfigs:
					file_save.write(self.ymlconfig)
					file_save.write("\n")
			call(["ansible-playbook", self.filename_domainyml])
		if self.question1.lower() == 'y':
			shutil.copy(self.filename_domainyml, self.filename_domainyml1)
			call(["ansible-playbook", self.filename_domainyml1])
