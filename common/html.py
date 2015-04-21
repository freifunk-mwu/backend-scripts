
def page(photon, content, sub=None):
    from os import path
    from photon.util.locations import search_location, change_location
    from photon.util.system import get_timestamp, get_hostname

    settings = photon.settings.get
    pwd = path.dirname(__file__)

    out = path.join(settings['web']['output'], sub if sub else '', 'index.html')
    search_location(out, create_in=path.dirname(out))

    if sub: prfx, sub = '../', '&mdash; %s' %(sub)
    else:
        prfx, sub = './', ''
        change_location(path.join(pwd, 'static'), path.join(settings['web']['output'], 'static'))

    template = photon.template_handler(
        path.join(pwd, 'main.tpl'),
        fields=dict(
            hostname=get_hostname(),
            prfx=prfx,
            sub=sub,
            content=content,
            timestamp=get_timestamp()
        )
    )
    template.write(out, append=False)
