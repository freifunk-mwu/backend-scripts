#!/usr/bin/env python3

from photon.util.files import read_file

from common import pinit


def update_bird_conf():
    '''
    Pulls updates from the
    `freifunk icvpn-meta repo <https://github.com/freifunk/icvpn-meta>`_
    and creates with the tools from the
    `freifunk icvpn-scripts repo <https://github.com/freifunk/icvpn-scripts>`_
    a configuration for bird.

    This is done twice, for ``bird`` and ``bird6``.

    Restarts both daemons when the configuration changed.
    '''
    photon, settings = pinit('update_bird_conf', verbose=True)

    for repo in ['scripts', 'meta']:
        photon.git_handler(
            settings['icvpn']['bird'][repo]['local'],
            remote_url=settings['icvpn']['bird'][repo]['remote']
        )._pull()

    for ip_ver in settings['icvpn']['bird']['ip_ver']:
        do_restart = False

        # peers
        bird_peers_conf = photon.template_handler('${peers_config_content}')
        peers_config_content = photon.m(
            'generating ip_ver%s bgp peers conf' % (ip_ver),
            cmdd=dict(
                cmd='./mkbgp -f bird -%s -s %s '
                    '-p icvpn_ -x mainz -x wiesbaden -x bingen -d ebgp_ic' % (
                        ip_ver,
                        settings['icvpn']['bird']['meta']['local']
                    ),
                cwd=settings['icvpn']['bird']['scripts']['local']
            )
        ).get('out')
        bird_peers_conf.sub = dict(peers_config_content=peers_config_content)

        peers_conf = settings['icvpn']['bird']['ip_ver'][ip_ver]['peers_conf']

        if bird_peers_conf.sub != read_file(peers_conf):
            bird_peers_conf.write(peers_conf, append=False)
            do_restart = True

        # roa
        bird_roa_conf = photon.template_handler('${roa_config_content}')
        roa_config_content = photon.m(
            'generating ip_ver%s bgp roa conf' % (ip_ver),
            cmdd=dict(
                cmd='./mkroa -f bird -%s -s %s -m %s -x mainz -x wiesbaden' % (
                    ip_ver,
                    settings['icvpn']['bird']['meta']['local'],
                    settings['icvpn']['bird']['ip_ver'][ip_ver]['roa_maxlen']
                ),
                cwd=settings['icvpn']['bird']['scripts']['local']
            )
        ).get('out')
        bird_roa_conf.sub = dict(roa_config_content=roa_config_content)

        roa_conf = settings['icvpn']['bird']['ip_ver'][ip_ver]['roa_conf']

        if bird_roa_conf.sub != read_file(roa_conf):
            bird_roa_conf.write(roa_conf, append=False)
            do_restart = True

        if do_restart:
            photon.m(
                'restarting bird daemon for v%s' % (ip_ver),
                cmdd=dict(
                    cmd='sudo service %s restart' % (
                        settings['icvpn']['bird']['ip_ver'][ip_ver]['exec']
                    )
                )
            )


if __name__ == '__main__':
    update_bird_conf()
