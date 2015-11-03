#!/usr/bin/env python3
'''
You may or may not see it's output on

* `lotuswurzel <http://lotuswurzel.freifunk-mwu.de/traffic>`_
* `aubergine <http://aubergine.freifunk-mwu.de/traffic>`_
* `kaschu <http://kaschu.ffwi.org/traffic>`_ (inside wi mesh)
* `spinat <http://spinat.ffmz.org/traffic>`_ (inside mz mesh)

.. seealso::

    :meth:`common.html.page`
'''
from os import path

from photon.util.locations import search_location

from common import pinit
from common.html import page


IMAGE = '''
<img src="${image}" alt="${interface} - ${itype}" /><br />
'''
IFBLOCK = '''
\t<div class="ifblock" onclick="toggle('${interface}')">
\t\t<h2>${interface}</h2>
\t\t<div class="ifimg" id="${interface}">
\t\t\t${images}
\t\t</div>
\t</div>
'''


def draw_traffic():
    '''
    Draws `vnstat <http://humdi.net/vnstat/>`_  Graphs, and glues them
    into a Webseite.

    Run only on machines which are connected to the mesh (Gateways,
    Service-Machines).

    * If a specified interface does not exist on this machine, it's skipped.
    * If no vnstat database was found for one interface, it will be created.
    '''
    photon, settings = pinit('draw_traffic', verbose=True)

    traffic = '<small>click to show or hide</small><br />'
    avail_if = photon.m(
        'checking for available interfaces',
        cmdd=dict(
            cmd='sudo vnstat --iflist'
        )
    ).get('out', '')

    interfaces = settings['web']['traffic']['interfaces'] + [
        settings['fastd'][com]['interface'] for
        com in settings['common']['communities']
    ]
    for interface in interfaces:
        if interface in avail_if:
            if not search_location(
                path.join(settings['web']['traffic']['dbdir'], interface)
            ):
                photon.m(
                    'creating vnstat db for %s' % (interface),
                    cmdd=dict(
                        cmd='sudo vnstat -u -i %s' % (interface)
                    ),
                    verbose=True
                )

            images = ''
            for flag, itype in settings['web']['traffic']['types']:
                image = '%s-%s.png' % (interface, itype)
                photon.m(
                    'drawing %s graph for %s' % (itype, interface),
                    cmdd=dict(
                        cmd='vnstati -i %s -%s -o %s' % (
                            interface, flag, path.join(
                                settings['web']['output'], 'traffic', image
                            )
                        )
                    ),
                    critical=False
                )

                images += photon.template_handler(
                    IMAGE,
                    fields=dict(
                        interface=interface,
                        itype=itype,
                        image=image
                    )
                ).sub

            traffic += photon.template_handler(
                IFBLOCK,
                fields=dict(
                    interface=interface,
                    images=images
                )
            ).sub

    page(photon, traffic, sub='traffic')


if __name__ == '__main__':
    draw_traffic()
