#!/usr/bin/env python3

def draw_traffic():
    from os import path
    from photon.util.locations import search_location
    from common import pinit
    from common.html import page

    photon, settings = pinit('draw_traffic', verbose=True)

    traffic = ''
    for interface in settings['web']['traffic']['interfaces'] + [settings['fastd'][c]['interface'] for c in settings['fastd'].keys()]:
        if not search_location(path.join(settings['web']['traffic']['dbdir'], interface)):
            photon.m(
                'creating vnstat db for %s' %(interface),
                cmdd=dict(cmd='sudo vnstat -u -i %s' %(interface)),
                verbose=True
            )

        images = ''
        for flag, itype in settings['web']['traffic']['types']:
            image = '%s-%s.png' %(interface, itype)
            photon.m(
                'drawing %s graph for %s' %(itype, interface),
                cmdd=dict(cmd='vnstati -i %s -%s -o %s' %(interface, flag, path.join(settings['web']['output'], 'traffic', image))),
                critical=False
            )

            images += photon.template_handler('\n<img src="${image}" alt="${interface} - ${itype}" /><br />', fields=dict(interface=interface, itype=itype, image=image)).sub

        traffic += photon.template_handler('''
    <div class="ifblock" onclick="toggle('${interface}')">
        <h2>${interface}</h2>
        <div class="ifimg" id="${interface}">
            ${images}
        </div>
    </div>
''', fields=dict(interface=interface, images=images) ).sub

    page(photon, traffic, sub='traffic')


if __name__ == '__main__':
    draw_traffic()
