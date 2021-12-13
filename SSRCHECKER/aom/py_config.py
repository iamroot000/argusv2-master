#!/usr/bin/python3
#created by: Yroll Jay-R Macalino
import os 

def colordesign(colorrr):
	d_color = {
	"cgreen" : "\033[1;32m",
	"cred" : "\033[1;31m",
	"cblue" : "\033[1;34m",
	"cyellow" : "\033[1;33m",
	"ccyan" : "\033[1;36m",
	"cwhite" : "\033[1;37m",
	"cnormal" : "\033[1;0m"
	}
	return d_color[colorrr]



