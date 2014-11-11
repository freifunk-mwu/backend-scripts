#!/usr/bin/env python3

def draw_traffic():
    from os import path
    from photon.util.locations import search_location
    from common import pinit
    from common.html import page

    p, s = pinit('draw_traffic', verbose=True)

    traffic = ''
    for i in s['web']['traffic']['interfaces'] + [s['fastd'][c]['interface'] for c in s['fastd'].keys()]:
        if not search_location(path.join(s['web']['traffic']['dbdir'], i)):
            p.m(
                'creating vnstat db for %s' %(i),
                cmdd=dict(cmd='sudo vnstat -u -i %s' %(i)),
                verbose=True
            )

        r = ''
        for flag, itype in s['web']['traffic']['types']:
            image = '%s-%s.png' %(i, itype)
            p.m(
                'drawing %s graph for %s' %(itype, i),
                cmdd=dict(cmd='vnstati -i %s -%s -o %s' %(i, flag, path.join(s['web']['output'], 'traffic', image))),
                critical=False
            )

            r += p.template_handler('<img src="${image}" alt="${interface} - ${itype}" /><br />', fields=dict(interface=i, itype=itype, image=image)).sub

        traffic += p.template_handler(
            '''
    <div class="ifblock" onclick="toggle('${interface}')">
        <h2>${interface}</h2>
        <div class="ifimg" id="${interface}">
            ${images}
        </div>
    </div>
''', fields=dict(interface=i, images=r)
        ).sub

    page(p, traffic, sub='traffic')


if __name__ == '__main__':
    draw_traffic()
