
from os import path
from photon import Photon

def init(mname, verbose=True):
    cf = path.dirname(__file__)
    p = Photon(
        config=path.join(cf, 'ffmwu_config.yaml'),
        summary=path.join(cf, 'ffmwu_summary.yaml'),
        meta='%s_meta.json' %(mname),
        verbose=verbose
    )
    return p, p.settings.get
