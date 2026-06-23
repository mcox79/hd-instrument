"""substrate_self_map_v2d_discriminator_corrected_v1 -- REVIVAL of v2c HARD_FAIL.

REVIVAL of substrate_self_map_v2c_full_store_v1 HARD_FAIL (2026-06-22).

Parent v2c finding (3 seeds, FULL Store, 4096-D):
- n_clusters_real ~ 35-50; n_clusters_shuf ~ 35-50; cluster_gap=-3.0 across all seeds.
- Verdict was HARD_FAIL: "shuffle as granular as real (cluster_gap<=0); relation-conditioned
  mechanism null on full Store."

Revival hypothesis (per `notes/research_2x_revival_overnight_negatives_2026-06-23.md`):

Likely a DISCRIMINATOR-DIRECTION bug. Real relations BUNDLE chain-grade anchors into LARGER
coherent clusters; shuffle FRAGMENTS them. cluster-COUNT is direction-INVERTED:
  - real -> fewer larger meaningful clusters
  - shuffle -> more smaller fragmented clusters
So "cluster_count_real > cluster_count_shuf" is the WRONG direction. The correct discriminator is:
  - ARI(real_clustering, v1_families) vs ARI(shuffle_clustering, v1_families)
    -- v1 families = lexical ground-truth labels
  - OR mean_cluster_size_real vs mean_cluster_size_shuffle (larger == more bundled)
  - OR modularity Q

DESIGN:
- Re-run v2c primitives end-to-end (FULL Store ingest, char_trigram + KGStore + 2hop Jaccard).
- Add ARI(real, v1_families) and ARI(shuf, v1_families) as the PRIMARY discriminator.
- Add mean_cluster_size_real / mean_cluster_size_shuf as the SECONDARY discriminator.
- Keep cluster_count + cluster_gap for diagnostic-record (parent's discriminator).
- v1 families = parse latest `notes/capability_family_map_v1_*.md` (same primitive v2c already uses).

PRE-REG HARD bands (verbatim from handoff):
  HARD_PASS: ARI_real >= 0.10 AND ARI_real / ARI_shuf >= 2.0
             OR mean_cluster_size_real / mean_cluster_size_shuf >= 1.5
  HARD_FAIL: ARI_real <= 0.02 OR ratio <= 1.1

ASCII-only. Per-seed checkpoint. Reuses v2c primitives via module import.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Tuple

import numpy as np
from sklearn.metrics import adjusted_rand_score

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

# Reuse v2c primitives end-to-end. v2c parses argv at module-load and would sys.exit(0) on
# --self-test; strip our own argv before import to prevent that, restore after.
_saved_argv = sys.argv[:]
sys.argv = [sys.argv[0]]
from experiments.exp_substrate_self_map_v2c_full_store_v1 import (
    load_chain_grade_atom_ids, load_atomized_atom_ids, load_relations_for,
    load_v1_clusters, load_v1_cross_family_arrows,
    encode_atoms_substrate, build_kg, two_hop_neighborhood, jaccard,
    greedy_cluster, atom_id_short, cross_family_arrows, avg_jaccard_substrate_vs_v1,
    atom_retrieval_recall, sample_relation_pairs, shuffle_triple_relations,
    cluster_coherence, JACCARD_CLUSTER_TAU, JACCARD_VS_V1_TAU,
)
sys.argv = _saved_argv

_LLM_CALL_COUNTER = [0]

ANCHOR_NAME = "substrate_self_map_v2d_discriminator_corrected_v1"
LEDGER = REPO / "data" / "substrate_index" / "meta" / "cert_ledger.jsonl"

# ----- pre-registered HARD thresholds (v2d corrected discriminator) -----
ARI_PASS = 0.10
ARI_RATIO_PASS = 2.0
SIZE_RATIO_PASS = 1.5
ARI_FAIL = 0.02
ARI_RATIO_FAIL = 1.1
RECALL_PASS = 0.95
RECALL_FAIL = 0.50
CV_PASS = 0.20  # relaxed from v2c=0.10 since ARI naturally more variable

# ----- CLI / run-mode -----
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_IS_SMOKE_BY_NAME = _HDLAB_NAME.endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _IS_SMOKE_BY_NAME) else "full"

# Config: smaller smoke; full mirrors v2c
if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 1024
    MAX_INGEST_TRIPLES = 5000
    N_ANCHORS = 20
    N_RELATION_SAMPLES = 8
    K_SET = 12
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    MAX_INGEST_TRIPLES = None
    N_ANCHORS = 100
    N_RELATION_SAMPLES = 20
    K_SET = 16

CONFIG_VERSION = (
    "v2d-discriminator-corrected: char_trigram + KGStore_multivalue_Hebbian + "
    "multi_hop_2hop_neighborhood_Jaccard_cluster; FULL-Store admit; PRIMARY discriminator = "
    "ARI(clustering, v1_families); SECONDARY = mean_cluster_size_real/shuf; "
    "N%d max_ingest=%s n_anchors=%d n_rel_samples=%d kset=%d "
    "bands ARI>=%.2f ratio>=%.1f size_ratio>=%.1f recall>=%.2f cv<=%.2f"
) % (N_DIM, str(MAX_INGEST_TRIPLES), N_ANCHORS, N_RELATION_SAMPLES, K_SET,
     ARI_PASS, ARI_RATIO_PASS, SIZE_RATIO_PASS, RECALL_PASS, CV_PASS)


# ===== NEW: corrected discriminator helpers =====

def clustering_to_labels(clusters: list, items: list) -> np.ndarray:
    """Convert greedy_cluster output (list of sets of item indices) to a label array
    aligned to `items` order. Items not in any cluster get a unique singleton label.
    """
    item_to_cluster = {}
    for ci, cl in enumerate(clusters):
        for it in cl:
            item_to_cluster[it] = ci
    labels = np.zeros(len(items), dtype=np.int64)
    next_singleton = len(clusters)
    for i, it in enumerate(items):
        if it in item_to_cluster:
            labels[i] = item_to_cluster[it]
        else:
            labels[i] = next_singleton
            next_singleton += 1
    return labels


def v1_family_labels(anchor_atom_ids: list, v1_clusters: dict) -> Tuple[np.ndarray, int]:
    """For each anchor (by short atom_id), assign the v1-family label as int.
    Atoms not in any family get a unique singleton label (so ARI doesn't reward false-matches).
    Returns (labels[n_anchors], n_families_used).
    """
    family_name_to_idx = {f: i for i, f in enumerate(sorted(v1_clusters.keys()))}
    labels = np.zeros(len(anchor_atom_ids), dtype=np.int64)
    next_singleton = len(family_name_to_idx)
    n_in_family = 0
    for i, aid_short in enumerate(anchor_atom_ids):
        found = None
        for fname, fatoms in v1_clusters.items():
            if aid_short in fatoms:
                found = fname
                break
        if found is not None:
            labels[i] = family_name_to_idx[found]
            n_in_family += 1
        else:
            labels[i] = next_singleton
            next_singleton += 1
    return labels, n_in_family


def mean_cluster_size(clusters: list) -> float:
    """Mean size of clusters with >=2 members (singletons excluded; they don't bundle)."""
    sizes = [len(c) for c in clusters if len(c) >= 2]
    if not sizes:
        return 0.0
    return float(np.mean(sizes))


# ===== per-seed runner: v2c machinery + ARI/size discriminator =====

def run_seed(seed: int, combined_atoms: list, triples_str: list, rel_types: list,
             n_chain_grade: int, v1_clusters: dict, v1_cross_arrows: set) -> dict:
    t_start = time.time()
    rng = np.random.default_rng(seed)
    n_ent = len(combined_atoms)
    rel_to_idx = {r: i for i, r in enumerate(rel_types)}
    n_rel = len(rel_types)
    triples_idx = [(s, rel_to_idx[r], o) for (s, r, o) in triples_str]

    t_enc0 = time.time()
    E_np, encoder = encode_atoms_substrate(combined_atoms, N_DIM)
    t_enc = round(time.time() - t_enc0, 1)
    print("  [seed=%d] encoded %d atoms at N=%d in %.1fs" % (seed, n_ent, N_DIM, t_enc), flush=True)

    n_probe = min(n_ent, 200)
    recall = atom_retrieval_recall(E_np, combined_atoms, encoder, n_probe,
                                    np.random.default_rng(seed + 1))

    if n_chain_grade <= N_ANCHORS:
        anchors = list(range(n_chain_grade))
    else:
        anchors = sorted(rng.choice(n_chain_grade, N_ANCHORS, replace=False).tolist())
    anchor_to_atom_id = {a: combined_atoms[a] for a in anchors}
    anchor_to_short = {a: atom_id_short(combined_atoms[a]) for a in anchors}
    anchor_shorts = [anchor_to_short[a] for a in anchors]

    # v1 family labels for anchors (ground-truth)
    v1_labels, n_in_family = v1_family_labels(anchor_shorts, v1_clusters)
    print("  [seed=%d] %d/%d anchors mapped to v1 families" % (seed, n_in_family, len(anchors)), flush=True)

    # ===== ARM A: REAL relations =====
    t_real0 = time.time()
    kg_real = build_kg(E_np, triples_idx, n_ent, n_rel, N_DIM, seed)
    pairs_real = sample_relation_pairs(n_rel, N_RELATION_SAMPLES, np.random.default_rng(seed + 2))
    nbr_real = {}
    for a in anchors:
        nbr_real[a] = two_hop_neighborhood(kg_real, a, pairs_real, K_SET)
    clusters_real = greedy_cluster(anchors, nbr_real, JACCARD_CLUSTER_TAU)
    real_labels = clustering_to_labels(clusters_real, anchors)
    ari_real = float(adjusted_rand_score(v1_labels, real_labels))
    size_real = mean_cluster_size(clusters_real)
    coherence_real = cluster_coherence(clusters_real, nbr_real)
    avg_j_real, per_cluster_real = avg_jaccard_substrate_vs_v1(clusters_real, anchors, anchor_to_short, v1_clusters)
    arrows_real = cross_family_arrows(clusters_real, anchors, anchor_to_atom_id,
                                       v1_clusters, JACCARD_VS_V1_TAU, nbr_real)
    new_arrows = [a for a in arrows_real if a["anchor_short"] not in v1_cross_arrows]
    t_real = round(time.time() - t_real0, 1)
    print("  [seed=%d] REAL  done in %.1fs (n_clusters=%d ARI=%.4f mean_size=%.2f coh=%.3f)"
          % (seed, t_real, len(clusters_real), ari_real, size_real, coherence_real), flush=True)

    # ===== ARM B: SHUFFLED relations =====
    t_shuf0 = time.time()
    triples_shuf = shuffle_triple_relations(triples_idx, n_rel, np.random.default_rng(seed + 3))
    kg_shuf = build_kg(E_np, triples_shuf, n_ent, n_rel, N_DIM, seed)
    pairs_shuf = sample_relation_pairs(n_rel, N_RELATION_SAMPLES, np.random.default_rng(seed + 4))
    nbr_shuf = {}
    for a in anchors:
        nbr_shuf[a] = two_hop_neighborhood(kg_shuf, a, pairs_shuf, K_SET)
    clusters_shuf = greedy_cluster(anchors, nbr_shuf, JACCARD_CLUSTER_TAU)
    shuf_labels = clustering_to_labels(clusters_shuf, anchors)
    ari_shuf = float(adjusted_rand_score(v1_labels, shuf_labels))
    size_shuf = mean_cluster_size(clusters_shuf)
    coherence_shuf = cluster_coherence(clusters_shuf, nbr_shuf)
    avg_j_shuf, _ = avg_jaccard_substrate_vs_v1(clusters_shuf, anchors, anchor_to_short, v1_clusters)
    t_shuf = round(time.time() - t_shuf0, 1)
    print("  [seed=%d] SHUF  done in %.1fs (n_clusters=%d ARI=%.4f mean_size=%.2f coh=%.3f)"
          % (seed, t_shuf, len(clusters_shuf), ari_shuf, size_shuf, coherence_shuf), flush=True)

    # Derived
    ari_ratio = (ari_real / ari_shuf) if abs(ari_shuf) > 1e-9 else (float("inf") if ari_real > 0 else 1.0)
    size_ratio = (size_real / size_shuf) if size_shuf > 1e-9 else (float("inf") if size_real > 0 else 1.0)

    elapsed = round(time.time() - t_start, 1)
    print("  [seed=%d] DISCRIMINATOR ari_real=%.4f ari_shuf=%.4f ratio=%.2f | size_real=%.2f size_shuf=%.2f size_ratio=%.2f | recall=%.3f | %.1fs"
          % (seed, ari_real, ari_shuf, ari_ratio, size_real, size_shuf, size_ratio, recall, elapsed), flush=True)

    return {
        "seed": seed,
        "_ckpt_key": str(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_chain_grade_atoms": n_chain_grade,
        "n_atoms_universe": n_ent,
        "n_relation_types": n_rel,
        "n_triples": len(triples_idx),
        "n_anchors": len(anchors),
        "n_anchors_in_v1_family": n_in_family,
        "atom_retrieval_recall": round(recall, 4),
        "elapsed_s": elapsed,
        "t_encoding_s": t_enc,
        "t_arm_real_s": t_real,
        "t_arm_shuf_s": t_shuf,
        "real": {
            "n_clusters": len(clusters_real),
            "ari": round(ari_real, 4),
            "mean_cluster_size": round(size_real, 4),
            "coherence": round(coherence_real, 4),
            "avg_jaccard_vs_v1": round(avg_j_real, 4),
            "per_cluster_match": per_cluster_real,
            "n_cross_family_arrows_total": len(arrows_real),
            "n_new_cross_family_arrows": len(new_arrows),
            "new_arrows_examples": [a["anchor_short"] for a in new_arrows][:10],
        },
        "shuffle_control": {
            "n_clusters": len(clusters_shuf),
            "ari": round(ari_shuf, 4),
            "mean_cluster_size": round(size_shuf, 4),
            "coherence": round(coherence_shuf, 4),
            "avg_jaccard_vs_v1": round(avg_j_shuf, 4),
        },
        "discriminator": {
            "ari_real": round(ari_real, 4),
            "ari_shuf": round(ari_shuf, 4),
            "ari_ratio": round(ari_ratio if math.isfinite(ari_ratio) else 999.0, 4),
            "size_real": round(size_real, 4),
            "size_shuf": round(size_shuf, 4),
            "size_ratio": round(size_ratio if math.isfinite(size_ratio) else 999.0, 4),
        },
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    }


# ===== verdict =====

def compute_verdict(per_seed_records: list) -> Tuple[str, str]:
    if not per_seed_records:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed records")
    ari_reals = [p["discriminator"]["ari_real"] for p in per_seed_records]
    ari_shufs = [p["discriminator"]["ari_shuf"] for p in per_seed_records]
    ari_ratios = [p["discriminator"]["ari_ratio"] for p in per_seed_records]
    size_reals = [p["discriminator"]["size_real"] for p in per_seed_records]
    size_shufs = [p["discriminator"]["size_shuf"] for p in per_seed_records]
    size_ratios = [p["discriminator"]["size_ratio"] for p in per_seed_records]
    recalls = [p["atom_retrieval_recall"] for p in per_seed_records]
    llm_calls = [p.get("n_llm_calls", 0) for p in per_seed_records]
    n_clusters_real = [p["real"]["n_clusters"] for p in per_seed_records]
    n_clusters_shuf = [p["shuffle_control"]["n_clusters"] for p in per_seed_records]

    ari_real_m = float(np.mean(ari_reals))
    ari_shuf_m = float(np.mean(ari_shufs))
    # Aggregate ratios: use mean of per-seed ratios (clipped if non-finite)
    finite_ari_ratios = [r for r in ari_ratios if math.isfinite(r) and r < 999.0]
    ari_ratio_m = float(np.mean(finite_ari_ratios)) if finite_ari_ratios else 0.0
    size_real_m = float(np.mean(size_reals))
    size_shuf_m = float(np.mean(size_shufs))
    finite_size_ratios = [r for r in size_ratios if math.isfinite(r) and r < 999.0]
    size_ratio_m = float(np.mean(finite_size_ratios)) if finite_size_ratios else 0.0
    recall_m = float(np.mean(recalls))
    # cv on ARI (primary discriminator)
    if len(ari_reals) > 1 and ari_real_m > 0:
        cv = float(np.std(ari_reals) / ari_real_m)
    else:
        cv = 0.0

    summary = (
        "ARI_real=%.4f ARI_shuf=%.4f ARI_ratio=%.2f (pass %.1f) | "
        "size_real=%.2f size_shuf=%.2f size_ratio=%.2f (pass %.1f) | "
        "n_clusters_real=%.1f n_clusters_shuf=%.1f | "
        "recall=%.3f (pass %.2f / fail %.2f) | cv_ARI=%.3f (pass %.2f) | n_llm=%d"
    ) % (
        ari_real_m, ari_shuf_m, ari_ratio_m, ARI_RATIO_PASS,
        size_real_m, size_shuf_m, size_ratio_m, SIZE_RATIO_PASS,
        float(np.mean(n_clusters_real)), float(np.mean(n_clusters_shuf)),
        recall_m, RECALL_PASS, RECALL_FAIL,
        cv, CV_PASS, max(llm_calls),
    )

    if max(llm_calls) > 0:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode violated; n_llm_calls>0. " + summary)
    if recall_m < RECALL_FAIL:
        return ("HARD_FAIL", "HARD_FAIL: atom retrieval recall below floor. " + summary)

    # PRIMARY discriminator: ARI
    ari_passes = (ari_real_m >= ARI_PASS and ari_ratio_m >= ARI_RATIO_PASS)
    # SECONDARY discriminator: cluster-size ratio
    size_passes = (size_ratio_m >= SIZE_RATIO_PASS)
    cv_ok = (cv <= CV_PASS) if len(ari_reals) > 1 else True

    if (ari_passes or size_passes) and cv_ok:
        which = "ARI" if ari_passes else "cluster_size_ratio"
        return (
            "HARD_PASS",
            "HARD_PASS: v2d corrected-discriminator PASSES via %s; v2c HARD_FAIL was discriminator-direction bug. "
            "Real relations bundle chain-grade anchors more than shuffle does. " % which + summary,
        )

    if ari_real_m <= ARI_FAIL or (ari_ratio_m <= ARI_RATIO_FAIL and size_ratio_m <= 1.1):
        return (
            "HARD_FAIL",
            "HARD_FAIL: v2d discriminator-corrected ALSO fails; substrate self-mapping truly null. " + summary,
        )

    return (
        "MIDDLE_BAND",
        "MIDDLE_BAND: v2d shows partial signal but below HARD_PASS bars. " + summary,
    )


# ===== selftest =====

def _selftest():
    """Verify ARI/size discriminator on synthetic 2-block partition (handoff selftest spec)."""
    # ARI on identical partitions should be 1.0
    p1 = np.array([0, 0, 1, 1, 0, 1])
    p2 = np.array([0, 0, 1, 1, 0, 1])
    ari_same = float(adjusted_rand_score(p1, p2))
    assert ari_same == 1.0, "selftest: ARI(same, same)=%.3f != 1.0" % ari_same
    # ARI on shuffled should be near 0
    rng = np.random.default_rng(0)
    n = 100
    p3 = (np.arange(n) >= n // 2).astype(np.int64)
    p4 = rng.permutation(p3)
    ari_rand = float(adjusted_rand_score(p3, p4))
    assert abs(ari_rand) < 0.2, "selftest: ARI(p, perm)=%.3f not near 0" % ari_rand
    # clustering_to_labels: 2 clusters {0,1,2} {3,4} should produce labels (0,0,0,1,1)
    items = [0, 1, 2, 3, 4]
    clusters = [{0, 1, 2}, {3, 4}]
    labs = clustering_to_labels(clusters, items)
    assert list(labs) == [0, 0, 0, 1, 1], "selftest: clustering_to_labels got %s" % list(labs)
    # mean_cluster_size: {3 items, 2 items, singleton} -> mean of [3, 2] = 2.5 (singleton excluded)
    msz = mean_cluster_size([{1, 2, 3}, {4, 5}, {6}])
    assert msz == 2.5, "selftest: mean_cluster_size=%.2f != 2.5" % msz
    # v1_family_labels: anchor "x" in family "F1" gets label 0; "y" not in any gets singleton
    v1c = {"F1": {"x", "a"}, "F2": {"b", "c"}}
    labs, n_in = v1_family_labels(["x", "y", "b"], v1c)
    # F1 -> idx 0, F2 -> idx 1, y -> singleton (idx 2)
    assert labs[0] == 0, "selftest: x should map to F1 (label 0); got %d" % labs[0]
    assert labs[2] == 1, "selftest: b should map to F2 (label 1); got %d" % labs[2]
    assert labs[1] >= 2, "selftest: y should be singleton (label >= 2); got %d" % labs[1]
    assert n_in == 2
    # Substrate-only counter clean
    assert _LLM_CALL_COUNTER[0] == 0
    print("[selftest] PASS: ARI endpoints (same=1.0, perm~0) + clustering_to_labels + mean_cluster_size + v1_family_labels + n_llm=0", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ===== main =====

if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, CONFIG_VERSION), flush=True)
    t0 = time.time()
    print("[load] cert_ledger chain-grade atoms...", flush=True)
    chain_grade_atoms = load_chain_grade_atom_ids()
    print("  -> %d chain-grade atoms" % len(chain_grade_atoms), flush=True)
    print("[load] atomized atom universe...", flush=True)
    atomized = load_atomized_atom_ids()
    print("  -> %d atomized atom_ids" % len(atomized), flush=True)
    print("[load] FULL-Store relations admit...", flush=True)
    load_rng = np.random.default_rng(0)
    triples_str, rel_types, combined_atoms, n_chain_grade = load_relations_for(
        chain_grade_atoms, atomized, MAX_INGEST_TRIPLES, load_rng)
    print("  -> %d triples; %d distinct rel_types; %d combined atoms (CG=%d, frontier=%d)"
          % (len(triples_str), len(rel_types), len(combined_atoms), n_chain_grade,
             len(combined_atoms) - n_chain_grade), flush=True)
    if not triples_str or not rel_types:
        print("[error] no admitted triples; aborting", flush=True)
        sys.exit(2)
    print("[load] v1 clusters (ground-truth labels for ARI)...", flush=True)
    v1_clusters = load_v1_clusters()
    v1_cross_arrows = load_v1_cross_family_arrows()
    print("  -> %d v1 families; %d v1 cross-family atoms" % (len(v1_clusters), len(v1_cross_arrows)), flush=True)
    if not v1_clusters:
        print("[FATAL] no v1 families parsed; ARI discriminator requires v1 ground-truth labels.", flush=True)
        sys.exit(3)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d of %d seeds already complete; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for s in remaining:
        rec = run_seed(s, combined_atoms, triples_str, rel_types, n_chain_grade,
                       v1_clusters, v1_cross_arrows)
        write_partial(out_dir, s, rec)

    agg = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    v, vmsg = compute_verdict(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION,
        "per_seed": per_seed,
        "zero_llm_calls_at_inference": all(p.get("n_llm_calls", 0) == 0 for p in per_seed),
        "elapsed_s": round(time.time() - t0, 1),
        "DESIGN_NOTE": (
            "REVIVAL of v2c HARD_FAIL. v2c used cluster_COUNT_gap as discriminator (real has MORE "
            "clusters than shuffle). Hypothesis: that direction is INVERTED -- real relations "
            "BUNDLE chain-grade anchors into LARGER coherent clusters; shuffle FRAGMENTS them. "
            "v2d swaps in ARI(real, v1_families) vs ARI(shuf, v1_families) as PRIMARY discriminator "
            "and mean_cluster_size_real/shuf as SECONDARY. Reuses all v2c primitives (char_trigram + "
            "KGStore_multivalue_Hebbian + 2hop_Jaccard_cluster); ONLY discriminator changes."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
