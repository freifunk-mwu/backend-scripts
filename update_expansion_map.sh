#!/bin/sh

MAPDIR="/var/www/ffmwu-expansion-map"
NODELIST="http://map.freifunk-mwu.de/data/nodelist.json"

cd $MAPDIR
/usr/bin/python3 $MAPDIR/mkpoly -f nodelist $NODELIST

exit 0
