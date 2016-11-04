#!/bin/bash

RETVAL=0
WORK_PATH=/opt/apps/HubaoMS
STDOUT=/data/www/HubaoMS/logs/stdout.log
STDERR=/data/www/HubaoMS/logs/stderr.log

if [ ! -d "/data/www/HubaoMS/logs" ]; then
  mkdir -p /data/www/HubaoMS/logs
  touch ${STDOUT} ${STDERR}
fi

start(){
echo  "Starting Management system ..."
if [ `ps -ef | grep HubaoMS | grep -v grep | wc -l` == '0' ]; then
    exec ${WORK_PATH}/env/bin/gunicorn --chdir  ${WORK_PATH}/HubaoMS \
             -c ${WORK_PATH}/gunicorn.conf 'app:app' 1>>${STDOUT} 2>> ${STDERR} &

fi
}

stop(){
echo  "Terminating Management system..."
if [ `ps -ef | grep HubaoMS | grep -v grep | wc -l` != '0' ]; then
        ps -ef | grep HubaoMS | grep -v grep | awk '{print $2}' | xargs kill -9
fi
}


case $1 in
start)
start
;;
stop)
stop
;;
restart)
stop
start
;;
*)
echo "Invalid choice! Please input 'start', 'stop' or 'restart'";;
esac
exit ${RETVAL}
