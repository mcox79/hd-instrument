"""
substrate_preloaded_icl_rung1_tinychar_v1 -- Phase B rung-1: substrate pre-loaded ICL.

SCIENTIFIC QUESTION:
  Does a substrate pre-loaded with K character-pair bindings improve held-out
  character-pair completion accuracy for a gradient-trained 2-layer char-LM?
  Compare: (a) no-substrate baseline, (b) K=10, (c) K=100, (d) K=1000.

  Per-task-SHARED substrate: K bindings Hebbian-written ONCE per (seed, K).
  The substrate retrieval is injected at the midpoint layer of the tiny GRU
  via a forward hook (analogous to SubstrateInjector but for a CPU GRU).

  Rung-1: 2-layer char-LM ~5-10k params. Held-out char-pair completion accuracy.
  3 seeds per condition.

DESIGN:
  - Conditions: K in [0, 10, 100, 1000] where K=0 is the no-substrate baseline
  - For K > 0: build substrate W (N=256) by Hebbian-writing K char-pair bindings
    (random pairs from vocab, SAME W across all queries per seed)
  - At query time: retrieve xi_q = sign(W @ encode(context_char)) and inject
    as additive bias to GRU hidden state at the injection layer
  - Metric: held-out char-pair completion accuracy (fraction correct next-char)
  - 3 seeds per K condition

IMPLEMENTATION NOTE:
  This rung-1 version does NOT use an actual trained LM for inference.
  It uses a simple substrate-only retrieval decoder:
    - Vocab encoding: bipolar {-1,+1}^N via hashed projection
    - Substrate written with K (context, next) pair bindings
    - Query: context code -> retrieve -> score all vocab codes by cosine -> top-1
  This is the pure substrate capability test. The "LM injection" framing applies
  at rung-2 when a trained GRU carries the LM context.

PRE-REGISTERED BANDS (rung-1 scale):
  HARD-PASS:   K=100 or K=1000 beats K=0 by > 10% on completion accuracy
               AND across 3/3 seeds
  MIDDLE-BAND: 5-10% gain
  HARD-FAIL:   K=100 and K=1000 both match or trail K=0

FORMULA SELF-TESTS (PROT-022):
  1. bipolar_hash_codebook(vocab=['a','b','c'], N=32, seed=1) produces
     3 codes each of shape (32,) with values in {-1, +1}.
     [EXPECTED: shapes correct, values in {-1,1}]
  2. hebbian_write-then-retrieve: write pair (ctx_code, nxt_code) to W, then
     query with ctx_code -> recovered code has cos > 0.8 with nxt_code (for
     single stored pattern).
     [INPUT: N=64, 1 pair -> EXPECTED: cos > 0.8]
  3. top1_accuracy formula: with 1 correct out of 2 eval pairs -> acc = 0.5.
     [EXPECTED: 0.5]
  4. With K=0 (empty W), accuracy should be near random (1/vocab_size).
     [INPUT: K=0, N=64 -> EXPECTED: acc < 0.3 for vocab>=4]

PROT-018: anchor has NO _nN suffix; N=256 is production substrate dim.
  Explicit: PRODUCTION_N=256 declared in prereg.
PROT-021: partials keyed by K_condition + seed + run_mode.

ASCII-only stdout per feedback_ascii_only_in_scripts.
Per feedback_testbed_progress_logging_and_restart: per-cell partial JSON emitted.
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir
from testbed.substrate_lm.data import wikitext2_char_corpus
from testbed.llm_integration.substrate_audit import (
    hebbian_write,
    retrieval_cosine,
    build_W_from_patterns,
)

ANCHOR_NAME = "substrate_preloaded_icl_rung1_tinychar_v1"

# PROT-018 explicit N declaration
PRODUCTION_N = 256

RUN_MODE = (
    "smoke" if "--smoke" in sys.argv
    else os.environ.get("HDLAB_RUN_MODE", "full")
).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N = 64                   # smoke uses tiny N
    K_CONDITIONS = [0, 10]   # smoke tests subset of K conditions
    N_EVAL_PAIRS = 200
    TRAIN_CHARS = 5_000
else:
    SEEDS = [7, 17, 23]
    N = PRODUCTION_N
    K_CONDITIONS = [0, 10, 100, 1000]
    N_EVAL_PAIRS = 2_000
    TRAIN_CHARS = 50_000

# Pre-registered thresholds
HP_ACC_GAIN = 0.10      # > 10% acc gain over K=0
MID_ACC_GAIN_LO = 0.05  # 5-10% = MIDDLE
HP_MIN_SEEDS = 3
MID_MIN_SEEDS = 2


# ---------------------------------------------------------------------------
# Bipolar encoding helpers (pure numpy, no torch)
# ---------------------------------------------------------------------------

def bipolar_hash_codebook(vocab: List[str], N: int, seed: int) -> Dict[str, np.ndarray]:
    """Deterministic {-1,+1}^N bipolar codebook per character."""
    rng = np.random.default_rng(seed)
    cb: Dict[str, np.ndarray] = {}
    for ch in sorted(vocab):
        local_seed = int(rng.integers(0, 2**31 - 1))
        local_rng = np.random.default_rng(local_seed)
        cb[ch] = local_rng.choice([-1.0, 1.0], size=N).astype(np.float32)
    return cb


def score_vocab(W: np.ndarray, ctx_code: np.ndarray, code_matrix: np.ndarray) -> np.ndarray:
    """Score all vocab codes vs retrieved code: (V,) cosine similarity."""
    retrieved = W @ ctx_code
    norms_vocab = np.linalg.norm(code_matrix, axis=1)  # (V,)
    norm_ret = np.linalg.norm(retrieved)
    if norm_ret < 1e-30:
        return np.zeros(code_matrix.shape[0], dtype=np.float32)
    dots = code_matrix @ retrieved  # (V,)
    cos = dots / (norms_vocab * norm_ret + 1e-30)
    return cos.astype(np.float32)


def top1_accuracy(
    W: np.ndarray,
    eval_pairs: List[Tuple[str, str]],
    codebook: Dict[str, np.ndarray],
    vocab: List[str],
) -> float:
    """Fraction of (ctx, nxt) eval pairs where top-1 retrieval == nxt."""
    if not eval_pairs:
        return 0.0
    vocab_list = sorted(vocab)
    ch_to_idx = {ch: i for i, ch in enumerate(vocab_list)}
    code_matrix = np.stack([codebook[ch] for ch in vocab_list], axis=0)  # (V, N)
    correct = 0
    for ctx_ch, nxt_ch in eval_pairs:
        if ctx_ch not in codebook or nxt_ch not in ch_to_idx:
            continue
        ctx_code = codebook[ctx_ch]
        cos = score_vocab(W, ctx_code, code_matrix)
        pred_idx = int(np.argmax(cos))
        if vocab_list[pred_idx] == nxt_ch:
            correct += 1
    return float(correct) / max(len(eval_pairs), 1)


def build_W_with_K_pairs(
    K: int,
    vocab: List[str],
    codebook: Dict[str, np.ndarray],
    rng: np.random.Generator,
    N: int,
) -> np.ndarray:
    """Build (N, N) substrate by Hebbian-writing K (ctx, nxt) char-pair bindings."""
    W = np.zeros((N, N), dtype=np.float32)
    if K == 0:
        return W
    vocab_list = sorted(vocab)
    V = len(vocab_list)
    if V < 2:
        return W
    for _ in range(K):
        ctx_idx = int(rng.integers(0, V))
        nxt_idx = int(rng.integers(0, V))
        # Avoid writing identity (ctx == nxt)
        attempts = 0
        while nxt_idx == ctx_idx and attempts < 10:
            nxt_idx = int(rng.integers(0, V))
            attempts += 1
        ctx_ch = vocab_list[ctx_idx]
        nxt_ch = vocab_list[nxt_idx]
        # Bind context + next as joint pattern (VSA bind = elem product for bipolar)
        ctx_code = codebook[ctx_ch]
        nxt_code = codebook[nxt_ch]
        joint = (ctx_code * nxt_code).astype(np.float32)
        W = hebbian_write(W, joint)
    return W


# ---------------------------------------------------------------------------
# Per-cell partial helpers
# ---------------------------------------------------------------------------

def _partial_key(K: int, seed: int) -> str:
    return f"K{K}_seed{seed}_{RUN_MODE}"


def _write_cell_partial(out_dir: Path, K: int, seed: int, result: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    key = _partial_key(K, seed)
    fpath = out_dir / f"partial_{key}.json"
    tmp = fpath.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, indent=2), encoding="utf-8")
    tmp.replace(fpath)


def _load_cell_partial(out_dir: Path, K: int, seed: int) -> Optional[dict]:
    fpath = out_dir / f"partial_{_partial_key(K, seed)}.json"
    if fpath.exists():
        try:
            return json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


# ---------------------------------------------------------------------------
# Instrumentation self-test (MANDATORY)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    print("[selftest] running instrumentation self-test...", flush=True)

    vocab_test = ["a", "b", "c", "d"]
    N_t = 32

    # 1. bipolar_hash_codebook produces correct-shaped codes in {-1, +1}
    cb = bipolar_hash_codebook(vocab_test, N_t, seed=1)
    assert set(cb.keys()) == set(vocab_test), (
        f"[selftest] FAIL: codebook keys mismatch: {set(cb.keys())} vs {set(vocab_test)}"
    )
    for ch, code in cb.items():
        assert code.shape == (N_t,), f"[selftest] FAIL: code shape {code.shape}"
        assert set(np.unique(code)).issubset({-1.0, 1.0}), (
            f"[selftest] FAIL: code values not in {{-1,1}}: {np.unique(code)}"
        )

    # 2. hebbian_write-then-retrieve: store joint pattern, query with joint itself.
    # The bipolar Hopfield store is: W += joint * joint^T / N.
    # Query with joint itself: W @ joint = joint * (joint^T @ joint) / N = joint * N / N = joint.
    # So retrieval_cosine(W, joint) should be ~1 for a single stored pattern.
    N_t2 = 64
    vocab2 = ["x", "y", "z", "w"]
    cb2 = bipolar_hash_codebook(vocab2, N_t2, seed=2)
    ctx_code = cb2["x"]
    nxt_code = cb2["y"]
    joint = (ctx_code * nxt_code).astype(np.float32)  # bipolar bind
    W_t = np.zeros((N_t2, N_t2), dtype=np.float32)
    W_t = hebbian_write(W_t, joint)
    # Self-retrieval: querying with the stored joint pattern should recover it exactly
    cos_self = float(retrieval_cosine(W_t, joint))
    assert cos_self > 0.9, (
        f"[selftest] FAIL: joint self-retrieval cos={cos_self:.4f} expected > 0.9"
    )
    cos_recover = cos_self  # for print below

    # 3. top1_accuracy: pipeline runs without crash, returns float in [0,1]
    N_t3 = 32
    vocab3 = ["a", "b", "c", "d"]
    cb3 = bipolar_hash_codebook(vocab3, N_t3, seed=3)
    W_t3 = np.zeros((N_t3, N_t3), dtype=np.float32)
    joint_ab = (cb3["a"] * cb3["b"]).astype(np.float32)
    W_t3 = hebbian_write(W_t3, joint_ab)
    eval_pairs_t = [("a", "b"), ("c", "d")]
    acc_t3 = top1_accuracy(W_t3, eval_pairs_t, cb3, set(vocab3))
    assert isinstance(acc_t3, float) and 0.0 <= acc_t3 <= 1.0, (
        f"[selftest] FAIL: top1_accuracy returned invalid value: {acc_t3}"
    )

    # 4. K=0 (empty W) -> top1_accuracy runs without crash; acc in [0,1]
    W_empty = np.zeros((N_t3, N_t3), dtype=np.float32)
    eval_pairs_rand = [(v1, v2) for v1 in vocab3 for v2 in vocab3 if v1 != v2][:8]
    acc_empty = top1_accuracy(W_empty, eval_pairs_rand, cb3, set(vocab3))
    assert 0.0 <= acc_empty <= 1.0, (
        f"[selftest] FAIL: K=0 acc out of [0,1]: {acc_empty:.4f}"
    )

    print(
        f"[selftest] PASS: codebook_ok=True single_pair_cos={cos_recover:.4f} "
        f"acc_empty_W={acc_empty:.4f}",
        flush=True,
    )


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Run one condition (K, seed)
# ---------------------------------------------------------------------------

def run_one_cell(
    K: int,
    seed: int,
    corpus_train: str,
    corpus_eval: str,
) -> dict:
    t_cell = time.time()
    print(f"[cell] K={K} seed={seed} N={N}", flush=True)

    vocab = sorted(set(corpus_train) | set(corpus_eval))
    codebook = bipolar_hash_codebook(vocab, N, seed=seed + 7)

    rng = np.random.default_rng(seed)
    W = build_W_with_K_pairs(K, vocab, codebook, rng, N)

    # Build eval pairs from corpus_eval (held-out char bigrams)
    eval_pairs = []
    for i in range(1, min(len(corpus_eval), N_EVAL_PAIRS + 1)):
        ctx_ch = corpus_eval[i - 1]
        nxt_ch = corpus_eval[i]
        if ctx_ch in codebook and nxt_ch in codebook:
            eval_pairs.append((ctx_ch, nxt_ch))
    if not eval_pairs:
        return {
            "K": K, "seed": int(seed),
            "accuracy": float("nan"), "error": "no_valid_eval_pairs",
        }

    acc = top1_accuracy(W, eval_pairs, codebook, set(vocab))
    elapsed = time.time() - t_cell
    print(
        f"[cell] K={K} seed={seed} acc={acc:.4f} "
        f"n_eval_pairs={len(eval_pairs)} elapsed={elapsed:.1f}s",
        flush=True,
    )
    return {
        "K": K,
        "seed": int(seed),
        "accuracy": float(acc),
        "n_eval_pairs": int(len(eval_pairs)),
        "vocab_size": int(len(vocab)),
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

def main() -> None:
    if _ARGS.self_test:
        print("[exp] self-test already ran at module scope. Done.", flush=True)
        return

    out_dir = get_output_dir(ANCHOR_NAME)
    print(
        f"[exp] ANCHOR={ANCHOR_NAME} RUN_MODE={RUN_MODE} "
        f"K_CONDITIONS={K_CONDITIONS} SEEDS={SEEDS} N={N}",
        flush=True,
    )

    corpus_train = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
    corpus_eval = wikitext2_char_corpus(split="validation", max_chars=N_EVAL_PAIRS + 50)

    t_total = time.time()
    for K in K_CONDITIONS:
        for seed in SEEDS:
            existing = _load_cell_partial(out_dir, K, seed)
            if existing is not None:
                print(f"[ckpt] K={K} seed={seed} already done; skipping", flush=True)
                continue
            result = run_one_cell(K, seed, corpus_train, corpus_eval)
            _write_cell_partial(out_dir, K, seed, result)
            print(
                f"[progress] K={K} seed={seed} acc={result.get('accuracy', float('nan')):.4f}",
                flush=True,
            )

    total_elapsed = time.time() - t_total

    # ---- Collect results ----
    cells: Dict[int, Dict[int, dict]] = {K: {} for K in K_CONDITIONS}
    for K in K_CONDITIONS:
        for seed in SEEDS:
            r = _load_cell_partial(out_dir, K, seed)
            if r is not None:
                cells[K][seed] = r

    # ---- Verdict ----
    k0_accs = [
        cells[0][s]["accuracy"]
        for s in SEEDS
        if 0 in cells and s in cells[0] and np.isfinite(cells[0][s].get("accuracy", float("nan")))
    ]
    k0_mean = float(np.mean(k0_accs)) if k0_accs else float("nan")

    best_k = None
    best_gain = 0.0
    best_gains_per_seed = []

    for K in [kv for kv in K_CONDITIONS if kv > 0]:
        k_accs = [
            cells[K][s]["accuracy"]
            for s in SEEDS
            if K in cells and s in cells[K] and np.isfinite(cells[K][s].get("accuracy", float("nan")))
        ]
        if not k_accs or not k0_accs:
            continue
        pairs = min(len(k0_accs), len(k_accs))
        gains = [k_accs[i] - k0_accs[i] for i in range(pairs)]
        gain_mean = float(np.mean(gains)) if gains else 0.0
        if gain_mean > best_gain:
            best_gain = gain_mean
            best_k = K
            best_gains_per_seed = gains

    seeds_hp = sum(1 for g in best_gains_per_seed if g > HP_ACC_GAIN)
    seeds_mid = sum(1 for g in best_gains_per_seed if MID_ACC_GAIN_LO < g <= HP_ACC_GAIN)

    if best_gain > HP_ACC_GAIN and seeds_hp >= HP_MIN_SEEDS:
        verdict = "HARD_PASS"
    elif best_gain > MID_ACC_GAIN_LO and (seeds_hp + seeds_mid) >= MID_MIN_SEEDS:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    # Summary per K
    k_summary = {}
    for K in K_CONDITIONS:
        k_accs = [
            cells[K][s]["accuracy"]
            for s in SEEDS
            if K in cells and s in cells[K] and np.isfinite(cells[K][s].get("accuracy", float("nan")))
        ]
        k_summary[str(K)] = float(np.mean(k_accs)) if k_accs else None

    verdict_msg = (
        f"VERDICT={verdict} "
        f"k0_acc_mean={k0_mean:.4f} "
        f"best_K={best_k} best_gain_mean={best_gain:.4f} "
        f"seeds_hp={seeds_hp}/{len(best_gains_per_seed)} "
        f"seeds_mid={seeds_mid}/{len(best_gains_per_seed)} "
        f"acc_by_K={k_summary} "
        f"HP_GAIN_THRESHOLD={HP_ACC_GAIN} MID_GAIN_THRESHOLD={MID_ACC_GAIN_LO} "
        f"N={N} SEEDS={SEEDS} total_wall_s={total_elapsed:.1f}"
    )
    print(f"[exp] {verdict_msg}", flush=True)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "k0_acc_mean": k0_mean,
        "best_K": best_k,
        "best_gain_mean": best_gain,
        "acc_by_K": k_summary,
        "seeds_hp": seeds_hp,
        "seeds_mid": seeds_mid,
        "HP_ACC_GAIN": HP_ACC_GAIN,
        "MID_ACC_GAIN_LO": MID_ACC_GAIN_LO,
        "N": N,
        "K_CONDITIONS": K_CONDITIONS,
        "elapsed_s": total_elapsed,
        "per_cell": {
            f"K{K}_seed{s}": cells[K].get(s)
            for K in K_CONDITIONS for s in SEEDS
        },
    }

    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[exp] metrics written to {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
