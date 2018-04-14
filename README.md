#`zm-applet`

**A Zoneminder viewer for Raspberrypi with Adafruit PiTFT display  ** ![License](http://img.shields.io/badge/License-GNU%20GPL%20v3-blue.svg)

#Video Demo
https://youtu.be/njlV0YKWJrI

#Installation

##Ensure you Zoneminder service has Groups API support
* ZM Applet now uses the Zoneminder rest API to get monitor and group information.  Groups are new to the ZoneMinder API, it's available in the current master branch but not in the lasted release yet.  
    * You can use this branch of the latest ZoneMinder release with the groups API added:
        * https://github.com/Tim-Craig/ZoneMinder/tree/release-1.30.4-groups_api  
    * Another option is to apply the following changes to your ZoneMinder web folder: 
        * https://github.com/ZoneMinder/zoneminder/pull/2050/commits/0654c7e3b24ded1037394e288a070ff101f040fa

##Setup your RaspberryPi+PiTFT with Raspbian

* Follow instructions on this link `https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi`
    * Be sure to enable the X server at startup

##Install zm-applet

* Clone the repo.
* In the repo, copy the file zm_applet.cfg as a hidden file in the root folder `sudo cp zm_applet.cfg /root/.zm_applet.cfg`
    * If you are not going to run the app as root then copy the file to your home folder instead 
* Change the SERVER_HOST,SERVER_PORT,ZM_WEB_PATH items in the .zm_applet.cfg file to point to your Zoneminder server

##Setup Raspbian to start zm-applet

* Have the Raspbian set to boot to the desktop via raspi-config.
* We now want to set Raspbian to boot to zm-applet instead of the full desktop (this saves CPU and memory usage)
* Create the file /home/pi/.xinitrc with the follow line
    * `@exec sudo XAUTHORITY=$HOME/.Xauthority python /<path you cloned this repository in>/zm_applet.py`
        * We are running as root because it's the only way to access the GPIO ports, if you are not going to use the GPIO ports you can run this as a normal user instead.

#CHANGE LOG
* Version 1.1.0 (03/17/2018):
    * Major refactoring
        * Moved multi-treading work to multi-process
        * Streaming no longer lags behind
    * Moved from old XML skin to Zoneminder API for fetching monitor and group information
* Version 1.1.1 (4/14/2018)
    * Fixed bug were you couldn't change monitors when currently on a non-working monitor
    * Message views will find best fitting font size