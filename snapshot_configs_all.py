#!/usr/bin/env python3

from os import path

from photon.util.files import write_file
from photon.util.locations import change_location

from common import pinit


def snapshot_configs():
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

    queue = settings['queue'].get('locations') + settings['configs']['qadd']
    for loc in queue:
        change_location(
            loc,
            path.join(settings['configs']['target'], loc.lstrip('/'))
        )

    for b_cmd, b_file in [
        ('crontab -l', 'crontab'),
        ('dpkg -l', 'package_list')
    ]:
        result = photon.m(
            'retrieving %s contents' % (b_cmd),
            cmdd=dict(cmd=b_cmd),
            critical=False
        )
        if result.get('returncode') == 0:
            write_file(
                path.join(settings['configs']['target'], b_file),
                result.get('out')
            )

    git.publish


if __name__ == '__main__':
    snapshot_configs()
