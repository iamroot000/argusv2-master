#!/bin/bash
export PYTHONUNBUFFERED=1

bash /app/argus/sync.sh

cd /app/argus/

/app/pypy/bin/celery -A argus worker -c 1 -n DNS_WORKER -Q qdns -l INFO