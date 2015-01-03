#!/usr/bin/env python3

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
    from os import path
    from photon.util.locations import search_location
    from common import pinit
    from common.html import page

    photon, settings = pinit('draw_traffic', verbose=True)

    traffic = '<small>click to show or hide</small><br />'
    avail_if = photon.m(
        'checking for available interfaces',
        cmdd=dict(
            cmd='sudo vnstat --iflist'
        )
    ).get('out', '')
    interfaces = settings['web']['traffic']['interfaces'] + [settings['fastd'][community]['interface'] for community in settings['fastd'].keys()]
    for interface in interfaces:
        if interface in avail_if:
            if not search_location(path.join(settings['web']['traffic']['dbdir'], interface)):
                photon.m(
                    'creating vnstat db for %s' %(interface),
                    cmdd=dict(
                        cmd='sudo vnstat -u -i %s' %(interface)
                    ),
                    verbose=True
                )

            images = ''
            for flag, itype in settings['web']['traffic']['types']:
                image = '%s-%s.png' %(interface, itype)
                photon.m(
                    'drawing %s graph for %s' %(itype, interface),
                    cmdd=dict(
                        cmd='vnstati -i %s -%s -o %s' %(interface, flag, path.join(settings['web']['output'], 'traffic', image))
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
