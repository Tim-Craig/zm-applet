#`zm-applet`

**A Zoneminder viewer for Raspberrypi with Adafruit PiTFT display  ** ![License](http://img.shields.io/badge/License-GNU%20GPL%20v3-blue.svg)

#Video Demo
https://youtu.be/njlV0YKWJrI

#Installation

##Modify your Zoneminder box
* Apply this change: https://github.com/Tim-Craig/ZoneMinder/commit/d58480c589635702a8769a90838bb63f08b3e04e#diff-79f9437c5d1904783735af628f1e3437R258
    * In the future I'm going to adapt zm-applet to use the new rest API that was recently added to Zoneminder so we don't have to do this step

##Setup your RaspberryPi+PiTFT with Raspbian

* Follow instructions on this link `https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi`
    * Be sure to enable the X server at startup
* We need the lxml library for python `sudo apt-get install python-lxml`

##Install zm-applet

* Clone the repo.
* In the repo, copy the file zm_applet.cfg as a hidden file in the root folder `sudo cp zm_applet.cfg /root/.zm_applet.cfg`
* Change the SERVER_HOST,SERVER_PORT,ZM_WEB_PATH items in the .zm_applet.cfg file to point to your Zoneminder server

##Setup Raspbian to start zm-applet

* Have the Raspbian set to boot to the desktop via raspi-config.
* We now want to set Raspbian to boot to zm-applet instead of the full desktop (this saves CPU and memory usage)
* Create the file /home/pi/.xinitrc with the follow line
    * `@exec sudo XAUTHORITY=$HOME/.Xauthority python /<path you cloned this repository in>/zm_applet.py`
        * We are running as root because it's the only way to access the GPIO ports, if you are not going to use the GPIO ports you can run this as a normal user instead.
