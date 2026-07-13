"""PER-RELATION INFO-CEILING REFRAME of the additive inductive map-builder (magnitude VET lever #1).

STRATEGIC FRAME (magnitude 2x2 VET, MEASURED off-disk): composer/scorer levers are SATURATED -- the best arm
ANCHOR_PEEL_HARDNEG lands aggregate held-out-entity filtered-MRR 0.13787
(MEASURED@data/exp_anchor_compose_magnitude_opt_cskg_v1/metrics.json:gates.heldout_mrr.ANCHOR_PEEL_HARDNEG) which
is ~97.4% of its OWN hardneg oracle 0.14164 (MEASURED@...:gates.oracle_hardneg.mrr) -- oracle headroom ~0, so
capacity (dim/codes) is NOT the lever. The 0.14 AGGREGATE is a RELATION-MIXTURE INFO-CEILING artifact: the aggregate
mixes WINNABLE (near-functional, determined) relations with mathematically-UNWINNABLE (one-to-many) relations whose
filtered-MRR-vs-all is capped EVEN AT THE ORACLE because a single additive code z[h]+w[r] points at the CENTROID of
many valid tails (foreign non-true entities sit between the centroid and the specific held-out tail -> capped rank).

THIS CELL re-runs the CONFIRMED best-arm pipeline (identical split/fits/controls) and adds a PER-RELATION breakdown:
  (1) classify each relation by CARDINALITY = mean number of valid tails per (head, relation) pair (tph), computed
      from the filtered all_true set. tph is EXACTLY the filtered-set size = the quantity that caps filtered-MRR:
      tph~1 => near-functional => the additive centroid IS the tail (winnable); tph high => centroid far from any
      specific tail (unwinnable even at oracle). Determined := tph <= CARD_THRESH; underdetermined := tph > CARD_THRESH.
  (2) per relation report: our best-arm (ANCHOR_PEEL_HARDNEG) filtered-MRR, the ORACLE filtered-MRR (= the empirical
      info-ceiling for that relation), and fraction-of-ceiling = best / oracle.
  (3) pooled DETERMINED subset: where do we sit vs commonsense-SOTA 0.18-0.22, and what query-fraction lives there;
      vs pooled UNDERDETERMINED subset: oracle-capped, quantify how much of the aggregate gap-to-SOTA is unwinnable mass.
  (4) GUARD FIX the VET filed: the source run verdict was BROKEN_TEST_CONTROL_BEATS_POP -- a FALSE break, because
      BASELINE_POP is STRUCTURALLY ~0 on held-out entities (train-frequency 0), so ANY control trivially "beats POP".
      This cell ports the self-test pop_at_floor semantics to the FULL verdict: controls are governed vs the RANDOM
      arm-floor (scramble_controlled / peelscr_controlled / idshuf_collapses already do this); POP is a floor SANITY
      (pop_at_floor: POP must be AT-OR-BELOW the RANDOM floor, else frequency is leaking) NOT a bar controls must clear.
      The old POP-based broken test is REPORTED (old_broken_via_pop) for transparency but does NOT gate.

PRE-REGISTERED "we are already best-in-class on the DETERMINED subset" (ALL required; HYPOTHESIZED unless MEASURED@):
  - determined-subset best-arm pooled filtered-MRR IN/NEAR the SOTA band: PEELHN_det >= DET_SOTA_NEAR (0.17).
  - the determined subset is a MATERIAL fraction of held-out queries: det_query_frac >= DET_FRAC_MIN (0.20).
  - high oracle-fraction on determined (we are near the winnable ceiling): PEELHN_det / ORACLEHN_det >= DET_CEIL_FRAC_MIN (0.80).
  - the underdetermined subset is ORACLE-CAPPED (the drag is genuinely unwinnable): ORACLEHN_underdet <= UNDERDET_ORACLE_CAP (0.13).
  Verdict head PER_RELATION_INFO_CEILING_REFRAME; tag BEST_IN_CLASS_ON_DETERMINED iff all four; IN_SOTA_BAND iff
  PEELHN_det >= DET_SOTA_IN (0.18). Robustness: the determined/underdetermined split is re-reported at CARD_THRESH in
  {1.5, 2.0, 3.0}; the primary gate uses 2.0.

MUST-FAILS (guard-fixed; all required else run BROKEN): oracle fires (C_uni >= 3x RANDOM and headroom >= 0.003);
  SCRAMBLE + PEEL_SCRAMBLE controlled vs RANDOM (<= 0.25 * ANCHOR-margin-over-RANDOM); IDENTITY_SHUFFLE collapses
  (<= 20% of ANCHOR margin-over-RANDOM); pop_at_floor (POP <= RANDOM floor + eps); arms differ (>= 8 sigs);
  Gate-D reproduce (baseline ANCHOR within 0.02 of the confirmed v1 0.1282).

FOUR VALIDITY-PREFLIGHT (self-test): positive_control_passes (ORACLE recovers determined planted tails + clears
  RANDOM); metric_moves (MRR moves across RANDOM/ADDITIVE/ANCHOR/PEELHN/ORACLE); negative_control_margin (RANDOM +
  SCRAMBLE + PEEL_SCRAMBLE + IDSHUF below the best arm, det>=2); full_gates_exercised (aggregate_and_verdict runs).
ADVERSARIAL SELF-TEST DISCRIMINATOR: a PLANTED MIXED arena (functional determined relations + spread one-to-many
  relations) SEPARATES as predicted -- oracle recovers determined tails (det_oracle_mrr >= SELFTEST_DET_ORACLE_MIN)
  but is CAPPED on one-to-many (multi_oracle_mrr <= SELFTEST_MULTI_ORACLE_MAX) with a real gap (det - multi >=
  SELFTEST_SEP_MARGIN); AND the guard-fix fires correctly: a control legitimately beats the structurally-zero POP
  (old_broken_via_pop True = the false-break the source hit) while the NEW pop_at_floor guard stays healthy
  (broken False). This proves the per-relation reframe separates winnable from unwinnable AND the guard-fix flips
  the false BROKEN to a real verdict.

## Compute architecture
class (b/c) MIXED (INHERITED from exp_anchor_compose_magnitude_opt_cskg_v1, imported unchanged): split/POP =
sequential-CPU graph ops; the 4 additive fits (uniform/hardneg/uniform-oracle/hardneg-oracle) = minibatch SGD
(batched, neg-chunked); FLAT + SIC-PEEL compose = vectorized index_add; readouts = query-chunked batched matmul; the
NEW per-relation stratification re-uses the ALREADY-COMPUTED per-query arm_scores (zero extra fits) -- only cheap
masked filtered-MRR calls. Storage SHARDED. device=auto; remote_cpu forces cpu. FULL = the confirmed regime
(k=24/ep=500/k_core=12/support_frac=0.5, seeds=[7,13]) so ANCHOR reproduces 0.128 (Gate-D). No new fit knobs; this is
a re-analysis of the confirmed run with the per-relation lens + the guard-fix.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: 11 scored arms + POP -> >= 8 distinct sigs per seed (inherited fit_and_score).
# - final_metrics_atomicity: tmp_replace (write_metrics + os.replace via _seed_checkpoint).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - info-ceiling: the per-relation ORACLE IS the measured ceiling; the determined gate is ceiling-relative
#   (fraction-of-oracle) so every threshold is feasible-by-construction; the underdetermined cap is an absolute
#   oracle-MRR bound the FULL measures.
# - baseline_in_band: ORACLE must fire; RANDOM/POP near the 1/N floor; Gate-D reproduces the confirmed 0.1282.
# - discriminator survives scale: self-test PLANTED-MIXED arena separates determined from one-to-many; on CSKG the
#   per-relation oracle self-scales (the ceiling IS measured per relation). Must-fails fire deterministically at
#   self-test scale; the guard-fix is asserted (old-would-break vs new-healthy).
# - HARD-PASS strictly above floor: DET_SOTA_NEAR 0.17 clears the aggregate 0.138 by construction only if the
#   determined subset genuinely lifts; DET_CEIL_FRAC_MIN 0.80 and UNDERDET_ORACLE_CAP 0.13 are pre-registered.
# - HP_SCOPE: determined gate applies to ANCHOR_PEEL_HARDNEG (best arm) vs ORACLE_HARDNEG (its ceiling);
#   RANDOM/SCRAMBLE/PEEL_SCRAMBLE/IDSHUF = must-not-clear-floor; POP = pop_at_floor sanity; ORACLE_* = positive controls.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms + >= 8 sigs + a per-relation table.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: adaptive_with_discriminator_gate -- CARD_THRESH + all band fractions pre-registered, NOT tuned
#   on real data; the determined gate is a fraction of the MEASURED per-subset oracle.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the docstring/prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-relation flush prints).

ASCII-only. No bare except; except SystemExit before except Exception.
"""

import argparse
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments._seed_checkpoint import assert_discriminator_fires  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import Graph, build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores, PRIMARY_K,
)
from experiments._fit_checkpoint import cleanup_seed_checkpoints  # noqa: E402

# Reuse the CONFIRMED fit/compose/score machinery + arm names + bands unchanged (identical fit behavior).
from experiments.exp_anchor_compose_magnitude_opt_cskg_v1 import (  # noqa: E402
    fit_and_score, build_heldout_entity_split_ac,
    ANCHOR, PEEL, HARDNEG, PEELHN, ADDITIVE, RANDOM, SCRAMBLE, PEELSCR, IDSHUF, ORACLE, ORACLEHN, POP,
    ALL_ARMS, MECH_ARMS, EVAL_KS, CEIL_METRIC,
    ORACLE_FIRE_RATIO, ORACLE_FIRE_ABS, MIN_HELDOUT, CONTROL_LOSE_EPS,
    SCRAMBLE_CEIL_FRAC, IDSHUF_COLLAPSE_RATIO,
    GATED_REPRODUCE_TARGET, GATED_REPRODUCE_TOL, SOTA_LO, SOTA_HI,
    HELDOUT_ENTITY_FRAC, SUPPORT_FRAC,
    MEMSMOKE_CFG, FULL_CFG,
)

ANCHOR_NAME = "anchor_per_relation_info_ceiling_cskg_v1"

# ---- per-relation cardinality cut (pre-registered; tph = mean valid tails per (head,rel) = filtered-set size) ----
CARD_THRESH = 2.0                     # determined := tph <= this; underdetermined := tph > this
CARD_THRESH_ROBUST = (1.5, 2.0, 3.0)  # robustness sweep (primary gate = CARD_THRESH)

# ---- pre-registered "best-in-class on determined subset" gate (HYPOTHESIZED) ----
DET_SOTA_NEAR = 0.17                  # determined best-arm pooled MRR IN/NEAR SOTA band
DET_SOTA_IN = SOTA_LO                 # 0.18 == in-band lower edge (CITED InductivE/ConceptNet)
DET_FRAC_MIN = 0.20                   # determined subset is a material fraction of held-out queries
DET_CEIL_FRAC_MIN = 0.80             # best arm within 80% of its per-subset oracle ceiling on determined
UNDERDET_ORACLE_CAP = 0.13           # underdetermined oracle-MRR capped below this -> unwinnable mass confirmed

# ---- per-relation eval arms ----
REL_ARMS = [PEELHN, ANCHOR, HARDNEG, PEEL, ORACLE, ORACLEHN]
BEST_ARM = PEELHN                     # the additive best arm (MEASURED@...magnitude_opt:gates.combined.best_arm)
BEST_CEIL = ORACLEHN                  # the best arm's OWN info-ceiling (hardneg oracle)
MIN_REL_Q = 5                         # min queries in a relation to report its per-relation MRR

# ---- self-test planted thresholds (calibrated on the synthetic mixed arena, NOT real data) ----
SELFTEST_DET_ORACLE_MIN = 0.30        # oracle recovers functional/determined planted tails
SELFTEST_MULTI_ORACLE_MAX = 0.20      # oracle CAPPED on planted one-to-many tails (unwinnable even at oracle)
SELFTEST_SEP_MARGIN = 0.10            # (det_oracle - multi_oracle) >= this (the reframe separates)
SELFTEST_AC_BEATS_RANDOM_MRR = 0.03
SELFTEST_SCRAMBLE_MARGIN_MRR = 0.02
SELFTEST_MIN_HO = 8

POP_FLOOR_ABS = 0.02                  # pop_at_floor absolute tolerance (POP <= max(RANDOM, this) + eps)

# Config: reuse the confirmed FULL/MEMSMOKE; SELFTEST is this cell's own PLANTED-MIXED arena.
SELFTEST_CFG = dict(k=12, epochs=200, n_neg=32, batch=4096,
                    heldout_entity_frac=0.15, support_frac=0.5, n_heldout_eval=0, min_heldout=SELFTEST_MIN_HO)


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _sub(a, b):
    return (a - b) if (a == a and b == b) else float("nan")


def _ratio(a, b):
    if not (a == a and b == b):
        return float("nan")
    return float("inf") if b <= 0 else a / b


def _rnd(x, nd=6):
    return round(x, nd) if (x == x) else None


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
# Cardinality + per-relation stratified evaluation (the NEW analysis layer; zero extra fits).
# ---------------------------------------------------------------------------

def compute_rel_cardinality(all_true, rel_i2lbl):
    """tph[r] = mean number of valid tails per (head, rel) pair (= filtered-set size = info-ceiling proxy)."""
    rel_sizes = defaultdict(list)
    for (h, r), tails in all_true.items():
        rel_sizes[int(r)].append(len(tails))
    tph = {}
    for r, sizes in rel_sizes.items():
        tph[rel_i2lbl.get(r, "r%d" % r)] = float(np.mean(sizes))
    return tph


def _subset_mrr(scores, query_int, all_true, mask, arm_name):
    idx = np.where(mask)[0]
    if idx.size < 1:
        return float("nan"), 0
    sub = filtered_hits_from_scores(scores[idx], query_int[idx], all_true, ks=EVAL_KS)
    return float(sub.get(CEIL_METRIC, float("nan"))), int(idx.size)


def per_relation_eval(arm_scores, query_int, all_true, rel_i2lbl, tph):
    """Per individual relation: best-arm/baseline/oracle filtered-MRR + fraction-of-ceiling + cardinality (tph)."""
    rels_present = sorted(set(int(r) for r in query_int[:, 1].tolist()))
    per_rel = []
    for r in rels_present:
        lbl = rel_i2lbl.get(r, "r%d" % r)
        mask = (query_int[:, 1] == r)
        nq = int(mask.sum())
        if nq < MIN_REL_Q:
            continue
        mrrs = {}
        for a in REL_ARMS:
            v, _ = _subset_mrr(arm_scores[a], query_int, all_true, mask, a)
            mrrs[a] = v
        best = mrrs.get(BEST_ARM, float("nan"))
        ceil = mrrs.get(BEST_CEIL, float("nan"))
        frac = _ratio(best, ceil)
        per_rel.append(dict(
            rel=lbl, tph=round(tph.get(lbl, float("nan")), 4), n_query=nq,
            mrr_best=_rnd(best), mrr_baseline=_rnd(mrrs.get(ANCHOR, float("nan"))),
            mrr_oracle_hn=_rnd(ceil), mrr_oracle_uni=_rnd(mrrs.get(ORACLE, float("nan"))),
            frac_of_ceiling=(_rnd(frac) if frac != float("inf") else None),
            determined=bool(tph.get(lbl, 1e9) <= CARD_THRESH)))
    per_rel.sort(key=lambda d: (d["tph"] if d["tph"] == d["tph"] else 1e9))
    return per_rel


def determined_split_eval(arm_scores, query_int, all_true, rel_i2lbl, tph, thresh):
    """Pooled (query-weighted) determined vs underdetermined subset MRR for best-arm + baseline + oracles."""
    nq_total = query_int.shape[0]
    q_tph = np.array([tph.get(rel_i2lbl.get(int(query_int[i, 1]), ""), 1e9) for i in range(nq_total)],
                     dtype=np.float64)
    det_mask = q_tph <= thresh
    und_mask = ~det_mask
    out = dict(thresh=thresh, n_query_total=int(nq_total),
               n_determined=int(det_mask.sum()), n_underdetermined=int(und_mask.sum()),
               determined_query_frac=(round(float(det_mask.sum()) / nq_total, 5) if nq_total else None))
    for tag, mask in (("determined", det_mask), ("underdetermined", und_mask)):
        d = {}
        for a in (BEST_ARM, ANCHOR, ORACLE, ORACLEHN):
            v, n = _subset_mrr(arm_scores[a], query_int, all_true, mask, a)
            d[a] = _rnd(v)
        best = d.get(BEST_ARM)
        ceil = d.get(BEST_CEIL)
        d["frac_of_ceiling"] = (_rnd(best / ceil) if (best is not None and ceil not in (None, 0)) else None)
        d["n"] = int(mask.sum())
        out[tag] = d
    return out


# ---------------------------------------------------------------------------
# One corpus run: reuse the confirmed split + fit_and_score, add the per-relation lens.
# ---------------------------------------------------------------------------

def run_corpus(pool_lbl, cfg, device, seed, corpus_name, ckpt_dir=None):
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    rel_i2lbl = {v: k for k, v in rel2i.items()}
    train_lbl, support_lbl, query_lbl, hold_ids, n_cold = build_heldout_entity_split_ac(
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

    result = dict(corpus=corpus_name, seed=seed, N=int(N), n_rel=int(n_rel), n_train=int(train_int.shape[0]),
                  n_heldout_entities=len(hold_ids), n_support=int(support_int.shape[0]),
                  n_query_total=n_query_total, n_query_scored=int(query_int.shape[0]), n_cold=int(n_cold),
                  heldout_entity_frac=cfg["heldout_entity_frac"], support_frac=cfg["support_frac"])
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    fs = fit_and_score(train_int, support_int, query_int, hold_all, N, n_rel, cfg, device, seed,
                       gd.rel_tail_freq, all_true, ckpt_dir=ckpt_dir)
    am = fs["arm_metric"]
    result.update(
        arm_hits={a: {kk: round(vv, 5) for kk, vv in am[a].items() if kk != "n"} for a in ALL_ARMS},
        arm_n={a: am[a]["n"] for a in ALL_ARMS},
        arm_sigs=fs["arm_sig"],
    )
    tph = compute_rel_cardinality(all_true, rel_i2lbl)
    result["rel_cardinality"] = {k: round(v, 4) for k, v in tph.items()}
    result["per_relation"] = per_relation_eval(fs["arm_scores"], query_int, all_true, rel_i2lbl, tph)
    result["determined_split"] = {("thr_%.1f" % t): determined_split_eval(
        fs["arm_scores"], query_int, all_true, rel_i2lbl, tph, t) for t in CARD_THRESH_ROBUST}
    return result


# ---------------------------------------------------------------------------
# Aggregate + verdict (guard-fixed: pop_at_floor sanity replaces the false control-beats-POP break).
# ---------------------------------------------------------------------------

def _m(ps, arm):
    return ps["arm_hits"][arm].get(CEIL_METRIC, float("nan"))


def _agg_split(per_seed, thr_key):
    """n-weighted pool of the determined/underdetermined subset MRRs across seeds."""
    out = {}
    for tag in ("determined", "underdetermined"):
        acc = defaultdict(list); accn = defaultdict(list); fracs = []
        for ps in per_seed:
            blk = ps.get("determined_split", {}).get(thr_key, {}).get(tag, {})
            n = blk.get("n", 0)
            for a in (BEST_ARM, ANCHOR, ORACLE, ORACLEHN):
                v = blk.get(a)
                if v is not None and n >= 1:
                    acc[a].append(v * n); accn[a].append(n)
        for a in (BEST_ARM, ANCHOR, ORACLE, ORACLEHN):
            tot_n = sum(accn[a])
            out.setdefault(tag, {})[a] = (round(sum(acc[a]) / tot_n, 6) if tot_n > 0 else None)
        best = out[tag].get(BEST_ARM); ceil = out[tag].get(BEST_CEIL)
        out[tag]["frac_of_ceiling"] = (round(best / ceil, 5) if (best is not None and ceil not in (None, 0)) else None)
        out[tag]["n"] = int(_nm([ps.get("determined_split", {}).get(thr_key, {}).get(tag, {}).get("n", 0)
                                 for ps in per_seed]))
    fr = [ps.get("determined_split", {}).get(thr_key, {}).get("determined_query_frac")
          for ps in per_seed]
    fr = [x for x in fr if x is not None]
    out["determined_query_frac"] = (round(float(np.mean(fr)), 5) if fr else None)
    return out


def aggregate_and_verdict(per_seed):
    m = {a: _nm([_m(ps, a) for ps in per_seed]) for a in ALL_ARMS}
    n_query = int(_nm([ps["n_query_scored"] for ps in per_seed]))
    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    spectrum = {a: {mk: _nm([ps["arm_hits"][a].get(mk, float("nan")) for ps in per_seed]) for mk in metric_keys}
                for a in ALL_ARMS}

    b = m[ANCHOR]; C_uni = m[ORACLE]; C_hn = m[ORACLEHN]; rand = m[RANDOM]

    reproduce_ok = bool(b == b and abs(b - GATED_REPRODUCE_TARGET) <= GATED_REPRODUCE_TOL)

    oracle_headroom = _sub(C_uni, rand); oracle_ratio = _ratio(C_uni, rand)
    enough_heldout = bool(n_query >= MIN_HELDOUT)
    oracle_fires = bool(oracle_headroom == oracle_headroom and oracle_headroom >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)

    # ---- must-fail controls vs the RANDOM arm-floor (NOT POP) ----
    d_scramble = _sub(m[SCRAMBLE], rand); d_peelscr = _sub(m[PEELSCR], rand)
    anchor_margin = _sub(b, rand); peel_margin_over_rand = _sub(m[PEEL], rand)
    scramble_ceiling = (SCRAMBLE_CEIL_FRAC * anchor_margin) if anchor_margin == anchor_margin else float("nan")
    peelscr_ceiling = (SCRAMBLE_CEIL_FRAC * peel_margin_over_rand) if peel_margin_over_rand == peel_margin_over_rand else float("nan")
    scramble_controlled = bool(d_scramble == d_scramble and scramble_ceiling == scramble_ceiling and d_scramble <= scramble_ceiling)
    peelscr_controlled = bool(d_peelscr == d_peelscr and peelscr_ceiling == peelscr_ceiling and d_peelscr <= peelscr_ceiling)
    idshuf_margin = _sub(m[IDSHUF], rand)
    idshuf_collapse_ratio = _ratio(idshuf_margin, anchor_margin)
    idshuf_collapses = bool(idshuf_collapse_ratio == idshuf_collapse_ratio and idshuf_collapse_ratio <= IDSHUF_COLLAPSE_RATIO)

    # ---- GUARD FIX: pop_at_floor sanity (ported from self-test) replaces the false control-beats-POP break ----
    pop_at_floor = bool(m[POP] == m[POP] and m[POP] <= max(rand, POP_FLOOR_ABS) + CONTROL_LOSE_EPS)
    # transparency: what the OLD (buggy) POP-based broken test would have said (does NOT gate).
    old_broken_margin = max(CONTROL_LOSE_EPS, SCRAMBLE_CEIL_FRAC * _sub(C_uni, b)) if _sub(C_uni, b) == _sub(C_uni, b) else CONTROL_LOSE_EPS
    old_broken_via_pop = bool((m[RANDOM] == m[RANDOM] and m[POP] == m[POP] and (m[RANDOM] - m[POP]) > old_broken_margin)
                              or (m[SCRAMBLE] == m[SCRAMBLE] and m[POP] == m[POP] and (m[SCRAMBLE] - m[POP]) > old_broken_margin))
    broken = bool(not pop_at_floor)   # NEW: only a genuinely-leaking POP breaks the run

    all_sigs = set()
    for ps in per_seed:
        all_sigs |= set(ps.get("arm_sigs", {}).values())
    arms_differ = bool(len(all_sigs) >= 8)

    must_fails_ok = bool(oracle_fires and scramble_controlled and peelscr_controlled and idshuf_collapses
                         and pop_at_floor and not broken and arms_differ)

    # ---- per-relation info-ceiling reframe (primary threshold) ----
    primary_key = "thr_%.1f" % CARD_THRESH
    agg_primary = _agg_split(per_seed, primary_key)
    det = agg_primary.get("determined", {}); und = agg_primary.get("underdetermined", {})
    det_frac = agg_primary.get("determined_query_frac")
    peelhn_det = det.get(BEST_ARM); oracle_hn_det = det.get(BEST_CEIL)
    peelhn_und = und.get(BEST_ARM); oracle_hn_und = und.get(BEST_CEIL)
    det_ceil_frac = (peelhn_det / oracle_hn_det) if (peelhn_det is not None and oracle_hn_det not in (None, 0)) else None

    det_in_sota_near = bool(peelhn_det is not None and peelhn_det >= DET_SOTA_NEAR)
    det_in_sota_band = bool(peelhn_det is not None and peelhn_det >= DET_SOTA_IN)
    det_material = bool(det_frac is not None and det_frac >= DET_FRAC_MIN)
    det_near_ceiling = bool(det_ceil_frac is not None and det_ceil_frac >= DET_CEIL_FRAC_MIN)
    underdet_capped = bool(oracle_hn_und is not None and oracle_hn_und <= UNDERDET_ORACLE_CAP)
    best_in_class_determined = bool(det_in_sota_near and det_material and det_near_ceiling and underdet_capped)

    # aggregate gap-to-SOTA decomposition: how much of the (SOTA - aggregate) gap is unwinnable underdetermined mass.
    agg_best = m[BEST_ARM]
    gap_to_sota = _sub(DET_SOTA_IN, agg_best)
    # unwinnable drag = fraction of queries underdetermined * (SOTA - their oracle ceiling)
    und_frac = (1.0 - det_frac) if det_frac is not None else float("nan")
    unwinnable_drag = ((und_frac * _sub(DET_SOTA_IN, oracle_hn_und)) if (und_frac == und_frac and oracle_hn_und is not None) else float("nan"))
    unwinnable_gap_share = (_ratio(unwinnable_drag, gap_to_sota) if (unwinnable_drag == unwinnable_drag and gap_to_sota == gap_to_sota) else float("nan"))

    if not enough_heldout:
        verdict = "INCONCLUSIVE_TOO_FEW_HELDOUT"
    elif not reproduce_ok:
        verdict = "INCONCLUSIVE_BASELINE_DID_NOT_REPRODUCE_v1"
    elif broken:
        verdict = "BROKEN_POP_NOT_AT_FLOOR"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_UNDERFIT"
    elif not (scramble_controlled and peelscr_controlled and idshuf_collapses and arms_differ):
        verdict = "BROKEN_MUST_FAIL_CONTROL_FIRED"
    else:
        tags = []
        tags.append("BEST_IN_CLASS_ON_DETERMINED" if best_in_class_determined else "PARTIAL_DETERMINED")
        if det_in_sota_band:
            tags.append("DET_IN_SOTA_BAND")
        if not det_in_sota_near:
            tags.append("DET_BELOW_SOTA_NEAR")
        if not det_material:
            tags.append("DET_NOT_MATERIAL")
        if not det_near_ceiling:
            tags.append("DET_BELOW_CEILING_FRAC")
        if not underdet_capped:
            tags.append("UNDERDET_NOT_CAPPED")
        verdict = "PER_RELATION_INFO_CEILING_REFRAME__" + "_".join(tags)

    verdict_msg = (
        "%s || AGG best(%s)=%s baseline ANCHOR=%s (reproduce v1 0.1282 ok=%s) oracle_uni=%s oracle_hn=%s RANDOM=%s POP=%s "
        "|| DETERMINED(tph<=%.1f, frac=%s): best=%s oracle_hn=%s frac_of_ceiling=%s (>=%.2f near-SOTA=%s in-band[%.2f-%.2f]=%s) "
        "|| UNDERDETERMINED(frac=%s): best=%s oracle_hn=%s (capped<=%.2f=%s) "
        "|| unwinnable_gap_share=%s of gap_to_SOTA=%s || best_in_class_determined=%s "
        "|| GUARD-FIX pop_at_floor=%s (old_broken_via_pop=%s -> NEW broken=%s) "
        "|| oracle_fires=%s scramble_ok=%s peelscr_ok=%s idshuf_collapse=%s arms_differ=%s(sigs=%d) seeds=%d nq=%d"
        % (verdict, BEST_ARM, _fmt(agg_best), _fmt(b), reproduce_ok, _fmt(C_uni), _fmt(C_hn), _fmt(rand), _fmt(m[POP]),
           CARD_THRESH, (("%.3f" % det_frac) if det_frac is not None else "nan"),
           _fmt(peelhn_det if peelhn_det is not None else float("nan")),
           _fmt(oracle_hn_det if oracle_hn_det is not None else float("nan")),
           (("%.3f" % det_ceil_frac) if det_ceil_frac is not None else "nan"), DET_CEIL_FRAC_MIN, det_in_sota_near,
           DET_SOTA_IN, SOTA_HI, det_in_sota_band,
           (("%.3f" % und_frac) if und_frac == und_frac else "nan"),
           _fmt(peelhn_und if peelhn_und is not None else float("nan")),
           _fmt(oracle_hn_und if oracle_hn_und is not None else float("nan")), UNDERDET_ORACLE_CAP, underdet_capped,
           (_fmt(unwinnable_gap_share) if unwinnable_gap_share != float("inf") else "inf"), _fmt(gap_to_sota),
           best_in_class_determined, pop_at_floor, old_broken_via_pop, broken,
           oracle_fires, scramble_controlled, peelscr_controlled, idshuf_collapses, arms_differ, len(all_sigs),
           len(per_seed), n_query))

    gates = dict(
        verdict=verdict, ceil_metric=CEIL_METRIC,
        heldout_metric_spectrum={a: {mk: _rnd(spectrum[a][mk]) for mk in metric_keys} for a in ALL_ARMS},
        heldout_mrr={a: _rnd(m[a]) for a in ALL_ARMS},
        n_query_scored=n_query, primary_k=PRIMARY_K,
        baseline_reproduce=dict(measured=_rnd(b), target=GATED_REPRODUCE_TARGET, tol=GATED_REPRODUCE_TOL, ok=reproduce_ok),
        best_arm=dict(name=BEST_ARM, agg_mrr=_rnd(agg_best), ceiling_arm=BEST_CEIL, agg_ceiling=_rnd(C_hn)),
        per_relation_reframe=dict(
            card_metric="mean_valid_tails_per_head_rel_tph", card_thresh_primary=CARD_THRESH,
            determined=dict(best_arm_mrr=_rnd(peelhn_det) if peelhn_det is not None else None,
                            baseline_mrr=_rnd(det.get(ANCHOR)) if det.get(ANCHOR) is not None else None,
                            oracle_hn_mrr=_rnd(oracle_hn_det) if oracle_hn_det is not None else None,
                            oracle_uni_mrr=_rnd(det.get(ORACLE)) if det.get(ORACLE) is not None else None,
                            frac_of_ceiling=_rnd(det_ceil_frac) if det_ceil_frac is not None else None,
                            query_frac=det_frac, n=det.get("n")),
            underdetermined=dict(best_arm_mrr=_rnd(peelhn_und) if peelhn_und is not None else None,
                                 oracle_hn_mrr=_rnd(oracle_hn_und) if oracle_hn_und is not None else None,
                                 oracle_uni_mrr=_rnd(und.get(ORACLE)) if und.get(ORACLE) is not None else None,
                                 query_frac=_rnd(und_frac) if und_frac == und_frac else None, n=und.get("n")),
            gap_to_sota=_rnd(gap_to_sota), unwinnable_drag=_rnd(unwinnable_drag),
            unwinnable_gap_share=(_rnd(unwinnable_gap_share) if unwinnable_gap_share != float("inf") else None),
            det_in_sota_near=det_in_sota_near, det_in_sota_band=det_in_sota_band, det_material=det_material,
            det_near_ceiling=det_near_ceiling, underdet_capped=underdet_capped,
            best_in_class_determined=best_in_class_determined,
            robustness={tk: _agg_split(per_seed, tk) for tk in ["thr_%.1f" % t for t in CARD_THRESH_ROBUST]}),
        oracle_uniform=dict(mrr=_rnd(C_uni), headroom_vs_random=_rnd(oracle_headroom),
                            ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
                            fires=oracle_fires),
        oracle_hardneg=dict(mrr=_rnd(C_hn)),
        guard_fix=dict(pop_mrr=_rnd(m[POP]), random_mrr=_rnd(rand), pop_at_floor=pop_at_floor,
                       pop_floor_abs=POP_FLOOR_ABS, old_broken_via_pop=old_broken_via_pop, broken=broken,
                       note="controls governed vs RANDOM floor; POP is at-floor sanity not a bar"),
        must_fails=dict(scramble_margin=_rnd(d_scramble), scramble_ceiling=_rnd(scramble_ceiling),
                        scramble_controlled=scramble_controlled, peelscr_margin=_rnd(d_peelscr),
                        peelscr_ceiling=_rnd(peelscr_ceiling), peelscr_controlled=peelscr_controlled,
                        idshuf_margin=_rnd(idshuf_margin), anchor_margin=_rnd(anchor_margin),
                        idshuf_collapse_ratio=(round(idshuf_collapse_ratio, 4) if (idshuf_collapse_ratio == idshuf_collapse_ratio and idshuf_collapse_ratio != float("inf")) else None),
                        idshuf_collapses=idshuf_collapses, pop_at_floor=pop_at_floor, broken=broken,
                        arms_differ=arms_differ, n_distinct_sigs=len(all_sigs), must_fails_ok=must_fails_ok),
        bands=dict(CARD_THRESH=CARD_THRESH, CARD_THRESH_ROBUST=list(CARD_THRESH_ROBUST),
                   DET_SOTA_NEAR=DET_SOTA_NEAR, DET_SOTA_IN=DET_SOTA_IN, DET_FRAC_MIN=DET_FRAC_MIN,
                   DET_CEIL_FRAC_MIN=DET_CEIL_FRAC_MIN, UNDERDET_ORACLE_CAP=UNDERDET_ORACLE_CAP,
                   SOTA_LO=SOTA_LO, SOTA_HI=SOTA_HI, ORACLE_FIRE_RATIO=ORACLE_FIRE_RATIO,
                   ORACLE_FIRE_ABS=ORACLE_FIRE_ABS, SCRAMBLE_CEIL_FRAC=SCRAMBLE_CEIL_FRAC,
                   IDSHUF_COLLAPSE_RATIO=IDSHUF_COLLAPSE_RATIO, POP_FLOOR_ABS=POP_FLOOR_ABS,
                   HELDOUT_ENTITY_FRAC=HELDOUT_ENTITY_FRAC, SUPPORT_FRAC=SUPPORT_FRAC),
        enough_heldout=enough_heldout, reproduce_ok=reproduce_ok, oracle_fires=oracle_fires,
        must_fails_ok=must_fails_ok,
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Planted MIXED-cardinality arena: functional (determined) relations + spread one-to-many relations.
# ---------------------------------------------------------------------------

def build_planted_mixed_arena(seed, n_ent=360, n_rel_det=4, n_rel_multi=3, k_lat=8, deg_det=3,
                              multi_tails=5, w_scale=1.0):
    """Determined relations: functional argmin (1 tail per head) -> oracle recovers. One-to-many relations: each
    head emits `multi_tails` SPREAD tails (uniform-random distinct) whose additive centroid z[h]+w[r] sits in
    foreign space -> oracle CAPPED (non-true entities outrank the specific held-out tail). Deterministic dedup."""
    rng = np.random.default_rng(seed * 100019 + 3)
    n_rel = n_rel_det + n_rel_multi
    z = rng.standard_normal((n_ent, k_lat))
    w = rng.standard_normal((n_rel, k_lat)) * w_scale
    edges = []
    det_rels = list(range(n_rel_det))
    multi_rels = list(range(n_rel_det, n_rel))
    for h in range(n_ent):
        rels = rng.choice(det_rels, size=min(deg_det, n_rel_det), replace=False)
        for r in rels:
            target = z[h] + w[r]
            d = np.linalg.norm(z - target, axis=1); d[h] = np.inf
            t = int(np.argmin(d))
            edges.append(("e%d" % h, "r%d" % r, "e%d" % t))
    # one-to-many: each head, each multi relation -> multi_tails spread random tails
    for h in range(n_ent):
        for r in multi_rels:
            cands = [int(x) for x in rng.choice(n_ent, size=multi_tails + 2, replace=False) if int(x) != h][:multi_tails]
            for t in cands:
                edges.append(("e%d" % h, "r%d" % r, "e%d" % t))
    return list(dict.fromkeys(edges))


# ---------------------------------------------------------------------------
# Self-test: the reframe SEPARATES determined from one-to-many + the guard-fix fires correctly.
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    try:
        return _selftest_body(device)
    finally:
        torch.set_num_threads(_prev)


def _selftest_body(device):
    pool = build_planted_mixed_arena(7)
    cfg = dict(SELFTEST_CFG)
    res = run_corpus(pool, cfg, device, 7, "PLANTED_MIXED_HELDOUT_ENTITY")
    out = dict(N=res.get("N"), n_heldout_entities=res.get("n_heldout_entities"),
               n_support=res.get("n_support"), n_query=res.get("n_query_scored"), n_cold=res.get("n_cold"))
    if res.get("empty") or res.get("n_query_scored", 0) < SELFTEST_MIN_HO:
        out["fail"] = "planted arena too few held-out queries (%s)" % res.get("n_query_scored")
        return False, out

    ah = res["arm_hits"]
    m = {a: ah[a].get(CEIL_METRIC, float("nan")) for a in ALL_ARMS}
    n_sigs = len(set(res["arm_sigs"].values()))

    # per-relation separation: determined (functional r0..r3) vs one-to-many (r4..r6).
    dsplit = res["determined_split"]["thr_%.1f" % CARD_THRESH]
    det_oracle = dsplit["determined"].get(ORACLE, float("nan"))
    multi_oracle = dsplit["underdetermined"].get(ORACLE, float("nan"))
    det_oracle = det_oracle if det_oracle is not None else float("nan")
    multi_oracle = multi_oracle if multi_oracle is not None else float("nan")
    sep = _sub(det_oracle, multi_oracle)

    anchor_margin = m[ANCHOR] - m[RANDOM]
    scramble_margin = m[ANCHOR] - m[SCRAMBLE]
    oracle_margin = m[ORACLE] - m[RANDOM]
    oracle_ratio = _ratio(m[ORACLE], m[RANDOM])

    # GUARD-FIX proof: on this planted arena a control legitimately beats the structurally-zero POP (old false-break),
    # while the NEW pop_at_floor guard stays healthy.
    _st_v, _st_msg, st_gates = aggregate_and_verdict([res])
    gf = st_gates["guard_fix"]
    old_broken_via_pop = bool(gf["old_broken_via_pop"])
    new_broken = bool(gf["broken"])
    pop_at_floor = bool(gf["pop_at_floor"])

    det_separates = bool(det_oracle == det_oracle and det_oracle >= SELFTEST_DET_ORACLE_MIN
                         and multi_oracle == multi_oracle and multi_oracle <= SELFTEST_MULTI_ORACLE_MAX
                         and sep == sep and sep >= SELFTEST_SEP_MARGIN)
    oracle_fires = bool(oracle_margin == oracle_margin and oracle_margin >= ORACLE_FIRE_ABS
                        and oracle_ratio == oracle_ratio and oracle_ratio >= ORACLE_FIRE_RATIO)
    anchor_beats_random = bool(anchor_margin == anchor_margin and anchor_margin >= SELFTEST_AC_BEATS_RANDOM_MRR)
    scramble_fails = bool(scramble_margin == scramble_margin and scramble_margin >= SELFTEST_SCRAMBLE_MARGIN_MRR)
    guard_fix_fires = bool(old_broken_via_pop and (not new_broken) and pop_at_floor)
    arms_differ = bool(n_sigs >= 8)

    # VACUOUS-SMOKE guards: the arena must be answerable AND the reframe MUST separate AND the guard-fix MUST fire.
    assert_discriminator_fires(bool(anchor_margin <= SELFTEST_AC_BEATS_RANDOM_MRR), control_name=RANDOM,
                               headline_name="anchor_beats_random_heldout", run_mode="self_test",
                               extra="RANDOM reached ANCHOR on planted arena -> not answerable")
    assert_discriminator_fires(bool(sep < SELFTEST_SEP_MARGIN), control_name="ONE_TO_MANY_ORACLE",
                               headline_name="determined_oracle_separates_from_one_to_many_oracle",
                               run_mode="self_test",
                               extra="determined oracle did not exceed one-to-many oracle by %.3f -> the per-relation "
                                     "info-ceiling reframe does not separate winnable from unwinnable" % SELFTEST_SEP_MARGIN)
    assert_discriminator_fires(bool(not guard_fix_fires), control_name="POP_GUARD",
                               headline_name="guard_fix_flips_false_pop_break_to_healthy", run_mode="self_test",
                               extra="guard-fix did not fire: needs old_broken_via_pop=True AND new broken=False AND "
                                     "pop_at_floor=True (old=%s new_broken=%s pop_at_floor=%s)"
                                     % (old_broken_via_pop, new_broken, pop_at_floor))

    vp_ok = run_validity_preflight([
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(det_separates and oracle_fires),
         "control_name": "ORACLE_ADDITIVE", "headline_name": "oracle_recovers_determined_and_caps_one_to_many",
         "extra": "planted: determined oracle=%.3f >= %.2f, one-to-many oracle=%.3f <= %.2f (sep=%.3f)"
                  % (det_oracle, SELFTEST_DET_ORACLE_MIN, multi_oracle, SELFTEST_MULTI_ORACLE_MAX, sep)},
        {"kind": "metric_moves", "metric_name": "heldout_mrr",
         "values": [m[RANDOM], m[ADDITIVE], m[ANCHOR], m[PEELHN], m[ORACLE]],
         "extra": "MRR RANDOM=%.3f ADDITIVE=%.3f ANCHOR=%.3f PEELHN=%.3f ORACLE=%.3f"
                  % (m[RANDOM], m[ADDITIVE], m[ANCHOR], m[PEELHN], m[ORACLE])},
        {"kind": "negative_control_margin",
         "control_scores": [m[RANDOM], m[SCRAMBLE], m[PEELSCR], m[IDSHUF]],
         "headline_threshold": m[PEELHN], "higher_is_pass": True, "margin": SELFTEST_SCRAMBLE_MARGIN_MRR,
         "n_repeats_min": 2, "control_name": "RANDOM_SCRAMBLE_PEELSCR_IDSHUF_below_best",
         "extra": "RANDOM + relation-scrambled + identity-shuffled must sit below the best arm"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arms_differ", "oracle_fires", "scramble_controlled", "peelscr_controlled",
                                    "idshuf_collapses", "pop_at_floor", "determined_separates", "guard_fix"],
         "exercised_gates": ["arms_differ", "oracle_fires", "scramble_controlled", "peelscr_controlled",
                             "idshuf_collapses", "pop_at_floor", "determined_separates", "guard_fix"],
         "extra": "aggregate_and_verdict verdict=%s at self-test scale" % _st_v},
    ], run_mode="self_test")

    metric_keys = ["hits@%d" % k for k in EVAL_KS] + ["mrr"]
    out.update(
        heldout_mrr={a: round(m[a], 5) for a in ALL_ARMS},
        heldout_metric_spectrum={a: {mk: round(ah[a].get(mk, float("nan")), 5) for mk in metric_keys} for a in ALL_ARMS},
        n_distinct_sigs=n_sigs, det_oracle_mrr=round(det_oracle, 5) if det_oracle == det_oracle else None,
        multi_oracle_mrr=round(multi_oracle, 5) if multi_oracle == multi_oracle else None,
        determined_vs_onetomany_sep=round(sep, 5) if sep == sep else None,
        determined_query_frac=res["determined_split"]["thr_%.1f" % CARD_THRESH].get("determined_query_frac"),
        anchor_margin=round(anchor_margin, 5), scramble_margin=round(scramble_margin, 5),
        oracle_margin=round(oracle_margin, 5),
        oracle_ratio=(round(oracle_ratio, 2) if (oracle_ratio == oracle_ratio and oracle_ratio != float("inf")) else None),
        old_broken_via_pop=old_broken_via_pop, new_broken=new_broken, pop_at_floor=pop_at_floor,
        det_separates=det_separates, oracle_fires=oracle_fires, anchor_beats_random=anchor_beats_random,
        scramble_fails=scramble_fails, guard_fix_fires=guard_fix_fires, arms_differ=arms_differ,
        selftest_verdict=_st_v, validity_preflight_ok=bool(vp_ok),
        per_relation=res.get("per_relation"), rel_cardinality=res.get("rel_cardinality"),
        validity_preflight_declared=["positive_control_passes", "metric_moves",
                                     "negative_control_fails_with_margin", "full_gates_exercised_at_selftest"],
    )
    ok = bool(det_separates and oracle_fires and anchor_beats_random and scramble_fails
              and guard_fix_fires and arms_differ)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def _resolve_device(arg_device):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    force_cpu = (arg_device == "cpu") or (env_dev == "cpu") or (env_queue == "remote_cpu_queue")
    if force_cpu:
        return torch.device("cpu")
    want_cuda = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode])
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s cuda=%s run_mode=%s seeds=%s k=%s epochs=%s card_thresh=%s" %
         (device, torch.cuda.is_available(), run_mode, seeds, cfg["k"], cfg["epochs"], CARD_THRESH))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s det_oracle=%s multi_oracle=%s sep=%s guard_fix_fires=%s "
         "(old_break=%s new_break=%s pop_at_floor=%s) det_frac=%s vp_ok=%s" %
         (st_ok, st_res.get("det_oracle_mrr"), st_res.get("multi_oracle_mrr"),
          st_res.get("determined_vs_onetomany_sep"), st_res.get("guard_fix_fires"),
          st_res.get("old_broken_via_pop"), st_res.get("new_broken"), st_res.get("pop_at_floor"),
          st_res.get("determined_query_frac"), st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (determined/one-to-many did not separate / guard-fix did not "
                        "fire / must-fails did not fire / arms not distinct): %s" % st_res.get("fail", ""),
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS per-relation info-ceiling reframe: planted determined relations separate from "
                        "one-to-many (oracle recovers determined, caps one-to-many); guard-fix flips the false "
                        "control-beats-POP break to healthy (pop_at_floor); must-fails fire; 4 validity-preflight declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d avgdeg=%.1f rels=%d pool_edges=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["core_avgdeg"],
                    prov["n_rel_tokens"], len(pool)))
            res = run_corpus(pool, cfg, device, seed, "CSKG_CORE_HELDOUT_ENTITY", ckpt_dir=out_dir)
            res["cskg_provenance"] = prov
            if res.get("empty") or res["n_query_scored"] < cfg.get("min_heldout", MIN_HELDOUT):
                raise RuntimeError("held-out-entity query edges too few (%d < %d)" %
                                   (res.get("n_query_scored", 0), cfg.get("min_heldout", MIN_HELDOUT)))
            sigset = set(res["arm_sigs"].values())
            if len(sigset) < 8:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d only %d distinct sigs" % (seed, len(sigset)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            cleanup_seed_checkpoints(out_dir, seed)
            dsp = res["determined_split"]["thr_%.1f" % CARD_THRESH]
            _log("seed=%d nq=%d | AGG best=%s ANCHOR=%s ORACLE_hn=%s | DET(frac=%s) best=%s oracle=%s | "
                 "UNDET best=%s oracle=%s (%.1fs)" %
                 (seed, res["n_query_scored"], _fmt(res["arm_hits"][BEST_ARM]["mrr"]),
                  _fmt(res["arm_hits"][ANCHOR]["mrr"]), _fmt(res["arm_hits"][ORACLEHN]["mrr"]),
                  dsp.get("determined_query_frac"),
                  _fmt(dsp["determined"].get(BEST_ARM) or float("nan")),
                  _fmt(dsp["determined"].get(BEST_CEIL) or float("nan")),
                  _fmt(dsp["underdetermined"].get(BEST_ARM) or float("nan")),
                  _fmt(dsp["underdetermined"].get(BEST_CEIL) or float("nan")), time.time() - ts))
            _hb("cskg", si)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))
        finally:
            if getattr(device, "type", "") == "cuda":
                torch.cuda.empty_cache()

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=seeds, config=cfg, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "memsmoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--memsmoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("memsmoke" if args.memsmoke else args.run_mode)
    if not args.self_test and not args.memsmoke and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "memsmoke", "full"):
            run_mode = _env_mode
    device = _resolve_device(args.device)
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
