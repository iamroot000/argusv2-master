#!/bin/bash
export PYTHONUNBUFFERED=1

bash /app/argus/sync.sh

cd /app/argus/

celery -A argus worker -c 1 -n NRPE_WORKER -Q qnrpe -l INFO