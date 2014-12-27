
def pinit(mname, verbose=True):

    from os import path
    from photon import Photon

    cwd = path.dirname(__file__)
    photon = Photon(
        path.join(cwd, 'ffmwu_defaults.yaml'),
        config=path.join(cwd, 'ffmwu_config.yaml'),
        meta='%s_meta.json' %(mname),
        verbose=verbose
    )
    return photon, photon.settings.get
