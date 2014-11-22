#!/usr/bin/env python3

def update_tinc_conf():
    from os import listdir, path
    from photon.util.files import read_file
    from photon.util.locations import backup_location
    from common import pinit

    p, s = pinit('update_tinc_conf', verbose=True)

    p.git_handler(s['icvpn']['tinc']['local'], remote_url=s['icvpn']['tinc']['remote'])._pull

    iam = s['icvpn']['tinc']['iamdb'][s['common']['hostname']] if s['common']['hostname'] in s['icvpn']['tinc']['iamdb'] else None
    if not iam: p.m('Host not present in configuration!', more=dict(host=s['common']['hostname']), state=True)

    connects = set()

    for key in listdir(s['icvpn']['tinc']['hosts']):
        if key.lower() != iam.lower():
            for line in read_file(path.join(s['icvpn']['tinc']['hosts'], key)).split('\n'):
                if line.startswith('Address'):
                    connects.add('ConnectTo = %s' %(key))

    tc = p.template_handler(
        path.join(path.dirname(__file__), 'common', 'tinc.conf.tpl'),
        fields=dict(
            iam=iam,
            interface=s['icvpn']['interface'],
            connects='\n'.join(sorted(connects))
        )
    )
    if tc.sub != read_file(s['icvpn']['tinc']['conf']):
        backup_location(s['icvpn']['tinc']['conf'], s['icvpn']['tinc']['backups'])
        tc.write(s['icvpn']['tinc']['conf'], append=False)

        tinc = p.signal_handler(s['icvpn']['tinc']['pidfile'])
        tinc.hup

if __name__ == '__main__':
    update_tinc_conf()
