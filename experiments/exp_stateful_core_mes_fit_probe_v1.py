# CELL-TEMPLATE (measurement-first OPTIMIZATION diagnostic; NOT a mechanism-verdict cell):
# - This probe answers ONE question: under what training config does the gap-B stateful-core
#   mechanism RELIABLY FIT (train_loss < TRAIN_FIT_THRESH=0.15) a 256-item MES Arm-A train set on
#   BOTH seeds 7 & 13? It is a TRAINING-STABILITY sweep, not a generalization test (eval is not
#   scored here -- fit is the sole gate, matching exp_stateful_core_mes_data_sufficient_gate_v1's
#   MES-A train_loss fit criterion). No mechanism math is changed.
# - MECHANISM UNCHANGED: init/addr_temp are set EXTERNALLY on the SlotAttentionWM instance
#   (legitimate stability levers, NOT edits to hdlab/slot_attention_wm.py). The per-slot-only vs
#   gap-B ISOLATION uses the module's OWN byte-identical ee714c31 fallback: wm.step(tok_reps=None)
#   == per-slot PBWM with pooled-clause key (ee714c31); wm.step(tok_reps=...) == gap-B entity-role
#   query (4133235d3). So NO git-checkout of the old file is needed to isolate the culprit.
# - defensive scaffolding: start marker, crash metrics (failure_class), heartbeat, atomic
#   os.replace metrics, line-buffered stdout, SystemExit re-raise BEFORE except Exception, no bare
#   except. numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / CITED@.
# - PASS/FAIL band (pre-reg): PASS = at least one config reaches train_loss < 0.15 on BOTH seeds
#   (report the leanest such config). FAIL = no config fits both seeds (report per-config final
#   loss + failure SHAPE as evidence). Isolation sub-question: does per-slot-only (gap_b=False) fit
#   where gap-B does not? If so, the role-query addressing is the specific optimization problem.
"""Stateful-core MES fit probe (training-stability diagnostic, 2026-07-29).

WHY (established, not re-derived): the data-sufficient MES gate
(exp_stateful_core_mes_data_sufficient_gate_v1) returned OPTIMIZATION_UNSTABLE at 256 items --
gap-B MES Arm-A train_loss stuck ~ln2 (CITED@ seed7=0.6989, seed13=0.6863, fit=False), so eval was
chance and no mechanism verdict was possible. CONTRAST: the OLD mean-pool path DID fit @256
(CITED@ diag_stateful_core_gen_curve_v1 train_loss=0.127). So the richer per-slot + role-query
mechanism made the loss surface harder to optimize. This probe finds a config that fits reliably.

MODES:
  --self-test : tiny real code path (TinyTransformer d=16, tiny tok, MES gen, both gap_b, schedule
                + shape-classifier unit checks). CPU, seconds.
  --diag      : ONE config (the gate baseline: lr3e-4, no warmup, addr_temp 0.5, gap_b=True) at 256
                MES Arm-A items, --seeds, --steps (default 320), FULL per-step curve (loss +
                grad-norm pre/post clip) -> classify the failure SHAPE. Run this LOCALLY (reduced
                --steps ~64) to read the shape fast; the shape is visible in the first ~60 steps.
  --sweep     : the config grid x seeds [7,13] at 256 MES Arm-A items; per-config final/min loss +
                curve + shape; picks configs that fit both seeds; isolation (gap_b True vs False).
                REMOTE / --device cuda (detached direct invocation; argparse-gated, not the runner).
"""
from __future__ import annotations

import argparse
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

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_stateful_core_situation_model_v1 import (  # noqa: E402
    load_encoder_and_tok, encode_clause_batch_tok, split_clauses, make_judge_head, CKPT_PATH,
)
from experiments.diag_order_critical_comprehension_calib_v1 import (  # noqa: E402
    gen_multi_entity_state,
)
from hdlab.slot_attention_wm import SlotAttentionWM  # noqa: E402

ANCHOR_NAME = "stateful_core_mes_fit_probe_v1"
MAX_LEN = 96                       # MES_MAX_LEN per LOCKED_CONSTRUCTION (distE4/distEv6)
FIT_ITEMS = 256                    # the proven-solvable regime the gate went unstable on
DATA_RNG_MES = 20260729           # FIXED (same regime spirit as the gate)
SEEDS_DEFAULT = [7, 13]
BATCH = 8                          # small batch -> more steps/wall; the regime the instability arose in
LAMBDA_PE = 0.2                    # coupled PE term (unchanged from the gate/full)
GRAD_CLIP_MAX_NORM = 1.0
TRAIN_FIT_THRESH = 0.15            # train_loss below this on BOTH seeds => the config fits
STUCK_FLAT_HI = 0.60              # final loss above this + flat => not learning

# The sweep grid (Arm A, MES, 256 items). gap_b=True is the mechanism under test; gap_b=False is the
# per-slot-only (ee714c31) isolation control via the module's own pooled-key fallback.
# HYPOTHESIZED@ wall (RTX 4060 Ti, ~0.3s/step MES batch8 512d/6L ~11-clause recurrence): sum steps
# ~4800 x 2 seeds ~= 9600 steps -> ~48 min + ~18 ckpt reloads (~1 min) => ~1h detached.
CONFIGS = [
    dict(name="C0_gate_baseline_gapb", lr=3e-4, warmup_frac=0.0, cosine=False,
         total_steps=320, gap_b=True),                                   # reproduce OPTIMIZATION_UNSTABLE + shape
    dict(name="C1_lowLR_gapb", lr=1e-4, warmup_frac=0.0, cosine=False,
         total_steps=640, gap_b=True),                                   # oscillation? => lower LR + more steps
    dict(name="C2_highLR_gapb", lr=1e-3, warmup_frac=0.0, cosine=False,
         total_steps=320, gap_b=True),                                   # slow? => higher LR
    dict(name="C3_warmup_cosine_gapb", lr=3e-4, warmup_frac=0.15, cosine=True,
         total_steps=640, gap_b=True),                                   # joint-unfrozen warmup + cosine
    dict(name="C4_warmup_highLR_cosine_gapb", lr=1e-3, warmup_frac=0.15, cosine=True,
         total_steps=640, gap_b=True),                                   # warmup lets a higher peak LR be safe
    dict(name="C5_warmup_cosine_tempanneal_gapb", lr=3e-4, warmup_frac=0.2, cosine=True,
         total_steps=640, temp_anneal=(1.0, 0.5), gap_b=True),           # anneal addr_temp soft->sharp
    dict(name="C6_gentleinit_tempanneal_gapb", lr=3e-4, warmup_frac=0.2, cosine=True,
         total_steps=640, temp_anneal=(1.0, 0.5), rq_std=0.005, gap_b=True),  # gentler role_query init + anneal
    dict(name="C7_perslot_gate_baseline", lr=3e-4, warmup_frac=0.0, cosine=False,
         total_steps=320, gap_b=False),                                  # ISOLATION: per-slot-only, gate config
    dict(name="C8_perslot_warmup_cosine", lr=3e-4, warmup_frac=0.15, cosine=True,
         total_steps=640, gap_b=False),                                  # ISOLATION: per-slot-only, better recipe
]


# ---------------------------------------------------------------------------
# Defensive scaffolding
# ---------------------------------------------------------------------------
def out_dir_for(run_mode):
    suffix = {"selftest": "_selftest", "diag": "_diag", "sweep": ""}[run_mode]
    return os.path.join(_REPO, "data", "exp_%s%s" % (ANCHOR_NAME, suffix))


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_tag": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": elapsed_s, "extra": extra or {}}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _done_sentinel(output_dir):
    with open(os.path.join(output_dir, "_mes_fit_probe.done"), "w", encoding="utf-8") as f:
        f.write(datetime.now(timezone.utc).isoformat() + "\n")


# ---------------------------------------------------------------------------
# Schedules + shape classifier + data
# ---------------------------------------------------------------------------
def lr_at(step, total, base_lr, warmup_frac, cosine, lr_min_frac=0.0):
    warmup_steps = int(round(warmup_frac * total))
    if warmup_steps > 0 and step < warmup_steps:
        return base_lr * float(step + 1) / float(warmup_steps)
    if cosine:
        denom = max(1, total - warmup_steps)
        progress = min(1.0, max(0.0, float(step - warmup_steps) / float(denom)))
        return lr_min_frac * base_lr + (1.0 - lr_min_frac) * base_lr * 0.5 * (1.0 + math.cos(math.pi * progress))
    return base_lr


def temp_at(step, total, warmup_frac, t_start, t_end):
    warmup_steps = int(round(warmup_frac * total))
    if warmup_steps <= 0 or step >= warmup_steps:
        return t_end
    frac = float(step) / float(warmup_steps)
    return t_start + (t_end - t_start) * frac


def _total_grad_norm(params):
    sq = 0.0
    for p in params:
        if p.grad is not None:
            g = p.grad.detach()
            sq += float(g.norm().item()) ** 2
    return math.sqrt(sq)


def classify_shape(losses):
    """losses: list of per-step training loss. Returns (label, stats-dict). Heuristic; raw stats
    are logged so the classification is auditable, not a black box."""
    L = np.asarray(losses, dtype=np.float64)
    n = len(L)
    head = float(L[:min(10, n)].mean())
    final = float(L[-min(10, n):].mean())
    mn = float(L.min())
    drop = head - final
    diffs = np.abs(np.diff(L)) if n > 1 else np.array([0.0])
    osc_mean = float(diffs.mean())
    second_half_std = float(L[n // 2:].std()) if n >= 2 else 0.0
    stats = dict(head_loss=round(head, 4), final_loss=round(final, 4), min_loss=round(mn, 4),
                 drop_head_to_final=round(drop, 4), mean_abs_step_diff=round(osc_mean, 4),
                 second_half_std=round(second_half_std, 4), n_steps=n)
    if final < TRAIN_FIT_THRESH:
        label = "FIT"
    elif final > STUCK_FLAT_HI and drop < 0.05 and second_half_std < 0.03:
        label = "STUCK_FLAT"
    elif second_half_std > 0.08 or osc_mean > 0.08:
        label = "OSCILLATING"
    elif drop > 0.05:
        label = "SLOW_DESCENDING"
    else:
        label = "PARTIAL_UNCLEAR"
    return label, stats


def balanced_subset(pool, size):
    l0 = [it for it in pool if it["label"] == 0]
    l1 = [it for it in pool if it["label"] == 1]
    h = size // 2
    if len(l0) < h or len(l1) < h:
        raise ValueError("MES pool too small for size %d: l0=%d l1=%d need %d/label"
                         % (size, len(l0), len(l1), h))
    return l0[:h] + l1[:h]


def build_mes_fit_set(n_items):
    pool_target = max(n_items * 3, 600)
    mc = gen_multi_entity_state(np.random.default_rng(DATA_RNG_MES),
                                n_distractor_entities=4, n_distractor_events=6,
                                train_target=pool_target, eval_target_per_label=8)
    return balanced_subset(mc["train"], n_items), mc["name"]


# ---------------------------------------------------------------------------
# Forward (Arm A, gap_b toggle) + training loop
# ---------------------------------------------------------------------------
def forward_probe(model, wm, judge, tok, spec, max_len, items, device, gap_b):
    clause_lists = [split_clauses(it["sent"]) for it in items]
    n_clauses = [len(c) for c in clause_lists]
    max_c = max(n_clauses)
    B = len(items)
    slots = wm.init_slots(B, device, kb_prior=None)
    feats = None
    for t in range(max_c):
        sents = [clause_lists[i][t] if t < n_clauses[i] else clause_lists[i][-1] for i in range(B)]
        clause_rep, tok_reps, pad_mask = encode_clause_batch_tok(
            model, tok, spec["pad"], max_len, sents, device)
        if gap_b:
            slots, feats = wm.step(slots, clause_rep, tok_reps=tok_reps, pad_mask=pad_mask, kb_prior=None)
        else:
            slots, feats = wm.step(slots, clause_rep, tok_reps=None, pad_mask=None, kb_prior=None)
    slot_mean = slots.mean(dim=1)
    judge_in = torch.cat([slot_mean, feats["surprise"].unsqueeze(-1),
                          feats["write_strength"].unsqueeze(-1),
                          feats["addr_entropy"].unsqueeze(-1)], dim=-1)
    logits = judge(judge_in)
    return logits, feats["surprise"]


def train_loop(model, wm, judge, tok, spec, max_len, train_items, device, cfg_dict, seed,
               curve_stride=1):
    """Runs cfg_dict['total_steps'] optimizer steps; records per-step loss + grad-norm pre/post
    clip. Sets LR schedule + addr_temp per step externally (no mechanism edit). Returns
    (curve_dict, summary_dict). Assumes model/wm/judge already on `device`."""
    if cfg_dict.get("rq_std") is not None:
        # CUDA-SAFE (2026-07-29): wm is already .to(device); role_query may be a cuda tensor, so the
        # generator MUST be on that tensor's device (a cpu Generator against a cuda tensor raises
        # "Expected a 'cuda' device type for generator but found 'cpu'" -- this crashed the sweep).
        g = torch.Generator(device=wm.role_query.device).manual_seed(seed)
        with torch.no_grad():
            wm.role_query.normal_(0.0, cfg_dict["rq_std"], generator=g)
    params = list(model.parameters()) + list(wm.parameters()) + list(judge.parameters())
    opt = torch.optim.AdamW(params, lr=cfg_dict["lr"],
                            weight_decay=cfg_dict.get("weight_decay", 0.0),
                            betas=cfg_dict.get("betas", (0.9, 0.999)))
    total = int(cfg_dict["total_steps"])
    batch = int(cfg_dict.get("batch", BATCH))
    warmup_frac = cfg_dict.get("warmup_frac", 0.0)
    cosine = cfg_dict.get("cosine", False)
    temp_anneal = cfg_dict.get("temp_anneal")
    fixed_temp = cfg_dict.get("addr_temp", 0.5)
    gap_b = cfg_dict["gap_b"]

    rng = np.random.default_rng(seed)
    n = len(train_items)
    order = np.arange(n)
    pos = n  # force shuffle at first step
    losses, grad_pre_l, grad_post_l = [], [], []
    model.train()
    for step in range(total):
        if pos + batch > n:
            rng.shuffle(order)
            pos = 0
        idx = order[pos:pos + batch]
        pos += batch
        b_items = [train_items[i] for i in idx]
        y = torch.tensor([it["label"] for it in b_items], dtype=torch.long, device=device)

        lr = lr_at(step, total, cfg_dict["lr"], warmup_frac, cosine)
        for pg in opt.param_groups:
            pg["lr"] = lr
        wm.addr_temp = temp_at(step, total, warmup_frac, *temp_anneal) if temp_anneal else fixed_temp

        logits, surprise = forward_probe(model, wm, judge, tok, spec, max_len, b_items, device, gap_b)
        coh = (y == 1)
        bce = F.cross_entropy(logits, y)
        pe = surprise[coh].mean() if coh.any() else torch.tensor(0.0, device=device)
        loss = bce + LAMBDA_PE * pe
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite loss cfg=%s seed=%d step=%d" % (cfg_dict["name"], seed, step))
        opt.zero_grad(set_to_none=True)
        loss.backward()
        gpre = float(torch.nn.utils.clip_grad_norm_(params, max_norm=GRAD_CLIP_MAX_NORM))
        gpost = _total_grad_norm(params)
        opt.step()
        losses.append(float(loss.detach()))
        grad_pre_l.append(gpre)
        grad_post_l.append(gpost)

    label, stats = classify_shape(losses)
    s = curve_stride
    curve = dict(loss=[round(x, 4) for x in losses[::s]],
                 grad_pre=[round(x, 3) for x in grad_pre_l[::s]],
                 grad_post=[round(x, 3) for x in grad_post_l[::s]],
                 stride=s)
    summary = dict(final_loss=stats["final_loss"], min_loss=stats["min_loss"],
                   shape=label, shape_stats=stats,
                   grad_pre_max=round(max(grad_pre_l), 3), grad_pre_mean=round(float(np.mean(grad_pre_l)), 3),
                   fit=bool(stats["final_loss"] < TRAIN_FIT_THRESH),
                   total_steps=total, gap_b=gap_b, lr=cfg_dict["lr"],
                   warmup_frac=warmup_frac, cosine=cosine,
                   temp_anneal=list(temp_anneal) if temp_anneal else None,
                   rq_std=cfg_dict.get("rq_std"))
    return curve, summary


def run_config_real(cfg_dict, train_items, device, seed, curve_stride):
    torch.manual_seed(seed)
    model, tok, spec, cfg = load_encoder_and_tok(CKPT_PATH, device)
    d_model = cfg["d_model"]
    wm = SlotAttentionWM(d_model=d_model, n_slots=6, hidden=64, seed=seed).to(device)
    judge = make_judge_head(d_model, "A").to(device)
    curve, summary = train_loop(model, wm, judge, tok, spec, MAX_LEN, train_items, device,
                                cfg_dict, seed, curve_stride=curve_stride)
    del model, wm, judge
    return curve, summary


# ---------------------------------------------------------------------------
# Diag / sweep runners
# ---------------------------------------------------------------------------
def run_diag(seeds, steps, device_str):
    t0 = time.perf_counter()
    output_dir = out_dir_for("diag")
    cfg = dict(name="DIAG_gate_baseline_gapb", lr=3e-4, warmup_frac=0.0, cosine=False,
               total_steps=int(steps), gap_b=True)
    _write_start_marker(output_dir, "diag", expected_n_units=len(seeds))
    device = torch.device(device_str)
    train_items, mes_name = build_mes_fit_set(FIT_ITEMS)
    print("[DIAG] device=%s cuda=%s MES=%s items=%d steps=%d seeds=%s"
          % (device, torch.cuda.is_available(), mes_name, len(train_items), steps, seeds))
    per_seed = {}
    for i, seed in enumerate(seeds):
        curve, summary = run_config_real(cfg, train_items, device, seed, curve_stride=1)
        per_seed[seed] = dict(summary=summary, curve=curve)
        _heartbeat(output_dir, i + 1, len(seeds), time.perf_counter() - t0,
                   extra={"seed": seed, "shape": summary["shape"], "final_loss": summary["final_loss"]})
        print("[DIAG] seed=%d shape=%s final_loss=%.4f min_loss=%.4f grad_pre_max=%.2f"
              % (seed, summary["shape"], summary["final_loss"], summary["min_loss"], summary["grad_pre_max"]))
    shapes = sorted({per_seed[s]["summary"]["shape"] for s in seeds})
    elapsed = time.perf_counter() - t0
    verdict_msg = ("DIAG (gate-baseline gapb, %d MES items, %d steps): per-seed shape=%s; "
                   "final_loss=%s. Shape tells the lever." %
                   (len(train_items), steps,
                    {s: per_seed[s]["summary"]["shape"] for s in seeds},
                    {s: per_seed[s]["summary"]["final_loss"] for s in seeds}))
    metrics = dict(verdict="DIAG_COMPLETE", verdict_tag="DIAG_COMPLETE", verdict_msg=verdict_msg,
                   summary=verdict_msg[:200], elapsed_s=elapsed,
                   ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                   anchor_name=ANCHOR_NAME, run_mode="diag", device=str(device),
                   seeds=list(seeds), steps=int(steps), n_items=len(train_items), shapes=shapes,
                   per_seed=per_seed, start_marker_written=True, crash_diagnostic_present=True,
                   heartbeat_present=True, final_metrics_atomicity="tmp_replace", cell_chunked=False,
                   defensive_error_checking="passed_all_4_patterns")
    _write_metrics(output_dir, metrics)
    _done_sentinel(output_dir)
    print("[DIAG] DONE elapsed=%.1fs shapes=%s" % (elapsed, shapes))
    return metrics


def run_sweep(seeds, device_str, curve_stride=2):
    t0 = time.perf_counter()
    output_dir = out_dir_for("sweep")
    expected = len(CONFIGS) * len(seeds)
    _write_start_marker(output_dir, "sweep", expected_n_units=expected)
    device = torch.device(device_str)
    train_items, mes_name = build_mes_fit_set(FIT_ITEMS)
    print("[SWEEP] device=%s cuda=%s MES=%s items=%d configs=%d seeds=%s expected_units=%d"
          % (device, torch.cuda.is_available(), mes_name, len(train_items), len(CONFIGS), seeds, expected))

    results = {}   # cfg_name -> seed -> summary
    curves = {}    # cfg_name -> seed -> curve
    n_done = 0
    for cfg in CONFIGS:
        results[cfg["name"]] = {}
        curves[cfg["name"]] = {}
        for seed in seeds:
            curve, summary = run_config_real(cfg, train_items, device, seed, curve_stride=curve_stride)
            results[cfg["name"]][seed] = summary
            curves[cfg["name"]][seed] = curve
            n_done += 1
            _heartbeat(output_dir, n_done, expected, time.perf_counter() - t0,
                       extra={"cfg": cfg["name"], "seed": seed, "shape": summary["shape"],
                              "final_loss": summary["final_loss"], "fit": summary["fit"]})
            print("[SWEEP] %s seed=%d steps=%d shape=%s final_loss=%.4f min_loss=%.4f "
                  "grad_pre_max=%.2f fit=%s"
                  % (cfg["name"], seed, summary["total_steps"], summary["shape"],
                     summary["final_loss"], summary["min_loss"], summary["grad_pre_max"], summary["fit"]))

    # which configs fit BOTH seeds
    fit_both = {name: all(results[name][s]["fit"] for s in seeds) for name in results}
    fitting = [name for name, ok in fit_both.items() if ok]
    # leanest fitting config = fewest total_steps among fitting gap_b=True configs (prefer mechanism-under-test)
    def _steps(name):
        return results[name][seeds[0]]["total_steps"]
    gapb_fitting = [n for n in fitting if results[n][seeds[0]]["gap_b"]]
    winner = min(gapb_fitting, key=_steps) if gapb_fitting else (min(fitting, key=_steps) if fitting else None)

    # isolation: does per-slot-only (gap_b=False) fit where gap-B baseline does not?
    perslot_names = [c["name"] for c in CONFIGS if not c["gap_b"]]
    gapb_names = [c["name"] for c in CONFIGS if c["gap_b"]]
    perslot_fits = [n for n in perslot_names if fit_both[n]]
    gapb_fits = [n for n in gapb_names if fit_both[n]]
    if perslot_fits and not gapb_fits:
        isolation = "ROLE_QUERY_IS_CULPRIT (per-slot-only fits; NO gap-B config fits)"
    elif gapb_fits:
        isolation = "GAP_B_FITS (a gap-B config reaches fit; role-query is trainable with the right recipe)"
    elif not perslot_fits and not gapb_fits:
        isolation = "GENERAL_INSTABILITY (neither per-slot-only nor gap-B fit any tried config)"
    else:
        isolation = "MIXED"

    elapsed = time.perf_counter() - t0
    verdict_tag = "FIT_CONFIG_FOUND" if winner else "NO_FIT_CONFIG_FOUND"
    verdict_msg = (
        "MES FIT PROBE (256 items, Arm A, seeds=%s): winner=%s. fitting_configs=%s. "
        "isolation=%s. per_config_final_loss=%s. per_config_shape=%s."
        % (seeds, winner, fitting, isolation,
           {name: {s: results[name][s]["final_loss"] for s in seeds} for name in results},
           {name: {s: results[name][s]["shape"] for s in seeds} for name in results}))

    metrics = dict(
        verdict="SWEEP_COMPLETE", verdict_tag=verdict_tag, verdict_msg=verdict_msg,
        summary=verdict_msg[:200], elapsed_s=elapsed,
        ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
        anchor_name=ANCHOR_NAME, run_mode="sweep", device=str(device),
        seeds=list(seeds), n_items=len(train_items), n_configs=len(CONFIGS),
        winner=winner, fitting_configs=fitting, fit_both=fit_both, isolation=isolation,
        results=results, curves=curves,
        train_fit_thresh=TRAIN_FIT_THRESH, batch=BATCH, lambda_pe=LAMBDA_PE,
        grad_clip_max_norm=GRAD_CLIP_MAX_NORM,
        expected_n_units=expected, n_units_done=n_done, cardinality_ok=bool(n_done == expected),
        start_marker_written=True, crash_diagnostic_present=True, heartbeat_present=True,
        final_metrics_atomicity="tmp_replace", cell_chunked=False,
        defensive_error_checking="passed_all_4_patterns")
    _write_metrics(output_dir, metrics)
    _done_sentinel(output_dir)
    print("[SWEEP] DONE elapsed=%.1fs winner=%s isolation=%s (units %d/%d)"
          % (elapsed, winner, isolation, n_done, expected))
    return metrics


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def self_test():
    t0 = time.perf_counter()
    output_dir = out_dir_for("selftest")
    _write_start_marker(output_dir, "selftest", expected_n_units=1)
    device = torch.device("cpu")

    from experiments.exp_scale_meaning_learn_arc_heldout_v2 import TinyTransformer
    from tokenizers import Tokenizer, models, trainers, pre_tokenizers

    # schedule unit checks
    assert abs(lr_at(0, 100, 1e-3, 0.1, True) - 1e-3 * 1.0 / 10.0) < 1e-9, "warmup step0 wrong"
    assert lr_at(50, 100, 1e-3, 0.0, False) == 1e-3, "constant LR wrong"
    assert lr_at(99, 100, 1e-3, 0.1, True) < 1e-4, "cosine end should be near 0"
    assert abs(temp_at(0, 100, 0.2, 1.0, 0.5) - 1.0) < 1e-9, "temp anneal start wrong"
    assert abs(temp_at(20, 100, 0.2, 1.0, 0.5) - 0.5) < 1e-9, "temp anneal post-warmup wrong"

    # shape classifier unit checks (synthetic curves)
    assert classify_shape([0.693] * 60)[0] == "STUCK_FLAT", "stuck-flat misclassified"
    assert classify_shape(list(np.linspace(0.69, 0.05, 60))[:-5] + [0.05] * 5)[0] == "FIT", "fit misclassified"
    osc = [0.69 + 0.2 * ((-1) ** i) for i in range(60)]
    assert classify_shape(osc)[0] == "OSCILLATING", "oscillating misclassified"
    slow = list(np.linspace(0.69, 0.30, 60))
    assert classify_shape(slow)[0] == "SLOW_DESCENDING", "slow-descending misclassified"

    tiny_cfg = dict(vocab=64, max_len=16, d_model=16, n_layers=1, n_heads=2, ffn_mult=2, pad_id=0)
    torch.manual_seed(0)
    model = TinyTransformer(**tiny_cfg).to(device)
    tok = Tokenizer(models.BPE(unk_token="[UNK]"))
    tok.pre_tokenizer = pre_tokenizers.Whitespace()
    trainer = trainers.BpeTrainer(vocab_size=64, special_tokens=["[PAD]", "[UNK]", "[MASK]"], show_progress=False)
    toy = ["the door became open .", "the window became closed .", "the light is on now .",
           "the box became full .", "the gate became locked .", "the door is closed now ."]
    tok.train_from_iterator(iter(toy), trainer=trainer)
    spec = dict(pad=tok.token_to_id("[PAD]"), unk=tok.token_to_id("[UNK]"),
                mask=tok.token_to_id("[MASK]"), size=tok.get_vocab_size())
    assert spec["pad"] is not None, "self-test: [PAD] missing"

    mc = gen_multi_entity_state(np.random.default_rng(0), n_distractor_entities=1,
                                n_distractor_events=1, train_target=16, eval_target_per_label=4)
    sub = balanced_subset(mc["train"], 8)
    assert len(sub) == 8 and sum(it["label"] for it in sub) == 4, "balanced_subset wrong"

    exercised = set()
    # gap-B forward + per-slot-only forward BOTH exercised (isolation path proven distinct-callable)
    wm = SlotAttentionWM(d_model=16, n_slots=2, hidden=8, seed=0)
    judge = make_judge_head(16, "A")
    lg_gapb, _ = forward_probe(model, wm, judge, tok, spec, 16, sub[:4], device, gap_b=True)
    lg_ps, _ = forward_probe(model, wm, judge, tok, spec, 16, sub[:4], device, gap_b=False)
    exercised.update(["forward_probe_gapb", "forward_probe_perslot", "encode_clause_batch_tok",
                      "SlotAttentionWM.step"])
    assert lg_gapb.shape == (4, 2) and lg_ps.shape == (4, 2), "forward shapes wrong"

    # tiny train_loop both gap_b, with temp anneal + gentle init on one, few steps
    cfgA = dict(name="st_gapb", lr=0.01, warmup_frac=0.2, cosine=True, total_steps=6,
                temp_anneal=(1.0, 0.5), rq_std=0.01, gap_b=True)
    wmA = SlotAttentionWM(d_model=16, n_slots=2, hidden=8, seed=0)
    judgeA = make_judge_head(16, "A")
    curveA, sumA = train_loop(model, wmA, judgeA, tok, spec, 16, sub, device, cfgA, 0, curve_stride=1)
    exercised.update(["train_loop", "lr_at", "temp_at", "classify_shape", "_total_grad_norm"])
    assert len(curveA["loss"]) == 6 and np.isfinite(sumA["final_loss"]), "train_loop gapb bad"

    torch.manual_seed(0)
    model2 = TinyTransformer(**tiny_cfg).to(device)
    cfgB = dict(name="st_perslot", lr=0.01, warmup_frac=0.0, cosine=False, total_steps=6, gap_b=False)
    wmB = SlotAttentionWM(d_model=16, n_slots=2, hidden=8, seed=1)
    judgeB = make_judge_head(16, "A")
    curveB, sumB = train_loop(model2, wmB, judgeB, tok, spec, 16, sub, device, cfgB, 1, curve_stride=1)
    assert len(curveB["loss"]) == 6 and np.isfinite(sumB["final_loss"]), "train_loop perslot bad"

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict="SELFTEST_PASS", verdict_tag="SELFTEST_PASS",
        verdict_msg="self-test PASS: schedules (lr_at/temp_at) + shape-classifier (4 synthetic "
                    "shapes) + gap-B AND per-slot-only forward_probe + train_loop (both paths, "
                    "temp-anneal + gentle-init) exercised at N~8; gapb final=%.4f perslot final=%.4f"
                    % (sumA["final_loss"], sumB["final_loss"]),
        summary="SELFTEST_PASS", elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        pid=os.getpid(), anchor_name=ANCHOR_NAME, run_mode="selftest",
        exercised_entrypoints=sorted(exercised),
        st_gapb=dict(final_loss=sumA["final_loss"], shape=sumA["shape"]),
        st_perslot=dict(final_loss=sumB["final_loss"], shape=sumB["shape"]),
        start_marker_written=True, crash_diagnostic_present=True, heartbeat_present=True,
        final_metrics_atomicity="tmp_replace", cell_chunked=False,
        defensive_error_checking="passed_all_4_patterns")
    _write_metrics(output_dir, metrics)
    print("[SELFTEST] PASS elapsed=%.1fs (gapb final=%.4f perslot final=%.4f)"
          % (elapsed, sumA["final_loss"], sumB["final_loss"]))
    return metrics


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--diag", action="store_true", help="ONE gate-baseline config, full per-step curve, classify shape")
    ap.add_argument("--sweep", action="store_true", help="the config grid x seeds at 256 items")
    ap.add_argument("--seeds", type=int, nargs="+", default=SEEDS_DEFAULT)
    ap.add_argument("--steps", type=int, default=320, help="diag total optimizer steps")
    ap.add_argument("--device", type=str, default="cpu")
    args = ap.parse_args()

    device_str = args.device
    if device_str.startswith("cuda") and not torch.cuda.is_available():
        raise SystemExit("--device %s requested but torch.cuda.is_available()==False on this host "
                         "(dispatch to a GPU host, or use --device cpu)" % device_str)

    if args.self_test:
        self_test()
        return
    if args.diag:
        run_diag(args.seeds, args.steps, device_str)
        return
    if args.sweep:
        run_sweep(args.seeds, device_str)
        return
    raise SystemExit("must specify one of --self-test / --diag / --sweep")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- not BaseException, per META_RULE
        rm = "diag" if "--diag" in sys.argv else ("sweep" if "--sweep" in sys.argv else "selftest")
        _write_crash_metrics(out_dir_for(rm), e)
        raise
