#!/usr/bin/env python3

def update_icdns_conf():
    '''
        Jetzt mit Kommentaren!

        Ziel des Scripts ist es, eine Konfiguration für bird zu generieren, damit das Gateway am icvpn teilnehmen kann.

        Diese Script läuft periodisch, um den jeweils aktuellen Stand aus icvpn Repository in der Konfiguration abzubilden.
        Danach wird bird neu gestartet.
    '''

    from photon.util.files import read_file
    from common import pinit

    # Photon Instanz, und deren Settings aus common.pinit holen
    p, s = pinit('update_icdns_conf', verbose=True)

    # Photon (``p``) dazu veranlassen, jeweils einen ``git_handler`` mit den entsprechenden Werten aus seinen Settings (``s``) für
    # die 'scripts' und für 'meta' zu starten. Auf diese Handler-Funktionen jeweils ``_pull()`` in dem Repo aufrufen (a.k.a `git pull`)
    for r in ['scripts', 'meta']:
        p.git_handler(s['icvpn']['icdns'][r]['local'], remote_url=s['icvpn']['icdns'][r]['remote'])._pull()

    # Photon legt unter ``bc`` einen ``template_handler`` ab.
    # Der Inhalt der Templates ist nur eine Variable: ``conf``
    bc = p.template_handler('${conf}')

    # Mit ``p.m`` wird das ``mkbgp`` Script aus dem icvpn-meta Repository aufgerufen
    # Im ``cmdd`` steht der eigentliche Aufruf (``cmd``) sowie der Pfad (``cwd``) im dem das Kommando ausgeführt wird
    # Schlägt das Kommando fehl, schaltet Photon den ganzen Python-Interpreter mit hübsch Fehlermeldung ab.
    # Ansonsten: Vor Augen halten, was hier passiert: Im Python 3 Interpreter innerhalb einer Shell läuft diese Script hier,
    # welches eine weitere Shell startet um darin ein Python2 Script auszuführen. Dazu noch ohne den Code vorher zu prüfen..
    # Der Ausgabe-String (``get('out')``) wird jedenfalls mit ``bc.sub`` unter dem Namen ``conf`` abgelegt.
    bc.sub = dict(conf=p.m(
        'genarating dns conf',
        cmdd=dict(cmd='./mkdns -f bind -s %s -x mainz -x wiesbaden' %(s['icvpn']['icdns']['meta']['local']), cwd=s['icvpn']['icdns']['scripts']['local'])
    ).get('out'))

    # ``bc.sub`` setzt alle hinterlegten Werte (``conf``) in das Template ein und gibt dieses als String zurück.
    # Hat sich dieser gegenüber der momentan aktiven Konfiguration (``read_file``) geändert (``!=``)..
    conf = s['icvpn']['icdns']['conf']
    if bc.sub != read_file(conf):
        # .. wird die Konfiguration danach mit der aus dem Template-Handler (``bc.write``) ersetzt (``append=False``).
        bc.write(conf, append=False)

        # reload
        p.m(
            'reloading dns daemon',
            cmdd=dict(cmd='sudo rndc reload')
        )

if __name__ == '__main__':
    update_icdns_conf()
