Backend Scripts
===============

Hier werden Skripte gesammelt, die auf den Gates zum Einsatz kommen.

_etc/dot2json.pl
   Wandelt ein dot file, wie es als Topo aus tinc fällt, in ein json file, wie force directed graph (D3) es erwartet.

   Nutzt nur stdin und stdout.

----

`Photon <http://photon.readthedocs.org>`_ Skripte
-------------------------------------------------

Die Endungen der Scripte beschreiben auf welchem Typ von Maschine diese i.d.R. laufen sollen:

:_gw: Gateways
:_srv: Diensteserver
:_all: Alle (Gateways, Diensteserver, Buildserver, Webserver, ...)

Installation/Betrieb
^^^^^^^^^^^^^^^^^^^^

Die `Installation <http://gluon-gateway-doku.readthedocs.org/de/latest/operations/scripts.html>`_ ist Teil der Gluon Gateway Dokumentation.

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

Diensteserver
^^^^^^^^^^^^^

mirror_openwrt_repo_srv.py
    Erstellt einen OpenWRT Mirror mit Hilfe von **lftp**.

    Sollte nur auf Service Maschinen laufen. Benötigt viel Speicherplatz.

    Allein für stable Barrier Breaker werden ca. 36 GiB benötigt.

sync_ffapi_srv.py
    Synchronisiert die Freifunk-API Files mit ihren jeweiligen Repos (`mz <https://github.com/freifunk-mwu/ffapi-mainz>`_; `wi <https://github.com/freifunk-mwu/ffapi-wiesbaden>`_).
