.. OpenXC Accessories documentation master file, created by
   sphinx-quickstart on Fri Aug 28 12:54:56 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================================
OpenXC Accessories
=================================

.. image:: /_static/logo.png

:Version: 0.0.1
:Web: http://openxcplatform.com
:Documentation: http://accessories.openxcplatform.com
:Source: http://github.com/openxc/openxc-accessories

The OpenXC Accessories are a line of hardware accessories intended to augment the 
`Vehicle Interface (VI) <http://openxcplatform.com/vehicle-interface/hardware.html>`_
and communicate with other entities. The benefit of the Accessory Platform is that 
all accessories share a common base (or motherboard) and new features are added by
modifying or designing a new daughter card (mPCIe connector). 

The base board contains an Atmel SAMA5 (Cortex-A5) running embedded Linux. All
accessory functions are coded in Python. Interfaces include SD card slot, Bluetooth 
Classic, Bluetooth Low Energy (a.k.a Bluetooth Smart), USB OTG, and WiFi. A debug serial port is available.

The first in the line of accessories is a 3G Modem to enable sharing of vehicle 
data directly with the cloud, OTA updates to the Modem configuration, and still
allows use of the Enabler app. 

The second accessory is the V2X device.  The OpenXC-V2X device can act as a modem, which connects to the VI device or a phone, and shares OpenXC data via WiFi or 802.11p (in RSU mode).

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   getting-started
   system-overview
   configuration
   design-sources
   license-disclosure


License
-------

Copyright (c) 2015 Ford Motor Company

Licensed under the BSD license.

This software depends on other open source projects, and a binary distribution
may contain code covered by :doc:`other licenses <license-disclosure>`.
