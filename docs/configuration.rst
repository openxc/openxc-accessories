=============
Configuration
=============

Configuration File
-------

The following section describes the high level software design for the OpenXC-Modem and V2X devices.  The picture below shows the communication links between devices.




* /root/OpenXCAccessory/common

.. csv-table::
   :header: "Option Name", "Unit", "Default Value", "Description"
   :widths: 30, 20, 20, 40
   
   "openxc_vi_mac", "XX:XX:XX:XX:XX:XX", "None", "Vehicle Interface Dongle MAC"
   
   
   
   
   
   
   

   "xcmodem_topology", "File to specify the config mode/topology
   
      (1) Topology 1
      (2) Topology 2
      (3) Topology 3
      "
   "xc_led.py", "LED unit test"
   "xc_ser.py", "Serial Terminal Emulator
   
    Usage: xcmodem_ser.py [-h] dev
      where dev: Serial Device"
   "xc_cmd.py", "OpenXC-Modem application command handler and unit test"



.. image:: https://github.com/openxc/openxc-accessories/raw/master/docs/pictures/Figure%201.PNG

.. note::  1 - Not covered in this document




