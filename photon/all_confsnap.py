
from os import path
from photon import Photon
from photon.util.locations import change_location

if __name__ == '__main__':

    p = Photon(config='ffmwu_config.yaml', summary='ffmwu_summary.yaml', meta='confsnap_meta.json', verbose=True)
    s = p.settings.get

    git = p.git_handler(s['configs']['local'], remote_url=s['configs']['remote'])

    if p.settings.load('queue', s['configs']['queue']):

        for loc in s['queue'].get('locations'):
            change_location(loc, path.join(s['configs']['target'], loc.lstrip('/')))

        git.publish
