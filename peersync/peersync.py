
from photon import Photon
from photon.util.files import read_file

if __name__ == '__main__':

    p = Photon(config='peersync_config.yaml', summary='peersync_summary.yaml', meta='peersync_meta.json', verbose=False)
    s = p.settings.get

    for community in s['fastd']:
        git = p.new_git(s['fastd'][community]['local'], remote_url=s['fastd'][community]['remote'])
        git.cleanup

        pid = read_file(s['fastd'][community]['pidfile'])
        if pid:
            p.m(
                '%s - fastd key reload' %(community),
                cmdd=dict(cmd='sudo kill -HUP %s' %(pid.strip())),
                verbose=True
            )

        git.publish
