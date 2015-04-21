#!/usr/bin/env python3

def update_bird_conf():
    from photon.util.files import read_file
    from common import pinit

    photon, settings = pinit('update_bird_conf', verbose=True)

    for repo in ['scripts', 'meta']:
        photon.git_handler(
            settings['icvpn']['bird'][repo]['local'],
            remote_url=settings['icvpn']['bird'][repo]['remote']
        )._pull()

    for ip_ver in settings['icvpn']['bird']['ip_ver']:

        bird_conf = photon.template_handler('${config_content}')
        config_content=photon.m(
            'generating ip_ver%s bgp conf' %(ip_ver),
            cmdd=dict(
                cmd='./mkbgp -f bird -%s -s %s -x mainz -x wiesbaden -d ebgp_ic' %(ip_ver, settings['icvpn']['bird']['meta']['local']),
                cwd=settings['icvpn']['bird']['scripts']['local']
            )
        ).get('out')
        bird_conf.sub = dict(config_content=config_content)

        conf = settings['icvpn']['bird']['ip_ver'][ip_ver]['conf']

        if bird_conf.sub != read_file(conf):
            bird_conf.write(conf, append=False)

            photon.m(
                'restarting bird daemon for v%s' %(ip_ver),
                cmdd=dict(
                    cmd='sudo service %s restart' %(settings['icvpn']['bird']['ip_ver'][ip_ver]['exec'])
                )
            )

if __name__ == '__main__':
    update_bird_conf()
