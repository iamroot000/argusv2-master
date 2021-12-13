#!/bin/bash
export PYTHONUNBUFFERED=1

bash /app/argus/sync.sh

cd /app/argus/misc/async_tasks

LD_PRELOAD=/usr/local/lib/libjemalloc.so celery -A argus_app_eye worker -c 4 -Q q888 -l info -n 'argus-celery-app-eye'