#!/usr/bin/env python3

def snapshot_configs():
    from os import path
    from photon.util.locations import change_location
    from photon.util.files import write_file
    from common import pinit

    p, s = pinit('snapshot_configs', verbose=True)

    git = p.git_handler(s['configs']['local'], remote_url=s['configs']['remote'])
    git.cleanup

    if p.settings.load('queue', s['configs']['queue']):
        p.s2m

        change_location(s['configs']['target'], False, move=True)

        for loc in s['queue'].get('locations') + s['configs']['qadd']:
            change_location(loc, path.join(s['configs']['target'], loc.lstrip('/')))

        crontab = p.m('getting crontab', cmdd=dict(cmd='crontab -l'), critical=False)
        if crontab.get('returncode') == 0:
            write_file(path.join(s['configs']['target'], 'crontab_-l'), crontab.get('out'))

        git.publish

if __name__ == '__main__':
    snapshot_configs()
