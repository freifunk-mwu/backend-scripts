#!/usr/bin/env python3
'''
To create configuration for tinc, a template file is used.

**common/tinc.conf.tpl**

.. literalinclude:: ../../common/tinc.conf.tpl
    :language: bash
    :linenos:

'''
from os import path

from photon.util.files import read_file

from common import pinit


def update_tinc_conf():
    '''
    Pulls updates from the
    `freifunk icvpn repo <https://github.com/freifunk/icvpn>`_ and creates
    a config file for ``tinc``.

    It reads in the **metanodes** file and adds only those with an
    address in **hosts/$metanode** as ``ConnectTo = $metanode`` entry.
    '''
    photon, settings = pinit('update_tinc_conf', verbose=True)

    # pull updates from repo
    photon.git_handler(
        settings['icvpn']['tinc']['local'],
        remote_url=settings['icvpn']['tinc']['remote']
    )._pull()

    hostname = settings['common']['hostname']
    iam = settings['icvpn']['tinc']['iamdb'].get(hostname)
    metanodes = read_file(settings['icvpn']['tinc']['metanodes'])

    # exit early on severe errors
    if not all([iam, metanodes]):
        photon.m(
            'Host not present in configuration or empty metanodes file!',
            more=dict(
                host=settings['common']['hostname'],
                metanodes=settings['icvpn']['tinc']['metanodes']
            ),
            state=True
        )

    connects = set()
    for metanode in [m.strip() for m in metanodes.split('\n') if m]:
        if metanode.lower() == iam.lower():
            continue  # skip self

        content = read_file(path.join(
            settings['icvpn']['tinc']['hosts'], metanode
        ))
        if not content:
            continue  # skip empty files

        for line in content.split('\n'):
            if line.lower().startswith('address'):
                connects.add('ConnectTo = %s' % (metanode))

    if not connects:
        photon.m(
            'No hosts collected for connection!',
            more=dict(
                metanodes=settings['icvpn']['tinc']['metanodes']
            ),
            state=True
        )

    # open the tinc.conf.tpl file, fill in the fields
    conf = photon.template_handler(
        settings['icvpn']['tinc']['conf_tpl'],
        fields=dict(
            iam=iam,
            interface=settings['icvpn']['interface'],
            connects='\n'.join(sorted(connects))
        )
    )

    # compare filled template with original tinc config
    # write on change, reload tinc
    if conf.sub != read_file(settings['icvpn']['tinc']['conf']):
        conf.write(settings['icvpn']['tinc']['conf'], append=False)

        photon.m(
            'config changed - reloading tinc daemon',
            cmdd=dict(
                cmd='sudo service tinc reload %s' % (
                    path.basename(settings['icvpn']['tinc']['local'])
                )
            )
        )
    else:
        photon.m('no change in config')


if __name__ == '__main__':
    update_tinc_conf()
