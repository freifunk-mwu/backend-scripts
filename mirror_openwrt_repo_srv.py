#!/usr/bin/env python3

def mirror_openwrt_repo():
    from photon.util.files import read_file
    from common import pinit

    photon, settings = pinit('mirror_openwrt_repo', verbose=True)

    config_content=photon.m(
        'mirror openwrt repo dir %s%s' %(settings['openwrt']['remote_repo_url'], settings['openwrt']['bb_stable_dir']),
        cmdd=dict(
            cmd='lftp %s -e "mirror --delete %s %s"' %(settings['openwrt']['remote_repo_url'], settings['openwrt']['bb_stable_dir'], settings['openwrt']['local_repo_dir']),
        )
    ).get('out')

if __name__ == '__main__':
    mirror_openwrt_repo()
