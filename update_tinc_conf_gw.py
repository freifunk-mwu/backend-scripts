#!/usr/bin/env python3

def update_tinc_conf():
    '''
        Jetzt mit Kommentaren!

        Ziel des Scripts ist es, eine Konfiguration für tinc zu generieren, damit das Gateway am icvpn teilnehmen kann.

        Diese Script läuft periodisch, um den jeweils aktuellen Stand aus icvpn Repository in der Konfiguration abzubilden.
        Danach wird tinc dazu veranlasst, die Konfiguration neu einzulesen.
    '''

    from os import listdir, path
    from photon.util.files import read_file
    from common import pinit

    # Photon Instanz, und deren Settings aus common.pinit holen
    p, s = pinit('update_tinc_conf', verbose=True)

    # Photon (``p``) dazu veranlassen, einen ``git_handler`` mit Werten aus seinen Settings (``s``) zu starten
    # Mit den Parametern ``local`` weiss der Handler bescheid, wo er das Repo ablegen/wiederfinden soll,
    # Die ``remote_url`` wird dazu genutzt, das Repository von dieser Adresse zu klonen, liegt bereits unter
    # ``local`` ein Repository wird für alle Aktionen die darin hinterlegte Adresse genutzt
    # (== die ``remote_url`` mit der initial geklont wurde)
    # Erst danach wird die Handler-Funktion ``_pull()`` in dem Repo aufgerufen (a.k.a `git pull`)
    p.git_handler(s['icvpn']['tinc']['local'], remote_url=s['icvpn']['tinc']['remote'])._pull()

    # Das Gateway muss wissen, wie es sich dem icvpn gegenüber zu melden hat.
    # In den Settings von Photon (``s``) steht unter ``['icvpn']['tinc']['iamdb']``
    # eine Zuordnung der Hostnamen zu den entsprechenden Namen.
    # Das Settings Modul kann auf Keywords in der Konfigurationsdatei reagieren, z.B. wird der Hostname
    # unter ``['common']['hostname']`` in den Settings abgelegt. Diesen nutzen wir um unseren icvpn-Namen
    # aus der Zuordnung zu erhalten: ``iam``. Wird nichts gefunden (``iam == None``) darf Photon den
    # Gehsteig hochklappen: Fehlermeldungen werfen und den ganzen Python-Interpreter abschalten (``state=True``)
    iam = s['icvpn']['tinc']['iamdb'][s['common']['hostname']] if s['common']['hostname'] in s['icvpn']['tinc']['iamdb'] else None
    if not iam: p.m('Host not present in configuration!', more=dict(host=s['common']['hostname']), state=True)

    # Wohin soll sich tinc verbinden? Dies steht in den tinc-Keys der anderen icvpn Teilnehmer.
    # Ein Key kann aber auf mehrere Adressen verweisen, sollte aber nur einmal in der Konfiguration auftauchen.
    # Um doppelte Einträge zu vermeiden wird ein set genutzt.
    connects = set()

    # Einmal durch alle tinc-Keys aus dem Repository gehen
    for key in listdir(s['icvpn']['tinc']['hosts']):
        # Den eigenen Key ignorieren
        if key.lower() != iam.lower():
            # Den Key mit der Photon-Hilfs-Funktion ``read_file`` einlesen, danach zeilenweise (``split``) durchgehen
            for line in read_file(path.join(s['icvpn']['tinc']['hosts'], key)).split('\n'):
                # Beginnt eine Zeile innerhalb des Keys mit ``address`` oder ``Address`` (oder z.B. mit ``AdDrEsS`` ;)) ..
                if line.lower().startswith('address'):
                    # .. kommt der Dateiname des Keys in das set
                    connects.add('ConnectTo = %s' %(key))

    # Wir haben alles was wir brauchen.
    # Photon legt unter ``tc`` einen ``template_handler`` ab. Dieser liest beim Start das
    # ``tinc.conf.tpl`` im Unterordner ``common`` ein und hinterlegt die oben ermittelten Werte (``fields``).
    # Die ``connects`` werden zum String gewandelt, indem alle
    # Elemente im Set mit einer Leerzeile verbunden werden (``'\n'.join``)..
    tc = p.template_handler(
        path.join(path.dirname(__file__), 'common', 'tinc.conf.tpl'),
        fields=dict(
            iam=iam,
            interface=s['icvpn']['interface'],
            connects='\n'.join(sorted(connects))
        )
    )

    # ``tc.sub`` setzt alle unter ``fields`` hinterlegte Werte in das Template ein und gibt dieses als String zurück.
    # Hat sich dieser gegenüber der momentan aktiven Konfiguration (``read_file``) geändert (``!=``)..
    if tc.sub != read_file(s['icvpn']['tinc']['conf']):
        # .. wird die Konfiguration danach mit der aus dem Template-Handler (``bc.write``) ersetzt (``append=False``).
        tc.write(s['icvpn']['tinc']['conf'], append=False)

        # Der ``signal_handler`` liest beim Start das angegebene ``pidfile`` ein, und ermittelt so
        # die Prozess-ID
        tinc = p.signal_handler(s['icvpn']['tinc']['pidfile'])
        # Letzter Schritt: dem Prozess im Signal-Handler ein ``SIGHUP`` schicken
        # tinc liest daraufhin die Konfiguration neu ein, und passt seine Verbindungen entsprechend an..
        # (steht zumindest so in der man-page ;)
        tinc.hup

if __name__ == '__main__':
    update_tinc_conf()
