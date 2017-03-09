===================
Directory Structure
===================

The following directory structure is used.

* /root/OpenXCAccessory:

.. csv-table::
   :header: "Directory Name", "Description"
   :widths: 20, 60

   "bluez-test-script", "BlueZ 5.23 test scripts (1)"
   "openxc-python", "OpenXC Python development platform. (1)"
   "startup", "Base board startup scripts (1)"
   "common", "Common Software for OpenXC-Modem/OpenXC-V2X"
   "modem", "Modem specific software"
   "backup", "Place holder for Firmware Factory Reset and current software versions. Also has backup of configuration files such as WiFi, xc.conf, boardid, and topology"
   "etc", "wpa configuration files for modem, V2X, and RSU"
   "V2X", "V2X specific Software (1)"
   "rsu", "RSU specific Software"
   
.. note::  1 - Not covered in this document

* /root/OpenXCAccessory/common

.. csv-table::
   :header: "File Name", "Description"
   :widths: 20, 60

   "xcmodem_boardid", "Hidden file to specify board type: where board_type is
    
    board _type = {
      (0) {'type': 'MODEM-EVT', 'prefix': 'OpenXC-VI-MODEM'}, # OpenXC-Modem EVT
      (1) {'type': 'MODEM-DVT', 'prefix': 'OpenXC-VI-MODEM'}, # OpenXC-Modem DVT
      (2) {'type': 'V2X' , 'prefix': 'OpenXC-VI-V2X'} # OpenXC-V2X
      (3) {'type': 'RSU' , 'prefix': 'OpenXC-VI-V2X'} # OpenXC-V2X
    }"
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
   "xc_app.py", "OpenXC-Modem application (Mobile / PC) agent and unit test"
   "xc_vi.py", "OpenXC-Modem Vehicle Interface agent and unit test"
   "xcmodem.conf.web", "OpenXC-Modem auto start script, used during board startup"
   "xc.conf", "Local user variable options configuration file. This file is common to Modem, V2X and RSU"
   "xc_rsu_common.py", "File for RSU functions that are common to V2X and RSU"
   "ota_upgrade.py", "File for OTA upgrade functions"
   "xc_ver.py", "PpenXC-Modem version"
   "xc_scp.pem", "RSA Private Key"
   "xc.common.py", "OpenXC-Modem common functions"
   "cleanup.py", "RSU cleanup"
   
* /root/OpenXCAccessory/modem: (applicable for OpenXC Modem Accessory only)

.. csv-table::
   :header: "File Name", "Description"
   :widths: 20, 60

   "xc.conf", "Link to the xc.conf file in common directory"
   "xcmodem.conf.web", "Downloaded configuration file from remote server, if applicable"
   "xcmodem.conf.bk", "Configuration backup file which is generated during upgrading process"
   "xcmodem.conf.cur", "All options value currently in effect"
   "trace_raw.json", "Current raw VI stream snapshot in json format"
   "trace_raw_bk.json", "Back up of current raw VI stream snapshot to be processed for uploading"
   "trace.json", "Modified upload-able VI stream snapshot in json format"
   "xcmodem_gsm.py", "GSM agent and unit test"
   "xcmodem_gsm.sh", "GSM debug shell script"
   "xcmodem_gps.py", "GPS agent and unit test"
   "xcmodem_gps.sh", "GPS debug shell script"
    
* /root/OpenXCAccessory/backup: 

.. csv-table::
   :header: "File Name", "Description"
   :widths: 20, 60

   "factory", "Directory to store factory released SW version info (upgrade.ver) and its upgraded package"
   "current", "Directory to store current SW version info (upgrade.ver) and its upgraded package"
   "other", "Directory to store backup of wpa_supplicant config files for Modem, V2X, RSU, and xc.conf before upgrade is performed. Boardid and topology are also backed up"
   "previous", "Directory for previous SW version during over-the-air auto upgrade, if applicable"
   
* /root/OpenXCAccessory/v2x: (applicable for OpenXC V2X Accessory only)
   
.. csv-table::
   :header: "File Name", "Description"
   :widths: 20, 60

   "xc.conf", "Link to the xc.conf file in common directory"
   "xc_scp.pem", "PEM key file to access AWS"
   "xc.conf.cur", "All options value currently in effect"
   "xc_v2x.py", "V2X-MODEM MD client agent and unit test"
   
* /root/OpenXCAccessory/etc: 
   
.. csv-table::
   :header: "File Name", "Description"
   :widths: 20, 60

   "create_symlinks.sh", "Remove and replace exisiting .etc files with new files"
   "wpa_supplicant_modem.conf", "Overwrite modem configuration file whenever changed"
   "wpa_supplicant_rsu.conf", "Overwrite RSU configuration file whenever changed"
   "wpa_supplicant_v2x.conf", "Overwrite V2X configuration file whenever changed"
   "wpa_supplicant_v2x_top2.conf", "Overwrite V2X configuration file whenever changed in Topology 2"
   
* RSU: (applicable for OpenXC V2X Accessory only)
   
.. csv-table::
   :header: "File Name", "Description"
   :widths: 20, 60

   "xc_rsu.py", "V2X-MODEM MD client agent and unit test"
   "rsu_fn.py", "File for RSU specific functions e.g. garage"
   
