#!/usr/bin/env python3

def update_bind_conf():
    from photon.util.files import read_file
    from common import pinit

    photon, settings = pinit('update_bind_conf', verbose=True)

    for repo in ['scripts', 'meta']:
        photon.git_handler(
            settings['icvpn']['icdns'][repo]['local'],
            remote_url=settings['icvpn']['icdns'][repo]['remote']
        )._pull()

    bind_conf = photon.template_handler('${config_content}')
    config_content=photon.m(
        'genarating bind conf',
        cmdd=dict(
            cmd='./mkdns -f bind -s %s -x mainz -x wiesbaden -x bingen' %(settings['icvpn']['icdns']['meta']['local']),
            cwd=settings['icvpn']['icdns']['scripts']['local']\
        )
    ).get('out')
    bind_conf.sub = dict(config_content=config_content)

    conf = settings['icvpn']['icdns']['conf']
    if bind_conf.sub != read_file(conf):
        bind_conf.write(conf, append=False)

        photon.m(
            'reloading bind daemon',
            cmdd=dict(
                cmd='sudo rndc reload'
            )
        )

if __name__ == '__main__':
    update_bind_conf()
