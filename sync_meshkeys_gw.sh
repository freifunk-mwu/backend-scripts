#!/bin/bash

# stop on any error
set -e

# repos to sync
REPOS="mwu mzig wiig"

# repo definitions
mwu_REMOTE="https://github.com/freifunk-mwu/peers-ffmwu.git"
mwu_LOCAL="/home/admin/clones/peers-ffmwu"

mzig_REMOTE="https://github.com/freifunk-mwu/ffmz-infrastructure-peers.git"
mzig_LOCAL="/etc/fastd/mzigvpn-1406/peers"

wiig_REMOTE="https://github.com/freifunk-mwu/ffwi-infrastructure-peers.git"
wiig_LOCAL="/etc/fastd/wiigvpn-1406/peers"

# sync git repositories
for REPO in ${REPOS}; do
	REMOTE="$(eval echo \$${REPO}_REMOTE)"
	LOCAL="$(eval echo \$${REPO}_LOCAL)"

	echo --- sync peers: ${REPO} ---

	# create directory if necessary
	mkdir -p ${LOCAL}

	GIT="git -C ${LOCAL}"

	# check if directory is a git repository
	if ! $(${GIT} rev-parse --git-dir > /dev/null 2>&1) ; then
		git clone "${REMOTE}" "${LOCAL}"
	else
		${GIT} fetch
		${GIT} reset --hard origin/HEAD
	fi
done

KEY_DIR="${mwu_LOCAL}"
KEY_LIST="/etc/fastd/fastd_peers.txt"
KEY_LIST_TMP="/tmp/fastd_peers.tmp"

: > "${KEY_LIST_TMP}"

find "${KEY_DIR}" -type f -not -path '*/\.*' -not -name '*.md' | while read f; do
	egrep -o '[a-z0-9]{64}' "$f" >> "${KEY_LIST_TMP}"
done

sudo mv "${KEY_LIST_TMP}" "${KEY_LIST}"
