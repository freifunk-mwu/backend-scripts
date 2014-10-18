
from photon import Photon
from photon.util.files import read_file

if __name__ == '__main__':

    p = Photon(config='ffmwu_config.yaml', summary='ffmwu_summary.yaml', meta='fastdsync_meta.json', verbose=False)
    s = p.settings.get

    for community in s['common']['communities']:
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
