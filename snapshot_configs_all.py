#!/usr/bin/env python3

from os import path
from photon.util.locations import change_location
from common import pinit

def snapshot_configs():
    p, s = pinit('snapshot_configs', verbose=True)

    git = p.git_handler(s['configs']['local'], remote_url=s['configs']['remote'])

    if p.load('queue', s['configs']['queue']):

        change_location(s['configs']['target'], None, move=True)
        for loc in s['queue'].get('locations'):
            change_location(loc, path.join(s['configs']['target'], loc.lstrip('/')))

        git.publish

if __name__ == '__main__':
    snapshot_configs()
