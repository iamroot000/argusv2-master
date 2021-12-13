#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE}")" ; pwd -P )
cd "$parent_path"

ps aux | grep PROXYCONTROLLER | awk '{system("kill -9 " $2)}'

printlogfile="logs/out.log"

mkdir -p logs

#nohup /app/pypy/bin/pypy ./main.py //LEMORIA>> $printlogfile 2>>$printlogfile &
nohup python2.7 celery_worker.py //PROXYCONTROLLER $printlogfile 2>>$printlogfile &

echo "stdout is at $printlogfile"
