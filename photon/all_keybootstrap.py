
from photon import Photon
from photon.util.locations import search_location
from photon.util.files import write_file

if __name__ == '__main__':

    p = Photon(config='ffmwu_config.yaml', summary='ffmwu_summary.yaml', meta='keybootstrap_meta.json', verbose=False)
    s = p.settings.get

    from pprint import pprint
    pprint(s)

    if not search_location(s['common']['ssh']['prv']): p.m(
        'generating new private ssh keypair',
        cmdd=dict(cmd='ssh-keygen -t rsa -b 4096 -N "" -f %s' %(s['common']['ssh']['prv']), cwd=s['common']['ssh']['folder']),
        verbose=True
    )
    if not search_location(s['common']['ssh']['pub']):
        pub = p.m(
            'generating new public ssh key from private',
            cmdd=dict(cmd='ssh-keygen -f %s -y' %(s['common']['ssh']['prv']), cwd=s['common']['ssh']['folder']),
            verbose=True
        )
        if pub.get('returncode') == 0:
            write_file(s['common']['ssh']['pub'], pub.get('out'))
