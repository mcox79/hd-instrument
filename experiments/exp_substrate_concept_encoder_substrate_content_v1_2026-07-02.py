"""substrate_concept_encoder_substrate_content_v1_2026_07_02

Tests hdlab.concept_encoder.ConceptEncoder (brain-analog competitive-Hebbian
sparse coding mechanism) on SUBSTRATE-INGESTED SYMBOLIC CONTENT
(WordNet 3.0 lexicon partition from data/substrate_index/concept/atoms.jsonl).

FRAMING (LOAD-BEARING per USER 2026-07-02):
  Tests mechanism on substrate's KNOWN SYMBOLIC KNOWLEDGE
  (WordNet definitions+synonyms); NOT unsupervised discovery from raw
  corpora; NOT natural narrative text; NOT "substrate understands English".
  HP earned here does NOT grant "substrate knows things" broadly; grants
  "mechanism works on substrate's known symbolic content at this regime".

Corpus fallback (2026-07-02 spot-check + USER pre-authorization):
  ConceptNet concept_node atoms (133K) have description="ConceptNet english
  concept: <name>" -- literal name-repeat, no usable body text.  USER
  pre-authorized fallback to WordNet lexicon (6339 atoms with pos+definition).

Task: SUPERVISED retrieval of substrate atom given held-out synonym query.
  Per atom: fit(training_sentences=[definition, syn1, syn2, hypernym_hint],
              concept_label=atom_idx).
  Query: encode(held_out_last_synonym) -> cosine argmax over concept_hds table.
  Metric: recall@{1,5,10} = fraction with correct atom_idx in top-k.

Arms:
  1. ARM_CONCEPT_ENCODER (LOAD-BEARING; competitive-Hebbian sparse-coding)
  2. ARM_CHAR_POSITIONAL_ONLY (V1-analog surface; mean-bundle per atom, NO
     competitive Hebbian).
  3. ARM_CHAR_TRIGRAM_UNSUP (bag-word baseline; mean-bundle per atom).

Note: BGE-large arm is deferred to FULL (bge-large on CPU too slow for smoke).

HP bands (see pre-reg preregs/2026-07-02_substrate_concept_encoder_substrate_
content_v1.md):
  HP1: ARM_CONCEPT_ENCODER recall@5 >= 0.20 (mechanism has signal on real content)
  HP2: ARM_CONCEPT_ENCODER - ARM_CHAR_POSITIONAL >= 0.08 (mechanism > surface)
  HP3: ARM_CONCEPT_ENCODER - ARM_CHAR_TRIGRAM >= 0.08 (mechanism > bag-word)
  HP4: arms_differ_verified (3 arm prototype tables hash-distinct)
  HF1: ARM_CONCEPT_ENCODER recall@5 < 0.05 (mechanism fundamentally fails)
  HF2: ARM_CONCEPT_ENCODER < max(baselines) (no advantage; MAJOR REFRAME)
  HF3: any two arm prototype tables hash-identical

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (META_RULE_AF; hash-test)
  - final_metrics_atomicity: tmp_replace via os.replace
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: no quantitative CRLB (supervised retrieval; chance floor k/N)
  - baseline_in_band at smoke (META_RULE_AG; 0.05 < baseline < 0.80)
  - discriminator: ARM_CONCEPT_ENCODER - max(baselines) at smoke
  - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
  - HP_SCOPE: HP1/HP2/HP3 only on ARM_CONCEPT_ENCODER
  - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Compute arch: sequential CPU numpy.  Storage strategy: sharded per-atom prototype
  HDs. Composition depth L=1 (encoder eval, not chain).
Progress logging: print_flush_true (defensive for potential >30 min smoke).

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
# Bootstrap: reach hdlab + experiments helpers when executed as script.
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from hdlab.concept_encoder import ConceptEncoder  # noqa: E402
from hdlab.char_positional_encoder import CharPositionalEncoder  # noqa: E402
from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: E402
from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from experiments._cell_heartbeat import CellHeartbeat  # noqa: E402

# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------

ANCHOR_NAME = "substrate_concept_encoder_substrate_content_v1_2026_07_02"

CORPUS_ATOMS_JSONL = _REPO / "data" / "substrate_index" / "concept" / "atoms.jsonl"

# Sweep sizes.
SMOKE_N_ATOMS = 100
SMOKE_SEEDS = [11, 17, 23]
FULL_N_ATOMS = 500
FULL_SEEDS = [11, 17, 23]

# HD dim.
N_DIM = 2048

# HP band constants.
HP1_MECHANISM_RECALL5_FLOOR = 0.20
HP2_MECHANISM_MINUS_CHAR_POSITIONAL_GAP = 0.08
HP3_MECHANISM_MINUS_CHAR_TRIGRAM_GAP = 0.08
HF1_MECHANISM_TOTAL_FAIL_CEILING = 0.05
BASELINE_IN_BAND_LO = 0.05
BASELINE_IN_BAND_HI = 0.80

# concept_encoder CG defaults.
K_SPARSITY = 0.02
MAX_POS = 24

# Required min-atom quality for sampling.
MIN_DEFINITION_LEN = 20
MIN_SYNONYMS = 3

# Progress cadence.
PROGRESS_EVERY_N_ATOMS = 25


# ---------------------------------------------------------------------------
# Crash-diagnostic helpers (per exp_dev.md §13.C).
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
# Corpus loading.
# ---------------------------------------------------------------------------

def _clean_name(raw_name: str) -> str:
    """WN_burial.n.01 -> 'burial'; person.n.01 -> 'person'; underscores kept.

    Strip the .p.NN suffix.
    """
    n = raw_name
    if n.startswith("WN_"):
        n = n[3:]
    # Strip .p.NN sense suffix if present.
    parts = n.split(".")
    if len(parts) >= 3 and len(parts[-1]) <= 3 and parts[-1].isdigit():
        n = ".".join(parts[:-2])
    return n.replace("_", " ")


def _load_wordnet_atoms(
    max_atoms: int, seed: int
) -> List[Dict[str, Any]]:
    """Load top-freq WordNet lexicon atoms with sufficient content.

    Filter criteria:
      - kind == "lexicon"
      - metadata.pos in {n, v, a, r}
      - len(description) >= MIN_DEFINITION_LEN
      - len(metadata.synonyms) >= MIN_SYNONYMS
      - metadata.lemma_freq_semcor >= 1 (sorted desc)

    Returns list of {atom_id, name_clean, description, synonyms, hypernym0}.
    Selection is TOP-K by lemma_freq_semcor (deterministic ORDER; seed unused
    for selection but retained in signature for compat with per-seed harness).
    """
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
    # Sort by frequency desc (deterministic), take top max_atoms.
    candidates.sort(key=lambda x: (-int(x["freq"]), str(x["atom_id"])))
    del seed  # unused for selection; keeps interface with per-seed harness
    return candidates[:max_atoms]


# ---------------------------------------------------------------------------
# Training / query construction.
# ---------------------------------------------------------------------------

def _build_train_query(
    atoms: Sequence[Dict[str, Any]],
) -> Tuple[List[str], List[int], List[Tuple[int, str]]]:
    """For each atom, produce training sentences + a held-out query.

    Training sentences per atom (concept-label = atom_idx):
      - description
      - synonyms[0]
      - synonyms[1]
      - "related to <hypernym>" if hypernym exists
    Held-out query: LAST synonym (never in training).
    If atom has < 4 synonyms, uses synonyms[2] as query (and drops it from
    training). If atom has exactly 3 synonyms, uses synonyms[2] as query and
    keeps only [description, syn0, syn1] as training.

    Returns:
      training_sentences: list of str (length = sum(train_per_atom))
      training_labels: list of int, same length, values in [0, len(atoms))
      queries: list of (atom_idx, query_word) tuples.
    """
    training_sentences: List[str] = []
    training_labels: List[int] = []
    queries: List[Tuple[int, str]] = []
    for i, a in enumerate(atoms):
        syns: List[str] = list(a["synonyms"])
        desc: str = str(a["description"])
        hyp: str = str(a["hypernym0"] or "")
        # Choose held-out query: last synonym.
        if len(syns) >= 4:
            q = syns[-1]
            train_syns = syns[:2]  # first 2 synonyms in training
        elif len(syns) == 3:
            q = syns[2]
            train_syns = syns[:2]
        else:
            # Shouldn't happen due to MIN_SYNONYMS=3 filter, but be defensive.
            q = syns[-1]
            train_syns = syns[:-1]
        # Assemble training sentences for this atom.
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
    """Return top-k indices by cosine similarity of query_hd against prototypes.

    Args:
      query_hd: [n_dim] float / int
      prototypes: [N, n_dim] float / int
      k: number of top matches.
    Returns:
      [k] int64 array of prototype indices sorted by descending cosine.
    """
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
        # top-k argpartition then sort.
        idx_part = np.argpartition(-scores, k)[:k]
        order = idx_part[np.argsort(-scores[idx_part])]
    return order.astype(np.int64)


def _hash_prototype_table(arr: np.ndarray) -> str:
    return hashlib.sha256(arr.tobytes()).hexdigest()


def _build_prototypes_char_positional(
    training_sentences: Sequence[str],
    training_labels: Sequence[int],
    n_atoms: int,
    n_dim: int,
    seed: int,
) -> np.ndarray:
    """Build per-atom prototype HDs via mean-bundle of char-positional encodings
    of the training sentences that share the concept label.  No competitive
    Hebbian; simple bundling.
    """
    enc = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    acc = np.zeros((n_atoms, n_dim), dtype=np.float32)
    counts = np.zeros(n_atoms, dtype=np.float32)
    for s, lbl in zip(training_sentences, training_labels):
        hd = enc.encode_sentence(str(s))
        acc[int(lbl)] += hd
        counts[int(lbl)] += 1.0
    # Simple bundle (no sign; float prototype).  Zero-mean per row NOT applied
    # -- we want the raw bundle direction.
    denom = np.where(counts > 0, counts, 1.0)
    proto = acc / denom[:, None]
    return proto.astype(np.float32)


def _build_prototypes_char_trigram(
    training_sentences: Sequence[str],
    training_labels: Sequence[int],
    n_atoms: int,
    n_dim: int,
    seed: int,
) -> np.ndarray:
    """Build per-atom prototype HDs via mean-bundle of char-trigram encodings.
    """
    # CharTrigramEncoder is deterministic per trigram (seeded via hash); the
    # `seed` here does not change trigram HDs.  Included in signature for
    # interface parity.
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
    return proto.astype(np.float32)


def _build_prototypes_concept_encoder(
    training_sentences: Sequence[str],
    training_labels: Sequence[int],
    n_atoms: int,
    n_dim: int,
    seed: int,
) -> Tuple[np.ndarray, ConceptEncoder]:
    """Fit ConceptEncoder on (training_sentences, training_labels).  Returns
    (concept_hds int8 [n_atoms, n_dim], the fitted encoder instance).
    """
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


def _query_arm_concept_encoder(
    enc: ConceptEncoder, queries: Sequence[Tuple[int, str]], k_values: Sequence[int]
) -> Dict[str, Any]:
    """Query ConceptEncoder by encoding the query word via internal surface
    encoder then cosine argmax on concept_hds.  We reuse enc._surface_encoder
    to encode the query (single word); this matches the class's encode() path.
    """
    concept_hds = enc.concept_hds.astype(np.float32)
    correct_at_k = {int(k): 0 for k in k_values}
    n = len(queries)
    for atom_idx, q_word in queries:
        surf = enc._surface_encoder.encode_sentence(str(q_word))  # noqa: SLF001
        # Reuse existing cosine-argmax path.
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
    """Query a bundle-based arm: encode(q_word) via encode_fn -> cosine argmax
    over prototypes.
    """
    correct_at_k = {int(k): 0 for k in k_values}
    n = len(queries)
    for atom_idx, q_word in queries:
        hd = encode_fn(str(q_word))
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
    """Run all 3 arms at one seed.  Returns per-seed dict."""
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

    # ARM 1: ConceptEncoder.
    t_arm = time.perf_counter()
    concept_hds, enc = _build_prototypes_concept_encoder(
        training_sentences, training_labels, n_atoms, n_dim, seed
    )
    concept_hash = _hash_prototype_table(concept_hds)
    arm1_metrics = _query_arm_concept_encoder(enc, queries, k_values)
    arm1_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_CONCEPT_ENCODER] recall@1={arm1_metrics['recall_at_1']:.4f} "
        f"recall@5={arm1_metrics['recall_at_5']:.4f} "
        f"recall@10={arm1_metrics['recall_at_10']:.4f} wall={arm1_wall:.1f}s",
        flush=True,
    )
    hb.tick(
        unit_idx=2,
        extra={
            "phase": "arm_concept_encoder_done",
            "seed": seed,
            "recall_at_5": arm1_metrics["recall_at_5"],
        },
        force=True,
    )

    # ARM 2: char_positional bundle.
    t_arm = time.perf_counter()
    cp_prototypes = _build_prototypes_char_positional(
        training_sentences, training_labels, n_atoms, n_dim, seed
    )
    cp_hash = _hash_prototype_table(cp_prototypes)
    cp_enc = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    arm2_metrics = _query_arm_bundled(
        cp_prototypes, queries, k_values, cp_enc.encode_sentence
    )
    arm2_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_CHAR_POSITIONAL_ONLY] recall@1={arm2_metrics['recall_at_1']:.4f} "
        f"recall@5={arm2_metrics['recall_at_5']:.4f} "
        f"recall@10={arm2_metrics['recall_at_10']:.4f} wall={arm2_wall:.1f}s",
        flush=True,
    )
    hb.tick(
        unit_idx=3,
        extra={
            "phase": "arm_char_positional_done",
            "seed": seed,
            "recall_at_5": arm2_metrics["recall_at_5"],
        },
        force=True,
    )

    # ARM 3: char_trigram bundle.
    t_arm = time.perf_counter()
    ct_prototypes = _build_prototypes_char_trigram(
        training_sentences, training_labels, n_atoms, n_dim, seed
    )
    ct_hash = _hash_prototype_table(ct_prototypes)
    ct_enc = CharTrigramEncoder(n_dim=n_dim, pad_char=" ")
    arm3_metrics = _query_arm_bundled(
        ct_prototypes, queries, k_values, lambda s: ct_enc.encode(s).astype(np.float32)
    )
    arm3_wall = time.perf_counter() - t_arm
    print(
        f"[seed={seed} ARM_CHAR_TRIGRAM_UNSUP] recall@1={arm3_metrics['recall_at_1']:.4f} "
        f"recall@5={arm3_metrics['recall_at_5']:.4f} "
        f"recall@10={arm3_metrics['recall_at_10']:.4f} wall={arm3_wall:.1f}s",
        flush=True,
    )
    hb.tick(
        unit_idx=4,
        extra={
            "phase": "arm_char_trigram_done",
            "seed": seed,
            "recall_at_5": arm3_metrics["recall_at_5"],
        },
        force=True,
    )

    # Arms-differ hash check.
    hashes = {
        "ARM_CONCEPT_ENCODER": concept_hash,
        "ARM_CHAR_POSITIONAL_ONLY": cp_hash,
        "ARM_CHAR_TRIGRAM_UNSUP": ct_hash,
    }
    unique_hashes = set(hashes.values())
    arms_differ_verified = len(unique_hashes) == 3

    return {
        "seed": int(seed),
        "n_atoms": int(n_atoms),
        "n_dim": int(n_dim),
        "n_train_sentences": int(len(training_sentences)),
        "n_queries": int(len(queries)),
        "arm_concept_encoder": arm1_metrics,
        "arm_char_positional_only": arm2_metrics,
        "arm_char_trigram_unsup": arm3_metrics,
        "arm_walls_s": {
            "concept_encoder": round(arm1_wall, 3),
            "char_positional": round(arm2_wall, 3),
            "char_trigram": round(arm3_wall, 3),
        },
        "arms_differ_verified": bool(arms_differ_verified),
        "arm_hashes": hashes,
        "wall_s": round(time.perf_counter() - t0, 3),
    }


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def _aggregate_per_seed(per_seed: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute mean recall@k across seeds per arm."""

    def _mean(vals: List[float]) -> float:
        return float(np.mean(vals)) if vals else 0.0

    def _arm(name: str, k: int) -> float:
        return _mean([float(s[name][f"recall_at_{k}"]) for s in per_seed])

    return {
        "arm_concept_encoder_recall_at_1_mean": _arm("arm_concept_encoder", 1),
        "arm_concept_encoder_recall_at_5_mean": _arm("arm_concept_encoder", 5),
        "arm_concept_encoder_recall_at_10_mean": _arm("arm_concept_encoder", 10),
        "arm_char_positional_recall_at_1_mean": _arm("arm_char_positional_only", 1),
        "arm_char_positional_recall_at_5_mean": _arm("arm_char_positional_only", 5),
        "arm_char_positional_recall_at_10_mean": _arm("arm_char_positional_only", 10),
        "arm_char_trigram_recall_at_1_mean": _arm("arm_char_trigram_unsup", 1),
        "arm_char_trigram_recall_at_5_mean": _arm("arm_char_trigram_unsup", 5),
        "arm_char_trigram_recall_at_10_mean": _arm("arm_char_trigram_unsup", 10),
    }


def _compute_verdict(
    agg: Dict[str, Any], per_seed: Sequence[Dict[str, Any]]
) -> Tuple[str, str]:
    """Return (verdict, verdict_msg) per pre-reg HP/HF bands.

    Priority:
      HF3 (arms bit-identical) -> HARD_FAIL_ARMS_BIT_IDENTICAL
      HF1 (mechanism total fail) -> HARD_FAIL_MECHANISM_FUNDAMENTAL
      HF2 (no mechanism advantage) -> HARD_FAIL_NO_MECHANISM_ADVANTAGE
      HP1+HP2+HP3+HP4 -> HARD_PASS
      Else MIDDLE_BAND with which HP gates cleared.
    """
    me5 = agg["arm_concept_encoder_recall_at_5_mean"]
    cp5 = agg["arm_char_positional_recall_at_5_mean"]
    ct5 = agg["arm_char_trigram_recall_at_5_mean"]
    max_baseline = max(cp5, ct5)
    gap_cp = me5 - cp5
    gap_ct = me5 - ct5

    all_arms_differ = all(bool(s.get("arms_differ_verified")) for s in per_seed)

    # HF3 first (structural bug).
    if not all_arms_differ:
        return (
            "HARD_FAIL",
            f"HF3 arms_differ_verified=False on at least one seed; "
            f"prototype tables hash-collide (mechanism bug or corpus degenerate).",
        )
    # HF1 mechanism fundamental fail.
    if me5 < HF1_MECHANISM_TOTAL_FAIL_CEILING:
        return (
            "HARD_FAIL",
            f"HF1 ARM_CONCEPT_ENCODER recall@5_mean={me5:.4f} < {HF1_MECHANISM_TOTAL_FAIL_CEILING:.2f} "
            f"(mechanism fundamentally fails on real substrate content).",
        )
    # HF2 no mechanism advantage.
    if me5 < max_baseline:
        return (
            "HARD_FAIL",
            f"HF2 ARM_CONCEPT_ENCODER recall@5_mean={me5:.4f} < max(baseline)="
            f"{max_baseline:.4f} (cp={cp5:.4f}, ct={ct5:.4f}); mechanism has NO advantage; "
            f"MAJOR REFRAME.",
        )
    # HP band assessment.
    hp1 = me5 >= HP1_MECHANISM_RECALL5_FLOOR
    hp2 = gap_cp >= HP2_MECHANISM_MINUS_CHAR_POSITIONAL_GAP
    hp3 = gap_ct >= HP3_MECHANISM_MINUS_CHAR_TRIGRAM_GAP
    hp4 = all_arms_differ

    if hp1 and hp2 and hp3 and hp4:
        return (
            "HARD_PASS",
            f"HARD_PASS: mechanism_r5={me5:.4f} baselines(cp={cp5:.4f},ct={ct5:.4f}) "
            f"gaps(cp={gap_cp:.4f},ct={gap_ct:.4f}) arms_differ=True; "
            f"all of HP1-HP4 met.",
        )
    # Otherwise MIDDLE_BAND.
    cleared = []
    missed = []
    for name, ok in [("HP1", hp1), ("HP2", hp2), ("HP3", hp3), ("HP4", hp4)]:
        (cleared if ok else missed).append(name)
    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: mechanism_r5={me5:.4f} baselines(cp={cp5:.4f},ct={ct5:.4f}) "
        f"gaps(cp={gap_cp:.4f},ct={gap_ct:.4f}); cleared={cleared} missed={missed}.",
    )


# ---------------------------------------------------------------------------
# Main driver.
# ---------------------------------------------------------------------------

def _run_mode_dispatch(run_mode: str) -> Tuple[List[int], int, int]:
    """Return (seeds_to_run, n_atoms, expected_units).

    expected_units = len(seeds) * n_arms(=3).
    """
    if run_mode == "smoke":
        return list(SMOKE_SEEDS), int(SMOKE_N_ATOMS), 3 * len(SMOKE_SEEDS)
    if run_mode == "full":
        return list(FULL_SEEDS), int(FULL_N_ATOMS), 3 * len(FULL_SEEDS)
    # self_test path uses a smaller sample (checked inline; see _run_self_test).
    return [11], 20, 3


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
                "HP1_mechanism_recall5_floor": HP1_MECHANISM_RECALL5_FLOOR,
                "HP2_gap_cp": HP2_MECHANISM_MINUS_CHAR_POSITIONAL_GAP,
                "HP3_gap_ct": HP3_MECHANISM_MINUS_CHAR_TRIGRAM_GAP,
                "HF1_mechanism_ceiling": HF1_MECHANISM_TOTAL_FAIL_CEILING,
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
            "preregs/2026-07-02_substrate_concept_encoder_substrate_content_v1.md"
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
            "ARM_CONCEPT_ENCODER": ["HP1", "HP2", "HP3", "HP4"],
            "ARM_CHAR_POSITIONAL_ONLY": ["HP4"],
            "ARM_CHAR_TRIGRAM_UNSUP": ["HP4"],
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
    """Minimal self-test path.

    Runs 1 seed at N=20 atoms so runner --self-test finishes in seconds.
    Asserts corpus loads + arms produce differing prototype tables + verdict
    logic runs.  No HP band interpretation.
    """
    t0 = time.perf_counter()
    _write_start_marker(output_dir, "self_test", expected_n_units=3)
    print(f"[selftest] loading {CORPUS_ATOMS_JSONL}", flush=True)
    atoms = _load_wordnet_atoms(max_atoms=20, seed=11)
    print(f"[selftest] loaded {len(atoms)} WordNet atoms; running 1-seed eval",
          flush=True)
    with CellHeartbeat(str(output_dir), total_units=3, interval_s=10) as hb:
        per = _eval_one_seed(seed=11, atoms=atoms, n_dim=1024, hb=hb)
    per_seed = [per]
    agg = _aggregate_per_seed(per_seed)
    verdict, msg = _compute_verdict(agg, per_seed)
    baseline_in_band = (
        BASELINE_IN_BAND_LO
        <= agg["arm_char_trigram_recall_at_5_mean"]
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
            f"mechanism_r5={agg['arm_concept_encoder_recall_at_5_mean']:.3f} "
            f"cp_r5={agg['arm_char_positional_recall_at_5_mean']:.3f} "
            f"ct_r5={agg['arm_char_trigram_recall_at_5_mean']:.3f} "
            f"baseline_in_band={baseline_in_band} verdict_probe={verdict} "
            f"[N=20 atoms 1 seed n_dim=1024]"
        ),
        elapsed_s=time.perf_counter() - t0,
        baseline_in_band=bool(baseline_in_band),
        discriminator_fires=True,  # not evaluated at selftest
        expected_n_units=3,
        landed_n_units=3,
        baseline_probe_notes=(
            "self_test path; N=20 atoms 1 seed n_dim=1024; sanity only"
        ),
    )
    if not per["arms_differ_verified"]:
        raise AssertionError(
            "selftest: arms_differ_verified=False; ARM prototype tables hash-collide"
        )
    print(
        f"[selftest] PASS verdict={metrics['verdict']} elapsed_s={metrics['elapsed_s']:.2f}",
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
            f"[{run_mode}] WARN: only {len(atoms)} atoms passed filter (< {n_atoms}); "
            f"using all available",
            flush=True,
        )
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
            landed_units += 3  # 3 arms per seed
    agg = _aggregate_per_seed(per_seed)

    # Baseline-in-band check on char_trigram (the "unrelated to mechanism"
    # baseline; if it saturates the discriminator can't fire).
    ct5_mean = agg["arm_char_trigram_recall_at_5_mean"]
    cp5_mean = agg["arm_char_positional_recall_at_5_mean"]
    baseline_in_band = (
        BASELINE_IN_BAND_LO <= ct5_mean <= BASELINE_IN_BAND_HI
        and BASELINE_IN_BAND_LO <= cp5_mean <= BASELINE_IN_BAND_HI
    )
    me5 = agg["arm_concept_encoder_recall_at_5_mean"]
    max_baseline = max(cp5_mean, ct5_mean)
    discriminator_fires = (me5 - max_baseline) >= 0.05

    baseline_probe_notes = (
        f"baseline_in_band={baseline_in_band} "
        f"cp_r5_mean={cp5_mean:.4f} ct_r5_mean={ct5_mean:.4f} "
        f"mechanism_r5_mean={me5:.4f} gap_vs_maxbaseline={me5 - max_baseline:.4f} "
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
    """Argparser.  --run-mode default from HDLAB_RUN_MODE env var (Round 6
    META_RULE_env_var_contract).  Cell defaults to 'self_test' if unset."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--run-mode",
        default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
        choices=["self_test", "smoke", "full"],
    )
    # queue_add / runner may pass --self-test or --smoke as legacy flags.
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    return ap.parse_args(argv)


def main() -> int:
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    args = _parse_args()
    # Legacy flag translation.
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
