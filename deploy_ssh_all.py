#!/usr/bin/env python3

if __name__ == '__main__':
    from common import pinit
    from argparse import ArgumentParser

    a = ArgumentParser(prog='deploy_ssh')
    p, s = pinit('deploy_ssh', verbose=True)

    p.git_handler(s['configs']['local'], remote_url=s['configs']['remote'])
    if not p.settings.load('ssh_deploy', s['configs']['ssh_deploy']):
        p.m('could not load ssh_deploy', more=dict(ssh_deploy=s['configs']['ssh_deploy']), state=True)
    p.s2m

    a.add_argument('mtype', action='store', choices=s['ssh_deploy'].keys() - ['keys'])
    a = a.parse_args()

    for key in s['ssh_deploy'][a.mtype]:
        ct = p.template_handler('%s\n' %(key))
        ct.write(s['crypt']['ssh']['authorized'])
