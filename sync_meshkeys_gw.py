#!/usr/bin/env python3

from common import pinit


def sync_meshkeys():
    '''
    Updates the ``peers`` folder of ``fastd`` with it's repositories,

    Extra entries are keys in ``settings['fastd']``
    which are not listed in ``settings['common']['communities']``.

    Those require only a ``local`` and a ``remote`` setting, so the
    repo can be synced read-only. See ``_bingen`` as an example.

    For read-write sync, the user running the script must have full access to
    the key-repositories.

    Sends a SIGHUP to ``fastd`` afterwards, so it reloads the configuration and
    keys, so a ``pidfile`` is needed.
    '''
    photon, settings = pinit('sync_meshkeys', verbose=True)
    communities = settings['common']['communities']

    # only pulls keys from extra repos
    for extra in [
        e for e in settings['fastd'].keys() if e not in communities
    ]:
        photon.git_handler(
            settings['fastd'][extra]['local'],
            remote_url=settings['fastd'][extra]['remote']
        )._pull()

    for community in communities:
        git = photon.git_handler(
            settings['fastd'][community]['local'],
            remote_url=settings['fastd'][community]['remote']
        )
        git.cleanup

        # send sighup to fastd to reload configuration (and keys)
        photon.signal_handler(
            settings['fastd'][community]['pidfile'],
            cmdd_if_no_pid=dict(cmd='sudo service fastd start')
        ).hup

        git.publish


if __name__ == '__main__':
    sync_meshkeys()
