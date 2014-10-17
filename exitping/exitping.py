
from photon import Photon

if __name__ == '__main__':

    p = Photon(config='exitping_config.yaml', summary='exitping_summary.yaml', meta='exitping_meta.json', verbose=False)
    s = p.settings.get

    uping, aping = p.new_ping(net_if=s['ping']['interface']), p.new_ping(net_if=s['ping']['interface'])

    for url in s['ping']['urls']: uping.probe = url
    for add in s['ping']['addresses']: aping.probe = add

    for community in s['batman']:
        cif = s['batman'][community]['interface']
        cbw = s['batman'][community]['bandwidth']
        if uping.status['ratio'] <= s['ping']['min_ratio'] or aping.status['ratio'] <= s['ping']['min_ratio']:
            p.m(
                '%s - it seems you are not properly connected!\nremoving batman server flag for %s' %(community, cif),
                cmdd=dict(cmd='sudo batctl -m %s gw off' %(cif)),
                more=dict(ping_urls=uping.status, ping_addresses=aping.status),
                verbose=True
            )
        else:
            p.m(
                '%s - you are indeed connected!\nsetting batman server flag for %s (bw: %s)' %(community, cif, cbw),
                cmdd=dict(cmd='sudo batctl -m %s gw server %s' %(cif, cbw)),
                more=dict(ping_urls=uping.status, ping_addresses=aping.status),
                verbose=True
            )
