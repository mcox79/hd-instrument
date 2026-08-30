"""perceptual_access_ledger PROMOTED 2026-08-30 -> hdlab/perceptual_access_ledger.py.

The observation-cue front-end (who-witnessed-what: the ToM belief-update gate). Re-export shim so the
witness + the exp_perceptual_access_* cells import the SAME promoted core. The spaCy parse-based
extraction path stays LAZY (no hard hdlab dependency; the regex patterns are the spaCy-free core);
replacing the spaCy proxy with coref/situation-organ consumption is a noted follow-on.
"""
from hdlab.perceptual_access_ledger import *          # noqa: F401,F403
from hdlab import perceptual_access_ledger as _pal
import sys as _sys

_self = _sys.modules[__name__]
for _n in dir(_pal):
    if not _n.startswith("__") and not hasattr(_self, _n):
        setattr(_self, _n, getattr(_pal, _n))
