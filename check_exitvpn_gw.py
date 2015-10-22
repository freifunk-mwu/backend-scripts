#!/usr/bin/env python3

from common import pinit


def check_exitvpn():
    '''
    Sets the ``BATMAN`` Server Flag and starts/stops ``isc-dhcp-server``,
    if some given Hosts can be reached through the `ExitVPN`.
    '''
    photon, settings = pinit('check_exitvpn', verbose=True)

    uping = photon.ping_handler(net_if=settings['exitping']['interface'])
    aping = photon.ping_handler(net_if=settings['exitping']['interface'])

    uping.probe = settings['exitping']['urls']
    aping.probe = settings['exitping']['addresses']

    photon.m(
        'ping results',
        more=dict(
            ping_urls=uping.status,
            ping_addresses=aping.status
        )
    )

    for community in settings['common']['communities']:
        cif = settings['batman'][community]['interface']
        cbw = settings['batman'][community]['bandwidth']
        urat = uping.status['ratio'] <= settings['exitping']['min_ratio']
        arat = aping.status['ratio'] <= settings['exitping']['min_ratio']

        if urat or arat:
            photon.m(
                'exitvpn for %s - it seems you are not properly connected!' % (
                    community
                )
            )
            photon.m(
                'removing batman server flag for %s' % (cif),
                cmdd=dict(
                    cmd='sudo batctl -m %s gw off' % (cif)
                )
            )
            photon.m(
                'stopping isc-dhcp-server',
                cmdd=dict(
                    cmd='sudo initctl stop isc-dhcp-server'
                )
            )

        else:
            photon.m('exitvpn for %s - you are connected!!' % (community))
            photon.m(
                'setting batman server flag for %s (bw: %s)' % (cif, cbw),
                cmdd=dict(
                    cmd='sudo batctl -m %s gw server %s' % (cif, cbw)
                ),
            )
            photon.m(
                'starting isc-dhcp-server',
                cmdd=dict(
                    cmd='sudo initctl start isc-dhcp-server'
                ),
                critical=False
            )


if __name__ == '__main__':
    check_exitvpn()
