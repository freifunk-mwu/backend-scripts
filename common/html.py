'''
**common/main.tpl**

.. literalinclude:: ../../common/main.tpl
    :language: html
    :linenos:
'''
from os import path

from photon.util.locations import change_location, search_location
from photon.util.system import get_hostname, get_timestamp


def page(photon, content, sub=None):
    '''
    Helps creating webpages by placing the **content** into the ``main.tpl``
    and write the output to ``web/output/`` **sub/** ``index.html``.
    '''

    settings = photon.settings.get
    pwd = path.dirname(__file__)

    out = path.join(
        settings['web']['output'],
        sub if sub else '',
        'index.html'
    )
    search_location(out, create_in=path.dirname(out))

    if sub:
        prfx, sub = '../', '&mdash; %s' % (sub)
    else:
        prfx, sub = './', ''
        change_location(
            path.join(pwd, 'static'),
            path.join(settings['web']['output'], 'static')
        )

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
