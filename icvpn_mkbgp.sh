#!/bin/bash

SCRIPTPATH=$(dirname "$(readlink -f "$0")" )

# source configuration
. "$SCRIPTPATH/icvpn_config"

update_roa() (
	$ICVPN_SCRIPTS/mkroa -4 -m 20 -f bird -x $LOCAL_COMMUNITY -s $ICVPN_META > $BIRD4_ROA
	$ICVPN_SCRIPTS/mkroa -6 -m 64 -f bird -x $LOCAL_COMMUNITY -s $ICVPN_META > $BIRD6_ROA
)

update_bgp_peers() (
	if [ -e $BIRD4_PEERS ]; then
		CHECKSUM=$(sha1sum $BIRD4_PEERS)
	else
		CHECKSUM=0
	fi
	$ICVPN_SCRIPTS/mkbgp -4 -f bird -p icvpn_ -s $ICVPN_META -x $LOCAL_COMMUNITY -d $BIRD_BGP_TEMPLATE -P $BIRD_PASSIVE_TIMEOUT > $BIRD4_PEERS
	if [ "$(sha1sum $BIRD4_PEERS)" != "$CHECKSUM" ]; then
		sudo birdc configure check
		sudo birdc configure
	fi
)

update_bgp6_peers() (
	if [ -e $BIRD6_PEERS ]; then
		CHECKSUM=$(sha1sum $BIRD6_PEERS)
	else
		CHECKSUM=0
	fi
	$ICVPN_SCRIPTS/mkbgp -6 -f bird -p icvpn_ -s $ICVPN_META -x $LOCAL_COMMUNITY -d $BIRD_BGP_TEMPLATE -P $BIRD_PASSIVE_TIMEOUT > $BIRD6_PEERS
	if [ "$(sha1sum $BIRD6_PEERS)" != "$CHECKSUM" ]; then
		sudo birdc6 configure check
		sudo birdc6 configure
	fi
)

set -e

# tinc vpn
cd /etc/tinc/$TINC_NETWORK/
git remote update >/dev/null
git pull origin master
# post-merge hook handles configuration update

# icvpn-meta
cd $ICVPN_META
git fetch > /dev/null
git pull origin master
update_roa

# update peers
update_bgp_peers
update_bgp6_peers
