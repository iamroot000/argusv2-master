import os, json, requests

config_file = os.path.join('/root/Documents/django-dir/test_project/src/CDN', 'SSRCHECKER/aom/ansible/config.json')
config_read = open(config_file, 'r')
condigdata = json.load(config_read)

filenames = condigdata["configfile"]
files = {}
for filename, file in filenames.items():
    filename_f = os.path.join('/root/Documents/django-dir/test_project/src/CDN', "SSRCHECKER/aom/ansible/{}".format(file))
    filename_r = open(filename_f, 'r').read()
    files.update({filename:filename_r})


print(json.dumps(files, indent=4).replace('\n', ''))