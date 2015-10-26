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


Diensteserver
^^^^^^^^^^^^^

mirror_openwrt_repo_srv.py
    Erstellt einen OpenWRT Mirror mit Hilfe von **lftp**.

    Sollte nur auf Service Maschinen laufen. Benötigt viel Speicherplatz.

    Allein für stable Barrier Breaker werden ca. 36 GiB benötigt.
