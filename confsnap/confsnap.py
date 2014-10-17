
from os import path
from photon import Photon
from photon.util.locations import change_location

if __name__ == '__main__':

    p = Photon(config='confsnap_config.yaml', summary='confsnap_summary.yaml', meta='confsnap_meta.json', verbose=False)
    s = p.settings.get

    git = p.new_git(s['aww_snap']['local'], remote_url=s['aww_snap']['remote'])

    if p.settings.load('queue', s['aww_snap']['queue']):

        for loc in s['queue']['locations']: change_location(loc, path.join(s['aww_snap']['target'], loc.lstrip('/')))

        git.publish
