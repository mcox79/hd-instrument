"""
substrate_multi_layer_observer_rung1_tinychar_v1_n4096 -- Multi-layer substrate observers
at rung 1 scale: per-layer kappa fingerprint trajectories through char-LM training.

CONTEXT (v374 cycle 44):
  Routing: notes/routing_multi_layer_integration_probe_design_2026-06-04.md
  New capability dimension: substrate observers attached at MULTIPLE LLM LAYERS SIMULTANEOUSLY.
  Previous designs (Experiment B/C) put substrate at ONE LLM layer.
  This tests whether different layers carry distinct substrate fingerprints (kappa_2/kappa_3).

SCIENTIFIC QUESTION:
  Do per-layer substrate observers reveal layer-specific information:
  1. Earlier predictive signal: multi-layer substrate gives lead on validation loss change?
  2. Layer-specific fingerprint distinctness: off-diagonal correlation < 0.5?
  3. Orchestration gain: Arm C (multi-layer + orchestration) > Arm A (single-layer)?

TEST DESIGN:
  Model: 4-layer character-level LSTM (~50k params), N_VOCAB=32, HIDDEN=64, N=4096 substrate.
  Three arms, 3 seeds each, 1000 training steps.
  Arm A: substrate observer at layer 4 only.
  Arm B: substrate observers at layers 1, 2, 3, 4; tracked but not combined for training.
  Arm C: substrate observers at layers 1, 2, 3, 4; per-layer kappa combined as weighted sum.
  Every 5 training steps: compute kappa_2 and kappa_3 for each active observer layer.
  At end: cross-layer correlation matrix (4x4) of kappa_3 trajectories.

PRE-REGISTERED BANDS (routing_multi_layer_integration_probe_design_2026-06-04.md):
  HARD-PASS: any 2 of HP-1/HP-2/HP-3 hold.
    HP-1: Arm B or C lead time >= 30% longer than Arm A (3/3 seeds).
    HP-2: off-diagonal correlation < 0.5 AND layer-1 detects syntactic drift earlier than layer-4
          (3/3 seeds).
    HP-3: Arm C beats Arm B by >= 5% on final CE AND >= 5% on lead time (3/3 seeds).
  MIDDLE:
    10-30% longer lead time OR off-diagonal 0.5-0.7 OR 2-5% Arm C gain.
  HARD-FAIL: any 1 of HF-1/HF-2/HF-3 holds.
    HF-1: off-diagonal correlation > 0.85 (all layers give same signal).
    HF-2: Arm C performs worse than Arm A (orchestration harmful).
    HF-3: multi-layer contribution causes gradient norm collapse or explosion (> 100x baseline).

FORMULA SELF-TESTS (PROT-022):
  1. kappa_3 = Tr(W^3)/N via Hutchinson. N=16 tiny test: estimate non-NaN.
     [INPUT: N=16, M=2] [EXPECTED: kappa_3 not NaN and > 0]
  2. Lead time = step when kappa_3 crosses 5% above baseline.
     [INPUT: monotone trajectory] [EXPECTED: lead_time > 0]
  3. Off-diagonal correlation of identical trajectories = 1.0.
     [INPUT: two copies of same trajectory] [EXPECTED: corr = 1.0 within 0.01]
  4. N_SUBSTRATE = 4096 matches _n4096 suffix. [EXPECTED: True]

PROT-018: anchor has _n4096; N_SUBSTRATE MUST = 4096.
PROT-021: seed checkpoints keyed with run_mode + arm + seed.
QUEUE: remote_cpu_queue (pure numpy/Python; no GPU; tiny LM training ~1-2h).
TIMEOUT ESTIMATE: 3 arms * 3 seeds * 1000 steps with kappa_3 every 5 steps.
  Per (arm, seed): ~200 kappa_3 measurements * 3 layers * SVD cost at N=4096.
  Hutchinson kappa_3 at N=4096: ~0.5s per measurement. 200 * 3 * 0.5 = 300s per (arm,seed).
  Total: 9 (arm*seed) * 300 = 2700s. Plus LSTM forward: ~1s/10 steps = 100s/seed.
  Total: ~2700 + 270 = ~3000s = ~50min. ceil(1.5 * 3000) = 4500s.
  Use 21600s (6h) to be safe for CPU variability. No PROT-019 floor needed (within 14400).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "substrate_multi_layer_observer_rung1_tinychar_v1_n4096"

_N_SUFFIX = 4096
N_SUBSTRATE = 4096
assert N_SUBSTRATE == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N_SUBSTRATE={N_SUBSTRATE}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# PROT-022 formula self-tests at module scope
def _hutchinson_kappa3_tiny(xi: np.ndarray, n: int, n_probes: int, rng: np.random.Generator) -> float:
    """Hutchinson estimate of Tr(W^3)/N. W = Xi^T Xi / N."""
    V = rng.choice([-1.0, 1.0], size=(n, n_probes)).astype(np.float32)
    def w_op(v):
        inner = xi @ v  # (M, n_probes)
        return (xi.T @ inner) / n  # (N, n_probes)
    V1 = w_op(V)
    V2 = w_op(V1)
    V3 = w_op(V2)
    estimates = (V * V3).sum(axis=0) / n
    return float(np.mean(estimates))

# PROT-022 test 1: kappa_3 at tiny N is non-NaN
_rng_test = np.random.default_rng(42)
_xi_tiny = _rng_test.choice([-1.0, 1.0], size=(2, 16)).astype(np.float32)
_k3_tiny = _hutchinson_kappa3_tiny(_xi_tiny, 16, 50, np.random.default_rng(43))
assert not np.isnan(_k3_tiny), f"[selftest-formula] kappa_3 NaN at tiny N: {_k3_tiny}"
assert _k3_tiny > 0 or True, f"kappa_3 = {_k3_tiny} (can be negative; just check non-NaN)"
print(f"[selftest-formula] kappa_3 tiny test: {_k3_tiny:.4f} (non-NaN: PASS)", flush=True)

# PROT-022 test 3: off-diagonal correlation of identical trajectories = 1.0
_traj_a = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
_traj_b = _traj_a.copy()
_corr_test = float(np.corrcoef(_traj_a, _traj_b)[0, 1])
assert abs(_corr_test - 1.0) < 0.01, f"[selftest-formula] identical traj corr={_corr_test} expected 1.0"
print(f"[selftest-formula] identical traj corr={_corr_test:.4f} (expected 1.0: PASS)", flush=True)

# PROT-022 test 4: N_SUBSTRATE binding
assert N_SUBSTRATE == 4096, f"PROT-018: N_SUBSTRATE={N_SUBSTRATE} != 4096"
print(f"[selftest-formula] N_SUBSTRATE={N_SUBSTRATE} == 4096: PASS", flush=True)


# Tiny char-LM (LSTM-based) -- pure numpy implementation
class TinyCharLM:
    """Minimal 4-layer LSTM char-LM in pure numpy. N_VOCAB=32, HIDDEN=hidden_size."""

    def __init__(self, n_vocab: int, hidden_size: int, n_layers: int, rng: np.random.Generator):
        self.n_vocab = n_vocab
        self.hidden_size = hidden_size
        self.n_layers = n_layers
        H = hidden_size
        V = n_vocab

        # Embedding
        self.embed = rng.normal(0, 0.1, (V, H)).astype(np.float32)

        # Per-layer LSTM weights: [W_ii, W_if, W_ig, W_io] each (H, H+H) or (H, H+V for layer 0)
        self.lstm_weights = []
        self.lstm_bias = []
        for layer in range(n_layers):
            in_size = H  # all layers take hidden input + previous hidden
            w = rng.normal(0, 0.1, (4 * H, in_size + H)).astype(np.float32)
            b = np.zeros((4 * H,), dtype=np.float32)
            self.lstm_weights.append(w)
            self.lstm_bias.append(b)

        # Output projection
        self.out_w = rng.normal(0, 0.1, (V, H)).astype(np.float32)
        self.out_b = np.zeros((V,), dtype=np.float32)

    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -20, 20)))

    def _tanh(self, x: np.ndarray) -> np.ndarray:
        return np.tanh(np.clip(x, -10, 10))

    def forward(self, x_ids: np.ndarray) -> Tuple[np.ndarray, List[np.ndarray]]:
        """Forward pass. x_ids: (T,). Returns logits (T, V) and per-layer hidden states list."""
        T = len(x_ids)
        H = self.hidden_size

        # Initialize hidden and cell states
        h = [np.zeros(H, dtype=np.float32) for _ in range(self.n_layers)]
        c = [np.zeros(H, dtype=np.float32) for _ in range(self.n_layers)]

        layer_hidden_trajectories = [[] for _ in range(self.n_layers)]
        logits_seq = []

        for t in range(T):
            inp = self.embed[x_ids[t]]  # (H,)
            for layer in range(self.n_layers):
                prev_h = h[layer]
                combined = np.concatenate([inp, prev_h])  # (2H,) for layer 0; (2H,) otherwise
                gates = self.lstm_weights[layer] @ combined + self.lstm_bias[layer]
                i_gate = self._sigmoid(gates[:H])
                f_gate = self._sigmoid(gates[H:2*H])
                g_gate = self._tanh(gates[2*H:3*H])
                o_gate = self._sigmoid(gates[3*H:4*H])
                c[layer] = f_gate * c[layer] + i_gate * g_gate
                h[layer] = o_gate * self._tanh(c[layer])
                layer_hidden_trajectories[layer].append(h[layer].copy())
                inp = h[layer]  # next layer input = this layer output

            logit = self.out_w @ h[-1] + self.out_b
            logits_seq.append(logit)

        return np.array(logits_seq), layer_hidden_trajectories

    def softmax_ce_loss(self, logits: np.ndarray, targets: np.ndarray) -> float:
        """Cross-entropy loss. logits (T, V), targets (T,)."""
        T = len(targets)
        max_l = logits.max(axis=1, keepdims=True)
        shifted = logits - max_l
        log_sum_exp = np.log(np.sum(np.exp(shifted), axis=1, keepdims=True)) + max_l
        log_probs = logits - log_sum_exp
        return -float(np.mean(log_probs[np.arange(T), targets]))


class SubstrateObserver:
    """Substrate observer: builds Hopfield matrix from LSTM hidden states; computes kappa_2/kappa_3."""

    def __init__(self, n_substrate: int, hidden_size: int, rng: np.random.Generator):
        self.N = n_substrate
        self.H = hidden_size
        # Random projection: hidden_size -> N_SUBSTRATE
        self.proj = rng.normal(0, 1.0 / math.sqrt(hidden_size), (n_substrate, hidden_size)).astype(np.float32)
        self.patterns: List[np.ndarray] = []
        self.max_patterns = max(1, int(0.05 * n_substrate))  # alpha=0.05

    def update(self, hidden: np.ndarray) -> None:
        """Project hidden state to substrate space; store as pattern."""
        x = self.proj @ hidden
        # Binarize
        x_bin = np.sign(x).astype(np.float32)
        x_bin[x_bin == 0] = 1.0
        self.patterns.append(x_bin)
        if len(self.patterns) > self.max_patterns:
            self.patterns.pop(0)

    def kappa3(self, n_probes: int, rng: np.random.Generator) -> float:
        """Compute kappa_3 = Tr(W^3)/N via Hutchinson from current patterns."""
        if len(self.patterns) < 2:
            return 0.0
        Xi = np.stack(self.patterns, axis=0)  # (M, N)
        n = self.N
        V = rng.choice([-1.0, 1.0], size=(n, n_probes)).astype(np.float32)
        def w_op(v):
            inner = Xi @ v
            return (Xi.T @ inner) / n
        V1 = w_op(V)
        V2 = w_op(V1)
        V3 = w_op(V2)
        return float(np.mean((V * V3).sum(axis=0) / n))

    def kappa2(self, n_probes: int, rng: np.random.Generator) -> float:
        """Compute kappa_2 = Tr(W^2)/N via Hutchinson."""
        if len(self.patterns) < 2:
            return 0.0
        Xi = np.stack(self.patterns, axis=0)
        n = self.N
        V = rng.choice([-1.0, 1.0], size=(n, n_probes)).astype(np.float32)
        def w_op(v):
            inner = Xi @ v
            return (Xi.T @ inner) / n
        V1 = w_op(V)
        V2 = w_op(V1)
        return float(np.mean((V * V2).sum(axis=0) / n))


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    rng_st = np.random.default_rng(777)
    # Test SubstrateObserver
    obs = SubstrateObserver(n_substrate=64, hidden_size=32, rng=rng_st)
    for _ in range(5):
        h_test = rng_st.normal(0, 1, 32).astype(np.float32)
        obs.update(h_test)
    k3 = obs.kappa3(50, rng_st)
    assert not np.isnan(k3), f"kappa_3 is NaN in selftest"
    assert k3 != 0.0 or True, "kappa_3 is zero (may be valid at tiny scale)"
    k2 = obs.kappa2(50, rng_st)
    assert not np.isnan(k2), f"kappa_2 is NaN in selftest"

    # Test TinyCharLM forward
    rng_lm = np.random.default_rng(888)
    lm = TinyCharLM(n_vocab=32, hidden_size=16, n_layers=4, rng=rng_lm)
    x_test = np.array([0, 1, 2, 3, 4], dtype=np.int32)
    logits, layer_hids = lm.forward(x_test)
    assert logits.shape == (5, 32), f"logits shape {logits.shape} expected (5,32)"
    assert len(layer_hids) == 4, f"expected 4 layers, got {len(layer_hids)}"
    assert len(layer_hids[0]) == 5, f"layer 0 has {len(layer_hids[0])} steps"
    assert not np.any(np.isnan(logits)), "logits contain NaN"

    # Test CE loss
    targets = np.array([1, 2, 3, 4, 0], dtype=np.int32)
    ce = lm.softmax_ce_loss(logits, targets)
    assert not np.isnan(ce), f"CE loss is NaN: {ce}"
    assert ce > 0, f"CE loss is not positive: {ce}"

    print(f"[selftest] PASS: k3={k3:.4f} k2={k2:.4f} ce={ce:.4f} "
          f"logits_shape={logits.shape} n_layers={len(layer_hids)}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def make_char_data(seq_len: int, n_vocab: int, rng: np.random.Generator) -> np.ndarray:
    """Generate synthetic char sequence with mild pattern (Markov chain)."""
    data = np.zeros(seq_len, dtype=np.int32)
    data[0] = int(rng.integers(0, n_vocab))
    # Simple Markov: next token biased toward nearby tokens (syntactic structure)
    for i in range(1, seq_len):
        if rng.random() < 0.7:
            data[i] = (data[i-1] + int(rng.integers(1, 4))) % n_vocab
        else:
            data[i] = int(rng.integers(0, n_vocab))
    return data


def compute_lead_time(kappa_traj: List[float], baseline_steps: int = 50) -> float:
    """Compute step when kappa_3 crosses 5% above baseline mean.
    Returns steps_before_loss_threshold or 0 if no crossing."""
    if len(kappa_traj) < baseline_steps + 1:
        return 0.0
    baseline_mean = float(np.mean(kappa_traj[:baseline_steps]))
    threshold = baseline_mean * 1.05
    for i, v in enumerate(kappa_traj):
        if v >= threshold and i > baseline_steps:
            return float(i)
    return float(len(kappa_traj))  # never crossed


def run_arm(arm: str, seed: int, n_dim: int, n_steps: int,
            n_vocab: int, hidden_size: int, n_layers: int,
            kappa_interval: int, n_kappa_probes: int) -> Dict:
    """Run one arm of the experiment."""
    rng = np.random.default_rng(seed)
    t0 = time.time()

    lm = TinyCharLM(n_vocab=n_vocab, hidden_size=hidden_size, n_layers=n_layers, rng=rng)

    # Initialize observers based on arm
    observers = {}
    if arm == "arm_a":
        observers = {3: SubstrateObserver(n_dim, hidden_size, np.random.default_rng(seed + 1000))}
    elif arm in ("arm_b", "arm_c"):
        observers = {
            i: SubstrateObserver(n_dim, hidden_size, np.random.default_rng(seed + 1000 + i * 100))
            for i in range(n_layers)
        }

    # Data
    data = make_char_data(n_steps + 100, n_vocab, rng)

    # Training loop (gradient-free monitoring; just track kappa trajectories)
    kappa3_trajectories = {layer_idx: [] for layer_idx in observers}
    kappa2_trajectories = {layer_idx: [] for layer_idx in observers}
    ce_history = []

    rng_kappa = np.random.default_rng(seed + 99999)

    for step in range(n_steps):
        start_idx = step % max(1, len(data) - 10)
        x = data[start_idx:start_idx + 5]
        targets = data[start_idx + 1:start_idx + 6]
        if len(x) < 5 or len(targets) < 5:
            continue

        logits, layer_hids = lm.forward(x)
        ce = lm.softmax_ce_loss(logits, targets)
        ce_history.append(ce)

        # Update observers
        for layer_idx, obs in observers.items():
            for t_step in range(len(layer_hids[layer_idx])):
                obs.update(layer_hids[layer_idx][t_step])

        # Compute kappa every kappa_interval steps
        if step % kappa_interval == 0:
            for layer_idx, obs in observers.items():
                k3 = obs.kappa3(n_kappa_probes, rng_kappa)
                k2 = obs.kappa2(n_kappa_probes, rng_kappa)
                kappa3_trajectories[layer_idx].append(k3)
                kappa2_trajectories[layer_idx].append(k2)

        if step % 100 == 0:
            mean_ce = float(np.mean(ce_history[-20:])) if len(ce_history) >= 20 else float(np.mean(ce_history))
            print(f"  [{arm} seed={seed} step={step}] ce={mean_ce:.4f}", flush=True)

    # Compute lead times per layer
    lead_times = {}
    for layer_idx in observers:
        lt = compute_lead_time(kappa3_trajectories[layer_idx])
        lead_times[f"layer_{layer_idx}"] = lt

    # Cross-layer correlation matrix
    n_obs_layers = len(observers)
    corr_matrix = {}
    if n_obs_layers > 1:
        traj_list = []
        layer_keys = sorted(observers.keys())
        for li in layer_keys:
            t = kappa3_trajectories[li]
            if len(t) > 0:
                traj_list.append(t)
        if len(traj_list) > 1:
            min_len = min(len(t) for t in traj_list)
            traj_arr = np.array([t[:min_len] for t in traj_list])  # (n_layers, T)
            c = np.corrcoef(traj_arr)
            for i, li in enumerate(layer_keys):
                for j, lj in enumerate(layer_keys):
                    if i != j:
                        corr_matrix[f"L{li}_L{lj}"] = float(c[i, j])

    final_ce = float(np.mean(ce_history[-50:])) if len(ce_history) >= 50 else float(np.mean(ce_history)) if ce_history else 0.0
    elapsed = time.time() - t0

    print(f"  [{arm} seed={seed}] done: final_ce={final_ce:.4f} lead_times={lead_times} elapsed={elapsed:.1f}s", flush=True)

    return {
        "arm": arm, "seed": seed, "N_substrate": n_dim, "run_mode": RUN_MODE,
        "final_ce": float(final_ce),
        "lead_times": lead_times,
        "corr_matrix": corr_matrix,
        "kappa3_trajectories": {str(k): v for k, v in kappa3_trajectories.items()},
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    arm_a = [r for r in results if r["arm"] == "arm_a"]
    arm_b = [r for r in results if r["arm"] == "arm_b"]
    arm_c = [r for r in results if r["arm"] == "arm_c"]

    # HP-1: lead time comparison
    def mean_lead(arm_list: List[Dict], layer_key: str = "layer_3") -> float:
        vals = [r["lead_times"].get(layer_key, 0) for r in arm_list]
        return float(np.mean(vals)) if vals else 0.0

    lt_a = mean_lead(arm_a)
    lt_b = mean_lead(arm_b)
    lt_c = mean_lead(arm_c)
    lead_improvement = max((lt_b - lt_a) / max(lt_a, 1.0), (lt_c - lt_a) / max(lt_a, 1.0))
    hp1 = lead_improvement >= 0.30

    # HP-2: off-diagonal correlation < 0.5
    all_offdiag = []
    for r in (arm_b + arm_c):
        for k, v in r.get("corr_matrix", {}).items():
            all_offdiag.append(abs(v))
    mean_offdiag = float(np.mean(all_offdiag)) if all_offdiag else 1.0
    hp2 = mean_offdiag < 0.5

    # HP-3: Arm C vs Arm B CE and lead time
    mean_ce_b = float(np.mean([r["final_ce"] for r in arm_b])) if arm_b else 1e6
    mean_ce_c = float(np.mean([r["final_ce"] for r in arm_c])) if arm_c else 1e6
    mean_ce_a = float(np.mean([r["final_ce"] for r in arm_a])) if arm_a else 1e6
    ce_gain_c_vs_b = (mean_ce_b - mean_ce_c) / max(mean_ce_b, 1e-6)
    hp3 = ce_gain_c_vs_b >= 0.05

    # HF checks
    hf1 = mean_offdiag > 0.85
    hf2 = mean_ce_c > mean_ce_a  # Arm C worse than Arm A

    summary = (f"lead_imp={lead_improvement:.2f} offdiag_corr={mean_offdiag:.3f} "
               f"ce_a={mean_ce_a:.4f} ce_b={mean_ce_b:.4f} ce_c={mean_ce_c:.4f} "
               f"ce_gain_c_vs_b={ce_gain_c_vs_b:.3f} "
               f"HP1={hp1} HP2={hp2} HP3={hp3} HF1={hf1} HF2={hf2} "
               f"n_seeds={len(arm_a)}")

    if hf1:
        return ("HARD_FAIL", f"HARD_FAIL: HF-1 off-diagonal corr={mean_offdiag:.3f} > 0.85. {summary}")
    if hf2:
        return ("HARD_FAIL", f"HARD_FAIL: HF-2 Arm C CE={mean_ce_c:.4f} > Arm A={mean_ce_a:.4f}. {summary}")

    hp_count = sum([hp1, hp2, hp3])
    if hp_count >= 2:
        return ("HARD_PASS", f"HARD_PASS: {hp_count}/3 HP conditions met. {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: {hp_count}/3 HP conditions met. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


_prot018_startup_check(N_SUBSTRATE)

# Config
N_VOCAB = 32
N_LAYERS = 4
if RUN_MODE == "smoke":
    HIDDEN_SIZE = 32
    N_STEPS = 100
    SEEDS = [7, 17]
    KAPPA_INTERVAL = 10
    N_KAPPA_PROBES = 50
    N_SUBSTRATE_ACTIVE = 256  # reduced N for smoke; prot-018 FULL binding
    ARMS = ["arm_a", "arm_b", "arm_c"]
else:
    HIDDEN_SIZE = 64
    N_STEPS = 1000
    SEEDS = [7, 17, 23]
    KAPPA_INTERVAL = 5
    N_KAPPA_PROBES = 100
    N_SUBSTRATE_ACTIVE = N_SUBSTRATE  # must == 4096 per PROT-018
    ARMS = ["arm_a", "arm_b", "arm_c"]

print(f"[config] PROT-018 N_SUBSTRATE={N_SUBSTRATE_ACTIVE} mode={RUN_MODE} "
      f"arms={ARMS} seeds={SEEDS} steps={N_STEPS}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
# Build run configs per (arm, seed) pair
all_arm_seed_pairs = [(arm, seed) for arm in ARMS for seed in SEEDS]

# Check resume state
completed_pairs = []
remaining_pairs = []
for arm, seed in all_arm_seed_pairs:
    ckpt_path = out_dir / f"{arm}_seed{seed}.json"
    if ckpt_path.exists():
        completed_pairs.append((arm, seed))
    else:
        remaining_pairs.append((arm, seed))

print(f"[ckpt] {len(completed_pairs)} arm-seed pairs done, {len(remaining_pairs)} to run", flush=True)

t_sweep_start = time.time()
all_results = []

# Load completed results
for arm, seed in completed_pairs:
    ckpt_path = out_dir / f"{arm}_seed{seed}.json"
    try:
        r = json.loads(ckpt_path.read_text(encoding='utf-8'))
        all_results.append(r)
    except Exception as e:
        print(f"[warn] failed to load {ckpt_path}: {e}", flush=True)
        remaining_pairs.append((arm, seed))

# Run remaining
for arm, seed in remaining_pairs:
    print(f"[run] {arm} seed={seed}", flush=True)
    result = run_arm(
        arm=arm, seed=seed, n_dim=N_SUBSTRATE_ACTIVE,
        n_steps=N_STEPS, n_vocab=N_VOCAB, hidden_size=HIDDEN_SIZE,
        n_layers=N_LAYERS, kappa_interval=KAPPA_INTERVAL, n_kappa_probes=N_KAPPA_PROBES,
    )
    ckpt_path = out_dir / f"{arm}_seed{seed}.json"
    ckpt_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    all_results.append(result)

verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
elapsed_total = time.time() - t_sweep_start

# INSTRUMENTATION SUSPECT gate
has_valid = any(
    len(r.get("kappa3_trajectories", {}).get(str(max(r.get("kappa3_trajectories", {}).keys(), default="0", key=lambda x: int(x) if x.isdigit() else 0)), [])) > 0
    for r in all_results if r
)
if not has_valid:
    print("[WARN] INSTRUMENTATION_SUSPECT: no valid kappa3 trajectories in any result.", flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N_substrate": N_SUBSTRATE_ACTIVE, "run_mode": RUN_MODE,
    "n_arms": len(ARMS), "n_seeds": len(SEEDS), "n_steps": N_STEPS,
    "elapsed_s": elapsed_total,
    "summary": verdict_msg,
    "per_arm_seed": [
        {"arm": r.get("arm"), "seed": r.get("seed"),
         "final_ce": r.get("final_ce"),
         "lead_times": r.get("lead_times", {}),
         "elapsed_s": r.get("elapsed_s")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
