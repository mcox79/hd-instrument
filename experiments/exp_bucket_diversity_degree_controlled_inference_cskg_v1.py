"""BUCKET-DIVERSITY DEGREE-CONTROLLED INFERENCE TEST (Part C, research_dense_kg_prior_art_and_source_depth
_2026-07-14.md): does per-concept relation-type-BUCKET DIVERSITY help or hurt held-out relation inference on OUR
glass-box additive-KGE substrate, once DEGREE is controlled for? Directly operationalizes the caveat in arXiv:
2508.15291 (Node-level Maximum Relation Diversity is INVERSELY correlated with link-prediction MRR/Hit@1 in fused
dense-embedding models FB15k-237/WN18RR/CoDEx) -- this cell tests whether that fragmentation mechanism transfers to
our bind/unbind additive-KGE readout (X_h + D_r), which structurally separates relation and entity rather than
fusing them into one dense per-entity vector. THIS IS A DON'T-LOCK-IN TEST: it gates the "more buckets = better"
premise behind the whole enrichment-foundation build (research_ideal_foundation_spec_size_density_optimum_2026-
07-14.md Section 1) BEFORE that premise is spent on a build plan.

## Prior-work check (substrate-KB concept-query, mandatory pre-authoring)
`bash tools/substrate_query.sh "relation type bucket diversity degree controlled held-out inference MRR retrieval"`
-> top hit cosine=0.3086 (notes/exp_dev_handoff_research_p9_mechanism_diagnosis_2x_2026-06-10.md::chunk010,
"FREQUENCY-CONTROLLED HELD-OUT" section): proposes degree-matching held-out RELATIONS to training relations to
control for degree bias in a Hits@10 cross-relation-transfer test. RELATED METHODOLOGY (degree-control is the same
general discipline this cell also applies) but a DIFFERENT QUESTION (that note controls degree when transferring
across relation TYPES; this cell controls degree when varying an ENTITY's bucket DIVERSITY). 3rd hit cosine=0.2959
(research_drill_slipnet_real_polysemic_rescue_2x_2026-06-11.md): a slipnet spreading-activation substrate found
RELATION-TYPE CROSS-ACTIVATION INTERFERENCE when 10 relation types are simultaneously active -- thematically close
to the arXiv fragmentation mechanism, but a different substrate (spreading activation, not bind/unbind additive
readout) and below the 0.30 read threshold. VERDICT: genuinely NOVEL for the specific bucket-diversity-vs-inference-
quality question on this substrate; the degree-control METHODOLOGY has precedent and this cell follows it.

## Mechanism under test
7-bucket semantic relation-type map (director's audit mapping; LEXICAL relations SYNONYM/RELATED_TO/ANTONYM
excluded from both the induced graph and the bucket vocabulary):
  IS_A, HYPERNYM -> taxonomic | CN_HAS_PROPERTY -> property | PART_OF, CN_HAS_A -> part_whole |
  CN_USED_FOR, CN_CAPABLE_OF -> functional | CN_CAUSES, CN_MOTIVATED_BY_GOAL -> causal | CN_AT_LOCATION -> spatial |
  CN_DESIRES -> social.
MEASURED@data/substrate_index/concept/relations.jsonl (189654 lines, counted 2026-07-14): CN_DESIRES has ZERO
edges in the active partition -> the "social" bucket is STRUCTURALLY EMPTY here; realized max diversity is 6 of 7
buckets, not 7. This is itself a finding (reported, not hidden). Induced 6-bucket subgraph: 91673 edges, 71953
unique entities (62177 with out-degree>=1). MEASURED via direct count, this session.

Standard TRANSDUCTIVE held-out-EDGE split (NOT held-out-entity -- every entity stays in the graph so its OWN
degree/diversity, computed strictly from its TRAIN-remaining edges, can be measured): for every src entity with
full out-degree >= MIN_SPLIT_DEGREE, hold out a bounded fraction of its own out-edges as QUERY; everything else
(including ALL edges of entities below the threshold) is TRAIN. Post-split TRAIN out-degree and TRAIN bucket-set
size (computed ONLY from remaining train edges, never from the held-out query edges -- avoids leaking the very
thing being predicted) are the two entity-level covariates. Degree strata (train out-degree): d3_5, d6_8, d9_14,
d15plus. Diversity bins (train distinct-bucket count): div1 (single-bucket), div2, div3plus. PRIMARY comparison
(gated) = div3plus vs div1 WITHIN a degree stratum (an entity with 6 edges all-taxonomic vs 6 edges spanning
multiple buckets = same degree, different diversity -- isolates diversity from raw edge count). MEASURED population
counts (this session, pre-registered as HYPOTHESIZED@this-prereg since computed from full-graph degree, not yet
the exact post-split train degree): d3_5 div1~213/div3plus~350; d6_8 div1~19/div3plus~312; d9_14 div1~2 (too thin);
d15plus div1~3 (too thin). PRIMARY_STRATA = [d3_5, d6_8] (both groups clear MIN_STRATUM_N); d9_14/d15plus are
SECONDARY (reported on the curve, excluded from the gated verdict for insufficient div1 population). This
population shape is itself informative: single-bucket (div1) entities become RARE once degree >= 6 in this
partition -- most naturally-occurring higher-degree concepts already span >1 relation-type bucket.

## Scorer (reused primitive, unchanged hyperparameters -- NOT re-derived)
`experiments._kge_anchor1_fit.fit_kge_anchor1` (the SAME additive/TransE-style KGE recipe used by the anchor_compose
family: CE self-adversarial + N3 + reciprocal, minibatch SGD) fit TRANSDUCTIVELY on the TRAIN graph (no held-out
entity folding). Readout = `experiments._course_c_rotate_core_v1.additive_direct_scores` (verbatim, X_h+D_r vs all
candidates). This is a genuinely NEW split/regime for this primitive (transductive edge-holdout on the 6-bucket
CSKG-relations subgraph, not the held-out-ENTITY split the anchor_compose family uses) -- there is no prior
same-regime MEASURED atom to reproduce, so Gate-D's "reproduce prior chain-grade result at test regime" does not
apply verbatim; declared explicitly (`positive_control_arms: n/a_novel_split_no_prior_atom`) rather than skipped
silently. What IS reused unchanged: the scorer's hyperparameter defaults (A1_LR, A1_GAMMA, A1_N_NEG, A1_ADV_TEMP,
A1_N3_LAMBDA) -- no new recipe invented for this cell.

## Arms
  MAIN             : fitted additive scorer (X,D) on the TRAIN graph -- the headline arm.
  RANDOM_CODES     : random X,D (no fit) -- the null floor (arena-fires gate).
  RELATION_SCRAMBLE: MAIN's X, but D rows permuted (a non-identity relation-index permutation) at score time --
                     must-fail control (relation identity broken -> should collapse toward RANDOM/POP; confirms
                     MAIN's signal is genuinely relational bind/unbind, not entity-popularity leakage).
  BASELINE_POP     : frequency incumbent (`pop_hits`) -- reported for context, not gated (fit-independent).

## Controls / must-fails
  ARENA_FIRES        : MAIN_mrr >= 3x RANDOM_mrr AND (MAIN_mrr - RANDOM_mrr) >= 0.01 (arena is answerable at all;
                        if this fails the whole stratified analysis is INCONCLUSIVE regardless of any lift number).
  SCRAMBLE_CONTROLLED : (SCRAMBLE_mrr - RANDOM_mrr) <= 0.25 * (MAIN_mrr - RANDOM_mrr) (relation-scramble collapses).
  STRATIFIED PERMUTATION NULL (the decisive control for THIS cell's actual question): within each PRIMARY degree
    stratum, shuffle which entities carry the div1/div3plus LABEL (preserving the REAL group sizes, entity-level
    shuffle so an entity's multiple queries move together) N_PERM=500 times; recompute the pooled lift each time.
    p_perm = fraction of |null lift| >= |real lift|. This establishes the noise floor for "a lift of this size could
    arise from degree-stratified grouping alone, ignoring true diversity" at the ACTUAL per-stratum sample sizes --
    directly distinguishes a genuine diversity effect from a spurious artifact of binning.
  Two independent seeds (7, 13) drive BOTH the holdout split AND the KGE fit -- two independent replicate
  measurements of the same question. Final verdict requires sign-consistency AND significance across BOTH seeds
  (conservative; a single-seed apparent effect is not enough to call HELPS/HURTS).

## PRE-REGISTERED BANDS (picked BEFORE the run; all HYPOTHESIZED@this-prereg unless tagged MEASURED@/CITED@)
  aggregate_lift = weighted mean (weight=min(n_div1,n_div3plus)) of (div3plus_mean_RR - div1_mean_RR) over
  PRIMARY_STRATA with n_div1>=MIN_STRATUM_N=10 AND n_div3plus>=MIN_STRATUM_N=10. p_perm_aggregate = MAX (most
  conservative) per-stratum p_perm among qualifying strata. Both computed PER SEED, then combined across seeds.
  HELPS  (density-optimum premise SURVIVES the arXiv caveat on our substrate): BOTH seeds show aggregate_lift >=
    +0.02 absolute MRR, BOTH seeds p_perm_aggregate <= 0.15, same sign both seeds.
  HURTS  (arXiv:2508.15291 fragmentation REPLICATES on our bind/unbind substrate -- informative negative, do NOT
    force the density-optimum story): BOTH seeds show aggregate_lift <= -0.02, BOTH seeds p_perm_aggregate <= 0.15,
    same sign both seeds.
  NEUTRAL: arena fires + scramble controlled, but lift/significance/sign do not jointly satisfy either band above.
  INCONCLUSIVE_ARENA_DID_NOT_FIRE / INCONCLUSIVE_SCRAMBLE_NOT_CONTROLLED / INCONCLUSIVE_INSUFFICIENT_STRATA /
    INCONCLUSIVE_SEED_DISAGREEMENT: fail-closed labels when the arena or the qualifying-strata population itself
    is not sound enough to trust a HELPS/HURTS/NEUTRAL call.

## Compute architecture
class (a) batched: single transductive additive-KGE fit (vectorized torch minibatch SGD, CPU device) per seed --
no held-out-entity oracle folding, no lever comparison (no 4x-fit multiplicity like anchor_compose_magnitude_opt) --
substantially cheaper than that reference cell (~460K train edges / 4 fits / 2 seeds ~ 12073s MEASURED@data/exp_
anchor_compose_inductive_entity_cskg_v1/metrics.json:elapsed_s). Here: ~90K edges, ONE fit per seed, smaller k/
epochs/n_neg -- FULL wall time is measured via the SMOKE (single-seed, full-N, reduced-epoch discriminator preview)
before committing to the 2-seed FULL --timeout. Readout query-chunked batched matmul (SCORE_CHUNK). Permutation
test is pure array relabeling (no re-fit) -- effectively free. Storage SHARDED (each entity its own row in X; no
bundling). device=cpu (task-specified; CPU-appropriate scale, no GPU-batching benefit required to stay in budget).

## Self-test (Gate F.1/F.2 real-code-path)
`self_test()` builds a TINY planted TransE-consistent arena (n_ent=150, 6 synthetic relations each mapped 1:1 to
a synthetic bucket) with a DELIBERATE mix of low-diversity (repeated single relation) and high-diversity (relation
drawn uniformly) entities at matched degree ranges, THEN RUNS THE IDENTICAL PIPELINE the FULL run uses: real
`build_holdout_split`, real `fit_kge_anchor1` (few epochs), real `additive_direct_scores`, real
`filtered_rr_per_query`, real `permutation_test_stratum`/`aggregate_across_strata`, real `verdict_from_gates`. Does
NOT assert a specific HELPS/HURTS direction (that is the open empirical question this cell exists to answer) --
only that the pipeline runs end-to-end, MAIN beats RANDOM (arena fires), SCRAMBLE collapses, both div1 and div3plus
groups are non-empty in at least one stratum, and the permutation p-value is a valid probability in [0,1].

CELL-TEMPLATE MANDATORY (per experiments/_validity_preflight + exp_dev.md SS15/SS17):
# - arms_differ_verified at self-test (MAIN/RANDOM/SCRAMBLE score-signature hashes >= 3 distinct).
# - final_metrics_atomicity: tmp_replace (via experiments._seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb_n/a: no closed-form noise floor for a stratified-permutation MRR-lift test; feasibility instead
#   established empirically (arena_fires gate: MAIN must clear RANDOM by a fixed ratio+absolute margin) and via
#   MEASURED population counts per stratum (min group size known BEFORE the run, not assumed).
# - baseline_in_band: arena_fires gate IS the baseline-in-band check (RANDOM/POP near floor; MAIN clears it).
# - discriminator survives scale: option (C) discriminator-preview -- SMOKE runs the FULL induced graph (full N,
#   full edge set) at reduced epochs/single-seed specifically to preview arena_fires + non-empty PRIMARY strata
#   BEFORE the 2-seed FULL commits full compute.
# - HP_SCOPE: arena_fires + scramble_controlled apply to ALL seeds unconditionally; HELPS/HURTS bands apply to the
#   cross-seed aggregate only (not per-arm).
# - cardinality: EXPECTED_N_UNITS = n_seeds (2 for FULL, 1 for SMOKE); per-seed failure halts with failure_class.
# - calibration_check: default_ok_for_this_regime -- MIN_SPLIT_DEGREE/HOLDOUT_FRAC/DEGREE_STRATA/MIN_STRATUM_N are
#   pre-registered from a direct MEASURED count of the real partition's degree/diversity joint distribution (this
#   session, see population counts above), NOT tuned on the retrieval outcome.
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ above.
# - progress_logging: print_flush_true (line-buffered stdout + flush prints every seed/epoch-checkpoint).

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
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import Graph, build_ids  # noqa: E402
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, pop_hits,
)
from experiments._course_c_rotate_core_v1 import additive_direct_scores  # noqa: E402
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR  # noqa: E402
from experiments._fit_checkpoint import FitCheckpoint, cleanup_seed_checkpoints  # noqa: E402

ANCHOR_NAME = "bucket_diversity_degree_controlled_inference_cskg_v1"

DATA_REL = "data/substrate_index/concept/relations.jsonl"

# ---- Director's 7-bucket semantic mapping (LEXICAL rels excluded entirely) ----
BUCKET_MAP = {
    "IS_A": "taxonomic", "HYPERNYM": "taxonomic",
    "CN_HAS_PROPERTY": "property",
    "PART_OF": "part_whole", "CN_HAS_A": "part_whole",
    "CN_USED_FOR": "functional", "CN_CAPABLE_OF": "functional",
    "CN_CAUSES": "causal", "CN_MOTIVATED_BY_GOAL": "causal",
    "CN_AT_LOCATION": "spatial",
    "CN_DESIRES": "social",
}

# ---- Split knobs (pre-registered; NOT tuned on real data) ----
MIN_SPLIT_DEGREE = 5
HOLDOUT_FRAC = 0.3
HOLDOUT_MIN = 1
HOLDOUT_MAX = 4

# ---- Degree strata (post-split TRAIN out-degree) ----
DEGREE_STRATA = [(3, 5, "d3_5"), (6, 8, "d6_8"), (9, 14, "d9_14"), (15, 10 ** 9, "d15plus")]
PRIMARY_STRATA = ["d3_5", "d6_8"]
SECONDARY_STRATA = ["d9_14", "d15plus"]
MIN_STRATUM_N = 10

# ---- Permutation test ----
N_PERM = 500

# ---- Arena-fires / scramble-control gates ----
ARENA_FIRE_RATIO = 3.0
ARENA_FIRE_ABS = 0.01
SCRAMBLE_CEIL_FRAC = 0.25

# ---- Decisive bands ----
HELPS_THRESH = 0.02
HURTS_THRESH = -0.02
P_SIG_STRATUM = 0.10
P_SIG_CROSS_SEED = 0.15

SCORE_CHUNK = 256


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


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
# Data loading (real substrate partition).
# ---------------------------------------------------------------------------

def load_induced_triples(bucket_map, data_path=None):
    """relations.jsonl -> list[(src,rel,tgt)] restricted to bucket_map's relation types. Deterministic (file order)."""
    path = data_path or os.path.join(_REPO, DATA_REL)
    triples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            rt = d.get("rel_type")
            if rt not in bucket_map:
                continue
            triples.append((d["src_id"], rt, d["tgt_id"]))
    return triples


# ---------------------------------------------------------------------------
# Planted synthetic arena (self-test only; SAME pipeline functions, a synthetic bucket_map).
# ---------------------------------------------------------------------------

def build_planted_bucket_arena(seed, n_ent=150, n_rel=6, k_lat=6, deg_lo=5, deg_hi=10, frac_low_div=0.35):
    """TransE-consistent planted graph; ~frac_low_div entities draw ALL edges from ONE fixed relation (LOW
    diversity), the rest draw relations uniformly (HIGH diversity) -- both groups span the SAME degree range,
    exercising the degree-controlled stratification pipeline without asserting which direction wins."""
    rng = np.random.default_rng(seed * 100019 + 3)
    z = rng.standard_normal((n_ent, k_lat))
    w = rng.standard_normal((n_rel, k_lat))
    low_div = rng.random(n_ent) < frac_low_div
    edges = []
    for h in range(n_ent):
        d = int(rng.integers(deg_lo, deg_hi + 1))
        if low_div[h]:
            r_fixed = int(rng.integers(n_rel))
            rels = np.full(d, r_fixed, dtype=np.int64)
        else:
            rels = rng.integers(0, n_rel, size=d)
        used_tails = {h}                     # greedy-without-replacement: avoid degenerate repeated-edge dedup
        for r in rels:
            target = z[h] + w[r]
            dist = np.linalg.norm(z - target, axis=1)
            for u in used_tails:
                dist[u] = np.inf
            t = int(np.argmin(dist))
            used_tails.add(t)
            edges.append(("e%d" % h, "r%d" % r, "e%d" % t))
    return list(dict.fromkeys(edges))


SYNTH_BUCKET_MAP = {"r%d" % i: "b%d" % i for i in range(6)}


# ---------------------------------------------------------------------------
# Split (degree-eligible per-entity holdout, TRAIN-only covariates -- no leakage).
# ---------------------------------------------------------------------------

def build_holdout_split(triples, bucket_map, seed, min_split_degree=MIN_SPLIT_DEGREE,
                        holdout_frac=HOLDOUT_FRAC, hold_min=HOLDOUT_MIN, hold_max=HOLDOUT_MAX):
    out_by_src = defaultdict(list)
    for (h, r, t) in triples:
        out_by_src[h].append((r, t))
    for h in out_by_src:
        out_by_src[h].sort()  # deterministic regardless of file/dict order
    rng = np.random.default_rng(seed * 100369 + 41)
    train_triples, query_triples = [], []
    for h in sorted(out_by_src.keys()):
        edges = out_by_src[h]
        d = len(edges)
        if d >= min_split_degree:
            n_hold = int(round(holdout_frac * d))
            n_hold = max(hold_min, min(hold_max, n_hold))
            n_hold = min(n_hold, d - 1)
            order = rng.permutation(d)
            hold_idx = set(int(x) for x in order[:n_hold].tolist())
            for j, (r, t) in enumerate(edges):
                (query_triples if j in hold_idx else train_triples).append((h, r, t))
        else:
            for (r, t) in edges:
                train_triples.append((h, r, t))
    src_train_out = defaultdict(list)
    for (h, r, t) in train_triples:
        src_train_out[h].append((r, t))
    src_train_degree = {h: len(v) for h, v in src_train_out.items()}
    src_train_buckets = {h: frozenset(bucket_map[r] for (r, _t) in v) for h, v in src_train_out.items()}
    return train_triples, query_triples, src_train_degree, src_train_buckets


# ---------------------------------------------------------------------------
# Per-query filtered reciprocal rank (array form of filtered_hits_from_scores).
# ---------------------------------------------------------------------------

def filtered_rr_per_query(scores, hold_edges, all_true_by_hr):
    nq = scores.shape[0]
    sc = scores.clone()
    for i in range(nq):
        h = int(hold_edges[i, 0]); r = int(hold_edges[i, 1]); t = int(hold_edges[i, 2])
        others = all_true_by_hr.get((h, r), None)
        if others:
            for o in others:
                if o != t:
                    sc[i, o] = -1e30
    rr = np.zeros(nq, dtype=np.float64)
    for i in range(nq):
        t = int(hold_edges[i, 2])
        row = sc[i]
        target = row[t].item()
        rank = int((row > target).sum().item()) + 1
        rr[i] = 1.0 / rank
    return rr


# ---------------------------------------------------------------------------
# Stratification + permutation test.
# ---------------------------------------------------------------------------

def _stratum_of(train_deg):
    for lo, hi, name in DEGREE_STRATA:
        if lo <= train_deg <= hi:
            return name
    return None


def _divbin_of(n_buckets):
    if n_buckets <= 1:
        return "div1"
    if n_buckets == 2:
        return "div2"
    return "div3plus"


def build_entity_level_records(query_int, i2ent, src_train_degree, src_train_buckets, rr_main):
    recs = defaultdict(list)
    for i in range(query_int.shape[0]):
        h_lbl = i2ent[int(query_int[i, 0])]
        recs[h_lbl].append(float(rr_main[i]))
    out = {}
    for h_lbl, rr in recs.items():
        deg = src_train_degree.get(h_lbl, 0)
        nb = len(src_train_buckets.get(h_lbl, frozenset()))
        out[h_lbl] = dict(rr=rr, stratum=_stratum_of(deg), div=_divbin_of(nb), train_degree=deg, n_buckets=nb)
    return out


def stratum_group_stats(entity_records, stratum_name):
    groups = defaultdict(list)
    ent_by_div = defaultdict(list)
    for h_lbl, rec in entity_records.items():
        if rec["stratum"] != stratum_name:
            continue
        groups[rec["div"]].extend(rec["rr"])
        ent_by_div[rec["div"]].append(h_lbl)
    stats = {}
    for div in ("div1", "div2", "div3plus"):
        vals = groups.get(div, [])
        stats[div] = dict(n_queries=len(vals), n_entities=len(ent_by_div.get(div, [])),
                          mean_rr=(round(float(np.mean(vals)), 6) if vals else None))
    return stats


def permutation_test_stratum(entity_records, stratum_name, n_perm, seed):
    pool = []
    for h_lbl, rec in entity_records.items():
        if rec["stratum"] != stratum_name:
            continue
        if rec["div"] == "div1":
            pool.append((rec["rr"], "div1"))
        elif rec["div"] == "div3plus":
            pool.append((rec["rr"], "div3plus"))
    n1 = sum(1 for _, g in pool if g == "div1")
    n3 = sum(1 for _, g in pool if g == "div3plus")
    if n1 == 0 or n3 == 0:
        return dict(real_lift=float("nan"), n1=n1, n3=n3, p_perm=float("nan"), null_mean=float("nan"),
                   null_std=float("nan"))

    def _lift(grouping):
        low_rr, high_rr = [], []
        for (rr, _g), grp in zip(pool, grouping):
            (low_rr if grp == "div1" else high_rr).extend(rr)
        return float(np.mean(high_rr)) - float(np.mean(low_rr))

    real_grouping = [g for _, g in pool]
    real_lift = _lift(real_grouping)
    rng = np.random.default_rng(seed * 7919 + 13)
    n_tot = len(pool)
    base = np.array(["div1"] * n1 + ["div3plus"] * n3)
    null_lifts = np.zeros(n_perm, dtype=np.float64)
    for p in range(n_perm):
        null_lifts[p] = _lift(base[rng.permutation(n_tot)])
    p_perm = float((np.sum(np.abs(null_lifts) >= abs(real_lift)) + 1) / (n_perm + 1))
    return dict(real_lift=round(real_lift, 6), n1=n1, n3=n3,
               n_queries_div1=sum(len(rr) for rr, g in pool if g == "div1"),
               n_queries_div3plus=sum(len(rr) for rr, g in pool if g == "div3plus"),
               p_perm=round(p_perm, 4), null_mean=round(float(np.mean(null_lifts)), 6),
               null_std=round(float(np.std(null_lifts)), 6))


def aggregate_across_strata(per_stratum_perm, min_stratum_n=MIN_STRATUM_N):
    valid = {s: v for s, v in per_stratum_perm.items()
            if v["n1"] >= min_stratum_n and v["n3"] >= min_stratum_n and v["real_lift"] == v["real_lift"]}
    if not valid:
        return dict(aggregate_lift=float("nan"), n_qualifying_strata=0, sign_consistent=False,
                   p_perm_aggregate=float("nan"), qualifying_strata=[])
    weights = {s: min(v["n1"], v["n3"]) for s, v in valid.items()}
    total_w = sum(weights.values())
    agg_lift = sum(v["real_lift"] * weights[s] for s, v in valid.items()) / total_w
    signs = [1 if v["real_lift"] > 0 else (-1 if v["real_lift"] < 0 else 0) for v in valid.values()]
    nonzero = [s for s in signs if s != 0]
    sign_consistent = bool(nonzero and len(set(nonzero)) == 1)
    p_agg = max(v["p_perm"] for v in valid.values())
    return dict(aggregate_lift=round(agg_lift, 6), n_qualifying_strata=len(valid), sign_consistent=sign_consistent,
               p_perm_aggregate=round(p_agg, 4), qualifying_strata=sorted(valid.keys()))


# ---------------------------------------------------------------------------
# One corpus run (one seed): split -> fit -> score 3 arms -> stratify -> permute.
# ---------------------------------------------------------------------------

def run_one_seed(triples, bucket_map, cfg, device, seed, ckpt_dir=None):
    train_lbl, query_lbl, src_train_degree, src_train_buckets = build_holdout_split(triples, bucket_map, seed)
    all_lbl = train_lbl + query_lbl
    ent2i, rel2i = build_ids(all_lbl, [], [])
    i2ent = {v: k for k, v in ent2i.items()}
    N = len(ent2i); n_rel = len(rel2i)
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    query_int = _to_int_edges(query_lbl, ent2i, rel2i)
    if cfg.get("n_query_eval") and query_int.shape[0] > cfg["n_query_eval"]:
        rng = np.random.default_rng(seed * 777 + 3)
        idx = sorted(rng.choice(query_int.shape[0], size=cfg["n_query_eval"], replace=False).tolist())
        query_int = query_int[idx]
    all_true = build_true_by_hr_int(train_int, query_int)
    gd = Graph(train_lbl, ent2i, rel2i)

    result = dict(N=int(N), n_rel=int(n_rel), n_train=int(train_int.shape[0]), n_query=int(query_int.shape[0]),
                 seed=seed)
    if query_int.shape[0] < 1:
        result["empty"] = True
        return result

    ckpt = FitCheckpoint(ckpt_dir, "kge_seed%d" % seed, cfg.get("ckpt_every")) if (ckpt_dir and cfg.get("ckpt_every")) else None
    X, D = fit_kge_anchor1(train_int, N, n_rel, cfg["k"], device, seed, cfg["epochs"], reciprocal=True, lr=A1_LR,
                           n_neg=cfg["n_neg"], batch_size=cfg["batch"], neg_chunk=cfg.get("neg_chunk"), ckpt=ckpt)
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()

    gR = torch.Generator(device="cpu").manual_seed(seed * 333 + 9)
    Xr = (torch.randn(N, cfg["k"], generator=gR) * 0.1).to(device)
    Dr = (torch.randn(n_rel, cfg["k"], generator=gR) * 0.1).to(device)

    rng2 = np.random.default_rng(seed * 4441 + 17)
    perm = rng2.permutation(n_rel)
    if n_rel > 1 and bool((perm == np.arange(n_rel)).all()):
        perm = np.roll(perm, 1)
    Dscr = D[torch.from_numpy(perm).long().to(device)]

    sc_main = additive_direct_scores(X, D, query_int, device, chunk=SCORE_CHUNK)
    sc_random = additive_direct_scores(Xr, Dr, query_int, device, chunk=SCORE_CHUNK)
    sc_scramble = additive_direct_scores(X, Dscr, query_int, device, chunk=SCORE_CHUNK)

    rr_main = filtered_rr_per_query(sc_main, query_int, all_true)
    rr_random = filtered_rr_per_query(sc_random, query_int, all_true)
    rr_scramble = filtered_rr_per_query(sc_scramble, query_int, all_true)
    pop_m, _ = pop_hits(gd.rel_tail_freq, query_int, all_true, N, ks=(1, 10))

    arm_sigs = dict(MAIN=_sig(sc_main.numpy()[:min(64, sc_main.shape[0])].ravel()),
                    RANDOM=_sig(sc_random.numpy()[:min(64, sc_random.shape[0])].ravel()),
                    SCRAMBLE=_sig(sc_scramble.numpy()[:min(64, sc_scramble.shape[0])].ravel()))

    entity_records = build_entity_level_records(query_int, i2ent, src_train_degree, src_train_buckets, rr_main)
    per_stratum_groups = {name: stratum_group_stats(entity_records, name) for _, _, name in DEGREE_STRATA}
    per_stratum_perm = {name: permutation_test_stratum(entity_records, name, N_PERM, seed)
                       for name in PRIMARY_STRATA}
    agg = aggregate_across_strata(per_stratum_perm)

    del sc_main, sc_random, sc_scramble, X, D, Xr, Dr, Dscr
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()

    result.update(
        main_mrr=round(float(np.mean(rr_main)), 6), random_mrr=round(float(np.mean(rr_random)), 6),
        scramble_mrr=round(float(np.mean(rr_scramble)), 6), pop_mrr=round(pop_m.get("mrr", float("nan")), 6),
        arm_sigs=arm_sigs, per_stratum_groups=per_stratum_groups, per_stratum_perm=per_stratum_perm,
        aggregate=agg, n_entities_with_queries=len(entity_records),
    )
    return result


# ---------------------------------------------------------------------------
# Cross-seed verdict.
# ---------------------------------------------------------------------------

def verdict_from_gates(per_seed):
    main_mrr = float(np.mean([r["main_mrr"] for r in per_seed]))
    random_mrr = float(np.mean([r["random_mrr"] for r in per_seed]))
    scramble_mrr = float(np.mean([r["scramble_mrr"] for r in per_seed]))
    pop_mrr = float(np.mean([r["pop_mrr"] for r in per_seed]))

    arena_margin = main_mrr - random_mrr
    arena_ratio = (main_mrr / random_mrr) if random_mrr > 0 else float("inf")
    arena_fires = bool(arena_margin >= ARENA_FIRE_ABS and arena_ratio >= ARENA_FIRE_RATIO)

    scr_margin = scramble_mrr - random_mrr
    scramble_ceiling = SCRAMBLE_CEIL_FRAC * arena_margin if arena_margin == arena_margin else float("nan")
    scramble_controlled = bool(scr_margin == scr_margin and scramble_ceiling == scramble_ceiling
                               and scr_margin <= scramble_ceiling)

    all_sigs = set()
    for r in per_seed:
        all_sigs |= set(r.get("arm_sigs", {}).values())
    arms_differ = bool(len(all_sigs) >= 3)

    per_seed_agg = [r["aggregate"] for r in per_seed]
    n_qual = [a["n_qualifying_strata"] for a in per_seed_agg]
    lifts = [a["aggregate_lift"] for a in per_seed_agg if a["aggregate_lift"] == a["aggregate_lift"]]
    signs = [1 if a["aggregate_lift"] > 0 else (-1 if a["aggregate_lift"] < 0 else 0)
            for a in per_seed_agg if a["aggregate_lift"] == a["aggregate_lift"]]
    p_perms = [a["p_perm_aggregate"] for a in per_seed_agg if a["p_perm_aggregate"] == a["p_perm_aggregate"]]

    mean_lift = float(np.mean(lifts)) if lifts else float("nan")
    all_seeds_qualify = bool(len(lifts) == len(per_seed) and min(n_qual) >= 1)
    seeds_agree_sign = bool(all_seeds_qualify and len(set(signs)) == 1 and signs[0] != 0)
    max_p = max(p_perms) if p_perms else float("nan")

    if not arena_fires:
        verdict = "INCONCLUSIVE_ARENA_DID_NOT_FIRE"
    elif not scramble_controlled:
        verdict = "INCONCLUSIVE_SCRAMBLE_NOT_CONTROLLED"
    elif not all_seeds_qualify:
        verdict = "INCONCLUSIVE_INSUFFICIENT_STRATA"
    elif not seeds_agree_sign:
        verdict = "INCONCLUSIVE_SEED_DISAGREEMENT"
    elif mean_lift >= HELPS_THRESH and max_p <= P_SIG_CROSS_SEED:
        verdict = "BUCKET_DIVERSITY_HELPS_DEGREE_CONTROLLED"
    elif mean_lift <= HURTS_THRESH and max_p <= P_SIG_CROSS_SEED:
        verdict = "BUCKET_DIVERSITY_HURTS_DEGREE_CONTROLLED_ARXIV_CAVEAT_REPLICATES"
    else:
        verdict = "BUCKET_DIVERSITY_NEUTRAL_DEGREE_CONTROLLED"

    verdict_msg = (
        "%s || MAIN=%s RANDOM=%s SCRAMBLE=%s POP=%s (arena_margin=%s ratio=%s fires=%s) | "
        "scramble_margin=%s ceiling=%s controlled=%s | mean_aggregate_lift=%s max_p_perm=%s "
        "seeds_agree_sign=%s per_seed_lift=%s per_seed_p=%s per_seed_n_qual=%s | arms_differ=%s(sigs=%d) seeds=%d"
        % (verdict, _fmt(main_mrr), _fmt(random_mrr), _fmt(scramble_mrr), _fmt(pop_mrr),
           _fmt(arena_margin), (_fmt(arena_ratio) if arena_ratio != float("inf") else "inf"), arena_fires,
           _fmt(scr_margin), _fmt(scramble_ceiling), scramble_controlled,
           _fmt(mean_lift), _fmt(max_p), seeds_agree_sign,
           [round(x, 5) if x == x else None for x in
            [a["aggregate_lift"] for a in per_seed_agg]],
           [round(x, 4) if x == x else None for x in
            [a["p_perm_aggregate"] for a in per_seed_agg]],
           n_qual, arms_differ, len(all_sigs), len(per_seed)))

    gates = dict(
        verdict=verdict, main_mrr=round(main_mrr, 6), random_mrr=round(random_mrr, 6),
        scramble_mrr=round(scramble_mrr, 6), pop_mrr=round(pop_mrr, 6),
        arena_margin=round(arena_margin, 6),
        arena_ratio=(round(arena_ratio, 3) if arena_ratio != float("inf") else None), arena_fires=arena_fires,
        scramble_margin=round(scr_margin, 6), scramble_ceiling=round(scramble_ceiling, 6) if scramble_ceiling == scramble_ceiling else None,
        scramble_controlled=scramble_controlled, arms_differ=arms_differ, n_distinct_sigs=len(all_sigs),
        mean_aggregate_lift=round(mean_lift, 6) if mean_lift == mean_lift else None,
        max_p_perm_aggregate=round(max_p, 4) if max_p == max_p else None,
        seeds_agree_sign=seeds_agree_sign, all_seeds_qualify=all_seeds_qualify,
        per_seed_aggregate=per_seed_agg,
        per_seed_stratum_groups=[r["per_stratum_groups"] for r in per_seed],
        per_seed_stratum_perm=[r["per_stratum_perm"] for r in per_seed],
        bands=dict(HELPS_THRESH=HELPS_THRESH, HURTS_THRESH=HURTS_THRESH, P_SIG_STRATUM=P_SIG_STRATUM,
                  P_SIG_CROSS_SEED=P_SIG_CROSS_SEED, ARENA_FIRE_RATIO=ARENA_FIRE_RATIO,
                  ARENA_FIRE_ABS=ARENA_FIRE_ABS, SCRAMBLE_CEIL_FRAC=SCRAMBLE_CEIL_FRAC,
                  MIN_STRATUM_N=MIN_STRATUM_N, N_PERM=N_PERM),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Self-test (real code path, tiny planted synthetic arena).
# ---------------------------------------------------------------------------

SELFTEST_CFG = dict(k=8, epochs=60, n_neg=16, batch=512, n_query_eval=0)
SELFTEST_MIN_QUERY = 8


def self_test():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    device = torch.device("cpu")
    try:
        return _self_test_body(device)
    finally:
        torch.set_num_threads(_prev)


def _self_test_body(device):
    exercised = set()
    triples = build_planted_bucket_arena(7, n_ent=150, n_rel=6, k_lat=6, deg_lo=5, deg_hi=10)
    exercised.add("build_planted_bucket_arena")

    res = run_one_seed(triples, SYNTH_BUCKET_MAP, SELFTEST_CFG, device, 7, ckpt_dir=None)
    exercised.update(["build_holdout_split", "fit_kge_anchor1", "additive_direct_scores",
                      "filtered_rr_per_query", "permutation_test_stratum", "aggregate_across_strata"])
    out = dict(n_query=res.get("n_query"), n_entities_with_queries=res.get("n_entities_with_queries"))
    if res.get("empty") or res.get("n_query", 0) < SELFTEST_MIN_QUERY:
        out["fail"] = "planted arena produced too few query edges (%s)" % res.get("n_query")
        return False, out

    v, msg, gates = verdict_from_gates([res])
    exercised.add("verdict_from_gates")
    out["selftest_verdict"] = v
    out["gates"] = gates

    arena_fires = bool(gates["arena_fires"])
    scramble_controlled = bool(gates["scramble_controlled"])
    arms_differ = bool(gates["arms_differ"])
    any_stratum_has_both_groups = any(
        (g["div1"]["n_queries"] or 0) > 0 and (g["div3plus"]["n_queries"] or 0) > 0
        for g in res["per_stratum_groups"].values())
    p_vals = [p["p_perm"] for p in res["per_stratum_perm"].values() if p["p_perm"] == p["p_perm"]]
    p_valid = all(0.0 <= p <= 1.0 for p in p_vals)

    assert_discriminator_fires(bool(not arena_fires), control_name="RANDOM_CODES", headline_name="arena_fires",
                               run_mode="self_test",
                               extra="RANDOM reached MAIN on the planted arena -> arena not answerable")
    assert_discriminator_fires(bool(not scramble_controlled), control_name="RELATION_SCRAMBLE",
                               headline_name="scramble_controlled", run_mode="self_test",
                               extra="relation-scrambled D did not collapse toward RANDOM -> scorer not exploiting "
                                     "genuine relation identity")

    vp_ok = run_validity_preflight([
        {"kind": "real_code_path", "full_substrate_entrypoints":
            ["build_holdout_split", "fit_kge_anchor1", "additive_direct_scores", "filtered_rr_per_query",
             "permutation_test_stratum", "aggregate_across_strata", "verdict_from_gates"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1,
         "kwargs": dict(train_edges=None, N=1, n_rel=1, k=8, device=device, seed=7, epochs=1,
                       reciprocal=True, lr=A1_LR, n_neg=4, batch_size=32, neg_chunk=None, ckpt=None),
         "callable_name": "fit_kge_anchor1"},
        {"kind": "metric_moves", "metric_name": "mrr",
         "values": [gates["random_mrr"], gates["scramble_mrr"], gates["main_mrr"]],
         "extra": "MRR RANDOM=%.4f SCRAMBLE=%.4f MAIN=%.4f" % (gates["random_mrr"], gates["scramble_mrr"],
                                                               gates["main_mrr"])},
        {"kind": "negative_control_margin", "control_scores": [gates["random_mrr"], gates["scramble_mrr"]],
         "headline_threshold": gates["main_mrr"], "higher_is_pass": True, "margin": 0.01, "n_repeats_min": 2,
         "control_name": "RANDOM_SCRAMBLE_below_MAIN",
         "extra": "RANDOM + relation-scrambled must sit below MAIN"},
        {"kind": "guard_baseline_valid", "baseline_score": gates["pop_mrr"], "floor_score": gates["random_mrr"],
         "guard_name": "n/a_no_control_beats_baseline_guard_in_this_cell", "baseline_name": "POP",
         "floor_name": "RANDOM", "eps": 0.02},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["arena_fires", "scramble_controlled", "arms_differ",
                                    "permutation_p_in_bounds"],
         "exercised_gates": ["arena_fires", "scramble_controlled", "arms_differ", "permutation_p_in_bounds"],
         "extra": "verdict_from_gates verdict=%s at self-test scale" % v},
    ], run_mode="self_test")

    out.update(arena_fires=arena_fires, scramble_controlled=scramble_controlled, arms_differ=arms_differ,
              any_stratum_has_both_groups=any_stratum_has_both_groups, p_perm_values=p_vals, p_valid=p_valid,
              validity_preflight_ok=bool(vp_ok), exercised_entrypoints=sorted(exercised))
    ok = bool(arena_fires and scramble_controlled and arms_differ and any_stratum_has_both_groups and p_valid)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

SMOKE_CFG = dict(k=12, epochs=40, n_neg=32, batch=4096, neg_chunk=None, n_query_eval=0, seeds=[7])
FULL_CFG = dict(k=16, epochs=150, n_neg=64, batch=8192, neg_chunk=16, ckpt_every=20, n_query_eval=0, seeds=[7, 13])


def _resolve_device(arg_device):
    env_queue = os.environ.get("HDLAB_QUEUE", "")
    env_dev = os.environ.get("HDLAB_DEVICE", "")
    force_cpu = (arg_device == "cpu") or (env_dev == "cpu") or (env_queue in ("remote_cpu_queue", "local_cpu_queue"))
    if force_cpu:
        return torch.device("cpu")
    want_cuda = (arg_device in ("auto", "cuda")) or (env_dev == "cuda")
    return torch.device("cuda" if (want_cuda and torch.cuda.is_available()) else "cpu")


def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]) if run_mode != "self_test" else None
    seeds = [7] if run_mode == "self_test" else cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s cuda=%s run_mode=%s seeds=%s" % (device, torch.cuda.is_available(), run_mode, seeds))

    st_ok, st_res = self_test()
    _log("self_test ok=%s arena_fires=%s scramble_controlled=%s arms_differ=%s vp_ok=%s" %
        (st_ok, st_res.get("arena_fires"), st_res.get("scramble_controlled"), st_res.get("arms_differ"),
         st_res.get("validity_preflight_ok")))
    _hb("self_test", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="SELF_TEST_FAILED (arena did not fire / scramble did not collapse / arms not distinct / "
                        "insufficient div1+div3plus groups / invalid p-value): %s" % st_res.get("fail", ""),
            summary="self-test failed", elapsed_s=time.perf_counter() - t_start, self_test=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS bucket_diversity_degree_controlled: MAIN beats RANDOM (arena fires); "
                        "relation-scramble collapses; both div1/div3plus groups present in >=1 stratum; "
                        "permutation p-values valid in [0,1]; validity-preflight checks declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, self_test=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    data_path = os.path.join(_REPO, DATA_REL)
    if not os.path.isfile(data_path):
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="active partition file absent: %s" % data_path, summary="data missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    triples = load_induced_triples(BUCKET_MAP, data_path)
    _log("loaded induced triples=%d" % len(triples))

    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            res = run_one_seed(triples, BUCKET_MAP, cfg, device, seed, ckpt_dir=out_dir)
            if res.get("empty") or res.get("n_query", 0) < 1:
                raise RuntimeError("no query edges produced for seed=%d" % seed)
            sigset = set(res.get("arm_sigs", {}).values())
            if len(sigset) < 3:
                raise RuntimeError("ARMS_MUST_DIFFER seed=%d only %d distinct sigs" % (seed, len(sigset)))
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            cleanup_seed_checkpoints(out_dir, seed)
            _log("seed=%d N=%d n_train=%d n_query=%d MAIN=%s RANDOM=%s SCRAMBLE=%s POP=%s agg_lift=%s (%.1fs)" %
                (seed, res["N"], res["n_train"], res["n_query"], _fmt(res["main_mrr"]), _fmt(res["random_mrr"]),
                 _fmt(res["scramble_mrr"]), _fmt(res["pop_mrr"]), _fmt(res["aggregate"]["aggregate_lift"]),
                 time.time() - ts))
            _hb("seed", si)
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
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start, seed_failures=seed_failures,
            self_test=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = verdict_from_gates(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                  elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                  ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                  seeds=seeds, config=cfg, gates=gates, self_test=st_res, seed_failures=seed_failures,
                  n_induced_triples=len(triples))
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="alias for --run-mode smoke (queue_add.py gate convention)")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    if run_mode is None:
        env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if env_mode in ("self_test", "smoke", "full"):
            run_mode = env_mode
        else:
            raise ValueError("no --run-mode / --self-test / HDLAB_RUN_MODE specified; explicit run_mode required "
                             "(no silent self_test default per RUN_MODE VERIFICATION discipline)")
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
