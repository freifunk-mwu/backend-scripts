#!/usr/bin/env python3

from common import pinit


def check_radvd():
    photon, settings = pinit('check_radvd', verbose=True)

    status = photon.m(
        'testing for radvd',
        cmdd=dict(
            cmd='sudo service radvd status',
        ),
        critical=False
    )

    if status.get('returncode') != 0:
        photon.m(
            '(re) starting radvd',
            cmdd=dict(
                cmd='sudo service radvd start'
            ),
            critical=False
        )
    else:
        photon.m('radvd is running')

if __name__ == '__main__':
    check_radvd()
