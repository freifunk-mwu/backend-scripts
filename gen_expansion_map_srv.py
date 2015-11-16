#!/usr/bin/env python3
'''
This script relies on the
`expansion-map <https://github.com/Freifunk-Rhein-Neckar/ffrn-expansion-map>`_

You may or may not see the results for:

    :FFMWU: http://einzugsgebiet.freifunk-mwu.de/
    :FFMZ: http://einzugsgebiet.freifunk-mwu.de/mainz
    :FFWI: http://einzugsgebiet.freifunk-mwu.de/wiesbaden
'''
from os import path
from re import sub as re_sub

from photon.util.files import read_file, write_file
from photon.util.locations import change_location, search_location

from common import pinit


def gen_expansion_map():
    '''
    This script generates several expansion-maps.

    It pulls updates first, generates a map, patches assets, and then
    copies over the generated files.

    A common ``app.chache`` file is used for all builds, for speedup reasons.

    When finished, it leaves the clean repo behind.
    '''
    photon, settings = pinit('gen_expansion_map')

    # fetch updates from remote repository
    git = photon.git_handler(
        settings['expansion']['local'],
        remote_url=settings['expansion']['remote']
    )
    git._pull()

    for name, sub in settings['expansion']['maps'].items():
        # generate map
        build = photon.m(
            'generate %s expansion map' % (name),
            cmdd=dict(
                cmd='./mkpoly -f nodelist %s' % (sub['url']),
                cwd=settings['expansion']['local'],
                timeout=600,  # for initial run, only (to create app.cache)
            )
        )
        if build.get('returncode') == 0:
            for patch in settings['expansion']['patch']:
                content = read_file(patch)
                if not content:
                    # skip empty files
                    continue
                # set title
                content = re_sub(
                    r'<title>(.*?)</title>',
                    '<title>%s</title>' % (sub['title']),
                    content
                )
                # set description
                content = re_sub(
                    r'this._div.innerHTML\ =\ \'<h4>(.*?)</h4>\'',
                    'this._div.innerHTML = \'<h4>%s</h4>\'' % (sub['descr']),
                    content
                )
                # set initial position
                content = re_sub(
                    r'L\.map\(\'map\'\)\.setView\((.*?),\ 10\);',
                    'L.map(\'map\').setView([%s, %s], 10);' % (
                        sub['ipos'][0], sub['ipos'][1]
                    ),
                    content
                )
                # save result
                photon.m('written %d bytes into %s' % (
                    write_file(patch, content),
                    patch
                ))

            # copy generated files & folders
            search_location(sub['output'], create_in=sub['output'])
            for folder in ['js', 'css']:
                change_location(
                    path.join(settings['expansion']['local'], folder),
                    path.join(sub['output'], folder),
                    move=False
                )
            for fdoc in ['nodes.geojson', 'index.html', 'LICENSE']:
                change_location(
                    path.join(settings['expansion']['local'], fdoc),
                    sub['output'],
                    move=False
                )

        # reset changed files
        for reset in settings['expansion']['patch'] + [
            path.join(settings['expansion']['local'], 'nodes.geojson')
        ]:
            photon.m('clean up %s' % (reset))
            git._checkout('-- %s' % (reset))


if __name__ == '__main__':
    gen_expansion_map()
