"""substrate_concept_encoder_v2_A_ppmi_svd_sparse_2026_07_03

Tests hdlab.ppmi_sparse_encoder.PPMISparseEncoder (PPMI/SVD-then-threshold
sparse encoder; substrate-native forward-only closed-form) on
SUBSTRATE-INGESTED SYMBOLIC CONTENT (WordNet 3.0 lexicon partition from
data/substrate_index/concept/atoms.jsonl).

Per ML/AI drill 5x-5/5 rec 2026-07-02: this is PARALLEL rescue path #2
against v1 concept_encoder HF (v1 recall@5=0.160 < char_trigram=0.28 on
this task). ML/AI drill said LOCAL COMPETITIVE/HEBBIAN LEARNING was the
wrong signal; accumulated co-occurrence statistics (PPMI/SVD or Random
Indexing) should work.

Same task + regime as prior baseline cell (substrate_concept_encoder_
substrate_content_v1) for apples-to-apples comparison.

FRAMING (LOAD-BEARING per USER 2026-07-02):
  Tests PPMI/SVD mechanism on substrate's KNOWN SYMBOLIC KNOWLEDGE
  (WordNet definitions+synonyms); NOT unsupervised discovery from raw
  corpora; NOT natural narrative text; NOT "substrate understands English".
  HP earned here does NOT grant "substrate knows things"; grants "PPMI/SVD
  mechanism works on substrate's known symbolic content at this regime".

Arms (5, mirror + extend v1 baseline):
  1. ARM_V2A_PPMI_SVD (LOAD-BEARING; PPMI/SVD sparse encoder)
  2. ARM_V1_CONCEPT_ENCODER (competitive-Hebbian; recall@5=0.160
     MEASURED@data/exp_substrate_concept_encoder_substrate_content_v1_
     2026_07_02/metrics.json:aggregate.arm_concept_encoder_recall_at_5_mean)
  3. ARM_CHAR_TRIGRAM_UNSUP_REFERENCE (bag-word baseline; recall@5=0.280
     MEASURED@same:aggregate.arm_char_trigram_recall_at_5_mean; TARGET to beat)
  4. ARM_RANDOM_INDEXING (Sahlgren bonus arm; accumulated co-occurrence)
  5. ARM_RANDOM_BASELINE (chance floor; recall@5=~0.05 THEORETICAL@k/N)

HP bands (see prereg preregs/2026-07-03_substrate_concept_encoder_v2_A_
ppmi_svd_sparse.md); HP_SCOPE LOAD-BEARING on ARM_V2A_PPMI_SVD:
  HP1: ARM_V2A_PPMI_SVD recall@5 > ARM_V1_CONCEPT_ENCODER recall@5 + 0.10
       (meaningful lift over failed v1 competitive-Hebbian).
  HP2: ARM_V2A_PPMI_SVD recall@5 >= ARM_CHAR_TRIGRAM_UNSUP_REFERENCE + 0.05
       (v2-A architecture beats trivial bag baseline).
  HP3: ARM_V1_CONCEPT_ENCODER recall@5 within +/-0.03 of prior baseline
       0.16 (positive control; reproduces prior HF measurement).
  HP4: ARM_RANDOM_BASELINE recall@5 <= 0.10 (chance floor sanity).
  HP5: arms_differ_verified (5 arm prototype tables hash-distinct;
       exempted pair: RANDOM_BASELINE proto vs any other -- proto IS random
       so hash-differ tautologically holds; we still verify).
  HF1: ARM_V2A_PPMI_SVD < ARM_V1_CONCEPT_ENCODER (mechanism worse than
       failed baseline; PPMI signal is WORSE than competitive-Hebbian
       on this content).
  HF2: ARM_V2A_PPMI_SVD < ARM_CHAR_TRIGRAM_UNSUP_REFERENCE (v2-A still
       loses to bag; MAJOR REFRAME).
  MIDDLE_BAND: v2-A lifts v1 but ties or marginally below bag
       (HP1 pass, HP2 marginal).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (META_RULE_AF; 5-way hash-test)
  - final_metrics_atomicity: tmp_replace via os.replace
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: no quantitative CRLB (supervised retrieval; chance floor k/N)
  - baseline_in_band at smoke (META_RULE_AG; 0.05 < baseline < 0.80)
  - discriminator: ARM_V2A_PPMI_SVD - ARM_CHAR_TRIGRAM at smoke
  - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
  - HP_SCOPE: HP1/HP2 only on ARM_V2A_PPMI_SVD; HP3 only on ARM_V1_CONCEPT
  - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Compute arch: sequential CPU numpy (Compute architecture: (b) sequential-CPU;
per-atom SVD training + numpy matmul; wall < 10min at smoke). Storage
strategy: sharded per-atom prototype HDs. Composition depth L=1 (encoder
eval, not chain). Progress logging: print_flush_true.

Prior-work check (substrate-KB concept-query 2026-07-03): Wave14 series
2026-05-24 (exp_wave14_sparse_coding_ppmi_v1, exp_wave14b_m2_ppmi,
exp_wave14d_sparse_vs_ppmi) used PPMI on byte-bigram co-occurrence for VSA
DICTIONARY ATOM generation (bpc / bigram prediction); DIFFERENT REGIME
from WordNet held-out synonym retrieval. Novel synthesis for this task at
top substrate-KB match cosine=0.39 (Mutual information).

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
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Bootstrap.
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from hdlab.concept_encoder import ConceptEncoder  # noqa: E402
from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: E402
from hdlab.ppmi_sparse_encoder import (  # noqa: E402
    PPMISparseEncoder,
    RandomIndexingEncoder,
)
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402,F401
from experiments._cell_heartbeat import CellHeartbeat  # noqa: E402

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------

ANCHOR_NAME = "substrate_concept_encoder_v2_A_ppmi_svd_sparse_2026_07_03"

CORPUS_ATOMS_JSONL = _REPO / "data" / "substrate_index" / "concept" / "atoms.jsonl"

SMOKE_N_ATOMS = 100
SMOKE_SEEDS = [11, 17, 23]
FULL_N_ATOMS = 500
FULL_SEEDS = [11, 17, 23]

N_DIM = 2048

# PPMI hyperparameters (v2-A CG defaults).
PPMI_K_SPARSITY = 0.02
PPMI_MIN_TERM_FREQ = 2
PPMI_SMOOTHING = 0.75
# Random Indexing.
RI_K_SIGNS = 8

# concept_encoder CG defaults (mirror v1 baseline exactly).
CE_K_SPARSITY = 0.02
CE_MAX_POS = 24

# HP band constants.
HP1_V2A_MINUS_V1_GAP = 0.10  # HYPOTHESIZED per drill rec
HP2_V2A_MINUS_TRIGRAM_GAP = 0.05
HP3_V1_RECOVERY_TOL = 0.03
HP3_V1_TARGET_R5 = 0.16  # MEASURED@prior_baseline
HP4_RANDOM_CEILING = 0.10  # THEORETICAL@chance_floor 5/N=0.05
CHAR_TRIGRAM_PRIOR = 0.28  # MEASURED@prior_baseline
BASELINE_IN_BAND_LO = 0.05
BASELINE_IN_BAND_HI = 0.80

# Required min-atom quality (mirror v1).
MIN_DEFINITION_LEN = 20
MIN_SYNONYMS = 3


# ---------------------------------------------------------------------------
# Crash-diagnostic helpers (per exp_dev.md §13.C).
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": _now_iso(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "anchor_name": ANCHOR_NAME,
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": _now_iso(),
        "pid": os.getpid(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Corpus loading (mirror v1 baseline for apples-to-apples).
# ---------------------------------------------------------------------------

def _clean_name(raw_name: str) -> str:
    n = raw_name
    if n.startswith("WN_"):
        n = n[3:]
    parts = n.split(".")
    if len(parts) >= 3 and len(parts[-1]) <= 3 and parts[-1].isdigit():
        n = ".".join(parts[:-2])
    return n.replace("_", " ")


def _load_wordnet_atoms(max_atoms: int, seed: int) -> List[Dict[str, Any]]:
    if not CORPUS_ATOMS_JSONL.exists():
        raise FileNotFoundError(f"substrate concept atoms not found: {CORPUS_ATOMS_JSONL}")
    candidates: List[Dict[str, Any]] = []
    with CORPUS_ATOMS_JSONL.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("kind") != "lexicon":
                continue
            meta = d.get("metadata") or {}
            pos = meta.get("pos")
            if pos not in ("n", "v", "a", "r"):
                continue
            desc = d.get("description") or ""
            if len(desc) < MIN_DEFINITION_LEN:
                continue
            syns = meta.get("synonyms") or []
            if len(syns) < MIN_SYNONYMS:
                continue
            freq = meta.get("lemma_freq_semcor")
            if freq is None or int(freq) < 1:
                continue
            hyp = meta.get("hypernyms") or []
            hyp0 = hyp[0] if hyp else ""
            raw_name = d.get("name") or d.get("id")
            candidates.append({
                "atom_id": d.get("id"),
                "name_clean": _clean_name(str(raw_name)),
                "description": desc,
                "synonyms": [str(s) for s in syns],
                "hypernym0": _clean_name(hyp0) if hyp0 else "",
                "freq": int(freq),
            })
    if not candidates:
        raise RuntimeError("no WordNet lexicon atoms passed the filter")
    candidates.sort(key=lambda x: (-int(x["freq"]), str(x["atom_id"])))
    del seed
    return candidates[:max_atoms]


def _build_train_query(
    atoms: Sequence[Dict[str, Any]],
) -> Tuple[List[str], List[int], List[Tuple[int, str]]]:
    training_sentences: List[str] = []
    training_labels: List[int] = []
    queries: List[Tuple[int, str]] = []
    for i, a in enumerate(atoms):
        syns: List[str] = list(a["synonyms"])
        desc: str = str(a["description"])
        hyp: str = str(a["hypernym0"] or "")
        if len(syns) >= 4:
            q = syns[-1]
            train_syns = syns[:2]
        elif len(syns) == 3:
            q = syns[2]
            train_syns = syns[:2]
        else:
            q = syns[-1]
            train_syns = syns[:-1]
        atom_sents: List[str] = [desc]
        atom_sents.extend(train_syns)
        if hyp:
            atom_sents.append(f"related to {hyp}")
        for s in atom_sents:
            training_sentences.append(str(s))
            training_labels.append(i)
        queries.append((i, str(q)))
    return training_sentences, training_labels, queries


# ---------------------------------------------------------------------------
# Arm helpers.
# ---------------------------------------------------------------------------

def _cosine_argmax_topk(query_hd: np.ndarray, prototypes: np.ndarray, k: int) -> np.ndarray:
    q = query_hd.astype(np.float32)
    p = prototypes.astype(np.float32)
    q_norm = float(np.linalg.norm(q))
    if q_norm < 1e-12:
        return np.arange(min(k, p.shape[0]), dtype=np.int64)
    p_norms = np.linalg.norm(p, axis=1)
    p_norms_safe = np.where(p_norms < 1e-12, 1.0, p_norms)
    scores = (p @ q) / (p_norms_safe * q_norm)
    scores = np.where(p_norms < 1e-12, -1e9, scores)
    if k >= scores.shape[0]:
        order = np.argsort(-scores)
    else:
        idx_part = np.argpartition(-scores, k)[:k]
        order = idx_part[np.argsort(-scores[idx_part])]
    return order.astype(np.int64)


def _hash_prototype_table(arr: np.ndarray) -> str:
    return hashlib.sha256(arr.tobytes()).hexdigest()


def _build_prototypes_bundled(
    encode_fn,
    training_sentences: Sequence[str],
    training_labels: Sequence[int],
    n_atoms: int,
    n_dim: int,
) -> np.ndarray:
    """Mean-bundle prototype builder for any encode_fn(str) -> [n_dim] float."""
    acc = np.zeros((n_atoms, n_dim), dtype=np.float32)
    counts = np.zeros(n_atoms, dtype=np.float32)
    for s, lbl in zip(training_sentences, training_labels):
        hd = encode_fn(str(s)).astype(np.float32)
        acc[int(lbl)] += hd
        counts[int(lbl)] += 1.0
    denom = np.where(counts > 0, counts, 1.0)
    return (acc / denom[:, None]).astype(np.float32)


def _build_prototypes_concept_encoder(
    training_sentences: Sequence[str],
    training_labels: Sequence[int],
    n_atoms: int,
    n_dim: int,
    seed: int,
) -> Tuple[np.ndarray, ConceptEncoder]:
    enc = ConceptEncoder(
        n_dim=n_dim,
        n_concepts=n_atoms,
        k_sparsity=CE_K_SPARSITY,
        seed=seed,
        max_pos=CE_MAX_POS,
        concept_names=None,
        mask_target_word=False,
    )
    labels_arr = np.asarray(list(training_labels), dtype=np.int64)
    enc.fit(list(training_sentences), labels_arr)
    return enc.concept_hds.astype(np.int8), enc


def _build_prototypes_random(
    n_atoms: int, n_dim: int, seed: int
) -> np.ndarray:
    """Random bipolar prototypes; queries also random. Chance-floor control."""
    rng = np.random.default_rng(seed + 999983)
    return (rng.integers(0, 2, size=(n_atoms, n_dim)) * 2 - 1).astype(np.int8)


def _query_arm_concept_encoder(
    enc: ConceptEncoder,
    queries: Sequence[Tuple[int, str]],
    k_values: Sequence[int],
) -> Dict[str, Any]:
    concept_hds = enc.concept_hds.astype(np.float32)
    correct_at_k = {int(k): 0 for k in k_values}
    n = len(queries)
    for atom_idx, q_word in queries:
        surf = enc._surface_encoder.encode_sentence(str(q_word))  # noqa: SLF001
        topk_max = max(k_values)
        order = _cosine_argmax_topk(surf, concept_hds, int(topk_max))
        for k in k_values:
            if int(atom_idx) in order[: int(k)].tolist():
                correct_at_k[int(k)] += 1
    return {f"recall_at_{k}": correct_at_k[int(k)] / max(1, n) for k in k_values}


def _query_arm_bundled(
    prototypes: np.ndarray,
    queries: Sequence[Tuple[int, str]],
    k_values: Sequence[int],
    encode_fn,
) -> Dict[str, Any]:
    correct_at_k = {int(k): 0 for k in k_values}
    n = len(queries)
    for atom_idx, q_word in queries:
        hd = encode_fn(str(q_word)).astype(np.float32)
        topk_max = max(k_values)
        order = _cosine_argmax_topk(hd, prototypes, int(topk_max))
        for k in k_values:
            if int(atom_idx) in order[: int(k)].tolist():
                correct_at_k[int(k)] += 1
    return {f"recall_at_{k}": correct_at_k[int(k)] / max(1, n) for k in k_values}


def _query_arm_random(
    prototypes: np.ndarray,
    queries: Sequence[Tuple[int, str]],
    k_values: Sequence[int],
    seed: int,
) -> Dict[str, Any]:
    """Random-baseline: for each query, generate a fresh random HD."""
    rng = np.random.default_rng(seed + 424242)
    correct_at_k = {int(k): 0 for k in k_values}
    n = len(queries)
    n_dim = prototypes.shape[1]
    for atom_idx, _q_word in queries:
        hd = (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)
        topk_max = max(k_values)
        order = _cosine_argmax_topk(hd, prototypes, int(topk_max))
        for k in k_values:
            if int(atom_idx) in order[: int(k)].tolist():
                correct_at_k[int(k)] += 1
    return {f"recall_at_{k}": correct_at_k[int(k)] / max(1, n) for k in k_values}


# ---------------------------------------------------------------------------
# One-seed evaluation.
# ---------------------------------------------------------------------------

def _eval_one_seed(
    seed: int,
    atoms: Sequence[Dict[str, Any]],
    n_dim: int,
    hb: CellHeartbeat,
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    n_atoms = len(atoms)
    training_sentences, training_labels, queries = _build_train_query(atoms)
    print(
        f"[seed={seed}] n_atoms={n_atoms} n_train_sent={len(training_sentences)} "
        f"n_queries={len(queries)}",
        flush=True,
    )
    hb.tick(unit_idx=1, extra={"phase": "corpus_built", "seed": seed}, force=True)

    k_values = [1, 5, 10]

    # ARM 1: V2A_PPMI_SVD.
    t_arm = time.perf_counter()
    ppmi_enc = PPMISparseEncoder(
        n_dim=n_dim,
        k_sparsity=PPMI_K_SPARSITY,
        min_term_freq=PPMI_MIN_TERM_FREQ,
        smoothing=PPMI_SMOOTHING,
        seed=seed,
    )
    ppmi_enc.fit(list(training_sentences), np.asarray(training_labels, dtype=np.int64))
    ppmi_prototypes = _build_prototypes_bundled(
        ppmi_enc.encode, training_sentences, training_labels, n_atoms, n_dim
    )
    ppmi_hash = _hash_prototype_table(ppmi_prototypes)
    arm1_metrics = _query_arm_bundled(ppmi_prototypes, queries, k_values, ppmi_enc.encode)
    arm1_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_V2A_PPMI_SVD] recall@1={arm1_metrics['recall_at_1']:.4f} "
        f"recall@5={arm1_metrics['recall_at_5']:.4f} "
        f"recall@10={arm1_metrics['recall_at_10']:.4f} "
        f"effective_dim={ppmi_enc.effective_n_dim} V={len(ppmi_enc.term_to_idx)} "
        f"wall={arm1_wall:.1f}s",
        flush=True,
    )
    hb.tick(
        unit_idx=2,
        extra={"phase": "arm_v2a_ppmi_done", "seed": seed,
               "recall_at_5": arm1_metrics["recall_at_5"]},
        force=True,
    )

    # ARM 2: V1_CONCEPT_ENCODER.
    t_arm = time.perf_counter()
    ce_hds, ce_enc = _build_prototypes_concept_encoder(
        training_sentences, training_labels, n_atoms, n_dim, seed
    )
    ce_hash = _hash_prototype_table(ce_hds)
    arm2_metrics = _query_arm_concept_encoder(ce_enc, queries, k_values)
    arm2_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_V1_CONCEPT_ENCODER] recall@1={arm2_metrics['recall_at_1']:.4f} "
        f"recall@5={arm2_metrics['recall_at_5']:.4f} "
        f"recall@10={arm2_metrics['recall_at_10']:.4f} wall={arm2_wall:.1f}s",
        flush=True,
    )
    hb.tick(
        unit_idx=3,
        extra={"phase": "arm_v1_concept_done", "seed": seed,
               "recall_at_5": arm2_metrics["recall_at_5"]},
        force=True,
    )

    # ARM 3: CHAR_TRIGRAM_UNSUP_REFERENCE.
    t_arm = time.perf_counter()
    ct_enc = CharTrigramEncoder(n_dim=n_dim, pad_char=" ")
    ct_prototypes = _build_prototypes_bundled(
        lambda s: ct_enc.encode(s).astype(np.float32),
        training_sentences, training_labels, n_atoms, n_dim,
    )
    ct_hash = _hash_prototype_table(ct_prototypes)
    arm3_metrics = _query_arm_bundled(
        ct_prototypes, queries, k_values, lambda s: ct_enc.encode(s).astype(np.float32)
    )
    arm3_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_CHAR_TRIGRAM_UNSUP_REFERENCE] "
        f"recall@1={arm3_metrics['recall_at_1']:.4f} "
        f"recall@5={arm3_metrics['recall_at_5']:.4f} "
        f"recall@10={arm3_metrics['recall_at_10']:.4f} wall={arm3_wall:.1f}s",
        flush=True,
    )
    hb.tick(
        unit_idx=4,
        extra={"phase": "arm_char_trigram_done", "seed": seed,
               "recall_at_5": arm3_metrics["recall_at_5"]},
        force=True,
    )

    # ARM 4: RANDOM_INDEXING.
    t_arm = time.perf_counter()
    ri_enc = RandomIndexingEncoder(n_dim=n_dim, k_signs=RI_K_SIGNS)
    ri_prototypes = _build_prototypes_bundled(
        ri_enc.encode, training_sentences, training_labels, n_atoms, n_dim
    )
    ri_hash = _hash_prototype_table(ri_prototypes)
    arm4_metrics = _query_arm_bundled(ri_prototypes, queries, k_values, ri_enc.encode)
    arm4_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_RANDOM_INDEXING] recall@1={arm4_metrics['recall_at_1']:.4f} "
        f"recall@5={arm4_metrics['recall_at_5']:.4f} "
        f"recall@10={arm4_metrics['recall_at_10']:.4f} wall={arm4_wall:.1f}s",
        flush=True,
    )
    hb.tick(
        unit_idx=5,
        extra={"phase": "arm_random_indexing_done", "seed": seed,
               "recall_at_5": arm4_metrics["recall_at_5"]},
        force=True,
    )

    # ARM 5: RANDOM_BASELINE.
    t_arm = time.perf_counter()
    rb_prototypes = _build_prototypes_random(n_atoms, n_dim, seed)
    rb_hash = _hash_prototype_table(rb_prototypes)
    arm5_metrics = _query_arm_random(rb_prototypes, queries, k_values, seed)
    arm5_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_RANDOM_BASELINE] recall@1={arm5_metrics['recall_at_1']:.4f} "
        f"recall@5={arm5_metrics['recall_at_5']:.4f} "
        f"recall@10={arm5_metrics['recall_at_10']:.4f} wall={arm5_wall:.1f}s",
        flush=True,
    )
    hb.tick(
        unit_idx=6,
        extra={"phase": "arm_random_baseline_done", "seed": seed,
               "recall_at_5": arm5_metrics["recall_at_5"]},
        force=True,
    )

    # Arms-differ hash check (5-way).
    hashes = {
        "ARM_V2A_PPMI_SVD": ppmi_hash,
        "ARM_V1_CONCEPT_ENCODER": ce_hash,
        "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE": ct_hash,
        "ARM_RANDOM_INDEXING": ri_hash,
        "ARM_RANDOM_BASELINE": rb_hash,
    }
    unique_hashes = set(hashes.values())
    arms_differ_verified = len(unique_hashes) == 5

    return {
        "seed": int(seed),
        "n_atoms": int(n_atoms),
        "n_dim": int(n_dim),
        "n_train_sentences": int(len(training_sentences)),
        "n_queries": int(len(queries)),
        "arm_v2a_ppmi_svd": arm1_metrics,
        "arm_v1_concept_encoder": arm2_metrics,
        "arm_char_trigram_unsup_reference": arm3_metrics,
        "arm_random_indexing": arm4_metrics,
        "arm_random_baseline": arm5_metrics,
        "ppmi_effective_dim": int(ppmi_enc.effective_n_dim),
        "ppmi_vocab_size": int(len(ppmi_enc.term_to_idx)),
        "arm_walls_s": {
            "v2a_ppmi_svd": round(arm1_wall, 3),
            "v1_concept_encoder": round(arm2_wall, 3),
            "char_trigram_unsup_reference": round(arm3_wall, 3),
            "random_indexing": round(arm4_wall, 3),
            "random_baseline": round(arm5_wall, 3),
        },
        "arms_differ_verified": bool(arms_differ_verified),
        "arm_hashes": hashes,
        "wall_s": round(time.perf_counter() - t0, 3),
    }


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def _aggregate_per_seed(per_seed: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    def _mean(vals: List[float]) -> float:
        return float(np.mean(vals)) if vals else 0.0

    def _arm(name: str, k: int) -> float:
        return _mean([float(s[name][f"recall_at_{k}"]) for s in per_seed])

    return {
        "arm_v2a_ppmi_svd_recall_at_1_mean": _arm("arm_v2a_ppmi_svd", 1),
        "arm_v2a_ppmi_svd_recall_at_5_mean": _arm("arm_v2a_ppmi_svd", 5),
        "arm_v2a_ppmi_svd_recall_at_10_mean": _arm("arm_v2a_ppmi_svd", 10),
        "arm_v1_concept_encoder_recall_at_1_mean": _arm("arm_v1_concept_encoder", 1),
        "arm_v1_concept_encoder_recall_at_5_mean": _arm("arm_v1_concept_encoder", 5),
        "arm_v1_concept_encoder_recall_at_10_mean": _arm("arm_v1_concept_encoder", 10),
        "arm_char_trigram_recall_at_1_mean": _arm("arm_char_trigram_unsup_reference", 1),
        "arm_char_trigram_recall_at_5_mean": _arm("arm_char_trigram_unsup_reference", 5),
        "arm_char_trigram_recall_at_10_mean": _arm("arm_char_trigram_unsup_reference", 10),
        "arm_random_indexing_recall_at_1_mean": _arm("arm_random_indexing", 1),
        "arm_random_indexing_recall_at_5_mean": _arm("arm_random_indexing", 5),
        "arm_random_indexing_recall_at_10_mean": _arm("arm_random_indexing", 10),
        "arm_random_baseline_recall_at_1_mean": _arm("arm_random_baseline", 1),
        "arm_random_baseline_recall_at_5_mean": _arm("arm_random_baseline", 5),
        "arm_random_baseline_recall_at_10_mean": _arm("arm_random_baseline", 10),
    }


def _compute_verdict(
    agg: Dict[str, Any], per_seed: Sequence[Dict[str, Any]]
) -> Tuple[str, str]:
    v2a = agg["arm_v2a_ppmi_svd_recall_at_5_mean"]
    v1 = agg["arm_v1_concept_encoder_recall_at_5_mean"]
    ct = agg["arm_char_trigram_recall_at_5_mean"]
    ri = agg["arm_random_indexing_recall_at_5_mean"]
    rb = agg["arm_random_baseline_recall_at_5_mean"]

    all_arms_differ = all(bool(s.get("arms_differ_verified")) for s in per_seed)

    # Structural bug first.
    if not all_arms_differ:
        return (
            "HARD_FAIL",
            f"HF_STRUCTURAL arms_differ_verified=False on at least one seed; "
            f"5-arm prototype tables hash-collide.",
        )

    # HF1: v2A worse than v1.
    if v2a < v1:
        return (
            "HARD_FAIL",
            f"HF1 v2A_ppmi_svd r5={v2a:.4f} < v1_concept_encoder r5={v1:.4f}; "
            f"PPMI/SVD mechanism WORSE than failed competitive-Hebbian baseline. "
            f"(char_trigram={ct:.4f}, random_indexing={ri:.4f}, random_baseline={rb:.4f})",
        )
    # HF2: v2A worse than char_trigram.
    if v2a < ct:
        return (
            "HARD_FAIL",
            f"HF2 v2A_ppmi_svd r5={v2a:.4f} < char_trigram_ref r5={ct:.4f}; "
            f"v2-A still loses to bag baseline; MAJOR REFRAME. "
            f"(v1={v1:.4f}, random_indexing={ri:.4f}, random_baseline={rb:.4f})",
        )

    # HP band assessment.
    gap_v1 = v2a - v1
    gap_ct = v2a - ct
    hp1 = gap_v1 > HP1_V2A_MINUS_V1_GAP
    hp2 = gap_ct >= HP2_V2A_MINUS_TRIGRAM_GAP
    hp3 = abs(v1 - HP3_V1_TARGET_R5) <= HP3_V1_RECOVERY_TOL
    hp4 = rb <= HP4_RANDOM_CEILING
    hp5 = all_arms_differ

    if hp1 and hp2 and hp3 and hp4 and hp5:
        return (
            "HARD_PASS",
            f"HARD_PASS: v2A_r5={v2a:.4f} v1_r5={v1:.4f} ct_r5={ct:.4f} "
            f"ri_r5={ri:.4f} rb_r5={rb:.4f}; gaps(v1={gap_v1:.4f},ct={gap_ct:.4f}); "
            f"HP1-HP5 all met.",
        )

    # MIDDLE_BAND.
    cleared = []
    missed = []
    for name, ok in [("HP1", hp1), ("HP2", hp2), ("HP3", hp3),
                     ("HP4", hp4), ("HP5", hp5)]:
        (cleared if ok else missed).append(name)
    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: v2A_r5={v2a:.4f} v1_r5={v1:.4f} ct_r5={ct:.4f} "
        f"ri_r5={ri:.4f} rb_r5={rb:.4f}; gaps(v1={gap_v1:.4f},ct={gap_ct:.4f}); "
        f"cleared={cleared} missed={missed}.",
    )


# ---------------------------------------------------------------------------
# Main driver.
# ---------------------------------------------------------------------------

N_ARMS = 5


def _run_mode_dispatch(run_mode: str) -> Tuple[List[int], int, int]:
    if run_mode == "smoke":
        return list(SMOKE_SEEDS), int(SMOKE_N_ATOMS), N_ARMS * len(SMOKE_SEEDS)
    if run_mode == "full":
        return list(FULL_SEEDS), int(FULL_N_ATOMS), N_ARMS * len(FULL_SEEDS)
    return [11], 20, N_ARMS


def _write_final_metrics(
    output_dir: Path,
    run_mode: str,
    per_seed: List[Dict[str, Any]],
    agg: Dict[str, Any],
    verdict: str,
    verdict_msg: str,
    elapsed_s: float,
    baseline_in_band: bool,
    discriminator_fires: bool,
    expected_n_units: int,
    landed_n_units: int,
    baseline_probe_notes: str,
) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": round(float(elapsed_s), 3),
        "run_mode": run_mode,
        "ts_iso": _now_iso(),
        "config": {
            "n_dim": int(N_DIM),
            "ppmi_k_sparsity": float(PPMI_K_SPARSITY),
            "ppmi_min_term_freq": int(PPMI_MIN_TERM_FREQ),
            "ppmi_smoothing": float(PPMI_SMOOTHING),
            "ri_k_signs": int(RI_K_SIGNS),
            "ce_k_sparsity": float(CE_K_SPARSITY),
            "ce_max_pos": int(CE_MAX_POS),
            "smoke_n_atoms": int(SMOKE_N_ATOMS),
            "full_n_atoms": int(FULL_N_ATOMS),
            "smoke_seeds": list(SMOKE_SEEDS),
            "full_seeds": list(FULL_SEEDS),
            "corpus_path": str(CORPUS_ATOMS_JSONL),
            "corpus_filter": (
                "kind=lexicon AND pos in {n,v,a,r} AND "
                f"len(desc)>={MIN_DEFINITION_LEN} AND "
                f"len(synonyms)>={MIN_SYNONYMS}"
            ),
            "hp_bands": {
                "HP1_v2A_minus_v1_gap": HP1_V2A_MINUS_V1_GAP,
                "HP2_v2A_minus_trigram_gap": HP2_V2A_MINUS_TRIGRAM_GAP,
                "HP3_v1_target_r5": HP3_V1_TARGET_R5,
                "HP3_v1_recovery_tol": HP3_V1_RECOVERY_TOL,
                "HP4_random_ceiling": HP4_RANDOM_CEILING,
                "char_trigram_prior": CHAR_TRIGRAM_PRIOR,
                "baseline_in_band_lo": BASELINE_IN_BAND_LO,
                "baseline_in_band_hi": BASELINE_IN_BAND_HI,
            },
        },
        "aggregate": agg,
        "per_seed": per_seed,
        "cardinality_ok": bool(landed_n_units == expected_n_units),
        "expected_n_units": int(expected_n_units),
        "landed_n_units": int(landed_n_units),
        "baseline_in_band": bool(baseline_in_band),
        "discriminator_fires_at_smoke": bool(discriminator_fires),
        "arms_differ_verified": bool(
            all(bool(s.get("arms_differ_verified")) for s in per_seed)
        ),
        "final_metrics_atomicity": "tmp_replace",
        "progress_logging": "print_flush_true",
        "storage_strategy": "sharded_per_atom_prototype_hds",
        "compute_arch": "sequential_cpu_numpy",
        "baseline_probe_notes": baseline_probe_notes,
        "prereg_path": "preregs/2026-07-03_substrate_concept_encoder_v2_A_ppmi_svd_sparse.md",
        "meta_rules_touched": [
            "AF_arms_differ", "AG_baseline_in_band", "AH_atomic_final_metrics",
            "K_discriminator_fires", "L_strict_above_floor",
            "M_calibration_default_ok", "H_cardinality_ok",
            "run_mode_verification_16",
        ],
        "hp_scope": {
            "ARM_V2A_PPMI_SVD": ["HP1", "HP2", "HP5"],
            "ARM_V1_CONCEPT_ENCODER": ["HP3", "HP5"],
            "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE": ["HP5"],
            "ARM_RANDOM_INDEXING": ["HP5"],
            "ARM_RANDOM_BASELINE": ["HP4", "HP5"],
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return metrics


def _run_self_test(output_dir: Path) -> Dict[str, Any]:
    t0 = time.perf_counter()
    _write_start_marker(output_dir, "self_test", expected_n_units=N_ARMS)
    print(f"[selftest] loading {CORPUS_ATOMS_JSONL}", flush=True)
    atoms = _load_wordnet_atoms(max_atoms=20, seed=11)
    print(f"[selftest] loaded {len(atoms)} atoms; running 1-seed 5-arm eval", flush=True)
    with CellHeartbeat(str(output_dir), total_units=6, interval_s=10) as hb:
        per = _eval_one_seed(seed=11, atoms=atoms, n_dim=1024, hb=hb)
    per_seed = [per]
    agg = _aggregate_per_seed(per_seed)
    verdict, msg = _compute_verdict(agg, per_seed)
    baseline_in_band = (
        BASELINE_IN_BAND_LO <= agg["arm_char_trigram_recall_at_5_mean"] <= BASELINE_IN_BAND_HI
    )
    metrics = _write_final_metrics(
        output_dir=output_dir,
        run_mode="self_test",
        per_seed=per_seed,
        agg=agg,
        verdict=("SELFTEST_PASS" if per["arms_differ_verified"] else "SELFTEST_FAIL"),
        verdict_msg=(
            f"SELFTEST: arms_differ={per['arms_differ_verified']} "
            f"v2A_r5={agg['arm_v2a_ppmi_svd_recall_at_5_mean']:.3f} "
            f"v1_r5={agg['arm_v1_concept_encoder_recall_at_5_mean']:.3f} "
            f"ct_r5={agg['arm_char_trigram_recall_at_5_mean']:.3f} "
            f"ri_r5={agg['arm_random_indexing_recall_at_5_mean']:.3f} "
            f"rb_r5={agg['arm_random_baseline_recall_at_5_mean']:.3f} "
            f"baseline_in_band={baseline_in_band} verdict_probe={verdict} "
            f"[N=20 atoms 1 seed n_dim=1024]"
        ),
        elapsed_s=time.perf_counter() - t0,
        baseline_in_band=bool(baseline_in_band),
        discriminator_fires=True,
        expected_n_units=N_ARMS,
        landed_n_units=N_ARMS,
        baseline_probe_notes="self_test path; N=20 atoms 1 seed n_dim=1024; sanity only",
    )
    if not per["arms_differ_verified"]:
        raise AssertionError(
            "selftest: arms_differ_verified=False; ARM prototype tables hash-collide"
        )
    print(
        f"[selftest] PASS verdict={metrics['verdict']} "
        f"elapsed_s={metrics['elapsed_s']:.2f}",
        flush=True,
    )
    return metrics


def _run_smoke_or_full(output_dir: Path, run_mode: str) -> Dict[str, Any]:
    t0 = time.perf_counter()
    seeds, n_atoms, expected_units = _run_mode_dispatch(run_mode)
    _write_start_marker(output_dir, run_mode, expected_n_units=expected_units)
    print(
        f"[{run_mode}] loading corpus + running {len(seeds)} seeds "
        f"at N={n_atoms} atoms n_dim={N_DIM}",
        flush=True,
    )
    atoms = _load_wordnet_atoms(max_atoms=n_atoms, seed=seeds[0])
    if len(atoms) < n_atoms:
        print(
            f"[{run_mode}] WARN: only {len(atoms)} atoms passed filter (< {n_atoms})",
            flush=True,
        )
    n_atoms_actual = len(atoms)
    per_seed: List[Dict[str, Any]] = []
    landed_units = 0
    with CellHeartbeat(str(output_dir), total_units=expected_units,
                       interval_s=30, every_n_units=1) as hb:
        for seed in seeds:
            per = _eval_one_seed(seed=int(seed), atoms=atoms, n_dim=N_DIM, hb=hb)
            per_seed.append(per)
            landed_units += N_ARMS
    agg = _aggregate_per_seed(per_seed)

    ct5 = agg["arm_char_trigram_recall_at_5_mean"]
    v1_5 = agg["arm_v1_concept_encoder_recall_at_5_mean"]
    baseline_in_band = (
        BASELINE_IN_BAND_LO <= ct5 <= BASELINE_IN_BAND_HI
        and BASELINE_IN_BAND_LO <= v1_5 <= BASELINE_IN_BAND_HI
    )
    v2a5 = agg["arm_v2a_ppmi_svd_recall_at_5_mean"]
    discriminator_fires = (v2a5 - ct5) >= 0.05

    baseline_probe_notes = (
        f"baseline_in_band={baseline_in_band} "
        f"ct_r5={ct5:.4f} v1_r5={v1_5:.4f} v2A_r5={v2a5:.4f} "
        f"ri_r5={agg['arm_random_indexing_recall_at_5_mean']:.4f} "
        f"rb_r5={agg['arm_random_baseline_recall_at_5_mean']:.4f} "
        f"gap_v2A_vs_ct={v2a5 - ct5:.4f} "
        f"discriminator_fires_at_0.05={discriminator_fires}"
    )
    print(f"[{run_mode}] {baseline_probe_notes}", flush=True)

    verdict, msg = _compute_verdict(agg, per_seed)

    metrics = _write_final_metrics(
        output_dir=output_dir,
        run_mode=run_mode,
        per_seed=per_seed,
        agg=agg,
        verdict=verdict,
        verdict_msg=(
            msg + f" [{run_mode} N={n_atoms_actual} n_dim={N_DIM} "
            f"seeds={list(seeds)}]"
        ),
        elapsed_s=time.perf_counter() - t0,
        baseline_in_band=bool(baseline_in_band),
        discriminator_fires=bool(discriminator_fires),
        expected_n_units=int(expected_units),
        landed_n_units=int(landed_units),
        baseline_probe_notes=baseline_probe_notes,
    )
    print(
        f"[{run_mode}] verdict={metrics['verdict']} elapsed_s={metrics['elapsed_s']:.2f}",
        flush=True,
    )
    return metrics


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--run-mode",
        default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
        choices=["self_test", "smoke", "full"],
    )
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    return ap.parse_args(argv)


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    args = _parse_args()
    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode
    output_dir = get_output_dir(ANCHOR_NAME)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(
        f"[main] anchor={ANCHOR_NAME} run_mode={run_mode} output_dir={output_dir}",
        flush=True,
    )
    if run_mode == "self_test":
        _run_self_test(output_dir)
    else:
        _run_smoke_or_full(output_dir, run_mode)
    return 0


if __name__ == "__main__":
    _out_dir = get_output_dir(ANCHOR_NAME)
    try:
        _rc = main()
        sys.exit(_rc)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:  # noqa: BLE001
        _write_crash_metrics(_out_dir, _e)
        raise
