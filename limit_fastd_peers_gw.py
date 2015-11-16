#!/usr/bin/env python3
'''
This module is intended to ask other Gateways for connected peers of each
community. Then, an ``average`` value and a ``gauge`` is determined, forming
the ``limit``.

This number will be added as ``limit`` to the ``fast.conf`` of each community.

This will hopefully distribute the nodes better on all gateways.

Start with :meth:`limit_fastd_peers`

To create configuration for fastd, the existing one is used, but with
``peer limit 23;`` replaced.
'''

from datetime import datetime
from json import loads
from re import sub as re_sub
from socket import gaierror
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from photon.util.files import read_file, write_json

from common import pinit


def timestamp(rel=0):
    '''
    Helper function for timestamps

    :param rel: specify seconds (epoch: ``rel`` = 0)
    :return: seconds between now and ``rel`` seconds
    '''
    return (datetime.utcnow() - datetime.utcfromtimestamp(rel)).total_seconds()


def get_url(photon, url):
    '''
    Helper function to retrieve data from the web

    :param photon: photon instance (for error reporting)
    :param url: url of file to retrieve
    '''

    try:
        rsp = urlopen(url)
        return rsp.read().decode('utf-8')
    except (HTTPError, URLError, gaierror) as ex:
        photon.m(
            'error fetching url %s - %s' % (url, ex)
        )


def unload_json(photon, raw, fallback=None):
    '''
    Helper function to unpickle json data.

    :param photon: photon instance (for error reporting)
    :param raw: json string to unload
    :param fallback: value to return on problems
    '''
    if raw:
        try:
            return loads(raw)
        except ValueError as ex:
            photon.m(
                'could not decode json. fallback to %s - %s' % (fallback, ex)
            )
    return fallback


class Peers:
    '''
    Central class to track the number of peers for each community over
    each gateway.

    On start, first all settings are stored,
    then :meth:`pull_remote` and :meth:`pull_local` are called.
    '''
    def __init__(self, photon):
        self.p = photon
        settings = photon.settings.get

        self.additional = settings['limit']['additional']
        self.communities = settings['common']['communities']
        self.fastd = settings['limit']['fastd']
        self.fastd_status = settings['limit']['fastd_status']
        self.gateways = settings['limit']['query']
        self.hostname = settings['common']['hostname']
        self.stat_ext = settings['limit']['stat_ext']
        self.stat_local = settings['limit']['stat_local']
        self.timeout = settings['limit']['timeout']

        if self.hostname not in self.gateways:
            self.p.m(
                '%s is not in gateways' % (self.hostname),
                more=self.gateways,
                state=True
            )

        self.peers = {}

        # self.pull_remote()
        self.pull_local()

    def pull_remote(self):
        '''
        Cycles over gateways, tries to :meth:`get_url` and :meth:`unload_json`
        other ``fastd_status`` files.

        Validates files by timestamp, if data is too old, it will be ignored.
        '''
        for gw in self.gateways:
            if self.hostname == gw:
                self.p.m('skipping self query %s' % (gw))
                continue
            request = get_url(self.p, self.stat_ext % (gw))
            data = unload_json(self.p, request)
            if data and data.get('_timestamp'):
                if (
                    timestamp() >= data['_timestamp'] >=
                    timestamp(rel=self.timeout)
                ):
                    self.peers[gw] = data
                    self.p.m('got data for %s' % (gw), more=data)
                else:
                    self.p.m('data for %s too old' % (gw))
            else:
                self.p.m('data for %s invalid' % (gw))

    def pull_local(self):
        '''
        Queries ``fastd-status`` command for each community,
        after :meth:`unload_json` it counts connections and adds them into
        ``peers``.
        '''
        res = {}
        for com in self.communities:
            status = self.p.m(
                'running fastd-status for %s' % (com),
                cmdd=dict(cmd='ssh kaschu "sudo %s %s"' % (
                    self.fastd_status,
                    self.fastd[com]['sockfile']
                )),
                critical=False
            )
            if status.get('returncode') == 0:
                current = unload_json(self.p, '\n'.join(status.get('stdout')))
                if current.get('peers'):
                    connected = [
                        p for p in current['peers'].values() if
                        p.get('connection')
                    ]
                    res[com] = {'peers': len(connected)}
                    self.p.m('got data for %s' % (com), more=res[com])
                else:
                    self.p.m('data for %s invalid' % (com))
            else:
                self.p.m('no data for %s available' % (com))

        self.peers[self.hostname] = res

    def dump_local(self):
        '''
        Saves local part of ``peers`` into json file, retrievable by other
        Gateways. Adds :meth:`timestamp` into ``_timestamp``.
        '''
        data = self.peers[self.hostname]
        if data:
            data.update({'_timestamp': timestamp()})
            return self.p.m(
                'write peers file for %s to %s' % (
                    self.hostname, self.stat_local
                ),
                more='%s bytes' % (write_json(self.stat_local, data))
            )
        self.p.m('no data available for %s' % (self.hostname))

    def limit(self):
        '''
        Loops over Communities and it's Gateways, proposing a ``limit`` for
        each Community.

        * First the ``average`` peers per gateway are calculated.
        * Then the ``gauge`` is calculated:
            * one time ``additional`` and
            * one time ``additional`` for each offline gateway
        * The proposed ``limit`` is then ``average`` + ``gauge``

        Calls :meth:`dump_local` when finished.
        '''
        for com in self.communities:
            total_peers = 0
            total_gws = len(self.gateways)
            online_gws = 0
            for gw in self.gateways:
                peers = self.peers.get(gw, {}).get(com, {}).get('peers')
                if peers:
                    online_gws += 1
                    total_peers += peers

            avg_peers = int(total_peers / online_gws)
            self.p.m('%s: %s peers on %s gateways: avg %s' % (
                com, total_peers, online_gws, avg_peers
            ))

            offline_gws = total_gws - online_gws
            gauge = ((1 + offline_gws) * self.additional)
            self.p.m('%s: (1 + %s gateways offline) * %s additional: %s' % (
                com, offline_gws, self.additional, gauge
            ))

            limit = avg_peers + gauge
            self.p.m('%s: %s + %s: limit %s' % (
                com, avg_peers, gauge, limit
            ))

            yield com, limit

            data = self.peers[self.hostname].get(com)
            if data:
                data.update({'limit': limit})
                self.peers[self.hostname][com] = data

        self.dump_local()


def limit_fastd_peers():
    '''
    Main function on script run.
    Creates ``peers`` instance, iterates over :meth:`Peers.limit` proposals
    and reads existing config files into templates.

    Only if any ``peers limit 23;`` option is set, the value ``23`` is replaced
    by ``limit``. Then, writes template.

    Restarts ``fastd`` if there were any changes.
    '''
    photon, settings = pinit('limit_fastd_peers')

    peers = Peers(photon)
    restart_required = False

    for community, limit in peers.limit():

        config_file = settings['limit']['fastd'][community]['fastd']
        config = read_file(config_file)
        if config:
            config_template = re_sub(
                r'peer limit [0-9]+;',
                'peer limit ${limit};',
                config
            )
            template = photon.template_handler(
                config_template,
                fields={'limit': limit}
            )
            if config != template.sub:
                restart_required = True

            template.write(config_file, append=False, backup=False)
        else:
            photon.m('error writing fastd config for %s' % (community))

    if restart_required:
        photon.m(
            'fastd restart required',
            cmdd=dict(cmd='sudo service fastd restart')
        )

if __name__ == '__main__':
    limit_fastd_peers()
