
def page(p, content, sub=None):
    from os import path
    from photon.util.locations import search_location, change_location
    from photon.util.system import get_timestamp, get_hostname

    s = p.settings.get
    dnf = path.dirname(__file__)

    out = path.join(s['web']['output'], sub if sub else '', 'index.html')
    search_location(out, create_in=path.dirname(out))

    if sub: prfx, sub = '../', '&mdash; %s' %(sub)
    else:
        prfx, sub = './', ''
        change_location(path.join(dnf, 'static'), path.join(s['web']['output'], 'static'))

    t = p.template_handler(
        path.join(dnf, 'main.tpl'),
        fields=dict(
            hostname=get_hostname(),
            prfx=prfx,
            sub=sub,
            content=content,
            timestamp=get_timestamp()
        )
    )
    t.write(out, append=False)
