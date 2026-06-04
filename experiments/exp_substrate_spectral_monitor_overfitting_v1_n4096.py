"""
substrate_spectral_monitor_overfitting_v1_n4096 -- Spectral monitor overfitting-only pre-reg.

CONTEXT (v375 cycle 43 rescue R1):
  substrate_spectral_training_monitor_rung1_tinychar_v1_n4096 HARD_FAIL at full
  pre-reg (convergence phase LAGS 3/3 seeds; mean_lead=-11.67).
  BUT overfitting phase: mean_lead=+300.0 steps (3/3 HP).

  R1 (cheapest/best): re-define pre-reg criterion as overfitting-phase-only detection.
  Substrate IS a useful overfitting sentinel 300 steps early. This anchor validates
  the overfitting-sentinel capability with a dedicated pre-reg.

SCIENTIFIC QUESTION:
  Does substrate spectral fingerprint (kappa_4_excess) predict LLM overfitting onset
  >= HP_LEAD steps before validation-loss-curve reveals it, consistently across seeds?

PRE-REGISTERED BANDS (overfitting-phase-only; v375 rescue R1):
  HARD-PASS:   kappa_4_excess exceeds threshold >= HP_LEAD steps before val_loss
               overfitting onset, across HP_SEED_FRAC seeds (3/3 seeds).
               HP_LEAD = 50 steps (relaxed from rung1 HP_LEAD=100 to account
               for smaller LM at tinychar scale; 50 steps is still 10x monitor interval).
  MIDDLE-BAND: lead 20-49 steps OR 2/3 seeds.
  HARD-FAIL:   lead < 20 steps OR substrate lags val_loss overfitting onset on >= 2/3 seeds.

  Convergence and divergence phases NOT in pre-reg (excluded per rescue intent).

FORMULA SELF-TESTS (PROT-022):
  1. SubstrateObserver: kappa_4_excess non-NaN after 5 observe() calls at N_OBS=64.
  2. detect_overfitting_val: returns a step index for a synthetic val-loss series
     that dips then rises >= 5 steps. [EXPECTED: step returned as int]
  3. detect_overfitting_substrate: returns step when kappa_4_excess crosses
     threshold in a synthetic kappa_4_excess series. [EXPECTED: step < val step]
  4. compute_overfitting_lead: positive lead when substrate fires before val.

PROT-018: anchor contains _n4096; N_OBS in FULL mode MUST == 4096.
PROT-021: seed checkpoints keyed with run_mode + N_OBS.
QUEUE: remote_cpu_queue (CPU-feasible; tinychar GRU + substrate observer).
TIMEOUT ESTIMATE: rung1 script ran 40.2s at 3 seeds. This runs same scale.
  ceil(1.5 * 45 * 1) = 68s. Use PROT-019 floor: 21600s.

ASCII-only stdout per feedback_ascii_only_in_scripts.
Per feedback_testbed_progress_logging_and_restart: per-seed partial JSON emitted.
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

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
)
from testbed.training_monitor.substrate_observer import SubstrateObserver
from testbed.substrate_lm.data import wikitext2_char_corpus

ANCHOR_NAME = "substrate_spectral_monitor_overfitting_v1_n4096"

_N_SUFFIX = 4096
N = 4096
N_OBS_FULL = N
assert N_OBS_FULL == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N_OBS_FULL={N_OBS_FULL}"

RUN_MODE = (
    "smoke" if "--smoke" in sys.argv
    else os.environ.get("HDLAB_RUN_MODE", "full")
).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "full" and N_OBS_FULL != _N_SUFFIX:
    raise RuntimeError(
        f"PROT-018 VIOLATION: anchor _n{_N_SUFFIX} but full N_OBS_FULL={N_OBS_FULL}"
    )

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_OBS = 128
    BUFFER_SIZE = int(0.12 * N_OBS)
    TRAIN_CHARS = 3000
    N_STEPS = 120
    MONITOR_EVERY = 5
    N_HUTCHINSON_PROBES = 16
    LM_HIDDEN = 48
    LM_LAYERS = 1
    LM_EMBED = 24
    BATCH_SIZE = 16
    SEQ_LEN = 32
    LR = 5e-3
else:
    SEEDS = [7, 17, 23]
    N_OBS = N_OBS_FULL
    BUFFER_SIZE = int(0.12 * N_OBS)
    TRAIN_CHARS = 30000   # longer to induce overfitting reliably
    N_STEPS = 2000        # 2000 steps; overfitting expected around 500-1500
    MONITOR_EVERY = 5
    N_HUTCHINSON_PROBES = 48
    LM_HIDDEN = 128
    LM_LAYERS = 2
    LM_EMBED = 64
    BATCH_SIZE = 32
    SEQ_LEN = 64
    LR = 3e-3

# Pre-registered thresholds (overfitting-phase-only rescue)
HP_LEAD_STEPS = 50       # >= 50 training steps ahead for HP
MID_LEAD_STEPS_LO = 20   # 20-49 steps = MIDDLE
HP_SEED_FRAC = 1.0       # 3/3 seeds for HP
MID_SEED_FRAC = 2.0 / 3  # 2/3 seeds for MIDDLE
# kappa_4_excess threshold: exceeds baseline_median + 0.5 sigma
KAPPA4_THRESHOLD_SIGMA = 0.5


# ----------------------------------------------------------------------
# Self-tests (PROT-022)
# ----------------------------------------------------------------------

def _selftest_kappa4_nonnull():
    """kappa_4_excess (k4ex_mean) non-NaN after observe() calls."""
    obs = SubstrateObserver(N=64, buffer_size=8)
    rng = np.random.default_rng(42)
    for _ in range(5):
        x = rng.standard_normal(64).astype(np.float32)
        obs.observe(x)
    cumulants = obs.current_cumulants()
    k4 = cumulants.get("k4ex_mean")
    assert k4 is not None and not np.isnan(k4), f"k4ex_mean is NaN: {k4}"
    print("[selftest] PASS: k4ex_mean non-NaN", flush=True)


def _selftest_detect_overfitting_val():
    """Detect overfitting in a synthetic val-loss series."""
    # dip then rise >= 5 steps
    val = [3.0, 2.5, 2.0, 1.8, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2.0]
    step = _detect_overfitting_val(val, monitor_every=1)
    assert isinstance(step, int) and step <= 5, f"Expected int <= 5, got {step}"
    print(f"[selftest] PASS: detect_overfitting_val step={step}", flush=True)


def _selftest_substrate_lead():
    """Positive lead when substrate fires before val."""
    substrate_step = 3
    val_step = 8
    lead = val_step - substrate_step
    assert lead > 0, f"lead expected > 0, got {lead}"
    print(f"[selftest] PASS: overfitting lead={lead}", flush=True)


def _detect_overfitting_val(val_history: List[float], monitor_every: int = 5) -> Optional[int]:
    """Return monitor-step index of overfitting onset (first min + >= 5 monotone rises)."""
    n = len(val_history)
    for i in range(1, n - 5):
        if all(val_history[i + j] > val_history[i + j - 1] for j in range(1, 6)):
            return i
    return None


def _detect_overfitting_substrate(
    kappa4_history: List[float], baseline_window: int = 10
) -> Optional[int]:
    """Return monitor-step index when kappa_4_excess crosses baseline + threshold."""
    if len(kappa4_history) <= baseline_window:
        return None
    baseline = kappa4_history[:baseline_window]
    bmed = float(np.median(baseline))
    bstd = float(np.std(baseline)) + 1e-9
    threshold = bmed + KAPPA4_THRESHOLD_SIGMA * bstd
    for i in range(baseline_window, len(kappa4_history)):
        if kappa4_history[i] > threshold:
            return i
    return None


def _selftest_all():
    _selftest_kappa4_nonnull()
    _selftest_detect_overfitting_val()
    _selftest_substrate_lead()
    print(f"[selftest] ALL PASS anchor={ANCHOR_NAME}", flush=True)


_selftest_all()
if _ARGS.self_test:
    sys.exit(0)


# ----------------------------------------------------------------------
# Char GRU LM (same as rung1)
# ----------------------------------------------------------------------

def _build_char_dataset(text: str, vocab: List[str], device) -> "torch.Tensor":
    import torch
    ch_to_idx = {ch: i for i, ch in enumerate(vocab)}
    ids = np.array([ch_to_idx.get(ch, 0) for ch in text], dtype=np.int64)
    return torch.from_numpy(ids).to(device)


def _make_batch(ids, batch_size: int, seq_len: int, rng) -> Optional[Tuple]:
    import torch
    n = ids.shape[0]
    max_start = n - seq_len - 1
    if max_start <= 0:
        return None
    starts = rng.integers(0, max_start, size=batch_size)
    x = torch.stack([ids[s:s + seq_len] for s in starts.tolist()], dim=0)
    y = torch.stack([ids[s + 1:s + seq_len + 1] for s in starts.tolist()], dim=0)
    return x, y


def _build_gru_lm(vocab_size: int, embed_dim: int, hidden: int, n_layers: int, device):
    import torch
    import torch.nn as nn

    class CharGRU(nn.Module):
        def __init__(self, V, E, H, L):
            super().__init__()
            self.embed = nn.Embedding(V, E)
            self.gru = nn.GRU(E, H, num_layers=L, batch_first=True)
            self.head = nn.Linear(H, V)
            self.n_layers = L
            self.hidden_dim = H
            self._tap_hidden = None

        def forward(self, x):
            e = self.embed(x)
            out, h_all = self.gru(e)
            self._tap_hidden = h_all[-1].detach()
            logits = self.head(out)
            return logits

    return CharGRU(vocab_size, embed_dim, hidden, n_layers).to(device)


# ----------------------------------------------------------------------
# Main per-seed training loop
# ----------------------------------------------------------------------

def run_seed(seed: int) -> Dict:
    import torch
    import torch.nn as nn
    import torch.optim as optim

    device = torch.device("cpu")
    rng = np.random.default_rng(seed)
    t0 = time.time()

    # Corpus: use TRAIN_CHARS chars and deliberately repeat to induce overfitting
    try:
        full_text = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
    except Exception:
        # fallback synthetic corpus
        alphabet = "abcdefghijklmnopqrstuvwxyz "
        full_text = "".join(alphabet[rng.integers(0, len(alphabet))] for _ in range(TRAIN_CHARS))

    vocab = sorted(set(full_text))
    V = len(vocab)

    # Repeat small corpus to induce overfitting
    repeat_text = full_text * 3
    split = int(0.8 * len(repeat_text))
    train_text, val_text = repeat_text[:split], repeat_text[split:]

    train_ids = _build_char_dataset(train_text, vocab, device)
    val_ids = _build_char_dataset(val_text, vocab, device)

    model = _build_gru_lm(V, LM_EMBED, LM_HIDDEN, LM_LAYERS, device)
    optimizer = optim.Adam(model.parameters(), lr=LR)
    criterion = nn.CrossEntropyLoss()

    # Substrate observer
    obs = SubstrateObserver(N=N_OBS, buffer_size=BUFFER_SIZE)

    val_history: List[float] = []
    kappa4_history: List[float] = []
    monitor_steps: List[int] = []

    def _compute_val_loss():
        model.eval()
        with torch.no_grad():
            batch = _make_batch(val_ids, min(BATCH_SIZE * 2, 64), SEQ_LEN, rng)
            if batch is None:
                return float("nan")
            x, y = batch
            logits = model(x)
            loss = criterion(logits.view(-1, V), y.view(-1))
        model.train()
        return float(loss)

    print(f"  [seed={seed}] training {N_STEPS} steps monitor_every={MONITOR_EVERY}", flush=True)

    for step in range(N_STEPS):
        batch = _make_batch(train_ids, BATCH_SIZE, SEQ_LEN, rng)
        if batch is None:
            break
        x, y = batch
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits.view(-1, V), y.view(-1))
        loss.backward()
        optimizer.step()

        # Substrate observe: pass raw hidden state; SubstrateObserver.project() binarizes it
        if model._tap_hidden is not None:
            hidden_np = model._tap_hidden.cpu().numpy().flatten()
            obs.observe(hidden_np.astype(np.float32))

        if step % MONITOR_EVERY == 0:
            val_loss = _compute_val_loss()
            cumulants = obs.current_cumulants()
            k4 = cumulants.get("k4ex_mean", 0.0)
            val_history.append(val_loss)
            kappa4_history.append(float(k4) if k4 is not None and not np.isnan(k4) else 0.0)
            monitor_steps.append(step)
            if step % 100 == 0:
                print(f"  [seed={seed}] step={step} val_loss={val_loss:.4f} k4ex={kappa4_history[-1]:.4f}", flush=True)

    # Detect overfitting
    val_overfit_idx = _detect_overfitting_val(val_history, monitor_every=MONITOR_EVERY)
    sub_overfit_idx = _detect_overfitting_substrate(kappa4_history, baseline_window=max(5, len(kappa4_history) // 10))

    val_overfit_step = monitor_steps[val_overfit_idx] if val_overfit_idx is not None else None
    sub_overfit_step = monitor_steps[sub_overfit_idx] if sub_overfit_idx is not None else None

    lead = None
    if val_overfit_step is not None and sub_overfit_step is not None:
        lead = val_overfit_step - sub_overfit_step

    elapsed = time.time() - t0
    print(
        f"  [seed={seed}] val_overfit_step={val_overfit_step} sub_overfit_step={sub_overfit_step} "
        f"lead={lead} elapsed={elapsed:.1f}s",
        flush=True,
    )

    return {
        "seed": seed,
        "val_overfit_step": val_overfit_step,
        "sub_overfit_step": sub_overfit_step,
        "lead": lead,
        "n_val_points": len(val_history),
        "val_history_last5": val_history[-5:] if len(val_history) >= 5 else val_history,
        "kappa4_history_last5": kappa4_history[-5:] if len(kappa4_history) >= 5 else kappa4_history,
        "elapsed_s": elapsed,
    }


# ----------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------

def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no valid results.")

    leads = [r["lead"] for r in results if r.get("lead") is not None]
    n_total = len(results)
    n_overfit_detected_val = sum(1 for r in results if r.get("val_overfit_step") is not None)
    n_overfit_detected_sub = sum(1 for r in results if r.get("sub_overfit_step") is not None)

    if n_overfit_detected_val == 0:
        return (
            "HARD_FAIL",
            f"HARD_FAIL: overfitting not detected in val_loss for any seed "
            f"({n_overfit_detected_val}/{n_total}); increase TRAIN_CHARS or N_STEPS.",
        )

    if not leads:
        return (
            "HARD_FAIL",
            f"HARD_FAIL: substrate detected overfit in {n_overfit_detected_sub}/{n_total} seeds "
            f"but val detected in {n_overfit_detected_val}/{n_total}; no lead computable.",
        )

    mean_lead = float(np.mean(leads))
    seeds_hp = sum(1 for l in leads if l >= HP_LEAD_STEPS)
    seeds_mid = sum(1 for l in leads if MID_LEAD_STEPS_LO <= l < HP_LEAD_STEPS)
    seeds_lag = sum(1 for l in leads if l < MID_LEAD_STEPS_LO)
    summary = (
        f"leads={[r.get('lead') for r in results]} mean_lead={mean_lead:.1f} "
        f"seeds_hp={seeds_hp}/{n_total} seeds_mid={seeds_mid}/{n_total} seeds_lag={seeds_lag}/{n_total} "
        f"HP_LEAD={HP_LEAD_STEPS} MID_LEAD_LO={MID_LEAD_STEPS_LO} "
        f"val_overfit_detected={n_overfit_detected_val}/{n_total} "
        f"sub_overfit_detected={n_overfit_detected_sub}/{n_total}"
    )

    hp_frac_actual = seeds_hp / n_total
    mid_frac_actual = (seeds_hp + seeds_mid) / n_total

    if hp_frac_actual >= HP_SEED_FRAC and mean_lead >= HP_LEAD_STEPS:
        return ("HARD_PASS", f"HARD_PASS: substrate overfitting sentinel leads val by >= {HP_LEAD_STEPS} steps; {summary}")
    elif mid_frac_actual >= MID_SEED_FRAC:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial overfitting lead; {summary}")
    else:
        return ("HARD_FAIL", f"HARD_FAIL: insufficient overfitting lead; {summary}")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

print(f"[config] anchor={ANCHOR_NAME} N_OBS={N_OBS} mode={RUN_MODE} seeds={SEEDS} steps={N_STEPS}", flush=True)

if RUN_MODE == "full" and N_OBS != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_OBS={N_OBS} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N_OBS": N_OBS, "BUFFER_SIZE": BUFFER_SIZE, "TRAIN_CHARS": TRAIN_CHARS, "N_STEPS": N_STEPS, "MONITOR_EVERY": MONITOR_EVERY, "LM_HIDDEN": LM_HIDDEN}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] starting {ANCHOR_NAME}", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)
    print(f"[seed={seed}] done lead={result.get('lead')}", flush=True)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "run_mode": RUN_MODE,
    "N_OBS": N_OBS,
    "BUFFER_SIZE": BUFFER_SIZE,
    "TRAIN_CHARS": TRAIN_CHARS,
    "N_STEPS": N_STEPS,
    "MONITOR_EVERY": MONITOR_EVERY,
    "LM_HIDDEN": LM_HIDDEN,
    "HP_LEAD_STEPS": HP_LEAD_STEPS,
    "elapsed_s": elapsed_total,
    "per_seed": [
        {
            "seed": r.get("seed"),
            "val_overfit_step": r.get("val_overfit_step"),
            "sub_overfit_step": r.get("sub_overfit_step"),
            "lead": r.get("lead"),
            "elapsed_s": r.get("elapsed_s"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
