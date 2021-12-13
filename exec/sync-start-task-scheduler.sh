#!/bin/bash
export PYTHONUNBUFFERED=1

bash /app/argus/sync.sh

cd /app/argus/task_scheduler

python2.7 main.py