#!/usr/bin/env python3

def check_exitvpn():
    from common import pinit

    photon, settings = pinit('check_exitvpn', verbose=True)

    uping, aping = photon.ping_handler(net_if=settings['exitping']['interface']), photon.ping_handler(net_if=settings['exitping']['interface'])
    uping.probe, aping.probe = settings['exitping']['urls'], settings['exitping']['addresses']

    photon.m('ping results', more=dict(ping_urls=uping.status, ping_addresses=aping.status))

    for community in settings['common']['communities']:
        cif, cbw = settings['batman'][community]['interface'], settings['batman'][community]['bandwidth']

        if uping.status['ratio'] <= settings['exitping']['min_ratio'] or aping.status['ratio'] <= settings['exitping']['min_ratio']:

            photon.m('%s - it seems you are not properly connected!' %(community))
            photon.m(
                'removing batman server flag for %s' %(cif),
                cmdd=dict(cmd='sudo batctl -m %s gw off' %(cif)),
            )
            photon.m(
                'stopping isc-dhcp-server',
                cmdd=dict(cmd='sudo initctl stop isc-dhcp-server'),
            )
        else:

            photon.m('%s - you are connected!!' %(community))
            photon.m(
                'setting batman server flag for %s (bw: %s)' %(cif, cbw),
                cmdd=dict(cmd='sudo batctl -m %s gw server %s' %(cif, cbw)),
            )
            photon.m(
                'starting isc-dhcp-server',
                cmdd=dict(cmd='sudo initctl start isc-dhcp-server'),
                critical=False,
            )

if __name__ == '__main__':
    check_exitvpn()
