#!/usr/bin/env python3

from datetime import datetime, timedelta

from common import pinit


def nagg_exitvpn_accouts():
    '''
    Runs through a list of VPN-accounts inside the
    `gateway configs <https://github.com/freifunk-mwu/gateway-configs.git>`_,
    and sends mails.

    Either as weekly digest, or as daily reminder, a week before a VPN-account
    is running out.
    '''
    photon, settings = pinit('nagg_exitvpn_accouts', verbose=True)

    # initialize the gateway-configs repo ...
    photon.git_handler(
        settings['configs']['local'],
        remote_url=settings['configs']['remote']
    )._update()

    # .. to load contents from the exitvpn.yaml into the settings
    if not photon.settings.load('exitvpn', settings['configs']['exitvpn']):
        photon.m(
            'could not load exitvpn from git',
            more=dict(
                exitvpn=settings['configs']['exitvpn']
            ),
            state=True
        )
    photon.s2m

    res = dict(overdue=list(), warning=list(), good=list())
    now = datetime.now()
    warndays = settings['exitvpn']['conf']['warndays']
    digestday = settings['exitvpn']['conf']['digestday']

    for gateway in sorted(settings['exitvpn']['gateways'].keys()):
        if settings['exitvpn']['gateways'][gateway].get('until'):
            until = datetime.strptime(
                settings['exitvpn']['gateways'][gateway]['until'],
                settings['exitvpn']['conf']['date_format']
            )
            delta = until - now
            flag = 'good'
            if delta <= timedelta(days=0):
                flag = 'overdue'
            elif delta <= timedelta(days=warndays):
                flag = 'warning'
            res[flag].append({
                gateway: settings['exitvpn']['gateways'][gateway]
            })

    photon.m('results', more=res)

    if now.weekday() == digestday or res['warning']:

        punchline = 'VPN Wochenbericht'
        if res['warning']:
            punchline = 'Achtung! VPN Account läuft aus'

        mail = photon.mail_handler(
            to=settings['common']['mailto']['admin'],
            cc=[
                settings['common']['mailto']['kontakt_mz'],
                settings['common']['mailto']['kontakt_wi']
            ],
            sender=settings['common']['mailto']['local'],
            subject='photon exitVPN notify',
            punchline=punchline,
            add_settings=False
        )
        mail.text = ''
        mail.text = res
        mail.text = 'Do not forget to update the exitvpn.yaml ' \
                    '( https://github.com/freifunk-mwu/gateway-configs.git )'
        mail.text = ''
        mail.send


if __name__ == '__main__':
    nagg_exitvpn_accouts()
