"""Composed front-end reader v2 -- wire the INCREMENTAL PARSER's structured candidates (the accuracy lever STEP 8
diagnosed as missing), measured OFF-vs-ON on the ROLE-BALANCED gold.

STEP-8 finding: OFF used ALL nominals as patient candidates (crude, 0.32) -- the nearest post-verbal nominal is
usually NOT the patient head. The brain-foundational fix: the incremental left-corner parser binds the verb's
ACTUAL argument slots (subject/object), so restrict the candidate set to THOSE, then resolve voice/relcl over them.

ONE-VARIABLE OFF-vs-ON (the design gate):
  * FLOOR positional-only : nearest POST-verbal nominal (all nominals, ignore voice)               -> the naive floor.
  * OFF   resolve/ALL      : resolve_patient over ALL nominals (voice+relcl, crude candidates)       -> the STEP-8 baseline.
  * ON    resolve/INCR     : resolve_patient over the INCREMENTAL PARSER's argument slots for the verb -> composed front-end.
  * TWIN  random nominal   : info-free control -> MUST lose.
The ONE variable OFF->ON is the CANDIDATE SET (all nominals vs incremental argument slots). If ON beats OFF + the
floor CI-separated with the twin losing, the incremental parser's candidate PRECISION earns its keep on a fair test.

Run:  .venv/Scripts/python.exe experiments/exp_composed_reader_role_balanced_measure_v2.py [--smoke]
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

from hdlab.incremental_parser import incremental_build  # noqa: E402
from hdlab.relcl_resolver import resolve_patient, _cands  # noqa: E402

GOLD = os.path.join(REPO_ROOT, "data", "role_balanced_comprehension_gold_v1", "gold.jsonl")
SEED = 20260827


def _positional_only(toks, pos, v, cands):
    after = [i for i in cands if i > v]
    return after[0] if after else (cands[-1] if cands else None)


def _incr_cands(toks, pos, v):
    """The incremental parser's ARGUMENT slots for verb v (1-based). Falls back to all nominals if the parser
    found no frame for this verb (so ON is never candidate-starved -- a fair, non-degenerate fallback)."""
    frames = incremental_build(toks, pos, predictor=None)
    args = frames.get(v)
    if args:
        return sorted(args)
    return _cands(pos)


def _span_set(gold_span):
    """QA-SRL patient is a (start, end) HALF-OPEN span -> expand to the token indices it covers.
    (A scoring bug treated [start,end] as the 2-element set {start,end}, capping the oracle at ~0.49; the true
    ceiling with range(start,end) is ~0.97.)"""
    if len(gold_span) == 2 and gold_span[1] > gold_span[0]:
        return set(range(gold_span[0], gold_span[1]))
    return set(gold_span)


def _in_span(pred_1, gold_span):
    return pred_1 is not None and (pred_1 - 1) in _span_set(gold_span)


def _boot_ci(correct, seed, n_boot=2000):
    a = np.asarray(correct, float); r = np.random.default_rng(seed); n = len(a)
    b = np.array([a[r.integers(0, n, n)].mean() for _ in range(n_boot)])
    return float(a.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def _boot_diff(a, b, seed, n_boot=2000):
    a = np.asarray(a, float); b = np.asarray(b, float); r = np.random.default_rng(seed); n = len(a)
    d = np.array([(a[i].mean() - b[i].mean()) for i in (r.integers(0, n, n) for _ in range(n_boot))])
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    return {"delta": round(float(a.mean() - b.mean()), 4), "ci": [round(lo, 4), round(hi, 4)],
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")}


def main():
    smoke = "--smoke" in sys.argv
    from experiments.exp_stated_entity_fate_reading_extractor_v1 import _load_or_build_frontend
    from exp_reader_vs_twoline_qasrl_power_v1 import parse_and_align

    items = [json.loads(l) for l in open(GOLD, encoding="utf-8")]
    if smoke:
        items = items[:600] + items[-600:]
    gen = _load_or_build_frontend()
    aligned = parse_and_align(gen, items)
    print(f"loaded {len(items)}; {len(aligned)} aligned")

    rng = random.Random(SEED)
    floor, off, on, twin = [], [], [], []
    by_pos = {"pre": [0, 0], "post": [0, 0]}    # [on_correct, n] by patient position
    for it in aligned:
        toks, pos = it["toks"], it["pos"]; v = it["verb_idx"] + 1; g = it["patient"]
        all_c = _cands(pos)
        if not all_c:
            continue
        inc_c = _incr_cands(toks, pos, v)
        floor.append(_in_span(_positional_only(toks, pos, v, all_c), g))
        off.append(_in_span(resolve_patient(toks, pos, v, all_c), g))
        c_on = _in_span(resolve_patient(toks, pos, v, inc_c), g)
        on.append(c_on)
        twin.append(_in_span(rng.choice(all_c), g))
        b = by_pos.get(it["patient_position"])
        if b is not None:
            b[0] += int(c_on); b[1] += 1

    n = len(off)
    print(f"\n=== COMPOSED FRONT-END v2 (incremental candidates), ROLE-BALANCED GOLD (n={n}) ===")
    for name, arr in (("FLOOR positional", floor), ("OFF resolve/ALL-nominals", off),
                      ("ON  resolve/INCR-slots", on), ("TWIN random", twin)):
        acc, lo, hi = _boot_ci(arr, SEED + 1)
        print(f"  {name:26s} {acc:.4f}  CI[{lo:.4f},{hi:.4f}]")
    print(f"\n  ON - OFF   : {_boot_diff(on, off, SEED+2)}   (the incremental candidate-precision lever)")
    print(f"  ON - FLOOR : {_boot_diff(on, floor, SEED+3)}")
    print(f"  ON - TWIN  : {_boot_diff(on, twin, SEED+4)}")
    for k, (c, m) in by_pos.items():
        if m:
            print(f"  ON on {k}-verbal-patient: {c}/{m} = {c/m:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
