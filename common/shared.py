
from photon import Photon

def init(mname, verbose=True):
    p = Photon(config='common/ffmwu_config.yaml', summary='common/ffmwu_summary.yaml', meta='%s_meta.json' %(mname), verbose=verbose)
    return p, p.settings.get
