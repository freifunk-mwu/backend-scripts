#!/usr/bin/env python3

from common import pinit


def check_exitvpn():
    '''
    Sets the ``BATMAN`` Server Flag and starts/stops ``isc-dhcp-server``,
    if some given Hosts can be reached through the `ExitVPN`.
    '''
    photon, settings = pinit('check_exitvpn', verbose=True)

    ping = photon.ping_handler(net_if=settings['exitping']['interface'])

    photon.m('sending pings', more=settings['exitping']['targets'])
    ping.probe = settings['exitping']['targets']
    photon.m('ping results', more=ping.status)

    for community in settings['common']['communities']:
        interface = settings['batman'][community]['interface']
        bandwidth = settings['batman'][community]['bandwidth']

        if ping.status['ratio'] <= settings['exitping']['min_ratio']:
            photon.m('exitvpn for %s - you are _not_ connected!' % (community))

            photon.m(
                'removing batman server flag for %s' % (interface),
                cmdd=dict(cmd='sudo batctl -m %s gw off' % (interface))
            )

            if 'start/running' in photon.m(
                'check if isc-dhcp-server is running to stop it',
                cmdd=dict(cmd='initctl status isc-dhcp-server')
            ).get('out', ''):
                photon.m(
                    'stopping isc-dhcp-server',
                    cmdd=dict(cmd='sudo initctl stop isc-dhcp-server')
                )

        else:
            photon.m('exitvpn for %s - you are connected!!' % (community))

            photon.m(
                'setting batman server flag for %s (bw: %s)' % (
                    interface, bandwidth
                ),
                cmdd=dict(cmd='sudo batctl -m %s gw server %s' % (
                    interface, bandwidth
                )),
            )

            if 'stop/waiting' in photon.m(
                'check if isc-dhcp-server is not running to start it',
                cmdd=dict(cmd='initctl status isc-dhcp-server')
            ).get('out', ''):
                photon.m(
                    'starting isc-dhcp-server',
                    cmdd=dict(cmd='sudo initctl start isc-dhcp-server')
                )


if __name__ == '__main__':
    check_exitvpn()
