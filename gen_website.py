#!/usr/bin/env python3

def sys_block(p, cmd):
    cmdout = p.m('getting system info', cmdd=dict(cmd=cmd), critical=False).get('out').replace(' ', '&nbsp;').replace('\n', '<br />')
    return '''
    <div class="block" onclick="toggle('{cmdt}')">
        <h2>{cmd}</h2>
        <div class="cblock" id="{cmdt}">
            {cmdout}
        </div>
    </div>
    '''.format(cmd=cmd, cmdt=''.join(cmd.split()), cmdout=cmdout)

def gen_website():
    from os import path
    from common import pinit
    from photon.util.locations import change_location
    from photon.util.system import get_timestamp

    p, s = pinit('gen_website', verbose=True)

    change_location(path.join(path.dirname(__file__), 'common/static'), s['web']['output'])

    firmware = '<div class="block"><a href="firmware">firmware</a></div>'  if path.exists(path.join(s['web']['output'], 'firmware')) else ''
    sys = ''.join([sys_block(p, cmd) for cmd in [
        'uptime',
        'fortune',
        'uname -a',
        'hostname -i',
        'ip address show label "*[BR,VPN]"',
        'lsblk',
        'df -h',
        'free -h',
        'swapon -s',
        'who -H'
    ]])

    index = p.template_handler(
        path.join(path.dirname(__file__), 'common/index.tpl'),
        fields=dict(
            hostname=s['common']['hostname'],
            timestamp=get_timestamp(),
            firmware=firmware,
        )
    )
    index.write(s['web']['index'], append=False)

    system = p.template_handler(
        path.join(path.dirname(__file__), 'common/system.tpl'),
        fields=dict(
            hostname=s['common']['hostname'],
            timestamp=get_timestamp(),
            sys=sys
        )
    )
    system.write(s['web']['system'], append=False)

if __name__ == '__main__':
    gen_website()
