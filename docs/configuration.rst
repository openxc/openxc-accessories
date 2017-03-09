=============
Configuration
=============

Configuration File
-------

The following section describes the configuration file for the OpenXC Software.  

* /root/OpenXCAccessory/common

.. csv-table::
   :header: "Option Name", "Unit", "Default Value", "Description"
   :widths: 20, 20, 20, 30
   
   "openxc_vi_mac", "XX:XX:XX:XX:XX:XX", "None", "Vehicle Interface Dongle MAC"
   "openxc_vi_enable", "boolean (0 .. 1)", "1/0 for MODEM/V2X", "Enabling Vehicle Interface communication"
   "openxc_md_enable", "boolean (0 .. 1)", "1/0 for MODEM/V2X", "Enabling V2X-MD Interface communication (10)"
   "openxc_vi_trace_snapshot_duration", "seconds", "10", "Vehicle data stream trace recording snapshot duration"
   "openxc_vi_trace_idle_duration", "seconds", "110", "Idle duration between subsequent Vehicle data trace recording snapshot"
   "openxc_vi_trace_truncate_size", "bytes", "0", "Vehicle data trace snapshot truncate size where 0 means no truncate"
   "openxc_vi_trace_filter_script", "", "None", "Vehicle data trace filtering executable script where the script is required to accept stdin input stream and generate stdout output (1)"
   "openxc_vi_trace_number_of_backup", "integer", "0", "Number of vehicle data trace will be backed up in provided micro SD card (2)  where O means no back up is needed"
   "openxc_vi_trace_backup_overwrite_enable", "boolean (0 .. 1)", "1", "Enabling to overwrite backup files when the SD disk is full"
   "web_scp_userid", "", "anonymous", "Remote server scp userid"
   "v2x_lan_scp_userid", "", "root", "Remote server(Modem) scp userid for V2X in Topology 3"
   "web_scp_pem", "", "None Remote server SSL Enscripted Private key PEM"
   "web_scp_apn", "", "apn", "Remote server Access Point Name as per details provided with the SIM card contract"
   "web_scp_config_download_enable", "boolean (0 .. 1)", "0", "Enabling congifuration file download from remote server"
   "web_scp_config_url", "", "ip:file", "Configuration file URL on the remote server 
   
      (<IP>:[<directory>/]<filename>)
      (3)"
   "web_scp_vi_target_url", "", "ip:file", "Remote server target file URL in this format
   
      (<IP>:[<directory>/]<filename>)
      (4)"
   "web_scp_target_overwrite_enable", "boolean (0 .. 1)", "1", "Enabling to overwrite remote server target file (5)"
   "web_scp_vi_trace_upload_enable", "boolean (0 .. 1)", "0", "Enabling vehicle data records to be uploaded into remote server"
   "web_scp_vi_trace_upload_interval", "seconds", "3600", "Interval to upload vehicle data stream into a remote server (6)"
   "web_scp_sw_latest_version_url", "",  "None", "Auto upgrade version URL
   
      (<IP>:[<directory>/]<filename>)
      where None means Auto Upgrade is disable"
   "v2x_lan_scp_sw_latest_version_url", "", "20.0.0.1:/tmp/upgrade.ver", "Auto upgrade version URL 
   
      (<IP>:[<directory>/]<filename>)"
   "fw_factory_reset_enable", "boolean (0 .. 1)", "1", "Enabling Firmware Factory Reset Button support"
   "power_saving_mode", "", "Normal", "Power saving profile where value is (performance / normal / saving)"
   "led_brightness", "", "128", "LED brightness level where level is (0 .. 255) (7)"
   "gps_log_interval", "seconds", "10", "Interval to log GPS Acquire Current Position into /var/log/xcmodem.gps if applicable"
   "gps_enable", "boolean (0 .. 1)", "1/0", "for MODEM/V2X Enabling GPS module (8)"
   "gsm_enable", "boolean (0 .. 1)", "1/0", "for MODEM/V2X Enabling GSM module (9)"
   "openxc_v2x_trace_snapshot_duration*", "seconds", "", "RSU data stream trace recording snapshot duration for topology 3."
   "openxc_v2x_trace_idle_duration*", "seconds", "", "Idle duration between subsequent RSU data trace recording snapshot for topology 3"
   "xcmodem_ip_addr", "IP address", "20.0.0.1", "IP address for the Modem when it acts as an AP"
   "openxc_xcV2Xrsu_trace_snapshot_duration", "seconds", "", "Duration control for RSU snapshot in V2X and RSU"
   "openxc_xcV2Xrsu_trace_idle_duration", "seconds", "", "Interval control between RSU snapshots"
   "web_scp_xcV2Xrsu_target_url", "URL", "", "URL for uploading RSU logs"
   "web_scp_rxcV2Xsu_trace_upload_interval", "seconds", "", "Interval control between successive web uploads"
   "web_scp_xcV2Xrsu_trace_upload_enable", "seconds", "", "Enable/Disable control for web upload of RSU log"
   "openxc_xcV2Xrsu_msg_send_interval*", "seconds", "", "Control for interval between RSU identification message broadcast"
   "chd_txpower", "", "2 dBm", "Transmit power for cohda radio" 
   "chd_radio", "(‘a’..’b’)", "a", "Radio to be used for the Cohda module"
   "chd_antenna", "(1..3)", "3", "Antenna(s) to be used for radio"
   "chd_chan_no", "
   | 10 MHz channel 
   | (172, 174, 176, 
   | 180, 182, 184)  
   | 20MHz channel 
   | (175, 181) All 
   | channels SCH", "184", "802.11p Channel"
   "chd_modulation", "
   | MK2MCS_R12BPSK 
   | MK2MCS_R34BPSK 
   | MK2MCS_R12QPSK 
   | MK2MCS_R34QPSK 
   | MK2MCS_R12QAM16 
   | MK2MCS_R34QAM16 
   | MK2MCS_R23QAM64 
   | MK2MCS_R34QAM64 
   | MK2MCS_DEFAULT 
   | MK2MCS_TRC", "MK2MCS_R12QPSK", "Modulation scheme for cohda"
   "chd_ch_update_enable", "Boolean(0..1)", "0", "Flag to update the cohda channel parameters from the config parameters during the application run"
   
* For optimal RSU trace recording in topology 3, trace time interval should be set as 1:2:1 ratio. Default value is 20:40:20. Where:

   * RSU device set “openxc_xcV2Xrsu_msg_send_interval = 20”
   * Modem device set “openxc_v2x_trace_snapshot_duration = 40” and “openxc_v2x_trace_idle_duration = 20”


Notes
-------

1) An executable shell script like the following:

   #!/bin/bash
   egrep "transmission|ignition”

   will generate a trace file such as:
   
   {"name":"ignition_status","value":"run","timestamp":1427334376.624450}
   {"name":"ignition_status","value":"run","timestamp":1427334376.664466}
   {"name":"ignition_status","value":"accessory","timestamp":1427334376.700860}
   {"name":"transmission_gear_position","value":"neutral","timestamp":1427334376.724524}
   {"name":"torque_at_transmission","value":10.200000,"timestamp":1427334376.734772}
   {"name":"transmission_gear_position","value":"first","timestamp":1427334376.765584}
   {"name":"ignition_status","value":"run","timestamp":1427334376.786151}
   ...

2) Raw vehicle trace snapshot will be saved as /mnt/data/trace_raw_<no>.json  
   
   */mnt/data is mounted to the first recognized formatted partition on the inserted micro SD card
    
3) A unique configuration template will be created at the remote server during the device registration process, e.g: <IP>:[<directory>/]<hostname>.<filename>

   *To be used instead of provided <IP>:[<directory>/]<filename>, where <filename> is xconfig.conf by design
   
4) Uploading file will be named as <IP>:[<directory>/]<hostname>[.<timestamp>].<filename> at remote server where <filename> is trace.json by design
5) If overwrite flag is disabled, YYMMDDhhmmss timestamp will be added to target file name.
6) User should be aware of additional time due to trace file conversion and server connection establishment.
7) LED brightness default is 255|128|0 for performance|normal|saving of power_saving_mode respectively
8) Default value is based upon board type. This option is not valid for V2X as the V2X accessory does not support GPS.
9) Default value is based upon board type. This option is not valid for V2X as the V2X does not support GSM.
10) Default value is based upon board type. Need to be enable on both MODEM and V2X to operate V2X-Modem interface.


Power-Saving Mode Profile
^^^^^^^^^^^^^

To illustrate ability to support different power saving modes, OpenXC-Modem Embedded Software implements simple profiles
(aka performance, normal and saving) for certain functions as shown in the following table:

.. image:: https://github.com/openxc/openxc-accessories/raw/master/docs/pictures/Table%209.PNG


LEDs
-------

The Modem has 5 LED indicator lights. Battery LED has 2 colors (RED and GREEN) while the others are single color.  OpenXC Modem Embedded SW controls the LEDs via gpio (/sys/class/leds/XXX).

* After power up, all LEDs except the Battery LED will blink fast.
* During software upgrades (Over-The-Air or Manufacturing Firmware Reset), all LEDs will blink slow.
* Run xcmodem.py to change LEDs according to the following table. 

.. csv-table::
   :header: "LED", "Color Mode", "Function", "Keyword", "State"
   :widths: 20, 20, 20, 20, 20
   
   "Bat_grn_led", "
   | OFF 
   | ON 
   | FAST BLINK", "
   | VBAT < 3.55V 
   | VBAT >= 3.55V 
   | Charging", "charger", "
   | NOT_CHARGE/CHARGE_DONE 
   | PRE_CHARGE/FAST_CHARGE"
   "Bat_red_led", "
   | OFF 
   | ON 
   | FAST BLINK", "
   | VBAT > 3.65V 
   | VBAT <= 3.65V 
   | Charging", "charger", "
   | NOT_CHARGE/CHARGE_DONE 
   | PRE_CHARGE/FAST_CHARGE"
   "GSM_led", "
   | OFF 
   | ON 
   | FAST BLINK 
   | SLOW BLINK", "
   | IDLE or PPP lost 
   | GSM is ready 
   | PPP data transferring 
   | SIM not inserted", "gsm_app", "
   | IDLE / LOST 
   | PENDING 
   | OPERATION 
   | PENDING"
   "GPS_led*", "
   | OFF 
   | ON 
   | FAST BLINK 
   | SLOW BLINK", "
   | Not start 
   | GPS Unit power up 
   | Valid GPSAPC 
   | Locking for valid GPSAPC", "gps_app", "
   | IDLE 
   | CONNECT 
   | OPERATION 
   | LOCKING"
   "BT_led", "
   | OFF 
   | ON 
   | FAST BLINK 
   | SLOW BLINK", "
   | IDLE 
   | VI Dongle Connect 
   | VI Dongle Pairing 
   | VI Dongle Discovery", "vi_app", "
   | IDLE / LOST 
   | OPERATION 
   | DISCOVERED 
   | ADDR_INQUIRY/ADDR_ASSIGNED/DISCOVERED"
   "Wifi_led**", "
   | OFF 
   | ON 
   | FAST BLINK 
   | SLOW BLINK", "
   | Not Connected 
   | Connected 
   | Data Transmitting 
   | Device N/A", "na", "
   | IDLE 
   | PENDING 
   | OPERATION 
   | NO WIFI DEVICE DETECTED***"
   "80211_led", "
   | OFF 
   | FAST BLINK", "
   | Not Connected 
   | Data Transmittin", "na", "
   | IDLE 
   | OPERATION"
 
.. note:: 
    .* V2X and RSU use “gps” as “wifi” led.
   
    .** V2X and RSU use “wifi” led for 802.11p led.
   
    .*** TI WiFi module occasionally doesn’t come up during boot-up and may need manual power cycle.


Brightness Control
^^^^^^^^^^^^^

LED brightness is controlled by Power-saving-mode profile. However, users can overwrite the brightness level using “led_brightness” (in xcmodem.conf). The brightness level can be adjusted from 0 (dim) to 255 (bright).
