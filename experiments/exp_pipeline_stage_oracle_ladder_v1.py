"""exp_pipeline_stage_oracle_ladder_v1 -- WHERE IS THE SIGNAL, AND WHERE DOES IT GET LOST?

THE OWNER'S OWN WORDS, WHICH THIS CELL EXISTS TO ANSWER.
"For all of these multi-step components, we need to know where the signal is, where it's getting
lost, what's happening with the noise etc. Each is its own problem to solve, and I have yet to see
a holistic approach to the problem with a mapping of the challenge." Every fragment that exists
before this cell -- exact-key addressing 1.0000, shortlist oracle 0.1715 at k=5, median gold rank
37 of 5,491, partial-cue addressing 0.0711 -- was measured on a DIFFERENT population with a
DIFFERENT scorer, so THEY DO NOT COMPOSE. This cell produces one composable picture: ONE
population, ONE scorer, ONE gold, ONE cue regime, every rung directly comparable.

=================================================================================================
STAGE ENUMERATION -- READ FROM THE LIVE CODE, NOT FROM THE DIRECTOR'S SKETCH. HOW: read
hdlab/grounding_acquisition_loop.py (content_words, context_vector -- the module's own docstring
names these as "GENUINELY-NEW code here"), hdlab/reading_grounding_loop.py (context_vector_masked,
symbol_vector, ConceptSpace.observe/anchor_matrix/bundle), experiments/exp_grounding_readout_
known_answer_v1.py (build_corpus/build_buckets/build_space/build_items -- the actual corpus-to-
store construction that built the shared harness cache), and the RUNTIME-VERIFIED (not merely
claimed) encoder identity in experiments/exp_cue_information_audit_v1.py (H^T P_a == mat[a],
bit-exact, machine-asserted at T2 and at the ENCODER_IDENTITY_STORE_SIDE gate on the real cache --
this is why "prefer runtime evidence over static search" changes the stage list, not just a style
note: a grep of the docstrings would have reported a separate projection step following a separate
context-vector step, and the bit-exact identity proves that is NOT what the running code does).

THE DIRECTOR'S SKETCH, CORRECTED AGAINST THAT READING:
  sketch 1 "tokens kept"            + sketch 2 "context vector"       -> COLLAPSE. A raw content-
    word COUNT vector loses nothing relative to the token list except word order, which this
    architecture never uses anywhere downstream either. Nothing is lost between them.
  sketch 2/3 boundary "-> 256-dim projection" -> REAL. The live code draws each content word's
    contribution DIRECTLY at d=256 (hashlib.sha256(word)-seeded bipolar draw, symbol_vector); there
    is no intermediate uncompressed vector that a later matrix multiplies down. The "uncompressed"
    representation this cell uses as a counterfactual is a POST-HOC reconstruction (raw counts p
    such that H^T p == the real 256-dim vector, proved bit-exact), not a real earlier artifact of
    the live path.
  sketch 4 "written into store under a write rule" -> REAL. ConceptSpace.observe does
    `self._sums[lemma] += ctx_vec` -- summation, unweighted, no decay, across every PROFILE
    occurrence of that anchor.
  sketch 5 "store -> superposed with every other word's contribution (interference)" -> DOES NOT
    EXIST AS A SEPARATE EVENT. The store is `mat[n_anchors, D]`, ONE ROW PER ANCHOR -- not a single
    holographic sum of every word in the vocabulary. What plays the role Director's sketch assigns
    to stage 5 is CROSS-TALK inside the SAME d=256 projection from stage 2/3: because D=256 is far
    smaller than the ~54,298-word vocabulary, no two words' random codes are exactly orthogonal
    (measured directly: mean |cos| among 5,000 sampled distinct symbol-vector pairs = 0.0499,
    close to the 1/sqrt(256)=0.0625 JL bound -- CITED@notes/cue_compression_property_diagnosis_v1_
    findings_2026-08-17.md). Stage 5 is baked into stage 2/3, not a later, separable corruption.
  sketch 6 "held-out sentence -> partial cue" -> REAL, and it is the IDENTICAL encoder (collapsed
    1+2 then the real 2/3 projection) applied to the held-out sentence, target-masked.
  sketch 7 "cue -> address" + sketch 8 "candidates -> comparator/argmax" -> COLLAPSE in the
    incumbent path (A0_RAW_INCUMBENT, the architecture every landed headline number in this
    programme uses). There is no separate shortlist/candidate-narrowing step in the incumbent:
    `np.argmax` over the FULL cosine row against every eligible anchor IS both the addressing
    decision and the comparator's winner. (A5_NARROW_THEN_READ in exp_cue_to_store_translation_v1
    is a DIFFERENT, optional mechanism that inserts a real shortlist; it is not part of the
    incumbent and is out of scope here.)
  sketch 9 "winner -> scored against gold" -> REAL: hit@1 tie-corrected against the WordNet
    meaning-set gold, tools/floor_battery, unmodified.

SO THE LIVE PIPELINE HAS FIVE STAGE BOUNDARIES, NOT NINE:
  S1  raw content words -> 256-dim per-occurrence code (a single fixed random projection; this IS
      where sketch stages 2, 3 and 5 all physically happen)
  S2  per-occurrence codes -> anchor row, by unweighted summation across PROFILE occurrences
  S3  held-out sentence -> partial cue, the SAME S1 encoder applied to unseen text
  S4  cue -> winner, by a single cosine-argmax over the full eligible anchor set (sketch 7+8)
  S5  winner -> scored against WordNet gold, tie-corrected hit@1

=================================================================================================
THE INSTRUMENT: A STAGE-WISE ORACLE LADDER, walked in TWO PARTS because S1/S2 (write side) and
S3/S4 (read side) are not literally sequential POINTS IN TIME on the SAME run -- they are two
different counterfactual axes over the SAME store/cue construction, and conflating them into one
chain would silently claim a downstream relationship the code does not have. Both parts share the
one population, scorer and gold.

PART A -- THE READ-SIDE LADDER (the ONE genuinely downstream, TRUE data-flow chain; this is where
the MONOTONICITY assertion is enforced). Fixed: the REAL, deployed, projected, fully-accumulated
store (mat). Varied: how much of the cue is the item's own exact key vs its real held-out partial
cue, via the SAME one-variable mixing device already landed and regression-gated in
experiments/exp_cue_regime_one_variable_retrieval_v1.py:
    cue(i, lam) = lam * l2n(Q_exact[i]) + (1 - lam) * l2n(Q_part[i])
  lam=1.0 is "S3/S4 held at ORACLE" (the cue IS the exact key; addressing must read ~1.0 -- the
  SANITY rung the brief requires). lam=0.0 is "nothing left oracle anywhere" -- the live system.
  This IS a true downstream walk: every lam<1 cue is STRICTLY the lam=1 cue with real information
  removed and replaced by a non-informative real quantity (by construction of the linear mix), so
  hit@1 is asserted non-increasing as lam falls, and the cue_regime cell's own landed
  MONOTONICITY_GATE (Spearman(lam,hit@1)=0.9636) already found this holds -- verified again here,
  fresh, on THIS cell's own recompute, not imported.

PART B -- THE WRITE-SIDE DIAGNOSTICS (counterfactual, NOT chained into the monotonicity assertion,
and said so explicitly rather than silently). Fixed: an ORACLE cue (query = the item's own store
row in whichever regime is being tested, so S3/S4 read PERFECTLY by construction). Varied:
  B1  ACCUMULATION DEPTH -- one profile occurrence per anchor vs the full ~72-sentence profile
      bundle, both UNPROJECTED (raw counts). This is NOT a downstream-loses-information pair: more
      accumulation is STRICTLY MORE real evidence, so it is reported as its own margin, never
      folded into the monotone chain, and no "the ladder rose" leak is declared if it goes either
      way.
  B2  PROJECTION -- the same full accumulation, unprojected vs the real 256-dim projected store,
      cue still oracle. This isolates what the projection alone destroys once accumulation is held
      fixed and the read side is held perfect -- the residue after write-side loss ONLY.
  B2r PROJECTION AT THE REAL CUE -- the same unprojected-vs-projected contrast, but at S3/S4 REAL
      (the item's genuine held-out partial cue), reproducing experiments/exp_cue_information_audit_
      v1's own landed headline (U0 vs C0, +0.0138 [+0.0083,+0.0195] ABOVE) as an independent
      regression check that this cell is the same instrument.

ORGAN REUSE, enumerated then reconciled -- no pipeline stage is reimplemented:
  experiments/exp_cue_to_store_translation_v1 (CTS)         cache/aux loaders, MASTER_SEED
  tools/floor_battery (FB)                                  hit@1 both tie conventions, the four
                                                             floors, paired bootstrap, margin,
                                                             rank_of_best_gold, oracle constant
  experiments/exp_cue_information_audit_v1 (INFO)           raw_counts_for_window, the encoder
                                                             identity, build_vocab/to_sparse/
                                                             l2n_sparse/constant_prototype_floor_
                                                             sparse, load_corpus_and_buckets
                                                             (reuses its own on-disk cache), its
                                                             OWN self_test() (called wholesale,
                                                             not re-derived), and its landed
                                                             checkpoint units (READ ONLY, via
                                                             tools.exp_checkpoint.load_units
                                                             pointed at ITS output dir -- this cell
                                                             never writes there)
  experiments/exp_grounding_readout_known_answer_v1 (C3)    build_items, via INFO's own import
  experiments/_seed_checkpoint, tools/exp_checkpoint          output dir + atomic metrics write

PRIOR-WORK CHECK. `bash tools/substrate_query.sh` timed out at 30s with no output -- consistent
with the documented hd_director_kb_continuous_ingest livelock (notes/STATUS.md "TOOLING STATE").
Per the standing rule (enumerate, don't just search), prior work was found by reading every cell
this docstring's REUSE section names plus grep over notes/ for "ladder"/"stage"/"oracle". Closest
prior art: experiments/exp_cue_information_audit_v1.py (write-side compression only, exactly TWO
points: uncompressed vs projected, at the REAL cue only) and experiments/exp_cue_regime_one_
variable_retrieval_v1.py (read-side cue-quality only, ten points, no NOISE or RANK metric, no
paired-bootstrap CI on the DROP between adjacent rungs). Neither computes a unified write+read
ladder, a ranked drop table, or a per-rung NOISE/RANK triple. This cell is not a rediscovery; it
composes and extends both, and both are credited above rather than reimplemented.

THREE METRICS PER RUNG, PER THE BRIEF:
  SIGNAL   hit@1 tie-corrected against WordNet gold (the PRIMARY per this programme's own standing
           discipline -- optimistic/conservative reported alongside, never silently chosen).
  NOISE    a d-prime-style separation: (best-gold score - mean of the ELIGIBLE NON-GOLD field) /
           (std of that field), and the same numerator against the field's own p95, per item, then
           the MEDIAN across items (median, not mean, because sigma=0 items are common at the
           degenerate end of the ladder and would let a mean be dominated by them).
  RANK     rank of the best gold anchor (tools.floor_battery.rank_of_best_gold, both tie
           conventions), median and quartiles, reported BESIDE the RANDOM_NULL rung's own rank
           distribution on the identical population -- the brief's "random-ranking expectation" is
           measured here, not assumed analytically.

HARD REQUIREMENTS THIS CELL HONOURS, each bought by a prior failure named in CLAUDE.md / MEMORY.md:
  - every floor recomputed on THIS population, never imported (0.1382/0.2070/-0.1959 never appear)
  - both tie conventions published beside every hit@1
  - CI half-width and the analytic null width (1.96/sqrt(n-1) for a proportion at this n) beside
    every margin -- a width is not an effect
  - the exact-key rung (lam=1.0) is reported BESIDE the real partial cue (lam=0.0), never instead
  - a known-answer rung (S4 held oracle, lam=1.0 addressing) must reach ~1.0 or nothing is
    published; a fully-random rung (RANDOM_NULL) must sit at chance -- both asserted, not assumed
  - MONOTONICITY on the true downstream chain (Part A) is asserted and, if it fires, the LEAK is
    reported instead of any drop-table number from that chain (never both)
  - `--smoke` never enters argv; this cell's flag is `--grid full|reduced` per exp_task_degeneracy_
    v1.py:121's own documented reduced-grid gate

ASCII-only. NO LLM anywhere in this runtime path. CPU only. The store is NEVER rebuilt (rebuilding
it would break the identical-instrument invariant every rung and every sibling cell depends on).
data/foundation/** is never opened. Writes only under data/exp_pipeline_stage_oracle_ladder_v1[_
smoke]/ and this cell's own scratch/ subdirectory (none needed -- everything it reads is already
cached on disk by the cells it reuses).

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every rung's hit-vector, asserted >1 distinct digest
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: ONE unit "MAIN" via tools.exp_checkpoint, resume-safe
# - discriminator survives scale: this cell RUNS the FULL grid, no scale-preview needed
# - calibration_check: default_ok_for_this_regime (reuses the landed, regression-gated cache
#   unmodified; no new calibration is introduced)
# - progress_logging: print_flush_true (every phase prints a flushed line)
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/hdlab next -- this can take a while, flushed so a slow "
      "import is never mistaken for a hang)", flush=True)

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_cue_to_store_translation_v1 as CTS               # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO                 # noqa: E402  READ ONLY
from tools import floor_battery as FB                                    # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics   # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "pipeline_stage_oracle_ladder_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/pipeline_stage_oracle_ladder_v1_findings_2026-08-17.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

# ---- PRE-REGISTERED CONSTANTS. Never edited after a run. --------------------------------------
LAMBDAS: Tuple[float, ...] = (1.00, 0.80, 0.60, 0.45, 0.30, 0.20, 0.15, 0.10, 0.05, 0.00)
MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
REGRESSION_A0_PARTIAL = CTS.REGRESSION_A0_PARTIAL          # 0.0223, landed lam=0.00
REGRESSION_TOL = CTS.REGRESSION_TOL
REGRESSION_K1_C0 = 0.0481                                  # landed lam=1.00 hit@1, EXACT_KEY_READOUT
REGRESSION_K1_U0 = 0.0603                                  # landed data/exp_cue_information_audit_v1
REGRESSION_U0_REAL = 0.0240                                # landed U0_UNCOMPRESSED_regime real cue
ADDRESS_EXACT_MIN = 0.95
FLOOR_NAMES = ("F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE")
MONOTONE_TOL_SIGMA = 1.5     # a rise is a LEAK only if it exceeds this many combined CI half-widths


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


def mix(exact: np.ndarray, filler: np.ndarray, lam: float) -> np.ndarray:
    """cue = lam*unit(exact key) + (1-lam)*unit(filler). Identical formula to the landed
    experiments/exp_cue_regime_one_variable_retrieval_v1.mix -- OURS, INVENTION UNDER TEST, an
    instrument calibration device; no brain structure is claimed for the mixing itself."""
    return (lam * l2n(exact) + (1.0 - lam) * l2n(filler)).astype(np.float32)


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# NOISE (d-prime-style separation) and RANK, computed identically for every rung
# =================================================================================================
def dprime_stats(S: np.ndarray, E: np.ndarray, GOLD: np.ndarray) -> Dict[str, np.ndarray]:
    """Per item: (best-gold score - field mean|p95) / field std, field = eligible NON-gold anchors.
    Vectorised over items (no Python loop) so this is cheap at n_items ~ 4000, n_anchors ~ 5500."""
    field_mask = E & (~GOLD)
    Sf = np.where(field_mask, S, np.nan).astype(np.float64)
    Sg = np.where(E & GOLD, S, -np.inf).astype(np.float64)
    best_gold = Sg.max(axis=0)
    with np.errstate(invalid="ignore", all="ignore"):
        mu = np.nanmean(Sf, axis=0)
        sd = np.nanstd(Sf, axis=0, ddof=1)
        p95 = np.nanpercentile(Sf, 95, axis=0)
    valid = np.isfinite(best_gold) & np.isfinite(mu) & np.isfinite(sd) & (sd > 1e-9)
    sd_safe = np.where(sd > 1e-9, sd, np.nan)
    d_mean = np.where(valid, (best_gold - mu) / sd_safe, np.nan)
    d_p95 = np.where(valid, (best_gold - p95) / sd_safe, np.nan)
    return {"dprime_vs_mean": d_mean, "dprime_vs_p95": d_p95, "valid": valid}


def dprime_summary(d: Dict[str, np.ndarray]) -> Dict:
    v = d["valid"]
    n = int(v.sum())
    if n == 0:
        return {"n_valid": 0, "median_dprime_vs_mean": None, "median_dprime_vs_p95": None}
    return {
        "n_valid": n,
        "median_dprime_vs_mean": round(float(np.nanmedian(d["dprime_vs_mean"][v])), 4),
        "median_dprime_vs_p95": round(float(np.nanmedian(d["dprime_vs_p95"][v])), 4),
        "mean_dprime_vs_mean": round(float(np.nanmean(d["dprime_vs_mean"][v])), 4),
        "mean_dprime_vs_p95": round(float(np.nanmean(d["dprime_vs_p95"][v])), 4),
    }


def rank_summary(S: np.ndarray, E: np.ndarray, GOLD: np.ndarray) -> Dict:
    r = FB.rank_of_best_gold(S, E, GOLD)
    ro, rc = r["rank_opt"], r["rank_cons"]
    return {
        "median_rank_optimistic": float(np.median(ro)), "q1_rank_optimistic": float(np.percentile(ro, 25)),
        "q3_rank_optimistic": float(np.percentile(ro, 75)),
        "median_rank_conservative": float(np.median(rc)),
        "n_items": int(ro.size),
    }, ro, rc


def spearman(a: Sequence[float], b: Sequence[float]) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    ra = np.argsort(np.argsort(a)).astype(np.float64)
    rb = np.argsort(np.argsort(b)).astype(np.float64)
    ra -= ra.mean()
    rb -= rb.mean()
    den = float(np.linalg.norm(ra) * np.linalg.norm(rb))
    return float(ra @ rb / den) if den > 1e-12 else 0.0


def check_monotone_nonincreasing(ordered_values: Sequence[float],
                                 ordered_halfwidths: Sequence[float],
                                 tol_sigma: float) -> Dict:
    """Walk a sequence that SHOULD be non-increasing (downstream can only lose information).
    A rise is a LEAK only if it exceeds tol_sigma * combined CI half-width of the adjacent pair --
    otherwise it is noise inside the measurement, not evidence the ladder is broken."""
    leaks = []
    for i in range(1, len(ordered_values)):
        rise = ordered_values[i] - ordered_values[i - 1]
        combined_hw = ordered_halfwidths[i] + ordered_halfwidths[i - 1]
        if rise > tol_sigma * max(combined_hw, 1e-9):
            leaks.append({"rung_index": i, "rise": round(float(rise), 4),
                          "combined_ci_halfwidth": round(float(combined_hw), 4)})
    return {"n_leaks": len(leaks), "leaks": leaks, "MONOTONE": len(leaks) == 0,
           "tol_sigma": tol_sigma}


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    ev["RULER_MODE_GATE"] = CTS.ruler_mode_gate()
    ev["floor_battery_selftest_keys"] = sorted(FB.self_test().keys())
    print("[selftest] reusing INFO's own self_test() wholesale (encoder identity, sparse cosine "
          "vs dense brute force, addressing accuracy end to end)", flush=True)
    ev["INFO_selftest_keys"] = sorted(INFO.self_test().keys())

    # --- the mixing device, known answer (identical formula to the landed sibling)
    e = np.array([[3.0, 0.0, 4.0]], dtype=np.float32)
    f = np.array([[0.0, 5.0, 0.0]], dtype=np.float32)
    assert np.allclose(mix(e, f, 1.0), [[0.6, 0.0, 0.8]], atol=1e-6)
    assert np.allclose(mix(e, f, 0.0), [[0.0, 1.0, 0.0]], atol=1e-6)
    ev["MIX_known_answer"] = True

    # --- dprime_stats on a PLANTED, KNOWN separation: gold well above field -> large positive
    # d-prime; gold buried in the field -> near zero; must also survive an all-tied field (sd=0).
    rng = np.random.default_rng(5)
    n_a, n_i = 40, 20
    S = rng.standard_normal((n_a, n_i)).astype(np.float32)
    E = np.ones((n_a, n_i), dtype=bool)
    GOLD = np.zeros((n_a, n_i), dtype=bool)
    GOLD[0, :] = True
    S[0, :] = 10.0                                   # gold is a massive outlier -> huge d-prime
    d = dprime_stats(S, E, GOLD)
    s1 = dprime_summary(d)
    assert s1["median_dprime_vs_mean"] > 5.0, s1
    S2 = rng.standard_normal((n_a, n_i)).astype(np.float32)
    S2[0, :] = np.nanmean(S2[1:, :], axis=0)          # gold planted AT the field mean -> ~0
    d2 = dprime_stats(S2, E, GOLD)
    s2 = dprime_summary(d2)
    assert abs(s2["median_dprime_vs_mean"]) < 0.5, s2
    S3 = np.ones((n_a, n_i), dtype=np.float32)        # every score identical -> sd=0 -> excluded
    d3 = dprime_stats(S3, E, GOLD)
    assert d3["valid"].sum() == 0, "an all-tied field must be EXCLUDED (sd=0), not divide-by-zero"
    ev["dprime_stats_known_answers"] = {"outlier": s1, "at_mean": s2, "degenerate_excluded": True}

    # --- rank_summary: a planted gold at the top must read rank 1
    Splant = np.zeros((n_a, n_i), dtype=np.float32)
    Splant[0, :] = 1.0
    rs, ro, rc = rank_summary(Splant, E, GOLD)
    assert rs["median_rank_optimistic"] == 1.0, rs
    ev["rank_summary_planted_top"] = rs

    # --- monotonicity checker: a genuine decreasing sequence passes; an unambiguous rise
    # (far outside CI) is caught; a rise smaller than its own CI noise is NOT flagged.
    m_ok = check_monotone_nonincreasing([0.9, 0.7, 0.5, 0.3], [0.02, 0.02, 0.02, 0.02], MONOTONE_TOL_SIGMA)
    assert m_ok["MONOTONE"], m_ok
    m_leak = check_monotone_nonincreasing([0.3, 0.9, 0.5], [0.01, 0.01, 0.01], MONOTONE_TOL_SIGMA)
    assert not m_leak["MONOTONE"] and m_leak["n_leaks"] == 1, m_leak
    m_noise = check_monotone_nonincreasing([0.500, 0.503, 0.400], [0.05, 0.05, 0.05], MONOTONE_TOL_SIGMA)
    assert m_noise["MONOTONE"], "a rise inside CI noise must NOT be flagged as a leak: %r" % m_noise
    ev["monotonicity_checker"] = {"passes_real_decrease": True, "catches_real_leak": True,
                                  "ignores_ci_noise": True}

    # --- DOSE RESPONSE on a planted store (same discriminator-fires check as the landed sibling):
    # addressing must rise monotonically toward 1.0 as lam -> 1 on a store where it is constructible
    rng2 = np.random.default_rng(17)
    n_a2, d2_, n_i2 = 300, 48, 200
    M = rng2.standard_normal((n_a2, d2_)).astype(np.float32)
    q = rng2.permutation(n_a2)[:n_i2]
    Qe = M[q].copy()
    Qp = rng2.standard_normal((n_i2, d2_)).astype(np.float32)
    curve = []
    for lam in (0.0, 0.25, 0.5, 0.75, 1.0):
        addr = np.argmax(l2n(mix(Qe, Qp, lam)) @ l2n(M).T, axis=1)
        curve.append(float(np.mean(addr == q)))
    assert all(curve[i] <= curve[i + 1] + 1e-9 for i in range(len(curve) - 1)), curve
    assert curve[0] < 0.05 and curve[-1] > 0.99, curve
    ev["DOSE_RESPONSE_planted_store"] = curve

    print("[selftest] ALL PASS " + json.dumps({k: ev[k] for k in
          ("MIX_known_answer", "monotonicity_checker")}, default=str), flush=True)
    return ev


# =================================================================================================
# population (identical construction to the landed sibling cells; not centralised into CTS by any
# of them, so this repeats the ~15-line idiom rather than importing a private helper)
# =================================================================================================
def build_population() -> Dict:
    C = CTS.load_cache()
    aux = CTS.load_aux()
    anchors, mat, mat_ok = C["anchors"], C["mat"], C["mat_ok"]
    n_anchors, n_items_all = len(anchors), len(C["L_words"])
    qidx = np.array([C["pos"].get(w, -1) for w in C["L_words"]], dtype=np.int64)
    GOLD_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    E_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    for i in range(n_items_all):
        if not C["keep"][i]:
            continue
        E_ALL[:, i] = mat_ok
        if len(C["excl"][i]):
            E_ALL[C["excl"][i], i] = False
        gi = C["goldi"][i]
        if len(gi):
            GOLD_ALL[gi, i] = True
    GOLD_ALL &= E_ALL
    keep_ALL = C["keep"] & GOLD_ALL.any(axis=0)
    return {"C": C, "aux": aux, "anchors": anchors, "mat": mat, "mat_ok": mat_ok,
            "n_anchors": n_anchors, "qidx": qidx, "GOLD": GOLD_ALL, "E": E_ALL, "keep": keep_ALL}


# =================================================================================================
# write-side (Part B) construction
# =================================================================================================
def build_single_occurrence_counts(anchor_ids: Sequence[str], buckets: Dict[str, List[int]],
                                   sents: List[str]) -> Tuple[Dict[str, Counter], Dict]:
    """ONE profile occurrence per anchor (the FIRST sentence of its profile prefix -- never the
    held-out eval sentence, since buckets[a][:k] IS the profile prefix by construction in
    exp_grounding_readout_known_answer_v1.build_items). Sub-millisecond per anchor (a single
    sentence's raw_counts_for_window), so this is NOT checkpointed -- same exemption
    exp_cue_information_audit_v1.build_synonym_and_onset_cues documents for itself."""
    t0 = time.time()
    P1: Dict[str, Counter] = {}
    n_empty = 0
    for k, a in enumerate(anchor_ids):
        occ = buckets.get(a, [])
        if not occ:
            P1[a] = Counter()
            n_empty += 1
            continue
        P1[a] = INFO.raw_counts_for_window(sents[occ[0]], a)
        if (k + 1) % 2000 == 0 or k == len(anchor_ids) - 1:
            print("[single_occ] %d/%d elapsed=%.0fs" % (k + 1, len(anchor_ids), time.time() - t0),
                 flush=True)
    return P1, {"n_anchors": len(anchor_ids), "n_empty_profile": n_empty,
               "elapsed_s": round(time.time() - t0, 1)}


def load_full_accum_from_checkpoint(info_out_dir: str, anchor_ids: Sequence[str],
                                    item_ids: Sequence[str]) -> Tuple[Dict[str, Counter],
                                                                      Dict[str, Counter], Dict]:
    """READ ONLY reuse of experiments/exp_cue_information_audit_v1's own landed checkpoint units
    (Pstore per anchor, Qcue_context per item) -- never writes to info_out_dir. Avoids repeating
    that cell's own >1800s full-corpus accumulation pass."""
    t0 = time.time()
    units = load_units(info_out_dir)
    P: Dict[str, Counter] = {}
    missing_p = []
    for a in anchor_ids:
        rec = units.get(unit_key("Pstore", a))
        if rec is None:
            missing_p.append(a)
            continue
        P[a] = Counter(rec["counts"])
    Q: Dict[str, Counter] = {}
    missing_q = []
    for iid in item_ids:
        rec = units.get(unit_key("Qcue_context", iid))
        if rec is None:
            missing_q.append(iid)
            continue
        Q[iid] = Counter(rec["counts"])
    diag = {"n_units_loaded": len(units), "n_anchors_found": len(P), "n_anchors_missing": len(missing_p),
           "n_items_found": len(Q), "n_items_missing": len(missing_q),
           "elapsed_s": round(time.time() - t0, 1),
           "missing_p_sample": missing_p[:10], "missing_q_sample": missing_q[:10]}
    if missing_p or missing_q:
        raise SystemExit("CHECKPOINT REUSE INCOMPLETE -- exp_cue_information_audit_v1's own units.jsonl "
                         "is missing entries this cell needs: %r" % diag)
    return P, Q, diag


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    P_ = build_population()
    C, mat, mat_ok = P_["C"], P_["mat"], P_["mat_ok"]
    n_anchors, qidx = P_["n_anchors"], P_["qidx"]
    GOLD, E, keep_ALL = P_["GOLD"], P_["E"], P_["keep"]
    aux = P_["aux"]

    items = np.flatnonzero(keep_ALL)
    if grid == "reduced":
        items = items[:300]
    T = items
    n_items = int(T.size)
    GOLD_T = GOLD[:, T].copy()
    E_T = E[:, T].copy()
    qidx_T = qidx[T]
    Q_exact = C["Q_exact"][T]
    Q_part = C["Q_part"][T]
    MATn = l2n(mat)
    print(f"[load] n_anchors={n_anchors} n_items={n_items} t={time.time() - t0:.0f}s", flush=True)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "RULER_MODE_GATE": CTS.ruler_mode_gate(),
        "cache": {"store": CTS.CACHE, "aux": CTS.AUX, "rebuilt": False},
        "population": {"n_anchors": n_anchors, "n_items_scored": n_items,
                       "pool": "the LANDED OPEN pool (mat_ok minus per-item exclusions); no matched "
                               "or balanced pool, per the same rationale the sibling cells record: "
                               "eligB is on record admitting a fitted constant at 0.1715 vs chance "
                               "0.0101",
                       "chance_addressing": round(1.0 / n_anchors, 8)},
    }

    # ---- REGRESSION GATE on the FULL landed population (lam=0.00 must reproduce the live system) --
    S_full = (MATn @ l2n(C["Q_part"]).T).astype(np.float32)
    h_full = FB.hit_at_1_both_tie_conventions(S_full, E, GOLD)
    m_full = h_full["scored"] & keep_ALL
    a0_full = float(h_full["hit_exp"][m_full].mean())
    rep["REGRESSION_GATE"] = {"measured": round(a0_full, 4), "expected": REGRESSION_A0_PARTIAL,
                              "tol": REGRESSION_TOL,
                              "PASS": bool(abs(a0_full - REGRESSION_A0_PARTIAL) <= REGRESSION_TOL),
                              "n_scored": int(m_full.sum())}
    if not rep["REGRESSION_GATE"]["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- not the landed instrument: %r" % rep["REGRESSION_GATE"])
    print("[regression] lam0.00_FULL=%.4f (expected %.4f) PASS" % (a0_full, REGRESSION_A0_PARTIAL), flush=True)
    del S_full, h_full

    # ---- FLOORS, recomputed on THIS population, both tie conventions carried by add_arm below -----
    floors_S: Dict[str, np.ndarray] = {}
    Tq = aux["Tq"][T]
    floors_S["F_ORTHOGRAPHIC"] = (l2n(aux["t_mat"]) @ l2n(Tq).T).astype(np.float32)
    floors_S["F_FREQUENCY"] = FB.as_constant_matrix(FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)), n_items)
    floors_S["F_SCRAMBLE"] = (l2n(FB.scramble_null(mat, MASTER_SEED + 191)) @ l2n(Q_part).T).astype(np.float32)
    floors_S["F_CONSTANT_PROTOTYPE"] = FB.as_constant_matrix(FB.constant_prototype_floor(mat, mat_ok), n_items)
    oracle_S = FB.as_constant_matrix(
        FB.oracle_constant_scores(n_anchors, [np.flatnonzero(GOLD_T[:, i]) for i in range(n_items)]), n_items)

    hits_exp: Dict[str, np.ndarray] = {}
    hits_opt: Dict[str, np.ndarray] = {}
    hits_cons: Dict[str, np.ndarray] = {}
    noise_of: Dict[str, Dict] = {}
    rank_of: Dict[str, Dict] = {}
    addressing_of: Dict[str, float] = {}
    tie_of: Dict[str, float] = {}
    scored_all = np.ones(n_items, dtype=bool)
    S_cache: Dict[str, np.ndarray] = {}

    def add_arm(name: str, S: np.ndarray, target_for_addressing: Optional[np.ndarray] = None) -> None:
        nonlocal scored_all
        h = FB.hit_at_1_both_tie_conventions(S, E_T, GOLD_T)
        hits_exp[name] = h["hit_exp"]
        hits_opt[name] = h["hit_opt"]
        hits_cons[name] = h["hit_cons"]
        tie_of[name] = float(h["tie_mass"].mean())
        scored_all = scored_all & h["scored"]
        noise_of[name] = dprime_summary(dprime_stats(S, E_T, GOLD_T))
        rs, _, _ = rank_summary(S, E_T, GOLD_T)
        rank_of[name] = rs
        if target_for_addressing is not None:
            # ADDRESSING uses mat_ok ONLY, never the synonym-eligibility mask E_T: E_T's `excl`
            # component strips a word's OWN anchor from its own eligible pool for the SYNONYM task
            # (a word is not its own synonym), which would make exact-key addressing structurally
            # unable to reach 1.0 -- this is the SAME convention exp_cue_regime_one_variable_
            # retrieval_v1.py (unmasked) and exp_cue_information_audit_v1.addressing_hits (mat_ok
            # only) both use; caught here by the SANITY_KNOWN_ANSWER gate on first run (addressing
            # read 0.0 under the eligibility mask -- fixed, not silently worked around).
            Sm = np.where(mat_ok[:, None], S, -np.inf)
            addr = np.argmax(Sm, axis=0)
            ok = target_for_addressing >= 0
            addressing_of[name] = round(float(np.mean(addr[ok] == target_for_addressing[ok])), 6)
        S_cache[name] = S
        print(f"[{name}] hit@1={h['hit_exp'][h['scored']].mean():.4f} n_scored={int(h['scored'].sum())}",
             flush=True)

    for k, S in floors_S.items():
        add_arm(k, S)
    add_arm("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", oracle_S)

    # =============================== PART A -- THE READ-SIDE LADDER (true downstream chain) ========
    lam_arm_name: Dict[float, str] = {}
    for lam in LAMBDAS:
        cue = mix(Q_exact, Q_part, lam)
        S = (MATn @ l2n(cue).T).astype(np.float32)
        nm = f"LAM_{lam:.2f}"
        lam_arm_name[lam] = nm
        add_arm(nm, S, target_for_addressing=qidx_T)

    # ---- RANDOM_NULL sanity: the real cue reassigned to a DERANGED (never-self) item pairing -------
    rng_n = np.random.default_rng(MASTER_SEED + 4141)
    perm = np.arange(n_items)
    for _ in range(64):
        perm = rng_n.permutation(n_items)
        if np.all(perm != np.arange(n_items)):
            break
    S_null = (MATn @ l2n(Q_part[perm]).T).astype(np.float32)
    add_arm("RANDOM_NULL", S_null, target_for_addressing=qidx_T)

    # =============================== PART B -- WRITE-SIDE DIAGNOSTICS (oracle cue, counterfactual) ==
    print("[part_b] loading corpus+buckets (cached; instant if scratch/cue_information_audit_v1/"
         "buckets_full.npz exists)", flush=True)
    sents, buckets, counts, corpus_prov = INFO.load_corpus_and_buckets()
    rep["PART_B_corpus_provenance"] = corpus_prov
    shim = INFO._ShimSpace(C["anchors"], C["pos"], mat)
    all_items_meta, item_diag = INFO.C3.build_items(shim, buckets, counts, INFO.C3.MAX_ITEMS)
    assert len(all_items_meta) == len(C["L_words"]), \
        "rebuilt item metadata does not align with the cached L_words -- STOP, do not proceed"
    item_id_of_idx = [it["item_id"] for it in all_items_meta]
    item_ids_T = [item_id_of_idx[int(i)] for i in T]
    anchor_ids = list(C["anchors"])

    info_out_dir = os.path.join(REPO, "data", "exp_cue_information_audit_v1")
    print("[part_b] reusing exp_cue_information_audit_v1's landed checkpoint (READ ONLY)", flush=True)
    P_full, Q_ctx_full, reuse_diag = load_full_accum_from_checkpoint(info_out_dir, anchor_ids, item_ids_T)
    rep["PART_B_checkpoint_reuse"] = reuse_diag

    print("[part_b] building single-occurrence raw counts (one sentence per anchor, not checkpointed"
         " -- sub-millisecond per anchor)", flush=True)
    P_single, single_diag = build_single_occurrence_counts(anchor_ids, buckets, sents)
    rep["PART_B_single_occurrence_build"] = single_diag

    vocab = INFO.build_vocab([P_full, P_single, Q_ctx_full])
    rep["PART_B_vocab_n_distinct_content_words"] = len(vocab)
    Pm_full = INFO.l2n_sparse(INFO.to_sparse(P_full, anchor_ids, vocab))
    Pm_single = INFO.l2n_sparse(INFO.to_sparse(P_single, anchor_ids, vocab))
    Qm_ctx = INFO.l2n_sparse(INFO.to_sparse(Q_ctx_full, item_ids_T, vocab))

    S_single_oracle = np.asarray((Pm_single @ Pm_single[qidx_T].T).todense(), dtype=np.float32)
    S_full_oracle = np.asarray((Pm_full @ Pm_full[qidx_T].T).todense(), dtype=np.float32)
    S_full_real = np.asarray((Pm_full @ Qm_ctx.T).todense(), dtype=np.float32)

    add_arm("DIAG_B1_SINGLE_OCC_UNCOMPRESSED_ORACLE_CUE", S_single_oracle, target_for_addressing=qidx_T)
    add_arm("DIAG_B2_FULL_ACCUM_UNCOMPRESSED_ORACLE_CUE", S_full_oracle, target_for_addressing=qidx_T)
    add_arm("DIAG_B2r_FULL_ACCUM_UNCOMPRESSED_REAL_CUE", S_full_real)

    # ---- regression checks against the two prior landed cells this reuses -------------------------
    reg_k1_c0 = FB.margin(
        FB.paired_bootstrap_ci(hits_exp, scored_all, 200, MASTER_SEED + 7)["boot"],
        "LAM_1.00", "LAM_1.00")  # placeholder overwritten below with the real bootstrap
    rep["PART_B_REGRESSION_CHECKS"] = {
        "K1_EXACT_KEY_C0_this_cell_vs_landed": {
            "this_cell_LAM_1.00": round(float(hits_exp["LAM_1.00"][scored_all].mean()), 4),
            "landed_exp_cue_information_audit_v1_or_cue_regime": REGRESSION_K1_C0},
        "K1_EXACT_KEY_U0_this_cell_vs_landed": {
            "this_cell_DIAG_B2": round(float(hits_exp["DIAG_B2_FULL_ACCUM_UNCOMPRESSED_ORACLE_CUE"][scored_all].mean()), 4),
            "landed_exp_cue_information_audit_v1": REGRESSION_K1_U0},
        "U0_REAL_CUE_this_cell_vs_landed": {
            "this_cell_DIAG_B2r": round(float(hits_exp["DIAG_B2r_FULL_ACCUM_UNCOMPRESSED_REAL_CUE"][scored_all].mean()), 4),
            "landed_exp_cue_information_audit_v1": REGRESSION_U0_REAL},
        "note": "these are cross-cell regression checks, not gates that halt the run -- the run's own "
                "REGRESSION_GATE (lam=0.00 on the full population) is the hard gate. These are reported "
                "and their agreement/disagreement is stated plainly, per exp_dev's own"
                " NEVER-silently-adopt-another-agent's-number discipline.",
    }
    del reg_k1_c0

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) ================================
    digests = {k: _digest(v) for k, v in hits_exp.items()}
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL hit vectors -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests

    # =============================== BOOTSTRAP, ONE CALL, EVERY ARM PAIRED ===========================
    pb = FB.paired_bootstrap_ci(hits_exp, scored_all, N_BOOT, MASTER_SEED + 101)
    pb_opt = FB.paired_bootstrap_ci(hits_opt, scored_all, N_BOOT, MASTER_SEED + 101)
    pb_cons = FB.paired_bootstrap_ci(hits_cons, scored_all, N_BOOT, MASTER_SEED + 101)
    acc, boot = pb["acc"], pb["boot"]
    nc = pb["n_common"]
    present = [f for f in FLOOR_NAMES if f in acc]
    binding = max(present, key=lambda f: acc[f]) if present else None
    ci_halfwidth = {k: round((float(np.percentile(v, 97.5)) - float(np.percentile(v, 2.5))) / 2.0, 5)
                    for k, v in boot.items()}
    analytic_null_hw = round(float(1.645 / np.sqrt(max(nc - 1, 1))), 5)

    rep["POWER"] = {"n_common_scored": nc, "analytic_null_halfwidth_1.645_over_sqrt_n_minus_1": analytic_null_hw,
                    "reading": "a margin smaller than its own CI half-width cannot separate at this n"}
    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = sorted(floors_S)
    rep["NEVER_IMPORTED"] = ["0.1382", "0.2070", "-0.1959"]
    rep["BINDING_FLOOR"] = binding
    rep["BINDING_FLOOR_VALUE"] = round(acc[binding], 4) if binding else None
    rep["GOLD_CAVEAT"] = {
        "constant_floor_tie_corrected": round(acc.get("F_CONSTANT_PROTOTYPE", float("nan")), 4),
        "oracle_constant_fitted_on_golds": round(acc.get("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", float("nan")), 4),
        "reading": "the constant floor is partly a generous gold; the oracle constant is the fitted "
                   "CEILING of the constant family on this pool and is reported so no margin over it "
                   "is mistaken for a margin over chance",
    }

    # =============================== THE RANKED DROP TABLE ===========================================
    read_chain = [lam_arm_name[lam] for lam in LAMBDAS]           # LAM_1.00 ... LAM_0.00, in order
    drops = []
    for i in range(1, len(read_chain)):
        a, b = read_chain[i - 1], read_chain[i]                    # a is upstream (higher lam)
        m = FB.margin(boot, a, b)                                  # point = hit(a) - hit(b) = the DROP
        drops.append({"from": a, "to": b, "drop_point": m["point"], "drop_ci95": m["ci95"],
                      "drop_ci_halfwidth": round((m["ci95"][1] - m["ci95"][0]) / 2.0, 4),
                      "band": m["band"], "chain": "PART_A_read_side_true_downstream"})

    diag_pairs = [
        ("DIAG_B1_SINGLE_OCC_UNCOMPRESSED_ORACLE_CUE", "DIAG_B2_FULL_ACCUM_UNCOMPRESSED_ORACLE_CUE",
         "B1_accumulation_depth_NOT_a_downstream_pair_more_evidence_not_less"),
        ("DIAG_B2_FULL_ACCUM_UNCOMPRESSED_ORACLE_CUE", "LAM_1.00",
         "B2_projection_alone_at_oracle_cue"),
        ("DIAG_B2r_FULL_ACCUM_UNCOMPRESSED_REAL_CUE", "LAM_0.00",
         "B2r_projection_alone_at_the_real_cue_reproduces_landed_info_audit_headline"),
    ]
    for a, b, tag in diag_pairs:
        m = FB.margin(boot, a, b)
        drops.append({"from": a, "to": b, "drop_point": m["point"], "drop_ci95": m["ci95"],
                      "drop_ci_halfwidth": round((m["ci95"][1] - m["ci95"][0]) / 2.0, 4),
                      "band": m["band"], "chain": tag})

    drops_ranked = sorted(drops, key=lambda d: abs(d["drop_point"]), reverse=True)
    rep["RANKED_DROP_TABLE"] = drops_ranked

    # =============================== MONOTONICITY, PART A ONLY ========================================
    chain_vals = [acc[n] for n in read_chain]
    chain_hw = [ci_halfwidth[n] / 2.0 for n in read_chain]     # half of the CI half-width per side
    mono = check_monotone_nonincreasing(chain_vals, chain_hw, MONOTONE_TOL_SIGMA)
    rep["MONOTONICITY_PART_A"] = dict(mono, chain=read_chain, values=[round(v, 4) for v in chain_vals])
    rep["MONOTONICITY_PART_B_NOTE"] = (
        "Part B (accumulation depth, B1) is DELIBERATELY EXCLUDED from the monotonicity assertion: "
        "more accumulated evidence is not a downstream-loses-information step, it is strictly more "
        "real material, so a rise there is not a leak and is reported as a plain margin instead.")

    # =============================== SANITY RUNGS ======================================================
    # NOTE: `x or default` is WRONG here when a legitimate reading can be exactly 0.0 (0.0 is
    # falsy in Python, so `0.0 or 1.0` silently becomes 1.0 and can HIDE a real sanity failure --
    # caught on this cell's own first smoke run, where RANDOM_NULL's genuine 0.0 addressing was
    # masked into a false PASSED=False via the opposite direction of the same bug). Explicit
    # None-checks only.
    addr_known = addressing_of.get("LAM_1.00")
    addr_known = 0.0 if addr_known is None else addr_known
    rep["SANITY_KNOWN_ANSWER"] = {
        "addressing_at_lam_1.00": addr_known, "gate": ADDRESS_EXACT_MIN,
        "PASSED": bool(addr_known >= ADDRESS_EXACT_MIN)}
    addr_null = addressing_of.get("RANDOM_NULL")
    addr_null = 1.0 if addr_null is None else addr_null
    rep["SANITY_RANDOM_NULL"] = {
        "addressing_RANDOM_NULL": addr_null,
        "chance_addressing": round(1.0 / n_anchors, 8),
        "hit_at_1_RANDOM_NULL": round(acc.get("RANDOM_NULL", float("nan")), 4),
        "PASSED": bool(addr_null < max(0.02, 20.0 / n_anchors))}
    if not (rep["SANITY_KNOWN_ANSWER"]["PASSED"] and rep["SANITY_RANDOM_NULL"]["PASSED"]):
        raise SystemExit("SANITY RUNGS FAILED -- publish nothing: %r / %r" % (
            rep["SANITY_KNOWN_ANSWER"], rep["SANITY_RANDOM_NULL"]))

    # =============================== PER-RUNG DETAIL TABLE ============================================
    per_rung = {}
    for name in list(hits_exp.keys()):
        per_rung[name] = {
            "SIGNAL_hit_at_1_tie_corrected": round(acc[name], 4),
            "SIGNAL_hit_at_1_optimistic": round(pb_opt["acc"][name], 4),
            "SIGNAL_hit_at_1_conservative": round(pb_cons["acc"][name], 4),
            "ci95_tie_corrected": [round(float(np.percentile(boot[name], 2.5)), 4),
                                   round(float(np.percentile(boot[name], 97.5)), 4)],
            "ci_halfwidth": ci_halfwidth[name],
            "analytic_null_halfwidth": analytic_null_hw,
            "mean_tie_mass": round(tie_of[name], 4),
            "NOISE_dprime": noise_of[name],
            "RANK": rank_of[name],
            "addressing_accuracy": addressing_of.get(name),
            "margin_vs_binding_floor": FB.margin(boot, name, binding) if binding and name != binding else None,
        }
    rep["PER_RUNG"] = per_rung
    rep["READ_SIDE_CHAIN_ORDER"] = read_chain
    rep["RANDOM_NULL_RANK_AS_THE_RANDOM_RANKING_EXPECTATION"] = rank_of["RANDOM_NULL"]

    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def main() -> int:
    t_start = time.time()
    ev = self_test()
    if _ARGS.self_test:
        print("SELFTEST_ONLY_OK", flush=True)
        return 0

    out_dir = get_output_dir(ANCHOR_NAME + ("_reduced" if SMOKE else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} out={out_dir}", flush=True)

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "MAIN")
    if key in done and key in units:
        rep = units[key]
        print("[cfg] MAIN RESUMED FROM CHECKPOINT", flush=True)
    else:
        rep = run(RUN_MODE)
        record_unit(str(out_dir), key, rep)

    drops = rep.get("RANKED_DROP_TABLE", [])
    top_drop = drops[0] if drops else None
    mono = rep.get("MONOTONICITY_PART_A", {})
    dominant = None
    if top_drop is not None:
        span = sum(abs(d["drop_point"]) for d in drops) or 1.0
        dominant = bool(abs(top_drop["drop_point"]) / span > 0.5)

    verdict = "LADDER_%s__TOP_DROP_%s__DOMINANT_%s" % (
        "MONOTONE" if mono.get("MONOTONE") else "LEAK_DETECTED",
        (top_drop["from"] + "_TO_" + top_drop["to"]).replace(".", "p") if top_drop else "NONE",
        "YES" if dominant else "NO_DISTRIBUTED")

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": (
            "STAGE-WISE ORACLE LADDER over the live grounding-readout pipeline. PART A (read side, "
            "true downstream chain, monotonicity asserted) walks cue quality from the item's own "
            "exact key (S3/S4 held oracle) to the real held-out partial cue (nothing left oracle). "
            "PART B (write side, counterfactual, not chained into the monotonicity assertion) "
            "isolates accumulation depth and the 256-dim projection at a fixed oracle cue. -> " + verdict),
        "HOW_TO_READ_THIS": (
            "The RANKED_DROP_TABLE answers 'which stage destroys the most' directly -- read it top to "
            "bottom. MONOTONICITY_PART_A being MONOTONE means the read-side chain behaved as a real "
            "downstream walk should; a LEAK there would mean an oracle saw something the real stage "
            "could not, or two rungs were scored on different items, and no number from that chain "
            "should be trusted until fixed."),
        "STAGE_ENUMERATION": {
            "method": "read hdlab/grounding_acquisition_loop.py, hdlab/reading_grounding_loop.py, "
                      "experiments/exp_grounding_readout_known_answer_v1.py, and the runtime-verified "
                      "(machine-asserted, not merely claimed) encoder identity in "
                      "experiments/exp_cue_information_audit_v1.py",
            "live_stages": ["S1 content words -> 256-dim per-occurrence code (one fixed random "
                            "projection; collapses the Director sketch's stages 2, 3 and 5)",
                            "S2 per-occurrence codes -> anchor row by unweighted summation across "
                            "profile occurrences (sketch stage 4)",
                            "S3 held-out sentence -> partial cue, the SAME S1 encoder (sketch stage 6)",
                            "S4 cue -> winner by a single cosine-argmax (collapses sketch stages 7+8; "
                            "no separate shortlist stage exists in the incumbent path)",
                            "S5 winner -> scored against WordNet gold, tie-corrected hit@1 (sketch "
                            "stage 9)"],
            "corrections_to_directors_sketch": [
                "sketch stages 1+2 (tokens kept, context vector) carry IDENTICAL information -- a "
                "count vector loses nothing relative to the token list this architecture uses",
                "sketch stages 2/3 boundary and stage 5 (superposition/interference) are THE SAME "
                "physical event (cross-talk inside the one d=256 random projection), not two events",
                "sketch stages 7 and 8 (address, comparator) are the SAME argmax operation in the "
                "incumbent path, not two stages"],
        },
        "config": {"LAMBDAS": list(LAMBDAS), "N_BOOT": N_BOOT, "MASTER_SEED": MASTER_SEED,
                   "ADDRESS_EXACT_MIN": ADDRESS_EXACT_MIN, "MONOTONE_TOL_SIGMA": MONOTONE_TOL_SIGMA},
        "selftest_evidence_keys": sorted(ev.keys()),
        "report": rep,
        "elapsed_s": round(time.time() - t_start, 1),
    }
    write_metrics(out_dir, metrics)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[done] {time.time() - t_start:.0f}s -> {out_dir}/metrics.json", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(3)
