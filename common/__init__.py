
def pinit(mname, verbose=True):

    from os import path
    from photon import Photon

    cf = path.dirname(__file__)
    p = Photon(
        path.join(cf, 'ffmwu_defaults.yaml'),
        config=path.join(cf, 'ffmwu_config.yaml'),
        meta='%s_meta.json' %(mname),
        verbose=verbose
    )
    return p, p.settings.get
