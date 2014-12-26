#!/usr/bin/env python3

def gen_website():
    from os import path
    from common import pinit
    from common.html import page

    photon, settings = pinit('gen_website', verbose=True)

    main = '\n<div class="block"><a href="firmware">Firmware</a></div>'  if path.exists(path.join(settings['web']['output'], 'firmware')) else ''
    main += '\n<div class="block"><a href="_archive">Firmware Archive</a></div>'  if path.exists(path.join(settings['web']['output'], '_archive')) else ''
    main += '\n<div class="block"><a href="traffic">Traffic</a></div>'  if path.exists(path.join(settings['web']['output'], 'traffic')) else ''
    main += '\n<div class="block"><a href="system">System Statistics</a></div>'

    page(photon, main)

    sys = '<small>click to show/hide</small>'
    for cmd in settings['web']['system']:
        cmdo = photon.m('system info', cmdd=dict(cmd=cmd), critical=False).get('out')
        sys += '''
        <div class="block" onclick="toggle('{cmdt}')">
            <h2>{cmd}</h2>
            <div class="cblock" id="{cmdt}">
                <pre>{cmdo}</pre>
            </div>
        </div>
        '''.format(cmd=cmd, cmdt=cmd.split()[0], cmdo=cmdo)

    page(photon, sys, sub='system')


if __name__ == '__main__':
    gen_website()
