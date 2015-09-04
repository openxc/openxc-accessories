#!/bin/bash

# $Rev: 400 $
# $Author: mlgantra $
# $Date: 2015-06-25 16:41:12 -0700 (Thu, 25 Jun 2015) $

# Main script to upgrade xcmodem software
# The script is tailored for included components of the upgrading package.
# Assume that there is no network connection
# and base system supports basic function such as python, apt-get

ver=0.14

header="OpenXCModem Software Upgrade Utility - Rev:${ver}"

function usage {
  cat <<EOU

${header}

Usage: $0 

  Upgrade utility for following components:
    xcmodem-0.1.4.tar.gz

EOU
  exit 1
}

image=${PWD}/$1
logname=`echo $0 |sed 's/.sh//'`".log"
logfile=/var/log/$logname

filelist="$0 \
xcmodem-0.1.4.tar.gz"


missing () {
    echo "missing $1"
    exit 1
}


main () {
    echo $header

    if [ $# -gt 0 ]; then
        usage
    fi

    for f in $filelist
        do [ -f $f ] || missing $f
    done

    if [ -d /root/OpenXCModem ]; then
        mv -f /root/OpenXCModem /root/OpenXCAccessory
    fi

    # Upgrade 0.9 packge as prerequisite
    # blueZ 5 
    bt_ver=`bluetoothd -v | awk '/5./'`
    if [ "$bt_ver" == "" ]; then
        echo "Unexpected blueZ `bluetoothd -v` - Please perform upgrade 0.9 first"
        exit 1
    fi

    #
    # Handle images tarball
    #
    sdir=${PWD}

    # copy applications
    # create application directory
    wdir=/root/OpenXCAccessory
    mkdir -p $wdir $wdir/modem $wdir/common $wdir/startup

    # install code drop
    cd $wdir
    # wipe out common directory - Precaution
    rm -fr common/*
    tar xvf $sdir/xcmodem-0.1.4.tar.gz
    mv -f modem/xcmodem.conf modem/xcmodem.conf.bk
    mv -f common/xcmodem.conf modem
    mv -f common/xcmodem_scp.pem modem
    chmod 600 modem/xcmodem_scp.pem
    cd $wdir/common
    for f in `ls`; do rm -f ../modem/$f; ln -sf ../common/$f ../modem; done

    # /etc/rc.local
    cp -p $wdir/startup/rc.local /etc/rc.local 
    chmod 755 /etc/rc.local

    # create backup directory if needed
    # Note: 0.1.4 is factory reset version
    mkdir -p $wdir/backup
    dlist="factory current"
    for i in $dlist
        do  dir="$wdir/backup/$i"
            rm -fr $dir
            mkdir -p $dir
            echo "0.1.4" > $dir/upgrade.ver
            echo "xcmodem-upgrade-0.14.tar.gz" >> $dir/upgrade.ver
            cp -p $sdir/xcmodem-upgrade-0.14.tar.gz $dir
        done

    echo "system need to be rebooted to take effect ..."
    reboot
}

main $1 2>&1 | tee $logfile
