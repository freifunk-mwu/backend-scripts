#!/usr/bin/env python3

def check_bind9():
    from common import pinit

    photon, settings = pinit('check_bind9', verbose=True)

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
    check_bind9()
