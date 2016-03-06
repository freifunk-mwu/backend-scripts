#!/usr/bin/env python3

import json
import argparse
import requests
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
    nodedict = {
        "nodes": dict(),
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

    for node in nodedb['nodes']:
        contact = ''
        node_out = dict()
        nodes_sum += 1
        node_out['hostname'] = node['nodeinfo']['hostname']
        node_out['lastseen'] = node['lastseen']

        contact = get_owner(node['nodeinfo'])

        if contact:
            owner = contact[0]
            type = contact[1]
            nodes_with_contact += 1
            if owner in contactlist:
                nodedict['nodes'][owner].append(node_out)
            else:
                contactlist.append(owner)
                nodedict['nodes'][owner] = list()
                nodedict['nodes'][owner].append(node_out)
        else:
            nodes_without_contact += 1
            
    nodedict['nodes_total'] = nodes_sum
    nodedict['nodes_with_contact'] = nodes_with_contact
    nodedict['nodes_without_contact'] = nodes_without_contact

    print(json.dumps(nodedict, sort_keys=True, indent=4))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-u', '--url', action='store',
                        help='URL to nodes.json',required=True)

    args = parser.parse_args()
    options = vars(args)

    main(options)
