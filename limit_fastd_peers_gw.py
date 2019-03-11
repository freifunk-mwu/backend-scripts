#!/usr/bin/env python3

import os
import requests
import yaml

from prometheus_client.parser import text_string_to_metric_families

def pull_metrics(url, timeout):
    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.RequestException as e:
        print('error fetching url %s - %s' % (url, e))
        return(False, None)

    if response.status_code != 200:
        return(False, None)

    metrics = response.content.decode('utf-8')
    return (True, metrics)

def parse_metrics(metrics, instances):
    peers = 0

    for family in text_string_to_metric_families(metrics):
        if family.name != 'fastd_peers_up_total':
            continue

        for sample in family.samples:
            if sample.labels['interface'] in instances:
                peers += int(sample.value)

    return(peers)

def limit_fastd_peers():
    home = os.getenv('HOME')
    config_file = home + '/.ffmwu-config/fastd_peer_limit.yaml'
    with open(config_file, 'r') as stream:
        settings = yaml.load(stream)

    total_gws = len(settings['gateways'])

    online_gws = 0
    online_peers = 0

    for gw in settings['gateways']:
        url = settings['metrics_url'] % (gw)
        ok, metrics = pull_metrics(url, settings['fetch_timeout'])

        if ok:
            online_gws += 1
            peers = parse_metrics(metrics, settings['fastd_instances'])
            online_peers += int(peers)

    avg_peers = online_peers / online_gws

    offline_gws = total_gws - online_gws
    gauge = ((1 + offline_gws) * settings['additional'])

    limit = avg_peers + gauge

    print('gateways online: %d/%d' % (online_gws, total_gws))
    print('peers connected: %d' % (online_peers))
    print('avg peers per gw: %d' % (avg_peers))
    print('additional peers: %d' % (gauge))
    print('peer limit per gw: %d' % (limit))

    limit_file = settings['limit_file']
    with open (limit_file, "w") as f:
        f.write('%d\n' % (limit))
        print('wrote %s'  % (limit_file))

if __name__ == '__main__':
    limit_fastd_peers()
