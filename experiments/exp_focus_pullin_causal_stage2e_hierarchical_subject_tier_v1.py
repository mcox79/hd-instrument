# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; hierarchical_sparse vs scrambled_tier2 digest-differ)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace top-level + per-scale resumable unit)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (empirical dual-regime shard-capacity diagnostic; see prereg + leaf-capacity-sweep)
# - HP_SCOPE: {hierarchical_sparse: [relevant_recall, false_pull_in_rate, scramble_margin]}
# - cardinality_ok: EXPECTED_N_UNITS=len(SCALES) (sweep-axis units are ingest-SCALES)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: hierarchical_sparse/scrambled_tier2=adaptive_with_discriminator_gate (DG-space tau
#   via refuse_gate_calibrate_from_scores, 50/50 internal split, per scale, SAME mechanism Stage-2D used)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs REAL tiny SparseHeteroShardStore + the REAL 2-tier routing functions against a
#   tiny synthetic BIGFAM(K=3)/SMALLFAM(K=1) corpus (real_code_path); verifies ingest/query tier-2 routing
#   agreement for the REAL arm + SCRAMBLE-degrades mechanism at tiny scale
# - progress_logging: print_flush_true (timeout likely >=1800s given DG precompute + double-ingest sweep)
# See preregs/2026-08-10_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1.md for the full pre-reg.
"""exp_focus_pullin_causal_stage2e_hierarchical_subject_tier_v1 -- Stage 2 SUB-TEST E: does adding a
HIERARCHICAL (nested) 2nd routing tier keyed by SUBJECT to Stage-2D's oversized source-shards (AT/VG/CN),
composed with Stage-2D's DG/CA3 sparse within-shard coding, hold relevant_recall >= 0.50 at BOTH 100K AND
1.2M (where Stage-2D's tier-1-only ARM_SHARDED_SPARSE collapsed 0.547 -> 0.053), with scramble margin
>= 0.30 and false_pull_in <= 0.20 at both scales?

MOTIVATION (Director task, this session): Stage-2D (MIDDLE_BAND, `data/exp_focus_pullin_causal_stage2d_
context_gated_sharded_store_v1/metrics.json`) moved the collapse wall 30K -> past 100K but re-collapsed at
1.2M because 3 of its 7 source-shards are themselves oversized (AT=696,152/57.4%, VG=257,130/21.2%,
CN=214,890/17.7% edges in ONE physical [dg_dim,dg_dim] leaf each) AND its shard key (relation-majority
family) is weak (scramble margin only 0.20, below the 0.30 target). KGStore's E/R codebooks are i.i.d.
random bipolar with NO baked-in semantics, so a shard key only helps by routing a query to the leaf that
ACTUALLY holds its answer -- SUBJECT is a query-time-EXACT 2nd key (unlike relation, which is only an
approximate proxy for the coarse tier-1 family): a query (s,p)->o always knows its own subject s, so
routing tier-2 by a deterministic hash(subject) can ALWAYS find the correct leaf IF that subject's edges
were grouped there at write time too -- the entire benefit is reduced per-leaf crosstalk (fewer triples
sharing one Hebbian W), not routing accuracy per se. This composes ONE already-certified organ class
(`exp_hierarchical_subshard_kg_cpu_v1` smoke HARD_PASS relation-then-subject 1.000 vs 0.735;
`exp_community_of_communities_nested_retrieval_v2` FULL 3-seed HARD_PASS, 2nd tier holds fidelity flat to
V=48,000 while single-tier collapses) with Stage-2D's own already-built DenseShardStore/
SparseHeteroShardStore/DG-CA3 machinery -- disk-verified by exp_dev this session (both cited metrics read
directly, not trusted from the task prompt's summary alone).

CRITICAL DESIGN CORRECTION (per Director's explicit VET note, addressed BEFORE any full-scale compute was
spent): the mining drill's "~30-65 triples/leaf" capacity target was derived from an UNRELATED flat-bundle
mechanism (exp_skewed_shard_capacity, already dismissed at cosine=0.29 by Stage-2D's own prior-work check)
and CONTRADICTS Stage-2B's own empirics (recall 0.967 @ 1,000 triples, 0.70 @ 10,000 -- 30-65 would never
have survived that). Per the Director's instruction, this cell does NOT hard-code that number. Instead
`exp_focus_pullin_causal_stage2e_leaf_capacity_sweep_v1.py` (run this session, disk-verified, NOT
hypothesized) EMPIRICALLY measured, on AN ISOLATED SINGLE LEAF of THIS EXACT store (KGStore-shaped for
dense, SparseHeteroShardStore-with-n_shards=1 for sparse -- real_code_path, not synthetic), a real
AT-family recall-vs-leaf-size curve at 5 points {57000, 150000, 300000, 500000, 696152} (dense) and the
same 5 points (sparse), PLUS single full-family-count points for VG and CN. Result
(`data/exp_focus_pullin_causal_stage2e_leaf_capacity_sweep_v1/metrics.json`): DENSE recall=0.000 at EVERY
tested point (the dense-Hopfield cliff sits well below 57,000 -- consistent with, not contradicting,
Stage-2B's own known dense curve, since Stage-2B's own decline was already well underway by 10,000; dense
is NOT this cell's composed-arm substrate so it was not swept finer). SPARSE recall: 0.693 @ 57,000 (only
point clearing the 0.50 gate) -> 0.227 @ 150,000 -> 0.053 @ 300,000 -> 0.013 @ 500,000 -> 0.013 @ 696,152 --
a SHARP cliff bracketed between 57,000 (safe, comfortable 0.193 margin above the 0.50 bar) and 150,000
(unsafe). `SAFE_LEAF_SIZE_SPARSE=57,000` (the largest CLEARLY-safe measured point) is therefore a
conservative, disk-measured, non-hard-coded choice -- MEASURED@data/exp_focus_pullin_causal_stage2e_leaf_
capacity_sweep_v1/metrics.json:safe_leaf_size_sparse. K_family = ceil(family_occupancy / 57,000): AT=13,
VG=5, CN=4 (raw); a fan-out check (this session, `np.bincount` over real AT/VG/CN subject arrays) found AT
extremely hash-friendly (23,799 distinct subjects, max single-entity fan-out=96, top5_share=0.06% -- no
mega-hub risk) but VG (max fan-out=2456, top5_share=3.36%) and CN (max fan-out=6081, top5_share=4.25%) have
modest hub concentration, so K_VG and K_CN are bumped +1 for hash-imbalance safety margin: **K_FAMILY =
{AT: 14, VG: 6, CN: 5, WD/FN/WN/CN|WN: 1 (unchanged, already safely below 57,000)}**, giving average
per-leaf occupancy of 49,725 (AT) / 42,855 (VG) / 42,978 (CN), all comfortably below SAFE_LEAF_SIZE_SPARSE.

MECHANISM: tier-1 (family/source) routing is Stage-2D's EXACT, UNCHANGED mechanism (ingest = true source;
query = relation-majority-vote table) -- NOT touched here, since the task's ONE new variable is tier-2.
Tier-2 (subject) routing for oversized families: a deterministic, PYTHONHASHSEED-independent vectorized
avalanche hash of (subject_id, family_name, fixed salt) mod K_family (see `_vectorized_entity_hash` --
NOT Python's built-in `hash()`, no PYTHONHASHSEED dependency, per gate F.5/PROT-023). Both ingest (which
DOES know the true subject at write time, honest) and query (which ALWAYS knows its own subject s, honest,
not an oracle) use the IDENTICAL formula for the REAL/composed arm, so tier-2 routing is ALWAYS correct by
construction -- the only source of residual imperfection is per-leaf CAPACITY (crosstalk), which is exactly
what this cell measures. `CONTROL_SCRAMBLED_TIER2` scrambles ONLY the write-side tier-2 assignment (a
fresh per-scale-per-family permutation of the true tier-2-local multiset, Stage-2D's own
`scramble_labels_for_prefix` methodology applied one level deeper -- preserves the exact per-leaf-size
histogram) while QUERY-side routing stays IDENTICAL to the real arm (the "would-be-correct" hash) --
this creates a genuine write/read MISMATCH: a subject's own edges are scattered to essentially random
leaves at write time, but a query for that subject only checks the ONE leaf its true hash points to, so
recall should collapse toward ~1/K_family if grouping-by-subject is what actually mattered (not merely
"having more shards"). Tier-1 is IDENTICAL between the composed and scrambled arms (both reuse the SAME
rel_majority_family_idx table, SAME source-level ingest) -- isolates tier-2 as the one active variable.

COMPUTE-PROPORTIONALITY (disclosed): Stage-2D's own FLAT/DENSE/SPARSE/CONTROL_SCRAMBLED_SHARD_KEY arms are
DETERMINISTIC (Stage-2D's own `deterministic_seeding: true`, identical DATA_SEED/QUERY_SEED/SCRAMBLE_SEED
reused here unmodified) -- re-executing 693s of unchanged compute to reproduce numbers already on disk
would violate the compute-proportionality discipline. Instead: those 4 arms' 100K/1,213,912 numbers are
CITED (MEASURED@data/exp_focus_pullin_causal_stage2d_context_gated_sharded_store_v1/metrics.json) and this
cell spends its FULL compute budget on a fresh SPOT-CHECK reproduction of the tier-1-only SPARSE +
CONTROL_SCRAMBLED_SHARD_KEY arms at ONE cheap scale (10,000, within REPRO_TOLERANCE=0.05 absolute) PLUS the
genuinely new HIERARCHICAL_SPARSE + CONTROL_SCRAMBLED_TIER2 arms at the two scales the task's HARD-PASS/
HARD-FAIL bands require (100,000 and 1,213,912) -- this is where compute produces NEW information.

Modes:
  --self-test  Real-code-path check: tiny SparseHeteroShardStore (n_ent=48, dg_dim=256) + the REAL 2-tier
               routing functions (compute_ingest_shard_ids_real/scrambled, compute_query_shard_ids,
               _vectorized_entity_hash) against a tiny synthetic BIGFAM(K=3)/SMALLFAM(K=1) corpus; verifies
               ingest/query tier-2 agreement for the REAL arm (closed-form, no stochastic dependence) +
               SCRAMBLE-degrades-recall mechanism check. No dispatch.
  --smoke      Real CSKG data, scale=[1213912] only (DISCRIMINATOR-MUST-SURVIVE-SCALE option A: smoke AT
               full-N directly -- this is the hardest, most-discriminating point and the one Stage-2D
               catastrophically failed; a smaller-scale smoke would not exercise the mechanism this cell
               exists to test). Both hierarchical_sparse + scrambled_tier2 arms run.
  --full       scales=[100000, 1213912] (exactly the task contract's two required gate points), per-scale
               checkpointed via tools/exp_checkpoint.py (unit_key = scale). Also runs the ONE-TIME
               Stage-2D tier-1-only spot-check reproduction at scale=10000 (not itself a gated unit).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "8")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "8")
os.environ.setdefault("MKL_NUM_THREADS", "8")

import argparse
import hashlib
import json
import math
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List

import numpy as np
import torch

ANCHOR_NAME = "focus_pullin_causal_stage2e_hierarchical_subject_tier_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
CSKG_DIR = os.path.join(REPO_ROOT, "data", "cskg_foundation_v1")
STAGE2D_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_focus_pullin_causal_stage2d_context_gated_sharded_store_v1", "metrics.json")
LEAF_SWEEP_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_focus_pullin_causal_stage2e_leaf_capacity_sweep_v1", "metrics.json")

from hdlab.kg_traversal import KGStore  # noqa: E402
from experiments.exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1 import (  # noqa: E402
    load_entity_vocab, precheck_kgstore_and_loader, QUERY_SEED as S2B_QUERY_SEED,
    DATA_SEED as S2B_DATA_SEED, SHORTLIST_K as S2B_SHORTLIST_K, N_QUERY as S2B_N_QUERY,
)
from experiments.exp_focus_pullin_causal_stage2d_context_gated_sharded_store_v1 import (  # noqa: E402
    load_spine_edges_with_source, SparseHeteroShardStore, build_relation_majority_shard,
    scramble_labels_for_prefix, build_dg_projections, precompute_dg_val_codebook, _batched_score_settle,
    eval_gate_sparse_shard, precheck_source_field, DG_DIM, DG_SPARSITY, SCRAMBLE_SEED as S2D_SCRAMBLE_SEED,
    REC_THRESH_SPARSE, FP_THRESH, REPRO_TOLERANCE,
)
from experiments.exp_focus_pullin_causal_stage15_salted_cardinality_gate_v1 import (  # noqa: E402
    refuse_gate_calibrate_from_scores,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

QUERY_SEED = S2B_QUERY_SEED
DATA_SEED = S2B_DATA_SEED
SHORTLIST_K = S2B_SHORTLIST_K
N_QUERY = S2B_N_QUERY
SCRAMBLE_SEED = S2D_SCRAMBLE_SEED

SCALES_FULL = [100000, 1213912]
SCALES_SMOKE = [1213912]
STAGE2D_REPRO_SCALE = 10000

# MEASURED@data/exp_focus_pullin_causal_stage2e_leaf_capacity_sweep_v1/metrics.json:safe_leaf_size_sparse
SAFE_LEAF_SIZE_SPARSE = 57000
# MEASURED-derived: K = ceil(full_family_occupancy / SAFE_LEAF_SIZE_SPARSE), rounded up +1 for AT/VG/CN's
# non-uniform subject fan-out (this session's np.bincount hub-concentration check, see module docstring).
K_FAMILY = {"AT": 14, "VG": 6, "CN": 5, "WD": 1, "FN": 1, "WN": 1, "CN|WN": 1}
# fixed, arbitrary, deterministic per-family salt constants (NOT derived from Python's built-in hash())
FAMILY_SALT = {"AT": 11, "CN": 13, "CN|WN": 17, "FN": 19, "VG": 23, "WD": 29, "WN": 31}
TIER2_SALT_BASE = 20260810 + 999

HP_RECALL_MIN = 0.50
HP_FP_MAX = 0.20
HP_MARGIN_MIN = 0.30
HARD_FAIL_RECALL_CEILING = 0.10
HARD_FAIL_TIE_GAP = 0.10
IATTR_TEMP = 4.0


# ============================================================================ deterministic vectorized hash
def _vectorized_entity_hash(entity_ids: np.ndarray, salt: int) -> np.ndarray:
    """Deterministic, PYTHONHASHSEED-independent avalanche hash (SplitMix64-style finalizer) -- NOT
    Python's built-in hash() (gate F.5/PROT-023: no hash()-seeded routing). Vectorized over numpy uint64
    arrays (n_ent up to ~500K, n_edges up to ~1.2M scale in this cell)."""
    # wraparound (mod 2**64) is the INTENDED avalanche behavior, not an error -- silence the scalar
    # overflow RuntimeWarning numpy emits for uint64 * uint64 scalar multiplication.
    with np.errstate(over="ignore"):
        x = (entity_ids.astype(np.uint64) + np.uint64(salt) * np.uint64(0x9E3779B97F4A7C15))
        x = x ^ (x >> np.uint64(30))
        x = (x * np.uint64(0xBF58476D1CE4E5B9)) & np.uint64(0xFFFFFFFFFFFFFFFF)
        x = x ^ (x >> np.uint64(27))
        x = (x * np.uint64(0x94D049BB133111EB)) & np.uint64(0xFFFFFFFFFFFFFFFF)
        x = x ^ (x >> np.uint64(31))
    return x


def subject_tier2_local(entity_ids: np.ndarray, family: str, k_family_map: Dict[str, int],
                        salt_base: int) -> np.ndarray:
    kf = k_family_map.get(family, 1)
    if kf <= 1:
        return np.zeros(len(entity_ids), dtype=np.int64)
    salt = salt_base + FAMILY_SALT.get(family, 1)
    h = _vectorized_entity_hash(np.asarray(entity_ids, dtype=np.int64), salt)
    return (h % np.uint64(kf)).astype(np.int64)


# ============================================================================ shard layout
def build_family_shard_layout(source_to_idx: Dict[str, int], k_family_map: Dict[str, int]):
    families_sorted = sorted(source_to_idx.keys())
    base_offset: Dict[str, int] = {}
    off = 0
    for f in families_sorted:
        base_offset[f] = off
        off += k_family_map.get(f, 1)
    return base_offset, off


# ============================================================================ ingest-side routing (write-time)
def compute_ingest_shard_ids_real(s_arr: np.ndarray, src_idx_arr: np.ndarray, idx_to_source: Dict[int, str],
                                  base_offset: Dict[str, int], k_family_map: Dict[str, int],
                                  salt_base: int) -> np.ndarray:
    """TRUE family (source) + TRUE subject-hash -- honest write-time routing (ingest always knows the fact
    it is writing, matching Stage-2D's own convention where ingest uses the true source label)."""
    out = np.empty(len(s_arr), dtype=np.int64)
    for src_i in np.unique(src_idx_arr):
        fam = idx_to_source[int(src_i)]
        mask = src_idx_arr == src_i
        out[mask] = base_offset[fam] + subject_tier2_local(s_arr[mask], fam, k_family_map, salt_base)
    return out


def compute_ingest_shard_ids_scrambled(s_arr: np.ndarray, src_idx_arr: np.ndarray,
                                       idx_to_source: Dict[int, str], base_offset: Dict[str, int],
                                       k_family_map: Dict[str, int], salt_base: int, scale: int,
                                       scramble_seed: int) -> np.ndarray:
    """Tier-1 (family) placement stays TRUE (unscrambled) -- ONLY tier-2 (subject->leaf) is scrambled, per
    a fresh per-scale-per-family permutation of the TRUE tier-2-local multiset (Stage-2D's own
    scramble_labels_for_prefix methodology, applied one level deeper; preserves the exact per-leaf-size
    histogram the real arm produces)."""
    real = compute_ingest_shard_ids_real(s_arr, src_idx_arr, idx_to_source, base_offset, k_family_map,
                                         salt_base)
    out = real.copy()
    for src_i in np.unique(src_idx_arr):
        fam = idx_to_source[int(src_i)]
        kf = k_family_map.get(fam, 1)
        if kf <= 1:
            continue
        mask = src_idx_arr == src_i
        local_true = real[mask] - base_offset[fam]
        rng = np.random.default_rng(scramble_seed + int(scale) + FAMILY_SALT.get(fam, 1) * 100003)
        local_scrambled = rng.permutation(local_true)
        out[mask] = base_offset[fam] + local_scrambled
    return out


# ============================================================================ query-side routing (read-time)
def compute_query_shard_ids(s_arr: np.ndarray, p_arr: np.ndarray, rel_majority_family_idx: np.ndarray,
                            family_idx_to_name: Dict[int, str], base_offset: Dict[str, int],
                            k_family_map: Dict[str, int], salt_base: int) -> np.ndarray:
    """Family via the relation-majority-vote table (Stage-2D's unchanged, approximate tier-1 proxy --
    query does not know the true source). Tier-2 via the TRUE deterministic hash(subject) -- honest,
    since a query (s,p)->o always knows its own subject s. IDENTICAL for the real and scrambled arms
    (only ingest differs between them) -- this is what creates the scramble arm's write/read mismatch."""
    fam_idx = rel_majority_family_idx[p_arr]
    out = np.empty(len(s_arr), dtype=np.int64)
    for fi in np.unique(fam_idx):
        fam = family_idx_to_name[int(fi)]
        mask = fam_idx == fi
        out[mask] = base_offset[fam] + subject_tier2_local(s_arr[mask], fam, k_family_map, salt_base)
    return out


# ============================================================================ hierarchical eval (composed + scrambled share this)
def eval_gate_hierarchical(store: SparseHeteroShardStore, s_idx_ingested: np.ndarray,
                           p_idx_ingested: np.ndarray, o_idx: np.ndarray, src_idx_ingested: np.ndarray,
                           rel_majority_family_idx: np.ndarray, family_idx_to_name: Dict[int, str],
                           base_offset: Dict[str, int], k_family_map: Dict[str, int], salt_base: int,
                           dg_key_proj, E: torch.Tensor, R: torch.Tensor, n_rel: int, n_query: int,
                           query_seed: int, shortlist_k: int, ingested_triples: torch.Tensor) -> Dict:
    q_rng = np.random.default_rng(query_seed)
    n = ingested_triples.shape[0]
    existing_sp = set((int(s) * n_rel + int(p)) for s, p, _o in ingested_triples.tolist())
    n_ent = store.dg_val_codebook.shape[0]
    shortlist_k_eff = min(shortlist_k, n_ent)
    sq = math.sqrt(E.shape[1])

    rel_idx = q_rng.choice(n, size=min(n_query, n), replace=False)
    rel_s = s_idx_ingested[rel_idx]
    rel_p = p_idx_ingested[rel_idx]
    rel_family_true = src_idx_ingested[rel_idx]
    rel_shard_of = compute_query_shard_ids(rel_s, rel_p, rel_majority_family_idx, family_idx_to_name,
                                           base_offset, k_family_map, salt_base)
    rel_key_vecs = (E[torch.from_numpy(rel_s)].numpy() * R[torch.from_numpy(rel_p)].numpy()
                    * sq).astype(np.float32)
    rel_dg_keys = torch.from_numpy(dg_key_proj.encode_batch(rel_key_vecs)).to(torch.float32)
    rel_true_obj = o_idx[rel_idx]
    rel_results = _batched_score_settle(store, rel_dg_keys, rel_shard_of, shortlist_k_eff,
                                        true_obj=rel_true_obj)
    for li in range(len(rel_idx)):
        rel_results[li]["correct"] = (rel_results[li]["candidate"] == int(rel_true_obj[li]))
        rel_results[li]["family_idx"] = int(rel_family_true[li])

    neg_s: List[int] = []
    neg_p: List[int] = []
    tries = 0
    while len(neg_s) < n_query and tries < n_query * 20:
        tries += 1
        s = int(q_rng.integers(0, n_ent))
        p = int(q_rng.integers(0, n_rel))
        if (s * n_rel + p) in existing_sp:
            continue
        neg_s.append(s)
        neg_p.append(p)
    neg_s_arr = np.array(neg_s, dtype=np.int64)
    neg_p_arr = np.array(neg_p, dtype=np.int64)
    neg_shard_of = compute_query_shard_ids(neg_s_arr, neg_p_arr, rel_majority_family_idx,
                                           family_idx_to_name, base_offset, k_family_map, salt_base)
    neg_key_vecs = (E[torch.from_numpy(neg_s_arr)].numpy()
                    * R[torch.from_numpy(neg_p_arr)].numpy() * sq).astype(np.float32)
    neg_dg_keys = torch.from_numpy(dg_key_proj.encode_batch(neg_key_vecs)).to(torch.float32)
    neg_results = _batched_score_settle(store, neg_dg_keys, neg_shard_of, shortlist_k_eff, true_obj=None)

    in_scores = [r["score"] for r in rel_results]
    out_scores = [r["score"] for r in neg_results]
    calib = refuse_gate_calibrate_from_scores(in_scores, out_scores)
    tau = calib["tau"]
    h_in = len(in_scores) // 2
    h_out = len(out_scores) // 2
    eval_rel = rel_results[h_in:]
    eval_neg = neg_results[h_out:]

    rel_admitted_correct = sum(1 for r in eval_rel if r["correct"] and r["score"] >= tau)
    rel_in_shortlist = sum(1 for r in eval_rel if r["in_shortlist"])
    neg_admitted = sum(1 for r in eval_neg if r["score"] >= tau)

    per_family: Dict[str, Dict] = {}
    for fam_idx_val in sorted(set(r["family_idx"] for r in eval_rel)):
        fam_name = family_idx_to_name[fam_idx_val]
        sub = [r for r in eval_rel if r["family_idx"] == fam_idx_val]
        n_sub = len(sub)
        n_correct = sum(1 for r in sub if r["correct"] and r["score"] >= tau)
        per_family[fam_name] = {"n": n_sub, "relevant_recall": n_correct / max(n_sub, 1)}

    return {
        "n_relevant_queried": len(eval_rel),
        "relevant_recall": rel_admitted_correct / max(len(eval_rel), 1),
        "relevant_in_shortlist_rate": rel_in_shortlist / max(len(eval_rel), 1),
        "n_negative_queried": len(eval_neg),
        "false_pull_in_rate": neg_admitted / max(len(eval_neg), 1),
        "tau": tau, "calibration": calib, "per_family": per_family,
    }


# ============================================================================ per-scale unit
def run_scale_unit(scale: int, triples_shuffled: torch.Tensor, src_idx_shuffled: np.ndarray,
                   ingest_shard_real_full: np.ndarray, E: torch.Tensor, R: torch.Tensor, n_rel: int,
                   source_to_idx: Dict[str, int], family_idx_to_name: Dict[int, str],
                   base_offset: Dict[str, int], total_shards: int, dg_key_proj,
                   dg_val_codebook: torch.Tensor, do_stage2d_repro: bool) -> Dict:
    scale_eff = min(scale, len(triples_shuffled))
    ingested = triples_shuffled[:scale_eff]
    ingested_src = src_idx_shuffled[:scale_eff]
    s_idx = ingested[:, 0].numpy()
    p_idx = ingested[:, 1].numpy()
    o_idx = ingested[:, 2].numpy()
    sq = math.sqrt(E.shape[1])

    rel_majority_family_idx = build_relation_majority_shard(p_idx, ingested_src, n_rel, len(source_to_idx))

    ingest_shard_real = ingest_shard_real_full[:scale_eff]
    ingest_shard_scr = compute_ingest_shard_ids_scrambled(s_idx, ingested_src, family_idx_to_name,
                                                          base_offset, K_FAMILY, TIER2_SALT_BASE, scale_eff,
                                                          SCRAMBLE_SEED)

    unit: Dict = {"scale": scale_eff}

    composed_store = SparseHeteroShardStore(dg_val_codebook, DG_DIM, n_shards=total_shards)
    t0 = time.time()
    composed_diag = composed_store.ingest_from_triples(s_idx, p_idx, o_idx, ingest_shard_real, E, R,
                                                        dg_key_proj, sq)
    composed_ing_s = time.time() - t0
    t0 = time.time()
    composed_eval = eval_gate_hierarchical(composed_store, s_idx, p_idx, o_idx, ingested_src,
                                           rel_majority_family_idx, family_idx_to_name, base_offset,
                                           K_FAMILY, TIER2_SALT_BASE, dg_key_proj, E, R, n_rel, N_QUERY,
                                           QUERY_SEED, SHORTLIST_K, ingested)
    composed_eval_s = time.time() - t0
    composed_eval.update({"ingest_s": round(composed_ing_s, 3), "eval_s": round(composed_eval_s, 3),
                          "shard_diag": composed_diag})
    unit["hierarchical_sparse"] = composed_eval

    scrambled_store = SparseHeteroShardStore(dg_val_codebook, DG_DIM, n_shards=total_shards)
    t0 = time.time()
    scr_diag = scrambled_store.ingest_from_triples(s_idx, p_idx, o_idx, ingest_shard_scr, E, R, dg_key_proj,
                                                   sq)
    scr_ing_s = time.time() - t0
    t0 = time.time()
    scr_eval = eval_gate_hierarchical(scrambled_store, s_idx, p_idx, o_idx, ingested_src,
                                      rel_majority_family_idx, family_idx_to_name, base_offset, K_FAMILY,
                                      TIER2_SALT_BASE, dg_key_proj, E, R, n_rel, N_QUERY, QUERY_SEED,
                                      SHORTLIST_K, ingested)
    scr_eval_s = time.time() - t0
    scr_eval.update({"ingest_s": round(scr_ing_s, 3), "eval_s": round(scr_eval_s, 3), "shard_diag": scr_diag})
    unit["scrambled_tier2"] = scr_eval

    if do_stage2d_repro:
        n_fam = len(source_to_idx)
        tier1_sparse_store = SparseHeteroShardStore(dg_val_codebook, DG_DIM, n_shards=n_fam)
        tier1_sparse_store.ingest_from_triples(s_idx, p_idx, o_idx, ingested_src, E, R, dg_key_proj, sq)
        unit["stage2d_repro_sparse"] = eval_gate_sparse_shard(
            tier1_sparse_store, s_idx, p_idx, o_idx, rel_majority_family_idx, dg_key_proj, E, R, n_rel,
            N_QUERY, QUERY_SEED, SHORTLIST_K, n_fam, ingested)

        scr_src = scramble_labels_for_prefix(ingested_src, scale_eff)
        tier1_scr_store = SparseHeteroShardStore(dg_val_codebook, DG_DIM, n_shards=n_fam)
        tier1_scr_store.ingest_from_triples(s_idx, p_idx, o_idx, scr_src, E, R, dg_key_proj, sq)
        rel_maj_scr = build_relation_majority_shard(p_idx, scr_src, n_rel, n_fam)
        unit["stage2d_repro_scrambled"] = eval_gate_sparse_shard(
            tier1_scr_store, s_idx, p_idx, o_idx, rel_maj_scr, dg_key_proj, E, R, n_rel, N_QUERY,
            QUERY_SEED, SHORTLIST_K, n_fam, ingested)

    return unit


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    rec = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
          "total_units": total_units, "elapsed_s": round(elapsed_s, 2)}
    if extra:
        rec.update(extra)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


def load_stage2d_reference() -> Dict:
    with open(STAGE2D_METRICS_PATH, encoding="utf-8") as f:
        return json.load(f)


# ============================================================================ self-test
def self_test() -> Dict:
    pre = precheck_kgstore_and_loader()
    assert pre["ok"], f"STAGE2B_PRECHECK_FAIL: {pre}"
    src_pre = precheck_source_field()
    assert src_pre["ok"], f"SOURCE_FIELD_PRECHECK_FAIL: {src_pre}"
    assert os.path.exists(STAGE2D_METRICS_PATH), f"STAGE2D_REFERENCE_MISSING: {STAGE2D_METRICS_PATH}"
    assert os.path.exists(LEAF_SWEEP_METRICS_PATH), f"LEAF_SWEEP_REFERENCE_MISSING: {LEAF_SWEEP_METRICS_PATH}"

    # ---- unit-test: deterministic hash is PYTHONHASHSEED-independent + well-distributed at tiny scale
    ids_t = np.arange(1000, dtype=np.int64)
    h1 = _vectorized_entity_hash(ids_t, salt_base_test := (TIER2_SALT_BASE + FAMILY_SALT["AT"]))
    h2 = _vectorized_entity_hash(ids_t, salt_base_test)
    assert np.array_equal(h1, h2), "HASH_NONDETERMINISTIC_ACROSS_CALLS"
    buckets = (h1 % np.uint64(7)).astype(np.int64)
    counts = np.bincount(buckets, minlength=7)
    assert counts.min() >= 1000 / 7 * 0.5, f"HASH_POORLY_DISTRIBUTED: {counts.tolist()}"

    # ---- tiny synthetic corpus: BIGFAM (oversized, K=3) + SMALLFAM (small, K=1)
    n_ent_t = 48
    n_rel_t = 6
    gen = torch.Generator()
    gen.manual_seed(7)
    tmp_store = KGStore(n_ent=n_ent_t, n_rel=n_rel_t, n_dim=64, generator=gen)
    E_t, R_t = tmp_store.E, tmp_store.R

    source_to_idx_t = {"BIGFAM": 0, "SMALLFAM": 1}
    idx_to_source_t = {0: "BIGFAM", 1: "SMALLFAM"}
    k_family_t = {"BIGFAM": 3, "SMALLFAM": 1}
    base_offset_t, total_shards_t = build_family_shard_layout(source_to_idx_t, k_family_t)
    assert total_shards_t == 4, f"LAYOUT_WRONG: {base_offset_t} total={total_shards_t}"

    rng = np.random.default_rng(11)
    n_triples_t = 60
    s_t = rng.integers(0, n_ent_t, size=n_triples_t)
    p_t = rng.integers(0, n_rel_t, size=n_triples_t)
    o_t = rng.integers(0, n_ent_t, size=n_triples_t)
    src_t = (p_t % 2)  # deterministic, relation-correlated (mirrors real corpus's pure-relation structure)
    triples_t = torch.tensor(np.stack([s_t, p_t, o_t], axis=1), dtype=torch.long)

    # ---- real_code_path (F.1): ingest_shard_ids_real + query_shard_ids AGREE for the real arm
    # (closed-form assertion, no stochastic dependence)
    ingest_shards_real_t = compute_ingest_shard_ids_real(s_t, src_t, idx_to_source_t, base_offset_t,
                                                          k_family_t, TIER2_SALT_BASE)
    rel_maj_t = build_relation_majority_shard(p_t, src_t, n_rel_t, len(source_to_idx_t))
    query_shards_t = compute_query_shard_ids(s_t, p_t, rel_maj_t, idx_to_source_t, base_offset_t,
                                             k_family_t, TIER2_SALT_BASE)
    # for entries whose relation-majority family MATCHES the triple's own true family (expected: all of
    # them, since src_t = p_t % 2 is 100%-pure by construction, mirroring the real corpus's pure relations)
    agree = (ingest_shards_real_t == query_shards_t)
    assert agree.mean() >= 0.95, f"INGEST_QUERY_TIER2_DISAGREEMENT: {agree.mean()}"

    # ---- end-to-end tiny SparseHeteroShardStore: REAL arm decent recall, SCRAMBLE arm degrades
    dg_dim_t, sparsity_t = 256, 0.05
    dg_key_proj_t, dg_val_proj_t = build_dg_projections(3, 64, dg_dim_t, sparsity_t)
    dg_val_codebook_t = precompute_dg_val_codebook(dg_val_proj_t, E_t)

    ingest_shards_scr_t = compute_ingest_shard_ids_scrambled(s_t, src_t, idx_to_source_t, base_offset_t,
                                                              k_family_t, TIER2_SALT_BASE, scale=999,
                                                              scramble_seed=SCRAMBLE_SEED)
    assert not np.array_equal(ingest_shards_real_t, ingest_shards_scr_t), "SCRAMBLE_DID_NOT_CHANGE_INGEST"
    # BIGFAM per-leaf histogram preserved (same multiset, different assignment)
    big_mask = src_t == 0
    assert sorted((ingest_shards_real_t[big_mask] - base_offset_t["BIGFAM"]).tolist()) == \
        sorted((ingest_shards_scr_t[big_mask] - base_offset_t["BIGFAM"]).tolist()), \
        "SCRAMBLE_CHANGED_HISTOGRAM"

    sq_t = math.sqrt(64)
    real_store_t = SparseHeteroShardStore(dg_val_codebook_t, dg_dim_t, n_shards=total_shards_t)
    real_store_t.ingest_from_triples(s_t, p_t, o_t, ingest_shards_real_t, E_t, R_t, dg_key_proj_t, sq_t,
                                     chunk_size=17)
    scr_store_t = SparseHeteroShardStore(dg_val_codebook_t, dg_dim_t, n_shards=total_shards_t)
    scr_store_t.ingest_from_triples(s_t, p_t, o_t, ingest_shards_scr_t, E_t, R_t, dg_key_proj_t, sq_t,
                                    chunk_size=17)

    real_eval_t = eval_gate_hierarchical(real_store_t, s_t, p_t, o_t, src_t, rel_maj_t, idx_to_source_t,
                                         base_offset_t, k_family_t, TIER2_SALT_BASE, dg_key_proj_t, E_t,
                                         R_t, n_rel_t, n_query=15, query_seed=1, shortlist_k=8,
                                         ingested_triples=triples_t)
    scr_eval_t = eval_gate_hierarchical(scr_store_t, s_t, p_t, o_t, src_t, rel_maj_t, idx_to_source_t,
                                        base_offset_t, k_family_t, TIER2_SALT_BASE, dg_key_proj_t, E_t,
                                        R_t, n_rel_t, n_query=15, query_seed=1, shortlist_k=8,
                                        ingested_triples=triples_t)
    assert real_eval_t["relevant_recall"] > scr_eval_t["relevant_recall"], (
        f"SCRAMBLE_DID_NOT_DEGRADE_TIER2: real={real_eval_t['relevant_recall']} "
        f"scr={scr_eval_t['relevant_recall']}")

    def _digest(d):
        return hashlib.sha256(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()
    diff = {"real": _digest({k: v for k, v in real_eval_t.items() if k != "calibration"}),
           "scrambled": _digest({k: v for k, v in scr_eval_t.items() if k != "calibration"})}
    arms_differ = len(set(diff.values())) == len(diff)
    assert arms_differ, f"ARMS_IDENTICAL_TINY: {diff}"

    return {
        "kgstore_loader_precheck": pre, "source_field_precheck": src_pre,
        "hash_deterministic": True, "hash_bucket_counts": counts.tolist(),
        "ingest_query_tier2_agreement_rate": float(agree.mean()),
        "real_recall_tiny": real_eval_t["relevant_recall"], "scr_recall_tiny": scr_eval_t["relevant_recall"],
        "arms_differ_check": diff, "arms_differ": arms_differ,
        "real_eval_gate_smoke": {k: v for k, v in real_eval_t.items() if k != "calibration"},
        "scr_eval_gate_smoke": {k: v for k, v in scr_eval_t.items() if k != "calibration"},
    }


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        result = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                  "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                  "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps(metrics, indent=2, default=str))
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    scales = SCALES_SMOKE if args.smoke else SCALES_FULL
    expected_units = len(scales)
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    print(f"[{run_mode}] loading real CSKG entity vocab + edges (with source)...", flush=True)
    entity_to_idx = load_entity_vocab(CSKG_DIR)
    n_ent = len(entity_to_idx)
    triples_int, relation_to_idx, src_idx, source_to_idx = load_spine_edges_with_source(
        entity_to_idx, CSKG_DIR)
    n_rel = len(relation_to_idx)
    print(f"[{run_mode}] {n_ent} entities, {len(triples_int)} edges, n_rel={n_rel}, "
          f"n_families={len(source_to_idx)} ({source_to_idx}) t={time.time()-t0:.2f}s", flush=True)

    family_idx_to_name = {v: k for k, v in source_to_idx.items()}
    base_offset, total_shards = build_family_shard_layout(source_to_idx, K_FAMILY)
    print(f"[{run_mode}] K_FAMILY={K_FAMILY} base_offset={base_offset} total_shards={total_shards} "
          f"(vs Stage-2D's flat n_shards=7)", flush=True)

    rng = np.random.default_rng(DATA_SEED)
    perm = rng.permutation(len(triples_int))
    triples_shuffled = torch.from_numpy(triples_int[perm])
    src_idx_shuffled = src_idx[perm]

    gen = torch.Generator()
    gen.manual_seed(DATA_SEED)
    codebook_store = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=1024, generator=gen)
    E, R = codebook_store.E, codebook_store.R

    dg_key_proj, dg_val_proj = build_dg_projections(DATA_SEED, 1024, DG_DIM, DG_SPARSITY)
    print(f"[{run_mode}] DG projections built t={time.time()-t0:.2f}s; encoding DG_VAL_CODEBOOK "
          f"({n_ent} entities, dg_dim={DG_DIM})...", flush=True)
    dg_val_codebook = precompute_dg_val_codebook(dg_val_proj, E)
    print(f"[{run_mode}] DG_VAL_CODEBOOK done t={time.time()-t0:.2f}s", flush=True)

    # entity+family-deterministic, scale-independent -- precompute ONCE for the full shuffle, scales take
    # a prefix (same nested-prefix convention Stage-2B/2D already use)
    s_all = triples_shuffled[:, 0].numpy()
    ingest_shard_real_full = compute_ingest_shard_ids_real(s_all, src_idx_shuffled, family_idx_to_name,
                                                            base_offset, K_FAMILY, TIER2_SALT_BASE)
    print(f"[{run_mode}] ingest_shard_real_full precomputed t={time.time()-t0:.2f}s", flush=True)

    stage2d_repro: Dict = {}
    if run_mode == "full":
        print(f"[{run_mode}] Stage-2D tier-1-only repro spot-check at scale={STAGE2D_REPRO_SCALE} "
              f"starting t={time.time()-t0:.2f}s", flush=True)
        try:
            repro_unit = run_scale_unit(STAGE2D_REPRO_SCALE, triples_shuffled, src_idx_shuffled,
                                        ingest_shard_real_full, E, R, n_rel, source_to_idx,
                                        family_idx_to_name, base_offset, total_shards, dg_key_proj,
                                        dg_val_codebook, do_stage2d_repro=True)
            stage2d_ref = load_stage2d_reference()
            ref_sparse = stage2d_ref.get("per_scale", {}).get(str(STAGE2D_REPRO_SCALE), {}).get("sparse")
            ref_scr = stage2d_ref.get("per_scale", {}).get(str(STAGE2D_REPRO_SCALE), {}).get("scrambled")
            fresh_sparse = repro_unit.get("stage2d_repro_sparse")
            fresh_scr = repro_unit.get("stage2d_repro_scrambled")
            ok = True
            detail = {}
            for name, fresh, ref in [("sparse", fresh_sparse, ref_sparse),
                                     ("scrambled", fresh_scr, ref_scr)]:
                if ref is None or fresh is None:
                    ok = False
                    detail[name] = {"ok": False, "reason": "MISSING"}
                    continue
                d_rr = abs(fresh["relevant_recall"] - ref["relevant_recall"])
                d_fp = abs(fresh["false_pull_in_rate"] - ref["false_pull_in_rate"])
                pt_ok = (d_rr <= REPRO_TOLERANCE) and (d_fp <= REPRO_TOLERANCE)
                ok = ok and pt_ok
                detail[name] = {"ok": pt_ok, "fresh_rr": fresh["relevant_recall"],
                                "ref_rr": ref["relevant_recall"], "d_rr": d_rr, "d_fp": d_fp}
            stage2d_repro = {"ok": ok, "scale": STAGE2D_REPRO_SCALE, "detail": detail}
            print(f"[{run_mode}] Stage-2D repro spot-check ok={ok} t={time.time()-t0:.2f}s", flush=True)
        except Exception as e:  # noqa: BLE001 -- per-unit failure-class instrumentation, non-fatal
            stage2d_repro = {"ok": False, "failure_class": type(e).__name__, "msg": str(e)[:500]}
            print(f"[{run_mode}] Stage-2D repro spot-check FAILED: {type(e).__name__}: {e}", flush=True)

    done = completed_units(output_dir)
    unit_i = 0
    for scale in scales:
        scale_eff = min(scale, len(triples_shuffled))
        key = unit_key("scale", scale_eff)
        if key in done:
            print(f"[{run_mode}] scale={scale_eff} already complete (resume)", flush=True)
            unit_i += 1
            continue
        print(f"[{run_mode}] scale={scale_eff} starting t={time.time()-t0:.2f}s", flush=True)
        unit = run_scale_unit(scale_eff, triples_shuffled, src_idx_shuffled, ingest_shard_real_full, E, R,
                              n_rel, source_to_idx, family_idx_to_name, base_offset, total_shards,
                              dg_key_proj, dg_val_codebook, do_stage2d_repro=False)
        record_unit(output_dir, key, unit)
        unit_i += 1
        h = unit["hierarchical_sparse"]
        s = unit["scrambled_tier2"]
        print(f"[{run_mode}] scale={scale_eff} done: composed_rr={h['relevant_recall']:.3f} "
              f"composed_fp={h['false_pull_in_rate']:.3f} scr_rr={s['relevant_recall']:.3f} "
              f"margin={h['relevant_recall']-s['relevant_recall']:.3f} t={time.time()-t0:.2f}s", flush=True)
        _write_heartbeat(output_dir, unit_i, expected_units, time.time() - t0, extra={"scale": scale_eff})

    all_units = load_units(output_dir)
    per_scale = {str(u["scale"]): u for k, u in all_units.items() if k.startswith("scale|")}
    cardinality_ok = len(per_scale) == len(scales)

    def _get(scale_s, arm):
        u = per_scale.get(scale_s)
        return None if u is None else u.get(arm)

    composed_100k = _get("100000", "hierarchical_sparse")
    composed_full = _get("1213912", "hierarchical_sparse")
    scr_100k = _get("100000", "scrambled_tier2")
    scr_full = _get("1213912", "scrambled_tier2")

    checks: Dict = {}
    if composed_full:
        checks["hard_fail_skew_wins_1213912"] = bool(
            composed_full["relevant_recall"] < HARD_FAIL_RECALL_CEILING)
    if composed_full and scr_full:
        margin_full = composed_full["relevant_recall"] - scr_full["relevant_recall"]
        checks["margin_1213912"] = margin_full
        checks["hard_fail_tie_1213912"] = bool(margin_full < HARD_FAIL_TIE_GAP)
    if composed_100k and scr_100k:
        margin_100k = composed_100k["relevant_recall"] - scr_100k["relevant_recall"]
        checks["margin_100000"] = margin_100k
        checks["hard_fail_tie_100000"] = bool(margin_100k < HARD_FAIL_TIE_GAP)
    if composed_100k and composed_full and scr_100k and scr_full:
        checks["recall_ok_both"] = bool(composed_100k["relevant_recall"] >= HP_RECALL_MIN
                                        and composed_full["relevant_recall"] >= HP_RECALL_MIN)
        checks["fp_ok_both"] = bool(composed_100k["false_pull_in_rate"] <= HP_FP_MAX
                                    and composed_full["false_pull_in_rate"] <= HP_FP_MAX)
        checks["margin_ok_both"] = bool(checks["margin_100000"] >= HP_MARGIN_MIN
                                        and checks["margin_1213912"] >= HP_MARGIN_MIN)

    def _digest(d):
        if d is None:
            return None
        return hashlib.sha256(json.dumps(
            {k: v for k, v in d.items() if k not in ("ingest_s", "eval_s", "shard_diag", "calibration",
                                                      "per_family")},
            sort_keys=True, default=str).encode()).hexdigest()

    digests = {"composed_full": _digest(composed_full), "scrambled_full": _digest(scr_full),
              "composed_100k": _digest(composed_100k), "scrambled_100k": _digest(scr_100k)}
    present = {k: v for k, v in digests.items() if v is not None}
    arms_differ = len(set(present.values())) == len(present) if present else False

    hard_fail = bool(checks.get("hard_fail_skew_wins_1213912", False)
                     or checks.get("hard_fail_tie_1213912", False)
                     or (run_mode == "full" and not stage2d_repro.get("ok", True)))
    hard_pass = bool(checks.get("recall_ok_both", False) and checks.get("fp_ok_both", False)
                     and checks.get("margin_ok_both", False) and arms_differ and cardinality_ok)

    if hard_fail:
        overall_verdict = "HARD_FAIL"
    elif hard_pass:
        overall_verdict = "HARD_PASS"
    else:
        overall_verdict = "MIDDLE_BAND"

    verdict_msg = (f"{overall_verdict}: checks={checks} arms_differ={arms_differ} "
                  f"cardinality_ok={cardinality_ok} stage2d_repro_ok={stage2d_repro.get('ok')}")

    elapsed = time.time() - t0
    metrics = {
        "verdict": overall_verdict, "verdict_msg": verdict_msg[:2000], "summary": verdict_msg[:500],
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_ent": n_ent, "n_rel": n_rel, "n_families": len(source_to_idx), "source_to_idx": source_to_idx,
        "k_family": K_FAMILY, "base_offset": base_offset, "total_shards": total_shards,
        "safe_leaf_size_sparse": SAFE_LEAF_SIZE_SPARSE, "scales": scales, "dg_dim": DG_DIM,
        "dg_sparsity": DG_SPARSITY, "per_scale": per_scale, "stage2d_repro_check": stage2d_repro,
        "checks": checks, "arms_differ_check": digests, "arms_differ_verified": arms_differ,
        "cardinality_ok": cardinality_ok, "expected_n_units": expected_units, "cell_chunked": False,
        "start_marker_written": True, "crash_diagnostic_present": True, "heartbeat_present": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "empirical hierarchical shard-capacity diagnostic; per-leaf safe size MEASURED via "
                    "the leaf_capacity_sweep_v1 diagnostic (isolated single-leaf SparseHeteroShardStore, "
                    "AT-family real edges), not a closed-form floor",
        "deterministic_seeding": True,
        "calibration_check_hierarchical": "adaptive_with_discriminator_gate: DG-space tau via "
                                          "refuse_gate_calibrate_from_scores, per-scale, 50/50 internal "
                                          "split (identical mechanism Stage-2D's SPARSE/SCRAMBLED arms use)",
        "hp_scope": {"hierarchical_sparse": ["relevant_recall", "false_pull_in_rate", "scramble_margin"]},
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k != "per_scale"}, indent=2, default=str))
    per_scale_summary = {
        k: {arm: {kk: vv for kk, vv in v.items() if kk not in ("calibration",)}
           for arm, v in u.items() if arm != "scale"}
        for k, u in per_scale.items()
    }
    print(json.dumps({"per_scale_summary": per_scale_summary}, indent=2, default=str)[:10000])


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately not BaseException, see cell-template mandate
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
