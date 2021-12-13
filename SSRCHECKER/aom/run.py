#!/usr/bin/python3
#created by: Yroll Jay-R Macalino
from subprocess import *
from py_config import colordesign
import os, domainchecking, sshpubkey, initialization_centOS7_forwarding_2018_aom, initialization_centOS7_forwarding_with_puppet_2018, SSR_init

#class variables
class Runstart():
	def __init__(self):
		self.collect1 = initialization_centOS7_forwarding_2018_aom.Collect()
		self.collect2 = initialization_centOS7_forwarding_with_puppet_2018.Collect()
		self.collect3 = SSR_init.Collect()
		self.collect4 = sshpubkey.Collect()
		self.collect5 = domainchecking.Collect()
		self.num1 = colordesign("cred") + "1.)" + colordesign("cnormal") + " CentOS7 Forwarding Intialization\n"
		self.num2 = colordesign("cred") + "2.)" + colordesign("cnormal") + " Check Amount Loss\n"
		self.num3 = colordesign("cred") + "3.)" + colordesign("cnormal") + " SSR Initialization and Configuration\n"
		self.num4 = colordesign("cred") + "4.)" + colordesign("cnormal") + " Adding SSH Pubkey on VPN\n"
		self.num5 = colordesign("cred") + "5.)" + colordesign("cnormal") + " Domain Checking\n"
		self.numbers = [ self.num1, self.num2, self.num3, self.num4, self.num5 ]
		self.packages = ["xterm", "sshpass"]
		with os.popen("pip list") as py_package:
			self.python_packages = py_package.read()
		with os.popen("apt list --installed") as all_package:
			self.all_packages = all_package.read()
#the banner
	def banneeer(self):
		call('clear')
		call(["pyfiglet", "-j", "center", "--color=RED", "AOM Tools"])
		for number in self.numbers:
			print(number)	
#checking and installing packages
	def installpack(self):
		if "ansible" not in str(self.all_packages):
			call(["sudo", "apt-get", "update", "-y"])
			call(["sudo", "apt-get", "install", "software-properties-common", "-y"])
			call(["sudo", "apt-add-repository", "ppa:ansible/ansible"], stderr=PIPE, shell=True)
			call(["sudo", "apt-get", "update", "-y"])
			call(["sudo", "apt-get", "install", "ansible", "-y"])
		if "pyfiglet" not in str(self.python_packages):
			call(["sudo", "pip", "install", "pyfiglet"])
			call(["sudo", "pip", "install", "dnspython"])
			call(["sudo", "pip", "install", "pyyaml"])
		for package in self.packages:
			if package not in str(self.all_packages):
				call(["sudo", "apt-get", "install", package, "-y"])

