#!/usr/bin/env python3

from common import pinit


def check_bind():
    photon, settings = pinit('check_bind', verbose=True)

    status = photon.m(
        'testing for bind9',
        cmdd=dict(
            cmd='sudo rndc status',
        ),
        critical=False
    )

    if status.get('returncode') != 0:
        photon.m(
            '(re) starting bind9',
            cmdd=dict(
                cmd='sudo service bind9 start'
            ),
            critical=False
        )
    else:
        photon.m('bind9 is running')


if __name__ == '__main__':
    check_bind()
