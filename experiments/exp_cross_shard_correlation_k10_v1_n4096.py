"""CROSS-SHARD CORRELATION K=10 v1 at N=4096.

CONTEXT:
  Track-C Phase 1 gate test (user msg 1, 2026-05-30): does the pairwise
  cross-shard correlation tr(W_i.T @ W_j) correctly identify known related
  shard pairs in a 10-shard deployment with synthetic ground-truth entity
  overlaps? This is THE gate test for substrate-distinctive analytics
  capability across sharded deployments. HARD_PASS -> ship T3.P2 (more
  shards, more overlap densities). HARD_FAIL -> cross-shard analytics
  closes; per-shard query is the only mode.

SCIENTIFIC QUESTION:
  Given K=10 independently-populated substrate shards W_0..W_9 (same key
  space; independent BSC codebooks reused across shards is the canonical
  setup), the matrix inner product

      C_ij = tr(W_i.T @ W_j) / N

  is a similarity statistic between two outer-product memories. If shard
  i stored {(k_a, v_a)} and shard j stored {(k_a, v'_a)} (same KEY but
  different values), C_ij is proportional to the number of shared keys
  weighted by the value-pair inner product. We exploit this for shard
  relationship discovery:

  - Shards (0,1) share 30 stored KEYS (different values per shard).
  - Shards (2,3) share 30 stored KEYS.
  - Shards (4,5) share 30 stored KEYS.
  - Shards (6,7,8) share 30 KEYS in a 3-way overlap.
  - Shard 9 has NO key overlaps with any other shard.

  Total 45 pairwise (i,j) correlations per seed. Related pairs (and
  related triplet edges) should rank in the top of the 45.

DESIGN:
  - N=4096, BSC-equivalent Kerdock codebook (PROT-018 _n4096 binding).
  - K=10 shards. Each shard stores M=50 (key,value) pairs.
  - Overlap structure (key-sharing): see above.
  - Independent VALUE assignments per shard for the overlap keys.
  - 5 seeds [7, 17, 23, 31, 41] for shard population.
  - Pairwise C_ij computed for all C(10,2) = 45 unordered pairs per seed.
  - Fine-grained C_ij^{ab} = (W_i @ k_a) . (W_j @ k_a) tested for related
    pairs only (3 doublets + 3 triplet edges; 6 pairs x 30 candidate keys
    plus distractor keys).

METRICS:
  - correlation_AUC: AUC of the 45 pairwise C_ij as classifiers for
       "related" (= shared >= 1 key) vs "unrelated".
  - entity_resolution_precision: for related doublet pairs (0,1), (2,3),
       (4,5), threshold the fine-grained C_ij^{ab} at the top-30 entities;
       compute precision against the 30-true overlap set.
  - triplet_detection: rank of the three triplet-pair correlations
       C_{6,7}, C_{7,8}, C_{6,8} among all 45 pairwise correlations.
       (Top-9 means each is in the top 9 of 45.)

PRE-REGISTERED BANDS (matches user msg 1 spec):
  HARD_PASS: correlation_AUC >= 0.85 AND entity_resolution_precision >= 0.80
       in >= 3/5 seeds.
  HARD_FAIL: correlation_AUC <= 0.60 (indistinguishable from noise).
  MIDDLE_BAND: 0.60 < correlation_AUC < 0.85 OR entity precision weak.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. K=10 shards; C(10,2) = 45 pairwise correlations.
  3. Related-pair COUNT: 3 doublet pairs (0,1)/(2,3)/(4,5) + 3 triplet
     edges (6,7)/(7,8)/(6,8) = 6 related pairs; 45 - 6 = 39 unrelated.
  4. Each shard M=50 facts; overlap = 30 keys for related pairs.
  5. tr(W_i.T @ W_j) / N decomposes (with v's drawn independently) into a
     positive term for shared keys (proportional to # shared keys) plus a
     mean-zero noise term for unshared.
  6. AUC of a perfect separator on 45 items = 1.0; pure-noise = 0.5.

OOM CHECK:
  10 shards x 4096*4096*4 = 640MB. Codebook 64MB. Total ~700MB. Under 6GB.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: cross_shard_correlation_k10_v1_n4096
Queue: overnight_queue (GPU; N=4096; 5 cell-seeds; 45 pairs each)
Pre-reg: preregs/2026-05-30_cross_shard_correlation_k10_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import itertools
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load substrate primitives (Kerdock codebook)
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_xshard", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

v3 = c1.v3

# Per-cell-seed checkpoint
_ckpt_path = REPO / "experiments" / "_seed_checkpoint.py"
_ckpt_spec = importlib.util.spec_from_file_location("_seed_checkpoint_xshard", _ckpt_path)
_ckpt = importlib.util.module_from_spec(_ckpt_spec)
_ckpt_spec.loader.exec_module(_ckpt)
list_completed_keys = _ckpt.list_completed_keys
write_partial_key   = _ckpt.write_partial_key
load_partial_key    = _ckpt.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds to N = 4096
N = 4096        # PROT-018 production-N anchor line
N_FULL  = N
N_SMOKE = 1024   # Kerdock requires even log2(N); 1024=2^10 OK, 512=2^9 not.
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

K_SHARDS = 10
M_PER_SHARD_FULL = 50
M_PER_SHARD_SMOKE = 12
N_OVERLAP_FULL = 30
N_OVERLAP_SMOKE = 6

# Overlap structure: list of (i, j) pairs (i < j) sharing keys.
# Doublets: (0,1), (2,3), (4,5).
# Triplet (6,7,8): all three pairs (6,7), (7,8), (6,8) share keys -- but
# the SAME 30 keys (so all three shards in the triplet share the same 30
# overlap-key set).
DOUBLET_PAIRS  = [(0, 1), (2, 3), (4, 5)]
TRIPLET_SHARDS = (6, 7, 8)
TRIPLET_PAIRS  = [(6, 7), (7, 8), (6, 8)]

# All 45 pairs (i<j)
ALL_PAIRS = list(itertools.combinations(range(K_SHARDS), 2))
RELATED_PAIRS_SET = set(DOUBLET_PAIRS + TRIPLET_PAIRS)
UNRELATED_PAIRS = [p for p in ALL_PAIRS if p not in RELATED_PAIRS_SET]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (user msg 1)
HP_AUC_MIN        = 0.85
HP_PRECISION_MIN  = 0.80
HP_SEEDS_MIN      = 3
HF_AUC_MAX        = 0.60


def get_output_dir(default_name: str = "cross_shard_correlation_k10_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cell_key(seed: int) -> str:
    return f"seed{int(seed)}"


def build_shards(codebook: torch.Tensor, seed: int, N_use: int,
                  M_per_shard: int, n_overlap: int,
                  device: torch.device
                  ) -> Tuple[List[torch.Tensor], Dict[int, List[int]]]:
    """Build K_SHARDS shards with the prescribed overlap structure.

    Returns (W_list, key_idx_by_shard) where key_idx_by_shard[i] is the list
    of codebook indices stored as KEYS in shard i.
    """
    C = codebook.shape[0]
    # We need a generous index budget. Each shard has M_per_shard KEYS plus
    # M_per_shard VALUES drawn from codebook; with overlaps factored in,
    # M-related shards may reuse keys but each VALUE is independent.
    gen = torch.Generator(device=device).manual_seed(seed + 4242)

    # Step 1: pick a global "overlap key set" of size n_overlap for each
    # related cluster (doublets share their own; triplet shares its own).
    # Total special key sets: 3 doublets + 1 triplet-set = 4 disjoint
    # overlap groups; plus each shard has its own unique 20 keys.
    # Total unique keys needed: 4*n_overlap + K_SHARDS*(M_per_shard - n_overlap).
    # Determine how many overlap keys each shard receives:
    #   - shards 0,1: doublet overlap (n_overlap each).
    #   - shards 2,3: doublet overlap.
    #   - shards 4,5: doublet overlap.
    #   - shards 6,7,8: triplet overlap (same n_overlap set, shared by 3).
    #   - shard 9: zero overlap (isolated).
    # Each shard's "unique" count = M_per_shard - (overlap count it receives).
    def overlap_count_for_shard(i: int) -> int:
        for (a, b) in DOUBLET_PAIRS:
            if i == a or i == b:
                return n_overlap
        if i in TRIPLET_SHARDS:
            return n_overlap
        return 0

    n_unique_by_shard = [M_per_shard - overlap_count_for_shard(i)
                          for i in range(K_SHARDS)]
    total_unique_keys = sum(n_unique_by_shard)

    n_overlap_groups = 4   # 3 doublets + 1 triplet
    total_overlap_keys = n_overlap_groups * n_overlap

    # Also values (independent across shards): K_SHARDS * M_per_shard values
    total_values_needed = K_SHARDS * M_per_shard
    total_keys_needed = total_overlap_keys + total_unique_keys

    assert C >= total_keys_needed + total_values_needed, (
        f"codebook too small: C={C} need {total_keys_needed + total_values_needed} "
        f"keys({total_keys_needed}) + values({total_values_needed})")

    perm = torch.randperm(C, generator=gen, device=device).tolist()
    cursor = 0

    # Doublet overlap key sets
    doublet_overlap_keys = []
    for _ in range(len(DOUBLET_PAIRS)):
        doublet_overlap_keys.append(perm[cursor:cursor + n_overlap])
        cursor += n_overlap
    # Triplet overlap key set (single set shared by 6,7,8)
    triplet_overlap_keys = perm[cursor:cursor + n_overlap]
    cursor += n_overlap

    # Per-shard unique key sets
    shard_unique_keys = []
    for i in range(K_SHARDS):
        n_uniq = n_unique_by_shard[i]
        shard_unique_keys.append(perm[cursor:cursor + n_uniq])
        cursor += n_uniq

    # Compose per-shard key index lists
    key_idx_by_shard: Dict[int, List[int]] = {}
    for i in range(K_SHARDS):
        keys_i = list(shard_unique_keys[i])
        # Add overlap keys based on membership
        for d_idx, (a, b) in enumerate(DOUBLET_PAIRS):
            if i == a or i == b:
                keys_i = keys_i + list(doublet_overlap_keys[d_idx])
        if i in TRIPLET_SHARDS:
            keys_i = keys_i + list(triplet_overlap_keys)
        assert len(keys_i) == M_per_shard, (
            f"shard {i} has {len(keys_i)} keys, expected {M_per_shard}")
        key_idx_by_shard[i] = keys_i

    # Values: independent per shard
    W_list = []
    for i in range(K_SHARDS):
        val_perm = perm[cursor:cursor + M_per_shard]
        cursor += M_per_shard
        keys_t = codebook[torch.tensor(key_idx_by_shard[i],
                                          dtype=torch.long, device=device)]
        vals_t = codebook[torch.tensor(val_perm,
                                          dtype=torch.long, device=device)]
        W_i = (vals_t.T @ keys_t) / float(N_use)
        W_list.append(W_i)

    return W_list, key_idx_by_shard


def compute_pairwise_correlation(W_list: List[torch.Tensor], N_use: int
                                   ) -> Dict[Tuple[int, int], float]:
    """Compute C_ij = tr(W_i.T @ W_j) / N for all i<j pairs."""
    out = {}
    for (i, j) in ALL_PAIRS:
        # tr(W_i.T @ W_j) = sum(W_i * W_j) elementwise
        c = float((W_list[i] * W_list[j]).sum().item()) / float(N_use)
        out[(i, j)] = c
    return out


def compute_auc(pos_scores: List[float], neg_scores: List[float]) -> float:
    """Mann-Whitney AUC."""
    if not pos_scores or not neg_scores:
        return 0.5
    # Tied scores get 0.5 credit.
    wins = 0.0
    for p in pos_scores:
        for n in neg_scores:
            if p > n:
                wins += 1.0
            elif p == n:
                wins += 0.5
    return wins / (len(pos_scores) * len(neg_scores))


def compute_entity_resolution(W_list: List[torch.Tensor],
                                codebook: torch.Tensor,
                                key_idx_by_shard: Dict[int, List[int]],
                                N_use: int, device: torch.device,
                                pair: Tuple[int, int],
                                n_overlap: int,
                                n_distractors: int = 50
                                ) -> float:
    """For a related doublet pair (i, j), compute the fine-grained C_ij^{ab}
    for the true overlap keys plus n_distractors random unrelated keys.
    Threshold top-n_overlap; report precision = (true positives) / n_overlap.
    """
    i, j = pair
    keys_i_set = set(key_idx_by_shard[i])
    keys_j_set = set(key_idx_by_shard[j])
    overlap_set = list(keys_i_set & keys_j_set)
    # Expect at least n_overlap (may be more if i,j happen to both contain
    # the triplet overlap by some construction quirk; we trim to true count).
    if not overlap_set:
        return 0.0

    # Pool of distractors: keys NOT in the overlap, sampled from the codebook.
    C = codebook.shape[0]
    overlap_set_set = set(overlap_set)
    distractor_pool = [k for k in range(C) if k not in overlap_set_set]
    n_distr = min(n_distractors, len(distractor_pool))
    gen = torch.Generator(device=device).manual_seed(73)
    distr_idx = torch.randperm(len(distractor_pool), generator=gen, device=device)[:n_distr]
    distr_keys_codebook_idx = [distractor_pool[int(x)] for x in distr_idx.tolist()]

    candidate_idx = list(overlap_set) + distr_keys_codebook_idx
    candidate_keys = codebook[torch.tensor(candidate_idx, dtype=torch.long,
                                              device=device)]   # (Nc, N)

    # Fine-grained correlation: for each candidate key k, compute
    # <W_i k, W_j k>.
    Wi_k = candidate_keys @ W_list[i].T      # (Nc, N)
    Wj_k = candidate_keys @ W_list[j].T      # (Nc, N)
    scores = (Wi_k * Wj_k).sum(dim=1) / float(N_use)   # (Nc,)

    # Threshold top-len(overlap_set)
    k_top = min(len(overlap_set), scores.numel())
    top_pos = torch.topk(scores, k_top).indices.tolist()
    # candidate_idx[0..len(overlap_set)-1] are the TRUE positives.
    true_positives_idx_set = set(range(len(overlap_set)))
    n_correct = sum(1 for p in top_pos if p in true_positives_idx_set)
    return n_correct / float(k_top)


def run_one_cell(seed: int, N_use: int, M_per_shard: int, n_overlap: int,
                  device: torch.device) -> Dict:
    """One seed: build all K shards, compute correlation_AUC + entity precision."""
    codebook, _ = v3.make_kerdock_4coset_codebook(N_use, device)
    W_list, key_idx_by_shard = build_shards(
        codebook, seed, N_use, M_per_shard, n_overlap, device
    )
    C_ij = compute_pairwise_correlation(W_list, N_use)

    # AUC: related pairs are positives, unrelated are negatives.
    pos = [C_ij[p] for p in (DOUBLET_PAIRS + TRIPLET_PAIRS)]
    neg = [C_ij[p] for p in UNRELATED_PAIRS]
    auc = compute_auc(pos, neg)

    # Entity resolution: only for doublet pairs (clean ground-truth overlap)
    precs = []
    for p in DOUBLET_PAIRS:
        prec = compute_entity_resolution(W_list, codebook, key_idx_by_shard,
                                           N_use, device, p, n_overlap)
        precs.append(prec)
    entity_resolution_precision = sum(precs) / len(precs) if precs else 0.0

    # Triplet detection: rank of each TRIPLET_PAIRS correlation among all 45.
    sorted_pairs = sorted(C_ij.items(), key=lambda kv: -kv[1])
    rank_by_pair = {pair: idx + 1 for idx, (pair, _) in enumerate(sorted_pairs)}
    triplet_ranks = [rank_by_pair[p] for p in TRIPLET_PAIRS]
    triplet_in_top9 = sum(1 for r in triplet_ranks if r <= 9)

    # Report basic shape info
    return {
        "seed": int(seed),
        "N": int(N_use),
        "K_shards": int(K_SHARDS),
        "M_per_shard": int(M_per_shard),
        "n_overlap": int(n_overlap),
        "n_pairs": len(ALL_PAIRS),
        "correlation_AUC": round(auc, 5),
        "entity_resolution_precision": round(entity_resolution_precision, 5),
        "entity_precision_per_doublet": [round(p, 5) for p in precs],
        "triplet_ranks": triplet_ranks,
        "triplet_in_top9": int(triplet_in_top9),
        "related_mean_C": round(sum(pos) / len(pos), 6) if pos else 0.0,
        "unrelated_mean_C": round(sum(neg) / len(neg), 6) if neg else 0.0,
        "max_related_C": round(max(pos), 6) if pos else 0.0,
        "max_unrelated_C": round(max(neg), 6) if neg else 0.0,
    }


def cell_passes_hp(cell: Dict) -> bool:
    return (cell["correlation_AUC"] >= HP_AUC_MIN
            and cell["entity_resolution_precision"] >= HP_PRECISION_MIN)


def cell_is_hf(cell: Dict) -> bool:
    return cell["correlation_AUC"] <= HF_AUC_MAX


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("XSHARD_INCONCLUSIVE", "No cells.")

    pass_seeds = sum(1 for c in cells if cell_passes_hp(c))
    hf_seeds = sum(1 for c in cells if cell_is_hf(c))

    mean_auc = sum(c["correlation_AUC"] for c in cells) / len(cells)
    mean_prec = sum(c["entity_resolution_precision"] for c in cells) / len(cells)
    mean_triplet = sum(c["triplet_in_top9"] for c in cells) / len(cells)

    detail = (f"pass_seeds={pass_seeds}/{len(cells)} hf_seeds={hf_seeds} "
              f"mean_AUC={mean_auc:.3f} mean_entity_prec={mean_prec:.3f} "
              f"mean_triplet_in_top9={mean_triplet:.2f}/3 "
              f"N={summary.get('N', N_FULL)}")

    if hf_seeds >= len(cells) / 2:
        return ("XSHARD_HARD_FAIL",
                f"AUC_NOISE: {hf_seeds}/{len(cells)} cells with AUC<={HF_AUC_MAX}. "
                + detail)

    if pass_seeds >= HP_SEEDS_MIN or (summary.get("smoke") and pass_seeds >= 1):
        return ("XSHARD_HARD_PASS",
                f"XSHARD_OK: {pass_seeds}/{len(cells)} pass HP (>= {HP_SEEDS_MIN} required). "
                + detail)

    return ("XSHARD_MIDDLE_BAND",
            f"PARTIAL: pass={pass_seeds}/{len(cells)}, hf={hf_seeds}/{len(cells)}. "
            + detail)


def _instrumentation_selftest() -> None:
    """Mandatory: assert all metrics non-null + verdict gates + overlap algebra."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    assert K_SHARDS == 10, f"K_SHARDS: {K_SHARDS}"
    assert len(ALL_PAIRS) == 45, f"ALL_PAIRS: {len(ALL_PAIRS)}"
    assert len(RELATED_PAIRS_SET) == 6, f"related pairs: {len(RELATED_PAIRS_SET)}"
    assert len(UNRELATED_PAIRS) == 39, f"unrelated pairs: {len(UNRELATED_PAIRS)}"
    assert len(SEEDS_FULL) == 5, f"seeds: {SEEDS_FULL}"

    # AUC self-test: perfect separation = 1.0
    auc_perfect = compute_auc([1.0, 0.9, 0.8], [0.1, 0.2])
    assert abs(auc_perfect - 1.0) < 1e-6, f"perfect AUC: {auc_perfect}"
    # Pure overlap = 0.5
    auc_zero = compute_auc([0.5], [0.5])
    assert abs(auc_zero - 0.5) < 1e-6, f"tied AUC: {auc_zero}"

    # Smoke: 1 cell at small N on CPU
    device = torch.device("cpu")
    out = run_one_cell(17, N_SMOKE, M_PER_SHARD_SMOKE, N_OVERLAP_SMOKE, device)
    for k in ("correlation_AUC", "entity_resolution_precision", "triplet_in_top9",
              "related_mean_C", "unrelated_mean_C", "max_related_C", "max_unrelated_C"):
        v_ = out.get(k)
        assert v_ is not None and not (isinstance(v_, float) and math.isnan(v_)), (
            f"selftest: metric {k} null/NaN in {out}")
    assert 0.0 <= out["correlation_AUC"] <= 1.0
    assert 0.0 <= out["entity_resolution_precision"] <= 1.0
    assert len(out["triplet_ranks"]) == 3

    # Verdict self-tests
    fake_hf_cells = [
        {"seed": s, "correlation_AUC": 0.5, "entity_resolution_precision": 0.2,
         "triplet_in_top9": 0, "triplet_ranks": [40, 41, 42],
         "related_mean_C": 0.0, "unrelated_mean_C": 0.0,
         "max_related_C": 0.0, "max_unrelated_C": 0.0,
         "N": N_FULL, "K_shards": K_SHARDS, "M_per_shard": 50,
         "n_overlap": 30, "n_pairs": 45,
         "entity_precision_per_doublet": [0.2, 0.2, 0.2]}
        for s in SEEDS_FULL
    ]
    vf, mf = compute_verdict({"cells": fake_hf_cells, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf} {mf}"

    fake_hp_cells = [
        {"seed": s, "correlation_AUC": 0.95, "entity_resolution_precision": 0.92,
         "triplet_in_top9": 3, "triplet_ranks": [1, 2, 3],
         "related_mean_C": 1.0, "unrelated_mean_C": 0.0,
         "max_related_C": 1.5, "max_unrelated_C": 0.1,
         "N": N_FULL, "K_shards": K_SHARDS, "M_per_shard": 50,
         "n_overlap": 30, "n_pairs": 45,
         "entity_precision_per_doublet": [0.95, 0.92, 0.9]}
        for s in SEEDS_FULL
    ]
    vp, mp = compute_verdict({"cells": fake_hp_cells, "N": N_FULL})
    assert "HARD_PASS" in vp, f"HARD_PASS gate: {vp} {mp}"

    print(
        f"[selftest] cross_shard_correlation_k10_v1_n4096 PASS "
        f"smoke AUC={out['correlation_AUC']:.3f} "
        f"entity_prec={out['entity_resolution_precision']:.3f} "
        f"triplet_in_top9={out['triplet_in_top9']}/3 "
        f"rel_mean_C={out['related_mean_C']:.4f} "
        f"unrel_mean_C={out['unrelated_mean_C']:.4f}",
        flush=True,
    )


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    M_per = M_PER_SHARD_SMOKE if smoke else M_PER_SHARD_FULL
    n_over = N_OVERLAP_SMOKE if smoke else N_OVERLAP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    total_expected = len(seeds)
    out_dir = get_output_dir()
    done_keys = set(list_completed_keys(out_dir))

    print(f"[run] cross_shard_correlation_k10_v1_n4096 smoke={smoke} N={N_cfg} "
          f"K_shards={K_SHARDS} M_per_shard={M_per} n_overlap={n_over} "
          f"seeds={seeds} total_expected={total_expected} "
          f"already_done={len(done_keys)} device={device_str}", flush=True)
    t0 = time.time()

    for seed in seeds:
        ck = cell_key(seed)
        if ck in done_keys:
            continue
        try:
            out = run_one_cell(seed, N_cfg, M_per, n_over, device)
            out["seed_int"] = out["seed"]
            out["seed"] = ck
            write_partial_key(out_dir, ck, out)
            print(f"  {ck} AUC={out['correlation_AUC']:.3f} "
                  f"entity_prec={out['entity_resolution_precision']:.3f} "
                  f"triplet_top9={out['triplet_in_top9']}/3 "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  {ck} CELL_FAILED: {type(e).__name__}: {e}", flush=True)
            if device.type == 'cuda':
                torch.cuda.empty_cache()

    all_cells = []
    for ck in list_completed_keys(out_dir):
        body = load_partial_key(out_dir, ck)
        if body is None:
            continue
        all_cells.append(body)

    summary = {
        "anchor": "cross_shard_correlation_k10_v1_n4096",
        "N": N_cfg,
        "smoke": smoke,
        "seeds": seeds,
        "K_shards": K_SHARDS,
        "M_per_shard": M_per,
        "n_overlap": n_over,
        "total_expected": total_expected,
        "n_completed": len(all_cells),
        "cells": all_cells,
    }
    verdict, verdict_msg = compute_verdict(summary)
    elapsed = round(time.time() - t0, 2)
    summary["verdict"] = verdict
    summary["verdict_msg"] = verdict_msg
    summary["elapsed_s"] = elapsed

    out_path = out_dir / "metrics.json"
    payload = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": summary,
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[completed] {len(all_cells)}/{total_expected}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
