#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE}")" ; pwd -P )
cd "$parent_path"

ps ax | grep PROXYCONTROLLER_status_checker 

ps ax | grep PROXYCONTROLLER_status_checker | awk {'print $1'} | xargs kill -9

printlogfile="logs/print.log"

mkdir -p logs

#nohup /app/pypy/bin/pypy ./main.py //LEMORIA>> $printlogfile 2>>$printlogfile &
nohup python2.7 celery_worker.py //PROXYCONTROLLER_status_checker $printlogfile 2>>$printlogfile &

echo "stdout is at $printlogfile"
