#!/bin/bash

rsync -avPp aaron@192.168.11.172:~/PycharmProjects/argus/proxycontroller/lib/misc/ /app/proxy_agent/ --exclude=jsons/* --exclude=pids/* --exclude=logs/* --exclude=sscache --delete
