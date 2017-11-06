#!/bin/bash

# stop on any error
set -e

# sites to sync
SITES="bin mz mzig wi wiig"

# site definitions
bin_REMOTE="https://github.com/freifunk-bingen/peers-ffbin.git"
bin_LOCAL="/etc/fastd/mzVPN/peers_bingen"

mz_REMOTE="https://github.com/freifunk-mwu/peers-ffmz.git"
mz_LOCAL="/etc/fastd/mzVPN/peers"

mzig_REMOTE="https://github.com/freifunk-mwu/ffmz-infrastructure-peers.git"
mzig_LOCAL="/etc/fastd/mzigVPN/peers"

wi_REMOTE="https://github.com/freifunk-mwu/peers-ffmz.git"
wi_LOCAL="/etc/fastd/wiVPN/peers"

wiig_REMOTE="https://github.com/freifunk-mwu/ffwi-infrastructure-peers.git"
wiig_LOCAL="/etc/fastd/wiigVPN/peers"

# sync git repositories for all sites
for SITE in ${SITES}; do
	REMOTE="$(eval echo \$${SITE}_REMOTE)"
	LOCAL="$(eval echo \$${SITE}_LOCAL)"
	
	echo --- sync site ${SITE} ---
	
	# create directory if necessary
	mkdir -p ${LOCAL}
	
	GIT="git -C ${LOCAL}"
	
	# check if directory is a git repository
	if ! $(${GIT} rev-parse --git-dir > /dev/null 2>&1) ; then
		git clone "${REMOTE}" "${LOCAL}"
	else
		${GIT} reset --hard origin/HEAD
		${GIT} clean -f -d
		${GIT} pull
	fi
	
	# if site has a matching fastd instance reload it
	if [ -d "/etc/fastd/${SITE}VPN" ]; then
		sudo systemctl reload fastd@${SITE}VPN
	fi
done
