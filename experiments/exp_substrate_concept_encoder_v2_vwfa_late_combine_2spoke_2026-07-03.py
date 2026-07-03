"""substrate_concept_encoder_v2_vwfa_late_combine_2spoke_2026_07_03

v2 concept encoder P1 minimum path: brain-analog VWFA-analog + late-combine
composition on SAME task as substrate-content HF baseline (WordNet held-out-
synonym retrieval, N=100 atoms at smoke, seeds [11,17,23]).

FRAMING (LOAD-BEARING per USER 2026-07-02):
  Tests v2 architecture as brain-analog COMPOSITION (VWFA + ATL-hub via LATE
  COMBINE / N400-window integration).  Mechanism-claim scope stays in
  SUPERVISED HELD-OUT-SYNONYM RETRIEVAL on substrate-ingested WordNet content.
  HP earned here does NOT grant "substrate reads text" or "substrate knows
  language broadly"; grants "brain-analog v2 architecture rescues transfer
  failure on substrate's known symbolic content at this regime".

Prior baseline (MEASURED @ v1 smoke, 2026-07-02):
  data/exp_substrate_concept_encoder_substrate_content_v1_2026_07_02/metrics.json
    ARM_CONCEPT_ENCODER    recall@5_mean = 0.16  (target to RECOVER)
    ARM_CHAR_POSITIONAL    recall@5_mean = 0.21
    ARM_CHAR_TRIGRAM_UNSUP recall@5_mean = 0.28  (target to BEAT)
  verdict = HARD_FAIL (HF2: mechanism has NO advantage over char-trigram bag)

Arms (5 arms x 3 seeds = 15 units at smoke):
  1. ARM_V2_VWFA_ALONE
       VWFAEncoder(scales=[1,2,3,4], bind_position=True); v_query = v_ortho
       Sanity check: multi-scale + position should be within +-0.03 of trigram
       bag baseline (VWFA subsumes bag as scale=3 no-position degenerate case).
  2. ARM_V2_SEM_ALONE  (recovers v1 baseline)
       Current ConceptEncoder (sparse-competitive-Hebbian); v_query = v_sem
       Backward compat: HP1 requires recall@5 within +-0.02 of prior 0.16.
  3. ARM_V2_LATE_COMBINE (LOAD-BEARING)
       (alpha_fit, gamma_fit=1-alpha_fit) fit on 50%-atom held-out val split;
       reported on the other 50%; HP3 requires recall@5 >= trigram bag + 0.05.
  4. ARM_V2_LATE_COMBINE_EQUAL
       alpha=gamma=0.5 fixed; simpler control (no held-out fitting).  Same
       eval-split as ARM_V2_LATE_COMBINE for apples-to-apples.
  5. ARM_CHAR_TRIGRAM_UNSUP_REFERENCE
       CharTrigramEncoder bag baseline (target to beat 0.28).

Reference-arm evaluation is done on the SAME eval-split of queries as
ARM_V2_LATE_COMBINE so all 5 arms report apples-to-apples numbers.  The
50% fit-split is used ONLY by ARM_V2_LATE_COMBINE to fit alpha via
score-level late-combine grid search.

HP bands (see preregs/2026-07-03_substrate_concept_encoder_v2_vwfa_late_combine_2spoke.md):
  HP1 (Gate D: sem-only backward-compat): ARM_V2_SEM_ALONE recall@5 within
    +-0.02 of prior 0.16 baseline (v2 sem-only recovers current encoder).
  HP2 (VWFA correctness): ARM_V2_VWFA_ALONE recall@5 within +-0.03 of
    ARM_CHAR_TRIGRAM_UNSUP_REFERENCE (VWFA-analog subsumes char-trigram bag).
  HP3 (rescue): ARM_V2_LATE_COMBINE recall@5 >= ARM_CHAR_TRIGRAM_UNSUP_REFERENCE + 0.05
  HP4 (composition useful): ARM_V2_LATE_COMBINE recall@5 >=
    max(ARM_V2_VWFA_ALONE, ARM_V2_SEM_ALONE) + 0.03
  HP5 (arms differ): all 5 arm HD tables hash-distinct at smoke.
  HF1 VWFA broken: ARM_V2_VWFA_ALONE recall@5 < 0.20
  HF2 late-combine no rescue: ARM_V2_LATE_COMBINE recall@5 < max(VWFA, SEM)
  HF3 sem-only regression: ARM_V2_SEM_ALONE recall@5 outside [0.14, 0.18].
  HF4 arms hash-collide: any two arm tables bit-identical.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (META_RULE_AF; hash-test 5 arms)
  - final_metrics_atomicity: tmp_replace via os.replace
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: supervised retrieval; chance floor k/N (recall@5 = 5/100 = 0.05
    at smoke, 5/500 = 0.01 at full).  Discriminator = arm-vs-reference gap.
  - baseline_in_band at smoke (META_RULE_AG; 0.05 < ct_reference < 0.80).
  - discriminator survives scale: baseline v1 smoke ct5=0.28 at same regime
    (N=100 n_dim=2048) -- reproducing at the same regime is analytical
    justification; late-combine gap is the discriminator being probed.
  - HP_SCOPE:
      HP1 -> ARM_V2_SEM_ALONE only
      HP2 -> ARM_V2_VWFA_ALONE only
      HP3, HP4 -> ARM_V2_LATE_COMBINE only
      HP5 -> all arms
  - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@.

Compute arch: sequential CPU numpy (matches v1; no GPU speedup on
100-atom retrieval task).  Storage: sharded per-atom prototype HDs (no
composition depth L>=2).  Progress logging: print_flush_true.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Bootstrap: reach hdlab + experiments helpers when executed as script.
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from hdlab.concept_encoder import ConceptEncoder  # noqa: E402
from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: E402
from hdlab.vwfa import VWFAEncoder  # noqa: E402
from hdlab.late_combine import (  # noqa: E402
    LateCombine,
    fit_weights_grid_2spoke,
    score_combined_topk,
)
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from experiments._cell_heartbeat import CellHeartbeat  # noqa: E402

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------

ANCHOR_NAME = "substrate_concept_encoder_v2_vwfa_late_combine_2spoke_2026_07_03"

CORPUS_ATOMS_JSONL = _REPO / "data" / "substrate_index" / "concept" / "atoms.jsonl"

# Sweep sizes.
SMOKE_N_ATOMS = 100
SMOKE_SEEDS = [11, 17, 23]
FULL_N_ATOMS = 500
FULL_SEEDS = [11, 17, 23]

# HD dim.
N_DIM = 2048

# ConceptEncoder / VWFA config.
K_SPARSITY = 0.02
MAX_POS = 24
VWFA_SCALES = (1, 2, 3, 4)
VWFA_BIND_POSITION = True

# Required min-atom quality.
MIN_DEFINITION_LEN = 20
MIN_SYNONYMS = 3

# HP band constants (all recall@5 unless noted).
# v1 baseline reproduction target (MEASURED@data/exp_substrate_concept_encoder_
#   substrate_content_v1_2026_07_02/metrics.json:aggregate.arm_concept_encoder_recall_at_5_mean = 0.16).
HP1_SEM_TARGET_MEAN = 0.16
HP1_SEM_TOLERANCE = 0.02
# VWFA subsumption target (MEASURED@data/exp_substrate_concept_encoder_
#   substrate_content_v1_2026_07_02/metrics.json:aggregate.arm_char_trigram_recall_at_5_mean = 0.28).
HP2_VWFA_TARGET_MEAN = 0.28
HP2_VWFA_TOLERANCE = 0.03
# Rescue gap: late-combine over trigram bag.
HP3_LATE_COMBINE_GAP_TRIGRAM = 0.05
# Composition useful: late-combine over any single spoke.
HP4_LATE_COMBINE_GAP_ANY_SPOKE = 0.03
# VWFA broken floor.
HF1_VWFA_FLOOR = 0.20
# Sem-only regression band (mirror of HP1 band).
HF3_SEM_LO = HP1_SEM_TARGET_MEAN - HP1_SEM_TOLERANCE
HF3_SEM_HI = HP1_SEM_TARGET_MEAN + HP1_SEM_TOLERANCE

# baseline-in-band check (on the char_trigram REFERENCE arm; if it saturates
# or floors, discriminator can't fire).
BASELINE_IN_BAND_LO = 0.05
BASELINE_IN_BAND_HI = 0.80

# Weight-fit grid.
ALPHA_GRID = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)

# Fit/eval split: fraction of queries used for fitting alpha.
FIT_SPLIT_FRACTION = 0.5


# ---------------------------------------------------------------------------
# Crash-diagnostic helpers.
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(
    output_dir: Path, run_mode: str, expected_n_units: int
) -> None:
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
# Corpus loading (COPY from v1 -- avoids cross-cell import churn).
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
        raise FileNotFoundError(
            f"substrate concept atoms not found: {CORPUS_ATOMS_JSONL}"
        )
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
        raise RuntimeError(
            "no WordNet lexicon atoms passed filter; corpus may be stale"
        )
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

def _cosine_argmax_topk(
    query_hd: np.ndarray, prototypes: np.ndarray, k: int
) -> np.ndarray:
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


# ---------- prototype builders ----------

def _build_prototypes_vwfa(
    training_sentences: Sequence[str],
    training_labels: Sequence[int],
    n_atoms: int,
    n_dim: int,
    seed: int,
) -> Tuple[np.ndarray, VWFAEncoder]:
    """Build per-atom VWFA prototype HDs via mean-bundle of training sentence
    encodings.  Seed is passed via seed_prefix so different seeds get
    different VWFA codebooks (matches the seed-per-arm discipline used by
    ConceptEncoder + CharPositionalEncoder).
    """
    enc = VWFAEncoder(
        n_dim=n_dim,
        scales=VWFA_SCALES,
        bind_position=VWFA_BIND_POSITION,
        max_pos=MAX_POS,
        seed_prefix=f"VWFA_S{seed}",
        sign_bundle=True,
    )
    acc = np.zeros((n_atoms, n_dim), dtype=np.float32)
    counts = np.zeros(n_atoms, dtype=np.float32)
    for s, lbl in zip(training_sentences, training_labels):
        hd = enc.encode_sentence(str(s))
        acc[int(lbl)] += hd
        counts[int(lbl)] += 1.0
    denom = np.where(counts > 0, counts, 1.0)
    proto = acc / denom[:, None]
    return proto.astype(np.float32), enc


def _build_prototypes_char_trigram(
    training_sentences: Sequence[str],
    training_labels: Sequence[int],
    n_atoms: int,
    n_dim: int,
    seed: int,
) -> Tuple[np.ndarray, CharTrigramEncoder]:
    del seed
    enc = CharTrigramEncoder(n_dim=n_dim, pad_char=" ")
    acc = np.zeros((n_atoms, n_dim), dtype=np.float32)
    counts = np.zeros(n_atoms, dtype=np.float32)
    for s, lbl in zip(training_sentences, training_labels):
        hd = enc.encode(str(s)).astype(np.float32)
        acc[int(lbl)] += hd
        counts[int(lbl)] += 1.0
    denom = np.where(counts > 0, counts, 1.0)
    proto = acc / denom[:, None]
    return proto.astype(np.float32), enc


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
        k_sparsity=K_SPARSITY,
        seed=seed,
        max_pos=MAX_POS,
        concept_names=None,
        mask_target_word=False,
    )
    labels_arr = np.asarray(list(training_labels), dtype=np.int64)
    enc.fit(list(training_sentences), labels_arr)
    return enc.concept_hds.astype(np.int8), enc


# ---------- query encoders ----------

def _encode_query_vwfa(enc: VWFAEncoder, q_word: str) -> np.ndarray:
    return enc.encode_sentence(q_word).astype(np.float32)


def _encode_query_char_trigram(enc: CharTrigramEncoder, q_word: str) -> np.ndarray:
    return enc.encode(q_word).astype(np.float32)


def _encode_query_concept_encoder(enc: ConceptEncoder, q_word: str) -> np.ndarray:
    # Surface encoder path -- matches v1 cell.
    return enc._surface_encoder.encode_sentence(str(q_word)).astype(np.float32)  # noqa: SLF001


# ---------- eval helpers ----------

def _recall_at_k_single_arm(
    queries: Sequence[Tuple[int, str]],
    prototypes: np.ndarray,
    encode_query_fn,
    k_values: Sequence[int],
) -> Dict[str, float]:
    correct_at_k = {int(k): 0 for k in k_values}
    n = len(queries)
    for atom_idx, q_word in queries:
        q_hd = encode_query_fn(q_word)
        topk_max = max(k_values)
        order = _cosine_argmax_topk(q_hd, prototypes, int(topk_max))
        for k in k_values:
            if int(atom_idx) in order[: int(k)].tolist():
                correct_at_k[int(k)] += 1
    return {f"recall_at_{k}": correct_at_k[int(k)] / max(1, n) for k in k_values}


def _recall_at_k_late_combine(
    queries: Sequence[Tuple[int, str]],
    per_query_vwfa_hds: Sequence[np.ndarray],
    per_query_sem_hds: Sequence[np.ndarray],
    prot_vwfa: np.ndarray,
    prot_sem: np.ndarray,
    alpha: float,
    gamma: float,
    k_values: Sequence[int],
) -> Dict[str, float]:
    correct_at_k = {int(k): 0 for k in k_values}
    n = len(queries)
    for i, (atom_idx, _q_word) in enumerate(queries):
        topk_max = max(k_values)
        order = score_combined_topk(
            per_query_vwfa_hds[i], per_query_sem_hds[i],
            prot_vwfa, prot_sem, alpha, gamma, int(topk_max),
        )
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

    # Split queries into fit / eval halves by index (per-seed shuffle).
    rng = random.Random(int(seed))
    idx = list(range(len(queries)))
    rng.shuffle(idx)
    n_fit = int(round(len(queries) * FIT_SPLIT_FRACTION))
    fit_idx = sorted(idx[:n_fit])
    eval_idx = sorted(idx[n_fit:])
    fit_queries = [queries[i] for i in fit_idx]
    eval_queries = [queries[i] for i in eval_idx]
    print(
        f"[seed={seed}] fit_split n={len(fit_queries)} eval_split n={len(eval_queries)}",
        flush=True,
    )

    # ---- BUILD PROTOTYPES for all 3 encoders (once per seed) ----

    t_a = time.perf_counter()
    prot_vwfa, vwfa_enc = _build_prototypes_vwfa(
        training_sentences, training_labels, n_atoms, n_dim, seed
    )
    vwfa_hash = _hash_prototype_table(prot_vwfa)
    print(f"[seed={seed}] VWFA prototypes built wall={time.perf_counter()-t_a:.2f}s "
          f"hash={vwfa_hash[:16]}", flush=True)
    hb.tick(unit_idx=2, extra={"phase": "vwfa_built", "seed": seed}, force=True)

    t_a = time.perf_counter()
    prot_sem, sem_enc = _build_prototypes_concept_encoder(
        training_sentences, training_labels, n_atoms, n_dim, seed
    )
    sem_hash = _hash_prototype_table(prot_sem)
    print(f"[seed={seed}] SEM prototypes built wall={time.perf_counter()-t_a:.2f}s "
          f"hash={sem_hash[:16]}", flush=True)
    hb.tick(unit_idx=3, extra={"phase": "sem_built", "seed": seed}, force=True)

    t_a = time.perf_counter()
    prot_trigram, trigram_enc = _build_prototypes_char_trigram(
        training_sentences, training_labels, n_atoms, n_dim, seed
    )
    trigram_hash = _hash_prototype_table(prot_trigram)
    print(f"[seed={seed}] TRIGRAM prototypes built wall={time.perf_counter()-t_a:.2f}s "
          f"hash={trigram_hash[:16]}", flush=True)
    hb.tick(unit_idx=4, extra={"phase": "trigram_built", "seed": seed}, force=True)

    # Pre-encode per-query HDs (VWFA + SEM) so we can use them across arms
    # + fit_weights_grid_2spoke without recomputing.
    per_q_vwfa_fit = [_encode_query_vwfa(vwfa_enc, q) for _, q in fit_queries]
    per_q_sem_fit = [_encode_query_concept_encoder(sem_enc, q) for _, q in fit_queries]
    per_q_vwfa_eval = [_encode_query_vwfa(vwfa_enc, q) for _, q in eval_queries]
    per_q_sem_eval = [_encode_query_concept_encoder(sem_enc, q) for _, q in eval_queries]
    fit_labels = [ai for ai, _ in fit_queries]

    # ---- FIT ALPHA on the fit-split for ARM_V2_LATE_COMBINE ----
    t_fit = time.perf_counter()
    best_alpha, best_beta, best_gamma, fit_recall_at_1 = fit_weights_grid_2spoke(
        per_query_ortho=per_q_vwfa_fit,
        per_query_sem=per_q_sem_fit,
        prototypes_ortho=prot_vwfa,
        prototypes_sem=prot_sem,
        labels=fit_labels,
        alpha_grid=ALPHA_GRID,
    )
    fit_wall = time.perf_counter() - t_fit
    print(
        f"[seed={seed}] LATE_COMBINE fit alpha={best_alpha:.2f} gamma={best_gamma:.2f} "
        f"fit_recall@1={fit_recall_at_1:.4f} wall={fit_wall:.2f}s",
        flush=True,
    )

    # ---- EVAL all 5 arms on the eval-split ----

    # ARM_V2_VWFA_ALONE
    t_arm = time.perf_counter()
    arm_vwfa_alone = _recall_at_k_single_arm(
        eval_queries, prot_vwfa,
        lambda q: _encode_query_vwfa(vwfa_enc, q),
        k_values,
    )
    arm_vwfa_wall = time.perf_counter() - t_arm
    print(f"[seed={seed} ARM_V2_VWFA_ALONE] "
          f"recall@1={arm_vwfa_alone['recall_at_1']:.4f} "
          f"recall@5={arm_vwfa_alone['recall_at_5']:.4f} "
          f"recall@10={arm_vwfa_alone['recall_at_10']:.4f} "
          f"wall={arm_vwfa_wall:.2f}s", flush=True)

    # ARM_V2_SEM_ALONE
    t_arm = time.perf_counter()
    arm_sem_alone = _recall_at_k_single_arm(
        eval_queries, prot_sem,
        lambda q: _encode_query_concept_encoder(sem_enc, q),
        k_values,
    )
    arm_sem_wall = time.perf_counter() - t_arm
    print(f"[seed={seed} ARM_V2_SEM_ALONE] "
          f"recall@1={arm_sem_alone['recall_at_1']:.4f} "
          f"recall@5={arm_sem_alone['recall_at_5']:.4f} "
          f"recall@10={arm_sem_alone['recall_at_10']:.4f} "
          f"wall={arm_sem_wall:.2f}s", flush=True)

    # ARM_V2_LATE_COMBINE (fit alpha, gamma)
    t_arm = time.perf_counter()
    arm_late_combine = _recall_at_k_late_combine(
        eval_queries, per_q_vwfa_eval, per_q_sem_eval,
        prot_vwfa, prot_sem,
        best_alpha, best_gamma, k_values,
    )
    arm_lc_wall = time.perf_counter() - t_arm
    print(f"[seed={seed} ARM_V2_LATE_COMBINE] alpha={best_alpha:.2f} "
          f"recall@1={arm_late_combine['recall_at_1']:.4f} "
          f"recall@5={arm_late_combine['recall_at_5']:.4f} "
          f"recall@10={arm_late_combine['recall_at_10']:.4f} "
          f"wall={arm_lc_wall:.2f}s", flush=True)

    # ARM_V2_LATE_COMBINE_EQUAL (fixed 0.5/0.5)
    t_arm = time.perf_counter()
    arm_late_combine_equal = _recall_at_k_late_combine(
        eval_queries, per_q_vwfa_eval, per_q_sem_eval,
        prot_vwfa, prot_sem,
        0.5, 0.5, k_values,
    )
    arm_lce_wall = time.perf_counter() - t_arm
    print(f"[seed={seed} ARM_V2_LATE_COMBINE_EQUAL] "
          f"recall@1={arm_late_combine_equal['recall_at_1']:.4f} "
          f"recall@5={arm_late_combine_equal['recall_at_5']:.4f} "
          f"recall@10={arm_late_combine_equal['recall_at_10']:.4f} "
          f"wall={arm_lce_wall:.2f}s", flush=True)

    # ARM_CHAR_TRIGRAM_UNSUP_REFERENCE
    t_arm = time.perf_counter()
    arm_trigram_ref = _recall_at_k_single_arm(
        eval_queries, prot_trigram,
        lambda q: _encode_query_char_trigram(trigram_enc, q),
        k_values,
    )
    arm_tri_wall = time.perf_counter() - t_arm
    print(f"[seed={seed} ARM_CHAR_TRIGRAM_UNSUP_REFERENCE] "
          f"recall@1={arm_trigram_ref['recall_at_1']:.4f} "
          f"recall@5={arm_trigram_ref['recall_at_5']:.4f} "
          f"recall@10={arm_trigram_ref['recall_at_10']:.4f} "
          f"wall={arm_tri_wall:.2f}s", flush=True)

    hb.tick(
        unit_idx=5,
        extra={
            "phase": "arms_evaluated",
            "seed": seed,
            "vwfa_r5": arm_vwfa_alone["recall_at_5"],
            "sem_r5": arm_sem_alone["recall_at_5"],
            "late_combine_r5": arm_late_combine["recall_at_5"],
            "late_combine_equal_r5": arm_late_combine_equal["recall_at_5"],
            "trigram_ref_r5": arm_trigram_ref["recall_at_5"],
        },
        force=True,
    )

    # Arms-differ hash check across 4 unique HD tables (LATE_COMBINE and
    # LATE_COMBINE_EQUAL both use prot_vwfa + prot_sem so they don't have
    # their OWN prototype table; the ARM identity is the (weights, tables)
    # tuple.  Hash-check the 3 distinct prototype tables plus the two
    # weight-tuples.
    hashes = {
        "ARM_V2_VWFA_ALONE": vwfa_hash,
        "ARM_V2_SEM_ALONE": sem_hash,
        "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE": trigram_hash,
        "ARM_V2_LATE_COMBINE": _hash_prototype_table(
            np.array([best_alpha, best_gamma], dtype=np.float32)
        ) + "+" + vwfa_hash[:16] + "+" + sem_hash[:16],
        "ARM_V2_LATE_COMBINE_EQUAL": _hash_prototype_table(
            np.array([0.5, 0.5], dtype=np.float32)
        ) + "+" + vwfa_hash[:16] + "+" + sem_hash[:16],
    }
    unique_hashes = set(hashes.values())
    # Structural check: 3 distinct prototype tables + 2 distinct late-combine
    # arms (weight-signature differs from single-arm hashes).
    arms_differ_verified = len(unique_hashes) == 5

    return {
        "seed": int(seed),
        "n_atoms": int(n_atoms),
        "n_dim": int(n_dim),
        "n_train_sentences": int(len(training_sentences)),
        "n_queries_total": int(len(queries)),
        "n_queries_fit": int(len(fit_queries)),
        "n_queries_eval": int(len(eval_queries)),
        "alpha_fit": float(best_alpha),
        "gamma_fit": float(best_gamma),
        "fit_recall_at_1": float(fit_recall_at_1),
        "arm_v2_vwfa_alone": arm_vwfa_alone,
        "arm_v2_sem_alone": arm_sem_alone,
        "arm_v2_late_combine": arm_late_combine,
        "arm_v2_late_combine_equal": arm_late_combine_equal,
        "arm_char_trigram_reference": arm_trigram_ref,
        "arm_walls_s": {
            "vwfa": round(arm_vwfa_wall, 3),
            "sem": round(arm_sem_wall, 3),
            "late_combine": round(arm_lc_wall, 3),
            "late_combine_equal": round(arm_lce_wall, 3),
            "trigram_ref": round(arm_tri_wall, 3),
            "weight_fit": round(fit_wall, 3),
        },
        "arms_differ_verified": bool(arms_differ_verified),
        "arm_hashes": hashes,
        "wall_s": round(time.perf_counter() - t0, 3),
    }


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def _aggregate_per_seed(per_seed: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    def _mean(vals: List[float]) -> float:
        return float(np.mean(vals)) if vals else 0.0

    def _arm(name: str, k: int) -> float:
        return _mean([float(s[name][f"recall_at_{k}"]) for s in per_seed])

    return {
        "arm_v2_vwfa_alone_recall_at_1_mean": _arm("arm_v2_vwfa_alone", 1),
        "arm_v2_vwfa_alone_recall_at_5_mean": _arm("arm_v2_vwfa_alone", 5),
        "arm_v2_vwfa_alone_recall_at_10_mean": _arm("arm_v2_vwfa_alone", 10),
        "arm_v2_sem_alone_recall_at_1_mean": _arm("arm_v2_sem_alone", 1),
        "arm_v2_sem_alone_recall_at_5_mean": _arm("arm_v2_sem_alone", 5),
        "arm_v2_sem_alone_recall_at_10_mean": _arm("arm_v2_sem_alone", 10),
        "arm_v2_late_combine_recall_at_1_mean": _arm("arm_v2_late_combine", 1),
        "arm_v2_late_combine_recall_at_5_mean": _arm("arm_v2_late_combine", 5),
        "arm_v2_late_combine_recall_at_10_mean": _arm("arm_v2_late_combine", 10),
        "arm_v2_late_combine_equal_recall_at_1_mean": _arm("arm_v2_late_combine_equal", 1),
        "arm_v2_late_combine_equal_recall_at_5_mean": _arm("arm_v2_late_combine_equal", 5),
        "arm_v2_late_combine_equal_recall_at_10_mean": _arm("arm_v2_late_combine_equal", 10),
        "arm_char_trigram_reference_recall_at_1_mean": _arm("arm_char_trigram_reference", 1),
        "arm_char_trigram_reference_recall_at_5_mean": _arm("arm_char_trigram_reference", 5),
        "arm_char_trigram_reference_recall_at_10_mean": _arm("arm_char_trigram_reference", 10),
        "alpha_fit_mean": float(np.mean([float(s["alpha_fit"]) for s in per_seed])),
    }


def _compute_verdict(
    agg: Dict[str, Any], per_seed: Sequence[Dict[str, Any]]
) -> Tuple[str, str]:
    vwfa5 = agg["arm_v2_vwfa_alone_recall_at_5_mean"]
    sem5 = agg["arm_v2_sem_alone_recall_at_5_mean"]
    lc5 = agg["arm_v2_late_combine_recall_at_5_mean"]
    lce5 = agg["arm_v2_late_combine_equal_recall_at_5_mean"]
    tri5 = agg["arm_char_trigram_reference_recall_at_5_mean"]

    all_arms_differ = all(bool(s.get("arms_differ_verified")) for s in per_seed)

    # HF4 first (structural bug).
    if not all_arms_differ:
        return (
            "HARD_FAIL",
            f"HF4 arms_differ_verified=False on at least one seed; "
            f"HD tables hash-collide (mechanism bug).",
        )
    # HF1 VWFA broken.
    if vwfa5 < HF1_VWFA_FLOOR:
        return (
            "HARD_FAIL",
            f"HF1 ARM_V2_VWFA_ALONE recall@5_mean={vwfa5:.4f} < {HF1_VWFA_FLOOR:.2f} "
            f"(VWFA implementation broken; expected to reproduce char-trigram bag "
            f"performance).",
        )
    # HF3 sem-only regression.
    if not (HF3_SEM_LO <= sem5 <= HF3_SEM_HI):
        return (
            "HARD_FAIL",
            f"HF3 ARM_V2_SEM_ALONE recall@5_mean={sem5:.4f} outside "
            f"[{HF3_SEM_LO:.2f}, {HF3_SEM_HI:.2f}] (sem-only backward-compat "
            f"broken; expected ~{HP1_SEM_TARGET_MEAN:.2f} +- {HP1_SEM_TOLERANCE:.2f}).",
        )
    # HF2 late-combine no rescue.
    max_spoke = max(vwfa5, sem5)
    if lc5 < max_spoke:
        return (
            "HARD_FAIL",
            f"HF2 ARM_V2_LATE_COMBINE recall@5_mean={lc5:.4f} < "
            f"max(VWFA={vwfa5:.4f}, SEM={sem5:.4f})={max_spoke:.4f}; "
            f"composition HURTS relative to best single spoke.",
        )
    # HP assessments.
    hp1 = abs(sem5 - HP1_SEM_TARGET_MEAN) <= HP1_SEM_TOLERANCE
    hp2 = abs(vwfa5 - tri5) <= HP2_VWFA_TOLERANCE
    hp3 = (lc5 - tri5) >= HP3_LATE_COMBINE_GAP_TRIGRAM
    hp4 = (lc5 - max_spoke) >= HP4_LATE_COMBINE_GAP_ANY_SPOKE
    hp5 = all_arms_differ

    if hp1 and hp2 and hp3 and hp4 and hp5:
        return (
            "HARD_PASS",
            f"HARD_PASS: vwfa_r5={vwfa5:.4f} sem_r5={sem5:.4f} "
            f"late_combine_r5={lc5:.4f} late_combine_equal_r5={lce5:.4f} "
            f"trigram_ref_r5={tri5:.4f} alpha_fit_mean={agg['alpha_fit_mean']:.2f}; "
            f"all of HP1-HP5 met (v2 architecture RESCUES transfer failure).",
        )
    # Otherwise MIDDLE_BAND.
    cleared = []
    missed = []
    for name, ok in [("HP1", hp1), ("HP2", hp2), ("HP3", hp3), ("HP4", hp4), ("HP5", hp5)]:
        (cleared if ok else missed).append(name)
    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: vwfa_r5={vwfa5:.4f} sem_r5={sem5:.4f} "
        f"late_combine_r5={lc5:.4f} late_combine_equal_r5={lce5:.4f} "
        f"trigram_ref_r5={tri5:.4f} alpha_fit_mean={agg['alpha_fit_mean']:.2f} "
        f"gap_lc_vs_trigram={lc5-tri5:+.4f} gap_lc_vs_maxspoke={lc5-max_spoke:+.4f}; "
        f"cleared={cleared} missed={missed}.",
    )


# ---------------------------------------------------------------------------
# Main driver.
# ---------------------------------------------------------------------------

def _run_mode_dispatch(run_mode: str) -> Tuple[List[int], int, int]:
    """(seeds_to_run, n_atoms, expected_units).

    expected_units = len(seeds) * n_arms(=5).
    """
    if run_mode == "smoke":
        return list(SMOKE_SEEDS), int(SMOKE_N_ATOMS), 5 * len(SMOKE_SEEDS)
    if run_mode == "full":
        return list(FULL_SEEDS), int(FULL_N_ATOMS), 5 * len(FULL_SEEDS)
    return [11], 20, 5


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
            "k_sparsity": float(K_SPARSITY),
            "max_pos": int(MAX_POS),
            "vwfa_scales": list(VWFA_SCALES),
            "vwfa_bind_position": bool(VWFA_BIND_POSITION),
            "smoke_n_atoms": int(SMOKE_N_ATOMS),
            "full_n_atoms": int(FULL_N_ATOMS),
            "smoke_seeds": list(SMOKE_SEEDS),
            "full_seeds": list(FULL_SEEDS),
            "fit_split_fraction": float(FIT_SPLIT_FRACTION),
            "alpha_grid": list(ALPHA_GRID),
            "corpus_path": str(CORPUS_ATOMS_JSONL),
            "corpus_filter": (
                "kind=lexicon AND pos in {n,v,a,r} AND "
                f"len(desc)>={MIN_DEFINITION_LEN} AND "
                f"len(synonyms)>={MIN_SYNONYMS}"
            ),
            "hp_bands": {
                "HP1_sem_target_mean": HP1_SEM_TARGET_MEAN,
                "HP1_sem_tolerance": HP1_SEM_TOLERANCE,
                "HP2_vwfa_target_mean": HP2_VWFA_TARGET_MEAN,
                "HP2_vwfa_tolerance": HP2_VWFA_TOLERANCE,
                "HP3_late_combine_gap_trigram": HP3_LATE_COMBINE_GAP_TRIGRAM,
                "HP4_late_combine_gap_any_spoke": HP4_LATE_COMBINE_GAP_ANY_SPOKE,
                "HF1_vwfa_floor": HF1_VWFA_FLOOR,
                "HF3_sem_lo": HF3_SEM_LO,
                "HF3_sem_hi": HF3_SEM_HI,
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
        "prereg_path": (
            "preregs/2026-07-03_substrate_concept_encoder_v2_vwfa_late_combine_2spoke.md"
        ),
        "design_note_path": (
            "notes/research_brain_reading_architecture_emulation_v2_"
            "prescription_substrate_content_HF_2026-07-02.md"
        ),
        "meta_rules_touched": [
            "AF_arms_differ",
            "AG_baseline_in_band",
            "AH_atomic_final_metrics",
            "K_discriminator_fires",
            "L_strict_above_floor",
            "M_calibration_default_ok",
            "H_cardinality_ok",
            "run_mode_verification_16",
        ],
        "hp_scope": {
            "HP1": ["ARM_V2_SEM_ALONE"],
            "HP2": ["ARM_V2_VWFA_ALONE"],
            "HP3": ["ARM_V2_LATE_COMBINE"],
            "HP4": ["ARM_V2_LATE_COMBINE"],
            "HP5": ["ARM_V2_VWFA_ALONE", "ARM_V2_SEM_ALONE",
                    "ARM_V2_LATE_COMBINE", "ARM_V2_LATE_COMBINE_EQUAL",
                    "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE"],
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
    """1 seed, N=20 atoms, n_dim=1024 -- runner --self-test in seconds."""
    t0 = time.perf_counter()
    _write_start_marker(output_dir, "self_test", expected_n_units=5)
    print(f"[selftest] loading {CORPUS_ATOMS_JSONL}", flush=True)
    atoms = _load_wordnet_atoms(max_atoms=20, seed=11)
    print(f"[selftest] loaded {len(atoms)} WordNet atoms; running 1-seed eval",
          flush=True)
    with CellHeartbeat(str(output_dir), total_units=5, interval_s=10) as hb:
        per = _eval_one_seed(seed=11, atoms=atoms, n_dim=1024, hb=hb)
    per_seed = [per]
    agg = _aggregate_per_seed(per_seed)
    tri5 = agg["arm_char_trigram_reference_recall_at_5_mean"]
    baseline_in_band = BASELINE_IN_BAND_LO <= tri5 <= BASELINE_IN_BAND_HI
    verdict = "SELFTEST_PASS" if per["arms_differ_verified"] else "SELFTEST_FAIL"
    verdict_msg = (
        f"SELFTEST: arms_differ={per['arms_differ_verified']} "
        f"vwfa_r5={agg['arm_v2_vwfa_alone_recall_at_5_mean']:.3f} "
        f"sem_r5={agg['arm_v2_sem_alone_recall_at_5_mean']:.3f} "
        f"late_combine_r5={agg['arm_v2_late_combine_recall_at_5_mean']:.3f} "
        f"late_combine_equal_r5={agg['arm_v2_late_combine_equal_recall_at_5_mean']:.3f} "
        f"trigram_ref_r5={tri5:.3f} alpha_fit={agg['alpha_fit_mean']:.2f} "
        f"[N=20 atoms 1 seed n_dim=1024]"
    )
    metrics = _write_final_metrics(
        output_dir=output_dir,
        run_mode="self_test",
        per_seed=per_seed,
        agg=agg,
        verdict=verdict,
        verdict_msg=verdict_msg,
        elapsed_s=time.perf_counter() - t0,
        baseline_in_band=bool(baseline_in_band),
        discriminator_fires=True,
        expected_n_units=5,
        landed_n_units=5,
        baseline_probe_notes=(
            "self_test path; N=20 atoms 1 seed n_dim=1024; sanity only"
        ),
    )
    if not per["arms_differ_verified"]:
        raise AssertionError(
            "selftest: arms_differ_verified=False; ARM HD tables hash-collide"
        )
    print(f"[selftest] PASS verdict={metrics['verdict']} "
          f"elapsed_s={metrics['elapsed_s']:.2f}", flush=True)
    return metrics


def _run_smoke_or_full(output_dir: Path, run_mode: str) -> Dict[str, Any]:
    t0 = time.perf_counter()
    seeds, n_atoms, expected_units = _run_mode_dispatch(run_mode)
    _write_start_marker(output_dir, run_mode, expected_n_units=expected_units)
    print(f"[{run_mode}] loading corpus + running {len(seeds)} seeds "
          f"at N={n_atoms} atoms n_dim={N_DIM}", flush=True)
    atoms = _load_wordnet_atoms(max_atoms=n_atoms, seed=seeds[0])
    if len(atoms) < n_atoms:
        print(f"[{run_mode}] WARN: only {len(atoms)} atoms passed filter "
              f"(< {n_atoms}); using all available", flush=True)
    n_atoms_actual = len(atoms)
    per_seed: List[Dict[str, Any]] = []
    landed_units = 0
    with CellHeartbeat(str(output_dir), total_units=expected_units,
                       interval_s=30, every_n_units=1) as hb:
        for seed in seeds:
            per = _eval_one_seed(
                seed=int(seed), atoms=atoms, n_dim=N_DIM, hb=hb
            )
            per_seed.append(per)
            landed_units += 5
    agg = _aggregate_per_seed(per_seed)

    tri5 = agg["arm_char_trigram_reference_recall_at_5_mean"]
    baseline_in_band = BASELINE_IN_BAND_LO <= tri5 <= BASELINE_IN_BAND_HI

    lc5 = agg["arm_v2_late_combine_recall_at_5_mean"]
    vwfa5 = agg["arm_v2_vwfa_alone_recall_at_5_mean"]
    sem5 = agg["arm_v2_sem_alone_recall_at_5_mean"]
    max_spoke = max(vwfa5, sem5)
    discriminator_fires = (lc5 - max_spoke) >= 0.03 or (lc5 - tri5) >= 0.05

    baseline_probe_notes = (
        f"baseline_in_band={baseline_in_band} tri_r5={tri5:.4f} "
        f"vwfa_r5={vwfa5:.4f} sem_r5={sem5:.4f} late_combine_r5={lc5:.4f} "
        f"gap_vs_tri={lc5-tri5:+.4f} gap_vs_maxspoke={lc5-max_spoke:+.4f} "
        f"alpha_fit_mean={agg['alpha_fit_mean']:.2f} "
        f"discriminator_fires={discriminator_fires}"
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
    print(f"[{run_mode}] verdict={metrics['verdict']} "
          f"elapsed_s={metrics['elapsed_s']:.2f}", flush=True)
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
    print(f"[main] anchor={ANCHOR_NAME} run_mode={run_mode} "
          f"output_dir={output_dir}", flush=True)
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
