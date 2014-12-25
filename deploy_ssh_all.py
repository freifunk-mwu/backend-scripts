#!/usr/bin/env python3

if __name__ == '__main__':
    from common import pinit
    from argparse import ArgumentParser

    argp = ArgumentParser(prog='deploy_ssh')
    photon, settings = pinit('deploy_ssh', verbose=True)

    photon.git_handler(settings['configs']['local'], remote_url=settings['configs']['remote'])
    if not photon.settings.load('ssh_deploy', settings['configs']['ssh_deploy']):
        photon.m('could not load ssh_deploy', more=dict(ssh_deploy=settings['configs']['ssh_deploy']), state=True)
    photon.s2m

    argp.add_argument('mtype', action='store', choices=settings['ssh_deploy'].keys())
    argp = argp.parse_args()

    for key in settings['ssh_deploy'][argp.mtype]:
        ct = photon.template_handler('%s\n' %(settings['ssh_deploy'][argp.mtype][key]))
        ct.write(settings['crypt']['ssh']['authorized'])
