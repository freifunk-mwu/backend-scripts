#!/usr/bin/env python3

import argparse
import json
import requests
from datetime import datetime

def scrape(url):
    return requests.get(url).json()

def update(file, nodes, clients):
    date = datetime.now().isoformat('T')

    json_data = open(file)
    data = json.load(json_data)
    json_data.close()
    
    with open(file, 'r') as f:
        data = json.load(f)
    
    data["state"]["lastchange"] = datetime.now().isoformat('T')
    data["state"]["description"] = 'Wir erfreuen uns an %d Knoten und %d Clients' % (nodes, clients)
    data["state"]["nodes"] = int(nodes)

    with open(file, 'w') as f:
        f.write(json.dumps(data, indent=2))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Update Freifunk API file.')
    parser.add_argument('-u', '--url',    required=True, action='store', help='url for nodes.json')
    parser.add_argument('-f', '--file',   required=True, action='store', help='api file to update')
    parser.add_argument('-d', '--domain', required=True, action='append', help='domain to count')
    args = parser.parse_args()

    nodelist = scrape(args.url)

    nodes = 0
    clients = 0

    if nodelist:
        for node in nodelist['nodes']:
            if not 'domain_code' in node['nodeinfo']['system']:
                continue

            if node['flags']['online'] and node['nodeinfo']['system']['domain_code'] in args.domain:
                nodes += 1
                clients += node['statistics']['clients']
    
    print('%s: %d knoten, %d clients' % (args.domain, nodes, clients))

    update(args.file, nodes, clients)
