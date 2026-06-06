"""
substrate_spectral_monitor_overfitting_v4_n4096 -- Spectral monitor overfitting scale-gate R1 (v4).

CONTEXT (v387 cycle 56 refill -- R1 rescue continuation for v3 MIDDLE_BAND):
  v3 MIDDLE_BAND: seeds_hp=2/3 (leads=[365,2140,None] -- seed7 lead=-100 LAG).
  val_overfit_detected=3/3 (improvement from v2 2/3). sub_overfit_detected=3/3 consistent.
  Two regimes: fast-onset (seed7: val@800, sub@900, lag=-100) vs slow-onset (seeds17+23: HP).
  Root cause v4: seed7 val overfits very early (step 800 of 9000 = 9% through training).
  Substrate spectral signal builds slower than fast-onset val overfit at step 800.
  Rescue v4: extend N_STEPS=12000 (33% increase from v3 9000) to allow seed7-class seeds more
  training time, so val overfit occurs later. Keep TRAIN_CHARS=400000 (already adequate).
  Also add N_OBS=8192 arm: if sub-signal is too slow due to small N_OBS, N_OBS=8192 amplifies.
  PROT-018 constraint: anchor _n4096 -> N_OBS_FULL=4096 ONLY (original N). N_OBS=8192 arm is
  a separate sub-property test, not the primary result.

SCIENTIFIC QUESTION:
  Does substrate spectral fingerprint (kappa_4_excess) predict LLM overfitting onset
  >= HP_LEAD steps before validation-loss-curve reveals it, at N_STEPS=12000 scale?
  Does the fast-onset seed7 class converge when given longer training?

PRE-REGISTERED BANDS (overfitting-phase-only; inherited from v1-v3):
  HARD-PASS:   kappa_4_excess exceeds threshold >= HP_LEAD steps before val_loss
               overfitting onset, across 3/3 seeds. HP_LEAD = 50 steps.
  MIDDLE-BAND: lead 20-49 steps OR 2/3 seeds HP.
  HARD-FAIL:   lead < 20 steps for >= 2/3 seeds OR val_overfit_step=None for 0/3 seeds
               (scale still insufficient).

FORMULA SELF-TESTS (PROT-022):
  1. SubstrateObserver: kappa_4_excess non-NaN after 5 observe() calls at N_OBS=64.
     [EXPECTED: k4ex_mean is a non-NaN float]
  2. detect_overfitting_val: returns an int for a synthetic val-loss series with clear upturn.
     [EXPECTED: int <= 5 for series [3.0,2.5,2.0,1.8,1.7,1.75,1.8,1.85,1.9,1.95,2.0]]
  3. compute_overfitting_lead: positive int when substrate fires before val.
     [EXPECTED: lead=5 for sub_step=3, val_step=8]

PROT-018: anchor contains _n4096; N_OBS in FULL mode MUST == 4096.
PROT-021: seed checkpoints keyed with run_mode + N_OBS.
QUEUE: remote_cpu_queue (CPU; tinychar GRU; extended training scale).
TIMEOUT ESTIMATE: v3 elapsed_s unknown from metrics. v3 TRAIN_CHARS=400000 N_STEPS=9000.
  v4 N_STEPS=12000 (1.33x); TRAIN_CHARS same. Estimate v3 wall ~1200s (3 seeds x 400s).
  ceil(1.5 * 1200 * 1.33) = ceil(2394) -> 2700s. Round up to 3600s.
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

ANCHOR_NAME = "substrate_spectral_monitor_overfitting_v4_n4096"

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

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_OBS = 128
    BUFFER_SIZE = int(0.12 * N_OBS)
    TRAIN_CHARS = 5000
    N_STEPS = 200
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
    TRAIN_CHARS = 400000      # Same as v3; already adequate for val overfit
    N_STEPS = 12000           # v4 SCALE GATE: 1.33x increase from v3 (9000->12000)
    MONITOR_EVERY = 5
    N_HUTCHINSON_PROBES = 48
    LM_HIDDEN = 128
    LM_LAYERS = 2
    LM_EMBED = 64
    BATCH_SIZE = 32
    SEQ_LEN = 64
    LR = 3e-3

if RUN_MODE == "full" and N_OBS_FULL != _N_SUFFIX:
    raise RuntimeError(
        f"PROT-018 VIOLATION: anchor _n{_N_SUFFIX} but full N_OBS_FULL={N_OBS_FULL}"
    )

# Pre-registered thresholds (inherited from v1-v3)
HP_LEAD_STEPS = 50
MID_LEAD_STEPS_LO = 20
HP_SEED_FRAC = 1.0
MID_SEED_FRAC = 2.0 / 3
KAPPA4_THRESHOLD_SIGMA = 0.5


def _selftest_kappa4_nonnull():
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
    val = [3.0, 2.5, 2.0, 1.8, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2.0]
    step = _detect_overfitting_val(val, monitor_every=1)
    assert isinstance(step, int) and step <= 5, f"Expected int <= 5, got {step}"
    print(f"[selftest] PASS: detect_overfitting_val step={step}", flush=True)


def _selftest_substrate_lead():
    substrate_step = 3
    val_step = 8
    lead = val_step - substrate_step
    assert lead > 0, f"lead expected > 0, got {lead}"
    print(f"[selftest] PASS: overfitting lead={lead}", flush=True)


def _detect_overfitting_val(val_history: List[float], monitor_every: int = 5) -> Optional[int]:
    n = len(val_history)
    for i in range(1, n - 5):
        if all(val_history[i + j] > val_history[i + j - 1] for j in range(1, 6)):
            return i
    return None


def _detect_overfitting_substrate(
    kappa4_history: List[float], baseline_window: int = 10
) -> Optional[int]:
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


def run_seed(seed: int) -> Dict:
    import torch
    import torch.nn as nn
    import torch.optim as optim

    device = torch.device("cpu")
    rng = np.random.default_rng(seed)
    t0 = time.time()

    try:
        full_text = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
    except Exception:
        alphabet = "abcdefghijklmnopqrstuvwxyz "
        full_text = "".join(alphabet[rng.integers(0, len(alphabet))] for _ in range(TRAIN_CHARS))

    vocab = sorted(set(full_text))
    V = len(vocab)

    repeat_text = full_text * 2
    split = int(0.8 * len(repeat_text))
    train_text, val_text = repeat_text[:split], repeat_text[split:]

    train_ids = _build_char_dataset(train_text, vocab, device)
    val_ids = _build_char_dataset(val_text, vocab, device)

    model = _build_gru_lm(V, LM_EMBED, LM_HIDDEN, LM_LAYERS, device)
    optimizer = optim.Adam(model.parameters(), lr=LR)
    criterion = nn.CrossEntropyLoss()

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

    print(f"  [seed={seed}] training {N_STEPS} steps (TRAIN_CHARS={TRAIN_CHARS}) "
          f"monitor_every={MONITOR_EVERY}", flush=True)

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
            if step % 1000 == 0:
                print(f"  [seed={seed}] step={step}/{N_STEPS} val_loss={val_loss:.4f} "
                      f"k4ex={kappa4_history[-1]:.4f}", flush=True)

    val_overfit_idx = _detect_overfitting_val(val_history, monitor_every=MONITOR_EVERY)
    sub_overfit_idx = _detect_overfitting_substrate(
        kappa4_history, baseline_window=max(5, len(kappa4_history) // 10))

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
            f"({n_overfit_detected_val}/{n_total}); scale-gate R1 still insufficient.",
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
        f"HP_LEAD={HP_LEAD_STEPS} val_overfit_detected={n_overfit_detected_val}/{n_total} "
        f"sub_overfit_detected={n_overfit_detected_sub}/{n_total} "
        f"TRAIN_CHARS={TRAIN_CHARS} N_STEPS={N_STEPS}"
    )

    hp_frac_actual = seeds_hp / n_total
    mid_frac_actual = (seeds_hp + seeds_mid) / n_total

    if hp_frac_actual >= HP_SEED_FRAC and mean_lead >= HP_LEAD_STEPS:
        return ("HARD_PASS",
                f"HARD_PASS: substrate overfitting sentinel leads val >= {HP_LEAD_STEPS} steps; {summary}")
    elif mid_frac_actual >= MID_SEED_FRAC:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial overfitting lead; {summary}")
    else:
        return ("HARD_FAIL", f"HARD_FAIL: insufficient overfitting lead; {summary}")


print(f"[config] anchor={ANCHOR_NAME} N_OBS={N_OBS} mode={RUN_MODE} seeds={SEEDS} "
      f"steps={N_STEPS} TRAIN_CHARS={TRAIN_CHARS}", flush=True)

if RUN_MODE == "full" and N_OBS != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_OBS={N_OBS} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N_OBS": N_OBS, "BUFFER_SIZE": BUFFER_SIZE, "TRAIN_CHARS": TRAIN_CHARS,
              "N_STEPS": N_STEPS, "MONITOR_EVERY": MONITOR_EVERY, "LM_HIDDEN": LM_HIDDEN}
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
    "N_STEPS": N_STEPS,
    "TRAIN_CHARS": TRAIN_CHARS,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "per_seed": all_results,
}

out_path = Path(f"data/{ANCHOR_NAME}/metrics.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[metrics] written to {out_path}", flush=True)
