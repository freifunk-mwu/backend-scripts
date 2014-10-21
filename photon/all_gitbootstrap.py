
from photon import Photon
from photon.util.locations import search_location, change_location
from photon.util.files import write_file, read_file

# p = Photon(config='ffmwu_config.yaml', summary='ffmwu_summary.yaml', meta='keybootstrap_meta.json', verbose=False)
p = Photon(config='ffmwu_config.yaml', summary=None                   , meta='keybootstrap_meta.json', verbose=False)
s = p.settings.get

def mk_ssh_prv():
    return p.m(
        'generating new private ssh keypair',
        cmdd=dict(cmd='ssh-keygen -t rsa -b 4096 -N "" -f %s' %(s['crypt']['ssh']['prv']), cwd=s['crypt']['ssh']['folder'], verbose=True),
    )

def get_ssh_pub():
    if not search_location(s['crypt']['ssh']['prv']): mk_ssh_prv()

    pub = p.m(
        'generating new public ssh key from private',
        cmdd=dict(cmd='ssh-keygen -f %s -y' %(s['crypt']['ssh']['prv']), cwd=s['crypt']['ssh']['folder'])
    )
    if pub.get('returncode') == 0:

        if read_file(s['crypt']['ssh']['pub']) != pub.get('out'):
            write_file(s['crypt']['ssh']['pub'], pub.get('out'))
            p.m('wrote public ssh key', more=pub)

        return pub.get('out')

def add_github_to_ssh_config():

    pub = get_ssh_pub()
    if pub:
        conf = read_file(s['crypt']['ssh']['conf'])
        ks = 'Make sure this key is in a github account which has access to required repositories'
        if not 'Host %s' %(s['common']['gh_ident']) in conf:
            conf += '''\n
# freifunk-mwu github access
## {ks}
Host {gh_ident}
\tUser git
\tHostname github.com
\tPreferredAuthentications publickey
\tIdentityFile ~/.ssh/{prv_s}
\n'''.format(ks=ks, gh_ident=s['common']['gh_ident'], prv_s=s['crypt']['ssh']['prv_s'])

            change_location(s['crypt']['ssh']['conf'], s['crypt']['ssh']['conf_b'])
            write_file(s['crypt']['ssh']['conf'], conf)
        else: p.m('skipping config modification - entry already present')
        p.m('%s\n\n%s\n' %(ks, pub), verbose=True)

def set_git_config():
    p.m('setting git user.name', cmdd=dict(cmd='git config --global --replace-all user.name "%s"' %(s['common']['hostname'])))
    p.m('setting git user.email', cmdd=dict(cmd='git config --global --replace-all user.email "%s@%s"' %(s['common']['hostname'], s['common']['domain'])))

if __name__ == '__main__':

    add_github_to_ssh_config()
    set_git_config()
