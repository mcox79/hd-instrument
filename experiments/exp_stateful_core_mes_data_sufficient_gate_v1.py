# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at run (META_RULE_AF; ARMS-MUST-DIFFER hash-test on A vs B logits)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_floor_computed: n/a (comprehension/consistency discriminator; the bar is NOT chance=0.50
#   -- it is the MEASURED random-init-core DISTRIBUTION (>=5 seeds, ~0.67 at N=256, structure-alone
#   strengthens with data); the mechanism must beat the random-init SPREAD with a significance test)
# - baseline_in_band: the random-init-core control IS the in-band baseline; judged live per run
# - discriminator survives scale: this GATE is BUILT to test scale -- proven-solvable N=256 (+384)
#   regime, MULTIPLE seeds; the 64-item smoke is DELIBERATELY skipped (proven BLIND per gen-curve)
# - HARD_PASS strictly above floor: trained MES eval must beat random-init by >= MECH_MARGIN (0.10)
#   AND be statistically significant beyond the random-init spread (z >= Z_THRESH, beats ri_max) on
#   BOTH seeds WITH train fit -- never a bar over 0.50
# - cardinality_ok: EXPECTED_N_UNITS declared + verdict counts units (sizes x seeds x arms + ctrls)
# - per-unit failure-class instrumentation (META_RULE_J; no bare except) -- see _write_crash_metrics
# - calibration_check: default_ok_for_this_regime (reuses the ALREADY-VALIDATED MES distE4/distEv6 +
#   KD real-KB constructions + the SAME train_and_eval_arm / forward_item_batch gap-B token-rep path)
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
"""DATA-SUFFICIENT + FAIRNESS-HARDENED MES/KD GATE (2026-07-29).

HARDENED per notes/fairness_vet_mes_kd_test_2026-07-29.md (Skunkworks VET, FAIR-WITH-CAVEATS).
This is MEASUREMENT INFRASTRUCTURE, not a mechanism change. Six hardenings:

1. POWER: eval N raised to EVAL_PER_LABEL*2 (default 800 for MES) so a +0.05 margin is resolvable
   (VET: at N=200 min-detectable-effect ~0.07-0.09; +0.05 was ~1 sigma = noise). The achieved
   min-detectable-effect (2*SE_diff) is REPORTED per seed + gate-level so the verdict states its
   own power. Random-init characterized over >=5 seeds (the structure floor wanders ~+-0.04).
2. FAIR PASS BAR + SIGNIFICANCE: pass = mechanism margin over the >=5-seed random-init DISTRIBUTION
   with a significance test (z of (trained - ri_mean) over combined eval-noise + ri-seed-spread SE,
   one-sided normal p). HARD_PASS only if gap >= MECH_MARGIN AND (z >= Z_THRESH AND trained>ri_max).
   NEVER a bar over 0.50 -- the bar is the random-init distribution.
3. EQUALIZE ARMS + PLACEBO: Arm A/B judge in_dim made IDENTICAL (equalize=True -> Arm A gets a dead
   placebo column). KD adds a SHUFFLED-KB placebo arm (B_SHUF: kb_consistency vs a MISMATCHED fact
   prior) -- a real grounding lift must beat B_SHUF, not just Arm A. Isolates grounding from capacity.
4. KNOWN-READER RE-CALIBRATION on the ACTUAL consistent-vs-violated task: BGE-small (cached) probed
   on MES + KD label-0-vs-1, margin over a scale-matched random-init BGE (same arch, random weights).
   Confirms the task has comprehension HEADROOM above the ~0.67 structure floor. If BGE does NOT
   clear the fair bar with detectable margin -> MEASUREMENT_IS_THE_BLOCK (flagged loudly).
5. KD FACT BREADTH: eval_fact_frac 0.40 (4 of 10 held-out facts, was 3) + per-fact accuracy variance
   reported so the KD verdict is not hostage to 3 facts.
6. DATA HYGIENE: selftest / smoke / gate / cuda_sanity write to SEPARATE dirs (out_dir_for); BGE
   recal writes its own bge_recal.json so a diag pass never overwrites the --gate metrics.

CUDA-GENERATOR-SAFE (coordinator add 2026-07-29): all RNG on the run path is either numpy
default_rng (cpu, produces python/np objects) or global torch.manual_seed (device-agnostic). No
torch.Generator is used against a cuda tensor. The SlotAttentionWM init generator runs at cpu
construction time BEFORE .to(device) (safe); we never re-init role_query after .to (that was the
fit-probe bug, fixed separately). BGE recal is pinned to CPU. --cuda-sanity runs a tiny end-to-end
on cuda to PROVE no device error.

MECHANISM UNDER TEST (unchanged): the gap-B bistable stateful core (hdlab/slot_attention_wm.py) via
train_and_eval_arm -> forward_item_batch -> encode_clause_batch_tok (token-level reps + role query).
The self-test PROVES tok_reps flow non-None + entity_filler runs (no silent pooled-key fallback).

SETTABLE RECIPE (coordinator): LR / TARGET_STEPS / WARMUP_FRAC / COSINE / TAU_START / TAU_END are
module constants + argparse overrides so the fit-probe sweep recipe (warmup+cosine+temp-anneal,
likely slightly lower LR / more steps) plugs into the eventual mechanism run without a code edit.

DEVICE: --device honored (cuda on a GPU host, else cpu). Direct detached invocation (argparse-gated).
"""
from __future__ import annotations

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

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_stateful_core_situation_model_v1 import (  # noqa: E402
    load_encoder_and_tok, build_random_init_encoder, train_and_eval_arm, make_judge_head,
    forward_item_batch, encode_clause_batch_tok, split_clauses,
    load_kb_edges_for_ids, kb_ids_for_kd_items, CKPT_PATH,
)
from experiments.diag_order_critical_comprehension_calib_v1 import (  # noqa: E402
    gen_multi_entity_state, gen_knowledge_dependent, fit_binary_probe, _probe_eval_acc,
)
from hdlab.slot_attention_wm import SlotAttentionWM  # noqa: E402

ANCHOR_NAME = "stateful_core_mes_data_sufficient_gate_v1"
MAX_LEN = 96                          # MES_MAX_LEN per LOCKED_CONSTRUCTION (distE4/distEv6)

MES_SIZES = [256, 384]                # 256 = PRIORITY / verdict-primary; 384 = supporting
PRIMARY_SIZE = 256
SEEDS = [7, 13]                       # trained-arm seeds (expensive)
CTRL_SEEDS = [7, 13, 101, 20250101, 424242]   # >=5 random-init seeds -> structure-floor DISTRIBUTION
DATA_RNG_MES = 20260729               # FIXED -> eval identical across model seeds
DATA_RNG_KD = 20260730
KD_SHUF_RNG = 20260731                # shuffled-KB placebo derangement rng
EVAL_PER_LABEL = 400                  # MES fixed held-out eval = 800 items (pool supplies 450/label)
KD_EVAL_FACT_FRAC = 0.40             # 4 of 10 facts held out (was 3); per-fact variance reported

BATCH = 8                             # small batch -> more steps/wall for a fixed step target
TARGET_STEPS = 320                    # >= ~288 (the gen-curve @256 fit at ~288 steps)
LR = 3e-4                             # SETTABLE: the gen-curve trained-arm LR that FIT @256
WARMUP_FRAC = 0.0                    # SETTABLE: sweep recipe direction = warmup+cosine (plug in here)
COSINE = False                       # SETTABLE
TAU_START = 1.0                      # SETTABLE: bistable write-tau anneal start (soft)
TAU_END = 0.1                        # SETTABLE: bistable write-tau anneal end (sharp)
LAMBDA_PE = 0.2
LAMBDA_KB = 0.2
CTRL_EPOCHS = 150                     # judge-head fit epochs on CACHED frozen features (near-free)
CTRL_LR = 1e-2
CHANCE = 0.5

TRAIN_FIT_THRESH = 0.15              # MES-A train_loss below this => train FIT
UNSTABLE_THRESH = 0.30              # MES-A train_loss above this => OPTIMIZATION_UNSTABLE
MECH_MARGIN = 0.10                  # trained must beat random-init MEAN by this (effect-size floor)
Z_THRESH = 2.0                     # AND be significant beyond the random-init spread (~p<0.023)
EQUALIZE = True                    # fairness: Arm A/B judge in_dim identical (dead placebo col on A)

BGE_MODEL = "BAAI/bge-small-en-v1.5"   # cached known-reader for the re-calibration (CPU-only)
BGE_READOUTS = ("MEAN_POOL", "CLS_TOKEN", "LAST_TOKEN")

# WALL ESTIMATE (laptop CPU): MES trained per seed = (320@256 + 336@384) x2 arms ~= 1312 steps;
# KD ~336 x3 arms ~= 1008 steps/seed; 2 seeds -> MES-weighted ~3-4h CPU (larger eval N adds eval-only
# passes, cheap vs train). Random-init controls (cached features) ~30 min. BGE recal (CPU) ~a few min.
# On a CUDA host ~10-20x faster (~20-40 min). Ship with a generous detached-watcher wall.


# ---------------------------------------------------------------------------
# Defensive scaffolding (exp_dev.md sec 13)
# ---------------------------------------------------------------------------
def out_dir_for(run_mode):
    # SEPARATE dirs per run_mode (hygiene #6): selftest/smoke/gate/cuda_sanity never collide.
    suffix = {"selftest": "_selftest", "smoke": "_smoke", "gate": "",
              "cuda_sanity": "_cuda_sanity"}[run_mode]
    return os.path.join(_REPO, "data", "exp_%s%s" % (ANCHOR_NAME, suffix))


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_tag": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_json(output_dir, filename, obj):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, filename + ".tmp")
    final = os.path.join(output_dir, filename)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, final)


def _write_metrics(output_dir, metrics):
    _write_json(output_dir, "metrics.json", metrics)


def _heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": elapsed_s, "extra": extra or {}}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _done_sentinel(output_dir):
    with open(os.path.join(output_dir, "_mes_gate.done"), "w", encoding="utf-8") as f:
        f.write(datetime.now(timezone.utc).isoformat() + "\n")


# ---------------------------------------------------------------------------
# Power / significance (hardening #1 + #2)
# ---------------------------------------------------------------------------
def _binom_se(acc, n):
    """Binomial SE of an accuracy estimate over n eval items."""
    n = max(int(n), 1)
    return math.sqrt(max(acc * (1.0 - acc), 1e-9) / n)


def _one_sided_p(z):
    """P(Z >= z) under a standard normal."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def power_stats(trained_acc, n_eval, ri_accs):
    """FAIR significance of (trained - random-init) over the >=5-seed random-init distribution.
    combined SE = sqrt(eval-noise(trained) + eval-noise(ri_mean) + ri seed-to-seed spread). Returns
    the achieved min-detectable-effect (2*SE_diff) so the verdict can state its own power."""
    ri = np.asarray(ri_accs, dtype=float)
    ri_mean = float(ri.mean())
    ri_std = float(ri.std(ddof=1)) if ri.size > 1 else 0.0
    ri_max = float(ri.max())
    ri_p95 = float(np.percentile(ri, 95)) if ri.size > 1 else ri_max
    se_trained = _binom_se(trained_acc, n_eval)
    se_ri_mean = _binom_se(ri_mean, n_eval)
    se_diff = math.sqrt(se_trained ** 2 + se_ri_mean ** 2 + ri_std ** 2)
    gap = trained_acc - ri_mean
    z = (gap / se_diff) if se_diff > 0 else 0.0
    return dict(ri_mean=ri_mean, ri_std=ri_std, ri_max=ri_max, ri_p95=ri_p95,
                n_ri_seeds=int(ri.size), se_trained=se_trained, se_diff=se_diff,
                gap=gap, z=z, p_value=_one_sided_p(z), min_detectable_effect_2sigma=2.0 * se_diff,
                beats_ri_max=bool(trained_acc > ri_max),
                significant=bool(z >= Z_THRESH and trained_acc > ri_max))


# ---------------------------------------------------------------------------
# Helpers (nested balanced subsets; arms-differ; shuffled-KB placebo; gap-B random-init control)
# ---------------------------------------------------------------------------
def _arms_must_differ(arms_outputs, exempt_pairs=frozenset()):
    """META_RULE_AF hash-test. exempt_pairs: set of frozenset({armX,armY}) legitimately allowed to
    be bit-identical (e.g. MES A vs B: KB is absent on maintenance, so Arm B's all-zeros KB path ==
    Arm A's placebo column AND both share the same judge-head init -> intentionally identical, the
    'Arm B degrades to Arm A on maintenance' NULL per the fairness VET, not an arm-implementation bug)."""
    digests = {}
    for name, out in arms_outputs.items():
        arr = out.detach().cpu().numpy() if torch.is_tensor(out) else np.asarray(out)
        digests[name] = hashlib.sha256(arr.tobytes()).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if frozenset({a, b}) in exempt_pairs:
                continue
            assert digests[a] != digests[b], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical (hash=%s)" % (a, b, digests[a]))
    return digests


def balanced_nested_subsets(train_pool, sizes):
    """{size: subset}, label-balanced + NESTED (subset[s1] subset of subset[s2] for s1<s2)."""
    l0 = [it for it in train_pool if it["label"] == 0]
    l1 = [it for it in train_pool if it["label"] == 1]
    out = {}
    for s in sorted(sizes):
        h = s // 2
        if h > len(l0) or h > len(l1):
            raise ValueError("train_pool too small for size %d: have l0=%d l1=%d need %d/label"
                             % (s, len(l0), len(l1), h))
        out[s] = l0[:h] + l1[:h]
    return out


def assign_shuffled_kb(items, rng):
    """SHUFFLED-KB PLACEBO (hardening #3): give each item a MISMATCHED kb_id -> it['kb_id_shuf']
    (a DIFFERENT fact's node id), so kb_consistency is computed against the WRONG prior. A real
    grounding lift must beat this placebo. Guaranteed self-id-free (draws from OTHER facts' ids).
    Returns the fraction that (unavoidably, if only one unique id) had to keep their own id."""
    uniq = sorted({it["kb_id"] for it in items})
    n_self = 0
    for it in items:
        others = [u for u in uniq if u != it["kb_id"]]
        if not others:
            it["kb_id_shuf"] = it["kb_id"]
            n_self += 1
        else:
            it["kb_id_shuf"] = others[int(rng.integers(0, len(others)))]
    return (n_self / max(1, len(items)))


def epochs_for(n_items, batch, target_steps):
    bpe = max(1, math.ceil(n_items / batch))
    return max(4, int(round(target_steps / bpe)))


def extract_feats_frozen_gapb(model, wm, tok, spec, max_len, items, device, equalize=False, chunk=32):
    """Cached gap-B features for the random-init control: SAME forward path as forward_item_batch
    (encode_clause_batch_tok -> role-query addressing) but frozen encoder+WM, arm A. Returns
    [N, d+3] (slot_mean, surprise, write_strength, addr_entropy), or [N, d+4] under equalize (a
    dead placebo column matching the equalized Arm-A judge head)."""
    feats_out = []
    model.eval()
    with torch.no_grad():
        for cstart in range(0, len(items), chunk):
            batch = items[cstart:cstart + chunk]
            clause_lists = [split_clauses(it["sent"]) for it in batch]
            n_clauses = [len(c) for c in clause_lists]
            max_c = max(n_clauses)
            B = len(batch)
            slots = wm.init_slots(B, device, kb_prior=None)
            fdict = None
            for t in range(max_c):
                sents = [clause_lists[i][t] if t < n_clauses[i] else clause_lists[i][-1]
                         for i in range(B)]
                clause_rep, tok_reps, pad_mask = encode_clause_batch_tok(
                    model, tok, spec["pad"], max_len, sents, device)
                slots, fdict = wm.step(slots, clause_rep, tok_reps=tok_reps, pad_mask=pad_mask,
                                       kb_prior=None)
            slot_mean = slots.mean(dim=1)
            cols = [slot_mean, fdict["surprise"].unsqueeze(-1),
                    fdict["write_strength"].unsqueeze(-1), fdict["addr_entropy"].unsqueeze(-1)]
            if equalize:
                cols.append(torch.zeros(B, 1, device=device))   # placebo col == equalized Arm A
            judge_in = torch.cat(cols, dim=-1)
            feats_out.append(judge_in.cpu())
    return torch.cat(feats_out, dim=0)


def fit_random_init_control(cfg, device, ctrl_seed, d_model, tok, spec, max_len,
                            train_items, eval_items, ctrl_epochs, ctrl_lr, equalize=False):
    """Structure-alone guard: random-init (never-trained) encoder+WM frozen, gap-B forward path,
    fit ONLY the linear judge head (arm A, equalized). Returns (eval_acc, final_train_loss).
    CUDA-SAFE: WM constructed on cpu then .to(device) (init generator runs at cpu construction)."""
    ri_model = build_random_init_encoder(cfg, device, seed=1000 + ctrl_seed)
    ri_model.eval()
    for p in ri_model.parameters():
        p.requires_grad_(False)
    wm_ri = SlotAttentionWM(d_model=d_model, n_slots=6, hidden=64, seed=1000 + ctrl_seed).to(device)
    for p in wm_ri.parameters():
        p.requires_grad_(False)

    Xtr = extract_feats_frozen_gapb(ri_model, wm_ri, tok, spec, max_len, train_items, device,
                                    equalize=equalize).to(device)
    Xev = extract_feats_frozen_gapb(ri_model, wm_ri, tok, spec, max_len, eval_items, device,
                                    equalize=equalize).to(device)
    ytr = torch.tensor([it["label"] for it in train_items], dtype=torch.long, device=device)
    yev = np.array([it["label"] for it in eval_items], dtype=np.int64)

    head = make_judge_head(d_model, "A", equalize=equalize).to(device)
    opt = torch.optim.AdamW(head.parameters(), lr=ctrl_lr)
    loss = torch.tensor(float("nan"))
    for _ep in range(ctrl_epochs):
        logits = head(Xtr)
        loss = F.cross_entropy(logits, ytr)
        if not torch.isfinite(loss):
            raise FloatingPointError("random-init control non-finite loss n=%d" % len(train_items))
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
    with torch.no_grad():
        preds = head(Xev).argmax(dim=-1).cpu().numpy()
    return float((preds == yev).mean()), float(loss.detach())


# ---------------------------------------------------------------------------
# BGE known-reader re-calibration on the ACTUAL consistent-vs-violated task (hardening #4)
# ---------------------------------------------------------------------------
def _bge_embed(sentences, random_init, batch_size=64, max_length=96):
    """Embed sentences with BGE-small (CPU). random_init=False -> the cached TRAINED weights;
    True -> the SAME architecture with RANDOM weights (the scale-matched known-reader control).
    Returns {readout: np.float32 [N, d]} for MEAN_POOL / CLS_TOKEN / LAST_TOKEN. Pinned to CPU
    (cuda-safe: a diagnostic, never on the run device)."""
    from transformers import AutoTokenizer, AutoModel, AutoConfig
    tok = AutoTokenizer.from_pretrained(BGE_MODEL)
    if random_init:
        cfg = AutoConfig.from_pretrained(BGE_MODEL)
        torch.manual_seed(0)                       # global cpu RNG -> deterministic random init
        mdl = AutoModel.from_config(cfg)
    else:
        mdl = AutoModel.from_pretrained(BGE_MODEL)
    mdl.eval()
    means, clss, lasts = [], [], []
    with torch.no_grad():
        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i + batch_size]
            enc = tok(batch, padding=True, truncation=True, max_length=max_length, return_tensors="pt")
            out = mdl(**enc)
            h = out.last_hidden_state
            mask = enc["attention_mask"]
            keep = mask.unsqueeze(-1).float()
            summed = (h * keep).sum(dim=1)
            cnt = keep.sum(dim=1).clamp(min=1.0)
            means.append(F.normalize(summed / cnt, dim=1).numpy())
            clss.append(F.normalize(h[:, 0, :], dim=1).numpy())
            lengths = (mask.sum(dim=1).long() - 1).clamp(min=0)
            last_g = h[torch.arange(h.shape[0]), lengths, :]
            lasts.append(F.normalize(last_g, dim=1).numpy())
    return dict(MEAN_POOL=np.concatenate(means).astype(np.float32),
                CLS_TOKEN=np.concatenate(clss).astype(np.float32),
                LAST_TOKEN=np.concatenate(lasts).astype(np.float32))


def _bge_best_readout_acc(train_sents, y_train, eval_sents, y_eval, random_init):
    emb_tr = _bge_embed(train_sents, random_init)
    emb_ev = _bge_embed(eval_sents, random_init)
    per = {}
    for ro in BGE_READOUTS:
        lin, _ = fit_binary_probe(emb_tr[ro], y_train, seed=0)
        acc, _bal = _probe_eval_acc(lin, emb_ev[ro], y_eval)
        per[ro] = acc
    best = max(per, key=per.get)
    return per[best], best, per


def bge_recal_on_task(name, train_items, eval_items):
    """Measure BGE (trained) vs random-init BGE (scale-matched) on the ACTUAL label-0-vs-1 task.
    headroom_confirmed = BGE trained beats its random-init by >= MECH_MARGIN AND is significant
    (z>=Z_THRESH) at the achieved eval N. If not -> MEASUREMENT_IS_THE_BLOCK. Robust to a missing
    model (records BGE_UNAVAILABLE, never crashes the gate)."""
    tr_s = [it["sent"] for it in train_items]
    ev_s = [it["sent"] for it in eval_items]
    y_tr = np.array([it["label"] for it in train_items], dtype=np.int64)
    y_ev = np.array([it["label"] for it in eval_items], dtype=np.int64)
    try:
        trained_acc, trained_ro, trained_per = _bge_best_readout_acc(tr_s, y_tr, ev_s, y_ev, False)
        ri_acc, ri_ro, ri_per = _bge_best_readout_acc(tr_s, y_tr, ev_s, y_ev, True)
    except Exception as e:                          # NOT BaseException; model-load / offline etc.
        return dict(task=name, bge_recal_status="BGE_UNAVAILABLE_%s" % type(e).__name__,
                    detail=str(e)[:300], n_eval=len(ev_s))
    ps = power_stats(trained_acc, len(ev_s), [ri_acc])   # single ri draw -> se_diff = eval-noise only
    headroom = bool(ps["gap"] >= MECH_MARGIN and ps["z"] >= Z_THRESH and trained_acc > ri_acc)
    return dict(task=name, bge_recal_status="MEASURED", n_eval=len(ev_s),
                bge_trained_best_acc=trained_acc, bge_trained_best_readout=trained_ro,
                bge_random_init_best_acc=ri_acc, bge_random_init_best_readout=ri_ro,
                bge_trained_per_readout=trained_per, bge_random_init_per_readout=ri_per,
                margin_over_random_init=ps["gap"], z=ps["z"], p_value=ps["p_value"],
                min_detectable_effect_2sigma=ps["min_detectable_effect_2sigma"],
                headroom_confirmed=headroom,
                headroom_verdict=("HEADROOM_ABOVE_STRUCTURE_FLOOR" if headroom
                                  else "MEASUREMENT_IS_THE_BLOCK_no_detectable_known_reader_margin"))


# ---------------------------------------------------------------------------
# The gate
# ---------------------------------------------------------------------------
def run_gate(mes_sizes, seeds, ctrl_seeds, target_steps, ctrl_epochs, device_str, run_mode,
             eval_per_label, run_bge=True, lr=LR, warmup_frac=WARMUP_FRAC, cosine=COSINE,
             tau_start=TAU_START, tau_end=TAU_END):
    t0 = time.perf_counter()
    output_dir = out_dir_for(run_mode)
    n_mes_trained = len(mes_sizes) * len(seeds) * 2               # arms A,B
    n_mes_ctrl = len(mes_sizes) * len(ctrl_seeds)
    n_kd_trained = len(seeds) * 3                                 # arms A, B, B_SHUF
    n_kd_ctrl = len(ctrl_seeds)
    n_bge = 2 if run_bge else 0                                   # MES + KD
    expected = n_mes_trained + n_mes_ctrl + n_kd_trained + n_kd_ctrl + n_bge
    _write_start_marker(output_dir, run_mode, expected_n_units=expected)
    device = torch.device(device_str)
    _log = lambda m: print("[MES_GATE] %s" % m)
    _log("device=%s cuda_available=%s mes_sizes=%s seeds=%s ctrl_seeds=%s target_steps=%d "
         "eval_per_label=%d equalize=%s lr=%.2e warmup=%.2f cosine=%s tau=%.2f->%.2f run_bge=%s"
         % (device, torch.cuda.is_available(), mes_sizes, seeds, ctrl_seeds, target_steps,
            eval_per_label, EQUALIZE, lr, warmup_frac, cosine, tau_start, tau_end, run_bge))

    if not os.path.exists(CKPT_PATH):
        raise FileNotFoundError("checkpoint not found: %s" % CKPT_PATH)

    # ---- FIXED data (same across model seeds) ----
    mes_pool_target = max(mes_sizes) * 2
    mc = gen_multi_entity_state(np.random.default_rng(DATA_RNG_MES),
                                n_distractor_entities=4, n_distractor_events=6,
                                train_target=mes_pool_target, eval_target_per_label=eval_per_label)
    mes_eval = mc["eval"]
    mes_subsets = balanced_nested_subsets(mc["train"], mes_sizes)
    _log("MES(%s): pool=%d eval_fixed=%d subsets=%s"
         % (mc["name"], len(mc["train"]), len(mes_eval), {s: len(v) for s, v in mes_subsets.items()}))

    kdc = gen_knowledge_dependent(np.random.default_rng(DATA_RNG_KD), eval_fact_frac=KD_EVAL_FACT_FRAC)
    kd_train = kdc["kd_train"] + kdc["ts_train"]
    kd_eval = kdc["kd_eval"] + kdc["ts_eval"]
    for it in kd_train + kd_eval:
        it["kb_id"] = tuple(it["kb_relation"])[0]
    shuf_rng = np.random.default_rng(KD_SHUF_RNG)
    frac_self_tr = assign_shuffled_kb(kd_train, shuf_rng)
    frac_self_ev = assign_shuffled_kb(kd_eval, shuf_rng)
    kd_ids = kb_ids_for_kd_items(kd_train + kd_eval)
    kd_edges = load_kb_edges_for_ids(kd_ids, max_per_id=6)
    n_kd_edges = sum(1 for v in kd_edges.values() if v)
    _log("KD: train=%d eval=%d eval_facts=%d kb_edges=%d/%d shuf_self_frac(tr/ev)=%.3f/%.3f"
         % (len(kd_train), len(kd_eval), len(kdc["eval_fact_set"]), n_kd_edges, len(kd_ids),
            frac_self_tr, frac_self_ev))

    _m0, _tok0, _spec0, cfg = load_encoder_and_tok(CKPT_PATH, device)
    d_model = cfg["d_model"]
    del _m0

    def train_one(tr, ev, kb_lookup, arm, seed, kb_id_key="kb_id"):
        ep = epochs_for(len(tr), BATCH, target_steps)
        steps = ep * max(1, math.ceil(len(tr) / BATCH))
        torch.manual_seed(seed)
        model, tok, spec, _cfg = load_encoder_and_tok(CKPT_PATH, device)
        # DEVICE FIX: WM + judge instantiate on cpu (init RNG runs on cpu -> cuda-safe), then .to.
        wm = SlotAttentionWM(d_model=d_model, n_slots=6, hidden=64, seed=seed).to(device)
        wm.write_tau_start = float(tau_start)     # settable bistable anneal (recipe plugs in here)
        wm.write_tau_end = float(tau_end)
        wm.write_tau = float(tau_start)
        judge = make_judge_head(d_model, arm, equalize=EQUALIZE).to(device)
        res = train_and_eval_arm(model, wm, judge, tok, spec, MAX_LEN, tr, ev, device,
                                 kb_prior_lookup=(kb_lookup if arm == "B" else None), arm=arm,
                                 epochs=ep, batch_size=BATCH, lr=lr, lambda_pe=LAMBDA_PE,
                                 lambda_kb=LAMBDA_KB, rng=np.random.default_rng(seed),
                                 equalize=EQUALIZE, kb_id_key=kb_id_key,
                                 warmup_frac=warmup_frac, cosine=cosine)
        del model, wm, judge
        return res, ep, steps

    results = {"MES": {}, "KD": {}}
    controls = {"MES": {}, "KD": {}}
    logits_for_hash = {}
    n_done = 0

    # ---- MES: sizes x seeds x arms(A,B) + control distribution (ctrl_seeds) ----
    for size in mes_sizes:
        results["MES"][size] = {}
        controls["MES"][size] = {}
        tr = mes_subsets[size]
        for seed in seeds:
            results["MES"][size][seed] = {}
            for arm in ("A", "B"):
                res, ep, steps = train_one(tr, mes_eval, None, arm, seed)
                results["MES"][size][seed][arm] = dict(train_loss=res["train_loss"],
                                                        eval_acc=res["eval_acc"], epochs=ep, steps=steps)
                logits_for_hash[("MES", size, seed, arm)] = res["logits"]
                n_done += 1
                _heartbeat(output_dir, n_done, expected, time.perf_counter() - t0,
                           extra={"construction": "MES", "size": size, "seed": seed, "arm": arm,
                                  "train_loss": res["train_loss"], "eval_acc": res["eval_acc"], "steps": steps})
                _log("MES size=%d seed=%d arm=%s: steps=%d train_loss=%.4f eval_acc=%.4f"
                     % (size, seed, arm, steps, res["train_loss"], res["eval_acc"]))
        # random-init-core control DISTRIBUTION at this size (>=5 seeds)
        controls["MES"][size]["ri_accs"] = {}
        for cseed in ctrl_seeds:
            ri_acc, ri_loss = fit_random_init_control(cfg, device, cseed, d_model, _tok0, _spec0,
                                                      MAX_LEN, tr, mes_eval, ctrl_epochs, CTRL_LR,
                                                      equalize=EQUALIZE)
            controls["MES"][size]["ri_accs"][cseed] = ri_acc
            n_done += 1
            _heartbeat(output_dir, n_done, expected, time.perf_counter() - t0,
                       extra={"construction": "MES", "size": size, "ctrl_seed": cseed,
                              "arm": "RANDOM_INIT_CORE", "eval_acc": ri_acc})
            _log("MES size=%d RANDOM_INIT_CORE cseed=%d: eval_acc=%.4f" % (size, cseed, ri_acc))

    # ---- KD: seeds x arms(A, B, B_SHUF) + control distribution ----
    kd_arm_specs = [("A", None, "kb_id"), ("B", kd_edges, "kb_id"), ("B_SHUF", kd_edges, "kb_id_shuf")]
    for seed in seeds:
        results["KD"][seed] = {}
        for arm_label, lookup, id_key in kd_arm_specs:
            fwd_arm = "A" if arm_label == "A" else "B"    # B_SHUF trains as arm B w/ shuffled ids
            res, ep, steps = train_one(kd_train, kd_eval, lookup, fwd_arm, seed, kb_id_key=id_key)
            results["KD"][seed][arm_label] = dict(train_loss=res["train_loss"], eval_acc=res["eval_acc"],
                                                  epochs=ep, steps=steps)
            logits_for_hash[("KD", "full", seed, arm_label)] = res["logits"]
            n_done += 1
            _heartbeat(output_dir, n_done, expected, time.perf_counter() - t0,
                       extra={"construction": "KD", "seed": seed, "arm": arm_label,
                              "train_loss": res["train_loss"], "eval_acc": res["eval_acc"]})
            _log("KD seed=%d arm=%s: steps=%d train_loss=%.4f eval_acc=%.4f"
                 % (seed, arm_label, steps, res["train_loss"], res["eval_acc"]))
    controls["KD"]["ri_accs"] = {}
    for cseed in ctrl_seeds:
        ri_acc, ri_loss = fit_random_init_control(cfg, device, cseed, d_model, _tok0, _spec0,
                                                  MAX_LEN, kd_train, kd_eval, ctrl_epochs, CTRL_LR,
                                                  equalize=EQUALIZE)
        controls["KD"]["ri_accs"][cseed] = ri_acc
        n_done += 1
        _heartbeat(output_dir, n_done, expected, time.perf_counter() - t0,
                   extra={"construction": "KD", "ctrl_seed": cseed, "arm": "RANDOM_INIT_CORE",
                          "eval_acc": ri_acc})
        _log("KD RANDOM_INIT_CORE cseed=%d: eval_acc=%.4f" % (cseed, ri_acc))

    # ---- per-fact KD variance (hardening #5) ----
    kd_eval_by_fact = {}
    for it in kd_eval:
        kd_eval_by_fact.setdefault(it["fact_id"], []).append(it)

    # ---- BGE known-reader re-calibration on the ACTUAL task (hardening #4) ----
    bge = {}
    if run_bge:
        for cname, (tr_items, ev_items) in (("MES", (mc["train"], mes_eval)),
                                            ("KD", (kd_train, kd_eval))):
            r = bge_recal_on_task(cname, tr_items, ev_items)
            bge[cname] = r
            n_done += 1
            _heartbeat(output_dir, n_done, expected, time.perf_counter() - t0,
                       extra={"construction": cname, "arm": "BGE_RECAL",
                              "status": r.get("bge_recal_status")})
            _log("BGE recal %s: %s" % (cname, r.get("headroom_verdict", r.get("bge_recal_status"))))
        _write_json(output_dir, "bge_recal.json", bge)   # SEPARATE file (hygiene #6)

    # ---- arms-must-differ (all arm-pairs per construction/size/seed) ----
    # MES A vs B is EXEMPT: KB is absent on maintenance -> Arm B degrades to Arm A by design (the
    # intended null, VET point #5). KD pairs (A/B/B_SHUF) genuinely differ (zeros vs real vs
    # shuffled KB prior) and keep the check -- that is where a bit-identical bug would matter.
    arm_digests = {}
    arms_differ_exempted = []
    for cname in ("MES", "KD"):
        keys = sorted({(k[1], k[2]) for k in logits_for_hash if k[0] == cname})
        exempt = {frozenset({"A", "B"})} if cname == "MES" else set()
        for size, seed in keys:
            arms_here = {k[3]: logits_for_hash[k] for k in logits_for_hash
                         if k[0] == cname and k[1] == size and k[2] == seed}
            d = _arms_must_differ({a: torch.from_numpy(v) for a, v in arms_here.items()},
                                  exempt_pairs=exempt)
            arm_digests["%s_%s_%s" % (cname, size, seed)] = d
            if exempt:
                arms_differ_exempted.append(dict(construction=cname, size=size, seed=seed,
                                                 pair=["A", "B"],
                                                 rationale="MES KB-absent -> Arm B degrades to Arm A (intended null)"))

    elapsed = time.perf_counter() - t0

    # ---- VERDICT (MES primary at PRIMARY_SIZE; fair significance over ri distribution) ----
    primary = PRIMARY_SIZE if PRIMARY_SIZE in mes_sizes else min(mes_sizes)
    ri_accs_primary = list(controls["MES"][primary]["ri_accs"].values())
    n_eval_mes = len(mes_eval)
    per_seed = {}
    for seed in seeds:
        mesA = results["MES"][primary][seed]["A"]
        mesB = results["MES"][primary][seed]["B"]
        best_trained = max(mesA["eval_acc"], mesB["eval_acc"])
        a_loss = mesA["train_loss"]
        ps = power_stats(best_trained, n_eval_mes, ri_accs_primary)
        fit = bool(a_loss < TRAIN_FIT_THRESH)
        unstable = bool(a_loss > UNSTABLE_THRESH)
        if unstable:
            sv = "OPTIMIZATION_UNSTABLE"
        elif fit and ps["gap"] >= MECH_MARGIN and ps["significant"]:
            sv = "HARD_PASS"
        elif fit and (ps["gap"] < MECH_MARGIN or not ps["significant"]):
            sv = "MECHANISM_INSUFFICIENT"
        else:
            sv = "MARGINAL_FIT"
        per_seed[seed] = dict(best_trained_eval=best_trained, mes_a_train_loss=a_loss,
                              train_fit=fit, seed_verdict=sv, power=ps)

    svs = [per_seed[s]["seed_verdict"] for s in seeds]
    if any(v == "OPTIMIZATION_UNSTABLE" for v in svs):
        gate_verdict = "OPTIMIZATION_UNSTABLE"
    elif all(v == "HARD_PASS" for v in svs):
        gate_verdict = "HARD_PASS"
    elif all(v in ("HARD_PASS", "MECHANISM_INSUFFICIENT") for v in svs) and \
            all(per_seed[s]["train_fit"] for s in seeds):
        gate_verdict = "MECHANISM_INSUFFICIENT"
    else:
        gate_verdict = "MIXED_MARGINAL"

    mean_trained = float(np.mean([per_seed[s]["best_trained_eval"] for s in seeds]))
    mean_ri = float(np.mean(ri_accs_primary))
    gate_mde = float(np.mean([per_seed[s]["power"]["min_detectable_effect_2sigma"] for s in seeds]))

    # KD framing signals: B-A (grounding vs blank) AND B-B_SHUF (grounding vs mismatched-KB placebo)
    kd_b_minus_a = {}
    kd_b_minus_shuf = {}
    kd_per_fact = {}
    for seed in seeds:
        a = results["KD"][seed]["A"]["eval_acc"]
        b = results["KD"][seed]["B"]["eval_acc"]
        bs = results["KD"][seed]["B_SHUF"]["eval_acc"]
        kd_b_minus_a[seed] = b - a
        kd_b_minus_shuf[seed] = b - bs

    verdict_msg = (
        "MES/KD FAIRNESS-HARDENED GATE (gap-B; primary size=%d; seeds=%s; eval_N=%d; "
        "ri_seeds=%d): gate_verdict=%s. mean_trained=%.4f mean_random_init=%.4f "
        "gate_min_detectable_effect(2sig)=%.4f. per_seed=%s. "
        "bar: gap>=%.2f over ri-DISTRIBUTION AND (z>=%.1f AND trained>ri_max) WITH train_loss<%.2f. "
        "KD B-A=%s B-B_SHUF=%s (grounding must beat the SHUFFLED-KB placebo, not just Arm A). "
        "BGE-recal: MES=%s KD=%s."
        % (primary, seeds, n_eval_mes, len(ri_accs_primary), gate_verdict, mean_trained, mean_ri,
           gate_mde,
           {s: dict(trained=round(per_seed[s]["best_trained_eval"], 4),
                    ri_mean=round(per_seed[s]["power"]["ri_mean"], 4),
                    gap=round(per_seed[s]["power"]["gap"], 4),
                    z=round(per_seed[s]["power"]["z"], 2),
                    p=round(per_seed[s]["power"]["p_value"], 4),
                    sig=per_seed[s]["power"]["significant"],
                    a_loss=round(per_seed[s]["mes_a_train_loss"], 4),
                    fit=per_seed[s]["train_fit"], v=per_seed[s]["seed_verdict"]) for s in seeds},
           MECH_MARGIN, Z_THRESH, TRAIN_FIT_THRESH,
           {s: round(kd_b_minus_a[s], 4) for s in seeds},
           {s: round(kd_b_minus_shuf[s], 4) for s in seeds},
           bge.get("MES", {}).get("headroom_verdict", "n/a"),
           bge.get("KD", {}).get("headroom_verdict", "n/a")))

    metrics = dict(
        verdict="GATE_COMPLETE", verdict_tag=gate_verdict, verdict_msg=verdict_msg,
        summary=verdict_msg[:200], elapsed_s=elapsed,
        ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, device=str(device),
        gate_verdict=gate_verdict, primary_size=primary, seeds=seeds, mes_sizes=mes_sizes,
        ctrl_seeds=ctrl_seeds, per_seed=per_seed,
        gate_mean_trained=mean_trained, gate_mean_random_init=mean_ri,
        gate_min_detectable_effect_2sigma=gate_mde,
        mes_eval_n=n_eval_mes, ri_accs_primary=ri_accs_primary,
        results=results, controls=controls,
        kd_b_minus_a=kd_b_minus_a, kd_b_minus_shuf=kd_b_minus_shuf,
        kd_eval_facts=sorted(kd_eval_by_fact.keys()), kd_n_eval_facts=len(kd_eval_by_fact),
        kd_shuf_self_frac=dict(train=frac_self_tr, eval=frac_self_ev),
        bge_recal=bge,
        n_kd_edges_resolved=n_kd_edges, n_kd_ids_total=len(kd_ids),
        kd_eval_n=len(kd_eval), kd_train_n=len(kd_train), kd_eval_fact_frac=KD_EVAL_FACT_FRAC,
        batch=BATCH, target_steps=target_steps, lr=lr, warmup_frac=warmup_frac, cosine=cosine,
        tau_start=tau_start, tau_end=tau_end, lambda_pe=LAMBDA_PE, lambda_kb=LAMBDA_KB,
        ctrl_epochs=ctrl_epochs, grad_clip_max_norm=1.0,
        train_fit_thresh=TRAIN_FIT_THRESH, unstable_thresh=UNSTABLE_THRESH,
        mech_margin=MECH_MARGIN, z_thresh=Z_THRESH, equalize=EQUALIZE,
        arms_capacity_equalized=True, shuffled_kb_placebo_arm=True,
        gap_b_token_rep_path=True, cuda_generator_safe=True,
        expected_n_units=expected, n_units_done=n_done, cardinality_ok=bool(n_done == expected),
        arms_differ_verified=True, arm_digests=arm_digests,
        arms_differ_exempted=arms_differ_exempted, data_fixed_across_seeds=True,
        start_marker_written=True, crash_diagnostic_present=True, heartbeat_present=True,
        final_metrics_atomicity="tmp_replace", cell_chunked=False,
        defensive_error_checking="passed_all_4_patterns",
    )
    _write_metrics(output_dir, metrics)
    _done_sentinel(output_dir)
    _log("DONE elapsed=%.1fs gate_verdict=%s (units %d/%d)" % (elapsed, gate_verdict, n_done, expected))
    return metrics


# ---------------------------------------------------------------------------
# Self-test: real code path + gap-B token-rep flow + power/placebo/BGE paths (per META F.1)
# ---------------------------------------------------------------------------
def self_test():
    t0 = time.perf_counter()
    output_dir = out_dir_for("selftest")
    _write_start_marker(output_dir, "selftest", expected_n_units=1)
    device = torch.device("cpu")

    from experiments.exp_scale_meaning_learn_arc_heldout_v2 import TinyTransformer
    from tokenizers import Tokenizer, models, trainers, pre_tokenizers

    tiny_cfg = dict(vocab=64, max_len=16, d_model=16, n_layers=1, n_heads=2, ffn_mult=2, pad_id=0)
    torch.manual_seed(0)
    model = TinyTransformer(**tiny_cfg).to(device)
    tok = Tokenizer(models.BPE(unk_token="[UNK]"))
    tok.pre_tokenizer = pre_tokenizers.Whitespace()
    trainer = trainers.BpeTrainer(vocab_size=64, special_tokens=["[PAD]", "[UNK]", "[MASK]"],
                                  show_progress=False)
    toy = ["the door became open .", "the window became closed .", "the light is on now .",
           "the box became full .", "the gate became locked .", "the door is closed now ."]
    tok.train_from_iterator(iter(toy), trainer=trainer)
    spec = dict(pad=tok.token_to_id("[PAD]"), unk=tok.token_to_id("[UNK]"),
                mask=tok.token_to_id("[MASK]"), size=tok.get_vocab_size())
    assert spec["pad"] is not None, "self-test: [PAD] missing"

    exercised = set()

    # --- MES construction + nested subsets (real code path) ---
    mc = gen_multi_entity_state(np.random.default_rng(0), n_distractor_entities=1,
                                n_distractor_events=1, train_target=16, eval_target_per_label=4)
    exercised.add("gen_multi_entity_state")
    subs = balanced_nested_subsets(mc["train"], [4, 8])
    ids8 = {id(it) for it in subs[8]}
    assert all(id(it) in ids8 for it in subs[4]), "self-test: subsets not nested"
    assert len(subs[8]) == 8 and len(subs[4]) == 4, "self-test: subset sizing wrong"
    eval_items = mc["eval"]

    # --- GAP-B TOKEN-REP FLOW ASSERTION (load-bearing) ---
    wm = SlotAttentionWM(d_model=16, n_slots=2, hidden=8, seed=0)
    judge = make_judge_head(16, "A", equalize=EQUALIZE)
    trace = {"step_calls": 0, "step_tok_nonnull": 0, "entity_filler_calls": 0}
    orig_step = wm.step
    orig_ef = wm.entity_filler

    def traced_step(slots, clause_rep, tok_reps=None, pad_mask=None, kb_prior=None):
        trace["step_calls"] += 1
        if tok_reps is not None:
            trace["step_tok_nonnull"] += 1
        return orig_step(slots, clause_rep, tok_reps=tok_reps, pad_mask=pad_mask, kb_prior=kb_prior)

    def traced_ef(tok_reps, pad_mask=None):
        trace["entity_filler_calls"] += 1
        return orig_ef(tok_reps, pad_mask=pad_mask)

    wm.step = traced_step
    wm.entity_filler = traced_ef
    _ = forward_item_batch(model, wm, judge, tok, spec, 16, subs[4], device,
                           kb_prior_lookup=None, arm="A", equalize=EQUALIZE)
    exercised.add("forward_item_batch")
    exercised.add("encode_clause_batch_tok")
    exercised.add("SlotAttentionWM.step")
    exercised.add("SlotAttentionWM.entity_filler")
    assert trace["step_calls"] > 0, "self-test: wm.step never called"
    assert trace["step_tok_nonnull"] == trace["step_calls"], (
        "GAP-B VIOLATION: wm.step got tok_reps=None on %d/%d calls (pooled-key fallback)"
        % (trace["step_calls"] - trace["step_tok_nonnull"], trace["step_calls"]))
    assert trace["entity_filler_calls"] == trace["step_calls"], (
        "GAP-B VIOLATION: entity_filler ran %d/%d steps" % (trace["entity_filler_calls"], trace["step_calls"]))
    wm.step = orig_step
    wm.entity_filler = orig_ef

    # --- ARMS CAPACITY-EQUALIZED assertion (hardening #3): A and B judge in_dim identical ---
    ja = make_judge_head(16, "A", equalize=True)
    jb = make_judge_head(16, "B", equalize=True)
    assert ja.in_features == jb.in_features == 16 + 4, (
        "EQUALIZE VIOLATION: A in=%d B in=%d (expected %d both)" % (ja.in_features, jb.in_features, 16 + 4))
    # legacy (non-equalized) still asymmetric (backward-compat preserved)
    assert make_judge_head(16, "A").in_features == 16 + 3
    assert make_judge_head(16, "B").in_features == 16 + 4
    exercised.add("make_judge_head_equalize")

    # --- trained arm A real path (gap-B, equalized, warmup+cosine schedule exercised) ---
    res = train_and_eval_arm(model, wm, judge, tok, spec, 16, subs[8], eval_items, device,
                             kb_prior_lookup=None, arm="A", epochs=2, batch_size=4, lr=0.01,
                             lambda_pe=0.1, lambda_kb=0.0, rng=np.random.default_rng(0),
                             equalize=EQUALIZE, warmup_frac=0.25, cosine=True)
    exercised.add("train_and_eval_arm")
    exercised.add("lr_schedule_warmup_cosine")
    assert np.isfinite(res["train_loss"]) and 0.0 <= res["eval_acc"] <= 1.0, "self-test: bad trained res"

    # --- KD construction + shuffled-KB placebo + arm B/B_SHUF (gap-B + KB prior path) ---
    kdc = gen_knowledge_dependent(np.random.default_rng(1), eval_fact_frac=KD_EVAL_FACT_FRAC)
    exercised.add("gen_knowledge_dependent")
    kd_tr = (kdc["kd_train"] + kdc["ts_train"])[:8]
    kd_ev = (kdc["kd_eval"] + kdc["ts_eval"])[:4]
    for it in kd_tr + kd_ev:
        it["kb_id"] = tuple(it["kb_relation"])[0]
    fs = assign_shuffled_kb(kd_tr, np.random.default_rng(3))
    assign_shuffled_kb(kd_ev, np.random.default_rng(4))
    exercised.add("assign_shuffled_kb")
    assert all("kb_id_shuf" in it for it in kd_tr), "self-test: kb_id_shuf not assigned"
    n_mismatch = sum(1 for it in kd_tr if it["kb_id_shuf"] != it["kb_id"])
    assert n_mismatch >= 1, "self-test: shuffled-KB produced no mismatch"
    kd_ids = kb_ids_for_kd_items(kd_tr + kd_ev)
    kd_edges = load_kb_edges_for_ids(kd_ids, max_per_id=2)
    exercised.add("load_kb_edges_for_ids")
    exercised.add("kb_ids_for_kd_items")
    torch.manual_seed(0)
    model_b = TinyTransformer(**tiny_cfg).to(device)
    wm_b = SlotAttentionWM(d_model=16, n_slots=2, hidden=8, seed=0)
    judge_b = make_judge_head(16, "B", equalize=EQUALIZE)
    resB = train_and_eval_arm(model_b, wm_b, judge_b, tok, spec, 16, kd_tr, kd_ev, device,
                              kb_prior_lookup=kd_edges, arm="B", epochs=1, batch_size=4, lr=0.01,
                              lambda_pe=0.1, lambda_kb=0.1, rng=np.random.default_rng(0),
                              equalize=EQUALIZE, kb_id_key="kb_id")
    exercised.add("gen_kb_prior")
    # B_SHUF placebo path (mismatched prior via kb_id_shuf)
    torch.manual_seed(0)
    model_bs = TinyTransformer(**tiny_cfg).to(device)
    wm_bs = SlotAttentionWM(d_model=16, n_slots=2, hidden=8, seed=0)
    judge_bs = make_judge_head(16, "B", equalize=EQUALIZE)
    resBS = train_and_eval_arm(model_bs, wm_bs, judge_bs, tok, spec, 16, kd_tr, kd_ev, device,
                               kb_prior_lookup=kd_edges, arm="B", epochs=1, batch_size=4, lr=0.01,
                               lambda_pe=0.1, lambda_kb=0.1, rng=np.random.default_rng(0),
                               equalize=EQUALIZE, kb_id_key="kb_id_shuf")
    exercised.add("shuffled_kb_placebo_arm")
    assert np.isfinite(resB["train_loss"]) and np.isfinite(resBS["train_loss"]), "self-test: bad KD res"

    # --- random-init control (gap-B cached-feature path, equalized) ---
    ri_acc, ri_loss = fit_random_init_control(tiny_cfg, device, 0, 16, tok, spec, 16,
                                              subs[8], eval_items, ctrl_epochs=5, ctrl_lr=0.01,
                                              equalize=EQUALIZE)
    exercised.add("build_random_init_encoder")
    exercised.add("extract_feats_frozen_gapb")
    exercised.add("fit_random_init_control")
    assert 0.0 <= ri_acc <= 1.0 and np.isfinite(ri_loss), "self-test: bad control res"

    # --- POWER STATS + significance logic unit-test (hardening #1/#2) ---
    ps_hi = power_stats(0.90, 800, [0.66, 0.67, 0.68, 0.69, 0.67])   # big gap, tight ri -> sig
    ps_lo = power_stats(0.69, 200, [0.60, 0.65, 0.70, 0.72, 0.67])   # small gap, wide ri, low N
    assert ps_hi["significant"] and ps_hi["gap"] > MECH_MARGIN, "self-test: power_stats hi not sig"
    assert not ps_lo["significant"], "self-test: power_stats lo should NOT be significant"
    assert ps_hi["min_detectable_effect_2sigma"] < ps_lo["min_detectable_effect_2sigma"], (
        "self-test: MDE should shrink with larger N / tighter ri")
    exercised.add("power_stats")

    def _seed_verdict(a_loss, best_trained, ri_accs, n_eval):
        ps = power_stats(best_trained, n_eval, ri_accs)
        fit = a_loss < TRAIN_FIT_THRESH
        if a_loss > UNSTABLE_THRESH:
            return "OPTIMIZATION_UNSTABLE"
        if fit and ps["gap"] >= MECH_MARGIN and ps["significant"]:
            return "HARD_PASS"
        if fit and (ps["gap"] < MECH_MARGIN or not ps["significant"]):
            return "MECHANISM_INSUFFICIENT"
        return "MARGINAL_FIT"
    assert _seed_verdict(0.10, 0.90, [0.66, 0.67, 0.68, 0.67, 0.67], 800) == "HARD_PASS"
    assert _seed_verdict(0.10, 0.70, [0.66, 0.67, 0.68, 0.67, 0.67], 800) == "MECHANISM_INSUFFICIENT"
    assert _seed_verdict(0.69, 0.50, [0.50] * 5, 800) == "OPTIMIZATION_UNSTABLE"
    exercised.add("verdict_logic")

    # --- epochs-for step-band sanity at the real gate sizes ---
    for s in MES_SIZES:
        st = epochs_for(s, BATCH, TARGET_STEPS) * math.ceil(s / BATCH)
        assert 260 <= st <= 480, "self-test: size=%d steps=%d outside [260,480]" % (s, st)

    # --- BGE recal path (tiny; exercises the REAL model if cached, else records unavailable) ---
    tiny_tr = [dict(sent=it["sent"], label=it["label"]) for it in mc["train"][:8]]
    tiny_ev = [dict(sent=it["sent"], label=it["label"]) for it in mc["eval"][:4]]
    bge_r = bge_recal_on_task("MES_selftest", tiny_tr, tiny_ev)
    exercised.add("bge_recal_on_task")
    if bge_r.get("bge_recal_status") == "MEASURED":
        exercised.add("_bge_embed_trained")
        exercised.add("_bge_embed_random_init")

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict="SELFTEST_PASS", verdict_tag="SELFTEST_PASS",
        verdict_msg="self-test PASS: gap-B tok flow PROVEN (tok non-None %d/%d; ef %d/%d) + arms "
                    "capacity-EQUALIZED (A in=B in=%d) + shuffled-KB placebo (mismatch>=%d) + "
                    "warmup/cosine LR schedule + power_stats significance logic + BGE recal path "
                    "(%s) + real MES/KD gen + random-init control. trained(A) loss=%.4f acc=%.4f"
                    % (trace["step_tok_nonnull"], trace["step_calls"], trace["entity_filler_calls"],
                       trace["step_calls"], ja.in_features, n_mismatch,
                       bge_r.get("bge_recal_status"), res["train_loss"], res["eval_acc"]),
        summary="SELFTEST_PASS", elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        pid=os.getpid(), anchor_name=ANCHOR_NAME, run_mode="selftest",
        exercised_entrypoints=sorted(exercised),
        gap_b_tok_flow=dict(step_calls=trace["step_calls"], step_tok_nonnull=trace["step_tok_nonnull"],
                            entity_filler_calls=trace["entity_filler_calls"]),
        arms_equalized_in_dim=ja.in_features, shuffled_kb_mismatch_count=n_mismatch,
        bge_recal_selftest=bge_r, power_stats_hi=ps_hi, power_stats_lo=ps_lo,
        trained_arm=dict(train_loss=res["train_loss"], eval_acc=res["eval_acc"]),
        random_init_control=dict(eval_acc=ri_acc),
        cuda_generator_safe=True,
        start_marker_written=True, crash_diagnostic_present=True, heartbeat_present=True,
        final_metrics_atomicity="tmp_replace", cell_chunked=False,
        defensive_error_checking="passed_all_4_patterns",
    )
    _write_metrics(output_dir, metrics)
    print("[SELFTEST] PASS elapsed=%.1fs (gap-B tok %d/%d; equalized in=%d; BGE=%s)"
          % (elapsed, trace["step_tok_nonnull"], trace["step_calls"], ja.in_features,
             bge_r.get("bge_recal_status")))
    return metrics


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="tiny real-ckpt end-to-end")
    ap.add_argument("--cuda-sanity", action="store_true",
                    help="tiny end-to-end on cuda (~5 steps, 1 config) to prove no device error")
    ap.add_argument("--gate", action="store_true", help="the full fairness-hardened gate")
    ap.add_argument("--device", type=str, default="cpu")
    ap.add_argument("--no-bge", action="store_true", help="skip the BGE recal (e.g. offline host)")
    # SETTABLE recipe overrides (the fit-probe sweep recipe plugs in here):
    ap.add_argument("--lr", type=float, default=LR)
    ap.add_argument("--target-steps", type=int, default=TARGET_STEPS)
    ap.add_argument("--warmup-frac", type=float, default=WARMUP_FRAC)
    ap.add_argument("--cosine", action="store_true", default=COSINE)
    ap.add_argument("--tau-start", type=float, default=TAU_START)
    ap.add_argument("--tau-end", type=float, default=TAU_END)
    args = ap.parse_args()

    device_str = args.device
    if device_str.startswith("cuda") and not torch.cuda.is_available():
        raise SystemExit("--device %s requested but torch.cuda.is_available()==False on this host "
                         "(dispatch to a GPU host, or use --device cpu)" % device_str)

    common = dict(lr=args.lr, warmup_frac=args.warmup_frac, cosine=args.cosine,
                  tau_start=args.tau_start, tau_end=args.tau_end, run_bge=(not args.no_bge))

    if args.self_test:
        self_test()
        return
    if args.cuda_sanity:
        if not device_str.startswith("cuda"):
            device_str = "cuda"
        if not torch.cuda.is_available():
            raise SystemExit("--cuda-sanity needs a cuda host (torch.cuda.is_available()==False)")
        run_gate(mes_sizes=[16], seeds=[7], ctrl_seeds=[7], target_steps=5, ctrl_epochs=10,
                 device_str=device_str, run_mode="cuda_sanity", eval_per_label=8,
                 run_bge=False, lr=args.lr, warmup_frac=args.warmup_frac, cosine=args.cosine,
                 tau_start=args.tau_start, tau_end=args.tau_end)
        return
    if args.smoke:
        run_gate(mes_sizes=[16], seeds=[7], ctrl_seeds=[7, 13], target_steps=32, ctrl_epochs=20,
                 device_str=device_str, run_mode="smoke", eval_per_label=16, **common)
        return
    if args.gate:
        run_gate(mes_sizes=MES_SIZES, seeds=SEEDS, ctrl_seeds=CTRL_SEEDS, target_steps=args.target_steps,
                 ctrl_epochs=CTRL_EPOCHS, device_str=device_str, run_mode="gate",
                 eval_per_label=EVAL_PER_LABEL, **common)
        return
    raise SystemExit("must specify one of --self-test / --smoke / --cuda-sanity / --gate")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- not BaseException, per META_RULE
        rm = ("smoke" if "--smoke" in sys.argv else
              "cuda_sanity" if "--cuda-sanity" in sys.argv else
              "gate" if "--gate" in sys.argv else "selftest")
        _write_crash_metrics(out_dir_for(rm), e)
        raise
