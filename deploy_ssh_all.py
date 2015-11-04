#!/usr/bin/env python3
'''
Don't lock yourself out of your machine!

Please open a **second** ssh connection **before** running this script,
and check the results twice.
'''
from argparse import ArgumentParser

from common import pinit


def deploy_ssh():
    '''
    Adds keys into the ``~/.ssh/authorized_keys`` which are not already there.

    The Keys are read from the ``ssh.yaml`` inside the
    `gateway-configs <https://github.com/freifunk-mwu/gateway-configs>`_
    repository.
    '''
    parser = ArgumentParser(prog='deploy_ssh')
    photon, settings = pinit('deploy_ssh', verbose=True)

    # initialize the gateway-configs repo ...
    photon.git_handler(
        settings['configs']['local'],
        remote_url=settings['configs']['remote']
    )._update()

    # .. to load contents from the ssh.yaml into the settings
    if not photon.settings.load(
        'ssh_deploy', settings['configs']['ssh_deploy']
    ):
        photon.m(
            'could not load ssh_deploy',
            more=dict(ssh_deploy=settings['configs']['ssh_deploy']),
            state=True
        )
    photon.s2m

    parser.add_argument(
        'mtype',
        action='store',
        choices=settings['ssh_deploy'].keys()
    )
    args = parser.parse_args()

    for key in settings['ssh_deploy'][args.mtype]:
        conf_t = photon.template_handler(
            '%s\n' % (settings['ssh_deploy'][args.mtype][key])
        )
        conf_t.write(settings['crypt']['ssh']['authorized'])


if __name__ == '__main__':
    deploy_ssh()
