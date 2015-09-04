#!/bin/bash

# $Rev: 356 $
# $Author: mlgantra $
# $Date: 2015-06-12 17:29:06 -0700 (Fri, 12 Jun 2015) $

#
# XC-Modem main function script to be invoked (as background process) in rc.local as wish. 
#

function usage {
  cat <<EOU

  Simple script to invoke xcmodem function

Usage: $0 <options>

  where options are
    -k : terminate auto start process
    -h : display this menu

EOU
  exit 1
}


# setup correct path
export PATH=".:/usr/local/bin/:$PATH"
LOG=/var/log/syslog

[ $# -ge 0 ] || usage

prog="$0"
pid="$$"
stat=($(</proc/${pid}/stat))
ppid=${stat[3]}

while getopts "kh" opt; do
  case $opt in
    k)
      # list of lingering processes
      lid=`ps -efw | grep "$prog" | grep -v grep | awk '{print $2}'`
      for id in $lid
      do
        # terminate all except itself and its parent
        if [ $id -ne $pid ] && [ $id -ne $ppid ] ; then
          killall xcmodem.py bluez-simple-agent 2>/dev/null
          kill -9 $id 2>/dev/null
          wait $id 2>/dev/null
        fi
      done
      exit 0
      ;;
    *)
      usage
      ;;
    esac
done

# terminate lingering processes first
$prog -k

MIN_IDLE_TIME=120       # 2 mins
MAX_IDLE_TIME=3600      # 1 hour

I2C_ADDRESS=0x6b
REG_STATUS=0x08
CHARGE_MASK=0x30
NO_CHARGE=0          # 0x00

v2x=0
sdir=modem
if [ -e /root/OpenXCAccessory/common/.xcmodem_boardid ]; then
  id=`cat /root/OpenXCAccessory/common/.xcmodem_boardid`
  if [ "$id" -ge "2" ]; then
    v2x=1
    sdir=v2x
  fi
fi

cd /root/OpenXCAccessory/$sdir
IDLE_TIME=$MIN_IDLE_TIME
while [ 1 ]; do
  # Wait for stable system
  sleep 10
  echo "`date`: $0 starts" >> $LOG
  xcmodem.py
  # script exit assume Engine/Power is off
  status=`i2cget -y 0 $I2C_ADDRESS $REG_STATUS`
  state=$(($status & $CHARGE_MASK))
  echo "$status $state"
  if [ $state == $NO_CHARGE ]; then
     # Power saving mode
     if [ $v2x == 1 ]; then
        rtcwake -m standby -s $IDLE_TIME
     else
        xcmodem_gsm.sh -R 0    # Turn off Telit device
        rtcwake -m standby -s $IDLE_TIME
        xcmodem_gsm.sh -R 1    # Turn on Telit device
     fi
     # Progressive idle time
     if [ -e trace_raw.json ]; then
        IDLE_TIME=$(($IDLE_TIME * 2))
        if [ $IDLE_TIME -ge $MAX_IDLE_TIME ]; then
            IDLE_TIME=$MAX_IDLE_TIME
        fi
     fi
  fi
done

exit 0
