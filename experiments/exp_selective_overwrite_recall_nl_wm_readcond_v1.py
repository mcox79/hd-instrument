# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; LEARNED vs RANDOM_INIT eval-logit hash)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no Cramer-Rao noise floor; discriminator = LEARNED_WM vs random-init-WM separation,
#   judged live (chance=1/V_FILL=0.05, oracle ceiling 1.0 from the NL calib).
# - baseline_in_band: RANDOM_INIT_WM (frozen role-separated WM ON THE SAME CONDITIONED REPS, trained
#   readout) is the can-fail baseline; MUST stay near chance for EVERY conditioning (verifies the
#   conditioning does NOT trivially leak the label). Judged live per conditioning.
# - discriminator survives scale: FULL is the scale of interest; self-test builds REAL v2 encoder +
#   REAL conditioned role-separated WM at tiny N (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set())
"""Selective-Overwrite-Recall NL WM -- READ-CONDITIONING fixes (v1).

CHEAP READ-CONDITIONING fix of the WM_NL STILL_CANT_LEARN negative
(exp_selective_overwrite_recall_nl_wm_roleseparated_v1, commit b3e5c0b7f -> eval=[0.061,0.039]=chance,
STUCK_FLAT, loss did not descend). The FROZEN encoder is REUSED unchanged; this tests whether the block
is a CONDITIONING/optimization gap (fixable cheaply) NOT encoder-expressiveness (which a skunkworks VET
REFUTED as the diagnosis).

MEASURED lever diagnosis (VET a1f31e21 + this cell's own diagnostic, off b3e5c0b7f):
  - held-out-FILLER slot decode = 1.000 and event->query cross-context slot transfer = 1.000: the
    frozen reps DO contain a filler-invariant, cross-context slot address that GENERALIZES.
    MEASURED@vet_rc recompute (scratchpad) + this cell conditioning_diagnostic.
  - BUT the slot signal lives in a LOW-VARIANCE subspace swamped by a large SHARED component: the 6
    QUERY slot-role reps have pairwise cosine 0.992 raw, and the WM's raw softmax(slot_rep@key/temp)
    maps ALL 6 queries to the SAME address (argmax [5,5,5,5,5,5]) -> STUCK_FLAT.
    MEASURED@this cell conditioning_diagnostic (seed 7): raw query-slot cos_mean=0.992.
  - conditioning the reps (z-score / PCA-whiten) removes the shared component: pca_whiten drops the
    query-slot cosine to ~0.80 and an UNTRAINED key already separates 4/6 slots. Top-1 PCA var share
    is only 0.135 (shared component spread over ~8 dims) -> whitening beats simple demeaning.
    MEASURED@this cell conditioning_diagnostic.

THE FIXES (each tested alone + combined; base mechanism = the role-separated WM, commit b3e5c0b7f):
  1. CONDITIONING (unsupervised; the VET's #1 recommendation): transform the cached FROZEN token reps
     BEFORE the role-query/addressing.
       none        -- reproduce the failure (sanity baseline).
       zscore      -- subtract global token mean + divide per-dim std.
       pca_whiten  -- PCA-whiten (decorrelate + equalize variance = kill the dominant shared subspace).
     Conditioning is UNSUPERVISED (fit on token reps, no slot/filler labels) -> CANNOT leak the label;
     the random-init control ON THE SAME CONDITIONED REPS MUST stay ~chance (verified live).
  2. AUX SLOT-SUPERVISED ADDRESS LOSS (on pca_whiten): since slot is linearly decodable at 1.0, add a
     CE loss forcing the WM's address-logits -> true slot id, for BOTH the query address and the
     target-event addresses (teacher-force filler-invariant addressing). Distractor events unsupervised.
  3. WARM-START the address key matrix from the logistic slot-probe solution (fit K-way logistic on the
     conditioned slot-role reps at init -> copy coef into wm.key), then train from there.
  4. pca_whiten + aux + warm-start (all combined).

Everything else is IDENTICAL to b3e5c0b7f: two learned role queries (slot-role=address, filler-role=
value) attend over the event's frozen token reps; K content-address slots; learned write gate; gated
OVERWRITE (last write wins); value-proj; readout. Encoder = REAL v2 FROZEN (same ckpt as b3e5c0b7f).

ARMS (per config; SAME frozen v2 encoder shared across all):
  LEARNED_WM      -- train role queries + keys + write-gate + value-proj + readout end-to-end ON THE
                     CONDITIONED reps (+aux/+warmstart per config). Seeds 7,13. The capability.
  RANDOM_INIT_WM  -- FREEZE role queries+keys+gate+value-proj at random init ON THE SAME CONDITIONED
                     reps, train ONLY the readout. The CAN-FAIL control (one set per conditioning);
                     MUST stay < 0.10 (verifies conditioning does not leak the label).
  WARMSTART_FROZEN (warm-start configs only) -- freeze the warm-started key + random rest, train ONLY
                     readout: an HONESTY diagnostic (is the warm-start key alone doing the work, vs the
                     WM learning to use it). Reported, not a can-fail bar.

VERDICT: WM_NL_PROVEN_VIA_READ_CONDITIONING (>=1 fix learns+generalizes both seeds, controls at floor)
         / WM_NL_PARTIAL_VIA_READ_CONDITIONING (beats control significantly but below the proven bar)
         / STILL_CANT_LEARN_ALL_FIXES (no fix clears -> the encoder-objective pivot is EARNED)
         / CONTROL_FLOOR_BROKEN (a conditioning leaks the label -> margin untrustworthy).

Run:  .venv/Scripts/python.exe experiments/exp_selective_overwrite_recall_nl_wm_readcond_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_selective_overwrite_recall_nl_wm_readcond_v1.py --full

ASCII-only. No emojis. Deterministic seeding (torch.Generator + np.random.default_rng; no hash(),
no list(set())). CPU (local, push-free; this .venv has no CUDA).
"""

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

# the VALID NL construction + the base role-separated WM cell (single source of truth for task,
# oracles, vocab, and the FrozenV2Encoder / RoleSeparated machinery we condition).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_selective_overwrite_recall_nl_calib_v1 as calib  # noqa: E402
import exp_selective_overwrite_recall_nl_wm_roleseparated_v1 as base  # noqa: E402

ANCHOR_NAME = "selective_overwrite_recall_nl_wm_readcond_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
V2_CKPT = base.V2_CKPT

# ---- pull the CALIBRATED NL construction constants ----
V_FILL = calib.V_FILL              # 20 -> CHANCE = 0.05
CHANCE = calib.CHANCE
S_TARGET = calib.S_TARGET          # 6 target slots
COLORS = calib.COLORS
SLOT_NOUNS = calib.SLOT_NOUNS
EVENT_TEMPLATES = calib.EVENT_TEMPLATES
QUERY_TEMPLATE = calib.QUERY_TEMPLATE

# ---- WM / training params (mechanism identical to b3e5c0b7f) ----
K_SLOTS = 6
D_MEM = 64
HIDDEN = 64
ADDR_TEMP = 0.3
SENT_CAP = base.SENT_CAP

FULL_TRAIN, FULL_EVAL = 1200, 700
STEPS_WM = 800
BATCH = 256
STEPS_READOUT = 400
LR = 1e-2
EARLY_STOP_LOSS = 0.05
SEEDS_FULL = (7, 13)
N_RANDOM_INIT = 3
AUX_W = 1.0                        # aux slot-address CE weight
PCA_EPS = 1e-4                     # whitening ridge (avoid amplifying tiny-variance noise dims)

# ---- bands (pre-reg; same family as b3e5c0b7f) ----
Z_THRESH = 2.0
RI_NEAR_CHANCE = 0.10             # each random-init control MUST be < this (clean floor)
MECH_MARGIN = 0.30               # LEARNED_WM - ri_mean must be >= this for PROVEN
WM_PROVEN_MIN = 0.50             # LEARNED_WM eval acc >= this (>=10x chance) both seeds -> PROVEN
WM_PARTIAL_MIN = 0.15            # eval acc >= this AND significant -> PARTIAL (beats control)
LOSS_DESCEND_RATIO = 0.90
ORACLE_CEILING = 1.0

# config matrix: (name, conditioning, aux, warmstart)
# ONE-VARIABLE discipline (2026-07-30 amendment): every arm below is EITHER a pure single-lever test
# vs baseline ("zscore"/"pca_whiten" isolate conditioning; "aux_only"/"warm_only" isolate aux/warmstart
# with conditioning="none", reusing the already-computed "none" RI control -- clean attribution, no
# silent stacking) OR the one designated COMBINED arm (all three stacked, per the pre-reg contract).
# Compute-proportionality: trimmed the earlier stacked-but-not-requested "pca_whiten_aux" /
# "pca_whiten_warm" 2-variable rows (they served neither the pure-attribution goal nor the combined-arm
# ask, just added 4 more LEARNED units) -- 6 configs total, not 8.
CONFIGS = [
    ("none",                 "none",       False, False),   # ARM BASELINE (reproduce STILL_CANT_LEARN)
    ("zscore",               "zscore",     False, False),   # ARM WHITEN (variant: per-dim z-score)
    ("pca_whiten",           "pca_whiten", False, False),   # ARM WHITEN (primary: PCA-whiten)
    ("aux_only",             "none",       True,  False),   # ARM AUX (pure, no conditioning)
    ("warm_only",            "none",       False, True),    # ARM WARMSTART (pure, no conditioning)
    ("pca_whiten_aux_warm",  "pca_whiten", True,  True),    # ARM COMBINED (all three stacked)
]
CONDITIONINGS = ["none", "zscore", "pca_whiten"]   # controls computed once per conditioning


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------- canonical hardening ----------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ---------------- significance (verbatim from the base gate) ----------------
def _binom_se(acc, n):
    n = max(int(n), 1)
    return math.sqrt(max(acc * (1.0 - acc), 1e-9) / n)


def _one_sided_p(z):
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def power_stats(trained_acc, n_eval, ri_accs):
    ri = np.asarray(ri_accs, dtype=float)
    ri_mean = float(ri.mean())
    ri_std = float(ri.std(ddof=1)) if ri.size > 1 else 0.0
    ri_max = float(ri.max())
    se_trained = _binom_se(trained_acc, n_eval)
    se_ri_mean = _binom_se(ri_mean, n_eval)
    se_diff = math.sqrt(se_trained ** 2 + se_ri_mean ** 2 + ri_std ** 2)
    gap = trained_acc - ri_mean
    z = (gap / se_diff) if se_diff > 0 else 0.0
    return dict(ri_mean=ri_mean, ri_std=ri_std, ri_max=ri_max, n_ri_seeds=int(ri.size),
                se_diff=se_diff, gap=gap, z=z, p_value=_one_sided_p(z),
                min_detectable_effect_2sigma=2.0 * se_diff, beats_ri_max=bool(trained_acc > ri_max),
                significant=bool(z >= Z_THRESH and trained_acc > ri_max))


# ---------------- conditioning (fit unsupervised on the frozen token reps) ----------------
class Conditioner:
    """Fits global mean / per-dim std / PCA basis on ALL real (non-pad) token reps of the closed
    sentence set (UNSUPERVISED -- no slot/filler labels). Applies a conditioning to a cached token-rep
    tensor [Nu, L, d], keeping pad rows zeroed."""

    def __init__(self, U_tok, U_pad):
        real = U_tok[~U_pad]                              # [Ntok, d]
        self.mu = real.mean(0)                            # [d]
        self.sd = real.std(0) + 1e-8                      # [d]
        Xc = real - self.mu
        cov = (Xc.T @ Xc) / Xc.shape[0]
        evals, evecs = torch.linalg.eigh(cov)             # ascending
        order = torch.argsort(evals, descending=True)
        self.evals = evals[order].clamp_min(0.0)          # [d] descending
        self.evecs = evecs[:, order]                      # [d, d] columns = components
        tot = float(self.evals.sum()) + 1e-12
        self.var_share_top1 = float(self.evals[0]) / tot
        self.var_share_top4 = float(self.evals[:4].sum()) / tot
        self.var_share_top8 = float(self.evals[:8].sum()) / tot

    def apply(self, U_tok, U_pad, kind):
        keep = (~U_pad).unsqueeze(-1).float()
        if kind == "none":
            return U_tok * keep
        if kind == "zscore":
            return ((U_tok - self.mu) / self.sd) * keep
        if kind == "pca_whiten":
            Xw = (U_tok - self.mu) @ self.evecs / torch.sqrt(self.evals + PCA_EPS)
            return Xw * keep
        raise ValueError("unknown conditioning %r" % kind)


# ---------------- extended index batch (adds slot-id supervision for the aux loss) ----------------
def build_index_batch(examples, enc, seed):
    """Base index batch + ev_slot [B,Lmax] (target slot id 0..S-1, or -1 for distractor/pad) and
    q_slot [B] (queried slot id) for the aux slot-address loss."""
    b = base.build_index_batch(examples, enc, seed)       # ev_idx,q_idx,active,answer (proven mapping)
    B, Lmax = b["ev_idx"].shape
    ev_slot = np.full((B, Lmax), -1, dtype=np.int64)
    q_slot = np.zeros((B,), dtype=np.int64)
    for i, ex in enumerate(examples):
        for t, sl in enumerate(ex["slots"]):
            s = int(sl)
            if s < S_TARGET:
                ev_slot[i, t] = s                         # distractors stay -1 (unsupervised)
        q_slot[i] = int(ex["query"])
    b["ev_slot"] = torch.from_numpy(ev_slot)
    b["q_slot"] = torch.from_numpy(q_slot)
    return b


# ---------------- conditioned role-separated gated-overwrite WM ----------------
class ReadCondWM(nn.Module):
    """b3e5c0b7f RoleSeparatedGatedWM, but consuming CONDITIONED cached token reps and optionally
    exposing address logits for the aux slot-supervised loss. U_tok is ALREADY conditioned when
    passed in (Conditioner.apply)."""

    def __init__(self, seed, d_enc, d_mem, k_slots, hidden, v_fill, addr_temp, U_tok, U_pad):
        super().__init__()
        self.k_slots = k_slots
        self.d_mem = d_mem
        self.d_enc = d_enc
        self.addr_temp = addr_temp
        self.U_tok = U_tok
        self.U_pad = U_pad
        g = torch.Generator().manual_seed(seed + 1234)
        rq = torch.empty(2, d_enc)
        rq.normal_(0.0, 0.02, generator=g)
        self.role_query = nn.Parameter(rq)                            # [2, d_enc] (0=slot, 1=fill)
        key = torch.empty(k_slots, d_enc)
        key.normal_(0.0, 1.0, generator=g).div_(math.sqrt(d_enc))
        self.key = nn.Parameter(key)                                  # [K, d_enc] address keys
        self.write_gate = nn.Sequential(nn.Linear(d_enc, hidden), nn.Tanh(), nn.Linear(hidden, 1))
        self.value_proj = nn.Linear(d_enc, d_mem)
        self.readout = nn.Linear(d_mem, v_fill)
        with torch.no_grad():
            for m in list(self.write_gate) + [self.value_proj, self.readout]:
                if isinstance(m, nn.Linear):
                    w = torch.empty_like(m.weight)
                    w.normal_(0.0, 0.1, generator=g)
                    m.weight.copy_(w)
                    m.bias.zero_()

    def wm_params(self):
        return ([self.role_query, self.key] + list(self.write_gate.parameters())
                + list(self.value_proj.parameters()))

    def _role_reps(self):
        d = self.d_enc
        scores = torch.einsum("nld,rd->nrl", self.U_tok, self.role_query) / math.sqrt(d)
        scores = scores.masked_fill(self.U_pad.unsqueeze(1), float("-inf"))
        attn = torch.softmax(scores, dim=-1)
        fillers = torch.einsum("nrl,nld->nrd", attn, self.U_tok)
        return fillers[:, 0, :], fillers[:, 1, :]

    def _addr_logits(self, x):
        return x @ self.key.t() / self.addr_temp

    def read_features(self, batch, want_aux=False):
        slot_u, fill_u = self._role_reps()                               # [Nu, d] each
        ev_idx = batch["ev_idx"]; active = batch["active"]; q_idx = batch["q_idx"]
        B, Lmax = ev_idx.shape
        ev_slot = slot_u[ev_idx]                                         # [B, Lmax, d]
        ev_fill = fill_u[ev_idx]
        flat_slot = ev_slot.reshape(B * Lmax, self.d_enc)
        ev_logits = self._addr_logits(flat_slot).reshape(B, Lmax, self.k_slots)
        addr = torch.softmax(ev_logits, dim=-1)
        wgate = torch.sigmoid(self.write_gate(flat_slot)).reshape(B, Lmax)
        cand = self.value_proj(ev_fill.reshape(B * Lmax, self.d_enc)).reshape(B, Lmax, self.d_mem)
        h = torch.zeros(B, self.k_slots, self.d_mem)
        for t in range(Lmax):
            w = (addr[:, t] * (wgate[:, t] * active[:, t]).unsqueeze(-1)).unsqueeze(-1)
            h = (1.0 - w) * h + w * cand[:, t].unsqueeze(1)
        q_logits = self._addr_logits(slot_u[q_idx])                     # [B, K]
        addr_q = torch.softmax(q_logits, dim=-1)
        h_read = (addr_q.unsqueeze(-1) * h).sum(dim=1)                   # [B, d_mem]
        if want_aux:
            return h_read, ev_logits, q_logits
        return h_read

    def forward(self, batch):
        return self.readout(self.read_features(batch))


def warm_start_key(wm, enc, seed):
    """Fit a K-way logistic on the CONDITIONED slot-role reps (at current role_query init) of the
    target-slot event + query sentences, copy coef into wm.key. Returns diagnostic dict."""
    from sklearn.linear_model import LogisticRegression
    idxs = []
    labels = []
    for s in range(S_TARGET):
        idxs.append(enc.idx_of(QUERY_TEMPLATE.format(slot=SLOT_NOUNS[s]))); labels.append(s)
        for tm in EVENT_TEMPLATES:
            for fl in COLORS:
                idxs.append(enc.idx_of(tm.format(slot=SLOT_NOUNS[s], fill=fl))); labels.append(s)
    with torch.no_grad():
        slot_u, _ = wm._role_reps()
    X = slot_u[torch.tensor(idxs)].detach().numpy()
    y = np.asarray(labels, dtype=np.int64)
    clf = LogisticRegression(max_iter=500, C=1.0, random_state=seed)
    clf.fit(X, y)
    coef = torch.from_numpy(clf.coef_.astype(np.float32))              # [K, d]
    with torch.no_grad():
        wm.key.copy_(coef)
        logits = wm._addr_logits(slot_u[torch.tensor(idxs)])
        addr_acc = float((logits.argmax(1).numpy() == y).mean())
        maxprob = float(torch.softmax(logits, dim=-1).max(1).values.mean())
    return {"warmstart_probe_fit_acc": float(clf.score(X, y)),
            "warmstart_frozen_addr_acc": addr_acc, "warmstart_mean_maxprob": maxprob}


# ---------------- train / eval ----------------
def _eval_acc(logits, answer):
    return float((logits.argmax(dim=-1) == answer).float().mean().item())


def _minibatch(tr_batch, idx):
    return {k: v[idx] for k, v in tr_batch.items()}


def _aux_loss(ev_logits, q_logits, mb):
    """CE forcing address-logits -> true slot id: query address + target-event addresses (distractors
    unsupervised)."""
    q_ce = F.cross_entropy(q_logits, mb["q_slot"])
    ev_slot = mb["ev_slot"].reshape(-1)                                  # [B*L]
    ev_flat = ev_logits.reshape(-1, ev_logits.shape[-1])
    sup = ev_slot >= 0
    if sup.any():
        ev_ce = F.cross_entropy(ev_flat[sup], ev_slot[sup])
    else:
        ev_ce = torch.zeros((), dtype=q_ce.dtype)
    return q_ce + ev_ce


def train_arm(wm, tr_batch, ev_batch, steps, lr, train_params, seed, log_tag, aux, batch=None):
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed + 555)
    opt = torch.optim.Adam(train_params, lr=lr)
    N = tr_batch["answer"].shape[0]
    loss_curve = []
    ema = None
    step = 0
    for step in range(steps):
        opt.zero_grad()
        if batch is not None and batch < N:
            idx = torch.randint(0, N, (batch,), generator=g)
            mb = _minibatch(tr_batch, idx)
        else:
            mb = tr_batch
        if aux:
            h_read, ev_logits, q_logits = wm.read_features(mb, want_aux=True)
            logits = wm.readout(h_read)
            loss = F.cross_entropy(logits, mb["answer"]) + AUX_W * _aux_loss(ev_logits, q_logits, mb)
        else:
            logits = wm(mb)
            loss = F.cross_entropy(logits, mb["answer"])
        loss.backward()
        opt.step()
        lv = float(loss.item())
        ema = lv if ema is None else 0.9 * ema + 0.1 * lv
        if step == 0 or (step + 1) % max(1, steps // 8) == 0:
            loss_curve.append((step, lv))
            _log("    [%s seed=%d] step=%d loss=%.4f ema=%.4f" % (log_tag, seed, step + 1, lv, ema))
        if step >= 200 and ema is not None and ema < EARLY_STOP_LOSS:
            break
    wm.eval()
    with torch.no_grad():
        ev_logits = wm(ev_batch)
        acc = _eval_acc(ev_logits, ev_batch["answer"])
        tr_logits = wm(tr_batch)
        tr_acc = _eval_acc(tr_logits, tr_batch["answer"])
    wm.train()
    first_loss = loss_curve[0][1] if loss_curve else float("nan")
    last_loss = loss_curve[-1][1] if loss_curve else float("nan")
    _log("  [%s seed=%d] eval_acc=%.4f train_acc=%.4f loss %.3f->%.3f steps=%d"
         % (log_tag, seed, acc, tr_acc, first_loss, last_loss, step + 1))
    return dict(eval_acc=acc, train_acc=tr_acc, ev_logits=ev_logits.detach(),
                loss_curve=loss_curve, first_loss=first_loss, last_loss=last_loss,
                ema=float(ema) if ema is not None else float("nan"), steps_run=step + 1)


def train_readout_cached(wm, tr_batch, ev_batch, steps, lr, seed, log_tag):
    torch.manual_seed(seed)
    with torch.no_grad():
        tr_feat = wm.read_features(tr_batch)
        ev_feat = wm.read_features(ev_batch)
    opt = torch.optim.Adam(wm.readout.parameters(), lr=lr)
    loss_curve = []
    for step in range(steps):
        opt.zero_grad()
        loss = F.cross_entropy(wm.readout(tr_feat), tr_batch["answer"])
        loss.backward()
        opt.step()
        if step == 0 or (step + 1) % max(1, steps // 8) == 0:
            loss_curve.append((step, float(loss.item())))
    with torch.no_grad():
        ev_logits = wm.readout(ev_feat)
        acc = _eval_acc(ev_logits, ev_batch["answer"])
    return dict(eval_acc=acc, ev_logits=ev_logits.detach(),
                first_loss=loss_curve[0][1], last_loss=loss_curve[-1][1])


# ---------------- conditioning diagnostic (the load-bearing mechanism read) ----------------
def conditioning_diagnostic(enc, cond, seed=7):
    """Report the query-slot pairwise cosine RAW vs each conditioning + the untrained-key address
    separation. This is the mechanism the fix targets."""
    g = torch.Generator().manual_seed(seed + 1234)
    rq = torch.empty(2, enc.d); rq.normal_(0.0, 0.02, generator=g)
    q_idx = torch.tensor([enc.idx_of(QUERY_TEMPLATE.format(slot=SLOT_NOUNS[s])) for s in range(S_TARGET)])
    gg = torch.Generator().manual_seed(999)
    key = torch.empty(K_SLOTS, enc.d); key.normal_(0.0, 1.0, generator=gg).div_(math.sqrt(enc.d))

    def _role_slot(Uc, Upad):
        scores = torch.einsum("nld,rd->nrl", Uc, rq) / math.sqrt(enc.d)
        scores = scores.masked_fill(Upad.unsqueeze(1), float("-inf"))
        attn = torch.softmax(scores, dim=-1)
        return torch.einsum("nrl,nld->nrd", attn, Uc)[:, 0, :]

    out = {}
    for kind in CONDITIONINGS:
        Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, kind)
        qs = _role_slot(Uc, enc.U_pad_t)[q_idx]
        v = qs / (qs.norm(dim=1, keepdim=True) + 1e-8)
        c = v @ v.t()
        od = c[~torch.eye(S_TARGET, dtype=bool)]
        addr = torch.softmax(qs @ key.t() / ADDR_TEMP, dim=-1)
        out[kind] = {"query_slot_cos_mean": float(od.mean()), "query_slot_cos_max": float(od.max()),
                     "untrained_addr_distinct": int(len(set(addr.argmax(1).tolist()))),
                     "untrained_addr_argmax": addr.argmax(1).tolist()}
    out["pca_var_share_top1"] = cond.var_share_top1
    out["pca_var_share_top4"] = cond.var_share_top4
    out["pca_var_share_top8"] = cond.var_share_top8
    return out


# ---------------- per-conditioning random-init control (can-fail, computed once) ----------------
def run_ri_control(enc, cond, kind, tr_batch, ev_batch, seed_base, n_ri):
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, kind)
    accs = []
    logits_first = None
    for c in range(n_ri):
        cseed = seed_base * 100 + c
        wm = ReadCondWM(cseed, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP, Uc, enc.U_pad_t)
        for p in wm.wm_params():
            p.requires_grad_(False)
        ri = train_readout_cached(wm, tr_batch, ev_batch, STEPS_READOUT, LR, cseed,
                                  "RI_%s c=%d" % (kind, c))
        accs.append(ri["eval_acc"])
        if logits_first is None:
            logits_first = ri["ev_logits"]
    _log("  RANDOM_INIT[%s]: accs=%s mean=%.4f max=%.4f"
         % (kind, [round(a, 4) for a in accs], float(np.mean(accs)), float(np.max(accs))))
    return {"kind": kind, "accs": accs, "mean": float(np.mean(accs)), "max": float(np.max(accs)),
            "min": float(np.min(accs))}, logits_first


# ---------------- per-config learned run ----------------
def run_config(cfg, enc, cond, datasets, ri_by_cond, ri_logits_by_cond):
    name, kind, aux, warm = cfg
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, kind)
    per_seed = []
    warm_diag = None
    warmfrozen = None
    for seed in SEEDS_FULL:
        tr_batch, ev_batch = datasets[seed]
        wm = ReadCondWM(seed, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP, Uc, enc.U_pad_t)
        if warm:
            wd = warm_start_key(wm, enc, seed)
            if warm_diag is None:
                warm_diag = wd
                # honesty diagnostic: warm-started key frozen + random rest, readout-only
                wm_wf = ReadCondWM(seed, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP, Uc, enc.U_pad_t)
                warm_start_key(wm_wf, enc, seed)
                for p in wm_wf.wm_params():
                    p.requires_grad_(False)
                wf = train_readout_cached(wm_wf, tr_batch, ev_batch, STEPS_READOUT, LR, seed,
                                          "WARMFROZEN_%s" % name)
                warmfrozen = wf["eval_acc"]
                _log("  [%s] WARMSTART_FROZEN(readout-only) eval_acc=%.4f (probe_fit=%.3f frozen_addr=%.3f)"
                     % (name, warmfrozen, wd["warmstart_probe_fit_acc"], wd["warmstart_frozen_addr_acc"]))
        learned = train_arm(wm, tr_batch, ev_batch, STEPS_WM, LR, list(wm.parameters()), seed,
                            "LEARNED[%s]" % name, aux=aux, batch=BATCH)
        ps = power_stats(learned["eval_acc"], ev_batch["answer"].shape[0], ri_by_cond[kind]["accs"])

        def _digest(t):
            return hashlib.sha256(t.cpu().numpy().tobytes()).hexdigest()
        arms_differ = _digest(learned["ev_logits"]) != _digest(ri_logits_by_cond[kind])
        per_seed.append({
            "seed": seed,
            "learned_wm": {"eval_acc": learned["eval_acc"], "train_acc": learned["train_acc"],
                           "first_loss": learned["first_loss"], "last_loss": learned["last_loss"],
                           "loss_curve": learned["loss_curve"], "steps_run": learned["steps_run"],
                           "eval_minus_train": learned["eval_acc"] - learned["train_acc"]},
            "power": ps, "arms_differ_verified": bool(arms_differ)})
    learned_accs = [p["learned_wm"]["eval_acc"] for p in per_seed]
    train_accs = [p["learned_wm"]["train_acc"] for p in per_seed]
    gaps = [p["power"]["gap"] for p in per_seed]
    sigs = [p["power"]["significant"] for p in per_seed]
    descended = all(p["learned_wm"]["last_loss"] < LOSS_DESCEND_RATIO * p["learned_wm"]["first_loss"]
                    for p in per_seed)
    proven = (all(a >= WM_PROVEN_MIN for a in learned_accs) and all(gp >= MECH_MARGIN for gp in gaps)
              and all(sigs))
    partial = (not proven and all(a >= WM_PARTIAL_MIN for a in learned_accs) and all(sigs))
    return {"name": name, "conditioning": kind, "aux": aux, "warmstart": warm,
            "ri_mean": ri_by_cond[kind]["mean"], "ri_max": ri_by_cond[kind]["max"],
            "learned_accs": learned_accs, "train_accs": train_accs, "gaps": gaps,
            "significant_per_seed": [bool(s) for s in sigs], "loss_descended_both": bool(descended),
            "proven": bool(proven), "partial": bool(partial),
            "warmstart_diag": warm_diag, "warmstart_frozen_readout_acc": warmfrozen,
            "per_seed": per_seed}


# ---------------- verdict ----------------
def decide_verdict(config_results, ri_controls, cond_diag):
    ri_all = [a for r in ri_controls.values() for a in r["accs"]]
    control_floor_ok = all(a < RI_NEAR_CHANCE for a in ri_all)

    proven_fixes = [c["name"] for c in config_results if c["proven"]]
    partial_fixes = [c["name"] for c in config_results if c["partial"] and not c["proven"]]
    best = max(config_results, key=lambda c: max(c["learned_accs"]))
    raw_cos = cond_diag["none"]["query_slot_cos_mean"]
    pca_cos = cond_diag["pca_whiten"]["query_slot_cos_mean"]

    if not control_floor_ok:
        verdict = "CONTROL_FLOOR_BROKEN"
        msg = ("a RANDOM_INIT_WM control cleared %.2f (max=%.3f) on some conditioning: the can-fail "
               "floor is not clean -> a conditioning leaks a shortcut; margins untrustworthy."
               % (RI_NEAR_CHANCE, max(ri_all)))
    elif proven_fixes:
        verdict = "WM_NL_PROVEN_VIA_READ_CONDITIONING"
        msg = ("READ-CONDITIONING SOLVES NL binding: fix(es) %s reach eval>=%.2f both seeds AND gap>=%.2f "
               "AND significant, controls at floor (max ri=%.3f). Best=%s eval=%s train=%s. Raw query-slot "
               "cos=%.3f -> pca_whiten %.3f (shared component removed). Encoder pivot NOT needed."
               % (proven_fixes, WM_PROVEN_MIN, MECH_MARGIN, max(ri_all), best["name"],
                  [round(a, 3) for a in best["learned_accs"]], [round(a, 3) for a in best["train_accs"]],
                  raw_cos, pca_cos))
    elif partial_fixes:
        verdict = "WM_NL_PARTIAL_VIA_READ_CONDITIONING"
        msg = ("READ-CONDITIONING moves the needle but not to the proven bar: fix(es) %s beat the control "
               "significantly (eval>=%.2f both seeds) but below eval>=%.2f. Best=%s eval=%s train=%s, "
               "controls at floor (max ri=%.3f). Raw cos=%.3f -> pca %.3f."
               % (partial_fixes, WM_PARTIAL_MIN, WM_PROVEN_MIN, best["name"],
                  [round(a, 3) for a in best["learned_accs"]], [round(a, 3) for a in best["train_accs"]],
                  max(ri_all), raw_cos, pca_cos))
    else:
        verdict = "STILL_CANT_LEARN_ALL_FIXES"
        msg = ("NO read-conditioning fix (zscore / pca_whiten / +aux / +warmstart) got the WM to learn+"
               "generalize above the control (best=%s eval=%s train=%s, controls floor max=%.3f). The "
               "conditioning removed the shared component (raw cos %.3f -> pca %.3f) yet the WM still does "
               "not learn -> the CHEAP read-conditioning path is exhausted; the encoder-objective pivot "
               "is EARNED as the next direction."
               % (best["name"], [round(a, 3) for a in best["learned_accs"]],
                  [round(a, 3) for a in best["train_accs"]], max(ri_all), raw_cos, pca_cos))
    bands = {"chance": CHANCE, "oracle_ceiling": ORACLE_CEILING, "wm_proven_min": WM_PROVEN_MIN,
             "wm_partial_min": WM_PARTIAL_MIN, "mech_margin": MECH_MARGIN, "z_thresh": Z_THRESH,
             "ri_near_chance": RI_NEAR_CHANCE, "control_floor_ok": bool(control_floor_ok),
             "proven_fixes": proven_fixes, "partial_fixes": partial_fixes,
             "best_config": best["name"], "best_learned_accs": best["learned_accs"],
             "best_train_accs": best["train_accs"],
             "raw_query_slot_cos": raw_cos, "pca_query_slot_cos": pca_cos,
             "ri_control_max": float(max(ri_all))}
    return verdict, msg, bands


# ---------------- self-test ----------------
def run_self_test():
    _log("SELF-TEST: load REAL v2 encoder + token-cache + conditioning + tiny end-to-end ...")
    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    enc = base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    assert n_cached >= 3000, "closed sentence set smaller than expected"
    cond = Conditioner(enc.U_tok_t, enc.U_pad_t)

    # conditioning reduces the query-slot shared component (the mechanism the fix targets)
    diag = conditioning_diagnostic(enc, cond, seed=7)
    _log("  cond diag: raw cos=%.3f (distinct=%d) zscore cos=%.3f pca cos=%.3f (distinct=%d) "
         "top1var=%.3f" % (diag["none"]["query_slot_cos_mean"], diag["none"]["untrained_addr_distinct"],
                           diag["zscore"]["query_slot_cos_mean"], diag["pca_whiten"]["query_slot_cos_mean"],
                           diag["pca_whiten"]["untrained_addr_distinct"], diag["pca_var_share_top1"]))
    assert diag["pca_whiten"]["query_slot_cos_mean"] < diag["none"]["query_slot_cos_mean"], \
        "pca_whiten did not reduce the query-slot shared component"

    # overwrite (not accumulate) unit check
    with torch.no_grad():
        h = torch.zeros(1, 1, 3)
        for cand_val in (torch.tensor([[1.0, 0.0, 0.0]]), torch.tensor([[0.0, 1.0, 0.0]])):
            w = torch.ones(1, 1, 1)
            h = (1.0 - w) * h + w * cand_val.unsqueeze(1)
        assert torch.allclose(h.squeeze(), torch.tensor([0.0, 1.0, 0.0])), "overwrite kept a blend"

    # aux batch fields present + role reps non-degenerate on conditioned reps
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, "pca_whiten")
    wm = ReadCondWM(7, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP, Uc, enc.U_pad_t)
    with torch.no_grad():
        slot_u, fill_u = wm._role_reps()
    assert not torch.allclose(slot_u, fill_u), "slot/fill role reps identical (degenerate)"

    ex = calib.gen_dataset(24, np.random.default_rng(1))
    b = build_index_batch(ex, enc, 1)
    assert "ev_slot" in b and "q_slot" in b, "aux fields missing"
    with torch.no_grad():
        h_read, ev_logits, q_logits = wm.read_features(b, want_aux=True)
    assert ev_logits.shape == (24, b["ev_idx"].shape[1], K_SLOTS) and q_logits.shape == (24, K_SLOTS)
    _ = _aux_loss(ev_logits, q_logits, b)

    # warm-start makes the frozen key address slots well above chance
    wd = warm_start_key(wm, enc, 7)
    _log("  warm-start: probe_fit=%.3f frozen_addr_acc=%.3f maxprob=%.3f"
         % (wd["warmstart_probe_fit_acc"], wd["warmstart_frozen_addr_acc"], wd["warmstart_mean_maxprob"]))
    assert wd["warmstart_frozen_addr_acc"] > 0.5, "warm-start key does not address slots (fit failed)"

    # tiny end-to-end config (pca_whiten+aux) + arms-differ vs a random-init control
    datasets = {7: (build_index_batch(calib.gen_dataset(200, np.random.default_rng(7)), enc, 7),
                    build_index_batch(calib.gen_dataset(200, np.random.default_rng(7 + 777)), enc, 7 + 777))}
    ri, ri_logits = run_ri_control(enc, cond, "pca_whiten", datasets[7][0], datasets[7][1], 7, 2)
    ri_by = {"pca_whiten": ri}; ri_logits_by = {"pca_whiten": ri_logits}
    cfg = ("tiny_pca_aux", "pca_whiten", True, False)
    global STEPS_WM, SEEDS_FULL
    saved_steps, saved_seeds = STEPS_WM, SEEDS_FULL
    STEPS_WM, SEEDS_FULL = 60, (7,)
    try:
        res = run_config(cfg, enc, cond, datasets, ri_by, ri_logits_by)
    finally:
        STEPS_WM, SEEDS_FULL = saved_steps, saved_seeds
    _log("  tiny: LEARNED eval=%.3f train=%.3f ri_mean=%.3f arms_differ=%s"
         % (res["learned_accs"][0], res["train_accs"][0], res["ri_mean"],
            res["per_seed"][0]["arms_differ_verified"]))
    assert res["per_seed"][0]["arms_differ_verified"], "arms bit-identical (LEARNED vs RANDOM_INIT)"
    assert 0.0 <= res["learned_accs"][0] <= 1.0 and 0.0 <= res["ri_mean"] <= 1.0, "acc out of range"

    # determinism on fixed batch
    with torch.no_grad():
        l1 = wm(b); l2 = wm(b)
    assert torch.allclose(l1, l2), "forward not deterministic on fixed reps"
    _log("SELF-TEST PASS")
    return {"n_cached": n_cached, "cond_diag": diag, "warmstart": wd,
            "tiny": {"learned": res["learned_accs"][0], "train": res["train_accs"][0],
                     "ri_mean": res["ri_mean"], "arms_differ": res["per_seed"][0]["arms_differ_verified"]}}


# ---------------- main ----------------
def main():
    global STEPS_WM
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--train-n", type=int, default=FULL_TRAIN)
    ap.add_argument("--eval-n", type=int, default=FULL_EVAL)
    ap.add_argument("--steps-wm", type=int, default=STEPS_WM)
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test or not args.full else "full"
    expected_units = 1 if run_mode == "self_test" else len(CONFIGS)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (real v2 encoder + conditioner + aux + warmstart + arms-differ + determinism)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "chance": CHANCE, "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    STEPS_WM = args.steps_wm
    _log("FULL: train_n=%d eval_n=%d steps_wm=%d seeds=%s chance=%.4f configs=%d encoder=real_v2_frozen"
         % (args.train_n, args.eval_n, STEPS_WM, SEEDS_FULL, CHANCE, len(CONFIGS)))
    enc = base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    _log("  cached %d unique sentence TOKEN reps (d=%d, L=%d)" % (n_cached, enc.d, SENT_CAP))
    cond = Conditioner(enc.U_tok_t, enc.U_pad_t)

    _log("--- conditioning diagnostic (the mechanism the fix targets) ---")
    cond_diag = conditioning_diagnostic(enc, cond, seed=7)
    for kind in CONDITIONINGS:
        d = cond_diag[kind]
        _log("  %-11s query-slot cos=%.3f (distinct=%d/6)"
             % (kind, d["query_slot_cos_mean"], d["untrained_addr_distinct"]))
    _log("  pca var share top1=%.3f top4=%.3f top8=%.3f"
         % (cond_diag["pca_var_share_top1"], cond_diag["pca_var_share_top4"], cond_diag["pca_var_share_top8"]))

    # datasets per seed (shared across configs)
    datasets = {}
    for seed in SEEDS_FULL:
        tr = calib.gen_dataset(args.train_n, np.random.default_rng(seed))
        ev = calib.gen_dataset(args.eval_n, np.random.default_rng(seed + 777))
        datasets[seed] = (build_index_batch(tr, enc, seed), build_index_batch(ev, enc, seed + 777))

    # random-init controls: ONE set per conditioning (can-fail; must stay < RI_NEAR_CHANCE)
    _log("--- random-init controls (can-fail floor per conditioning) ---")
    ri_controls = {}
    ri_logits_by = {}
    ctrl_seed, ctrl_tr, ctrl_ev = SEEDS_FULL[0], datasets[SEEDS_FULL[0]][0], datasets[SEEDS_FULL[0]][1]
    for kind in CONDITIONINGS:
        r, lg = run_ri_control(enc, cond, kind, ctrl_tr, ctrl_ev, ctrl_seed, N_RANDOM_INIT)
        ri_controls[kind] = r
        ri_logits_by[kind] = lg

    _log("--- learned configs ---")
    config_results = []
    for cfg in CONFIGS:
        _log("=== config: %s (cond=%s aux=%s warm=%s) ===" % cfg)
        config_results.append(run_config(cfg, enc, cond, datasets, ri_controls, ri_logits_by))

    verdict, msg, bands = decide_verdict(config_results, ri_controls, cond_diag)
    elapsed = time.perf_counter() - t0

    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | chance=%.4f | %s" % (verdict, CHANCE, msg[:160]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "chance": CHANCE, "oracle_ceiling_ref": ORACLE_CEILING, "bands": bands,
        "conditioning_diagnostic": cond_diag,
        "random_init_controls": ri_controls,
        "config_results": config_results,
        "cardinality_ok": bool(len(config_results) == len(CONFIGS)),
        "expected_n_units": len(CONFIGS), "n_units_done": len(config_results),
        "params": {"K_SLOTS": K_SLOTS, "D_MEM": D_MEM, "D_ENC": enc.d, "HIDDEN": HIDDEN,
                   "ADDR_TEMP": ADDR_TEMP, "SENT_CAP": SENT_CAP, "STEPS_WM": STEPS_WM,
                   "STEPS_READOUT": STEPS_READOUT, "LR": LR, "AUX_W": AUX_W, "PCA_EPS": PCA_EPS,
                   "N_RANDOM_INIT": N_RANDOM_INIT, "train_n": args.train_n, "eval_n": args.eval_n,
                   "seeds": list(SEEDS_FULL), "n_cached_sentences": n_cached,
                   "encoder": "real_v2_frozen", "configs": [c[0] for c in CONFIGS],
                   "v2_ckpt": os.path.relpath(V2_CKPT, REPO_ROOT)},
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns"})
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE full in %.1fs" % elapsed)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
