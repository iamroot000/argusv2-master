#!/bin/bash
export PYTHONUNBUFFERED=1

bash /app/argus/sync.sh

cd /app/argus/proxycontroller/lib/status_checker

python2.7 celery_worker.py