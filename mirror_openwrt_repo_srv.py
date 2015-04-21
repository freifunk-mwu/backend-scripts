#!/usr/bin/env python3

def mirror_openwrt_repo():
    from os import path
    from photon.util.files import read_file
    from common import pinit

    photon, settings = pinit('mirror_openwrt_repo', verbose=True)

    lftp_conf = path.join(path.dirname(__file__), 'common', settings['openwrt']['lftp_conf'])

    config_content=photon.m(
        'mirror openwrt repo dir %s%s' %(settings['openwrt']['remote_repo_url'], settings['openwrt']['bb_stable_dir']),
        cmdd=dict(
            cmd='lftp -f %s' %(lftp_conf),
            timeout=43200,
        )
    ).get('out')

if __name__ == '__main__':
    mirror_openwrt_repo()
