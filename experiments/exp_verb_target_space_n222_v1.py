"""exp_verb_target_space_n222_v1 -- ITEM 2 of notes/PLAN_NEXT_24H.md section 4: at a sample size
where a margin COULD separate at all, can the EXISTING 12-dim target space order verb pairs when a
known-answer arm is handed the right answer?

THIS MEASURES THE INSTRUMENT, NOT A CAPABILITY. K1_OWN_NORMS is the known-answer arm: both words of
every SimLex pair keep their REAL 12-dim grounding-norms code (hdlab.grounded_similarity's own
z-scored Lancaster+Brysbaert table). No bridging, no held-out endpoint, no new target-space channel
is built here -- it is a measurement of what already exists.

WHY (RETRACTION 2, notes/PLAN_NEXT_24H.md section 0). The claim "our instrument cannot resolve
verbs even when handed the right answer" -- used to motivate building a new channel -- is currently
SUSPENDED, not confirmed wrong. Its only measurement,
data/exp_thematic_relation_supply_bridged_grounding_v2/metrics.json,
HILLS_2009_NOUN_VERB_FALSIFIER.known_answer_K1.V, ran at n=86 (bridging requires a held-out
endpoint) where the scramble floor 0.1776-0.1814 IS the null distribution's OWN width:
1.645/sqrt(85) = 0.1784. No arm of any quality could separate at that n. K1_OWN_NORMS needs no
bridge and can run on all 222 SimLex verb pairs, where the null width falls to ~0.1107. This script
runs that measurement and settles retraction 2 in one direction or the other.

POPULATION: data/encoder_eval_benchmarks/simlex999.txt, RECOUNTED at runtime (self_test() and
run() both report the count they measure; the plan's expectation is N 666 / V 222 / A 111 but this
script does not assume it). The 86-pair bridged stratum and this 222-pair stratum are DIFFERENT
POPULATIONS -- no floor, null or CI here is imported from the bridging cells; every one is
recomputed on this population, per standing rule 2.

LIBRARIES IMPORTED, NEVER EDITED (this cell is a leaner sibling of the two bridging cells that
established this exact scorer and floor battery; per CLAUDE.md "sibling cell, imported" convention):
  exp_encoding_quality_instrument_v2   (INS)  _l2n, _spearman -- THE SCORER. hdlab.grounded_
                                               similarity.grounded_similarity() is NEVER used (it
                                               saturates 76.18% of SimLex pairs onto two values);
                                               the scorer is the raw 12-dim vector, L2-normalised,
                                               plain cosine, exactly as the bridging cells state.
  exp_meaning_asset_fair_test_v1       (FT)   T_MARGIN_MIN, boot_rho, boot_rho_diff, band
  exp_bridged_grounding_from_core_v1   (CELL) load_simlex_pos, pair_cos, corpus_counts
  exp_selectional_constraint_bridge_v1 (SEL)  build_floors (4-floor incl F_CONSTANT_PROTOTYPE),
                                               _score_cos (per-floor margin/CI/band breakdown),
                                               POS_MIN_N, ORTHO_DIMS, the FLOOR_* name constants
  exp_task_degeneracy_v1               ruler_mode_gate() -- HARD GATE, called in self_test() AND
                                               run(). exp_encoding_quality_instrument_v2 resolves
                                               RUN_MODE from argv AT IMPORT: the bare token
                                               "--smoke" anywhere in argv silently drops V to 512
                                               and CORPUS_BYTES to a fraction of 64,000,000, which
                                               would silently recompute the frequency floor on a
                                               different corpus with no error. THIS IS WHY THIS
                                               CELL'S OWN FLAG IS "--grid reduced", NOT "--smoke"
                                               (standing rule 11 / exp_selectional_constraint_
                                               bridge_v1's own documented trap, re-earned here).

THE F_CONSTANT_PROTOTYPE GENERALISATION, STATED (OURS, not inherited unmodified -- read before
trusting this floor). The two sibling bridging cells' construction replaces the BRIDGED endpoint's
code with the mean CORE direction while the OTHER endpoint stays real -- an asymmetry that exists
only because bridging holds one endpoint out. K1_OWN_NORMS has no held-out role: both endpoints of
every pair are real. Two honest options were considered:
  (a) replace BOTH endpoints with the same constant -- every pair's cosine is then IDENTICALLY 1.0,
      so the correlation against gold has zero variance and is mathematically UNDEFINED. This is
      computed and reported explicitly as "DEGENERATE" (nan), never silently skipped.
  (b) generalise the sibling construction by replacing ONE endpoint, scored under BOTH orderings
      (word1 constant/word2 real, and word2 constant/word1 real -- SimLex's own column order
      carries no semantic role), taking whichever ordering scores HIGHER (harder to beat) as the
      floor. This mirrors this codebase's own "take the max variant" convention (scramble_floor's
      own row-permutation-vs-gold-permutation max; build_floors' own per-dim / per-channel argmax).
(b) is what is reported as F_CONSTANT_PROTOTYPE below; (a) is reported alongside, per stratum, as
"rho_both_endpoints_constant_DEGENERATE", for transparency. Neither number is imported from any
other population.

TIE CONVENTIONS (standing rule 4, "report tie conventions both ways"). That rule is stated for a
hit@1 instrument, where a tie at the argmax has an optimistic and a conservative reading. A
Spearman correlation has no such ambiguity -- INS._spearman is average-rank tie-corrected and
returns one number. What DOES vary here, and is the closest honest analogue, is which of the two
constant-floor orderings in (b) above is used; BOTH are always reported, never silently the
flattering one.

BAR (plan section 4 ITEM 2): a CI-separated margin over max(F_ORTHOGRAPHIC, F_FREQUENCY_HARDENED,
F_SCRAMBLE_PERM_P95, F_CONSTANT_PROTOTYPE) on THIS population, both constant-floor orderings
reported. Every margin is reported beside its CI half-width and the scramble p95 at this n.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. ASCII-only. CPU. No network.
data/foundation/** is never opened by this cell.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS          # THE SCORER, IMPORTED, NEVER EDITED
import exp_meaning_asset_fair_test_v1 as FT                # verdict machinery, unchanged
import exp_bridged_grounding_from_core_v1 as CELL           # sibling library, NEVER EDITED
import exp_selectional_constraint_bridge_v1 as SEL          # 4-floor battery + scorer, NEVER EDITED
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

ANCHOR_NAME = "verb_target_space_n222_v1"
CODE_VERSION = "v1.0"
PREREG = ("notes/PLAN_NEXT_24H.md section 4 ITEM 2 (2026-08-17) + section 0 RETRACTION 2 -- every "
          "threshold below (bar, floor set, N_PERM>=2000, stop-if) is fixed there, before this "
          "script was written. No separate preregs/*.md file: this item is explicitly a "
          "measurement of an existing target space, not a new channel.")

# THE FLAG IS `--grid reduced`, NOT `--smoke` -- LOAD-BEARING, see module docstring.
_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

# ---- PRE-REGISTERED CONSTANTS, fixed in the plan before this script was written --------------
T_MARGIN_MIN = FT.T_MARGIN_MIN                  # 0.05, inherited, informational only (see report)
N_BOOT = 2000 if SMOKE else 10000
N_PERM = 400 if SMOKE else 2000                 # plan requires >=2000 in full mode
BOOT_SEED = 20260816
POS_TAGS = ("V", "N", "A")
POS_MIN_N = SEL.POS_MIN_N                       # 25

FLOOR_ORTHO, FLOOR_FREQ, FLOOR_SCRAM, FLOOR_CONST = (
    SEL.FLOOR_ORTHO, SEL.FLOOR_FREQ, SEL.FLOOR_SCRAM, SEL.FLOOR_CONST)


def recount_simlex(pairs_all: List[Tuple[str, str, str, float]]) -> Dict:
    """RECOUNTED, not assumed -- the plan's own instruction. Reports whatever is measured."""
    import collections
    c = collections.Counter(p[2] for p in pairs_all)
    return {"N": int(c.get("N", 0)), "V": int(c.get("V", 0)), "A": int(c.get("A", 0)),
            "total": len(pairs_all), "other_tags": {k: int(v) for k, v in c.items()
                                                     if k not in ("N", "V", "A")}}


def load_raw_norms(vocab: List[str]) -> Dict[str, np.ndarray]:
    """RAW (unnormalised) 12-dim grounding-norms row per word. FATAL if any SimLex word is
    missing -- the known-answer arm is compromised, not degraded, if any code is a fallback."""
    from hdlab import grounded_similarity as GS
    tab = GS._table()
    raw: Dict[str, np.ndarray] = {}
    missing = []
    for w in vocab:
        v = tab.get(w.lower())
        if v is None:
            missing.append(w)
        else:
            raw[w] = np.asarray(v, dtype=np.float64)
    if missing:
        raise SystemExit(
            f"[fatal] {len(missing)} of {len(vocab)} SimLex words have no grounded-norms row, "
            f"e.g. {missing[:10]}. K1_OWN_NORMS is supposed to be the KNOWN-ANSWER arm; refusing "
            f"to silently fall back to noise for any word.")
    return raw


def run_stratum(tag: str, strat: List[Tuple[str, str, str, float]], vocab_idx: Dict[str, int],
                X_full: np.ndarray, raw: Dict[str, np.ndarray], counts: Dict[str, int],
                seed: int) -> Dict:
    """Score K1_OWN_NORMS on ONE POS stratum against its own 4-floor battery, own scramble null,
    own CI. Returns a dict with 'status'=NOT_CONSTRUCTIBLE if n < POS_MIN_N (a floor is NOT ready
    below that n, per plan section 4 header)."""
    n = len(strat)
    out: Dict = {
        "pos": tag, "n": n,
        "spearman_ci_halfwidth_approx_1_96_over_sqrt_n_minus_3": (
            round(1.96 / max(n - 3, 1) ** 0.5, 4) if n > 3 else None),
        "null_width_orientation_1_645_over_sqrt_n_minus_1": (
            round(1.645 / max(n - 1, 1) ** 0.5, 4) if n > 1 else None),
    }
    if n < POS_MIN_N:
        out["status"] = "NOT_CONSTRUCTIBLE"
        out["rule"] = f"n < POS_MIN_N={POS_MIN_N}; not a null and not a passed falsifier"
        return out

    ia = np.array([vocab_idx[p[0]] for p in strat])
    ib = np.array([vocab_idx[p[1]] for p in strat])
    gold = np.array([p[3] for p in strat], dtype=np.float64)
    obs = CELL.pair_cos(X_full, ia, ib)

    # ---- F_CONSTANT_PROTOTYPE, generalised (see module docstring) ----
    stratum_words = sorted(set(w for p in strat for w in (p[0], p[1])))
    proto = np.stack([raw[w] for w in stratum_words]).mean(axis=0)
    protoN = INS._l2n(proto[None, :].astype(np.float32))[0]
    cos_w2_replaced = (X_full[ia] @ protoN).astype(np.float64)   # word1 real, word2 -> proto
    cos_w1_replaced = (X_full[ib] @ protoN).astype(np.float64)   # word2 real, word1 -> proto
    rho_w2_replaced = INS._spearman(cos_w2_replaced, gold)
    rho_w1_replaced = INS._spearman(cos_w1_replaced, gold)
    cos_both_constant = np.ones(n, dtype=np.float64)              # cos(protoN, protoN) == 1.0
    rho_degenerate = INS._spearman(cos_both_constant, gold)

    use_w2 = (not np.isfinite(rho_w1_replaced)) or (rho_w2_replaced >= rho_w1_replaced)
    if use_w2:
        const_cos, const_variant = cos_w2_replaced, "word2_replaced_by_stratum_prototype_word1_real"
    else:
        const_cos, const_variant = cos_w1_replaced, "word1_replaced_by_stratum_prototype_word2_real"

    vocab_list = sorted(vocab_idx, key=vocab_idx.get)
    floors = SEL.build_floors(vocab_list, ia, ib, gold, counts, const_cos)

    scored = SEL._score_cos("K1_OWN_NORMS", obs, X_full, ia, ib, gold, floors, seed=seed,
                            light=False)
    scored.pop("_cos", None)
    scored["F_CONSTANT_PROTOTYPE_construction"] = {
        "STATUS": "OURS -- generalised from the sibling bridging cells' asymmetric construction; "
                  "see module docstring for why the exact construction does not type-check on a "
                  "non-bridged population.",
        "variant_used_as_the_reported_floor": const_variant,
        "rho_word2_replaced_word1_real": round(float(rho_w2_replaced), 6),
        "rho_word1_replaced_word2_real": (round(float(rho_w1_replaced), 6)
                                          if np.isfinite(rho_w1_replaced) else None),
        "rho_both_endpoints_constant_DEGENERATE": (
            round(float(rho_degenerate), 6) if np.isfinite(rho_degenerate) else None),
        "both_endpoints_constant_note": "cos(proto, proto) == 1.0 for every pair by construction "
                                        "(zero variance in the scored channel); Spearman is "
                                        "mathematically UNDEFINED there. INS._spearman returns "
                                        "nan on zero-variance input; reported as null, not "
                                        "silently omitted, and NOT used as the reported floor."}
    out.update(scored)
    return out


def self_test() -> Dict:
    from exp_task_degeneracy_v1 import ruler_mode_gate
    gate = ruler_mode_gate()
    if not gate["PASS"]:
        raise SystemExit(f"RULER MODE GATE FAILED -- the frequency floor cannot be trusted: {gate}")
    print(f"[self-test] ruler_mode_gate PASS: {gate}", flush=True)

    a5 = INS._spearman(np.array([1., 2., 3., 4., 5.]), np.array([1., 2., 3., 4., 5.]))
    assert abs(a5 - 1.0) < 1e-9, f"spearman(x,x) != 1.0: {a5}"
    a0 = INS._spearman(np.ones(10), np.arange(10, dtype=float))
    assert np.isnan(a0), f"constant input must give an UNDEFINED (nan) spearman, not {a0}"
    print("[self-test] INS._spearman: self-consistent, nan on zero-variance input", flush=True)

    pairs_all = CELL.load_simlex_pos()
    rc = recount_simlex(pairs_all)
    assert rc["total"] == 999, f"SimLex999 recount total != 999: {rc}"
    print(f"[self-test] SimLex999 recount: {rc}", flush=True)

    vocab = sorted(set(w for p in pairs_all for w in (p[0], p[1])))
    raw = load_raw_norms(vocab)     # fatal internally if any SimLex word is missing
    assert all(raw[w].shape == (12,) for w in vocab[:25]), "norms are not 12-dim"
    print(f"[self-test] {len(vocab)} distinct SimLex words, all resolved in the grounded-norms "
          f"table (zero missing, else load_raw_norms would already have raised)", flush=True)

    vtag = [p for p in pairs_all if p[2] == "V"][:POS_MIN_N + 5]
    vocab2 = sorted(set(w for p in vtag for w in (p[0], p[1])))
    idx2 = {w: i for i, w in enumerate(vocab2)}
    raw2 = load_raw_norms(vocab2)
    X2 = INS._l2n(np.stack([raw2[w] for w in vocab2]).astype(np.float32))
    counts = CELL.corpus_counts()
    res = run_stratum("V", vtag, idx2, X2, raw2, counts, seed=1)
    assert "rho" in res and "band" in res, f"run_stratum did not produce a scored arm: {res}"
    fc = res["F_CONSTANT_PROTOTYPE_construction"]
    assert fc["rho_both_endpoints_constant_DEGENERATE"] is None, (
        "the both-endpoints-constant construction must be degenerate (nan/None), got a real number")
    assert res["floor_rho_by_arm"].get(FLOOR_CONST) is not None, "F_CONSTANT_PROTOTYPE not scored"
    print(f"[self-test] run_stratum mechanics verified on a {len(vtag)}-pair V slice: "
          f"band={res['band']} margin={res['margin_over_strongest_floor']['point']}", flush=True)

    print("[self-test] PASS", flush=True)
    return {"ruler_gate": gate, "recount": rc, "n_vocab": len(vocab), "mini_run": res}


def run() -> Dict:
    t0 = time.time()
    out_dir = str(get_output_dir(ANCHOR_NAME))

    from exp_task_degeneracy_v1 import ruler_mode_gate
    gate = ruler_mode_gate()

    pairs_all = CELL.load_simlex_pos()
    recount = recount_simlex(pairs_all)

    vocab = sorted(set(w for p in pairs_all for w in (p[0], p[1])))
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    raw = load_raw_norms(vocab)
    X_full = INS._l2n(np.stack([raw[w] for w in vocab]).astype(np.float32))
    counts = CELL.corpus_counts()
    print(f"[run] vocab={len(vocab)} words, run_mode={RUN_MODE} N_PERM={N_PERM} N_BOOT={N_BOOT}",
          flush=True)

    results: Dict[str, Dict] = {}
    done = completed_units(out_dir)
    for tag in POS_TAGS:
        key = unit_key(ANCHOR_NAME, RUN_MODE, tag)
        if key in done:
            results[tag] = load_units(out_dir)[key]
            print(f"[ckpt] {tag}: resumed from units.jsonl", flush=True)
            continue
        strat = [p for p in pairs_all if p[2] == tag]
        seed = int(abs(hash((ANCHOR_NAME, RUN_MODE, tag))) % 100000) + 11
        t1 = time.time()
        res = run_stratum(tag, strat, vocab_idx, X_full, raw, counts, seed)
        res["elapsed_s"] = round(time.time() - t1, 2)
        record_unit(out_dir, key, res)
        results[tag] = res
        rho_pt = res.get("rho", {}).get("point") if "rho" in res else None
        p95 = res.get("scramble_null", {}).get("p95") if "scramble_null" in res else None
        print(f"[stratum] {tag} n={res.get('n')} status={res.get('status', 'SCORED')} "
              f"band={res.get('band')} K1_rho={rho_pt} scramble_p95={p95} "
              f"({res['elapsed_s']}s)", flush=True)

    v = results.get("V", {})
    band = v.get("band")
    n_v = v.get("n")
    margin_v = v.get("margin_over_strongest_floor", {})
    strongest_v = v.get("strongest_floor")
    null_width_v = v.get("null_width_orientation_1_645_over_sqrt_n_minus_1")
    p95_v = v.get("scramble_null", {}).get("p95") if "scramble_null" in v else None

    if v.get("status") == "NOT_CONSTRUCTIBLE":
        verdict = "STRATUM_NOT_CONSTRUCTIBLE"
        verdict_msg = (f"V stratum has n={n_v} < POS_MIN_N={POS_MIN_N}; retraction 2 cannot be "
                       f"resolved by this run.")
    elif band == "ABOVE":
        verdict = "RETRACTION_2_CONFIRMED_K1_CLEARS_AT_N222"
        verdict_msg = (
            f"K1_OWN_NORMS clears max(4 floors) CI-separated at n={n_v}: margin "
            f"{margin_v.get('point')} ci95={margin_v.get('ci95')} over strongest floor "
            f"{strongest_v}. Null width orientation {null_width_v}, measured scramble p95 "
            f"{p95_v}. THIS MEASURES THE INSTRUMENT, NOT A CAPABILITY: the existing 12-dim space "
            f"CAN order verb pairs when handed the known answer. Retraction 2 is CONFIRMED; the "
            f"'verbs are unresolvable' claim is dead and no channel build may cite it.")
    else:
        verdict = "RETRACTION_2_MEASURED_K1_DOES_NOT_CLEAR_AT_N222"
        verdict_msg = (
            f"K1_OWN_NORMS does NOT clear max(4 floors) CI-separated at n={n_v} (band={band}, "
            f"margin {margin_v.get('point')} ci95={margin_v.get('ci95')}) over strongest floor "
            f"{strongest_v}. Null width orientation {null_width_v}, measured scramble p95 "
            f"{p95_v}. THIS MEASURES THE INSTRUMENT, NOT A CAPABILITY. Whether this is "
            f"'measured rather than asserted' (plan stop-if ii) or 'power insufficient at every "
            f"available n' (stop-if iii) turns on whether p95 fell toward the null-width "
            f"orientation value or stayed elevated -- read both numbers above before citing "
            f"either reading; this script does not adjudicate that judgment call.")

    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME, "code_version": CODE_VERSION, "prereg": PREREG,
        "run_mode": RUN_MODE, "N_PERM": N_PERM, "N_BOOT": N_BOOT,
        "measures_the_instrument_not_a_capability": True,
        "ruler_mode_gate": gate,
        "population_recount": recount,
        "pos_strata": results,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 2), "summary": verdict_msg,
    }
    write_metrics(Path(out_dir), metrics)
    print(f"[run] DONE in {elapsed:.1f}s -- verdict={verdict}", flush=True)
    return metrics


def main() -> int:
    if _ARGS.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return 0
    m = run()
    print(json.dumps({"verdict": m["verdict"], "verdict_msg": m["verdict_msg"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
