#!/usr/bin/env python3

from common import pinit

def check_exitvpn():
    p, s = pinit('check_exitvpn', verbose=True)

    uping, aping = p.ping_handler(net_if=s['exitping']['interface']), p.ping_handler(net_if=s['exitping']['interface'])
    uping.probe, aping.probe = s['exitping']['urls'], s['exitping']['addresses']

    p.m('ping results', more=dict(ping_urls=uping.status, ping_addresses=aping.status))

    for community in s['common']['communities']:
        cif, cbw = s['batman'][community]['interface'], s['batman'][community]['bandwidth']

        if uping.status['ratio'] <= s['exitping']['min_ratio'] or aping.status['ratio'] <= s['exitping']['min_ratio']:

            p.m('%s - it seems you are not properly connected!' %(community))
            p.m(
                'removing batman server flag for %s' %(cif),
                cmdd=dict(cmd='sudo batctl -m %s gw off' %(cif)),
            )
            p.m(
                'stopping isc-dhcp-server',
                cmdd=dict(cmd='sudo initctl stop isc-dhcp-server'),
            )
        else:

            p.m('%s - you are connected!!' %(community))
            p.m(
                'setting batman server flag for %s (bw: %s)' %(cif, cbw),
                cmdd=dict(cmd='sudo batctl -m %s gw server %s' %(cif, cbw)),
            )
            p.m(
                'starting isc-dhcp-server',
                cmdd=dict(cmd='sudo initctl start isc-dhcp-server'),
                critical=False,
            )

if __name__ == '__main__':
    check_exitvpn()
