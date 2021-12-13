#!/usr/bin/python3
import yaml
filename = "initialization-centOS7-forwarding-with-puppet-2018.yml"
with open(filename) as f:
    fyaml = yaml.load(f, Loader=yaml.FullLoader)
test = fyaml[0]
print(test)

