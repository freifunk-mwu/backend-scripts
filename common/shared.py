
from os import path
from photon import Photon

def init(mname, verbose=True):
    cf = path.dirname(__file__)
    p = Photon(
        path.join(cf, 'ffmwu_defaults.yaml'),
        config=path.join(cf, 'ffmwu_config.yaml'),
        meta='%s_meta.json' %(mname),
        verbose=verbose
    )
    return p, p.settings
