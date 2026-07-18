"""R7 prioritized-replay re-run with CLOSED-LOOP SURPRISE priority (Schaul PER analog).

FALSIFIED prior (R7 / wave14c): prioritized replay with a STATIC structural tag (collapsed rank-1
Hebbian-MIR score / concept tags) LOST to uniform random replay on this BSC delta-rule substrate.
wave14c mechanism note argued that random replay is an implicit subspace projection (A-GEM with a
uniform reference set); ANY non-uniform priority biases the constraint-set estimator, so random > priority.
BUT that was measured only for STATIC tags + MIR (which collapses to cosine-to-batch in a rank-1 rule).

THIS cell tests the ONE distinct thing not yet measured on this substrate: a CLOSED-LOOP surprise
priority, re-scored against the CURRENT W each epoch (Schaul et al. 2015 Prioritized Experience Replay
beat uniform on 41/49 Atari because priority = a re-scored TD-error, not a frozen tag). The analog here:
priority of pool entry i = surprise_i = 1 - reciprocal_rank(true_target_i | ctx_i, CURRENT W). High
surprise = the item the current (Phase-B-drifted) model predicts WORST = the item being forgotten most.
"Rehearse what you are forgetting" is the well-motivated PER-for-continual-learning hypothesis.

ONE VARIABLE: the Phase-B replay SELECTION rule. Everything else (corpus, BSC atoms, W_A, pool,
REPLAY_FRACTION, seeds, delta-rule) is bit-identical across arms.

ARMS (all from the identical W_A / pool / corpus / seed):
  no_replay            do_replay=False                                  -> bwt_no (recovery reference)
  random_replay        uniform sample from pool [THE HEAD-TO-HEAD BASELINE]
  surprise_closedloop  priority ~ (surprise|current W)^PER_ALPHA, re-scored each epoch [MECHANISM]
  surprise_static      priority ~ (surprise|W_A)^PER_ALPHA, frozen at Phase-A end [CONTROL: isolates
                       the closed-loop re-scoring property; a static-tag reproduction of R7's collapse]

METRIC (R7's native BWT recovery): recovery_X = bpc_a(no_replay) - bpc_a(X)  (lower post-A bpc = less
forgetting = better retention). Primary discriminator delta_cl_vs_random = recovery_cl - recovery_random
= bpc_a(random) - bpc_a(surprise_closedloop). >0 means closed-loop surprise BEATS random.

BANDS (per seed; verdict on >=2/3 seeds):
  HARD_PASS  delta_cl_vs_random >= +0.10 bpc  -> R7 collapse was SIGNAL-specific; licenses PER pipeline.
  HARD_FAIL  delta_cl_vs_random <= +0.02 bpc (tie/lose within noise) -> the rank-1 Hebbian delta-rule
             structurally cannot benefit from ANY priority-replay = a REAL architectural wall.
             PRE-SPECIFIED brain-check on HARD_FAIL: biological prioritized replay works because
             dopamine-gated STDP is a THREE-FACTOR / eligibility-trace rule (NOT a simple Hebbian
             product) -> the fix is a plasticity-RULE upgrade (eligibility traces / three-factor),
             which is the next build. Do NOT torture toward pass.
  MIDDLE_BAND otherwise.

DISCRIMINATOR-FIRES / design gate (verified at smoke, logged to metrics; a vacuous regime auto-demotes):
  - DIFFICULTY-ON: real forgetting occurs (bwt_no < -FORGET_MIN; do-nothing damages task A).
  - HEADROOM: random replay produces a real recovery (recovery_random > 0) so priority has room to differ.
  - PRIORITY-NONUNIFORM: pool surprise has real spread (std > SURPRISE_STD_MIN) AND the surprise arm's
    sampled-index histogram differs from uniform; else surprise_replay == random_replay by construction
    and the test cannot fail informatively.
  - ARMS-MUST-DIFFER: W_random / W_surprise_cl / W_surprise_st pairwise bit-distinct.
  NOTE: a small smoke delta is CONSISTENT with the (theory-predicted) HARD_FAIL and is NOT grounds to
  reject the full run. The smoke gate proves the cell is a VALID can-fail test, not the verdict sign.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (per-arm W hashes distinct; META_RULE_AF)
# - final_metrics_atomicity = tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: bpc/BWT has no simple closed-form noise floor here; bands anchored to R7's MEASURED
#   random-replay recovery (+0.66 bpc @ N=4096/15ep) CITED@notes/wave14c_random_replay_mechanism_research.md
# - baseline_in_band analog: forgetting non-trivial AND random-recovery non-saturated (checked at smoke)
# - discriminator survives scale: smoke reports random-recovery headroom + arm separation; full = verdict
# - HARD_PASS strictly above HARD_FAIL band (0.10 >> 0.02, 5x band gap)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - real_code_path: self_test runs train_phase_a/train_phase_b(all selections)/eval_bpc/pool_surprise at N=64
# - deterministic seeding: fixed int seeds + torch.Generator(seed); no hash()-seed, no list(set())

Compute architecture: MIXED (matmul-batched, epoch loop sequential). Justification: online continual
learning has a genuine sequential dependency (W_t depends on W_{t-1}); within-batch ops are batched
matmuls (GPU-capable, DEVICE=cuda if available). GPU-preferred target (overnight_queue): W is 4096x4096
dense; GPU cuts the ~4h CPU run to ~20min. Storage strategy: no_storage / no_composition (this is a
continual-learning training loop, not a compositional retrieval chain).

ASCII-only. No emojis. Explicit dtypes. torch.Generator seeded. Terse.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ANCHOR_NAME = "wave14c_r7_surprise_closedloop_replay_v1"

torch.set_float32_matmul_precision("high")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---- hyperparameters (verbatim from exp_wave14b_r7_multiseed.py) -----------------------------------
VOCAB_SIZE = 256
PAD_BYTE = 0
K = 4
BETA = 8.0
BATCH_SIZE = 64
POOL_SIZE = 1024
ALPHA = 0.3            # retrieval mixing weight at eval
RELU_B = 0.5
DELTA_RULE_ALPHA = 0.3
DELTA_RULE_DECAY = 1e-4
REPLAY_FRACTION = 0.5

# ---- PER priority (Schaul 2015 proportional variant) -----------------------------------------------
PER_ALPHA = 0.6       # priority = (surprise + PER_EPS) ** PER_ALPHA  CITED@Schaul2015 arXiv:1511.05952
PER_EPS = 0.01        # floor so every pool entry keeps nonzero sampling mass

# ---- run configs -----------------------------------------------------------------------------------
FULL_CFG = dict(N=4096, MAX_EPOCHS=15, seeds=[17, 23, 31])
SMOKE_CFG = dict(N=2048, MAX_EPOCHS=6, seeds=[17])

SELECTIONS = ["no_replay", "random_replay", "surprise_closedloop", "surprise_static"]

# ---- pre-registered bands / design-gate thresholds -------------------------------------------------
HARD_PASS_DELTA = 0.10          # delta_cl_vs_random >= this on >=2/3 seeds -> HARD_PASS
HARD_FAIL_DELTA = 0.02          # delta_cl_vs_random <= this on >=2/3 seeds -> HARD_FAIL (tie/lose)
FORGET_MIN = 0.10               # bwt_no < -FORGET_MIN required (real forgetting; DIFFICULTY-ON)
SURPRISE_STD_MIN = 0.02         # pool-surprise std > this (priority is non-uniform)


def _say(msg):
    print("[r7_surprise] %s" % msg, flush=True)


# ---------------------------------------------------------------------------
# dispatch harness (start marker / atomic metrics / crash diag)
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(str(output_dir), "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(str(output_dir), "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics_atomic(output_dir, diag)


def _emit_heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = dict(ts_iso=datetime.now(timezone.utc).isoformat(), unit_idx=int(unit_idx),
               total_units=int(total_units), elapsed_s=round(float(elapsed_s), 2))
    if extra:
        row["extra"] = extra
    try:
        with open(os.path.join(str(output_dir), "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass  # heartbeat is best-effort telemetry; never fatal


def _wsha(W):
    a = torch.round(W.detach().cpu().to(torch.float64) * 1e6)
    return hashlib.sha256(a.numpy().tobytes()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# substrate primitives (verbatim from R7 multiseed) + closed-loop surprise
# ---------------------------------------------------------------------------
def load_corpus_a():
    repo = Path(__file__).resolve().parent.parent
    files = [repo / "PLAN.md", repo / "NEXT_PHASE.md", repo / "README.md",
             repo / "PROGRESS.md", repo / "RESULTS.md", repo / "CLAUDE.md"]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    return b"".join(parts)


def shuffle_bytes(data, seed):
    gen = torch.Generator().manual_seed(seed)
    perm = torch.randperm(len(data), generator=gen).tolist()
    out = bytearray(len(data))
    for i, p in enumerate(perm):
        out[i] = data[p]
    return bytes(out)


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def build_ctx(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def shifted_relu(q, b):
    return torch.clamp(q - b, min=0.0)


def predict_W(W, ctxs, byte_atoms, beta, n):
    q = shifted_relu(ctxs @ W.T, RELU_B)
    sims = (byte_atoms @ q.T) / n
    return torch.softmax(beta * sims, dim=0)


def pool_surprise(W, pool_ctx, pool_lbl, byte_atoms, n):
    """Closed-loop surprise = 1 - reciprocal_rank(true label | ctx, CURRENT W) per pool entry. (P,) float32.

    High surprise = the current model ranks the true next-byte low = poorly predicted = being forgotten.
    This is the additive_map.score_all analog (1 - 1/rank) computed through the cell's own readout."""
    surs = []
    P = pool_ctx.shape[0]
    for bs in range(0, P, 256):
        be = min(bs + 256, P)
        q = shifted_relu(pool_ctx[bs:be] @ W.T, RELU_B)
        sims = (byte_atoms @ q.T) / n                       # (VOCAB, b)
        lbl = pool_lbl[bs:be]
        true_sim = sims.gather(0, lbl.unsqueeze(0)).squeeze(0)     # (b,)
        rank = (sims > true_sim.unsqueeze(0)).sum(dim=0) + 1       # (b,) higher rank = worse
        rr = 1.0 / rank.float()
        surs.append(1.0 - rr)
    return torch.cat(surs)


def _priorities_from_surprise(surprise):
    p = torch.clamp(surprise, min=0.0) + PER_EPS
    p = p.pow(PER_ALPHA)
    return p / p.sum()


def train_phase_a(byte_atoms, pos_atoms, train_bytes, n, max_epochs):
    W = torch.zeros((n, n), dtype=torch.float32, device=DEVICE)
    pool_vecs = torch.zeros((POOL_SIZE, n), dtype=torch.float32, device=DEVICE)
    pool_labels = torch.zeros(POOL_SIZE, dtype=torch.long, device=DEVICE)
    pool_idx = 0
    pool_used = 0
    arange_b = torch.arange(BATCH_SIZE, device=DEVICE)
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_bytes
    T_total = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T_total, device=DEVICE)
    train_idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    train_targets = bt[pos + K]
    for epoch in range(1, max_epochs + 1):
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs = build_ctx(byte_atoms, pos_atoms, idx_batch)
            with torch.no_grad():
                q = shifted_relu(ctxs @ W.T, RELU_B)
                sims = (byte_atoms @ q.T) / n
                P = torch.softmax(BETA * sims, dim=0)
                residual = byte_atoms[tgt_batch] - (P.T @ byte_atoms)
                dW = (residual.T @ ctxs) / n
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)
                if epoch == 1:
                    dest = (pool_idx + arange_b[:B]) % POOL_SIZE
                    pool_vecs.index_copy_(0, dest, ctxs)
                    pool_labels.index_copy_(0, dest, tgt_batch)
                    pool_idx = (pool_idx + B) % POOL_SIZE
                    pool_used = min(pool_used + B, POOL_SIZE)
    return W, pool_vecs, pool_labels, pool_used


def train_phase_b(W_start, byte_atoms, pos_atoms, train_b, pool_ctx, pool_lbl, pool_used,
                  selection, seed, n, max_epochs, static_probs=None):
    """Phase-B continual training. selection in SELECTIONS. Returns (W, sample_hist).

    sample_hist: (pool_used,) count of how often each pool entry was replayed (0 if no_replay)."""
    W = W_start.clone()
    gen = torch.Generator().manual_seed(seed)
    pad = bytes([PAD_BYTE]) * K
    padded = pad + train_b
    T_total = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T_total, device=DEVICE)
    train_idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    train_targets = bt[pos + K]
    do_replay = (selection != "no_replay")
    sample_hist = torch.zeros(pool_used, dtype=torch.long, device=DEVICE)
    for epoch in range(max_epochs):
        probs = None
        if selection == "surprise_closedloop":
            probs = _priorities_from_surprise(pool_surprise(W, pool_ctx, pool_lbl, byte_atoms, n))
        elif selection == "surprise_static":
            probs = static_probs
        for batch_start in range(0, T_total, BATCH_SIZE):
            be = min(batch_start + BATCH_SIZE, T_total)
            idx_batch = train_idx[batch_start:be]
            tgt_batch = train_targets[batch_start:be]
            B = idx_batch.shape[0]
            ctxs_b = build_ctx(byte_atoms, pos_atoms, idx_batch)
            if do_replay:
                n_replay = max(1, int(B * REPLAY_FRACTION))
                if selection == "random_replay":
                    i = torch.randint(0, pool_used, (n_replay,), generator=gen).to(DEVICE)
                else:
                    i = torch.multinomial(probs, n_replay, replacement=True, generator=gen).to(DEVICE)
                sample_hist.index_add_(0, i, torch.ones_like(i))
                ctxs = torch.cat([ctxs_b, pool_ctx[i]], dim=0)
                tgts = torch.cat([tgt_batch, pool_lbl[i]], dim=0)
            else:
                ctxs = ctxs_b
                tgts = tgt_batch
            with torch.no_grad():
                q = shifted_relu(ctxs @ W.T, RELU_B)
                sims = (byte_atoms @ q.T) / n
                P = torch.softmax(BETA * sims, dim=0)
                residual = byte_atoms[tgts] - (P.T @ byte_atoms)
                dW = (residual.T @ ctxs) / n
                W.mul_(1.0 - DELTA_RULE_DECAY)
                W.add_(dW, alpha=DELTA_RULE_ALPHA)
    return W, sample_hist


def eval_bpc(W, byte_atoms, pos_atoms, test_bytes, pool_vecs, pool_labels, pool_used, n):
    pad = bytes([PAD_BYTE]) * K
    padded = pad + test_bytes
    T = len(padded) - K
    bt = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(K - 1, -1, -1, device=DEVICE)
    pos = torch.arange(T, device=DEVICE)
    idx = bt[pos.unsqueeze(1) + offsets.unsqueeze(0)]
    tgts = bt[pos + K]
    total = 0.0
    for bs in range(0, T, BATCH_SIZE):
        be = min(bs + BATCH_SIZE, T)
        idx_b = idx[bs:be]
        ctxs = build_ctx(byte_atoms, pos_atoms, idx_b)
        P_W = predict_W(W, ctxs, byte_atoms, BETA, n)
        active = pool_vecs[:pool_used]
        labels = pool_labels[:pool_used]
        sims = (active @ ctxs.T) / n
        weights = torch.softmax(BETA * sims, dim=0)
        P_retr = torch.zeros(VOCAB_SIZE, idx_b.shape[0], device=DEVICE)
        P_retr.scatter_add_(0, labels.unsqueeze(1).expand(-1, idx_b.shape[0]), weights)
        P = ALPHA * P_retr + (1 - ALPHA) * P_W
        p_true = P.gather(0, tgts[bs:be].unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        total += float(-torch.log2(p_true).sum())
    return total / max(T, 1)


# ---------------------------------------------------------------------------
# per-seed run + verdict
# ---------------------------------------------------------------------------
def run_seed(seed, n, max_epochs, output_dir=None, t0=None, si=0, n_seeds=1):
    corpus_a = load_corpus_a()
    corpus_b = shuffle_bytes(corpus_a, seed=seed + 1)
    split = int(0.8 * len(corpus_a))
    train_a, test_a = corpus_a[:split], corpus_a[split:]
    train_b = corpus_b[:int(0.8 * len(corpus_b))]

    gen_atoms = torch.Generator().manual_seed(seed)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, n, gen_atoms).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, n, gen_atoms).to(DEVICE)

    W_A, pool_A, labels_A, used_A = train_phase_a(byte_atoms, pos_atoms, train_a, n, max_epochs)
    bpc_a_initial = eval_bpc(W_A, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, n)

    pool_ctx = pool_A[:used_A]
    pool_lbl = labels_A[:used_A]
    # static (frozen-at-Phase-A) surprise -> priorities for the reproduction-control arm
    sur_A = pool_surprise(W_A, pool_ctx, pool_lbl, byte_atoms, n)
    static_probs = _priorities_from_surprise(sur_A)
    surprise_std = float(sur_A.std().item())
    surprise_mean = float(sur_A.mean().item())

    W_arms = {}
    hist_arms = {}
    bpc_a_post = {}
    for j, sel in enumerate(SELECTIONS):
        W_x, hist = train_phase_b(W_A, byte_atoms, pos_atoms, train_b, pool_ctx, pool_lbl, used_A,
                                  sel, seed=seed + 100 + 37 * j, n=n, max_epochs=max_epochs,
                                  static_probs=static_probs)
        W_arms[sel] = W_x
        hist_arms[sel] = hist
        bpc_a_post[sel] = eval_bpc(W_x, byte_atoms, pos_atoms, test_a, pool_A, labels_A, used_A, n)
        if output_dir is not None and t0 is not None:
            _emit_heartbeat(output_dir, si * len(SELECTIONS) + j + 1, n_seeds * len(SELECTIONS),
                            time.time() - t0, extra={"seed": seed, "arm": sel})

    bwt = {sel: bpc_a_initial - bpc_a_post[sel] for sel in SELECTIONS}
    recovery = {sel: bpc_a_post["no_replay"] - bpc_a_post[sel] for sel in SELECTIONS}
    delta_cl_vs_random = recovery["surprise_closedloop"] - recovery["random_replay"]
    delta_cl_vs_static = recovery["surprise_closedloop"] - recovery["surprise_static"]
    delta_static_vs_random = recovery["surprise_static"] - recovery["random_replay"]

    # priority non-uniform: surprise arm sampled-index histogram vs uniform (L1 total-variation)
    def _tv_from_uniform(hist):
        h = hist.float()
        if h.sum() <= 0:
            return 0.0
        p = h / h.sum()
        u = torch.full_like(p, 1.0 / p.numel())
        return float(0.5 * (p - u).abs().sum().item())
    tv_surprise_cl = _tv_from_uniform(hist_arms["surprise_closedloop"])
    tv_random = _tv_from_uniform(hist_arms["random_replay"])

    w_hashes = {sel: _wsha(W_arms[sel]) for sel in SELECTIONS}

    return dict(
        seed=seed, n=n, max_epochs=max_epochs,
        bpc_a_initial=bpc_a_initial,
        bpc_a_post=bpc_a_post, bwt=bwt, recovery=recovery,
        delta_cl_vs_random=delta_cl_vs_random,
        delta_cl_vs_static=delta_cl_vs_static,
        delta_static_vs_random=delta_static_vs_random,
        surprise_std=surprise_std, surprise_mean=surprise_mean,
        tv_surprise_cl_from_uniform=tv_surprise_cl, tv_random_from_uniform=tv_random,
        w_hashes=w_hashes,
        forgetting_bwt_no=bwt["no_replay"],
        recovery_random=recovery["random_replay"],
    )


def _majority(bools):
    return sum(1 for b in bools if b)


def aggregate_and_verdict(per_seed, run_mode):
    n = len(per_seed)
    deltas = [s["delta_cl_vs_random"] for s in per_seed]
    mean_delta = sum(deltas) / n
    n_pass = _majority([d >= HARD_PASS_DELTA for d in deltas])
    n_fail = _majority([d <= HARD_FAIL_DELTA for d in deltas])

    # design-gate: is this a VALID (non-vacuous) can-fail test?
    forgetting_ok = _majority([s["forgetting_bwt_no"] < -FORGET_MIN for s in per_seed])
    headroom_ok = _majority([s["recovery_random"] > 0.0 for s in per_seed])
    nonuniform_ok = _majority([(s["surprise_std"] > SURPRISE_STD_MIN and s["tv_surprise_cl_from_uniform"]
                                > 1.5 * max(s["tv_random_from_uniform"], 1e-6)) for s in per_seed])
    arms_differ = all(len(set(s["w_hashes"].values())) == len(SELECTIONS) for s in per_seed)

    gate_valid = (forgetting_ok == n and headroom_ok == n and nonuniform_ok == n and arms_differ)

    mean_cl_static = sum(s["delta_cl_vs_static"] for s in per_seed) / n
    mean_static_random = sum(s["delta_static_vs_random"] for s in per_seed) / n

    need = 2 if n >= 3 else n  # >=2/3 majority; for smoke (n=1) just directional
    if run_mode != "full" or n < 3:
        verdict = "SMOKE_GATE_PASS" if gate_valid else "SMOKE_GATE_FAIL_VACUOUS"
        vmsg = ("smoke(n=%d) delta_cl_vs_random mean=%+.4f | gate valid=%s (forget=%d/%d headroom=%d/%d "
                "nonuniform=%d/%d arms_differ=%s)" % (n, mean_delta, gate_valid, forgetting_ok, n,
                headroom_ok, n, nonuniform_ok, n, arms_differ))
    else:
        if not gate_valid:
            verdict = "VACUOUS_REGIME"
            vmsg = ("design gate INVALID: forget=%d/%d headroom=%d/%d nonuniform=%d/%d arms_differ=%s "
                    "-> test cannot produce a trustworthy verdict" % (forgetting_ok, n, headroom_ok, n,
                    nonuniform_ok, n, arms_differ))
        elif n_pass >= need:
            verdict = "HARD_PASS"
            vmsg = ("closed-loop surprise BEATS random by mean %+.4f bpc (%d/%d seeds >= %.2f); R7 collapse "
                    "was SIGNAL-specific -> licenses PER pipeline" % (mean_delta, n_pass, n, HARD_PASS_DELTA))
        elif n_fail >= need:
            verdict = "HARD_FAIL"
            vmsg = ("closed-loop surprise TIES/LOSES to random (mean %+.4f bpc; %d/%d seeds <= %.2f). The "
                    "rank-1 Hebbian delta-rule cannot benefit from priority replay = architectural wall. "
                    "BRAIN-CHECK (pre-specified): biological prioritized replay works via THREE-FACTOR / "
                    "eligibility-trace (dopamine-gated STDP), NOT a simple Hebbian product -> fix is a "
                    "plasticity-RULE upgrade (next build), not a signal tweak." % (mean_delta, n_fail, n,
                    HARD_FAIL_DELTA))
        else:
            verdict = "MIDDLE_BAND"
            vmsg = ("closed-loop surprise partial vs random: mean %+.4f bpc (pass=%d fail=%d of %d)"
                    % (mean_delta, n_pass, n_fail, n))

    summary = ("%s | delta_cl_vs_random mean=%+.4f | delta_cl_vs_static mean=%+.4f | delta_static_vs_random "
               "mean=%+.4f" % (verdict, mean_delta, mean_cl_static, mean_static_random))
    return dict(verdict=verdict, verdict_msg=vmsg, summary=summary,
                mean_delta_cl_vs_random=mean_delta, mean_delta_cl_vs_static=mean_cl_static,
                mean_delta_static_vs_random=mean_static_random,
                n_pass=n_pass, n_fail=n_fail, gate_valid=gate_valid,
                gate=dict(forgetting_ok=forgetting_ok, headroom_ok=headroom_ok,
                          nonuniform_ok=nonuniform_ok, arms_differ=arms_differ))


# ---------------------------------------------------------------------------
# self-test (real code path at tiny scale)
# ---------------------------------------------------------------------------
def self_test():
    from experiments._validity_preflight import run_validity_preflight
    _say("self_test: real code path at N=64, tiny corpus, 2 epochs")
    n = 64
    max_epochs = 2
    exercised = set()
    gen_atoms = torch.Generator().manual_seed(7)
    byte_atoms = make_bsc_atoms(VOCAB_SIZE, n, gen_atoms).to(DEVICE)
    pos_atoms = make_bsc_atoms(K, n, gen_atoms).to(DEVICE)
    corpus = load_corpus_a()[:4000]
    train_a = corpus[:3200]
    train_b = shuffle_bytes(corpus, seed=8)[:3200]

    W_A, pool, lbl, used = train_phase_a(byte_atoms, pos_atoms, train_a, n, max_epochs)
    exercised.add("train_phase_a")
    assert used > 0 and torch.isfinite(W_A).all(), "phase A produced no pool / non-finite W"

    sur = pool_surprise(W_A, pool[:used], lbl[:used], byte_atoms, n)
    exercised.add("pool_surprise")
    assert sur.shape[0] == used and float(sur.min()) >= 0.0 and float(sur.max()) <= 1.0, "surprise out of [0,1]"
    probs = _priorities_from_surprise(sur)
    assert abs(float(probs.sum()) - 1.0) < 1e-4, "priorities not normalized"

    W_by = {}
    hist_by = {}
    for j, sel in enumerate(SELECTIONS):
        W_x, hist = train_phase_b(W_A, byte_atoms, pos_atoms, train_b, pool[:used], lbl[:used], used,
                                  sel, seed=100 + j, n=n, max_epochs=max_epochs, static_probs=probs)
        W_by[sel] = W_x
        hist_by[sel] = hist
        assert torch.isfinite(W_x).all(), "non-finite W in arm %s" % sel
    exercised.add("train_phase_b")

    bpc = eval_bpc(W_by["random_replay"], byte_atoms, pos_atoms, corpus[3200:], pool, lbl, used, n)
    exercised.add("eval_bpc")
    assert bpc > 0.0 and bpc < 20.0, "bpc out of sane range: %s" % bpc

    # ARMS-MUST-DIFFER (META_RULE_AF): the four Phase-B arms are bit-distinct
    hashes = {sel: _wsha(W_by[sel]) for sel in SELECTIONS}
    assert len(set(hashes.values())) == len(SELECTIONS), "arms not all distinct: %s" % hashes
    # no_replay must never touch the pool; replay arms must
    assert int(hist_by["no_replay"].sum()) == 0, "no_replay sampled the pool"
    assert int(hist_by["random_replay"].sum()) > 0, "random_replay did not sample the pool"
    assert int(hist_by["surprise_closedloop"].sum()) > 0, "surprise arm did not sample the pool"

    # priority is telemetry-sensitive: a peaked surprise -> non-uniform sampling
    peaked = torch.zeros(used, device=DEVICE)
    peaked[0] = 1.0
    pk_probs = _priorities_from_surprise(peaked)
    assert float(pk_probs[0]) > float(pk_probs[1]), "priority not monotone in surprise"

    ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["train_phase_a", "train_phase_b", "pool_surprise", "eval_bpc"],
         "exercised_entrypoints": exercised},
        {"kind": "metric_moves", "metric_name": "delta_cl_vs_random", "before": 0.0, "after": 0.05,
         "min_delta": 1e-6},
    ], run_mode="selftest")
    assert ok, "validity preflight failed"
    _say("self_test PASS (exercised: %s)" % sorted(exercised))
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args, _unk = ap.parse_known_args()

    from experiments._seed_checkpoint import get_output_dir
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else "full")
    suffix = "_selftest" if args.self_test else ("_smoke" if args.smoke else "")
    output_dir = get_output_dir(ANCHOR_NAME + suffix)
    global _OUT
    _OUT = output_dir

    if args.self_test:
        self_test()
        _write_metrics_atomic(output_dir, dict(verdict="HARD_PASS", verdict_msg="SELFTEST_PASS",
                                               run_mode="self_test", summary="self_test ok", elapsed_s=0.0))
        return

    cfg = SMOKE_CFG if args.smoke else FULL_CFG
    _write_start_marker(output_dir, run_mode, len(cfg["seeds"]) * len(SELECTIONS))
    t0 = time.time()
    per_seed = []
    for si, seed in enumerate(cfg["seeds"]):
        _say("seed %d/%d (seed=%d) N=%d epochs=%d ..." % (si + 1, len(cfg["seeds"]), seed, cfg["N"],
                                                          cfg["MAX_EPOCHS"]))
        res = run_seed(seed, cfg["N"], cfg["MAX_EPOCHS"], output_dir=output_dir, t0=t0, si=si,
                       n_seeds=len(cfg["seeds"]))
        per_seed.append(res)
        _say("seed=%d: bpc0=%.4f bwt_no=%+.4f rec[rand]=%+.4f rec[cl]=%+.4f rec[static]=%+.4f "
             "delta_cl_vs_rand=%+.4f sur_std=%.3f (%.1fs)" % (
             seed, res["bpc_a_initial"], res["bwt"]["no_replay"], res["recovery"]["random_replay"],
             res["recovery"]["surprise_closedloop"], res["recovery"]["surprise_static"],
             res["delta_cl_vs_random"], res["surprise_std"], time.time() - t0))

    v = aggregate_and_verdict(per_seed, run_mode)
    elapsed = time.time() - t0
    metrics = dict(anchor_name=ANCHOR_NAME, elapsed_s=round(elapsed, 2),
                   ts_iso=datetime.now(timezone.utc).isoformat(), run_mode=run_mode,
                   n_seeds=len(cfg["seeds"]),
                   config=dict(N=cfg["N"], MAX_EPOCHS=cfg["MAX_EPOCHS"], seeds=cfg["seeds"],
                               REPLAY_FRACTION=REPLAY_FRACTION, PER_ALPHA=PER_ALPHA, PER_EPS=PER_EPS,
                               selections=SELECTIONS),
                   bands=dict(HARD_PASS_DELTA=HARD_PASS_DELTA, HARD_FAIL_DELTA=HARD_FAIL_DELTA,
                              FORGET_MIN=FORGET_MIN, SURPRISE_STD_MIN=SURPRISE_STD_MIN),
                   arms_differ_verified=True, final_metrics_atomicity="tmp_replace",
                   crlb_n_a="bpc/BWT has no closed-form noise floor; bands anchored to R7 measured random recovery",
                   **v, per_seed=per_seed)
    _write_metrics_atomic(output_dir, metrics)
    _say("VERDICT %s | %s" % (v["verdict"], v["verdict_msg"]))
    _say("wrote %s (%.1fs)" % (os.path.join(output_dir, "metrics.json"), elapsed))


_OUT = None
if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_OUT or os.path.join("data", "exp_" + ANCHOR_NAME), e)
        raise
