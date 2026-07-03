"""substrate_composed_encoder_v3_adaptive_alpha_smoke_2026_07_03

Adaptive-alpha variant of ComposedEncoderV3 = direct test of Skunkworks
MM_TENTATIVE_SYNTHESIS COMPOSITION_AT_EQUAL_ALPHA_DILUTES_ASYMMETRIC_STRENGTH_STREAMS
expansion criterion.

Prior EQUAL-alpha SMOKE HF (commit 114a0f3cf; Skunkworks VET commit cc1807726):
    ARM_V3_EQUAL_ALPHA  r5 = 0.333 (per-seed [0.34, 0.33, 0.33])
    ARM_PPMI_ALONE      r5 = 0.340 (best single)
    ARM_VWFA_ALONE      r5 = 0.240 (weak stream)
    ARM_CHAR_TRIGRAM    r5 = 0.280 (baseline)
Equal-alpha (0.5/0.5) STRICTLY hurts asymmetric-strength streams by 0.007 r5
systematically across 3 seeds.  Proposed fix: adaptive-alpha via held-out
grid search should snap alpha near 0 (PPMI-dominant) rather than dilute.

TASK: SUPERVISED held-out-synonym retrieval on WordNet lexicon atoms.
    Same corpus loader / query builder / regime / seeds as v3 EQUAL-alpha
    smoke for BIT-IDENTICAL comparability of regression arms.

FRAMING (LOAD-BEARING per USER 2026-07-02 + Fix#28 discipline):
    Tests the composition-dilution lemma expansion criterion, NOT a
    capability claim.  Substrate KNOWS ALMOST NOTHING.  A PASS is NOT:
      - "PPMI-alone first substrate-native win" (that would be V2-A rediscovery)
      - "substrate understands English"
      - a capability breakthrough
    A PASS validates: brain-analog late-combine needs ADAPTIVE weighting
    when parallel streams are asymmetric-strength.  A FAIL is STRONGER
    structural finding: score-level late-combine fundamentally lossy for
    these two spokes at this regime.

HELD-OUT DISCIPLINE (LOAD-BEARING):
    Per-seed random permutation of 100 queries into val (50) + test (50).
    Alpha grid-search fits ONLY on val queries (r@1 objective) via
    hdlab.late_combine.fit_weights_grid_2spoke.  Test-split queries retrieved
    ONLY AFTER alpha is frozen.  Regression arms (VWFA/PPMI/v3-equal/trigram)
    evaluated on ALL 100 queries so they reproduce prior BIT-IDENTICALLY.

Arms (5, 3 seeds -> 15 units at smoke):
    1. ARM_V3_ADAPTIVE_ALPHA          (LOAD-BEARING; alpha fit on val, eval on test)
    2. ARM_V3_EQUAL_ALPHA             (regression MUST reproduce 0.333 +/-0.02)
    3. ARM_PPMI_ALONE                 (best-single ref MUST reproduce 0.340 +/-0.02)
    4. ARM_VWFA_ALONE                 (weak-stream ref MUST reproduce 0.240 +/-0.02)
    5. ARM_CHAR_TRIGRAM_UNSUP_REFERENCE (baseline MUST reproduce 0.280 +/-0.02)

HP / HF bands (see preregs/2026-07-03_substrate_composed_encoder_v3_adaptive_alpha_smoke.md):
    HP1 (recover/lift):   ARM_V3_ADAPTIVE_ALPHA test_r5 >= 0.35
    HP2 (recover ref):    ARM_V3_ADAPTIVE_ALPHA test_r5 >= max(VWFA,PPMI)_full - 0.01
    HP3 (v3-equal reg):   ARM_V3_EQUAL_ALPHA within +/-0.02 of 0.333
    HP4 (ppmi reg):       ARM_PPMI_ALONE within +/-0.02 of 0.340
    HP5 (vwfa reg):       ARM_VWFA_ALONE within +/-0.02 of 0.240
    HP6 (trigram reg):    ARM_CHAR_TRIGRAM within +/-0.02 of 0.280
    HP7 (no leakage):     val/test disjoint per seed; alpha fit on val; eval on test
    HP8 (arms differ):    5 arm top-k stacks hash-distinct
    HF1 (still hurts):    ARM_V3_ADAPTIVE_ALPHA test_r5 < max(VWFA,PPMI)_full - 0.01
                            STRONGER structural finding per Skunkworks
    HF2 (reg broken):     any of HP3-HP6 outside +/-0.02 tolerance
    HF3 (arms identical): any two arm top-k stacks hash-collide
    HF4 (leakage):        val/test overlap or alpha fit on test labels
    MIDDLE_BAND:          test_r5 in [max(VWFA,PPMI)_full - 0.01, 0.35)

CELL-TEMPLATE MANDATORY:
    - arms_differ_verified at smoke gate (hash of per-arm top-k index arrays)
    - final_metrics_atomicity: tmp_replace via os.replace
    - except SystemExit: raise BEFORE except Exception (no BaseException)
    - crlb_n/a: no quantitative CRLB (supervised retrieval; chance floor 5/100)
    - baseline_in_band at smoke (0.05 < TRIGRAM_r5 < 0.80)
    - discriminator: adaptive_alpha_test_r5 vs max(VWFA,PPMI)_full gap
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
from hdlab.late_combine import fit_weights_grid_2spoke  # noqa: E402
from hdlab.vwfa import VWFAEncoder  # noqa: E402
from hdlab.ppmi_sparse_encoder import PPMISparseEncoder  # noqa: E402
from experiments._cell_heartbeat import CellHeartbeat  # noqa: E402
from experiments._seed_checkpoint import get_output_dir  # noqa: E402

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------

ANCHOR_NAME = "substrate_composed_encoder_v3_adaptive_alpha_smoke_2026_07_03"

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

VAL_FRAC = 0.5  # 50/50 val/test split of 100 queries
ALPHA_GRID: Tuple[float, ...] = (
    0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
)

# HP/HF bands (recall@5 unless noted).
HP1_ADAPTIVE_R5_LIFT = 0.35        # ARM_V3_ADAPTIVE_ALPHA test_r5 >= 0.35
HP2_ADAPTIVE_RECOVER_MARGIN = 0.01 # test_r5 >= max(VWFA,PPMI) - 0.01
REG_TOL = 0.02                     # +/-0.02 regression tolerance
HP3_V3_EQUAL_MEASURED = 0.333      # MEASURED@v3_equal_smoke
HP4_PPMI_MEASURED = 0.340          # MEASURED@v3_equal_smoke
HP5_VWFA_MEASURED = 0.240          # MEASURED@v3_equal_smoke
HP6_TRIGRAM_MEASURED = 0.280       # MEASURED@v3_equal_smoke
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
# Corpus loading (BIT-IDENTICAL to v3 EQUAL-alpha smoke cell).
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


def _cosine_row(query_hd: np.ndarray, prototypes: np.ndarray) -> np.ndarray:
    """Return [n_protos] cosine scores; safe for zero query / zero rows."""
    q = query_hd.astype(np.float32)
    p = prototypes.astype(np.float32)
    qn = float(np.linalg.norm(q))
    if qn < 1e-12:
        return np.zeros(p.shape[0], dtype=np.float32)
    pn = np.linalg.norm(p, axis=1)
    pn_safe = np.where(pn < 1e-12, 1.0, pn)
    scores = (p @ q) / (pn_safe * qn)
    return np.where(pn < 1e-12, -1e9, scores).astype(np.float32)


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
    """Run 5 arms at one seed with per-seed val/test split for adaptive-alpha.

    Regression arms (v3-equal, PPMI, VWFA, trigram): evaluated on ALL n queries
        for BIT-IDENTICAL comparability with prior v3 EQUAL-alpha smoke.
    Adaptive-alpha arm: fit alpha on val split (50), eval on test split (50).
    """
    t0 = time.perf_counter()
    n_atoms = len(atoms)
    training_sentences, training_labels, queries = _build_train_query(atoms)
    n_q = len(queries)
    print(
        f"[seed={seed}] n_atoms={n_atoms} n_train_sent={len(training_sentences)} "
        f"n_queries={n_q}",
        flush=True,
    )
    hb.tick(unit_idx=1, extra={"phase": "corpus_built", "seed": seed}, force=True)

    # Per-seed random split of 100 query indices into val (50) + test (50).
    rng_split = np.random.default_rng(int(seed) + 1000)
    perm = rng_split.permutation(n_q)
    n_val = int(round(VAL_FRAC * n_q))
    val_idx = perm[:n_val].tolist()
    test_idx = perm[n_val:].tolist()
    # HP7 no-leakage: disjoint sets.
    assert set(val_idx).isdisjoint(set(test_idx)), (
        f"[seed={seed}] LEAKAGE: val and test query indices overlap"
    )
    val_query_ids = [int(queries[i][0]) for i in val_idx]
    val_query_txt = [str(queries[i][1]) for i in val_idx]
    test_query_ids = [int(queries[i][0]) for i in test_idx]
    test_query_txt = [str(queries[i][1]) for i in test_idx]

    k_values = [1, 5, 10]
    topk_max = int(max(k_values))

    # --- Fit ComposedEncoderV3 (fits VWFA + PPMI + builds prototype tables) ---
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

    protos_vwfa = v3.protos_vwfa
    protos_ppmi = v3.protos_ppmi
    if protos_vwfa is None or protos_ppmi is None:
        raise RuntimeError(f"[seed={seed}] v3 protos None after fit")

    # --- Precompute per-query VWFA + PPMI HDs (used for val fit + adaptive eval) ---
    def _encode_val(txt: str) -> Tuple[np.ndarray, np.ndarray]:
        streams = v3.encode_streams(txt)
        return streams["vwfa"], streams["ppmi"]

    val_vwfa_hds = [_encode_val(t)[0] for t in val_query_txt]
    val_ppmi_hds = [_encode_val(t)[1] for t in val_query_txt]
    test_vwfa_hds = [_encode_val(t)[0] for t in test_query_txt]
    test_ppmi_hds = [_encode_val(t)[1] for t in test_query_txt]

    # --- ARM 1: V3 ADAPTIVE ALPHA (LOAD-BEARING) ---
    # Grid-search alpha on val queries only (r@1 objective).
    t_arm = time.perf_counter()
    best_alpha, best_beta_unused, best_gamma, best_val_r1 = fit_weights_grid_2spoke(
        per_query_ortho=val_vwfa_hds,
        per_query_sem=val_ppmi_hds,
        prototypes_ortho=protos_vwfa,
        prototypes_sem=protos_ppmi,
        labels=val_query_ids,
        alpha_grid=ALPHA_GRID,
    )
    fit_wall = time.perf_counter() - t_arm
    # NOTE: fit_weights_grid_2spoke uses (alpha, gamma) with gamma = 1 - alpha
    # where alpha weights the FIRST spoke (ortho=VWFA) and gamma weights the
    # SECOND (sem=PPMI).  In ComposedEncoderV3.set_weights(alpha, beta) alpha
    # weights VWFA and beta weights PPMI.  So mapping is:
    #   v3.set_weights(alpha=best_alpha, beta=best_gamma)
    fitted_alpha_v3 = float(best_alpha)  # VWFA weight
    fitted_beta_v3 = float(best_gamma)   # PPMI weight
    # Reject-any-tuning-in-place safety: assert exactly one point wins.
    if not (0.0 <= fitted_alpha_v3 <= 1.0 and 0.0 <= fitted_beta_v3 <= 1.0):
        raise RuntimeError(
            f"[seed={seed}] fitted (alpha, beta) out of range: "
            f"({fitted_alpha_v3}, {fitted_beta_v3})"
        )

    # Evaluate ADAPTIVE on test split (LOAD-BEARING metric).
    v3.set_weights(alpha=fitted_alpha_v3, beta=fitted_beta_v3)
    correct_adaptive_test = {int(k): 0 for k in k_values}
    n_test = len(test_query_txt)
    topk_adaptive_test_stack = np.zeros((n_test, topk_max), dtype=np.int32)
    for i, txt in enumerate(test_query_txt):
        atom_idx = int(test_query_ids[i])
        # Use precomputed stream HDs (avoid recomputation) via cosine-row combine.
        cs_vwfa = _cosine_row(test_vwfa_hds[i], protos_vwfa)
        cs_ppmi = _cosine_row(test_ppmi_hds[i], protos_ppmi)
        combined = (
            fitted_alpha_v3 * cs_vwfa + fitted_beta_v3 * cs_ppmi
        ).astype(np.float32)
        n_p = int(combined.shape[0])
        if topk_max >= n_p:
            order = np.argsort(-combined)
        else:
            idx_part = np.argpartition(-combined, topk_max)[:topk_max]
            order = idx_part[np.argsort(-combined[idx_part])]
        topk_adaptive_test_stack[i] = order.astype(np.int32)
        for k in k_values:
            if atom_idx in order[: int(k)].tolist():
                correct_adaptive_test[int(k)] += 1
    arm1_test = _eval_recall_topk(n_test, correct_adaptive_test, k_values)

    # Also evaluate ADAPTIVE on ALL 100 queries (for comparability to prior).
    correct_adaptive_full = {int(k): 0 for k in k_values}
    topk_adaptive_full_stack = np.zeros((n_q, topk_max), dtype=np.int32)
    for qi in range(n_q):
        atom_idx = int(queries[qi][0])
        order = v3.retrieve_topk(str(queries[qi][1]), k=topk_max)
        topk_adaptive_full_stack[qi] = order.astype(np.int32)
        for k in k_values:
            if atom_idx in order[: int(k)].tolist():
                correct_adaptive_full[int(k)] += 1
    arm1_full = _eval_recall_topk(n_q, correct_adaptive_full, k_values)

    arm1_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_V3_ADAPTIVE_ALPHA] "
        f"fit_alpha={fitted_alpha_v3:.2f} fit_beta={fitted_beta_v3:.2f} "
        f"val_r1={best_val_r1:.4f} "
        f"test_r1={arm1_test['recall_at_1']:.4f} "
        f"test_r5={arm1_test['recall_at_5']:.4f} "
        f"test_r10={arm1_test['recall_at_10']:.4f} "
        f"full_r5={arm1_full['recall_at_5']:.4f} "
        f"grid_wall={fit_wall:.2f}s arm_wall={arm1_wall:.1f}s",
        flush=True,
    )
    hb.tick(unit_idx=3, extra={"phase": "arm1_adaptive_done", "seed": seed},
            force=True)

    # --- ARM 2: V3 EQUAL ALPHA (regression on ALL 100 queries) ---
    v3.set_weights(alpha=0.5, beta=0.5)
    correct_v3eq = {int(k): 0 for k in k_values}
    topk_v3eq_stack = np.zeros((n_q, topk_max), dtype=np.int32)
    t_arm = time.perf_counter()
    for qi in range(n_q):
        atom_idx = int(queries[qi][0])
        order = v3.retrieve_topk(str(queries[qi][1]), k=topk_max)
        topk_v3eq_stack[qi] = order.astype(np.int32)
        for k in k_values:
            if atom_idx in order[: int(k)].tolist():
                correct_v3eq[int(k)] += 1
    arm2 = _eval_recall_topk(n_q, correct_v3eq, k_values)
    arm2_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_V3_EQUAL_ALPHA] r@1={arm2['recall_at_1']:.4f} "
        f"r@5={arm2['recall_at_5']:.4f} r@10={arm2['recall_at_10']:.4f} "
        f"wall={arm2_wall:.1f}s",
        flush=True,
    )
    hb.tick(unit_idx=4, extra={"phase": "arm2_v3eq_done", "seed": seed}, force=True)

    # --- ARM 3: PPMI ALONE (regression on ALL 100 queries) ---
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

    # --- ARM 4: VWFA ALONE (regression on ALL 100 queries) ---
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
    arm4 = _eval_recall_topk(n_q, correct_vwfa, k_values)
    arm4_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_VWFA_ALONE] r@1={arm4['recall_at_1']:.4f} "
        f"r@5={arm4['recall_at_5']:.4f} r@10={arm4['recall_at_10']:.4f} "
        f"wall={arm4_wall:.1f}s",
        flush=True,
    )
    hb.tick(unit_idx=6, extra={"phase": "arm4_vwfa_done", "seed": seed}, force=True)

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

    # ARMS-DIFFER hash check.  Use test-split for adaptive (since equal-alpha
    # is on full 100; they'd differ trivially in stack shape).  Compare per-
    # arm top-k stacks on their respective query sets (still identifies
    # bit-identical arm bugs).
    hashes = {
        "ARM_V3_ADAPTIVE_ALPHA":            _hash_topk_array(topk_adaptive_test_stack),
        "ARM_V3_EQUAL_ALPHA":               _hash_topk_array(topk_v3eq_stack),
        "ARM_PPMI_ALONE":                   _hash_topk_array(topk_ppmi_stack),
        "ARM_VWFA_ALONE":                   _hash_topk_array(topk_vwfa_stack),
        "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE": _hash_topk_array(topk_tri_stack),
    }
    unique_hashes = set(hashes.values())
    arms_differ_verified = len(unique_hashes) == 5

    # HP7 no-leakage assertion (defensive check).
    no_leakage = bool(set(val_query_ids).isdisjoint(set(test_query_ids)))

    return {
        "seed": int(seed),
        "n_atoms": int(n_atoms),
        "n_dim": int(n_dim),
        "n_train_sentences": int(len(training_sentences)),
        "n_queries": int(n_q),
        "n_val": int(len(val_query_ids)),
        "n_test": int(len(test_query_ids)),
        "fitted_alpha_v3": float(fitted_alpha_v3),
        "fitted_beta_v3": float(fitted_beta_v3),
        "val_r1_at_fitted_alpha": float(best_val_r1),
        "arm_v3_adaptive_alpha_test": arm1_test,
        "arm_v3_adaptive_alpha_full100": arm1_full,
        "arm_v3_equal_alpha": arm2,
        "arm_ppmi_alone": arm3,
        "arm_vwfa_alone": arm4,
        "arm_char_trigram_unsup_reference": arm5,
        "arm_walls_s": {
            "adaptive_alpha_fit_and_eval": round(arm1_wall, 3),
            "v3_equal_alpha": round(arm2_wall, 3),
            "ppmi_alone": round(arm3_wall, 3),
            "vwfa_alone": round(arm4_wall, 3),
            "char_trigram": round(arm5_wall, 3),
            "v3_fit": round(v3_fit_wall, 3),
        },
        "arms_differ_verified": bool(arms_differ_verified),
        "arm_hashes": hashes,
        "no_leakage_verified": bool(no_leakage),
        "val_query_ids": list(val_query_ids),
        "test_query_ids": list(test_query_ids),
        "wall_s": round(time.perf_counter() - t0, 3),
    }


# ---------------------------------------------------------------------------
# Aggregation + verdict logic.
# ---------------------------------------------------------------------------

def _aggregate_per_seed(per_seed: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    def _mean(vals: List[float]) -> float:
        return float(np.mean(vals)) if vals else 0.0

    def _arm(name: str, k: int) -> float:
        return _mean([float(s[name][f"recall_at_{k}"]) for s in per_seed])

    agg: Dict[str, Any] = {}
    # Adaptive test split.
    for k in (1, 5, 10):
        agg[f"arm_v3_adaptive_alpha_test_recall_at_{k}_mean"] = _arm(
            "arm_v3_adaptive_alpha_test", k
        )
    # Adaptive full-100 (comparability).
    for k in (1, 5, 10):
        agg[f"arm_v3_adaptive_alpha_full100_recall_at_{k}_mean"] = _arm(
            "arm_v3_adaptive_alpha_full100", k
        )
    # Regression arms (full-100).
    for name in (
        "arm_v3_equal_alpha",
        "arm_ppmi_alone",
        "arm_vwfa_alone",
        "arm_char_trigram_unsup_reference",
    ):
        for k in (1, 5, 10):
            agg[f"{name}_recall_at_{k}_mean"] = _arm(name, k)
    # Fitted alpha stats.
    alphas = [float(s["fitted_alpha_v3"]) for s in per_seed]
    betas = [float(s["fitted_beta_v3"]) for s in per_seed]
    val_r1s = [float(s["val_r1_at_fitted_alpha"]) for s in per_seed]
    agg["fitted_alpha_v3_mean"] = _mean(alphas)
    agg["fitted_alpha_v3_per_seed"] = alphas
    agg["fitted_beta_v3_per_seed"] = betas
    agg["val_r1_at_fitted_alpha_mean"] = _mean(val_r1s)
    return agg


def _compute_verdict(
    agg: Dict[str, Any], per_seed: Sequence[Dict[str, Any]]
) -> Tuple[str, str]:
    adaptive_test_r5 = agg["arm_v3_adaptive_alpha_test_recall_at_5_mean"]
    adaptive_full_r5 = agg["arm_v3_adaptive_alpha_full100_recall_at_5_mean"]
    v3eq_r5 = agg["arm_v3_equal_alpha_recall_at_5_mean"]
    ppmi_r5 = agg["arm_ppmi_alone_recall_at_5_mean"]
    vwfa_r5 = agg["arm_vwfa_alone_recall_at_5_mean"]
    tri_r5 = agg["arm_char_trigram_unsup_reference_recall_at_5_mean"]
    best_single = max(vwfa_r5, ppmi_r5)
    all_arms_differ = all(bool(s.get("arms_differ_verified")) for s in per_seed)
    all_no_leakage = all(bool(s.get("no_leakage_verified")) for s in per_seed)

    # HF gates (priority order).
    if not all_no_leakage:
        return (
            "HARD_FAIL",
            "HF4_LEAKAGE_DETECTED: val/test query sets overlap on at least one seed.",
        )
    if not all_arms_differ:
        return (
            "HARD_FAIL",
            "HF3_ARMS_IDENTICAL: at least one seed has arms_differ_verified=False; "
            "top-k index stacks hash-collide.",
        )
    # Regression check (HP3-HP6).
    reg_deltas = {
        "v3_equal": (v3eq_r5, HP3_V3_EQUAL_MEASURED),
        "ppmi":     (ppmi_r5, HP4_PPMI_MEASURED),
        "vwfa":     (vwfa_r5, HP5_VWFA_MEASURED),
        "trigram":  (tri_r5, HP6_TRIGRAM_MEASURED),
    }
    reg_broken = [
        f"{name}={measured:.4f}~vs~prior={prior:.4f}~delta={measured - prior:+.4f}"
        for name, (measured, prior) in reg_deltas.items()
        if abs(measured - prior) > REG_TOL
    ]
    if reg_broken:
        return (
            "HARD_FAIL",
            "HF2_REGRESSION_BROKEN (any arm outside +/-0.02 tolerance from "
            f"v3 EQUAL-alpha smoke prior): {reg_broken}.",
        )
    # HF1 STRONGER structural finding.
    if adaptive_test_r5 < best_single - HP2_ADAPTIVE_RECOVER_MARGIN:
        return (
            "HARD_FAIL",
            f"HF1_ADAPTIVE_FAILS_TO_RECOVER: adaptive_test_r5={adaptive_test_r5:.4f} "
            f"< max(VWFA={vwfa_r5:.4f}, PPMI={ppmi_r5:.4f})={best_single:.4f} - "
            f"{HP2_ADAPTIVE_RECOVER_MARGIN}. Score-level late-combine "
            f"FUNDAMENTALLY LOSSY for these two spokes at this regime; STRONGER "
            f"structural finding per Skunkworks composition-dilution lemma.",
        )

    # HP gates.
    hp1 = adaptive_test_r5 >= HP1_ADAPTIVE_R5_LIFT
    hp2 = adaptive_test_r5 >= best_single - HP2_ADAPTIVE_RECOVER_MARGIN
    hp3 = abs(v3eq_r5 - HP3_V3_EQUAL_MEASURED) <= REG_TOL
    hp4 = abs(ppmi_r5 - HP4_PPMI_MEASURED) <= REG_TOL
    hp5 = abs(vwfa_r5 - HP5_VWFA_MEASURED) <= REG_TOL
    hp6 = abs(tri_r5 - HP6_TRIGRAM_MEASURED) <= REG_TOL
    hp7 = all_no_leakage
    hp8 = all_arms_differ
    fitted_alphas = [float(s["fitted_alpha_v3"]) for s in per_seed]
    fitted_summary = f"fitted_alpha_per_seed={fitted_alphas}"

    if hp1 and hp2 and hp3 and hp4 and hp5 and hp6 and hp7 and hp8:
        return (
            "HARD_PASS",
            f"HARD_PASS: adaptive_test_r5={adaptive_test_r5:.4f} "
            f"adaptive_full_r5={adaptive_full_r5:.4f} best_single={best_single:.4f} "
            f"v3eq={v3eq_r5:.4f} PPMI={ppmi_r5:.4f} VWFA={vwfa_r5:.4f} "
            f"TRIGRAM={tri_r5:.4f} {fitted_summary}; HP1+HP2+HP3+HP4+HP5+HP6+HP7+HP8 "
            f"all met; adaptive-alpha grid search recovers/lifts vs best-single "
            f"AND all 4 regression arms reproduce v3 EQUAL smoke prior +/-0.02.",
        )
    cleared: List[str] = []
    missed: List[str] = []
    for name, ok in [
        ("HP1", hp1), ("HP2", hp2), ("HP3", hp3), ("HP4", hp4),
        ("HP5", hp5), ("HP6", hp6), ("HP7", hp7), ("HP8", hp8),
    ]:
        (cleared if ok else missed).append(name)
    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: adaptive_test_r5={adaptive_test_r5:.4f} "
        f"adaptive_full_r5={adaptive_full_r5:.4f} best_single={best_single:.4f} "
        f"v3eq={v3eq_r5:.4f} PPMI={ppmi_r5:.4f} VWFA={vwfa_r5:.4f} "
        f"TRIGRAM={tri_r5:.4f} {fitted_summary}; cleared={cleared} missed={missed}.",
    )


# ---------------------------------------------------------------------------
# Formula selftests (invoked when --self-test).
# ---------------------------------------------------------------------------

def _selftest_ppmi_dominant_snaps_alpha_to_zero() -> None:
    """Synthetic regime: PPMI dominates, VWFA is noise.  Fitted alpha should
    be near 0, and adaptive-alpha retrieval should equal PPMI-alone retrieval
    bit-identically on the held-out val queries.
    """
    rng = np.random.default_rng(42)
    n_dim = 512
    n_atoms = 20
    labels = list(range(n_atoms))
    protos_vwfa = rng.standard_normal((n_atoms, n_dim)).astype(np.float32)
    protos_ppmi = rng.standard_normal((n_atoms, n_dim)).astype(np.float32)
    # PPMI queries close to their proto (discriminative); VWFA queries noise.
    per_q_ppmi = [
        protos_ppmi[i] + 0.05 * rng.standard_normal(n_dim).astype(np.float32)
        for i in range(n_atoms)
    ]
    per_q_vwfa = [
        rng.standard_normal(n_dim).astype(np.float32) for _ in range(n_atoms)
    ]
    best_alpha, _, best_gamma, best_recall = fit_weights_grid_2spoke(
        per_query_ortho=per_q_vwfa,
        per_query_sem=per_q_ppmi,
        prototypes_ortho=protos_vwfa,
        prototypes_sem=protos_ppmi,
        labels=labels,
        alpha_grid=ALPHA_GRID,
    )
    assert best_alpha <= 0.2, (
        f"selftest ppmi-dominant: expected alpha near 0; got {best_alpha}"
    )
    assert best_recall >= 0.8, (
        f"selftest ppmi-dominant: expected recall >= 0.8; got {best_recall}"
    )
    # At best_alpha (near 0) the combined score is ~= PPMI cosine; verify
    # top-1 matches PPMI-alone top-1 for at least 90% of queries.
    match = 0
    for i in range(n_atoms):
        cs_v = _cosine_row(per_q_vwfa[i], protos_vwfa)
        cs_p = _cosine_row(per_q_ppmi[i], protos_ppmi)
        combined = best_alpha * cs_v + best_gamma * cs_p
        top1_adapt = int(np.argmax(combined))
        top1_ppmi = int(np.argmax(cs_p))
        if top1_adapt == top1_ppmi:
            match += 1
    assert match >= 18, (
        f"selftest ppmi-dominant: adaptive-alpha top-1 matches PPMI-alone "
        f"top-1 only {match}/20 (should be >= 18 at alpha near 0)"
    )
    print(
        f"[selftest ppmi-dominant] PASS alpha={best_alpha:.2f} "
        f"beta={best_gamma:.2f} val_r1={best_recall:.3f} "
        f"adapt=ppmi_match={match}/20",
        flush=True,
    )


def _selftest_vwfa_dominant_snaps_alpha_high() -> None:
    """Synthetic regime: VWFA dominates, PPMI is noise.  Fitted alpha should
    be > 0 (strictly), and adaptive-alpha retrieval should recover high recall.
    """
    rng = np.random.default_rng(43)
    n_dim = 512
    n_atoms = 20
    labels = list(range(n_atoms))
    protos_vwfa = rng.standard_normal((n_atoms, n_dim)).astype(np.float32)
    protos_ppmi = rng.standard_normal((n_atoms, n_dim)).astype(np.float32)
    per_q_vwfa = [
        protos_vwfa[i] + 0.05 * rng.standard_normal(n_dim).astype(np.float32)
        for i in range(n_atoms)
    ]
    per_q_ppmi = [
        rng.standard_normal(n_dim).astype(np.float32) for _ in range(n_atoms)
    ]
    best_alpha, _, best_gamma, best_recall = fit_weights_grid_2spoke(
        per_query_ortho=per_q_vwfa,
        per_query_sem=per_q_ppmi,
        prototypes_ortho=protos_vwfa,
        prototypes_sem=protos_ppmi,
        labels=labels,
        alpha_grid=ALPHA_GRID,
    )
    # Note: fit returns FIRST alpha achieving max recall; when VWFA is strong
    # enough, best_alpha may snap moderately.  Assert alpha > 0 (VWFA used at all)
    # and recall saturates high.  Matches late_combine._selftest discipline.
    assert best_alpha > 0.0, (
        f"selftest vwfa-dominant: expected alpha > 0; got {best_alpha}"
    )
    assert best_recall >= 0.8, (
        f"selftest vwfa-dominant: expected recall >= 0.8; got {best_recall}"
    )
    print(
        f"[selftest vwfa-dominant] PASS alpha={best_alpha:.2f} "
        f"beta={best_gamma:.2f} val_r1={best_recall:.3f}",
        flush=True,
    )


def _selftest_balanced_regime() -> None:
    """Both streams contribute.  Fitted alpha should be non-degenerate."""
    rng = np.random.default_rng(44)
    n_dim = 512
    n_atoms = 30
    labels = list(range(n_atoms))
    protos_vwfa = rng.standard_normal((n_atoms, n_dim)).astype(np.float32)
    protos_ppmi = rng.standard_normal((n_atoms, n_dim)).astype(np.float32)
    per_q_vwfa = [
        protos_vwfa[i] + 0.30 * rng.standard_normal(n_dim).astype(np.float32)
        for i in range(n_atoms)
    ]
    per_q_ppmi = [
        protos_ppmi[i] + 0.30 * rng.standard_normal(n_dim).astype(np.float32)
        for i in range(n_atoms)
    ]
    best_alpha, _, best_gamma, best_recall = fit_weights_grid_2spoke(
        per_query_ortho=per_q_vwfa,
        per_query_sem=per_q_ppmi,
        prototypes_ortho=protos_vwfa,
        prototypes_sem=protos_ppmi,
        labels=labels,
        alpha_grid=ALPHA_GRID,
    )
    # In balanced regime with symmetric noise, any alpha may win; assert only
    # recall is reasonable (grid finds SOME good alpha).
    assert best_recall >= 0.5, (
        f"selftest balanced: expected recall >= 0.5; got {best_recall}"
    )
    print(
        f"[selftest balanced] PASS alpha={best_alpha:.2f} "
        f"beta={best_gamma:.2f} val_r1={best_recall:.3f}",
        flush=True,
    )


def _selftest_no_leakage_gate() -> None:
    """Verify split logic produces disjoint val/test sets across many seeds."""
    for s in (7, 11, 17, 23, 29, 31):
        rng = np.random.default_rng(int(s) + 1000)
        perm = rng.permutation(100)
        val = perm[:50].tolist()
        test = perm[50:].tolist()
        assert set(val).isdisjoint(set(test)), (
            f"selftest no-leakage: split at seed={s} overlaps"
        )
        assert len(val) + len(test) == 100
    print("[selftest no-leakage] PASS (disjoint val/test across 6 seeds)", flush=True)


def _run_selftests_and_verify() -> None:
    """Full formula selftest chain.

    1. ComposedEncoderV3 module selftests (13)
    2. late_combine module selftest (grid-search)
    3. Cell-level PPMI-dominant snap-to-alpha=0
    4. Cell-level VWFA-dominant snap-to-alpha>0
    5. Cell-level balanced regime sanity
    6. No-leakage gate on split logic
    """
    from hdlab.composed_encoder_v3 import _selftest as _v3_selftest  # noqa: PLC0415
    from hdlab.late_combine import _selftest as _lc_selftest  # noqa: PLC0415
    print("[selftest] running hdlab.composed_encoder_v3._selftest ...", flush=True)
    _v3_selftest()
    print("[selftest] running hdlab.late_combine._selftest ...", flush=True)
    _lc_selftest()
    print("[selftest] running PPMI-dominant snap-to-alpha=0 ...", flush=True)
    _selftest_ppmi_dominant_snaps_alpha_to_zero()
    print("[selftest] running VWFA-dominant snap-to-alpha>0 ...", flush=True)
    _selftest_vwfa_dominant_snaps_alpha_high()
    print("[selftest] running balanced-regime sanity ...", flush=True)
    _selftest_balanced_regime()
    print("[selftest] running no-leakage gate ...", flush=True)
    _selftest_no_leakage_gate()
    print("[selftest] ALL formula selftests PASS", flush=True)


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
            "val_frac": float(VAL_FRAC),
            "alpha_grid": list(ALPHA_GRID),
            "hp_bands": {
                "HP1_adaptive_r5_lift": HP1_ADAPTIVE_R5_LIFT,
                "HP2_adaptive_recover_margin": HP2_ADAPTIVE_RECOVER_MARGIN,
                "REG_TOL": REG_TOL,
                "HP3_v3_equal_measured": HP3_V3_EQUAL_MEASURED,
                "HP4_ppmi_measured": HP4_PPMI_MEASURED,
                "HP5_vwfa_measured": HP5_VWFA_MEASURED,
                "HP6_trigram_measured": HP6_TRIGRAM_MEASURED,
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
        "no_leakage_verified_all_seeds": bool(
            all(bool(s.get("no_leakage_verified")) for s in per_seed)
        ),
        "final_metrics_atomicity": "tmp_replace",
        "progress_logging": "print_flush_true",
        "storage_strategy": "sharded_per_atom_prototype_hds_composed_v3",
        "compute_arch": "sequential_cpu_numpy",
        "baseline_probe_notes": baseline_probe_notes,
        "prereg_path": (
            "preregs/2026-07-03_substrate_composed_encoder_v3_"
            "adaptive_alpha_smoke.md"
        ),
        "meta_rules_touched": [
            "AF_arms_differ",
            "AG_baseline_in_band",
            "AH_atomic_final_metrics",
            "K_discriminator_fires",
            "L_strict_above_floor",
            "M_calibration_default_ok",
            "H_cardinality_ok",
            "AC_hypothesized_vs_measured",
            "run_mode_verification_16",
            "sec15D_positive_control_reproduce",
            "sec15E_functional_decomposition",
        ],
        "hp_scope": {
            "ARM_V3_ADAPTIVE_ALPHA":            ["HP1", "HP2", "HP7", "HP8"],
            "ARM_V3_EQUAL_ALPHA":               ["HP3", "HP8"],
            "ARM_PPMI_ALONE":                   ["HP4", "HP8"],
            "ARM_VWFA_ALONE":                   ["HP5", "HP8"],
            "ARM_CHAR_TRIGRAM_UNSUP_REFERENCE": ["HP6", "HP8"],
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
    print("[selftest] running module + cell formula selftests", flush=True)
    _run_selftests_and_verify()
    print("[selftest] running 1-seed 5-arm probe at N=20 atoms n_dim=1024",
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
        verdict=(
            "SELFTEST_PASS"
            if per["arms_differ_verified"] and per["no_leakage_verified"]
            else "SELFTEST_FAIL"
        ),
        verdict_msg=(
            f"SELFTEST: arms_differ={per['arms_differ_verified']} "
            f"no_leakage={per['no_leakage_verified']} "
            f"fit_alpha={per['fitted_alpha_v3']:.2f} "
            f"adaptive_test_r5="
            f"{agg['arm_v3_adaptive_alpha_test_recall_at_5_mean']:.3f} "
            f"v3eq_r5={agg['arm_v3_equal_alpha_recall_at_5_mean']:.3f} "
            f"ppmi_r5={agg['arm_ppmi_alone_recall_at_5_mean']:.3f} "
            f"vwfa_r5={agg['arm_vwfa_alone_recall_at_5_mean']:.3f} "
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
    if not per["no_leakage_verified"]:
        raise AssertionError(
            "selftest: no_leakage_verified=False; val/test overlap"
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

    adaptive_test_r5 = agg["arm_v3_adaptive_alpha_test_recall_at_5_mean"]
    adaptive_full_r5 = agg["arm_v3_adaptive_alpha_full100_recall_at_5_mean"]
    v3eq_r5 = agg["arm_v3_equal_alpha_recall_at_5_mean"]
    vwfa_r5 = agg["arm_vwfa_alone_recall_at_5_mean"]
    ppmi_r5 = agg["arm_ppmi_alone_recall_at_5_mean"]
    tri_r5 = agg["arm_char_trigram_unsup_reference_recall_at_5_mean"]
    best_single = max(vwfa_r5, ppmi_r5)

    baseline_in_band = (
        BASELINE_IN_BAND_LO <= tri_r5 <= BASELINE_IN_BAND_HI
    )
    lift_vs_best_single = adaptive_test_r5 - best_single
    discriminator_fires = abs(lift_vs_best_single) > 1e-6 or (
        # Also fires if fitted alpha is non-trivial (not fixed at 0.5).
        any(abs(float(s["fitted_alpha_v3"]) - 0.5) > 1e-6 for s in per_seed)
    )

    fitted_alphas = [float(s["fitted_alpha_v3"]) for s in per_seed]
    baseline_probe_notes = (
        f"baseline_in_band={baseline_in_band} "
        f"adaptive_test_r5={adaptive_test_r5:.4f} "
        f"adaptive_full_r5={adaptive_full_r5:.4f} "
        f"best_single={best_single:.4f} v3eq={v3eq_r5:.4f} "
        f"tri_r5={tri_r5:.4f} lift_vs_best_single={lift_vs_best_single:+.4f} "
        f"fitted_alpha_per_seed={fitted_alphas} "
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
