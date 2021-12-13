#!/bin/bash

cd /app/.cache/argus
git pull
rsync -avPcp /app/.cache/argus/ /app/argus/ --exclude=logs/* --exclude=*.pyc --exclude=static/screenshots --delete

cd /app/argus


