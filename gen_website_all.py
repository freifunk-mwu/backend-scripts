#!/usr/bin/env python3
'''
You may or may not see it's output on

* `lotuswurzel.freifunk-mwu.de <http://lotuswurzel.freifunk-mwu.de/>`_
* `pudding.freifunk-mwu.de <http://pudding.freifunk-mwu.de/>`_
* `kaschu.ffwi.org <http://kaschu.ffwi.org/>`_
* `spinat.ffmz.org <http://spinat.ffmz.org/>`_

.. seealso::

    :meth:`common.html.page`
'''
from os import path

from common import pinit
from common.html import page


BLOCK = '''
\t<div class="block"><a href="{href}">{text}</a></div>
'''
SYSBLOCK = '''
\t<div class="block" onclick="toggle('{command_tag}')">
\t\t<h2>{command}</h2>
\t\t<div class="cblock" id="{command_tag}">
\t\t\t<pre>{cmd_output}</pre>
\t\t</div>
\t</div>
'''


def gen_website():
    '''
    Generates a basic landing page, linking to firmware and/or traffic
    statistics (if any).

    Adds some basic system statistics by running shell commands, putting
    the output into the status page.
    '''
    photon, settings = pinit('gen_website', verbose=True)

    main = ''
    if path.exists(path.join(settings['web']['output'], 'firmware')):
        main += BLOCK.format(href='firmware', text='Firmware')

    if path.exists(path.join(settings['web']['output'], '_archive')):
        main += BLOCK.format(href='_archive', text='Firmware Archive')

    if path.exists(path.join(settings['web']['output'], 'traffic')):
        main += BLOCK.format(href='traffic', text='Traffic')

    main += BLOCK.format(href='system', text='System Statistics')

    page(photon, main)

    sys = '<small>click to show or hide</small><br />'
    for command in settings['web']['system']:
        cmd_output = photon.m(
            'retrieving system info',
            cmdd=dict(cmd=command),
            critical=False
        ).get('out')
        sys += SYSBLOCK.format(
            command=command,
            command_tag=command.split()[0],
            cmd_output=cmd_output
        )

    page(photon, sys, sub='system')


if __name__ == '__main__':
    gen_website()
