#!/bin/bash

# stop on any error
set -e

# sites to sync
SITES="mz mzig wi wiig"

# site definitions
mz_REMOTE="https://github.com/freifunk-mwu/peers-ffmwu.git"
mz_LOCAL="/etc/fastd/mzvpn-1406/peers"

mzig_REMOTE="https://github.com/freifunk-mwu/ffmz-infrastructure-peers.git"
mzig_LOCAL="/etc/fastd/mzigvpn-1406/peers"

wi_REMOTE="https://github.com/freifunk-mwu/peers-ffmwu.git"
wi_LOCAL="/etc/fastd/wivpn-1406/peers"

wiig_REMOTE="https://github.com/freifunk-mwu/ffwi-infrastructure-peers.git"
wiig_LOCAL="/etc/fastd/wiigvpn-1406/peers"

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
	if [ -d "/etc/fastd/${SITE}vpn-1406" ]; then
		sudo systemctl reload fastd@${SITE}vpn-1406
	fi
done
