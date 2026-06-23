"""N11 RANDOM-INDEXING SEMANTIC v1 -- substrate-native distributional semantics on text8.

Cell anchor: n11_random_indexing_semantic_v1.

Context (per `notes/research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md`):
- char_trigram_encoder (CERT 585) is the only substrate-native text encoder; it is
  SURFACE-FORM only -- cos(cat, dog) ~ cos(cat, car) because cat/dog share no trigrams.
- KGStore (CERT 584/585/588) requires EXPLICIT (s, p, o) ingestion; it does NOT learn
  semantic similarity from raw text.
- The MISSING substrate primitive: Random Indexing (Sahlgren 2005, Kanerva 1988) --
  forward-only Hebbian co-occurrence accumulator. cat-dog ends up close because they
  appear in contexts with similar surrounding words (pet, food, animal, ...).
- Composes with: substrate's bipolar bundling (Hebbian sum), HRR-style cyclic-shift
  for order (BEAGLE Jones-Mewhort 2007), and Hadamard binding for hub-spoke conjunction
  with char_trigram orthographic spoke (ATL hub-spoke per Patterson-Lambon Ralph 2007).

MECHANISM UNDER TEST: Random Indexing context-vector accumulator on text8 + 3 substrate-
native compositions (pure RI, RI+BEAGLE order, RI hub-spoke + char_trigram), all
compared vs CONTROL_RANDOM_PERMUTE which shuffles word positions to destroy semantic
structure (CAN-FAIL discriminator per Fix #16; ratio should collapse to ~1.0).

ARMS per (seed) unit:
  Arm 1: RANDOM_INDEXING_ALONE        -- canonical RI (bag-of-context bipolar bundling)
  Arm 2: RI_PLUS_BEAGLE_ORDER         -- RI + cyclic-shift HRR order-binding
  Arm 3: RI_HUB_SPOKE_KGSTORE         -- RI context-vector bound (Hadamard *) with
                                         char_trigram orthographic vector; hub-spoke
                                         per ATL semantic memory model
  Arm 4: CONTROL_RANDOM_PERMUTE       -- canonical RI but corpus is position-shuffled
                                         BEFORE ingest; destroys distributional signal;
                                         ratio should be ~1.0 if mechanism works

PRE-REG HARD bands (per drill estimate P_deflated=0.55):
  HARD_PASS:   ALL three substantive arms (1, 2, 3): mean cos(similar) >= 1.5 * mean cos(dissimilar)
               AND CONTROL arm ratio <= 1.1 (control fails to discriminate)
               AND CV across seeds <= 0.20 on the headline ratio
               AND n_llm_calls == 0 (substrate-only at all stages)
  HARD_FAIL:   ANY substantive arm ratio < 1.1 (no distributional signal)
               OR CONTROL ratio > 1.3 (control fails to be null -> probe is broken)
  MIDDLE_BAND: between the two; per by-construction-saturation discipline, Skunkworks
               tiers as MEASURED_MECHANISM not chain-grade win.

PROBE SET (handcrafted; avoid external WordSim-353/SimLex-999 to stay substrate-only
and avoid network dep at runtime):
  similar pairs   = within-category pairs from {animals, vehicles, body_parts, time_words, color_words}
  dissimilar pairs = across-category pairs (animals vs numbers, etc.)
  All probe words filtered to text8 vocabulary at min_count=5 before testing.

Corpus: data/text8_cache/text8.txt (canonical word2vec benchmark; ~17M tokens after
preprocessing). Smoke uses first 200k tokens; full uses entire text8.

CPU-only; numpy + hdlab/random_indexing.py; ASCII; per-seed checkpoint.

Cites:
  - notes/research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22.md
  - Sahlgren 2005 (Random Indexing); Kanerva 1988 (Sparse Distributed Memory)
  - Jones-Mewhort 2007 (BEAGLE: HRR context-order)
  - Patterson-Nestor-Rogers 2007 (ATL hub-and-spoke semantic memory)
  - CERT 585 (char_trigram_encoder; orthographic spoke)

Skunkworks structural blockers baked in:
  #3 _LLM_CALL_COUNTER = [0]   (NO LLM at any stage)
  #1 per_unit per seed         (multi-seed exhaustive)
  #2 cv computed across seeds in compute_verdict
  #4 N/A (no VQ-floor / ceiling_bpc; semantic-geometry cell)
"""
from __future__ import annotations
import argparse
import atexit
import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    aggregate_partials,
    get_output_dir,
    write_metrics,
    write_partial_key,
)
from hdlab.random_indexing import RandomIndexingEncoder  # noqa: E402

ANCHOR_NAME = "n11_random_indexing_semantic_v1"
_LLM_CALL_COUNTER = [0]

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 8192
SPARSITY = 10
WINDOW = 5
MIN_COUNT = 5
TEXT8_PATH = REPO / "data" / "text8_cache" / "text8.txt"

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    MAX_TOKENS = None  # use entire text8
else:
    SEEDS = [0]
    MAX_TOKENS = 200_000  # ~1MB; smoke

CONFIG_VERSION = (
    "n11_random_indexing_v1; N=%d sparsity=%d window=%d min_count=%d max_tokens=%s seeds=%s"
    % (N_DIM, SPARSITY, WINDOW, MIN_COUNT, str(MAX_TOKENS), SEEDS)
)

# Handcrafted probe set (filtered to text8 vocab; all are common words).
# Categories chosen to have multiple in-vocab members and clear semantic clustering.
_PROBE_CATEGORIES = {
    "animals": ["cat", "dog", "horse", "cow", "pig", "sheep", "bird", "fish", "lion", "tiger"],
    "vehicles": ["car", "truck", "bus", "train", "ship", "boat", "plane", "bike", "vehicle", "motorcycle"],
    "body_parts": ["hand", "foot", "head", "eye", "ear", "arm", "leg", "heart", "brain", "mouth"],
    "colors": ["red", "blue", "green", "yellow", "black", "white", "brown", "purple", "orange", "pink"],
    "time_words": ["day", "night", "morning", "evening", "week", "month", "year", "hour", "minute", "second"],
    "numbers": ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"],
    "weather": ["rain", "snow", "wind", "storm", "cloud", "sun", "thunder", "fog", "ice", "heat"],
}


def _load_text8_tokens(max_tokens: int | None) -> List[str]:
    """Load text8 as a list of whitespace tokens (lowercase, already preprocessed)."""
    if not TEXT8_PATH.exists():
        raise FileNotFoundError("text8 corpus not found at %s" % TEXT8_PATH)
    with open(TEXT8_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    toks = text.split()
    if max_tokens is not None:
        toks = toks[:max_tokens]
    return toks


def _filter_probe_to_vocab(enc: RandomIndexingEncoder) -> Dict[str, List[str]]:
    """Keep only words present in the encoder vocabulary."""
    out = {}
    for cat, words in _PROBE_CATEGORIES.items():
        kept = [w for w in words if enc.has(w)]
        if len(kept) >= 2:
            out[cat] = kept
    return out


def _build_probe_pairs(filtered: Dict[str, List[str]]) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """Build similar (within-category) and dissimilar (across-category) word pairs.

    Cap at 100 pairs per side to keep eval cheap and balanced.
    """
    similar = []
    cats = list(filtered.keys())
    for cat in cats:
        ws = filtered[cat]
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                similar.append((ws[i], ws[j]))
    dissimilar = []
    for ci in range(len(cats)):
        for cj in range(ci + 1, len(cats)):
            for wi in filtered[cats[ci]]:
                for wj in filtered[cats[cj]]:
                    dissimilar.append((wi, wj))
    # Cap and balance
    rng = np.random.default_rng(0)
    if len(similar) > 100:
        idx = rng.choice(len(similar), 100, replace=False)
        similar = [similar[i] for i in sorted(idx.tolist())]
    if len(dissimilar) > 100:
        idx = rng.choice(len(dissimilar), 100, replace=False)
        dissimilar = [dissimilar[i] for i in sorted(idx.tolist())]
    return similar, dissimilar


def _cosine_pairs(vectors_by_word: Dict[str, np.ndarray], pairs: List[Tuple[str, str]]) -> List[float]:
    """Return cosine similarities for each (w1, w2) pair. Skip missing."""
    out = []
    for w1, w2 in pairs:
        if w1 not in vectors_by_word or w2 not in vectors_by_word:
            continue
        v1 = vectors_by_word[w1]
        v2 = vectors_by_word[w2]
        n1 = float(np.linalg.norm(v1))
        n2 = float(np.linalg.norm(v2))
        if n1 < 1e-12 or n2 < 1e-12:
            continue
        out.append(float(np.dot(v1, v2) / (n1 * n2)))
    return out


def _char_trigram_vector(word: str, n_dim: int) -> np.ndarray:
    """Substrate char-trigram bipolar HV for a word (orthographic spoke).

    Uses the substrate's CharTrigramEncoder via direct import (no LLM, no external model).
    """
    from hdlab.char_trigram_encoder import CharTrigramEncoder
    enc = CharTrigramEncoder(n_dim=n_dim)
    return enc.encode(word).astype(np.float32)


def _hub_spoke_bind(ri_context_vec: np.ndarray, ortho_vec: np.ndarray) -> np.ndarray:
    """Hub-spoke convergence: per-spoke L2-normalized bundling (Hebbian superposition).

    ATL hub-and-spoke (Patterson-Lambon Ralph 2007) is a CONVERGENCE zone: multiple
    modality-specific spokes project INTO the hub via Hebbian conjunctive coding
    (Bussey-Saksida perirhinal; CLS McClelland-McNaughton-O'Reilly 1995). The hub
    representation is the conjunctive sum of normalized spoke activations -- NOT a
    Hadamard binding (which would scramble both spokes into a third unrelated vector).

    Substrate primitive: L2-normalize each spoke (puts them on equal footing on the
    unit sphere), then sum. Substrate's bundling.bundle (sum + sign/L2-renorm) is the
    canonical operation; we use the dense float form for cosine evaluation rather than
    sign() bipolar quantization (preserves more graded info for the cosine probe).
    """
    a = ri_context_vec.astype(np.float32)
    b = ortho_vec.astype(np.float32)
    a_n = float(np.linalg.norm(a))
    b_n = float(np.linalg.norm(b))
    if a_n > 1e-12:
        a = a / a_n
    if b_n > 1e-12:
        b = b / b_n
    return (a + b).astype(np.float32)


def _build_word_vectors_for_arm(
    enc: RandomIndexingEncoder,
    arm: str,
    n_dim: int,
    probe_words: List[str],
) -> Dict[str, np.ndarray]:
    """For each probe word, build the per-arm vector representation."""
    out = {}
    if arm == "RANDOM_INDEXING_ALONE":
        for w in probe_words:
            if enc.has(w):
                out[w] = enc.encode(w).copy()
    elif arm == "RI_PLUS_BEAGLE_ORDER":
        # enc has order_binding=True; encode returns the BEAGLE-augmented context
        for w in probe_words:
            if enc.has(w):
                out[w] = enc.encode(w).copy()
    elif arm == "RI_HUB_SPOKE_KGSTORE":
        for w in probe_words:
            if enc.has(w):
                ri_vec = enc.encode(w)
                ortho = _char_trigram_vector(w, n_dim)
                out[w] = _hub_spoke_bind(ri_vec, ortho)
    elif arm == "CONTROL_RANDOM_PERMUTE":
        for w in probe_words:
            if enc.has(w):
                out[w] = enc.encode(w).copy()
    else:
        raise ValueError("unknown arm %r" % arm)
    return out


def _ratio_and_means(similar_cos: List[float], dissim_cos: List[float]) -> Tuple[float, float, float]:
    """Return (similar_mean, dissim_mean, ratio). Ratio = similar_mean / dissim_mean."""
    if not similar_cos or not dissim_cos:
        return (0.0, 0.0, 0.0)
    sm = float(np.mean(similar_cos))
    dm = float(np.mean(dissim_cos))
    if abs(dm) < 1e-9:
        ratio = float("inf") if sm > 0 else 0.0
    else:
        ratio = sm / dm
    return (sm, dm, ratio)


def run_unit(seed: int) -> dict:
    t0_unit = time.time()
    rng_corpus = np.random.default_rng(seed)
    print("  [seed=%d] loading text8 (max_tokens=%s)..." % (seed, str(MAX_TOKENS)), flush=True)
    tokens = _load_text8_tokens(MAX_TOKENS)
    print("  [seed=%d] loaded %d tokens" % (seed, len(tokens)), flush=True)

    # Build the canonical (in-order) encoders for arms 1, 2, 3
    print("  [seed=%d] fitting RI (bag-of-context)..." % seed, flush=True)
    t0 = time.time()
    enc_bag = RandomIndexingEncoder(N=N_DIM, sparsity=SPARSITY, window=WINDOW, min_count=MIN_COUNT, seed=seed, order_binding=False)
    enc_bag.fit_corpus(tokens)
    t_bag = time.time() - t0
    print("  [seed=%d] RI bag fit: vocab=%d, %.1fs" % (seed, enc_bag.vocab_size(), t_bag), flush=True)

    print("  [seed=%d] fitting RI+BEAGLE_ORDER..." % seed, flush=True)
    t0 = time.time()
    enc_order = RandomIndexingEncoder(N=N_DIM, sparsity=SPARSITY, window=WINDOW, min_count=MIN_COUNT, seed=seed, order_binding=True)
    enc_order.fit_corpus(tokens)
    t_order = time.time() - t0
    print("  [seed=%d] RI+BEAGLE fit: vocab=%d, %.1fs" % (seed, enc_order.vocab_size(), t_order), flush=True)

    # Build the position-shuffled encoder for the CONTROL arm
    print("  [seed=%d] shuffling corpus for CONTROL arm..." % seed, flush=True)
    shuffled = tokens.copy()
    rng_corpus.shuffle(shuffled)
    print("  [seed=%d] fitting RI on shuffled corpus..." % seed, flush=True)
    t0 = time.time()
    enc_ctrl = RandomIndexingEncoder(N=N_DIM, sparsity=SPARSITY, window=WINDOW, min_count=MIN_COUNT, seed=seed, order_binding=False)
    enc_ctrl.fit_corpus(shuffled)
    t_ctrl = time.time() - t0
    print("  [seed=%d] CONTROL fit: vocab=%d, %.1fs" % (seed, enc_ctrl.vocab_size(), t_ctrl), flush=True)

    # Filter probe set to vocab (use bag encoder's vocab; identical to order/ctrl vocabs since same tokens set)
    filtered = _filter_probe_to_vocab(enc_bag)
    probe_words = sorted({w for ws in filtered.values() for w in ws})
    similar, dissimilar = _build_probe_pairs(filtered)
    print("  [seed=%d] probe: %d categories, %d probe words, %d similar pairs, %d dissimilar pairs"
          % (seed, len(filtered), len(probe_words), len(similar), len(dissimilar)), flush=True)

    by_arm = {}
    arms_with_encoders = [
        ("RANDOM_INDEXING_ALONE", enc_bag),
        ("RI_PLUS_BEAGLE_ORDER", enc_order),
        ("RI_HUB_SPOKE_KGSTORE", enc_bag),  # uses bag encoder + binds char_trigram
        ("CONTROL_RANDOM_PERMUTE", enc_ctrl),
    ]
    for arm_name, enc_obj in arms_with_encoders:
        t_arm = time.time()
        vecs = _build_word_vectors_for_arm(enc_obj, arm_name, N_DIM, probe_words)
        sim_cos = _cosine_pairs(vecs, similar)
        dis_cos = _cosine_pairs(vecs, dissimilar)
        sm, dm, ratio = _ratio_and_means(sim_cos, dis_cos)
        by_arm[arm_name] = {
            "n_similar": len(sim_cos),
            "n_dissimilar": len(dis_cos),
            "similar_mean_cos": round(sm, 4),
            "dissim_mean_cos": round(dm, 4),
            "ratio": round(ratio, 4),
            "similar_std_cos": round(float(np.std(sim_cos)) if sim_cos else 0.0, 4),
            "dissim_std_cos": round(float(np.std(dis_cos)) if dis_cos else 0.0, 4),
            "wall_s_arm": round(time.time() - t_arm, 2),
        }
        a = by_arm[arm_name]
        print("  [seed=%d arm=%s] sim=%.3f dis=%.3f ratio=%.3f (n_sim=%d n_dis=%d)"
              % (seed, arm_name, a["similar_mean_cos"], a["dissim_mean_cos"], a["ratio"],
                 a["n_similar"], a["n_dissimilar"]), flush=True)

    return {
        "seed": seed,
        "by_arm": by_arm,
        "n_tokens": len(tokens),
        "vocab_size_bag": enc_bag.vocab_size(),
        "vocab_size_order": enc_order.vocab_size(),
        "vocab_size_ctrl": enc_ctrl.vocab_size(),
        "n_probe_words": len(probe_words),
        "n_similar_pairs": len(similar),
        "n_dissimilar_pairs": len(dissimilar),
        "fit_wall_s_bag": round(t_bag, 2),
        "fit_wall_s_order": round(t_order, 2),
        "fit_wall_s_ctrl": round(t_ctrl, 2),
        "unit_wall_s": round(time.time() - t0_unit, 2),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }


def compute_verdict(units: List[dict]) -> Tuple[str, str, dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})
    arm_names = ["RANDOM_INDEXING_ALONE", "RI_PLUS_BEAGLE_ORDER", "RI_HUB_SPOKE_KGSTORE", "CONTROL_RANDOM_PERMUTE"]
    by_arm_agg = {}
    for arm in arm_names:
        ratios = [u["by_arm"][arm]["ratio"] for u in units if arm in u["by_arm"]]
        sims = [u["by_arm"][arm]["similar_mean_cos"] for u in units if arm in u["by_arm"]]
        diss = [u["by_arm"][arm]["dissim_mean_cos"] for u in units if arm in u["by_arm"]]
        if not ratios:
            by_arm_agg[arm] = {"ratio_mean": 0.0, "ratio_std": 0.0, "ratio_cv": 0.0,
                               "similar_mean": 0.0, "dissim_mean": 0.0, "n_seeds": 0}
            continue
        r_mean = float(np.mean(ratios))
        r_std = float(np.std(ratios))
        r_cv = r_std / max(abs(r_mean), 1e-6)
        by_arm_agg[arm] = {
            "ratio_mean": round(r_mean, 4),
            "ratio_std": round(r_std, 4),
            "ratio_cv": round(r_cv, 4),
            "similar_mean": round(float(np.mean(sims)), 4),
            "dissim_mean": round(float(np.mean(diss)), 4),
            "n_seeds": len(ratios),
        }
    substantive = ["RANDOM_INDEXING_ALONE", "RI_PLUS_BEAGLE_ORDER", "RI_HUB_SPOKE_KGSTORE"]
    ctrl = "CONTROL_RANDOM_PERMUTE"
    sub_ratios = [by_arm_agg[a]["ratio_mean"] for a in substantive]
    sub_cvs = [by_arm_agg[a]["ratio_cv"] for a in substantive]
    ctrl_ratio = by_arm_agg[ctrl]["ratio_mean"]
    n_seeds = len(units)

    headline_arm = "RANDOM_INDEXING_ALONE"
    headline_ratio = by_arm_agg[headline_arm]["ratio_mean"]
    headline_cv = by_arm_agg[headline_arm]["ratio_cv"]

    detail = {
        "by_arm_agg": by_arm_agg,
        "headline_arm": headline_arm,
        "headline_ratio_mean": headline_ratio,
        "headline_ratio_cv": headline_cv,
        "control_ratio_mean": ctrl_ratio,
        "all_substantive_pass_15x": all(r >= 1.5 for r in sub_ratios),
        "any_substantive_fail_11x": any(r < 1.1 for r in sub_ratios),
        "control_is_null": ctrl_ratio <= 1.1,
        "control_breaks_probe": ctrl_ratio > 1.3,
        "max_substantive_cv": round(max(sub_cvs), 4) if sub_cvs else None,
        "n_seeds": n_seeds,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "text8 corpus (~17M tokens full / 200k smoke); N_DIM=%d; sparsity=%d; "
            "window=%d; substrate-only (no LLM at any stage); handcrafted probe set "
            "(7 categories, capped 100 similar / 100 dissimilar pairs)"
        ) % (N_DIM, SPARSITY, WINDOW),
        "cites": [
            "research_brain_drill_substrate_native_relational_semantic_encoding_5x_DEEPER_2026-06-22",
            "Sahlgren_2005_random_indexing",
            "Kanerva_1988_sparse_distributed_memory",
            "Jones_Mewhort_2007_BEAGLE",
            "Patterson_Nestor_Rogers_2007_ATL_hub_and_spoke",
            "CERT_585_char_trigram_encoder",
        ],
    }
    summary = (
        "ratios: RI_alone=%.3f BEAGLE=%.3f hub_spoke=%.3f CONTROL=%.3f | CVs: RI=%.3f BEAGLE=%.3f hub=%.3f"
        % (
            by_arm_agg["RANDOM_INDEXING_ALONE"]["ratio_mean"],
            by_arm_agg["RI_PLUS_BEAGLE_ORDER"]["ratio_mean"],
            by_arm_agg["RI_HUB_SPOKE_KGSTORE"]["ratio_mean"],
            by_arm_agg["CONTROL_RANDOM_PERMUTE"]["ratio_mean"],
            by_arm_agg["RANDOM_INDEXING_ALONE"]["ratio_cv"],
            by_arm_agg["RI_PLUS_BEAGLE_ORDER"]["ratio_cv"],
            by_arm_agg["RI_HUB_SPOKE_KGSTORE"]["ratio_cv"],
        )
    )

    # HARD_PASS: all 3 substantive >= 1.5x; CONTROL <= 1.1; max CV <= 0.20
    if all(r >= 1.5 for r in sub_ratios) and ctrl_ratio <= 1.1 and max(sub_cvs) <= 0.20:
        return (
            "HARD_PASS",
            "DISCRIMINATOR HARD_PASS: substrate-native distributional semantics WORKS. "
            "All 3 substantive arms (RI / RI+BEAGLE / RI hub-spoke) achieve "
            "similar/dissimilar cosine ratio >= 1.5x; CONTROL_RANDOM_PERMUTE collapses "
            "to %.3f (<=1.1 null). Max substantive CV=%.3f (<=0.20). "
            "Substrate has substrate-native semantic encoder via Hebbian co-occurrence "
            "accumulation; zero LLM at any stage. " % (ctrl_ratio, max(sub_cvs)) + summary,
            detail,
        )
    # HARD_FAIL: any substantive < 1.1 (no signal) OR control > 1.3 (probe is broken)
    if any(r < 1.1 for r in sub_ratios):
        which = [a for a, r in zip(substantive, sub_ratios) if r < 1.1]
        return (
            "HARD_FAIL",
            "DISCRIMINATOR HARD_FAIL: substantive arm(s) %s show ratio < 1.1 "
            "(no distributional signal). Substrate-native RI insufficient at this "
            "config / corpus / N_DIM. " % which + summary,
            detail,
        )
    if ctrl_ratio > 1.3:
        return (
            "HARD_FAIL",
            "DISCRIMINATOR HARD_FAIL: CONTROL_RANDOM_PERMUTE arm ratio=%.3f > 1.3; "
            "the probe leaks signal even when corpus is shuffled. Probe construction or "
            "encoder has a bug; cannot trust substantive ratios. " % ctrl_ratio + summary,
            detail,
        )
    return (
        "MIDDLE_BAND",
        "MIDDLE_BAND: substrate-native distributional signal is real but partial. "
        "Substantive ratios=%s; CONTROL=%.3f; max_cv=%.3f. Per by-construction-saturation "
        "discipline, this is MEASURED_MECHANISM not chain-grade win; consider lever "
        "(N_DIM up, window tuning, BEAGLE-only, or hub-spoke composition variant). "
        % ([round(r, 3) for r in sub_ratios], ctrl_ratio, max(sub_cvs)) + summary,
        detail,
    )


# atexit / SIGTERM synthesize from partials (Fix #11 TODO #9)
_METRICS_WRITTEN = [False]
_OUT_DIR_REF: List[Path | None] = [None]
_T0_REF: List[float | None] = [None]


def _synthesize_on_exit() -> None:
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = (
                "PARTIAL_TIMEOUT",
                "atexit synthesize: compute_verdict failed: %s" % e,
                {"n_seeds_recovered": len(units)},
            )
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "sparsity": SPARSITY,
            "window": WINDOW,
            "min_count": MIN_COUNT,
            "max_tokens": MAX_TOKENS,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_n11_random_indexing_semantic_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg),
            "zero_llm_calls_at_inference": True,
            "n_llm_calls": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


def _selftest() -> None:
    """Cell wiring selftest: imports, probe construction, ratio math, arm coverage."""
    # 1. Primitive selftest delegated
    from hdlab.random_indexing import _selftest as ri_selftest
    ri_selftest()
    # 2. Probe categories non-empty
    assert len(_PROBE_CATEGORIES) >= 5
    for cat, ws in _PROBE_CATEGORIES.items():
        assert len(ws) >= 4, "category %s too small" % cat
    # 3. Tiny in-memory corpus: cat/dog appear in similar contexts, car appears separately
    toks = (
        "the cat ate food the dog ate food the cat sleeps the dog sleeps "
        "the car drives fast the car parks here the engine runs the wheel turns"
    ).split() * 50
    enc = RandomIndexingEncoder(N=2048, sparsity=8, window=3, min_count=2, seed=0, order_binding=False)
    enc.fit_corpus(toks)
    # cat-dog should be more similar than cat-car
    s_cd = enc.similarity("cat", "dog")
    s_cc = enc.similarity("cat", "car")
    print("[selftest] toy corpus: cat-dog=%.3f cat-car=%.3f" % (s_cd, s_cc), flush=True)
    assert s_cd > s_cc, "toy corpus: cat-dog should exceed cat-car (got %.3f vs %.3f)" % (s_cd, s_cc)
    # 4. Hub-spoke binding shapes correct
    ri_vec = enc.encode("cat")
    ortho = _char_trigram_vector("cat", enc.N)
    hs = _hub_spoke_bind(ri_vec, ortho)
    assert hs.shape == (enc.N,), "hub-spoke shape mismatch"
    # 5. Ratio math
    sm, dm, r = _ratio_and_means([0.8, 0.6, 0.7], [0.2, 0.3, 0.1])
    assert abs(sm - 0.7) < 1e-6 and abs(dm - 0.2) < 1e-6
    assert abs(r - 3.5) < 1e-3, "ratio math broken (got %.3f, expected 3.5)" % r
    # 6. verdict logic: synthetic HARD_PASS case
    fake_unit = {
        "seed": 0,
        "by_arm": {
            "RANDOM_INDEXING_ALONE":      {"ratio": 2.0, "similar_mean_cos": 0.6, "dissim_mean_cos": 0.3},
            "RI_PLUS_BEAGLE_ORDER":       {"ratio": 1.8, "similar_mean_cos": 0.55, "dissim_mean_cos": 0.31},
            "RI_HUB_SPOKE_KGSTORE":       {"ratio": 1.7, "similar_mean_cos": 0.5, "dissim_mean_cos": 0.29},
            "CONTROL_RANDOM_PERMUTE":     {"ratio": 1.0, "similar_mean_cos": 0.4, "dissim_mean_cos": 0.4},
        },
    }
    verdict, msg, detail = compute_verdict([fake_unit, fake_unit, fake_unit])
    assert verdict == "HARD_PASS", "synthetic HARD_PASS case failed verdict logic (got %s)" % verdict
    # 7. Synthetic HARD_FAIL case
    bad_unit = {
        "seed": 0,
        "by_arm": {
            "RANDOM_INDEXING_ALONE":      {"ratio": 0.9, "similar_mean_cos": 0.3, "dissim_mean_cos": 0.33},
            "RI_PLUS_BEAGLE_ORDER":       {"ratio": 1.5, "similar_mean_cos": 0.45, "dissim_mean_cos": 0.3},
            "RI_HUB_SPOKE_KGSTORE":       {"ratio": 1.5, "similar_mean_cos": 0.45, "dissim_mean_cos": 0.3},
            "CONTROL_RANDOM_PERMUTE":     {"ratio": 1.0, "similar_mean_cos": 0.4, "dissim_mean_cos": 0.4},
        },
    }
    verdict, msg, detail = compute_verdict([bad_unit])
    assert verdict == "HARD_FAIL", "synthetic HARD_FAIL case failed verdict logic (got %s)" % verdict
    print("[selftest] PASS: ri-primitive, probe, toy distributional, hub-spoke, ratio math, verdict logic", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print(
        "[config] %s mode=%s N=%d sparsity=%d window=%d min_count=%d max_tokens=%s seeds=%s name_says_smoke=%s | %s"
        % (
            ANCHOR_NAME,
            RUN_MODE,
            N_DIM,
            SPARSITY,
            WINDOW,
            MIN_COUNT,
            str(MAX_TOKENS),
            SEEDS,
            _NAME_SAYS_SMOKE,
            CONFIG_VERSION,
        ),
        flush=True,
    )
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "sparsity": SPARSITY,
        "window": WINDOW,
        "min_count": MIN_COUNT,
        "max_tokens": MAX_TOKENS,
        "schema": "n11-random-indexing-semantic-v1",
    }
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "sparsity": SPARSITY,
        "window": WINDOW,
        "min_count": MIN_COUNT,
        "max_tokens": MAX_TOKENS,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_n11_random_indexing_semantic_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "zero_llm_calls_at_inference": True,
        "n_llm_calls": _LLM_CALL_COUNTER[0],
        "_name_says_smoke_workaround": _NAME_SAYS_SMOKE,
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
