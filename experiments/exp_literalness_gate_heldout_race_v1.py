"""HELD-OUT GENERALIZATION test for the literalness gate on a THIRD, unseen modern genre.
   (problem: the_force_dynamic_reader_needs_a_literal_sense_and_attachment_gate)

The primary gold (exp_literalness_gate_v1) is UD-EWT web + MCScript2 narrative. This scores the SAME gate,
with ZERO parameters re-tuned, on RACE (modern reading-comprehension passages -- essay/expository prose, a
DIFFERENT genre with a LOWER physical base rate ~0.29). If FIRE-PRECISION still beats the base-rate floor
CI-separated on this unseen genre, the gate GENERALIZES (it has no fit parameters -- WordNet IS-A, FrameNet
force lexicon, idiom asset, dominant-sense prior are all external/derived -- so there is nothing to overfit).

n=130 (larger replication; items 1..55 unchanged from the original 55-item probe -- a clean superset).
seed=20260830 sample; EVERY drawn clause adjudicated (single adjudicator -- a second, INDEPENDENT adjudicator
runs via exp_literalness_gate_adjudicator_agreement_v1). ASCII only. No LLM (spaCy + WordNet). No hdlab writes.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._literalness_data import iter_race_clauses
from experiments._literalness_gate import LiteralnessGate
import experiments.exp_literalness_gate_v1 as V

ANCHOR = "literalness_gate_heldout_race_v1"
SEED = 20260830

LABELS = {
    1: "C", 2: "O", 3: "C", 4: "A", 5: "O", 6: "B", 7: "B", 8: "A", 9: "O", 10: "A",
    11: "B", 12: "O", 13: "A", 14: "C", 15: "C", 16: "O", 17: "C", 18: "O", 19: "C", 20: "A",
    21: "O", 22: "C", 23: "O", 24: "C", 25: "C", 26: "C", 27: "A", 28: "A", 29: "A", 30: "A",
    31: "A", 32: "A", 33: "C", 34: "A", 35: "A", 36: "O", 37: "A", 38: "C", 39: "C", 40: "C",
    41: "B", 42: "A", 43: "A", 44: "C", 45: "O", 46: "A", 47: "O", 48: "O", 49: "A", 50: "C",
    51: "C", 52: "C", 53: "O", 54: "A", 55: "A",
    # --- larger replication, items 56..130 (adjudicated 2026-08-30; same criterion) ---
    56: "C", 57: "C", 58: "C", 59: "C", 60: "B", 61: "C", 62: "O", 63: "A", 64: "O", 65: "C",
    66: "O", 67: "A", 68: "C", 69: "O", 70: "O", 71: "C", 72: "A", 73: "O", 74: "C", 75: "C",
    76: "B", 77: "C", 78: "A", 79: "C", 80: "C", 81: "O", 82: "A", 83: "C", 84: "A", 85: "O",
    86: "O", 87: "O", 88: "C", 89: "C", 90: "O", 91: "A", 92: "C", 93: "C", 94: "A", 95: "C",
    96: "B", 97: "A", 98: "O", 99: "C", 100: "B", 101: "A", 102: "O", 103: "A", 104: "O", 105: "C",
    106: "C", 107: "C", 108: "A", 109: "A", 110: "O", 111: "C", 112: "O", 113: "A", 114: "A", 115: "C",
    116: "B", 117: "C", 118: "A", 119: "A", 120: "O", 121: "O", 122: "C", 123: "A", 124: "C", 125: "B",
    126: "C", 127: "C", 128: "B", 129: "O", 130: "O",
}
N_RACE = 130   # larger replication (was 55; items 1..55 unchanged -- clean superset)


def load_gold():
    cl = list(iter_race_clauses(max_texts=120))
    rng = random.Random(SEED)
    rng.shuffle(cl)
    out = []
    for i, c in enumerate(cl[:N_RACE], start=1):
        c = dict(c); c["idx"] = i; c["label"] = LABELS[i]; c["engage_gold"] = (LABELS[i] == "A")
        out.append(c)
    return out


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def run(nlp=None, boot=2000):
    import spacy
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
    gate = LiteralnessGate(nlp=nlp)
    items = load_gold()
    gold = [c["engage_gold"] for c in items]
    rng = random.Random(SEED)
    frame_perm = V._fixed_frame_perm(rng)
    conc_perm = V._shuffled_conc_map(items, rng)

    eng_gated, eng_fireany, twin_aff = [], [], []
    for c in items:
        doc = nlp(c["sent"])
        sent = next((s for s in doc.sents if any(t.lemma_.lower() == c["lemma"] for t in s)),
                    list(doc.sents)[0])
        vt = V._locate_verb(sent, c["lemma"], c["patient"])
        if vt is None:
            eng_gated.append(False); eng_fireany.append(True); twin_aff.append(-1.0); continue
        eng_gated.append(gate.assess(sent, vt, c["affector"], c["patient"], c["context"],
                                     use_oblique=True)["engage"])
        eng_fireany.append(True)
        twin_aff.append(gate.assess(sent, vt, c["affector"], c["patient"], c["context"],
                                    shuffle_sense=frame_perm, conc_map=conc_perm, use_oblique=True)["affordance"])
    K = sum(eng_gated)
    order = sorted(range(len(twin_aff)), key=lambda i: -twin_aff[i])
    eng_twin = [i in set(order[:K]) for i in range(len(twin_aff))]

    rng2 = random.Random(SEED + 1)
    p_gate = V._precision(eng_gated, gold)
    p_any = V._precision(eng_fireany, gold)
    p_twin = V._precision(eng_twin, gold)
    r_gate = V._recall(eng_gated, gold)
    ci_gate = V._boot_ci(eng_gated, gold, V._precision, rng2, boot)
    d_any = V._paired_delta_ci(eng_gated, eng_fireany, gold, V._precision, rng2, boot)
    d_twin = V._paired_delta_ci(eng_gated, eng_twin, gold, V._precision, rng2, boot)

    m = {
        "verdict": "HELDOUT_RACE__" + ("GENERALIZES" if d_any[1] > 0 else "DOES_NOT_GENERALIZE"),
        "genre": "RACE modern reading-comprehension passages (essay/expository) -- UNSEEN third genre",
        "n": len(gold), "positive_A": sum(gold), "base_rate": round(sum(gold) / len(gold), 4),
        "precision_gated": round(p_gate, 4), "precision_ci": [round(x, 4) for x in ci_gate],
        "precision_fire_any": round(p_any, 4), "precision_twin": round(p_twin, 4),
        "recall_gated": round(r_gate, 4),
        "paired_delta_GATED_minus_FIRE_ANY": [round(x, 4) for x in d_any],
        "paired_delta_GATED_minus_TWIN": [round(x, 4) for x in d_twin],
        "labels": dict(Counter(c["label"] for c in items)),
        "headline": (f"HELD-OUT RACE (unseen genre, base rate {sum(gold)/len(gold):.3f}): GATED precision "
                     f"{p_gate:.3f} [{ci_gate[1]:.3f},{ci_gate[2]:.3f}] vs FIRE_ANY {p_any:.3f} "
                     f"(+{d_any[0]:.3f} [{d_any[1]:.3f},{d_any[2]:.3f}]); twin {p_twin:.3f} "
                     f"(+{d_twin[0]:.3f}); recall {r_gate:.3f}. ZERO parameters re-tuned."),
        "anchor_name": ANCHOR, "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    return m


def self_test():
    import spacy
    nlp = spacy.load("en_core_web_sm")
    m = run(nlp=nlp, boot=200)
    assert m["n"] == 130, m["n"]
    print("[self-test] PASS", m["headline"][:110])
    return True


def main():
    out = _out_dir()
    t0 = time.perf_counter()
    m = run()
    m["elapsed_s"] = round(time.perf_counter() - t0, 2)
    tmp = os.path.join(out, "metrics.json.tmp")
    with open(tmp, "w", encoding="ascii") as f:
        json.dump(m, f, indent=2)
    os.replace(tmp, os.path.join(out, "metrics.json"))
    print(m["headline"])
    print("[verdict]", m["verdict"])
    return m


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test(); sys.exit(0)
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        d = _out_dir()
        with open(os.path.join(d, "metrics.json"), "w", encoding="ascii") as f:
            json.dump({"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                       "traceback": traceback.format_exc()[:3000]}, f)
        raise
