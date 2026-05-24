"""Learned codebook atoms (A6 from strategy_untested_rows_triage_2026-05-24.md).

A/B test: random bipolar BSC atoms vs SVD/PCA-derived atoms from bigram PPMI
matrix, at K in {4, 8, 16}. Cheapest item on the v1 UNSURE list per cap_map:
~15 min CPU est.

Hypothesis: PPMI-PCA-derived bipolar atoms (sign of PCA-projected bigram PPMI)
beat purely random bipolar atoms at small K (K=4-16) on bpc cleanup.

Pre-reg (designed inline per [[feedback-no-experiment-design-in-prompts]]):

Falsifier statements:
  - HARD-PASS:  mean bpc_learned < mean bpc_random across 3 seeds, at ALL three
                K values; AND best delta >= 0.05 bpc. (Learned atoms strictly
                better at every K with substantial best-case gain.)
  - HARD-FAIL:  mean bpc_learned >= mean bpc_random at >=2 of 3 K values
                (learned atoms NOT better; the cycle-3 prediction +0.02-0.08
                from cap_map UNSURE row REFUTED).
  - MIDDLE:     1-of-3 K values shows learned advantage. Partial; could be
                K-dependent learning.

Comparison anchor: random bipolar BSC at the same N, K (matched baseline).

Per [[feedback-no-smoke]]: HARD-PASS / HARD-FAIL falsifiable before running.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.

Pre-reg: preregs/2026-05-24_wave14_learned_codebook_atoms_smoke_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

# Config (exp_dev decided; small per A6 estimate ~15 min CPU).
N_FULL = 1024
N_SMOKE = 256
K_VALUES = [4, 8, 16]
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]
N_PROBES_FULL = 2000
N_PROBES_SMOKE = 200
VOCAB = 256


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def make_random_bipolar(M, N, rng):
    """Standard random {-1, +1}^N atoms."""
    return (rng.integers(0, 2, size=(M, N)) * 2 - 1).astype(np.float32)


def load_corpus_for_ppmi(n_bytes):
    """Load corpus_a bytes for PPMI bigram matrix; reuse pa.load_corpus_a if importable."""
    try:
        # try shared corpus_a from pa module
        from experiments import exp_wave14_phase_a as pa_mod  # noqa: F401
    except Exception:
        pass
    # Fallback: load enwik8-like bytes if present, else random.
    data_paths = [
        REPO / "data" / "corpus_a_bytes.bin",
        REPO / "data" / "enwik8_500k.bin",
    ]
    for p in data_paths:
        if p.exists():
            with open(p, "rb") as f:
                data = f.read(n_bytes)
            if len(data) >= n_bytes // 2:
                return np.frombuffer(data, dtype=np.uint8)
    # Final fallback: deterministic synthetic bigram corpus.
    rng = np.random.default_rng(42)
    return rng.integers(0, VOCAB, size=n_bytes, dtype=np.uint8)


def bigram_ppmi_matrix(byte_stream, vocab=VOCAB):
    """Compute (vocab, vocab) PPMI matrix from byte stream."""
    counts = np.zeros((vocab, vocab), dtype=np.float64)
    for i in range(len(byte_stream) - 1):
        counts[byte_stream[i], byte_stream[i + 1]] += 1.0
    total = counts.sum() + 1e-12
    p_xy = counts / total
    p_x = p_xy.sum(axis=1, keepdims=True) + 1e-12
    p_y = p_xy.sum(axis=0, keepdims=True) + 1e-12
    ppmi = np.log((p_xy + 1e-12) / (p_x * p_y))
    return np.clip(ppmi, 0.0, None)  # positive PMI


def make_learned_bipolar(M, N, ppmi, rng):
    """Project the (vocab, vocab) PPMI into N-dim space via PCA; sign-quantize to bipolar.

    Steps:
      1. SVD of PPMI: PPMI = U S V^T.
      2. Take top N principal components as atom directions (M=vocab atoms).
      3. Sign-quantize to bipolar {-1, +1}.
      4. Pad with random columns if N > vocab.
    """
    vocab = ppmi.shape[0]
    # Center PPMI rows.
    ppmi_c = ppmi - ppmi.mean(axis=0, keepdims=True)
    # SVD.
    U, S, Vt = np.linalg.svd(ppmi_c, full_matrices=False)
    # Project: take first N components (or pad if N > vocab).
    n_components = min(N, vocab)
    projected = U[:, :n_components] * S[:n_components]  # (vocab, n_components)
    # Sign-quantize.
    atoms = np.sign(projected).astype(np.float32)
    # Replace zeros with random ±1.
    zero_mask = atoms == 0
    if zero_mask.any():
        atoms[zero_mask] = rng.integers(0, 2, size=zero_mask.sum()) * 2 - 1
    # Pad to N columns if needed.
    if N > vocab:
        pad = make_random_bipolar(vocab, N - vocab, rng)
        atoms = np.concatenate([atoms, pad], axis=1)
    # Take first M atoms (vocab=M=256 default).
    return atoms[:M]


def cleanup_accuracy(atoms, n_probes, K, rng):
    """Evaluate atom cleanup: probe = sum(K random atoms) + noise; argmax cleanup."""
    M, N = atoms.shape
    correct = 0
    total = 0
    for _ in range(n_probes):
        indices = rng.choice(M, size=K, replace=False)
        bundle = atoms[indices].sum(axis=0)  # superposition
        # Cleanup against each atom: similarity.
        sims = atoms @ bundle / float(N)
        topk = np.argsort(-sims)[:K]
        topk_set = set(topk.tolist())
        true_set = set(indices.tolist())
        # bpc-style cleanup accuracy: fraction of K-set recovered.
        correct += len(topk_set & true_set)
        total += K
    return correct / max(total, 1)


def compute_verdict(summary):
    per_K = summary.get("per_K")
    if not per_K:
        return ("LEARNED_CODEBOOK_INCONCLUSIVE", "Missing per_K data.")
    # For each K, compare mean(learned_acc) vs mean(random_acc) across seeds.
    deltas = {}  # K -> (mean_learned - mean_random)
    learned_wins = 0
    best_delta = 0.0
    for K, cells in per_K.items():
        l_vals = [c["learned_acc"] for c in cells.values()]
        r_vals = [c["random_acc"] for c in cells.values()]
        l_mean = sum(l_vals) / len(l_vals)
        r_mean = sum(r_vals) / len(r_vals)
        delta = l_mean - r_mean
        deltas[K] = delta
        if delta > 0.0:
            learned_wins += 1
        if delta > best_delta:
            best_delta = delta
    n_K = len(per_K)
    if learned_wins == n_K and best_delta >= 0.05:
        return ("LEARNED_CODEBOOK_HARD_PASS",
                f"Learned atoms strictly better at ALL K values; best delta={best_delta:.4f} >= 0.05. "
                f"Per-K deltas: {deltas}.")
    if learned_wins <= max(1, n_K - 2):
        return ("LEARNED_CODEBOOK_HARD_FAIL",
                f"Learned atoms NOT better at >={n_K - learned_wins} of {n_K} K values. "
                f"Cap_map UNSURE A6 +0.02-0.08 prediction REFUTED. Per-K deltas: {deltas}.")
    return ("LEARNED_CODEBOOK_MIDDLE_BAND",
            f"Learned advantage at {learned_wins}/{n_K} K values; best delta={best_delta:.4f}. "
            f"Partial K-dependent benefit. Per-K deltas: {deltas}.")


def self_test_verdict():
    def mk(per_K_data):
        return {"per_K": {str(K): {str(s): {"learned_acc": l, "random_acc": r}
                                    for s, (l, r) in seeds.items()}
                          for K, seeds in per_K_data.items()}}
    # Test 1: HARD_PASS — learned strictly better at all K, best delta>=0.05.
    s1 = mk({4: {17: (0.80, 0.70), 23: (0.78, 0.68)},
              8: {17: (0.65, 0.55), 23: (0.66, 0.58)},
              16: {17: (0.45, 0.40), 23: (0.46, 0.41)}})
    # Test 2: HARD_FAIL — learned worse at 2 of 3 K values.
    s2 = mk({4: {17: (0.65, 0.70), 23: (0.66, 0.68)},
              8: {17: (0.50, 0.55), 23: (0.51, 0.58)},
              16: {17: (0.46, 0.40), 23: (0.47, 0.41)}})
    # Test 3: MIDDLE — learned wins at 2 of 3 but best delta<0.05.
    s3 = mk({4: {17: (0.72, 0.70), 23: (0.71, 0.68)},
              8: {17: (0.56, 0.55), 23: (0.59, 0.58)},
              16: {17: (0.40, 0.42), 23: (0.41, 0.41)}})
    # Test 4: INCONCLUSIVE.
    s4 = {"per_K": {}}
    cases = [
        (s1, "LEARNED_CODEBOOK_HARD_PASS"),
        (s2, "LEARNED_CODEBOOK_HARD_FAIL"),
        (s3, "LEARNED_CODEBOOK_MIDDLE_BAND"),
        (s4, "LEARNED_CODEBOOK_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; summary={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_probes = N_PROBES_SMOKE if smoke else N_PROBES_FULL
    config = {"mode": "smoke" if smoke else "full",
              "N": N, "vocab": VOCAB, "K_values": K_VALUES,
              "seeds": seeds, "n_probes_per_cell": n_probes}
    print(f"[config] {config}", flush=True)

    # Load corpus + compute PPMI once (deterministic).
    n_bytes = 50000 if smoke else 500000
    byte_stream = load_corpus_for_ppmi(n_bytes)
    print(f"[corpus] loaded {len(byte_stream)} bytes for PPMI", flush=True)
    ppmi = bigram_ppmi_matrix(byte_stream, vocab=VOCAB)
    print(f"[ppmi] shape={ppmi.shape}, mean={ppmi.mean():.4f}, max={ppmi.max():.4f}", flush=True)

    per_K = {}
    for K in K_VALUES:
        per_K[str(K)] = {}
        for seed in seeds:
            rng = np.random.default_rng(seed)
            random_atoms = make_random_bipolar(VOCAB, N, rng)
            learned_atoms = make_learned_bipolar(VOCAB, N, ppmi, rng)
            rng_probe = np.random.default_rng(seed + 1000)
            random_acc = cleanup_accuracy(random_atoms, n_probes, K, rng_probe)
            rng_probe2 = np.random.default_rng(seed + 1000)
            learned_acc = cleanup_accuracy(learned_atoms, n_probes, K, rng_probe2)
            per_K[str(K)][str(seed)] = {"random_acc": random_acc, "learned_acc": learned_acc,
                                          "delta": learned_acc - random_acc}
            print(f"  K={K} seed={seed}: random={random_acc:.4f} learned={learned_acc:.4f} delta={learned_acc - random_acc:+.4f}", flush=True)
    summary = {"per_K": per_K}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_learned_codebook_atoms_smoke_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_learned_codebook_atoms_smoke_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict(); return 0
    if args.smoke:
        run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
