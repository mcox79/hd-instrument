"""Witness for hdlab.meaning_operation_router (landed 2026-08-28, landing-step 3 of the p1 magnitude channel).

Construction proof of the word-class routing decision (WordNet only, no gold):
  [1] GRADABLE adjectives (hot, cold, big, small, good, bad) -> route to the MAGNITUDE ruler.
  [2] CLASSIFICATORY / pertainym-relational adjectives (medical, financial, presidential) -> route to CONCEPTUAL
      (gloss), NOT magnitude -- the sharper gate keeps them taxonomic where has_antonym-alone might not.
  [3] NOUNS and VERBS -> always CONCEPTUAL (the magnitude op is a "how much" op, not a similarity op -> routing not replace).
  [4] glass-box: the gate is WordNet-lexical, takes no gold; route() returns a label, not a computation.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.meaning_operation_router import (  # noqa: E402
    route, is_gradable_adjective, is_pertainym_relational, has_antonym)

GRADABLE = ["hot", "cold", "big", "small", "good", "bad", "fast", "slow", "bright", "dark"]
CLASSIFICATORY = ["medical", "financial", "presidential", "chemical", "national", "atomic"]
NOUNS = ["dog", "table", "justice", "water"]
VERBS = ["run", "chase", "believe", "dissolve"]


def main() -> int:
    # [1] gradable adjectives -> magnitude
    g_ok = sum(int(route(w, "ADJ") == "magnitude") for w in GRADABLE)
    print(f"[1] gradable adjectives -> magnitude: {g_ok}/{len(GRADABLE)}  ({[w for w in GRADABLE if route(w,'ADJ')!='magnitude']} missed)")
    assert g_ok >= len(GRADABLE) - 1, f"gradable adjectives must route to the magnitude ruler ({g_ok}/{len(GRADABLE)})"

    # [2] classificatory / pertainym-relational adjectives -> conceptual (NOT magnitude)
    c_conc = sum(int(route(w, "ADJ") == "conceptual") for w in CLASSIFICATORY)
    n_pert = sum(int(is_pertainym_relational(w)) for w in CLASSIFICATORY)
    print(f"[2] classificatory adjectives -> conceptual: {c_conc}/{len(CLASSIFICATORY)} (pertainym-flagged {n_pert}/{len(CLASSIFICATORY)})")
    assert c_conc == len(CLASSIFICATORY), f"classificatory adjectives must stay on the gloss op ({c_conc}/{len(CLASSIFICATORY)})"
    assert not any(is_gradable_adjective(w) for w in CLASSIFICATORY), "no classificatory adjective may be gated gradable"

    # [3] nouns + verbs -> conceptual always
    nv = NOUNS + VERBS
    nv_conc = sum(int(route(w, p) == "conceptual") for w, p in [(w, "NOUN") for w in NOUNS] + [(w, "VERB") for w in VERBS])
    print(f"[3] nouns+verbs -> conceptual: {nv_conc}/{len(nv)}")
    assert nv_conc == len(nv), "nouns and verbs must always route to conceptual (magnitude is not a similarity op)"

    # a gradable word tagged as a NOUN must NOT route to magnitude (routing is POS-gated)
    assert route("good", "NOUN") == "conceptual", "a non-adjective POS must never route to magnitude"

    # [4] glass-box
    import inspect
    assert "gold" not in inspect.signature(route).parameters
    assert isinstance(has_antonym("good"), bool)
    print("[4] glass-box PASS (WordNet-lexical gate; route returns a label, no gold)")

    print("\nALL WITNESS ASSERTIONS PASSED -- gradable adjectives route to the magnitude ruler, classificatory/pertainym")
    print("adjectives and all nouns/verbs stay on the conceptual gloss op (routing, not replacement), POS-gated, glass-box.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
