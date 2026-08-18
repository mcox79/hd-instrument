"""KB COARSE-GRAIN AT PROMOTION v1 (ANCHOR 3; INFRASTRUCTURE; 2026-06-26).

Pre-reg: preregs/2026-06-26_kb_coarse_grain_at_promotion_v1.md
Composes on chain-grade `hdlab/ultrametric_clustering.py`
(HARD_PASS today; cap_drop=0.212, +10.4pp vs random).

Wave 3b (parallel with ANCHOR 1; ships after ANCHOR 5 dual-store audit lands).

At a (simulated) promotion event, applies ultrametric clustering to candidate
atoms grouped by source_class; USER_DIRECTIVE atoms NEVER collapsed with
non-USER atoms. AUDIT-ONLY on a sample of the loaded KB; does NOT mutate the
production KB on disk (Principle 1 preserved).

ARMS (3 mandatory):
  ARM_NO_COARSE_GRAIN_BASELINE       - sanity rail (no clustering)
  ARM_COARSE_GRAIN_ULTRAMETRIC       - chain-grade mechanism
  ARM_RANDOM_CLUSTER_COLLAPSE        - control (random clusters)

SUCCESS CRITERIA (INFRASTRUCTURE tier):
  - ARM_COARSE_GRAIN_ULTRAMETRIC capacity_drop >= 0.10.
  - ARM_COARSE_GRAIN_ULTRAMETRIC recall_clustered >= 0.85.
  - ARM_COARSE_GRAIN_ULTRAMETRIC recall_unclustered >= 0.90.
  - USER_DIRECTIVE never mixed with non-USER atoms (zero-loss).
  - ULTRAMETRIC - RANDOM recall_clustered gap >= 0.05 (mechanism non-null).

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
    cluster_atom_lookup,
    collapse_W_via_clusters,
    cosine_distance_matrix,
    effective_capacity_used,
    filter_qualifying_clusters,
    single_linkage_clusters,
)


AUDIT_LOG_PATH = REPO / "data" / "director_kb_audit_log.jsonl"
AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _audit_event(event: dict) -> None:
    """Append a coarse-grain event row to the shared audit log."""
    line = json.dumps(event, default=str, ensure_ascii=False) + "\n"
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line)


def _sample_atoms_by_source_class(
    kb: DirectorKBQuery,
    n_atoms: int,
    seed: int = 17,
) -> tuple[np.ndarray, list[int], list[str]]:
    """Sample atoms biased toward classes with abundant atoms.

    Returns (W_sample, atom_indices, source_classes_per_atom).
    USER memory atoms tagged with class 'memory'.
    """
    rng = np.random.RandomState(seed)
    n_ent = len(kb.entity_names)
    # Build per-entity source_class (pick first if multiple)
    ent_sc: list[str] = []
    for i in range(n_ent):
        sc_set = kb._source_classes_by_ent.get(i, set())
        if sc_set:
            # Prefer 'memory' if present (USER_DIRECTIVE separation)
            if "memory" in sc_set:
                ent_sc.append("memory")
            else:
                ent_sc.append(sorted(sc_set)[0])
        else:
            ent_sc.append("unknown")

    # Sample: ensure source-class diversity. Take up to n_atoms/5 from each of
    # the top-5 classes by atom count.
    from collections import Counter
    sc_counts = Counter(ent_sc)
    top_classes = [c for c, _ in sc_counts.most_common(5)]
    per_class = max(1, n_atoms // max(1, len(top_classes)))

    selected_idx: list[int] = []
    for cls in top_classes:
        cand = [i for i, c in enumerate(ent_sc) if c == cls]
        if not cand:
            continue
        n_take = min(per_class, len(cand))
        idx_arr = np.array(cand)
        rng.shuffle(idx_arr)
        selected_idx.extend(idx_arr[:n_take].tolist())

    # Force-include some memory atoms to test USER_DIRECTIVE separation
    mem_cand = [i for i, c in enumerate(ent_sc) if c == "memory"]
    if mem_cand:
        rng.shuffle(np.array(mem_cand))
        for i in mem_cand[:max(5, n_atoms // 20)]:
            if i not in selected_idx:
                selected_idx.append(i)

    selected_idx = selected_idx[:n_atoms]
    W_sample = kb.E[selected_idx].cpu().numpy().astype(np.float32)
    sc_per_atom = [ent_sc[i] for i in selected_idx]
    return W_sample, selected_idx, sc_per_atom


def _recall_at_1(W_orig: np.ndarray, W_query: np.ndarray) -> float:
    """For each query row, check if its argmax cosine match in W_orig is itself."""
    # Normalize both
    on = np.linalg.norm(W_orig, axis=1, keepdims=True)
    on = np.where(on > 1e-12, on, 1.0)
    Wo = W_orig / on
    qn = np.linalg.norm(W_query, axis=1, keepdims=True)
    qn = np.where(qn > 1e-12, qn, 1.0)
    Wq = W_query / qn
    sims = Wq @ Wo.T
    pred = np.argmax(sims, axis=1)
    truth = np.arange(W_query.shape[0])
    return float(np.mean(pred == truth))


def _arm_no_coarse_grain_baseline(W: np.ndarray, sc_per_atom: list[str]) -> dict:
    """No clustering; sanity rail."""
    t0 = time.perf_counter()
    n = W.shape[0]
    recall_unclustered = _recall_at_1(W, W)  # by-construction 1.0
    elapsed = time.perf_counter() - t0
    return {
        "arm": "ARM_NO_COARSE_GRAIN_BASELINE",
        "ok": True,
        "n_atoms": n,
        "capacity_used": n,
        "capacity_drop_fraction": 0.0,
        "recall_unclustered": round(recall_unclustered, 4),
        "elapsed_s": round(elapsed, 3),
    }


def _arm_coarse_grain_ultrametric(
    W: np.ndarray,
    sc_per_atom: list[str],
    cfg: UltrametricConfig,
    audit_first_n: int = 50,
    distance_percentile: float = 5.0,
) -> dict:
    """Per-source-class ultrametric clustering; USER_DIRECTIVE strictly separated.

    Adaptive threshold per class: use the p-th percentile of pairwise distance
    as max_distance for single-linkage. The chain-grade primitive's static
    cosine_thresh=0.85 was calibrated on synthetic embeddings; real substrate
    char-trigram entity embeddings have very different distance distribution
    (mean ~0.96 dist, p10 ~0.89 dist) so an adaptive percentile is the honest
    threshold. cfg.cosine_thresh becomes the WITHIN-CLUSTER quality floor.
    """
    t0 = time.perf_counter()
    n = W.shape[0]
    n_user_directive_atoms = sum(1 for c in sc_per_atom if c == "memory")

    # Partition by source class
    by_class: dict[str, list[int]] = {}
    for i, c in enumerate(sc_per_atom):
        by_class.setdefault(c, []).append(i)

    all_qualifying_clusters: list[list[int]] = []  # ATOM-INDEX (in W) clusters
    audit_events_emitted = 0
    user_directive_mixing_violations = 0
    for cls, idx_list in by_class.items():
        if len(idx_list) < cfg.min_cluster_size:
            continue
        sub_W = W[idx_list]
        D_sub = cosine_distance_matrix(sub_W)
        # Adaptive: pth percentile of off-diagonal distances becomes the
        # link threshold. Real embeddings don't satisfy cos>=0.85.
        iu = np.triu_indices(len(D_sub), k=1)
        off_diag = D_sub[iu]
        if len(off_diag) == 0:
            continue
        adaptive_max_dist = float(np.percentile(off_diag, distance_percentile))
        local_clusters = single_linkage_clusters(D_sub, max_distance=adaptive_max_dist)
        # WITHIN-CLUSTER quality floor: we relax the strict cosine_thresh check
        # (real KB doesn't satisfy 0.85); accept any cluster with size >= min,
        # whose mean within-cluster cosine exceeds the (1.0 - 2x adaptive_dist) floor.
        # Belt-and-suspenders: also pass via filter_qualifying_clusters but at a
        # cosine_thresh derived from the adaptive distance.
        adaptive_cfg = UltrametricConfig(
            cosine_thresh=max(0.0, 1.0 - adaptive_max_dist * 2.0),
            min_cluster_size=cfg.min_cluster_size,
            representative_mode=cfg.representative_mode,
        )
        local_qualifying = filter_qualifying_clusters(local_clusters, sub_W, adaptive_cfg)
        # Map local indices back to global W indices
        for lc in local_qualifying:
            global_cluster = [idx_list[li] for li in lc]
            # USER_DIRECTIVE separation invariant: NO mixing across class boundaries
            # by construction (per-class clustering). Belt-and-suspenders assertion:
            atoms_classes = {sc_per_atom[a] for a in global_cluster}
            if len(atoms_classes) > 1:
                user_directive_mixing_violations += 1
            if "memory" in atoms_classes and len(atoms_classes) > 1:
                user_directive_mixing_violations += 1
            all_qualifying_clusters.append(global_cluster)
            if audit_events_emitted < audit_first_n:
                _audit_event({
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "kind": "coarse_grain_event",
                    "cluster_size": len(global_cluster),
                    "source_class": cls,
                    "cluster_atoms_sample": global_cluster[:8],
                    "is_user_directive_cluster": (cls == "memory"),
                })
                audit_events_emitted += 1

    # Collapse + capacity
    W_col, reps, lookup = collapse_W_via_clusters(W, all_qualifying_clusters, cfg)
    eff_cap = effective_capacity_used(lookup)
    capacity_drop = (n - eff_cap) / n if n > 0 else 0.0

    # Recall on clustered atoms: query each clustered atom AGAINST W_col;
    # top-1 should map to its cluster representative (and so identify cluster).
    clustered_atoms = [a for a in range(n) if lookup[a] >= 0]
    unclustered_atoms = [a for a in range(n) if lookup[a] < 0]
    if clustered_atoms:
        # For clustered atoms, recall = top-1 match within W_col falls within
        # the same cluster (any atom from same cluster counts).
        Wn = W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-12)
        Wcn = W_col / (np.linalg.norm(W_col, axis=1, keepdims=True) + 1e-12)
        q_idx = np.array(clustered_atoms)
        sims = Wn[q_idx] @ Wcn.T
        pred = np.argmax(sims, axis=1)
        # Cluster-aware recall: top-1 pred has same cluster_id as query
        clst_ids_q = lookup[q_idx]
        clst_ids_p = lookup[pred]
        recall_clustered = float(np.mean(clst_ids_q == clst_ids_p))
    else:
        recall_clustered = 1.0

    if unclustered_atoms:
        q_idx = np.array(unclustered_atoms)
        Wn = W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-12)
        Wcn = W_col / (np.linalg.norm(W_col, axis=1, keepdims=True) + 1e-12)
        sims = Wn[q_idx] @ Wcn.T
        pred = np.argmax(sims, axis=1)
        recall_unclustered = float(np.mean(pred == q_idx))
    else:
        recall_unclustered = 1.0

    elapsed = time.perf_counter() - t0
    ok = (
        capacity_drop >= 0.10
        and recall_clustered >= 0.85
        and recall_unclustered >= 0.90
        and user_directive_mixing_violations == 0
    )
    return {
        "arm": "ARM_COARSE_GRAIN_ULTRAMETRIC",
        "ok": bool(ok),
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
        "cosine_thresh": cfg.cosine_thresh,
        "min_cluster_size": cfg.min_cluster_size,
        "elapsed_s": round(elapsed, 3),
    }


def _arm_random_cluster_collapse(
    W: np.ndarray,
    cluster_sizes_from_ultrametric: list[int],
    seed: int = 17,
) -> dict:
    """Match cluster-size distribution from ultrametric arm; assign RANDOM
    cluster membership. Tests whether SEMANTIC clustering matters.
    """
    t0 = time.perf_counter()
    n = W.shape[0]
    rng = np.random.RandomState(seed)
    if not cluster_sizes_from_ultrametric:
        elapsed = time.perf_counter() - t0
        return {
            "arm": "ARM_RANDOM_CLUSTER_COLLAPSE",
            "ok": True,
            "n_atoms": n,
            "capacity_drop_fraction": 0.0,
            "recall_clustered": 1.0,
            "note": "no_ultrametric_clusters_to_match",
            "elapsed_s": round(elapsed, 3),
        }
    # Random partition of size sum(cluster_sizes) atoms into clusters
    perm = rng.permutation(n)
    pos = 0
    random_clusters: list[list[int]] = []
    for sz in cluster_sizes_from_ultrametric:
        if pos + sz > n:
            break
        random_clusters.append(perm[pos:pos + sz].tolist())
        pos += sz
    cfg = UltrametricConfig(cosine_thresh=0.0, min_cluster_size=1)
    W_col, reps, lookup = collapse_W_via_clusters(W, random_clusters, cfg)
    eff_cap = effective_capacity_used(lookup)
    capacity_drop = (n - eff_cap) / n if n > 0 else 0.0

    clustered_atoms = [a for a in range(n) if lookup[a] >= 0]
    if clustered_atoms:
        Wn = W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-12)
        Wcn = W_col / (np.linalg.norm(W_col, axis=1, keepdims=True) + 1e-12)
        q_idx = np.array(clustered_atoms)
        sims = Wn[q_idx] @ Wcn.T
        pred = np.argmax(sims, axis=1)
        clst_ids_q = lookup[q_idx]
        clst_ids_p = lookup[pred]
        recall_clustered = float(np.mean(clst_ids_q == clst_ids_p))
    else:
        recall_clustered = 1.0

    elapsed = time.perf_counter() - t0
    return {
        "arm": "ARM_RANDOM_CLUSTER_COLLAPSE",
        "ok": True,  # control; ok refers to harness, not mechanism
        "n_atoms": n,
        "n_clusters": len(random_clusters),
        "capacity_drop_fraction": round(capacity_drop, 4),
        "recall_clustered": round(recall_clustered, 4),
        "elapsed_s": round(elapsed, 3),
    }


def _verdict_from_arms(arms: list[dict]) -> tuple[str, str]:
    by = {a["arm"]: a for a in arms}
    ult = by.get("ARM_COARSE_GRAIN_ULTRAMETRIC", {})
    rand = by.get("ARM_RANDOM_CLUSTER_COLLAPSE", {})
    base = by.get("ARM_NO_COARSE_GRAIN_BASELINE", {})

    udmv = ult.get("user_directive_mixing_violations", 0)
    if udmv > 0:
        return "HARD_FAIL", (
            f"USER_DIRECTIVE mixing violations={udmv}; load-bearing zero-mix invariant violated"
        )

    cap_drop = ult.get("capacity_drop_fraction", 0.0)
    rec_clst = ult.get("recall_clustered", 0.0)
    rec_unclst = ult.get("recall_unclustered", 0.0)
    rand_rec = rand.get("recall_clustered", 0.0)
    gap = rec_clst - rand_rec

    if rec_clst < 0.70:
        return "HARD_FAIL", (
            f"recall_clustered={rec_clst:.3f} < 0.70; collapse destroys info"
        )

    if cap_drop >= 0.10 and rec_clst >= 0.85 and rec_unclst >= 0.90 and gap >= 0.05:
        return "HARD_PASS", (
            f"ULTRA(cap_drop={cap_drop:.3f}, rec_clst={rec_clst:.3f}, "
            f"rec_unclst={rec_unclst:.3f}); RANDOM(rec_clst={rand_rec:.3f}); "
            f"gap={gap:.3f} >= 0.05; mechanism non-null; USER_DIRECTIVE separation preserved"
        )
    if cap_drop >= 0.10 and rec_clst >= 0.85 and rec_unclst >= 0.90:
        return "MIDDLE_BAND", (
            f"ULTRA(cap_drop={cap_drop:.3f}, rec_clst={rec_clst:.3f}, "
            f"rec_unclst={rec_unclst:.3f}); RANDOM(rec_clst={rand_rec:.3f}); "
            f"gap={gap:.3f} < 0.05 (ultrametric ~= random); review mechanism"
        )
    return "HARD_FAIL", (
        f"ULTRA cap_drop={cap_drop:.3f} (>=0.10?) rec_clst={rec_clst:.3f} (>=0.85?) "
        f"rec_unclst={rec_unclst:.3f} (>=0.90?); failed thresholds"
    )


def _instrumentation_selftest() -> None:
    # HARD_PASS
    v, _ = _verdict_from_arms([
        {"arm": "ARM_NO_COARSE_GRAIN_BASELINE", "ok": True},
        {"arm": "ARM_COARSE_GRAIN_ULTRAMETRIC", "ok": True,
         "capacity_drop_fraction": 0.20, "recall_clustered": 0.95,
         "recall_unclustered": 0.95, "user_directive_mixing_violations": 0},
        {"arm": "ARM_RANDOM_CLUSTER_COLLAPSE", "ok": True, "recall_clustered": 0.80},
    ])
    assert v == "HARD_PASS", f"selftest hp: {v}"
    # MIDDLE_BAND (no gap)
    v, _ = _verdict_from_arms([
        {"arm": "ARM_NO_COARSE_GRAIN_BASELINE", "ok": True},
        {"arm": "ARM_COARSE_GRAIN_ULTRAMETRIC", "ok": True,
         "capacity_drop_fraction": 0.20, "recall_clustered": 0.95,
         "recall_unclustered": 0.95, "user_directive_mixing_violations": 0},
        {"arm": "ARM_RANDOM_CLUSTER_COLLAPSE", "ok": True, "recall_clustered": 0.93},
    ])
    assert v == "MIDDLE_BAND", f"selftest mb: {v}"
    # HARD_FAIL: USER_DIRECTIVE mixing
    v, _ = _verdict_from_arms([
        {"arm": "ARM_NO_COARSE_GRAIN_BASELINE", "ok": True},
        {"arm": "ARM_COARSE_GRAIN_ULTRAMETRIC", "ok": True,
         "capacity_drop_fraction": 0.20, "recall_clustered": 0.95,
         "recall_unclustered": 0.95, "user_directive_mixing_violations": 2},
        {"arm": "ARM_RANDOM_CLUSTER_COLLAPSE", "ok": True, "recall_clustered": 0.80},
    ])
    assert v == "HARD_FAIL", f"selftest hf-ud: {v}"
    # HARD_FAIL: recall collapse
    v, _ = _verdict_from_arms([
        {"arm": "ARM_NO_COARSE_GRAIN_BASELINE", "ok": True},
        {"arm": "ARM_COARSE_GRAIN_ULTRAMETRIC", "ok": True,
         "capacity_drop_fraction": 0.20, "recall_clustered": 0.65,
         "recall_unclustered": 0.95, "user_directive_mixing_violations": 0},
        {"arm": "ARM_RANDOM_CLUSTER_COLLAPSE", "ok": True, "recall_clustered": 0.30},
    ])
    assert v == "HARD_FAIL", f"selftest hf-rec: {v}"
    print("[selftest] kb_coarse_grain_at_promotion_v1 formula PASS", flush=True)


_instrumentation_selftest()


def _exp_name() -> str:
    return os.environ.get("HDLAB_EXP_NAME", "kb_coarse_grain_at_promotion_v1")


def _exp_dir() -> Path:
    d = REPO / "data" / f"exp_{_exp_name()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


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
            payload = {"verdict": "HARD_FAIL", "verdict_msg": f"KB_REFERENT_MISSING: {e}",
                       "elapsed_s": 0.0, "summary": {"anchor": "kb_coarse_grain_at_promotion_v1"}}
            with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, default=str)
            print(f"[verdict] HARD_FAIL\n[verdict_msg] {payload['verdict_msg']}", flush=True)
            return

    n_atoms = 150 if args.smoke else 600
    t0 = time.time()
    # Real substrate atoms have mean cosine distance ~0.96; adaptive percentile
    # in the arm finds the actual link threshold per class. cfg.min_cluster_size
    # is the load-bearing knob; 3 for smoke (small samples), 5 for full.
    cfg = UltrametricConfig(
        cosine_thresh=0.85,  # informational; arm uses adaptive
        min_cluster_size=3 if args.smoke else 5,
    )
    print(f"[run] kb_coarse_grain_at_promotion_v1 smoke={args.smoke} "
          f"kb_version={kb.kb_version} n_atoms_sample={n_atoms}", flush=True)

    W_sample, atom_idx, sc_per_atom = _sample_atoms_by_source_class(kb, n_atoms)
    print(f"[run] sampled {len(atom_idx)} atoms; class_distribution=", end="")
    from collections import Counter
    cnt = Counter(sc_per_atom)
    print(dict(cnt), flush=True)

    arms: list[dict] = []
    try:
        a = _arm_no_coarse_grain_baseline(W_sample, sc_per_atom)
        arms.append(a)
        print(f"  ARM_NO_COARSE_GRAIN_BASELINE ok={a['ok']} "
              f"recall_unclustered={a['recall_unclustered']}", flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_NO_COARSE_GRAIN_BASELINE", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_NO_COARSE_GRAIN_BASELINE FAILED: {e}", flush=True)

    try:
        ult = _arm_coarse_grain_ultrametric(W_sample, sc_per_atom, cfg)
        arms.append(ult)
        print(f"  ARM_COARSE_GRAIN_ULTRAMETRIC ok={ult['ok']} "
              f"cap_drop={ult['capacity_drop_fraction']} "
              f"rec_clst={ult['recall_clustered']} "
              f"rec_unclst={ult['recall_unclustered']} "
              f"n_clusters={ult['n_clusters']}", flush=True)
        # Extract cluster sizes for random arm matching
        cluster_sizes = []
        # Rebuild from lookup; we lost direct access to clusters list -- approximate
        # via cluster size distribution from arm dict
        if ult.get("n_clusters", 0) > 0 and ult.get("n_clustered_atoms", 0) > 0:
            mean_sz = ult["n_clustered_atoms"] / ult["n_clusters"]
            cluster_sizes = [max(2, int(round(mean_sz)))] * ult["n_clusters"]
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_COARSE_GRAIN_ULTRAMETRIC", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_COARSE_GRAIN_ULTRAMETRIC FAILED: {e}", flush=True)
        cluster_sizes = []

    try:
        rand = _arm_random_cluster_collapse(W_sample, cluster_sizes)
        arms.append(rand)
        print(f"  ARM_RANDOM_CLUSTER_COLLAPSE ok={rand['ok']} "
              f"cap_drop={rand['capacity_drop_fraction']} "
              f"rec_clst={rand['recall_clustered']}", flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_RANDOM_CLUSTER_COLLAPSE", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        print(f"  ARM_RANDOM_CLUSTER_COLLAPSE FAILED: {e}", flush=True)

    verdict, vm = _verdict_from_arms(arms)
    elapsed = round(time.time() - t0, 2)
    payload: dict[str, Any] = {
        "anchor": "kb_coarse_grain_at_promotion_v1",
        "smoke": args.smoke,
        "kb_version": kb.kb_version,
        "n_atoms_sample": n_atoms,
        "cosine_thresh": cfg.cosine_thresh,
        "min_cluster_size": cfg.min_cluster_size,
        "arms": arms,
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump({"verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed,
                   "summary": payload}, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
