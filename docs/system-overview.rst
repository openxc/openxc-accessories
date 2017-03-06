=============
System Overview
=============

General Overview
-------

The following section describes the high level software design for the OpenXC-Modem and V2X devices.  The picture below shows the communication links between devices.

.. image:: https://github.com/openxc/openxc-accessories/raw/master/docs/pictures/Figure%201.PNG

The OpenXC Embedded Software initiates connections shown in Figure 1.
The devices (VI, V2X, Modem, Phone, RSU, AP and Cloud) can be configured as follows:

* Mode 1: VI + Modem + Phone + Cloud
* Mode 2: VI + V2X + RSU + Phone + Cloud
* Mode 3: VI + Modem + V2X + RSU + Phone + Cloud

The connections that are supported in these modes are shown below. 

.. image:: https://github.com/openxc/openxc-accessories/raw/master/docs/pictures/Figure%202.PNG

.. image:: https://github.com/openxc/openxc-accessories/raw/master/docs/pictures/Figure%203.PNG

.. image:: https://github.com/openxc/openxc-accessories/raw/master/docs/pictures/Figure%204.PNG

Application Overview
-------

.. image:: https://github.com/openxc/openxc-accessories/raw/master/docs/pictures/Figure%206.PNG

The Modem, V2X and RSU devices are designed as communication sources connecting through sockets and queues. 

Tasks are handled in separate threads to handle concurrent activities and exchange data safely.  The threads are designed to be stoppable, using the following techniques as applicable:

* System exception to detect connection errors, or connection termination.
* Timeout exception to detect lost connection, especially in receiving/listening thread.
* External control flag to terminate execution loop.

The exchange of data from the sources to apps can be enabled or disable based on the configuration parameters described in the next section. The devices are connected through either Bluetooth, WIFi or 802.11p as shown in Figure 1.

* The Bluetooth interface uses 2 independent RFCOMM socket (Send & Recv) threads and associated data buffer queues.
* The WiFi interface uses 2 independent INET socket (Send & Recv) threads and associated data buffer queues.
* The 802.11p interface uses 2 independent UDP broadcast socket (UdpSend & UdpRecv) threads and associated data buffer queues.


Modem Overview
-------

* Source: VI

  * VI through Bluetooth socket

*Applications

  * VI stream recording
  * GSM "Network Server Upload" task is handled in a separate stoppable thread
  * GPS "Acquire Current Position" task is handled in a separate stoppable thread
  * Environmental Monitor tasks (Battery level, Charger status, FW reset button …) are handled in separate stoppable threads.
  * Mobile App Thread
  * V2X connection thread (Topology 3)

V2X Overview
-------

* Sources:

  * VI through Bluetooth socket (Topology 2)
  * VI through modem over WiFI (Topology 3)
  * RSU through UDP broadcast over 802.11p
  * Self-identification announcement via UDP broadcast over 802.11p

* Applications

  * VI stream recording
  * RSU stream recording
  * Environmental Monitor tasks (Battery level, Charger status, FW reset button …) are handled in separate stoppable threads.
  * Mobile App Thread (Topology 2)
  * VI data upload
  * RSU data upload

RSU Overview
-------

* Source:

  * Garage Simulator, sends garage data through UDP broadcast over 802.11p

* Application

  * RSU data recording. Collects vehicle announcement and VI data if enabled)
  
