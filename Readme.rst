backend-scripts
===============

Hier werden Skripte gesammelt, die auf den Gates zum Einsatz kommen

.. topic:: dot2json.pl

    Wandelt ein dot file, wie es als Topo aus tinc fällt, in ein json file, wie force directed graph (D3) es erwartet.

    Nutzt nur stdin und stdout.


.. topic:: exitping

    Setzt den Server Flag von `BATMAN` je nach Erreichbarkeit von gegebenen Hosts durch das ExitVPN.


.. topic:: peersync

    Synchronisiert die ``peers``-Ordner von `fastd` mit den Git-Repos und lässt `fastd` die ``peers`` neu einlesen.


.. topic:: confsnap

    Füttert das `gateway-configs Repository <https://github.com/freifunk-mwu/gateway-configs>`_ mit Konfigurationsdateien frisch vom Gate.


.. _photon: https://github.com/spookey/photon
