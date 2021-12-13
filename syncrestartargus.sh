#!/bin/bash

#rm -rf /app/argus

cd /app/.cache/argus

git pull

rsync -avPcp /app/.cache/argus/ /app/argus/ --exclude=logs/* --exclude=*pyc --exclude=static/screenshots

bash /app/argus/startargus.sh
