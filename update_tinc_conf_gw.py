#!/usr/bin/env python3

def update_tinc_conf():
    '''
        Ziel des Scripts ist es, eine Konfiguration für tinc zu generieren, damit das Gateway am icvpn teilnehmen kann.

        Diese Script läuft periodisch, um den jeweils aktuellen Stand aus icvpn Repository in der Konfiguration abzubilden.
        Danach wird tinc dazu veranlasst, die Konfiguration neu einzulesen.
    '''

    from os import listdir, path
    from photon.util.files import read_file
    from common import pinit

    # Photon Instanz, und deren Settings aus common.pinit holen
    photon, settings = pinit('update_tinc_conf', verbose=True)

    # Photon dazu veranlassen, einen ``git_handler`` mit Werten aus seinen Settings zu starten
    # Mit den Parametern ``local`` weiss der Handler bescheid, wo er das Repo ablegen/wiederfinden soll,
    # Die ``remote_url`` wird dazu genutzt, das Repository von dieser Adresse zu klonen, liegt bereits unter
    # ``local`` ein Repository wird für alle Aktionen die darin hinterlegte Adresse genutzt
    # (== die ``remote_url`` mit der initial geklont wurde)
    # Erst danach wird die Handler-Funktion ``_pull()`` in dem Repo aufgerufen (a.k.a `git pull`)
    photon.git_handler(settings['icvpn']['tinc']['local'], remote_url=settings['icvpn']['tinc']['remote'])._pull()

    # Das Gateway muss wissen, wie es sich dem icvpn gegenüber zu melden hat.
    # In den Settings von Photon (``settings``) steht unter ``['icvpn']['tinc']['iamdb']``
    # eine Zuordnung der Hostnamen zu den entsprechenden Namen.
    # Das Settings Modul kann auf Keywords in der Konfigurationsdatei reagieren, z.B. wird der Hostname
    # unter ``['common']['hostname']`` in den Settings abgelegt. Diesen nutzen wir um unseren icvpn-Namen
    # aus der Zuordnung zu erhalten: ``iam``. Wird nichts gefunden (``iam == None``) darf Photon den
    # Gehsteig hochklappen: Fehlermeldungen werfen und den ganzen Python-Interpreter abschalten (``state=True``)
    iam = settings['icvpn']['tinc']['iamdb'][settings['common']['hostname']] if settings['common']['hostname'] in settings['icvpn']['tinc']['iamdb'] else None
    if not iam: photon.m('Host not present in configuration!', more=dict(host=settings['common']['hostname']), state=True)

    # Wohin soll sich tinc verbinden? Dies steht in den tinc-Keys der anderen icvpn Teilnehmer.
    # Ein Key kann aber auf mehrere Adressen verweisen, sollte aber nur einmal in der Konfiguration auftauchen.
    # Um doppelte Einträge zu vermeiden wird ein set genutzt.
    connects = set()

    # Einmal durch alle tinc-Keys aus dem Repository gehen
    for key in listdir(settings['icvpn']['tinc']['hosts']):
        # Den eigenen Key ignorieren
        if key.lower() != iam.lower():
            # Den Key mit der Photon-Hilfs-Funktion ``read_file`` einlesen, danach zeilenweise (``split``) durchgehen
            for line in read_file(path.join(settings['icvpn']['tinc']['hosts'], key)).split('\n'):
                # Beginnt eine Zeile innerhalb des Keys mit ``address`` oder ``Address`` (oder z.B. mit ``AdDrEsS`` ;)) ..
                if line.lower().startswith('address'):
                    # .. kommt der Dateiname des Keys in das set
                    connects.add('ConnectTo = %s' %(key))

    # Wir haben alles was wir brauchen.
    # Photon legt unter ``tc`` einen ``template_handler`` ab. Dieser liest beim Start das
    # ``tinc.conf.tpl`` im Unterordner ``common`` ein und hinterlegt die oben ermittelten Werte (``fields``).
    # Die ``connects`` werden zum String gewandelt, indem alle
    # Elemente im Set mit einer Leerzeile verbunden werden (``'\n'.join``)..
    tc = photon.template_handler(
        path.join(path.dirname(__file__), 'common', 'tinc.conf.tpl'),
        fields=dict(
            iam=iam,
            interface=settings['icvpn']['interface'],
            connects='\n'.join(sorted(connects))
        )
    )

    # ``tc.sub`` setzt alle unter ``fields`` hinterlegte Werte in das Template ein und gibt dieses als String zurück.
    # Hat sich dieser gegenüber der momentan aktiven Konfiguration (``read_file``) geändert (``!=``)..
    if tc.sub != read_file(settings['icvpn']['tinc']['conf']):
        # .. wird die Konfiguration danach mit der aus dem Template-Handler (``bc.write``) ersetzt (``append=False``).
        tc.write(settings['icvpn']['tinc']['conf'], append=False)

        # Offenbar ist leider nur ein restart die wirklich stabile Variante,
        # tinc zum Beachten der neuen config zu bringen _und_ überhaupt
        # sicherzustellen, dass tinc auch läuft.
        photon.m(
            'restarting tinc daemon',
            cmdd=dict(cmd='sudo service %s restart' %(settings['icvpn']['tinc']['exec']))
        )

if __name__ == '__main__':
    update_tinc_conf()
