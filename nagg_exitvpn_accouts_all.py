#!/usr/bin/env python3

def nagg_exitvpn_accouts():
    from common import pinit
    from datetime import datetime, timedelta

    p, s = pinit('nagg_exitvpn_accouts', verbose=True)

    p.git_handler(s['configs']['local'], remote_url=s['configs']['remote'])
    if not p.settings.load('exitvpn', s['configs']['exitvpn']):
        p.m('could not load exitvpn from git', more=dict(exitvpn=s['configs']['exitvpn']), state=True)
    p.s2m

    res=dict(overdue=list(), warning=list(), good=list())
    now = datetime.now()

    for gw in sorted(s['exitvpn']['gateways'].keys()):
        if s['exitvpn']['gateways'][gw].get('until'):
            until = datetime.strptime(s['exitvpn']['gateways'][gw]['until'], s['exitvpn']['conf']['date_format'])
            delta = until - now
            f = 'overdue' if delta <= timedelta(days=0) else 'warning' if delta <= timedelta(days=s['exitvpn']['conf']['warndays']) else 'good'
            res[f].append({gw: s['exitvpn']['gateways'][gw]})

    p.m('results', more=res)

    if now.weekday() == s['exitvpn']['conf']['digestday'] or res['warning']:
        pl = 'Achtung! VPN Account läuft aus' if res['warning'] else 'VPN Wochenbericht'
        mail = p.mail_handler(
            to=s['common']['mailto']['admin'],
            cc=s['common']['mailto']['kontakt'],
            sender=s['common']['mailto']['local'],
            subject='photon exitVPN notify',
            punchline=pl,
            add_settings=False
        )
        mail.text = ''
        mail.text = res
        mail.text = 'Do not forget to update the exitvpn.yaml ( https://github.com/freifunk-mwu/gateway-configs.git )'
        mail.send

if __name__ == '__main__':
    nagg_exitvpn_accouts()
