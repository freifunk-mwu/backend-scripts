#!/bin/bash

SCRIPTPATH=$(dirname "$(readlink -f "$0")" )

# source configuration
. "$SCRIPTPATH/icvpn_config"

update_bind() (
	$ICVPN_SCRIPTS/mkdns -f bind -s $ICVPN_META -x mwu > $BIND_CONFIG
	sudo named-checkconf
	sudo rndc reload
)


set -e

# icvpn-meta
cd $ICVPN_META
git remote update >/dev/null
git pull origin master

# update bind
update_bind

