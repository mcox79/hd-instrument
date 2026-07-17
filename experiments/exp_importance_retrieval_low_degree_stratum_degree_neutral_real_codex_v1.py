"""exp_importance_retrieval_low_degree_stratum_degree_neutral_real_codex_v1

DECISIVE CLOSE on the 4th axis (importance / downstream-reach) for our substrate.

CONTEXT. The pooled importance->retrieval test HARD_FAILED
(exp_importance_retrieval_relevance_query_centrality_real_codex_v1: pc_btwn=0.100, tert_btwn=0.035,
verdict HARD_FAIL) BUT the per-degree-bin breakdown showed a SIGN-FLIP: the lowest-degree quartile
(bin0, n=718) gave a top-vs-bottom-importance appearance-gap of +0.335 while the higher-degree bins
reversed (-0.025, -0.148, -0.185), cancelling to ~0 pooled -- a candidate Simpson's-paradox rescue
(classical-IR intuition: among SPARSE entities, high-betweenness bridges predict retrieval where degree
cannot). This cell tests the CORRECT-CALC hypothesis DECISIVELY: does importance predict retrieval-
relevance AMONG the low-degree periphery stratum, DEGREE-NEUTRAL WITHIN the stratum (the +0.335 must NOT
be a residual-degree artifact INSIDE the low-degree bin)?

DATASET NOTE (honest): CoDEx-claimvalidity is a filtered/dense KG; the MINIMUM entity degree is 10, so
the "low-degree periphery" stratum here = the RELATIVELY lowest-degree quartile (train degrees 10-15),
NOT absolute-sparse deg 1-3 entities. The classical-IR "bridges among sparse entities" intuition is
tested on the relatively-lowest-degree stratum available in this real graph. Reported plainly.

THE QUESTION (reported in SEPARATE PARTS -- do not blob):
  Within the low-degree stratum, does a train-graph entity's IMPORTANCE (degree-orthogonalized sampled
  vertex betweenness = value-of-information / downstream-reach) predict test_query_count (tqc = held-out
  test-positive appearances), DEGREE-NEUTRAL WITHIN the stratum (control residual within-stratum degree)?
    PART A  WITHIN-STRATUM PARTIAL CORR: partial rank-corr(importance, tqc | [log_deg, log_inc]) computed
            ONLY over stratum entities -> the residual within-stratum degree/incidence is controlled.
            PRIMARY decision scalar.
    PART B  EXACT-DEGREE-MATCHED TERTILE GAP: within each EXACT within-stratum degree value (deg==11,
            deg==12, ... groups of >= MIN_DEG_GROUP entities), top-vs-bottom within-stratum-re-
            orthogonalized-importance tertile test-appearance-rate gap; size-weighted mean across degree
            groups. Exact-degree matching = perfect within-stratum degree neutralization.
    PART C  ARTIFACT REPRODUCTION (diagnostic): the RAW non-degree-matched within-stratum tertile gap
            using the GLOBALLY-orthogonalized importance (reproduces the reported +0.335) shown alongside
            the degree-neutralized PART A/B -> makes the collapse (or survival) explicit.

ARMS: importance (within-stratum re-orthogonalized betweenness) vs within-stratum-degree-matched-scramble
  control (permute importance WITHIN each exact-degree group -> destroys importance<->target pairing,
  preserves degree-conditional distribution; must collapse to ~0) vs full-random null (must collapse ~0).

INFO-CEILING GATE (FIRST, MANDATORY): within the low-degree stratum the target must be non-vacuous --
  (a) stratum test-appearance rate strictly inside (CEIL_APPEAR_LO, CEIL_APPEAR_HI); (b) stratum tqc has
  non-zero variance; (c) the stratum is big enough (n_stratum >= MIN_STRATUM_N); (d) within-stratum degree
  RESOLVES tqc at all (|spearman(log_deg, tqc)| >= CEIL_DEG_PREDICTS_MIN, sign-agnostic -- degree carries
  target-relevant structure within the stratum, so the degree-neutral test is meaningful). If any fails ->
  VACUOUS.

PRE-REG BANDS (fixed a-priori; see preregs/2026-07-16_importance_retrieval_low_degree_stratum_degree_neutral.md).
  pc = within-stratum partial rank-corr(importance, tqc | [log_deg, log_inc]) (PRIMARY);
  tert = exact-degree-matched top-vs-bottom-importance tertile appearance-rate gap.
  HARD_PASS : info-ceiling PASS AND pc >= PC_HP AND tert >= TERT_HP AND pc_boot_p05 > 0 AND
              tert_boot_p05 > 0 AND both degree-matched-scramble AND random controls near-zero ->
              importance's CORRECT function = a STRATIFIED periphery-retrieval signal; the pooled fail was
              a wrong-calc / Simpson's-paradox artifact and the +0.335 SURVIVES degree-neutralization.
  HARD_FAIL : info-ceiling PASS AND NOT hard_pass AND (pc < PC_HF OR tert < TERT_HF) -> the +0.335 is a
              within-stratum residual-degree artifact / does not survive degree-neutralization ->
              importance is genuinely LOW-VALUE for our substrate (order FAILED, pooled-retrieval FAILED,
              stratified-retrieval FAILED). HONEST + FINAL: the SEPARABILITY finding still stands as a real
              measured quantity; what closes is any predictive value for retrieval-priority beyond
              popularity. Do NOT manufacture a role.
  MIDDLE    : info-ceiling PASS AND real-but-modest (pc / tert between the FAIL and PASS floors, controls
              clean) -> importance carries a weak within-stratum periphery signal; route to a heavier
              bounded-width variant before any capability claim.
  BLOCK_BROKEN_DEGREE_CONTROL : the degree-matched-scramble null is NOT near-zero (exact-degree grouping
              leaks) -> cannot trust PART B.
  VACUOUS_METRIC : info-ceiling FAIL (target cannot be interpreted within the stratum).
  HARD_FAIL_STRATUM_TOO_SMALL : n_stratum < MIN_STRATUM_N (a sub-case of VACUOUS; too little data to be
              real, not noise) -> reported distinctly.

Determinism: numpy default_rng(fixed int seeds); NO hash()-derived seeds; sorted() for set ops.
ASCII-only. No emojis. Local CPU single-shot run-to-completion (NOT a queue dispatch), so runner
start_marker/heartbeat/run_mode gates do not apply; atomic tmp+os.replace metrics write, no bare except,
SystemExit-first ordering, arms-differ check present. No queue/GPU/atoms/push.

CELL-TEMPLATE compliance (single-shot local, no queue):
- arms_differ_verified: importance vs scramble vs random importance vectors hashed distinct (META_RULE_AF).
- final_metrics_atomicity: tmp_replace (os.replace) (META_RULE_AH).
- except SystemExit: raise BEFORE except Exception (no BaseException).
- crlb_n/a: signal is a rank partial-correlation over a parameter-free structural score; no noise-floor.
- baseline_in_band (META_RULE_AG analog): info-ceiling verifies stratum appearance rate in band, degree
  resolves target, stratum big enough -> the discriminator can fire.
- discriminator-fires: the degree-matched-scramble null MUST return ~0 (BLOCK if it leaks) AND the exact-
  degree tertile groups must be populated (>= MIN_DEG_GROUP) -> the degree-neutral test actually fires.
- calibration_check: default_ok_for_this_regime -- thresholds pre-registered; target is a raw held-out
  count; no primitive-default inheritance.
- all reported numbers MEASURED@ this cell's metrics.json.
"""

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from collections import defaultdict, deque
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "importance_retrieval_low_degree_stratum_degree_neutral_real_codex_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

# Reuse the already-built, already-validated primitives (DRY; no re-derivation).
from experiments.exp_importance_downstream_reach_ingest_prioritization_real_codex_v1 import (  # noqa: E402
    read_triples, spearman, rankdata_avg, build_adj_list,
)
from experiments.exp_importance_retrieval_relevance_query_centrality_real_codex_v1 import (  # noqa: E402
    load_entities_and_targets, sampled_node_betweenness, ols_resid, entity_degree_bins,
    partial_spearman, N_BTWN_SOURCES_FULL, N_BTWN_SOURCES_SMOKE, BTWN_SEED,
)

# ---- fixed config (a-priori) ----
N_DEG_BINS = 4                 # PRIMARY stratum = bin0 of the pre-existing lowest-quartile scheme
MIN_STRATUM_N = 100            # stratum must have >= this many entities to be real, not noise
MIN_DEG_GROUP = 12             # an exact-degree group must have >= this many entities for a tertile
N_BOOT = 600
BOOT_LO_PCT = 5.0
BOOT_SEED = 909
SCRAMBLE_SEEDS = [7, 17, 29]   # degree-matched-scramble null (permute within exact-degree group)
RANDOM_SEEDS = [11, 23, 37]    # full-shuffle null
ALT_CUTOFFS = [3, 5]           # robustness: lowest bin of N_DEG_BINS in {3,5} (tertile, quintile)

# ---- pre-reg thresholds (FIXED a-priori) ----
CEIL_APPEAR_LO = 0.05
CEIL_APPEAR_HI = 0.98
CEIL_DEG_PREDICTS_MIN = 0.10   # |spearman(log_deg, tqc)| within stratum floor (sign-agnostic)

PC_HP = 0.15                   # within-stratum partial rank-corr HARD_PASS floor
PC_HF = 0.05                   # below -> within-stratum retrieval signal is popularity/degree in disguise
TERT_HP = 0.15                 # exact-degree-matched tertile appearance-gap HARD_PASS floor (15 pp)
TERT_HF = 0.05                 # below -> degree-matched arms show no separation
NEUTRAL_CTRL_MAX = 0.05        # degree-matched-scramble + random nulls must stay below this


def _digest(a):
    return hashlib.sha256(np.ascontiguousarray(a, dtype=np.float64).tobytes()).hexdigest()


def exact_degree_matched_gap(imp, tqc, deg, min_group=MIN_DEG_GROUP):
    """Within each EXACT degree value with >= min_group entities: top-importance-tertile minus
    bottom-importance-tertile test-appearance rate; size-weighted mean across degree groups.
    Exact-degree matching -> the top/bottom tertiles share an IDENTICAL degree -> perfect within-
    stratum degree neutralization. Returns (gap, per_group, n_groups_fired, n_entities_used)."""
    appear = (np.asarray(tqc) > 0).astype(np.float64)
    imp = np.asarray(imp, dtype=np.float64)
    deg = np.asarray(deg)
    num = 0.0; den = 0.0; per = {}; n_used = 0
    for dv in sorted(set(int(x) for x in deg.tolist())):
        gi = np.where(deg == dv)[0]
        if len(gi) < min_group:
            continue
        order = gi[np.argsort(imp[gi], kind="mergesort")]
        tert = len(order) // 3
        if tert < 1:
            continue
        bottom = order[:tert]; top = order[-tert:]
        top_rate = float(appear[top].mean()); bot_rate = float(appear[bottom].mean())
        gap = top_rate - bot_rate
        w = len(top) + len(bottom)
        num += gap * w; den += w; n_used += w
        per[int(dv)] = {"gap": gap, "n_group": int(len(gi)), "tert": int(tert),
                        "top_rate": top_rate, "bottom_rate": bot_rate}
    return (num / den if den > 0 else 0.0), per, int(len(per)), n_used


def scramble_within_degree(imp, deg, seed):
    """Permute importance WITHIN each exact-degree group (preserves degree-conditional importance
    distribution, destroys entity-level importance<->target pairing). The strict degree-matched null."""
    rng = np.random.default_rng(seed)
    out = np.asarray(imp, dtype=np.float64).copy()
    buckets = defaultdict(list)
    for i in range(len(deg)):
        buckets[int(deg[i])].append(i)
    for dv in sorted(buckets):
        idxs = buckets[dv]
        vals = out[idxs].copy()
        perm = rng.permutation(len(idxs))
        for k in range(len(idxs)):
            out[idxs[k]] = vals[perm[k]]
    return out


def stratum_indices(deg, n_bins):
    """Lowest-degree bin (bin 0) of the pre-existing quantile-of-log1p(degree) scheme. Principled cutoff
    (lowest 1/n_bins of connected entities by degree), NOT tuned-to-pass; identical to the parent cell's
    bin0 at n_bins=4 (where the +0.335 lives)."""
    dbin = entity_degree_bins(deg, n_bins)
    return np.where(dbin == 0)[0]


def analyze_stratum(bc, deg, inc, tqc, idx, n_boot=N_BOOT):
    """All within-stratum degree-neutral metrics for the entity subset `idx`."""
    bc_s = bc[idx]; deg_s = deg[idx]
    log_deg = np.log1p(deg[idx].astype(np.float64))
    log_inc = np.log1p(inc[idx].astype(np.float64))
    tqc_s = tqc[idx].astype(np.float64)
    controls = [log_deg, log_inc]

    # within-stratum re-orthogonalized importance (degree+incidence removed WITHIN the stratum)
    imp_s = ols_resid(bc_s, [log_deg, log_inc])

    # info-ceiling (within stratum)
    appear_rate = float((tqc_s > 0).mean())
    tqc_std = float(tqc_s.std())
    deg_predicts = spearman(log_deg, tqc_s)                 # signed; may be negative (split structure)
    n_stratum = int(len(idx))
    info_ceiling_pass = (CEIL_APPEAR_LO < appear_rate < CEIL_APPEAR_HI
                         and tqc_std > 0.0 and n_stratum >= MIN_STRATUM_N
                         and abs(deg_predicts) >= CEIL_DEG_PREDICTS_MIN)

    # PART A: within-stratum partial corr (PRIMARY, degree-neutral). Feed RAW bc; partial corr controls
    # log_deg/log_inc regardless of pre-orthogonalization (rank-partial-corr is invariant to adding a
    # monotone function of the controls to the predictor) -> reported on raw bc for transparency.
    pc = partial_spearman(bc_s, tqc_s, controls)

    # PART B: exact-degree-matched tertile gap (on within-stratum re-orthogonalized importance)
    tert, tert_per_group, n_groups, n_used = exact_degree_matched_gap(imp_s, tqc[idx], deg_s)

    # PART C: artifact-reproduction -- RAW non-degree-matched within-stratum tertile using the GLOBALLY-
    # orthogonalized importance (imp passed in via bc already global; here re-derive the parent's variant).
    # (computed by caller w/ global orth; here we also give the naive within-stratum tertile of imp_s.)
    appear = (tqc[idx] > 0).astype(np.float64)
    order = np.argsort(imp_s, kind="mergesort")
    t = len(order) // 3
    naive_gap = float(appear[order[-t:]].mean() - appear[order[:t]].mean()) if t >= 1 else 0.0

    # controls
    scr = [scramble_within_degree(imp_s, deg_s, s) for s in SCRAMBLE_SEEDS]
    pc_scramble = float(np.mean([abs(partial_spearman(si, tqc_s, controls)) for si in scr]))
    tert_scramble = float(np.mean([abs(exact_degree_matched_gap(si, tqc[idx], deg_s)[0]) for si in scr]))
    rnd = [np.random.default_rng(s).permutation(imp_s) for s in RANDOM_SEEDS]
    pc_random = float(np.mean([abs(partial_spearman(ri, tqc_s, controls)) for ri in rnd]))
    tert_random = float(np.mean([abs(exact_degree_matched_gap(ri, tqc[idx], deg_s)[0]) for ri in rnd]))

    # bootstrap over stratum entities (p05 of pc and tert)
    rng = np.random.default_rng(BOOT_SEED)
    boot_pc = []; boot_tert = []
    for _b in range(n_boot):
        bi = rng.integers(0, n_stratum, size=n_stratum)
        boot_pc.append(partial_spearman(bc_s[bi], tqc_s[bi], [log_deg[bi], log_inc[bi]]))
        boot_tert.append(exact_degree_matched_gap(imp_s[bi], tqc[idx][bi], deg_s[bi])[0])
    pc_p05 = float(np.percentile(boot_pc, BOOT_LO_PCT))
    tert_p05 = float(np.percentile(boot_tert, BOOT_LO_PCT))

    return {
        "n_stratum": n_stratum,
        "deg_min": int(deg_s.min()), "deg_max": int(deg_s.max()), "deg_mean": float(deg_s.mean()),
        "info_ceiling": {
            "test_appearance_rate": appear_rate, "tqc_std": tqc_std,
            "deg_predicts_tqc_spearman": deg_predicts, "n_stratum": n_stratum,
            "info_ceiling_pass": bool(info_ceiling_pass),
        },
        "partA_within_stratum_partial_corr": {
            "pc": pc, "pc_boot_p05": pc_p05, "bands": {"PC_HF": PC_HF, "PC_HP": PC_HP},
        },
        "partB_exact_degree_matched_tertile": {
            "tert": tert, "tert_boot_p05": tert_p05, "n_degree_groups_fired": n_groups,
            "n_entities_used": n_used, "tert_per_group": tert_per_group,
            "bands": {"TERT_HF": TERT_HF, "TERT_HP": TERT_HP},
        },
        "partC_artifact_repro": {
            "naive_within_stratum_gap_reorth": naive_gap,
            "note": "PART C global-orth naive gap reported by caller vs degree-matched PART B",
        },
        "controls": {
            "pc_scramble": pc_scramble, "tert_scramble": tert_scramble,
            "pc_random": pc_random, "tert_random": tert_random,
            "control_near_zero": bool(pc_scramble < NEUTRAL_CTRL_MAX and tert_scramble < NEUTRAL_CTRL_MAX
                                      and pc_random < NEUTRAL_CTRL_MAX and tert_random < NEUTRAL_CTRL_MAX),
            "NEUTRAL_CTRL_MAX": NEUTRAL_CTRL_MAX,
        },
        "_imp_s": imp_s, "_scr0": scr[0], "_rnd0": rnd[0],
    }


def run(d, scale):
    t0 = time.time()
    n_ent = d["n_ent"]; train_int = d["train_int"]
    deg = d["deg"]; inc = d["inc"]; tqc = d["tqc"]
    n_btwn = N_BTWN_SOURCES_SMOKE if scale == "smoke" else N_BTWN_SOURCES_FULL

    log_deg = np.log1p(deg.astype(np.float64))

    adj, _edge_id = build_adj_list(train_int, n_ent)
    print("[imp] sampled vertex betweenness: n_sources=%d n_ent=%d ..." % (n_btwn, n_ent), flush=True)
    tb = time.time()
    bc, used_sources = sampled_node_betweenness(adj, n_ent, n_btwn, BTWN_SEED)
    print("[imp] node betweenness done in %.1fs (sources=%d)" % (time.time() - tb, used_sources), flush=True)

    # GLOBAL degree-orthogonalized importance (the parent cell's PRIMARY variant), for PART C reproduction
    imp_btwn_orth_global = ols_resid(bc, [log_deg])

    # PRIMARY stratum = lowest-degree quartile (bin0, n_bins=4)
    idx = stratum_indices(deg, N_DEG_BINS)
    A = analyze_stratum(bc, deg, inc, tqc, idx)

    # PART C: reproduce the reported +0.335 -- raw non-degree-matched within-stratum tertile on the
    # GLOBALLY-orthogonalized importance (identical construction to the parent cell's bin0 gap).
    appear = (tqc[idx] > 0).astype(np.float64)
    order = np.argsort(imp_btwn_orth_global[idx], kind="mergesort")
    t = len(order) // 3
    raw_global_gap = float(appear[order[-t:]].mean() - appear[order[:t]].mean()) if t >= 1 else 0.0

    # robustness: alternative principled cutoffs (lowest bin of n_bins in {3,5})
    alt = {}
    for nb in ALT_CUTOFFS:
        ai = stratum_indices(deg, nb)
        if len(ai) >= MIN_STRATUM_N:
            aa = analyze_stratum(bc, deg, inc, tqc, ai, n_boot=200)
            alt["n_bins_%d_bin0" % nb] = {
                "n_stratum": aa["n_stratum"], "deg_range": [aa["deg_min"], aa["deg_max"]],
                "pc": aa["partA_within_stratum_partial_corr"]["pc"],
                "pc_p05": aa["partA_within_stratum_partial_corr"]["pc_boot_p05"],
                "tert": aa["partB_exact_degree_matched_tertile"]["tert"],
                "tert_p05": aa["partB_exact_degree_matched_tertile"]["tert_boot_p05"],
                "info_ceiling_pass": aa["info_ceiling"]["info_ceiling_pass"],
            }
        else:
            alt["n_bins_%d_bin0" % nb] = {"n_stratum": int(len(ai)), "too_small": True}

    # ---- arms-differ (META_RULE_AF) ----
    digests = {"imp_s": _digest(A["_imp_s"]), "scramble0": _digest(A["_scr0"]),
               "random0": _digest(A["_rnd0"])}
    arms_differ = len(set(digests.values())) == len(digests)

    # ---- verdict ----
    icp = A["info_ceiling"]["info_ceiling_pass"]
    pc = A["partA_within_stratum_partial_corr"]["pc"]
    pc_p05 = A["partA_within_stratum_partial_corr"]["pc_boot_p05"]
    tert = A["partB_exact_degree_matched_tertile"]["tert"]
    tert_p05 = A["partB_exact_degree_matched_tertile"]["tert_boot_p05"]
    ctrl_near0 = A["controls"]["control_near_zero"]
    n_stratum = A["n_stratum"]

    hard_pass = (icp and pc >= PC_HP and tert >= TERT_HP and pc_p05 > 0.0 and tert_p05 > 0.0
                 and ctrl_near0)
    if n_stratum < MIN_STRATUM_N:
        verdict = "HARD_FAIL_STRATUM_TOO_SMALL"
    elif not icp:
        verdict = "VACUOUS_METRIC_INFO_CEILING_FAIL"
    elif not arms_differ:
        verdict = "BLOCK_ARMS_IDENTICAL"
    elif not ctrl_near0:
        verdict = "BLOCK_BROKEN_DEGREE_CONTROL"
    elif hard_pass:
        verdict = "HARD_PASS_IMPORTANCE_STRATIFIED_PERIPHERY_RETRIEVAL_SIGNAL"
    elif pc < PC_HF or tert < TERT_HF:
        verdict = "HARD_FAIL_IMPORTANCE_LOW_VALUE_PLUS0335_IS_WITHIN_STRATUM_DEGREE_ARTIFACT"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.time() - t0
    out = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "run_mode": scale,
        "scale": scale,
        "dataset": "codex_claimvalidity",
        "elapsed_s": elapsed,
        "n_ent": n_ent, "n_train": int(train_int.shape[0]), "n_test_pos": d["n_test_pos"],
        "stratum_def": "lowest-degree quartile (bin0 of log1p(deg) quantiles, n_bins=%d)" % N_DEG_BINS,
        "n_stratum": n_stratum, "stratum_deg_range": [A["deg_min"], A["deg_max"]],
        "info_ceiling": A["info_ceiling"],
        "partA_within_stratum_partial_corr": A["partA_within_stratum_partial_corr"],
        "partB_exact_degree_matched_tertile": A["partB_exact_degree_matched_tertile"],
        "partC_artifact_reproduction": {
            "raw_global_orth_within_stratum_gap": raw_global_gap,
            "reorth_within_stratum_naive_gap": A["partC_artifact_repro"]["naive_within_stratum_gap_reorth"],
            "degree_matched_gap_partB": tert,
            "note": ("raw_global_orth_within_stratum_gap reproduces the reported +0.335; PART B is the "
                     "same top-vs-bottom-importance comparison but EXACT-degree-matched WITHIN the stratum "
                     "-> the delta is the residual-degree artifact removed"),
        },
        "controls": {k: v for k, v in A["controls"].items()},
        "robustness_alt_cutoffs": alt,
        "config": {
            "n_btwn_sources": used_sources, "n_deg_bins": N_DEG_BINS, "min_stratum_n": MIN_STRATUM_N,
            "min_deg_group": MIN_DEG_GROUP, "n_boot": N_BOOT, "scramble_seeds": SCRAMBLE_SEEDS,
            "random_seeds": RANDOM_SEEDS,
            "bands": {"PC_HP": PC_HP, "PC_HF": PC_HF, "TERT_HP": TERT_HP, "TERT_HF": TERT_HF,
                      "NEUTRAL_CTRL_MAX": NEUTRAL_CTRL_MAX, "CEIL_DEG_PREDICTS_MIN": CEIL_DEG_PREDICTS_MIN},
        },
        "arm_digests": digests, "arms_differ": bool(arms_differ),
        "verdict_msg": (
            "%s | stratum=bin0(deg %d-%d, n=%d) | A[degree-neutral] pc=%.4f (p05=%+.4f) | "
            "B[exact-deg-matched] tert=%.4f (p05=%+.4f, %d deg-groups) | "
            "C[artifact] raw_global_gap=%.4f -> deg_matched=%.4f | "
            "ctrl(scr pc=%.4f tert=%.4f; rnd pc=%.4f tert=%.4f near0=%s) | "
            "info_ceiling(appear=%.3f deg_predicts=%+.3f pass=%s)" % (
                verdict, A["deg_min"], A["deg_max"], n_stratum, pc, pc_p05,
                tert, tert_p05, A["partB_exact_degree_matched_tertile"]["n_degree_groups_fired"],
                raw_global_gap, tert, A["controls"]["pc_scramble"], A["controls"]["tert_scramble"],
                A["controls"]["pc_random"], A["controls"]["tert_random"], ctrl_near0,
                A["info_ceiling"]["test_appearance_rate"], A["info_ceiling"]["deg_predicts_tqc_spearman"],
                icp)),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    out["summary"] = verdict
    return out


def write_metrics(out):
    out_dir = os.path.join(REPO, "data", "exp_%s" % ANCHOR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    clean = {k: v for k, v in out.items() if not k.startswith("_")}
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2)
    os.replace(tmp, final)
    return final


def self_test():
    # (A) exact-degree-matched gap FIRES on a within-degree-planted signal and the scramble null collapses.
    rng = np.random.default_rng(0)
    n = 900
    deg = rng.integers(11, 16, size=n)                       # exact-degree groups 11..15
    imp = rng.normal(size=n)
    # plant: WITHIN every degree value, high importance -> appears in test (tqc>0) more often
    p = 1.0 / (1.0 + np.exp(-1.6 * imp))
    tqc = (rng.random(n) < p).astype(np.int64)
    gap, per, ng, nu = exact_degree_matched_gap(imp, tqc, deg)
    assert ng >= 3 and gap > 0.12, "exact-degree gap must fire on planted within-degree signal (gap=%.3f groups=%d)" % (gap, ng)
    scr = scramble_within_degree(imp, deg, 7)
    gap_scr, _p, _g, _u = exact_degree_matched_gap(scr, tqc, deg)
    assert abs(gap_scr) < gap, "degree-matched scramble null must collapse below the true gap (scr=%.3f true=%.3f)" % (gap_scr, gap)

    # (B) DEGREE-ARTIFACT CATCH: a signal that is a PURE function of degree, where degree drives tqc, must
    #     produce a LARGE naive (non-matched) gap but ~0 EXACT-degree-matched gap (the artifact is removed).
    deg2 = rng.integers(11, 16, size=n)
    imp_degonly = deg2.astype(np.float64) + 0.001 * rng.normal(size=n)   # importance == degree (+ tiny jitter)
    tqc2 = (deg2 >= 14).astype(np.int64)                                  # target driven purely by degree
    # naive: sort all by imp_degonly, top vs bottom tertile
    appear = (tqc2 > 0).astype(np.float64)
    order = np.argsort(imp_degonly, kind="mergesort"); tt = len(order) // 3
    naive = float(appear[order[-tt:]].mean() - appear[order[:tt]].mean())
    matched, _p2, _g2, _u2 = exact_degree_matched_gap(imp_degonly, tqc2, deg2)
    assert naive > 0.5, "degree-artifact self-test: naive gap must be large (got %.3f)" % naive
    assert abs(matched) < 0.05, "degree-artifact self-test: EXACT-degree-matched gap must remove the artifact (got %.3f)" % matched

    # (C) partial corr recovers signal-beyond-controls and ~0 for a pure function of them.
    m = 700
    c1 = rng.normal(size=m); c2 = rng.normal(size=m); extra = rng.normal(size=m)
    pred = c1 + 0.5 * c2 + 0.9 * extra
    tgt = 0.8 * extra + 0.2 * rng.normal(size=m)
    pc = partial_spearman(pred, tgt, [c1, c2])
    assert pc > 0.20, "partial corr must recover signal beyond controls (got %.3f)" % pc
    pc0 = partial_spearman(2.0 * c1 - c2, tgt, [c1, c2])
    assert abs(pc0) < 0.10, "partial corr of a pure-control predictor must be ~0 (got %.3f)" % pc0

    # (D) REAL code path + REAL info-ceiling on CoDEx at the FULL entity index (fast). Exercises the ACTUAL
    #     loader + node-betweenness + stratum extraction the FULL run uses, at a tiny betweenness sample,
    #     and asserts the low-degree stratum target is non-vacuous and the stratum is real (not tiny).
    d = load_entities_and_targets("codex_claimvalidity")
    assert d["n_ent"] == 2034, "expected CoDEx n_ent=2034, got %d" % d["n_ent"]
    idx = stratum_indices(d["deg"], N_DEG_BINS)
    assert len(idx) >= MIN_STRATUM_N, "low-degree stratum must be >= MIN_STRATUM_N (got %d)" % len(idx)
    tqc_s = d["tqc"][idx].astype(np.float64)
    appear_s = float((tqc_s > 0).mean())
    assert CEIL_APPEAR_LO < appear_s < CEIL_APPEAR_HI, \
        "info-ceiling: stratum appearance rate %.3f must be in band" % appear_s
    dsub = d["deg"][idx]
    # exact-degree groups must be populous enough to matched-tertile within the real stratum
    grp_ok = sum(1 for dv in sorted(set(dsub.tolist())) if int((dsub == dv).sum()) >= MIN_DEG_GROUP)
    assert grp_ok >= 2, "real stratum must have >= 2 populous exact-degree groups (got %d)" % grp_ok
    adj_r, _e = build_adj_list(d["train_int"], d["n_ent"])
    bc_r, used = sampled_node_betweenness(adj_r, d["n_ent"], 8, BTWN_SEED)   # tiny sample: real path only
    assert used == 8 and bc_r.sum() > 0.0, "real node-betweenness path must run and produce nonzero mass"
    print("[SELF-TEST] PASS  exact_deg_gap_fires | scramble_collapses | degree_artifact_caught | "
          "partial_corr_ok | REAL stratum(n=%d deg %d-%d appear=%.3f groups_ok=%d) real_btwn(sources=%d)" % (
              len(idx), int(dsub.min()), int(dsub.max()), appear_s, grp_ok, used))
    return True


def main(scale="full"):
    d = load_entities_and_targets("codex_claimvalidity")
    print("[load] scale=%s n_ent=%d n_train=%d n_test_pos=%d" % (
        scale, d["n_ent"], d["train_int"].shape[0], d["n_test_pos"]), flush=True)
    out = run(d, scale)
    final = write_metrics(out)
    print("[VERDICT] %s" % out["verdict"])
    ic = out["info_ceiling"]
    print("  STRATUM: %s | n=%d deg %s | appear=%.3f deg_predicts=%+.3f pass=%s" % (
        out["stratum_def"], out["n_stratum"], out["stratum_deg_range"],
        ic["test_appearance_rate"], ic["deg_predicts_tqc_spearman"], ic["info_ceiling_pass"]))
    a = out["partA_within_stratum_partial_corr"]
    print("  PART A DEGREE-NEUTRAL partial_corr: pc=%.4f (boot_p05=%+.4f) [PC_HF=%.2f PC_HP=%.2f]" % (
        a["pc"], a["pc_boot_p05"], PC_HF, PC_HP))
    b = out["partB_exact_degree_matched_tertile"]
    print("  PART B EXACT-DEG-MATCHED tertile: tert=%.4f (boot_p05=%+.4f, %d deg-groups, n_used=%d)" % (
        b["tert"], b["tert_boot_p05"], b["n_degree_groups_fired"], b["n_entities_used"]))
    c = out["partC_artifact_reproduction"]
    print("  PART C ARTIFACT: raw_global_within_stratum_gap=%.4f -> degree_matched=%.4f (delta removed)" % (
        c["raw_global_orth_within_stratum_gap"], c["degree_matched_gap_partB"]))
    ct = out["controls"]
    print("  CONTROLS: scramble(pc=%.4f tert=%.4f) random(pc=%.4f tert=%.4f) near0=%s" % (
        ct["pc_scramble"], ct["tert_scramble"], ct["pc_random"], ct["tert_random"], ct["control_near_zero"]))
    print("  ROBUSTNESS alt cutoffs:", json.dumps(out["robustness_alt_cutoffs"]))
    print("  elapsed=%.1fs metrics -> %s" % (out["elapsed_s"], final))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    try:
        if args.self_test:
            self_test()
        else:
            main(scale="smoke" if args.smoke else "full")
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        sys.stderr.write("[CELL_CRASHED] %s: %s\n%s\n" % (type(e).__name__, e, traceback.format_exc()))
        raise
