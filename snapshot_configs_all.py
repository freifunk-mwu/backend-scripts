
from os import path
from photon.util.locations import change_location
from common.shared import init

if __name__ == '__main__':

    p, s = init('snapshot_configs', verbose=True)

    git = p.git_handler(s['configs']['local'], remote_url=s['configs']['remote'])

    if p.load('queue', s['configs']['queue']):

        change_location(s['configs']['target'], None, move=True)
        for loc in s['queue'].get('locations'):
            change_location(loc, path.join(s['configs']['target'], loc.lstrip('/')))

        git.publish
