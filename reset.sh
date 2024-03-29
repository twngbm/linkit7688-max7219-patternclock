#!/bin/ash
sleep 5
while true
do
  ls /Media/USB-A1
  retval=$?
  echo $retval
  if [ $retval -eq 0 ] ; then
    cp /Media/USB-A1/Schedule.json /root/
    sleep 1
    pgrep python | xargs kill
    while true
    do
      ls /Media/USB-A1
      if [ $? -eq 0 ] ; then
        echo "USB Mounted"
      else
        break
      fi
    done
    python /root/main.py &
  else
    sleep 1
  fi
done
