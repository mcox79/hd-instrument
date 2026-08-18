# CELL-TEMPLATE (reuses probe1 SCAFFOLD: arm loop, per-(arm,seed)-unit checkpoint via
# tools/exp_checkpoint.py, atomic os.replace metrics, decide_verdict floor/pass bands, heartbeat).
# ONE VARIABLE: content-gated WM ON (SlotAttentionWM trained end-to-end) vs OFF (random-init frozen
# SlotAttentionWM + trained linear readout). Reuses hdlab/slot_attention_wm.py (atom 29592) UNCHANGED.
# CAN-FAIL FLOOR VERIFIED FIRST (numpy echo-state reservoir pre-calibration, the worst-case recency-
# decodable floor, floors at 0.04-0.09 across all hardness -> a weaker frozen-WM OFF will floor too;
# see report). all numbers tagged MEASURED@ / CITED@ / REASONED@. ASCII-only, no em dashes in output.
"""Contextual-stream WM: Selective-Overwrite-Recall (SOR) cheap first probe.

Spec: notes/contextual_stream_wm_sor_task_and_cheap_first_probe_2026-08-01.md (commit b55fca5bd).
Tests whether content-gated WM (hdlab.slot_attention_wm.SlotAttentionWM: addr_net content routing +
boundary_k PBWM overwrite-with-suppression + HRR bind/unbind recall) can maintain 6 entity slots over
a distractor-heavy, position-randomized, multiply-overwritten oracle-vector stream and recall each
slot's MOST-RECENTLY-WRITTEN filler -- which a random-init frozen reservoir + trained linear readout
provably cannot (recency decoding cannot isolate a slot's last write from the superposition of its
overwrites when position is randomized). Oracle vectors only (no encoder, no real text): SOR proves
the WM mechanism in isolation, exactly as probe1 proved the interactive loop on oracle vectors first.

ARM_OFF = random-init frozen SlotAttentionWM (addr/gate/theta NOT trained) + trained linear readout on
  final slot states + query slot_id. Reservoir shortcut arm; MUST fail (<= 0.20) or task is vacuous.
ARM_ON  = SAME SlotAttentionWM trained end-to-end (addr routes by slot_id content; gate learns
  overwrite; theta learns the write boundary), parameter-free HRR-unbind recall readout.
CONTROLS: shuffled-slot placebo (slot_id vectors randomized per-event -> routing has nothing to key
  on -> MUST fail); position-only (predict from global-most-recent-in-stream, ignoring slot -> MUST
  fail since position is randomized). BRAIN-METRIC: overwrite-spiking (write_strength on new-info
  WRITE events >= 2x on RECALL events, Zacks update-at-discontinuity) + routing-consistency (same
  slot_id -> same slot argmax >= 0.80) + allocate (novel slot_id -> unused slot).

Run:  .venv/Scripts/python.exe experiments/exp_contextual_stream_wm_sor_probe1_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_contextual_stream_wm_sor_probe1_v1.py --full
"""

import argparse
import hashlib
import json
import math
import os
import sys
import time
import traceback
from datetime import datetime, timezone

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
import exp_checkpoint as ckpt  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cell_heartbeat import CellHeartbeat  # noqa: E402
from hdlab.slot_attention_wm import SlotAttentionWM  # noqa: E402
from hdlab.binding import bind, unbind  # noqa: E402


class PEGatedSlotWM(SlotAttentionWM):
    """SlotAttentionWM with the write gate made PURELY PE-driven (the 2026-08-02 fix). The organ's
    write is write_k = boundary_k * gate_mod, and the LEARNED gate_mod modulator can (and here did)
    settle to a near-constant ~0.47 that WASHES OUT the PE-boundary selectivity -> the slot blends
    every write (spike_ratio_WR=1.03) -> muddy recall. This override REMOVES gate_mod so the write is
    w_k = addr_w (which slot, routing) x boundary_k (PE event-boundary: HIGH when the incoming filler
    mismatches the routed slot's current bound content = a WRITE; LOW when it matches = a RECALL).
    This is Probe-1's validated PE-gate + Zacks update-at-discontinuity. ONE VARIABLE vs the prior
    cell; addressing / key / binding / recall are byte-identical to the organ. No gate_net, no kb."""

    def step(self, slots, clause_rep, tok_reps=None, pad_mask=None, kb_prior=None):
        B, K, d = slots.shape
        addr_src = self.entity_filler(tok_reps, pad_mask) if tok_reps is not None else clause_rep
        key = F.normalize(self.role_key_net(addr_src), dim=-1)
        clause_b = clause_rep.unsqueeze(1).expand(B, K, d)
        addr_b = addr_src.unsqueeze(1).expand(B, K, d)
        addr_logits = self.addr_net(torch.cat([addr_b, slots], dim=-1)).squeeze(-1)
        addr_w = torch.softmax(addr_logits / self.addr_temp, dim=-1)          # [B,K] routing
        readback = unbind(slots, key.unsqueeze(1))                           # [B,K,d]
        surprise_k = 1.0 - F.cosine_similarity(readback, clause_b, dim=-1)   # [B,K] per-slot PE
        tau = max(float(self.write_tau), 1e-4)
        boundary_k = torch.sigmoid((surprise_k - self.write_theta) / tau)    # [B,K] PE event-boundary
        candidate = bind(key, clause_rep).unsqueeze(1)                       # [B,1,d]
        w_k = (addr_w * boundary_k).unsqueeze(-1)                            # [B,K,1] routing x PE
        new_slots = (1.0 - w_k) * slots + w_k * candidate                   # overwrite-with-suppression
        surprise = (addr_w * surprise_k).sum(dim=-1)
        write_strength = (addr_w * boundary_k).sum(dim=-1)                   # PE-selective write
        ent = -(addr_w.clamp_min(1e-8) * addr_w.clamp_min(1e-8).log()).sum(dim=-1)
        addr_entropy = ent / math.log(self.n_slots)
        return new_slots, dict(surprise=surprise, write_strength=write_strength, addr_entropy=addr_entropy)

ANCHOR_NAME = "contextual_stream_wm_sor_probe1_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
DEVICE = torch.device("cpu")

# --- task constants (T/D locked from the numpy echo-state floor calibration; reservoir floors here) ---
D_MODEL = 32
N_SLOTS = 8              # >= N_QUERY (room for distractors + allocate)
N_QUERY = 6
N_DISTRACT_IDS = 24
N_FILLERS = 20
T_OVERWRITE = 4          # writes per query slot (multi-overwrite -> defeats recency readout)
N_RECALL = 8             # re-mention (same filler) events -> HOLD; brain-metric contrast
N_DISTRACT = 30          # distractor touches (>> slots)
CHANCE = 1.0 / N_FILLERS
RECALL_TEMP = 0.1

# --- pre-registered bands (fixed BEFORE running) ---
FLOOR_MAX = 0.20         # ARM_OFF must be AT/BELOW this (else task reservoir-decodable -> harden)
PASS_MIN = 0.75          # ARM_ON HARD-PASS recall
PASS_LIFT_MIN = 0.50     # ARM_ON must exceed OFF by this
HARD_FAIL_LIFT = 0.10    # ARM_ON <= OFF + this -> content-gating gave no lift
SPIKE_RATIO_MIN = 2.0    # write_strength(WRITE)/write_strength(RECALL) brain-metric
ROUTE_CONSIST_MIN = 0.80 # same slot_id -> same slot argmax

EPOCHS_ON = 220
EPOCHS_OFF = 320
LR_ON = 5e-3
LR_OFF = 1e-2
N_TRAIN = 384
N_TEST = 192


# ---------------------------------------------------------------------------
# SOR STREAM GENERATION
# ---------------------------------------------------------------------------
# Fixed TYPE schedule per position (so the brain-metric knows each event's type), but the slot_id /
# filler IDENTITIES at each position are randomized per example -> position does NOT predict the
# answer (which write is a slot's LAST is randomized), while event-type-per-position is known.
def _type_schedule(g):
    types = ([0] * (N_QUERY * T_OVERWRITE)) + ([1] * N_RECALL) + ([2] * N_DISTRACT)  # 0=W,1=R,2=D
    idx = torch.randperm(len(types), generator=g).tolist()
    return [types[i] for i in idx]


def _gen_example(schedule, g, shuffle_slot_ids=False):
    """Build one SOR stream given a fixed type schedule. Returns per-position (slot_idx, filler_idx,
    type) arrays + query_slot + gold_filler. shuffle_slot_ids: PLACEBO -- each event gets a random
    (identity-breaking) slot vector index so the same logical slot has no stable id."""
    L = len(schedule)
    # assign the N_QUERY*T_OVERWRITE write events to query slots so each gets exactly T writes,
    # in RANDOM order (last-write position per slot is randomized).
    write_slots = []
    for s in range(N_QUERY):
        write_slots += [s] * T_OVERWRITE
    perm = torch.randperm(len(write_slots), generator=g).tolist()
    write_slots = [write_slots[i] for i in perm]
    cur_filler = {}
    slot_idx = [0] * L
    fill_idx = [0] * L
    actual_type = list(schedule)
    w_ptr = 0
    for t in range(L):
        ty = schedule[t]
        if ty == 0:  # WRITE new filler to a query slot
            s = write_slots[w_ptr]; w_ptr += 1
            f = int(torch.randint(0, N_FILLERS, (1,), generator=g).item())
            cur_filler[s] = f
            slot_idx[t] = s; fill_idx[t] = f
        elif ty == 1 and cur_filler:  # RECALL: re-present a query slot's CURRENT filler (HOLD)
            written = list(cur_filler.keys())
            s = written[int(torch.randint(0, len(written), (1,), generator=g).item())]
            slot_idx[t] = s; fill_idx[t] = cur_filler[s]
        else:  # DISTRACTOR (or an early RECALL before any write -> reclassified distractor)
            slot_idx[t] = N_QUERY + int(torch.randint(0, N_DISTRACT_IDS, (1,), generator=g).item())
            fill_idx[t] = int(torch.randint(0, N_FILLERS, (1,), generator=g).item())
            actual_type[t] = 2
    q = int(torch.randint(0, N_QUERY, (1,), generator=g).item())
    gold = cur_filler[q]
    if shuffle_slot_ids:
        # PLACEBO: replace every slot index with a random one drawn from the FULL id space so the
        # same logical slot has a DIFFERENT id vector each touch -> content routing cannot key on it.
        n_ids = N_QUERY + N_DISTRACT_IDS
        slot_idx = [int(torch.randint(0, n_ids, (1,), generator=g).item()) for _ in range(L)]
        # query id also randomized to a fresh unseen id -> recall key has no match
        q_id = int(torch.randint(0, n_ids, (1,), generator=g).item())
    else:
        q_id = q
    return {"slot_idx": slot_idx, "fill_idx": fill_idx, "type": actual_type,
            "q": q, "q_id": q_id, "gold": gold}


def gen_dataset(n, seed, shuffle_slot_ids=False):
    g = torch.Generator().manual_seed(seed)
    schedule = _type_schedule(g)
    return [_gen_example(schedule, g, shuffle_slot_ids) for _ in range(n)], schedule


def _vocab(seed):
    g = torch.Generator().manual_seed(seed + 5000)
    n_ids = N_QUERY + N_DISTRACT_IDS
    slot_vecs = F.normalize(torch.randn(n_ids, D_MODEL, generator=g), dim=-1)
    filler_vecs = F.normalize(torch.randn(N_FILLERS, D_MODEL, generator=g), dim=-1)
    return slot_vecs, filler_vecs


def _batch_tensors(ds, slot_vecs, filler_vecs):
    B = len(ds)
    L = len(ds[0]["type"])
    slot_ids = torch.stack([torch.tensor(e["slot_idx"]) for e in ds])   # [B,L]
    fill_ids = torch.stack([torch.tensor(e["fill_idx"]) for e in ds])   # [B,L]
    clause_reps = [filler_vecs[fill_ids[:, t]] for t in range(L)]        # list of [B,d]
    tok_reps = [slot_vecs[slot_ids[:, t]].unsqueeze(1) for t in range(L)]  # list of [B,1,d]
    q_id = torch.tensor([e["q_id"] for e in ds])
    gold = torch.tensor([e["gold"] for e in ds])
    return clause_reps, tok_reps, q_id, gold, slot_ids


# ---------------------------------------------------------------------------
# WM ROLLOUT + RECALL
# ---------------------------------------------------------------------------
def rollout(wm, clause_reps, tok_reps, capture=False):
    """Run the stream through wm.step. Returns final_slots [B,K,d]; if capture, also per-step
    write_strength [L,B] and addr_argmax [L,B] (routing) computed from the live slot state."""
    B = clause_reps[0].shape[0]
    slots = wm.init_slots(B, DEVICE)
    ws_list, route_list = [], []
    for t in range(len(clause_reps)):
        if capture:
            addr_src = wm.entity_filler(tok_reps[t])
            addr_logits = wm.addr_net(torch.cat([addr_src.unsqueeze(1).expand(B, wm.n_slots, wm.d_model),
                                                 slots], dim=-1)).squeeze(-1)
            addr_w = torch.softmax(addr_logits / wm.addr_temp, dim=-1)
            route_list.append(addr_w.argmax(dim=-1))
        slots, feats = wm.step(slots, clause_reps[t], tok_reps=tok_reps[t])
        if capture:
            ws_list.append(feats["write_strength"].detach())
    if capture:
        return slots, torch.stack(ws_list), torch.stack(route_list)
    return slots, None, None


def recall_logits(wm, final_slots, q_id, slot_vecs, filler_vecs):
    """Parameter-free HRR-unbind recall: address final slots by the query slot_id, unbind the content
    key, score against the filler vocab. Returns [B, N_FILLERS] logits."""
    B = final_slots.shape[0]
    q_vec = slot_vecs[q_id]                                   # [B,d]
    key = F.normalize(wm.role_key_net(q_vec), dim=-1)         # [B,d]
    addr_logits = wm.addr_net(torch.cat([q_vec.unsqueeze(1).expand(B, wm.n_slots, wm.d_model),
                                         final_slots], dim=-1)).squeeze(-1)
    addr_w = torch.softmax(addr_logits / wm.addr_temp, dim=-1)          # [B,K]
    readback = unbind(final_slots, key.unsqueeze(1))                    # [B,K,d]
    pred = (addr_w.unsqueeze(-1) * readback).sum(dim=1)                 # [B,d]
    logits = (F.normalize(pred, dim=-1) @ filler_vecs.t()) / RECALL_TEMP  # [B,F]
    return logits


# ---------------------------------------------------------------------------
# TRAIN ARMS
# ---------------------------------------------------------------------------
def train_on(seed, n_train, n_test, epochs, shuffle_slot_ids=False):
    slot_vecs, filler_vecs = _vocab(seed)
    train_ds, _ = gen_dataset(n_train, seed + 1, shuffle_slot_ids)
    test_ds, sched = gen_dataset(n_test, seed + 2, shuffle_slot_ids)
    tr = _batch_tensors(train_ds, slot_vecs, filler_vecs)
    te = _batch_tensors(test_ds, slot_vecs, filler_vecs)
    wm = PEGatedSlotWM(D_MODEL, n_slots=N_SLOTS, hidden=64, seed=seed)
    opt = torch.optim.Adam(wm.parameters(), lr=LR_ON)
    for ep in range(epochs):
        wm.anneal_write_tau(ep / max(1, epochs - 1))
        opt.zero_grad()
        final, _, _ = rollout(wm, tr[0], tr[1])
        logits = recall_logits(wm, final, tr[2], slot_vecs, filler_vecs)
        loss = F.cross_entropy(logits, tr[3])
        loss.backward()
        opt.step()
    wm.set_write_tau(wm.write_tau_end)
    acc, extra = _eval_on(wm, te, test_ds, sched, slot_vecs, filler_vecs)
    return acc, extra, wm, (slot_vecs, filler_vecs)


def _eval_on(wm, te, test_ds, sched, slot_vecs, filler_vecs):
    with torch.no_grad():
        final, ws, route = rollout(wm, te[0], te[1], capture=True)
        logits = recall_logits(wm, final, te[2], slot_vecs, filler_vecs)
        acc = (logits.argmax(-1) == te[3]).float().mean().item()
        # brain-metric: write_strength by event type (ws: [L,B])
        types = torch.tensor(sched)                       # [L]
        w_mask = (types == 0); r_mask = (types == 1); d_mask = (types == 2)
        mean_w = ws[w_mask].mean().item() if w_mask.any() else 0.0
        mean_r = ws[r_mask].mean().item() if r_mask.any() else 0.0
        mean_d = ws[d_mask].mean().item() if d_mask.any() else 0.0
        spike_ratio = mean_w / mean_r if mean_r > 1e-6 else float("inf")
        # routing-consistency: for each example, for each query slot, are its write-touches routed
        # to the same slot? route: [L,B]; slot_ids [B,L].
        slot_ids = te[4]                                   # [B,L]
        consist, alloc_hits, alloc_tot = [], 0, 0
        route_t = route.t()                                # [B,L]
        for b in range(slot_ids.shape[0]):
            used = {}
            for s in range(N_QUERY):
                touches = [t for t in range(len(sched)) if slot_ids[b, t].item() == s]
                if not touches:
                    continue
                routed = [route_t[b, t].item() for t in touches]
                modal = max(set(routed), key=routed.count)
                consist.append(sum(1 for r in routed if r == modal) / len(routed))
                # allocate: first touch of this slot routes to a slot not yet claimed by another id
                first_slot = route_t[b, touches[0]].item()
                alloc_tot += 1
                if first_slot not in used.values():
                    alloc_hits += 1
                used[s] = first_slot
        route_consist = float(sum(consist) / len(consist)) if consist else 0.0
        allocate_rate = alloc_hits / alloc_tot if alloc_tot else 0.0
    return acc, {"mean_write_W": mean_w, "mean_write_R": mean_r, "mean_write_D": mean_d,
                 "spike_ratio_WR": spike_ratio, "spike_ratio_WD": (mean_w / mean_d if mean_d > 1e-6 else float("inf")),
                 "route_consistency": route_consist, "allocate_rate": allocate_rate}


def train_off(seed, n_train, n_test, epochs):
    """Frozen random-init WM + trained linear readout on [flatten(final_slots), query_slot_vec]."""
    slot_vecs, filler_vecs = _vocab(seed)
    train_ds, _ = gen_dataset(n_train, seed + 1)
    test_ds, _ = gen_dataset(n_test, seed + 2)
    tr = _batch_tensors(train_ds, slot_vecs, filler_vecs)
    te = _batch_tensors(test_ds, slot_vecs, filler_vecs)
    wm = PEGatedSlotWM(D_MODEL, n_slots=N_SLOTS, hidden=64, seed=seed)
    wm.set_write_tau(wm.write_tau_end)
    for p in wm.parameters():
        p.requires_grad_(False)
    with torch.no_grad():
        final_tr, _, _ = rollout(wm, tr[0], tr[1])
        final_te, _, _ = rollout(wm, te[0], te[1])
    Xtr = torch.cat([final_tr.reshape(final_tr.shape[0], -1), slot_vecs[tr[2]]], dim=-1)
    Xte = torch.cat([final_te.reshape(final_te.shape[0], -1), slot_vecs[te[2]]], dim=-1)
    readout = nn.Linear(Xtr.shape[1], N_FILLERS)
    opt = torch.optim.Adam(readout.parameters(), lr=LR_OFF, weight_decay=1e-4)
    for _ in range(epochs):
        opt.zero_grad()
        loss = F.cross_entropy(readout(Xtr), tr[3])
        loss.backward()
        opt.step()
    with torch.no_grad():
        acc = (readout(Xte).argmax(-1) == te[3]).float().mean().item()
    return acc


def position_only_acc(seed, n_test):
    """Predict from GLOBAL-most-recent-in-stream filler (position heuristic, slot-blind). Must fail
    since position is randomized (queried slot's last write is rarely the stream's last event)."""
    test_ds, sched = gen_dataset(n_test, seed + 2)
    hits = 0
    for e in test_ds:
        last_fill = e["fill_idx"][-1]         # global last event's filler
        hits += int(last_fill == e["gold"])
    return hits / len(test_ds)


# ---------------------------------------------------------------------------
# HARNESS
# ---------------------------------------------------------------------------
def _digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def run_all(mode):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()
    if mode == "self_test":
        seeds, n_tr, n_te, ep_on, ep_off = [0], 48, 32, 30, 60
    else:
        seeds, n_tr, n_te, ep_on, ep_off = [0, 1], N_TRAIN, N_TEST, EPOCHS_ON, EPOCHS_OFF

    with CellHeartbeat(OUTPUT_DIR, total_units=len(seeds) * 2, interval_s=20) as hb:
        tick = 0
        for seed in seeds:
            # OFF FIRST (floor verification before trusting any ON number)
            key = ckpt.unit_key(mode, "OFF", seed)
            if key not in ckpt.completed_units(OUTPUT_DIR):
                off_acc = train_off(seed, n_tr, n_te, ep_off)
                pos_acc = position_only_acc(seed, n_te)
                ckpt.record_unit(OUTPUT_DIR, key, {"seed": seed, "arm": "OFF",
                                                   "recall_acc": off_acc, "position_only_acc": pos_acc})
                print("[OFF seed=%d] recall=%.3f position_only=%.3f (floor<=%.2f)"
                      % (seed, off_acc, pos_acc, FLOOR_MAX), flush=True)
            tick += 1; hb.tick(tick)
            # ON + placebo
            key = ckpt.unit_key(mode, "ON", seed)
            if key not in ckpt.completed_units(OUTPUT_DIR):
                on_acc, extra, _, _ = train_on(seed, n_tr, n_te, ep_on)
                plac_acc, _, _, _ = train_on(seed, n_tr, n_te, ep_on, shuffle_slot_ids=True)
                rec = {"seed": seed, "arm": "ON", "recall_acc": on_acc, "placebo_acc": plac_acc}
                rec.update(extra)
                ckpt.record_unit(OUTPUT_DIR, key, rec)
                print("[ON seed=%d] recall=%.3f placebo=%.3f spike_WR=%.2f route_consist=%.2f alloc=%.2f"
                      % (seed, on_acc, plac_acc, extra["spike_ratio_WR"], extra["route_consistency"],
                         extra["allocate_rate"]), flush=True)
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
    on = [units["ON|%d" % s]["recall_acc"] for s in seeds]
    plac = [units["ON|%d" % s]["placebo_acc"] for s in seeds]
    pos = [units["OFF|%d" % s]["position_only_acc"] for s in seeds]
    spike = [units["ON|%d" % s]["spike_ratio_WR"] for s in seeds]
    route = [units["ON|%d" % s]["route_consistency"] for s in seeds]
    alloc = [units["ON|%d" % s]["allocate_rate"] for s in seeds]
    off_m, on_m, plac_m, pos_m = _mean(off), _mean(on), _mean(plac), _mean(pos)
    spike_m, route_m, alloc_m = _mean(spike), _mean(route), _mean(alloc)

    summary = {"off_recall": off_m, "on_recall": on_m, "placebo_recall": plac_m,
               "position_only": pos_m, "spike_ratio_WR": spike_m, "route_consistency": route_m,
               "allocate_rate": alloc_m, "off_per_seed": off, "on_per_seed": on,
               "floor_max": FLOOR_MAX, "pass_min": PASS_MIN, "chance": CHANCE}

    floor_held = all(o <= FLOOR_MAX for o in off)
    summary["floor_held"] = floor_held
    placebo_failed = plac_m is not None and plac_m <= max(off_m, FLOOR_MAX) + 0.15
    position_failed = pos_m is not None and pos_m <= FLOOR_MAX
    summary["placebo_failed"] = placebo_failed
    summary["position_failed"] = position_failed

    if not floor_held:
        return "FLOOR_NOT_HELD_TASK_RESERVOIR_DECODABLE_HARDEN", summary
    brain_ok = (spike_m is not None and spike_m >= SPIKE_RATIO_MIN
                and route_m is not None and route_m >= ROUTE_CONSIST_MIN)
    summary["brain_metric_ok"] = brain_ok
    hard_pass_acc = all(a >= PASS_MIN for a in on) and (on_m - off_m) >= PASS_LIFT_MIN
    if hard_pass_acc and brain_ok and placebo_failed:
        return "HARD_PASS_CONTENT_GATED_WM_RESOLVES_SOR", summary
    if hard_pass_acc and not brain_ok:
        return "MIDDLE_ACCURACY_UP_BUT_GATING_DYNAMICS_FLAT", summary
    if on_m is not None and on_m <= off_m + HARD_FAIL_LIFT:
        return "HARD_FAIL_CONTENT_GATING_NO_LIFT", summary
    return "MIDDLE_PARTIAL_SIGNAL", summary


def _write_metrics(verdict, summary, units, elapsed, mode):
    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": ("%s | OFF=%.3f ON=%.3f placebo=%.3f pos_only=%.3f | spike_WR=%.2f "
                        "route=%.2f alloc=%.2f | floor_held=%s brain_ok=%s"
                        % (verdict, summary.get("off_recall") or -1, summary.get("on_recall") or -1,
                           summary.get("placebo_recall") or -1, summary.get("position_only") or -1,
                           summary.get("spike_ratio_WR") or -1, summary.get("route_consistency") or -1,
                           summary.get("allocate_rate") or -1, summary.get("floor_held"),
                           summary.get("brain_metric_ok"))),
        "summary": summary,
        "bands": {"FLOOR_MAX": FLOOR_MAX, "PASS_MIN": PASS_MIN, "PASS_LIFT_MIN": PASS_LIFT_MIN,
                  "SPIKE_RATIO_MIN": SPIKE_RATIO_MIN, "ROUTE_CONSIST_MIN": ROUTE_CONSIST_MIN},
        "task": {"D_MODEL": D_MODEL, "N_SLOTS": N_SLOTS, "N_QUERY": N_QUERY, "N_FILLERS": N_FILLERS,
                 "T_OVERWRITE": T_OVERWRITE, "N_RECALL": N_RECALL, "N_DISTRACT": N_DISTRACT,
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
