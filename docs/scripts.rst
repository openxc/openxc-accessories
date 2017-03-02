=======
Scripts
=======

Main Functions
--------

OpenXCSoftware main functions can be performed by invoking the appropriate scripts depending on the device (Modem, V2X or RSU) as described in this section.

**Modem**: The Modem main function can be started by invoking xc_modem.py in /root/OpenXCAccessory/modem directory

.. image:: https://github.com/openxc/openxc-accessories/raw/master/docs/pictures/Figure%2014.PNG

**V2X**: The V2X main function can be started by invoking xc_v2x.py in /root/OpenXCAccessory/v2x directory

.. image:: https://github.com/openxc/openxc-accessories/raw/master/docs/pictures/Figure%2015.PNG

**RSU**: The RSU main function can be started by invoking xc_rsu.py in /root/OpenXCAccessory/rsu directory

.. image:: https://github.com/openxc/openxc-accessories/raw/master/docs/pictures/Figure%2016.PNG

Config Scripts
--------

The Configuration scripts are used to setup the environment for the application. These scripts are stored in ~/OpenXCAccessory/startup directory.

* openxc_init

 * Set the config files, Set boardid file contents, set topology, set .pem files found `here <https://github.com/openxc/OpenXCAccessory/tree/master/scripts>`_.

* openxc_load_config

 * Load /restore config files found `here <https://github.com/openxc/OpenXCAccessory/tree/master/scripts>`_.

* openxc_save_config

 * Save backup of current configuration found `here <https://github.com/openxc/OpenXCAccessory/tree/master/scripts>`_.

Python Scripts
--------

Helpful Python scripts for converting OpenXC trace files into JSON data files optimized for browsers (and Freeboard!)

* /openxc_json_converter.py

Takes any raw trace file from the OpenXC library (examples can be downloaded from `here <http://openxcplatform.com/resources/traces.html>`_) and converts into an array of JSON data objects, which can be parsed by Freeboard datasources and widgets, and many other external APIs

Example Usage:
```Shell
$ python openxc_json_converter.py input_trace_filename.json
```

This will output a new version of the trace file named `input_trace_filename_VALIDATED.json`

* /signal_extractor.py

Takes in a JSON data file (created by using /openxc_json_converter.py) and a list of signals (each prepended with '-s') that the user wishes to keep.  Outputs new JSON data file with only those signals included, named `input_trace_filename_VALIDATED_STRIPPED.json`

Example Usage:
```Shell
$ python signal_extractor.py input_trace_filename_VALIDATED.json -s openxc_signal_name -s openxc_signal_name2 [...]
```

* /normalizer.py

Strips the input JSON data file to one data point, per signal, per second.  Outputs new files named `input_trace_filename_VALIDATED_STRIPPED_NORMALIZED.json`

Example Usage:
```Shell
$ python normalizer.py input_trace_filename_VALIDATED_STRIPPED.json
```

WiFi Setup
--------

* Modem

  * The script connects the modem to one of the Access Points (APs) specified in the "wpa_supplicant" file.
  * The script opens an “OPENXC_AP” access point with 20.0.0.1 IP address for the V2X device to connect to the modem, in topology 3.
  
* V2X

  * The script connects the V2X device to one of the APs specified in the "wpa_supplicant" file, in topology 2.
  * The script connects to “OPENXC_AP” from modem, in topology 3. 
   
* RSU

  * The script connects the RSU to one of the APs specified in the "wpa_supplicant" file.
   
.. note:: 
 The scripts reset the hardware (Modem and V2X) if the required connector is not connected.

Cohda Setup
--------

The "Cohda_setup.sh" script performs the following functions for the setting the Cohda environment and the necessary IP setup for the
802.11p based network.

* Enable Cohda HW.
* Download Firmware.
* Install llc kernel object with TCP/IP and UDP/IP support.
* Bring up Cohda interface and assign IP address.
* Create IP neighborhood for other Cohda devices (this is a pre-assigned network configuration).

  * Each Cohda device is assigned a unique 10.0.0.XX address and a unique MAC address based on the last four characters of the Bluetooth MAC address, found through a lookup table in the script.
  * All the Cohda devices in the supplied population (50 units) are added to the current device neighborhood.
  
  
