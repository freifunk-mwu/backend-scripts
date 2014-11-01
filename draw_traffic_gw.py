#!/usr/bin/env python3

def draw_traffic():
    from os import path
    from common import pinit
    from photon.util.locations import search_location
    from photon.util.system import get_timestamp

    p, s = pinit('draw_traffic', verbose=True)

    search_location(s['traffic']['output'], create_in=s['traffic']['output'])
    res = ''

    for i in s['traffic']['interfaces'] + [s['fastd'][c]['interface'] for c in s['fastd'].keys()]:
        if not search_location(path.join(s['traffic']['dbdir'], i)):
            p.m(
                'creating vnstat db for %s' %(i),
                cmdd=dict(cmd='sudo vnstat -u -i %s' %(i)),
                verbose=True
            )

        r = ''

        for flag, itype in s['traffic']['types']:
            image = '%s-%s.png' %(i, itype)
            p.m(
                'drawing %s graph for %s' %(itype, i),
                cmdd=dict(cmd='vnstati -i %s -%s -o %s' %(i, flag, path.join(s['traffic']['output'], image)))
            )

            ii = p.template_handler(
                '''
            <img src="${image}" alt="${interface} - ${itype}" /><br />
''', fields=dict(interface=i, itype=itype, image=image)
            )
            r += ii.sub

        ib = p.template_handler(
            '''
    <div class="ifblock" onclick="toggle('${interface}')">
        <h2>${interface}</h2>
        <div class="ifimg" id="${interface}">
            ${images}
        </div>
    </div>
''', fields=dict(interface=i, images=r)
        )
        res += ib.sub

    traffic = p.template_handler(
        path.join(path.dirname(__file__), 'common/traffic.tpl'),
        fields=dict(
            hostname=s['common']['hostname'],
            timestamp=get_timestamp(),
            traffic=res
        )
    )
    traffic.write(s['traffic']['index'], append=False)


if __name__ == '__main__':
    draw_traffic()
