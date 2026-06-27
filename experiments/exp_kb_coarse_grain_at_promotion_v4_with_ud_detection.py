"""KB COARSE-GRAIN AT PROMOTION v4 (ANCHOR 3 RESCUE; UD DETECTION + EXTERNAL DIR;
2026-06-27).

Pre-reg: preregs/2026-06-27_kb_coarse_grain_at_promotion_v4_with_ud_detection.md

v3 SELF_CONTAINED HARD_FAILed: RC-1 invariant n_UD=0 < 10 halted the run because
the repo's `memory/` directory was empty (USER directives actually live in
`~/.claude/projects/d--AI/memory/`). RC-1 fired correctly in protective
direction; the failure was path-scope, not mechanism.

v4 fix (Skunkworks recommendation b + a):
  (a) External-dir FALLBACK: try `~/.claude/projects/d--AI/memory/` as an
      additional source class file root if the in-repo `memory/` is empty.
      Windows-portable: `Path.home() / '.claude' / 'projects' / 'd--AI' / 'memory'`.
  (b) Content-based UD DETECTION: post-ingest pass marks chunk atoms whose
      original source file content contains markers ("USER:", "USER directive",
      "USER-locked", "USER 2026-") as source_class='user_directive' regardless
      of original source class. Preserves self-contained principle and catches
      USER directives embedded in notes/ + preregs/ even if the external memory/
      dir is unreachable on the remote runner.

MECHANISM IS UNCHANGED FROM v3 chain-grade-path:
  - RC-1: USER_DIRECTIVE n_UD >= 10 forced into sample.
  - RC-2: n_atoms >= 10000 cap-break.
  - discriminator-must-survive-scale full-N preview at smoke.

KEY ADAPTATION: v4 sampler accepts EITHER `chunk_memory` (from in-repo or
external-dir ingest) OR `user_directive` (from post-ingest content detection
re-labeling). The USER_DIRECTIVE mixing invariant treats both tokens as the
UD class.

ARMS (identical to v3):
  ARM_NO_COARSE_GRAIN_BASELINE   - sanity rail
  ARM_COARSE_GRAIN_ULTRAMETRIC   - chain-grade mechanism
  ARM_RANDOM_CLUSTER_COLLAPSE    - control
  ARM_FULL_N_PREVIEW             - smoke-only (n=10000, 1 seed, ULTRA only)

HARD_PASS bar (chain-grade; identical to v3):
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

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hdlab.director_kb import load_schema  # noqa: E402
from hdlab.director_kb_chunk_ingest import (  # noqa: E402
    build_chunk_plan,
    run_chunk_ingest,
)
from hdlab.director_kb_query import DirectorKBQuery  # noqa: E402
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


# ---------- v4 thresholds (identical to v3 chain-grade-path) ----------
HP_MIN_CAPACITY_DROP = 0.20
HP_MIN_GAP_VS_RANDOM = 0.30
HP_MAX_CV = 0.05
HP_MAX_REC_UNCLUSTERED_NONSAT = 0.999
HP_MIN_N_UD_IN_SAMPLE = 10
HP_MIN_N_ATOMS_FULL = 10000

MB_MIN_GAP_VS_RANDOM = 0.15
MB_MAX_CV = 0.10
HF_MIN_CAPACITY_DROP = 0.10

SEEDS_FULL = (17, 23, 31)
SEEDS_SMOKE = (17,)

SMOKE_PREVIEW_N_ATOMS = 10000

# v4 ingest envelope (self-contained build budget; identical to v3)
SELF_CONTAINED_CHUNK_CLASSES = ("note", "memory", "prereg")
SELF_CONTAINED_MAX_FILES_FULL = 200
SELF_CONTAINED_MAX_FILES_SMOKE = 50
INGEST_N_DIM = 2048
INGEST_SEED = 17

# v4 USER_DIRECTIVE class tokens (BOTH accepted as UD):
#   - "chunk_memory": chunk-ingest prefixed token over memory/ source class
#   - "user_directive": content-based detection re-label (NEW v4)
UD_SOURCE_CLASS_FROM_MEMORY = "chunk_memory"
UD_SOURCE_CLASS_FROM_CONTENT = "user_directive"

# v4: external memory directory fallback (USER directives live here per
# substrate-Director-KB scope; ~/.claude/projects/d--AI/memory/)
EXTERNAL_MEMORY_DIR_DEFAULT = (
    Path(os.path.expanduser("~")) / ".claude" / "projects" / "d--AI" / "memory"
)

# v4 UD content-detection markers (case-sensitive substring match).
# Conservative regex set to avoid mass-relabeling: requires explicit USER token.
UD_CONTENT_MARKERS = [
    "USER:",
    "USER directive",
    "USER-locked",
    "USER LOCKED",
    "USER 2026-",
    "USER 2025-",
]


# Ingest cardinality minimums
EXPECTED_INGEST_ENTITIES_MIN_SMOKE = 100
EXPECTED_INGEST_ENTITIES_MIN_FULL = 500


def _audit_event(event: dict) -> None:
    line = json.dumps(event, default=str, ensure_ascii=False) + "\n"
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line)


def _is_ud_class(c: str) -> bool:
    """v4 UD-class predicate: accept either memory-ingested OR content-detected."""
    return c in (UD_SOURCE_CLASS_FROM_MEMORY, UD_SOURCE_CLASS_FROM_CONTENT)


def _detect_ud_in_text(text: str) -> bool:
    """Conservative content-based USER_DIRECTIVE detection."""
    if not text:
        return False
    for marker in UD_CONTENT_MARKERS:
        if marker in text:
            return True
    return False


def _enumerate_files_in_dir(root: Path, glob_pat: str = "*.md",
                              limit: int | None = None) -> list[Path]:
    """Enumerate files in a directory matching glob; deterministic-order."""
    if not root.exists() or not root.is_dir():
        return []
    files = sorted(root.glob(glob_pat))
    if limit is not None:
        files = files[:limit]
    return files


def _post_ingest_ud_relabel(
    inline_kb_dir: Path,
    external_memory_dir: Path | None,
) -> tuple[int, int, dict]:
    """v4 post-ingest pass: re-label atoms as 'user_directive' based on content
    detection in the original source files.

    Mutates atoms.jsonl in place. Returns (n_atoms_relabeled,
    n_files_with_ud_content, debug_dict).

    Detection strategy:
      1. Walk each unique source_path in atoms.jsonl
      2. For each, read original file from REPO root (chunk_ingest's source
         was REPO-relative)
      3. If file content contains any UD marker, re-label all atoms with that
         source_path as source_class='user_directive'
      4. If file unreadable (e.g., notes/ but source from external memory),
         fall back to scanning the atom's o_name for CHUNK_CONTENT atoms.
    """
    atoms_path = inline_kb_dir / "atoms.jsonl"
    if not atoms_path.exists():
        return (0, 0, {"reason": "atoms_jsonl_missing"})

    # Pass 1: collect unique source_paths + sample one CHUNK_CONTENT body per
    # source_path for fallback detection
    atoms = []
    with atoms_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            atoms.append(json.loads(line))

    source_paths_to_text: dict[str, str] = {}
    for a in atoms:
        sp = a.get("source_path")
        if not sp:
            continue
        # Prefer CHUNK_CONTENT atoms for fallback body text (carries o_name = content_tag)
        if a.get("p_name") == "CHUNK_CONTENT" and sp not in source_paths_to_text:
            source_paths_to_text[sp] = a.get("o_name", "")
        elif sp not in source_paths_to_text:
            source_paths_to_text[sp] = ""

    # Pass 2: try to read each source_path from REPO + external dir for full
    # content; fall back to chunk content tag if file unreadable
    ud_source_paths: set[str] = set()
    for sp, fallback_text in source_paths_to_text.items():
        full_text = None
        # Try REPO-relative
        repo_path = REPO / sp
        if repo_path.exists() and repo_path.is_file():
            try:
                full_text = repo_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                full_text = None
        # Try external memory dir (rel basename match) if REPO read failed
        if full_text is None and external_memory_dir is not None:
            ext_path = external_memory_dir / Path(sp).name
            if ext_path.exists() and ext_path.is_file():
                try:
                    full_text = ext_path.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    full_text = None
        text_to_scan = full_text if full_text is not None else fallback_text
        if _detect_ud_in_text(text_to_scan):
            ud_source_paths.add(sp)

    # Pass 3: re-label atoms whose source_path is in ud_source_paths
    n_relabeled = 0
    for a in atoms:
        if a.get("source_path") in ud_source_paths:
            old_cls = a.get("source_class")
            if old_cls != UD_SOURCE_CLASS_FROM_CONTENT:
                a["source_class"] = UD_SOURCE_CLASS_FROM_CONTENT
                a["_ud_relabel_from"] = old_cls
                n_relabeled += 1

    # Write back atoms.jsonl
    with atoms_path.open("w", encoding="utf-8", newline="\n") as f:
        for a in atoms:
            f.write(json.dumps(a, sort_keys=True) + "\n")

    return (n_relabeled, len(ud_source_paths), {
        "n_atoms_total": len(atoms),
        "n_unique_source_paths": len(source_paths_to_text),
        "n_ud_source_paths": len(ud_source_paths),
        "n_atoms_relabeled": n_relabeled,
        "sample_ud_source_paths": sorted(ud_source_paths)[:10],
    })


def _sample_atoms_with_forced_ud(
    kb: DirectorKBQuery,
    n_atoms: int,
    seed: int,
    min_ud: int = HP_MIN_N_UD_IN_SAMPLE,
) -> tuple[np.ndarray, list[int], list[str], int]:
    """Sample atoms biased toward classes with abundant atoms; force at least
    `min_ud` UD atoms (either chunk_memory OR user_directive) into the sample.

    Returns (W_sample, atom_indices, source_classes_per_atom, n_ud_in_sample).
    """
    rng = np.random.RandomState(seed)
    n_ent = len(kb.entity_names)

    # Per-entity primary source_class (prefer UD class if present)
    ent_sc: list[str] = []
    for i in range(n_ent):
        sc_set = kb._source_classes_by_ent.get(i, set())
        if sc_set:
            # v4 priority: user_directive (content-detected) > chunk_memory > other
            if UD_SOURCE_CLASS_FROM_CONTENT in sc_set:
                ent_sc.append(UD_SOURCE_CLASS_FROM_CONTENT)
            elif UD_SOURCE_CLASS_FROM_MEMORY in sc_set:
                ent_sc.append(UD_SOURCE_CLASS_FROM_MEMORY)
            else:
                ent_sc.append(sorted(sc_set)[0])
        else:
            ent_sc.append("unknown")

    # Force-include UD atoms FIRST (load-bearing for v3/v4)
    ud_cand = [i for i, c in enumerate(ent_sc) if _is_ud_class(c)]
    if not ud_cand:
        raise RuntimeError(
            f"USER_DIRECTIVE_REFERENT_MISSING: zero UD-class atoms "
            f"(chunk_memory or user_directive) in inline KB (n_ent={n_ent}); "
            f"cannot satisfy v4 cardinality_ok bar (n_UD >= {min_ud}). Check "
            f"chunk_ingest over memory/ + post-ingest UD detection over content."
        )
    ud_arr = np.array(ud_cand)
    rng.shuffle(ud_arr)
    n_ud_target = max(min_ud, min(len(ud_cand), n_atoms // 20))
    n_ud_actual = min(n_ud_target, len(ud_cand))
    forced_ud_idx = ud_arr[:n_ud_actual].tolist()

    # Stratified sample for the rest: top-5 non-UD classes
    from collections import Counter

    sc_counts = Counter(ent_sc)
    top_classes = [c for c, _ in sc_counts.most_common(7)
                   if not _is_ud_class(c)][:5]
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
    n_ud_in_sample = sum(1 for c in sc_per_atom if _is_ud_class(c))
    return W_sample, selected_idx, sc_per_atom, n_ud_in_sample


def _arm_no_coarse_grain_baseline(W: np.ndarray, sc_per_atom: list[str]) -> dict:
    t0 = time.perf_counter()
    n = W.shape[0]
    elapsed = time.perf_counter() - t0
    return {
        "arm": "ARM_NO_COARSE_GRAIN_BASELINE",
        "ok": True,
        "n_atoms": n,
        "n_user_directive_atoms": sum(1 for c in sc_per_atom
                                       if _is_ud_class(c)),
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

    v4 adaptation: UD invariant checks BOTH chunk_memory AND user_directive
    tokens via _is_ud_class predicate.
    """
    t0 = time.perf_counter()
    n = W.shape[0]
    n_user_directive_atoms = sum(1 for c in sc_per_atom if _is_ud_class(c))

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
            # USER_DIRECTIVE mixing invariant (load-bearing; v4: both UD tokens)
            if len(atoms_classes) > 1:
                user_directive_mixing_violations += 1
            ud_in_cluster = any(_is_ud_class(c) for c in atoms_classes)
            non_ud_in_cluster = any(not _is_ud_class(c) for c in atoms_classes)
            if ud_in_cluster and non_ud_in_cluster:
                user_directive_mixing_violations += 1
            all_qualifying_clusters.append(global_cluster)
            if audit_events_emitted < audit_first_n:
                _audit_event({
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "kind": "coarse_grain_event_v4",
                    "seed": seed,
                    "cluster_size": len(global_cluster),
                    "source_class": cls,
                    "cluster_atoms_sample": global_cluster[:8],
                    "is_user_directive_cluster": _is_ud_class(cls),
                })
                audit_events_emitted += 1

    W_col, _reps, lookup = collapse_W_via_clusters(W, all_qualifying_clusters, cfg)
    eff_cap = effective_capacity_used(lookup)
    capacity_drop = (n - eff_cap) / n if n > 0 else 0.0

    clustered_atoms = [a for a in range(n) if lookup[a] >= 0]
    unclustered_atoms = [a for a in range(n) if lookup[a] < 0]

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
    """Chain-grade verdict aggregator; identical to v3 (UD predicate widened
    at sampling layer, not here)."""
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
            f"(RC-1 invariant: test would be vacuously satisfied like v1/v3)"
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

    saturated = all(ru >= HP_MAX_REC_UNCLUSTERED_NONSAT for ru in rec_unclst)
    if saturated:
        return "HARD_FAIL", (
            f"saturation_at_n={n_atoms_full}: rec_unclst all >= "
            f"{HP_MAX_REC_UNCLUSTERED_NONSAT} (per-seed={rec_unclst}); "
            f"metric cap not broken; RC-2 unsuccessful"
        )

    if mean_cap_drop < HF_MIN_CAPACITY_DROP:
        return "HARD_FAIL", (
            f"cap_drop_mean={mean_cap_drop:.3f} < HF floor {HF_MIN_CAPACITY_DROP}"
        )

    if mean_gap <= 0.05:
        return "HARD_FAIL", (
            f"gap_mean={mean_gap:.3f} <= 0.05 (mechanism null vs random control)"
        )

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
            f"cv_rec_clst={cv_rec_clst:.3f}; one or more HP thresholds not met"
        )
    return "HARD_FAIL", (
        f"cap_drop_mean={mean_cap_drop:.3f}, gap_mean={mean_gap:.3f}, "
        f"cv_rec_clst={cv_rec_clst:.3f}; below MB floor"
    )


def _instrumentation_selftest() -> None:
    """Formula self-tests (v3 verbatim shape; UD predicate covers both tokens)."""
    # T1: UD-class predicate
    assert _is_ud_class("chunk_memory")
    assert _is_ud_class("user_directive")
    assert not _is_ud_class("chunk_note")
    assert not _is_ud_class("chunk_prereg")
    assert not _is_ud_class("")

    # T2: UD content detection
    assert _detect_ud_in_text("Some prefix... USER: pause new experiments")
    assert _detect_ud_in_text("USER directive: NO LOCAL until further notice")
    assert _detect_ud_in_text("USER 2026-06-27: directive text here")
    assert _detect_ud_in_text("USER-locked 13th rule active state check")
    assert not _detect_ud_in_text("ordinary note content without markers")
    assert not _detect_ud_in_text("")
    assert not _detect_ud_in_text("uppercase USER in middle without colon")

    # T3: verdict formula
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
    v, _msg = _verdict_from_seeds(hp_seed_results, n_ud_in_sample=15,
                                   n_atoms_full=10000, n_seeds=3)
    assert v == "HARD_PASS", f"selftest HP: {v} :: {_msg}"

    bad_ud = [dict(r) for r in hp_seed_results]
    bad_ud[0] = {"seed": 17, "ultra": {"user_directive_mixing_violations": 2,
                                        "capacity_drop_fraction": 0.25,
                                        "recall_clustered": 0.90,
                                        "recall_unclustered": 0.85},
                  "random": {"recall_clustered": 0.50}}
    v, _ = _verdict_from_seeds(bad_ud, n_ud_in_sample=15, n_atoms_full=10000, n_seeds=3)
    assert v == "HARD_FAIL", f"selftest HF-UD: {v}"

    v, _ = _verdict_from_seeds(hp_seed_results, n_ud_in_sample=0,
                                n_atoms_full=10000, n_seeds=3)
    assert v == "HARD_FAIL", f"selftest HF-nUD0: {v}"

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
    v, _ = _verdict_from_seeds(null_gap, n_ud_in_sample=15,
                                n_atoms_full=10000, n_seeds=3)
    assert v == "HARD_FAIL", f"selftest HF-nullgap: {v}"

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

    print("[selftest] kb_coarse_grain_at_promotion_v4_with_ud_detection formula PASS",
          flush=True)


_instrumentation_selftest()


def _exp_name() -> str:
    return os.environ.get(
        "HDLAB_EXP_NAME", "kb_coarse_grain_at_promotion_v4_with_ud_detection"
    )


def _exp_dir() -> Path:
    d = REPO / "data" / f"exp_{_exp_name()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _build_inline_kb(
    out_dir: Path,
    smoke: bool,
    external_memory_dir: Path | None,
) -> dict:
    """Build the self-contained chunk-KB from notes/ + memory/ + preregs/.

    v4 additions:
      - If repo `memory/` is empty AND external_memory_dir is provided +
        non-empty, the plan's `memory` class root is FALLBACK-redirected to
        external_memory_dir (Skunkworks recommendation a).
      - After base ingest, runs post-ingest UD content-detection re-label
        pass over notes/+preregs/+memory/ atoms (Skunkworks recommendation b).

    Returns the manifest dict (now with v4_external_memory_dir +
    v4_ud_relabel_stats fields added).
    """
    schema = load_schema(REPO)
    max_files = (SELF_CONTAINED_MAX_FILES_SMOKE if smoke
                 else SELF_CONTAINED_MAX_FILES_FULL)
    plan = build_chunk_plan(
        schema=schema,
        repo_root=REPO,
        chunk_classes=SELF_CONTAINED_CHUNK_CLASSES,
        max_files_per_class=max_files,
    )

    # v4 fallback: if repo memory/ class is empty/unreachable, splice in
    # external memory dir's files under the memory class
    mem_plan = plan.get("memory", {})
    mem_files = mem_plan.get("files", []) or []
    used_external = False
    external_files: list[Path] = []
    if (not mem_files) and external_memory_dir is not None:
        external_files = _enumerate_files_in_dir(
            external_memory_dir, glob_pat="*.md", limit=max_files,
        )
        if external_files:
            plan["memory"] = {
                "root": external_memory_dir,
                "files": external_files,
                "skipped_unreachable": False,
                "_v4_external_dir_fallback": True,
            }
            used_external = True
            print(f"[v4-fallback] in-repo memory/ empty; using external "
                  f"{external_memory_dir} n_files={len(external_files)}",
                  flush=True)

    n_disc = sum(len(plan[c]["files"]) for c in plan)
    t0 = time.perf_counter()
    manifest = run_chunk_ingest(
        plan=plan,
        out_dir=out_dir,
        schema=schema,
        n_dim=INGEST_N_DIM,
        seed=INGEST_SEED,
        wipe=True,
        redact_timestamps_in_atoms=False,
    )
    elapsed = time.perf_counter() - t0

    # v4 post-ingest pass: content-based UD relabel over all source files
    t1 = time.perf_counter()
    n_relabeled, n_ud_paths, ud_dbg = _post_ingest_ud_relabel(
        inline_kb_dir=out_dir,
        external_memory_dir=external_memory_dir,
    )
    ud_elapsed = time.perf_counter() - t1

    manifest["_build_elapsed_s"] = round(elapsed, 3)
    manifest["_n_files_discovered"] = n_disc
    manifest["_smoke"] = bool(smoke)
    manifest["_v4_external_memory_used"] = used_external
    manifest["_v4_external_memory_dir"] = str(external_memory_dir) if external_memory_dir else None
    manifest["_v4_external_memory_files"] = len(external_files)
    manifest["_v4_ud_relabel_stats"] = ud_dbg
    manifest["_v4_ud_relabel_elapsed_s"] = round(ud_elapsed, 3)
    manifest["_v4_n_atoms_relabeled_to_user_directive"] = n_relabeled
    return manifest


def _run_one_seed(
    W_sample: np.ndarray,
    sc_per_atom: list[str],
    cfg: UltrametricConfig,
    seed: int,
) -> dict:
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
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--inline-kb-dir", default=None,
                   help="Override inline KB build dir.")
    p.add_argument("--external-memory-dir", default=None,
                   help="Override external memory dir fallback. "
                        f"Default: {EXTERNAL_MEMORY_DIR_DEFAULT}")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    out_dir = _exp_dir()
    inline_kb_dir = (Path(args.inline_kb_dir) if args.inline_kb_dir
                     else out_dir / "_inline_kb")
    external_memory_dir = (Path(args.external_memory_dir)
                            if args.external_memory_dir
                            else EXTERNAL_MEMORY_DIR_DEFAULT)

    t0 = time.time()

    # Phase 1: build inline KB (with v4 external-dir fallback + UD relabel)
    try:
        print(f"[ingest] building inline KB at {inline_kb_dir} "
              f"smoke={args.smoke} classes={SELF_CONTAINED_CHUNK_CLASSES} "
              f"max_files="
              f"{SELF_CONTAINED_MAX_FILES_SMOKE if args.smoke else SELF_CONTAINED_MAX_FILES_FULL} "
              f"external_memory_fallback={external_memory_dir}",
              flush=True)
        manifest = _build_inline_kb(
            inline_kb_dir, smoke=args.smoke,
            external_memory_dir=external_memory_dir,
        )
        n_ent = manifest.get("n_entities", 0)
        min_ent = (EXPECTED_INGEST_ENTITIES_MIN_SMOKE if args.smoke
                   else EXPECTED_INGEST_ENTITIES_MIN_FULL)
        print(f"[ingest] done: n_entities={n_ent} "
              f"n_chunks={manifest.get('n_chunks')} "
              f"n_triples={manifest.get('n_triples')} "
              f"coverage={manifest.get('coverage_ratio')} "
              f"v4_external_used={manifest.get('_v4_external_memory_used')} "
              f"v4_n_relabeled={manifest.get('_v4_n_atoms_relabeled_to_user_directive')} "
              f"elapsed_s={manifest.get('_build_elapsed_s')}", flush=True)
        if n_ent < min_ent:
            payload = {
                "verdict": "HARD_FAIL",
                "verdict_msg": (
                    f"INGEST_TOO_SMALL: n_entities={n_ent} < min {min_ent} "
                    f"(smoke={args.smoke}); inline KB did not populate; "
                    f"check notes/ memory/ preregs/ on this runner + "
                    f"external_memory_dir={external_memory_dir}"
                ),
                "elapsed_s": round(time.time() - t0, 2),
                "summary": {"anchor": _exp_name(),
                            "inline_kb_manifest": manifest,
                            "cardinality_ok": False},
            }
            with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, default=str)
            print(f"\n[verdict] HARD_FAIL\n[verdict_msg] {payload['verdict_msg']}",
                  flush=True)
            return
    except Exception as e:  # noqa: BLE001
        payload = {
            "verdict": "HARD_FAIL",
            "verdict_msg": f"INGEST_EXCEPTION: {type(e).__name__}: {e}",
            "elapsed_s": round(time.time() - t0, 2),
            "summary": {"anchor": _exp_name(), "cardinality_ok": False},
        }
        with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        print(f"\n[verdict] HARD_FAIL\n[verdict_msg] {payload['verdict_msg']}",
              flush=True)
        return

    # Phase 2: load query over inline KB
    try:
        kb = DirectorKBQuery(kb_dir=inline_kb_dir)
    except Exception as e:  # noqa: BLE001
        payload = {
            "verdict": "HARD_FAIL",
            "verdict_msg": (
                f"KB_LOAD_EXCEPTION: {type(e).__name__}: {e}; "
                f"inline_kb_dir={inline_kb_dir}"
            ),
            "elapsed_s": round(time.time() - t0, 2),
            "summary": {"anchor": _exp_name(),
                        "inline_kb_manifest": manifest,
                        "cardinality_ok": False},
        }
        with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        print(f"\n[verdict] HARD_FAIL\n[verdict_msg] {payload['verdict_msg']}",
              flush=True)
        return

    n_total_inline = len(kb.entity_names)
    if args.smoke:
        n_atoms = min(600, n_total_inline)
    else:
        n_atoms = min(HP_MIN_N_ATOMS_FULL, n_total_inline)
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    cfg = UltrametricConfig(
        cosine_thresh=0.85,
        min_cluster_size=3 if args.smoke else 5,
    )

    print(
        f"[run] {_exp_name()} smoke={args.smoke} "
        f"kb_version={kb.kb_version} n_inline={n_total_inline} "
        f"n_atoms={n_atoms} seeds={seeds}",
        flush=True,
    )

    # Phase 3: per-seed arms (D3 no-silent-except)
    seed_results: list[dict] = []
    n_ud_in_sample_per_seed: list[int] = []
    for seed in seeds:
        try:
            W_sample, atom_idx, sc_per_atom, n_ud_in_sample = (
                _sample_atoms_with_forced_ud(kb, n_atoms, seed)
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
                f"rec_clst={u['recall_clustered']} "
                f"rec_unclst={u['recall_unclustered']} "
                f"n_clusters={u['n_clusters']} "
                f"ud_mix_viol={u['user_directive_mixing_violations']}",
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

    # Phase 4: smoke-only full-N preview
    full_n_preview = None
    if args.smoke:
        preview_n = min(SMOKE_PREVIEW_N_ATOMS, n_total_inline)
        try:
            print(
                f"[smoke-preview] running ARM_FULL_N_PREVIEW at n={preview_n} "
                f"(capped at inline n={n_total_inline})",
                flush=True,
            )
            W_prev, _prev_idx, sc_prev, n_ud_prev = (
                _sample_atoms_with_forced_ud(kb, preview_n, seed=seeds[0])
            )
            prev_cfg = UltrametricConfig(cosine_thresh=0.85, min_cluster_size=5)
            prev_ultra, _ = _arm_coarse_grain_ultrametric(
                W_prev, sc_prev, prev_cfg, seed=seeds[0]
            )
            full_n_preview = {
                "n_atoms": preview_n,
                "n_ud_in_sample": n_ud_prev,
                "recall_clustered": prev_ultra["recall_clustered"],
                "recall_unclustered": prev_ultra["recall_unclustered"],
                "capacity_drop_fraction": prev_ultra["capacity_drop_fraction"],
                "n_clusters": prev_ultra["n_clusters"],
                "elapsed_s": prev_ultra["elapsed_s"],
                "saturation_risk_flag": bool(
                    prev_ultra["recall_unclustered"] >= HP_MAX_REC_UNCLUSTERED_NONSAT
                ),
                "preview_capped_below_target": bool(
                    preview_n < SMOKE_PREVIEW_N_ATOMS
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

    n_ud_for_verdict = (min(n_ud_in_sample_per_seed)
                        if n_ud_in_sample_per_seed else 0)
    n_atoms_for_verdict = (
        full_n_preview["n_atoms"]
        if args.smoke and full_n_preview
        and "recall_unclustered" in full_n_preview
        else n_atoms
    )

    if args.smoke and full_n_preview and "recall_unclustered" in full_n_preview:
        if full_n_preview["recall_unclustered"] >= HP_MAX_REC_UNCLUSTERED_NONSAT:
            verdict = "HARD_FAIL"
            vm = (
                f"SMOKE_PREVIEW_SATURATED: rec_unclst="
                f"{full_n_preview['recall_unclustered']} >= "
                f"{HP_MAX_REC_UNCLUSTERED_NONSAT} at n={full_n_preview['n_atoms']}; "
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
                f"{HP_MAX_REC_UNCLUSTERED_NONSAT}); "
                f"n_UD={n_ud_for_verdict}; safe to dispatch full"
            )
    else:
        verdict, vm = _verdict_from_seeds(
            seed_results, n_ud_for_verdict, n_atoms_for_verdict, len(seeds)
        )

    elapsed = round(time.time() - t0, 2)

    cardinality_ok = bool(
        n_ud_for_verdict >= HP_MIN_N_UD_IN_SAMPLE
        and (
            (args.smoke and full_n_preview
             and "recall_unclustered" in full_n_preview)
            or (not args.smoke
                and n_atoms >= HP_MIN_N_ATOMS_FULL
                and len(seeds) >= 3)
        )
    )

    payload: dict[str, Any] = {
        "anchor": _exp_name(),
        "smoke": args.smoke,
        "kb_version": kb.kb_version,
        "inline_kb_manifest": manifest,
        "inline_kb_dir": str(inline_kb_dir),
        "external_memory_dir": str(external_memory_dir),
        "n_inline_entities": n_total_inline,
        "n_atoms_per_seed": n_atoms,
        "seeds": list(seeds),
        "cosine_thresh": cfg.cosine_thresh,
        "min_cluster_size": cfg.min_cluster_size,
        "ud_source_class_from_memory": UD_SOURCE_CLASS_FROM_MEMORY,
        "ud_source_class_from_content": UD_SOURCE_CLASS_FROM_CONTENT,
        "ud_content_markers": UD_CONTENT_MARKERS,
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
        "chunk_classes_ingested": list(SELF_CONTAINED_CHUNK_CLASSES),
    }
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "verdict": verdict,
                "verdict_msg": vm,
                "elapsed_s": elapsed,
                "summary": payload,
            },
            f, indent=2, default=str,
        )
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
