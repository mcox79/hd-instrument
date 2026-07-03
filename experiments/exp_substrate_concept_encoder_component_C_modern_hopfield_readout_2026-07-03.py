"""substrate_concept_encoder_component_C_modern_hopfield_readout_2026_07_03

Component C brain-analog: softmax-controlled retrieval / modern-Hopfield readout
(Ramsauer et al. 2020, arXiv:2008.02217). Neocortex pMTG-IFG semantic control
analog. Sibling of Component A (VWFA char-2/3/4-gram bank, in flight v2 P1) and
Component B (ATL amodal semantic hub PPMI/SVD, in flight V2-A).

FRAMING (LOAD-BEARING per USER 2026-07-02):
  Substrate mechanism = sparse-competitive-Hebbian at k=2% is architecturally
  HIPPOCAMPAL (DG-CA3 regime). Neocortex needs (a) surface V1-analog, (b) amodal
  hub, (c) SOFTMAX SEMANTIC CONTROL. This cell tests whether swapping the
  READOUT geometry (cosine argmax -> modern-Hopfield softmax) rescues the
  EXISTING ConceptEncoder on substrate content, without changing the encoder.

  Substrate DOES NOT KNOW ENGLISH. Test operates on substrate's WordNet lexicon
  atoms with definition+synonyms+hypernym as supervised concept-labelled surface
  content (same task as `exp_substrate_concept_encoder_substrate_content_v1`).

TASK: SUPERVISED held-out-synonym retrieval on WordNet lexicon atoms.
  Per atom: fit(training_sentences=[definition, syn1, syn2, "related to hyp"],
              concept_label=atom_idx).
  Query: encode(held_out_last_synonym) -> READOUT -> top-k over concept_hds.
  Metric: recall@{1,5,10}.

Arms (5, 3 seeds -> 15 units):
  1. ARM_V1_CONCEPT_ENCODER_COSINE           (baseline; MEASURED 0.16 r@5 prior)
  2. ARM_V1_CONCEPT_ENCODER_MODERN_HOPFIELD  (LOAD-BEARING; beta=4 one-step upd)
  3. ARM_V1_CONCEPT_ENCODER_MODERN_HOPFIELD_HIGH_BETA (beta=8)
  4. ARM_CHAR_TRIGRAM_UNSUP_REFERENCE        (bag-word bench; MEASURED 0.28 r@5)
  5. ARM_RANDOM_BASELINE                     (uniform random pick over N atoms)

READOUT DIFFERENCE (LOAD-BEARING notes):
  - COSINE arm: score_i = cos(surface_hd(query), concept_hd_i); top-k by score.
  - HOPFIELD arm: y = softmax(beta * cos(q, K) / sqrt(N)) @ K; rank i by
    cos(y, K_i). y is a one-step attractor blend; because concept_hds are
    sparse-bipolar with equal L2 norm, ranking by attention_weights is
    IDENTICAL to cosine argmax. The distinguishing behaviour under equal-norm
    storage is the RETRIEVED y (interpolation between neighbouring
    prototypes) + re-ranking by cos(y, K_i).
  - RANDOM arm: uniform-at-random top-k over concept indices; chance ceiling.

HP bands (see pre-reg preregs/2026-07-03_substrate_concept_encoder_component_C_
modern_hopfield_readout.md):
  HP1 rescue lift : HOPFIELD_r5 > COSINE_r5 + 0.10
  HP2 beats bag   : HOPFIELD_r5 >= TRIGRAM_r5 + 0.05
  HP3 baseline    : COSINE_r5 within +/-0.03 of prior MEASURED 0.16
  HP4 chance      : RANDOM_r5 <= 0.10
  HF1 no lift     : HOPFIELD_r5 <= COSINE_r5 + 0.03
  HF2 no bag beat : HOPFIELD_r5 < TRIGRAM_r5
  MB              : COSINE + 0.05 < HOPFIELD <= COSINE + 0.10 (partial rescue)

CELL-TEMPLATE MANDATORY:
  - arms_differ_verified at smoke gate (hash of per-arm top-k index arrays)
  - final_metrics_atomicity: tmp_replace via os.replace
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: no quantitative CRLB (supervised retrieval; chance floor k/N)
  - baseline_in_band at smoke (0.05 < COSINE_r5 < 0.80 AND 0.05 < TRIGRAM_r5 < 0.80)
  - discriminator: HOPFIELD_r5 - COSINE_r5 (rescue lift) at smoke; must be
    non-degenerate (i.e. not literally zero) for smoke sign-off
  - HP_SCOPE: HP1/HP2 on HOPFIELD arms; HP3 on COSINE arm; HP4 on RANDOM arm

Compute arch: sequential CPU numpy. Storage strategy: sharded per-atom
  concept HD (same as prior baseline; reuses existing ConceptEncoder). Depth L=1.
Progress logging: print_flush_true.

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

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from hdlab.concept_encoder import ConceptEncoder  # noqa: E402
from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: E402
from hdlab.modern_hopfield_readout import ModernHopfieldReadout  # noqa: E402
from experiments._seed_checkpoint import get_output_dir  # noqa: E402
from experiments._cell_heartbeat import CellHeartbeat  # noqa: E402

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------

ANCHOR_NAME = "substrate_concept_encoder_component_C_modern_hopfield_readout_2026_07_03"

CORPUS_ATOMS_JSONL = _REPO / "data" / "substrate_index" / "concept" / "atoms.jsonl"

SMOKE_N_ATOMS = 100
SMOKE_SEEDS = [11, 17, 23]
FULL_N_ATOMS = 500
FULL_SEEDS = [11, 17, 23]

N_DIM = 2048
K_SPARSITY = 0.02
MAX_POS = 24

# Modern-Hopfield betas.
HOPFIELD_BETA_DEFAULT = 4.0
HOPFIELD_BETA_HIGH = 8.0

MIN_DEFINITION_LEN = 20
MIN_SYNONYMS = 3

# HP bands.
HP1_RESCUE_LIFT = 0.10           # HOPFIELD > COSINE + 0.10
HP2_BEATS_BAG = 0.05             # HOPFIELD >= TRIGRAM + 0.05
HP3_COSINE_MEASURED = 0.16       # MEASURED@data/exp_substrate_concept_encoder_substrate_content_v1_2026_07_02/metrics.json:aggregate.arm_concept_encoder_recall_at_5_mean
HP3_COSINE_TOL = 0.03            # +/- band for baseline recovery
HP4_RANDOM_CEILING = 0.10        # chance @ N=100, k=5 -> 0.05; band <= 0.10
HF1_NO_LIFT_GAP = 0.03           # HOPFIELD <= COSINE + 0.03 = degenerate
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
# Corpus loading (borrowed / kept identical to substrate_content_v1).
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
# Readout helpers.
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


# ---------------------------------------------------------------------------
# Arm eval logic.
# ---------------------------------------------------------------------------

def _fit_concept_encoder(
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
    """Run 5 arms at one seed. All arms share the same fitted ConceptEncoder
    for arms 1-3; only the READOUT differs between COSINE and the two HOPFIELD
    arms. Arms 4 and 5 (trigram, random) are independent baselines.
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

    # Fit ConceptEncoder once; used by all 3 substrate-content arms.
    t_arm = time.perf_counter()
    enc = _fit_concept_encoder(
        training_sentences, training_labels, n_atoms, n_dim, seed
    )
    concept_hds = enc.concept_hds.astype(np.int8)  # [n_atoms, n_dim] sparse-bipolar
    fit_wall = time.perf_counter() - t_arm
    print(f"[seed={seed}] ConceptEncoder fit wall={fit_wall:.1f}s", flush=True)

    # Precompute per-query surface encoding via ConceptEncoder's surface path.
    surf_queries = np.stack(
        [
            enc._surface_encoder.encode_sentence(str(qw))  # noqa: SLF001
            for _, qw in queries
        ],
        axis=0,
    ).astype(np.float32)  # [n_queries, n_dim]

    n_q = surf_queries.shape[0]

    # --- ARM 1: COSINE (baseline) ---
    correct_cos = {int(k): 0 for k in k_values}
    topk_cos_stack = np.zeros((n_q, topk_max), dtype=np.int32)
    t_arm = time.perf_counter()
    for qi in range(n_q):
        atom_idx = int(queries[qi][0])
        order = _cosine_argmax_topk(
            surf_queries[qi], concept_hds, topk_max
        )
        topk_cos_stack[qi] = order.astype(np.int32)
        for k in k_values:
            if atom_idx in order[: int(k)].tolist():
                correct_cos[int(k)] += 1
    arm1 = _eval_recall_topk(n_q, correct_cos, k_values)
    arm1_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_COSINE] r@1={arm1['recall_at_1']:.4f} "
        f"r@5={arm1['recall_at_5']:.4f} r@10={arm1['recall_at_10']:.4f} "
        f"wall={arm1_wall:.1f}s",
        flush=True,
    )
    hb.tick(unit_idx=2, extra={"phase": "cosine_done", "seed": seed}, force=True)

    # --- ARM 2: MODERN-HOPFIELD default beta ---
    hop_lo = ModernHopfieldReadout(
        beta=HOPFIELD_BETA_DEFAULT, normalize_query_and_store=True
    )
    correct_hop_lo = {int(k): 0 for k in k_values}
    topk_hop_lo_stack = np.zeros((n_q, topk_max), dtype=np.int32)
    t_arm = time.perf_counter()
    for qi in range(n_q):
        atom_idx = int(queries[qi][0])
        top, _y, _w = hop_lo.top_k_by_retrieved(
            surf_queries[qi], concept_hds, k=topk_max
        )
        topk_hop_lo_stack[qi] = top.astype(np.int32)
        for k in k_values:
            if atom_idx in top[: int(k)].tolist():
                correct_hop_lo[int(k)] += 1
    arm2 = _eval_recall_topk(n_q, correct_hop_lo, k_values)
    arm2_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_HOPFIELD_beta={HOPFIELD_BETA_DEFAULT}] "
        f"r@1={arm2['recall_at_1']:.4f} r@5={arm2['recall_at_5']:.4f} "
        f"r@10={arm2['recall_at_10']:.4f} wall={arm2_wall:.1f}s",
        flush=True,
    )
    hb.tick(unit_idx=3, extra={"phase": "hop_lo_done", "seed": seed}, force=True)

    # --- ARM 3: MODERN-HOPFIELD high beta ---
    hop_hi = ModernHopfieldReadout(
        beta=HOPFIELD_BETA_HIGH, normalize_query_and_store=True
    )
    correct_hop_hi = {int(k): 0 for k in k_values}
    topk_hop_hi_stack = np.zeros((n_q, topk_max), dtype=np.int32)
    t_arm = time.perf_counter()
    for qi in range(n_q):
        atom_idx = int(queries[qi][0])
        top, _y, _w = hop_hi.top_k_by_retrieved(
            surf_queries[qi], concept_hds, k=topk_max
        )
        topk_hop_hi_stack[qi] = top.astype(np.int32)
        for k in k_values:
            if atom_idx in top[: int(k)].tolist():
                correct_hop_hi[int(k)] += 1
    arm3 = _eval_recall_topk(n_q, correct_hop_hi, k_values)
    arm3_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_HOPFIELD_beta={HOPFIELD_BETA_HIGH}] "
        f"r@1={arm3['recall_at_1']:.4f} r@5={arm3['recall_at_5']:.4f} "
        f"r@10={arm3['recall_at_10']:.4f} wall={arm3_wall:.1f}s",
        flush=True,
    )
    hb.tick(unit_idx=4, extra={"phase": "hop_hi_done", "seed": seed}, force=True)

    # --- ARM 4: CHAR-TRIGRAM UNSUP REFERENCE (bag-word baseline) ---
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
    arm4 = _eval_recall_topk(n_q, correct_tri, k_values)
    arm4_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_CHAR_TRIGRAM] r@1={arm4['recall_at_1']:.4f} "
        f"r@5={arm4['recall_at_5']:.4f} r@10={arm4['recall_at_10']:.4f} "
        f"wall={arm4_wall:.1f}s",
        flush=True,
    )
    hb.tick(unit_idx=5, extra={"phase": "trigram_done", "seed": seed}, force=True)

    # --- ARM 5: RANDOM BASELINE (chance) ---
    t_arm = time.perf_counter()
    rng_arm5 = np.random.default_rng(seed + 1000)
    correct_rnd = {int(k): 0 for k in k_values}
    topk_rnd_stack = np.zeros((n_q, topk_max), dtype=np.int32)
    for qi in range(n_q):
        atom_idx = int(queries[qi][0])
        perm = rng_arm5.permutation(n_atoms)
        top = perm[:topk_max]
        topk_rnd_stack[qi] = top.astype(np.int32)
        for k in k_values:
            if atom_idx in top[: int(k)].tolist():
                correct_rnd[int(k)] += 1
    arm5 = _eval_recall_topk(n_q, correct_rnd, k_values)
    arm5_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_RANDOM] r@1={arm5['recall_at_1']:.4f} "
        f"r@5={arm5['recall_at_5']:.4f} r@10={arm5['recall_at_10']:.4f} "
        f"wall={arm5_wall:.1f}s",
        flush=True,
    )
    hb.tick(unit_idx=6, extra={"phase": "random_done", "seed": seed}, force=True)

    # ARMS-DIFFER hash check on per-arm top-k index stacks.
    hashes = {
        "ARM_V1_CONCEPT_ENCODER_COSINE": _hash_topk_array(topk_cos_stack),
        "ARM_V1_CONCEPT_ENCODER_MODERN_HOPFIELD": _hash_topk_array(
            topk_hop_lo_stack
        ),
        "ARM_V1_CONCEPT_ENCODER_MODERN_HOPFIELD_HIGH_BETA": _hash_topk_array(
            topk_hop_hi_stack
        ),
        "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE": _hash_topk_array(topk_tri_stack),
        "ARM_RANDOM_BASELINE": _hash_topk_array(topk_rnd_stack),
    }
    unique_hashes = set(hashes.values())
    arms_differ_verified = len(unique_hashes) == 5

    return {
        "seed": int(seed),
        "n_atoms": int(n_atoms),
        "n_dim": int(n_dim),
        "n_train_sentences": int(len(training_sentences)),
        "n_queries": int(n_q),
        "arm_v1_concept_encoder_cosine": arm1,
        "arm_v1_concept_encoder_modern_hopfield": arm2,
        "arm_v1_concept_encoder_modern_hopfield_high_beta": arm3,
        "arm_char_trigram_unsup_reference": arm4,
        "arm_random_baseline": arm5,
        "arm_walls_s": {
            "cosine": round(arm1_wall, 3),
            "hopfield_beta_default": round(arm2_wall, 3),
            "hopfield_beta_high": round(arm3_wall, 3),
            "trigram": round(arm4_wall, 3),
            "random": round(arm5_wall, 3),
            "concept_encoder_fit": round(fit_wall, 3),
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

    arms = [
        "arm_v1_concept_encoder_cosine",
        "arm_v1_concept_encoder_modern_hopfield",
        "arm_v1_concept_encoder_modern_hopfield_high_beta",
        "arm_char_trigram_unsup_reference",
        "arm_random_baseline",
    ]
    agg: Dict[str, Any] = {}
    for a in arms:
        for k in (1, 5, 10):
            agg[f"{a}_recall_at_{k}_mean"] = _arm(a, k)
    return agg


def _compute_verdict(
    agg: Dict[str, Any], per_seed: Sequence[Dict[str, Any]]
) -> Tuple[str, str]:
    """Priority:
      HF_ARMS_IDENTICAL (structural bug) -> HARD_FAIL
      HF2 no bag beat (HOPFIELD_r5 < TRIGRAM_r5)  -> HARD_FAIL
      HF1 no lift (HOPFIELD - COSINE <= 0.03) AND not HP1 -> HARD_FAIL
      HP1 + HP2 + HP3 + HP4 -> HARD_PASS
      Else MIDDLE_BAND with which HP gates cleared.
    """
    cos5 = agg["arm_v1_concept_encoder_cosine_recall_at_5_mean"]
    hop5_lo = agg["arm_v1_concept_encoder_modern_hopfield_recall_at_5_mean"]
    hop5_hi = agg[
        "arm_v1_concept_encoder_modern_hopfield_high_beta_recall_at_5_mean"
    ]
    hop5 = max(hop5_lo, hop5_hi)  # best HOPFIELD variant
    tri5 = agg["arm_char_trigram_unsup_reference_recall_at_5_mean"]
    rnd5 = agg["arm_random_baseline_recall_at_5_mean"]

    all_arms_differ = all(bool(s.get("arms_differ_verified")) for s in per_seed)

    if not all_arms_differ:
        return (
            "HARD_FAIL",
            "HF_ARMS_IDENTICAL: at least one seed has arms_differ_verified=False; "
            "top-k index stacks hash-collide (readout bug or degenerate corpus).",
        )
    # HF2 (major reframe if HOPFIELD can't beat bag)
    if hop5 < tri5:
        return (
            "HARD_FAIL",
            f"HF2_NO_BAG_BEAT: best HOPFIELD r5={hop5:.4f} < TRIGRAM r5={tri5:.4f} "
            f"(HOPFIELD_lo={hop5_lo:.4f} HOPFIELD_hi={hop5_hi:.4f} "
            f"COSINE={cos5:.4f}); readout geometry didn't reach bag-word floor.",
        )
    # HF1 (no lift at all)
    lift = hop5 - cos5
    if lift <= HF1_NO_LIFT_GAP:
        return (
            "HARD_FAIL",
            f"HF1_NO_LIFT: HOPFIELD - COSINE = {lift:.4f} <= "
            f"{HF1_NO_LIFT_GAP:.2f}; readout geometry didn't matter under "
            f"equal-norm sparse-bipolar storage (HOPFIELD={hop5:.4f} "
            f"COSINE={cos5:.4f}).",
        )
    # HP band assessment (on best HOPFIELD variant).
    hp1 = lift > HP1_RESCUE_LIFT
    hp2 = hop5 >= tri5 + HP2_BEATS_BAG
    hp3 = abs(cos5 - HP3_COSINE_MEASURED) <= HP3_COSINE_TOL
    hp4 = rnd5 <= HP4_RANDOM_CEILING

    if hp1 and hp2 and hp3 and hp4:
        return (
            "HARD_PASS",
            f"HARD_PASS: HOPFIELD_r5={hop5:.4f} (lift={lift:.4f}) COSINE={cos5:.4f} "
            f"TRIGRAM={tri5:.4f} RANDOM={rnd5:.4f}; HP1+HP2+HP3+HP4 all met; "
            f"softmax retrieval RESCUES existing encoder (single load-bearing lever).",
        )
    cleared = []
    missed = []
    for name, ok in [("HP1", hp1), ("HP2", hp2), ("HP3", hp3), ("HP4", hp4)]:
        (cleared if ok else missed).append(name)
    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: HOPFIELD_r5={hop5:.4f} (lift={lift:.4f}) "
        f"COSINE={cos5:.4f} TRIGRAM={tri5:.4f} RANDOM={rnd5:.4f}; "
        f"cleared={cleared} missed={missed}; "
        f"HOPFIELD_lo={hop5_lo:.4f} HOPFIELD_hi={hop5_hi:.4f} "
        f"(partial rescue; may need A+B composition).",
    )


# ---------------------------------------------------------------------------
# Main driver.
# ---------------------------------------------------------------------------

def _run_mode_dispatch(run_mode: str) -> Tuple[List[int], int, int]:
    """Return (seeds, n_atoms, expected_units).  expected_units = seeds * 5 arms."""
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
            "hopfield_beta_default": float(HOPFIELD_BETA_DEFAULT),
            "hopfield_beta_high": float(HOPFIELD_BETA_HIGH),
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
                "HP1_rescue_lift": HP1_RESCUE_LIFT,
                "HP2_beats_bag": HP2_BEATS_BAG,
                "HP3_cosine_measured": HP3_COSINE_MEASURED,
                "HP3_cosine_tol": HP3_COSINE_TOL,
                "HP4_random_ceiling": HP4_RANDOM_CEILING,
                "HF1_no_lift_gap": HF1_NO_LIFT_GAP,
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
        "storage_strategy": "sharded_per_atom_concept_hds_reused_from_ConceptEncoder",
        "compute_arch": "sequential_cpu_numpy",
        "baseline_probe_notes": baseline_probe_notes,
        "prereg_path": (
            "preregs/2026-07-03_substrate_concept_encoder_component_C_"
            "modern_hopfield_readout.md"
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
            "ARM_V1_CONCEPT_ENCODER_COSINE": ["HP3"],
            "ARM_V1_CONCEPT_ENCODER_MODERN_HOPFIELD": ["HP1", "HP2"],
            "ARM_V1_CONCEPT_ENCODER_MODERN_HOPFIELD_HIGH_BETA": ["HP1", "HP2"],
            "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE": ["HP2_ref"],
            "ARM_RANDOM_BASELINE": ["HP4"],
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
    print(f"[selftest] loading {CORPUS_ATOMS_JSONL}", flush=True)
    atoms = _load_wordnet_atoms(max_atoms=20)
    print(
        f"[selftest] loaded {len(atoms)} WordNet atoms; running 1-seed 5-arm eval",
        flush=True,
    )
    with CellHeartbeat(str(output_dir), total_units=5, interval_s=10) as hb:
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
        verdict=("SELFTEST_PASS" if per["arms_differ_verified"] else "SELFTEST_FAIL"),
        verdict_msg=(
            f"SELFTEST: arms_differ={per['arms_differ_verified']} "
            f"cos_r5={agg['arm_v1_concept_encoder_cosine_recall_at_5_mean']:.3f} "
            f"hop_r5={agg['arm_v1_concept_encoder_modern_hopfield_recall_at_5_mean']:.3f} "
            f"tri_r5={agg['arm_char_trigram_unsup_reference_recall_at_5_mean']:.3f} "
            f"rnd_r5={agg['arm_random_baseline_recall_at_5_mean']:.3f} "
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

    cos5 = agg["arm_v1_concept_encoder_cosine_recall_at_5_mean"]
    tri5 = agg["arm_char_trigram_unsup_reference_recall_at_5_mean"]
    hop5 = max(
        agg["arm_v1_concept_encoder_modern_hopfield_recall_at_5_mean"],
        agg[
            "arm_v1_concept_encoder_modern_hopfield_high_beta_recall_at_5_mean"
        ],
    )
    baseline_in_band = (
        BASELINE_IN_BAND_LO <= cos5 <= BASELINE_IN_BAND_HI
        and BASELINE_IN_BAND_LO <= tri5 <= BASELINE_IN_BAND_HI
    )
    lift = hop5 - cos5
    # Discriminator = "is HOPFIELD - COSINE non-degenerate?"; non-zero required.
    discriminator_fires = abs(lift) > 1e-6

    baseline_probe_notes = (
        f"baseline_in_band={baseline_in_band} cos_r5={cos5:.4f} "
        f"tri_r5={tri5:.4f} hop_r5={hop5:.4f} lift_hop_minus_cos={lift:.4f} "
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
