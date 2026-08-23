"""Scaffold-free witness for substrate_never_resumes: the MEASUREMENT headline recomputes live.

Two independent claims, recomputed (tracing=False, no scaffold):

  1. WIRING both ways (delegates to test_substrate_resume_wiring): OFF loads nothing and starts at
     seeds byte-identically; ON loads once and starts populated.

  2. THE MEASUREMENT headline: RESUMING DOES NOT HELP GROUNDING. On the real rich foundation this
     project built (reused if present, else a small clean one is built here), over a FIXED test slice
     disjoint from the snapshot:
        (a) INERT READ: RESUMED grounds far FEWER new meanings than COLD on the identical read -- the
            substrate already knows the recurring vocabulary, so a matched re-read is nearly inert.
        (b) THE ANCHORS DO NOT MATCH: in the pure-mechanism probe (novel words, IDENTICAL accumulated
            context sums, only the anchor space varies), COLD's words match their co-read neighbours
            but RESUMED's words match NONE of the loaded anchors above threshold -- match rate
            collapses. (The apparent "degeneracy fell to distinct/grounded=1.0" is an ARTIFACT of
            counting each no-match SELF-RETURN as its own anchor; a self-return is a refusal.)
        (c) BINS, NOT MEANING: DECOY (same anchor vectors, LABELS permuted) matches IDENTICALLY to
            RESUMED -- a bijection on labels cannot change which vectors clear the threshold.
        (d) NO CORRECTNESS: SUBSTRATE grounding precision is not CI-separated above its own
            RANDOM_ANCHOR floor in either arm (brief failure mode (b)).

  3. If the landed full-run metrics exist, its aggregated headline is asserted too (RESUMED grounds
     far fewer new meanings than COLD across seeds).

Run:  python verification/test_substrate_resume_measurement.py
ASCII-only.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import json
import sys

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import substrate_resume as R
from verification.test_substrate_resume_wiring import (
    test_off_arm_does_not_load_and_matches_plain_substrate,
    test_on_arm_loads_once_and_starts_populated,
)

SNAP_FULL = os.path.join(_REPO, "data", "exp_substrate_resume_solver", "clean_snapshot_full")
SNAP_WITNESS = os.path.join(_REPO, "data", "exp_substrate_resume_solver", "clean_snapshot_witness")
LANDED = os.path.join(_REPO, "data", "exp_substrate_resume_helps_v1", "metrics.json")
CORPORA = ["simplewiki", "textbook_biology_2e", "textbook_psychology_2e", "mcguffey_readers",
           "sherlock_holmes", "race", "onestop", "social_iqa"]
SEED = 20260819


def _ensure_snapshot():
    """Reuse the full snapshot if present; else build a small clean one. Returns (dir, offset_n)."""
    if os.path.isfile(os.path.join(SNAP_FULL, "manifest.json")):
        return SNAP_FULL, 16000
    # a RICH snapshot is required for the effect (a small one leaves the substrate ignorant, so it
    # still grounds a lot). Reuse the full one when present; else build the same 16000-sentence one
    # (slow only on a first run with no artifact -- ~2-3 min).
    if not os.path.isfile(os.path.join(SNAP_WITNESS, "manifest.json")):
        snap, _test, _info = R.corpus_slices(CORPORA, snapshot_n=16000, test_n=1)
        cs = R.cold_state(seed=SEED)
        sr = R.read_fixed(cs, snap, consolidate_every=200, source_tag="snap")
        R.fp.save_foundation(cs, SNAP_WITNESS, source_tag="witness_snapshot",
                             next_pass_idx=sr["end_pass_idx"] + 1)
    return SNAP_WITNESS, 16000


def test_wiring_both_ways():
    test_off_arm_does_not_load_and_matches_plain_substrate()
    test_on_arm_loads_once_and_starts_populated()


def _match_rate(raw, space):
    """Fraction of novel words that find ANY anchor above threshold (canon_obj != the word). A
    self-return (canon_obj == word) is canonicalize's NO-MATCH signal and is refused, not grounded."""
    a = R.canonicalize_over_space(raw, space)
    if not a:
        return 0.0
    return sum(1 for w, (o, _c) in a.items() if o != w) / len(a)


def test_resume_does_not_help_grounding():
    import random as _rnd
    snap_dir, offset = _ensure_snapshot()
    man = R.fp.load_manifest(snap_dir)
    start_pi = int(man.get("next_pass_idx", 0))
    # a test slice disjoint from the snapshot (same cursor, taken AFTER the snapshot region)
    _snap, test, info = R.corpus_slices(CORPORA, snapshot_n=offset, test_n=1200)
    assert info["snapshot_test_overlap"] == 0
    gold = R.load_gold()

    # end-to-end arms (delta-only)
    cold = R.cold_state(seed=SEED)
    d_cold = R.read_fixed(cold, test, start_pass_idx=0, source_tag="test")
    cold_prec = R.precision_arms(d_cold["provenance"], gold, _rnd.Random(SEED), np.random.default_rng(SEED))
    resumed = R.resumed_state(snap_dir)
    d_res = R.read_fixed(resumed, test, start_pass_idx=start_pi, source_tag="test")
    res_prec = R.precision_arms(d_res["provenance"], gold, _rnd.Random(SEED), np.random.default_rng(SEED))
    print("[witness] end-to-end new groundings  COLD=%d RESUMED=%d"
          % (d_cold["n_new_grounded"], d_res["n_new_grounded"]))

    # (a) INERT READ: resuming grounds fewer new meanings on the identical read (it knows the words)
    assert d_res["n_new_grounded"] < d_cold["n_new_grounded"], \
        "resume did not reduce new groundings (%d !< %d)" % (
            d_res["n_new_grounded"], d_cold["n_new_grounded"])

    # PURE-MECHANISM probe: identical raw_sums, only the anchor space varies (fresh, pre-read spaces)
    snap_vocab = set(resumed.space.anchors()) | set(resumed.known_seed)
    W = [p["subject"] for p in d_cold["provenance"]
         if p.get("subject") in cold.space._sums and p["subject"] not in snap_vocab]
    raw = {w: cold.space._sums[w] for w in W}
    assert len(W) >= 10, "too few novel words to probe (%d)" % len(W)
    cold_mr = _match_rate(raw, cold.space)
    res_mr = _match_rate(raw, R.resumed_state(snap_dir).space)
    dec_mr = _match_rate(raw, R.decoy_state(snap_dir, np.random.default_rng(SEED)).space)
    print("[witness] pure-probe match_rate  COLD=%.3f RESUMED=%.3f DECOY=%.3f (n=%d)"
          % (cold_mr, res_mr, dec_mr, len(W)))

    # (b) THE ANCHORS DO NOT MATCH: novel words match co-read anchors but NOT the loaded snapshot
    assert res_mr < cold_mr, "resumed match-rate not below cold (%.3f !< %.3f)" % (res_mr, cold_mr)
    # (c) BINS not MEANING: permuting labels cannot change which vectors clear the threshold
    assert abs(res_mr - dec_mr) < 1e-9, \
        "decoy match-rate differs from resumed -- would mean the labels (meaning) mattered"
    # (d) NO correctness: SUBSTRATE precision not CI-separated above its RANDOM floor in either arm
    for tag, p in (("COLD", cold_prec), ("RESUMED", res_prec)):
        sub, rnd = p["SUBSTRATE"], p["RANDOM_ANCHOR"]
        if sub["n"] > 0:
            assert sub["ci_lo"] <= rnd["ci_hi"], \
                "%s: SUBSTRATE precision CI-separated ABOVE random floor (unexpected gain)" % tag


def test_landed_full_run_headline_if_present():
    if not os.path.isfile(LANDED):
        print("[witness] SKIP landed-metrics check (full run not present yet)")
        return
    with open(LANDED, encoding="utf-8") as fh:
        m = json.load(fh)
    units = m.get("units", {})
    units = list(units.values()) if isinstance(units, dict) else units
    cold = [u["arms"]["COLD"]["n_new_grounded"] for u in units]
    res = [u["arms"]["RESUMED"]["n_new_grounded"] for u in units]
    assert cold and res, "landed metrics carry no groundings"
    print("[witness] landed new groundings  COLD mean=%.1f  RESUMED mean=%.1f  (n=%d seeds)"
          % (float(np.mean(cold)), float(np.mean(res)), len(res)))
    assert np.mean(res) < np.mean(cold), "landed: RESUMED did not ground fewer than COLD"


def _main() -> int:
    ok = True
    for fn in (test_wiring_both_ways, test_resume_does_not_help_grounding,
               test_landed_full_run_headline_if_present):
        try:
            fn()
            print("[witness] PASS", fn.__name__)
        except AssertionError as e:
            ok = False
            print("[witness] FAIL", fn.__name__, "--", e, file=sys.stderr)
    print("[witness] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_main())
