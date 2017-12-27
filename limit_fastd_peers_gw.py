#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module is intended to ask other Gateways for connected peers of each
fastd node instance. Then, an ``average`` value and a ``gauge`` is determined,
forming the ``limit``.

This number will be added as ``limit`` to the ``peer_limit.conf`` of each fastd instance.

Start with :meth:`limit_fastd_peers`

To create configuration for fastd, the existing one is used, but with
``peer limit 23;`` replaced.
'''

from datetime import datetime
from fileinput import FileInput
from json import dump, loads
from os import path, getenv
from pprint import pprint
from re import search as re_search
from re import sub as re_sub
from socket import gaierror, gethostname
from subprocess import call, getstatusoutput
from sys import exit
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
import yaml

def timestamp(rel=0):
    '''
    Helper function for timestamps

    :param rel: specify seconds (epoch: ``rel`` = 0)
    :return: seconds between now and ``rel`` seconds
    '''
    return (datetime.utcnow() - datetime.utcfromtimestamp(rel)).total_seconds()


def get_url(url):
    '''
    Helper function to retrieve data from the web

    :param url: url of file to retrieve
    '''

    try:
        rsp = urlopen(url)
        return rsp.read().decode('utf-8')
    except (HTTPError, URLError, gaierror) as ex:
        print('error fetching url %s - %s' % (url, ex))


def unload_json(raw, fallback=None):
    '''
    Helper function to unpickle json data.

    :param raw: json string to unload
    :param fallback: value to return on problems
    '''
    if raw:
        try:
            return loads(raw)
        except ValueError as ex:
            print('~ could not decode json. fallback to %s - %s' % (fallback, ex))
    return fallback


class Peers:
    '''
    Central class to track the number of peers for each fastd instance over
    each gateway.

    On start, first all settings are stored,
    then :meth:`pull_remote` and :meth:`pull_local` are called.
    '''
    def __init__(self, settings):
        self.hostname = gethostname()
        self.settings = settings

        #: stop the script, if it was started on the wrong machine.
        if self.hostname not in self.settings['gateways']:
            print('~ %s is not in gateways' % (self.hostname))
            print(self.settings['gateways'])
            exit(1)

        #: everything is stored in here
        self.peers = {}

        #: initialize the data
        self.pull_local()
        self.pull_remote()

    def pull_remote(self):
        '''
        Cycles over gateways, tries to :meth:`get_url` and :meth:`unload_json`
        other ``fastd_status`` files.

        Validates files by timestamp, if data is too old, it will be ignored.
        '''
        for gw in self.settings['gateways']:
            if self.hostname == gw:
                print('~ skipping self query %s' % (gw))
                continue

            request = get_url(self.settings['stat_ext'] % (gw, self.settings['stat']))
            data = unload_json(request)
            if data and data.get('_timestamp'):
                #: check remote timestamp
                if (
                    timestamp() >= data['_timestamp'] >=
                    timestamp(rel=self.settings['timeout'])
                ):
                    #: copy received and valid data over
                    self.peers[gw] = data
                    print('~ got data for %s' % (gw))
                    pprint(data)
                else:
                    print('~ data for %s too old' % (gw))
            else:
                print('~ data for %s invalid' % (gw))

    def pull_local(self):
        '''
        Queries ``fastd-status`` command for each fastd instance,
        after :meth:`unload_json` it counts connections and adds them into
        ``peers``.
        '''
        res = {}
        for instance in self.settings['fastd_instances']:
            print('~ running fastd-status for %s' % (instance))
            #: TODO: replace with subprocess.run() when uprading to Python
            status, output = getstatusoutput('sudo '+ self.settings['fastd_status'] +
                    ' /var/run/fastd-%s.status' % (instance))
            if status == 0:
                #: we got data from fastd-status. unpickle the json here
                current = unload_json(output)
                if current.get('peers') and current.get('uptime'):
                    #: filter peers without connection
                    connected = [
                        p for p in current['peers'].values() if
                        p.get('connection')
                    ]
                    #: set own values here
                    #: convert uptime into seconds right at the source
                    res[instance] = {
                        'peers': len(connected),
                        'uptime': int(current.get('uptime', 0) / 1000)
                    }
                    print('~ got data for %s' % (instance))
                    pprint(res[instance])
                else:
                    print('~ data for %s invalid' % (instance))
            else:
                print('~ no data for %s available' % (instance))

        self.peers[self.hostname] = res

    def dump_local(self):
        '''
        Saves local part of ``peers`` into json file, retrievable by other
        Gateways. Adds :meth:`timestamp` into ``_timestamp``.
        '''
        data = self.peers[self.hostname]
        if data:
            #: update timestamp
            data.update({'_timestamp': timestamp()})
            if self.settings['ansible_gate']:
                data.update({'ansible': True})
            with open(self.settings['stat_local'] % (self.settings['stat']), 'w') as outfile:
                dump(data, outfile, indent=4, sort_keys=True)
            print('~ write peers file for %s to %s' % 
                (self.hostname, self.settings['stat_local'] % (self.settings['stat'])))
        else:
            print('~ no data available for %s' % (self.hostname))

    def limit(self):
        '''
        Loops over fastd instances and Gateways, proposing a ``limit`` for
        each fastd instance.

        * First the ``average`` peers per gateway are calculated.
        * Then the ``gauge`` is calculated:
            * one time ``additional`` and
            * one time ``additional`` for each offline gateway
        * The proposed ``limit`` is then ``average`` + ``gauge``

        Calls :meth:`dump_local` when finished.
        '''
        for instance in self.settings['fastd_instances']:
            total_peers = 0
            total_gws = len(self.settings['gateways'])
            online_gws = 0
            for gw in self.settings['gateways']:
                #: find the peers per gateway of the current fastd instance,
                #: sum them up, if any present
                #: while gateway migration (ansible) we implement backward 
                #: compatibility for fastd instances of legacy gateways
                ansible = self.peers.get(gw, {}).get('ansible')
                if ansible:
                    peers = self.peers.get(gw, {}).get(instance, {}).get('peers')
                elif instance.startswith('mz'):
                    peers = self.peers.get(gw, {}).get('mz', {}).get('peers')
                elif instance.startswith('wi'):
                    peers = self.peers.get(gw, {}).get('wi', {}).get('peers')

                if peers:
                    online_gws += 1
                    total_peers += peers

            if not online_gws:
                #: this only happens when both :meth:`pull_remote`
                #: and :meth:`pull_local` produced no output
                #: a.k.a ``self.peers`` is empty.
                #: it avoids zero divisions while developing
                print('~ fatal: not a single gateway seems to be online')
                exit(1)

            #: calculate an average per gateway for current fastd instance
            avg_peers = int(total_peers / online_gws)
            print('~ %s: %s peers on %s gateways: avg %s' % (
                instance, total_peers, online_gws, avg_peers
            ))

            #: calculate how much additional peers to provide above average
            #: per default, it is the average plus ``additional``
            #:
            #: if there was any gateway not reachable,
            #: additionally add ``additional`` per offline gateway
            offline_gws = total_gws - online_gws
            gauge = ((1 + offline_gws) * self.settings['additional'])
            print('~ %s: (1 + %s gateways offline) * %s additional: %s' % (
                instance, offline_gws, self.settings['additional'], gauge
            ))

            #: calculate the limit
            limit = avg_peers + gauge
            print('~ %s: %s + %s: limit %s' % (instance, avg_peers, gauge, limit))

            #: finaly pull own data ...
            data = self.peers.get(self.hostname, {}).get(instance, {})

            #: ... to report community, limit and daemon uptime ...
            yield instance, limit, data.get('uptime', 0)

            #: ... and to store it in ``self.peers``
            if data:
                data.update({'limit': limit})
                self.peers[self.hostname][instance] = data

        self.dump_local()


def write_fastd_config_limit(settings, instance, limit, uptime):
    '''
    Writes calculated limit to the config file of ``fastd``.

    :param settings: script settings
    :param instance: fastd instance name
    :param limit: calculated fastd peer limit to write
    :param uptime: current fastd daemon uptime in seconds
    :return: ``True`` if ``fastd`` should be restarted then.
    '''
    LIMIT_RX = r'peer limit ([\d]+);'

    #: locate the fastd config
    config_file = settings['fastd_config'] % (instance)
    if not path.exists(config_file):
        print('~ %s: %s not found' %(instance,config_file))
        return False

    #: load config to string
    with open (config_file, "r") as file:
        lines = file.readlines()
        config = ''.join(lines)

    #: find current peer limit in fast config
    #: skip the rest if none present
    match = re_search(LIMIT_RX, config)
    if not match:
        print('~ no peer limit present in config for %s. skipping' % (instance))
        return False

    old_limit = int(match.group(1))

    #: replacing the current limit with the calculated limit
    new_config = re_sub(LIMIT_RX, 'peer limit %s;' % (limit), config)
    with open (config_file, "w") as file:
        file.write(new_config)

    #: return ``True`` if there was a huge bump in the limit, or
    #: fast was running long enough..
    return any([
        abs(limit - old_limit) >= settings['additional'],
        uptime >= settings['restart_max']
    ])


def limit_fastd_peers():
    '''
    Main function on script run.
    Creates ``peers`` instance, iterates over :meth:`Peers.limit` proposals
    and reads existing config files into templates.

    Only if any ``peers limit 42;`` option is set, the value ``42`` is replaced
    by ``limit``. Then, writes template.

    Restarts ``fastd`` if there were changes greater than ``additional`` or
    fastd was running for more than ``restart_max`` seconds.
    '''

    home = getenv('HOME')
    stream = open(home + '/.config/fastd_peer_limit_config.yaml', 'r')
    settings = yaml.load(stream)

    peers = Peers(settings)

    for instance, limit, uptime in peers.limit():
        if write_fastd_config_limit(settings, instance, limit, uptime):
            print('~ fastd restart for %s required' % (instance))
            call(['sudo', 'systemctl', 'restart', 'fastd@%s' % (instance)])

if __name__ == '__main__':
    limit_fastd_peers()
