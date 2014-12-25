#!/usr/bin/env python3

from common import pinit

photon, settings = pinit('bootstrap_git', verbose=True)

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

def mkprv_ssh():
    return photon.m(
        'generating new private ssh keypair',
        cmdd=dict(cmd='ssh-keygen -t rsa -b 4096 -N "" -f %s' %(settings['crypt']['ssh']['prv']), cwd=settings['crypt']['ssh']['folder'], verbose=True),
    )

def getpub_ssh():
    from photon.util.locations import search_location
    from photon.util.files import write_file, read_file

    if not search_location(settings['crypt']['ssh']['prv']): mkprv_ssh()

    pub = photon.m(
        'generating new public ssh key from private',
        cmdd=dict(cmd='ssh-keygen -f %s -y' %(settings['crypt']['ssh']['prv']), cwd=settings['crypt']['ssh']['folder'])
    )
    if not pub.get('returncode') == 0: photon.m('Error creating public ssh key', state=False)

    if read_file(settings['crypt']['ssh']['pub']) != pub.get('out'):
        write_file(settings['crypt']['ssh']['pub'], pub.get('out'))
        photon.m('wrote public ssh key', more=pub)

    return pub.get('out')

def bootstrap_git():

    pub = getpub_ssh()
    if not pub: photon.m('Can not bootstrap', state=True)

    ct = photon.template_handler(SSH_TPL)
    ct.sub = dict(
        desc=DESC,
        gh_ident=settings['common']['gh_ident'],
        prv_s=settings['crypt']['ssh']['prv_s']
    )
    ct.write(settings['crypt']['ssh']['conf'])

    photon.m('setting git user.name', cmdd=dict(cmd='git config --global --replace-all user.name "%s"' %(settings['common']['hostname'])))
    photon.m('setting git user.email', cmdd=dict(cmd='git config --global --replace-all user.email "%s@%s"' %(settings['common']['hostname'], settings['common']['domain'])))

    pt = photon.template_handler('${l}${desc}${l}\n${pub} ${local}\n${l}', fields=dict(desc=DESC, pub=pub, local=settings['common']['mailto']['local'], l='\n%s\n' %('~'*8)))
    photon.m(pt.sub, verbose=True)

if __name__ == '__main__':
    bootstrap_git()
