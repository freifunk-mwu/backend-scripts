#!/bin/bash

/usr/bin/rsync -avh --delete rsync://downloads.openwrt.org/downloads/releases/packages-17.01 /var/www/opkg_mirror/releases/
/usr/bin/rsync -avh --delete rsync://downloads.openwrt.org/downloads/releases/packages-18.06 /var/www/opkg_mirror/releases/

