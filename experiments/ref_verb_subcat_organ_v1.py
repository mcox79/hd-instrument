"""ref_verb_subcat_organ_v1 -- RE-EXPORT SHIM. PROMOTED 2026-08-31 to hdlab/verb_subcat.py (Q111, the
landing of p2 wire_the_incremental_parser...). This reference file now re-exports the promoted organ so
existing importers keep working; edit hdlab/verb_subcat.py, not this file. NO external LLM.
"""
from __future__ import annotations

from hdlab.verb_subcat import (  # noqa: F401
    CONSERVATIVE_THR,
    TRANS_GATE_THR,
    patient_present,
    patient_present_prob,
    presence_features,
    suppress_patient,
    transitivity,
)

__all__ = ["transitivity", "presence_features", "patient_present_prob", "patient_present",
           "suppress_patient", "CONSERVATIVE_THR", "TRANS_GATE_THR"]


if __name__ == "__main__":
    t1 = "the man arrived at the station".split(); p1 = ["DET", "NOUN", "VERB", "ADP", "DET", "NOUN"]
    t2 = "the dog chased the cat".split(); p2 = ["DET", "NOUN", "VERB", "DET", "NOUN"]
    print("arrive+PP  prob=%.3f present=%s" % (patient_present_prob(t1, p1, 3, 6), patient_present(t1, p1, 3, 6)))
    print("chased SVO prob=%.3f present=%s" % (patient_present_prob(t2, p2, 3, 5), patient_present(t2, p2, 3, 5)))
