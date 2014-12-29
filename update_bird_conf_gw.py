#!/usr/bin/env python3

def update_bird_conf():
    '''
        Ziel des Scripts ist es, eine Konfiguration für bird zu generieren, damit das Gateway am icvpn teilnehmen kann.

        Diese Script läuft periodisch, um den jeweils aktuellen Stand aus icvpn Repository in der Konfiguration abzubilden.
        Danach wird bird neu gestartet.
    '''

    from photon.util.files import read_file
    from common import pinit

    # Photon Instanz, und deren Settings aus common.pinit holen
    photon, settings = pinit('update_bird_conf', verbose=True)

    # Photon dazu veranlassen, jeweils einen ``git_handler`` mit den entsprechenden Werten aus seinen Settings für
    # die 'scripts' und für 'meta' zu starten. Auf diese Handler-Funktionen jeweils ``_pull()`` in dem Repo aufrufen (a.k.a `git pull`)
    for repo in ['scripts', 'meta']:
        photon.git_handler(settings['icvpn']['bird'][repo]['local'], remote_url=settings['icvpn']['bird'][repo]['remote'])._pull()

    # Zwei verschiedene Protokoll-Versionen bedeutet: Zwei verschiedene bird-Daemons mit jeweils einer Konfiguration.
    # Dazu die Felder ``exec`` und ``conf`` unter ``ip_ver`` in den Settings
    for ip_ver in settings['icvpn']['bird']['ip_ver']:

        # Photon legt unter ``bc`` einen ``template_handler`` ab.
        # Der Inhalt der Templates ist nur eine Variable: ``conf``
        bc = photon.template_handler('${conf}')

        # Mit ``photon.m`` wird das ``mkbgp`` Script aus dem icvpn-meta Repository aufgerufen
        # Im ``cmdd`` steht der eigentliche Aufruf (``cmd``) sowie der Pfad (``cwd``) im dem das Kommando ausgeführt wird
        # Schlägt das Kommando fehl, schaltet Photon den ganzen Python-Interpreter mit hübsch Fehlermeldung ab.
        # Ansonsten: Vor Augen halten, was hier passiert: Im Python 3 Interpreter innerhalb einer Shell läuft diese Script hier,
        # welches eine weitere Shell startet um darin ein Python2 Script auszuführen. Dazu noch ohne den Code vorher zu prüfen..
        # Der Ausgabe-String (``get('out')``) wird jedenfalls mit ``bc.sub`` unter dem Namen ``conf`` abgelegt.
        bc.sub = dict(conf=photon.m(
            'generating ip_ver%s bgp conf' %(ip_ver),
            cmdd=dict(cmd='./mkbgp -f bird -%s -s %s -x mainz -x wiesbaden -d ebgp_ic' %(ip_ver, settings['icvpn']['bird']['meta']['local']), cwd=settings['icvpn']['bird']['scripts']['local'])
        ).get('out'))

        # ``bc.sub`` setzt alle hinterlegten Werte (``conf``) in das Template ein und gibt dieses als String zurück.
        # Hat sich dieser gegenüber der momentan aktiven Konfiguration (``read_file``) geändert (``!=``)..
        conf = settings['icvpn']['bird']['ip_ver'][ip_ver]['conf']
        if bc.sub != read_file(conf):
            # .. wird die Konfiguration danach mit der aus dem Template-Handler (``bc.write``) ersetzt (``append=False``).
            bc.write(conf, append=False)

            # Leider lässt sich bird nicht mittels Signalen dazu veranlassen die Konfiguration einzulesen.
            # Also wird mit ``photon.m`` auf den ``service`` Befehl vom Betriebssystem drunter zurückgegriffen:
            # ... besser doch die harte Tour (restart) ...
            photon.m(
                'restarting ip_ver%s daemon' %(ip_ver),
                cmdd=dict(cmd='sudo service %s restart' %(settings['icvpn']['bird']['ip_ver'][ip_ver]['exec']))
            )

if __name__ == '__main__':
    update_bird_conf()
