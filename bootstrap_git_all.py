#!/usr/bin/env python3

from common import pinit

p, s = pinit('bootstrap_git', verbose=True)

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
    return p.m(
        'generating new private ssh keypair',
        cmdd=dict(cmd='ssh-keygen -t rsa -b 4096 -N "" -f %s' %(s['crypt']['ssh']['prv']), cwd=s['crypt']['ssh']['folder'], verbose=True),
    )

def getpub_ssh():
    from photon.util.locations import search_location
    from photon.util.files import write_file, read_file

    if not search_location(s['crypt']['ssh']['prv']): mkprv_ssh()

    pub = p.m(
        'generating new public ssh key from private',
        cmdd=dict(cmd='ssh-keygen -f %s -y' %(s['crypt']['ssh']['prv']), cwd=s['crypt']['ssh']['folder'])
    )
    if not pub.get('returncode') == 0: p.m('Error creating public ssh key', state=False)

    if read_file(s['crypt']['ssh']['pub']) != pub.get('out'):
        write_file(s['crypt']['ssh']['pub'], pub.get('out'))
        p.m('wrote public ssh key', more=pub)

    return pub.get('out')

def bootstrap_git():

    pub = getpub_ssh()
    if not pub: p.m('Can not bootstrap', state=True)

    ct = p.template_handler(SSH_TPL)
    ct.sub = dict(
        desc=DESC,
        gh_ident=s['common']['gh_ident'],
        prv_s=s['crypt']['ssh']['prv_s']
    )
    ct.write(s['crypt']['ssh']['conf'])

    p.m('setting git user.name', cmdd=dict(cmd='git config --global --replace-all user.name "%s"' %(s['common']['hostname'])))
    p.m('setting git user.email', cmdd=dict(cmd='git config --global --replace-all user.email "%s@%s"' %(s['common']['hostname'], s['common']['domain'])))

    pt = p.template_handler('${l}${desc}${l}\n${pub} ${local}\n${l}', fields=dict(desc=DESC, pub=pub, local=s['common']['mailto']['local'], l='\n%s\n' %('~'*8)))
    p.m(pt.sub, verbose=True)

if __name__ == '__main__':
    bootstrap_git()
