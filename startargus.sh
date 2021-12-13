#!/bin/bash
export PYTHONUNBUFFERED=1


echo Killing Celery Processes, DIE YOU LITTLE SHIT!
ps ax | grep celery | grep argus |grep -v grep

ps ax | grep celery | grep argus |grep -v grep | awk {'print $1'} | xargs kill -9

ps ax | grep -i xvfb | awk {'print $1'} | xargs kill -9

cd /app/argus_final/app/argus

echo Turning off Debug mode
#sed -i 's/DEBUG = True/DEBUG = False/g' argus/settings.py

#echo Purging Celery messages from redis
#/app/pypy/bin/celery -A argus purge -f

echo Killing Gunicorn Processes, DIE YOU LITTLE SHIT!
ps ax | grep gunicorn | grep argus | grep -v grep
ps ax |grep gunicorn | grep argus | grep -v grep | awk {'print $1'} | xargs kill -9

echo Restarting...
#nohup /app/argus_final/venv/bin/gunicorn -w2 --worker-class="gevent" -b0.0.0.0:45612 --chdir /app/argus_final/app/argus argus.wsgi --access-logfile /app/argus_final/app/argus/logs/access.log > /app/argus_final/app/argus/logs/stdout.log &
nohup /app/argus_final/venv/bin/gunicorn -w2 --worker-class="gevent" -b0.0.0.0:8000 --chdir /app/argus_final/app/argus argus.wsgi --access-logfile /app/argus_final/app/argus/logs/access.log > /app/argus_final/app/argus/logs/stdout.log &

echo Success!
sleep 3
ps ax | grep gunicorn | grep argus |grep -v grep

