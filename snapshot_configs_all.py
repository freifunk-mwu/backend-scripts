#!/usr/bin/env python3

def snapshot_configs():
    from os import path
    from photon.util.locations import change_location
    from photon.util.files import write_file
    from common import pinit

    photon, settings = pinit('snapshot_configs', verbose=True)

    git = photon.git_handler(
        settings['configs']['local'],
        remote_url=settings['configs']['remote']
    )
    git.cleanup

    if not photon.settings.load('queue', settings['configs']['queue']):
        photon.m(
            'could not load snapshot queue from git',
            more=dict(
                queue=settings['configs']['queue']
            ),
            state=True
        )
    photon.s2m

    change_location(settings['configs']['target'], False, move=True)

    for loc in settings['queue'].get('locations') + settings['configs']['qadd']:
        change_location(loc, path.join(settings['configs']['target'], loc.lstrip('/')))

    crontab = photon.m(
        'retrieving crontab contents',
        cmdd=dict(
            cmd='crontab -l'
        ),
        critical=False
    )
    if crontab.get('returncode') == 0:
        write_file(path.join(settings['configs']['target'], 'crontab'), crontab.get('out'))

    git.publish

if __name__ == '__main__':
    snapshot_configs()
