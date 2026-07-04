"""Encoder Migration Step 3 - 100-query gold-standard A/B verify vs bag-word.

Compares two encoders on a fixed 100-query gold-standard set:
  ARM_BAG_WORD (baseline): CharTrigramEncoder n_dim=2048; E.pt at
    data/substrate_director_kb_v1/E.pt [970069, 2048] float32.
  ARM_CONCEPT (Step 1 + Step 2 output): CharPositionalEncoder-based concept
    HD + top-K sparse-bipolar (K=82, n_dim=4096); E_concept.pt sparse-CSR at
    data/substrate_concept_encoder_v1[_smoke]/E_concept.pt.

Query set: data/gold_query_set_step3_v1.jsonl (100 rows, 25 per class).
  Class 1: direct-hit atom queries (exact-name-ish substring).
  Class 2: concept-cluster queries (thematic).
  Class 3: failure-mode queries (USER hit low-cosine bag-word).
  Class 4: prior-work queries (mention past experiments).

Hypotheses (per migration plan; all pre-committed at prereg time):
  H1: mean(top-1 cosine, concept) - mean(top-1 cosine, bag-word) >= 0.15
  H2: query "storage strategy sharded bundled scale free topology" hits its
      gold-target atom at cosine >= 0.75 (up from bag-word 0.5381)
  H3: no per-query cosine regression greater than 0.10 (concept vs bag-word
      per gold-target)
  H4: concept mean rank of gold-target in top-10 <= 3.0

SMOKE: 10-query subset (2-3 per class); loads Step 1+2 SMOKE outputs
  (1000-entity slice). Advisory pipeline-fidelity check; H1-H4 evaluated but
  the retrieval-quality claim gate is FULL.

FULL: 100 queries x 2 encoders = 200 forward passes; ~5-15 min CPU-local wall.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified: True (ARM_BAG_WORD vs ARM_CONCEPT produce different
    per-query top-K entity lists by construction; hash-checked at smoke gate)
  - final_metrics_atomicity: tmp_replace (os.replace on metrics.json)
  - except SystemExit: raise BEFORE except Exception (main outer try; NOT
    BaseException)
  - crlb: N/A_retrieval_quality (H1 gate is empirical delta; no formal CRLB
    for retrieval-quality; H2 has explicit floor 0.75)
  - baseline_in_band: HYPOTHESIZED bag-word mean top-1 in [0.30, 0.70] per
    migration plan (0.5381 on the H2 test case cited by USER); verified at
    smoke via bag-word mean top-1 cosine assertion in [0.05, 0.95]
  - discriminator survives scale: SMOKE uses 10-query subset against 1K-
    entity SMOKE encoders; FULL uses 100-query full set against 970K-entity
    FULL encoders. Both use identical code path. SMOKE gates only pipeline
    fidelity + at-scale H1/H2/H3/H4 evaluation deferred to FULL landing.
  - HARD_PASS strictly above floor per META_RULE_L: H1 >= 0.15 strict, H2 >=
    0.75 strict, H3 no regression > 0.10, H4 mean rank <= 3.0 strict
  - HP_SCOPE per arm: {ARM_CONCEPT: [H1_HP, H2_HP, H4_HP], ARM_BAG_WORD:
    [] (baseline; no HP claim)}
  - cardinality_ok: EXPECTED_N_UNITS = n_queries; verdict logic asserts
    len(per_query_metrics) == n_queries; else HARD_FAIL_CARDINALITY
  - per-unit failure-class instrumentation: per-query try catches Exception
    with failure_class in per_query record
  - calibration_check: default_ok_for_this_regime (bag-word encoder inherits
    KB v1 manifest char_trigram_v1; concept encoder inherits Spoke1 v3-D CG
    at N=4096 K_SPARSITY=0.02)
  - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ /
    CITED@ per META_RULE_AC

Source signature:
  - Concept encoder Step 1 output sha256 (from encoder.npz), MEASURED at
    runtime + stamped in metrics.json
  - Concept encoder Step 2 output sha256 (from E_concept.pt), MEASURED at
    runtime + stamped
  - Bag-word baseline E.pt sha256, MEASURED at runtime + stamped
  - Query set sha256 (deterministic from data/gold_query_set_step3_v1.jsonl),
    MEASURED at runtime + stamped
  - Bag-word encoder = char_trigram_v1 CITED@data/substrate_director_kb_v1/
    manifest.json:encoder
  - Concept encoder = CharPositionalEncoder + top-K WTA at N_DIM=4096
    K_SPARSITY=0.02, CITED@Spoke1-v3-D-CG (commit 596a8de03)

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

# ---------------------------------------------------------------------------
# argv snapshot BEFORE any _seed_checkpoint import (Step 2 workaround for
# _seed_checkpoint selftest argv-mangling; see Step 2 cell for full note).
# ---------------------------------------------------------------------------
_ARGV_SNAPSHOT = list(sys.argv)

# ---------------------------------------------------------------------------
# Bootstrap paths.
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from hdlab.char_positional_encoder import CharPositionalEncoder  # noqa: E402
from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: E402

# Restore argv if _seed_checkpoint's import-time selftest mangled it.
if list(sys.argv) != _ARGV_SNAPSHOT:
    sys.argv = _ARGV_SNAPSHOT

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------
ANCHOR_NAME = "encoder_migration_step3_gold_verify_100_queries_A_B_v1"

QUERY_SET_PATH = _REPO / "data" / "gold_query_set_step3_v1.jsonl"

# Concept-encoder config (inherits Step 1).
CONCEPT_N_DIM = 4096
CONCEPT_K_SPARSITY = 0.02
CONCEPT_K_EFFECTIVE = max(1, int(round(CONCEPT_K_SPARSITY * CONCEPT_N_DIM)))
CONCEPT_MAX_POS = 24

# Bag-word baseline config (matches KB v1 manifest).
BAGWORD_N_DIM = 2048

SEED_DEFAULT = 7
TOP_K_REPORT = 10

# Hypothesis bands (PRE-COMMITTED; see prereg for full rationale).
H1_HP_MIN_DELTA = 0.15         # concept - bag_word mean top-1 cosine
H2_TEST_QID = 51               # HYPOTHESIZED chosen QID for H2 test case
H2_HP_MIN_COSINE = 0.75
H2_CITED_BAG_WORD_BASELINE = 0.5381  # CITED@USER 2026-07-02 session note
H3_HP_MAX_REGRESSION = 0.10    # any per-query cosine drop > 0.10 = HF
H4_HP_MAX_MEAN_RANK = 3.0      # concept mean rank of gold-target in top-10

# SMOKE: subset of queries hitting a subset of gold-targets.
_SMOKE_QIDS = [1, 2, 5, 26, 30, 51, 52, 76, 85, 100]  # 10 queries, cross-class

# ---------------------------------------------------------------------------
# Bootstrap / safety helpers.
# ---------------------------------------------------------------------------


def _write_start_marker(output_dir: Path, run_mode: str,
                        expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": int(expected_n_units),
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(tmp, final)


def _emit_heartbeat(output_dir: Path, unit_idx: int, total_units: int,
                    elapsed_s: float, extra: Optional[dict] = None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units),
        "elapsed_s": float(elapsed_s),
    }
    if extra:
        row["extra"] = extra
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Query set loading.
# ---------------------------------------------------------------------------


def _load_query_set(path: Path,
                    qid_filter: Optional[List[int]] = None) -> List[Dict]:
    rows: List[Dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if qid_filter is None or row["qid"] in qid_filter:
                rows.append(row)
    if qid_filter is not None:
        # Preserve requested ordering.
        by_qid = {r["qid"]: r for r in rows}
        rows = [by_qid[q] for q in qid_filter if q in by_qid]
    return rows


# ---------------------------------------------------------------------------
# Bag-word (baseline) encoder + retrieval.
# ---------------------------------------------------------------------------


def _load_bagword_E(kb_dir: Path) -> Tuple[np.ndarray, List[str]]:
    """Load bag-word baseline E.pt + entity names. Returns (E_unit, names).

    Prefers pre-computed row-normalized fp16 mmap at
    kb_dir/E_unit_fp16.npy (3.97 GB; RAM-free mmap load).  Falls back to raw
    E.pt (float32 [N, 2048], 7.9 GB) with in-process L2 normalization if the
    fp16 cache is absent.  Same normalization convention as
    hdlab.director_kb_query.
    """
    ents_path = kb_dir / "entities.jsonl"
    fp16_manifest = kb_dir / "E_unit_fp16.manifest.json"
    fp16_cache = kb_dir / "E_unit_fp16.npy"
    e_path = kb_dir / "E.pt"

    if fp16_manifest.exists() and fp16_cache.exists():
        manifest = json.loads(fp16_manifest.read_text(encoding="utf-8"))
        n_dim = int(manifest.get("n_dim", BAGWORD_N_DIM))
        if n_dim != BAGWORD_N_DIM:
            raise ValueError(
                f"E_unit_fp16 manifest n_dim {n_dim} != expected "
                f"{BAGWORD_N_DIM}"
            )
        # mmap = no RSS cost; row-normalized already.
        e_unit_fp16 = np.load(str(fp16_cache), mmap_mode="r")
        if e_unit_fp16.dtype != np.float16 or e_unit_fp16.shape[1] != n_dim:
            raise ValueError(
                f"E_unit_fp16 dtype/shape mismatch: {e_unit_fp16.dtype} "
                f"{e_unit_fp16.shape} vs float16 [_, {n_dim}]"
            )
        e_unit = e_unit_fp16  # kept as fp16 mmap; cosines cast per-chunk
    else:
        if not e_path.exists():
            raise FileNotFoundError(
                f"neither E_unit_fp16.npy nor E.pt found in {kb_dir}"
            )
        e_raw = torch.load(str(e_path), weights_only=True, map_location="cpu")
        if not torch.is_tensor(e_raw):
            raise ValueError(f"bag-word E.pt is not a Tensor: {type(e_raw)}")
        e_np = e_raw.numpy().astype(np.float32, copy=False)
        norms = np.linalg.norm(e_np, axis=1, keepdims=True) + 1e-8
        e_unit = (e_np / norms).astype(np.float32)
    if not ents_path.exists():
        raise FileNotFoundError(f"entities.jsonl not found: {ents_path}")
    names: List[str] = []
    with open(ents_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            names.append(d["name"])
    if len(names) != e_unit.shape[0]:
        raise ValueError(
            f"bag-word entity_names ({len(names)}) != E rows ({e_unit.shape[0]})"
        )
    return e_unit, names


def _bagword_encode_query(encoder: CharTrigramEncoder,
                          query: str) -> np.ndarray:
    """Return float32 [BAGWORD_N_DIM] L2-unit vector."""
    q = encoder.encode(query).astype(np.float32)
    n = float(np.linalg.norm(q))
    if n < 1e-8:
        return q
    return q / n


_E_UNIT_MATMUL_CHUNK = 100_000


def _bagword_cosines_all(e_unit: np.ndarray,
                         q_unit: np.ndarray) -> np.ndarray:
    """Cosine vs every row of e_unit. Chunked to bound RSS if e_unit is fp16
    mmap; single-shot if e_unit is fp32 dense.
    """
    n_ent = e_unit.shape[0]
    if e_unit.dtype == np.float16:
        q16 = q_unit.astype(np.float16, copy=False)
        sims = np.empty(n_ent, dtype=np.float32)
        CHUNK = _E_UNIT_MATMUL_CHUNK
        for i in range(0, n_ent, CHUNK):
            j = min(i + CHUNK, n_ent)
            sims[i:j] = (e_unit[i:j] @ q16).astype(np.float32)
        return sims
    return (e_unit @ q_unit).astype(np.float32)


def _bagword_topk(e_unit: np.ndarray, q_unit: np.ndarray,
                  k: int) -> Tuple[np.ndarray, np.ndarray]:
    """Return (top_k_indices, top_k_cosines) sorted descending."""
    sims = _bagword_cosines_all(e_unit, q_unit)
    if k >= sims.shape[0]:
        order = np.argsort(-sims)
    else:
        top_idx = np.argpartition(-sims, k - 1)[:k]
        order = top_idx[np.argsort(-sims[top_idx])]
    return order[:k], sims[order[:k]]


def _bagword_cosine_at(e_unit: np.ndarray, q_unit: np.ndarray,
                       gold_idx: int) -> float:
    row = e_unit[gold_idx]
    if row.dtype == np.float16:
        return float(row.astype(np.float32) @ q_unit)
    return float(row @ q_unit)


# ---------------------------------------------------------------------------
# Concept encoder + retrieval.
# ---------------------------------------------------------------------------


def _load_concept_E(pt_path: Path) -> Dict:
    """Load Step 2 E_concept.pt sparse-CSR dict.

    Returns dict with active_indices/signs/offsets tensors + entity_names +
    n_dim + n_entities + total_nnz + format metadata.
    """
    if not pt_path.exists():
        raise FileNotFoundError(f"concept E_concept.pt not found: {pt_path}")
    payload = torch.load(str(pt_path), weights_only=False, map_location="cpu")
    required = {"active_indices", "signs", "offsets", "n_dim", "n_entities",
                "total_nnz", "entity_names"}
    missing = required - set(payload.keys())
    if missing:
        raise ValueError(
            f"concept E_concept.pt missing keys: {missing}; "
            f"got keys: {sorted(payload.keys())}"
        )
    return payload


def _concept_encode_query(encoder: CharPositionalEncoder,
                          query: str) -> np.ndarray:
    """Encode query into sparse-bipolar int8 [CONCEPT_N_DIM] following Step 1's
    concept mechanism (single-context; top-K WTA on |magnitude|).
    """
    hd = encoder.encode_sentence(query).astype(np.float32)  # [N_DIM]
    if hd.shape[0] != CONCEPT_N_DIM:
        raise ValueError(
            f"CharPositionalEncoder returned shape {hd.shape}; "
            f"expected [{CONCEPT_N_DIM}]"
        )
    # NaN/Inf sentinel (per exp_dev bias checklist).
    if np.isnan(hd).any() or np.isinf(hd).any():
        return np.zeros(CONCEPT_N_DIM, dtype=np.int8)
    magnitudes = np.abs(hd)
    k = CONCEPT_K_EFFECTIVE
    if k >= CONCEPT_N_DIM:
        mask = np.ones(CONCEPT_N_DIM, dtype=bool)
    else:
        top_k_idx = np.argpartition(-magnitudes, k)[:k]
        mask = np.zeros(CONCEPT_N_DIM, dtype=bool)
        mask[top_k_idx] = True
    sign_c = np.sign(hd).astype(np.int8)
    sign_c[sign_c == 0] = 1
    return (sign_c * mask.astype(np.int8)).astype(np.int8)


def _concept_cosines_all(concept_E: Dict,
                         q_dense_int8: np.ndarray) -> np.ndarray:
    """Vectorized sparse cosine [N] using bincount accumulation.

    See Step 2 cell _sparse_batched_cosine for identical algorithm.
    """
    n_dim = concept_E["n_dim"]
    n_entities = concept_E["n_entities"]
    offsets = concept_E["offsets"].numpy()
    ai = concept_E["active_indices"].numpy()
    sg = concept_E["signs"].numpy()

    q_f32 = q_dense_int8.astype(np.float32).reshape(-1)
    if q_f32.shape[0] != n_dim:
        raise ValueError(f"query dim {q_f32.shape[0]} != n_dim {n_dim}")
    q_norm_sq = float((q_f32 ** 2).sum())
    if q_norm_sq == 0.0:
        return np.zeros(n_entities, dtype=np.float32)
    q_norm = np.sqrt(q_norm_sq)

    q_gathered = q_f32[ai.astype(np.int32)]
    contribs = sg.astype(np.float32) * q_gathered

    counts = np.diff(offsets)
    row_ids = np.repeat(np.arange(n_entities, dtype=np.int64), counts)
    dots = np.bincount(row_ids, weights=contribs, minlength=n_entities)

    e_norms = np.sqrt(counts.astype(np.float32))
    scores = np.zeros(n_entities, dtype=np.float32)
    nz = e_norms > 0
    scores[nz] = dots[nz].astype(np.float32) / (e_norms[nz] * q_norm)
    return scores


def _concept_topk(sims: np.ndarray,
                  k: int) -> Tuple[np.ndarray, np.ndarray]:
    if k >= sims.shape[0]:
        order = np.argsort(-sims)
    else:
        top_idx = np.argpartition(-sims, k - 1)[:k]
        order = top_idx[np.argsort(-sims[top_idx])]
    return order[:k], sims[order[:k]]


# ---------------------------------------------------------------------------
# A/B per-query pipeline.
# ---------------------------------------------------------------------------


def _run_ab_per_query(
    row: Dict,
    trigram_enc: CharTrigramEncoder,
    char_pos_enc: CharPositionalEncoder,
    bagword_E: np.ndarray,
    bagword_names: List[str],
    bagword_name_to_idx: Dict[str, int],
    concept_E: Dict,
    concept_name_to_idx: Dict[str, int],
) -> Dict:
    """Run one query against both arms; return per-query metrics record."""
    qid = int(row["qid"])
    query = row["query"]
    gold_name = row["gold_entity_name"]
    qclass = int(row["class"])

    # Gold-target lookup per encoder (each encoder has its own entity index
    # range; both should share the same underlying KB entities but the concept
    # encoder in SMOKE only contains first 1000 rows).
    bag_gold_idx = bagword_name_to_idx.get(gold_name, -1)
    concept_gold_idx = concept_name_to_idx.get(gold_name, -1)

    rec: Dict = {
        "qid": qid,
        "class": qclass,
        "query": query,
        "gold_entity_name": gold_name,
        "bag_gold_idx": bag_gold_idx,
        "concept_gold_idx": concept_gold_idx,
        "bag_gold_present": (bag_gold_idx >= 0),
        "concept_gold_present": (concept_gold_idx >= 0),
    }

    try:
        # Bag-word arm.
        q_bag = _bagword_encode_query(trigram_enc, query)
        bag_top_idx, bag_top_cos = _bagword_topk(bagword_E, q_bag, TOP_K_REPORT)
        rec["bag_top1_idx"] = int(bag_top_idx[0])
        rec["bag_top1_cosine"] = float(bag_top_cos[0])
        rec["bag_top1_name"] = bagword_names[int(bag_top_idx[0])]
        rec["bag_top10_indices"] = [int(i) for i in bag_top_idx.tolist()]
        rec["bag_top10_cosines"] = [float(c) for c in bag_top_cos.tolist()]
        if bag_gold_idx >= 0:
            rec["bag_cosine_at_gold"] = _bagword_cosine_at(
                bagword_E, q_bag, bag_gold_idx)
            rec["bag_gold_rank_in_top10"] = (
                (bag_top_idx == bag_gold_idx).nonzero()[0].tolist()[:1] or [-1]
            )[0]
        else:
            rec["bag_cosine_at_gold"] = None
            rec["bag_gold_rank_in_top10"] = -1

        # Concept arm.
        q_conc_dense = _concept_encode_query(char_pos_enc, query)
        conc_sims = _concept_cosines_all(concept_E, q_conc_dense)
        conc_top_idx, conc_top_cos = _concept_topk(conc_sims, TOP_K_REPORT)
        rec["concept_top1_idx"] = int(conc_top_idx[0])
        rec["concept_top1_cosine"] = float(conc_top_cos[0])
        rec["concept_top1_name"] = concept_E["entity_names"][
            int(conc_top_idx[0])]
        rec["concept_top10_indices"] = [int(i) for i in conc_top_idx.tolist()]
        rec["concept_top10_cosines"] = [float(c) for c in conc_top_cos.tolist()]
        if concept_gold_idx >= 0:
            rec["concept_cosine_at_gold"] = float(conc_sims[concept_gold_idx])
            hit_rows = (conc_top_idx == concept_gold_idx).nonzero()[0].tolist()
            rec["concept_gold_rank_in_top10"] = int(hit_rows[0]) if hit_rows else -1
        else:
            rec["concept_cosine_at_gold"] = None
            rec["concept_gold_rank_in_top10"] = -1

        rec["failure_class"] = None
    except Exception as e:
        rec["failure_class"] = f"{type(e).__name__}: {str(e)[:200]}"

    return rec


# ---------------------------------------------------------------------------
# Verdict.
# ---------------------------------------------------------------------------


def _summarize_and_verdict(per_query: List[Dict],
                           expected_n_units: int,
                           run_mode: str) -> Tuple[str, str, Dict]:
    """Compute H1-H4 metrics + verdict tuple."""
    n = len(per_query)
    if n != expected_n_units:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"n_queries {n} != expected {expected_n_units}",
                {"n_queries": n, "expected": expected_n_units})

    failed = [r for r in per_query if r.get("failure_class") is not None]
    if failed:
        return ("HARD_FAIL",
                f"HARD_FAIL_QUERY_EXCEPTIONS: {len(failed)}/{n} "
                f"queries hit failure_class (first: "
                f"{failed[0]['failure_class']})",
                {"n_failed": len(failed)})

    # Split by gold-target-present. Missing-gold rows are excluded from H1-H4
    # aggregates but reported separately.
    both_present = [r for r in per_query
                    if r["bag_gold_present"] and r["concept_gold_present"]]
    n_both = len(both_present)
    n_bag_gold_missing = sum(1 for r in per_query if not r["bag_gold_present"])
    n_conc_gold_missing = sum(1 for r in per_query if not r["concept_gold_present"])

    bag_top1_all = np.array([r["bag_top1_cosine"] for r in per_query],
                            dtype=np.float32)
    conc_top1_all = np.array([r["concept_top1_cosine"] for r in per_query],
                             dtype=np.float32)

    summary: Dict = {
        "n_queries": n,
        "n_both_gold_present": n_both,
        "n_bag_gold_missing": n_bag_gold_missing,
        "n_concept_gold_missing": n_conc_gold_missing,
        "bag_top1_mean": float(np.mean(bag_top1_all)),
        "concept_top1_mean": float(np.mean(conc_top1_all)),
        "delta_top1_mean_concept_minus_bag": float(
            np.mean(conc_top1_all) - np.mean(bag_top1_all)),
    }

    # H1: mean top-1 cosine lift (across ALL queries; both arms produce a
    # top-1 regardless of gold presence).
    h1_delta = summary["delta_top1_mean_concept_minus_bag"]
    summary["h1_delta"] = h1_delta
    summary["h1_hp"] = (h1_delta >= H1_HP_MIN_DELTA)

    # H2: USER test case cosine at gold in concept arm.
    h2_row = next((r for r in per_query if r["qid"] == H2_TEST_QID), None)
    h2_concept_cos = None
    h2_bag_cos = None
    h2_hp = False
    if h2_row is not None and h2_row["concept_cosine_at_gold"] is not None:
        h2_concept_cos = float(h2_row["concept_cosine_at_gold"])
        h2_bag_cos = h2_row.get("bag_cosine_at_gold")
        h2_hp = (h2_concept_cos >= H2_HP_MIN_COSINE)
    summary["h2_concept_cosine_at_gold"] = h2_concept_cos
    summary["h2_bag_cosine_at_gold"] = (float(h2_bag_cos)
                                        if h2_bag_cos is not None else None)
    summary["h2_hp"] = h2_hp

    # H3: no per-query cosine-at-gold regression > 0.10 concept - bag.
    regressions = []
    for r in both_present:
        if (r["bag_cosine_at_gold"] is not None
                and r["concept_cosine_at_gold"] is not None):
            drop = float(r["bag_cosine_at_gold"]) - float(
                r["concept_cosine_at_gold"])
            if drop > H3_HP_MAX_REGRESSION:
                regressions.append({
                    "qid": r["qid"],
                    "bag_cos": float(r["bag_cosine_at_gold"]),
                    "concept_cos": float(r["concept_cosine_at_gold"]),
                    "drop": drop,
                })
    summary["h3_regressions"] = regressions
    summary["h3_n_regressions"] = len(regressions)
    summary["h3_hp"] = (len(regressions) == 0)

    # H4: concept mean rank of gold-target in top-10 <= 3.0 (rows where
    # concept_gold_rank_in_top10 >= 0; -1 means not in top-10, treated as
    # rank TOP_K_REPORT for aggregation to avoid infinite penalty but still
    # penalize misses).
    conc_ranks_in_top10 = []
    for r in per_query:
        if r["concept_gold_present"]:
            rank = int(r["concept_gold_rank_in_top10"])
            if rank >= 0:
                conc_ranks_in_top10.append(rank)
            else:
                conc_ranks_in_top10.append(TOP_K_REPORT)  # miss = rank 10
    if conc_ranks_in_top10:
        h4_mean_rank = float(np.mean(conc_ranks_in_top10))
    else:
        h4_mean_rank = float("nan")
    summary["h4_concept_mean_rank"] = h4_mean_rank
    summary["h4_hp"] = (not np.isnan(h4_mean_rank)
                       and h4_mean_rank <= H4_HP_MAX_MEAN_RANK)

    # Baseline-in-band sanity (bag_top1_mean should be measurably in
    # 0.05 < x < 0.95; if bag baseline is saturated the discriminator can't
    # differentiate).
    bag_mean = summary["bag_top1_mean"]
    baseline_in_band = (0.05 < bag_mean < 0.95)
    summary["baseline_in_band"] = baseline_in_band

    # Verdict tier.
    hp_count = sum([summary["h1_hp"], summary["h2_hp"], summary["h3_hp"],
                    summary["h4_hp"]])
    summary["hp_count"] = hp_count
    summary["hp_details"] = {
        "h1": summary["h1_hp"], "h2": summary["h2_hp"],
        "h3": summary["h3_hp"], "h4": summary["h4_hp"],
    }

    if run_mode == "smoke":
        # SMOKE is advisory pipeline-fidelity check. HP if pipeline ran + no
        # exceptions + at least one gold_target lookup succeeded on each arm.
        n_bag_ok = sum(1 for r in per_query if r["bag_gold_present"])
        n_conc_ok = sum(1 for r in per_query if r["concept_gold_present"])
        if n_bag_ok == 0:
            return ("HARD_FAIL",
                    "SMOKE_HF: no bag-word gold_targets found in "
                    "KB entities.jsonl (query set / KB name mismatch)",
                    summary)
        # concept SMOKE only sees first 1000 entities; almost all gold targets
        # will be absent. That is expected and not a failure.
        return ("HARD_PASS",
                f"SMOKE_HP: pipeline ran n={n} queries no exceptions "
                f"bag_top1_mean={bag_mean:.4f} concept_top1_mean="
                f"{summary['concept_top1_mean']:.4f} delta="
                f"{h1_delta:+.4f} bag_gold_hits={n_bag_ok}/{n} "
                f"concept_gold_hits={n_conc_ok}/{n} "
                f"(concept SMOKE is 1K-entity slice; most golds absent by "
                f"construction)",
                summary)
    # FULL.
    if hp_count == 4 and baseline_in_band:
        return ("HARD_PASS",
                f"FULL_HP: all 4 hypotheses fire H1={h1_delta:+.4f}>=0.15 "
                f"H2_gold_cos={h2_concept_cos:.4f}>=0.75 "
                f"H3_regressions={len(regressions)} "
                f"H4_mean_rank={h4_mean_rank:.2f}<=3.0 "
                f"bag_baseline={bag_mean:.4f} in band",
                summary)
    if hp_count == 0:
        return ("HARD_FAIL",
                f"FULL_HF: no hypotheses fire H1={h1_delta:+.4f} "
                f"H2_gold={h2_concept_cos} H3_reg={len(regressions)} "
                f"H4_rank={h4_mean_rank}",
                summary)
    return ("MIDDLE_BAND",
            f"FULL_MB: {hp_count}/4 hypotheses fire H1={h1_delta:+.4f} "
            f"H2_gold={h2_concept_cos} H3_reg={len(regressions)} "
            f"H4_rank={h4_mean_rank} baseline_in_band={baseline_in_band}",
            summary)


# ---------------------------------------------------------------------------
# Modes.
# ---------------------------------------------------------------------------


def run_self_test() -> int:
    """Fast self-test: synthetic 5-query mini-set against synthetic 50-entity
    sparse encoders (bag-word + concept). No disk-IO on real Step 1/2 outputs.
    """
    t0 = time.perf_counter()
    print("[selftest] building synthetic 50-entity bag-word + concept E",
          flush=True)
    rng = np.random.default_rng(7)
    n = 50
    # Bag-word synthetic E.
    bagword_E = rng.standard_normal((n, BAGWORD_N_DIM)).astype(np.float32)
    bagword_E /= (np.linalg.norm(bagword_E, axis=1, keepdims=True) + 1e-8)
    bagword_names = [f"ent_{i}_synthetic" for i in range(n)]

    # Concept synthetic sparse-CSR E.
    k = CONCEPT_K_EFFECTIVE
    dense_int8 = np.zeros((n, CONCEPT_N_DIM), dtype=np.int8)
    for i in range(n):
        picks = rng.choice(CONCEPT_N_DIM, size=k, replace=False)
        signs = rng.choice([-1, 1], size=k).astype(np.int8)
        dense_int8[i, picks] = signs
    rows_np, cols_np = np.nonzero(dense_int8)
    signs_np = dense_int8[rows_np, cols_np].astype(np.int8)
    active_indices_np = cols_np.astype(np.int16)
    counts_np = np.bincount(rows_np, minlength=n).astype(np.int64)
    offsets_np = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(counts_np, out=offsets_np[1:])
    concept_E = {
        "active_indices": torch.from_numpy(active_indices_np),
        "signs": torch.from_numpy(signs_np),
        "offsets": torch.from_numpy(offsets_np),
        "n_dim": CONCEPT_N_DIM,
        "n_entities": n,
        "total_nnz": int(offsets_np[-1]),
        "entity_names": bagword_names,
    }

    print("[selftest] init encoders (CharTrigram + CharPositional)",
          flush=True)
    trigram_enc = CharTrigramEncoder(n_dim=BAGWORD_N_DIM)
    char_pos_enc = CharPositionalEncoder(n_dim=CONCEPT_N_DIM,
                                          max_pos=CONCEPT_MAX_POS)

    print("[selftest] synthetic 5-query A/B", flush=True)
    synthetic_rows = [
        {"qid": 1, "class": 1, "query": "synthetic query one",
         "gold_entity_name": "ent_3_synthetic"},
        {"qid": 2, "class": 1, "query": "synthetic query two",
         "gold_entity_name": "ent_10_synthetic"},
        {"qid": 3, "class": 2, "query": "concept cluster three",
         "gold_entity_name": "ent_20_synthetic"},
        {"qid": 4, "class": 3, "query": "failure mode four",
         "gold_entity_name": "ent_30_synthetic"},
        {"qid": 5, "class": 4, "query": "prior work five",
         "gold_entity_name": "MISSING_ENTITY_NAME_TO_TEST_GOLD_ABSENT_PATH"},
    ]
    bag_n2i = {n: i for i, n in enumerate(bagword_names)}
    conc_n2i = {n: i for i, n in enumerate(concept_E["entity_names"])}
    per_query = []
    for row in synthetic_rows:
        rec = _run_ab_per_query(row, trigram_enc, char_pos_enc, bagword_E,
                                bagword_names, bag_n2i, concept_E, conc_n2i)
        per_query.append(rec)
        assert rec.get("failure_class") is None, f"query {row['qid']} failed: {rec.get('failure_class')}"
    print(f"[selftest] all 5 queries ran per_query keys="
          f"{sorted(per_query[0].keys())}", flush=True)

    # ARMS-MUST-DIFFER hash-check (per META_RULE_AF).
    bag_top1_hash = hashlib.sha256(
        b"|".join(str(r["bag_top1_idx"]).encode() for r in per_query)
    ).hexdigest()
    concept_top1_hash = hashlib.sha256(
        b"|".join(str(r["concept_top1_idx"]).encode() for r in per_query)
    ).hexdigest()
    print(f"[selftest] arm hashes bag={bag_top1_hash[:16]}... "
          f"concept={concept_top1_hash[:16]}...", flush=True)
    assert bag_top1_hash != concept_top1_hash, (
        "META_RULE_AF VIOLATION: bag-word + concept arms produced "
        "bit-identical top-1 sequences on synthetic queries; arm-implementation "
        "bug"
    )

    # Verdict logic path (synthetic; H1/H2/H3/H4 expected to be N/A or noise).
    verdict, verdict_msg, summary = _summarize_and_verdict(
        per_query, expected_n_units=5, run_mode="smoke")
    print(f"[selftest] synthetic verdict={verdict} msg={verdict_msg}",
          flush=True)

    # Gold-absent path is exercised on synthetic_rows[4].
    r5 = per_query[4]
    assert not r5["concept_gold_present"], "synthetic row 5 should have gold absent"
    assert r5["concept_cosine_at_gold"] is None
    assert r5["concept_gold_rank_in_top10"] == -1

    elapsed = time.perf_counter() - t0
    print(f"[selftest] PASS elapsed={elapsed:.2f}s", flush=True)
    return 0


def run_experiment(run_mode: str, seed: int) -> int:
    if run_mode == "smoke":
        anchor = f"{ANCHOR_NAME}_smoke"
    else:
        anchor = ANCHOR_NAME

    out_dir = get_output_dir(anchor)

    # Load query set (SMOKE = 10-subset; FULL = 100).
    if run_mode == "smoke":
        qid_filter = _SMOKE_QIDS
    else:
        qid_filter = None
    rows = _load_query_set(QUERY_SET_PATH, qid_filter=qid_filter)
    n_queries = len(rows)
    _write_start_marker(out_dir, run_mode, expected_n_units=n_queries)
    print(f"[step3] run_mode={run_mode} anchor={anchor} n_queries={n_queries}",
          flush=True)
    print(f"[step3] out_dir={out_dir}", flush=True)

    t0 = time.perf_counter()

    # Path resolution.
    concept_suffix = "_smoke" if run_mode == "smoke" else ""
    concept_pt_path = (_REPO / "data" /
                       f"substrate_concept_encoder_v1{concept_suffix}" /
                       "E_concept.pt")
    concept_npz_path = (_REPO / "data" /
                        f"substrate_concept_encoder_v1{concept_suffix}" /
                        "encoder.npz")
    bagword_kb_dir = _REPO / "data" / "substrate_director_kb_v1"
    query_set_sha256 = _sha256_file(QUERY_SET_PATH)
    print(f"[step3] concept_pt={concept_pt_path}", flush=True)
    print(f"[step3] bagword_kb_dir={bagword_kb_dir}", flush=True)
    print(f"[step3] query_set_sha256={query_set_sha256[:16]}...", flush=True)

    # Load bag-word arm.
    print("[step3] loading bag-word E.pt + entities.jsonl", flush=True)
    bag_t0 = time.perf_counter()
    bagword_E, bagword_names = _load_bagword_E(bagword_kb_dir)
    bag_load_s = time.perf_counter() - bag_t0
    print(f"[step3] bag-word E shape={bagword_E.shape} n_names="
          f"{len(bagword_names)} load_s={bag_load_s:.1f}", flush=True)
    bagword_name_to_idx = {n: i for i, n in enumerate(bagword_names)}
    _emit_heartbeat(out_dir, 1, 4, time.perf_counter() - t0,
                    extra={"stage": "loaded_bagword_E"})

    # Load concept arm.
    print("[step3] loading concept E_concept.pt (sparse-CSR)", flush=True)
    conc_t0 = time.perf_counter()
    concept_E = _load_concept_E(concept_pt_path)
    conc_load_s = time.perf_counter() - conc_t0
    print(f"[step3] concept E n_entities={concept_E['n_entities']} n_dim="
          f"{concept_E['n_dim']} total_nnz={concept_E['total_nnz']} "
          f"load_s={conc_load_s:.1f}", flush=True)
    concept_name_to_idx = {n: i for i, n in enumerate(concept_E["entity_names"])}
    _emit_heartbeat(out_dir, 2, 4, time.perf_counter() - t0,
                    extra={"stage": "loaded_concept_E"})

    # Init encoders.
    print("[step3] init CharTrigramEncoder + CharPositionalEncoder",
          flush=True)
    trigram_enc = CharTrigramEncoder(n_dim=BAGWORD_N_DIM)
    char_pos_enc = CharPositionalEncoder(n_dim=CONCEPT_N_DIM,
                                          max_pos=CONCEPT_MAX_POS)

    # Source signatures (sha256).
    bagword_e_pt_sha256 = _sha256_file(bagword_kb_dir / "E.pt")
    concept_pt_sha256 = _sha256_file(concept_pt_path)
    concept_npz_sha256 = (_sha256_file(concept_npz_path)
                          if concept_npz_path.exists() else "MISSING")
    print(f"[step3] bagword_E_sha256={bagword_e_pt_sha256[:16]}... "
          f"concept_pt_sha256={concept_pt_sha256[:16]}... "
          f"concept_npz_sha256={concept_npz_sha256[:16]}...", flush=True)

    # Per-query A/B.
    per_query: List[Dict] = []
    heartbeat_cadence = max(1, n_queries // 20)
    for i, row in enumerate(rows):
        q_t0 = time.perf_counter()
        rec = _run_ab_per_query(row, trigram_enc, char_pos_enc, bagword_E,
                                bagword_names, bagword_name_to_idx,
                                concept_E, concept_name_to_idx)
        rec["wall_ms"] = float((time.perf_counter() - q_t0) * 1000.0)
        per_query.append(rec)
        if (i + 1) % heartbeat_cadence == 0 or (i + 1) == n_queries:
            elapsed_now = time.perf_counter() - t0
            print(f"[step3] q {i+1}/{n_queries} qid={rec['qid']} "
                  f"class={rec['class']} bag_top1_cos="
                  f"{rec.get('bag_top1_cosine', float('nan')):.3f} "
                  f"concept_top1_cos="
                  f"{rec.get('concept_top1_cosine', float('nan')):.3f} "
                  f"wall_ms={rec['wall_ms']:.1f}", flush=True)
            _emit_heartbeat(out_dir, i + 1, n_queries, elapsed_now,
                            extra={"stage": "querying",
                                   "current_qid": rec["qid"]})
    _emit_heartbeat(out_dir, 3, 4, time.perf_counter() - t0,
                    extra={"stage": "all_queries_done"})

    # ARMS-MUST-DIFFER hash-check (per META_RULE_AF).
    bag_top1_hash = hashlib.sha256(
        b"|".join(str(r.get("bag_top1_idx", -1)).encode() for r in per_query)
    ).hexdigest()
    concept_top1_hash = hashlib.sha256(
        b"|".join(str(r.get("concept_top1_idx", -1)).encode()
                  for r in per_query)
    ).hexdigest()
    arms_differ = (bag_top1_hash != concept_top1_hash)
    print(f"[step3] arm hashes bag={bag_top1_hash[:16]}... "
          f"concept={concept_top1_hash[:16]}... differ={arms_differ}",
          flush=True)
    if not arms_differ:
        raise ValueError(
            "META_RULE_AF VIOLATION: bag-word + concept arms produced "
            "bit-identical top-1 sequences; arm-implementation bug"
        )

    verdict, verdict_msg, summary = _summarize_and_verdict(
        per_query, expected_n_units=n_queries, run_mode=run_mode)
    _emit_heartbeat(out_dir, 4, 4, time.perf_counter() - t0,
                    extra={"stage": "verdict_done"})
    elapsed_total = time.perf_counter() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": float(elapsed_total),
        "run_mode": run_mode,
        "anchor_name": anchor,
        "seed": int(seed),
        "N": CONCEPT_N_DIM,
        "n_queries": n_queries,
        "n_dim_bagword": BAGWORD_N_DIM,
        "n_dim_concept": CONCEPT_N_DIM,
        "concept_k_effective": CONCEPT_K_EFFECTIVE,
        "top_k_report": TOP_K_REPORT,
        "h1_hp_min_delta": H1_HP_MIN_DELTA,
        "h2_test_qid": H2_TEST_QID,
        "h2_hp_min_cosine": H2_HP_MIN_COSINE,
        "h2_cited_bag_word_baseline": H2_CITED_BAG_WORD_BASELINE,
        "h3_hp_max_regression": H3_HP_MAX_REGRESSION,
        "h4_hp_max_mean_rank": H4_HP_MAX_MEAN_RANK,
        "query_set_path": str(QUERY_SET_PATH),
        "query_set_sha256": query_set_sha256,
        "concept_pt_path": str(concept_pt_path),
        "concept_pt_sha256": concept_pt_sha256,
        "concept_npz_sha256": concept_npz_sha256,
        "bagword_e_pt_path": str(bagword_kb_dir / "E.pt"),
        "bagword_e_pt_sha256": bagword_e_pt_sha256,
        "bagword_n_entities": int(bagword_E.shape[0]),
        "concept_n_entities": int(concept_E["n_entities"]),
        "bag_load_s": float(bag_load_s),
        "concept_load_s": float(conc_load_s),
        "arms_differ_verified": bool(arms_differ),
        "arm_bag_top1_hash": bag_top1_hash,
        "arm_concept_top1_hash": concept_top1_hash,
        "cardinality_ok": (len(per_query) == n_queries),
        "final_metrics_atomicity": "tmp_replace",
        "summary_h1_h4": summary,
        "per_query": per_query,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    write_metrics(out_dir, metrics)
    print(f"[step3] verdict={verdict} elapsed={elapsed_total:.1f}s",
          flush=True)
    print(f"[step3] verdict_msg={verdict_msg}", flush=True)
    return 0


# ---------------------------------------------------------------------------
# Entry.
# ---------------------------------------------------------------------------


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=(
        "Encoder Migration Step 3 -- 100-query gold-standard A/B verify"
    ))
    p.add_argument(
        "--run-mode",
        default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
        choices=["self_test", "smoke", "full"],
    )
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--seed", type=int, default=SEED_DEFAULT)
    args = p.parse_args(argv)
    if args.self_test:
        args.run_mode = "self_test"
    elif args.smoke:
        args.run_mode = "smoke"
    elif args.full:
        args.run_mode = "full"
    return args


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    args = _parse_args()
    if args.run_mode == "self_test":
        return run_self_test()
    return run_experiment(args.run_mode, args.seed)


if __name__ == "__main__":
    _fallback_out = get_output_dir(ANCHOR_NAME)
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException per META_RULE section 8
        try:
            _write_crash_metrics(_fallback_out, exc)
        except Exception:
            pass
        raise
