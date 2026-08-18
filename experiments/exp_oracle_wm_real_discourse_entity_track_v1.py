# CELL-TEMPLATE (reuses probe1/allocate-cell scaffold conventions: per-unit checkpoint via
# tools/exp_checkpoint.py, atomic os.replace metrics, decide_verdict floor/pass bands, heartbeat).
# ONE VARIABLE across arms: whether the WM's content-routed PE-gated overwrite (PEGatedSlotWM,
# hdlab/slot_attention_wm.py SlotAttentionWM w/ the pure-PE write override, atom 29592/29607) is
# TRAINED (arm ON, generalizes to unseen entity vectors) vs UNTRAINED/random-init (arm OFF, the
# non-vacuous reservoir floor). ORACLE arm: gold (entity, role) sequences fed directly, no
# extraction, no encoder, no borrowed embeddings -- one FIXED random vector per entity identity,
# one FIXED random vector per ROLE label (MEANING=ASSIGNMENT). Isolates "does the overwrite-WM
# maintain + correctly UPDATE entity roles across a REAL multi-clause McGuffey passage" from
# extraction error (design: notes/wire_extraction_wm_real_text_entity_tracking_design_2026-08-02.md).
#
# QUERY SEMANTICS (Finding 1, load-bearing): a situation-model WM holds CURRENT state, not full
# history (Zwaan; Zacks event-segmentation-update). So the query for entity E is E's FINAL/current
# gold role (last chronological mention in `entities[E]`), evaluated after streaming the WHOLE
# passage -- NOT the role at an arbitrary earlier query_clause (which may have been legitimately
# overwritten). CONSTANT-role entities test stable recall; ROLE-VARIATION entities test correct
# UPDATE (the overwrite gate's actual job). This script queries ALL entities per passage (15 total
# across the 6-passage starter gold), a superset of the gold's `target_queries` field.
#
# ARMS (this run):
#   ON        = PEGatedSlotWM trained on SYNTHETIC entity-tracking streams (same structural shape as
#               real passages: 2-4 clauses, 2-3 entities, per-mention role HOLD/CHANGE, FRESH random
#               entity vectors every synthetic example so addr_net/role_key_net/gate must learn
#               content-generic routing, not memorize a fixed vocab) -- then evaluated ZERO-SHOT on
#               the 6 real gold passages (fresh random entity vectors per passage, never seen in
#               training). Role vectors are a small FIXED shared vocab (agent/patient/theme/
#               recipient/addressee/speaker), used identically train+test (closed class).
#   OFF (CAN-FAIL #1, reservoir/random-WM) = SAME architecture, random-init, FROZEN (no training of
#               addr/gate/key); only a linear readout on [final_slots, query_vec] is trained (on the
#               same synthetic distribution) and evaluated zero-shot on real. Must fail near chance --
#               the mandatory non-vacuous-floor control (same discipline as the SOR probe's ARM_OFF).
#   SHUFFLED (CAN-FAIL #2) = the TRAINED ON weights, real passages replayed with event order shuffled
#               (5 shuffles/passage, averaged) -- should degrade vs true order.
#   LAST-CLAUSE (CAN-FAIL #3, no-memory) = pure rule baseline, no WM: predicts the queried entity's
#               role AT THE FINAL CLAUSE if mentioned there, else a fixed default ("agent", the modal
#               role). HONEST CAVEAT (Finding 2): most starter-gold entities recur in the final
#               clause, so this control is UNDERPOWERED here (expect it to look artificially strong);
#               reported for completeness, not as a clean discriminator until memory-test-optimized
#               gold exists.
#
# BRAIN-METRIC (component-fidelity, real text): per-mention write_strength during the TRUE-order arm-
# ON rollout, split into ROLE-CHANGE events (role differs from that entity's immediately-prior
# mention) vs ROLE-REPEAT events (same role as prior mention); first-mention-per-entity events are
# excluded (no "prior" to compare). spike_ratio = mean(write_strength|change) / mean(write_strength|
# repeat) -- the real-discourse analog of the SOR probe's spike_ratio_WR selectivity.
#
# Run:  .venv/Scripts/python.exe experiments/exp_oracle_wm_real_discourse_entity_track_v1.py --self-test
#       .venv/Scripts/python.exe experiments/exp_oracle_wm_real_discourse_entity_track_v1.py --full
"""Oracle-WM real-discourse entity-tracking probe (first arm of extraction->WM wiring)."""

import argparse
import hashlib
import json
import os
import random
import sys
import time
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

ANCHOR_NAME = "oracle_wm_real_discourse_entity_track_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
GOLD_PATH = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1",
                          "gold_multiclause_entity_track_v1.jsonl")
DEVICE = torch.device("cpu")


class PEGatedSlotWM(SlotAttentionWM):
    """Verbatim reuse of the validated pure-PE-driven write override (atom 29607/29592 lineage):
    write_k = addr_w (routing) x boundary_k (PE event-boundary), NO gate_net washout term. See
    experiments/exp_contextual_stream_wm_sor_probe1_v1.py for the original + rationale."""

    def step(self, slots, clause_rep, tok_reps=None, pad_mask=None, kb_prior=None):
        B, K, d = slots.shape
        addr_src = self.entity_filler(tok_reps, pad_mask) if tok_reps is not None else clause_rep
        key = F.normalize(self.role_key_net(addr_src), dim=-1)
        clause_b = clause_rep.unsqueeze(1).expand(B, K, d)
        addr_b = addr_src.unsqueeze(1).expand(B, K, d)
        addr_logits = self.addr_net(torch.cat([addr_b, slots], dim=-1)).squeeze(-1)
        addr_w = torch.softmax(addr_logits / self.addr_temp, dim=-1)
        readback = unbind(slots, key.unsqueeze(1))
        surprise_k = 1.0 - F.cosine_similarity(readback, clause_b, dim=-1)
        tau = max(float(self.write_tau), 1e-4)
        boundary_k = torch.sigmoid((surprise_k - self.write_theta) / tau)
        candidate = bind(key, clause_rep).unsqueeze(1)
        w_k = (addr_w * boundary_k).unsqueeze(-1)
        new_slots = (1.0 - w_k) * slots + w_k * candidate
        surprise = (addr_w * surprise_k).sum(dim=-1)
        write_strength = (addr_w * boundary_k).sum(dim=-1)
        return new_slots, dict(surprise=surprise, write_strength=write_strength)


# --- pre-registered constants (fixed BEFORE running; do not tune post-hoc) -------------------
D_MODEL = 32
N_SLOTS = 6
ROLE_NAMES = ["agent", "patient", "theme", "recipient", "addressee", "speaker"]
N_ROLES = len(ROLE_NAMES)
ROLE_IDX = {r: i for i, r in enumerate(ROLE_NAMES)}
CHANCE = 1.0 / N_ROLES
RECALL_TEMP = 0.1

N_TRAIN_SYNTH = 320
EPOCHS_ON = 25
EPOCHS_OFF_READOUT = 60
LR_ON = 5e-3
LR_OFF = 1e-2
P_ROLE_CHANGE = 0.45
N_SHUFFLES = 5

SEEDS_FULL = [0, 1, 2]
SEEDS_SELFTEST = [0]

# --- pre-registered bands (fixed BEFORE running) ---
FLOOR_MAX = 0.35          # ARM_OFF (reservoir) current-state accuracy must be AT/BELOW this
PASS_MIN = 0.70           # ARM_ON HARD-PASS overall accuracy
MIDDLE_MIN = 0.45         # below this = FAIL, not MIDDLE
LIFT_MIN = 0.25           # ARM_ON must exceed OFF by this (absolute)
SHUFFLE_DEGRADE_MIN = 0.05  # shuffled accuracy should be <= true-order accuracy - this (soft check)
SPIKE_RATIO_MIN = 1.3     # brain-metric soft threshold (real text; relaxed vs synthetic SOR's 2.0)


# ---------------------------------------------------------------------------
# ROLE VOCAB (fixed, shared, MEANING=ASSIGNMENT: one vector per role label)
# ---------------------------------------------------------------------------
def role_vocab_vecs(base_seed=1234):
    g = torch.Generator().manual_seed(base_seed)
    return F.normalize(torch.randn(N_ROLES, D_MODEL, generator=g), dim=-1)


# ---------------------------------------------------------------------------
# SYNTHETIC PRETRAIN STREAM GENERATOR (structurally mirrors the real gold: 2-4 clauses,
# 2-3 entities, per-mention role HOLD-or-CHANGE; FRESH random entity vectors every example so
# the network learns content-generic routing, not a memorized fixed vocab)
# ---------------------------------------------------------------------------
def gen_synth_example(py_rng, torch_gen, role_vecs):
    n_clauses = py_rng.randint(2, 4)
    n_entities = py_rng.randint(2, 3)
    entity_vecs = F.normalize(torch.randn(n_entities, D_MODEL, generator=torch_gen), dim=-1)

    entity_mentions = []  # list of (clause_idx, role_idx) per entity, chronological
    for _ in range(n_entities):
        k = py_rng.randint(1, n_clauses)
        clauses = sorted(py_rng.sample(range(n_clauses), k))
        role = py_rng.randrange(N_ROLES)
        seq = [(clauses[0], role)]
        for c in clauses[1:]:
            if py_rng.random() < P_ROLE_CHANGE:
                choices = [r for r in range(N_ROLES) if r != role]
                role = py_rng.choice(choices)
            seq.append((c, role))
        entity_mentions.append(seq)

    events_by_clause = [[] for _ in range(n_clauses)]
    for e_idx, seq in enumerate(entity_mentions):
        for (c, r) in seq:
            events_by_clause[c].append((e_idx, r))
    events = []
    for c in range(n_clauses):
        mentions = events_by_clause[c]
        py_rng.shuffle(mentions)
        events.extend(mentions)

    gold_current = [seq[-1][1] for seq in entity_mentions]
    return entity_vecs, events, gold_current


def gen_synth_dataset(n, seed):
    py_rng = random.Random(seed)
    torch_gen = torch.Generator().manual_seed(seed + 7777)
    return [gen_synth_example(py_rng, torch_gen, None) for _ in range(n)]


# ---------------------------------------------------------------------------
# REAL GOLD LOADER (oracle roles; fresh random entity vector per unique entity per passage)
# ---------------------------------------------------------------------------
def load_gold():
    rows = []
    with open(GOLD_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def gold_passage_events(passage, torch_gen):
    """Flatten one gold passage into (entity_vecs[n_ent,d], events[(e_idx,role_idx)],
    gold_current[n_ent role_idx], entity_names[n_ent]) in clause order. Entity vectors are
    fresh random draws from torch_gen (caller controls seed -> reproducible per (seed,passage))."""
    entity_names = sorted(passage["entities"].keys())
    n_ent = len(entity_names)
    entity_vecs = F.normalize(torch.randn(n_ent, D_MODEL, generator=torch_gen), dim=-1)
    name_to_idx = {n: i for i, n in enumerate(entity_names)}
    n_clauses = len(passage["clauses"])
    events_by_clause = [[] for _ in range(n_clauses)]
    per_entity_seq = {n: [] for n in entity_names}
    for name, mentions in passage["entities"].items():
        for m in mentions:
            role_idx = ROLE_IDX[m["role"]]
            events_by_clause[m["clause"]].append((name_to_idx[name], role_idx))
            per_entity_seq[name].append((m["clause"], role_idx))
    events = []
    for c in range(n_clauses):
        events.extend(events_by_clause[c])  # gold mention order within clause == list order
    gold_current = [per_entity_seq[n][-1][1] for n in entity_names]
    is_variation = [len(set(r for (_, r) in per_entity_seq[n])) > 1 for n in entity_names]
    return entity_vecs, events, gold_current, entity_names, is_variation, per_entity_seq


# ---------------------------------------------------------------------------
# ROLLOUT + RECALL (mirrors exp_contextual_stream_wm_sor_probe1_v1.rollout/recall_logits)
# ---------------------------------------------------------------------------
def rollout(wm, entity_vecs, events, role_vecs, capture=False):
    slots = wm.init_slots(1, DEVICE)
    ws_list, change_flags = [], []
    prev_role = {}
    for (e_idx, r_idx) in events:
        ent_vec = entity_vecs[e_idx].view(1, 1, D_MODEL)
        role_vec = role_vecs[r_idx].view(1, D_MODEL)
        slots, feats = wm.step(slots, role_vec, tok_reps=ent_vec)
        if capture:
            ws_list.append(float(feats["write_strength"].item()))
            if e_idx in prev_role:
                change_flags.append(prev_role[e_idx] != r_idx)
            else:
                change_flags.append(None)  # first mention: excluded from spike metric
        prev_role[e_idx] = r_idx
    if capture:
        return slots, ws_list, change_flags
    return slots, None, None


def recall_role_logits(wm, slots, q_vec, role_vecs):
    B = slots.shape[0]
    key = F.normalize(wm.role_key_net(q_vec), dim=-1)
    addr_logits = wm.addr_net(torch.cat(
        [q_vec.unsqueeze(1).expand(B, wm.n_slots, wm.d_model), slots], dim=-1)).squeeze(-1)
    addr_w = torch.softmax(addr_logits / wm.addr_temp, dim=-1)
    readback = unbind(slots, key.unsqueeze(1))
    pred = (addr_w.unsqueeze(-1) * readback).sum(dim=1)
    logits = (F.normalize(pred, dim=-1) @ role_vecs.t()) / RECALL_TEMP
    return logits


# ---------------------------------------------------------------------------
# ARM ON: train PEGatedSlotWM on synthetic, zero-shot eval on real gold
# ---------------------------------------------------------------------------
def train_arm_on(seed, n_train, epochs, role_vecs):
    wm = PEGatedSlotWM(D_MODEL, n_slots=N_SLOTS, hidden=64, seed=seed)
    opt = torch.optim.Adam(wm.parameters(), lr=LR_ON)
    train_ds = gen_synth_dataset(n_train, seed + 1)
    for ep in range(epochs):
        random.Random(seed * 1000 + ep).shuffle(train_ds)
        ep_loss = 0.0
        for (entity_vecs, events, gold_current) in train_ds:
            slots, _, _ = rollout(wm, entity_vecs, events, role_vecs)
            loss = 0.0
            for e_idx, gold_r in enumerate(gold_current):
                logits = recall_role_logits(wm, slots, entity_vecs[e_idx].view(1, D_MODEL), role_vecs)
                loss = loss + F.cross_entropy(logits, torch.tensor([gold_r]))
            loss = loss / len(gold_current)
            opt.zero_grad()
            loss.backward()
            opt.step()
            ep_loss += float(loss.item())
    return wm


def eval_arm_on_real(wm, gold_rows, role_vecs, seed, shuffle=False, n_shuffles=1):
    """Returns dict with overall/constant/variation accuracy + per-query detail, averaged over
    n_shuffles independent event-order shuffles when shuffle=True (else true clause order)."""
    torch_gen = torch.Generator().manual_seed(seed + 555000)
    accs = []
    detail = []
    for rep in range(n_shuffles):
        correct = correct_const = correct_var = 0
        n_const = n_var = 0
        for passage in gold_rows:
            pg = torch.Generator().manual_seed(hash((seed, passage["passage_id"])) % (2 ** 31))
            entity_vecs, events, gold_current, names, is_var, _ = gold_passage_events(passage, pg)
            ev = list(events)
            if shuffle:
                rnd = random.Random(hash((seed, rep, passage["passage_id"])) % (2 ** 31))
                rnd.shuffle(ev)
            slots, _, _ = rollout(wm, entity_vecs, ev, role_vecs)
            for e_idx, gold_r in enumerate(gold_current):
                logits = recall_role_logits(wm, slots, entity_vecs[e_idx].view(1, D_MODEL), role_vecs)
                pred = int(logits.argmax(dim=-1).item())
                hit = int(pred == gold_r)
                correct += hit
                if is_var[e_idx]:
                    n_var += 1
                    correct_var += hit
                else:
                    n_const += 1
                    correct_const += hit
                if rep == 0:
                    detail.append({"passage": passage["passage_id"], "entity": names[e_idx],
                                   "gold_role": ROLE_NAMES[gold_r], "pred_role": ROLE_NAMES[pred],
                                   "variation": is_var[e_idx], "hit": bool(hit)})
        n_total = n_const + n_var
        accs.append({"overall": correct / n_total, "constant": (correct_const / n_const) if n_const else None,
                     "variation": (correct_var / n_var) if n_var else None, "n_total": n_total,
                     "n_const": n_const, "n_var": n_var})
    overall = sum(a["overall"] for a in accs) / len(accs)
    const_vals = [a["constant"] for a in accs if a["constant"] is not None]
    var_vals = [a["variation"] for a in accs if a["variation"] is not None]
    return {"overall": overall,
            "constant": sum(const_vals) / len(const_vals) if const_vals else None,
            "variation": sum(var_vals) / len(var_vals) if var_vals else None,
            "n_total": accs[0]["n_total"], "n_const": accs[0]["n_const"], "n_var": accs[0]["n_var"],
            "detail": detail}


def brain_metric_real(wm, gold_rows, role_vecs, seed):
    torch_gen = torch.Generator().manual_seed(seed + 555000)
    change_ws, repeat_ws = [], []
    for passage in gold_rows:
        pg = torch.Generator().manual_seed(hash((seed, passage["passage_id"])) % (2 ** 31))
        entity_vecs, events, _, _, _, _ = gold_passage_events(passage, pg)
        _, ws_list, change_flags = rollout(wm, entity_vecs, events, role_vecs, capture=True)
        for ws, ch in zip(ws_list, change_flags):
            if ch is None:
                continue
            (change_ws if ch else repeat_ws).append(ws)
    m_change = sum(change_ws) / len(change_ws) if change_ws else None
    m_repeat = sum(repeat_ws) / len(repeat_ws) if repeat_ws else None
    ratio = (m_change / m_repeat) if (m_change is not None and m_repeat not in (None, 0)) else None
    return {"mean_write_strength_change": m_change, "mean_write_strength_repeat": m_repeat,
            "spike_ratio": ratio, "n_change": len(change_ws), "n_repeat": len(repeat_ws)}


# ---------------------------------------------------------------------------
# ARM OFF (CAN-FAIL #1): random-init frozen PEGatedSlotWM + trained linear readout
# ---------------------------------------------------------------------------
def train_arm_off(seed, n_train, epochs, role_vecs):
    wm = PEGatedSlotWM(D_MODEL, n_slots=N_SLOTS, hidden=64, seed=seed + 90000)
    for p in wm.parameters():
        p.requires_grad_(False)
    train_ds = gen_synth_dataset(n_train, seed + 20001)
    feats, labels = [], []
    with torch.no_grad():
        for (entity_vecs, events, gold_current) in train_ds:
            slots, _, _ = rollout(wm, entity_vecs, events, role_vecs)
            for e_idx, gold_r in enumerate(gold_current):
                q_vec = entity_vecs[e_idx]
                feats.append(torch.cat([slots.view(-1), q_vec]))
                labels.append(gold_r)
    X = torch.stack(feats)
    y = torch.tensor(labels)
    readout = nn.Linear(N_SLOTS * D_MODEL + D_MODEL, N_ROLES)
    opt = torch.optim.Adam(readout.parameters(), lr=LR_OFF)
    n = X.shape[0]
    for ep in range(epochs):
        perm = torch.randperm(n)
        for i in range(0, n, 32):
            idx = perm[i:i + 32]
            logits = readout(X[idx])
            loss = F.cross_entropy(logits, y[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
    return wm, readout


def eval_arm_off_real(wm, readout, gold_rows, role_vecs, seed):
    correct = correct_const = correct_var = 0
    n_const = n_var = 0
    with torch.no_grad():
        for passage in gold_rows:
            pg = torch.Generator().manual_seed(hash((seed, passage["passage_id"])) % (2 ** 31))
            entity_vecs, events, gold_current, names, is_var, _ = gold_passage_events(passage, pg)
            slots, _, _ = rollout(wm, entity_vecs, events, role_vecs)
            for e_idx, gold_r in enumerate(gold_current):
                q_vec = entity_vecs[e_idx]
                x = torch.cat([slots.view(-1), q_vec]).unsqueeze(0)
                pred = int(readout(x).argmax(dim=-1).item())
                hit = int(pred == gold_r)
                correct += hit
                if is_var[e_idx]:
                    n_var += 1; correct_var += hit
                else:
                    n_const += 1; correct_const += hit
    n_total = n_const + n_var
    return {"overall": correct / n_total,
            "constant": (correct_const / n_const) if n_const else None,
            "variation": (correct_var / n_var) if n_var else None,
            "n_total": n_total, "n_const": n_const, "n_var": n_var}


# ---------------------------------------------------------------------------
# CAN-FAIL #3: no-memory / last-clause-only rule baseline (no WM)
# ---------------------------------------------------------------------------
def last_clause_baseline(gold_rows, default_role="agent"):
    correct = correct_const = correct_var = 0
    n_const = n_var = 0
    default_idx = ROLE_IDX[default_role]
    for passage in gold_rows:
        n_clauses = len(passage["clauses"])
        final_clause = n_clauses - 1
        for name, mentions in passage["entities"].items():
            gold_r = ROLE_IDX[mentions[-1]["role"]]
            is_var = len(set(m["role"] for m in mentions)) > 1
            final_mentions = [m for m in mentions if m["clause"] == final_clause]
            pred_r = ROLE_IDX[final_mentions[-1]["role"]] if final_mentions else default_idx
            hit = int(pred_r == gold_r)
            correct += hit
            if is_var:
                n_var += 1; correct_var += hit
            else:
                n_const += 1; correct_const += hit
    n_total = n_const + n_var
    return {"overall": correct / n_total,
            "constant": (correct_const / n_const) if n_const else None,
            "variation": (correct_var / n_var) if n_var else None,
            "n_total": n_total, "n_const": n_const, "n_var": n_var}


# ---------------------------------------------------------------------------
# HARNESS
# ---------------------------------------------------------------------------
def _digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def run_all(mode):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()
    gold_rows = load_gold()
    role_vecs = role_vocab_vecs()

    if mode == "self_test":
        seeds, n_train, ep_on, ep_off = SEEDS_SELFTEST, 24, 3, 5
    else:
        seeds, n_train, ep_on, ep_off = SEEDS_FULL, N_TRAIN_SYNTH, EPOCHS_ON, EPOCHS_OFF_READOUT

    lc_base = last_clause_baseline(gold_rows)
    print("[LAST-CLAUSE baseline] overall=%.3f const=%s var=%s n=%d"
          % (lc_base["overall"], lc_base["constant"], lc_base["variation"], lc_base["n_total"]),
          flush=True)

    with CellHeartbeat(OUTPUT_DIR, total_units=len(seeds), interval_s=20) as hb:
        for tick, seed in enumerate(seeds, start=1):
            key = ckpt.unit_key(mode, "seed", seed)
            if key not in ckpt.completed_units(OUTPUT_DIR):
                wm_off, readout = train_arm_off(seed, n_train, ep_off, role_vecs)
                off_res = eval_arm_off_real(wm_off, readout, gold_rows, role_vecs, seed)
                wm_on = train_arm_on(seed, n_train, ep_on, role_vecs)
                on_res = eval_arm_on_real(wm_on, gold_rows, role_vecs, seed)
                shuf_res = eval_arm_on_real(wm_on, gold_rows, role_vecs, seed,
                                            shuffle=True, n_shuffles=N_SHUFFLES)
                brain = brain_metric_real(wm_on, gold_rows, role_vecs, seed)
                rec = {"seed": seed, "off": off_res, "on": on_res, "shuffled": shuf_res,
                       "brain_metric": brain, "last_clause": lc_base}
                ckpt.record_unit(OUTPUT_DIR, key, rec)
                print("[seed=%d] OFF=%.3f ON=%.3f(const=%s var=%s) SHUF=%.3f spike=%s"
                      % (seed, off_res["overall"], on_res["overall"], on_res["constant"],
                         on_res["variation"], shuf_res["overall"], brain["spike_ratio"]), flush=True)
            hb.tick(tick, force=True)

    units = ckpt.load_units(OUTPUT_DIR)
    units = {k.split("|", 1)[1]: v for k, v in units.items() if k.startswith(mode + "|")}
    elapsed = time.perf_counter() - t0
    return units, elapsed, seeds, lc_base


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def decide_verdict(units, seeds):
    off = [units["seed|%d" % s]["off"]["overall"] for s in seeds]
    on = [units["seed|%d" % s]["on"]["overall"] for s in seeds]
    on_const = [units["seed|%d" % s]["on"]["constant"] for s in seeds]
    on_var = [units["seed|%d" % s]["on"]["variation"] for s in seeds]
    shuf = [units["seed|%d" % s]["shuffled"]["overall"] for s in seeds]
    spike = [units["seed|%d" % s]["brain_metric"]["spike_ratio"] for s in seeds]

    off_m, on_m, shuf_m, spike_m = _mean(off), _mean(on), _mean(shuf), _mean(spike)
    on_const_m, on_var_m = _mean(on_const), _mean(on_var)

    floor_held = all(o <= FLOOR_MAX for o in off)
    lift_ok = on_m is not None and off_m is not None and (on_m - off_m) >= LIFT_MIN
    shuffle_degrades = (shuf_m is not None and on_m is not None
                        and (on_m - shuf_m) >= SHUFFLE_DEGRADE_MIN)
    brain_ok = spike_m is not None and spike_m >= SPIKE_RATIO_MIN

    summary = {
        "off_recall": off_m, "on_recall": on_m, "on_recall_constant": on_const_m,
        "on_recall_variation": on_var_m, "shuffled_recall": shuf_m, "spike_ratio": spike_m,
        "off_per_seed": off, "on_per_seed": on, "shuffled_per_seed": shuf, "spike_per_seed": spike,
        "floor_held": floor_held, "lift_ok": lift_ok, "shuffle_degrades": shuffle_degrades,
        "brain_metric_ok": brain_ok, "chance": CHANCE,
    }

    if not floor_held:
        return "FLOOR_NOT_HELD_TASK_RESERVOIR_DECODABLE_VACUOUS", summary
    if on_m is None:
        return "RUN_INCOMPLETE", summary
    if on_m >= PASS_MIN and lift_ok:
        verdict = "HARD_PASS_ORACLE_WM_MAINTAINS_REAL_DISCOURSE_ROLES"
    elif on_m >= MIDDLE_MIN and lift_ok:
        verdict = "MIDDLE_PARTIAL_ORACLE_WM_SOME_SIGNAL"
    elif lift_ok:
        verdict = "MIDDLE_WEAK_LIFT_BELOW_MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL_NO_LIFT_OVER_RESERVOIR"
    if not brain_ok:
        verdict += "_GATING_DYNAMICS_FLAT"
    return verdict, summary


def _fmt(x):
    return "%.3f" % x if isinstance(x, (int, float)) else str(x)


def _write_metrics(verdict, summary, units, elapsed, mode, lc_base):
    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": ("%s | OFF=%s ON=%s (const=%s var=%s) SHUF=%s LASTCLAUSE=%.3f "
                        "spike=%s | floor_held=%s lift_ok=%s shuffle_degrades=%s brain_ok=%s"
                        % (verdict, _fmt(summary.get("off_recall")), _fmt(summary.get("on_recall")),
                           _fmt(summary.get("on_recall_constant")), _fmt(summary.get("on_recall_variation")),
                           _fmt(summary.get("shuffled_recall")), lc_base["overall"],
                           _fmt(summary.get("spike_ratio")), summary.get("floor_held"),
                           summary.get("lift_ok"), summary.get("shuffle_degrades"),
                           summary.get("brain_metric_ok"))),
        "summary": summary,
        "last_clause_baseline": lc_base,
        "bands": {"FLOOR_MAX": FLOOR_MAX, "PASS_MIN": PASS_MIN, "MIDDLE_MIN": MIDDLE_MIN,
                  "LIFT_MIN": LIFT_MIN, "SHUFFLE_DEGRADE_MIN": SHUFFLE_DEGRADE_MIN,
                  "SPIKE_RATIO_MIN": SPIKE_RATIO_MIN},
        "task": {"D_MODEL": D_MODEL, "N_SLOTS": N_SLOTS, "N_ROLES": N_ROLES,
                 "ROLE_NAMES": ROLE_NAMES, "chance": CHANCE, "n_synth_train": N_TRAIN_SYNTH,
                 "epochs_on": EPOCHS_ON, "epochs_off_readout": EPOCHS_OFF_READOUT},
        "scope_notes": [
            "N=6 real passages / 15 entities / oracle roles (gold in, no extraction) -- exploratory.",
            "Coref is SUPPLIED by the gold (pronoun chains pre-resolved); this probe tests WM "
            "maintenance/update, NOT coref resolution.",
            "LAST-CLAUSE control is UNDERPOWERED on this starter gold (Finding 2): most entities "
            "recur in the final clause, so it is not yet a clean discriminator.",
            "Query semantics = CURRENT/final gold role per entity (Finding 1: situation-model "
            "holds current state, not history).",
        ],
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
    mode = "self_test" if args.self_test else "full"
    units, elapsed, seeds, lc_base = run_all(mode)
    verdict, summary = decide_verdict(units, seeds)
    metrics = _write_metrics(verdict, summary, units, elapsed, mode, lc_base)
    print("VERDICT:", verdict, flush=True)
    print(json.dumps(metrics["verdict_msg"]), flush=True)


if __name__ == "__main__":
    main()
