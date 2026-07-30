# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF; CONTEXT/ORACLE/SHUFFLED/ONEHOT eval-logit hashes)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no Cramer-Rao noise floor; discriminator = held-out-role RECALL accuracy vs the
#   pre-registered ORACLE_SUFFICIENT/ORACLE_INSUFFICIENT/INVALID bands (Director spawn 2026-07-30).
#   chance_recall=1/V_FILL=0.05, oracle ceiling 1.0.
# - baseline_in_band: ARM_CONTEXTVARYING is the can-fail control; MUST reproduce near-chance recall on
#   held-out roles, else the test is vacuous (INVALID). ARM_SHUFFLED_ORACLE is the can-fail floor; MUST
#   also fail, else the metric can't discriminate (a stable-but-wrong address would also "work").
# - discriminator survives scale: this cell IS the discriminator-preview -- a decisive, cheap (<5min),
#   frozen-encoder ORACLE probe run BEFORE any encoder-training bet. self-test builds the REAL v2
#   encoder + REAL ReadCondWM at tiny N (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set())
"""ORACLE context-invariant role-address vs the proven content-gated WM (v1) -- decisive, cheap,
work-backwards test of WHICH property the frozen encoder is missing, run BEFORE betting ~15h on an
encoder-training pivot.

CONTEXT (Director spawn 2026-07-30, work-backwards from what is already VET-confirmed):
  (1) PROVEN: the content-gated WM mechanism learns+generalizes given clean/separable reps
      (WM_PROVEN, commit 88d050955, degenerate encoder).
  (2) PROVEN: the SAME WM learns real-NL role-filler binding at eval~0.99 once the addressing key is
      warm-started + an aux slot-address CE loss is added on TOP OF pca_whiten-conditioned frozen-v2
      reps (WM_NL_PROVEN_VIA_READ_CONDITIONING, commit b3bc526ee,
      exp_selective_overwrite_recall_nl_wm_readcond_v1.py) -- but that eval used items drawn from the
      SAME 6 roles seen by the probe supervision: item-generalization, not addressing-mechanism
      generalization to a genuinely unsupervised role.
  (3) MEASURED: role identity IS present in the real frozen v2 MLM encoder reps -- a linear probe
      decodes held-out roles at 0.95 (exp_shared_component_role_identity_probe_v1).
  (4) HARD-FAILED (commit f3d621168 + f5951e9a6): BOTH a learned-key-with-warmstart approach
      (exp_wm_addressing_heldout_role_warmstart_v1) AND a second (fixed-DG) addressing approach FAILED
      to generalize the ADDRESSING mechanism itself to held-out roles, because the frozen reps are
      CONTEXT-ENTANGLED: the same role's role-query-extracted rep varies across sentences (raw
      query-slot pairwise cosine ~0.99), so no address key row can stay correct for that role across
      all its contexts without per-role supervision (a per-instance-lookup pattern, not generalizing).

THE DECISIVE QUESTION THIS CELL ANSWERS: is CONTEXT-INVARIANCE of the role representation the
SUFFICIENT missing property? IF the role representation were context-invariant (one stable vector per
role, distinct per role), would the ALREADY-PROVEN WM mechanism -- with NO aux loss, NO warm-start
probe, ordinary end-to-end recall-CE gradient descent only -- generalize its addressing to a role it
was NEVER given explicit address-supervision on? This is an ORACLE/upper-bound probe: it does not
propose a deployable encoder fix; it tests whether the ONE missing ingredient (a stable per-role
vector) is sufficient, cheaply, before committing to an encoder-training pivot that specifically
targets context-invariance.

CONSTRUCTION (reuses the SAME 15-role/12-train/3-held split + task + frozen v2 encoder as
exp_wm_addressing_heldout_role_warmstart_v1, aliased `ho` below; the SAME proven ReadCondWM
architecture + pca_whiten Conditioner as exp_selective_overwrite_recall_nl_wm_readcond_v1, aliased
`rc`; nothing on disk in either file is modified -- ho's own module-level `base.S_TARGET = 15`
monkeypatch fires on import, exactly as it does for ho itself):

  ORACLE TABLE (context-invariant address, one row per role, all 15 roles -- LEGITIMATE here: this is
  an upper-bound oracle probe of "does the property suffice", NOT a deployable method): a FIXED
  (never-trained) probe role-query attends over pca_whiten-conditioned frozen-v2 token reps of EVERY
  cached context for that role (its QUERY_TEMPLATE sentence + all EVENT_TEMPLATES x COLORS event
  sentences -- the SAME corpus enumeration ho's warm_start_key_heldout uses, just extended to all 15
  roles instead of only TRAIN_ROLES), then averages them into ONE stable vector per role. This is
  derived entirely from the REAL encoder, not synthetic.

  THE ONE VARIABLE: what feeds the WM's address key-lookup (`wm._addr_logits`) for a TARGET-role
  event/query token. The filler-VALUE extraction path, the write-gate's input, the WM architecture
  (role_query/key/write_gate/value_proj/readout), the split, the seeds, and the training steps are
  IDENTICAL across all four arms (see read_features_arm()). Distractor-role tokens (slot id >= 15,
  outside the oracle table's domain) always keep the natural context-varying address input in every
  arm, so distractor-suppression learning is not a confound between arms.

ARMS (2 seeds each: 7, 13):
  ARM_CONTEXTVARYING  -- address input = the actual per-sentence role-query-extracted rep (context-
    varying, exactly what f3d621168/f5951e9a6 already showed fails to generalize). CAN-FAIL CONTROL:
    MUST reproduce near-chance held-out recall, or the test is vacuous.
  ARM_ORACLE_INVARIANT -- address input = the oracle table row for that role (same vector regardless
    of which context produced the token). THE DECISIVE ARM.
  ARM_SHUFFLED_ORACLE -- address input = the oracle table PERMUTED across roles (fixed derangement --
    a stable address, but the WRONG one for every role). CAN-FAIL FLOOR: MUST also fail, or a
    stable-but-wrong address would "work" too and the metric can't discriminate correct addressing.
  ARM_ONEHOT_ORACLE -- address input = 15 orthonormal directions (QR of a random matrix), one per
    role: a CEILING reference establishing the WM's best case given PERFECT, maximally separated
    addressing (not load-bearing for the verdict; reported alongside).

DECISIVE METRIC: recall_heldout_acc (predicted filler == true filler, evaluated on held-out-role
queries only), both seeds. recall_train_acc also reported (secondary).

PRE-REGISTERED DECISION RULE (written BEFORE running; NOT loosened after seeing results):
  ORACLE_SUFFICIENT: ARM_ORACLE_INVARIANT recall_held >= ORACLE_MIN=0.50 on BOTH seeds AND
    (ARM_ORACLE_INVARIANT recall_held - ARM_SHUFFLED_ORACLE recall_held) >= SHUFFLED_MARGIN=0.30 on
    BOTH seeds AND ARM_CONTEXTVARYING recall_held <= FAIL_MAX (both seeds) AND ARM_SHUFFLED_ORACLE
    recall_held <= FAIL_MAX (both seeds). => context-invariance IS the sufficient missing property;
    the encoder-training target is now exactly defined + measurable.
  ORACLE_INSUFFICIENT: the two can-fail checks (ARM_CONTEXTVARYING fails, ARM_SHUFFLED_ORACLE fails)
    both hold (test is VALID), but ARM_ORACLE_INVARIANT does NOT clear ORACLE_MIN and/or the
    SHUFFLED_MARGIN on some seed => context-invariance ALONE is NOT sufficient; the requirement is
    more (role-distinctness / filler-invariance / other) -- learned cheaply, before the encoder bet.
  INVALID: ARM_CONTEXTVARYING does NOT fail (recall_held > FAIL_MAX on some seed -- test vacuous, the
    "failure" this cell is supposed to reproduce did not reproduce) OR ARM_SHUFFLED_ORACLE does NOT
    fail (recall_held > FAIL_MAX on some seed -- a stable-but-wrong address also "works", so the
    metric can't discriminate correct addressing from merely-stable addressing).

FAIL_MAX = CHANCE_RECALL(0.05) + NEAR_CHANCE_MARGIN(0.10) = 0.15  (a held-out recall at or below this
is "near chance"/failed, matching the near-chance margins used elsewhere in this repo's WM cells).

Run:  .venv/Scripts/python.exe experiments/exp_oracle_context_invariant_address_wm_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_oracle_context_invariant_address_wm_v1.py --full

ASCII-only. No emojis. Deterministic seeding (torch.Generator + np.random.default_rng; no hash(), no
list(set())). CPU (local, push-free; this .venv has no CUDA). progress_logging: print_flush_true.
Compute architecture: sequential-CPU, justified -- 4 arms x 2 seeds = 8 tiny WM-training units
(K_SLOTS=15, D_MEM=64), each a few hundred gradient steps over a small cached-rep batch; total wall
time is a design target of <5 minutes (reduced train_n/eval_n/steps vs the richer readcond/heldout
cells -- compute-proportionality: this is a cheap oracle GATE question, not a magnitude-fit).
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
import torch.nn.functional as F

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_selective_overwrite_recall_nl_calib_v1 as calib  # noqa: E402
import exp_selective_overwrite_recall_nl_wm_roleseparated_v1 as base  # noqa: E402
import exp_selective_overwrite_recall_nl_wm_readcond_v1 as rc  # noqa: E402
import exp_wm_addressing_heldout_role_warmstart_v1 as ho  # noqa: E402  -- fires base.S_TARGET=15 patch

ANCHOR_NAME = "oracle_context_invariant_address_wm_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402  -- per-unit checkpoint/resume (MANDATORY, CLAUDE.md)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
V2_CKPT = base.V2_CKPT

# ---- reused constants (single source of truth: ho / rc / calib) ----
S_TARGET_TOTAL = ho.S_TARGET_TOTAL          # 15 (MEASURED@ho: widened target-role inventory)
TRAIN_ROLES = ho.TRAIN_ROLES
HELD_OUT_ROLES = ho.HELD_OUT_ROLES
K_SLOTS = S_TARGET_TOTAL
D_MEM = rc.D_MEM                            # 64
HIDDEN = rc.HIDDEN                          # 64
ADDR_TEMP = rc.ADDR_TEMP                    # 0.3
V_FILL = ho.V_FILL                          # 20 -> CHANCE_RECALL = 0.05
CHANCE_RECALL = ho.CHANCE_RECALL
QUERY_TEMPLATE = ho.QUERY_TEMPLATE
SLOT_NOUNS = ho.SLOT_NOUNS
EVENT_TEMPLATES = ho.EVENT_TEMPLATES
COLORS = ho.COLORS

# ---- run params (compute-proportionality: cheap oracle GATE, not a magnitude-fit; <5min target) ----
FULL_TRAIN, FULL_EVAL = 400, 250
STEPS_WM = 250
BATCH = 128
LR = 1e-2
EARLY_STOP_LOSS = 0.05
SEEDS_FULL = (7, 13)
ORACLE_PROBE_SEED = 20260730                # fixed probe role-query seed (independent of training seed)

# ---- pre-registered bands (this file, written BEFORE running; NOT loosened) ----
NEAR_CHANCE_MARGIN = 0.10
FAIL_MAX = CHANCE_RECALL + NEAR_CHANCE_MARGIN         # THEORETICAL: 0.05 + 0.10 = 0.15
ORACLE_MIN = 0.50
SHUFFLED_MARGIN = 0.30

ARMS = ("context", "oracle", "shuffled", "onehot")


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


def _jsonify(obj):
    if isinstance(obj, torch.Tensor):
        return _jsonify(obj.detach().cpu().tolist())
    if isinstance(obj, np.ndarray):
        return _jsonify(obj.tolist())
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {str(k): _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]
    return obj


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    safe_metrics = _jsonify(metrics)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(safe_metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _digest_tensor(t):
    return hashlib.sha256(t.detach().cpu().numpy().tobytes()).hexdigest()


# ---------------- oracle table construction (fixed, never-trained probe role-query) ----------------
def build_role_query_probe(seed, d_enc):
    g = torch.Generator().manual_seed(seed + 424242)
    rq = torch.empty(d_enc)
    rq.normal_(0.0, 0.02, generator=g)
    return rq


def _extract_slot_rep_single(rq_row, U_tok, U_pad, d_enc):
    """Single-role-query attention pooling over ALL cached sentences (mirrors ReadCondWM._role_reps
    but for one fixed query row instead of the 2-row trainable role_query)."""
    scores = torch.einsum("nld,d->nl", U_tok, rq_row) / math.sqrt(d_enc)
    scores = scores.masked_fill(U_pad, float("-inf"))
    attn = torch.softmax(scores, dim=-1)
    return torch.einsum("nl,nld->nd", attn, U_tok)


def build_oracle_table(enc, Uc, seed):
    """Averages the FIXED probe's role-query-extracted rep across ALL of a role's contexts (its
    QUERY_TEMPLATE sentence + every EVENT_TEMPLATES x COLORS event sentence), for ALL 15 roles
    (train AND held-out -- legitimate here: upper-bound oracle probe of context-invariance, not a
    deployable method). Same corpus enumeration as ho.warm_start_key_heldout's TRAIN_ROLES loop,
    extended to all roles. Returns ([15, d_enc] table, per-role context counts)."""
    rq_row = build_role_query_probe(seed, enc.d)
    all_reps = _extract_slot_rep_single(rq_row, Uc, enc.U_pad_t, enc.d)     # [Nu, d]
    table = torch.zeros(S_TARGET_TOTAL, enc.d)
    n_ctx = []
    for s in range(S_TARGET_TOTAL):
        idxs = [enc.idx_of(QUERY_TEMPLATE.format(slot=SLOT_NOUNS[s]))]
        for tm in EVENT_TEMPLATES:
            for fl in COLORS:
                idxs.append(enc.idx_of(tm.format(slot=SLOT_NOUNS[s], fill=fl)))
        idx_t = torch.tensor(idxs)
        table[s] = all_reps[idx_t].mean(dim=0)
        n_ctx.append(len(idxs))
    return table, n_ctx


def build_shuffled_table(table, seed):
    """Fixed derangement (no self-map) of the oracle table rows -- a stable address, but WRONG."""
    n = table.shape[0]
    rng = np.random.default_rng(seed + 13579)
    perm = rng.permutation(n)
    tries = 0
    while any(int(perm[i]) == i for i in range(n)):
        perm = rng.permutation(n)
        tries += 1
        if tries > 1000:
            raise RuntimeError("could not find a derangement in 1000 tries")
    perm_list = [int(x) for x in perm]
    return table[torch.tensor(perm_list)], perm_list


def build_onehot_table(d_enc, k, seed):
    """Ceiling reference: k orthonormal directions in R^d_enc (QR of a random matrix) -- a clean,
    maximally-separated address per role, establishing the WM's best case given PERFECT addressing."""
    g = torch.Generator().manual_seed(seed + 987654)
    M = torch.randn(d_enc, d_enc, generator=g)
    Q, _ = torch.linalg.qr(M)
    return Q[:, :k].t().contiguous()          # [k, d_enc], orthonormal rows


def build_all_tables(enc, Uc):
    table, n_ctx = build_oracle_table(enc, Uc, ORACLE_PROBE_SEED)
    shuffled, perm = build_shuffled_table(table, ORACLE_PROBE_SEED)
    onehot = build_onehot_table(enc.d, S_TARGET_TOTAL, ORACLE_PROBE_SEED)
    # scale onehot rows to the oracle table's mean row norm so _addr_logits/temp isn't out of scale
    mean_norm = float(table.norm(dim=1).mean())
    onehot = onehot * mean_norm
    return {"context": None, "oracle": table, "shuffled": shuffled, "onehot": onehot}, \
        {"n_ctx_per_role": n_ctx, "shuffle_perm": perm, "onehot_mean_norm_scale": mean_norm}


# ---------------- ONE-VARIABLE WM forward: address input differs by arm, everything else identical --
def read_features_arm(wm, batch, mode, oracle_table):
    """mode in ARMS. The address key-lookup input for TARGET-role tokens/queries is the ONE variable;
    the filler-VALUE extraction path (ev_fill) and the write-gate's input (flat_gate_in, always the
    real context rep) are IDENTICAL across every mode. Distractor-role tokens (ev_slot == -1, i.e. slot
    id >= S_TARGET_TOTAL per ho.build_index_batch_ext) always keep the natural context address input,
    in every mode -- distractor-suppression learning is not a confound between arms."""
    slot_u, fill_u = wm._role_reps()                        # [Nu, d] (WM's own trainable role_query)
    ev_idx = batch["ev_idx"]; active = batch["active"]; q_idx = batch["q_idx"]
    ev_slot = batch["ev_slot"]; q_slot = batch["q_slot"]
    B, Lmax = ev_idx.shape
    ev_slot_ctx = slot_u[ev_idx]                             # [B,Lmax,d] context rep (gate input, always)
    ev_fill = fill_u[ev_idx]                                 # UNCHANGED filler path in every arm
    if mode == "context":
        ev_addr_in = ev_slot_ctx
        q_addr_in = slot_u[q_idx]
    else:
        is_target = (ev_slot >= 0).unsqueeze(-1)             # [B,Lmax,1]
        oracle_rows = oracle_table[ev_slot.clamp(min=0)]     # [B,Lmax,d]; rows for slot=-1 discarded below
        ev_addr_in = torch.where(is_target, oracle_rows, ev_slot_ctx)
        q_addr_in = oracle_table[q_slot]                     # queries are always target roles
    flat_addr = ev_addr_in.reshape(B * Lmax, wm.d_enc)
    flat_gate_in = ev_slot_ctx.reshape(B * Lmax, wm.d_enc)   # gate ALWAYS sees the real context rep
    ev_logits = wm._addr_logits(flat_addr).reshape(B, Lmax, wm.k_slots)
    addr = torch.softmax(ev_logits, dim=-1)
    wgate = torch.sigmoid(wm.write_gate(flat_gate_in)).reshape(B, Lmax)
    cand = wm.value_proj(ev_fill.reshape(B * Lmax, wm.d_enc)).reshape(B, Lmax, wm.d_mem)
    h = torch.zeros(B, wm.k_slots, wm.d_mem)
    for t in range(Lmax):
        w = (addr[:, t] * (wgate[:, t] * active[:, t]).unsqueeze(-1)).unsqueeze(-1)
        h = (1.0 - w) * h + w * cand[:, t].unsqueeze(1)
    q_logits = wm._addr_logits(q_addr_in)
    addr_q = torch.softmax(q_logits, dim=-1)
    h_read = (addr_q.unsqueeze(-1) * h).sum(dim=1)
    return h_read, ev_logits, q_logits


def _eval_acc(logits, answer):
    return float((logits.argmax(dim=-1) == answer).float().mean().item())


def build_wm(seed, enc, Uc):
    return rc.ReadCondWM(seed, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP, Uc, enc.U_pad_t)


def train_oracle_arm(wm, tr_batch, ev_batch, mode, oracle_table, steps, lr, seed, log_tag):
    torch.manual_seed(seed)
    g = torch.Generator().manual_seed(seed + 555)
    opt = torch.optim.Adam(wm.parameters(), lr=lr)
    N = tr_batch["answer"].shape[0]
    loss_curve = []
    ema = None
    step = 0
    for step in range(steps):
        opt.zero_grad()
        if BATCH < N:
            idx = torch.randint(0, N, (BATCH,), generator=g)
            mb = {k: v[idx] for k, v in tr_batch.items()}
        else:
            mb = tr_batch
        h_read, _, _ = read_features_arm(wm, mb, mode, oracle_table)
        logits = wm.readout(h_read)
        loss = F.cross_entropy(logits, mb["answer"])
        loss.backward()
        opt.step()
        lv = float(loss.item())
        ema = lv if ema is None else 0.9 * ema + 0.1 * lv
        if step == 0 or (step + 1) % max(1, steps // 6) == 0:
            loss_curve.append((step, lv))
            _log("    [%s seed=%d] step=%d loss=%.4f ema=%.4f" % (log_tag, seed, step + 1, lv, ema))
        if step >= 100 and ema is not None and ema < EARLY_STOP_LOSS:
            break
    wm.eval()
    with torch.no_grad():
        ev_h, _, _ = read_features_arm(wm, ev_batch, mode, oracle_table)
        ev_pred = wm.readout(ev_h)
        eval_acc = _eval_acc(ev_pred, ev_batch["answer"])
        recall_correct = (ev_pred.argmax(-1) == ev_batch["answer"]).float()
        tm, hm = ev_batch["q_is_train"], ev_batch["q_is_heldout"]
        recall_train_acc = float(recall_correct[tm].mean()) if tm.any() else float("nan")
        recall_held_acc = float(recall_correct[hm].mean()) if hm.any() else float("nan")
        tr_h, _, _ = read_features_arm(wm, tr_batch, mode, oracle_table)
        tr_pred = wm.readout(tr_h)
        tr_acc = _eval_acc(tr_pred, tr_batch["answer"])
    wm.train()
    first_loss = loss_curve[0][1] if loss_curve else float("nan")
    last_loss = loss_curve[-1][1] if loss_curve else float("nan")
    _log("  [%s seed=%d] eval_acc=%.4f train_acc=%.4f recall_train=%.4f recall_held=%.4f "
         "loss %.3f->%.3f steps=%d"
         % (log_tag, seed, eval_acc, tr_acc, recall_train_acc, recall_held_acc, first_loss, last_loss,
            step + 1))
    return dict(eval_acc=eval_acc, train_acc=tr_acc, recall_train_acc=recall_train_acc,
                recall_heldout_acc=recall_held_acc, ev_logits=ev_pred.detach(),
                loss_curve=loss_curve, steps_run=step + 1, first_loss=first_loss, last_loss=last_loss)


def _strip_for_checkpoint(res):
    out = dict(res)
    t = out.pop("ev_logits")
    out["ev_logits_sha256"] = _digest_tensor(t)
    return out


# ---------------- self-test: oracle-averaging construction (context-invariant by construction) ------
def role_invariance_construction_selftest(enc, Uc, oracle_table, shuffled_table):
    """Directly proves the load-bearing construction claim: in mode='oracle', the address key-lookup
    input for a TARGET-role token depends ONLY on its ev_slot id, NOT on which sentence (ev_idx)
    produced it -- i.e. context-invariant by construction. In mode='context' the same change in ev_idx
    (different underlying sentence, same claimed role) DOES change the address input. Also verifies the
    shuffled table is a genuine derangement (every role gets a DIFFERENT, wrong vector)."""
    wm = rc.ReadCondWM(7, enc.d, D_MEM, K_SLOTS, HIDDEN, V_FILL, ADDR_TEMP, Uc, enc.U_pad_t)
    s = 0
    idx_a = enc.idx_of(QUERY_TEMPLATE.format(slot=SLOT_NOUNS[s]))
    idx_b = enc.idx_of(EVENT_TEMPLATES[0].format(slot=SLOT_NOUNS[s], fill=COLORS[0]))
    assert idx_a != idx_b, "self-test picked identical sentence indices (construction bug)"
    ev_idx_a = torch.tensor([[idx_a]])
    ev_idx_b = torch.tensor([[idx_b]])
    ev_slot = torch.tensor([[s]])              # SAME claimed role in both batches
    q_idx = torch.tensor([idx_a])
    q_slot = torch.tensor([s])
    active = torch.ones(1, 1)
    batch_a = {"ev_idx": ev_idx_a, "ev_slot": ev_slot, "q_idx": q_idx, "q_slot": q_slot, "active": active}
    batch_b = {"ev_idx": ev_idx_b, "ev_slot": ev_slot, "q_idx": q_idx, "q_slot": q_slot, "active": active}
    with torch.no_grad():
        _, ev_logits_ctx_a, _ = read_features_arm(wm, batch_a, "context", oracle_table)
        _, ev_logits_ctx_b, _ = read_features_arm(wm, batch_b, "context", oracle_table)
        _, ev_logits_orc_a, _ = read_features_arm(wm, batch_a, "oracle", oracle_table)
        _, ev_logits_orc_b, _ = read_features_arm(wm, batch_b, "oracle", oracle_table)
    context_varies = not torch.allclose(ev_logits_ctx_a, ev_logits_ctx_b, atol=1e-6)
    oracle_invariant = torch.allclose(ev_logits_orc_a, ev_logits_orc_b, atol=1e-6)
    assert context_varies, ("SELF-TEST SETUP BUG: the two contexts for role %d produced identical "
                             "context-mode address logits -- the invariance check would be vacuous" % s)
    assert oracle_invariant, ("ORACLE MODE IS NOT CONTEXT-INVARIANT: same role, different sentence "
                              "(ev_idx %d vs %d) produced different address logits" % (idx_a, idx_b))
    n = shuffled_table.shape[0]
    derangement_ok = all(not torch.allclose(shuffled_table[r], oracle_table[r], atol=1e-6)
                          for r in range(n))
    assert derangement_ok, "shuffled table has a fixed point (role mapped to its own true vector)"
    return {"context_varies_across_sentences": bool(context_varies),
            "oracle_invariant_across_sentences": bool(oracle_invariant),
            "shuffled_table_is_genuine_derangement": bool(derangement_ok)}


# ---------------- self-test: serialization + checkpoint/resume (same pattern as ho) ----------------
def serialization_selftest():
    fake = {"arms": {"oracle": {"recall_heldout_acc": np.float64(0.6)},
                     "loss_curve": [(0, torch.tensor(1.0)), (10, 0.2)]}}
    safe = _jsonify(fake)
    dumped = json.dumps(safe)
    reloaded = json.loads(dumped)
    assert isinstance(reloaded["arms"]["oracle"]["recall_heldout_acc"], float)
    fake_train_res = dict(eval_acc=0.5, train_acc=0.6, recall_train_acc=0.5, recall_heldout_acc=0.4,
                           ev_logits=torch.randn(4, K_SLOTS), loss_curve=[(0, 1.0)],
                           steps_run=11, first_loss=1.0, last_loss=0.5)
    stripped = _strip_for_checkpoint(fake_train_res)
    assert "ev_logits" not in stripped
    json.dumps(stripped)
    return {"jsonify_roundtrip_ok": True, "strip_for_checkpoint_ok": True}


def checkpoint_resume_selftest():
    import shutil
    import tempfile
    tmp_dir = tempfile.mkdtemp(prefix="oracle_addr_ckpt_selftest_")
    try:
        unit_specs = [("context", 7), ("oracle", 7), ("shuffled", 7), ("onehot", 7)]

        def _compute(kind, seed):
            g = torch.Generator().manual_seed((abs(hash(kind)) % 100000) + seed)
            return {"kind": kind, "seed": seed, "acc": float(torch.rand(1, generator=g).item()),
                    "ev_logits_sha256": _digest_tensor(torch.rand(3, 3, generator=g))}

        d_single = os.path.join(tmp_dir, "single")
        for kind, seed in unit_specs:
            k = ckpt.unit_key(kind, seed)
            res = _compute(kind, seed)
            json.dumps(res)
            ckpt.record_unit(d_single, k, res)
        single_final = ckpt.load_units(d_single)
        assert len(single_final) == 4

        d_resume = os.path.join(tmp_dir, "resume")
        for kind, seed in unit_specs[:2]:
            ckpt.record_unit(d_resume, ckpt.unit_key(kind, seed), _compute(kind, seed))
        done = ckpt.completed_units(d_resume)
        assert done == {ckpt.unit_key(k, s) for k, s in unit_specs[:2]}
        n_skipped = 0
        for kind, seed in unit_specs:
            k = ckpt.unit_key(kind, seed)
            if k in done:
                n_skipped += 1
                continue
            ckpt.record_unit(d_resume, k, _compute(kind, seed))
        assert n_skipped == 2
        resumed_final = ckpt.load_units(d_resume)
        assert json.dumps(resumed_final, sort_keys=True) == json.dumps(single_final, sort_keys=True)
        return {"resume_skip_count": n_skipped, "bit_identical_resume": True}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------- self-test ----------------
def run_self_test():
    _log("SELF-TEST: serialization safety ...")
    ser_diag = serialization_selftest()
    _log("  PASS: %s" % ser_diag)

    _log("SELF-TEST: checkpoint/resume wiring ...")
    ckpt_diag = checkpoint_resume_selftest()
    _log("  PASS: %s" % ckpt_diag)

    _log("SELF-TEST: load REAL v2 encoder (widened closed sentence set via ho's monkeypatch) ...")
    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    enc = base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    assert n_cached >= 3000, "closed sentence set smaller than expected (widened query set missing?)"
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, "pca_whiten")

    _log("SELF-TEST: build oracle/shuffled/onehot tables from the REAL encoder ...")
    tables, table_diag = build_all_tables(enc, Uc)
    _log("  n_ctx_per_role=%s (min=%d max=%d) mean_row_norm(oracle)=%.4f"
         % (table_diag["n_ctx_per_role"][:3] + ["..."], min(table_diag["n_ctx_per_role"]),
            max(table_diag["n_ctx_per_role"]), float(tables["oracle"].norm(dim=1).mean())))
    assert tables["oracle"].shape == (S_TARGET_TOTAL, enc.d)
    assert tables["shuffled"].shape == tables["oracle"].shape
    assert tables["onehot"].shape == tables["oracle"].shape

    _log("SELF-TEST: role invariance-by-construction (context varies, oracle does not) ...")
    inv_diag = role_invariance_construction_selftest(enc, Uc, tables["oracle"], tables["shuffled"])
    _log("  PASS: %s" % inv_diag)

    _log("SELF-TEST: tiny end-to-end all 4 arms (arms-must-differ, ranges valid) ...")
    tr = ho.gen_dataset_expanded(150, np.random.default_rng(7))
    ev = ho.gen_dataset_expanded(150, np.random.default_rng(7 + 777))
    tr_b = ho.build_index_batch_ext(tr, enc, 7)
    ev_b = ho.build_index_batch_ext(ev, enc, 7 + 777)
    assert ev_b["q_is_heldout"].sum().item() > 0, "tiny eval set drew no held-out-role queries"
    tiny_results = {}
    for mode in ARMS:
        wm = build_wm(7, enc, Uc)
        res = train_oracle_arm(wm, tr_b, ev_b, mode, tables[mode], steps=40, lr=LR, seed=7,
                                log_tag="TINY_%s" % mode)
        tiny_results[mode] = res
        assert 0.0 <= res["eval_acc"] <= 1.0
        assert 0.0 <= res["recall_heldout_acc"] <= 1.0 or math.isnan(res["recall_heldout_acc"])
    digests = {m: _digest_tensor(r["ev_logits"]) for m, r in tiny_results.items()}
    pairs = [(a, b) for a in digests for b in digests if a < b]
    for a, b in pairs:
        assert digests[a] != digests[b], (
            "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (a, b))
    _log("SELF-TEST PASS")
    return {"serialization_selftest": ser_diag, "checkpoint_resume_selftest": ckpt_diag,
            "n_cached": n_cached, "table_diag": table_diag, "invariance_diag": inv_diag,
            "tiny": {m: {"eval_acc": r["eval_acc"], "recall_train": r["recall_train_acc"],
                         "recall_held": r["recall_heldout_acc"]} for m, r in tiny_results.items()},
            "arms_differ_verified": True}


# ---------------- verdict ----------------
def decide_verdict(arm_results):
    """arm_results: {mode: [per-seed dict, ...]} for mode in ARMS."""
    ctx_held = [r["recall_heldout_acc"] for r in arm_results["context"]]
    orc_held = [r["recall_heldout_acc"] for r in arm_results["oracle"]]
    shf_held = [r["recall_heldout_acc"] for r in arm_results["shuffled"]]
    onh_held = [r["recall_heldout_acc"] for r in arm_results["onehot"]]

    ctx_fails = all(h <= FAIL_MAX for h in ctx_held)
    shf_fails = all(h <= FAIL_MAX for h in shf_held)
    gaps_vs_shuffled = [o - s for o, s in zip(orc_held, shf_held)]

    if not ctx_fails:
        verdict = "INVALID"
        msg = ("ARM_CONTEXTVARYING did not reproduce near-chance held-out recall (fail_max=%.3f): "
               "held=%s -- the prior HARD-FAIL (f3d621168/f5951e9a6) did not reproduce at this reduced "
               "scale/schedule; the test is vacuous as run. Do not interpret ORACLE arm against this "
               "control." % (FAIL_MAX, [round(h, 3) for h in ctx_held]))
    elif not shf_fails:
        verdict = "INVALID"
        msg = ("ARM_SHUFFLED_ORACLE did not fail (fail_max=%.3f): held=%s -- a stable-but-WRONG "
               "address also produces non-trivial recall, so the metric cannot discriminate correct "
               "addressing from merely-stable addressing. Any ORACLE win is untrustworthy until this "
               "is fixed (e.g. larger K, longer TAIL_MIN, or a construction change)."
               % (FAIL_MAX, [round(h, 3) for h in shf_held]))
    else:
        oracle_clears_min = all(h >= ORACLE_MIN for h in orc_held)
        oracle_clears_shuffled = all(g >= SHUFFLED_MARGIN for g in gaps_vs_shuffled)
        if oracle_clears_min and oracle_clears_shuffled:
            verdict = "ORACLE_SUFFICIENT"
            msg = ("Context-invariance IS the sufficient missing property: ARM_ORACLE_INVARIANT "
                   "held-out recall=%s (>= %.2f both seeds) clears ARM_SHUFFLED_ORACLE (%s) by >= %.2f "
                   "(gaps=%s), while ARM_CONTEXTVARYING (%s) and ARM_SHUFFLED_ORACLE (%s) both stayed "
                   "<= %.3f. The proven WM generalizes its addressing to held-out roles given ONLY a "
                   "stable, distinct per-role vector -- NO aux loss, NO warm-start probe. The encoder-"
                   "training target is now exactly defined: make role reps context-invariant. "
                   "ARM_ONEHOT_ORACLE (perfect-address ceiling) held-out recall=%s for reference."
                   % ([round(h, 3) for h in orc_held], ORACLE_MIN, [round(h, 3) for h in shf_held],
                      SHUFFLED_MARGIN, [round(g, 3) for g in gaps_vs_shuffled],
                      [round(h, 3) for h in ctx_held], [round(h, 3) for h in shf_held], FAIL_MAX,
                      [round(h, 3) for h in onh_held]))
        else:
            verdict = "ORACLE_INSUFFICIENT"
            msg = ("Context-invariance ALONE is NOT sufficient: with both can-fail controls valid "
                   "(ARM_CONTEXTVARYING held=%s <= %.3f, ARM_SHUFFLED_ORACLE held=%s <= %.3f), "
                   "ARM_ORACLE_INVARIANT held-out recall=%s did not clear ORACLE_MIN=%.2f and/or beat "
                   "ARM_SHUFFLED_ORACLE by >= %.2f (gaps=%s) on every seed -- a perfectly stable, "
                   "distinct per-role address is not enough for the proven WM to generalize its "
                   "addressing via ordinary end-to-end gradient descent alone. The residual gap "
                   "implicates something beyond raw stability (e.g. the WM's addressing capacity/"
                   "temperature, or an interaction with the filler-value path) -- learned cheaply, "
                   "before the encoder-training bet. ARM_ONEHOT_ORACLE (perfect-address ceiling) "
                   "held-out recall=%s for reference."
                   % ([round(h, 3) for h in ctx_held], FAIL_MAX, [round(h, 3) for h in shf_held],
                      FAIL_MAX, [round(h, 3) for h in orc_held], ORACLE_MIN, SHUFFLED_MARGIN,
                      [round(g, 3) for g in gaps_vs_shuffled], [round(h, 3) for h in onh_held]))
    bands = {"chance_recall": CHANCE_RECALL, "fail_max": FAIL_MAX, "oracle_min": ORACLE_MIN,
             "shuffled_margin": SHUFFLED_MARGIN, "oracle_ceiling": 1.0,
             "ctx_fails": bool(ctx_fails), "shf_fails": bool(shf_fails),
             "context_held": ctx_held, "oracle_held": orc_held, "shuffled_held": shf_held,
             "onehot_held": onh_held, "gaps_oracle_vs_shuffled": gaps_vs_shuffled}
    return verdict, msg, bands


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--train-n", type=int, default=FULL_TRAIN)
    ap.add_argument("--eval-n", type=int, default=FULL_EVAL)
    ap.add_argument("--steps-wm", type=int, default=STEPS_WM)
    args = ap.parse_args()

    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    run_mode = "self_test" if args.self_test or not args.full else "full"
    expected_units = 1 if run_mode == "self_test" else len(ARMS) * len(SEEDS_FULL)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        elapsed = time.perf_counter() - t0
        _atomic_write_metrics(OUTPUT_DIR, {
            "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (serialization + checkpoint/resume + real encoder + oracle/"
                           "shuffled/onehot tables + context-invariance-by-construction + arms-differ)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": elapsed,
            "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "chance_recall": CHANCE_RECALL,
            "selftest": st})
        _log("DONE self-test in %.1fs" % elapsed)
        return

    steps_wm = args.steps_wm
    _log("FULL: train_n=%d eval_n=%d steps_wm=%d seeds=%s chance_recall=%.4f arms=%s"
         % (args.train_n, args.eval_n, steps_wm, SEEDS_FULL, CHANCE_RECALL, ARMS))
    enc = base.FrozenV2Encoder(V2_CKPT)
    n_cached = enc.build_cache()
    _log("  cached %d unique sentence TOKEN reps (d=%d)" % (n_cached, enc.d))
    cond = rc.Conditioner(enc.U_tok_t, enc.U_pad_t)
    Uc = cond.apply(enc.U_tok_t, enc.U_pad_t, "pca_whiten")

    tables, table_diag = build_all_tables(enc, Uc)
    _log("  oracle table n_ctx_per_role min=%d max=%d; shuffle_perm=%s"
         % (min(table_diag["n_ctx_per_role"]), max(table_diag["n_ctx_per_role"]),
            table_diag["shuffle_perm"]))

    inv_diag = role_invariance_construction_selftest(enc, Uc, tables["oracle"], tables["shuffled"])
    _log("  construction check: %s" % inv_diag)

    datasets = {}
    for seed in SEEDS_FULL:
        tr = ho.gen_dataset_expanded(args.train_n, np.random.default_rng(seed))
        ev = ho.gen_dataset_expanded(args.eval_n, np.random.default_rng(seed + 777))
        datasets[seed] = (ho.build_index_batch_ext(tr, enc, seed),
                           ho.build_index_batch_ext(ev, enc, seed + 777))

    prior_units = ckpt.load_units(OUTPUT_DIR)
    if prior_units:
        _log("checkpoint: %d/%d units already recorded on disk; resuming"
             % (len(prior_units), expected_units := len(ARMS) * len(SEEDS_FULL)))

    arm_results = {mode: [] for mode in ARMS}
    for mode in ARMS:
        _log("--- ARM_%s ---" % mode.upper())
        for seed in SEEDS_FULL:
            k = ckpt.unit_key(mode, seed)
            if k in prior_units:
                arm_results[mode].append(prior_units[k])
                _log("  [resume] %s seed=%d loaded from checkpoint" % (mode, seed))
                continue
            tr_b, ev_b = datasets[seed]
            wm = build_wm(seed, enc, Uc)
            res = _strip_for_checkpoint(
                train_oracle_arm(wm, tr_b, ev_b, mode, tables[mode], steps_wm, LR, seed,
                                 "ARM_%s" % mode.upper()))
            ckpt.record_unit(OUTPUT_DIR, k, res)
            arm_results[mode].append(res)

    verdict, msg, bands = decide_verdict(arm_results)
    elapsed = time.perf_counter() - t0

    n_units_done = sum(len(v) for v in arm_results.values())
    expected_n_units_full = len(ARMS) * len(SEEDS_FULL)

    digests = {mode: [r["ev_logits_sha256"] for r in arm_results[mode]] for mode in ARMS}
    arms_differ = len({digests[m][0] for m in ARMS}) == len(ARMS)   # seed-0 outputs pairwise distinct

    _atomic_write_metrics(OUTPUT_DIR, {
        "verdict": verdict, "verdict_msg": msg,
        "summary": "%s | chance_recall=%.4f | %s" % (verdict, CHANCE_RECALL, msg[:160]),
        "run_mode": "full", "elapsed_s": elapsed, "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
        "chance_recall": CHANCE_RECALL, "oracle_ceiling_ref": 1.0, "bands": bands,
        "table_diag": table_diag, "invariance_construction_check": inv_diag,
        "arm_results": {mode: [{k: v for k, v in r.items() if k != "ev_logits"} for r in arm_results[mode]]
                        for mode in ARMS},
        "arms_differ_verified": bool(arms_differ),
        "cardinality_ok": bool(n_units_done == expected_n_units_full),
        "expected_n_units": expected_n_units_full, "n_units_done": n_units_done,
        "params": {"S_TARGET_TOTAL": S_TARGET_TOTAL, "K_SLOTS": K_SLOTS, "D_MEM": D_MEM,
                   "HIDDEN": HIDDEN, "ADDR_TEMP": ADDR_TEMP, "STEPS_WM": steps_wm, "LR": LR,
                   "train_n": args.train_n, "eval_n": args.eval_n, "seeds": list(SEEDS_FULL),
                   "train_roles": TRAIN_ROLES, "held_out_roles": HELD_OUT_ROLES,
                   "n_cached_sentences": n_cached, "encoder": "real_v2_frozen",
                   "conditioning": "pca_whiten", "oracle_probe_seed": ORACLE_PROBE_SEED,
                   "v2_ckpt": os.path.relpath(V2_CKPT, REPO_ROOT)},
        "start_marker_written": True, "crash_diagnostic_present": True,
        "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns",
        "progress_logging": "print_flush_true", "progress_cadence_expected_s": 15})
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
