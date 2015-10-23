#!/usr/bin/env python3

from common import pinit


def sync_meshkeys():
    photon, settings = pinit('sync_meshkeys', verbose=True)

    for community in settings['common']['communities']:
        git = photon.git_handler(
            settings['fastd'][community]['local'],
            remote_url=settings['fastd'][community]['remote']
        )
        git.cleanup

        # send sighup to fastd to reload configuration (and keys)
        photon.signal_handler(
            settings['fastd'][community]['pidfile'],
            cmdd_if_no_pid=dict(cmd='sudo service fastd start')
        ).hup

        git.publish


if __name__ == '__main__':
    sync_meshkeys()
