#!/usr/bin/env python3

def update_icdns_conf():
    '''
        Ziel des Scripts ist es, eine Konfiguration für bind zu generieren, damit das Gateway am icvpn teilnehmen kann.

        Diese Script läuft periodisch, um den jeweils aktuellen Stand aus icvpn Repository in der Konfiguration abzubilden.
        Danach wird bind dazu veranlasst die Konfiguration neu einzulesen und zu laden.
    '''

    from photon.util.files import read_file
    from common import pinit

    # Photon Instanz, und deren Settings aus common.pinit holen
    photon, settings = pinit('update_icdns_conf', verbose=True)

    # Photon dazu veranlassen, jeweils einen ``git_handler`` mit den entsprechenden Werten aus seinen Settings für
    # die 'scripts' und für 'meta' zu starten. Auf diese Handler-Funktionen jeweils ``_pull()`` in dem Repo aufrufen (a.k.a `git pull`)
    for repo in ['scripts', 'meta']:
        photon.git_handler(settings['icvpn']['icdns'][repo]['local'], remote_url=settings['icvpn']['icdns'][repo]['remote'])._pull()

    # Photon legt unter ``bc`` einen ``template_handler`` ab.
    # Der Inhalt der Templates ist nur eine Variable: ``conf``
    bc = photon.template_handler('${conf}')

    # Mit ``photon.m`` wird das ``mkdns`` Script aus dem icvpn-meta Repository aufgerufen
    # Im ``cmdd`` steht der eigentliche Aufruf (``cmd``) sowie der Pfad (``cwd``) im dem das Kommando ausgeführt wird
    # Schlägt das Kommando fehl, schaltet Photon den ganzen Python-Interpreter mit hübsch Fehlermeldung ab.
    # Ansonsten: Vor Augen halten, was hier passiert: Im Python 3 Interpreter innerhalb einer Shell läuft diese Script hier,
    # welches eine weitere Shell startet um darin ein Python2 Script auszuführen. Dazu noch ohne den Code vorher zu prüfen..
    # Der Ausgabe-String (``get('out')``) wird jedenfalls mit ``bc.sub`` unter dem Namen ``conf`` abgelegt.
    bc.sub = dict(conf=photon.m(
        'genarating dns conf',
        cmdd=dict(cmd='./mkdns -f bind -s %s -x mainz -x wiesbaden' %(settings['icvpn']['icdns']['meta']['local']), cwd=settings['icvpn']['icdns']['scripts']['local'])
    ).get('out'))

    # ``bc.sub`` setzt alle hinterlegten Werte (``conf``) in das Template ein und gibt dieses als String zurück.
    # Hat sich dieser gegenüber der momentan aktiven Konfiguration (``read_file``) geändert (``!=``)..
    conf = settings['icvpn']['icdns']['conf']
    if bc.sub != read_file(conf):
        # .. wird die Konfiguration danach mit der aus dem Template-Handler (``bc.write``) ersetzt (``append=False``).
        bc.write(conf, append=False)

        # reload
        photon.m(
            'reloading dns daemon',
            cmdd=dict(cmd='sudo rndc reload')
        )

if __name__ == '__main__':
    update_icdns_conf()
