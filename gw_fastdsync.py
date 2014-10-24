
from photon import Photon

if __name__ == '__main__':

    p = Photon(config='ffmwu_config.yaml', summary='ffmwu_summary.yaml', meta='fastdsync_meta.json', verbose=False)
    s = p.settings.get

    for community in s['common']['communities']:
        git = p.git_handler(s['fastd'][community]['local'], remote_url=s['fastd'][community]['remote'])
        git.cleanup

        fastd = p.signal_handler(s['fastd']['community']['pidfile'])
        fastd.hup

        git.publish
