
from photon import Photon

if __name__ == '__main__':

    p = Photon(config='ffmwu_config.yaml', summary='ffmwu_summary.yaml', meta='exitping_meta.json', verbose=False)
    s = p.settings.get

    uping, aping = p.ping_handler(net_if=s['exitping']['interface']), p.ping_handler(net_if=s['exitping']['interface'])

    uping.probe, aping.probe = s['exitping']['urls'], s['exitping']['addresses']

    for community in s['common']['communities']:
        cif = s['batman'][community]['interface']
        cbw = s['batman'][community]['bandwidth']
        if uping.status['ratio'] <= s['exitping']['min_ratio'] or aping.status['ratio'] <= s['exitping']['min_ratio']:
            p.m(
                '%s - it seems you are not properly connected!\nremoving batman server flag for %s' %(community, cif),
                cmdd=dict(cmd='sudo batctl -m %s gw off' %(cif)),
                more=dict(ping_urls=uping.status, ping_addresses=aping.status),
                verbose=True
            )
        else:
            p.m(
                '%s - you are connected!\nsetting batman server flag for %s (bw: %s)' %(community, cif, cbw),
                cmdd=dict(cmd='sudo batctl -m %s gw server %s' %(cif, cbw)),
                more=dict(ping_urls=uping.status, ping_addresses=aping.status),
                verbose=True
            )
