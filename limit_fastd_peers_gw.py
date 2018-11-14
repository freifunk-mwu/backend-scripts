#!/usr/bin/env python3
'''
This module is intended to ask other Gateways for connected peers of each
community. Then, an ``average`` value and a ``gauge`` is determined, forming
the ``limit``.

This number will be added as ``limit`` to the ``fast.conf`` of each community.

This will hopefully distribute the nodes better over all our gateways.

Start with :meth:`limit_fastd_peers`

To create configuration for fastd, the existing one is used, but with
``peer limit 23;`` replaced.
'''

from datetime import datetime
from json import loads
from re import search as re_search
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

        #: stop the script, if it was started on the wrong machine.
        if self.hostname not in self.gateways:
            self.p.m(
                '%s is not in gateways' % (self.hostname),
                more=self.gateways,
                state=True
            )

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
        for gw in self.gateways:
            if self.hostname == gw:
                self.p.m('skipping self query %s' % (gw))
                continue

            request = get_url(self.p, self.stat_ext % (gw))
            data = unload_json(self.p, request)
            if data and data.get('_timestamp'):
                #: check remote timestamp
                if (
                    timestamp() >= data['_timestamp'] >=
                    timestamp(rel=self.timeout)
                ):
                    #: copy received and valid data over
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
                cmdd=dict(cmd='sudo %s %s' % (
                    self.fastd_status,
                    self.fastd[com]['sockfile']
                )),
                critical=False
            )
            if status.get('returncode') == 0:
                #: we got data from fastd-status. unpickle the json here
                current = unload_json(self.p, '\n'.join(status.get('stdout')))
                if current.get('peers') and current.get('uptime'):
                    #: filter peers without connection
                    connected = [
                        p for p in current['peers'].values() if
                        p.get('connection')
                    ]
                    #: set own values here
                    #: convert uptime into seconds right at the source
                    res[com] = {
                        'peers': len(connected),
                        'uptime': int(current.get('uptime', 0) / 1000)
                    }
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
            #: update timestamp
            data.update({'_timestamp': timestamp()})
            return self.p.m(
                'write peers file for %s to %s' % (
                    self.hostname, self.stat_local
                ),
                more='%s bytes' % (write_json(self.stat_local, data))
            )
        self.p.m('no data available for %s' % (self.hostname))

    def append_csv_logs(self):
        '''
        append a log line to static csv logs each, for long term observation
        one log file per community
        format: hostname,timestamp,num_gates,limit,peers,total,[other gates:hostname,limit,peers]
        '''
        for com in self.communities:
            #: the following few lines just copied from "limit"
            on_gws = 0
            total = 0
            for gw in self.gateways:
                peers = self.peers.get(gw, {}).get(com, {}).get('peers')
                if peers:
                    on_gws += 1
                    total += peers
                    
            data = self.peers.get(self.hostname, {}).get(com, {})
            with open("/home/admin/.cronlog/limit."+com+".log","a") as logfile:
                logfile.write("%s,%d,%d,%03d,%03d,%03d" %
                              (self.hostname,timestamp(),on_gws,
                              data.get('limit'),data.get('peers'),total))
                for gw in self.gateways:
                    if self.hostname != gw:
                        try:
                            data = self.peers.get(gw, {}).get(com, {})
                            if data:
                                logfile.write(",%s,%03d,%03d" %
                                      (gw,data.get('limit'),data.get('peers')))
                            else:
                                logfile.write(",%s,<off?>" % gw)
                        except:
                            logfile.write(",%s,<ERR>" % gw)
            
                logfile.write("\n")
                
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
                #: find the peers per gateway of the current community,
                #: sum them up, if any present
                peers = self.peers.get(gw, {}).get(com, {}).get('peers')
                if peers:
                    online_gws += 1
                    total_peers += peers

            if not online_gws:
                #: this only happens when both :meth:`pull_remote`
                #: and :meth:`pull_local` produced no output
                #: a.k.a ``self.peers`` is empty.
                #: it avoids zero divisions while developing
                self.p.m(
                    'fatal: not a single gateway seems to be online',
                    more='this should never happen',
                    state=True
                )

            #: calculate an average per gateway for current community
            avg_peers = int(total_peers / online_gws)
            self.p.m('%s: %s peers on %s gateways: avg %s' % (
                com, total_peers, online_gws, avg_peers
            ))

            #: calculate how much additional peers to provide above average
            #: per default, it is the average plus ``additional``
            #:
            #: if there was any gateway not reachable,
            #: additionally add ``additional`` per offline gateway
            offline_gws = total_gws - online_gws
            gauge = ((1 + offline_gws) * self.additional)
            self.p.m('%s: (1 + %s gateways offline) * %s additional: %s' % (
                com, offline_gws, self.additional, gauge
            ))

            #: calculate the limit
            limit = avg_peers + gauge
            self.p.m('%s: %s + %s: limit %s' % (
                com, avg_peers, gauge, limit
            ))

            #: finaly pull own data ...
            data = self.peers.get(self.hostname, {}).get(com, {})

            #: ... to report community, limit and daemon uptime ...
            yield com, limit, data.get('uptime', 0)

            #: ... and to store it in ``self.peers``
            if data:
                data.update({'limit': limit})
                self.peers[self.hostname][com] = data

        self.dump_local()


def write_fastd_config_limit(photon, com, limit, uptime):
    '''
    Writes calculated limit to the config file of ``fastd``.

    :param photon: photon instance (for error reporting, settings and helpers)
    :param com: Community short name
    :param limit: calculated fastd peer limit to write
    :param uptime: current fastd daemon uptime in seconds
    :return: ``True`` if ``fastd`` should be restarted then.
    '''
    LIMIT_RX = r'peer limit ([\d]+);'
    settings = photon.settings.get

    #: locate the fastd config
    config_file = settings['limit']['fastd'][com]['fastd']
    config = read_file(config_file)
    if not config:
        photon.m('no fastd config found for %s (%s)' % (com, config_file))
        return False

    #: find current peer limit in fast config
    #: skip the rest if none present
    match = re_search(LIMIT_RX, config)
    if not match:
        photon.m('no peer limit present in config for %s. skipping' % (com))
        return False

    old_limit = int(match.group(1))

    #: use the template_handler with the current fastd config,
    #: replacing the current limit by ``${limit}`` which itself
    #: gets substituted with the calculated limit on writing
    template = photon.template_handler(
        re_sub(LIMIT_RX, 'peer limit ${limit};', config),
        fields={'limit': limit}
    )
    template.write(config_file, append=False, backup=False)

    #: return ``True`` if there was a huge bump in the limit, or
    #: fast was running long enough..
    return any([
        abs(limit - old_limit) >= settings['limit']['additional'],
        uptime >= settings['limit']['restart_max']
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
    photon, settings = pinit('limit_fastd_peers')
    peers = Peers(photon)

    for community, limit, uptime in peers.limit():
        if write_fastd_config_limit(photon, community, limit, uptime):
            photon.m(
                'fastd restart for %s required' % (community),
                cmdd=dict(cmd='sudo service fastd restart %s' % (
                    settings['limit']['fastd'][community]['interface']
                ))
            )
    peers.append_csv_logs()

if __name__ == '__main__':
    limit_fastd_peers()
