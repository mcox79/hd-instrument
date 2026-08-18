"""
exp_viability_shotgun_v1 -- 8-probe substrate viability shotgun (pure numpy; CPU only).

Goal: per-primitive x per-scale LIVE/DEAD map.
Probes 1-8 per USER directive 2026-06-23.
No cert atomization; no queue ship. Diagnostic only.

Probe 1: Baseline-reproducer sanity (Hebbian/fair_harness reference)
Probe 2: Sparse-bipolar amplitude-scaling viability
Probe 3: Lock-in amp viability across N
Probe 4: HRR bipolar bind involutive property
Probe 5: Hopfield cleanup with amplitude-scaled codebook
Probe 6: Multiplicative vs additive compose discriminator
Probe 7: READOUT_DEGENERATE detector (temperature range)
Probe 8: Per-context vs global temperature smoke

ASCII-only. numpy only. No torch imports (per directive).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import math
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

# ============================================================
# Utility
# ============================================================

def _bipolar_codebook(M: int, N: int, rng: np.random.RandomState) -> np.ndarray:
    """Dense bipolar codebook: shape (M, N), entries in {-1, +1}."""
    raw = rng.randn(M, N)
    cb = np.sign(raw)
    cb[cb == 0] = 1.0
    return cb.astype(np.float64)


def _sparse_bipolar_codebook(M: int, N: int, f: float, rng: np.random.RandomState,
                              amplitude_scale: bool = True) -> np.ndarray:
    """Sparse bipolar codebook: fraction f active, rest 0.
    If amplitude_scale=True, scale active entries by 1/sqrt(f) so L2 ~ sqrt(N)
    (same as dense bipolar). Otherwise raw bipolar +/-1 on active positions.
    """
    cb = np.zeros((M, N), dtype=np.float64)
    mask = rng.rand(M, N) < f
    signs = rng.choice([-1.0, 1.0], size=(M, N))
    cb[mask] = signs[mask]
    if amplitude_scale:
        cb *= (1.0 / math.sqrt(max(f, 1e-9)))
    return cb


def _recall_at_1(query: np.ndarray, codebook: np.ndarray) -> int:
    """Return 1 if argmax dot-product is index 0 (first row = target)."""
    scores = codebook @ query
    return int(np.argmax(scores) == 0)


def _softmax_bpc(logits: np.ndarray, temp: float) -> float:
    """Compute BPC from raw logits (shape V) at temperature temp."""
    scaled = logits / max(temp, 1e-9)
    scaled -= scaled.max()
    probs = np.exp(scaled)
    probs /= probs.sum()
    return float(-np.log2(probs.max() + 1e-40))  # BPC for top prediction (not true label)


def _read_text8(n_words: int) -> List[str]:
    """Read first n_words from text8."""
    with open(TEXT8, "r", encoding="utf-8") as f:
        content = f.read(n_words * 8)  # over-read
    words = content.split()
    return words[:n_words]


def _build_vocab_and_bigrams(words: List[str]) -> Tuple[Dict[str,int], Counter]:
    """Build vocab index and bigram counts from word list."""
    vocab_set = sorted(set(words))
    vocab = {w: i for i, w in enumerate(vocab_set)}
    bigrams: Counter = Counter()
    for i in range(len(words) - 1):
        bigrams[(words[i], words[i+1])] += 1
    return vocab, bigrams


# ============================================================
# PROBE 1: Baseline-reproducer sanity (rank-1 Hebbian LM)
# ============================================================

def _hebbian_train(words: List[str], vocab: Dict[str,int], N: int, seed: int) -> np.ndarray:
    """Train rank-1 Hebbian W = sum outer(encode(w_t), encode(w_{t+1})) at given N."""
    rng = np.random.RandomState(seed)
    V = len(vocab)
    # Random gaussian encoder: each word -> N-dim vector (not bipolar; this is diagnostic probe)
    E = rng.randn(V, N).astype(np.float64)
    # L2-normalize
    norms = np.linalg.norm(E, axis=1, keepdims=True)
    E /= np.maximum(norms, 1e-12)
    W = np.zeros((N, N), dtype=np.float64)
    for i in range(len(words) - 1):
        wi, wj = words[i], words[i+1]
        ei, ej = E[vocab[wi]], E[vocab[wj]]
        W += np.outer(ej, ei)
    return E, W


def _evaluate_lm_bpc(words: List[str], vocab: Dict[str,int],
                      E: np.ndarray, W: np.ndarray,
                      n_test: int = 500) -> Tuple[float, float]:
    """
    Evaluate BPC and top-1 accuracy using rank-1 Hebbian W.
    Uses a grid of temperatures [0.1, 0.5, 1.0, 2.0, 5.0]; picks best (lowest BPC).
    Returns (best_bpc, best_top1).
    """
    V = len(vocab)
    inv_vocab = {i: w for w, i in vocab.items()}
    temp_grid = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
    test_start = max(0, len(words) - n_test - 1)
    bpc_at_T = []
    top1_at_T = []
    for T in temp_grid:
        total_bpc = 0.0
        top1_count = 0
        n_eval = 0
        for i in range(test_start, min(test_start + n_test, len(words) - 1)):
            wi = words[i]
            wj = words[i + 1]
            if wi not in vocab or wj not in vocab:
                continue
            ei = E[vocab[wi]]
            logits = E @ (W @ ei)  # shape (V,)
            true_idx = vocab[wj]
            # BPC for true next word
            scaled = logits / max(T, 1e-9)
            scaled -= scaled.max()
            probs = np.exp(scaled)
            probs /= probs.sum()
            p_true = float(probs[true_idx])
            total_bpc += -math.log2(max(p_true, 1e-40))
            if np.argmax(probs) == true_idx:
                top1_count += 1
            n_eval += 1
        if n_eval > 0:
            bpc_at_T.append(total_bpc / n_eval)
            top1_at_T.append(top1_count / n_eval)
        else:
            bpc_at_T.append(99.0)
            top1_at_T.append(0.0)
    best_idx = int(np.argmin(bpc_at_T))
    return float(bpc_at_T[best_idx]), float(top1_at_T[best_idx])


def probe1_baseline_reproducer() -> Dict:
    """Probe 1: rank-1 Hebbian LM reproducer at N_DIM in {2048, 4096, 8192}.
    LIVE: bpc within 2.0 of unigram bpc AND cv < 0.15 across 2 seeds.
    NOTE: chain-grade reference is bpc~7.30 (text8 word-bigram); but on tiny N_TRAIN=5000
    words the vocab is ~500 words so unigram bpc is much lower (~log2(500)~9 but weighted
    by freq closer to ~7-8 bits). We measure relative to unigram, not absolute 7.30.
    """
    print("\n=== PROBE 1: Baseline-reproducer sanity ===", flush=True)
    t0 = time.time()
    N_TRAIN = 5000
    SEEDS = [7, 42]
    N_DIMS = [2048, 4096, 8192]
    LIVE_BPC_DELTA_FROM_UNIGRAM = 2.0  # LIVE if bpc < unigram + 2.0
    DEAD_CV = 0.15

    words = _read_text8(N_TRAIN + 600)
    train_words = words[:N_TRAIN]
    vocab, _ = _build_vocab_and_bigrams(train_words)
    V = len(vocab)

    # Unigram bpc
    unigram_counts = Counter(train_words)
    total = sum(unigram_counts.values())
    unigram_probs = {w: c / total for w, c in unigram_counts.items()}
    test_words = words[N_TRAIN:N_TRAIN + 500]
    unigram_bpc_vals = []
    for w in test_words:
        if w in unigram_probs:
            unigram_bpc_vals.append(-math.log2(max(unigram_probs[w], 1e-40)))
    unigram_bpc = float(np.mean(unigram_bpc_vals)) if unigram_bpc_vals else 10.0
    print(f"  Vocab size: {V}  Unigram BPC: {unigram_bpc:.4f}", flush=True)

    results_by_N = {}
    for N in N_DIMS:
        bpcs = []
        top1s = []
        for seed in SEEDS:
            E, W = _hebbian_train(train_words, vocab, N, seed)
            bpc, top1 = _evaluate_lm_bpc(words, vocab, E, W, n_test=300)
            bpcs.append(bpc)
            top1s.append(top1)
            print(f"  N={N} seed={seed}: bpc={bpc:.4f} top1={top1:.4f}", flush=True)
        mean_bpc = float(np.mean(bpcs))
        cv_bpc = float(np.std(bpcs) / max(np.mean(bpcs), 1e-9))
        verdict = "LIVE" if (mean_bpc < unigram_bpc + LIVE_BPC_DELTA_FROM_UNIGRAM
                             and cv_bpc < DEAD_CV) else "DEAD"
        results_by_N[N] = {
            "bpcs": bpcs, "top1s": top1s, "mean_bpc": mean_bpc,
            "cv_bpc": cv_bpc, "verdict": verdict
        }
        print(f"  N={N}: mean_bpc={mean_bpc:.4f} cv={cv_bpc:.4f} -> {verdict}", flush=True)

    elapsed = time.time() - t0
    print(f"  Probe 1 elapsed: {elapsed:.1f}s", flush=True)
    return {
        "probe": "P1_baseline_reproducer",
        "unigram_bpc": unigram_bpc,
        "by_N": results_by_N,
        "elapsed_s": elapsed
    }


# ============================================================
# PROBE 2: Sparse-bipolar amplitude-scaling viability
# ============================================================

def probe2_sparse_bipolar_amplitude() -> Dict:
    """Probe 2: sparse-bipolar codebook with/without 1/sqrt(f) amplitude scaling.
    Tests recall@1 on a simple nearest-neighbor codebook retrieval task.
    LIVE: amplitude-scaled shows higher recall than unscaled at matched noise level.
    DEAD: amplitude scaling makes no difference (encoding bug).
    """
    print("\n=== PROBE 2: Sparse-bipolar amplitude-scaling viability ===", flush=True)
    t0 = time.time()
    N_DIM = 4096
    M = 200
    N_EVAL = 100
    SEED = 7
    rng = np.random.RandomState(SEED)
    F_VALS = [0.005, 0.01, 0.02, 0.05, 0.1, 0.5]
    SIGMA = 0.3  # noise level for recall test (relative to unit-norm vectors)

    results = {}
    for f in F_VALS:
        row = {}
        for scaled_label, amplitude_scale in [("scaled", True), ("unscaled", False)]:
            rng_f = np.random.RandomState(SEED + int(f * 1000))
            codebook = _sparse_bipolar_codebook(M, N_DIM, f, rng_f, amplitude_scale)
            # L2 norm of codebook rows
            norms = np.linalg.norm(codebook, axis=1)
            mean_norm = float(np.mean(norms))
            # Eval: pick random queries from codebook, add noise, recall@1
            rng_eval = np.random.RandomState(SEED + 999)
            recall_sum = 0
            for _ in range(N_EVAL):
                idx = rng_eval.randint(0, M)
                query = codebook[idx].copy()
                noise = rng_eval.randn(N_DIM) * SIGMA * mean_norm / math.sqrt(N_DIM)
                query_noisy = query + noise
                # Put target at index 0 for recall_at_1 convention
                rows = [codebook[idx]] + [codebook[j] for j in range(M) if j != idx][:M-1]
                cb_test = np.array(rows)
                recall_sum += _recall_at_1(query_noisy, cb_test)
            recall = recall_sum / N_EVAL
            row[scaled_label] = {"recall": recall, "mean_norm": mean_norm}
        # Verdict
        lift = row["scaled"]["recall"] - row["unscaled"]["recall"]
        verdict = "LIVE" if lift > 0.05 else ("FLAT" if abs(lift) <= 0.05 else "INVERTED")
        results[f] = {**row, "lift": lift, "verdict": verdict}
        print(f"  f={f:.3f}: scaled={row['scaled']['recall']:.3f} "
              f"unscaled={row['unscaled']['recall']:.3f} lift={lift:+.3f} -> {verdict}  "
              f"(scaled_norm={row['scaled']['mean_norm']:.2f} unscaled_norm={row['unscaled']['mean_norm']:.2f})",
              flush=True)

    elapsed = time.time() - t0
    # Overall verdict: LIVE if scaling consistently helps at sparse f values
    live_count = sum(1 for f, r in results.items() if f <= 0.05 and r["verdict"] == "LIVE")
    overall = "LIVE" if live_count >= 2 else "DEAD"
    print(f"  Overall: {live_count}/4 sparse-f values show LIVE amplitude-scaling -> {overall}", flush=True)
    print(f"  Probe 2 elapsed: {elapsed:.1f}s", flush=True)
    return {"probe": "P2_sparse_bipolar_amplitude", "by_f": results,
            "overall": overall, "elapsed_s": elapsed}


# ============================================================
# PROBE 3: Lock-in amp viability across N
# ============================================================

def _lock_in_transmit_v2(cue: np.ndarray, P: int, k_signal: int,
                          sigma: float, rng: np.random.RandomState) -> np.ndarray:
    """Lock-in transmit v2 (from exp_lock_in_amplifier_hd_frequency_smoke_v1.py).
    Transmit-side AND demodulation-side cos weighting; signal coheres at sigma=0.
    """
    if P == 1:
        return cue + sigma * rng.randn(cue.shape[0])
    acc = np.zeros_like(cue, dtype=np.float64)
    for p in range(P):
        carrier_p = math.cos(2.0 * math.pi * p / P)
        rolled = np.roll(cue, p * k_signal)
        transmit_p = rolled * carrier_p
        noise_p = sigma * rng.randn(cue.shape[0])
        received = transmit_p + noise_p
        unrolled = np.roll(received, -p * k_signal)
        decoded_p = unrolled * carrier_p
        acc += decoded_p
    return (2.0 / P) * acc


def probe3_lock_in_amp_scaling() -> Dict:
    """Probe 3: lock-in amp recall@1 across N_DIM in {1024, 4096, 16384}.
    LIVE: recall@1 at best-sigma for P=32 >= 0.70 at N=4096 (conservative vs chain-grade 0.95;
          we use SIGMA_GRID = [16, 32, 64] as in spec but adjust baseline expectation
          to moderate-noise regime to be informative).
    DEAD: recall collapses to baseline level (lift < 0.05) or nan/inf.
    """
    print("\n=== PROBE 3: Lock-in amp viability across N ===", flush=True)
    t0 = time.time()
    M = 200
    SEEDS = [7, 17, 23]
    SIGMA_GRID = [16.0, 32.0, 64.0]
    P_SWEEP = [1, 8, 32]
    K_SIGNAL = 31
    HP_RECALL_P32 = 0.70  # LIVE band (at N=4096, best sigma)
    N_DIMS = [1024, 4096, 16384]

    results = {}
    for N in N_DIMS:
        recalls_by_P_sigma = {}
        for P in P_SWEEP:
            for sigma in SIGMA_GRID:
                recall_vals = []
                for seed in SEEDS:
                    rng = np.random.RandomState(seed)
                    codebook = _bipolar_codebook(M, N, rng)
                    # Normalize rows to unit length
                    norms = np.linalg.norm(codebook, axis=1, keepdims=True)
                    codebook_normed = codebook / np.maximum(norms, 1e-12)
                    recall_count = 0
                    N_EVAL = 50
                    for q_idx in range(N_EVAL):
                        target = codebook_normed[q_idx % M]
                        rng_q = np.random.RandomState(seed * 10000 + q_idx)
                        received = _lock_in_transmit_v2(target, P=P, k_signal=K_SIGNAL,
                                                        sigma=sigma / math.sqrt(N),
                                                        rng=rng_q)
                        recall_count += _recall_at_1(received, codebook_normed)
                    recall_vals.append(recall_count / N_EVAL)
                key = f"P{P}_s{int(sigma)}"
                recalls_by_P_sigma[key] = float(np.mean(recall_vals))

        # Find best recall at P=32
        p32_recalls = {k: v for k, v in recalls_by_P_sigma.items() if k.startswith("P32")}
        p1_recalls = {k: v for k, v in recalls_by_P_sigma.items() if k.startswith("P1")}
        best_P32 = max(p32_recalls.values()) if p32_recalls else 0.0
        best_P1 = max(p1_recalls.values()) if p1_recalls else 0.0
        lift = best_P32 - best_P1
        verdict = "LIVE" if best_P32 >= HP_RECALL_P32 else ("PARTIAL" if lift > 0.1 else "DEAD")
        results[N] = {
            "by": recalls_by_P_sigma,
            "best_P32": best_P32,
            "best_P1": best_P1,
            "lift": lift,
            "verdict": verdict
        }
        print(f"  N={N}: best_P32={best_P32:.3f} best_P1(baseline)={best_P1:.3f} lift={lift:+.3f} -> {verdict}",
              flush=True)
        for k, v in sorted(recalls_by_P_sigma.items()):
            print(f"    {k}: {v:.3f}", flush=True)

    elapsed = time.time() - t0
    print(f"  Probe 3 elapsed: {elapsed:.1f}s", flush=True)
    return {"probe": "P3_lock_in_amp_scaling", "by_N": results, "elapsed_s": elapsed}


# ============================================================
# PROBE 4: HRR bipolar bind involutive property
# ============================================================

def _hrr_bind_bipolar(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR circular convolution via FFT. Bipolar inputs in {-1, +1}."""
    fa = np.fft.rfft(a)
    fb = np.fft.rfft(b)
    return np.fft.irfft(fa * fb, n=len(a))


def _hrr_unbind_bipolar(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR correlation = convolution with conjugated b. Inverse of bind."""
    fc = np.fft.rfft(c)
    fb = np.fft.rfft(b)
    return np.fft.irfft(fc * np.conj(fb), n=len(c))


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def probe4_hrr_bipolar_involutive() -> Dict:
    """Probe 4: bind(bind(a,b),b) == a (involutive property) for bipolar HRR.
    LIVE: cosine(unbind(bind(a,b), b), a) >= 0.99 across N_DIM in {512, 4096, 8192}.
    NOTE: bipolar HRR via FFT is not perfectly involutive by construction (unlike FHRR).
    The test is: unbind(bind(a,b), b) has high cosine sim with a, meaning the
    approximate inverse holds well in practice.
    DEAD: cosine < 0.80 (the operation doesn't recover the original at all).
    """
    print("\n=== PROBE 4: HRR bipolar bind involutive property ===", flush=True)
    t0 = time.time()
    N_DIMS = [512, 4096, 8192]
    N_TRIALS = 50
    HP_COSINE = 0.99
    DEAD_COSINE = 0.80
    SEED = 42

    results = {}
    for N in N_DIMS:
        rng = np.random.RandomState(SEED)
        cosines = []
        for _ in range(N_TRIALS):
            # Generate bipolar vectors
            a = np.sign(rng.randn(N)).astype(np.float64)
            b = np.sign(rng.randn(N)).astype(np.float64)
            a[a == 0] = 1.0
            b[b == 0] = 1.0
            # bind(a, b) then unbind with b
            bound = _hrr_bind_bipolar(a, b)
            recovered = _hrr_unbind_bipolar(bound, b)
            sim = _cosine_similarity(recovered, a)
            cosines.append(sim)
        mean_cos = float(np.mean(cosines))
        std_cos = float(np.std(cosines))
        if mean_cos >= HP_COSINE:
            verdict = "LIVE"
        elif mean_cos >= DEAD_COSINE:
            verdict = "PARTIAL"
        else:
            verdict = "DEAD"
        results[N] = {"mean_cosine": mean_cos, "std_cosine": std_cos, "verdict": verdict}
        print(f"  N={N}: cosine={mean_cos:.5f} +/- {std_cos:.5f} -> {verdict}", flush=True)

    elapsed = time.time() - t0
    print(f"  Probe 4 elapsed: {elapsed:.1f}s", flush=True)
    return {"probe": "P4_hrr_involutive", "by_N": results, "elapsed_s": elapsed}


# ============================================================
# PROBE 5: Hopfield cleanup with amplitude-scaled codebook
# ============================================================

def _hopfield_modern_recall(query: np.ndarray, codebook: np.ndarray, beta: float = 8.0) -> np.ndarray:
    """Single-step modern Hopfield update. Returns retrieved pattern."""
    # Softmax attention
    logits = beta * (codebook @ query)  # shape (M,)
    logits -= logits.max()
    attn = np.exp(logits)
    attn /= attn.sum()
    return codebook.T @ attn  # weighted sum


def probe5_hopfield_amplitude_scaled() -> Dict:
    """Probe 5: Hopfield cleanup with amplitude-scaled sparse codebook.
    f=0.02, N_DIM=4096, M=500, sigma in {0, 0.1, 0.3}.
    LIVE: recall@1 at sigma=0.1 >= 0.90.
    DEAD: recall < 0.5 at sigma=0 (cleanup broken at clean input).
    Uses approximate recall: cosine_sim of retrieved pattern with target >= 0.9 as 'match'.
    """
    print("\n=== PROBE 5: Hopfield cleanup with amplitude-scaled codebook ===", flush=True)
    t0 = time.time()
    N_DIM = 4096
    M = 500
    F = 0.02
    SIGMA_GRID = [0.0, 0.1, 0.3]
    SEED = 7
    HP_RECALL_SIGMA01 = 0.90
    DEAD_RECALL_SIGMA0 = 0.50
    N_EVAL = 50
    # Use amplitude_scale=True (divide by norm)
    rng = np.random.RandomState(SEED)
    codebook_raw = _sparse_bipolar_codebook(M, N_DIM, F, rng, amplitude_scale=True)
    # L2-normalize each row for stable Hopfield
    norms = np.linalg.norm(codebook_raw, axis=1, keepdims=True)
    codebook = codebook_raw / np.maximum(norms, 1e-12)

    results_by_sigma = {}
    for sigma in SIGMA_GRID:
        rng_eval = np.random.RandomState(SEED + int(sigma * 100 + 1))
        recall_count = 0
        for q_idx in range(N_EVAL):
            target = codebook[q_idx % M]
            noise = rng_eval.randn(N_DIM) * sigma
            query = target + noise
            retrieved = _hopfield_modern_recall(query, codebook)
            # Match: cosine sim of retrieved with target >= 0.9
            sim = _cosine_similarity(retrieved, target)
            if sim >= 0.90:
                recall_count += 1
        recall = recall_count / N_EVAL
        if sigma == 0.0:
            verdict_part = "LIVE" if recall >= DEAD_RECALL_SIGMA0 else "DEAD"
        elif abs(sigma - 0.1) < 0.01:
            verdict_part = "LIVE" if recall >= HP_RECALL_SIGMA01 else "DEAD"
        else:
            verdict_part = "INFO"
        results_by_sigma[sigma] = {"recall": recall, "verdict": verdict_part}
        print(f"  sigma={sigma:.2f}: recall@1={recall:.3f} -> {verdict_part}", flush=True)

    recall_sigma0 = results_by_sigma[0.0]["recall"]
    recall_sigma01 = results_by_sigma[0.1]["recall"]
    overall = ("LIVE" if recall_sigma0 >= DEAD_RECALL_SIGMA0
                         and recall_sigma01 >= HP_RECALL_SIGMA01
               else ("PARTIAL" if recall_sigma0 >= DEAD_RECALL_SIGMA0
               else "DEAD"))
    print(f"  Overall: sigma=0 recall={recall_sigma0:.3f}, sigma=0.1 recall={recall_sigma01:.3f} -> {overall}",
          flush=True)
    elapsed = time.time() - t0
    print(f"  Probe 5 elapsed: {elapsed:.1f}s", flush=True)
    return {"probe": "P5_hopfield_amplitude_scaled",
            "by_sigma": results_by_sigma, "overall": overall, "elapsed_s": elapsed}


# ============================================================
# PROBE 6: Multiplicative vs additive compose discriminator
# ============================================================

def probe6_multiplicative_vs_additive() -> Dict:
    """Probe 6: gate_multiplicative = a*b*c vs gate_additive = sigmoid(a+b+c).
    Tests across modulator regimes where one modulator is near-zero.
    LIVE: multiplicative collapses when any mod <= 0.1 (prediction confirmed);
          additive stays non-degenerate (output entropy > 0.3 of max_entropy).
    """
    print("\n=== PROBE 6: Multiplicative vs additive compose discriminator ===", flush=True)
    t0 = time.time()
    N_DIM = 2048
    M = 100
    SEED = 7
    rng = np.random.RandomState(SEED)

    def sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

    def gate_multiplicative(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
        return a * b * c

    def gate_additive(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
        return sigmoid(a + b + c)

    # Generate base signal
    signal = rng.randn(M, N_DIM).astype(np.float64)

    modulator_regimes = {
        "all_high": [0.9, 0.9, 0.9],
        "one_low": [0.1, 0.9, 0.9],
        "two_low": [0.1, 0.1, 0.9],
        "all_low": [0.05, 0.05, 0.05],
        "mixed": [0.5, 0.3, 0.8],
    }

    def entropy_of_mean_magnitude(output: np.ndarray) -> float:
        """Proxy: mean absolute value relative to max possible."""
        abs_mean = float(np.mean(np.abs(output)))
        # For sigmoid output in [0,1], max is 1; report as fraction of 0.5
        return abs_mean

    results = {}
    for regime_name, mod_vals in modulator_regimes.items():
        a_mod = np.full((M, N_DIM), mod_vals[0])
        b_mod = np.full((M, N_DIM), mod_vals[1])
        c_mod = np.full((M, N_DIM), mod_vals[2])

        # For multiplicative, use mods directly as scalars on signal
        out_mult = gate_multiplicative(a_mod, b_mod, c_mod) * signal
        out_add = gate_additive(
            signal * mod_vals[0],
            signal * mod_vals[1],
            signal * mod_vals[2]
        )

        mean_mult = float(np.mean(np.abs(out_mult)))
        mean_add = float(np.mean(np.abs(out_add)))
        std_mult = float(np.std(out_mult))
        std_add = float(np.std(out_add))
        # Predicted: mult collapses (mean << std; or mean_mult / mean_add << 1)
        collapse_ratio = mean_mult / max(mean_add * prod([mod_vals[i] for i in range(3)]) /
                                         max(sigmoid_scalar(sum(mod_vals)), 0.001), 1e-9)
        results[regime_name] = {
            "mod_vals": mod_vals,
            "mean_mult": mean_mult, "std_mult": std_mult,
            "mean_add": mean_add, "std_add": std_add,
        }
        print(f"  {regime_name} mods={mod_vals}: "
              f"mult_mean={mean_mult:.4f} mult_std={std_mult:.4f} | "
              f"add_mean={mean_add:.4f} add_std={std_add:.4f}", flush=True)

    # Verdict: multiplicative should be ~1000x smaller than additive when any mod=0.05
    all_low_mult = results["all_low"]["mean_mult"]
    all_high_mult = results["all_high"]["mean_mult"]
    one_low_mult = results["one_low"]["mean_mult"]
    all_high_add = results["all_high"]["mean_add"]
    # The multiplicative collapse: all_low_mult should be << all_high_mult
    mult_collapse_ratio = all_low_mult / max(all_high_mult, 1e-9)
    # Additive stability: all_low_add should be within 2x of all_high_add
    all_low_add = results["all_low"]["mean_add"]
    add_stability_ratio = all_low_add / max(all_high_add, 1e-9)
    predicted_mult_collapse = mult_collapse_ratio < 0.01  # 100x drop = collapse
    predicted_add_stable = add_stability_ratio > 0.5       # additive stays >50%
    verdict = "LIVE" if predicted_mult_collapse and predicted_add_stable else "PARTIAL"
    print(f"  Multiplicative collapse: mult_all_low/mult_all_high={mult_collapse_ratio:.5f} "
          f"(collapse predicted: {predicted_mult_collapse})", flush=True)
    print(f"  Additive stability: add_all_low/add_all_high={add_stability_ratio:.3f} "
          f"(stable predicted: {predicted_add_stable})", flush=True)
    print(f"  Overall -> {verdict}", flush=True)

    elapsed = time.time() - t0
    print(f"  Probe 6 elapsed: {elapsed:.1f}s", flush=True)
    return {"probe": "P6_mult_vs_add_compose",
            "by_regime": results,
            "mult_collapse_ratio": mult_collapse_ratio,
            "add_stability_ratio": add_stability_ratio,
            "overall": verdict,
            "elapsed_s": elapsed}


def prod(vals):
    r = 1.0
    for v in vals:
        r *= v
    return r

def sigmoid_scalar(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-min(max(x, -30), 30)))


# ============================================================
# PROBE 7: READOUT_DEGENERATE detector (temperature range)
# ============================================================

def probe7_readout_degenerate() -> Dict:
    """Probe 7: fair_harness sparse-bipolar at N=8192 N_TRAIN=5000 with TEMP_GRID.
    LIVE: best T in {0.05, 0.1, 0.2} per methodology audit.
    DEAD: best T at extremes (0.01 or 10.0) -> temperature range still wrong.
    Uses a simplified sparse-bipolar Hebbian LM.
    """
    print("\n=== PROBE 7: READOUT_DEGENERATE detector ===", flush=True)
    t0 = time.time()
    N_DIM = 8192
    N_TRAIN = 5000
    SEED = 7
    F_SPARSE = 0.05
    TEMP_GRID = [0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 5.0, 10.0]
    N_TEST = 300
    HP_BEST_T_RANGE = {0.05, 0.1, 0.2}

    words = _read_text8(N_TRAIN + N_TEST + 100)
    train_words = words[:N_TRAIN]
    test_words = words[N_TRAIN:N_TRAIN + N_TEST]
    vocab, _ = _build_vocab_and_bigrams(train_words)
    V = len(vocab)
    print(f"  Vocab size: {V}", flush=True)

    rng = np.random.RandomState(SEED)
    # Sparse-bipolar encoder (amplitude-scaled)
    E = _sparse_bipolar_codebook(V, N_DIM, F_SPARSE, rng, amplitude_scale=True)
    # L2-normalize rows
    norms = np.linalg.norm(E, axis=1, keepdims=True)
    E = E / np.maximum(norms, 1e-12)

    # Train rank-1 Hebbian W on train words
    W = np.zeros((N_DIM, N_DIM), dtype=np.float64)
    for i in range(len(train_words) - 1):
        wi, wj = train_words[i], train_words[i+1]
        if wi in vocab and wj in vocab:
            ei, ej = E[vocab[wi]], E[vocab[wj]]
            W += np.outer(ej, ei)

    # Evaluate BPC at each temperature on test words
    bpc_by_T = {}
    top1_by_T = {}
    for T in TEMP_GRID:
        total_bpc = 0.0
        top1_count = 0
        n_eval = 0
        test_start = N_TRAIN
        for i in range(min(N_TEST, len(test_words) - 1)):
            wi = test_words[i]
            wj = test_words[i + 1] if i + 1 < len(test_words) else None
            if wi not in vocab or wj is None or wj not in vocab:
                continue
            ei = E[vocab[wi]]
            logits = E @ (W @ ei)  # shape (V,)
            # Compute BPC for true next word
            scaled = logits / max(T, 1e-9)
            scaled -= scaled.max()
            probs_raw = np.exp(scaled)
            probs = probs_raw / probs_raw.sum()
            p_true = float(probs[vocab[wj]])
            total_bpc += -math.log2(max(p_true, 1e-40))
            if np.argmax(probs) == vocab[wj]:
                top1_count += 1
            n_eval += 1
        if n_eval > 0:
            bpc_by_T[T] = total_bpc / n_eval
            top1_by_T[T] = top1_count / n_eval
        else:
            bpc_by_T[T] = 99.0
            top1_by_T[T] = 0.0
        print(f"  T={T:.3f}: bpc={bpc_by_T[T]:.4f} top1={top1_by_T[T]:.4f}", flush=True)

    # Find best T (lowest BPC)
    best_T = min(bpc_by_T, key=lambda T: bpc_by_T[T])
    best_bpc = bpc_by_T[best_T]
    in_hp_range = best_T in HP_BEST_T_RANGE
    verdict = "LIVE" if in_hp_range else "DEAD"
    print(f"  Best T={best_T} (bpc={best_bpc:.4f}) in HP_RANGE={HP_BEST_T_RANGE}: {in_hp_range} -> {verdict}",
          flush=True)
    # Check degenerate: at T=1.0, are logits near uniform?
    # Proxy: at T=1.0 bpc should be much higher than at best_T
    bpc_T1 = bpc_by_T.get(1.0, 99.0)
    degen_flag = bpc_T1 > 9.0  # near uniform over V words -> ~log2(V)
    print(f"  Degenerate check: bpc(T=1.0)={bpc_T1:.4f} degen={degen_flag}", flush=True)

    elapsed = time.time() - t0
    print(f"  Probe 7 elapsed: {elapsed:.1f}s", flush=True)
    return {"probe": "P7_readout_degenerate",
            "bpc_by_T": bpc_by_T, "top1_by_T": top1_by_T,
            "best_T": best_T, "best_bpc": best_bpc,
            "in_hp_T_range": in_hp_range,
            "degen_at_T1": degen_flag,
            "overall": verdict,
            "elapsed_s": elapsed}


# ============================================================
# PROBE 8: Per-context vs global temperature smoke
# ============================================================

def probe8_pertoken_vs_global_temp() -> Dict:
    """Probe 8: does per-token T calibration produce different distribution shape?
    Per-context T is calibrated per input based on output entropy of the context vector.
    LIVE: per-token T distribution has measurably different entropy variance vs global T (>= 10% delta).
    DEAD: per-token T equivalent to global T (mechanism doesn't compute anything).
    """
    print("\n=== PROBE 8: Per-context vs global temperature smoke ===", flush=True)
    t0 = time.time()
    N_DIM = 2048
    N_TRAIN = 5000
    SEED = 7
    N_TEST = 300
    GLOBAL_T = 0.1  # Use the best T from probe 7 hypothesis

    words = _read_text8(N_TRAIN + N_TEST + 100)
    train_words = words[:N_TRAIN]
    test_words = words[N_TRAIN:N_TRAIN + N_TEST]
    vocab, _ = _build_vocab_and_bigrams(train_words)
    V = len(vocab)
    print(f"  Vocab size: {V}", flush=True)

    rng = np.random.RandomState(SEED)
    E = rng.randn(V, N_DIM).astype(np.float64)
    norms = np.linalg.norm(E, axis=1, keepdims=True)
    E /= np.maximum(norms, 1e-12)

    W = np.zeros((N_DIM, N_DIM), dtype=np.float64)
    for i in range(len(train_words) - 1):
        wi, wj = train_words[i], train_words[i+1]
        if wi in vocab and wj in vocab:
            W += np.outer(E[vocab[wj]], E[vocab[wi]])

    def compute_entropy(probs: np.ndarray) -> float:
        return float(-np.sum(probs * np.log2(probs + 1e-40)))

    def per_token_T(logits: np.ndarray, T_min: float = 0.01, T_max: float = 2.0) -> float:
        """Calibrate T per context: use T that achieves 50% of max entropy."""
        target_entropy = 0.5 * math.log2(max(len(logits), 1))
        # Binary search for T
        lo, hi = T_min, T_max
        for _ in range(20):
            mid = (lo + hi) / 2.0
            sc = logits / mid
            sc -= sc.max()
            p = np.exp(sc); p /= p.sum()
            ent = compute_entropy(p)
            if ent < target_entropy:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2.0

    entropies_global = []
    entropies_pertoken = []
    T_pertoken_vals = []
    n_eval = 0
    for i in range(min(N_TEST, len(test_words) - 1)):
        wi = test_words[i]
        if wi not in vocab:
            continue
        ei = E[vocab[wi]]
        logits = E @ (W @ ei)

        # Global T
        sc_g = logits / GLOBAL_T
        sc_g -= sc_g.max()
        p_g = np.exp(sc_g); p_g /= p_g.sum()
        entropies_global.append(compute_entropy(p_g))

        # Per-token T
        T_pt = per_token_T(logits)
        T_pertoken_vals.append(T_pt)
        sc_pt = logits / T_pt
        sc_pt -= sc_pt.max()
        p_pt = np.exp(sc_pt); p_pt /= p_pt.sum()
        entropies_pertoken.append(compute_entropy(p_pt))
        n_eval += 1

    if not entropies_global:
        print("  ERROR: no valid test tokens", flush=True)
        return {"probe": "P8_pertoken_vs_global_temp", "overall": "DEAD", "error": "no_test_tokens"}

    var_global = float(np.var(entropies_global))
    var_pertoken = float(np.var(entropies_pertoken))
    mean_T_pt = float(np.mean(T_pertoken_vals))
    std_T_pt = float(np.std(T_pertoken_vals))

    # Delta: per-token variance vs global variance
    delta_frac = abs(var_pertoken - var_global) / max(var_global, 1e-9)
    verdict = "LIVE" if delta_frac >= 0.10 else "DEAD"

    print(f"  n_eval={n_eval}  global_T={GLOBAL_T}", flush=True)
    print(f"  Entropy global: mean={np.mean(entropies_global):.4f} var={var_global:.6f}", flush=True)
    print(f"  Entropy per-token: mean={np.mean(entropies_pertoken):.4f} var={var_pertoken:.6f}", flush=True)
    print(f"  Per-token T: mean={mean_T_pt:.4f} std={std_T_pt:.4f}", flush=True)
    print(f"  Variance delta fraction: {delta_frac:.4f} (>= 0.10 = LIVE) -> {verdict}", flush=True)

    elapsed = time.time() - t0
    print(f"  Probe 8 elapsed: {elapsed:.1f}s", flush=True)
    return {"probe": "P8_pertoken_vs_global_temp",
            "var_global": var_global, "var_pertoken": var_pertoken,
            "delta_frac": delta_frac, "mean_T_pertoken": mean_T_pt,
            "n_eval": n_eval, "overall": verdict,
            "elapsed_s": elapsed}


# ============================================================
# INSTRUMENTATION SELF-TEST (validates probe primitives at tiny scale)
# ============================================================

def _instrumentation_selftest():
    """Assert all claimed probe primitives are non-null and non-sentinel at small scale."""
    rng = np.random.RandomState(1)

    # Bipolar codebook
    cb = _bipolar_codebook(5, 64, rng)
    assert cb.shape == (5, 64), "codebook shape"
    assert np.all(np.abs(cb) == 1.0), "codebook entries are +-1"

    # Sparse bipolar
    scb = _sparse_bipolar_codebook(5, 64, 0.1, rng, amplitude_scale=True)
    assert scb.shape == (5, 64), "sparse codebook shape"
    assert not np.all(scb == 0), "sparse codebook not all zero"

    # Recall at 1 (clean: query = first row, should be 100%)
    query = cb[0].copy()
    r = _recall_at_1(query, cb)
    assert r == 1, f"recall_at_1 clean should be 1, got {r}"

    # HRR bind/unbind
    a = np.sign(rng.randn(64)).astype(np.float64)
    b = np.sign(rng.randn(64)).astype(np.float64)
    a[a == 0] = 1.0; b[b == 0] = 1.0
    bound = _hrr_bind_bipolar(a, b)
    recovered = _hrr_unbind_bipolar(bound, b)
    sim = _cosine_similarity(recovered, a)
    assert sim > 0.5, f"HRR unbind cosine too low at N=64: {sim}"

    # Lock-in transmit v2
    rng_li = np.random.RandomState(2)
    v = rng_li.randn(64)
    out = _lock_in_transmit_v2(v, P=8, k_signal=7, sigma=0.0, rng=rng_li)
    assert out.shape == (64,), "lock-in output shape"
    assert np.all(np.isfinite(out)), "lock-in finite"
    # At sigma=0 v2 should recover v exactly (per v2 formula: signal = (2/P)*sum cos^2 = 1.0)
    assert float(np.max(np.abs(out - v))) < 1e-9, "lock-in v2 sigma=0 should recover v"

    # Text8 file readable
    words = _read_text8(100)
    assert len(words) >= 100, "text8 readable"

    print("[selftest] PASS: all probe primitives non-null at small scale.", flush=True)

_instrumentation_selftest()


# ============================================================
# MAIN: run all probes and collect summary
# ============================================================

def run_all_probes():
    total_start = time.time()
    print("=" * 60, flush=True)
    print("SUBSTRATE VIABILITY SHOTGUN -- 8 probes", flush=True)
    print("=" * 60, flush=True)

    results = []

    r1 = probe1_baseline_reproducer()
    results.append(r1)

    r2 = probe2_sparse_bipolar_amplitude()
    results.append(r2)

    r3 = probe3_lock_in_amp_scaling()
    results.append(r3)

    r4 = probe4_hrr_bipolar_involutive()
    results.append(r4)

    r5 = probe5_hopfield_amplitude_scaled()
    results.append(r5)

    r6 = probe6_multiplicative_vs_additive()
    results.append(r6)

    r7 = probe7_readout_degenerate()
    results.append(r7)

    r8 = probe8_pertoken_vs_global_temp()
    results.append(r8)

    total_elapsed = time.time() - total_start

    # ---- SUMMARY ----
    print("\n" + "=" * 60, flush=True)
    print("VIABILITY MAP SUMMARY", flush=True)
    print("=" * 60, flush=True)

    # P1
    p1_summary = []
    for N, info in r1["by_N"].items():
        p1_summary.append(f"N={N}:{info['verdict']}")
    print(f"P1 Baseline-Hebbian: {' | '.join(p1_summary)}", flush=True)

    # P2
    print(f"P2 Sparse-Bipolar-Amplitude: overall={r2['overall']}", flush=True)
    for f, info in r2["by_f"].items():
        print(f"   f={f:.3f}: {info['verdict']} (scaled={info['scaled']['recall']:.3f} unscaled={info['unscaled']['recall']:.3f} lift={info['lift']:+.3f})", flush=True)

    # P3
    p3_summary = []
    for N, info in r3["by_N"].items():
        p3_summary.append(f"N={N}:{info['verdict']}(P32={info['best_P32']:.3f})")
    print(f"P3 Lock-in-amp scaling: {' | '.join(p3_summary)}", flush=True)

    # P4
    p4_summary = []
    for N, info in r4["by_N"].items():
        p4_summary.append(f"N={N}:{info['verdict']}(cos={info['mean_cosine']:.4f})")
    print(f"P4 HRR-bipolar involutive: {' | '.join(p4_summary)}", flush=True)

    # P5
    print(f"P5 Hopfield-amplitude-scaled: {r5['overall']}", flush=True)

    # P6
    print(f"P6 Mult-vs-Additive: {r6['overall']} "
          f"(mult_collapse={r6['mult_collapse_ratio']:.5f} add_stable={r6['add_stability_ratio']:.3f})", flush=True)

    # P7
    print(f"P7 Readout-degenerate: {r7['overall']} "
          f"(best_T={r7['best_T']} bpc={r7['best_bpc']:.4f} in_HP_range={r7['in_hp_T_range']})", flush=True)

    # P8
    print(f"P8 Per-token-T: {r8['overall']} "
          f"(var_delta_frac={r8.get('delta_frac', 0):.4f})", flush=True)

    print(f"\nTotal elapsed: {total_elapsed:.1f}s", flush=True)

    # Count LIVE / DEAD / PARTIAL
    live_count = 0
    dead_count = 0
    partial_count = 0

    def tally(verdict_str):
        nonlocal live_count, dead_count, partial_count
        v = str(verdict_str).upper()
        if "LIVE" in v:
            live_count += 1
        elif "DEAD" in v:
            dead_count += 1
        elif "PARTIAL" in v:
            partial_count += 1

    # Tally per-probe overall verdicts
    for N, info in r1["by_N"].items():
        tally(info["verdict"])
    tally(r2["overall"])
    for N, info in r3["by_N"].items():
        tally(info["verdict"])
    for N, info in r4["by_N"].items():
        tally(info["verdict"])
    tally(r5["overall"])
    tally(r6["overall"])
    tally(r7["overall"])
    tally(r8["overall"])

    print(f"\nVERDICT COUNTS: LIVE={live_count} DEAD={dead_count} PARTIAL={partial_count}", flush=True)

    return results


if __name__ == "__main__":
    run_all_probes()
