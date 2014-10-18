backend-scripts
===============

Hier werden Skripte gesammelt, die auf den Gates zum Einsatz kommen

.. topic:: dot2json.pl

    Wandelt ein dot file, wie es als Topo aus tinc fällt, in ein json file, wie force directed graph (D3) es erwartet. [#stdio]_

photon
------

Diese Scripte nutzen nach Lust und Laune photon_ als Backend.

.. topic:: all_confsnap.py

    Füttert das `gateway-configs Repository <https://github.com/freifunk-mwu/gateway-configs>`_ mit Konfigurationsdateien frisch vom Gate.


.. topic:: all_keybootstrap.py

    Erzeugt ein ssh-keypaar, und hinterlegt diesen für eiheitlichen Zugriff auf Github in die ``~/.ssh/config``

    .. todo 0 To be finished


.. topic:: gw_exitping.py

    Setzt den Server Flag [#root]_ von `BATMAN` je nach Erreichbarkeit von gegebenen Hosts durch das ExitVPN.


.. topic:: gw_peersync.py

    Synchronisiert die ``peers``-Ordner von `fastd` mit den Git-Repos und lässt `fastd` die ``peers`` neu einlesen [#root]_.


.. [#root] Benötigt Root-Rechte
.. [#stdio] Nutzt nur stdin und stdout.
.. _photon: https://github.com/spookey/photon
