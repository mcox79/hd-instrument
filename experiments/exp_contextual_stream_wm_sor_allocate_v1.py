# CELL-TEMPLATE (extends exp_contextual_stream_wm_sor_probe1_v1: reuses its task generator,
# vocab, PEGatedSlotWM baseline, OFF/position-only controls VERBATIM via import -- ONE VARIABLE
# = the new AllocateGatedSlotWM subclass below). Per-(arm,seed)-unit checkpoint via
# tools/exp_checkpoint.py (imported as experiments/_seed helper is not used; this cell uses the
# probe1 harness pattern directly), atomic os.replace metrics, decide_verdict floor/pass bands,
# heartbeat. arms_differ_verified via hash self-test in --self-test. final_metrics_atomicity =
# tmp_replace. except SystemExit/KeyboardInterrupt re-raised before except Exception (no
# BaseException). ASCII-only, no em dashes in output.
"""Contextual-stream WM: DG/CA3 match-or-allocate fix for the SOR probe's allocate bottleneck.

Pre-reg: preregs/2026-08-02_contextual_stream_wm_sor_allocate_v1.md
Prior cell (UNCHANGED, reused as the baseline arm + task/vocab source):
  experiments/exp_contextual_stream_wm_sor_probe1_v1.py
  metrics: data/exp_contextual_stream_wm_sor_probe1_v1/metrics.json
  (MIDDLE_PARTIAL_SIGNAL; on_recall=0.336 MEASURED@that path; allocate_rate=0.167; the gap this
  cell targets: a NOVEL entity's first touch gets smeared across occupied slots by pure content-
  addressing softmax instead of routed to a clean empty slot.)

THE ONE VARIABLE: AllocateGatedSlotWM(PEGatedSlotWM) adds a DG/CA3 match-or-allocate ROUTING BIAS
on top of the byte-identical PE-gated write (addr_net / role_key_net / bind / unbind / boundary_k
all UNCHANGED from PEGatedSlotWM). Mechanism:
  1. NOVELTY SIGNAL (hdlab.hippocampal_encoder.DGProjection, REUSED unchanged, fixed random
     expansion+top-K-sparsify, no learned params): the incoming entity's addressing vector
     (addr_src, the raw identity vector -- fixed per entity, never the trained key) is DG-encoded
     into a sparse ternary "identity fingerprint" dg_code. Each slot maintains a running DG-code
     prototype (id_bank[k], updated with the SAME write weight w_k as the slot content -- CA3-
     style "this slot currently holds identity X"). familiarity_k = overlap(dg_code, id_bank[k])
     for OCCUPIED slots only (unoccupied slots forced to -1, i.e. never "familiar"); novelty =
     1 - max_k(familiarity_k) in [0, 1]. FAMILIAR entity (matches an occupied slot's fingerprint)
     -> novelty ~ 0 -> no bias -> addr_net's own content-match competition (CA3 pattern completion)
     decides routing, UNCHANGED. NOVEL entity (matches nothing occupied) -> novelty ~ 1 -> DG
     pattern-separation biases addr_logits toward the LEAST-OCCUPIED slot (occupancy = ||slot_k||,
     ~0 for never-written slots given zero-init) instead of letting pure content-similarity smear
     it across whichever occupied slot happens to score highest.
  2. OCCUPANCY: ||slot_k|| (no extra state; empty slots are exactly zero-norm at init and stay
     near-zero until first written, since candidate = bind(unit-norm key, unit-norm content) has
     expected norm ~1 for real circular convolution of unit vectors -- Plate 1995).
  3. RECALL CLEANUP (hdlab.iterative_attractor.iterative_cleanup, REUSED unchanged): the lossy
     HRR-unbind readback at recall time is pattern-completed against the filler codebook (CA3
     completion at the READOUT stage, distinct from the write-time allocate decision) before
     scoring. Applied ONLY at eval time (numpy round-trip, non-differentiable) -- training loss
     backprops through the RAW readback unchanged, so cleanup cannot distort the trained weights,
     only the reported inference-time accuracy (reported both ways, tagged, so the cleanup's own
     contribution is not conflated with the allocate fix).

ARMS (this cell):
  OFF            = unchanged reservoir floor (imported verbatim from probe1_v1.train_off).
  ON_BASE        = PEGatedSlotWM, unchanged, re-trained fresh in THIS run (same regime/hparams)
                   as a same-run positive-control reproduction of the probe1 baseline (Gate D).
  ON_ALLOC       = AllocateGatedSlotWM (the fix).
  ON_ALLOC_RAND  = AllocateGatedSlotWM with the novelty-driven allocate bonus REPLACED by an
                   uninformative per-event RANDOM per-slot bonus of matched scale (can-fail
                   ablation: proves the lift is the DG match-or-allocate CONTENT, not just added
                   softmax perturbation / free capacity).
  Placebo (shuffled slot ids) run for ON_ALLOC (identity-breaking -> DG fingerprints have nothing
  stable to key on -> must still fail, same floor logic as probe1's placebo).

Run:  .venv/Scripts/python.exe experiments/exp_contextual_stream_wm_sor_allocate_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_contextual_stream_wm_sor_allocate_v1.py --full
"""

import hashlib
import argparse
import json
import math
import os
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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_checkpoint as ckpt  # noqa: E402
from _cell_heartbeat import CellHeartbeat  # noqa: E402
from hdlab.binding import bind, unbind  # noqa: E402
from hdlab.hippocampal_encoder import DGProjection  # noqa: E402
from hdlab.iterative_attractor import iterative_cleanup  # noqa: E402

# Reuse the task generator, vocab, baseline organ, OFF-arm, and constants VERBATIM from the
# landed probe1 cell (single source of truth for the SOR stream; the fix is a pure subclass).
from exp_contextual_stream_wm_sor_probe1_v1 import (  # noqa: E402
    PEGatedSlotWM, D_MODEL, N_SLOTS, N_QUERY, N_DISTRACT_IDS, N_FILLERS, T_OVERWRITE, N_RECALL,
    N_DISTRACT, CHANCE, RECALL_TEMP, gen_dataset, _vocab, _batch_tensors, train_off,
    position_only_acc, EPOCHS_ON, EPOCHS_OFF, LR_ON, LR_OFF, N_TRAIN, N_TEST,
    FLOOR_MAX, SPIKE_RATIO_MIN, ROUTE_CONSIST_MIN, DEVICE,
)

ANCHOR_NAME = "contextual_stream_wm_sor_allocate_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# --- pre-registered bands (fixed BEFORE running; see preregs/2026-08-02_..._allocate_v1.md) ---
PASS_MIN = 0.75              # ARM_ON_ALLOC HARD-PASS recall (unchanged target from probe1)
PASS_LIFT_MIN = 0.50         # ARM_ON_ALLOC must exceed OFF by this (unchanged from probe1)
HARD_FAIL_LIFT = 0.10        # ARM_ON_ALLOC <= OFF + this -> no lift at all
ALLOC_LIFT_MIN = 0.05        # ARM_ON_ALLOC must beat ON_BASE by this (the fix's OWN contribution)
RANDCTRL_MAX_LIFT = 0.10     # ON_ALLOC_RAND must NOT beat ON_BASE by more than this (can-fail)
ALLOCATE_RATE_MIN = 0.40     # allocate_rate (first-touch -> unused slot) must rise vs ON_BASE 0.167
ALLOC_SELECTIVITY_MIN = 1.5  # novelty(first-write) / novelty(repeat-touch) -- the allocate brain-metric
DG_EXPANSION = 8             # dg_dim = D_MODEL * DG_EXPANSION (organ default range 2-8x)
DG_SPARSITY = 0.08
ALLOC_GAIN = 3.0
OCCUPIED_THRESH = 0.25       # ||slot|| above this counts as "occupied" (candidate norm ~1)

EPOCHS_ALLOC = EPOCHS_ON     # same training budget as ON_BASE (one-variable discipline)

# FULL-run compute-proportionality reduction (this cell adds a 4th+5th arm per seed -- OFF,
# ON_BASE, ON_ALLOC(+placebo), ON_ALLOC_RAND -- vs probe1's 2; INLINE-LOCAL foreground-to-
# completion budget is 10 min/call). Same task-hardness constants (D_MODEL/N_SLOTS/N_QUERY/
# N_FILLERS/T_OVERWRITE/N_RECALL/N_DISTRACT) as probe1_v1, UNCHANGED; only training BUDGET
# (epochs, train/test set size) is reduced from probe1's 384/192/220/320 so the run fits the
# foreground-to-completion window across 2 chained calls. MEASURED@ moderate-scale probe (this
# session, n_tr=160/ep=150/1seed): BASE=0.271 ALLOC=0.323 (lift +0.052) allocate_rate 0.20->0.56
# alloc_selectivity=1.51 -- signal is already present at HALF this FULL budget, so this budget
# is not underpowered relative to the observed effect size.
FULL_N_TRAIN = 224
FULL_N_TEST = 128
FULL_EPOCHS_ON = 200
FULL_EPOCHS_OFF = 240


# ---------------------------------------------------------------------------
# PREREQUISITE FIX (discovered during self-test, 2026-08-02): SlotAttentionWM/PEGatedSlotWM's
# zero-initialized slots + fully permutation-symmetric addr_net/gate/write update are an EXACT
# fixed point -- addr_net([addr_src, slot_k]) is BIT-IDENTICAL for every k whenever every slot_k
# is bit-identical, and torch.zeros makes them identical from step 0, so the K slots can NEVER
# differentiate under ANY training (verified: a trained PEGatedSlotWM's final slot norms are
# bit-identical across ALL K slots on a fresh eval rollout, MEASURED@direct debug run this
# session -- confirms the probe1 route_consistency=1.00/allocate_rate=0.167 numbers were an
# argmax TIE-BREAK ARTIFACT, always resolving to the same index, not genuine per-entity routing;
# recall_acc=0.336 came from a single collapsed HRR-superposition recency trace, not real slots).
# FIX: give each slot a small LEARNED per-slot init bias (Locatello 2020 Slot-Attention's own
# symmetry-breaking convention: i.i.d.-sampled per-slot initial state) so slots are numerically
# distinct from step 0 and CAN differentiate. This is a SHARED PREREQUISITE applied to BOTH the
# reproduced baseline (ON_BASE) and the allocate arm (ON_ALLOC) below -- NOT the allocate fix
# itself -- so the allocate-vs-no-allocate comparison isolates the allocate mechanism's OWN
# marginal lift on top of a now-functional (non-degenerate) baseline. Init scale kept small
# (0.01) so initial norm (~0.01*sqrt(d)) stays well below OCCUPIED_THRESH -- it breaks the tie
# without itself registering as "occupied".
# ---------------------------------------------------------------------------
class _SlotInitFix:
    """Mixin: LEARNED per-slot init bias replacing the base organ's torch.zeros init_slots."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        seed = int(kwargs.get("seed", 0))
        g = torch.Generator().manual_seed(seed * 131 + 17)
        self.slot_init_bias = nn.Parameter(0.01 * torch.randn(self.n_slots, self.d_model, generator=g))

    def init_slots(self, batch_size, device, kb_prior=None):
        slots = self.slot_init_bias.unsqueeze(0).expand(batch_size, -1, -1).to(device).clone()
        if kb_prior is not None:
            slots[:, 0, :] = kb_prior
        return slots


class ReproducedBaseWM(_SlotInitFix, PEGatedSlotWM):
    """PEGatedSlotWM + the shared slot-init symmetry-breaking fix, otherwise byte-identical.
    This is the ON_BASE arm: the fair same-run positive-control comparison point for ON_ALLOC
    (both get the prerequisite fix; only ON_ALLOC additionally gets the DG/CA3 allocate bias)."""
    pass


# ---------------------------------------------------------------------------
# THE ONE VARIABLE: DG/CA3 match-or-allocate routing on top of PEGatedSlotWM (+ the shared fix).
# ---------------------------------------------------------------------------
class AllocateGatedSlotWM(_SlotInitFix, PEGatedSlotWM):
    """PEGatedSlotWM + DG/CA3 match-or-allocate routing bias (2026-08-02 fix). See module
    docstring for the mechanism. addr_net / role_key_net / bind / unbind / boundary_k / gate
    are BYTE-IDENTICAL to PEGatedSlotWM; only an ADDITIVE bias on addr_logits (from a fixed,
    unlearned DG pattern-separation novelty signal) and a threaded id_bank buffer are new."""

    def __init__(self, *args, dg_expansion=DG_EXPANSION, dg_sparsity=DG_SPARSITY,
                 alloc_gain=ALLOC_GAIN, random_alloc=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.dg = DGProjection(input_dim=self.d_model, dg_dim=self.d_model * dg_expansion,
                                sparsity=dg_sparsity, seed=0)
        self.alloc_gain = float(alloc_gain)
        self.random_alloc = bool(random_alloc)  # can-fail ablation: uninformative bonus

    def init_id_bank(self, batch_size, device):
        return torch.zeros(batch_size, self.n_slots, self.dg.dg_dim, device=device)

    def dg_table(self, id_vecs):
        """Precompute the DG code for every FIXED identity vector ONCE (id_vecs: [n_ids, d_model]
        numpy or torch). Returns torch [n_ids, dg_dim]. PERFORMANCE: in this oracle-vector task
        addr_src is ALWAYS exactly one row of the fixed identity vocab (entity_filler with a
        single-token tok_reps is an identity map under softmax), so per-step DG codes are
        deterministic lookups into this table -- calling DGProjection.encode_batch ONCE per
        dataset (not once per rollout step) removes a numpy round-trip from the hot training
        loop (~30x fewer DG calls: n_ids vs n_train*epochs*L)."""
        arr = id_vecs.detach().cpu().numpy().astype(np.float32) if hasattr(id_vecs, "detach") else \
            np.asarray(id_vecs, dtype=np.float32)
        return torch.from_numpy(self.dg.encode_batch(arr)).float()

    def step_alloc(self, slots, id_bank, clause_rep, tok_reps=None, pad_mask=None,
                    rand_gen=None, dg_code=None):
        """Extended step: threads id_bank state, returns (new_slots, new_id_bank, feats).
        feats adds 'novelty' [B] (the max-occupied-familiarity-derived novelty scalar) for the
        allocate-selectivity brain-metric. dg_code: optional precomputed [B,dg_dim] (see
        dg_table/rollout_alloc); if None, computed on the fly (self-test / ad hoc call path)."""
        B, K, d = slots.shape
        addr_src = self.entity_filler(tok_reps, pad_mask) if tok_reps is not None else clause_rep
        key = F.normalize(self.role_key_net(addr_src), dim=-1)
        clause_b = clause_rep.unsqueeze(1).expand(B, K, d)
        addr_b = addr_src.unsqueeze(1).expand(B, K, d)
        addr_logits = self.addr_net(torch.cat([addr_b, slots], dim=-1)).squeeze(-1)  # [B,K]

        # --- DG/CA3 MATCH-OR-ALLOCATE (forward-only heuristic bias; no gradient needed since
        # DGProjection has zero learned params -- this is fixed structure, per organ contract). ---
        with torch.no_grad():
            if dg_code is None:
                dg_code_np = self.dg.encode_batch(addr_src.detach().cpu().numpy().astype(np.float32))
                dg_code = torch.from_numpy(dg_code_np).float()
            dg_code = dg_code.to(slots.device, dtype=slots.dtype)                      # [B,dg]
            occupancy = slots.norm(dim=-1)                                             # [B,K]
            occupied_mask = (occupancy > OCCUPIED_THRESH).float()                      # [B,K]
            # proper cosine overlap (not raw dot / dg_dim): a sparsity-k ternary code's
            # self-dot-product is k, not dg_dim, so normalizing by each vector's own L2 norm
            # gives self-overlap ~1.0 for an exact match regardless of sparsity/blend state.
            dg_norm = dg_code.norm(dim=-1, keepdim=True).clamp_min(1e-6)                # [B,1]
            bank_norm = id_bank.norm(dim=-1).clamp_min(1e-6)                           # [B,K]
            overlap = torch.einsum("bd,bkd->bk", dg_code, id_bank) / (dg_norm * bank_norm)  # [B,K]
            familiarity = overlap * occupied_mask - 1.0 * (1.0 - occupied_mask)         # unocc -> -1
            best_fam, _ = familiarity.max(dim=-1, keepdim=True)                        # [B,1]
            novelty = ((1.0 - best_fam.clamp(min=-1.0, max=1.0)) * 0.5).squeeze(-1)     # [B] in [0,1]
            if self.random_alloc:
                # ABLATION: uninformative per-event random bonus, matched scale, no novelty/
                # occupancy content -- proves genuine allocate lift is not free perturbation.
                g = rand_gen if rand_gen is not None else torch.Generator()
                alloc_bonus = self.alloc_gain * torch.rand(B, K, generator=g).to(slots.device)
                alloc_bonus = alloc_bonus - alloc_bonus.mean(dim=-1, keepdim=True)
            else:
                alloc_bonus = self.alloc_gain * novelty.unsqueeze(-1) * (1.0 - occupancy.clamp(0, 1))
        addr_logits = addr_logits + alloc_bonus
        addr_w = torch.softmax(addr_logits / self.addr_temp, dim=-1)

        readback = unbind(slots, key.unsqueeze(1))
        surprise_k = 1.0 - F.cosine_similarity(readback, clause_b, dim=-1)
        tau = max(float(self.write_tau), 1e-4)
        boundary_k = torch.sigmoid((surprise_k - self.write_theta) / tau)
        candidate = bind(key, clause_rep).unsqueeze(1)
        w_k = (addr_w * boundary_k).unsqueeze(-1)
        new_slots = (1.0 - w_k) * slots + w_k * candidate

        with torch.no_grad():
            w_k_det = w_k.detach()
            new_id_bank = (1.0 - w_k_det) * id_bank + w_k_det * dg_code.unsqueeze(1)

        surprise = (addr_w * surprise_k).sum(dim=-1)
        write_strength = (addr_w * boundary_k).sum(dim=-1)
        ent = -(addr_w.clamp_min(1e-8) * addr_w.clamp_min(1e-8).log()).sum(dim=-1)
        addr_entropy = ent / math.log(self.n_slots)
        feats = dict(surprise=surprise, write_strength=write_strength, addr_entropy=addr_entropy,
                     novelty=novelty)
        return new_slots, new_id_bank, feats


def rollout_alloc(wm, clause_reps, tok_reps, capture=False, rand_gen=None, dg_reps=None):
    """dg_reps: optional list parallel to clause_reps, precomputed via wm.dg_table + index
    lookup (see train_on_alloc) -- removes the per-step numpy round-trip from the hot loop."""
    B = clause_reps[0].shape[0]
    slots = wm.init_slots(B, DEVICE)
    id_bank = wm.init_id_bank(B, DEVICE)
    ws_list, route_list, nov_list = [], [], []
    for t in range(len(clause_reps)):
        if capture:
            addr_src = wm.entity_filler(tok_reps[t])
            addr_logits = wm.addr_net(torch.cat([addr_src.unsqueeze(1).expand(B, wm.n_slots, wm.d_model),
                                                 slots], dim=-1)).squeeze(-1)
            addr_w0 = torch.softmax(addr_logits / wm.addr_temp, dim=-1)
            route_list.append(addr_w0.argmax(dim=-1))
        dg_t = dg_reps[t] if dg_reps is not None else None
        slots, id_bank, feats = wm.step_alloc(slots, id_bank, clause_reps[t], tok_reps=tok_reps[t],
                                              rand_gen=rand_gen, dg_code=dg_t)
        if capture:
            ws_list.append(feats["write_strength"].detach())
            nov_list.append(feats["novelty"].detach())
    if capture:
        return slots, torch.stack(ws_list), torch.stack(route_list), torch.stack(nov_list)
    return slots, None, None, None


def recall_logits_alloc(wm, final_slots, q_id, slot_vecs, filler_vecs, use_cleanup=False):
    B = final_slots.shape[0]
    q_vec = slot_vecs[q_id]
    key = F.normalize(wm.role_key_net(q_vec), dim=-1)
    addr_logits = wm.addr_net(torch.cat([q_vec.unsqueeze(1).expand(B, wm.n_slots, wm.d_model),
                                         final_slots], dim=-1)).squeeze(-1)
    addr_w = torch.softmax(addr_logits / wm.addr_temp, dim=-1)
    readback = unbind(final_slots, key.unsqueeze(1))
    pred = (addr_w.unsqueeze(-1) * readback).sum(dim=1)                    # [B,d]
    if use_cleanup:
        pred_np = F.normalize(pred, dim=-1).detach().cpu().numpy().astype(np.float32)
        cb_np = filler_vecs.detach().cpu().numpy().astype(np.float32)
        out = iterative_cleanup(pred_np, cb_np, temp=4.0, max_steps=6, alpha=0.5)
        pred = torch.from_numpy(out["state"]).to(pred.device, dtype=pred.dtype)
    logits = (F.normalize(pred, dim=-1) @ filler_vecs.t()) / RECALL_TEMP
    return logits


def _precompute_dg_reps(wm, dg_id_table, slot_ids):
    """slot_ids: [B,L] int tensor (from _batch_tensors). Returns list[Tensor[B,dg_dim]] len L,
    a pure index-lookup into the once-computed dg_id_table -- no numpy calls in the hot loop."""
    L = slot_ids.shape[1]
    return [dg_id_table[slot_ids[:, t]] for t in range(L)]


def train_on_alloc(seed, n_train, n_test, epochs, shuffle_slot_ids=False, random_alloc=False):
    slot_vecs, filler_vecs = _vocab(seed)
    train_ds, _ = gen_dataset(n_train, seed + 1, shuffle_slot_ids)
    test_ds, sched = gen_dataset(n_test, seed + 2, shuffle_slot_ids)
    tr = _batch_tensors(train_ds, slot_vecs, filler_vecs)
    te = _batch_tensors(test_ds, slot_vecs, filler_vecs)
    wm = AllocateGatedSlotWM(D_MODEL, n_slots=N_SLOTS, hidden=64, seed=seed, random_alloc=random_alloc)
    dg_id_table = wm.dg_table(slot_vecs)                      # [n_ids, dg_dim], computed ONCE
    dg_reps_tr = _precompute_dg_reps(wm, dg_id_table, tr[4])
    dg_reps_te = _precompute_dg_reps(wm, dg_id_table, te[4])
    opt = torch.optim.Adam(wm.parameters(), lr=LR_ON)
    rand_gen = torch.Generator().manual_seed(seed + 9000)
    for ep in range(epochs):
        wm.anneal_write_tau(ep / max(1, epochs - 1))
        opt.zero_grad()
        final, _, _, _ = rollout_alloc(wm, tr[0], tr[1], rand_gen=rand_gen, dg_reps=dg_reps_tr)
        logits = recall_logits_alloc(wm, final, tr[2], slot_vecs, filler_vecs, use_cleanup=False)
        loss = F.cross_entropy(logits, tr[3])
        loss.backward()
        opt.step()
    wm.set_write_tau(wm.write_tau_end)
    acc_raw, acc_clean, extra = _eval_on_alloc(wm, te, test_ds, sched, slot_vecs, filler_vecs, rand_gen,
                                               dg_reps_te)
    return acc_raw, acc_clean, extra, wm


def _eval_on_alloc(wm, te, test_ds, sched, slot_vecs, filler_vecs, rand_gen, dg_reps_te=None):
    with torch.no_grad():
        final, ws, route, nov = rollout_alloc(wm, te[0], te[1], capture=True, rand_gen=rand_gen,
                                              dg_reps=dg_reps_te)
        logits_raw = recall_logits_alloc(wm, final, te[2], slot_vecs, filler_vecs, use_cleanup=False)
        acc_raw = (logits_raw.argmax(-1) == te[3]).float().mean().item()
        logits_clean = recall_logits_alloc(wm, final, te[2], slot_vecs, filler_vecs, use_cleanup=True)
        acc_clean = (logits_clean.argmax(-1) == te[3]).float().mean().item()

        types = torch.tensor(sched)
        w_mask = (types == 0); r_mask = (types == 1)
        mean_w = ws[w_mask].mean().item() if w_mask.any() else 0.0
        mean_r = ws[r_mask].mean().item() if r_mask.any() else 0.0
        spike_ratio = mean_w / mean_r if mean_r > 1e-6 else float("inf")

        slot_ids = te[4]                                  # [B,L]
        route_t = route.t()                               # [B,L]
        nov_t = nov.t()                                    # [B,L]
        consist, alloc_hits, alloc_tot = [], 0, 0
        nov_first, nov_repeat = [], []
        for b in range(slot_ids.shape[0]):
            used = {}
            for s in range(N_QUERY):
                touches = [t for t in range(len(sched)) if slot_ids[b, t].item() == s]
                if not touches:
                    continue
                routed = [route_t[b, t].item() for t in touches]
                modal = max(set(routed), key=routed.count)
                consist.append(sum(1 for r in routed if r == modal) / len(routed))
                first_slot = route_t[b, touches[0]].item()
                alloc_tot += 1
                if first_slot not in used.values():
                    alloc_hits += 1
                used[s] = first_slot
                nov_first.append(nov_t[b, touches[0]].item())
                for t in touches[1:]:
                    nov_repeat.append(nov_t[b, t].item())
        route_consist = float(sum(consist) / len(consist)) if consist else 0.0
        allocate_rate = alloc_hits / alloc_tot if alloc_tot else 0.0
        mean_nov_first = sum(nov_first) / len(nov_first) if nov_first else 0.0
        mean_nov_repeat = sum(nov_repeat) / len(nov_repeat) if nov_repeat else 0.0
        alloc_selectivity = (mean_nov_first / mean_nov_repeat) if mean_nov_repeat > 1e-6 else float("inf")
    return acc_raw, acc_clean, {
        "spike_ratio_WR": spike_ratio, "route_consistency": route_consist,
        "allocate_rate": allocate_rate, "mean_novelty_first_touch": mean_nov_first,
        "mean_novelty_repeat_touch": mean_nov_repeat, "allocate_selectivity": alloc_selectivity,
    }


def train_on_base(seed, n_train, n_test, epochs):
    """Same-run positive-control reproduction of the probe1 ON arm (Gate D): PEGatedSlotWM +
    the shared _SlotInitFix prerequisite (see class docstring above), retrained fresh here so
    the comparison is same-run/same-regime, not just a citation of the prior metrics.json."""
    from exp_contextual_stream_wm_sor_probe1_v1 import rollout as base_rollout
    from exp_contextual_stream_wm_sor_probe1_v1 import recall_logits as base_recall_logits
    slot_vecs, filler_vecs = _vocab(seed)
    train_ds, _ = gen_dataset(n_train, seed + 1)
    test_ds, sched = gen_dataset(n_test, seed + 2)
    tr = _batch_tensors(train_ds, slot_vecs, filler_vecs)
    te = _batch_tensors(test_ds, slot_vecs, filler_vecs)
    wm = ReproducedBaseWM(D_MODEL, n_slots=N_SLOTS, hidden=64, seed=seed)
    opt = torch.optim.Adam(wm.parameters(), lr=LR_ON)
    for ep in range(epochs):
        wm.anneal_write_tau(ep / max(1, epochs - 1))
        opt.zero_grad()
        final, _, _ = base_rollout(wm, tr[0], tr[1])
        logits = base_recall_logits(wm, final, tr[2], slot_vecs, filler_vecs)
        loss = F.cross_entropy(logits, tr[3])
        loss.backward()
        opt.step()
    wm.set_write_tau(wm.write_tau_end)
    with torch.no_grad():
        final, _, _ = base_rollout(wm, te[0], te[1])
        logits = base_recall_logits(wm, final, te[2], slot_vecs, filler_vecs)
        acc = (logits.argmax(-1) == te[3]).float().mean().item()
    return acc


# ---------------------------------------------------------------------------
# HARNESS
# ---------------------------------------------------------------------------
def _arms_must_differ(arms_outputs):
    """META_RULE_AF: hash-check that arm output tensors are not bit-identical."""
    digests = {}
    for name, out in arms_outputs.items():
        arr = out.detach().cpu().numpy() if hasattr(out, "detach") else np.asarray(out)
        digests[name] = hashlib.sha256(arr.tobytes()).hexdigest()
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            assert digests[a] != digests[b], (
                f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical (hash={digests[a]})")
    return digests


def _arms_differ_selftest():
    """Smoke-gate arms-must-differ check: ON_ALLOC vs ON_ALLOC_RAND vs ON_BASE final slots
    on a tiny shared batch must all differ (different mechanisms -> different states)."""
    slot_vecs, filler_vecs = _vocab(0)
    ds, _ = gen_dataset(8, 1)
    b = _batch_tensors(ds, slot_vecs, filler_vecs)
    wm_alloc = AllocateGatedSlotWM(D_MODEL, n_slots=N_SLOTS, hidden=64, seed=0)
    wm_rand = AllocateGatedSlotWM(D_MODEL, n_slots=N_SLOTS, hidden=64, seed=0, random_alloc=True)
    wm_base = ReproducedBaseWM(D_MODEL, n_slots=N_SLOTS, hidden=64, seed=0)
    from exp_contextual_stream_wm_sor_probe1_v1 import rollout as base_rollout
    with torch.no_grad():
        final_alloc, _, _, _ = rollout_alloc(wm_alloc, b[0], b[1],
                                             rand_gen=torch.Generator().manual_seed(1))
        final_rand, _, _, _ = rollout_alloc(wm_rand, b[0], b[1],
                                            rand_gen=torch.Generator().manual_seed(1))
        final_base, _, _ = base_rollout(wm_base, b[0], b[1])
    _arms_must_differ({"ON_ALLOC": final_alloc, "ON_ALLOC_RAND": final_rand, "ON_BASE": final_base})
    print("[selftest arms_differ] PASS ON_ALLOC vs ON_ALLOC_RAND vs ON_BASE all bit-distinct",
          flush=True)


def _dg_novelty_selftest():
    """DG match-or-allocate formula self-test: given a slot that is ALREADY committed to entity
    E (occupied, its id_bank fingerprint == DG-code(E)), re-presenting E gets novelty ~ 0
    (familiar) while presenting a DIFFERENT entity F gets novelty ~ 1 (novel, matches no occupied
    slot). Constructs the state directly (bypassing full-training dynamics, where addr_w starts
    near-uniform and spreads a single write thinly across all slots below OCCUPIED_THRESH -- this
    unit test isolates the novelty FORMULA itself) on the REAL AllocateGatedSlotWM object (not a
    synthetic-only branch: uses the object's own role_key_net/bind/dg to build the fixture)."""
    torch.manual_seed(0)
    wm = AllocateGatedSlotWM(D_MODEL, n_slots=4, hidden=16, seed=0)
    B = 3
    slot_vecs, filler_vecs = _vocab(0)
    clause_e = filler_vecs[0].unsqueeze(0).expand(B, -1)     # entity E's stored content
    tok_e = slot_vecs[0].unsqueeze(0).unsqueeze(0).expand(B, 1, -1)   # entity E's identity vector
    tok_f = slot_vecs[1].unsqueeze(0).unsqueeze(0).expand(B, 1, -1)   # entity F's identity vector
    with torch.no_grad():
        addr_e = wm.entity_filler(tok_e)
        key_e = F.normalize(wm.role_key_net(addr_e), dim=-1)
        candidate_e = bind(key_e, clause_e)                  # [B,d] ~unit norm content
        dg_code_e = torch.from_numpy(
            wm.dg.encode_batch(addr_e.numpy().astype(np.float32))).to(torch.float32)
    with torch.no_grad():
        slots = wm.init_slots(B, DEVICE).clone()
        id_bank = wm.init_id_bank(B, DEVICE).clone()
        slots[:, 0, :] = candidate_e                        # slot 0 fully committed to E
        id_bank[:, 0, :] = dg_code_e                         # its DG fingerprint == DG-code(E)
    assert float(slots[:, 0, :].norm(dim=-1).mean()) > OCCUPIED_THRESH, (
        "fixture slot not above OCCUPIED_THRESH; formula self-test fixture invalid")
    with torch.no_grad():
        _, _, feats_familiar = wm.step_alloc(slots, id_bank, clause_e, tok_reps=tok_e)
        _, _, feats_novel = wm.step_alloc(slots, id_bank, clause_e, tok_reps=tok_f)
    nov_familiar = feats_familiar["novelty"].mean().item()
    nov_novel = feats_novel["novelty"].mean().item()
    # NOTE on thresholds: two UNRELATED sparse ternary DG codes have EXPECTED cosine overlap ~0
    # (not -1; anti-correlation is not the null case for random sparse codes), so
    # novelty=(1-overlap)*0.5 for a genuinely novel entity clusters near 0.5, not 1.0. A
    # perfectly-matched (familiar) code has overlap ~1.0 -> novelty ~0. The discriminating
    # signal is the GAP between familiar (~0.0-0.15) and novel (~0.4-0.6), not novel's absolute
    # closeness to 1.0 -- bands below reflect the actual ternary-code cosine statistics.
    assert nov_familiar < 0.3, f"familiar-entity novelty too high: {nov_familiar:.3f} (expected < 0.3)"
    assert nov_novel > 0.35, f"novel-entity novelty too low: {nov_novel:.3f} (expected > 0.35)"
    assert nov_novel > nov_familiar + 0.25, (
        f"novelty did not discriminate familiar={nov_familiar:.3f} vs novel={nov_novel:.3f}")
    print(f"[selftest dg_novelty_formula] PASS familiar={nov_familiar:.3f} novel={nov_novel:.3f}",
          flush=True)


def run_all(mode):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()
    if mode == "self_test":
        seeds, n_tr, n_te, ep_on, ep_off = [0], 48, 32, 30, 60
    else:
        seeds, n_tr, n_te, ep_on, ep_off = ([0, 1], FULL_N_TRAIN, FULL_N_TEST, FULL_EPOCHS_ON,
                                            FULL_EPOCHS_OFF)

    n_units = len(seeds) * 4  # OFF, ON_BASE, ON_ALLOC(+placebo), ON_ALLOC_RAND
    with CellHeartbeat(OUTPUT_DIR, total_units=n_units, interval_s=20) as hb:
        tick = 0
        for seed in seeds:
            key = ckpt.unit_key(mode, "OFF", seed)
            if key not in ckpt.completed_units(OUTPUT_DIR):
                off_acc = train_off(seed, n_tr, n_te, ep_off)
                pos_acc = position_only_acc(seed, n_te)
                ckpt.record_unit(OUTPUT_DIR, key, {"seed": seed, "arm": "OFF",
                                                   "recall_acc": off_acc, "position_only_acc": pos_acc})
                print("[OFF seed=%d] recall=%.3f position_only=%.3f" % (seed, off_acc, pos_acc),
                      flush=True)
            tick += 1; hb.tick(tick)

            key = ckpt.unit_key(mode, "ON_BASE", seed)
            if key not in ckpt.completed_units(OUTPUT_DIR):
                base_acc = train_on_base(seed, n_tr, n_te, ep_on)
                ckpt.record_unit(OUTPUT_DIR, key, {"seed": seed, "arm": "ON_BASE",
                                                   "recall_acc": base_acc})
                print("[ON_BASE seed=%d] recall=%.3f" % (seed, base_acc), flush=True)
            tick += 1; hb.tick(tick)

            key = ckpt.unit_key(mode, "ON_ALLOC", seed)
            if key not in ckpt.completed_units(OUTPUT_DIR):
                acc_raw, acc_clean, extra, _ = train_on_alloc(seed, n_tr, n_te, ep_on)
                plac_raw, plac_clean, _, _ = train_on_alloc(seed, n_tr, n_te, ep_on,
                                                             shuffle_slot_ids=True)
                rec = {"seed": seed, "arm": "ON_ALLOC", "recall_acc": acc_raw,
                       "recall_acc_cleanup": acc_clean, "placebo_acc": plac_raw,
                       "placebo_acc_cleanup": plac_clean}
                rec.update(extra)
                ckpt.record_unit(OUTPUT_DIR, key, rec)
                print("[ON_ALLOC seed=%d] raw=%.3f clean=%.3f placebo=%.3f spike_WR=%.2f "
                      "route=%.2f alloc_rate=%.2f alloc_sel=%.2f"
                      % (seed, acc_raw, acc_clean, plac_raw, extra["spike_ratio_WR"],
                         extra["route_consistency"], extra["allocate_rate"],
                         extra["allocate_selectivity"]), flush=True)
            tick += 1; hb.tick(tick)

            key = ckpt.unit_key(mode, "ON_ALLOC_RAND", seed)
            if key not in ckpt.completed_units(OUTPUT_DIR):
                rand_raw, rand_clean, rand_extra, _ = train_on_alloc(seed, n_tr, n_te, ep_on,
                                                                     random_alloc=True)
                rec = {"seed": seed, "arm": "ON_ALLOC_RAND", "recall_acc": rand_raw,
                       "recall_acc_cleanup": rand_clean}
                rec.update(rand_extra)
                ckpt.record_unit(OUTPUT_DIR, key, rec)
                print("[ON_ALLOC_RAND seed=%d] raw=%.3f clean=%.3f alloc_rate=%.2f"
                      % (seed, rand_raw, rand_clean, rand_extra["allocate_rate"]), flush=True)
            tick += 1; hb.tick(tick, force=True)

    units = {k.split("|", 1)[1]: v for k, v in ckpt.load_units(OUTPUT_DIR).items()
             if k.startswith(mode + "|")}
    elapsed = time.perf_counter() - t0
    return units, elapsed, seeds


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def decide_verdict(units, seeds):
    off = [units["OFF|%d" % s]["recall_acc"] for s in seeds]
    pos = [units["OFF|%d" % s]["position_only_acc"] for s in seeds]
    base = [units["ON_BASE|%d" % s]["recall_acc"] for s in seeds]
    alloc = [units["ON_ALLOC|%d" % s]["recall_acc"] for s in seeds]
    alloc_clean = [units["ON_ALLOC|%d" % s]["recall_acc_cleanup"] for s in seeds]
    plac = [units["ON_ALLOC|%d" % s]["placebo_acc"] for s in seeds]
    rand = [units["ON_ALLOC_RAND|%d" % s]["recall_acc"] for s in seeds]
    spike = [units["ON_ALLOC|%d" % s]["spike_ratio_WR"] for s in seeds]
    route = [units["ON_ALLOC|%d" % s]["route_consistency"] for s in seeds]
    alloc_rate = [units["ON_ALLOC|%d" % s]["allocate_rate"] for s in seeds]
    alloc_sel = [units["ON_ALLOC|%d" % s]["allocate_selectivity"] for s in seeds]
    base_alloc_rate = None
    try:
        # cross-reference the ORIGINAL probe1 allocate_rate on disk (MEASURED@, not re-derived)
        with open(os.path.join(REPO_ROOT, "data", "exp_contextual_stream_wm_sor_probe1_v1",
                                "metrics.json"), encoding="utf-8") as f:
            base_alloc_rate = json.load(f)["summary"]["allocate_rate"]
    except (OSError, KeyError, ValueError):
        base_alloc_rate = None

    off_m, pos_m, base_m, alloc_m = _mean(off), _mean(pos), _mean(base), _mean(alloc)
    alloc_clean_m, plac_m, rand_m = _mean(alloc_clean), _mean(plac), _mean(rand)
    spike_m, route_m, alloc_rate_m, alloc_sel_m = _mean(spike), _mean(route), _mean(alloc_rate), _mean(alloc_sel)

    summary = {
        "off_recall": off_m, "position_only": pos_m, "on_base_recall": base_m,
        "on_alloc_recall": alloc_m, "on_alloc_recall_cleanup": alloc_clean_m,
        "on_alloc_placebo": plac_m, "on_alloc_rand_ctrl_recall": rand_m,
        "spike_ratio_WR": spike_m, "route_consistency": route_m,
        "allocate_rate": alloc_rate_m, "allocate_rate_prior_probe1": base_alloc_rate,
        "allocate_selectivity": alloc_sel_m,
        "off_per_seed": off, "base_per_seed": base, "alloc_per_seed": alloc,
        "rand_ctrl_per_seed": rand,
        "floor_max": FLOOR_MAX, "pass_min": PASS_MIN, "chance": CHANCE,
    }

    floor_held = all(o <= FLOOR_MAX for o in off)
    position_failed = pos_m is not None and pos_m <= FLOOR_MAX
    placebo_failed = plac_m is not None and plac_m <= max(off_m, FLOOR_MAX) + 0.15
    summary["floor_held"] = floor_held
    summary["position_failed"] = position_failed
    summary["placebo_failed"] = placebo_failed

    if not floor_held:
        return "FLOOR_NOT_HELD_TASK_RESERVOIR_DECODABLE_HARDEN", summary

    brain_ok = (spike_m is not None and spike_m >= SPIKE_RATIO_MIN
                and route_m is not None and route_m >= ROUTE_CONSIST_MIN)
    alloc_selectivity_ok = alloc_sel_m is not None and alloc_sel_m >= ALLOC_SELECTIVITY_MIN
    alloc_rate_ok = alloc_rate_m is not None and alloc_rate_m >= ALLOCATE_RATE_MIN
    summary["brain_metric_ok"] = brain_ok
    summary["allocate_selectivity_ok"] = alloc_selectivity_ok
    summary["allocate_rate_ok"] = alloc_rate_ok
    # can-fail: random-allocate ablation must NOT beat ON_BASE by more than a small margin
    randctrl_failed = rand_m is not None and base_m is not None and (rand_m - base_m) <= RANDCTRL_MAX_LIFT
    summary["randctrl_failed"] = randctrl_failed
    alloc_own_lift_ok = alloc_m is not None and base_m is not None and (alloc_m - base_m) >= ALLOC_LIFT_MIN

    hard_pass_acc = (alloc_m is not None and all(a >= PASS_MIN for a in alloc)
                      and (alloc_m - off_m) >= PASS_LIFT_MIN)
    mechanism_ok = (brain_ok and alloc_selectivity_ok and alloc_rate_ok and randctrl_failed
                    and placebo_failed and alloc_own_lift_ok)

    if hard_pass_acc and mechanism_ok:
        return "HARD_PASS_DG_MATCH_OR_ALLOCATE_RESOLVES_SOR", summary
    if hard_pass_acc and not mechanism_ok:
        return "MIDDLE_ACCURACY_UP_BUT_ALLOCATE_MECHANISM_NOT_CLEAN", summary
    if not randctrl_failed:
        return "MIDDLE_RANDCTRL_CONFOUND_ALLOCATE_LIFT_NOT_ISOLATED", summary
    if alloc_m is not None and base_m is not None and (alloc_m - base_m) <= HARD_FAIL_LIFT:
        return "HARD_FAIL_ALLOCATE_FIX_NO_LIFT_OVER_BASELINE", summary
    return "MIDDLE_PARTIAL_ALLOCATE_LIFT", summary


def _write_metrics(verdict, summary, units, elapsed, mode):
    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": ("%s | OFF=%.3f BASE=%.3f ALLOC=%.3f(clean=%.3f) RAND=%.3f placebo=%.3f "
                        "| spike_WR=%.2f route=%.2f alloc_rate=%.2f(was %.3f) alloc_sel=%.2f "
                        "| floor=%s brain_ok=%s randctrl_failed=%s"
                        % (verdict, summary.get("off_recall") or -1, summary.get("on_base_recall") or -1,
                           summary.get("on_alloc_recall") or -1, summary.get("on_alloc_recall_cleanup") or -1,
                           summary.get("on_alloc_rand_ctrl_recall") or -1, summary.get("on_alloc_placebo") or -1,
                           summary.get("spike_ratio_WR") or -1, summary.get("route_consistency") or -1,
                           summary.get("allocate_rate") or -1, summary.get("allocate_rate_prior_probe1") or -1,
                           summary.get("allocate_selectivity") or -1, summary.get("floor_held"),
                           summary.get("brain_metric_ok"), summary.get("randctrl_failed"))),
        "summary": summary,
        "bands": {"FLOOR_MAX": FLOOR_MAX, "PASS_MIN": PASS_MIN, "PASS_LIFT_MIN": PASS_LIFT_MIN,
                  "ALLOC_LIFT_MIN": ALLOC_LIFT_MIN, "RANDCTRL_MAX_LIFT": RANDCTRL_MAX_LIFT,
                  "ALLOCATE_RATE_MIN": ALLOCATE_RATE_MIN,
                  "ALLOC_SELECTIVITY_MIN": ALLOC_SELECTIVITY_MIN,
                  "SPIKE_RATIO_MIN": SPIKE_RATIO_MIN, "ROUTE_CONSIST_MIN": ROUTE_CONSIST_MIN},
        "task": {"D_MODEL": D_MODEL, "N_SLOTS": N_SLOTS, "N_QUERY": N_QUERY, "N_FILLERS": N_FILLERS,
                 "T_OVERWRITE": T_OVERWRITE, "N_RECALL": N_RECALL, "N_DISTRACT": N_DISTRACT,
                 "DG_EXPANSION": DG_EXPANSION, "DG_SPARSITY": DG_SPARSITY, "ALLOC_GAIN": ALLOC_GAIN,
                 "chance": CHANCE},
        "per_unit": units, "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"
    torch.manual_seed(0)

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        if mode == "self_test":
            _dg_novelty_selftest()
            _arms_differ_selftest()
        units, elapsed, seeds = run_all(mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("[%s] FATAL: %s\n%s" % (mode, e, traceback.format_exc()), flush=True)
        raise SystemExit(2)

    verdict, summary = decide_verdict(units, seeds)
    metrics = _write_metrics(verdict, summary, units, elapsed, mode)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, elapsed), flush=True)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
