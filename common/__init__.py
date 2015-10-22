'''
**common/ffmwu_defaults.yaml**

.. literalinclude:: ../../common/ffmwu_defaults.yaml
    :language: yaml
    :linenos:

'''
from os import path

from photon import Photon


def pinit(mname, verbose=True):
    '''
    Prepares a Photon Instance to load the ``ffmwu_defaults.yaml`` file.

    On the first run of Photon the ``ffmwu_config.yaml`` file is generated, so
    custom changes can be applied here.
    '''
    cwd = path.dirname(__file__)
    photon = Photon(
        path.join(cwd, 'ffmwu_defaults.yaml'),
        config=path.join(cwd, 'ffmwu_config.yaml'),
        meta='%s_meta.json' % (mname),
        verbose=verbose
    )
    return photon, photon.settings.get
