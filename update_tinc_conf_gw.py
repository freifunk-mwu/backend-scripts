#!/usr/bin/env python3

def update_tinc_conf():
    from os import listdir, path
    from photon.util.files import read_file
    from common import pinit

    photon, settings = pinit('update_tinc_conf', verbose=True)

    photon.git_handler(settings['icvpn']['tinc']['local'], remote_url=settings['icvpn']['tinc']['remote'])._pull()

    hostname = settings['common']['hostname']
    iam = settings['icvpn']['tinc']['iamdb'][hostname] if hostname in settings['icvpn']['tinc']['iamdb'] else None
    if not iam:
        photon.m(
            'Host not present in configuration!',
            more=dict(
                host=settings['common']['hostname']
            ),
            state=True
        )

    connects = set()

    for key in listdir(settings['icvpn']['tinc']['hosts']):
        if key.lower() != iam.lower():
            for line in read_file(path.join(settings['icvpn']['tinc']['hosts'], key)).split('\n'):
                if line.lower().startswith('address'):
                    connects.add('ConnectTo = %s' %(key))

    tinc_conf = photon.template_handler(
        path.join(path.dirname(__file__), 'common', 'tinc.conf.tpl'),
        fields=dict(
            iam=iam,
            interface=settings['icvpn']['interface'],
            connects='\n'.join(sorted(connects))
        )
    )

    if tinc_conf.sub != read_file(settings['icvpn']['tinc']['conf']):
        tinc_conf.write(settings['icvpn']['tinc']['conf'], append=False)

        photon.m(
            'restarting tinc daemon',
            cmdd=dict(
                cmd='sudo service %s restart' %(settings['icvpn']['tinc']['exec'])
            )
        )

if __name__ == '__main__':
    update_tinc_conf()
