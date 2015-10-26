#!/usr/bin/env python3
'''
This script should be run (once) in the beginning, so that the other scripts
can work.

Repo-Access-Syntax: ``ssh://github_mwu/freifunk-mwu/backend-scripts.git``
'''
from photon.util.files import read_file, write_file
from photon.util.locations import search_location

from common import pinit

DESC = 'Make sure this key is associated with the "freifunkmwu" user on github'
SSH_TPL = '''\n
# freifunk-mwu github access
## ${desc}
Host ${gh_ident}
\tUser git
\tHostname github.com
\tPreferredAuthentications publickey
\tIdentityFile ~/.ssh/${prv_s}
\n'''


def bootstrap_git():
    '''
    Creates an ssh-keypair (*hostname_rsa*, *hostname_rsa.pub*) and
    adds them for unified access to GitHub into the ``~/.ssh/config``.

    Do not forget to add the generated key to the GitHub-User
    `ffmwu <https://github.com/freifunkmwu>`_.
    It is member of the group
    `machines <https://github.com/orgs/freifunk-mwu/teams/machines>`_,
    and thus has access to all needed reposotories.
    '''
    photon, settings = pinit('bootstrap_git', verbose=True)

    def mkprv_ssh():
        return photon.m(
            'generating new private ssh keypair',
            cmdd=dict(
                cmd='ssh-keygen -t rsa -b 4096 -N "" -f %s' % (
                    settings['crypt']['ssh']['prv']
                ),
                cwd=settings['crypt']['ssh']['folder'], verbose=True
            )
        )

    def getpub_ssh():
        if not search_location(settings['crypt']['ssh']['prv']):
            mkprv_ssh()

        pub = photon.m(
            'generating new public ssh key from private',
            cmdd=dict(
                cmd='ssh-keygen -f %s -y' % (settings['crypt']['ssh']['prv']),
                cwd=settings['crypt']['ssh']['folder']
            )
        )
        if not pub.get('returncode') == 0:
            photon.m('Error creating public ssh key', state=False)

        if read_file(settings['crypt']['ssh']['pub']) != pub.get('out'):
            write_file(settings['crypt']['ssh']['pub'], pub.get('out'))
            photon.m('wrote public ssh key', more=pub)

        return pub.get('out')

    pub = getpub_ssh()
    if not pub:
        photon.m('Can not bootstrap git configuration', state=True)

    # add entry to config
    conf_t = photon.template_handler(SSH_TPL)
    conf_t.sub = dict(
        desc=DESC,
        gh_ident=settings['common']['gh_ident'],
        prv_s=settings['crypt']['ssh']['prv_s']
    )
    conf_t.write(settings['crypt']['ssh']['conf'])

    photon.m(
        'setting git user.name',
        cmdd=dict(
            cmd='git config --global --replace-all user.name "%s"' % (
                settings['common']['hostname']
            )
        )
    )
    photon.m(
        'setting git user.email',
        cmdd=dict(
            cmd='git config --global --replace-all user.email "%s@%s"' % (
                settings['common']['hostname'],
                settings['common']['domain']
            )
        )
    )

    # display public-key on shell
    shell_t = photon.template_handler(
        '${br}${desc}${br}\n${pub} ${local}\n${br}',
        fields=dict(
            desc=DESC,
            pub=pub,
            local=settings['common']['mailto']['local'],
            br='\n%s\n' % ('~'*8)
        )
    )
    photon.m(shell_t.sub, verbose=True)


if __name__ == '__main__':
    bootstrap_git()
