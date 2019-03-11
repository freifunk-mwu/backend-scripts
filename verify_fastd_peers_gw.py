#!/usr/bin/env python3

import os
import requests
import sys
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

def verify_fastd_peer():
    peer_key = sys.argv[1]
    keys_file = '/etc/fastd/fastd_peers.txt'

    config_file = '/home/admin/.ffmwu-config/fastd_peer_limit.yaml'
    with open(config_file, 'r') as stream:
        settings = yaml.load(stream)

    with open(keys_file) as keys:
        if peer_key not in keys.read():
            sys.exit(1)

    url = 'http://127.0.0.1:9281/metrics'
    ok, metrics = pull_metrics(url, settings['fetch_timeout'])

    if ok:
        peers = parse_metrics(metrics, settings['fastd_instances'])

    with open (settings['limit_file'], "rt") as f:
        line = f.readline().strip()
        limit = int(line)

    if peers >= limit:
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    verify_fastd_peer()
