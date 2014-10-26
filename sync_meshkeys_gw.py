
from common.shared import init

if __name__ == '__main__':

    p, s = init('sync_meshkeys', verbose=True)

    for community in s['common']['communities']:
        git = p.git_handler(s['fastd'][community]['local'], remote_url=s['fastd'][community]['remote'])
        git.cleanup

        fastd = p.signal_handler(s['fastd'][community]['pidfile'])
        fastd.hup

        git.publish
