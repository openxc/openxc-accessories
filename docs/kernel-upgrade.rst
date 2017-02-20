==============
Kernel Upgrade
==============

In order to successfully upgrade the kernel, you will need the following two cables:

* USB-A to micro-B cable
* USB to Serial UART (FTDI TTL-232R-3V3), which can be purchased `here <http://www.amazon.com/GearMo%C2%AE-3-3v-Header-like-TTL-232R-3V3/dp/B004LBXO2A>`_.

Upgrade Procedure
--------

* Power V2X device Off.
* Remove top cover by unscrewing the 4 screws on bottom of device.
* Connect micro-B side of USB-A to micro-B cable to device. 
* Connect USB-A side of cable to PC. 
* Connect FTDI cable to device.
        
    * You will need to install the FTDI driver when connecting the cable to a PC for the first time. The FTDI driver can be downloaded from `here <https://github.com/openxc/openxc-accessories/blob/master/tools/FTDI_Cable_Windows_Driver.zip>`_.
    
    * When connecting the FTDI cable to the V2X device, make sure the Black cable on the serial connector connects to the GND pin on the V2X device. This is to ensure proper polarity. 
    
* Connect the USB-A side of the FTDI cable to your PC and allow the FTDI driver to complete the installation.

    * Driver installation will assign a COMx port.
    
* Open TeraTerm and connect to the previously assigned COMx port with a 115200 baud rate.

    * Instructions for downloading TeraTerm can be found  `here <https://github.com/openxc/openxc-accessories/tree/master/tools/ModemConnect/Documents>`_.

* Power V2X device On.
* Stop “autoboot” by pressing any key on your keyboard.

.. image:: https://github.com/openxc/openxc-accessories/blob/master/docs/pictures/Figure%20A.PNG

* Type “nand erase.chip” and hit Enter.

.. image:: https://github.com/openxc/openxc-accessories/blob/master/docs/pictures/Figure%20B.PNG

* Type “reset” and hit Enter.

.. image:: https://github.com/openxc/openxc-accessories/blob/master/docs/pictures/Figure%20C.PNG

* The Device Manager should have registered a new device under Ports (COM & LPT) named “AT91 USB to Serial Converter”.

    * Install or update provided driver “atm6124_cdc_signed.zip” if device did not register or install correctly.

.. TODO double check the file name and location

.. image:: https://github.com/openxc/openxc-accessories/blob/master/docs/pictures/Figure%20D.PNG

* Install executable file “sam-ba_2.15.exe”.

.. TODO double check the file name and location

* Extract KERNEL file.

    * For the V2X device, download “sama5d3_xplained-v2.1_V2X_011316.zip” to Desktop.
    
    * For the Modem device, download “sama5d3_xplained-v2.0_TEST_2_Modem.zip” to Desktop.
    
* Run “demo_linux_nandflash.bat” from extracted folder above. 

    * Select “Run” on any warning popups.
    
.. TODO double check the file name and location
    
* Power V2X device Off then back On after the Kernel finishes flashing to nandflash.

    * Terminal 1 will stop scrolling and Terminal 2 will automatically close. 
    
.. image:: https://github.com/openxc/openxc-accessories/blob/master/docs/pictures/Figure%20E.PNG

Congratulations, you have successfully upgraded the V2X kernel.

