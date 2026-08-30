"""FROZEN literalness gold for the force-dynamic reader's sense/attachment gate.
   (problem: the_force_dynamic_reader_needs_a_literal_sense_and_attachment_gate)

The gold is the DETERMINISTIC seed=20260830 sample (experiments/_dump_literalness_candidates.py) with a
hand adjudication per index. EVERY drawn clause was adjudicated (no cherry-picking within the draw); the
sample is stratified by source only (UD-EWT web = figurative-rich; MCScript2 = literal-rich) so both
classes are represented -- disclosed.

LABELS (the research drill's three-way, made four for the abstract-non-force residue):
  A = LITERAL_PHYSICAL  -- a literal physical event: an affector applies force to / moves / contacts a
                           CONCRETE physical patient (slam into Biloxi, cut the vegetables, pour water,
                           put the dish in the oven). The force-dynamic reader SHOULD engage. engage=True.
  B = NONPHYS_FORCE     -- a genuine force/causation event at the SOCIAL/PSYCH/INSTITUTIONAL level (pull
                           back forces, arrest the dealer, dispatch a person). Real force, NOT physical
                           -> a future social-force reader's job; the PHYSICAL reader abstains. engage=False.
  C = FIGURATIVE_IDIOM  -- conventional/lexicalized-figurative or idiom; NO force simulation (fell in love,
                           throw a party, break the color barrier, blown away, move overseas=relocate).
                           This is the graded-simulation OFF bucket + the residual over-fire class. engage=False.
  O = NONPHYS_OTHER     -- non-physical, non-force: abstract change / communication / configuration
                           (increase poverty, send comments, change the wording). engage=False.

BINARY BAR: the reader should ENGAGE iff label == 'A'.

*** SINGLE-ADJUDICATOR CAVEAT (stated, not hidden): one adjudicator (this solver) labeled all 150.
    Literal-vs-figurative for physical verbs is a high-agreement task (cf. VU Amsterdam Metaphor Corpus
    IAA), but a SECOND independent adjudicator is the right follow-on (noted in SOLVED.md NEXT STEPS).
    The A-vs-not-A boundary was the adjudication axis; B/C/O sub-splits do not affect the binary score. ***

ASCII only.
"""
from __future__ import annotations

import os
import random
import sys
from typing import Dict, List

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._literalness_data import iter_udewt_clauses, iter_mcscript_clauses

SEED = 20260830
N_UDEWT = 90
N_MCS = 60

# index (1-based, matching the dump) -> label. Adjudicated 2026-08-30.
LABELS: Dict[int, str] = {
    # ---- UD-EWT (1..90) ----
    1: "O", 2: "C", 3: "A", 4: "O", 5: "O", 6: "C", 7: "C", 8: "C", 9: "O", 10: "A",
    11: "A", 12: "A", 13: "O", 14: "O", 15: "C", 16: "A", 17: "A", 18: "A", 19: "C", 20: "O",
    21: "C", 22: "B", 23: "O", 24: "C", 25: "C", 26: "O", 27: "C", 28: "A", 29: "C", 30: "O",
    31: "A", 32: "C", 33: "O", 34: "O", 35: "O", 36: "C", 37: "C", 38: "O", 39: "A", 40: "O",
    41: "A", 42: "A", 43: "C", 44: "C", 45: "O", 46: "A", 47: "A", 48: "B", 49: "A", 50: "B",
    51: "C", 52: "A", 53: "C", 54: "B", 55: "A", 56: "A", 57: "C", 58: "C", 59: "A", 60: "C",
    61: "C", 62: "C", 63: "C", 64: "C", 65: "A", 66: "B", 67: "C", 68: "C", 69: "O", 70: "C",
    71: "C", 72: "O", 73: "O", 74: "A", 75: "A", 76: "A", 77: "C", 78: "A", 79: "C", 80: "A",
    81: "O", 82: "O", 83: "A", 84: "O", 85: "A", 86: "A", 87: "C", 88: "A", 89: "A", 90: "A",
    # ---- MCScript2 (91..150) ----
    91: "A", 92: "A", 93: "A", 94: "A", 95: "A", 96: "A", 97: "A", 98: "A", 99: "A", 100: "A",
    101: "A", 102: "O", 103: "A", 104: "A", 105: "A", 106: "A", 107: "A", 108: "A", 109: "A", 110: "A",
    111: "A", 112: "A", 113: "A", 114: "A", 115: "A", 116: "A", 117: "C", 118: "A", 119: "A", 120: "A",
    121: "A", 122: "A", 123: "A", 124: "A", 125: "A", 126: "A", 127: "A", 128: "A", 129: "A", 130: "A",
    131: "A", 132: "C", 133: "A", 134: "A", 135: "A", 136: "C", 137: "A", 138: "A", 139: "A", 140: "A",
    141: "A", 142: "O", 143: "A", 144: "A", 145: "A", 146: "A", 147: "A", 148: "O", 149: "O", 150: "A",
}


def load_gold() -> List[dict]:
    """Regenerate the exact seed=20260830 sample and attach the frozen label per index."""
    rng = random.Random(SEED)
    ud = list(iter_udewt_clauses())
    rng.shuffle(ud)
    ud_s = ud[:N_UDEWT]
    mcs = list(iter_mcscript_clauses(max_texts=400))
    rng.shuffle(mcs)
    mcs_s = mcs[:N_MCS]
    out = []
    for i, cl in enumerate(ud_s + mcs_s, start=1):
        lab = LABELS[i]
        cl = dict(cl)
        cl["idx"] = i
        cl["label"] = lab
        cl["engage_gold"] = (lab == "A")
        out.append(cl)
    return out


if __name__ == "__main__":
    g = load_gold()
    from collections import Counter
    c = Counter(x["label"] for x in g)
    pos = sum(x["engage_gold"] for x in g)
    print(f"gold n={len(g)}  labels={dict(c)}  positive(A)={pos}  negative={len(g)-pos}")
    by_src = Counter((x["source"], x["label"] == "A") for x in g)
    print("by source (source, is_A):", dict(by_src))
