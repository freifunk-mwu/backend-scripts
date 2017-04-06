#!/bin/bash

/usr/bin/rsync -avh --delete rsync://downloads.lede-project.org/downloads/releases/packages-17.01 /var/www/lede_mirror/releases/
/usr/bin/rsync -avh --delete rsync://downloads.lede-project.org/downloads/snapshots/packages /var/www/lede_mirror/snapshots/

