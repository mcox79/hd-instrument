"""Selective-Overwrite-Recall: LEARNED content-gated WM -- the WM PROOF (v1).

CULMINATING TEST. The calibration cell (exp_selective_overwrite_recall_calib_v1) proved the task
is RESERVOIR_FAILING_VALID: random-init frozen reservoir + all naive shortcuts land at chance
(0.05), while a FIXED-RULE gate reading the reservoir state at the queried slot's last-write hits
1.00. So the FEATURES are sufficient; the ONLY missing ingredient is LEARNED content-gated
selection of WHICH write to read. This cell builds the SIMPLEST content-gated entity memory that
can express overwrite-with-suppression (EntNet-style, Henaff 2017) and asks: can it LEARN the task?

SIMPLEST-FIRST (one variable). NO bistable-PE-threshold, NO role-query multi-head, NO addr_temp
anneal stack (that full stack collapsed earlier -- see hdlab/slot_attention_wm.py). Just:
  - learned per-slot content-address key  (route slot_id -> slot)
  - learned scalar write gate on slot_id  (write on target events, SUPPRESS distractors)
  - gated OVERWRITE update (1-w)*h + w*candidate  (last write wins; NOT accumulate/average)
  - learned value projection + readout      (decode stored filler -> class)
Those are ADD-ONs for later IF the simple version works.

ENCODER = RANDOM-INIT FROZEN Gaussian embeddings (E_slot, E_fill), identical in spirit to the
calibration's reservoir input encoding. The point of THIS test is the WM's LEARNED gating, not
encoder richness -- so the encoder is frozen and the ONLY learned params are the WM (key /
write-gate / value-proj) + readout. Each event is an atomic (slot_id, filler) pair, so the
"contextual pass + slice" is degenerate here (each event rep already carries slot+filler);
the sequential WM itself supplies the cross-event integration. Stated: random-init frozen encoder.

ARMS (per seed in {7,13}; SAME frozen encoder shared across arms within a seed):
  LEARNED_WM    -- train key + write-gate + value-proj + readout end-to-end. The capability.
  RANDOM_INIT_WM (>=5 control seeds) -- FREEZE key + write-gate + value-proj at random init,
                   train ONLY the readout. The CAN-FAIL control: MUST stay ~chance (0.05), same
                   as the calibration reservoir arm. LEARNED_WM must BEAT this by a large,
                   significant margin (power_stats z >= 2.0, beats ri_max) -- else the LEARNED
                   gating mechanism is the block.

VERDICT: WM_PROVEN / WM_CANT_LEARN / WM_PARTIAL (see pre-reg bands). Sanity: train_loss must
descend (fit); a STUCK_FLAT loss is the trainability signal, reported explicitly.

Run:  python experiments/exp_selective_overwrite_recall_wm_v1.py --self-test
      python experiments/exp_selective_overwrite_recall_wm_v1.py --full   (default)

ASCII-only. No emojis. Deterministic seeding (torch.Generator + np.random.default_rng; no hash(),
no list(set())). CPU (light task; torch cpu build).
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

# import the CALIBRATED construction (same dir on sys.path when run as a script)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_selective_overwrite_recall_calib_v1 as calib  # noqa: E402

ANCHOR_NAME = "selective_overwrite_recall_wm_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pull the CALIBRATED construction constants (single source of truth) ----
V_FILL = calib.V_FILL              # 20 -> CHANCE = 0.05
CHANCE = calib.CHANCE
S_TARGET = calib.S_TARGET          # 6 target slots
N_DISTRACT_SLOTS = calib.N_DISTRACT_SLOTS
SLOT_VOCAB = S_TARGET + N_DISTRACT_SLOTS
D_EMB = calib.D_EMB                # 64 frozen embedding dim

# ---- WM / training params (author-owned; simplest-first) ----
K_SLOTS = 6                        # content-addressed slots (= S_TARGET; distractors suppressed by gate)
D_MEM = 64                        # slot memory width
HIDDEN = 64                       # write-gate MLP hidden
ADDR_TEMP = 0.3                   # addressing softmax temp: sharpened competition. MEASURED trainability
                                  # probe (2026-07-30): temp=0.3 -> train_acc 0.83@900 steps (learns);
                                  # temp=1.0 -> undertrained/smeared; temp=0.1 -> STUCK@0.33 (too sharp
                                  # from step 0 = degenerate loss surface). 0.3 is the fair-shot lever.

FULL_TRAIN, FULL_EVAL = 1200, 800
STEPS_WM = 2000                   # minibatch Adam steps for LEARNED_WM (early-stops on convergence)
BATCH = 256                       # minibatch size (SGD noise + wall-time affordable)
STEPS_READOUT = 400               # readout-only steps for RANDOM_INIT_WM control (cached-feature fast-path)
LR = 1e-2
EARLY_STOP_LOSS = 0.03            # stop when EMA loss below this (exact-rule fit reached)
RETRY_TRAIN_ACC = 0.50            # a COMPLETED LEARNED_WM run below this train_acc = a dud trajectory
MAX_RESTARTS = 4                  # RESTART a failed LEARNED_WM with a bumped RNG init (measured:
                                  # full-scale seed-13 stalled on ONE trajectory while both seeds
                                  # converge to 1.0 on others -> restart is training-robustness, NOT a
                                  # mechanism change). Trigger = FINAL train_acc (reliable), not an
                                  # early EMA (which killed slow-but-successful escapes -- 2026-07-30).
SEEDS_FULL = (7, 13)
N_RANDOM_INIT = 5                 # random-init-WM control seeds -> distribution for power_stats

# ---- bands (pre-reg) ----
Z_THRESH = 2.0                    # significance beyond random-init spread (~p<0.023)
RI_NEAR_CHANCE = 0.10             # each random-init control MUST be < this (clean floor)
MECH_MARGIN = 0.30                # LEARNED_WM - ri_mean must be >= this
WM_PROVEN_MIN = 0.50              # LEARNED_WM eval acc must be >= this (>=10x chance), both seeds
WM_CANT_LEARN_MAX = 0.15          # <= this (near chance, <3x) on BOTH seeds -> can't-learn
LOSS_DESCEND_RATIO = 0.90         # last_loss < ratio*first_loss => "descended" (else STUCK_FLAT)
ORACLE_CEILING = 1.0              # MEASURED@data/exp_selective_overwrite_recall_calib_v1/metrics.json


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------- canonical hardening: start-marker / crash / atomic ----------------
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
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
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


# ---------------- significance (reused verbatim from the hardened MES gate) ----------------
def _binom_se(acc, n):
    n = max(int(n), 1)
    return math.sqrt(max(acc * (1.0 - acc), 1e-9) / n)


def _one_sided_p(z):
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def power_stats(trained_acc, n_eval, ri_accs):
    """FAIR significance of (trained - random-init) over the random-init distribution. combined SE =
    sqrt(eval-noise(trained) + eval-noise(ri_mean) + ri seed spread). Mirrors exp_stateful_core_mes_
    data_sufficient_gate_v1.power_stats."""
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


# ---------------- batch tensor-ization of the (slot,filler) streams ----------------
def batchify(examples):
    """examples -> padded tensors. Returns dict of LongTensors + a float pad-mask.
      slots [B,Lmax] (int), fills [B,Lmax] (int), active [B,Lmax] (1.0=real event, 0.0=pad),
      query [B] (int, target slot id), answer [B] (int, filler id)."""
    B = len(examples)
    lengths = [len(ex["slots"]) for ex in examples]
    Lmax = max(lengths)
    slots = np.zeros((B, Lmax), dtype=np.int64)
    fills = np.zeros((B, Lmax), dtype=np.int64)
    active = np.zeros((B, Lmax), dtype=np.float32)
    query = np.zeros((B,), dtype=np.int64)
    answer = np.zeros((B,), dtype=np.int64)
    for i, ex in enumerate(examples):
        L = lengths[i]
        slots[i, :L] = ex["slots"]
        fills[i, :L] = ex["fills"]
        active[i, :L] = 1.0
        query[i] = ex["query"]
        answer[i] = ex["answer"]
    return {"slots": torch.from_numpy(slots), "fills": torch.from_numpy(fills),
            "active": torch.from_numpy(active), "query": torch.from_numpy(query),
            "answer": torch.from_numpy(answer)}


# ---------------- frozen random-init encoder (embeddings) ----------------
class FrozenEncoder(nn.Module):
    """Random-init FROZEN Gaussian embeddings for slot ids and fillers. No training."""

    def __init__(self, seed, slot_vocab, v_fill, d_emb):
        super().__init__()
        g = torch.Generator().manual_seed(seed + 90001)
        E_slot = torch.empty(slot_vocab, d_emb)
        E_fill = torch.empty(v_fill, d_emb)
        E_slot.normal_(0.0, 1.0, generator=g).div_(math.sqrt(d_emb))
        E_fill.normal_(0.0, 1.0, generator=g).div_(math.sqrt(d_emb))
        self.E_slot = nn.Parameter(E_slot, requires_grad=False)
        self.E_fill = nn.Parameter(E_fill, requires_grad=False)

    def slot_emb(self, ids):
        return F.embedding(ids, self.E_slot)

    def fill_emb(self, ids):
        return F.embedding(ids, self.E_fill)


# ---------------- the SIMPLEST content-gated overwrite WM ----------------
class ContentGatedWM(nn.Module):
    """K content-addressed slots. Per event: learned content-address key routes slot_id -> slot;
    learned scalar write gate (on slot_id) decides write-or-suppress; gated OVERWRITE update
    (1-w)*h + w*candidate keeps the LAST write (suppresses earlier). Query addresses the queried
    slot_id, reads its slot, readout -> filler class. EntNet-style (Henaff 2017), minimal."""

    def __init__(self, seed, d_emb, d_mem, k_slots, hidden, v_fill, addr_temp):
        super().__init__()
        self.k_slots = k_slots
        self.d_mem = d_mem
        self.addr_temp = addr_temp
        g = torch.Generator().manual_seed(seed + 1234)
        key = torch.empty(k_slots, d_emb)
        key.normal_(0.0, 1.0, generator=g).div_(math.sqrt(d_emb))
        self.key = nn.Parameter(key)                                  # [K, d_emb] address keys
        self.write_gate = nn.Sequential(nn.Linear(d_emb, hidden), nn.Tanh(), nn.Linear(hidden, 1))
        self.value_proj = nn.Linear(d_emb, d_mem)                     # filler emb -> stored candidate
        self.readout = nn.Linear(d_mem, v_fill)                       # stored content -> filler class
        with torch.no_grad():
            for m in list(self.write_gate) + [self.value_proj, self.readout]:
                if isinstance(m, nn.Linear):
                    w = torch.empty_like(m.weight)
                    w.normal_(0.0, 0.1, generator=g)
                    m.weight.copy_(w)
                    m.bias.zero_()

    def wm_params(self):
        """key + write-gate + value-proj (everything BUT the readout) -- frozen in the control."""
        return list(self.write_gate.parameters()) + list(self.value_proj.parameters()) + [self.key]

    def _address(self, slot_emb):
        """slot_emb [B,d_emb] -> addr [B,K] softmax over slots (content-addressed by slot id)."""
        logits = slot_emb @ self.key.t() / self.addr_temp                # [B, K]
        return torch.softmax(logits, dim=-1)

    def read_features(self, enc, batch):
        """Run the WM over the padded stream, then read the queried slot -> h_read [B, d_mem].
        This is everything BEFORE the readout (the WM state the readout decodes)."""
        slots_ids = batch["slots"]; fills_ids = batch["fills"]; active = batch["active"]
        B, Lmax = slots_ids.shape
        h = torch.zeros(B, self.k_slots, self.d_mem)
        for t in range(Lmax):
            s_emb = enc.slot_emb(slots_ids[:, t])                        # [B, d_emb]
            f_emb = enc.fill_emb(fills_ids[:, t])                        # [B, d_emb]
            addr = self._address(s_emb)                                  # [B, K]
            wgate = torch.sigmoid(self.write_gate(s_emb)).squeeze(-1)    # [B] write-or-suppress
            cand = self.value_proj(f_emb)                                # [B, d_mem]
            am = active[:, t]                                            # [B] mask padded events
            w = (addr * (wgate * am).unsqueeze(-1)).unsqueeze(-1)        # [B, K, 1] per-slot write wt
            h = (1.0 - w) * h + w * cand.unsqueeze(1)                    # gated OVERWRITE (last wins)
        q_emb = enc.slot_emb(batch["query"])                            # [B, d_emb]
        addr_q = self._address(q_emb)                                    # [B, K]
        return (addr_q.unsqueeze(-1) * h).sum(dim=1)                     # [B, d_mem] h_read

    def forward(self, enc, batch):
        """Run the WM over the padded stream, then read the queried slot. Returns logits [B, V]."""
        return self.readout(self.read_features(enc, batch))             # [B, V]


# ---------------- train / eval ----------------
def _eval_acc(logits, answer):
    return float((logits.argmax(dim=-1) == answer).float().mean().item())


def _minibatch(tr_batch, idx):
    """Slice a padded batch dict by row indices (LongTensor idx)."""
    return {k: v[idx] for k, v in tr_batch.items()}


def train_arm(enc, wm, tr_batch, ev_batch, steps, lr, train_params, seed, log_tag, batch=None):
    """Train `train_params` (Adam) on CE(query readout, answer), MINIBATCH SGD when `batch` given
    (full-batch otherwise). Returns eval_acc, eval_logits, loss_curve, first/last loss."""
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed + 555)
    opt = torch.optim.Adam(train_params, lr=lr)
    N = tr_batch["answer"].shape[0]
    loss_curve = []
    ema = None
    for step in range(steps):
        opt.zero_grad()
        if batch is not None and batch < N:
            idx = torch.randint(0, N, (batch,), generator=g)
            mb = _minibatch(tr_batch, idx)
        else:
            mb = tr_batch
        logits = wm(enc, mb)
        loss = F.cross_entropy(logits, mb["answer"])
        loss.backward()
        opt.step()
        lv = float(loss.item())
        ema = lv if ema is None else 0.9 * ema + 0.1 * lv   # responsive EMA (only for early-STOP)
        if step == 0 or (step + 1) % max(1, steps // 8) == 0:
            loss_curve.append((step, lv))
        # EARLY-STOP ON CONVERGENCE ONLY (safe: fires when the exact-rule fit is essentially reached).
        # NO early-stall break here -- a slow plateau-escape (measured: seed 7 escapes late) must NOT
        # be killed early. Dud trajectories are caught by the caller via FINAL train_acc + restarted.
        if step >= 400 and ema is not None and ema < EARLY_STOP_LOSS:
            break
    wm.eval()
    with torch.no_grad():
        ev_logits = wm(enc, ev_batch)
        acc = _eval_acc(ev_logits, ev_batch["answer"])
        tr_logits = wm(enc, tr_batch)
        tr_acc = _eval_acc(tr_logits, tr_batch["answer"])
    wm.train()
    first_loss = loss_curve[0][1] if loss_curve else float("nan")
    last_loss = loss_curve[-1][1] if loss_curve else float("nan")
    _log("  [%s seed=%d] eval_acc=%.4f train_acc=%.4f loss %.3f->%.3f ema=%.3f steps=%d"
         % (log_tag, seed, acc, tr_acc, first_loss, last_loss, ema if ema is not None else float("nan"),
            step + 1))
    return dict(eval_acc=acc, train_acc=tr_acc, ev_logits=ev_logits.detach(),
                loss_curve=loss_curve, first_loss=first_loss, last_loss=last_loss,
                ema=float(ema) if ema is not None else float("nan"), steps_run=step + 1)


def train_readout_cached(enc, wm, tr_batch, ev_batch, steps, lr, seed, log_tag):
    """CONTROL fast-path: WM frozen -> read features are FIXED, so compute them ONCE (no_grad) and
    fit ONLY the readout linear on the cached features. Byte-equivalent objective to train_arm with
    train_params=readout, but ~100x faster (skips the sequential WM forward every step)."""
    torch.manual_seed(seed)
    with torch.no_grad():
        tr_feat = wm.read_features(enc, tr_batch)                        # [Ntr, d_mem] fixed
        ev_feat = wm.read_features(enc, ev_batch)
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
    _log("  [%s seed=%d] eval_acc=%.4f loss %.3f->%.3f"
         % (log_tag, seed, acc, loss_curve[0][1], loss_curve[-1][1]))
    return dict(eval_acc=acc, ev_logits=ev_logits.detach(),
                first_loss=loss_curve[0][1], last_loss=loss_curve[-1][1])


def run_seed(seed, train_n, eval_n, steps_wm, steps_readout, n_random_init):
    rng = np.random.default_rng(seed)
    tr = calib.gen_dataset(train_n, rng)
    ev = calib.gen_dataset(eval_n, np.random.default_rng(seed + 777))
    tr_batch = batchify(tr)
    ev_batch = batchify(ev)

    enc = FrozenEncoder(seed, SLOT_VOCAB, V_FILL, D_EMB)

    # LEARNED_WM: train everything (key + write-gate + value-proj + readout). RESTART on early stall
    # (a dud init/trajectory) with a bumped RNG -- training-robustness so the both-seeds replication
    # is real, not trajectory-luck in EITHER direction. First non-stalled attempt is accepted.
    n_attempts = 0
    for attempt in range(MAX_RESTARTS + 1):
        n_attempts = attempt + 1
        wseed = seed + attempt * 7919
        wm = ContentGatedWM(wseed, D_EMB, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP)
        learned = train_arm(enc, wm, tr_batch, ev_batch, steps_wm, LR,
                            list(wm.parameters()), wseed, "LEARNED_WM a%d" % attempt, batch=BATCH)
        if learned["train_acc"] >= RETRY_TRAIN_ACC:
            break
        _log("  LEARNED_WM seed=%d attempt=%d DUD (train_acc=%.3f < %.2f) -> restart"
             % (seed, attempt, learned["train_acc"], RETRY_TRAIN_ACC))
    learned["n_attempts"] = n_attempts

    # RANDOM_INIT_WM controls: freeze key+write-gate+value-proj at random init; train ONLY readout.
    ri_accs = []
    ri_logits_first = None
    for c in range(n_random_init):
        cseed = seed * 100 + c
        wm_ri = ContentGatedWM(cseed, D_EMB, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP)
        for p in wm_ri.wm_params():
            p.requires_grad_(False)
        ri = train_readout_cached(enc, wm_ri, tr_batch, ev_batch, steps_readout, LR,
                                  cseed, "RANDOM_INIT_WM c=%d" % c)
        ri_accs.append(ri["eval_acc"])
        if ri_logits_first is None:
            ri_logits_first = ri["ev_logits"]

    ps = power_stats(learned["eval_acc"], eval_n, ri_accs)

    # arms-must-differ: LEARNED_WM eval logits vs a RANDOM_INIT_WM eval logits (bit-identity guard)
    def _digest(t):
        return hashlib.sha256(t.cpu().numpy().tobytes()).hexdigest()
    arms_differ = _digest(learned["ev_logits"]) != _digest(ri_logits_first)

    return {
        "seed": seed, "train_n": train_n, "eval_n": eval_n, "chance": CHANCE,
        "learned_wm": {"eval_acc": learned["eval_acc"], "train_acc": learned["train_acc"],
                       "first_loss": learned["first_loss"], "last_loss": learned["last_loss"],
                       "loss_curve": learned["loss_curve"], "ema": learned.get("ema"),
                       "n_attempts": learned.get("n_attempts", 1), "steps_run": learned.get("steps_run"),
                       "stalled": learned.get("stalled", False)},
        "random_init_wm": {"accs": ri_accs, "mean": float(np.mean(ri_accs)),
                           "max": float(np.max(ri_accs)), "min": float(np.min(ri_accs))},
        "power": ps,
        "arms_differ_verified": bool(arms_differ),
    }


# ---------------- verdict ----------------
def decide_verdict(per_seed):
    learned_accs = [ps["learned_wm"]["eval_acc"] for ps in per_seed]
    ri_maxes = [ps["random_init_wm"]["max"] for ps in per_seed]
    gaps = [ps["power"]["gap"] for ps in per_seed]
    sigs = [ps["power"]["significant"] for ps in per_seed]

    # control-floor validity: every random-init control MUST be near chance (clean can-fail)
    ri_all = [a for ps in per_seed for a in ps["random_init_wm"]["accs"]]
    control_floor_ok = all(a < RI_NEAR_CHANCE for a in ri_all)

    # loss-descend sanity (per seed)
    loss_shapes = []
    stuck_any = False
    for ps in per_seed:
        fl, ll = ps["learned_wm"]["first_loss"], ps["learned_wm"]["last_loss"]
        descended = (ll < LOSS_DESCEND_RATIO * fl)
        loss_shapes.append({"seed": ps["seed"], "first_loss": fl, "last_loss": ll,
                            "descended": bool(descended)})
        if not descended:
            stuck_any = True

    proven = (all(a >= WM_PROVEN_MIN for a in learned_accs)
              and all(g >= MECH_MARGIN for g in gaps)
              and all(sigs)
              and control_floor_ok)
    cant_learn = all(a <= WM_CANT_LEARN_MAX for a in learned_accs)

    if not control_floor_ok:
        verdict = "CONTROL_FLOOR_BROKEN"
        msg = ("a RANDOM_INIT_WM control cleared %.2f (max over controls=%.3f): the can-fail floor "
               "is not clean -> the task/encoder leaks a shortcut; LEARNED_WM margin not trustworthy"
               % (RI_NEAR_CHANCE, max(ri_all)))
    elif proven:
        verdict = "WM_PROVEN"
        msg = ("LEARNED_WM eval_acc=%s >> chance %.3f AND >> random-init (gap=%s, z=%s, beats ri_max), "
               "BOTH seeds, controls at floor -> the learned content-gated overwrite WM LEARNS the "
               "selective-overwrite-recall the reservoir provably fails. ceiling(oracle)=%.2f."
               % ([round(a, 3) for a in learned_accs], CHANCE, [round(g, 3) for g in gaps],
                  [round(ps["power"]["z"], 2) for ps in per_seed], ORACLE_CEILING))
    elif cant_learn:
        verdict = "WM_CANT_LEARN"
        msg = ("LEARNED_WM stalls near chance (accs=%s <= %.2f) despite features sufficient "
               "(calib gated=1.00): the learned gating mechanism is the block. loss %s -> %s"
               % ([round(a, 3) for a in learned_accs], WM_CANT_LEARN_MAX,
                  "STUCK_FLAT (no fit)" if stuck_any else "DESCENDED (fits but eval-chance: gating not learned)",
                  "diagnose WHY the gate can't be learned"))
    else:
        verdict = "WM_PARTIAL"
        msg = ("LEARNED_WM accs=%s (chance %.3f, gaps=%s, sig=%s): beats random-init but not the "
               "WM_PROVEN bar (>=%.2f both seeds, gap>=%.2f, significant) -> partial; report and iterate."
               % ([round(a, 3) for a in learned_accs], CHANCE, [round(g, 3) for g in gaps], sigs,
                  WM_PROVEN_MIN, MECH_MARGIN))

    bands = {"chance": CHANCE, "oracle_ceiling": ORACLE_CEILING, "wm_proven_min": WM_PROVEN_MIN,
             "wm_cant_learn_max": WM_CANT_LEARN_MAX, "mech_margin": MECH_MARGIN,
             "z_thresh": Z_THRESH, "ri_near_chance": RI_NEAR_CHANCE,
             "learned_accs": learned_accs, "ri_maxes": ri_maxes, "gaps": gaps,
             "significant_per_seed": [bool(s) for s in sigs], "control_floor_ok": bool(control_floor_ok),
             "loss_shapes": loss_shapes}
    return verdict, msg, bands


# ---------------- self-test ----------------
def run_self_test():
    _log("SELF-TEST: torch import + tiny end-to-end (real WM objects) ...")
    torch.manual_seed(7)
    # tiny full pipeline at reduced scale: builds the REAL FrozenEncoder + ContentGatedWM + trains
    res = run_seed(7, train_n=200, eval_n=200, steps_wm=120, steps_readout=60, n_random_init=3)
    lw = res["learned_wm"]["eval_acc"]
    ri = res["random_init_wm"]["mean"]
    _log("  tiny: LEARNED_WM=%.3f RANDOM_INIT_WM(mean)=%.3f gap=%.3f arms_differ=%s"
         % (lw, ri, res["power"]["gap"], res["arms_differ_verified"]))
    # structural asserts (NOT capability asserts -- capability is the FULL run's job):
    assert res["arms_differ_verified"], "arms bit-identical (LEARNED vs RANDOM_INIT eval logits)"
    assert 0.0 <= lw <= 1.0 and 0.0 <= ri <= 1.0, "acc out of range"
    # readback determinism: same seed -> same eval logits
    torch.manual_seed(7)
    enc = FrozenEncoder(7, SLOT_VOCAB, V_FILL, D_EMB)
    wm = ContentGatedWM(7, D_EMB, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP)
    b = batchify(calib.gen_dataset(16, np.random.default_rng(1)))
    with torch.no_grad():
        l1 = wm(enc, b); l2 = wm(enc, b)
    assert torch.allclose(l1, l2), "forward not deterministic on fixed inputs"
    # overwrite (not accumulate) unit check: a slot written twice keeps the LAST candidate when
    # gate*addr ~ 1. Force gate=1, addr one-hot to slot 0, value_proj=identity via manual tensors.
    with torch.no_grad():
        h = torch.zeros(1, 1, 3)
        for cand_val in (torch.tensor([[1.0, 0.0, 0.0]]), torch.tensor([[0.0, 1.0, 0.0]])):
            w = torch.ones(1, 1, 1)  # full overwrite
            h = (1.0 - w) * h + w * cand_val.unsqueeze(1)
        assert torch.allclose(h.squeeze(), torch.tensor([0.0, 1.0, 0.0])), "overwrite kept a blend, not last"
    _log("SELF-TEST PASS")
    return {"tiny": {"learned_wm": lw, "random_init_wm_mean": ri, "gap": res["power"]["gap"],
                     "arms_differ": res["arms_differ_verified"]}}


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--train-n", type=int, default=FULL_TRAIN)
    ap.add_argument("--eval-n", type=int, default=FULL_EVAL)
    ap.add_argument("--steps-wm", type=int, default=STEPS_WM)
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))  # fixed; avoid thread-thrash slowdown
    run_mode = "self_test" if args.self_test else "full"   # default = FULL (defensive; §16)
    expected_units = 1 if run_mode == "self_test" else len(SEEDS_FULL)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS", "verdict_msg": "SELFTEST_PASS (real WM objects + overwrite unit + determinism)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "chance": CHANCE, "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    _log("FULL: train_n=%d eval_n=%d steps_wm=%d seeds=%s chance=%.4f K=%d"
         % (args.train_n, args.eval_n, args.steps_wm, SEEDS_FULL, CHANCE, K_SLOTS))
    per_seed = []
    for seed in SEEDS_FULL:
        _log("--- seed %d ---" % seed)
        per_seed.append(run_seed(seed, args.train_n, args.eval_n, args.steps_wm,
                                 STEPS_READOUT, N_RANDOM_INIT))
    verdict, msg, bands = decide_verdict(per_seed)
    elapsed = time.perf_counter() - t0

    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | chance=%.4f | %s" % (verdict, CHANCE, msg[:140]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "chance": CHANCE, "oracle_ceiling_ref": ORACLE_CEILING, "bands": bands,
        "params": {"K_SLOTS": K_SLOTS, "D_MEM": D_MEM, "D_EMB": D_EMB, "HIDDEN": HIDDEN,
                   "ADDR_TEMP": ADDR_TEMP, "STEPS_WM": args.steps_wm, "STEPS_READOUT": STEPS_READOUT,
                   "LR": LR, "N_RANDOM_INIT": N_RANDOM_INIT, "train_n": args.train_n,
                   "eval_n": args.eval_n, "seeds": list(SEEDS_FULL), "encoder": "random_init_frozen"},
        "per_seed": per_seed})
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
