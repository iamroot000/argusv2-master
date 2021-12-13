#!/usr/bin/python3
#created by: Yroll Jay-R Macalino
from subprocess import *
import yaml

with open('initialization-centOS7-forwarding-2019.yml', 'r') as inityaml:
    centyaml = yaml.load(inityaml)
test = centyaml["hosts"]
for testing in test:
    print(testing["hosts"])