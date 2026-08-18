"""shotgun_smoke_k_bank_count_sweep_v1 -- K-bank count sweep at small scale.

Parameter taxonomy B SECONDARY: K-bank count is load-bearing (4 of 17 params).
Substrate-mine: 4-modulator-on-one-bank HARD_FAILED at N=4096; multi-bank UNTESTED.
Drosophila MB has K=4 compartments (Aso-Hattori 2014).
Substrate-unique avenues drill confirmed K-bank is one of 2 genuine lift candidates.

Design:
  N_TOTAL=2048, N_TRAIN=2000 text8 words, pure numpy.
  K in {1, 2, 4, 8, 16}.
  N_per_bank = N_TOTAL // K (each bank shrinks as K grows).
  Feature-gated selection: input projects to K-dim gate, softmax -> bank choice.
  Metric: BPC on held-out 400 words + lift vs K=1 + gate entropy.

Pre-reg HARD_INFO bands:
  HARD_PASS  = K* in {2,4,8} shows BPC lower than K=1 by > 0.05 bits/char on held-out.
  HARD_FAIL  = ALL K values within 0.01 BPC of K=1 (flat; bank-count irrelevant).
  MIDDLE_BAND = some lift but < 0.05 margin OR non-monotonic shape with lift < 0.05.

ASCII-only. Pure numpy. No cert atomization. WHAT_THIS_DOES_NOT_SHOW: small-scale
(N=2048, N_TRAIN=2000); not testing K-bank at production N=8192; gate-selection
mechanism may not generalize; soft-assignment gate differs from hard winner-takes-all
Drosophila KC->MBON routing.
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
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

# ---- Config ----------------------------------------------------------------

N_TOTAL = 2048           # total vector dimensionality budget
N_TRAIN = 2000           # training words
N_HELD = 400             # held-out words for BPC
K_SWEEP = [1, 2, 4, 8, 16]
SEED = 42
GATE_TEMP = 0.5          # softmax temperature for gate (lower = more decisive)

# ---- Helpers ---------------------------------------------------------------

def _load_text8(n_words: int) -> List[str]:
    """Load first n_words from text8."""
    with open(TEXT8, "r", encoding="utf-8") as fh:
        raw = fh.read()
    words = raw.split()
    return words[:n_words]


def _build_vocab(words: List[str], max_v: int = 300) -> Tuple[dict, dict]:
    from collections import Counter
    counts = Counter(words)
    top = [w for w, _ in counts.most_common(max_v)]
    w2i = {w: i for i, w in enumerate(top)}
    i2w = {i: w for w, i in w2i.items()}
    return w2i, i2w


def _char_trigram(word: str, dim: int, rng: np.random.Generator) -> np.ndarray:
    """Deterministic char-trigram HD vector for a word (random-projection skeleton)."""
    padded = "##" + word + "##"
    trigrams = [padded[i:i+3] for i in range(len(padded) - 2)]
    v = np.zeros(dim, dtype=np.float32)
    for tg in trigrams:
        h = hash(tg) % (2**31)
        local_rng = np.random.default_rng(h % (2**32))
        v += local_rng.standard_normal(dim).astype(np.float32)
    nrm = np.linalg.norm(v)
    if nrm > 1e-9:
        v /= nrm
    return v


def _make_encodings(vocab: List[str], dim: int, seed: int) -> np.ndarray:
    """Return (V, dim) matrix of char-trigram HD vectors."""
    rng = np.random.default_rng(seed)
    return np.stack([_char_trigram(w, dim, rng) for w in vocab], axis=0)


def _gate_softmax(v: np.ndarray, W_gate: np.ndarray, temp: float) -> np.ndarray:
    """Project v (dim,) through W_gate (K, dim) -> softmax probabilities (K,)."""
    logits = W_gate @ v       # (K,)
    logits = logits / temp
    logits -= logits.max()
    probs = np.exp(logits)
    probs /= probs.sum()
    return probs              # (K,)


def _gate_entropy(probs: np.ndarray) -> float:
    """Shannon entropy of gate distribution (nats)."""
    eps = 1e-12
    return float(-np.sum(probs * np.log(probs + eps)))


def _max_entropy(K: int) -> float:
    return math.log(K)


# ---- K-bank associative memory ---------------------------------------------

class KBankMemory:
    """
    K banks, each with N_per_bank dimensions.
    Storage: W[k] = (N_per_bank, V) Hebbian matrix per bank k.
    Gate: W_gate (K, N_per_bank_input) projects input to bank probabilities.
    Write: write to EACH bank weighted by gate prob (soft assignment).
    Read: sum of (gate_prob[k] * W[k]^T x_k) across banks.
    """

    def __init__(self, K: int, N_total: int, V: int, seed: int):
        self.K = K
        self.N_per = N_total // K
        self.V = V
        rng = np.random.default_rng(seed)

        # Per-bank Hebbian matrices (N_per, V)
        self.W = [np.zeros((self.N_per, V), dtype=np.float32) for _ in range(K)]

        # Gate projection: maps input slice (N_per of bank 0) -> K logits
        # We use the first N_per dims as the "gate input" for simplicity.
        self.W_gate = rng.standard_normal((K, self.N_per)).astype(np.float32)
        self.W_gate /= np.linalg.norm(self.W_gate, axis=1, keepdims=True) + 1e-9

        # Bank input projections: encode (N_total,) -> (N_per,) per bank k
        # Simple slice: bank k uses dims [k*N_per : (k+1)*N_per]
        # (No extra projection matrix needed; each bank sees its own slice.)

    def _bank_slice(self, v_full: np.ndarray, k: int) -> np.ndarray:
        """Return the k-th bank's slice of v_full."""
        return v_full[k * self.N_per : (k + 1) * self.N_per]

    def write(self, v_full: np.ndarray, one_hot: np.ndarray) -> float:
        """Hebbian write across K banks; return gate entropy."""
        gate_input = self._bank_slice(v_full, 0)  # use bank-0 slice as gate signal
        probs = _gate_softmax(gate_input, self.W_gate, GATE_TEMP)
        entropy = _gate_entropy(probs)
        for k in range(self.K):
            v_k = self._bank_slice(v_full, k)      # (N_per,)
            # Outer product weighted by gate prob
            self.W[k] += probs[k] * np.outer(v_k, one_hot).astype(np.float32)
        return entropy

    def read_logits(self, v_full: np.ndarray) -> np.ndarray:
        """Return (V,) logit vector for next-word prediction."""
        gate_input = self._bank_slice(v_full, 0)
        probs = _gate_softmax(gate_input, self.W_gate, GATE_TEMP)
        logits = np.zeros(self.V, dtype=np.float32)
        for k in range(self.K):
            v_k = self._bank_slice(v_full, k)      # (N_per,)
            logits += probs[k] * (self.W[k].T @ v_k)   # (V,)
        return logits


# ---- BPC evaluation --------------------------------------------------------

def _compute_bpc(memory: KBankMemory, held_pairs: List[Tuple[np.ndarray, int]]) -> float:
    """BPC on held-out (context_vec, next_word_idx) pairs."""
    total_bits = 0.0
    n_chars = 0
    for ctx_v, target_idx in held_pairs:
        logits = memory.read_logits(ctx_v)
        # softmax
        logits -= logits.max()
        probs = np.exp(logits)
        probs /= probs.sum() + 1e-30
        p_target = float(probs[target_idx])
        p_target = max(p_target, 1e-30)
        # We treat each "token" as one prediction event; BPC = -log2(p) / len(word)
        word_len = 1  # placeholder; we use per-token bits/token then convert
        total_bits += -math.log2(p_target)
        n_chars += 1
    if n_chars == 0:
        return float("nan")
    return total_bits / n_chars   # bits per token (approximate BPC)


# ---- Main sweep ------------------------------------------------------------

def run_k_sweep(
    words: List[str],
    w2i: dict,
    vocab: List[str],
    K_list: List[int],
    seed: int,
) -> Dict[str, dict]:
    V = len(vocab)
    N_DIM_FULL = N_TOTAL

    # Build HD encodings in FULL N_TOTAL dims (each bank sees its slice)
    print("  Building encodings (N_TOTAL={}, V={})...".format(N_DIM_FULL, V))
    enc = _make_encodings(vocab, N_DIM_FULL, seed)   # (V, N_TOTAL)

    # Build training + held-out pairs
    train_words = words[:N_TRAIN]
    held_words  = words[N_TRAIN:N_TRAIN + N_HELD]

    def _make_pairs(wlist: List[str]) -> List[Tuple[np.ndarray, int]]:
        pairs = []
        for i in range(len(wlist) - 1):
            ctx = wlist[i]
            nxt = wlist[i + 1]
            if ctx in w2i and nxt in w2i:
                pairs.append((enc[w2i[ctx]], w2i[nxt]))
        return pairs

    held_pairs = _make_pairs(held_words)
    print("  Held pairs: {}".format(len(held_pairs)))

    results = {}

    for K in K_list:
        t0 = time.time()
        mem = KBankMemory(K, N_DIM_FULL, V, seed + K * 100)

        # Training
        total_entropy = 0.0
        n_written = 0
        for i in range(len(train_words) - 1):
            ctx = train_words[i]
            if ctx not in w2i:
                continue
            one_hot = np.zeros(V, dtype=np.float32)
            nxt = train_words[i + 1]
            if nxt not in w2i:
                continue
            one_hot[w2i[nxt]] = 1.0
            ent = mem.write(enc[w2i[ctx]], one_hot)
            total_entropy += ent
            n_written += 1

        avg_gate_entropy = total_entropy / max(n_written, 1)
        max_ent = _max_entropy(K) if K > 1 else 1.0
        gate_utilization = avg_gate_entropy / max(max_ent, 1e-9)

        # BPC on held-out
        bpc = _compute_bpc(mem, held_pairs)
        wall = time.time() - t0

        results[K] = {
            "K": K,
            "N_per_bank": N_DIM_FULL // K,
            "bpc": round(bpc, 4),
            "gate_entropy_avg": round(avg_gate_entropy, 4),
            "gate_utilization": round(gate_utilization, 4),
            "wall_s": round(wall, 2),
        }
        print("  K={:2d}  N_per={:5d}  BPC={:.4f}  gate_ent={:.4f}  util={:.3f}  wall={:.1f}s".format(
            K, N_DIM_FULL // K, bpc, avg_gate_entropy, gate_utilization, wall
        ))

    return results


# ---- Instrumentation self-test ---------------------------------------------

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    print("[SELF-TEST] Running instrumentation self-test...")
    rng = np.random.default_rng(0)
    K_test = 2
    N_test = 64
    V_test = 10

    mem = KBankMemory(K_test, N_test, V_test, seed=0)
    v = rng.standard_normal(N_test).astype(np.float32)
    v /= np.linalg.norm(v) + 1e-9
    one_hot = np.zeros(V_test, dtype=np.float32)
    one_hot[3] = 1.0
    ent = mem.write(v, one_hot)
    assert ent is not None and not math.isnan(ent), "gate_entropy is null/nan"
    assert ent >= 0.0, "gate_entropy is negative: {}".format(ent)

    logits = mem.read_logits(v)
    assert logits is not None, "read_logits returned None"
    assert len(logits) == V_test, "logits shape mismatch"
    assert not np.all(logits == 0.0), "logits are all-zero after one write"

    # BPC on tiny pair
    held = [(v, 3)]
    bpc = _compute_bpc(mem, held)
    assert bpc is not None and not math.isnan(bpc), "bpc is null/nan"
    assert bpc > 0.0, "bpc is zero or negative: {}".format(bpc)

    # Gate entropy for K=1 edge case
    mem1 = KBankMemory(1, N_test, V_test, seed=1)
    ent1 = mem1.write(v, one_hot)
    assert ent1 >= 0.0, "K=1 gate_entropy negative"

    print("[SELF-TEST] PASS")


_instrumentation_selftest()


# ---- Entry point -----------------------------------------------------------

def main():
    t_start = time.time()
    print("=" * 60)
    print("shotgun_smoke_k_bank_count_sweep_v1")
    print("N_TOTAL={}, N_TRAIN={}, N_HELD={}, K_SWEEP={}".format(
        N_TOTAL, N_TRAIN, N_HELD, K_SWEEP))
    print("=" * 60)

    print("Loading text8...")
    all_words = _load_text8(N_TRAIN + N_HELD + 10)

    print("Building vocab (top-300)...")
    w2i, i2w = _build_vocab(all_words[:N_TRAIN], max_v=300)
    vocab = list(w2i.keys())
    V = len(vocab)
    print("V={}".format(V))

    print("\nRunning K-bank sweep (seed={})...".format(SEED))
    results = run_k_sweep(all_words, w2i, vocab, K_SWEEP, SEED)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY: K-bank count sweep")
    print("=" * 60)
    bpc_k1 = results[1]["bpc"]
    print("K=1 baseline BPC: {:.4f}".format(bpc_k1))
    print()
    print("{:>4s}  {:>8s}  {:>8s}  {:>10s}  {:>10s}".format(
        "K", "BPC", "lift", "gate_util", "wall_s"))
    print("-" * 50)

    best_k = 1
    best_lift = 0.0
    all_lifts = {}
    for K in K_SWEEP:
        r = results[K]
        lift = bpc_k1 - r["bpc"]  # positive = better than K=1
        all_lifts[K] = lift
        marker = ""
        if K > 1 and abs(lift) > 0.05:
            marker = " <-- NOTABLE"
        print("{:>4d}  {:>8.4f}  {:>+8.4f}  {:>10.3f}  {:>10.2f}{}".format(
            K, r["bpc"], lift, r["gate_utilization"], r["wall_s"], marker))
        if lift > best_lift:
            best_lift = lift
            best_k = K

    print()
    print("Optimal K: {} (lift={:+.4f} BPC vs K=1)".format(best_k, best_lift))

    # HARD_INFO verdict
    max_lift = max(all_lifts[K] for K in K_SWEEP if K > 1)
    flat_threshold = 0.01
    pass_threshold = 0.05

    if max_lift >= pass_threshold:
        verdict = "HARD_PASS: K*={} shows BPC lift {:.4f} > 0.05 threshold".format(best_k, best_lift)
    elif max_lift < flat_threshold:
        verdict = "HARD_FAIL: all K values within {:.4f} BPC of K=1 (flat; bank-count irrelevant at this scale)".format(max_lift)
    else:
        verdict = "MIDDLE_BAND: best lift {:.4f} in (0.01, 0.05) -- non-decisive at N_TOTAL={}".format(max_lift, N_TOTAL)

    print("\nVERDICT: " + verdict)

    # Shape analysis
    lifts = [all_lifts[K] for K in K_SWEEP]
    monotonic_up = all(lifts[i] <= lifts[i+1] for i in range(len(lifts)-1))
    monotonic_down = all(lifts[i] >= lifts[i+1] for i in range(len(lifts)-1))
    peaked = any(
        lifts[i-1] < lifts[i] and lifts[i] > lifts[i+1]
        for i in range(1, len(lifts)-1)
    )
    if monotonic_up:
        shape = "monotonic_increase (more banks always better at this scale)"
    elif monotonic_down:
        shape = "monotonic_decrease (fewer banks better; K=1 optimal)"
    elif peaked:
        peak_idx = max(range(len(K_SWEEP)), key=lambda i: lifts[i])
        shape = "peaked at K={} (optimal interior point)".format(K_SWEEP[peak_idx])
    else:
        shape = "irregular (non-monotonic, non-peaked)"

    print("Shape: " + shape)

    # Gate entropy analysis
    print("\nGate entropy utilization by K:")
    for K in K_SWEEP:
        r = results[K]
        if K == 1:
            print("  K=1: no gate (single bank)")
        else:
            util_pct = r["gate_utilization"] * 100
            print("  K={:2d}: utilization={:.1f}%  (avg_entropy={:.4f} / max={:.4f})".format(
                K, util_pct, r["gate_entropy_avg"], _max_entropy(K)))

    total_wall = time.time() - t_start
    print("\nTotal wall: {:.1f}s".format(total_wall))
    print("\nWHAT_THIS_DOES_NOT_SHOW:")
    print("  - Small-scale only (N_TOTAL=2048, N_TRAIN=2000 words)")
    print("  - Not testing K-bank at production N=8192")
    print("  - Soft gate (softmax) differs from hard winner-takes-all Drosophila KC->MBON routing")
    print("  - Gate trained randomly (no gradient); gate quality may be sub-optimal")
    print("  - BPC metric is bits-per-token (not chars); comparison to text8 BPC floor is approximate")
    print("  - Does not test K-bank with pretrained or backprop encoder")

    return results, verdict, shape


if __name__ == "__main__":
    main()
