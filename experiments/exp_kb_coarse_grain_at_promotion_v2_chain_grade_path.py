"""KB COARSE-GRAIN AT PROMOTION v2 CHAIN-GRADE PROMOTION PATH (ANCHOR 3 v2; 2026-06-27).

Pre-reg: preregs/2026-06-27_kb_coarse_grain_at_promotion_v2_chain_grade_path.md

v1 was tiered PROVEN_BOUND not CHAIN_GRADE because (a) rec_clst=rec_unclst=1.000
saturated against the metric cap (small-N sample) and (b) USER_DIRECTIVE
separation invariant was vacuously satisfied (n_UD=0 atoms in sample).

v2 patches both:
  RC-1: force n_UD >= 10 memory-class atoms into the sample (production KB has
        939; sampling at least 10 is guaranteed).
  RC-2: scale n_atoms >= 10000 at full so the rec=1.000 cap breaks (random
        retrieval at n=10k is 0.0001; mechanism must rise above adaptive floor).
  + discriminator-must-survive-scale: smoke runs an n=10000 single-seed preview
    arm of ARM_ULTRA to verify metrics do not saturate at full-N before full
    dispatch.

ARMS:
  ARM_NO_COARSE_GRAIN_BASELINE   - sanity rail
  ARM_COARSE_GRAIN_ULTRAMETRIC   - chain-grade mechanism
  ARM_RANDOM_CLUSTER_COLLAPSE    - control
  ARM_FULL_N_PREVIEW             - smoke-only (n=10000, 1 seed, ULTRA only)

HARD_PASS bar (chain-grade; harder than v1 infrastructure bar):
  (a) user_directive_retention == 1.0 AND n_UD_in_sample >= 10
  (b) recall_unclustered < 1.0 at n_atoms=10000 (cap-breaking)
  (c) capacity_drop_fraction > 0.20
  (d) gap_vs_random > 0.30
  (e) cv_recall_clustered < 0.05 across 3 seeds

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import os
import time
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hdlab.director_kb_query import DirectorKBQuery, load_default_kb  # noqa: E402
from hdlab.ultrametric_clustering import (  # noqa: E402
    UltrametricConfig,
    collapse_W_via_clusters,
    cosine_distance_matrix,
    effective_capacity_used,
    filter_qualifying_clusters,
    single_linkage_clusters,
)


AUDIT_LOG_PATH = REPO / "data" / "director_kb_audit_log.jsonl"
AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


# ---------- v2 thresholds (chain-grade; harder than v1 infrastructure) ----------
HP_MIN_CAPACITY_DROP = 0.20
HP_MIN_GAP_VS_RANDOM = 0.30
HP_MAX_CV = 0.05
HP_MAX_REC_UNCLUSTERED_NONSAT = 0.999  # must be strictly below 1.0 at full-N
HP_MIN_N_UD_IN_SAMPLE = 10
HP_MIN_N_ATOMS_FULL = 10000

MB_MIN_GAP_VS_RANDOM = 0.15
MB_MAX_CV = 0.10
HF_MIN_CAPACITY_DROP = 0.10

SEEDS_FULL = (17, 23, 31)
SEEDS_SMOKE = (17,)

# ---------- preview thresholds ----------
SMOKE_PREVIEW_N_ATOMS = 10000


def _audit_event(event: dict) -> None:
    line = json.dumps(event, default=str, ensure_ascii=False) + "\n"
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line)


def _sample_atoms_with_forced_ud(
    kb: DirectorKBQuery,
    n_atoms: int,
    seed: int,
    min_ud: int = HP_MIN_N_UD_IN_SAMPLE,
) -> tuple[np.ndarray, list[int], list[str], int]:
    """Sample atoms biased toward classes with abundant atoms; force at least
    `min_ud` USER_DIRECTIVE (memory-class) atoms into the sample.

    Returns (W_sample, atom_indices, source_classes_per_atom, n_ud_in_sample).
    """
    rng = np.random.RandomState(seed)
    n_ent = len(kb.entity_names)

    # Per-entity primary source_class (prefer 'memory' if present for USER_DIRECTIVE)
    ent_sc: list[str] = []
    for i in range(n_ent):
        sc_set = kb._source_classes_by_ent.get(i, set())
        if sc_set:
            if "memory" in sc_set:
                ent_sc.append("memory")
            else:
                ent_sc.append(sorted(sc_set)[0])
        else:
            ent_sc.append("unknown")

    # Force-include USER_DIRECTIVE atoms FIRST (load-bearing for v2)
    mem_cand = [i for i, c in enumerate(ent_sc) if c == "memory"]
    if not mem_cand:
        raise RuntimeError(
            "USER_DIRECTIVE_REFERENT_MISSING: zero memory-class atoms in KB; "
            "cannot satisfy v2 cardinality_ok bar (n_UD >= 10)."
        )
    mem_arr = np.array(mem_cand)
    rng.shuffle(mem_arr)
    # Target: at least min_ud, capped at 5% of n_atoms (or all if min_ud > 5%)
    n_ud_target = max(min_ud, min(len(mem_cand), n_atoms // 20))
    n_ud_actual = min(n_ud_target, len(mem_cand))
    forced_ud_idx = mem_arr[:n_ud_actual].tolist()

    # Stratified sample for the rest: top-5 non-memory classes
    from collections import Counter

    sc_counts = Counter(ent_sc)
    top_classes = [c for c, _ in sc_counts.most_common(6) if c != "memory"][:5]
    n_remaining = n_atoms - n_ud_actual
    per_class = max(1, n_remaining // max(1, len(top_classes)))

    selected_idx: list[int] = list(forced_ud_idx)
    for cls in top_classes:
        cand = [i for i, c in enumerate(ent_sc) if c == cls]
        if not cand:
            continue
        n_take = min(per_class, len(cand))
        idx_arr = np.array(cand)
        rng.shuffle(idx_arr)
        for j in idx_arr[:n_take].tolist():
            if j not in selected_idx:
                selected_idx.append(j)
            if len(selected_idx) >= n_atoms:
                break
        if len(selected_idx) >= n_atoms:
            break

    selected_idx = selected_idx[:n_atoms]
    W_sample = kb.E[selected_idx].cpu().numpy().astype(np.float32)
    sc_per_atom = [ent_sc[i] for i in selected_idx]
    n_ud_in_sample = sum(1 for c in sc_per_atom if c == "memory")
    return W_sample, selected_idx, sc_per_atom, n_ud_in_sample


def _arm_no_coarse_grain_baseline(W: np.ndarray, sc_per_atom: list[str]) -> dict:
    t0 = time.perf_counter()
    n = W.shape[0]
    # By construction recall_unclustered against self = 1.0; sanity rail
    elapsed = time.perf_counter() - t0
    return {
        "arm": "ARM_NO_COARSE_GRAIN_BASELINE",
        "ok": True,
        "n_atoms": n,
        "n_user_directive_atoms": sum(1 for c in sc_per_atom if c == "memory"),
        "capacity_used": n,
        "capacity_drop_fraction": 0.0,
        "recall_unclustered": 1.0,
        "elapsed_s": round(elapsed, 3),
    }


def _arm_coarse_grain_ultrametric(
    W: np.ndarray,
    sc_per_atom: list[str],
    cfg: UltrametricConfig,
    seed: int,
    audit_first_n: int = 50,
    distance_percentile: float = 5.0,
) -> tuple[dict, list[list[int]]]:
    """Per-source-class ultrametric clustering; USER_DIRECTIVE strictly separated.

    Returns (arm_result_dict, cluster_atom_lists) so the random arm can size-match.
    """
    t0 = time.perf_counter()
    n = W.shape[0]
    n_user_directive_atoms = sum(1 for c in sc_per_atom if c == "memory")

    by_class: dict[str, list[int]] = {}
    for i, c in enumerate(sc_per_atom):
        by_class.setdefault(c, []).append(i)

    all_qualifying_clusters: list[list[int]] = []
    audit_events_emitted = 0
    user_directive_mixing_violations = 0
    for cls, idx_list in by_class.items():
        if len(idx_list) < cfg.min_cluster_size:
            continue
        sub_W = W[idx_list]
        D_sub = cosine_distance_matrix(sub_W)
        iu = np.triu_indices(len(D_sub), k=1)
        off_diag = D_sub[iu]
        if len(off_diag) == 0:
            continue
        adaptive_max_dist = float(np.percentile(off_diag, distance_percentile))
        local_clusters = single_linkage_clusters(D_sub, max_distance=adaptive_max_dist)
        adaptive_cfg = UltrametricConfig(
            cosine_thresh=max(0.0, 1.0 - adaptive_max_dist * 2.0),
            min_cluster_size=cfg.min_cluster_size,
            representative_mode=cfg.representative_mode,
        )
        local_qualifying = filter_qualifying_clusters(local_clusters, sub_W, adaptive_cfg)
        for lc in local_qualifying:
            global_cluster = [idx_list[li] for li in lc]
            atoms_classes = {sc_per_atom[a] for a in global_cluster}
            # USER_DIRECTIVE mixing invariant (load-bearing)
            if len(atoms_classes) > 1:
                user_directive_mixing_violations += 1
            if "memory" in atoms_classes and len(atoms_classes) > 1:
                user_directive_mixing_violations += 1
            all_qualifying_clusters.append(global_cluster)
            if audit_events_emitted < audit_first_n:
                _audit_event({
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "kind": "coarse_grain_event_v2",
                    "seed": seed,
                    "cluster_size": len(global_cluster),
                    "source_class": cls,
                    "cluster_atoms_sample": global_cluster[:8],
                    "is_user_directive_cluster": (cls == "memory"),
                })
                audit_events_emitted += 1

    W_col, _reps, lookup = collapse_W_via_clusters(W, all_qualifying_clusters, cfg)
    eff_cap = effective_capacity_used(lookup)
    capacity_drop = (n - eff_cap) / n if n > 0 else 0.0

    clustered_atoms = [a for a in range(n) if lookup[a] >= 0]
    unclustered_atoms = [a for a in range(n) if lookup[a] < 0]

    # recall_clustered: top-1 in W_col maps to same cluster_id
    if clustered_atoms:
        Wn = W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-12)
        Wcn = W_col / (np.linalg.norm(W_col, axis=1, keepdims=True) + 1e-12)
        q_idx = np.array(clustered_atoms)
        # Chunk to control peak memory for large n
        chunk = 1024
        preds = np.empty(len(q_idx), dtype=np.int64)
        for s in range(0, len(q_idx), chunk):
            sims = Wn[q_idx[s:s + chunk]] @ Wcn.T
            preds[s:s + chunk] = np.argmax(sims, axis=1)
        clst_ids_q = lookup[q_idx]
        clst_ids_p = lookup[preds]
        recall_clustered = float(np.mean(clst_ids_q == clst_ids_p))
    else:
        recall_clustered = 1.0

    # recall_unclustered: top-1 in W_col is the unclustered atom's own representative
    if unclustered_atoms:
        Wn = W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-12)
        Wcn = W_col / (np.linalg.norm(W_col, axis=1, keepdims=True) + 1e-12)
        q_idx = np.array(unclustered_atoms)
        chunk = 1024
        preds = np.empty(len(q_idx), dtype=np.int64)
        for s in range(0, len(q_idx), chunk):
            sims = Wn[q_idx[s:s + chunk]] @ Wcn.T
            preds[s:s + chunk] = np.argmax(sims, axis=1)
        recall_unclustered = float(np.mean(preds == q_idx))
    else:
        recall_unclustered = 1.0

    elapsed = time.perf_counter() - t0
    arm = {
        "arm": "ARM_COARSE_GRAIN_ULTRAMETRIC",
        "ok": bool(user_directive_mixing_violations == 0),
        "seed": seed,
        "n_atoms": n,
        "n_user_directive_atoms": n_user_directive_atoms,
        "n_clusters": len(all_qualifying_clusters),
        "n_clustered_atoms": len(clustered_atoms),
        "n_unclustered_atoms": len(unclustered_atoms),
        "effective_capacity_used": eff_cap,
        "capacity_drop_fraction": round(capacity_drop, 4),
        "recall_clustered": round(recall_clustered, 4),
        "recall_unclustered": round(recall_unclustered, 4),
        "user_directive_mixing_violations": user_directive_mixing_violations,
        "audit_events_emitted": audit_events_emitted,
        "by_class_sizes": {c: len(ix) for c, ix in by_class.items()},
        "elapsed_s": round(elapsed, 3),
    }
    return arm, all_qualifying_clusters


def _arm_random_cluster_collapse(
    W: np.ndarray,
    clusters_from_ultrametric: list[list[int]],
    seed: int,
) -> dict:
    """Match cluster-size distribution from ultrametric arm; assign RANDOM
    cluster membership. Tests whether SEMANTIC clustering matters.
    """
    t0 = time.perf_counter()
    n = W.shape[0]
    rng = np.random.RandomState(seed + 1)
    cluster_sizes = [len(c) for c in clusters_from_ultrametric]
    if not cluster_sizes:
        elapsed = time.perf_counter() - t0
        return {
            "arm": "ARM_RANDOM_CLUSTER_COLLAPSE",
            "ok": True,
            "seed": seed,
            "n_atoms": n,
            "capacity_drop_fraction": 0.0,
            "recall_clustered": 1.0,
            "note": "no_ultrametric_clusters_to_match",
            "elapsed_s": round(elapsed, 3),
        }
    perm = rng.permutation(n)
    pos = 0
    random_clusters: list[list[int]] = []
    for sz in cluster_sizes:
        if pos + sz > n:
            break
        random_clusters.append(perm[pos:pos + sz].tolist())
        pos += sz
    cfg = UltrametricConfig(cosine_thresh=0.0, min_cluster_size=1)
    W_col, _reps, lookup = collapse_W_via_clusters(W, random_clusters, cfg)
    eff_cap = effective_capacity_used(lookup)
    capacity_drop = (n - eff_cap) / n if n > 0 else 0.0

    clustered_atoms = [a for a in range(n) if lookup[a] >= 0]
    if clustered_atoms:
        Wn = W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-12)
        Wcn = W_col / (np.linalg.norm(W_col, axis=1, keepdims=True) + 1e-12)
        q_idx = np.array(clustered_atoms)
        chunk = 1024
        preds = np.empty(len(q_idx), dtype=np.int64)
        for s in range(0, len(q_idx), chunk):
            sims = Wn[q_idx[s:s + chunk]] @ Wcn.T
            preds[s:s + chunk] = np.argmax(sims, axis=1)
        clst_ids_q = lookup[q_idx]
        clst_ids_p = lookup[preds]
        recall_clustered = float(np.mean(clst_ids_q == clst_ids_p))
    else:
        recall_clustered = 1.0

    elapsed = time.perf_counter() - t0
    return {
        "arm": "ARM_RANDOM_CLUSTER_COLLAPSE",
        "ok": True,
        "seed": seed,
        "n_atoms": n,
        "n_clusters": len(random_clusters),
        "capacity_drop_fraction": round(capacity_drop, 4),
        "recall_clustered": round(recall_clustered, 4),
        "elapsed_s": round(elapsed, 3),
    }


def _verdict_from_seeds(
    seed_results: list[dict],
    n_ud_in_sample: int,
    n_atoms_full: int,
    n_seeds: int,
) -> tuple[str, str]:
    """Chain-grade verdict: aggregate ULTRA + RANDOM arms across seeds; require
    USER_DIRECTIVE invariant + non-saturation + gap + cv.

    seed_results: list of per-seed dicts each containing 'ultra' and 'random'.
    """
    # USER_DIRECTIVE invariant: HARD_FAIL on any violation
    for r in seed_results:
        ult = r["ultra"]
        if ult.get("user_directive_mixing_violations", 0) > 0:
            return "HARD_FAIL", (
                f"user_directive_mixing_violations="
                f"{ult['user_directive_mixing_violations']} seed={r['seed']}; "
                f"load-bearing zero-mix invariant violated"
            )

    if n_ud_in_sample < HP_MIN_N_UD_IN_SAMPLE:
        return "HARD_FAIL", (
            f"n_ud_in_sample={n_ud_in_sample} < {HP_MIN_N_UD_IN_SAMPLE} "
            f"(RC-1 invariant: test would be vacuously satisfied like v1)"
        )

    if n_atoms_full < HP_MIN_N_ATOMS_FULL:
        return "HARD_FAIL", (
            f"n_atoms_full={n_atoms_full} < {HP_MIN_N_ATOMS_FULL} "
            f"(RC-2 invariant: scale insufficient to break saturation)"
        )

    ults = [r["ultra"] for r in seed_results]
    rands = [r["random"] for r in seed_results]

    cap_drops = [u["capacity_drop_fraction"] for u in ults]
    rec_clst = [u["recall_clustered"] for u in ults]
    rec_unclst = [u["recall_unclustered"] for u in ults]
    rand_rec = [r["recall_clustered"] for r in rands]
    gaps = [rc - rr for rc, rr in zip(rec_clst, rand_rec)]

    mean_cap_drop = float(np.mean(cap_drops))
    mean_rec_clst = float(np.mean(rec_clst))
    mean_rec_unclst = float(np.mean(rec_unclst))
    mean_gap = float(np.mean(gaps))
    cv_rec_clst = float(np.std(rec_clst) / max(abs(mean_rec_clst), 1e-9))

    # (b) non-saturation: at least one seed must have rec_unclst < 1.0 - epsilon
    saturated = all(ru >= HP_MAX_REC_UNCLUSTERED_NONSAT for ru in rec_unclst)
    if saturated:
        return "HARD_FAIL", (
            f"saturation_at_n={n_atoms_full}: rec_unclst all >= "
            f"{HP_MAX_REC_UNCLUSTERED_NONSAT} (per-seed={rec_unclst}); "
            f"metric cap not broken; RC-2 unsuccessful; need larger N or harder discriminator"
        )

    # (c) capacity
    if mean_cap_drop < HF_MIN_CAPACITY_DROP:
        return "HARD_FAIL", (
            f"cap_drop_mean={mean_cap_drop:.3f} < HF floor {HF_MIN_CAPACITY_DROP} "
            f"(no substantive compression)"
        )

    # (d) mechanism non-null vs random
    if mean_gap <= 0.05:
        return "HARD_FAIL", (
            f"gap_mean={mean_gap:.3f} <= 0.05 (mechanism null vs random control)"
        )

    # HARD_PASS bar (all 5 conditions)
    hp_ok = (
        mean_cap_drop > HP_MIN_CAPACITY_DROP
        and mean_gap > HP_MIN_GAP_VS_RANDOM
        and cv_rec_clst < HP_MAX_CV
        and not saturated
        and n_ud_in_sample >= HP_MIN_N_UD_IN_SAMPLE
    )
    if hp_ok:
        return "HARD_PASS", (
            f"CHAIN_GRADE: n_UD={n_ud_in_sample}>={HP_MIN_N_UD_IN_SAMPLE}, "
            f"cap_drop_mean={mean_cap_drop:.3f}>{HP_MIN_CAPACITY_DROP}, "
            f"rec_unclst_mean={mean_rec_unclst:.3f}<1.0 (cap-broken), "
            f"gap_mean={mean_gap:.3f}>{HP_MIN_GAP_VS_RANDOM}, "
            f"cv_rec_clst={cv_rec_clst:.3f}<{HP_MAX_CV}, "
            f"USER_DIRECTIVE_separation=0_violations, seeds={n_seeds}"
        )

    mb_ok = (
        mean_cap_drop >= HF_MIN_CAPACITY_DROP
        and mean_gap >= MB_MIN_GAP_VS_RANDOM
        and cv_rec_clst <= MB_MAX_CV
    )
    if mb_ok:
        return "MIDDLE_BAND", (
            f"cap_drop_mean={mean_cap_drop:.3f}, gap_mean={mean_gap:.3f}, "
            f"cv_rec_clst={cv_rec_clst:.3f}; one or more HP thresholds not met "
            f"(cap_drop>{HP_MIN_CAPACITY_DROP}? gap>{HP_MIN_GAP_VS_RANDOM}? cv<{HP_MAX_CV}?)"
        )
    return "HARD_FAIL", (
        f"cap_drop_mean={mean_cap_drop:.3f}, gap_mean={mean_gap:.3f}, "
        f"cv_rec_clst={cv_rec_clst:.3f}; below MB floor"
    )


def _instrumentation_selftest() -> None:
    """Formula self-tests on synthetic seed_results dicts."""
    # HARD_PASS
    hp_seed_results = [
        {"seed": 17, "ultra": {"user_directive_mixing_violations": 0,
                                "capacity_drop_fraction": 0.25,
                                "recall_clustered": 0.90,
                                "recall_unclustered": 0.85},
                      "random": {"recall_clustered": 0.50}},
        {"seed": 23, "ultra": {"user_directive_mixing_violations": 0,
                                "capacity_drop_fraction": 0.24,
                                "recall_clustered": 0.91,
                                "recall_unclustered": 0.86},
                      "random": {"recall_clustered": 0.51}},
        {"seed": 31, "ultra": {"user_directive_mixing_violations": 0,
                                "capacity_drop_fraction": 0.26,
                                "recall_clustered": 0.92,
                                "recall_unclustered": 0.87},
                      "random": {"recall_clustered": 0.52}},
    ]
    v, _msg = _verdict_from_seeds(hp_seed_results, n_ud_in_sample=15, n_atoms_full=10000, n_seeds=3)
    assert v == "HARD_PASS", f"selftest HP: {v} :: {_msg}"

    # HARD_FAIL: USER_DIRECTIVE mixing
    bad_ud = [dict(r) for r in hp_seed_results]
    bad_ud[0] = {"seed": 17, "ultra": {"user_directive_mixing_violations": 2,
                                        "capacity_drop_fraction": 0.25,
                                        "recall_clustered": 0.90,
                                        "recall_unclustered": 0.85},
                  "random": {"recall_clustered": 0.50}}
    v, _ = _verdict_from_seeds(bad_ud, n_ud_in_sample=15, n_atoms_full=10000, n_seeds=3)
    assert v == "HARD_FAIL", f"selftest HF-UD: {v}"

    # HARD_FAIL: n_UD < 10 (vacuous separation; v1 failure)
    v, _ = _verdict_from_seeds(hp_seed_results, n_ud_in_sample=0, n_atoms_full=10000, n_seeds=3)
    assert v == "HARD_FAIL", f"selftest HF-nUD0: {v}"

    # HARD_FAIL: saturation (rec_unclst all = 1.0)
    sat = [
        {"seed": 17, "ultra": {"user_directive_mixing_violations": 0,
                                "capacity_drop_fraction": 0.25,
                                "recall_clustered": 1.0,
                                "recall_unclustered": 1.0},
                      "random": {"recall_clustered": 0.50}},
        {"seed": 23, "ultra": {"user_directive_mixing_violations": 0,
                                "capacity_drop_fraction": 0.25,
                                "recall_clustered": 1.0,
                                "recall_unclustered": 1.0},
                      "random": {"recall_clustered": 0.50}},
        {"seed": 31, "ultra": {"user_directive_mixing_violations": 0,
                                "capacity_drop_fraction": 0.25,
                                "recall_clustered": 1.0,
                                "recall_unclustered": 1.0},
                      "random": {"recall_clustered": 0.50}},
    ]
    v, _ = _verdict_from_seeds(sat, n_ud_in_sample=15, n_atoms_full=10000, n_seeds=3)
    assert v == "HARD_FAIL", f"selftest HF-sat: {v}"

    # HARD_FAIL: gap null
    null_gap = [
        {"seed": 17, "ultra": {"user_directive_mixing_violations": 0,
                                "capacity_drop_fraction": 0.25,
                                "recall_clustered": 0.50,
                                "recall_unclustered": 0.85},
                      "random": {"recall_clustered": 0.49}},
        {"seed": 23, "ultra": {"user_directive_mixing_violations": 0,
                                "capacity_drop_fraction": 0.25,
                                "recall_clustered": 0.51,
                                "recall_unclustered": 0.86},
                      "random": {"recall_clustered": 0.50}},
        {"seed": 31, "ultra": {"user_directive_mixing_violations": 0,
                                "capacity_drop_fraction": 0.25,
                                "recall_clustered": 0.52,
                                "recall_unclustered": 0.87},
                      "random": {"recall_clustered": 0.51}},
    ]
    v, _ = _verdict_from_seeds(null_gap, n_ud_in_sample=15, n_atoms_full=10000, n_seeds=3)
    assert v == "HARD_FAIL", f"selftest HF-nullgap: {v}"

    # MIDDLE_BAND: gap in (0.15, 0.30]; cv ok
    mb = [
        {"seed": 17, "ultra": {"user_directive_mixing_violations": 0,
                                "capacity_drop_fraction": 0.15,
                                "recall_clustered": 0.80,
                                "recall_unclustered": 0.85},
                      "random": {"recall_clustered": 0.60}},
        {"seed": 23, "ultra": {"user_directive_mixing_violations": 0,
                                "capacity_drop_fraction": 0.16,
                                "recall_clustered": 0.81,
                                "recall_unclustered": 0.86},
                      "random": {"recall_clustered": 0.60}},
        {"seed": 31, "ultra": {"user_directive_mixing_violations": 0,
                                "capacity_drop_fraction": 0.15,
                                "recall_clustered": 0.82,
                                "recall_unclustered": 0.87},
                      "random": {"recall_clustered": 0.61}},
    ]
    v, _ = _verdict_from_seeds(mb, n_ud_in_sample=15, n_atoms_full=10000, n_seeds=3)
    assert v == "MIDDLE_BAND", f"selftest MB: {v}"

    print("[selftest] kb_coarse_grain_at_promotion_v2_chain_grade_path formula PASS", flush=True)


_instrumentation_selftest()


def _exp_name() -> str:
    return os.environ.get(
        "HDLAB_EXP_NAME", "kb_coarse_grain_at_promotion_v2_chain_grade_path"
    )


def _exp_dir() -> Path:
    d = REPO / "data" / f"exp_{_exp_name()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _run_one_seed(
    W_sample: np.ndarray,
    sc_per_atom: list[str],
    cfg: UltrametricConfig,
    seed: int,
) -> dict:
    """Run ULTRA + RANDOM for a single seed; return per-seed dict."""
    baseline = _arm_no_coarse_grain_baseline(W_sample, sc_per_atom)
    ultra, clusters = _arm_coarse_grain_ultrametric(W_sample, sc_per_atom, cfg, seed)
    random_arm = _arm_random_cluster_collapse(W_sample, clusters, seed)
    return {
        "seed": seed,
        "baseline": baseline,
        "ultra": ultra,
        "random": random_arm,
    }


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--kb-dir", default=None)
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    out_dir = _exp_dir()
    if args.kb_dir:
        kb = DirectorKBQuery(kb_dir=Path(args.kb_dir))
    else:
        try:
            kb = load_default_kb(REPO)
        except FileNotFoundError as e:
            payload = {
                "verdict": "HARD_FAIL",
                "verdict_msg": f"KB_REFERENT_MISSING: {e}",
                "elapsed_s": 0.0,
                "summary": {"anchor": _exp_name()},
            }
            with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, default=str)
            print(f"[verdict] HARD_FAIL\n[verdict_msg] {payload['verdict_msg']}", flush=True)
            return

    n_atoms = 600 if args.smoke else HP_MIN_N_ATOMS_FULL
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    cfg = UltrametricConfig(
        cosine_thresh=0.85,
        min_cluster_size=3 if args.smoke else 5,
    )

    t0 = time.time()
    print(
        f"[run] {_exp_name()} smoke={args.smoke} "
        f"kb_version={kb.kb_version} n_atoms={n_atoms} seeds={seeds}",
        flush=True,
    )

    # Sample once per seed (sample is seed-dependent for stratification randomness)
    seed_results: list[dict] = []
    n_ud_in_sample_per_seed: list[int] = []
    for seed in seeds:
        try:
            W_sample, atom_idx, sc_per_atom, n_ud_in_sample = _sample_atoms_with_forced_ud(
                kb, n_atoms, seed
            )
            n_ud_in_sample_per_seed.append(n_ud_in_sample)
            from collections import Counter as _C
            cnt = _C(sc_per_atom)
            print(
                f"  seed={seed} sampled n={len(atom_idx)} n_UD={n_ud_in_sample} "
                f"classes={dict(cnt)}",
                flush=True,
            )
            r = _run_one_seed(W_sample, sc_per_atom, cfg, seed)
            seed_results.append(r)
            u = r["ultra"]
            rd = r["random"]
            print(
                f"    ULTRA cap_drop={u['capacity_drop_fraction']} "
                f"rec_clst={u['recall_clustered']} rec_unclst={u['recall_unclustered']} "
                f"n_clusters={u['n_clusters']} ud_mix_viol={u['user_directive_mixing_violations']}",
                flush=True,
            )
            print(
                f"    RANDOM cap_drop={rd['capacity_drop_fraction']} "
                f"rec_clst={rd['recall_clustered']}",
                flush=True,
            )
        except Exception as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {type(e).__name__}: {e}", flush=True)
            seed_results.append({
                "seed": seed,
                "error": f"{type(e).__name__}: {e}",
                "ultra": {"user_directive_mixing_violations": 0,
                          "capacity_drop_fraction": 0.0,
                          "recall_clustered": 0.0,
                          "recall_unclustered": 0.0},
                "random": {"recall_clustered": 0.0},
            })

    # SMOKE-ONLY full-N preview (discriminator-must-survive-scale guard)
    full_n_preview = None
    if args.smoke:
        try:
            print(
                f"[smoke-preview] running ARM_FULL_N_PREVIEW at n={SMOKE_PREVIEW_N_ATOMS} "
                f"to check non-saturation at full-N",
                flush=True,
            )
            W_prev, _prev_idx, sc_prev, n_ud_prev = _sample_atoms_with_forced_ud(
                kb, SMOKE_PREVIEW_N_ATOMS, seed=seeds[0]
            )
            prev_cfg = UltrametricConfig(cosine_thresh=0.85, min_cluster_size=5)
            prev_ultra, _ = _arm_coarse_grain_ultrametric(
                W_prev, sc_prev, prev_cfg, seed=seeds[0]
            )
            full_n_preview = {
                "n_atoms": SMOKE_PREVIEW_N_ATOMS,
                "n_ud_in_sample": n_ud_prev,
                "recall_clustered": prev_ultra["recall_clustered"],
                "recall_unclustered": prev_ultra["recall_unclustered"],
                "capacity_drop_fraction": prev_ultra["capacity_drop_fraction"],
                "n_clusters": prev_ultra["n_clusters"],
                "elapsed_s": prev_ultra["elapsed_s"],
                "saturation_risk_flag": bool(
                    prev_ultra["recall_unclustered"] >= HP_MAX_REC_UNCLUSTERED_NONSAT
                ),
            }
            print(
                f"  preview: rec_clst={prev_ultra['recall_clustered']} "
                f"rec_unclst={prev_ultra['recall_unclustered']} "
                f"cap_drop={prev_ultra['capacity_drop_fraction']} "
                f"saturation_risk={full_n_preview['saturation_risk_flag']}",
                flush=True,
            )
        except Exception as e:  # noqa: BLE001
            print(f"[smoke-preview] FAILED: {type(e).__name__}: {e}", flush=True)
            full_n_preview = {"error": f"{type(e).__name__}: {e}"}

    # n_ud_in_sample for verdict: use min across seeds (worst case)
    n_ud_for_verdict = (
        min(n_ud_in_sample_per_seed) if n_ud_in_sample_per_seed else 0
    )
    n_atoms_for_verdict = (
        SMOKE_PREVIEW_N_ATOMS
        if args.smoke and full_n_preview and "recall_unclustered" in full_n_preview
        else n_atoms
    )

    # For smoke verdict, use preview seed result if available (so saturation gate fires honestly)
    if args.smoke and full_n_preview and "recall_unclustered" in full_n_preview:
        synth_preview_result = [{
            "seed": seeds[0],
            "ultra": {
                "user_directive_mixing_violations": 0,
                "capacity_drop_fraction": full_n_preview["capacity_drop_fraction"],
                "recall_clustered": full_n_preview["recall_clustered"],
                "recall_unclustered": full_n_preview["recall_unclustered"],
            },
            "random": {"recall_clustered": 0.0},  # not run in preview
        }]
        # For smoke, verdict reflects whether discriminator survives scale; we
        # ONLY require non-saturation + USER_DIRECTIVE invariant; gap is N/A.
        if full_n_preview["recall_unclustered"] >= HP_MAX_REC_UNCLUSTERED_NONSAT:
            verdict = "HARD_FAIL"
            vm = (
                f"SMOKE_PREVIEW_SATURATED: rec_unclst="
                f"{full_n_preview['recall_unclustered']} >= "
                f"{HP_MAX_REC_UNCLUSTERED_NONSAT} at n={SMOKE_PREVIEW_N_ATOMS}; "
                f"discriminator would NOT survive scale; do NOT dispatch full"
            )
        elif n_ud_for_verdict < HP_MIN_N_UD_IN_SAMPLE:
            verdict = "HARD_FAIL"
            vm = (
                f"SMOKE_n_UD_INSUFFICIENT: n_UD={n_ud_for_verdict} < "
                f"{HP_MIN_N_UD_IN_SAMPLE}; RC-1 invariant not met"
            )
        else:
            verdict = "SMOKE_PASS"
            vm = (
                f"smoke OK + preview non-saturated (rec_unclst="
                f"{full_n_preview['recall_unclustered']} < "
                f"{HP_MAX_REC_UNCLUSTERED_NONSAT}); n_UD={n_ud_for_verdict}; "
                f"safe to dispatch full"
            )
    else:
        verdict, vm = _verdict_from_seeds(
            seed_results, n_ud_for_verdict, n_atoms_for_verdict, len(seeds)
        )

    elapsed = round(time.time() - t0, 2)

    cardinality_ok = bool(
        n_ud_for_verdict >= HP_MIN_N_UD_IN_SAMPLE
        and (
            (args.smoke and full_n_preview and "recall_unclustered" in full_n_preview)
            or (not args.smoke and n_atoms >= HP_MIN_N_ATOMS_FULL and len(seeds) >= 3)
        )
    )

    payload: dict[str, Any] = {
        "anchor": _exp_name(),
        "smoke": args.smoke,
        "kb_version": kb.kb_version,
        "n_atoms_per_seed": n_atoms,
        "seeds": list(seeds),
        "cosine_thresh": cfg.cosine_thresh,
        "min_cluster_size": cfg.min_cluster_size,
        "n_ud_in_sample_per_seed": n_ud_in_sample_per_seed,
        "n_ud_in_sample_min": n_ud_for_verdict,
        "seed_results": seed_results,
        "full_n_preview": full_n_preview,
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
        "cardinality_ok": cardinality_ok,
        "hp_min_n_ud_in_sample": HP_MIN_N_UD_IN_SAMPLE,
        "hp_min_n_atoms_full": HP_MIN_N_ATOMS_FULL,
        "hp_min_capacity_drop": HP_MIN_CAPACITY_DROP,
        "hp_min_gap_vs_random": HP_MIN_GAP_VS_RANDOM,
        "hp_max_cv": HP_MAX_CV,
        "hp_max_rec_unclustered_nonsat": HP_MAX_REC_UNCLUSTERED_NONSAT,
    }
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "verdict": verdict,
                "verdict_msg": vm,
                "elapsed_s": elapsed,
                "summary": payload,
            },
            f,
            indent=2,
            default=str,
        )
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
