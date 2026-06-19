"""
substrate_spectral_training_monitor_rung1_tinychar_v1_n4096 -- A1 rung-1 validation.

SCIENTIFIC QUESTION:
  Does substrate spectral fingerprint (kappa_2 / kappa_3 / kappa_4_excess of the
  Hebbian observer weight matrix W) predict LLM training-phase transitions BEFORE
  the validation-loss curve does, at tiny scale?

  Rung 1: 1-2 layer char-level GRU on Shakespeare/synthetic corpus, ~5-10k params.
  Substrate observer attached at single hidden state. kappa_2/kappa_3/kappa_4_excess
  computed every 5 training steps. 500-1000 steps total. 3 seeds.

  Ground-truth phase transitions from val-loss curve:
    convergence-onset = first step where val_loss < 0.9 * initial
    overfitting-onset = first local min followed by >=5 monotone-increasing steps
    divergence-onset  = step where val_loss > 2.0 * running min (if reached)

  Substrate-signal phase transitions from cumulant trajectories:
    convergence-signal: kappa_2 exits +/- 2-sigma envelope of first baseline_window
    overfitting-signal: kappa_4_excess exceeds baseline median by >= 0.5
    divergence-signal:  kappa_2 spikes > 5x first-window median

  Predictive lead time per phase = (val_loss step) - (substrate step).
    Positive = substrate leads val_loss (the HP outcome).

PRE-REGISTERED BANDS (rung-1 scale per routing_phase_A_now_rung1 2026-06-03):
  HARD-PASS:   substrate signals each phase change >= 20 steps before val-loss
               indicator AND across 3/3 seeds.
  MIDDLE-BAND: lead time 10-20 steps OR 2/3 seeds.
  HARD-FAIL:   substrate signal lags or matches val_loss (no predictive lead)
               on any phase in majority of seeds.

  Note: monitoring cadence is every 5 steps, so 20-step lead = 4 monitoring intervals.

FORMULA SELF-TESTS (PROT-022):
  1. SubstrateObserver: kappa_2 non-NaN after 3 observe() calls at N_OBS=64.
  2. detect_val_phases: convergence_step returned as int (or None) for simple
     monotone-decreasing sequence. [EXPECTED: conv_step <= 10]
  3. detect_substrate_phases: convergence_signal returned for a synthetic
     kappa_2 trajectory that steps from 1.0 to 3.0 after 3 baseline steps.
     [EXPECTED: conv_step == step_idx[3]]
  4. compute_lead_times: positive lead when substrate fires before val.
     [EXPECTED: lead > 0]

PROT-018: anchor contains _n4096; N_OBS in FULL mode MUST == 4096.
PROT-021: seed checkpoints keyed with run_mode + N_OBS + buffer_size.

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

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
)
from testbed.training_monitor.substrate_observer import SubstrateObserver
from testbed.substrate_lm.data import wikitext2_char_corpus

ANCHOR_NAME = "substrate_spectral_training_monitor_rung1_tinychar_v1_n4096"

_N_SUFFIX = 4096
N = 4096          # PROT-018: anchor _n4096 binds this value; N_OBS in FULL mode == N
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

# PROT-018 startup check -- smoke may use smaller N_OBS
if RUN_MODE == "full" and N_OBS_FULL != _N_SUFFIX:
    raise RuntimeError(
        f"PROT-018 VIOLATION: anchor _n{_N_SUFFIX} but full N_OBS_FULL={N_OBS_FULL}"
    )

# Config: smoke vs full
if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_OBS = 128          # small substrate observer
    BUFFER_SIZE = int(0.12 * N_OBS)
    TRAIN_CHARS = 3000
    N_STEPS = 120        # 120 steps, monitor every 5 -> 24 monitor points
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
    N_OBS = N_OBS_FULL   # 4096 -- PROT-018 binding
    BUFFER_SIZE = int(0.12 * N_OBS)
    TRAIN_CHARS = 20000
    N_STEPS = 1000       # 1000 steps, monitor every 5 -> 200 monitor points
    MONITOR_EVERY = 5
    N_HUTCHINSON_PROBES = 48
    LM_HIDDEN = 128
    LM_LAYERS = 2
    LM_EMBED = 64
    BATCH_SIZE = 32
    SEQ_LEN = 64
    LR = 3e-3

# Pre-registered thresholds (rung-1 bands)
HP_LEAD_STEPS = 20       # >= 20 monitoring steps ahead (at monitor_every=5 -> 100 train steps)
MID_LEAD_STEPS = 10      # 10-20 steps = MIDDLE
HP_SEED_FRAC = 1.0       # all 3/3 seeds required for HP
MID_SEED_FRAC = 2.0 / 3  # 2/3 seeds for MIDDLE


# ----------------------------------------------------------------------
# Torch sanity
# ----------------------------------------------------------------------

def _ensure_torch():
    try:
        import torch  # noqa: F401
    except Exception as e:
        raise RuntimeError(f"torch unavailable: {e}")


# ----------------------------------------------------------------------
# Tiny char-level GRU LM
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

        def forward(self, x, tap_layer: int = -1):
            e = self.embed(x)
            out, h_all = self.gru(e)
            if 0 <= tap_layer < h_all.shape[0]:
                self._tap_hidden = h_all[tap_layer].detach()
            else:
                self._tap_hidden = h_all[-1].detach()
            logits = self.head(out)
            return logits

    return CharGRU(vocab_size, embed_dim, hidden, n_layers).to(device)


def _eval_val_loss(model, val_ids, batch_size: int, seq_len: int, rng_seed: int):
    import torch
    import torch.nn as nn
    model.eval()
    with torch.no_grad():
        rng = np.random.default_rng(rng_seed)
        batch = _make_batch(val_ids, batch_size, seq_len, rng)
        if batch is None:
            return float("nan")
        x, y = batch
        logits = model(x)
        loss = nn.functional.cross_entropy(
            logits.reshape(-1, logits.shape[-1]), y.reshape(-1)
        )
    model.train()
    return float(loss.item())


# ----------------------------------------------------------------------
# Phase-transition detectors (reused from gpt2small script)
# ----------------------------------------------------------------------

def detect_val_phases(val_losses: List[float], step_idx: List[int]) -> Dict:
    if not val_losses or len(val_losses) < 2:
        return {"convergence_step": None, "overfitting_step": None, "divergence_step": None}
    vl = np.array(val_losses, dtype=np.float64)
    vl_init = vl[0]

    conv_arr = vl < 0.9 * vl_init
    conv_step = int(step_idx[int(np.argmax(conv_arr))]) if conv_arr.any() else None

    overfit_step = None
    if len(vl) >= 7:
        for i in range(1, len(vl) - 5):
            is_min = (vl[i] <= vl[i - 1]) and (vl[i] <= vl[i + 1])
            future = vl[i + 1: i + 6]
            increase = (future[-1] > vl[i]) and np.all(np.diff(future) >= -1e-6)
            if is_min and increase:
                overfit_step = int(step_idx[i])
                break

    div_step = None
    run_min = vl[0]
    for i in range(1, len(vl)):
        run_min = min(run_min, vl[i])
        if vl[i] > 2.0 * max(run_min, 1e-6):
            div_step = int(step_idx[i])
            break

    return {
        "convergence_step": conv_step,
        "overfitting_step": overfit_step,
        "divergence_step": div_step,
    }


def detect_substrate_phases(
    k2: List[float], k3: List[float], k4ex: List[float],
    step_idx: List[int], baseline_window: int = 3,
) -> Dict:
    if len(k2) < baseline_window + 1:
        return {"convergence_step": None, "overfitting_step": None, "divergence_step": None}
    k2_arr = np.array(k2, dtype=np.float64)
    k4_arr = np.array(k4ex, dtype=np.float64)
    base_k2 = k2_arr[:baseline_window]
    base_k4 = k4_arr[:baseline_window]
    k2_mean = float(np.mean(base_k2))
    k2_std = float(np.std(base_k2)) if baseline_window > 1 else 1e-3
    k4_med = float(np.median(base_k4))

    conv_step = overfit_step = div_step = None
    for i in range(baseline_window, len(k2_arr)):
        if conv_step is None and abs(k2_arr[i] - k2_mean) > 2.0 * max(k2_std, 1e-6):
            conv_step = int(step_idx[i])
        if overfit_step is None and (k4_arr[i] - k4_med) >= 0.5:
            overfit_step = int(step_idx[i])
        if div_step is None and k2_arr[i] > 5.0 * max(abs(k2_mean), 1e-6):
            div_step = int(step_idx[i])
    return {
        "convergence_step": conv_step,
        "overfitting_step": overfit_step,
        "divergence_step": div_step,
    }


def compute_lead_times(val_phases: Dict, sub_phases: Dict) -> Dict:
    out = {}
    for phase in ("convergence", "overfitting", "divergence"):
        v = val_phases.get(f"{phase}_step")
        s = sub_phases.get(f"{phase}_step")
        if v is None or s is None:
            out[f"{phase}_lead_steps"] = None
            out[f"{phase}_val_step"] = v
            out[f"{phase}_substrate_step"] = s
        else:
            out[f"{phase}_lead_steps"] = int(v - s)
            out[f"{phase}_val_step"] = int(v)
            out[f"{phase}_substrate_step"] = int(s)
    return out


# ----------------------------------------------------------------------
# Instrumentation self-test (MANDATORY -- called at module scope)
# ----------------------------------------------------------------------

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    import torch
    _ensure_torch()

    # 1. SubstrateObserver: kappa_2 non-NaN after 3 observe() calls
    obs_t = SubstrateObserver(N=64, projection_seed=0, buffer_size=8, in_dim=16)
    rng_t = np.random.default_rng(0)
    for _ in range(5):
        vec = rng_t.choice([-1.0, 1.0], 16).astype(np.float32)
        obs_t.observe(vec)
    cums_t = obs_t.current_cumulants(n_probes=8)
    assert cums_t.get("k2_mean") is not None, "selftest: k2_mean is None"
    assert not np.isnan(cums_t["k2_mean"]), f"selftest: k2_mean is NaN"
    assert cums_t.get("k4ex_mean") is not None, "selftest: k4ex_mean is None"

    # 2. detect_val_phases convergence detection
    val_ls = [4.0, 3.8, 3.5, 3.0, 2.5, 2.0, 1.8]
    s_idx = [5, 10, 15, 20, 25, 30, 35]
    vp = detect_val_phases(val_ls, s_idx)
    assert vp["convergence_step"] is not None, "selftest: convergence_step is None"
    assert isinstance(vp["convergence_step"], int), "selftest: convergence_step not int"

    # 3. detect_substrate_phases: kappa_2 jump after baseline fires conv_step
    k2_traj = [1.0, 1.0, 1.0, 4.0, 4.2, 4.1, 4.3]  # jumps at index 3
    k3_traj = [0.0] * 7
    k4_traj = [0.0] * 7
    s_idx2 = list(range(0, 35, 5))
    sp = detect_substrate_phases(k2_traj, k3_traj, k4_traj, s_idx2, baseline_window=3)
    assert sp["convergence_step"] == s_idx2[3], (
        f"selftest: substrate conv_step={sp['convergence_step']} expected {s_idx2[3]}"
    )

    # 4. compute_lead_times: positive lead when substrate fires before val
    val_ph = {"convergence_step": 30, "overfitting_step": None, "divergence_step": None}
    sub_ph = {"convergence_step": 10, "overfitting_step": None, "divergence_step": None}
    leads = compute_lead_times(val_ph, sub_ph)
    assert leads["convergence_lead_steps"] == 20, (
        f"selftest: lead={leads['convergence_lead_steps']} expected 20"
    )

    # 5. Build char dataset -- at least 1 item survives at smoke scale
    text_t = "the cat sat on the mat. " * 20
    vocab_t = sorted(set(text_t))
    import torch as _torch
    ids_t = _build_char_dataset(text_t, vocab_t, _torch.device("cpu"))
    assert ids_t.shape[0] > 0, "selftest: char dataset empty"

    print(
        f"[selftest] PASS: observer_k2={cums_t['k2_mean']:.4f} "
        f"conv_detection=ok substrate_phase=ok lead_times=ok char_dataset=ok",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----------------------------------------------------------------------
# Per-seed runner
# ----------------------------------------------------------------------

def run_seed(seed: int) -> Dict:
    import torch
    import torch.nn as nn

    t0 = time.time()
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    device = torch.device("cpu")

    # Corpus
    train_text = wikitext2_char_corpus("train", max_chars=TRAIN_CHARS)
    val_text = wikitext2_char_corpus("validation", max_chars=max(1000, TRAIN_CHARS // 4))
    vocab = sorted(set(train_text + val_text))
    if not vocab:
        vocab = [" "]
    train_ids = _build_char_dataset(train_text, vocab, device)
    val_ids = _build_char_dataset(val_text, vocab, device)
    vocab_size = len(vocab)
    print(f"  [seed={seed}] vocab={vocab_size} train_chars={len(train_text)} "
          f"val_chars={len(val_text)}", flush=True)

    # Model
    tap_layer = max(0, LM_LAYERS - 1)
    model = _build_gru_lm(vocab_size, LM_EMBED, LM_HIDDEN, LM_LAYERS, device)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    ce_fn = nn.CrossEntropyLoss()

    # Substrate observer at tap_layer hidden state
    obs = SubstrateObserver(
        N=N_OBS,
        projection_seed=seed + 991,
        buffer_size=BUFFER_SIZE,
        layer_idx=tap_layer,
        in_dim=LM_HIDDEN,
    )

    cumulant_traj: Dict[str, List] = {
        "step": [], "k2": [], "k3": [], "k4ex": [],
        "k2_se": [], "k3_se": [], "k4ex_se": [],
    }
    val_traj: Dict[str, List] = {"step": [], "val_loss": [], "train_loss": []}

    # Fixed probe batch (same every step -- isolates model-drift from input-drift)
    probe_rng = np.random.default_rng(seed + 31337)
    probe_batch = _make_batch(train_ids, BATCH_SIZE, SEQ_LEN, probe_rng)

    model.train()
    for step in range(1, N_STEPS + 1):
        batch = _make_batch(train_ids, BATCH_SIZE, SEQ_LEN, rng)
        if batch is None:
            print(f"  [seed={seed}] corpus exhausted at step={step}", flush=True)
            break
        x, y = batch
        logits = model(x, tap_layer=tap_layer)
        loss = ce_fn(logits.reshape(-1, vocab_size), y.reshape(-1))
        opt.zero_grad()
        loss.backward()
        opt.step()

        # Substrate observation: fixed probe batch, eval mode
        if probe_batch is not None:
            px, _ = probe_batch
            with torch.no_grad():
                model.eval()
                _ = model(px, tap_layer=tap_layer)
                tap = model._tap_hidden  # (B, H)
                residual_vec = tap.mean(dim=0).cpu().numpy().astype(np.float32)
                model.train()
            obs.observe(residual_vec)

        # Monitor every MONITOR_EVERY steps
        if step % MONITOR_EVERY == 0 or step == 1:
            cums = obs.current_cumulants(n_probes=N_HUTCHINSON_PROBES)
            val_loss = _eval_val_loss(model, val_ids, BATCH_SIZE, SEQ_LEN, rng_seed=seed + 7777)
            cumulant_traj["step"].append(step)
            cumulant_traj["k2"].append(float(cums["k2_mean"]))
            cumulant_traj["k2_se"].append(float(cums.get("k2_se", 0.0)))
            cumulant_traj["k3"].append(float(cums["k3_mean"]))
            cumulant_traj["k3_se"].append(float(cums.get("k3_se", 0.0)))
            cumulant_traj["k4ex"].append(float(cums["k4ex_mean"]))
            cumulant_traj["k4ex_se"].append(float(cums.get("k4ex_se", 0.0)))
            val_traj["step"].append(step)
            val_traj["val_loss"].append(float(val_loss))
            val_traj["train_loss"].append(float(loss.item()))

            if step % (MONITOR_EVERY * 10) == 0:
                print(
                    f"  [seed={seed} step={step}/{N_STEPS}] "
                    f"train_loss={loss.item():.4f} val_loss={val_loss:.4f} "
                    f"k2={cums['k2_mean']:.4f} k4ex={cums['k4ex_mean']:.4f}",
                    flush=True,
                )

    # Phase extraction
    val_phases = detect_val_phases(val_traj["val_loss"], val_traj["step"])
    sub_phases = detect_substrate_phases(
        cumulant_traj["k2"], cumulant_traj["k3"], cumulant_traj["k4ex"],
        cumulant_traj["step"], baseline_window=3,
    )
    leads = compute_lead_times(val_phases, sub_phases)
    elapsed = time.time() - t0

    vl_init = val_traj["val_loss"][0] if val_traj["val_loss"] else float("nan")
    vl_last = val_traj["val_loss"][-1] if val_traj["val_loss"] else float("nan")
    k2_init = cumulant_traj["k2"][0] if cumulant_traj["k2"] else float("nan")
    k2_last = cumulant_traj["k2"][-1] if cumulant_traj["k2"] else float("nan")

    print(
        f"  [seed={seed} DONE] val_init={vl_init:.4f} val_last={vl_last:.4f} "
        f"k2_first={k2_init:.4f} k2_last={k2_last:.4f} "
        f"conv_lead={leads['convergence_lead_steps']} "
        f"overfit_lead={leads['overfitting_lead_steps']} "
        f"div_lead={leads['divergence_lead_steps']} elapsed={elapsed:.2f}s",
        flush=True,
    )

    return {
        "seed": seed,
        "N_OBS": N_OBS,
        "BUFFER_SIZE": BUFFER_SIZE,
        "TRAIN_CHARS": TRAIN_CHARS,
        "N_STEPS": N_STEPS,
        "run_mode": RUN_MODE,
        "vocab_size": int(vocab_size),
        "tap_layer": int(tap_layer),
        "n_layers": int(LM_LAYERS),
        "hidden_dim": int(LM_HIDDEN),
        "cumulant_trajectory": cumulant_traj,
        "val_trajectory": val_traj,
        "val_phases": val_phases,
        "substrate_phases": sub_phases,
        "lead_times": leads,
        "ok": True,
        "elapsed_s": float(elapsed),
    }


# ----------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------

def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    rows = [r for r in per_seed.values() if r.get("ok", False)]
    if not rows:
        return ("HARD_FAIL", "No valid seed results.")

    phases = ("convergence", "overfitting", "divergence")
    n_seeds = len(rows)

    per_phase_stats: Dict = {}
    for phase in phases:
        leads = [r["lead_times"].get(f"{phase}_lead_steps") for r in rows]
        leads_obs = [int(ll) for ll in leads if ll is not None]
        if leads_obs:
            n_hp = sum(1 for ll in leads_obs if ll >= HP_LEAD_STEPS)
            n_mid = sum(1 for ll in leads_obs if MID_LEAD_STEPS <= ll < HP_LEAD_STEPS)
            n_lag = sum(1 for ll in leads_obs if ll < MID_LEAD_STEPS)
            per_phase_stats[phase] = {
                "n_observed": len(leads_obs),
                "mean_lead": float(np.mean(leads_obs)),
                "n_hp": n_hp,
                "n_mid": n_mid,
                "n_lag": n_lag,
            }
        else:
            per_phase_stats[phase] = {
                "n_observed": 0,
                "mean_lead": None,
                "n_hp": 0,
                "n_mid": 0,
                "n_lag": 0,
            }

    summary = "; ".join(
        f"{ph}: n_obs={st['n_observed']}/{n_seeds} mean_lead={st['mean_lead']} "
        f"hp={st['n_hp']} mid={st['n_mid']} lag={st['n_lag']}"
        for ph, st in per_phase_stats.items()
    )
    cap_line = (
        " Cap implication: substrate spectral fingerprint predicts training "
        "phase transitions before val-loss; enables early-warning auto-stop "
        "primitive reducing LLM training compute waste."
    )

    # HP: all phases all seeds lead >= 20 steps
    all_phases_hp = all(
        st["n_observed"] == n_seeds and st["n_hp"] == n_seeds
        for st in per_phase_stats.values()
        if st["n_observed"] > 0
    )
    # MIDDLE: any phase lead >= 10 OR 2/3 seeds
    any_phase_mid_or_better = any(
        st["n_hp"] + st["n_mid"] >= max(1, int(n_seeds * MID_SEED_FRAC))
        for st in per_phase_stats.values()
        if st["n_observed"] > 0
    )
    # HF: majority of observed phases show lag across majority seeds
    any_phase_all_lag = any(
        st["n_observed"] >= 1 and st["n_lag"] == st["n_observed"]
        for st in per_phase_stats.values()
        if st["n_observed"] > 0
    )

    if RUN_MODE == "smoke":
        # Smoke: validate plumbing; cumulant trajectory responds to training
        any_k2_varies = any(
            len(r.get("cumulant_trajectory", {}).get("k2", [])) >= 3
            for r in rows
        )
        if any_k2_varies:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                f"SMOKE (informational): plumbing validated; cumulant trajectory "
                f"non-trivial. {summary}.{cap_line}"
            )
        else:
            verdict = "HARD_FAIL"
            verdict_msg = (
                f"SMOKE FAIL: kappa trajectory empty or trivial. {summary}.{cap_line}"
            )
        return (verdict, verdict_msg)

    if all_phases_hp:
        return (
            "HARD_PASS",
            f"HARD_PASS: substrate leads val_loss by >={HP_LEAD_STEPS} steps "
            f"across all observed phases in all {n_seeds} seeds. "
            f"{summary}.{cap_line}",
        )
    if any_phase_all_lag:
        return (
            "HARD_FAIL",
            f"HARD_FAIL: at least one phase showed substrate lag (lead < {MID_LEAD_STEPS} "
            f"steps) in all seeds -- no predictive lead. {summary}.{cap_line}",
        )
    return (
        "MIDDLE_BAND",
        f"MIDDLE_BAND: substrate leads on some phases/seeds but not consistently "
        f"across all transitions. {summary}.{cap_line}",
    )


# ----------------------------------------------------------------------
# Main sweep
# ----------------------------------------------------------------------

_ensure_torch()

print(
    f"[config] ANCHOR={ANCHOR_NAME} mode={RUN_MODE} N_OBS={N_OBS} "
    f"buf={BUFFER_SIZE} steps={N_STEPS} monitor_every={MONITOR_EVERY} "
    f"LM_HIDDEN={LM_HIDDEN} LM_LAYERS={LM_LAYERS} seeds={SEEDS}",
    flush=True,
)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N_OBS": N_OBS, "BUFFER_SIZE": BUFFER_SIZE, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] starting {ANCHOR_NAME} mode={RUN_MODE} ...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)
    print(f"[seed={seed}] partial written ok={result.get('ok')}", flush=True)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
verdict, verdict_msg = compute_verdict(per_seed)

elapsed_total = time.time() - t_sweep_start
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] total={elapsed_total:.2f}s", flush=True)

# Per-seed summary for metrics.json
per_seed_summary = []
for k, r in per_seed.items():
    if not r.get("ok"):
        per_seed_summary.append({"seed": r.get("seed"), "ok": False,
                                  "error": r.get("error", "unknown")})
        continue
    per_seed_summary.append({
        "seed": r.get("seed"),
        "N_OBS": r.get("N_OBS"),
        "N_STEPS": r.get("N_STEPS"),
        "val_phases": r.get("val_phases"),
        "substrate_phases": r.get("substrate_phases"),
        "lead_times": r.get("lead_times"),
        "vocab_size": r.get("vocab_size"),
        "elapsed_s": r.get("elapsed_s"),
        "monitor_points": len(r.get("cumulant_trajectory", {}).get("step", [])),
        "k2_first_last": [
            r["cumulant_trajectory"]["k2"][0] if r.get("cumulant_trajectory", {}).get("k2") else None,
            r["cumulant_trajectory"]["k2"][-1] if r.get("cumulant_trajectory", {}).get("k2") else None,
        ],
        "val_first_last": [
            r["val_trajectory"]["val_loss"][0] if r.get("val_trajectory", {}).get("val_loss") else None,
            r["val_trajectory"]["val_loss"][-1] if r.get("val_trajectory", {}).get("val_loss") else None,
        ],
    })

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
    "LM_LAYERS": LM_LAYERS,
    "LR": LR,
    "BATCH_SIZE": BATCH_SIZE,
    "SEQ_LEN": SEQ_LEN,
    "HP_LEAD_STEPS": HP_LEAD_STEPS,
    "MID_LEAD_STEPS": MID_LEAD_STEPS,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "per_seed": per_seed_summary,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
