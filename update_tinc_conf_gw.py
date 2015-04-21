#!/usr/bin/env python3

def update_tinc_conf():
    from os import listdir, path
    from photon.util.files import read_file
    from common import pinit

    photon, settings = pinit('update_tinc_conf', verbose=True)

    photon.git_handler(settings['icvpn']['tinc']['local'], remote_url=settings['icvpn']['tinc']['remote'])._pull()

if __name__ == '__main__':
    update_tinc_conf()
