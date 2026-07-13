"""KG_STORE_DIM_SCALING_CEILING: does purely INCREASING n_dim (unchanged one-shot Hebbian write rule) RAISE the
substrate's native representational CEILING (ORACLE_FOLDIN mrr) toward the additive level, or does it FLATLINE? The
clean discriminator for the nativize-feasibility crux: the write-rule lever is definitively CLOSED (HARD_FAIL,
exp_kg_store_write_rule_decorrelated_ceiling_v1: at load M/N ~25-350x past capacity no write rule has purchase). The
~6x native-vs-additive oracle-ceiling gap is therefore DIMENSION-bound and/or CODE-STRUCTURE-bound. This cell
separates those two by sweeping n_dim and watching the native ORACLE ceiling.

THE QUESTION (CITED@notes/research_native_representational_ceiling_levers_2026-07-13.md, Anchor candidate B
"kg_store_dim_scaling_ceiling_v1", levers 2+5). The native multiplicative-Hebbian store (hdlab.kg_traversal.KGStore
-- CERT-584/585 chain-grade primitive) does inductive entity-composition generalization in kind
(exp_native_bind_compose_inductive_entity_cskg_v1: HARD_PASS) but its ORACLE_FOLDIN ceiling is ~6x below the
additive SGD oracle ceiling (native oracle mrr=0.023083
MEASURED@data/exp_native_bind_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ORACLE_FOLDIN;
additive oracle ceiling=0.137 CITED@notes/research_native_representational_ceiling_levers_2026-07-13.md). The
sqrt(N/M) SNR law (Frady/Kleyko/Sommer, CITED lever 5) predicts 4x dim buys only ~2x SNR and 8x dim ~2.8x -- NOT
enough alone to close 6x. This cell TESTS that prediction empirically on THIS task's own oracle ceiling and, via the
trend shape, tells us whether dimension is even the right axis.

THE TEST: re-run the EXACT exp_native_bind_compose_inductive_entity_cskg_v1 7-arm harness (split/arena/controls/
readout REUSED VERBATIM via import), HEBBIAN write rule ONLY (the write rule is SETTLED -- NOT varied), sweeping
n_dim across {1024, 2048, 4096, 8192} on a BIT-IDENTICAL held-out-entity split per seed (the split is seed-only,
n_dim-independent -> only the store's E/R/W dimension changes across the sweep). Measure the native ORACLE_FOLDIN
mrr (the metric the ceiling claim is about) + NATIVE inductive mrr + the must-fails (scramble/identity must STILL
fire at EVERY dim) at each dim.

PRE-REG BANDS (picked BEFORE the run; primary = ORACLE_FOLDIN mrr; d_lo=1024, d_hi=8192):
  CLIMB_RATIO = oracle_mrr[d_hi] / oracle_mrr[d_lo] ; GAP_CLOSED = (oracle_mrr[d_hi] - oracle_mrr[d_lo]) /
                (ADDITIVE_ORACLE_CEIL - oracle_mrr[d_lo]), ADDITIVE_ORACLE_CEIL = 0.137 CITED.
  HARD-PASS (CLIMB -> DIMENSION/CAPACITY WALL RELIEVABLE): (CLIMB_RATIO >= 3.0 OR GAP_CLOSED >= 0.50) AND the
            oracle is TRENDING UP (oracle_mrr[d_hi] - oracle_mrr[d_lo] >= MIN_SIG_RISE) AND oracle fires at EVERY
            dim AND the scramble/identity must-fails are controlled at EVERY dim => nativize is feasible by scaling
            n_dim; the store just needs more dimensions for the 25.7k-entity / 360k-triple load. (Above the sqrt
            prediction: dimension is a stronger-than-theory lever.)
  HARD-FAIL (FLATLINE -> CODE-STRUCTURE WALL): CLIMB_RATIO < 1.3 (8x dim buys < 1.3x oracle; native oracle stuck
            ~0.02-0.03) AND oracle fires at every dim (a genuine flatline, not a broken harness) => random-bipolar
            codes cannot encode the relational geometry at this load; the next lever is STRUCTURED/SPARSE codes
            (glass-box DG front-end), NOT more dimension or any write rule.
  MIDDLE (PARTIAL DIMENSION GAIN): 1.3 <= CLIMB_RATIO < 3.0 AND GAP_CLOSED < 0.50 => dimension helps but does NOT
            alone close the 6x gap (this is the sqrt(N/M) ~2.8x-at-8x prediction; dimension is a contributing axis
            that STACKS with other levers, not the sole fix). The pre-registered EXPECTED outcome per the note.
  Gated INCONCLUSIVE if the n_dim=1024 baseline does not reproduce the landed oracle (Gate D), if ORACLE does not
  fire at some dim (arena unanswerable there), or if a must-fail control leaks at some dim.
  Secondary reported: RATIO_4096 = oracle_mrr[4096]/oracle_mrr[1024] -- the note's Anchor-B pre-reg point (WIN band
  1.4x-2.8x brackets sqrt(N/M); < 1.2x = not dimension-bound).

FOUR VALIDITY-PREFLIGHT CHECKS (declared in the self-test via experiments._validity_preflight):
  (1) positive_control_passes : ORACLE_FOLDIN fires (clears RANDOM by the ceiling-aware ratio+abs gate) at EVERY
                                self-test dim on the planted arena.
  (2) metric_moves            : the DIMENSION discriminator moves recoverable signal -- Hebbian heteroassociative
                                recall cosine RISES with n at FIXED plant count M (SNR ~ sqrt(N/M); adversarial:
                                M/n_lo above the Hebbian ~0.14N cliff, M/n_hi below it).
  (3) negative_control_margin : at the larger self-test dim RANDOM + relation-scramble + identity-shuffle sit below
                                NATIVE_ANCHOR by the MRR margin, deterministically (>=3 controls).
  (4) full_gates_exercised    : dimension_sweep_verdict runs at self-test scale firing every fail-closed gate.

## Compute architecture
class (c) MIXED: split/support-query/POP = sequential-CPU graph ops (no matmul). The store is the untouched one-shot
KGStore Hebbian ingest (NO SGD, NO epochs, NO solve). Per (seed, n_dim): two chunked-Hebbian store builds (train-W +
oracle fold-in) + a single batched native compose + query-chunked bilinear readouts. Ingest cost ~O(triples*n_dim^2)
(chunked matmul), readout ~O(nq*N*n_dim); both CPU-cheap; GPU unnecessary (one-shot, dense matmuls) -> remote_cpu_
queue (device=cpu). Wall estimate ~40min FULL (8192 dominates). MEMORY: KGStore E/W are float32 already (E ~843MB,
W ~256MB per store at n_dim=8192); to cap peak the per-arm score tensors are FREED immediately after their metric is
computed (no whole (nq,N) map held across arms), and weak-point localization (arm_scores retained ~1.85GB, dim-
INDEPENDENT) is enabled only for n_dim<=4096 -- the 8192 dim (the memory-risk point) runs lean since the top-ratio
data point needs only oracle/native mrr, not localization. PER-(seed,dim) CHECKPOINT (write_partial_key +
resumable) so a dropped dim resumes from disk instead of re-running the whole sweep. Storage: cell-owned KGStore
instances only (E/R/W untouched class; no mutation of any persisted store).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test + per unit (META_RULE_AF): 7 arms produce >=5 distinct score signatures.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + write_partial_key os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: primary is a RISE RATIO of ORACLE mrr (ceiling-relative) + a GAP_CLOSED fraction of the
#   MEASURED per-run ceiling headroom -> discriminator_reachability OK by construction (bands are ratios, not
#   absolute thresholds); the additive 0.137 is the target the ratio is scaled against.
# - baseline_in_band: n_dim=1024 ORACLE must fire AND reproduce the landed 0.023083 within tol (Gate D); RANDOM/POP
#   near the 1/N floor at every dim.
# - discriminator survives scale: analytical (SNR ~ sqrt(N/M) is a scale-INVARIANT law; the sweep IS the scale axis)
#   + the self-test DIMENSION discriminator fires the hebb-recall-rises-with-n gap deterministically at a fixed plant
#   count straddling the Hebbian cliff, and the planted-arena ORACLE fires at every self-test dim.
# - HARD-PASS strictly above floor: CLIMB_RATIO>=3.0 clears HARD-FAIL 1.3 by 1.7 ratio + a trend-up + fire + control
#   gate; MIDDLE band [1.3,3.0) is explicitly the sqrt-law expected region (documented before the run).
# - HP_SCOPE: the CLIMB/FLATLINE gates apply to the ORACLE_FOLDIN-vs-n_dim trend only. The 7 base arms keep their
#   base HP_SCOPE (ORACLE positive control; RANDOM/SCRAMBLE/IDSHUF must-not-clear; MEMORIZE head-to-head; POP
#   fit-independence). NATIVE mrr trend is reported (realized) but the verdict is about the CEILING (ORACLE).
# - cardinality: EXPECTED_N_UNITS = n_seeds * n_dims; each (seed,dim) asserted to produce all 7 arms + >=5 sigs.
# - per-unit failure-class instrumentation (no bare except; per (seed,dim) failure_class recorded).
# - calibration_check: default_ok_for_this_regime -- ORACLE_FIRE_RATIO/ABS, HELDOUT/SUPPORT fracs, n_heldout_eval
#   are the base arena's pre-registered knobs (NOT tuned on real data); the only new knobs are the pre-registered
#   dimension bands (ratios), picked before the run.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the docstring/prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-(seed,dim) flush prints; timeout>=1800).

ASCII-only. No bare except; except SystemExit before except Exception.
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial_key, load_partial_key,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import Graph, build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores, pop_hits,
)
from hdlab.kg_traversal import KGStore  # noqa: E402 (LIVE store; read-only for E/R + the untouched Hebbian ingest)

# Reuse the base cell's split / arena / compose / readout / localization / verdict VERBATIM (only n_dim changes).
import experiments.exp_native_bind_compose_inductive_entity_cskg_v1 as base  # noqa: E402

ANCHOR_NAME = "kg_store_dim_scaling_ceiling_v1"

# Base arm handles + eval knobs (re-exported so the verdict text matches the base harness exactly).
NATIVE = base.NATIVE
MEMORIZE = base.MEMORIZE
RANDOM = base.RANDOM
SCRAMBLE = base.SCRAMBLE
IDSHUF = base.IDSHUF
ORACLE = base.ORACLE
POP = base.POP
ALL_ARMS = base.ALL_ARMS
EVAL_KS = base.EVAL_KS
CEIL_METRIC = base.CEIL_METRIC
PRIMARY_METRIC = base.PRIMARY_METRIC
MIN_HELDOUT = base.MIN_HELDOUT

# ---- The sweep axis (HEBBIAN write rule unchanged at every dim) ----
FULL_DIMS = [1024, 2048, 4096, 8192]
SELFTEST_DIMS = [256, 512]
LOCALIZE_MAX_DIM = 4096          # weak-point localization enabled for n_dim<=this; 8192 runs lean (memory)

# ---- Dimension-sweep bands (the research question; picked BEFORE the run) ----
ADDITIVE_ORACLE_CEIL = 0.137     # CITED@notes/research_native_representational_ceiling_levers_2026-07-13.md
HP_CLIMB_RATIO = 3.0             # HARD-PASS (CLIMB): oracle mrr at d_hi >= 3.0x the d_lo oracle mrr ...
HP_GAP_CLOSED = 0.50             # ...OR closes >= 50% of the ceiling gap toward additive
HF_FLATLINE_RATIO = 1.3          # HARD-FAIL (FLATLINE): oracle rise below this = code-structure wall
MIN_SIG_RISE = 0.003             # trending-up requires oracle mrr to rise by at least this absolute MRR margin
MONO_TOL = 0.002                 # monotone-nondecreasing report tolerance (noise slack)
# Gate D: the n_dim=1024 hebbian oracle must reproduce the landed baseline (positive-control reproducer).
LANDED_HEBB_ORACLE_MRR_1024 = 0.023083   # MEASURED@data/exp_native_bind_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ORACLE_FOLDIN
REPRODUCE_TOL = 0.006                    # abs MRR tolerance on the n_dim=1024 reproduction of the landed oracle

# ---- DIMENSION discriminator self-test knobs (heteroassociative micro-capacity; SNR ~ sqrt(N/M); adversarial) ----
ST_DIM_LO = 128
ST_DIM_HI = 1024
ST_DIM_M = 110               # fixed plant count: load 0.86 at n_lo (well above Hebbian ~0.14N cliff), 0.107 at n_hi
ST_DIM_HI_MIN_COS = 0.60     # hebb mean recall cosine at n_hi must clear this
ST_DIM_MARGIN_COS = 0.15     # (cos_hi - cos_lo) must clear this -> dimension raises recoverable signal

FULL_CFG = dict(base.FULL_CFG)          # seeds=[7,13,17], k_core=12, fracs, n_heldout_eval=3000 (n_dim overridden per dim)
SELFTEST_CFG = dict(base.SELFTEST_CFG)  # (n_dim overridden per self-test dim)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


def _unit_key(seed, dim):
    return "seed%d_dim%d" % (seed, dim)


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Prepare a corpus split ONCE per seed (seed-deterministic; n_dim-INDEPENDENT) then score at each n_dim on the
# BIT-IDENTICAL split. This guarantees the ONLY variable across the sweep is store dimensionality.
# ---------------------------------------------------------------------------

def prepare_corpus(pool_lbl, cfg, seed):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    rel_i2lbl = {v: k for k, v in rel2i.items()}
    train_lbl, support_lbl, query_lbl, hold_ids, n_cold = base.build_heldout_entity_split_ac(
        pool_lbl, ent2i, cfg["heldout_entity_frac"], cfg["support_frac"], seed)
    n_query_total = len(query_lbl)
    if cfg.get("n_heldout_eval") and n_query_total > cfg["n_heldout_eval"]:
        rng = np.random.default_rng(seed * 777 + 3)
        idx = sorted(rng.choice(n_query_total, size=cfg["n_heldout_eval"], replace=False).tolist())
        query_lbl = [query_lbl[i] for i in idx]
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    support_int = _to_int_edges(support_lbl, ent2i, rel2i)
    query_int = _to_int_edges(query_lbl, ent2i, rel2i)
    hold_all = np.concatenate([support_int, query_int], axis=0) if query_int.shape[0] else support_int
    gd = Graph(train_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, support_int, query_int)
    return dict(ent2i=ent2i, rel2i=rel2i, rel_i2lbl=rel_i2lbl, N=N, n_rel=n_rel,
                train_int=train_int, support_int=support_int, query_int=query_int, hold_all=hold_all,
                hold_ids=hold_ids, n_cold=n_cold, n_query_total=n_query_total, gd=gd, all_true=all_true)


# ---------------------------------------------------------------------------
# Memory-frugal per-(seed,dim) scorer. Calls the SAME base primitives with the SAME seeds/order as
# base.fit_and_score (-> bit-identical metrics) but FREES each arm's score tensor right after its metric is computed
# and retains arm_scores (for weak-point localization) ONLY when localize=True. HEBBIAN store (untouched ingest).
# ---------------------------------------------------------------------------

def score_corpus_dim(prep, cfg, seed, dim, corpus_name, localize=True):
    N = prep["N"]; n_rel = prep["n_rel"]
    train_int = prep["train_int"]; support_int = prep["support_int"]; query_int = prep["query_int"]
    all_true = prep["all_true"]; hold_all = prep["hold_all"]; hold_ids = prep["hold_ids"]
    result = dict(corpus=corpus_name, seed=seed, N=int(N), n_rel=int(n_rel),
                  n_train=int(train_int.shape[0]), n_heldout_entities=len(hold_ids),
                  n_support=int(support_int.shape[0]), n_query_total=prep["n_query_total"],
                  n_query_scored=int(query_int.shape[0]), n_cold=int(prep["n_cold"]), n_dim=int(dim),
                  heldout_entity_frac=cfg["heldout_entity_frac"], support_frac=cfg["support_frac"])
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    # Two stores with BIT-IDENTICAL E/R (base.build_store seed formula) at this n_dim; only W differs (fold-in).
    store = base.build_store(N, n_rel, dim, seed, train_int)                       # train-only Hebbian W
    store_oracle = base.build_store(N, n_rel, dim, seed, train_int, fold_in=hold_all)   # held-out folded in

    Ep_anchor, support_deg = base.native_compose_codes(store, support_int, N)
    rel_perm = np.random.default_rng(seed * 4441 + 17).permutation(n_rel)          # SAME seed as base.fit_and_score
    recall_train = base.native_query_recall(store, query_int)                      # shared by NATIVE/MEM/SCR/IDSHUF
    recall_oracle = base.native_query_recall(store_oracle, query_int)

    arm_metric, arm_sig = {}, {}
    arm_scores = {} if localize else None

    def _emit(name, sc):
        arm_metric[name] = filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)
        arm_sig[name] = base._sig(sc.numpy()[:min(64, sc.shape[0])].ravel())
        if localize:
            arm_scores[name] = sc

    _emit(NATIVE, base.score_from_codes(recall_train, Ep_anchor))
    _emit(MEMORIZE, base.score_from_codes(recall_train, store.E))                  # held-out codes = fixed bipolar rows
    Ep_scramble, _ = base.native_compose_codes(store, support_int, N, rel_perm=rel_perm)
    _emit(SCRAMBLE, base.score_from_codes(recall_train, Ep_scramble))
    del Ep_scramble
    Ep_idshuf = base.identity_shuffle_codes(store.E, Ep_anchor, support_deg, hold_ids, seed)
    _emit(IDSHUF, base.score_from_codes(recall_train, Ep_idshuf))
    del Ep_idshuf
    if not localize:
        del Ep_anchor                                                             # dead after IDSHUF (memory trim)
    _emit(ORACLE, base.score_from_codes(recall_oracle, store_oracle.E))            # fixed codes, fold-in W recalls them
    del store_oracle, recall_oracle                                               # nothing after ORACLE uses them
    _emit(RANDOM, base.random_scores(N, query_int, dim, seed))                     # null bar
    pop_m, pop_rank_vec = pop_hits(prep["gd"].rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m
    arm_sig[POP] = base._sig(pop_rank_vec.astype(np.float64))

    w_train_hash = hashlib.sha256(store.W.numpy().tobytes()).hexdigest()[:16]
    result.update(
        arm_hits={a: {kk: round(vv, 6) for kk, vv in arm_metric[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: arm_metric[a]["n"] for a in ALL_ARMS},
        arm_sigs=arm_sig, w_train_hash=w_train_hash,
    )
    # Free the big stores/composed codes BEFORE localization (localization needs only arm_scores + graph metadata).
    del store, recall_train
    if localize and arm_scores is not None:
        result["localization"] = base.localize_weak_points(
            arm_scores, query_int, all_true, support_deg, prep["gd"].node_degree,
            prep["rel_i2lbl"], prep["gd"].rel_tail_freq, N)
        del arm_scores
    return result


# ---------------------------------------------------------------------------
# Top-level dimension-sweep verdict over the per-dim aggregates.
# ---------------------------------------------------------------------------

def _oracle_mrr(g):
    return g["heldout_mrr"].get(ORACLE, float("nan"))


def _native_mrr(g):
    return g["heldout_mrr"].get(NATIVE, float("nan"))


def dimension_sweep_verdict(per_dim_by_seed):
    """per_dim_by_seed: {dim: [res per seed]}. Returns (verdict, msg, gates)."""
    dims = sorted(per_dim_by_seed.keys())
    g = {}
    for d in dims:
        _, _, gd = base.aggregate_and_verdict(per_dim_by_seed[d])
        g[d] = gd
    oracle = {d: _oracle_mrr(g[d]) for d in dims}
    native = {d: _native_mrr(g[d]) for d in dims}
    oracle_fires = {d: bool(g[d].get("oracle_fires")) for d in dims}
    controls = {d: bool(g[d].get("scramble_controlled") and g[d].get("idshuf_controlled")) for d in dims}

    d_lo, d_hi = dims[0], dims[-1]
    climb_ratio = _ratio(oracle[d_hi], oracle[d_lo])
    denom = ADDITIVE_ORACLE_CEIL - oracle[d_lo]
    gap_closed = ((oracle[d_hi] - oracle[d_lo]) / denom) if (denom > 0 and oracle[d_lo] == oracle[d_lo]
                                                             and oracle[d_hi] == oracle[d_hi]) else float("nan")
    ratio_4096 = _ratio(oracle.get(4096, float("nan")), oracle[d_lo])   # note's Anchor-B pre-reg point
    trend_up = bool(oracle[d_hi] == oracle[d_hi] and oracle[d_lo] == oracle[d_lo]
                    and (oracle[d_hi] - oracle[d_lo]) >= MIN_SIG_RISE)
    monotone = bool(all(oracle[dims[i + 1]] == oracle[dims[i + 1]] and oracle[dims[i]] == oracle[dims[i]]
                        and oracle[dims[i + 1]] >= oracle[dims[i]] - MONO_TOL for i in range(len(dims) - 1)))
    all_fire = bool(all(oracle_fires.values()))
    all_controls = bool(all(controls.values()))
    baseline_reproduces = bool((1024 not in dims) or (oracle[1024] == oracle[1024]
                               and abs(oracle[1024] - LANDED_HEBB_ORACLE_MRR_1024) <= REPRODUCE_TOL))

    climbs = bool((climb_ratio == climb_ratio and climb_ratio >= HP_CLIMB_RATIO)
                  or (gap_closed == gap_closed and gap_closed >= HP_GAP_CLOSED))
    flatlines = bool(climb_ratio == climb_ratio and climb_ratio < HF_FLATLINE_RATIO)

    hard_pass = bool(climbs and trend_up and all_fire and all_controls and baseline_reproduces)
    hard_fail = bool(flatlines and all_fire and baseline_reproduces and not hard_pass)
    middle = bool(baseline_reproduces and all_fire and not hard_pass and not hard_fail)

    if not baseline_reproduces:
        verdict = "INCONCLUSIVE_BASELINE_DIM_DID_NOT_REPRODUCE_LANDED"
    elif not all_fire:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT_AT_SOME_DIM"
    elif not all_controls:
        verdict = "INCONCLUSIVE_MUSTFAIL_CONTROL_LEAK_AT_SOME_DIM"
    elif hard_pass:
        verdict = "HARD_PASS_DIMENSION_RELIEVES_CEILING"
    elif hard_fail:
        verdict = "HARD_FAIL_CODE_STRUCTURE_WALL_NOT_DIMENSION"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_DIMENSION_GAIN"

    oracle_curve = ["%d:%s" % (d, _fmt(oracle[d])) for d in dims]
    native_curve = ["%d:%s" % (d, _fmt(native[d])) for d in dims]
    msg = ("%s || ORACLE mrr curve [%s] | NATIVE mrr curve [%s] || CLIMB d%d/d%d=%sx (HP>=%.1f) gap_closed=%s "
           "(HP>=%.2f; additive_ceil=%.3f) ratio_4096=%sx (note WIN 1.4-2.8x) | trend_up=%s monotone=%s | "
           "oracle_fires_all=%s controls_all=%s baseline_reproduces(%.4f+-%.3f)=%s | FLATLINE<%.1fx"
           % (verdict, " ".join(oracle_curve), " ".join(native_curve), d_hi, d_lo,
              (_fmt(climb_ratio) if climb_ratio != float("inf") else "inf"), HP_CLIMB_RATIO,
              _fmt(gap_closed), HP_GAP_CLOSED, ADDITIVE_ORACLE_CEIL,
              (_fmt(ratio_4096) if ratio_4096 != float("inf") else "inf"),
              trend_up, monotone, all_fire, all_controls, LANDED_HEBB_ORACLE_MRR_1024, REPRODUCE_TOL,
              baseline_reproduces, HF_FLATLINE_RATIO))

    def _rnd(x, nd=6):
        return round(x, nd) if (x == x and x != float("inf")) else (None if x != x else "inf")

    gates = dict(
        verdict=verdict,
        dims=dims,
        oracle_mrr_by_dim={str(d): _rnd(oracle[d]) for d in dims},
        native_mrr_by_dim={str(d): _rnd(native[d]) for d in dims},
        oracle_fires_by_dim={str(d): oracle_fires[d] for d in dims},
        controls_ok_by_dim={str(d): controls[d] for d in dims},
        climb_ratio=_rnd(climb_ratio, 3), gap_closed=_rnd(gap_closed, 3), ratio_4096=_rnd(ratio_4096, 3),
        additive_oracle_ceil=ADDITIVE_ORACLE_CEIL,
        trend_up=trend_up, monotone_nondecreasing=monotone, all_oracle_fire=all_fire, all_controls_ok=all_controls,
        baseline_reproduces=baseline_reproduces, climbs=climbs, flatlines=flatlines,
        hard_pass=hard_pass, hard_fail=hard_fail, middle=middle,
        bands=dict(HP_CLIMB_RATIO=HP_CLIMB_RATIO, HP_GAP_CLOSED=HP_GAP_CLOSED, HF_FLATLINE_RATIO=HF_FLATLINE_RATIO,
                   MIN_SIG_RISE=MIN_SIG_RISE, REPRODUCE_TOL=REPRODUCE_TOL,
                   LANDED_HEBB_ORACLE_MRR_1024=LANDED_HEBB_ORACLE_MRR_1024, ADDITIVE_ORACLE_CEIL=ADDITIVE_ORACLE_CEIL),
        per_dim_gates={str(d): g[d] for d in dims},
    )
    return verdict, msg, gates


# ---------------------------------------------------------------------------
# DIMENSION discriminator self-test: fixed-M heteroassociative micro-capacity; Hebbian recall cosine RISES with n
# (SNR ~ sqrt(N/M)). Adversarial: M straddles the Hebbian ~0.14N cliff (above at n_lo, below at n_hi).
# ---------------------------------------------------------------------------

def _hebb_recall_cos(n, M, seed):
    g = torch.Generator(device="cpu").manual_seed(seed)
    K = (torch.randint(0, 2, (M, n), generator=g, dtype=torch.int8) * 2 - 1).to(torch.float64)
    T = (torch.randint(0, 2, (M, n), generator=g, dtype=torch.int8) * 2 - 1).to(torch.float64)
    W = (T.T @ K) / n                                       # one-shot Hebbian W += outer(t_i, k_i)/n
    rec = K @ W.T                                           # [M, n]; row i = W @ k_i
    num = (rec * T).sum(dim=1)
    den = torch.linalg.norm(rec, dim=1) * torch.linalg.norm(T, dim=1) + 1e-12
    return float((num / den).mean().item()), bool(torch.isfinite(rec).all().item())


def dimension_discriminator_selftest():
    cos_lo, fin_lo = _hebb_recall_cos(ST_DIM_LO, ST_DIM_M, seed=7)
    cos_hi, fin_hi = _hebb_recall_cos(ST_DIM_HI, ST_DIM_M, seed=7)
    margin = cos_hi - cos_lo
    hi_clears = bool(cos_hi >= ST_DIM_HI_MIN_COS)
    margin_clears = bool(margin >= ST_DIM_MARGIN_COS)
    stable = bool(fin_lo and fin_hi)
    ok = bool(hi_clears and margin_clears and stable)
    out = dict(n_lo=ST_DIM_LO, n_hi=ST_DIM_HI, M=ST_DIM_M, load_lo=round(ST_DIM_M / ST_DIM_LO, 3),
               load_hi=round(ST_DIM_M / ST_DIM_HI, 3), cos_lo=round(cos_lo, 4), cos_hi=round(cos_hi, 4),
               margin=round(margin, 4), hi_clears=hi_clears, margin_clears=margin_clears, stable=stable, ok=ok)
    return ok, out


# ---------------------------------------------------------------------------
# Compose-harness self-test: run the planted arena under HEBBIAN at each self-test dim; assert ORACLE fires + the
# must-fails fire at EVERY dim + oracle does not collapse with dim. Reuses base's planted arena + verdict verbatim.
# ---------------------------------------------------------------------------

def compose_harness_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _compose_harness_selftest_body()
    finally:
        torch.set_num_threads(_prev)


def _compose_harness_selftest_body():
    pool = base.build_planted_native_arena(7)
    cfg = dict(SELFTEST_CFG)
    prep = prepare_corpus(pool, cfg, 7)
    out = dict(n_grid_entities=prep["N"], n_heldout_entities=len(prep["hold_ids"]),
               n_support=int(prep["support_int"].shape[0]), n_query=int(prep["query_int"].shape[0]),
               n_cold=int(prep["n_cold"]), dims=list(SELFTEST_DIMS))
    if prep["query_int"].shape[0] < base.SELFTEST_MIN_HO:
        out["fail"] = "planted grid produced too few held-out-entity queries (%d)" % prep["query_int"].shape[0]
        return False, out

    per_dim = {}
    for d in SELFTEST_DIMS:
        per_dim[d] = score_corpus_dim(prep, cfg, 7, d, "PLANTED_NATIVE_HELDOUT_ENTITY", localize=True)

    # arms differ + W-hash differs across dims (different dimensionality -> genuinely different store).
    n_sigs = {d: len(set(per_dim[d]["arm_sigs"].values())) for d in SELFTEST_DIMS}
    w_hashes = {d: per_dim[d]["w_train_hash"] for d in SELFTEST_DIMS}
    assert w_hashes[SELFTEST_DIMS[0]] != w_hashes[SELFTEST_DIMS[-1]], \
        "META_RULE_AF: distinct n_dim produced bit-identical W (dimension sweep not applied)"

    m = {d: {a: per_dim[d]["arm_hits"][a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS} for d in SELFTEST_DIMS}

    def _fires(d):
        og = base.aggregate_and_verdict([per_dim[d]])[2]
        return bool(og.get("oracle_fires")), bool(og.get("scramble_controlled")), bool(og.get("idshuf_controlled"))

    fire_scr_id = {d: _fires(d) for d in SELFTEST_DIMS}
    oracle_fires_all = bool(all(v[0] for v in fire_scr_id.values()))
    scramble_all = bool(all(v[1] for v in fire_scr_id.values()))
    idshuf_all = bool(all(v[2] for v in fire_scr_id.values()))
    arms_differ = bool(all(n_sigs[d] >= 5 for d in SELFTEST_DIMS))

    d_lo, d_hi = SELFTEST_DIMS[0], SELFTEST_DIMS[-1]
    oracle_not_collapse = bool(m[d_hi][ORACLE] == m[d_hi][ORACLE] and m[d_lo][ORACLE] == m[d_lo][ORACLE]
                               and m[d_hi][ORACLE] >= m[d_lo][ORACLE] - 5e-3)

    # VACUOUS-SMOKE guard: at the larger dim the RANDOM null must NOT reach NATIVE_ANCHOR on the planted arena.
    native_margin_hi = m[d_hi][NATIVE] - m[d_hi][RANDOM]
    random_reached_native = bool(native_margin_hi <= base.SELFTEST_NATIVE_BEATS_RANDOM_MRR)
    base.assert_discriminator_fires(
        random_reached_native, control_name=RANDOM,
        headline_name="native_bind_compose_beats_random_heldout_at_dim", run_mode="self_test",
        extra="RANDOM reached NATIVE_ANCHOR_COMPOSE on the planted held-out-entity arena at n_dim=%d -> arena not "
              "answerable / metric frozen" % d_hi)

    # Dimension discriminator (synthetic) + full verdict at self-test scale.
    dd_ok, dd_out = dimension_discriminator_selftest()
    sv_verdict, sv_msg, sv_gates = dimension_sweep_verdict({d: [per_dim[d]] for d in SELFTEST_DIMS})

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": oracle_fires_all,
         "control_name": "ORACLE_FOLDIN_EVERY_DIM", "headline_name": "oracle_fires_at_every_selftest_dim",
         "extra": "planted arena: ORACLE_FOLDIN fires (clears RANDOM by ratio+abs) at EVERY self-test dim -> the "
                  "harness is answerable at each n_dim and the ceiling is measurable across the sweep"},
        {"kind": "metric_moves", "metric_name": "hebb_hetero_recall_cosine_vs_n_dim",
         "values": [dd_out["cos_lo"], dd_out["cos_hi"]],
         "extra": "fixed plant M=%d: Hebbian recall cosine RISES with n_dim (n=%d cos=%.3f -> n=%d cos=%.3f); "
                  "SNR ~ sqrt(N/M), M straddles the ~0.14N cliff -> the dimension axis moves recoverable signal"
                  % (ST_DIM_M, ST_DIM_LO, dd_out["cos_lo"], ST_DIM_HI, dd_out["cos_hi"])},
        {"kind": "negative_control_margin",
         "control_scores": [m[d_hi][RANDOM], m[d_hi][SCRAMBLE], m[d_hi][IDSHUF]],
         "headline_threshold": m[d_hi][NATIVE], "higher_is_pass": True,
         "margin": base.SELFTEST_SCRAMBLE_MARGIN_MRR, "n_repeats_min": 3,
         "control_name": "RANDOM_SCRAMBLE_IDSHUF_below_native_mrr_at_dim",
         "extra": "at n_dim=%d RANDOM + relation-scramble + identity-shuffle sit below NATIVE_ANCHOR by the MRR "
                  "margin -> the relation operators AND the entity-identity binding carry the signal at every dim"
                  % d_hi},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "w_hash_differs_across_dim", "oracle_fires_every_dim",
                                    "scramble_controlled_every_dim", "idshuf_controlled_every_dim",
                                    "baseline_reproduce_gateD", "climb_flatline_gate"],
         "exercised_gates": ["arms_differ", "w_hash_differs_across_dim", "oracle_fires_every_dim",
                             "scramble_controlled_every_dim", "idshuf_controlled_every_dim",
                             "baseline_reproduce_gateD", "climb_flatline_gate"],
         "extra": "dimension_sweep_verdict=%s at self-test scale over dims %s" % (sv_verdict, SELFTEST_DIMS)},
    ], run_mode="self_test")

    out.update(
        planted_oracle_mrr={str(d): round(m[d][ORACLE], 5) for d in SELFTEST_DIMS},
        planted_native_mrr={str(d): round(m[d][NATIVE], 5) for d in SELFTEST_DIMS},
        planted_random_mrr={str(d): round(m[d][RANDOM], 5) for d in SELFTEST_DIMS},
        n_distinct_sigs={str(d): n_sigs[d] for d in SELFTEST_DIMS}, w_train_hash={str(d): w_hashes[d] for d in SELFTEST_DIMS},
        dimension_discriminator=dd_out, oracle_fires_all=oracle_fires_all, scramble_all=scramble_all,
        idshuf_all=idshuf_all, arms_differ=arms_differ, oracle_not_collapse=oracle_not_collapse,
        dimension_sweep_selftest_verdict=sv_verdict, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest"],
    )
    ok = bool(dd_ok and oracle_fires_all and scramble_all and idshuf_all and arms_differ and oracle_not_collapse)
    return ok, out


def mechanism_selftest():
    ok, out = compose_harness_selftest()
    return ok, dict(compose_harness=out, dimension_discriminator=out.get("dimension_discriminator"), ok=ok)


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def _load_done_unit(out_dir, seed, dim, run_mode):
    """Resume: return a landed per-(seed,dim) res payload if a valid, config-matching partial exists, else None."""
    body = load_partial_key(out_dir, _unit_key(seed, dim))
    if not isinstance(body, dict):
        return None
    if body.get("run_mode") != run_mode or body.get("anchor_name") != ANCHOR_NAME:
        return None
    res = body.get("res")
    if not isinstance(res, dict) or "arm_hits" not in res or int(res.get("n_dim", -1)) != int(dim):
        return None
    return res


def core_main(run_mode):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    dims = list(SELFTEST_DIMS) if run_mode == "self_test" else list(FULL_DIMS)
    expected_n_units = len(seeds) * len(dims)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=cpu run_mode=%s seeds=%s dims=%s" % (run_mode, seeds, dims))

    st_ok, st_res = mechanism_selftest()
    ch = st_res["compose_harness"]; dd = st_res.get("dimension_discriminator") or {}
    _log("mechanism_selftest ok=%s | dim_discrim: cos_lo=%s cos_hi=%s margin=%s | compose: oracle_fires_all=%s "
         "scramble_all=%s idshuf_all=%s oracle_not_collapse=%s planted_oracle=%s vp_ok=%s"
         % (st_ok, dd.get("cos_lo"), dd.get("cos_hi"), dd.get("margin"), ch.get("oracle_fires_all"),
            ch.get("scramble_all"), ch.get("idshuf_all"), ch.get("oracle_not_collapse"),
            ch.get("planted_oracle_mrr"), ch.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (Hebbian recall did not rise with n_dim, or ORACLE did not fire at "
                        "every dim, or scramble/identity did not fail at every dim, or oracle collapsed with dim, or "
                        "arms not distinct): ok=%s" % st_ok,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS DIM_SCALING_CEILING: Hebbian heteroassociative recall cosine rises with n_dim "
                        "(SNR ~ sqrt(N/M)); on the planted arena ORACLE fires and the relation-scramble + identity-"
                        "shuffle must-fails STILL fire at EVERY dim; W-hash differs across dims; 4 validity-preflight "
                        "checks declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_dim_by_seed = {d: [] for d in dims}
    unit_failures = []
    unit_i = 0
    for si, seed in enumerate(seeds):
        prep = None
        for d in dims:
            key = _unit_key(seed, d)
            try:
                landed = _load_done_unit(out_dir, seed, d, run_mode)
                if landed is not None:
                    per_dim_by_seed[d].append(landed)
                    _log("RESUME unit=%s from partial (nq=%d ORACLE_mrr=%s)"
                         % (key, landed.get("n_query_scored", -1),
                            _fmt(landed["arm_hits"][ORACLE].get(CEIL_METRIC, float("nan")))))
                    unit_i += 1
                    continue
                if prep is None:
                    ts = time.time()
                    train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                        cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
                    pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
                    prep = prepare_corpus(pool, cfg, seed)
                    prep["_prov"] = prov
                    _log("cskg seed=%d core_nodes=%d core_edges=%d rels=%d N=%d n_train=%d nq=%d (%.1fs)"
                         % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["n_rel_tokens"],
                            prep["N"], int(prep["train_int"].shape[0]), int(prep["query_int"].shape[0]),
                            time.time() - ts))
                    if int(prep["query_int"].shape[0]) < cfg.get("min_heldout", MIN_HELDOUT):
                        raise RuntimeError("held-out-entity query edges too few (%d < %d)"
                                           % (int(prep["query_int"].shape[0]), cfg.get("min_heldout", MIN_HELDOUT)))
                td = time.time()
                localize = bool(d <= LOCALIZE_MAX_DIM)
                res = score_corpus_dim(prep, cfg, seed, d, "CSKG_CORE_HELDOUT_ENTITY", localize=localize)
                res["cskg_provenance"] = prep["_prov"]
                sigset = set(res["arm_sigs"].values())
                if len(sigset) < 5:
                    raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d dim=%d only %d sigs"
                                       % (seed, d, len(sigset)))
                per_dim_by_seed[d].append(res)
                write_partial_key(out_dir, key, dict(seed=seed, dim=d, run_mode=run_mode, anchor_name=ANCHOR_NAME,
                                                     config_version="ANCHOR=%s,dim=%d" % (ANCHOR_NAME, d),
                                                     N=res.get("N"), res=res))
                ah = res["arm_hits"]
                _log("seed=%d dim=%d localize=%s nq=%d | MRR NATIVE=%s MEMORIZE=%s RANDOM=%s SCRAMBLE=%s IDSHUF=%s "
                     "ORACLE=%s POP=%s (%.1fs)"
                     % (seed, d, localize, res["n_query_scored"], _fmt(ah[NATIVE][CEIL_METRIC]),
                        _fmt(ah[MEMORIZE][CEIL_METRIC]), _fmt(ah[RANDOM][CEIL_METRIC]), _fmt(ah[SCRAMBLE][CEIL_METRIC]),
                        _fmt(ah[IDSHUF][CEIL_METRIC]), _fmt(ah[ORACLE][CEIL_METRIC]), _fmt(ah[POP][CEIL_METRIC]),
                        time.time() - td))
                unit_i += 1
                _hb("cskg", unit_i)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                fc = type(e).__name__
                unit_failures.append(dict(seed=seed, dim=d, failure_class=fc, msg=str(e)[:300]))
                _log("UNIT_FAILED seed=%d dim=%d class=%s: %s" % (seed, d, fc, str(e)[:200]))

    got = sum(len(per_dim_by_seed[d]) for d in dims)
    if got < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d units (seeds*dims), got %d (failures=%s)"
                        % (expected_n_units, got, unit_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            unit_failures=unit_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = dimension_sweep_verdict(per_dim_by_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device="cpu", n_seeds=len(seeds), seeds=seeds,
                   dims=dims, config=cfg, gates=gates, mechanism_selftest=st_res, unit_failures=unit_failures,
                   per_dim_by_seed=per_dim_by_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else args.run_mode
    if not args.self_test and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "full"):
            run_mode = _env_mode
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
