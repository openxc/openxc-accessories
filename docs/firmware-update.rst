===============
Firmware Update
===============

Firmware Reset Button
-------

1. The OpenXC-Modem and V2X Embedded SW supports a Firmware Reset Button to reset the embedded software to a known factory released version as needed.

2. Users can activate this feature by holding the button for 5 seconds (to prevent accidental triggering) once software (vi_app) is in OPERATION stage.

3. Users can also enable this feature by calling "fw_factory_reset_enable".
  
4. The Embedded Software will be reset to the factory released version and reboot.

Over-The-Air Auto Upgrade
-------

1. OpenXC-Modem and V2X supports Over-The-Air Auto Upgrade if applicable

  1.1. Modem requires WiFi or GSM connection
  
  1.2. V2X requires WiFi connection
  
    1.2.1. WAN connection – upgrade file on AWS
    
    1.2.2. LAN via “Open_AP” – upgrade file on Modem (Modem must have the latest FW)
  
  1.3. During upgrade, some configurations will be backup to /root/OpenXCAccessory/backup such as wpa_supplicants, xc.conf, boardid, and toplogy
  
  1.4. After upgrade, user will have the option to restore configuration:
  
    1.4.1. All – restore all config wpa, id, topology, xc.conf
    
    1.4.2. Yes – option to choose, wpa configs or id, topology, xc.conf
    
    1.4.3. No – no restore will perform

2. Users can control this feature by calling "web_scp_sw_latest_version_url"
  
  The provided file from that url should contain the latest version and its associated upgraded package:

    * version
    * package
    
3. Modem & V2X SW will look for a newer version and perform upgrading as needed. If the upgrade fails, modem SW will
perform best attempt to restore previous working version


Filesystem Upgrade
-------

The V2X and Modem Filesystem can be upgraded using provided image. The upgrade process is performed using a Linux
environment.

Requirement:

1. PC with Linux OS (Ubuntu, Debian, or similar)
2. Micro SD card reader

Procedures:

1. Power on PC and boot into Linux OS
2. Download Filesystem image file

  a. For V2X, use “V2X_fs_CLEAN_v2.1.1_020516.img.gz” and save to a directory
  
  b. For Modem, use “Modem_fs_CLEAN_v2.1.1_020516.img.gz” and save to a directory
  
3. Open Terminal Window and type “sudo fdisk –l” and pay attention to what drive is mounted
4. Remove Micro SD from V2X and insert into card reader
5. Install card reader in Linux PC
6. In Terminal Window, type “sudo fdisk –l” 
  
  * System should detect newly insert Micro SD /dev/sdX1 and /dev/sdX2, where X is your Micro SD drive with partition 1 (sdX1) and partition 2 (sdX2)
  
7. Open another Terminal Window:

  a. Erase all contents from Micro SDcard “rm -r /media/john/rootfs/*” or format partition 1 with ext4 and label “rootfs”
  
  b. To copy image, type “sudo gunzip –c /YourDirectory/ V2X_fs_CLEAN_v2.1.1_020516.img.gz | dd of=/dev/sdX1 bs=8M”
  
    **WARNING: make sure image is copied to partition 1 of Micro SD. If your system doesn’t have gunzip, you will need to install with command “apt-get -y install gzip”**

8. Safely Eject Micro SD from PC, install in device, and power it on.


Mirco SD Partition
-------

The following procedure will guide you in how to partition a Micro SD card of any size to use for both V2X and Modem.

Requirement:

1. PC with Linux OS (Ubuntu, Debian, or similar)
2. Micro SD card reader
3. New 16GB Micro SD (recommended)

Procedures:

1. Power on PC and boot into Linux OS
2. Open Terminal Window and type “sudo fdisk –l” and pay attention to what drive is mounted
3. Remove Micro SD from V2X and insert into card reader
4. Install card reader in Linux PC
5. In Terminal Window, type “sudo fdisk –l” 

  * System should detect newly inserted Micro SD /dev/sdX where X is your Micro SD drive with factory partition 1 (sdX1)

6. Umount Micro SD, type “umount /dev/sdX1”
7. Start “fdisk” to partition Micro SD, type “sudo fdisk /dev/sdX” 

  In command console, type the following: See Figure F

  * “d” – delete partition

    a. Select correct partition to be deleted. Repeat this step if there is more than 1 partition

  * “n” – create new partition #1
  * “p” – create Primary partition #1
  * “1” – create partition #1
  * Press “Enter” – to use Default value 2048 for First Sector
  * “+1024M” – Last Sector end at 1GB
  * “n” – create new partition #2
  * “p” – create Primary partition #2
  * “2” – create partition #2
  * Press “Enter” – to use Default value for First Sector
  * Press “Enter” – to use Default value for Last Sector
  * “w” – to write created partition to Micro SD

.. image:: https://github.com/openxc/openxc-accessories/raw/master/docs/pictures/Figure%20F.PNG
Figure F

8. The newly created partition needs to be formatted, where Partition #1 use “ext4” and Partition #2 use “vfat” 

  * Some Linux distributions do not come with preinstalled “dosfstools” which are required for “vfat”. To install, type “apt-get –y install dosfstools” 
  
    * This command should work for Ubuntu and Debian. Please search on how to install “dosfstools” for other Linux distros

  a. “sudo mkfs.ext4 -L rootfs /dev/sdX1” - format Partition #1 with ext4 and label “rootfs”
  b. “sudo mkfs.vfat -F 32 -n DATALOG /dev/sdX2” – format Partition #2 with vfat and label “DATALOG”
  c. Note - you may need to unmount SDcard if an error occurs when trying to format “umount /dev/sdX1)

9. Safely Eject Micro SD from PC and install to device and power it on.

