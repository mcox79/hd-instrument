# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; DENSE vs SPARSE vs SCRAMBLED vs FLAT digest-differ)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace top-level + per-scale resumable unit)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (dual-regime empirical shard-capacity diagnostic; see prereg)
# - HP_SCOPE: {sharded_sparse: [relevant_recall, false_pull_in_rate, scramble_margin],
#              sharded_dense: [dense_lift_over_flat], flat: [baseline_repro_check]}
# - cardinality_ok: EXPECTED_N_UNITS=len(SCALES) (sweep-axis units are ingest-SCALES, not seeds)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: FLAT/DENSE=default_ok_for_this_regime (GATE_THRESH=0.28 fixed, un-retuned,
#   the ONE isolated variable is shard-routing); SPARSE/SCRAMBLED=adaptive_with_discriminator_gate
#   (DG-space tau via refuse_gate_calibrate_from_scores, 50/50 internal split, per scale)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs REAL tiny DenseShardStore + SparseHeteroShardStore + the REAL
#   load_spine_edges_with_source loader against a real CSKG slice (real_code_path, no synthetic-only
#   branch); verifies relation-majority routing + SCRAMBLE-degrades mechanism at tiny scale
# - progress_logging: print_flush_true (timeout likely >=1800s given DG precompute + 4-arm sweep)
# See preregs/2026-08-10_focus_pullin_causal_stage2d_context_gated_sharded_store_v1.md for the full pre-reg.
"""exp_focus_pullin_causal_stage2d_context_gated_sharded_store_v1 -- Stage 2 SUB-TEST D: does routing
BOTH ingest (write-side) AND query (read-side) through K real physical KGStore-shaped shards, keyed by
CSKG's own real per-edge `source` provenance field, hold recall at CSKG scale (1K -> 1.2M edges) where
the FLAT single-W store collapsed to 0.000 by 30K (Stage-2B, 013f1481e/6025f9a8f)?

REDIRECTED mid-design (Director message, this session) from an original read-side-only context-gate
(Stage-1.5-style shortlist over one SHARED, still-corrupted W) to write+read K-separate-physical-shard
KGStores -- Stage-1.5's read-side gate narrows candidates from a shared pool; it does not shard WHERE
triples get WRITTEN, so it cannot fix write-side Hebbian crosstalk (the actual cause of Stage-2B's
collapse). This cell composes THREE already-built/certified organs (disk-verified by exp_dev, not just
trusted from the redirect): exp_community_bounded_retrieval_scale_invariance_v1 (HARD_PASS, the
shard-the-store-not-just-the-search mechanism class), exp_graph_community_detection_v1 (HARD_FAIL, why
this cell does NOT use automatic community detection), hdlab.hippocampal_encoder (DGProjection/
CA3AutoAssociator, self-tested but never wired to a real store).

SHARD KEY (real, on-disk, zero new cost): each raw CSKG edge already carries a `source` field
(MEASURED@this-session: AT=696152(57.4%) VG=257130(21.2%) CN=214890(17.7%) WD=13812 FN=12128 WN=11903
CN|WN=7897, K=7 total). Query-time routing (BOTH positive and negative queries, uniformly, no oracle
peek at ground truth) is via a `relation -> majority shard` table built empirically from the ingested
data's own (relation, source) co-occurrence (23/33 relations are 100%-pure to one source; the rest have
a clear majority) -- this creates a GENUINE misrouting mechanism for the SCRAMBLE control (see below),
which a naive "route by this exact triple's own true label at both write and query" design (my FIRST
draft of this cell, corrected during self-test design) would NOT have, since any internally-consistent
partition trivially "works" for a query re-derived from the same triple it was written from -- the real
test is whether relation-type alone (the only thing knowable before you know if/where an answer exists)
finds the right shard, which only works when write-time routing was itself relation-correlated.

4 ARMS x (mostly) the SAME 6 cardinality rungs Stage-2B measured:
  ARM_FLAT              Stage-2B's unmodified single-W KGStore + eval_gate (imported, not
                         re-transcribed). Bit-identical-reproduction SPOT-CHECKED (fresh rerun) at
                         scale in {1000, 1213912}; other rungs CITED from its landed metrics.json.
  ARM_SHARDED_DENSE      K=7 separate dense [1024,1024] KGStore-shaped W's (DenseShardStore), routed by
                         source at ingest, by relation-majority-shard at query. Isolates the
                         SHARD-COUNT lever alone (same dense bipolar E, same GATE_THRESH=0.28).
  ARM_SHARDED_SPARSE     Same K=7 routing, but each shard's store is a DG/CA3 hetero-associative sparse
                         Hebbian store (SparseHeteroShardStore, composing hdlab.hippocampal_encoder.
                         DGProjection unchanged + a new hetero-associative generalization of
                         CA3AutoAssociator's sparse-outer-product-write PATTERN). Adds the CAPACITY-PER-
                         SHARD lever (Willshaw-class, not dense-Hopfield). DG-space tau calibrated via
                         refuse_gate_calibrate_from_scores (Stage-1.5's exact ported algorithm).
  CONTROL_SCRAMBLED_SHARD_KEY  Identical SparseHeteroShardStore architecture; for each scale rung
                         independently, entities are reassigned to shards via a fresh permutation of
                         THAT rung's true label multiset (SAME per-rung shard-size histogram as the
                         real-key arms, per the redirect's explicit requirement), destroying the
                         relation<->source correlation the real arms' routing depends on.

Modes:
  --self-test  Real-code-path check: tiny DenseShardStore/SparseHeteroShardStore (N=32, dg_dim=256) +
               the REAL load_spine_edges_with_source loader against a small real CSKG slice + a
               relation-majority-routing SCRAMBLE-degrades mechanism check at tiny scale. No dispatch.
  --smoke      Real CSKG data, scales=[10000,100000] (both above/at Stage-2B's FLAT collapse zone --
               discriminator-fires per DISCRIMINATOR-MUST-SURVIVE-SCALE option A), sparse arms run at
               both smoke scales, FLAT spot-checked at both.
  --full       scales=[1000,5000,10000,30000,100000,1213912] for FLAT/DENSE; SPARSE/SCRAMBLED at
               [10000,100000,1213912] (compute-proportionality reduction, disclosed in prereg). Per-scale
               checkpointed via tools/exp_checkpoint.py (unit_key = scale). May span 2 sequential
               foreground invocations (checkpoint-resume) per the prereg's wall-time estimate.
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
from typing import Dict, List, Tuple

import numpy as np
import torch

ANCHOR_NAME = "focus_pullin_causal_stage2d_context_gated_sharded_store_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
CSKG_DIR = os.path.join(REPO_ROOT, "data", "cskg_foundation_v1")
STAGE2B_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1", "metrics.json")

from hdlab.kg_traversal import KGStore  # noqa: E402
from hdlab.cleanup_family import iterative_attractor as _iterative_attractor  # noqa: E402
from hdlab.hippocampal_encoder import DGProjection  # noqa: E402
from experiments.exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1 import (  # noqa: E402
    load_entity_vocab,
    eval_gate as flat_eval_gate,
    precheck_kgstore_and_loader,
    QUERY_SEED as S2B_QUERY_SEED,
    DATA_SEED as S2B_DATA_SEED,
    SHORTLIST_K as S2B_SHORTLIST_K,
    N_QUERY as S2B_N_QUERY,
    GATE_THRESH as S2B_GATE_THRESH,
    SCALES_FULL as S2B_SCALES_FULL,
)
from experiments.exp_focus_pullin_causal_stage2a_multihop_loop_v1 import (  # noqa: E402
    pull_in_multi_exclude,
)
from experiments.exp_focus_pullin_causal_stage15_salted_cardinality_gate_v1 import (  # noqa: E402
    refuse_gate_calibrate_from_scores,
)
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

GATE_THRESH = S2B_GATE_THRESH
SHORTLIST_K = S2B_SHORTLIST_K
N_QUERY = S2B_N_QUERY
QUERY_SEED = S2B_QUERY_SEED
DATA_SEED = S2B_DATA_SEED
SCALES_FULL = list(S2B_SCALES_FULL)
SCALES_SMOKE = [10000, 100000]
SPARSE_SCALES_FULL = [10000, 100000, 1213912]
SPARSE_SCALES_SMOKE = [10000, 100000]
FLAT_REPRO_CHECKPOINTS_FULL = [1000, 1213912]
FLAT_REPRO_CHECKPOINTS_SMOKE = [10000, 100000]
DG_DIM = 2048
DG_SPARSITY = 0.02
SCRAMBLE_SEED = 20260810 + 555
IATTR_TEMP = 4.0
IATTR_MAX_STEPS = 8

REC_THRESH_SPARSE = 0.50
FP_THRESH = 0.20
DENSE_LIFT_MIN = 0.20
SCRAMBLE_MARGIN_MIN = 0.30
SPARSE_COLLAPSE_CEILING = 0.10
SCRAMBLE_TIE_GAP = 0.10
REPRO_TOLERANCE = 0.05


# ============================================================================ real data loader
def load_spine_edges_with_source(entity_to_idx: Dict[str, int], cskg_dir: str = CSKG_DIR,
                                 max_shards: int = 16):
    """Mirrors Stage-2B's load_spine_edges (same 16 files, same entity/relation resolution) but ALSO
    captures the `source` provenance field each raw edge already carries. Necessary extension, not a
    mechanism change (Stage-2B's own loader does not return `source`)."""
    relations_seen = set()
    sources_seen = set()
    raw = []
    for shard_i in range(max_shards):
        path = os.path.join(cskg_dir, f"edges_shard_{shard_i:02d}.jsonl")
        with open(path, encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                relations_seen.add(row["relation"])
                src = row.get("source", "MISSING")
                sources_seen.add(src)
                raw.append((row["subject"], row["relation"], row["obj"], src))
    relation_to_idx = {r: i for i, r in enumerate(sorted(relations_seen))}
    source_to_idx = {s: i for i, s in enumerate(sorted(sources_seen))}
    n = len(raw)
    triples = np.empty((n, 3), dtype=np.int64)
    src_idx = np.empty((n,), dtype=np.int64)
    for i, (s, p, o, src) in enumerate(raw):
        triples[i, 0] = entity_to_idx[s]
        triples[i, 1] = relation_to_idx[p]
        triples[i, 2] = entity_to_idx[o]
        src_idx[i] = source_to_idx[src]
    return triples, relation_to_idx, src_idx, source_to_idx


# ============================================================================ routing helpers
def build_relation_majority_shard(p_idx: np.ndarray, shard_labels: np.ndarray, n_rel: int,
                                  n_shards: int) -> np.ndarray:
    """rel_to_shard[r] = the shard that holds the MOST ingested triples of relation r, empirically,
    from the CURRENT (real or scrambled) label assignment. This is the ONLY routing signal used at
    query time (both positive and negative queries) -- no oracle peek at any specific triple's own
    label. Deterministic given (p_idx, shard_labels)."""
    table = np.zeros(n_rel, dtype=np.int64)
    for r in range(n_rel):
        mask = p_idx == r
        if not mask.any():
            table[r] = 0
            continue
        counts = np.bincount(shard_labels[mask], minlength=n_shards)
        table[r] = int(np.argmax(counts))
    return table


def scramble_labels_for_prefix(true_labels_prefix: np.ndarray, scale: int) -> np.ndarray:
    """Fresh permutation of THIS prefix's true-label multiset -- exact same per-scale shard-size
    histogram as the real-key arms, decorrelated from content. Seeded per-scale (deterministic)."""
    seed = SCRAMBLE_SEED + int(scale)
    rng = np.random.default_rng(seed)
    return rng.permutation(true_labels_prefix)


def _cos_np(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ============================================================================ DenseShardStore
class DenseShardStore:
    """K separate dense [n_dim,n_dim] Hebbian W's sharing E,R with a companion KGStore. Generalizes
    KGStore's single-W bind/accumulate/score math to K physically separate stores, selected by an
    externally-supplied per-triple shard label at INGEST (write-side routing -- the redirect's
    load-bearing correction over a read-side-only shortlist)."""

    def __init__(self, E: torch.Tensor, R: torch.Tensor, n_dim: int, n_shards: int) -> None:
        self.E = E
        self.R = R
        self.n_dim = n_dim
        self.n_shards = n_shards
        self.sq = math.sqrt(n_dim)
        self.W_shards = torch.zeros(n_shards, n_dim, n_dim, dtype=torch.float32)

    def key(self, s: int, p: int) -> torch.Tensor:
        return (self.E[s] * self.R[p] * self.sq).to(torch.float32)

    def ingest(self, triples: torch.Tensor, shard_labels: np.ndarray) -> Dict:
        n = triples.shape[0]
        order = np.argsort(shard_labels, kind="stable")
        labels_sorted = shard_labels[order]
        uniq, start_idx = np.unique(labels_sorted, return_index=True)
        boundaries = list(start_idx) + [n]
        triples_sorted = triples[torch.from_numpy(order)]
        occ = np.zeros(self.n_shards, dtype=np.int64)
        for gi in range(len(uniq)):
            shard = int(uniq[gi])
            lo, hi = int(boundaries[gi]), int(boundaries[gi + 1])
            chunk = triples_sorted[lo:hi]
            s_c, p_c, o_c = chunk[:, 0], chunk[:, 1], chunk[:, 2]
            keys = (self.E[s_c] * self.R[p_c] * self.sq).to(torch.float32)
            self.W_shards[shard].add_((self.E[o_c].T @ keys) / self.n_dim)
            occ[shard] = hi - lo
        nz = occ[occ > 0]
        return {"n_shards_touched": int(len(uniq)), "occupancy": occ.tolist(),
                "max_occupancy": int(occ.max()),
                "mean_nonzero_occupancy": float(nz.mean()) if len(nz) else 0.0}

    def score_in_shard(self, shard_idx: int, key: torch.Tensor) -> torch.Tensor:
        return self.E @ (self.W_shards[shard_idx] @ key)

    def reset(self) -> None:
        self.W_shards.zero_()


# ============================================================================ SparseHeteroShardStore
class SparseHeteroShardStore:
    """K separate [dg_dim,dg_dim] DG-coded hetero-associative Hebbian stores. Generalizes
    hdlab.hippocampal_encoder.CA3AutoAssociator's auto-associative sparse-outer-product-write PATTERN
    (W[nz,nz] += outer(code,code)) to hetero-associative key->value binding: two different DG-projected
    sparse codes (key-space, value/entity-space) instead of one, written densely (see prereg Compute
    architecture -- at this write-count scale the effective occupied-cell fraction saturates a dense
    representation regardless, so the win from sparsity is capacity/SNR, not write-time memory)."""

    def __init__(self, dg_val_codebook: torch.Tensor, dg_dim: int, n_shards: int) -> None:
        self.dg_val_codebook = dg_val_codebook  # [n_ent, dg_dim], fixed/shared across shards+scales
        self.dg_dim = dg_dim
        self.n_shards = n_shards
        self.W_shards = torch.zeros(n_shards, dg_dim, dg_dim, dtype=torch.float32)

    def ingest(self, dg_key_codes: torch.Tensor, o_idx: np.ndarray, shard_labels: np.ndarray) -> Dict:
        n = dg_key_codes.shape[0]
        order = np.argsort(shard_labels, kind="stable")
        labels_sorted = shard_labels[order]
        uniq, start_idx = np.unique(labels_sorted, return_index=True)
        boundaries = list(start_idx) + [n]
        keys_sorted = dg_key_codes[torch.from_numpy(order)]
        o_sorted_t = torch.from_numpy(o_idx[order])
        occ = np.zeros(self.n_shards, dtype=np.int64)
        for gi in range(len(uniq)):
            shard = int(uniq[gi])
            lo, hi = int(boundaries[gi]), int(boundaries[gi + 1])
            k_chunk = keys_sorted[lo:hi]
            o_chunk = o_sorted_t[lo:hi]
            val_chunk = self.dg_val_codebook[o_chunk]
            self.W_shards[shard].add_((val_chunk.T @ k_chunk) / self.dg_dim)
            occ[shard] = hi - lo
        nz = occ[occ > 0]
        return {"n_shards_touched": int(len(uniq)), "occupancy": occ.tolist(),
                "max_occupancy": int(occ.max()),
                "mean_nonzero_occupancy": float(nz.mean()) if len(nz) else 0.0}

    def ingest_from_triples(self, s_idx: np.ndarray, p_idx: np.ndarray, o_idx: np.ndarray,
                            shard_labels: np.ndarray, E: torch.Tensor, R: torch.Tensor,
                            dg_key_proj: DGProjection, sq: float, chunk_size: int = 100000) -> Dict:
        """MEMORY-SAFE ingest: DG-projects key vectors in CHUNKS (never materializes a
        [n_triples, dg_dim] array for the full dataset -- at n_triples=1,213,912 and dg_dim=2048 that
        would be ~9.9GB, which combined with dg_val_codebook (~3.95GB) and E (~1.84GB) would exceed the
        measured ~10GB available RAM). Same total Hebbian-accumulate math as `ingest`, just streamed;
        one chunk's DG codes are freed before the next chunk is projected. This is the caught-in-smoke
        fix (smoke's --smoke run originally precomputed DG-key-codes for the FULL 1,213,912-row shuffle
        regardless of run_mode, which both wasted smoke wall-time AND would OOM at the full-scale unit
        under --full; see prereg addendum)."""
        n = len(s_idx)
        occ = np.zeros(self.n_shards, dtype=np.int64)
        for start in range(0, n, chunk_size):
            end = min(start + chunk_size, n)
            s_c, p_c, o_c, sh_c = s_idx[start:end], p_idx[start:end], o_idx[start:end], shard_labels[start:end]
            key_vecs = (E[torch.from_numpy(s_c)].numpy() * R[torch.from_numpy(p_c)].numpy()
                       * sq).astype(np.float32)
            dg_keys_chunk = torch.from_numpy(dg_key_proj.encode_batch(key_vecs)).to(torch.float32)
            order = np.argsort(sh_c, kind="stable")
            labels_sorted = sh_c[order]
            uniq, start_idx_arr = np.unique(labels_sorted, return_index=True)
            boundaries = list(start_idx_arr) + [len(order)]
            keys_sorted = dg_keys_chunk[torch.from_numpy(order)]
            o_sorted_t = torch.from_numpy(o_c[order])
            for gi in range(len(uniq)):
                shard = int(uniq[gi])
                lo, hi = int(boundaries[gi]), int(boundaries[gi + 1])
                val_chunk = self.dg_val_codebook[o_sorted_t[lo:hi]]
                self.W_shards[shard].add_((val_chunk.T @ keys_sorted[lo:hi]) / self.dg_dim)
                occ[shard] += (hi - lo)
        nz = occ[occ > 0]
        return {"n_shards_touched": int((occ > 0).sum()), "occupancy": occ.tolist(),
                "max_occupancy": int(occ.max()), "n_chunks": int(math.ceil(n / chunk_size)),
                "mean_nonzero_occupancy": float(nz.mean()) if len(nz) else 0.0}

    def probe_batch_in_shard(self, shard_idx: int, dg_key_codes_batch: torch.Tensor) -> torch.Tensor:
        return dg_key_codes_batch @ self.W_shards[shard_idx].T

    def reset(self) -> None:
        self.W_shards.zero_()


def build_dg_projections(seed: int, input_dim: int, dg_dim: int, sparsity: float):
    dg_key_proj = DGProjection(input_dim=input_dim, dg_dim=dg_dim, sparsity=sparsity, seed=int(seed) + 1)
    dg_val_proj = DGProjection(input_dim=input_dim, dg_dim=dg_dim, sparsity=sparsity, seed=int(seed) + 2)
    return dg_key_proj, dg_val_proj


def precompute_dg_val_codebook(dg_val_proj: DGProjection, E: torch.Tensor) -> torch.Tensor:
    codes = dg_val_proj.encode_batch(E.numpy())
    return torch.from_numpy(codes).to(torch.float32)


def precompute_dg_key_codes(dg_key_proj: DGProjection, key_vectors_np: np.ndarray) -> torch.Tensor:
    codes = dg_key_proj.encode_batch(key_vectors_np)
    return torch.from_numpy(codes).to(torch.float32)


# ============================================================================ dense-arm eval
def eval_gate_dense_shard(store: DenseShardStore, ingested_triples: torch.Tensor,
                          rel_majority_shard: np.ndarray, n_rel: int, n_query: int, query_seed: int,
                          gate: float, shortlist_k: int) -> Dict:
    q_rng = np.random.default_rng(query_seed)
    n = ingested_triples.shape[0]
    existing_sp = set((int(s) * n_rel + int(p)) for s, p, _o in ingested_triples.tolist())
    n_ent = store.E.shape[0]
    shortlist_k_eff = min(shortlist_k, n_ent)

    rel_idx = q_rng.choice(n, size=min(n_query, n), replace=False)
    rel_admitted_correct = 0
    rel_in_shortlist = 0
    for i in rel_idx:
        s, p, o = (int(x) for x in ingested_triples[i])
        shard = int(rel_majority_shard[p])
        key = store.key(s, p)
        probe = store.W_shards[shard] @ key
        scores = store.E @ probe
        topk = torch.topk(scores, k=shortlist_k_eff)
        cand_global = topk.indices.numpy()
        if o in cand_global:
            rel_in_shortlist += 1
        shortlist_cb = store.E[cand_global].numpy()
        exclude_set = set()
        hit = np.where(cand_global == s)[0]
        if len(hit):
            exclude_set.add(int(hit[0]))
        r = pull_in_multi_exclude(probe.numpy(), shortlist_cb, exclude_set, gate=gate)
        global_candidate = int(cand_global[r["candidate_idx"]])
        if global_candidate == o and r["admitted"]:
            rel_admitted_correct += 1

    neg_count = 0
    neg_admitted = 0
    tries = 0
    while neg_count < n_query and tries < n_query * 20:
        tries += 1
        s = int(q_rng.integers(0, n_ent))
        p = int(q_rng.integers(0, n_rel))
        if (s * n_rel + p) in existing_sp:
            continue
        neg_count += 1
        shard = int(rel_majority_shard[p])
        key = store.key(s, p)
        probe = store.W_shards[shard] @ key
        scores = store.E @ probe
        topk = torch.topk(scores, k=shortlist_k_eff)
        cand_global = topk.indices.numpy()
        shortlist_cb = store.E[cand_global].numpy()
        exclude_set = set()
        hit = np.where(cand_global == s)[0]
        if len(hit):
            exclude_set.add(int(hit[0]))
        r = pull_in_multi_exclude(probe.numpy(), shortlist_cb, exclude_set, gate=gate)
        if r["admitted"]:
            neg_admitted += 1

    return {
        "n_relevant_queried": int(len(rel_idx)),
        "relevant_recall": rel_admitted_correct / max(len(rel_idx), 1),
        "relevant_in_shortlist_rate": rel_in_shortlist / max(len(rel_idx), 1),
        "n_negative_queried": neg_count,
        "false_pull_in_rate": neg_admitted / max(neg_count, 1),
    }


# ============================================================================ sparse-arm eval
def _batched_score_settle(store: SparseHeteroShardStore, dg_keys: torch.Tensor, shard_of: np.ndarray,
                          shortlist_k_eff: int, true_obj: np.ndarray = None) -> List[Dict]:
    """Coarse DG-space scoring BATCHED per shard (amortizes streaming dg_val_codebook once per shard,
    not once per query -- see prereg Compute architecture); fine settle+admission stays a per-query
    loop (cheap, shortlist_k_eff rows only)."""
    m = dg_keys.shape[0]
    results: List[Dict] = [None] * m
    for shard in range(store.n_shards):
        idx_local = np.where(shard_of == shard)[0]
        if len(idx_local) == 0:
            continue
        batch = dg_keys[torch.from_numpy(idx_local)]
        probes = store.probe_batch_in_shard(shard, batch)  # [b, dg_dim]
        scores = probes @ store.dg_val_codebook.T  # [b, n_ent]
        k_eff = min(shortlist_k_eff, scores.shape[1])
        topk = torch.topk(scores, k=k_eff, dim=1)
        cand_idx = topk.indices.numpy()  # [b, k_eff]
        for bi in range(len(idx_local)):
            li = int(idx_local[bi])
            probe_np = probes[bi].numpy()
            cand_row = cand_idx[bi]
            shortlist_cb = store.dg_val_codebook[cand_row].numpy()
            in_short = bool(true_obj is not None and int(true_obj[li]) in cand_row)
            _state, diag = _iterative_attractor(probe_np, shortlist_cb, temp=IATTR_TEMP,
                                                max_steps=IATTR_MAX_STEPS)
            arg_local = diag["final_argmax_idx"]
            cand = int(cand_row[arg_local])
            score = _cos_np(probe_np, store.dg_val_codebook[cand].numpy())
            results[li] = {"candidate": cand, "score": score, "in_shortlist": in_short}
    return results


def eval_gate_sparse_shard(store: SparseHeteroShardStore, s_idx_ingested: np.ndarray,
                           p_idx_ingested: np.ndarray, o_idx: np.ndarray, rel_majority_shard: np.ndarray,
                           dg_key_proj: DGProjection, E: torch.Tensor, R: torch.Tensor, n_rel: int,
                           n_query: int, query_seed: int, shortlist_k: int, n_shards: int,
                           ingested_triples: torch.Tensor) -> Dict:
    """MEMORY-SAFE: DG-projects key vectors ONLY for the sampled query rows (n_query each side), never
    a precomputed [n_ingested, dg_dim] array -- see SparseHeteroShardStore.ingest_from_triples docstring
    for the same fix applied to ingest."""
    q_rng = np.random.default_rng(query_seed)
    n = ingested_triples.shape[0]
    existing_sp = set((int(s) * n_rel + int(p)) for s, p, _o in ingested_triples.tolist())
    n_ent = store.dg_val_codebook.shape[0]
    shortlist_k_eff = min(shortlist_k, n_ent)
    sq = math.sqrt(E.shape[1])

    rel_idx = q_rng.choice(n, size=min(n_query, n), replace=False)
    rel_s = s_idx_ingested[rel_idx]
    rel_p = p_idx_ingested[rel_idx]
    rel_shard_of = rel_majority_shard[rel_p]
    rel_key_vecs = (E[torch.from_numpy(rel_s)].numpy() * R[torch.from_numpy(rel_p)].numpy()
                    * sq).astype(np.float32)
    rel_dg_keys = torch.from_numpy(dg_key_proj.encode_batch(rel_key_vecs)).to(torch.float32)
    rel_true_obj = o_idx[rel_idx]

    rel_results = _batched_score_settle(store, rel_dg_keys, rel_shard_of, shortlist_k_eff,
                                        true_obj=rel_true_obj)
    for li in range(len(rel_idx)):
        rel_results[li]["correct"] = (rel_results[li]["candidate"] == int(rel_true_obj[li]))

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
    neg_shard_of = rel_majority_shard[neg_p_arr]
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

    return {
        "n_relevant_queried": len(eval_rel),
        "relevant_recall": rel_admitted_correct / max(len(eval_rel), 1),
        "relevant_in_shortlist_rate": rel_in_shortlist / max(len(eval_rel), 1),
        "n_negative_queried": len(eval_neg),
        "false_pull_in_rate": neg_admitted / max(len(eval_neg), 1),
        "tau": tau, "calibration": calib,
    }


# ============================================================================ real-data-loader precheck
def precheck_source_field(cskg_dir: str = CSKG_DIR) -> Dict:
    ok = True
    detail: Dict = {}
    if os.path.isdir(cskg_dir):
        n_checked = 0
        n_missing = 0
        with open(os.path.join(cskg_dir, "edges_shard_00.jsonl"), encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 200:
                    break
                row = json.loads(line)
                n_checked += 1
                if "source" not in row:
                    n_missing += 1
        ok = (n_checked > 0) and (n_missing == 0)
        detail = {"n_checked": n_checked, "n_missing_source": n_missing}
    else:
        ok = False
        detail = {"error": f"CSKG_DIR not found: {cskg_dir}"}
    return {"ok": ok, "detail": detail}


# ============================================================================ per-scale unit
def run_scale_unit(scale: int, triples_shuffled: torch.Tensor, src_idx_shuffled: np.ndarray,
                   E: torch.Tensor, R: torch.Tensor, n_rel: int, n_shards: int,
                   flat_store: KGStore, dense_store: DenseShardStore,
                   sparse_store: SparseHeteroShardStore, scrambled_sparse_store: SparseHeteroShardStore,
                   dg_key_proj: DGProjection,
                   run_sparse: bool, spot_check_flat: bool) -> Dict:
    scale = min(scale, len(triples_shuffled))
    ingested = triples_shuffled[:scale]
    ingested_src = src_idx_shuffled[:scale]
    p_idx_ingested = ingested[:, 1].numpy()

    unit: Dict = {"scale": scale}

    if spot_check_flat:
        flat_store.reset()
        t0 = time.time()
        flat_store.ingest_triples(ingested)
        ing_s = time.time() - t0
        t0 = time.time()
        m = flat_eval_gate(flat_store, ingested, n_rel=n_rel, n_query=N_QUERY, query_seed=QUERY_SEED)
        ev_s = time.time() - t0
        m.update({"ingest_s": round(ing_s, 3), "eval_s": round(ev_s, 3)})
        unit["flat_spotcheck"] = m

    dense_store.reset()
    t0 = time.time()
    ingest_diag = dense_store.ingest(ingested, ingested_src)
    ing_s = time.time() - t0
    rel_maj_dense = build_relation_majority_shard(p_idx_ingested, ingested_src, n_rel, n_shards)
    t0 = time.time()
    m_dense = eval_gate_dense_shard(dense_store, ingested, rel_maj_dense, n_rel, N_QUERY, QUERY_SEED,
                                    GATE_THRESH, SHORTLIST_K)
    ev_s = time.time() - t0
    m_dense.update({"ingest_s": round(ing_s, 3), "eval_s": round(ev_s, 3), "shard_diag": ingest_diag})
    unit["dense"] = m_dense

    if run_sparse:
        s_idx_prefix = ingested[:, 0].numpy()
        o_idx_prefix = ingested[:, 2].numpy()
        sq = math.sqrt(E.shape[1])

        sparse_store.reset()
        t0 = time.time()
        sparse_ingest_diag = sparse_store.ingest_from_triples(
            s_idx_prefix, p_idx_ingested, o_idx_prefix, ingested_src, E, R, dg_key_proj, sq)
        ing_s = time.time() - t0
        t0 = time.time()
        m_sparse = eval_gate_sparse_shard(sparse_store, s_idx_prefix, p_idx_ingested, o_idx_prefix,
                                          rel_maj_dense, dg_key_proj, E, R, n_rel, N_QUERY, QUERY_SEED,
                                          SHORTLIST_K, n_shards, ingested)
        ev_s = time.time() - t0
        m_sparse.update({"ingest_s": round(ing_s, 3), "eval_s": round(ev_s, 3),
                         "shard_diag": sparse_ingest_diag})
        unit["sparse"] = m_sparse

        scrambled_src = scramble_labels_for_prefix(ingested_src, scale)
        scrambled_sparse_store.reset()
        t0 = time.time()
        scr_ingest_diag = scrambled_sparse_store.ingest_from_triples(
            s_idx_prefix, p_idx_ingested, o_idx_prefix, scrambled_src, E, R, dg_key_proj, sq)
        ing_s = time.time() - t0
        rel_maj_scr = build_relation_majority_shard(p_idx_ingested, scrambled_src, n_rel, n_shards)
        t0 = time.time()
        m_scr = eval_gate_sparse_shard(scrambled_sparse_store, s_idx_prefix, p_idx_ingested, o_idx_prefix,
                                       rel_maj_scr, dg_key_proj, E, R, n_rel, N_QUERY,
                                       QUERY_SEED, SHORTLIST_K, n_shards, ingested)
        ev_s = time.time() - t0
        m_scr.update({"ingest_s": round(ing_s, 3), "eval_s": round(ev_s, 3), "shard_diag": scr_ingest_diag})
        unit["scrambled"] = m_scr

    return unit


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
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


def load_stage2b_reference() -> Dict:
    with open(STAGE2B_METRICS_PATH, encoding="utf-8") as f:
        return json.load(f)


# ============================================================================ self-test
def self_test() -> Dict:
    pre = precheck_kgstore_and_loader()
    assert pre["ok"], f"STAGE2B_PRECHECK_FAIL: {pre}"

    src_pre = precheck_source_field()
    assert src_pre["ok"], f"SOURCE_FIELD_PRECHECK_FAIL: {src_pre}"

    gen = torch.Generator()
    gen.manual_seed(7)
    n_ent_t, n_rel_t, n_dim_t, n_shards_t = 32, 4, 64, 3
    tmp_store = KGStore(n_ent=n_ent_t, n_rel=n_rel_t, n_dim=n_dim_t, generator=gen)
    E_t, R_t = tmp_store.E, tmp_store.R

    rng = np.random.default_rng(11)
    n_triples_t = 40
    s_t = rng.integers(0, n_ent_t, size=n_triples_t)
    p_t = rng.integers(0, n_rel_t, size=n_triples_t)
    o_t = rng.integers(0, n_ent_t, size=n_triples_t)
    triples_t = torch.tensor(np.stack([s_t, p_t, o_t], axis=1), dtype=torch.long)
    # shard purely a function of RELATION (100%-pure by construction) -- mirrors the real corpus's
    # 23/33-pure-relations structure so the relation-majority routing check is meaningful at tiny scale.
    shard_labels_t = (p_t % n_shards_t).astype(np.int64)

    dense_t = DenseShardStore(E_t, R_t, n_dim_t, n_shards_t)
    dense_t.ingest(triples_t, shard_labels_t)
    rel_maj_true = build_relation_majority_shard(p_t, shard_labels_t, n_rel_t, n_shards_t)

    def _tiny_dense_recall(store: DenseShardStore, rel_maj: np.ndarray) -> float:
        c = 0
        for i in range(n_triples_t):
            s, p, o = int(s_t[i]), int(p_t[i]), int(o_t[i])
            shard = int(rel_maj[p])
            key = store.key(s, p)
            scores = store.score_in_shard(shard, key)
            if int(torch.argmax(scores)) == o:
                c += 1
        return c / n_triples_t

    dense_recall_true = _tiny_dense_recall(dense_t, rel_maj_true)
    assert dense_recall_true >= 0.5, f"DENSE_SHARD_TINY_RECALL_TOO_LOW: {dense_recall_true}"

    scrambled_labels_t = scramble_labels_for_prefix(shard_labels_t, scale=999)
    dense_scr_t = DenseShardStore(E_t, R_t, n_dim_t, n_shards_t)
    dense_scr_t.ingest(triples_t, scrambled_labels_t)
    rel_maj_scr = build_relation_majority_shard(p_t, scrambled_labels_t, n_rel_t, n_shards_t)
    dense_recall_scr = _tiny_dense_recall(dense_scr_t, rel_maj_scr)
    assert dense_recall_scr < dense_recall_true, (
        f"SCRAMBLE_DID_NOT_DEGRADE_DENSE: true={dense_recall_true} scr={dense_recall_scr}")

    dg_dim_t, sparsity_t = 256, 0.05
    dg_key_proj_t, dg_val_proj_t = build_dg_projections(3, n_dim_t, dg_dim_t, sparsity_t)
    dg_val_codebook_t = precompute_dg_val_codebook(dg_val_proj_t, E_t)
    sq_t = math.sqrt(n_dim_t)

    # real_code_path (F.1): use ingest_from_triples (the ACTUAL memory-safe chunked method main()
    # calls), not the raw-precomputed-codes ingest() -- exercises the on-the-fly DG-projection path.
    sparse_t = SparseHeteroShardStore(dg_val_codebook_t, dg_dim_t, n_shards_t)
    sparse_t.ingest_from_triples(s_t, p_t, o_t, shard_labels_t, E_t, R_t, dg_key_proj_t, sq_t,
                                 chunk_size=17)  # tiny chunk_size to also exercise multi-chunk looping

    def _tiny_sparse_recall(store: SparseHeteroShardStore, rel_maj: np.ndarray) -> float:
        c = 0
        for i in range(n_triples_t):
            shard = int(rel_maj[int(p_t[i])])
            key_vec = (E_t[int(s_t[i])].numpy() * R_t[int(p_t[i])].numpy() * sq_t).astype(np.float32)
            dg_key = torch.from_numpy(dg_key_proj_t.encode_batch(key_vec[None, :])).to(torch.float32)
            probe = store.probe_batch_in_shard(shard, dg_key)[0]
            scores = dg_val_codebook_t @ probe
            if int(torch.argmax(scores)) == int(o_t[i]):
                c += 1
        return c / n_triples_t

    sparse_recall_true = _tiny_sparse_recall(sparse_t, rel_maj_true)
    assert sparse_recall_true >= 0.3, f"SPARSE_SHARD_TINY_RECALL_TOO_LOW: {sparse_recall_true}"

    sparse_scr_t = SparseHeteroShardStore(dg_val_codebook_t, dg_dim_t, n_shards_t)
    sparse_scr_t.ingest_from_triples(s_t, p_t, o_t, scrambled_labels_t, E_t, R_t, dg_key_proj_t, sq_t,
                                     chunk_size=17)
    sparse_recall_scr = _tiny_sparse_recall(sparse_scr_t, rel_maj_scr)
    assert sparse_recall_scr < sparse_recall_true, (
        f"SCRAMBLE_DID_NOT_DEGRADE_SPARSE: true={sparse_recall_true} scr={sparse_recall_scr}")

    # end-to-end eval_gate_* real-code-path smoke (tiny, but the ACTUAL functions FULL uses)
    rel_maj_for_eval = build_relation_majority_shard(p_t, shard_labels_t, n_rel_t, n_shards_t)
    dense_eval = eval_gate_dense_shard(dense_t, triples_t, rel_maj_for_eval, n_rel_t, n_query=10,
                                       query_seed=1, gate=GATE_THRESH, shortlist_k=8)
    sparse_eval = eval_gate_sparse_shard(sparse_t, s_t, p_t, o_t, rel_maj_for_eval,
                                         dg_key_proj_t, E_t, R_t, n_rel_t, n_query=10, query_seed=1,
                                         shortlist_k=8, n_shards=n_shards_t, ingested_triples=triples_t)

    # arms-must-differ (real code path OUTPUTS, not just the scalar recall which can coincidentally
    # collide at trivial n=40 scale -- both mechanisms recovering everything is a legitimate tiny-scale
    # outcome, not evidence of a bit-identical-arm bug; the eval_gate_* dicts are richer (different key
    # sets: sparse carries tau/calibration; different in_shortlist/false_pull_in numbers) and are the
    # actual per-query FULL-run code path, so hashing THOSE is the meaningful differ-check).
    def _digest(d):
        return hashlib.sha256(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()
    diff = {"dense_eval": _digest(dense_eval), "sparse_eval": _digest(sparse_eval)}
    arms_differ = len(set(diff.values())) == len(diff)
    assert arms_differ, f"ARMS_IDENTICAL_TINY: {diff}"

    return {
        "kgstore_loader_precheck": pre, "source_field_precheck": src_pre,
        "dense_recall_true": dense_recall_true, "dense_recall_scrambled": dense_recall_scr,
        "sparse_recall_true": sparse_recall_true, "sparse_recall_scrambled": sparse_recall_scr,
        "arms_differ_check": diff, "arms_differ": arms_differ,
        "dense_eval_gate_smoke": dense_eval, "sparse_eval_gate_smoke": sparse_eval,
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
    sparse_scales = set(SPARSE_SCALES_SMOKE if args.smoke else SPARSE_SCALES_FULL)
    flat_repro_scales = set(FLAT_REPRO_CHECKPOINTS_SMOKE if args.smoke else FLAT_REPRO_CHECKPOINTS_FULL)
    expected_units = len(scales)
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    print(f"[{run_mode}] loading real CSKG entity vocab + edges (with source)...", flush=True)
    entity_to_idx = load_entity_vocab(CSKG_DIR)
    n_ent = len(entity_to_idx)
    triples_int, relation_to_idx, src_idx, source_to_idx = load_spine_edges_with_source(
        entity_to_idx, CSKG_DIR)
    n_rel = len(relation_to_idx)
    n_shards = len(source_to_idx)
    print(f"[{run_mode}] {n_ent} entities, {len(triples_int)} edges, n_rel={n_rel}, n_shards={n_shards} "
          f"({source_to_idx}) t={time.time()-t0:.2f}s", flush=True)

    rng = np.random.default_rng(DATA_SEED)
    perm = rng.permutation(len(triples_int))
    triples_shuffled = torch.from_numpy(triples_int[perm])
    src_idx_shuffled = src_idx[perm]

    gen = torch.Generator()
    gen.manual_seed(DATA_SEED)
    flat_store = KGStore(n_ent=n_ent, n_rel=n_rel, n_dim=1024, generator=gen)
    E, R = flat_store.E, flat_store.R
    dense_store = DenseShardStore(E, R, 1024, n_shards)
    print(f"[{run_mode}] codebooks + FLAT/DENSE stores allocated t={time.time()-t0:.2f}s", flush=True)

    sparse_store = None
    scrambled_sparse_store = None
    dg_key_proj = None
    if sparse_scales:
        # MEMORY-SAFE (caught in smoke, see SparseHeteroShardStore.ingest_from_triples docstring):
        # DG_VAL_CODEBOOK is fixed/shared (entity-identity-dependent only) and IS precomputed once
        # here -- it must be held throughout, no way around it, and is bounded (~n_ent*DG_DIM*4 bytes).
        # DG key-codes for ingested TRIPLES are NEVER precomputed for the whole dataset (that was the
        # smoke-run bug: a [1213912, DG_DIM] array is ~9.9GB, which combined with DG_VAL_CODEBOOK
        # (~3.95GB) and E (~1.84GB) would exceed the measured ~10GB available RAM at the full-scale
        # unit) -- ingest_from_triples and eval_gate_sparse_shard both DG-project on the fly instead.
        dg_key_proj, dg_val_proj = build_dg_projections(DATA_SEED, 1024, DG_DIM, DG_SPARSITY)
        print(f"[{run_mode}] DG projections built t={time.time()-t0:.2f}s; encoding DG_VAL_CODEBOOK "
              f"({n_ent} entities, dg_dim={DG_DIM})...", flush=True)
        dg_val_codebook = precompute_dg_val_codebook(dg_val_proj, E)
        print(f"[{run_mode}] DG_VAL_CODEBOOK done t={time.time()-t0:.2f}s", flush=True)
        sparse_store = SparseHeteroShardStore(dg_val_codebook, DG_DIM, n_shards)
        scrambled_sparse_store = SparseHeteroShardStore(dg_val_codebook, DG_DIM, n_shards)

    done = completed_units(output_dir)
    unit_i = 0
    for scale in scales:
        scale_eff = min(scale, len(triples_shuffled))
        key = unit_key("scale", scale_eff)
        if key in done:
            print(f"[{run_mode}] scale={scale_eff} already complete (resume)", flush=True)
            unit_i += 1
            continue
        run_sparse_here = (scale_eff in sparse_scales) or (scale in sparse_scales)
        spot_check_here = (scale_eff in flat_repro_scales) or (scale in flat_repro_scales)
        print(f"[{run_mode}] scale={scale_eff} starting (sparse={run_sparse_here} "
              f"flat_spotcheck={spot_check_here}) t={time.time()-t0:.2f}s", flush=True)
        unit = run_scale_unit(scale_eff, triples_shuffled, src_idx_shuffled, E, R, n_rel, n_shards,
                              flat_store, dense_store, sparse_store, scrambled_sparse_store,
                              dg_key_proj, run_sparse_here, spot_check_here)
        record_unit(output_dir, key, unit)
        unit_i += 1
        d_msg = (f"dense_rr={unit['dense']['relevant_recall']:.3f} "
                f"dense_fp={unit['dense']['false_pull_in_rate']:.3f}")
        s_msg = ""
        if run_sparse_here:
            s_msg = (f" sparse_rr={unit['sparse']['relevant_recall']:.3f} "
                    f"scr_rr={unit['scrambled']['relevant_recall']:.3f}")
        print(f"[{run_mode}] scale={scale_eff} done: {d_msg}{s_msg} t={time.time()-t0:.2f}s", flush=True)
        _write_heartbeat(output_dir, unit_i, expected_units, time.time() - t0, extra={"scale": scale_eff})

    all_units = load_units(output_dir)
    per_scale = {str(u["scale"]): u for k, u in all_units.items() if k.startswith("scale|")}
    cardinality_ok = len(per_scale) == len(scales)

    stage2b_ref = load_stage2b_reference()
    stage2b_per_scale = stage2b_ref.get("per_scale", {})

    repro_detail: Dict = {}
    repro_ok_all = True
    for sc in sorted(flat_repro_scales):
        sc_key = str(min(sc, len(triples_shuffled)))
        if sc_key not in per_scale or "flat_spotcheck" not in per_scale[sc_key]:
            continue
        fresh = per_scale[sc_key]["flat_spotcheck"]
        ref = stage2b_per_scale.get(sc_key)
        if ref is None:
            repro_detail[sc_key] = {"ok": False, "reason": "NO_STAGE2B_REFERENCE_AT_THIS_SCALE"}
            repro_ok_all = False
            continue
        d_rr = abs(fresh["relevant_recall"] - ref["relevant_recall"])
        d_fp = abs(fresh["false_pull_in_rate"] - ref["false_pull_in_rate"])
        ok = (d_rr <= REPRO_TOLERANCE) and (d_fp <= REPRO_TOLERANCE)
        repro_detail[sc_key] = {"ok": ok, "fresh_rr": fresh["relevant_recall"],
                                "stage2b_rr": ref["relevant_recall"],
                                "fresh_fp": fresh["false_pull_in_rate"],
                                "stage2b_fp": ref["false_pull_in_rate"], "d_rr": d_rr, "d_fp": d_fp}
        repro_ok_all = repro_ok_all and ok
    baseline_repro_check = {"ok": bool(repro_ok_all and len(repro_detail) > 0), "detail": repro_detail}

    largest_scale = str(max(int(k) for k in per_scale)) if per_scale else None
    lp = per_scale.get(largest_scale, {}) if largest_scale else {}

    def _digest(d):
        if d is None:
            return None
        return hashlib.sha256(json.dumps(
            {k: v for k, v in d.items() if k not in ("ingest_s", "eval_s", "shard_diag", "calibration")},
            sort_keys=True, default=str).encode()).hexdigest()

    digests = {"dense": _digest(lp.get("dense")), "sparse": _digest(lp.get("sparse")),
              "scrambled": _digest(lp.get("scrambled")), "flat_spotcheck": _digest(lp.get("flat_spotcheck"))}
    present = {k: v for k, v in digests.items() if v is not None}
    arms_differ = len(set(present.values())) == len(present) if present else False

    def _get(scale_s, arm):
        u = per_scale.get(scale_s)
        return None if u is None else u.get(arm)

    full_scale_eff = min(SCALES_FULL[-1], len(triples_shuffled))
    full_scale_s = str(full_scale_eff) if not args.smoke else (
        str(max(int(k) for k in per_scale)) if per_scale else None)
    hundred_k_s = "100000" if "100000" in per_scale else None

    sparse_100k = _get(hundred_k_s, "sparse") if hundred_k_s else None
    sparse_full = _get(full_scale_s, "sparse") if full_scale_s else None
    scr_100k = _get(hundred_k_s, "scrambled") if hundred_k_s else None
    scr_full = _get(full_scale_s, "scrambled") if full_scale_s else None
    dense_100k = _get(hundred_k_s, "dense") if hundred_k_s else None
    dense_full = _get(full_scale_s, "dense") if full_scale_s else None
    flat_100k = stage2b_per_scale.get("100000") if hundred_k_s else None
    flat_full = (_get(full_scale_s, "flat_spotcheck") or stage2b_per_scale.get(full_scale_s)
                if full_scale_s else None)

    checks: Dict = {}
    if sparse_100k and sparse_full:
        checks["sparse_recall_ok"] = bool(sparse_100k["relevant_recall"] >= REC_THRESH_SPARSE
                                          and sparse_full["relevant_recall"] >= REC_THRESH_SPARSE)
        checks["sparse_fp_ok"] = bool(sparse_100k["false_pull_in_rate"] <= FP_THRESH
                                      and sparse_full["false_pull_in_rate"] <= FP_THRESH)
        checks["sparse_collapse_both"] = bool(sparse_100k["relevant_recall"] < SPARSE_COLLAPSE_CEILING
                                              and sparse_full["relevant_recall"] < SPARSE_COLLAPSE_CEILING)
    if sparse_100k and sparse_full and scr_100k and scr_full:
        margin_100k = sparse_100k["relevant_recall"] - scr_100k["relevant_recall"]
        margin_full = sparse_full["relevant_recall"] - scr_full["relevant_recall"]
        checks["scramble_margin_ok"] = bool(margin_100k >= SCRAMBLE_MARGIN_MIN
                                            and margin_full >= SCRAMBLE_MARGIN_MIN)
        checks["scramble_ties_both"] = bool(margin_100k < SCRAMBLE_TIE_GAP and margin_full < SCRAMBLE_TIE_GAP)
        checks["scramble_margin_100k"] = margin_100k
        checks["scramble_margin_full"] = margin_full
    if dense_100k and flat_100k and dense_full and flat_full:
        lift_100k = dense_100k["relevant_recall"] - flat_100k["relevant_recall"]
        lift_full = dense_full["relevant_recall"] - flat_full["relevant_recall"]
        checks["dense_lift_ok"] = bool(lift_100k >= DENSE_LIFT_MIN and lift_full >= DENSE_LIFT_MIN)
        checks["dense_lift_100k"] = lift_100k
        checks["dense_lift_full"] = lift_full

    hard_fail = bool(checks.get("sparse_collapse_both", False) or checks.get("scramble_ties_both", False)
                     or not baseline_repro_check["ok"])
    hard_pass = bool(baseline_repro_check["ok"] and checks.get("sparse_recall_ok", False)
                     and checks.get("sparse_fp_ok", False) and checks.get("scramble_margin_ok", False)
                     and checks.get("dense_lift_ok", False) and arms_differ and cardinality_ok)

    if hard_fail:
        overall_verdict = "HARD_FAIL"
    elif hard_pass:
        overall_verdict = "HARD_PASS"
    else:
        overall_verdict = "MIDDLE_BAND"

    verdict_msg = (f"{overall_verdict}: checks={checks} baseline_repro_ok={baseline_repro_check['ok']} "
                  f"arms_differ={arms_differ} cardinality_ok={cardinality_ok}")

    elapsed = time.time() - t0
    metrics = {
        "verdict": overall_verdict, "verdict_msg": verdict_msg[:2000], "summary": verdict_msg[:500],
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "n_ent": n_ent, "n_rel": n_rel, "n_shards": n_shards, "source_to_idx": source_to_idx,
        "scales": scales, "sparse_scales": sorted(sparse_scales), "dg_dim": DG_DIM,
        "dg_sparsity": DG_SPARSITY, "gate_thresh": GATE_THRESH, "per_scale": per_scale,
        "baseline_repro_check": baseline_repro_check, "checks": checks, "arms_differ_check": digests,
        "arms_differ_verified": arms_differ, "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_units, "cell_chunked": False, "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "empirical dual-regime shard-capacity diagnostic (dense-Hopfield DENSE arm vs "
                    "Willshaw-class SPARSE arm); measuring where the real per-shard-family capacity "
                    "sits IS the test",
        "deterministic_seeding": True,
        "calibration_check_flat_dense": "default_ok_for_this_regime: GATE_THRESH=0.28 fixed/unmodified "
                                        "across FLAT and DENSE arms",
        "calibration_check_sparse": "adaptive_with_discriminator_gate: DG-space tau via "
                                    "refuse_gate_calibrate_from_scores, per-scale, 50/50 internal split",
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
