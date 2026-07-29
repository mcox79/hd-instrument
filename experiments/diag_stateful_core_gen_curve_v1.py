# DIAGNOSTIC (not a verdict-experiment): generalization-curve probe for the stateful core.
# Question answered: is the "memorize-but-don't-generalize" MES result DATA-limited or
# MECHANISM-limited? Re-smoke (264ba7f76+) fixed undertraining -- MES Arm-A train_loss=0.042
# (memorizes 64 items) but eval_acc=0.469 = CHANCE, TIED to random-init-core (0.4375). This probe
# grows MES train size [64,128,256,512] against a FIXED held-out eval and plots two curves:
#   trained_eval_acc(size)   and   random_init_core_eval_acc(size).
# DATA-limited signature   = trained climbs above chance AND pulls away from random-init as size up.
# MECHANISM-limited signature = both stay ~chance / stay tied through 512.
#
# SCOPE (deliberately tight, reuses the FULL cell's real machinery -- NO new mechanism):
#   - MES construction ONLY (maintenance test); distE4/distEv6 LOCKED_CONSTRUCTION.
#   - Arm A ONLY (blank slots) -- isolates the mechanism from the KB variable.
#   - seed 7, single seed (DIAGNOSTIC, not a 2-seed verdict -- reported as such).
#   - trained core = UNFROZEN encoder + WM + judge, grad-clip 1.0, steps held ~constant across
#     sizes by scaling epochs down (TARGET_STEPS).
#   - random-init-core control at the SAME size = fit ONLY the linear judge head on a random-init
#     (never-trained) encoder+WM; encoder+WM features are CONSTANT under this control, so they are
#     extracted ONCE and cached, then the head is fit on cached features (fast + exact).
#
# Reuses (imported, unchanged) from the FULL cell + siblings:
#   load_encoder_and_tok, build_random_init_encoder, train_and_eval_arm, make_judge_head,
#   split_clauses, encode_clause_batch, CKPT_PATH (exp_stateful_core_situation_model_v1);
#   gen_multi_entity_state (diag_order_critical_comprehension_calib_v1);
#   SlotAttentionWM (hdlab.slot_attention_wm).
#
# CELL-TEMPLATE (defensive, exp_dev.md sec 13 + META rules): start marker, crash-metrics
# (except SystemExit: raise before except Exception; no BaseException), heartbeat, atomic
# tmp+os.replace metrics write, real-code-path self-test at tiny scale.
"""Generalization-curve diagnostic for the stateful-core situation model (2026-07-29)."""
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
    split_clauses, encode_clause_batch, CKPT_PATH,
)
from experiments.diag_order_critical_comprehension_calib_v1 import (  # noqa: E402
    gen_multi_entity_state,
)
from hdlab.slot_attention_wm import SlotAttentionWM  # noqa: E402

ANCHOR_NAME = "diag_stateful_core_gen_curve_v1"
MAX_LEN = 96                      # MES_MAX_LEN per LOCKED_CONSTRUCTION
TRAIN_SIZES = [64, 128, 256, 512]
EVAL_PER_LABEL = 100             # fixed held-out eval = 200 items, SAME across all train sizes
BATCH = 8                        # small batch -> more steps/wall for a fixed step target (cheap)
TARGET_STEPS = 280               # optimizer steps held ~constant per size (task band 250-400)
LR = 3e-4                        # matches the re-smoke's trained-arm LR (step-count was the deficit)
LAMBDA_PE = 0.2                  # PE/surprise term weight (same as FULL cell smoke)
CTRL_EPOCHS = 150                # judge-head fit epochs on CACHED frozen features (near-free)
CTRL_LR = 1e-2
CHANCE = 0.5

# WALL ESTIMATE (laptop CPU micro-benchmark from the parent cell: MES ~3.5s/optimizer-step at
# batch=8 on the real 512d/6L ckpt): trained steps = 280+288+288+256 = 1112 -> ~65 min; the
# cached-feature random-init control adds ~10-15 min; 4 encoder reloads + MES gen ~1 min; eval
# passes ~7 min. => ~80-90 min laptop wall. Ship with a 3h (10800s) timeout for a slower remote CPU.


# ---------------------------------------------------------------------------
# Defensive scaffolding (exp_dev.md sec 13)
# ---------------------------------------------------------------------------
def out_dir():
    return os.path.join(_REPO, "data", ANCHOR_NAME)


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


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _heartbeat(output_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": elapsed_s, "extra": extra or {}}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ---------------------------------------------------------------------------
# Frozen-feature extractor for the random-init control (mirrors forward_item_batch, arm A path).
# encoder + WM are frozen for the control, so features are constant -> extract once, cache, fit
# the linear head on the cache. in_dim = d_model + 3 (slot_mean, surprise, write_strength,
# addr_entropy) -- matches make_judge_head(d, "A").
# ---------------------------------------------------------------------------
def extract_feats_frozen(model, wm, tok, spec, max_len, items, device, chunk=32):
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
                clause_rep = encode_clause_batch(model, tok, spec["pad"], max_len, sents, device)
                slots, fdict = wm.step(slots, clause_rep, kb_prior=None)
            slot_mean = slots.mean(dim=1)
            judge_in = torch.cat([slot_mean, fdict["surprise"].unsqueeze(-1),
                                  fdict["write_strength"].unsqueeze(-1),
                                  fdict["addr_entropy"].unsqueeze(-1)], dim=-1)
            feats_out.append(judge_in.cpu())
    return torch.cat(feats_out, dim=0)  # [N, d+3]


def fit_random_init_control(cfg, device, seed, d_model, tok, spec, max_len,
                            train_items, eval_items):
    """Fit ONLY the linear judge head on a random-init (never-trained) encoder+WM at this size.
    Encoder+WM frozen -> features constant -> extracted once + cached, head fit on the cache."""
    ri_model = build_random_init_encoder(cfg, device, seed=1000 + seed)
    ri_model.eval()
    for p in ri_model.parameters():
        p.requires_grad_(False)
    wm_ri = SlotAttentionWM(d_model=d_model, n_slots=6, hidden=64, seed=1000 + seed)
    for p in wm_ri.parameters():
        p.requires_grad_(False)

    Xtr = extract_feats_frozen(ri_model, wm_ri, tok, spec, max_len, train_items, device).to(device)
    Xev = extract_feats_frozen(ri_model, wm_ri, tok, spec, max_len, eval_items, device).to(device)
    ytr = torch.tensor([it["label"] for it in train_items], dtype=torch.long, device=device)
    yev = np.array([it["label"] for it in eval_items], dtype=np.int64)

    head = make_judge_head(d_model, "A").to(device)
    opt = torch.optim.AdamW(head.parameters(), lr=CTRL_LR)
    for _ep in range(CTRL_EPOCHS):
        logits = head(Xtr)
        loss = F.cross_entropy(logits, ytr)
        if not torch.isfinite(loss):
            raise FloatingPointError("random-init control non-finite loss size=%d" % len(train_items))
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
    with torch.no_grad():
        preds = head(Xev).argmax(dim=-1).cpu().numpy()
    acc = float((preds == yev).mean())
    return acc, float(loss.detach())


def epochs_for_size(size):
    bpe = max(1, math.ceil(size / BATCH))
    return max(4, int(round(TARGET_STEPS / bpe)))


def balanced_nested_subsets(train_pool, sizes):
    """Return {size: subset} where subsets are label-balanced and NESTED (subset[s1] subset[s2]
    for s1 < s2), so the curve isolates train SIZE (same items + more added)."""
    l0 = [it for it in train_pool if it["label"] == 0]
    l1 = [it for it in train_pool if it["label"] == 1]
    out = {}
    for s in sizes:
        h = s // 2
        if h > len(l0) or h > len(l1):
            raise ValueError("train_pool too small for size %d: have l0=%d l1=%d need %d/label"
                             % (s, len(l0), len(l1), h))
        out[s] = l0[:h] + l1[:h]
    return out


# ---------------------------------------------------------------------------
def run(seed, device_str):
    t0 = time.perf_counter()
    output_dir = out_dir()
    n_units = len(TRAIN_SIZES) * 2  # trained + control per size
    _write_start_marker(output_dir, "run", expected_n_units=n_units)
    device = torch.device(device_str)
    _log = lambda m: print("[GEN_CURVE] %s" % m)
    _log("device=%s cuda_available=%s seed=%d" % (device, torch.cuda.is_available(), seed))

    if not os.path.exists(CKPT_PATH):
        raise FileNotFoundError("checkpoint not found: %s" % CKPT_PATH)

    # ONE MES generation: train pool 512 (256/label), FIXED eval 2*EVAL_PER_LABEL.
    mes_rng = np.random.default_rng(seed + 555)
    mc = gen_multi_entity_state(mes_rng, n_distractor_entities=4, n_distractor_events=6,
                                train_target=max(TRAIN_SIZES), eval_target_per_label=EVAL_PER_LABEL)
    eval_items = mc["eval"]
    subsets = balanced_nested_subsets(mc["train"], TRAIN_SIZES)
    _log("MES(%s): train_pool=%d eval_fixed=%d (%d/label)"
         % (mc["name"], len(mc["train"]), len(eval_items), EVAL_PER_LABEL))

    # cfg / d_model from a throwaway load (each size reloads its own fresh pretrained core)
    _m0, _tok0, _spec0, cfg = load_encoder_and_tok(CKPT_PATH, device)
    d_model = cfg["d_model"]
    del _m0

    curve = {}
    n_done = 0
    for size in TRAIN_SIZES:
        tr = subsets[size]
        ep = epochs_for_size(size)
        steps = ep * max(1, math.ceil(size / BATCH))

        # TRAINED core: fresh pretrained ckpt_seed_7 + fresh WM + fresh judge, UNFROZEN, Arm A.
        torch.manual_seed(seed)
        model, tok, spec, _cfg = load_encoder_and_tok(CKPT_PATH, device)
        wm = SlotAttentionWM(d_model=d_model, n_slots=6, hidden=64, seed=seed)
        judge = make_judge_head(d_model, "A")
        res = train_and_eval_arm(model, wm, judge, tok, spec, MAX_LEN, tr, eval_items, device,
                                 kb_prior_lookup=None, arm="A", epochs=ep, batch_size=BATCH, lr=LR,
                                 lambda_pe=LAMBDA_PE, lambda_kb=0.0, rng=np.random.default_rng(seed))
        n_done += 1
        _heartbeat(output_dir, n_done, n_units, time.perf_counter() - t0,
                   extra={"size": size, "kind": "trained", "eval_acc": res["eval_acc"],
                          "train_loss": res["train_loss"], "steps": steps})
        _log("size=%d TRAINED: epochs=%d steps=%d train_loss=%.4f eval_acc=%.4f"
             % (size, ep, steps, res["train_loss"], res["eval_acc"]))

        # RANDOM-INIT-CORE control at the SAME size (cached frozen features).
        del model, wm, judge
        ri_acc, ri_loss = fit_random_init_control(cfg, device, seed, d_model, tok, spec, MAX_LEN,
                                                  tr, eval_items)
        n_done += 1
        _heartbeat(output_dir, n_done, n_units, time.perf_counter() - t0,
                   extra={"size": size, "kind": "random_init", "eval_acc": ri_acc})
        _log("size=%d RANDOM_INIT_CORE: eval_acc=%.4f" % (size, ri_acc))

        curve[size] = dict(train_size=size, epochs=ep, opt_steps=steps,
                           trained_train_loss=res["train_loss"],
                           trained_eval_acc=res["eval_acc"],
                           random_init_eval_acc=ri_acc,
                           gap_trained_minus_random=res["eval_acc"] - ri_acc)

    elapsed = time.perf_counter() - t0

    # DIAGNOSTIC signature (not a PASS/FAIL verdict): compare largest vs smallest size.
    sizes_sorted = sorted(curve)
    s_lo, s_hi = sizes_sorted[0], sizes_sorted[-1]
    trained_hi = curve[s_hi]["trained_eval_acc"]
    trained_lo = curve[s_lo]["trained_eval_acc"]
    gap_hi = curve[s_hi]["gap_trained_minus_random"]
    trained_climbs = bool(trained_hi >= 0.55 and (trained_hi - trained_lo) >= 0.05)
    pulls_away = bool(gap_hi >= 0.05)
    if trained_climbs and pulls_away:
        signature = "DATA_LIMITED_SIGNATURE"
    elif trained_hi < 0.55 and abs(gap_hi) < 0.05:
        signature = "MECHANISM_LIMITED_SIGNATURE"
    else:
        signature = "AMBIGUOUS_SIGNATURE"

    verdict_msg = (
        "DIAGNOSTIC (single-seed=%d, NOT a verdict): MES Arm-A generalization curve. "
        "trained_eval_acc: %s ; random_init_eval_acc: %s ; gap(trained-random): %s ; "
        "trained_train_loss: %s ; signature=%s (trained_climbs=%s pulls_away_from_random=%s; "
        "chance=%.2f)"
        % (seed,
           {s: round(curve[s]["trained_eval_acc"], 4) for s in sizes_sorted},
           {s: round(curve[s]["random_init_eval_acc"], 4) for s in sizes_sorted},
           {s: round(curve[s]["gap_trained_minus_random"], 4) for s in sizes_sorted},
           {s: round(curve[s]["trained_train_loss"], 4) for s in sizes_sorted},
           signature, trained_climbs, pulls_away, CHANCE))

    metrics = dict(
        verdict="DIAG_COMPLETE", verdict_tag=signature, verdict_msg=verdict_msg,
        summary=verdict_msg[:200], elapsed_s=elapsed,
        ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
        anchor_name=ANCHOR_NAME, run_mode="run", seed=seed, device=str(device),
        is_diagnostic=True, single_seed=True,
        construction="MULTI_ENTITY_STATE_distE4_distEv6", arm="A",
        chance=CHANCE, train_sizes=TRAIN_SIZES, eval_fixed_n=len(eval_items),
        eval_per_label=EVAL_PER_LABEL, batch=BATCH, target_steps=TARGET_STEPS, lr=LR,
        lambda_pe=LAMBDA_PE, grad_clip_max_norm=1.0,
        curve=curve, signature=signature,
        trained_climbs=trained_climbs, pulls_away_from_random=pulls_away,
        start_marker_written=True, crash_diagnostic_present=True, heartbeat_present=True,
        final_metrics_atomicity="tmp_replace", cell_chunked=False,
        defensive_error_checking="passed_all_4_patterns",
    )
    _write_metrics(output_dir, metrics)
    _log("DONE elapsed=%.1fs signature=%s" % (elapsed, signature))
    return metrics


# ---------------------------------------------------------------------------
# Self-test: real code path at tiny scale (per META F.1) -- builds the REAL objects the run uses.
# ---------------------------------------------------------------------------
def self_test():
    t0 = time.perf_counter()
    output_dir = out_dir()
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
    rng = np.random.default_rng(0)
    mc = gen_multi_entity_state(rng, n_distractor_entities=1, n_distractor_events=1,
                                train_target=16, eval_target_per_label=4)
    exercised.add("gen_multi_entity_state")
    eval_items = mc["eval"]
    subs = balanced_nested_subsets(mc["train"], [4, 8])
    ids8 = {id(it) for it in subs[8]}
    assert all(id(it) in ids8 for it in subs[4]), "self-test: subsets not nested by identity"
    assert len(subs[8]) == 8 and len(subs[4]) == 4, "self-test: nested subset sizing wrong"

    wm = SlotAttentionWM(d_model=16, n_slots=2, hidden=8, seed=0)
    judge = make_judge_head(16, "A")
    res = train_and_eval_arm(model, wm, judge, tok, spec, 16, subs[8], eval_items, device,
                             kb_prior_lookup=None, arm="A", epochs=1, batch_size=4, lr=0.01,
                             lambda_pe=0.1, lambda_kb=0.0, rng=np.random.default_rng(0))
    exercised.add("train_and_eval_arm")
    exercised.add("SlotAttentionWM_step")
    assert np.isfinite(res["train_loss"]) and 0.0 <= res["eval_acc"] <= 1.0, "self-test: bad trained res"

    # random-init control real path (cached-feature extractor + head fit)
    cfg_like = tiny_cfg
    ri_acc, ri_loss = fit_random_init_control(cfg_like, device, 0, 16, tok, spec, 16,
                                              subs[8], eval_items)
    exercised.add("build_random_init_encoder")
    exercised.add("extract_feats_frozen")
    exercised.add("fit_random_init_control")
    assert 0.0 <= ri_acc <= 1.0 and np.isfinite(ri_loss), "self-test: bad control res"

    # epochs-for-size sanity: steps ~ TARGET_STEPS, epochs scale DOWN as size grows
    e64, e512 = epochs_for_size(64), epochs_for_size(512)
    assert e64 > e512, "self-test: epochs must scale down as train size grows (%d !> %d)" % (e64, e512)
    for s in TRAIN_SIZES:
        st = epochs_for_size(s) * math.ceil(s / BATCH)
        assert 200 <= st <= 420, "self-test: size=%d steps=%d outside [200,420] band" % (s, st)

    elapsed = time.perf_counter() - t0
    metrics = dict(
        verdict="SELFTEST_PASS", verdict_tag="SELFTEST_PASS",
        verdict_msg="self-test PASS: real load/train/eval + gen_multi_entity_state + "
                    "SlotAttentionWM + random-init cached-feature control exercised at N~4-16; "
                    "trained(A) loss=%.4f acc=%.4f; control acc=%.4f; steps-band OK "
                    "(e64=%d e512=%d)" % (res["train_loss"], res["eval_acc"], ri_acc, e64, e512),
        summary="SELFTEST_PASS", elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        pid=os.getpid(), anchor_name=ANCHOR_NAME, run_mode="selftest",
        exercised_entrypoints=sorted(exercised),
        trained_arm=dict(train_loss=res["train_loss"], eval_acc=res["eval_acc"]),
        random_init_control=dict(eval_acc=ri_acc),
        start_marker_written=True, crash_diagnostic_present=True, heartbeat_present=True,
        final_metrics_atomicity="tmp_replace", cell_chunked=False,
        defensive_error_checking="passed_all_4_patterns",
    )
    _write_metrics(output_dir, metrics)
    print("[SELFTEST] PASS elapsed=%.1fs" % elapsed)
    return metrics


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--device", type=str, default="cpu")
    args = ap.parse_args()

    device_str = args.device
    if device_str.startswith("cuda") and not torch.cuda.is_available():
        raise SystemExit("--device %s requested but torch.cuda.is_available()==False" % device_str)

    if args.self_test:
        self_test()
        return
    if args.run:
        run(args.seed, device_str)
        return
    raise SystemExit("must specify one of --self-test / --run")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- not BaseException, per META_RULE
        _write_crash_metrics(out_dir(), e)
        raise
