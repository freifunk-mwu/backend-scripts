backend-scripts
===============

Hier werden Skripte gesammelt, die auf den Gates zum Einsatz kommen.

_etc/dot2json.pl
    Wandelt ein dot file, wie es als Topo aus tinc fällt, in ein json file, wie force directed graph (D3) es erwartet.
    Nutzt nur stdin und stdout.

----

Die folgenden Scripte nutzen selbst `Photon <http://photon.readthedocs.org>`_ als Backend.

Die `Installation <http://gluon-gateway-doku.readthedocs.org/de/latest/operations/scripts.html>`_ ist Teil der Gluon Gateway Dokumentation.

Die Endungen der Scripte beschreiben auf welchem Typ von Maschine diese i.d.R. laufen sollen:

:_gw: Gateways
:_all: Alle (== Gateways, Buildserver, Webserver und weitere)

common/ffmwu_defaults.yaml
    Die Konfiguration der Backend Scripte für **ffmwu**.

    Sollte man lokale Änderungen vornehmen wollen, nutzt man die nach dem ersten Start von Photon_ erstellte *ffmwu_config.yaml* und ersetzt die entsprechenden Werte.

bootstrap_git_all.py
    Erzeugt ein ssh-Keypaar (*hostname_rsa*, *hostname_rsa.pub*), und hinterlegt diesen für eiheitlichen Zugriff auf Github in die ``~/.ssh/config``. Nicht vergessen, den Schlüssel dem `Nutzer ffmwu <https://github.com/freifunkmwu>`_ hinterlegen. Dieser hat über die `Gruppe machines <https://github.com/orgs/freifunk-mwu/teams/machines>`_ Zugriff auf die benötigten Repositories

    Repo-Zugriffs-Syntax: ``ssh://github_mwu/freifunk-mwu/backend-scripts.git``

check_exitvpn_gw.py
    Setzt das `BATMAN` Server Flag [#root]_ und startet/stoppt den `isc-dhcp-server` [#root]_  je nach Erreichbarkeit von gegebenen Hosts durch das ExitVPN.

deploy_ssh_all.py
    Setzt noch nicht vorhandene Schlüssel aus dem `gateway-configs Repository <https://github.com/freifunk-mwu/gateway-configs>`_ in die ``~/.ssh/authorized_keys``.

draw_traffic_gw.py
    Zeichnet `vnstat <http://humdi.net/vnstat/>`_  Graphen, und klebt diese in eine Webseite.

gen_website_all.py
    Generiert eine einfache Webseite, mit rudimentären Informationen.

nagg_exitvpn_accouts_all.py
    Geht die Liste der ExitVPN Accounts im `gateway-configs Repository`_ durch und schickt Mails.

    Entweder als Wochenbericht, oder täglich, wenn ein Account droht auszulaufen.

snapshot_configs_all.py
    Füttert das `gateway-configs Repository`_ mit Konfigurationsdateien frisch vom Gate.

sync_meshkeys_gw.py
    Synchronisiert die ``peers``-Ordner mit den Git-Repos und lässt `fastd` danach die ``peers`` neu einlesen [#root]_.

.. [#root] Benötigt dazu Root-Rechte
