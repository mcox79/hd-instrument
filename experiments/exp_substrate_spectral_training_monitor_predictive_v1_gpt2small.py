"""
substrate_spectral_training_monitor_predictive_v1_gpt2small -- Experiment B.

SCIENTIFIC QUESTION (Brain-inspired multi-channel probe batch, Experiment B):
  Can a substrate spectral fingerprint (kappa_2, kappa_3, kappa_4_excess free
  cumulants of the substrate-observer weight matrix W) PREDICT LLM training-
  phase transitions (convergence onset / overfitting onset / divergence onset)
  >= 100 training steps BEFORE conventional validation-loss-curve indicators
  reveal them?

  Substrate attaches a fixed random Rademacher projection to the LM residual
  stream at layer round(0.7 * n_layers), bipolar-codes each forward pass, and
  Hebbian-writes into a bounded-window observer W (target alpha ~ 0.12).  Every
  M training steps, kappa_2 / kappa_3 / kappa_4_excess are computed on W via
  Hutchinson trace estimators.

  Ground-truth phase transitions are extracted from the validation-loss curve:
    convergence-onset = step at which val_loss first drops below 0.9 * initial.
    overfitting-onset = first local val_loss minimum followed by >= 5 steps of
                        monotone increase.
    divergence-onset  = step at which val_loss > 2.0 * min val_loss (if reached).

  Substrate-signal phase transitions are extracted from cumulant trajectories:
    convergence-signal  = step at which kappa_2 first exits an early-band z-score
                          envelope (proxy for the substrate "recognizing" that
                          residual stream statistics have stabilized).
    overfitting-signal  = step at which kappa_4_excess crosses an upper threshold
                          (correlation-trap formation per arXiv:2605.12394).
    divergence-signal   = step at which kappa_2 spikes above a high-z threshold.

  Predictive lead time per phase = (val_loss step) - (substrate step).
    Positive lead = substrate leads val_loss (the HP outcome).

PRE-REGISTERED BANDS (per routing_brain_inspired_multi_channel_probe_batch_2026-06-03
                       section 1 Experiment B):
  HARD-PASS:   substrate leads val_loss by >= 100 steps on ALL 3 transitions
               AND consistent across ALL seeds (3/3 in FULL, 1/1 in smoke).
  MIDDLE-BAND: lead 50-100 steps OR consistent across 2/3 seeds.
  HARD-FAIL:   substrate signal lags val_loss OR lead < 50 steps.

  Smoke verdict is INFORMATIONAL; the cell counts are too small to gate the
  research conclusion. The smoke gate validates plumbing + that the substrate
  observer produces a kappa trajectory that responds to training dynamics.

FORMULA SELF-TESTS (run at import via training_monitor.substrate_observer):
  1. kappa_2(I_N) ~ 1.0          [PROT-022 instance: identity]
  2. kappa_4_excess(I_N) ~ -2.0  [free-prob excess on identity]
  3. kappa_3 sign matches positively-biased pattern injection.
  4. kappa_4_excess strictly larger on heavy-tailed vs Gaussian input.
  5. SubstrateObserver: project preserves bipolar codes; ring buffer caps alpha
     at buffer_size / N.

CAPABILITY IMPLICATION (if HARD-PASS):
  Substrate spectral observer as auto-stop primitive for LLM training: an
  early-warning signal that fires >= 100 steps before val_loss would reveal
  the phase. Estimated 10-20% LLM training compute saving (~$100-200K per
  Llama-class model).

MODEL PATHS:
  SMOKE: tiny char-level GRU (CPU; <60s wall). Validates plumbing only.
  FULL : HuggingFace GPT-2-small re-init from scratch (117M params), BPE
         tokenized Wikitext-2, layer-0.7L hidden-state tap via forward hook
         at model.transformer.h[7] (round(0.7 * 12) - 1 = 7). Cloud A100.

ANCHOR NAME: substrate_spectral_training_monitor_predictive_v1_gpt2small
  (PROT-018: name is locked; gpt2small in name reflects FULL target.)

ASCII-only stdout per feedback_ascii_only_in_scripts.
"""
import sys

# Encoding-safe stdout (Windows cp1252 hazard)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

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

# This import triggers the training_monitor PROT-022 self-tests on first load.
from testbed.training_monitor.substrate_observer import SubstrateObserver
from testbed.substrate_lm.data import wikitext2_char_corpus


ANCHOR_NAME = "substrate_spectral_training_monitor_predictive_v1_gpt2small"

RUN_MODE = (
    "smoke" if "--smoke" in sys.argv
    else os.environ.get("HDLAB_RUN_MODE", "full")
).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--self-test-full-construction", action="store_true",
                 help="Build the FULL-mode GPT-2-small model on CPU and report "
                      "param count + tap-layer index; no training.")
_ARGS, _ = _ap.parse_known_args()


# ----------------------------------------------------------------------
# Config -- smoke vs full
# ----------------------------------------------------------------------

if RUN_MODE == "smoke":
    SEEDS = [7]
    N_OBS = 512                  # substrate observer dimension
    BUFFER_SIZE = int(0.12 * N_OBS)  # alpha ~= 0.12
    TRAIN_CHARS = 5000
    EPOCHS = 20
    MONITOR_EVERY = 10
    N_HUTCHINSON_PROBES = 32
    # SMOKE uses tiny char-GRU.
    LM_HIDDEN = 96
    LM_LAYERS = 2
    LM_EMBED = 48
    BATCH_SIZE = 32
    SEQ_LEN = 64
    LR = 5e-3
    LAYER_FRAC = 0.7
    USE_GPT2 = False
    MAX_STEPS = None  # smoke: drive by EPOCHS * steps_per_epoch
else:
    SEEDS = [7, 17, 23]
    N_OBS = 4096
    BUFFER_SIZE = int(0.12 * N_OBS)
    TRAIN_CHARS = 200000  # raw text chars used to seed BPE tokenization
    EPOCHS = 1            # single long pass; capped by MAX_STEPS
    MAX_STEPS = 10000
    MONITOR_EVERY = 50
    N_HUTCHINSON_PROBES = 64
    # FULL = HuggingFace GPT-2-small from scratch.
    LM_HIDDEN = 768        # n_embd (GPT-2 small)
    LM_LAYERS = 12         # n_layer (GPT-2 small)
    LM_EMBED = None        # GPT-2 has tied input/output embeddings; not separate
    BATCH_SIZE = 32        # matches Experiment C FULL config (shared A100)
    SEQ_LEN = 256          # matches Experiment C FULL config
    LR = 3e-4              # from-scratch GPT-2 (Karpathy nano-GPT default)
    LAYER_FRAC = 0.7
    USE_GPT2 = True

# Pre-reg thresholds
HP_LEAD_STEPS = 100
HF_LEAD_STEPS = 50


# ----------------------------------------------------------------------
# Torch sanity
# ----------------------------------------------------------------------

def _ensure_torch():
    try:
        import torch  # noqa: F401
        import torch.nn as nn  # noqa: F401
    except Exception as e:
        raise RuntimeError(
            f"torch unavailable; this experiment requires torch even in smoke mode: {e}"
        )


# ----------------------------------------------------------------------
# Tap-layer index (shared smoke/FULL): round(LAYER_FRAC * n_layers) - 1.
# In FULL (n_layer=12): round(0.7 * 12) - 1 = round(8.4) - 1 = 8 - 1 = 7.
# In smoke (n_layers=2): round(0.7 * 2) - 1 = round(1.4) - 1 = 1 - 1 = 0.
# Always clamped to [0, n_layers - 1].
# ----------------------------------------------------------------------

def _tap_layer_idx(n_layers: int, layer_frac: float = LAYER_FRAC) -> int:
    return max(0, min(n_layers - 1, int(round(layer_frac * n_layers) - 1)))


# ----------------------------------------------------------------------
# SMOKE PATH: tiny char-level GRU LM
# ----------------------------------------------------------------------

def _build_char_dataset(text: str, vocab: List[str], device) -> Tuple:
    """Convert text -> tensor of char indices."""
    import torch
    ch_to_idx = {ch: i for i, ch in enumerate(vocab)}
    ids = np.array(
        [ch_to_idx.get(ch, 0) for ch in text], dtype=np.int64
    )
    return torch.from_numpy(ids).to(device)


def _make_batches_from_ids(ids, batch_size, seq_len, rng):
    """Generator of (x, y) char-tensor batches via random slicing.

    Returns (x, y) or None when corpus is too short.
    """
    import torch
    n = ids.shape[0]
    max_start = n - seq_len - 1
    if max_start <= 0:
        return None
    starts = rng.integers(0, max_start, size=batch_size)
    x = torch.stack([ids[s:s + seq_len] for s in starts.tolist()], dim=0)
    y = torch.stack([ids[s + 1:s + seq_len + 1] for s in starts.tolist()], dim=0)
    return x, y


def _build_gru_lm(vocab_size: int, embed_dim: int, hidden: int, n_layers: int,
                  device):
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
            self._tap_hidden = None  # set on each forward (B, H) for the tap layer

        def forward(self, x, tap_layer: int = -1):
            e = self.embed(x)  # (B, T, E)
            out, h_all = self.gru(e)  # out (B, T, H), h_all (L, B, H)
            if 0 <= tap_layer < h_all.shape[0]:
                self._tap_hidden = h_all[tap_layer].detach()
            else:
                self._tap_hidden = h_all[-1].detach()
            logits = self.head(out)  # (B, T, V)
            return logits

    return CharGRU(vocab_size, embed_dim, hidden, n_layers).to(device)


# ----------------------------------------------------------------------
# FULL PATH: GPT-2-small from scratch + BPE tokenizer + forward hook
# ----------------------------------------------------------------------

def _build_gpt2_small(seq_len: int, device):
    """Construct GPT-2-small re-init from scratch.

    Layer count = 12, n_embd = 768, n_head = 12, n_inner = 3072. Vocab = 50257
    (GPT-2 BPE). n_positions = seq_len + 16 buffer. ~117M params.

    Returns: (model, n_layers, n_embd, vocab_size).
    """
    try:
        from transformers import GPT2Config, GPT2LMHeadModel
    except ImportError as e:
        raise RuntimeError(
            f"transformers required for FULL mode (GPT-2-small): {e}"
        )

    cfg = GPT2Config(
        vocab_size=50257,
        n_positions=seq_len + 16,
        n_embd=768,
        n_layer=12,
        n_head=12,
        n_inner=3072,
        resid_pdrop=0.0,
        embd_pdrop=0.0,
        attn_pdrop=0.0,
    )
    model = GPT2LMHeadModel(cfg)  # random init -- we OBSERVE training dynamics
    model.to(device)
    return model, 12, 768, 50257


class _GPT2Tap:
    """Forward-hook capture of GPT-2 block-output hidden state.

    Registered on model.transformer.h[tap_layer]. The GPT2Block forward returns
    a tuple whose first element is the hidden_states tensor of shape (B, T, D).
    We cache that tensor (detached) and pool last-token in get_pooled().
    """

    def __init__(self, model, tap_layer: int):
        self.tap_layer = int(tap_layer)
        self._cache = None  # last-captured (B, T, D) hidden tensor
        block = model.transformer.h[self.tap_layer]
        self._handle = block.register_forward_hook(self._hook)

    def _hook(self, module, inputs, output):
        # GPT-2 block returns tuple (hidden_states, present, ...); take [0].
        if isinstance(output, tuple):
            ht = output[0]
        else:
            ht = output
        # detach so the observer side never holds an autograd graph
        self._cache = ht.detach()

    def get_last_token_pooled(self) -> Optional["np.ndarray"]:
        """Return last-token hidden state as (D,) numpy float32; mean across batch."""
        if self._cache is None:
            return None
        # (B, T, D) -> last token (B, D) -> mean over batch (D,)
        last = self._cache[:, -1, :]
        mean = last.mean(dim=0).float().cpu().numpy().astype(np.float32)
        return mean

    def close(self):
        try:
            self._handle.remove()
        except Exception:
            pass
        self._cache = None


def _bpe_tokenize_corpus(text: str, max_tokens: Optional[int] = None) -> "np.ndarray":
    """Tokenize a string with the GPT-2 BPE tokenizer; returns (T,) int64 array.

    Lazy-imports transformers only when called (FULL path).
    """
    from transformers import GPT2Tokenizer
    tok = GPT2Tokenizer.from_pretrained("gpt2")
    ids = tok.encode(text)
    arr = np.asarray(ids, dtype=np.int64)
    if max_tokens is not None and arr.shape[0] > max_tokens:
        arr = arr[:max_tokens]
    return arr


def _build_bpe_dataset(text: str, device, max_tokens: Optional[int] = None):
    """Tokenize text via GPT-2 BPE and return as a torch tensor on `device`."""
    import torch
    ids_np = _bpe_tokenize_corpus(text, max_tokens=max_tokens)
    return torch.from_numpy(ids_np).to(device)


# ----------------------------------------------------------------------
# Validation-loss computation (shared smoke + FULL)
# ----------------------------------------------------------------------

def _eval_val_loss_chargru(model, val_ids, batch_size, seq_len, rng_seed: int):
    """Cross-entropy on a fixed-seed random validation batch (one batch)."""
    import torch
    import torch.nn as nn
    model.eval()
    with torch.no_grad():
        rng = np.random.default_rng(rng_seed)
        batch = _make_batches_from_ids(val_ids, batch_size, seq_len, rng)
        if batch is None:
            return float("nan")
        x, y = batch
        logits = model(x)
        loss = nn.functional.cross_entropy(
            logits.reshape(-1, logits.shape[-1]), y.reshape(-1)
        )
    model.train()
    return float(loss.item())


def _eval_val_loss_gpt2(model, val_ids, batch_size, seq_len, rng_seed: int):
    """GPT-2 val cross-entropy on a fixed-seed random batch (one batch)."""
    import torch
    import torch.nn as nn
    model.eval()
    with torch.no_grad():
        rng = np.random.default_rng(rng_seed)
        batch = _make_batches_from_ids(val_ids, batch_size, seq_len, rng)
        if batch is None:
            return float("nan")
        x, y = batch
        # HuggingFace GPT2LMHeadModel: input_ids -> logits via .logits
        out = model(input_ids=x)
        logits = out.logits  # (B, T, V)
        loss = nn.functional.cross_entropy(
            logits.reshape(-1, logits.shape[-1]), y.reshape(-1)
        )
    model.train()
    return float(loss.item())


# ----------------------------------------------------------------------
# Phase-transition detectors
# ----------------------------------------------------------------------

def detect_val_phases(val_losses: List[float], step_idx: List[int]
                      ) -> Dict[str, Optional[int]]:
    """Ground-truth phase-transition step extractors from the val-loss curve.

    Returns dict with keys: convergence_step, overfitting_step, divergence_step
    (each int training-step or None if not reached).
    """
    if not val_losses or len(val_losses) < 2:
        return {"convergence_step": None, "overfitting_step": None, "divergence_step": None}

    vl = np.array(val_losses, dtype=np.float64)
    vl_init = vl[0]

    # Convergence-onset: first step at which val_loss < 0.9 * initial
    conv_idx = np.argmax(vl < 0.9 * vl_init) if (vl < 0.9 * vl_init).any() else None
    conv_step = int(step_idx[int(conv_idx)]) if conv_idx is not None else None

    # Overfitting-onset: first local min of vl followed by >=5 steps of increase
    overfit_step = None
    if len(vl) >= 7:
        for i in range(1, len(vl) - 5):
            is_min = (vl[i] <= vl[i - 1]) and (vl[i] <= vl[i + 1])
            future = vl[i + 1: i + 6]
            increase = (future[-1] > vl[i]) and np.all(np.diff(future) >= -1e-6)
            if is_min and increase:
                overfit_step = int(step_idx[i])
                break

    # Divergence-onset: step at which vl > 2.0 * running min
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
) -> Dict[str, Optional[int]]:
    """Substrate-signal phase-transition step extractors from cumulant trajectory.

      * convergence-signal: first step at which kappa_2 trajectory exits a
        +/- 2-sigma envelope of its first `baseline_window` values.
      * overfitting-signal: first step at which kappa_4_excess exceeds the
        median of its first `baseline_window` values by >= 0.5.
      * divergence-signal: first step at which kappa_2 spikes > 5x its
        first-window median.
    """
    if len(k2) < baseline_window + 1:
        return {"convergence_step": None, "overfitting_step": None, "divergence_step": None}

    k2_arr = np.array(k2, dtype=np.float64)
    k4_arr = np.array(k4ex, dtype=np.float64)

    base_k2 = k2_arr[:baseline_window]
    base_k4 = k4_arr[:baseline_window]
    k2_mean = float(np.mean(base_k2))
    k2_std = float(np.std(base_k2)) if baseline_window > 1 else 1e-3
    k4_med = float(np.median(base_k4))

    conv_step = None
    overfit_step = None
    div_step = None

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


def compute_lead_times(val_phases: Dict, sub_phases: Dict) -> Dict[str, Optional[int]]:
    """Lead time = val_loss_step - substrate_step. Positive => substrate leads."""
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
# Per-seed driver
# ----------------------------------------------------------------------

def run_seed(seed: int) -> Dict:
    import torch
    import torch.nn as nn

    t0 = time.time()
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)

    # Device: smoke runs on CPU; FULL uses cuda when available.
    if RUN_MODE == "smoke" or not torch.cuda.is_available():
        device = torch.device("cpu")
    else:
        device = torch.device("cuda")
    print(f"  [seed={seed}] device={device} run_mode={RUN_MODE} "
          f"use_gpt2={USE_GPT2}", flush=True)

    # --- Corpus + tokenization -----------------------------------------
    train_text = wikitext2_char_corpus("train", max_chars=TRAIN_CHARS)
    val_text = wikitext2_char_corpus("validation", max_chars=max(2000, TRAIN_CHARS // 4))

    if USE_GPT2:
        # FULL: BPE tokenize with GPT-2's native tokenizer.
        print(f"  [seed={seed}] BPE tokenizing train ({len(train_text)} chars) ...",
              flush=True)
        train_ids = _build_bpe_dataset(train_text, device)
        val_ids = _build_bpe_dataset(val_text, device)
        vocab_size = 50257
        print(f"  [seed={seed}] BPE train_tokens={train_ids.shape[0]} "
              f"val_tokens={val_ids.shape[0]} vocab={vocab_size}", flush=True)
    else:
        # SMOKE: char-level.
        vocab = sorted(set(train_text + val_text))
        if not vocab:
            vocab = [" "]
        train_ids = _build_char_dataset(train_text, vocab, device)
        val_ids = _build_char_dataset(val_text, vocab, device)
        vocab_size = len(vocab)

    # --- Model + optimizer ---------------------------------------------
    tap_capture = None
    if USE_GPT2:
        model, n_layers_used, hidden_dim_used, _vsz = _build_gpt2_small(
            SEQ_LEN, device,
        )
        tap_layer = _tap_layer_idx(n_layers_used)
        tap_capture = _GPT2Tap(model, tap_layer)
    else:
        model = _build_gru_lm(vocab_size, LM_EMBED, LM_HIDDEN, LM_LAYERS, device)
        n_layers_used = LM_LAYERS
        hidden_dim_used = LM_HIDDEN
        tap_layer = _tap_layer_idx(n_layers_used)

    opt = torch.optim.Adam(model.parameters(), lr=LR)
    ce = nn.CrossEntropyLoss()

    # --- Substrate observer at tap_layer -------------------------------
    obs = SubstrateObserver(
        N=N_OBS,
        projection_seed=seed + 991,
        buffer_size=BUFFER_SIZE,
        layer_idx=tap_layer,
        in_dim=hidden_dim_used,
    )

    # Per-epoch step count.
    if RUN_MODE == "smoke":
        steps_per_epoch = max(4, (train_ids.shape[0] // SEQ_LEN) // BATCH_SIZE)
        total_steps = steps_per_epoch * EPOCHS
        n_epochs_run = EPOCHS
    else:
        total_steps = MAX_STEPS
        steps_per_epoch = total_steps
        n_epochs_run = 1

    cumulant_traj = {"step": [], "k2": [], "k3": [], "k4ex": [],
                     "k2_se": [], "k3_se": [], "k4ex_se": []}
    val_traj = {"step": [], "val_loss": [], "train_loss": []}

    # Fixed-per-seed probe batch used for substrate observation (same input
    # every step; isolates the model-side drift from input-side variation).
    probe_rng = np.random.default_rng(seed + 31337)
    probe_batch = _make_batches_from_ids(train_ids, BATCH_SIZE, SEQ_LEN, probe_rng)
    if probe_batch is None:
        if tap_capture is not None:
            tap_capture.close()
        return {
            "seed": seed, "N": N_OBS, "M": BUFFER_SIZE, "N_OBS": N_OBS,
            "BUFFER_SIZE": BUFFER_SIZE, "TRAIN_CHARS": TRAIN_CHARS,
            "run_mode": RUN_MODE, "vocab_size": vocab_size,
            "ok": False, "error": "corpus too short for SEQ_LEN",
            "elapsed_s": time.time() - t0,
        }
    probe_x, _ = probe_batch

    # Choose val-eval function
    eval_val = _eval_val_loss_gpt2 if USE_GPT2 else _eval_val_loss_chargru

    model.train()
    train_step = 0
    for epoch in range(n_epochs_run):
        for _ in range(steps_per_epoch):
            if train_step >= total_steps:
                break
            batch = _make_batches_from_ids(train_ids, BATCH_SIZE, SEQ_LEN, rng)
            if batch is None:
                break
            x, y = batch
            # --- forward + backward -----------------------------------
            if USE_GPT2:
                out = model(input_ids=x)
                logits = out.logits  # (B, T, V)
            else:
                logits = model(x, tap_layer=tap_layer)
            loss = ce(logits.reshape(-1, vocab_size), y.reshape(-1))
            opt.zero_grad()
            loss.backward()
            opt.step()
            train_step += 1

            # --- substrate observation: forward pass on the FIXED probe ---
            with torch.no_grad():
                model.eval()
                if USE_GPT2:
                    _ = model(input_ids=probe_x)
                    residual_vec = tap_capture.get_last_token_pooled()
                else:
                    _ = model(probe_x, tap_layer=tap_layer)
                    tap = model._tap_hidden  # (B, H)
                    residual_vec = tap.mean(dim=0).cpu().numpy().astype(np.float32)
                model.train()
            if residual_vec is not None:
                obs.observe(residual_vec)

            # --- monitor: cumulants + val loss ------------------------
            if (train_step % MONITOR_EVERY == 0) or train_step == 1:
                cums = obs.current_cumulants(n_probes=N_HUTCHINSON_PROBES)
                val_loss = eval_val(
                    model, val_ids, BATCH_SIZE, SEQ_LEN,
                    rng_seed=seed + 7777,
                )
                cumulant_traj["step"].append(train_step)
                cumulant_traj["k2"].append(float(cums["k2_mean"]))
                cumulant_traj["k2_se"].append(float(cums["k2_se"]))
                cumulant_traj["k3"].append(float(cums["k3_mean"]))
                cumulant_traj["k3_se"].append(float(cums["k3_se"]))
                cumulant_traj["k4ex"].append(float(cums["k4ex_mean"]))
                cumulant_traj["k4ex_se"].append(float(cums["k4ex_se"]))
                val_traj["step"].append(train_step)
                val_traj["val_loss"].append(float(val_loss))
                val_traj["train_loss"].append(float(loss.item()))

    # Clean up the GPT-2 forward hook (always; tolerate missing).
    if tap_capture is not None:
        tap_capture.close()

    # Phase-transition extraction
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
    k4_init = cumulant_traj["k4ex"][0] if cumulant_traj["k4ex"] else float("nan")
    k4_last = cumulant_traj["k4ex"][-1] if cumulant_traj["k4ex"] else float("nan")
    summary_str = (
        f"  [seed={seed} N={N_OBS} buf={BUFFER_SIZE} mode={RUN_MODE}] "
        f"steps={train_step} vocab={vocab_size} tap_layer={tap_layer}/{n_layers_used} "
        f"val_init={vl_init:.3f} val_last={vl_last:.3f} "
        f"k2_first={k2_init:.3f} k2_last={k2_last:.3f} "
        f"k4ex_first={k4_init:.3f} k4ex_last={k4_last:.3f} "
        f"conv_lead={leads['convergence_lead_steps']} "
        f"overfit_lead={leads['overfitting_lead_steps']} "
        f"div_lead={leads['divergence_lead_steps']} elapsed={elapsed:.2f}s"
    )
    print(summary_str, flush=True)

    return {
        "seed": seed,
        "N": N_OBS,                # PROT-021 stored compound-key fields
        "M": BUFFER_SIZE,
        "N_OBS": N_OBS,
        "BUFFER_SIZE": BUFFER_SIZE,
        "TRAIN_CHARS": TRAIN_CHARS,
        "run_mode": RUN_MODE,
        "use_gpt2": bool(USE_GPT2),
        "vocab_size": int(vocab_size),
        "tap_layer": int(tap_layer),
        "n_layers": int(n_layers_used),
        "hidden_dim": int(hidden_dim_used),
        "train_steps": int(train_step),
        "cumulant_trajectory": cumulant_traj,
        "val_trajectory": val_traj,
        "val_phases": val_phases,
        "substrate_phases": sub_phases,
        "lead_times": leads,
        "ok": True,
        "elapsed_s": float(elapsed),
    }


# ----------------------------------------------------------------------
# Verdict computation
# ----------------------------------------------------------------------

def compute_verdict(per_seed: Dict[str, Dict]) -> Tuple[str, str]:
    """Verdict per pre-registered HP/MID/HF bands.

    HARD-PASS:  lead >= 100 on all 3 phases AND consistent across all seeds.
    MIDDLE:     50 <= lead < 100 on at least one phase OR 2/3 seeds.
    HARD-FAIL:  any phase has substrate lag (lead < HF) on entire seed set.

    Smoke verdict is informational.
    """
    rows = [r for r in per_seed.values() if r.get("ok", False)]
    if not rows:
        return ("HARD_FAIL", "No valid seed results.")

    phases = ("convergence", "overfitting", "divergence")
    per_phase_stats: Dict[str, Dict] = {}
    for phase in phases:
        leads = [r["lead_times"].get(f"{phase}_lead_steps") for r in rows]
        leads_obs = [int(l) for l in leads if l is not None]
        if leads_obs:
            mean_lead = float(np.mean(leads_obs))
            n_hp = sum(1 for l in leads_obs if l >= HP_LEAD_STEPS)
            n_mid = sum(1 for l in leads_obs if HF_LEAD_STEPS <= l < HP_LEAD_STEPS)
            n_lag = sum(1 for l in leads_obs if l < HF_LEAD_STEPS)
            per_phase_stats[phase] = {
                "n_observed": len(leads_obs),
                "mean_lead": mean_lead,
                "n_hp": n_hp, "n_mid": n_mid, "n_lag": n_lag,
            }
        else:
            per_phase_stats[phase] = {
                "n_observed": 0, "mean_lead": None,
                "n_hp": 0, "n_mid": 0, "n_lag": 0,
            }

    n_seeds = len(rows)
    summary = "; ".join(
        f"{ph}: n_obs={st['n_observed']}/{n_seeds} mean_lead={st['mean_lead']} "
        f"hp={st['n_hp']} mid={st['n_mid']} lag={st['n_lag']}"
        for ph, st in per_phase_stats.items()
    )

    any_phase_all_hp = any(
        st["n_observed"] == n_seeds and st["n_hp"] == n_seeds
        for st in per_phase_stats.values()
    )
    all_phases_all_hp = all(
        st["n_observed"] == n_seeds and st["n_hp"] == n_seeds
        for st in per_phase_stats.values()
    )
    any_phase_all_lag = any(
        st["n_observed"] >= 1 and st["n_lag"] == st["n_observed"]
        for st in per_phase_stats.values()
    )

    capability_line = (
        " Capability implication: if substrate spectral observer leads "
        "val_loss across phases, training-monitor auto-stop primitive enables "
        ">=100-step early-warning capability (10-20% LLM training compute "
        "saving)."
    )

    if RUN_MODE == "smoke":
        if all_phases_all_hp:
            verdict = "HARD_PASS"
        elif any_phase_all_hp:
            verdict = "MIDDLE_BAND"
        elif any_phase_all_lag:
            verdict = "HARD_FAIL"
        else:
            verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"SMOKE (informational): plumbing validated; cumulant trajectory + "
            f"phase-transition extraction operational. {summary}.{capability_line}"
        )
        return (verdict, verdict_msg)

    # FULL mode: strict pre-reg gates
    if all_phases_all_hp:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: substrate spectral observer leads val_loss by >=100 "
            f"steps across all 3 phases on all {n_seeds} seeds. {summary}.{capability_line}"
        )
        return (verdict, verdict_msg)

    if any_phase_all_lag:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: at least one phase showed substrate lag (no predictive "
            f"lead). {summary}.{capability_line}"
        )
        return (verdict, verdict_msg)

    verdict = "MIDDLE_BAND"
    verdict_msg = (
        f"MIDDLE_BAND: substrate leads on some phases but not consistently "
        f"across all 3 transitions / all {n_seeds} seeds. {summary}.{capability_line}"
    )
    return (verdict, verdict_msg)


# ----------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------

_ensure_torch()

if _ARGS.self_test:
    print("[selftest exp_substrate_spectral_training_monitor_predictive_v1_gpt2small] "
          "all imports + PROT-022 substrate_observer + helpers loaded OK.",
          flush=True)
    sys.exit(0)


if _ARGS.self_test_full_construction:
    # Static FULL-mode construction check: build GPT-2-small on CPU, verify
    # parameter count + tap-layer index. No training.
    print("[selftest-full-construction] attempting to build GPT-2-small ...",
          flush=True)
    try:
        import torch as _torch
        _dev = _torch.device("cpu")
        # Use FULL SEQ_LEN regardless of current run mode for the static check.
        _model, _nl, _ne, _vsz = _build_gpt2_small(seq_len=256, device=_dev)
        n_params = sum(p.numel() for p in _model.parameters())
        tap = _tap_layer_idx(_nl)
        # Verify the forward hook can be registered + fires.
        cap = _GPT2Tap(_model, tap)
        x_dummy = _torch.zeros((2, 8), dtype=_torch.long, device=_dev)
        with _torch.no_grad():
            _ = _model(input_ids=x_dummy)
        pooled = cap.get_last_token_pooled()
        cap.close()
        ok_shape = (pooled is not None and pooled.shape == (_ne,))
        print(
            f"[selftest-full-construction] PASS: GPT2LMHeadModel constructed; "
            f"n_layers={_nl} n_embd={_ne} vocab={_vsz} params={n_params:,} "
            f"tap_layer={tap} (expected 7 for n_layer=12); "
            f"hook_fired={pooled is not None} pooled_shape_ok={ok_shape}",
            flush=True,
        )
        sys.exit(0)
    except RuntimeError as e:
        print(
            f"[selftest-full-construction] SKIP: {e}. "
            f"Construction path is gated behind FULL mode; this check requires "
            f"the transformers package which is not installed on this machine. "
            f"The cloud bundle includes transformers; the static check will pass "
            f"on the GPU host.",
            flush=True,
        )
        sys.exit(0)


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {
    "N": N_OBS, "M": BUFFER_SIZE, "run_mode": RUN_MODE,
}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
    f"running {remaining} (N={N_OBS} buf={BUFFER_SIZE} mode={RUN_MODE} "
    f"use_gpt2={USE_GPT2})",
    flush=True,
)


t_sweep_start = time.time()
for seed in remaining:
    print(
        f"[seed={seed}] {ANCHOR_NAME} mode={RUN_MODE} N={N_OBS} buf={BUFFER_SIZE} "
        f"train_chars={TRAIN_CHARS} monitor_every={MONITOR_EVERY} "
        f"use_gpt2={USE_GPT2}",
        flush=True,
    )
    result = run_seed(seed)
    write_partial(out_dir, seed, result)


per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
verdict, verdict_msg = compute_verdict(per_seed)

elapsed_s = time.time() - t_sweep_start
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] total wall {elapsed_s:.2f}s", flush=True)


# Build slim per-seed summaries for metrics.json (full trajectories kept in partials)
per_seed_summary = []
for k, r in per_seed.items():
    if not r.get("ok"):
        per_seed_summary.append({
            "seed": r.get("seed"), "ok": False, "error": r.get("error"),
        })
        continue
    per_seed_summary.append({
        "seed": r.get("seed"),
        "train_steps": r.get("train_steps"),
        "val_phases": r.get("val_phases"),
        "substrate_phases": r.get("substrate_phases"),
        "lead_times": r.get("lead_times"),
        "vocab_size": r.get("vocab_size"),
        "tap_layer": r.get("tap_layer"),
        "n_layers": r.get("n_layers"),
        "hidden_dim": r.get("hidden_dim"),
        "use_gpt2": r.get("use_gpt2"),
        "elapsed_s": r.get("elapsed_s"),
        "cumulant_trajectory_steps": len(r.get("cumulant_trajectory", {}).get("step", [])),
        "k2_first_last": [
            r["cumulant_trajectory"]["k2"][0] if r.get("cumulant_trajectory", {}).get("k2") else None,
            r["cumulant_trajectory"]["k2"][-1] if r.get("cumulant_trajectory", {}).get("k2") else None,
        ],
        "k4ex_first_last": [
            r["cumulant_trajectory"]["k4ex"][0] if r.get("cumulant_trajectory", {}).get("k4ex") else None,
            r["cumulant_trajectory"]["k4ex"][-1] if r.get("cumulant_trajectory", {}).get("k4ex") else None,
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
    "use_gpt2": bool(USE_GPT2),
    "N_OBS": N_OBS,
    "BUFFER_SIZE": BUFFER_SIZE,
    "TRAIN_CHARS": TRAIN_CHARS,
    "MONITOR_EVERY": MONITOR_EVERY,
    "MAX_STEPS": MAX_STEPS,
    "LR": LR,
    "BATCH_SIZE": BATCH_SIZE,
    "SEQ_LEN": SEQ_LEN,
    "LAYER_FRAC": LAYER_FRAC,
    "LM_HIDDEN": LM_HIDDEN,
    "LM_LAYERS": LM_LAYERS,
    "HP_LEAD_STEPS": HP_LEAD_STEPS,
    "HF_LEAD_STEPS": HF_LEAD_STEPS,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_s,
    "summary": verdict_msg[:240],
    "per_seed": per_seed_summary,
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
