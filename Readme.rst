backend-scripts
===============

Hier werden Skripte gesammelt, die auf den Gates zum Einsatz kommen.

_etc/dot2json.pl
    Wandelt ein dot file, wie es als Topo aus tinc fällt, in ein json file, wie force directed graph (D3) es erwartet.
    Nutzt nur stdin und stdout.

----

`Photon <http://photon.readthedocs.org>`_ Scripte
-------------------------------------------------

Die Endungen der Scripte beschreiben auf welchem Typ von Maschine diese i.d.R. laufen sollen:

:_gw: Gateways
:_srv: Diensteserver
:_all: Alle (Gateways, Diensteserver, Buildserver, Webserver, ...)

Installation/Betrieb
^^^^^^^^^^^^^^^^^^^^

Die `Installation <http://gluon-gateway-doku.readthedocs.org/de/latest/operations/scripts.html>`_ ist Teil der Gluon Gateway Dokumentation.

common/ffmwu_defaults.yaml
    Die Konfiguration der Backend Scripte für **ffmwu**.

    Sollte man lokale Änderungen vornehmen wollen, nutzt man die nach dem ersten Start von Photon_ erstellte *ffmwu_config.yaml* und ersetzt die entsprechenden Werte.

bootstrap_git_all.py
    Zu Beginn sollte man (einmalig) Git einrichten, so dass die anderen Skripte funkionieren.

        Erzeugt ein ssh-Keypaar (*hostname_rsa*, *hostname_rsa.pub*), und hinterlegt diesen für eiheitlichen Zugriff auf Github in die ``~/.ssh/config``. Nicht vergessen, den Schlüssel dem `Nutzer ffmwu <https://github.com/freifunkmwu>`_ hinterlegen. Dieser hat über die `Gruppe machines <https://github.com/orgs/freifunk-mwu/teams/machines>`_ Zugriff auf die benötigten Repositories

    Repo-Zugriffs-Syntax: ``ssh://github_mwu/freifunk-mwu/backend-scripts.git``

deploy_ssh_all.py
    Danach kann man die fehlenden pubkeys der Kollegen nachtragen.

    Setzt noch nicht vorhandene Schlüssel aus dem `gateway-configs Repository <https://github.com/freifunk-mwu/gateway-configs>`_ in die ``~/.ssh/authorized_keys``.

    .. note::
        Obwohl theoretisch immer Backups angelegt werden, schaut es in der Praxis meist anders aus.

        Es kann auch nicht verhindert werden, dass man sich aus dem eigenen Server aussperrt. Deshalb immer **davor** eine zweite ssh Verbindung öffnen, und **danach** *immer* die Ergebnisse überprüfen!

Gateways
^^^^^^^^

sync_meshkeys_gw.py
    Synchronisiert die ``peers``-Ordner mit den Git-Repos und lässt `fastd` danach die ``peers`` neu einlesen [#root]_.

check_exitvpn_gw.py
    Setzt das `BATMAN` Server Flag [#root]_ und startet/stoppt den `isc-dhcp-server` [#root]_  je nach Erreichbarkeit von gegebenen Hosts durch das ExitVPN.

Intercity VPN
^^^^^^^^^^^^^

update_tinc_conf_gw.py
    Holt updates aus dem `freifunk icvpn repo <https://github.com/freifunk/icvpn>`_, und erstellt eine Konfiguration für tinc.

    Startet tinc neu [#root]_, bei einer Änderung in der Konfiguration.

update_bird_conf_gw.py
    Holt updates aus dem `freifunk icvpn-meta repo <https://github.com/freifunk/icvpn-meta>`_ und erstellt mit den Tools aus dem `freifunk icvpn-scripts repo <https://github.com/freifunk/icvpn-scripts>`_ eine Konfiguration für bird.

    Startet bird neu [#root]_, bei einer Änderung in der Konfiguration.

update_bind_conf_gw.py
    Holt updates aus dem `freifunk icvpn-meta repo`_ und erstellt mit den Tools aus dem `freifunk icvpn-scripts repo`_ eine Konfiguration für bind.

    Startet bind neu [#root]_, bei einer Änderung in der Konfiguration.

Diensteserver
^^^^^^^^^^^^^

mirror_openwrt_repo_srv.py
    Erstellt einen OpenWRT Mirror mit Hilfe von **lftp**.

    Sollte nur auf Service Maschinen laufen. Benötigt viel Speicherplatz.

    Allein für stable Barrier Breaker werden ca. 36 GiB benötigt.

sync_ffapi_srv.py
    Synchronisiert die Freifunk-API Files mit ihren jeweiligen Repos (`mz <https://github.com/freifunk-mwu/ffapi-mainz>`_; `wi <https://github.com/freifunk-mwu/ffapi-wiesbaden>`_).

Weitere/Alle Maschinen
^^^^^^^^^^^^^^^^^^^^^^

snapshot_configs_all.py
    Füttert das `gateway-configs Repository`_ mit Konfigurationsdateien frisch vom Gate.

gen_website_all.py
    Generiert eine einfache Webseite, und einen Status mit rudimentären Informationen.

draw_traffic_all.py
    Zeichnet `vnstat <http://humdi.net/vnstat/>`_  Graphen, und klebt diese in eine Webseite.

    Ist nur sinnvoll auf Maschinen mit Verbindung ins Mesh (Gateways, Diensteserver).

    Nicht vorhandene Interfaces werden übersprungen, nicht vorhandene vnstat Datenbanken werden erzeugt [#root]_

nagg_exitvpn_accouts_all.py
    Geht die Liste der ExitVPN Accounts im `gateway-configs Repository`_ durch und schickt Mails.

    Entweder als Wochenbericht, oder täglich, wenn ein Account droht auszulaufen.

    Sollte nur auf einer einzelnen Maschine laufen

.. [#root] Benötigt dazu Root-Rechte
