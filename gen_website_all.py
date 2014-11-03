#!/usr/bin/env python3

def gen_website():
    from os import path
    from common import pinit
    from common.html import page

    p, s = pinit('gen_website', verbose=True)

    main = '<div class="block"><a href="firmware">Firmware</a></div>'  if path.exists(path.join(s['web']['output'], 'firmware')) else ''
    main += '<div class="block"><a href="traffic">Traffic</a></div>'  if path.exists(path.join(s['web']['output'], 'traffic')) else ''
    main += '<div class="block"><a href="system">System Statistics</a></div>'

    page(p, main)

    sys = '<small>click to show/hide</small>'
    for cmd in s['web']['system']:
        cmdo = p.m('system info', cmdd=dict(cmd=cmd), critical=False).get('out')
        sys += '''
        <div class="block" onclick="toggle('{cmdt}')">
            <h2>{cmd}</h2>
            <div class="cblock" id="{cmdt}">
                {cmdo}
            </div>
        </div>
        '''.format(cmd=cmd, cmdt=cmd.split()[0], cmdo=cmdo.replace(' ', '&nbsp;').replace('\n', '<br />'))

    page(p, sys, sub='system')


if __name__ == '__main__':
    gen_website()
