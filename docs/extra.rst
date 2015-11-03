Extra
=====


Firmware-Sync
-------------

All our gateways provide a firmware mirror for initial flashing and autoupdating of nodes.

Our buildserver called `Pudding <http://pudding.freifunk-mwu.de/firmware/>`_ provides the firmware via rsync.

So we put this into the crontab::

    23 */8 * * * /usr/bin/rsync -avh --delete rsync://pudding.freifunk-mwu.de:2873/firmware /var/www/html/firmware > $HOME/.cronlog/firmware_rsync.log 2>&1

You can see the synced results via our DNS Round-Robin at `firmware.freifunk-mwu.de <http://firmware.freifunk-mwu.de/>`_


Package-Mirror-Sync
-------------------

Our service-machine provides a package mirror for openwrt inside the mesh.

The Sync is done via ``lftp`` using a command file:

.. literalinclude:: ../common/lftp_commands
    :linenos:

In the crontab we then call this command::

    19 1 * * * /usr/bin/lftp -f $HOME/clones/backend-scripts/common/lftp_commands > $HOME/.cronlog/mirror_openwrt_repo.log 2>&1

.. note::

    This eats up much space.

    * Barrier Breaker stable uses ± 36 GiB.
    * Chaos Calmer stable uses ± 35 GiB.
    * Chaos Calmer as release candidate uses ± 51 GiB.


_etc
----

_etc/**dot2json.pl**
    Converts a dot-file, generated as topo from tinc into a json-file how force directed graph (D3) expects it.

    Uses stdin and stdout only.
