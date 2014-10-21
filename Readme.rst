backend-scripts
===============

Hier werden Skripte gesammelt, die auf den Gates zum Einsatz kommen.

Die `Installation <http://gluon-gateway-doku.readthedocs.org/de/latest/operations/scripts.html>`_ ist Teil der Gluon Gateway Dokumentation.


.. topic:: dot2json.pl

    Wandelt ein dot file, wie es als Topo aus tinc fällt, in ein json file, wie force directed graph (D3) es erwartet.
    Nutzt nur stdin und stdout.


.. topic:: all_confsnap.py

    Füttert das `gateway-configs Repository <https://github.com/freifunk-mwu/gateway-configs>`_ mit Konfigurationsdateien frisch vom Gate.


.. topic:: all_keybootstrap.py

    Erzeugt ein ssh-Keypaar, und hinterlegt dieses für eiheitlichen Zugriff auf Github in die ``~/.ssh/config``


.. topic:: gw_exitping.py

    Setzt das `BATMAN` Server Flag [#root]_ je nach Erreichbarkeit von gegebenen Hosts durch das ExitVPN.


.. topic:: gw_peersync.py

    Synchronisiert die ``peers``-Ordner von `fastd` mit den Git-Repos und lässt `fastd` die ``peers`` neu einlesen [#root]_.


.. [#root] Benötigt dazu Root-Rechte
