#!/bin/sh

KEYDIR=${KEYDIR-"/etc/fastd/mzVPN/peers_bingen"}
REMOTE=${REMOTE-"https://github.com/freifunk-bingen/peers-ffbin"}
USERGROUP=${USERGROUP-"admin:admin"}

if [ ! -d "$KEYDIR" ]; then
    sudo mkdir "$KEYDIR"
    sudo chown -R "$USERGROUP" "$KEYDIR"
    git clone "$REMOTE" "$KEYDIR"
else
    git -C "$KEYDIR" pull
fi
