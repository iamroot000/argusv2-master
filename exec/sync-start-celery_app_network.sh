#!/bin/bash
export PYTHONUNBUFFERED=1

bash /app/argus/sync.sh

cd /app/argus/

celery -A argus worker -c 1 -n NETWORK_WORKER -Q qnetwork -l INFO