#!/usr/bin/env python3

import json
import argparse
import requests
import arrow
from datetime import datetime
from email_validator import validate_email, EmailNotValidError, EmailSyntaxError

def main(params):
    nodes_fn = requests.get(params['url'], verify=False)
    nodedb = nodes_fn.json()

    now = datetime.utcnow().replace(microsecond=0)

    nodes_sum = 0
    nodes_with_contact = 0
    nodes_without_contact = 0

    contactlist = list()
    contactdict = {
        "contacts": dict(),
        "nodes_total": "0",
        "nodes_with_contact": "0",
        "nodes_without_contact": "0",
        "updated_at": now.isoformat()
    }

    def check_email(mail):
        try:
            email = validate_email(mail, check_deliverability=False)
            return email['email']
        except ValueError:
            return None

    def get_owner(nodeinfo):
        try:
            if 'owner' in nodeinfo:
                mail = check_email(nodeinfo['owner']['contact'].lower())
                if mail:
                    return (mail, "email")
                else:
                    return nodeinfo['owner']['contact'].lower(), "other"

        except (KeyError, EmailSyntaxError):
            return None

    def get_offline_days(timestamp):
        datetime_now = arrow.get(now.isoformat())
        node_lastseen = arrow.get(timestamp)
        daydiff = datetime_now - node_lastseen

        return daydiff.days

    for node in nodedb['nodes']:
        contact = ''
        node_out = dict()
        nodes_sum += 1
        hostname = node['nodeinfo']['hostname']
        node_out[hostname] = dict()

        if not node['flags']['online']:
            offline_days = get_offline_days(node['lastseen'])
            node_out[hostname]['status'] = "offline"
            node_out[hostname]['days_offline'] = offline_days
        else:
            node_out[hostname]['status'] = "online"

        contact = get_owner(node['nodeinfo'])

        if contact:
            owner = contact[0]
            type = contact[1]
            nodes_with_contact += 1
            if owner in contactlist:
                contactdict['contacts'][owner]['nodes'].update(node_out)
            else:
                contactlist.append(owner)
                contactdict['contacts'][owner] = dict()
                contactdict['contacts'][owner]['type'] = type
                contactdict['contacts'][owner]['nodes'] = dict()
                contactdict['contacts'][owner]['nodes'].update(node_out)
        else:
            nodes_without_contact += 1

    contactdict['nodes_total'] = nodes_sum
    contactdict['nodes_with_contact'] = nodes_with_contact
    contactdict['nodes_without_contact'] = nodes_without_contact

    print(json.dumps(contactdict, sort_keys=True, indent=4))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-u', '--url', action='store',
                        help='URL to nodes.json',required=True)

    args = parser.parse_args()
    options = vars(args)

    main(options)
