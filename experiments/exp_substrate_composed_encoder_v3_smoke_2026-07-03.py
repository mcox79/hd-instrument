"""substrate_composed_encoder_v3_smoke_2026_07_03

Composed brain-analog concept encoder v3 = VWFA (surface orthographic) + PPMI/SVD
(amodal semantic co-occurrence) parallel-stream late-combine at N400 window.

Skunkworks + 4/5 drills 2026-07-03 recommended SKIP modern-Hopfield readout
(Component C HF'd at smoke commit 4cd1d30ba); real load-bearing lever is
COMPOSITION.  This cell tests: does score-level parallel-stream composition
BEAT the char-trigram bag baseline (0.28) that killed v1 concept_encoder (0.16)?

FRAMING (LOAD-BEARING per USER 2026-07-02):
  MECHANISM-COMPOSITION CG on SUPERVISED regime (WordNet lexicon partition
  as designer-supplied labeled corpus).  Substrate KNOWS ALMOST NOTHING.
  HP earned here does NOT grant "substrate understands English"; grants
  "brain-analog VWFA+ATL score-level late-combine composition rescues the
  substrate-content HF on this SUPERVISED corpus at this regime."

TASK: SUPERVISED held-out-synonym retrieval on WordNet lexicon atoms.
  Same task + regime + corpus loader + query selection as
  exp_substrate_concept_encoder_component_C_modern_hopfield_readout_2026-07-03
  for apples-to-apples comparison.

Arms (5, 3 seeds -> 15 units at smoke):
  1. ARM_V3_COMPOSED_EQUAL_ALPHA        (LOAD-BEARING; alpha=beta=0.5)
  2. ARM_VWFA_ALONE                     (positive control; alpha=1,beta=0)
  3. ARM_PPMI_ALONE                     (positive control; alpha=0,beta=1)
  4. ARM_V1_CONCEPT_ENCODER_COSINE      (regression check; MEASURED 0.16 prior)
  5. ARM_CHAR_TRIGRAM_UNSUP_REFERENCE   (target to beat; MEASURED 0.28 prior)

Arms 2 and 3 are BIT-IDENTICAL to pure-VWFA-argmax and pure-PPMI-argmax
respectively (score-scaling invariance of argmax; verified in
hdlab/composed_encoder_v3.py selftests 5 and 6 which run in the cell's
--self-test path).

HP bands (see preregs/2026-07-03_substrate_composed_encoder_v3_smoke.md):
  HP1 (composition lift):  ARM_V3 r@5 >= max(VWFA, PPMI) + 0.03
  HP2 (beat bag):          ARM_V3 r@5 >= TRIGRAM + 0.04  (target 0.32)
  HP3 (v1 backward-compat): ARM_V1_COSINE within +/-0.03 of 0.16
  HP4 (trigram match):     ARM_TRIGRAM within +/-0.03 of 0.28
  HP5 (arms differ):       5 arm top-k stacks hash-distinct
  HP6 (formula identity):  ARM_VWFA_ALONE == pure-VWFA r@5; ARM_PPMI_ALONE == pure-PPMI r@5
  HF1 (composition hurts): ARM_V3 < max(VWFA, PPMI)
  HF2 (still loses bag):   ARM_V3 < TRIGRAM
  HF3 (arms identical):    any two arm top-k stacks hash-collide
  HF4 (v1 regression):     ARM_V1_COSINE outside [0.13, 0.19]
  MIDDLE_BAND:             subset of HP1-HP6 met, not all-6

CELL-TEMPLATE MANDATORY:
  - arms_differ_verified at smoke gate (hash of per-arm top-k index arrays)
  - final_metrics_atomicity: tmp_replace via os.replace
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: no quantitative CRLB (supervised retrieval; chance floor k/N)
  - baseline_in_band at smoke (0.05 < TRIGRAM_r5 < 0.80)
  - discriminator: ARM_V3 vs max(VWFA, PPMI) gap; must be non-degenerate at smoke
  - HP_SCOPE: per-arm declared

Compute arch: sequential CPU numpy.  Storage strategy: sharded per-atom
  prototype HDs.  Composition depth L=1.
Progress logging: print_flush_true + line-buffered stdout at cell entry.

ASCII-only.  No emojis.  No em dashes.
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

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: E402
from hdlab.composed_encoder_v3 import ComposedEncoderV3  # noqa: E402
from hdlab.concept_encoder import ConceptEncoder  # noqa: E402
from hdlab.ppmi_sparse_encoder import PPMISparseEncoder  # noqa: E402
from hdlab.vwfa import VWFAEncoder  # noqa: E402
from experiments._cell_heartbeat import CellHeartbeat  # noqa: E402
from experiments._seed_checkpoint import get_output_dir  # noqa: E402

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------

ANCHOR_NAME = "substrate_composed_encoder_v3_smoke_2026_07_03"

CORPUS_ATOMS_JSONL = _REPO / "data" / "substrate_index" / "concept" / "atoms.jsonl"

SMOKE_N_ATOMS = 100
SMOKE_SEEDS = [11, 17, 23]
FULL_N_ATOMS = 500
FULL_SEEDS = [11, 17, 23]

N_DIM = 2048
K_SPARSITY = 0.02
MAX_POS = 24

MIN_DEFINITION_LEN = 20
MIN_SYNONYMS = 3

# HP bands (recall@5 unless noted).
HP1_COMPOSITION_LIFT = 0.03      # ARM_V3 >= max(VWFA, PPMI) + 0.03
HP2_BEAT_BAG_MARGIN = 0.04       # ARM_V3 >= TRIGRAM + 0.04  (target 0.32)
HP3_V1_MEASURED = 0.16           # MEASURED@Component_C_smoke:aggregate.arm_v1_concept_encoder_cosine_recall_at_5_mean
HP3_V1_TOL = 0.03
HP4_TRIGRAM_MEASURED = 0.28      # MEASURED@Component_C_smoke:aggregate.arm_char_trigram_unsup_reference_recall_at_5_mean
HP4_TRIGRAM_TOL = 0.03
HF4_V1_LO = 0.13
HF4_V1_HI = 0.19
BASELINE_IN_BAND_LO = 0.05
BASELINE_IN_BAND_HI = 0.80


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
# Corpus loading (BIT-IDENTICAL to Component C cell for apples-to-apples).
# ---------------------------------------------------------------------------

def _clean_name(raw_name: str) -> str:
    n = raw_name
    if n.startswith("WN_"):
        n = n[3:]
    parts = n.split(".")
    if len(parts) >= 3 and len(parts[-1]) <= 3 and parts[-1].isdigit():
        n = ".".join(parts[:-2])
    return n.replace("_", " ")


def _load_wordnet_atoms(max_atoms: int) -> List[Dict[str, Any]]:
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
            "no WordNet lexicon atoms passed the filter; corpus may be stale"
        )
    candidates.sort(key=lambda x: (-int(x["freq"]), str(x["atom_id"])))
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
# Retrieval helpers.
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


def _hash_topk_array(topk_stack: np.ndarray) -> str:
    return hashlib.sha256(topk_stack.tobytes()).hexdigest()


def _build_trigram_prototypes(
    training_sentences: Sequence[str],
    training_labels: Sequence[int],
    n_atoms: int,
    n_dim: int,
) -> Tuple[np.ndarray, CharTrigramEncoder]:
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


def _fit_v1_concept_encoder(
    training_sentences: Sequence[str],
    training_labels: Sequence[int],
    n_atoms: int,
    n_dim: int,
    seed: int,
) -> ConceptEncoder:
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
    return enc


# ---------------------------------------------------------------------------
# Arm eval logic.
# ---------------------------------------------------------------------------

def _eval_recall_topk(
    n_queries: int,
    correct_at_k: Dict[int, int],
    k_values: Sequence[int],
) -> Dict[str, float]:
    return {
        f"recall_at_{k}": correct_at_k[int(k)] / max(1, n_queries)
        for k in k_values
    }


def _eval_one_seed(
    seed: int,
    atoms: Sequence[Dict[str, Any]],
    n_dim: int,
    hb: CellHeartbeat,
) -> Dict[str, Any]:
    """Run 5 arms at one seed.  Reuses one ComposedEncoderV3 fit for arms 1-3
    (different (alpha, beta) via set_weights).  Arms 4 (V1 concept encoder)
    and 5 (char-trigram) are independent.
    """
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
    topk_max = int(max(k_values))
    n_q = len(queries)

    # Fit ComposedEncoderV3 once; reused for arms 1-3 via set_weights.
    t_fit = time.perf_counter()
    v3 = ComposedEncoderV3(
        n_dim=n_dim,
        alpha=0.5,
        beta=0.5,
        vwfa_kwargs={
            "scales": (1, 2, 3, 4),
            "bind_position": True,
            "max_pos": MAX_POS,
            "seed_prefix": f"COMPOSED_V3_S{seed}",
            "sign_bundle": True,
        },
        ppmi_kwargs={
            "min_term_freq": 2,
            "smoothing": 0.75,
            "seed": int(seed),
            "k_sparsity": K_SPARSITY,
        },
    )
    v3.fit(training_sentences, training_labels)
    v3_fit_wall = time.perf_counter() - t_fit
    print(f"[seed={seed}] ComposedEncoderV3 fit wall={v3_fit_wall:.1f}s", flush=True)
    hb.tick(unit_idx=2, extra={"phase": "v3_fit_done", "seed": seed}, force=True)

    # --- ARM 1: V3 COMPOSED EQUAL ALPHA (LOAD-BEARING) ---
    v3.set_weights(alpha=0.5, beta=0.5)
    correct_v3 = {int(k): 0 for k in k_values}
    topk_v3_stack = np.zeros((n_q, topk_max), dtype=np.int32)
    t_arm = time.perf_counter()
    for qi in range(n_q):
        atom_idx = int(queries[qi][0])
        order = v3.retrieve_topk(str(queries[qi][1]), k=topk_max)
        topk_v3_stack[qi] = order.astype(np.int32)
        for k in k_values:
            if atom_idx in order[: int(k)].tolist():
                correct_v3[int(k)] += 1
    arm1 = _eval_recall_topk(n_q, correct_v3, k_values)
    arm1_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_V3_COMPOSED_EQUAL_ALPHA] r@1={arm1['recall_at_1']:.4f} "
        f"r@5={arm1['recall_at_5']:.4f} r@10={arm1['recall_at_10']:.4f} "
        f"wall={arm1_wall:.1f}s",
        flush=True,
    )
    hb.tick(unit_idx=3, extra={"phase": "arm1_v3_done", "seed": seed}, force=True)

    # --- ARM 2: VWFA ALONE (alpha=1, beta=0; formula-identity to pure VWFA) ---
    v3.set_weights(alpha=1.0, beta=0.0)
    correct_vwfa = {int(k): 0 for k in k_values}
    topk_vwfa_stack = np.zeros((n_q, topk_max), dtype=np.int32)
    t_arm = time.perf_counter()
    for qi in range(n_q):
        atom_idx = int(queries[qi][0])
        order = v3.retrieve_topk(str(queries[qi][1]), k=topk_max)
        topk_vwfa_stack[qi] = order.astype(np.int32)
        for k in k_values:
            if atom_idx in order[: int(k)].tolist():
                correct_vwfa[int(k)] += 1
    arm2 = _eval_recall_topk(n_q, correct_vwfa, k_values)
    arm2_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_VWFA_ALONE] r@1={arm2['recall_at_1']:.4f} "
        f"r@5={arm2['recall_at_5']:.4f} r@10={arm2['recall_at_10']:.4f} "
        f"wall={arm2_wall:.1f}s",
        flush=True,
    )
    hb.tick(unit_idx=4, extra={"phase": "arm2_vwfa_done", "seed": seed}, force=True)

    # --- ARM 3: PPMI ALONE (alpha=0, beta=1; formula-identity to pure PPMI) ---
    v3.set_weights(alpha=0.0, beta=1.0)
    correct_ppmi = {int(k): 0 for k in k_values}
    topk_ppmi_stack = np.zeros((n_q, topk_max), dtype=np.int32)
    t_arm = time.perf_counter()
    for qi in range(n_q):
        atom_idx = int(queries[qi][0])
        order = v3.retrieve_topk(str(queries[qi][1]), k=topk_max)
        topk_ppmi_stack[qi] = order.astype(np.int32)
        for k in k_values:
            if atom_idx in order[: int(k)].tolist():
                correct_ppmi[int(k)] += 1
    arm3 = _eval_recall_topk(n_q, correct_ppmi, k_values)
    arm3_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_PPMI_ALONE] r@1={arm3['recall_at_1']:.4f} "
        f"r@5={arm3['recall_at_5']:.4f} r@10={arm3['recall_at_10']:.4f} "
        f"wall={arm3_wall:.1f}s",
        flush=True,
    )
    hb.tick(unit_idx=5, extra={"phase": "arm3_ppmi_done", "seed": seed}, force=True)

    # HP6 formula-identity verification (in-cell):
    #   ARM_VWFA_ALONE top-k stack == pure-VWFA argmax top-k stack
    #   ARM_PPMI_ALONE top-k stack == pure-PPMI argmax top-k stack
    protos_vwfa = v3.protos_vwfa
    protos_ppmi = v3.protos_ppmi
    if protos_vwfa is None or protos_ppmi is None:
        raise RuntimeError("HP6 verification: v3 protos None after fit")
    pure_vwfa_stack = np.zeros((n_q, topk_max), dtype=np.int32)
    pure_ppmi_stack = np.zeros((n_q, topk_max), dtype=np.int32)
    for qi in range(n_q):
        qw = str(queries[qi][1])
        vw = v3.vwfa.encode_sentence(qw).astype(np.float32)
        vw_n = float(np.linalg.norm(vw))
        vw_norm = vw / vw_n if vw_n > 1e-12 else vw
        pp = v3.ppmi.encode(qw).astype(np.float32)
        pp_n = float(np.linalg.norm(pp))
        pp_norm = pp / pp_n if pp_n > 1e-12 else pp
        pure_vwfa_stack[qi] = _cosine_argmax_topk(
            vw_norm, protos_vwfa, topk_max
        ).astype(np.int32)
        pure_ppmi_stack[qi] = _cosine_argmax_topk(
            pp_norm, protos_ppmi, topk_max
        ).astype(np.int32)
    hp6_vwfa_ok = bool(np.array_equal(topk_vwfa_stack, pure_vwfa_stack))
    hp6_ppmi_ok = bool(np.array_equal(topk_ppmi_stack, pure_ppmi_stack))

    # --- ARM 4: V1 CONCEPT ENCODER COSINE (regression check) ---
    t_arm = time.perf_counter()
    v1_enc = _fit_v1_concept_encoder(
        training_sentences, training_labels, n_atoms, n_dim, int(seed)
    )
    v1_concept_hds = v1_enc.concept_hds.astype(np.int8)  # [n_atoms, n_dim]
    v1_surf_encoder = v1_enc._surface_encoder  # noqa: SLF001
    correct_v1 = {int(k): 0 for k in k_values}
    topk_v1_stack = np.zeros((n_q, topk_max), dtype=np.int32)
    for qi in range(n_q):
        atom_idx = int(queries[qi][0])
        q_hd = v1_surf_encoder.encode_sentence(str(queries[qi][1])).astype(np.float32)
        order = _cosine_argmax_topk(q_hd, v1_concept_hds, topk_max)
        topk_v1_stack[qi] = order.astype(np.int32)
        for k in k_values:
            if atom_idx in order[: int(k)].tolist():
                correct_v1[int(k)] += 1
    arm4 = _eval_recall_topk(n_q, correct_v1, k_values)
    arm4_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_V1_CONCEPT_ENCODER_COSINE] r@1={arm4['recall_at_1']:.4f} "
        f"r@5={arm4['recall_at_5']:.4f} r@10={arm4['recall_at_10']:.4f} "
        f"wall={arm4_wall:.1f}s",
        flush=True,
    )
    hb.tick(unit_idx=6, extra={"phase": "arm4_v1_done", "seed": seed}, force=True)

    # --- ARM 5: CHAR-TRIGRAM UNSUP REFERENCE ---
    t_arm = time.perf_counter()
    tri_proto, tri_enc = _build_trigram_prototypes(
        training_sentences, training_labels, n_atoms, n_dim
    )
    correct_tri = {int(k): 0 for k in k_values}
    topk_tri_stack = np.zeros((n_q, topk_max), dtype=np.int32)
    for qi in range(n_q):
        atom_idx = int(queries[qi][0])
        q_hd = tri_enc.encode(str(queries[qi][1])).astype(np.float32)
        order = _cosine_argmax_topk(q_hd, tri_proto, topk_max)
        topk_tri_stack[qi] = order.astype(np.int32)
        for k in k_values:
            if atom_idx in order[: int(k)].tolist():
                correct_tri[int(k)] += 1
    arm5 = _eval_recall_topk(n_q, correct_tri, k_values)
    arm5_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_CHAR_TRIGRAM_UNSUP_REFERENCE] r@1={arm5['recall_at_1']:.4f} "
        f"r@5={arm5['recall_at_5']:.4f} r@10={arm5['recall_at_10']:.4f} "
        f"wall={arm5_wall:.1f}s",
        flush=True,
    )
    hb.tick(unit_idx=7, extra={"phase": "arm5_trigram_done", "seed": seed}, force=True)

    # ARMS-DIFFER hash check.
    hashes = {
        "ARM_V3_COMPOSED_EQUAL_ALPHA":       _hash_topk_array(topk_v3_stack),
        "ARM_VWFA_ALONE":                    _hash_topk_array(topk_vwfa_stack),
        "ARM_PPMI_ALONE":                    _hash_topk_array(topk_ppmi_stack),
        "ARM_V1_CONCEPT_ENCODER_COSINE":     _hash_topk_array(topk_v1_stack),
        "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE":  _hash_topk_array(topk_tri_stack),
    }
    unique_hashes = set(hashes.values())
    arms_differ_verified = len(unique_hashes) == 5

    return {
        "seed": int(seed),
        "n_atoms": int(n_atoms),
        "n_dim": int(n_dim),
        "n_train_sentences": int(len(training_sentences)),
        "n_queries": int(n_q),
        "arm_v3_composed_equal_alpha": arm1,
        "arm_vwfa_alone": arm2,
        "arm_ppmi_alone": arm3,
        "arm_v1_concept_encoder_cosine": arm4,
        "arm_char_trigram_unsup_reference": arm5,
        "arm_walls_s": {
            "v3_composed": round(arm1_wall, 3),
            "vwfa_alone": round(arm2_wall, 3),
            "ppmi_alone": round(arm3_wall, 3),
            "v1_concept_cosine": round(arm4_wall, 3),
            "char_trigram": round(arm5_wall, 3),
            "v3_fit": round(v3_fit_wall, 3),
        },
        "arms_differ_verified": bool(arms_differ_verified),
        "arm_hashes": hashes,
        "hp6_vwfa_identity_ok": bool(hp6_vwfa_ok),
        "hp6_ppmi_identity_ok": bool(hp6_ppmi_ok),
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

    arms = [
        "arm_v3_composed_equal_alpha",
        "arm_vwfa_alone",
        "arm_ppmi_alone",
        "arm_v1_concept_encoder_cosine",
        "arm_char_trigram_unsup_reference",
    ]
    agg: Dict[str, Any] = {}
    for a in arms:
        for k in (1, 5, 10):
            agg[f"{a}_recall_at_{k}_mean"] = _arm(a, k)
    return agg


def _compute_verdict(
    agg: Dict[str, Any], per_seed: Sequence[Dict[str, Any]]
) -> Tuple[str, str]:
    v3_5 = agg["arm_v3_composed_equal_alpha_recall_at_5_mean"]
    vwfa_5 = agg["arm_vwfa_alone_recall_at_5_mean"]
    ppmi_5 = agg["arm_ppmi_alone_recall_at_5_mean"]
    v1_5 = agg["arm_v1_concept_encoder_cosine_recall_at_5_mean"]
    tri_5 = agg["arm_char_trigram_unsup_reference_recall_at_5_mean"]
    best_spoke = max(vwfa_5, ppmi_5)

    all_arms_differ = all(bool(s.get("arms_differ_verified")) for s in per_seed)
    hp6_vwfa_ok = all(bool(s.get("hp6_vwfa_identity_ok")) for s in per_seed)
    hp6_ppmi_ok = all(bool(s.get("hp6_ppmi_identity_ok")) for s in per_seed)

    # HF gates (priority order).
    if not all_arms_differ:
        return (
            "HARD_FAIL",
            "HF3_ARMS_IDENTICAL: at least one seed has arms_differ_verified=False; "
            "top-k index stacks hash-collide (arm-implementation bug).",
        )
    if not hp6_vwfa_ok or not hp6_ppmi_ok:
        return (
            "HARD_FAIL",
            f"HP6_FORMULA_IDENTITY_BROKEN: hp6_vwfa_ok={hp6_vwfa_ok} "
            f"hp6_ppmi_ok={hp6_ppmi_ok}; ComposedEncoderV3 argmax at (alpha=1,beta=0) "
            f"or (alpha=0,beta=1) diverges from pure single-stream argmax; "
            f"composition-identity broken.",
        )
    if not (HF4_V1_LO <= v1_5 <= HF4_V1_HI):
        return (
            "HARD_FAIL",
            f"HF4_V1_REGRESSION: ARM_V1_CONCEPT_ENCODER_COSINE r5={v1_5:.4f} "
            f"outside [{HF4_V1_LO}, {HF4_V1_HI}]; regression from prior 0.16 baseline.",
        )
    if v3_5 < best_spoke:
        return (
            "HARD_FAIL",
            f"HF1_COMPOSITION_HURTS: v3_r5={v3_5:.4f} < max(VWFA={vwfa_5:.4f}, "
            f"PPMI={ppmi_5:.4f})={best_spoke:.4f}; composition STRICTLY hurts "
            f"single-spoke performance; mechanism design bug.",
        )
    if v3_5 < tri_5:
        return (
            "HARD_FAIL",
            f"HF2_LOSES_TO_BAG: v3_r5={v3_5:.4f} < TRIGRAM={tri_5:.4f}; "
            f"composition still BELOW trivial bag baseline; skip-C recommendation "
            f"may need reconsideration OR VWFA+PPMI composition insufficient.",
        )

    # HP gates.
    hp1 = v3_5 >= best_spoke + HP1_COMPOSITION_LIFT
    hp2 = v3_5 >= tri_5 + HP2_BEAT_BAG_MARGIN
    hp3 = abs(v1_5 - HP3_V1_MEASURED) <= HP3_V1_TOL
    hp4 = abs(tri_5 - HP4_TRIGRAM_MEASURED) <= HP4_TRIGRAM_TOL
    hp5 = all_arms_differ
    hp6 = hp6_vwfa_ok and hp6_ppmi_ok

    if hp1 and hp2 and hp3 and hp4 and hp5 and hp6:
        return (
            "HARD_PASS",
            f"HARD_PASS: v3_r5={v3_5:.4f} best_spoke={best_spoke:.4f} "
            f"TRIGRAM={tri_5:.4f} V1={v1_5:.4f} (VWFA={vwfa_5:.4f} PPMI={ppmi_5:.4f}); "
            f"HP1+HP2+HP3+HP4+HP5+HP6 all met; brain-analog COMPOSITION rescues "
            f"substrate-content HF on this SUPERVISED regime.",
        )
    cleared: List[str] = []
    missed: List[str] = []
    for name, ok in [
        ("HP1", hp1), ("HP2", hp2), ("HP3", hp3),
        ("HP4", hp4), ("HP5", hp5), ("HP6", hp6),
    ]:
        (cleared if ok else missed).append(name)
    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: v3_r5={v3_5:.4f} best_spoke={best_spoke:.4f} "
        f"TRIGRAM={tri_5:.4f} V1={v1_5:.4f} (VWFA={vwfa_5:.4f} PPMI={ppmi_5:.4f}); "
        f"cleared={cleared} missed={missed}.",
    )


# ---------------------------------------------------------------------------
# Formula selftests (invoked when --self-test).
# ---------------------------------------------------------------------------

def _run_selftests_and_verify() -> None:
    """Invokes ComposedEncoderV3 module selftests (13) + inline formula sanity."""
    from hdlab.composed_encoder_v3 import _selftest as _v3_selftest  # noqa: PLC0415
    _v3_selftest()
    # Formula sanity on tiny corpus.
    v3 = ComposedEncoderV3(
        n_dim=512, alpha=1.0, beta=0.0,
        vwfa_kwargs={"seed_prefix": "SELFTEST_CELL"},
        ppmi_kwargs={"min_term_freq": 1, "seed": 11},
    )
    sents = ["cat pet feline", "dog canine bark", "airplane pilot fly"]
    labels = np.array([0, 1, 2], dtype=np.int64)
    v3.fit(sents, labels)
    # alpha=1, beta=0 -> pure VWFA argmax.
    top_v3 = v3.retrieve_topk("cat pet", k=1)
    # Direct pure-VWFA argmax:
    protos = v3.protos_vwfa
    if protos is None:
        raise RuntimeError("selftest: protos_vwfa None after fit")
    qhd = v3.vwfa.encode_sentence("cat pet").astype(np.float32)
    qn = float(np.linalg.norm(qhd))
    qh_norm = qhd / qn if qn > 1e-12 else qhd
    top_pure = _cosine_argmax_topk(qh_norm, protos, k=1)
    if not np.array_equal(top_v3, top_pure):
        raise AssertionError(
            f"CELL_SELFTEST formula-identity broken: v3(alpha=1,beta=0)={top_v3} "
            f"pure_vwfa={top_pure}"
        )
    print("[cell selftest] formula-identity in-cell verification PASS", flush=True)


# ---------------------------------------------------------------------------
# Main driver.
# ---------------------------------------------------------------------------

def _run_mode_dispatch(run_mode: str) -> Tuple[List[int], int, int]:
    """Return (seeds, n_atoms, expected_units).  expected_units = seeds * 5."""
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
                "HP1_composition_lift": HP1_COMPOSITION_LIFT,
                "HP2_beat_bag_margin": HP2_BEAT_BAG_MARGIN,
                "HP3_v1_measured": HP3_V1_MEASURED,
                "HP3_v1_tol": HP3_V1_TOL,
                "HP4_trigram_measured": HP4_TRIGRAM_MEASURED,
                "HP4_trigram_tol": HP4_TRIGRAM_TOL,
                "HF4_v1_lo": HF4_V1_LO,
                "HF4_v1_hi": HF4_V1_HI,
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
        "hp6_vwfa_identity_ok_all_seeds": bool(
            all(bool(s.get("hp6_vwfa_identity_ok")) for s in per_seed)
        ),
        "hp6_ppmi_identity_ok_all_seeds": bool(
            all(bool(s.get("hp6_ppmi_identity_ok")) for s in per_seed)
        ),
        "final_metrics_atomicity": "tmp_replace",
        "progress_logging": "print_flush_true",
        "storage_strategy": "sharded_per_atom_prototype_hds_composed_v3",
        "compute_arch": "sequential_cpu_numpy",
        "baseline_probe_notes": baseline_probe_notes,
        "prereg_path": "preregs/2026-07-03_substrate_composed_encoder_v3_smoke.md",
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
            "ARM_V3_COMPOSED_EQUAL_ALPHA": ["HP1", "HP2"],
            "ARM_VWFA_ALONE": ["HP6"],
            "ARM_PPMI_ALONE": ["HP6"],
            "ARM_V1_CONCEPT_ENCODER_COSINE": ["HP3"],
            "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE": ["HP4"],
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
    _write_start_marker(output_dir, "self_test", expected_n_units=5)
    print("[selftest] running module selftests + cell formula-identity check",
          flush=True)
    _run_selftests_and_verify()
    print(f"[selftest] running 1-seed 5-arm probe at N=20 atoms",
          flush=True)
    atoms = _load_wordnet_atoms(max_atoms=20)
    with CellHeartbeat(str(output_dir), total_units=7, interval_s=10) as hb:
        per = _eval_one_seed(seed=11, atoms=atoms, n_dim=1024, hb=hb)
    per_seed = [per]
    agg = _aggregate_per_seed(per_seed)
    verdict, msg = _compute_verdict(agg, per_seed)
    baseline_in_band = (
        BASELINE_IN_BAND_LO
        <= agg["arm_char_trigram_unsup_reference_recall_at_5_mean"]
        <= BASELINE_IN_BAND_HI
    )
    metrics = _write_final_metrics(
        output_dir=output_dir,
        run_mode="self_test",
        per_seed=per_seed,
        agg=agg,
        verdict=("SELFTEST_PASS" if per["arms_differ_verified"] and
                 per["hp6_vwfa_identity_ok"] and per["hp6_ppmi_identity_ok"]
                 else "SELFTEST_FAIL"),
        verdict_msg=(
            f"SELFTEST: arms_differ={per['arms_differ_verified']} "
            f"hp6_vwfa={per['hp6_vwfa_identity_ok']} "
            f"hp6_ppmi={per['hp6_ppmi_identity_ok']} "
            f"v3_r5={agg['arm_v3_composed_equal_alpha_recall_at_5_mean']:.3f} "
            f"vwfa_r5={agg['arm_vwfa_alone_recall_at_5_mean']:.3f} "
            f"ppmi_r5={agg['arm_ppmi_alone_recall_at_5_mean']:.3f} "
            f"v1_r5={agg['arm_v1_concept_encoder_cosine_recall_at_5_mean']:.3f} "
            f"tri_r5={agg['arm_char_trigram_unsup_reference_recall_at_5_mean']:.3f} "
            f"verdict_probe={verdict} [N=20 1seed n_dim=1024]"
        ),
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
            "selftest: arms_differ_verified=False; top-k stacks hash-collide"
        )
    if not per["hp6_vwfa_identity_ok"] or not per["hp6_ppmi_identity_ok"]:
        raise AssertionError(
            f"selftest: HP6 formula-identity broken; "
            f"vwfa_ok={per['hp6_vwfa_identity_ok']} "
            f"ppmi_ok={per['hp6_ppmi_identity_ok']}"
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
    atoms = _load_wordnet_atoms(max_atoms=n_atoms)
    if len(atoms) < n_atoms:
        print(
            f"[{run_mode}] WARN: only {len(atoms)} atoms passed filter "
            f"(< {n_atoms}); using all available",
            flush=True,
        )
    n_atoms_actual = len(atoms)
    per_seed: List[Dict[str, Any]] = []
    landed_units = 0
    with CellHeartbeat(
        str(output_dir), total_units=expected_units, interval_s=30,
        every_n_units=1,
    ) as hb:
        for seed in seeds:
            per = _eval_one_seed(
                seed=int(seed), atoms=atoms, n_dim=N_DIM, hb=hb
            )
            per_seed.append(per)
            landed_units += 5
    agg = _aggregate_per_seed(per_seed)

    v3_5 = agg["arm_v3_composed_equal_alpha_recall_at_5_mean"]
    vwfa_5 = agg["arm_vwfa_alone_recall_at_5_mean"]
    ppmi_5 = agg["arm_ppmi_alone_recall_at_5_mean"]
    tri_5 = agg["arm_char_trigram_unsup_reference_recall_at_5_mean"]
    v1_5 = agg["arm_v1_concept_encoder_cosine_recall_at_5_mean"]
    best_spoke = max(vwfa_5, ppmi_5)

    baseline_in_band = (
        BASELINE_IN_BAND_LO <= tri_5 <= BASELINE_IN_BAND_HI
        and BASELINE_IN_BAND_LO <= v1_5 <= BASELINE_IN_BAND_HI
    )
    lift_vs_best_spoke = v3_5 - best_spoke
    discriminator_fires = abs(lift_vs_best_spoke) > 1e-6

    baseline_probe_notes = (
        f"baseline_in_band={baseline_in_band} v3_r5={v3_5:.4f} "
        f"best_spoke={best_spoke:.4f} tri_r5={tri_5:.4f} v1_r5={v1_5:.4f} "
        f"lift_vs_best_spoke={lift_vs_best_spoke:.4f} "
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
    print(
        f"[{run_mode}] verdict={metrics['verdict']} "
        f"elapsed_s={metrics['elapsed_s']:.2f}",
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
        f"[main] anchor={ANCHOR_NAME} run_mode={run_mode} "
        f"output_dir={output_dir}",
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
