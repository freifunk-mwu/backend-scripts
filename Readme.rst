backend-scripts
===============

Hier werden Skripte gesammelt, die auf den Gates zum Einsatz kommen.

Die `Installation <http://gluon-gateway-doku.readthedocs.org/de/latest/operations/scripts.html>`_ ist Teil der Gluon Gateway Dokumentation.


.. topic:: _etc/dot2json.pl

    Wandelt ein dot file, wie es als Topo aus tinc fällt, in ein json file, wie force directed graph (D3) es erwartet.
    Nutzt nur stdin und stdout.

Die folgenden Scripte nutzen selbst `Photon <http://photon.readthedocs.org>`_ als Backend.

.. topic:: common/ffmwu_defaults.yaml

    Die Konfiguration der Backend Scripte für **ffmwu**.
    
    Sollte man lokale Änderungen vornehmen wollen, nutzt man die nach dem ersten Start von Photon_ erstellte *ffmwu_config.yaml* und ersetzt die entsprechenden Werte.

.. topic:: bootstrap_git_all.py

    Erzeugt ein ssh-Keypaar (*hostname_rsa*, *hostname_rsa.pub*), und hinterlegt diesen für eiheitlichen Zugriff auf Github in die ``~/.ssh/config``.

    :Zugriff: ``ssh://github_mwu/freifunk-mwu/backend-scripts.git``

.. topic:: check_exitvpn_gw.py

    Setzt das `BATMAN` Server Flag [#root]_ und startet/stoppt den `isc-dhcp-server` [#root]_  je nach Erreichbarkeit von gegebenen Hosts durch das ExitVPN.
    
.. topic:: snapshot_configs_all.py

    Füttert das `gateway-configs Repository <https://github.com/freifunk-mwu/gateway-configs>`_ mit Konfigurationsdateien frisch vom Gate.

.. topic:: sync_meshkeys_gw.py

    Synchronisiert die ``peers``-Ordner mit den Git-Repos und lässt `fastd` danach die ``peers`` neu einlesen [#root]_.

.. [#root] Benötigt dazu Root-Rechte
