"""Composed front-end reader, measured OFF-vs-ON on the ROLE-BALANCED gold (consolidation payoff measurement).

The front-end was the PROVEN binding constraint (the wire-and-measure). This measures whether the newly-landed
front-end organs earn their keep on a FAIR test (positional-only floor ~0.5, not the McGuffey 0.78).

TASK: given (sentence, verb), predict the PATIENT token; correct if the predicted token falls in the gold patient span.
ONE-VARIABLE OFF-vs-ON (the design gate):
  * FLOOR   positional-only : always the nearest POST-verbal nominal (ignores voice)      -> ~0.5 by construction.
  * OFF     two_line        : voice-aware word order (passive -> pre-verbal; else post)   -> the real live baseline.
  * ON      resolve_patient : OFF + the relcl OBJECT-GAP arm (hdlab.relcl_resolver)        -> the composed front-end.
  * TWIN    random nominal  : info-free control -> MUST lose.
The OFF->ON gain localises to the object-relative REVERSIBLES (pre-verbal patient, NOT passive) -- the relcl organ's
domain. DECISIVE either way: ON beats OFF + the floor CI-separated (the front-end organs earn their keep on a fair
test), OR a rigorous negative that localises what is still missing.

Run:  .venv/Scripts/python.exe experiments/exp_composed_reader_role_balanced_measure_v1.py [--smoke]
"""
from __future__ import annotations

import json
import os
import random
import sys

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

from hdlab.relcl_resolver import resolve_patient, two_line_patient, _cands  # noqa: E402

GOLD = os.path.join(REPO_ROOT, "data", "role_balanced_comprehension_gold_v1", "gold.jsonl")
SEED = 20260827


def _positional_only(toks, pos, v, cands):
    """Nearest POST-verbal nominal, ignoring voice (the naive floor)."""
    after = [i for i in cands if i > v]
    return after[0] if after else (cands[-1] if cands else None)


def _in_span(pred_1based, gold_span_0based) -> bool:
    # SUPERSEDED-BUG FIX: the QA-SRL patient is a HALF-OPEN (start,end) span, not a 2-element set. (v1 originally
    # scored `in {start,end}`, capping the oracle at ~0.49 -> flat 0.32; see v2 + LOG STEP 9. Corrected here for
    # hygiene; the DEFINITIVE measurement is exp_composed_reader_role_balanced_measure_v2.py.)
    if pred_1based is None:
        return False
    g = gold_span_0based
    idxs = set(range(g[0], g[1])) if (len(g) == 2 and g[1] > g[0]) else set(g)
    return (pred_1based - 1) in idxs


def _boot_ci(correct, seed, n_boot=2000):
    a = np.asarray(correct, dtype=np.float64)
    r = np.random.default_rng(seed)
    n = len(a)
    boots = np.array([a[r.integers(0, n, n)].mean() for _ in range(n_boot)])
    return float(a.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def _boot_diff(a, b, seed, n_boot=2000):
    a = np.asarray(a, float); b = np.asarray(b, float)
    r = np.random.default_rng(seed)
    n = len(a)
    boots = np.array([(a[idx].mean() - b[idx].mean()) for idx in (r.integers(0, n, n) for _ in range(n_boot))])
    lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    pt = float(a.mean() - b.mean())
    band = "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")
    return {"delta": round(pt, 4), "ci": [round(lo, 4), round(hi, 4)], "half_width": round((hi - lo) / 2, 4), "band": band}


def main():
    smoke = "--smoke" in sys.argv
    from experiments.exp_stated_entity_fate_reading_extractor_v1 import _load_or_build_frontend
    from exp_reader_vs_twoline_qasrl_power_v1 import parse_and_align

    items = []
    with open(GOLD, encoding="utf-8") as fh:
        for line in fh:
            items.append(json.loads(line))
    if smoke:
        items = items[:600] + items[-600:]      # a mix of pre + post (the file is pre-block then post-block)

    gen = _load_or_build_frontend()
    aligned = parse_and_align(gen, items)
    print(f"loaded {len(items)} gold items; {len(aligned)} tokenization-aligned (parsed)")

    rng = random.Random(SEED)
    off, on, floor, twin = [], [], [], []
    rev_off, rev_on = [], []                     # the object-relative REVERSIBLE slice (pre-verbal, non-passive)
    for it in aligned:
        toks, pos = it["toks"], it["pos"]
        v = it["verb_idx"] + 1                    # 1-based
        gspan = it["patient"]
        cands = _cands(pos)
        if not cands:
            continue
        p_off = two_line_patient(toks, pos, v, cands)
        p_on = resolve_patient(toks, pos, v, cands)
        p_floor = _positional_only(toks, pos, v, cands)
        p_twin = rng.choice(cands)
        c_off, c_on = _in_span(p_off, gspan), _in_span(p_on, gspan)
        off.append(c_off); on.append(c_on)
        floor.append(_in_span(p_floor, gspan)); twin.append(_in_span(p_twin, gspan))
        if it["patient_position"] == "pre" and it["category"] != "passive":
            rev_off.append(c_off); rev_on.append(c_on)

    n = len(off)
    print(f"\n=== COMPOSED FRONT-END, ROLE-BALANCED GOLD (n={n}) ===")
    for name, arr in (("FLOOR positional-only", floor), ("OFF two_line (voice)", off),
                      ("ON  resolve_patient", on), ("TWIN random nominal", twin)):
        acc, lo, hi = _boot_ci(arr, SEED + 1)
        print(f"  {name:24s} {acc:.4f}  CI[{lo:.4f},{hi:.4f}]")
    d_on_off = _boot_diff(on, off, SEED + 2)
    d_on_floor = _boot_diff(on, floor, SEED + 3)
    d_on_twin = _boot_diff(on, twin, SEED + 4)
    print(f"\n  ON - OFF   : {d_on_off['delta']:+.4f} CI{d_on_off['ci']} [{d_on_off['band']}]  (the relcl object-gap arm)")
    print(f"  ON - FLOOR : {d_on_floor['delta']:+.4f} CI{d_on_floor['ci']} [{d_on_floor['band']}]")
    print(f"  ON - TWIN  : {d_on_twin['delta']:+.4f} CI{d_on_twin['ci']} [{d_on_twin['band']}] (info-free twin must lose)")
    if rev_on:
        r_off = float(np.mean(rev_off)); r_on = float(np.mean(rev_on))
        d_rev = _boot_diff(rev_on, rev_off, SEED + 5)
        print(f"\n  REVERSIBLE slice (object-relative, n={len(rev_on)}): OFF {r_off:.4f} -> ON {r_on:.4f}  "
              f"({d_rev['delta']:+.4f} CI{d_rev['ci']} [{d_rev['band']}])  <- where the relcl organ earns its keep")

    print("\n[interpretation] ON beats OFF -> the relcl object-gap resolution earns its keep on a fair test; "
          "ON beats the positional floor + the twin loses -> the composed front-end is real, not positional/artifact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
