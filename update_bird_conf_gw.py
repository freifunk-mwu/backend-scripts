#!/usr/bin/env python3

def update_bird_conf():
    from photon.util.files import read_file
    from photon.util.locations import backup_location
    from common import pinit

    p, s = pinit('update_bird_conf', verbose=True)

    for r in ['scripts', 'meta']:
        p.git_handler(s['icvpn']['bird'][r]['local'], remote_url=s['icvpn']['bird'][r]['remote'])._pull()

    for v in s['icvpn']['bird']['ip_ver']:

        bc = p.template_handler('${conf}')

        bc.sub = dict(conf=p.m(
            'genarating v%s bgp conf' %(v),
            cmdd=dict(cmd='./mkbgp -f bird -%s -s %s -x mainz -x wiesbaden -d ebgp_inc' %(v, s['icvpn']['bird']['meta']), cwd=s['icvpn']['bird']['scripts']['local'])
        ).get('out'))

        conf = s['icvpn']['bird']['ip_ver'][v]['conf']
        if bc.sub != read_file(conf):
            backup_location(conf, s['icvpn']['bird']['backups'])
            bc.write(conf, append=False)

            p.m(
                'reloading v%s daemon' %(v),
                cmdd=dict(cmd='sudo service %s reload' %(s['icvpn']['bird']['ip_ver'][v]['exec']))
            )

if __name__ == '__main__':
    update_bird_conf()
