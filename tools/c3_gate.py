#!/usr/bin/env python
"""The C3 grounding-quality gate, as an EXECUTABLE PREDICATE rather than prose.

Why this file exists. The C3 gate used to be one sentence in a document -- ">=10% MEANINGFUL
against a recorded floor, tautologies <10%" -- and on 2026-08-14 a pure character-trigram control
carrying NO MEANING AT ALL scored hit@1 0.10275 on that read-out and cleared it
(data/exp_meaning_supply_separation_v1/metrics.json, arm A5_STRINGCTRL at w=1.00, commit c0e6ec0da).
A prose gate gets re-interpreted by whoever quotes it. A gate that is a function does not.

Two jobs:
  1. `string_form_profile` / `string_control_scores` -- the MANDATORY zero-meaning control arm,
     supplied here so no future cell has an excuse to skip it. Identical construction to the arm
     that caught the defect (sha256-hashed character trigrams with ^ $ boundaries, L2-normalized).
  2. `evaluate` / `--score` -- the four-condition gate. It returns NOT_EVALUABLE, never PASS, when
     the string control arm is absent. That is the guard, and `--self-test` proves it.

Usage:
    python tools/c3_gate.py --self-test
    python tools/c3_gate.py --score data/exp_meaning_supply_separation_v1/metrics.json
    python tools/c3_gate.py --score <metrics.json> --arm A4_BOTH --base-arm A1_BASE

Exit codes: 0 = at least one arm PASSes (or self-test passed), 1 = nothing passes, 2 = bad input.

Doc coupling (CLAUDE.md "a doc parsed by code is coupled to it"): the authoritative prose statement
of this gate lives in notes/SUBSTRATE_STRATEGY.md PART 1, under the C3 row. That prose must name
this file; this file names that section. Changing one without the other is the defect.
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
from typing import Dict, List, Optional, Sequence

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------------ gate constants
HIT_AT_1_FLOOR = 0.10          # the historical magnitude clause, unchanged
TAUTOLOGY_CEILING = 0.10       # the historical tautology clause, unchanged
STRING_CONTROL_DIM = 512       # matches experiments/exp_meaning_supply_separation_v1.TRIGRAM_DIM

PASS, FAIL, NOT_EVALUABLE = "PASS", "FAIL", "NOT_EVALUABLE"

# Set False only by --_disable_guard, to prove in the self-test that the guard is load-bearing.
GUARD_ENABLED = True


# ------------------------------------------------------------------ the mandatory control arm
def string_form_profile(words: Sequence[str], dim: int = STRING_CONTROL_DIM) -> np.ndarray:
    """Hashed character-trigram profile per word, rows L2-normalized. Shape [len(words), dim].

    Pure SURFACE STRING content: no meaning, no corpus, no training. Cosine between two rows is a
    morphology/spelling similarity. Uses hashlib, never the built-in hash(), so the arm is
    reproducible across processes (PROT-023 determinism).
    """
    mat = np.zeros((len(words), dim), dtype=np.float64)
    for i, w in enumerate(words):
        s = "^" + str(w) + "$"
        for k in range(len(s) - 2):
            j = int.from_bytes(hashlib.sha256(s[k:k + 3].encode("utf-8")).digest()[:4], "big") % dim
            mat[i, j] += 1.0
        nrm = float(np.linalg.norm(mat[i]))
        if nrm >= 1e-9:
            mat[i] /= nrm
    return mat


def string_control_scores(query: str, candidates: Sequence[str],
                          dim: int = STRING_CONTROL_DIM) -> np.ndarray:
    """Zero-meaning auxiliary similarity of `query` against each candidate. Shape [len(candidates)].

    Drop-in for whatever aux similarity the treatment arm blends: score the control arm with the
    IDENTICAL blend mechanism and the IDENTICAL weight, so the only difference between the arms is
    whether the auxiliary signal carries meaning.
    """
    prof = string_form_profile([query] + list(candidates), dim=dim)
    return prof[1:] @ prof[0]


# ------------------------------------------------------------------ the gate
def _get(d: Optional[dict], *path, default=None):
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def _margin(arm: Optional[dict]) -> Optional[float]:
    """Separation margin, preferring the RESTANDARDIZED form when a cell reports it.

    `separation_margin_z` as emitted by exp_meaning_supply_separation_v1 is measured in sd units of
    the item's candidate pool but on a blended score z(base)+w*sum(z(aux)) that is NOT itself
    restandardized, so an arm carrying more aux weight has a mechanically larger |margin|. New cells
    must report `separation_margin_z.restandardized`; this reader uses it when present.
    """
    r = _get(arm, "separation_margin_z", "restandardized")
    if r is None:
        r = _get(arm, "separation_margin_z", "mean")
    if r is None:
        r = _get(arm, "separation_margin")
    return None if r is None else float(r)


def evaluate(arm: dict,
             base: dict,
             stringctrl: Optional[dict],
             *,
             arm_minus_floor_ci_lo: Optional[float] = None,
             arm_minus_stringctrl_ci_lo: Optional[float] = None,
             tautology_rate: Optional[float] = None,
             arm_name: str = "ARM") -> dict:
    """Score one candidate arm against the hardened four-condition C3 gate.

    HG1 MAGNITUDE_WITH_FLOOR       hit@1 >= 0.10, CI on (arm - recorded floor) excludes 0,
                                   tautology rate < 0.10.
    HG2 DISTRIBUTION_MOVED         median target rank strictly improves AND frac-gold-in-top-50
                                   strictly improves, vs the SAME cell's base arm on the SAME items.
    HG3 SEPARATION_NOT_DEGRADED    separation margin does not fall below the base arm's.
    HG4 STRING_CONTROL_BEATEN      a zero-meaning string-form arm was RUN, and the CI on
                                   (arm - string control) excludes 0.

    Returns {"status": PASS|FAIL|NOT_EVALUABLE, "conditions": {...}, "reasons": [...]}.
    Missing evidence is NOT_EVALUABLE. It is never PASS.
    """
    cond: Dict[str, dict] = {}
    missing: List[str] = []

    def need(val, label):
        if val is None:
            missing.append(label)
        return val

    # ---- HG1 magnitude, against a recorded floor
    h = need(_get(arm, "hit_at_1"), f"{arm_name}.hit_at_1")
    taut = tautology_rate if tautology_rate is not None else _get(arm, "tautology_rate")
    hg1_parts = {
        "hit_at_1": h,
        "threshold": HIT_AT_1_FLOOR,
        "arm_minus_floor_ci_lo": arm_minus_floor_ci_lo,
        "tautology_rate": taut,
        "tautology_ceiling": TAUTOLOGY_CEILING,
    }
    if h is None or arm_minus_floor_ci_lo is None or taut is None:
        if arm_minus_floor_ci_lo is None:
            missing.append(f"{arm_name}-minus-floor CI")
        if taut is None:
            missing.append(f"{arm_name}.tautology_rate")
        cond["HG1_MAGNITUDE_WITH_FLOOR"] = {"ok": None, **hg1_parts}
    else:
        cond["HG1_MAGNITUDE_WITH_FLOOR"] = {
            "ok": bool(h >= HIT_AT_1_FLOOR and arm_minus_floor_ci_lo > 0
                       and taut < TAUTOLOGY_CEILING),
            **hg1_parts,
        }

    # ---- HG2 the whole distribution moved, not just the argmax
    ar, br = _get(arm, "median_rank"), _get(base, "median_rank")
    at, bt = _get(arm, "frac_gold_in_top50"), _get(base, "frac_gold_in_top50")
    for v, lbl in ((ar, f"{arm_name}.median_rank"), (br, "base.median_rank"),
                   (at, f"{arm_name}.frac_gold_in_top50"), (bt, "base.frac_gold_in_top50")):
        need(v, lbl)
    if None in (ar, br, at, bt):
        cond["HG2_DISTRIBUTION_MOVED"] = {"ok": None, "median_rank": [br, ar],
                                          "frac_gold_in_top50": [bt, at]}
    else:
        cond["HG2_DISTRIBUTION_MOVED"] = {
            "ok": bool(ar < br and at > bt),
            "median_rank": [br, ar], "frac_gold_in_top50": [bt, at],
        }

    # ---- HG3 within-neighbourhood separation did not degrade
    am, bm = _margin(arm), _margin(base)
    for v, lbl in ((am, f"{arm_name}.separation_margin"), (bm, "base.separation_margin")):
        need(v, lbl)
    if None in (am, bm):
        cond["HG3_SEPARATION_NOT_DEGRADED"] = {"ok": None, "separation_margin": [bm, am]}
    else:
        cond["HG3_SEPARATION_NOT_DEGRADED"] = {"ok": bool(am >= bm),
                                               "separation_margin": [bm, am]}

    # ---- HG4 THE GUARD: the zero-meaning string arm must exist and must be beaten
    if GUARD_ENABLED and stringctrl is None:
        missing.append("string-form control ARM (mandatory; see tools/c3_gate.string_control_scores)")
        cond["HG4_STRING_CONTROL_BEATEN"] = {"ok": None, "stringctrl_arm_present": False}
    else:
        present = stringctrl is not None
        ch = _get(stringctrl, "hit_at_1")
        if arm_minus_stringctrl_ci_lo is None:
            missing.append(f"{arm_name}-minus-stringctrl paired CI")
            cond["HG4_STRING_CONTROL_BEATEN"] = {"ok": None, "stringctrl_arm_present": present,
                                                 "stringctrl_hit_at_1": ch,
                                                 "ci_lo": None}
        else:
            cond["HG4_STRING_CONTROL_BEATEN"] = {
                "ok": bool(arm_minus_stringctrl_ci_lo > 0),
                "stringctrl_arm_present": present, "stringctrl_hit_at_1": ch,
                "ci_lo": arm_minus_stringctrl_ci_lo,
            }

    failed = [k for k, v in cond.items() if v["ok"] is False]
    unknown = [k for k, v in cond.items() if v["ok"] is None]
    if failed:
        status = FAIL
    elif unknown:
        status = NOT_EVALUABLE
    else:
        status = PASS

    reasons = []
    if failed:
        reasons.append("FAILS: " + ", ".join(sorted(failed)))
    if unknown:
        reasons.append("NOT EVALUABLE on " + ", ".join(sorted(unknown))
                       + " | missing: " + "; ".join(sorted(set(missing))))
    if status == PASS:
        reasons.append("all four conditions hold")
    return {"arm": arm_name, "status": status, "conditions": cond, "reasons": reasons}


# ------------------------------------------------------------------ scoring a metrics.json
def _open_vocab_pseudo_arms(m: dict) -> Optional[tuple]:
    """Adapter for exp_grounding_readout_known_answer_v1's own layout.

    That cell -- the one the 4.80% C3 headline comes from -- reports ONLY hit@1 and the tautology
    rate for its open-vocabulary arms. It records no median rank, no top-50 fraction and no
    separation margin, so it is structurally unable to answer HG2/HG3, and it ran no string-form
    control at all. Scoring it here makes that visible instead of crashing.
    """
    ov = _get(m, "stage_b", "open_vocabulary_readout")
    if not isinstance(ov, dict) or "hit_at_1" not in ov:
        return None
    per_arm = {k: {"hit_at_1": _get(v, "acc")} for k, v in ov["hit_at_1"].items()}
    boot = {"deltas": {}}
    for name, d in (ov.get("delta") or {}).items():
        boot["deltas"][name] = d
    return ("open_vocab", per_arm, boot)


def score_metrics(path: str, base_arm: str = "A1_BASE", string_arm: str = "A5_STRINGCTRL",
                  only_arm: Optional[str] = None,
                  tautology_rate: Optional[float] = None) -> List[dict]:
    """Re-score every arm of a metrics.json that carries a per_w/per_arm block."""
    with open(path, "r", encoding="utf-8") as fh:
        m = json.load(fh)

    blocks = []
    if isinstance(m.get("per_w"), dict):
        for w, blk in sorted(m["per_w"].items()):
            blocks.append((w, blk.get("per_arm", {}), blk.get("bootstrap", {})))
    elif isinstance(m.get("per_arm"), dict):
        blocks.append(("-", m["per_arm"], m.get("bootstrap", {})))
    else:
        ov = _open_vocab_pseudo_arms(m)
        if ov is None:
            raise SystemExit(f"[c3_gate] {path}: no per_w/per_arm block -- cannot score. "
                             "A C3 claim must report per-arm hit@1, median_rank, "
                             "frac_gold_in_top50 and separation margin.")
        blocks.append(ov)

    # A tautology rate reported once for the cell applies to every arm unless overridden.
    cell_taut = tautology_rate
    if cell_taut is None:
        cell_taut = _get(m, "stage_b", "open_vocabulary_readout", "tautology_rate")
    if cell_taut is None:
        cell_taut = m.get("tautology_rate")

    out = []
    for w, per_arm, boot in blocks:
        base = per_arm.get(base_arm)
        ctrl = per_arm.get(string_arm)
        deltas = boot.get("deltas", {}) if isinstance(boot, dict) else {}
        for name in sorted(per_arm):
            if name == base_arm or (only_arm and name != only_arm):
                continue
            # (arm - floor) CI: the cell records arm-minus-BASE; base-minus-floor is a separate
            # delta. An arm that beats base, where base beats the floor, beats the floor.
            d_arm_base = _get(deltas, f"d_{name}_minus_BASE", "ci_lo")
            d_base_floor = _get(deltas, "d_A1_BASE_minus_F_SCRAMBLE", "ci_lo")
            if d_base_floor is None:
                d_base_floor = _get(deltas, f"d_{name}_minus_B6_OPEN_SCRAMBLE", "ci_lo")
                if d_base_floor is None:
                    d_base_floor = _get(deltas, "d_B5_minus_B6", "ci_lo")
                d_arm_base = d_base_floor
            floor_ci = None
            if d_arm_base is not None and d_base_floor is not None:
                floor_ci = min(d_arm_base, d_base_floor)
            d_ctrl = _get(deltas, f"d_{name}_minus_{string_arm}", "ci_lo")
            r = evaluate(per_arm[name], base or {}, ctrl,
                         arm_minus_floor_ci_lo=floor_ci,
                         arm_minus_stringctrl_ci_lo=d_ctrl,
                         tautology_rate=cell_taut,
                         arm_name=name)
            r["w"] = w
            out.append(r)
    return out


def _fmt(r: dict) -> str:
    c = r["conditions"]

    def mark(k):
        v = c[k]["ok"]
        return "PASS" if v is True else ("FAIL" if v is False else "  ? ")
    return ("  %-16s w=%-6s %-14s HG1 %s | HG2 %s | HG3 %s | HG4 %s\n      %s"
            % (r["arm"], r.get("w", "-"), r["status"],
               mark("HG1_MAGNITUDE_WITH_FLOOR"), mark("HG2_DISTRIBUTION_MOVED"),
               mark("HG3_SEPARATION_NOT_DEGRADED"), mark("HG4_STRING_CONTROL_BEATEN"),
               " ".join(r["reasons"])))


# ------------------------------------------------------------------ self-test
def _arm(hit, rank, top50, margin):
    return {"hit_at_1": hit, "median_rank": rank, "frac_gold_in_top50": top50,
            "separation_margin_z": {"mean": margin}}


def self_test() -> int:
    """Prove the guard: a C3 claim with NO string-form control can never come back PASS.

    Five cases, three of them replays of numbers measured on disk 2026-08-14.
    """
    ok = True

    def check(label, got, want):
        nonlocal ok
        if got == want:
            print(f"[self-test] PASS {label} -> {got}")
        else:
            print(f"[self-test] FAIL {label} -> {got}, expected {want}", file=sys.stderr)
            ok = False

    # Measured base arm (exp_meaning_supply_separation_v1 A1_BASE == the 4.80% C3 headline).
    base = _arm(0.0480, 37.0, 0.5565, -2.5422609616204763)

    # CASE 1 -- THE GUARD. An arm that clears every OTHER condition (hit@1, rank, top-50 and
    # separation all good) but ran NO string control. Must be NOT_EVALUABLE, so that the missing
    # control is the ONLY thing deciding the outcome. If this ever returns PASS the gate is back to
    # the state that let a trigram control through on 2026-08-14.
    gamer = _arm(0.1200, 30.0, 0.6000, -2.40)
    r = evaluate(gamer, base, None, arm_minus_floor_ci_lo=0.03, tautology_rate=0.0,
                 arm_name="NO_CONTROL")
    check("no string-control arm is NOT_EVALUABLE, never PASS", r["status"], NOT_EVALUABLE)
    check("  and it names the missing arm",
          "string-form control ARM" in " ".join(r["reasons"]), True)

    # CASE 2 -- MEASURED REPLAY. exp_meaning_supply_separation_v1 A5_STRINGCTRL at w=1.00: hit@1
    # 0.10275 (clears 10%), median rank 31.0 < 37.0, top-50 0.58675 > 0.5565 -- so hit@1 + rank +
    # top-50 ALL pass. Only the separation margin (-5.473 vs -2.542) catches it.
    a5 = _arm(0.10275, 31.0, 0.58675, -5.473060945852469)
    r = evaluate(a5, base, a5, arm_minus_floor_ci_lo=0.04375,
                 arm_minus_stringctrl_ci_lo=0.0, tautology_rate=0.0, arm_name="A5_STRINGCTRL")
    check("measured trigram control at w=1.00 is FAIL", r["status"], FAIL)
    check("  HG1 magnitude alone would have PASSED it",
          r["conditions"]["HG1_MAGNITUDE_WITH_FLOOR"]["ok"], True)
    check("  HG2 rank+top50 alone would ALSO have passed it",
          r["conditions"]["HG2_DISTRIBUTION_MOVED"]["ok"], True)
    check("  HG3 separation is what stops it",
          r["conditions"]["HG3_SEPARATION_NOT_DEGRADED"]["ok"], False)

    # CASE 3 -- the string control REPRODUCES a real arm's gain. Must FAIL on HG4 alone.
    good = _arm(0.1100, 20.0, 0.6600, -2.30)
    r = evaluate(good, base, a5, arm_minus_floor_ci_lo=0.05,
                 arm_minus_stringctrl_ci_lo=-0.004, tautology_rate=0.0, arm_name="REPRODUCED")
    check("string control reproduces the gain -> FAIL", r["status"], FAIL)
    check("  and only HG4 is the failing condition",
          [k for k, v in r["conditions"].items() if v["ok"] is False],
          ["HG4_STRING_CONTROL_BEATEN"])

    # CASE 4 -- NON-VACUITY. A well-formed genuine win must PASS, or the gate is unusable.
    r = evaluate(good, base, a5, arm_minus_floor_ci_lo=0.05,
                 arm_minus_stringctrl_ci_lo=0.006, tautology_rate=0.0, arm_name="GENUINE")
    check("a genuine, string-control-beating arm PASSES (gate is not vacuous)", r["status"], PASS)

    # CASE 5 -- MEASURED REPLAY, the best real arm. A4_BOTH at w=1.00 clears HG1/HG2/HG3 and is
    # NOT_EVALUABLE only because the cell never computed the arm-minus-stringctrl paired CI.
    a4 = _arm(0.1190, 13.0, 0.7040, -2.3670214335543847)
    r = evaluate(a4, base, a5, arm_minus_floor_ci_lo=0.03775, tautology_rate=0.0,
                 arm_name="A4_BOTH")
    check("measured A4_BOTH w=1.00 is NOT_EVALUABLE (no paired CI vs the control)",
          r["status"], NOT_EVALUABLE)
    check("  but it does clear HG3, so the gate is reachable by real meaning",
          r["conditions"]["HG3_SEPARATION_NOT_DEGRADED"]["ok"], True)

    # CASE 6 -- the control constructor itself carries no meaning: morphological relatives score
    # high, synonyms score low. This is why it is the right zero-meaning control.
    s = string_control_scores("abnormality", ["abnormal", "duplication", "chromosomal"])
    check("string control ranks 'abnormal' above 'duplication' for 'abnormality'",
          bool(s[0] > s[1]), True)
    s2 = string_control_scores("sofa", ["couch", "sofas"])
    check("string control ranks 'sofas' above the SYNONYM 'couch' (no meaning in it)",
          bool(s2[1] > s2[0]), True)

    # NEGATIVE CONTROL for the guard: with the guard disabled, CASE 1 must stop being protected.
    global GUARD_ENABLED
    GUARD_ENABLED = False
    try:
        r = evaluate(gamer, base, None, arm_minus_floor_ci_lo=0.03,
                     arm_minus_stringctrl_ci_lo=0.01, tautology_rate=0.0, arm_name="NO_CONTROL")
        check("guard DISABLED: the same no-control arm becomes PASS (guard is load-bearing)",
              r["status"], PASS)
    finally:
        GUARD_ENABLED = True

    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--score", metavar="METRICS_JSON", help="re-score a cell's arms under the gate")
    ap.add_argument("--arm", default=None, help="score only this arm")
    ap.add_argument("--base-arm", default="A1_BASE")
    ap.add_argument("--string-arm", default="A5_STRINGCTRL")
    ap.add_argument("--json", action="store_true", help="emit the full per-condition JSON")
    ap.add_argument("--tautology", type=float, default=None,
                    help="tautology rate to apply when the cell inherits it from another cell "
                         "(state the inheritance in the report; do not assume it)")
    ap.add_argument("--self-test", action="store_true", help="prove the mandatory-control guard")
    ap.add_argument("--_disable_guard", action="store_true",
                    help="self-test only: negative control for the guard")
    args = ap.parse_args(argv)

    if args._disable_guard:
        global GUARD_ENABLED
        GUARD_ENABLED = False
        print("[c3_gate] WARNING guard DISABLED (negative control)")

    if args.self_test:
        return self_test()

    if not args.score:
        ap.print_help()
        return 2

    rows = score_metrics(args.score, base_arm=args.base_arm, string_arm=args.string_arm,
                         only_arm=args.arm, tautology_rate=args.tautology)
    if args.json:
        print(json.dumps(rows, indent=1))
    else:
        print(f"[c3_gate] {args.score}")
        for r in rows:
            print(_fmt(r))
    n_pass = sum(1 for r in rows if r["status"] == PASS)
    print(f"[c3_gate] {n_pass} of {len(rows)} arm-by-w cells PASS the hardened C3 gate")
    return 0 if n_pass else 1


if __name__ == "__main__":
    sys.exit(main())
