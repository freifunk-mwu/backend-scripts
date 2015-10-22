#!/usr/bin/env python3

from os import path

from photon.util.locations import change_location, search_location

from common import pinit


def gen_documentation():
    '''
    Pulls updates from our repositories containing (Sphinx) documentation,
    builds them, and on success copies over the generated files.

    You may or may not see the results on
    `rtfm.freifunk-mwu.de <http://rtfm.freifunk-mwu.de>`_,
    the mirrored repos are currently:

        :gluon_builder: https://github.com/freifunk-mwu/gluon-builder-ffmwu
        :gluon_gateway: https://github.com/freifunk-mwu/technik-meta
        :photon: https://github.com/spookey/photon

    '''
    photon, settings = pinit('gen_documentation', verbose=True)
    result = {
        'build': {},
        'result': {},
        'update': {}
    }

    lroot = search_location(
        settings['documentation']['local'],
        create_in=settings['documentation']['local']
    )

    for name, data in settings['documentation']['repositories'].items():
        local = path.join(lroot, name)
        builddir = path.join(settings['documentation']['builddir'], name)
        outdir = path.join(settings['documentation']['output'], name)

        result['update'][name] = photon.git_handler(
            local,
            remote_url=data['remote']
        )._pull()

        build = photon.m(
            'building documentation for %s' % (name),
            cmdd=dict(
                cmd='sphinx-build -a -b html %s %s' % (
                    path.join(local, data['docpath']),
                    builddir
                )
            ),
            critical=False
        )
        result['build'][name] = build
        if build.get('returncode') == 0:
            change_location(outdir, False, move=True)
            change_location(builddir, outdir, move=True)
            result['result'] = photon.m('build for %s successful')

    photon.m('all done', more=result)


if __name__ == '__main__':
    gen_documentation()
