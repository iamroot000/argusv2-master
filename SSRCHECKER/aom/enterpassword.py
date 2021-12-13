#!/usr/bin/python3
#created by: Yroll Jay-R Macalino
from py_config import colordesign
import getpass

def enterpassword():
	print(colordesign("cnormal"))
	print("enter office PC settings password".title())
	of_password = getpass.getpass("Password: ")
	return of_password
