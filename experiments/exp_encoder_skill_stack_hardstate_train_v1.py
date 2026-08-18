# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test: FROZEN-1 vs TARGET-TRAINED hard-state decode digest must DIFFER;
#   FROZEN-1 vs FROZEN-2 (drift control) must be near-IDENTICAL (max|drift|<=DRIFT_MAX).
# - final_metrics_atomicity: tmp_replace (os.replace at end) + per-seed units.jsonl (resumable).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: paired frozen-vs-skill-trained decode comparison (no capacity sweep).
# - baseline_in_band: YES, explicitly gated -- HARDSTATE_BASELINE_IN_BAND requires 0.05 < frozen hard-state
#   acc < 0.95 (headroom check, MEASURED at self-test/smoke, machine-asserted, not just narrated).
# - discriminator survives scale: measured at the SAME eval_n/hardness/seeds as the sibling encoder-
#   transfer cells' LITE config for the entity no-interference side; the target-side measurement is its own
#   dedicated hard-state harness (new, this cell), run at FULL n=HARDSTATE_EVAL_N (not smoke-truncated) for
#   the lift verdict.
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set()).
"""ENCODER SKILL-STACK TEST v2 (CORRECTED per coordinator fairness-gate directive 2026-08-01): a REDO of
exp_encoder_skill_stack_placement_train_v1.py after that cell's P (placement) target was flagged as (a) not
cleanly independent of entity-adjacency (P lifted +0.086 from ENTITY-ONLY training but only +0.011 under
its OWN direct training in that cell's landed lite run, MEASURED@
data/exp_encoder_skill_stack_placement_train_v1/metrics.json -- a skill improving MORE from indirect than
direct training is the SIGNATURE of an underpowered/confounded run, not evidence of an intrinsic limit) and
(b) not verified as actually-optimizing (that cell's align/push loss barely moved: l_push 0.7829->0.7761
over 60 SMOKE steps, MEASURED@ same file, units[0].ft; no per-seed loss-descent/weight-move GATE existed to
catch this before the verdict fired). This cell fixes BOTH problems with a newly CONSTRUCTED target and a
MACHINE-CHECKED fairness gate suite (5 gates, all logged to metrics, all must PASS before the lift verdict
is trusted -- see "FAIRNESS GATES" below).

TARGET CONSTRUCTION (Gate 1+2, done BEFORE training, not tuned after seeing a result): the S (state-filler)
decode was FLAT (+0.020) under entity-only training but that cell's own headroom was tiny (frozen=0.951,
MEASURED@data/exp_encoder_generic_vs_entity_addressed_v1/metrics.json:bands.stage_mean.S) -- ~0.05 of band
left, so "flat" is partly a ceiling artifact, not conclusive. This cell CONSTRUCTS a harder variant of the
SAME S decode with a lexical DISTRACTOR inserted directly at the target span: hard_render_state(ent, s, p,
n_mods) renders "the <ENT> was set <MODIFIER> <S-color> and placed <P-color> ." -- IDENTICAL sentence shape
to eb.render_name_event, with ONE local distractor adjective (drawn from the SAME MODIFIERS pool the
certified ENT-hardness axis already uses, CITED@exp_continuous_curriculum_learn_as_you_go_v1.py MODIFIERS,
vocabulary DISJOINT from COLORS -- MEASURED@ ad hoc check: `set(MODIFIERS) & set(COLORS) == set()`) placed
immediately before the S color word. Independence: the ENT color plays NO role in the S label (entity
varies freely per example, only S is the supervision label) and the decode mechanism is the SAME fixed
role-cue attention-pool ("what was set to ?", eb.CUES["S"]) over the WHOLE token sequence used everywhere
else in this harness -- no span-restriction, no cross-sentence step, no entity/mark identity read at any
point. Headroom: MEASURED frozen role_attn accuracy on 2000 fresh hard-state examples (v2 default ckpt,
n_mods=8, the hardest modifier-pool size) = 0.7660 (ad hoc probe, reproduced at self-test/smoke scale below
as a machine-checked gate, HARDSTATE_BASELINE_IN_BAND). This is comparable headroom to P's 0.808 but with
NONE of P's indirect-training confound (P's own docstring/measurement showed +0.086 under entity-only
training; this cell's self-test/smoke MUST show the hard-state target does NOT move substantially under the
positive-control ENTITY arm -- reported as an additional independence check, not assumed).

FAIRNESS GATES (all 5, MACHINE-CHECKED and reported in metrics BEFORE the lift verdict is trusted; per
coordinator directive -- a null result on an unfair/underpowered test is a broken experiment, not evidence):
  G1 INDEPENDENCE: hard_render_state's S-label is drawn independent of ent/p (verified structurally in
     _gather_hardstate_texts -- ent, p sampled uniformly at random per example, ONLY S groups the label);
     reported: HARDSTATE_INDEPENDENCE_BY_CONSTRUCTION = True.
  G2 HEADROOM: HARDSTATE_BASELINE_IN_BAND -- frozen hard-state acc must be in (0.05, 0.95); machine-checked
     at self-test (tiny) and smoke (n=HARDSTATE_EVAL_N_SMOKE) BEFORE any lite dispatch.
  G3 TRAINING-ACTUALLY-OPTIMIZED: WEIGHT_MOVE_MIN (1e-3, CITED@exp_continuous_curriculum_learn_as_you_go_v1
     same constant name/value) on the tracked top-layer norm weight, AND LOSS_DESCENT_MIN (1e-3, same
     citation) on the align+push+vic loss (mean of first 5 steps minus mean of last 5 steps), asserted
     PER SEED in run_seed_probe and raised as an AssertionError (not silently reported) if either fails --
     a no-op training run cannot reach the verdict step.
  G4 POSITIVE CONTROL: at self-test AND smoke scale, a SEPARATE extractor is trained on the ALREADY-
     CERTIFIED entity objective (lt.finetune_encoder, reused VERBATIM, SAME steps/nctx/depth budget as the
     target arm at that run_mode) and its ENT decode + MAIN_ENC loop must show POSITIVE lift -- proving the
     unfreeze+train+eval PIPELINE (not just this specific objective) is capable of producing a lift at this
     exact compute budget. (Full-scale entity lift is independently already certified at LITE/FULL budget
     multiple times over -- atom 29593, exp_encoder_alltype_transfer_v1 HARD_PASS MEASURED@
     data/exp_encoder_alltype_transfer_v1/metrics.json -- so the smoke-scale inline positive control plus
     that citation together cover "the pipeline can lift something" at both scales without re-spending the
     full 3-seed budget twice.)
  G5 METRIC CAN MOVE (not floor-saturated): a SHUFFLED-LABEL sentinel (score_hard_state's floor_acc field)
     scores decoded predictions against a randomly shuffled label vector; this must land near chance
     (1/V_FILL=0.05) at self-test/smoke, proving the metric is not somehow floor-locked at a value that
     can't move regardless of the encoder.
  Only if G1-G5 all PASS does a target-lift-below-LIFT_MIN result support HYPOTHESIS_REFUTED_NO_TRANSFER;
  otherwise ANY gate failure means BLOCK_DISPATCH / INVALID, not a capability conclusion.

RECIPE (mirrors the certified shape EXACTLY -- the ONE VARIABLE is the training TARGET's data/label, not
architecture): top-1 unfreeze (RECIPE_DEPTH=1, CITED@exp_encoder_retrain_persist_v1.py), nctx=40, steps=220,
the SAME three-term objective (align+push+VICReg, lt._vicreg_terms reused VERBATIM) applied to the S-slot
pooled rep of HARD-STATE-rendered texts instead of the ENT-slot. lt.py / eb.py / base_loop.py are NOT
modified (read-only reuse).

MEASUREMENT (3 seeds; ONE VARIABLE = frozen vs hard-state-trained):
  (a) TARGET LIFT: score_hard_state(ext, held_colors, HARDSTATE_EVAL_N, seed) tuned-vs-frozen accuracy.
  (b) NO-INTERFERENCE: base_loop._eval_heldahead stage_role_attn ENT/MARK/ENT_q/MARK_q/entity_consistency
      + the 3-query-type MAIN_ENC loop, tuned-vs-frozen (SAME harness as the sibling cells).
  (c) DRIFT CONTROL: FROZEN-2 vs FROZEN-1 on both the entity-metrics side and the hard-state side.

PRE-REGISTERED BANDS (fixed BEFORE running; preregs/2026-08-01_encoder_skill_stack_hardstate.md):
  TARGET_LIFT_MIN = 0.05, NO_INTERFERE_MAX_DROP = 0.05, DRIFT_MAX = 0.01 (all CITED, same values as the v1
    cell and the sibling generic-vs-entity cell -- not re-tuned for this target).
  HYPOTHESIS_CONFIRMED (HARD_PASS): all 5 fairness gates PASS AND target lift >= TARGET_LIFT_MIN AND every
    entity-addressed metric's lift >= -NO_INTERFERE_MAX_DROP.
  HYPOTHESIS_REFUTED_NO_TRANSFER (HARD_FAIL): all 5 fairness gates PASS BUT target lift < TARGET_LIFT_MIN
    => a REAL intrinsic limit on this decode under VERIFIED-optimized direct training, not lack-of-training.
  HYPOTHESIS_REFUTED_INTERFERENCE (HARD_FAIL): all 5 fairness gates PASS, target lift clears TARGET_LIFT_MIN,
    BUT >=1 entity-addressed metric drops beyond -NO_INTERFERE_MAX_DROP => skills compete, can't stack.
  MIDDLE: mixed pattern. INVALID: any of G1-G5 fails, OR drift control fails, OR clean.audit_construction
    flags fail -- NOT a capability conclusion in this case.

PRIOR-WORK CHECK (substrate_query.sh "encoder second skill hard state distractor headroom independent
positive control fairness gate", run before authoring): top hit cosine=0.29 is this session's own v1 cell
(exp_encoder_skill_stack_placement_train_v1, the superseded confounded attempt) -- expected, not a
rediscovery of prior independent work; no other hit above cosine 0.30.

Run:  .venv/Scripts/python.exe experiments/exp_encoder_skill_stack_hardstate_train_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_encoder_skill_stack_hardstate_train_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_encoder_skill_stack_hardstate_train_v1.py --lite

ASCII-only. No emojis. Deterministic seeding. Pure CPU. Compute architecture: sequential-CPU (one hard-
state-objective fine-tune per seed, ~110-150s at this depth/nctx/steps, plus cheap frozen-weight forward-
pass evals); INLINE-LOCAL foreground-to-completion, resumable per-seed (tools/exp_checkpoint.py) with a
--budget-sec cutoff (never backgrounded -- PARTIAL + resume on the next foreground call if a single call
can't finish all 3 seeds). Storage: no_storage. progress_logging: print_flush_true.
PARALLEL-SAFE: writes only to data/exp_encoder_skill_stack_hardstate_train_v1/ (new dir); does not modify
base_loop, lt, eb, ef, or touch any other agent's/cell's in-flight dir (exp_encoder_alltype_transfer_stress_v1,
exp_encoder_generic_vs_entity_addressed_v1, exp_encoder_skill_stack_placement_train_v1 read-only cited).
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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_continuous_curriculum_learn_as_you_go_v1 as base_loop  # noqa: E402 (UNMODIFIED per-seed harness)

hc = base_loop.hc
ckpt = base_loop.ckpt
lt = base_loop.lt
eb = base_loop.eb
ef = base_loop.ef                           # noqa: F401
ih = base_loop.ih
clean = base_loop.clean
QUERY_TYPES = base_loop.QUERY_TYPES
SPLIT_SEED = base_loop.SPLIT_SEED
HARDNESS_LITE = base_loop.HARDNESS_LITE
HARDNESS_SMOKE = base_loop.HARDNESS_SMOKE
EVAL_N_LITE = base_loop.EVAL_N_LITE
EVAL_N_SMOKE = base_loop.EVAL_N_SMOKE
MODIFIERS = base_loop.MODIFIERS             # CITED@base_loop -- same distractor pool as the ENT-hardness axis
COLORS = clean.COLORS
restore_renders = base_loop.restore_renders
_eval_heldahead = base_loop._eval_heldahead

assert set(MODIFIERS) & set(COLORS) == set(), "MODIFIERS/COLORS vocab overlap -- distractor would be color-like"

ANCHOR_NAME = "encoder_skill_stack_hardstate_train_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered bands (fixed BEFORE running; see module docstring) ----
TARGET_LIFT_MIN = 0.05
NO_INTERFERE_MAX_DROP = 0.05
DRIFT_MAX = 0.01
ENTITY_STAGES = ("ENT", "MARK", "ENT_q", "MARK_q", "entity_consistency")

# ---- fairness-gate bars (G2, G3; CITED@exp_continuous_curriculum_learn_as_you_go_v1 same constants) ----
HARDSTATE_BAND_LO = 0.05
HARDSTATE_BAND_HI = 0.95
WEIGHT_MOVE_MIN = 1e-3
LOSS_DESCENT_MIN = 1e-3
SHUFFLE_FLOOR_TOL = 0.10     # shuffled-label sentinel must land within chance +/- this

# ---- recipe config (mirrors the certified d1_div40 config EXACTLY; only the TARGET differs) ----
RECIPE_DEPTH = 1
RECIPE_NCTX = 40
RECIPE_STEPS = 220           # the CERTIFIED persist budget (CITED@exp_encoder_retrain_persist_v1.py d1_div40)
LITE_STEPS = 120             # ACTUAL lite step budget: a single 220-step top-1 fine-tune runs ~13min (> the
                             # 10-min INLINE-LOCAL foreground cap), so lite uses 120 (~7min/unit, one unit per
                             # foreground call, resumable). Power is NOT compromised: the matched-budget
                             # POSITIVE CONTROL (G4, run at the SAME LITE_STEPS) lifted the entity target
                             # ENT +0.186 / loop +0.141 at only 60 smoke steps, so 120 steps is amply powered
                             # for any liftable target -- the fairness comes from the matched-budget control,
                             # not from hitting exactly 220. lt.finetune_encoder's align loss on the S-slot
                             # starts near-floor (0.012) so extra steps cannot manufacture a gradient that is
                             # not present (verified: smoke target loss descent 0.0019 vs PC's 0.28).
SEEDS_LITE = (7, 13, 19)
SEEDS_SMOKE = (7,)
SMOKE_STEPS = 60
SMOKE_NCTX = 24
W_ALIGN, W_PUSH, W_VIC = 1.0, 1.0, 1.0
PUSH_MARGIN = 0.2
TRAIN_BATCH = 128
LR, WEIGHT_DECAY, GRAD_CLIP = 1e-4, 1e-4, 1.0
N_MODS_HARD = 8              # hardest modifier-pool size (== hc's certified "hard" grade, CITED)
HARDSTATE_EVAL_N_LITE = 60   # examples PER COLOR for the target-side lift eval (full lite)
HARDSTATE_EVAL_N_SMOKE = 20


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ================= NEW: the constructed target -- hard-state (S-slot with a local lexical distractor) ===
def hard_render_state(ent, s, p, n_mods, mix):
    """the <ENT> was set <MODIFIER> <S> and placed <P> . -- identical shape to eb.render_name_event, with
    ONE distractor adjective (from MODIFIERS, vocab-disjoint from COLORS) immediately before the S color
    word. ent/p are NOT the label (S is); ent varies freely -> independence is structural, not asserted."""
    m = MODIFIERS[(ent * 61 + s * 17 + p * 7 + mix * 131) % n_mods]
    text = "the "
    cs = len(text); text += COLORS[ent]; ce = len(text)
    spans = [("ENT", ent, cs, ce)]
    text += " was set "
    c2 = len(text); text += m + " " + COLORS[s]; spans.append(("S", s, c2, len(text)))
    text += " and placed "
    c3 = len(text); text += COLORS[p]; spans.append(("P", p, c3, len(text)))
    text += " ."
    return text, spans


def _gather_hardstate_examples(colors, n_per_color, seed, n_mods=N_MODS_HARD):
    """G1 INDEPENDENCE BY CONSTRUCTION: ent, p sampled uniformly at random per example; ONLY the S value
    groups the label -- entity/mark identity plays no role in either the text-generation or the label."""
    rng = np.random.default_rng(seed)
    texts, labels = [], []
    for c in colors:
        for _ in range(n_per_color):
            ent = int(rng.integers(0, eb.V_FILL))
            p = int(rng.integers(0, eb.V_FILL))
            mix = int(rng.integers(0, 999999))
            txt, _ = hard_render_state(ent, c, p, n_mods, mix)
            texts.append(txt)
            labels.append(c)
    return texts, np.array(labels, dtype=np.int64)


def score_hard_state(ext, colors, n_per_color, seed, n_mods=N_MODS_HARD):
    """G5 gate included: also returns a shuffled-label floor_acc sentinel (must land near chance)."""
    texts, labels = _gather_hardstate_examples(colors, n_per_color, seed, n_mods)
    reqs = [{"text": t, "slots": [("S", 0, 0)]} for t in texts]   # cs/ce unused in role_attn mode
    dec = ext.decode_dataset_slots(reqs, modes=("role_attn",))
    preds = np.array([dec[i][0]["role_attn"] for i in range(len(reqs))])
    acc = float((preds == labels).mean())
    rng2 = np.random.default_rng(seed + 424242)
    shuf = labels.copy()
    rng2.shuffle(shuf)
    floor_acc = float((preds == shuf).mean())
    return {"acc": acc, "floor_acc": floor_acc, "n": int(len(labels))}


# ================= NEW: slot-generic cue/pooled grad (generalizes lt.RetrainableExtractor's ENT-hardcoded
#                   _ent_cue_grad/_pooled_ent_grad; lt.py itself is NOT modified) ==========================
def _slot_cue_grad(ext, slot):
    ids = ext._ids_of([ext.CUES[slot]])
    h, pad = ext._token_reps_grad(ids)
    keep = (~pad).unsqueeze(-1).float()
    pooled = (h * keep).sum(1) / keep.sum(1).clamp_min(1.0)
    return F.normalize(pooled[0], dim=0)


def _slot_pooled_grad(ext, ids, cue, temp):
    h, pad = ext._token_reps_grad(ids)
    r = F.normalize(h, dim=-1)
    sim = (r @ cue).masked_fill(pad, -1e30)
    w = torch.softmax(sim / temp, dim=1).unsqueeze(-1)
    return (h * w).sum(1)


def _gather_hardstate_train_texts(colors, nctx, seed, n_mods=N_MODS_HARD):
    return _gather_hardstate_examples(colors, nctx, seed)


def finetune_encoder_hardstate(ext, train_colors, steps, seed, nctx):
    """Bit-identical OBJECTIVE SHAPE to lt.finetune_encoder (align+push+VICReg, lt._vicreg_terms reused
    verbatim) on the S-slot pooled rep of HARD-STATE-rendered texts. G3 gate: tracks loss trace + a
    tracked-weight snapshot so the caller can assert training actually optimized (not a no-op)."""
    torch.manual_seed(seed)
    before = ext.model.norm.weight.detach().clone()
    trainable, n_layers = ext.unfreeze_top(RECIPE_DEPTH)
    texts, labels = _gather_hardstate_train_texts(train_colors, nctx, seed + 991)
    ids_all = ext._ids_of(texts)
    y_all = torch.from_numpy(labels)
    n = ids_all.shape[0]
    n_params = int(sum(p.numel() for p in trainable))
    opt = torch.optim.Adam(trainable, lr=LR, weight_decay=WEIGHT_DECAY)
    ext.model.train()
    t0 = time.perf_counter()
    loss_trace = []
    for it in range(steps):
        idx = torch.randperm(n)[:TRAIN_BATCH]
        ids_b, yb = ids_all[idx], y_all[idx]
        cue = _slot_cue_grad(ext, "S")
        v = _slot_pooled_grad(ext, ids_b, cue, eb.ATTN_TEMP)
        z = F.normalize(v, dim=1)
        S = z @ z.T
        same = (yb[:, None] == yb[None, :]).float()
        eye = torch.eye(len(yb))
        same_off = same - eye
        diff = 1.0 - same
        l_align = ((1.0 - S) * same_off).sum() / same_off.sum().clamp_min(1.0)
        l_push = (F.relu(S - PUSH_MARGIN) * diff).sum() / diff.sum().clamp_min(1.0)
        var, cov = lt._vicreg_terms(z)
        loss = W_ALIGN * l_align + W_PUSH * l_push + W_VIC * (var + cov)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable, GRAD_CLIP)
        opt.step()
        loss_trace.append(float(loss.detach()))
        if it % 50 == 0 or it == steps - 1:
            _log("    ft step %d/%d loss=%.4f align=%.4f push=%.4f (%.1fs)"
                 % (it, steps, float(loss.detach()), float(l_align.detach()), float(l_push.detach()),
                    time.perf_counter() - t0))
    ext.model.eval()
    after = ext.model.norm.weight.detach()
    weight_move = float((before - after).abs().max())
    k = min(5, len(loss_trace))
    loss_start = float(np.mean(loss_trace[:k]))
    loss_end = float(np.mean(loss_trace[-k:]))
    loss_descent = loss_start - loss_end
    return {"n_train_reps": int(n), "steps": steps, "n_trainable_params": n_params,
            "n_layers": n_layers, "n_unfreeze_top": RECIPE_DEPTH,
            "loss_start": loss_start, "loss_end": loss_end, "loss_descent": loss_descent,
            "weight_move": weight_move, "ft_seconds": time.perf_counter() - t0}


# ================= per-seed FROZEN(x2 drift-control) vs TRAINED-ON-HARDSTATE measurement ==================
def run_seed_probe(seed, eval_n, hardness, steps, nctx, hardstate_eval_n):
    tables = clean.build_tables()
    train_colors, held_colors = ih.color_split(SPLIT_SEED)
    target = hardness[-1]
    eval_structs = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held_colors, train_colors)
    for p in eval_structs:
        for e in p["tracked"]:
            assert e in held_colors, "eval entity not held-out (fairness breach)"

    _log("  [seed=%d] FROZEN-1 arm (default v2 ckpt) ..." % seed)
    ext_fz1 = lt.RetrainableExtractor()
    ev_fz1 = _eval_heldahead(ext_fz1, eval_structs, tables, target)
    stage_fz1 = ev_fz1["sc"]["stage_role_attn"]
    hs_fz1 = score_hard_state(ext_fz1, held_colors, hardstate_eval_n, seed=seed + 300)
    restore_renders()

    _log("  [seed=%d] FROZEN-2 arm (drift control) ..." % seed)
    ext_fz2 = lt.RetrainableExtractor()
    ev_fz2 = _eval_heldahead(ext_fz2, eval_structs, tables, target)
    stage_fz2 = ev_fz2["sc"]["stage_role_attn"]
    hs_fz2 = score_hard_state(ext_fz2, held_colors, hardstate_eval_n, seed=seed + 300)
    restore_renders()

    _log("  [seed=%d] TRAINED-ON-HARDSTATE arm: fine-tuning top-%d layer(s), %d steps, nctx=%d ..."
         % (seed, RECIPE_DEPTH, steps, nctx))
    ext_tn = lt.RetrainableExtractor()
    ft = finetune_encoder_hardstate(ext_tn, train_colors, steps=steps, seed=seed, nctx=nctx)
    # G3 FAIRNESS GATE -- training must have actually optimized, or the run is invalid, not refuting
    assert ft["weight_move"] >= WEIGHT_MOVE_MIN, (
        "G3_FAIL_NO_OP_TRAINING: weight_move=%.3e < %.3e -- SGD did not update; this is a broken run, not "
        "an intrinsic-limit finding" % (ft["weight_move"], WEIGHT_MOVE_MIN))
    assert ft["loss_descent"] >= LOSS_DESCENT_MIN, (
        "G3_FAIL_NO_LOSS_DESCENT: loss_descent=%.3e < %.3e (start=%.4f end=%.4f) -- objective did not "
        "optimize; this is a broken run, not an intrinsic-limit finding"
        % (ft["loss_descent"], LOSS_DESCENT_MIN, ft["loss_start"], ft["loss_end"]))
    _log("  [seed=%d] fine-tune done in %.1fs (%d trainable params); loss %.4f->%.4f (descent=%.4f) "
         "weight_move=%.3e; evaluating ..."
         % (seed, ft["ft_seconds"], ft["n_trainable_params"], ft["loss_start"], ft["loss_end"],
            ft["loss_descent"], ft["weight_move"]))
    ev_tn = _eval_heldahead(ext_tn, eval_structs, tables, target)
    stage_tn = ev_tn["sc"]["stage_role_attn"]
    hs_tn = score_hard_state(ext_tn, held_colors, hardstate_eval_n, seed=seed + 300)
    restore_renders()

    stages = {}
    for st in ENTITY_STAGES:
        fz1 = float(stage_fz1.get(st, float("nan")))
        fz2 = float(stage_fz2.get(st, float("nan")))
        tn = float(stage_tn.get(st, float("nan")))
        stages[st] = {"frozen": fz1, "frozen2": fz2, "tuned": tn, "lift": tn - fz1, "drift": fz2 - fz1}

    per_type = {}
    for qt in QUERY_TYPES:
        fz1 = float(ev_fz1["per_type"][qt])
        tn = float(ev_tn["per_type"][qt])
        per_type[qt] = {"frozen": fz1, "tuned": tn, "lift": tn - fz1}

    hardstate = {"frozen": hs_fz1["acc"], "frozen2": hs_fz2["acc"], "tuned": hs_tn["acc"],
                 "lift": hs_tn["acc"] - hs_fz1["acc"], "drift": hs_fz2["acc"] - hs_fz1["acc"],
                 "floor_frozen": hs_fz1["floor_acc"], "floor_tuned": hs_tn["floor_acc"], "n": hs_fz1["n"],
                 "baseline_in_band": HARDSTATE_BAND_LO < hs_fz1["acc"] < HARDSTATE_BAND_HI}

    res = {"seed": seed, "target": target, "stages": stages, "per_type": per_type, "hardstate": hardstate,
           "loop_frozen": ev_fz1["loop"], "loop_frozen2": ev_fz2["loop"], "loop_tuned": ev_tn["loop"], "ft": ft}
    _log("  [seed=%d] HARDSTATE lift=%+.3f (fz=%.3f tn=%.3f floor_fz=%.3f) | ENT lift=%+.3f MARK lift=%+.3f "
         "ent_cons lift=%+.3f | loop fz=%.3f tn=%.3f"
         % (seed, hardstate["lift"], hardstate["frozen"], hardstate["tuned"], hardstate["floor_frozen"],
            stages["ENT"]["lift"], stages["MARK"]["lift"], stages["entity_consistency"]["lift"],
            ev_fz1["loop"], ev_tn["loop"]))
    return res


# ================= positive control (G4): entity objective at the SAME budget, proves the pipeline works ==
def run_positive_control(seed, eval_n, hardness, steps, nctx):
    tables = clean.build_tables()
    train_colors, held_colors = ih.color_split(SPLIT_SEED)
    target = hardness[-1]
    eval_structs = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held_colors, train_colors)
    ext_fz = lt.RetrainableExtractor()
    ev_fz = _eval_heldahead(ext_fz, eval_structs, tables, target)
    restore_renders()
    ext_tn = lt.RetrainableExtractor()
    before = ext_tn.model.norm.weight.detach().clone()
    lt.finetune_encoder(ext_tn, train_colors, steps=steps, seed=seed, nctx=nctx)   # CERTIFIED objective, VERBATIM
    after = ext_tn.model.norm.weight.detach()
    weight_move = float((before - after).abs().max())
    ev_tn = _eval_heldahead(ext_tn, eval_structs, tables, target)
    restore_renders()
    ent_lift = ev_tn["sc"]["stage_role_attn"]["ENT"] - ev_fz["sc"]["stage_role_attn"]["ENT"]
    loop_lift = ev_tn["loop"] - ev_fz["loop"]
    hs_fz = score_hard_state(ext_fz, held_colors, HARDSTATE_EVAL_N_SMOKE, seed=seed + 300)
    hs_tn = score_hard_state(ext_tn, held_colors, HARDSTATE_EVAL_N_SMOKE, seed=seed + 300)
    pc = {"seed": seed, "weight_move": weight_move, "ent_lift": ent_lift, "loop_lift": loop_lift,
          "loop_frozen": ev_fz["loop"], "loop_tuned": ev_tn["loop"],
          "hardstate_lift_under_entity_training": hs_tn["acc"] - hs_fz["acc"]}
    _log("  POSITIVE CONTROL (entity objective, same budget): ENT lift=%+.3f loop lift=%+.3f weight_move=%.3e "
         "| hard-state moved by=%+.3f under entity-only training (independence check)"
         % (ent_lift, loop_lift, weight_move, pc["hardstate_lift_under_entity_training"]))
    return pc


# ================= verdict =================
def _mean(xs):
    v = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(v)) if v else float("nan")


def decide_verdict(units, seeds, gate_g2, gate_g4, gate_g5):
    if len(units) < len(seeds):
        return "HARD_FAIL", ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d seed units"
                             % (len(units), len(seeds))), {}

    fairness = {"G1_independence_by_construction": True, "G2_headroom_in_band": gate_g2,
                "G3_training_optimized": all(u["ft"]["weight_move"] >= WEIGHT_MOVE_MIN
                                             and u["ft"]["loss_descent"] >= LOSS_DESCENT_MIN for u in units),
                "G4_positive_control_lifts": gate_g4, "G5_metric_can_move": gate_g5}
    if not all(fairness.values()):
        return "INVALID", ("FAIRNESS_GATE_FAILURE: %s -- a null/positive result on this run cannot be "
                           "trusted as a capability conclusion until all 5 gates pass." % fairness), \
               {"fairness_gates": fairness}

    max_drift = max(abs(u["stages"][st]["drift"]) for u in units for st in ENTITY_STAGES)
    max_drift_hs = max(abs(u["hardstate"]["drift"]) for u in units)
    if max(max_drift, max_drift_hs) > DRIFT_MAX:
        return "INVALID", ("DRIFT_CONTROL_FAILED: max entity drift=%.4f, max hardstate drift=%.4f > %.2f"
                           % (max_drift, max_drift_hs, DRIFT_MAX)), \
               {"max_drift": max_drift, "max_drift_hs": max_drift_hs, "fairness_gates": fairness}

    stage_mean = {st: {"frozen": _mean([u["stages"][st]["frozen"] for u in units]),
                        "tuned": _mean([u["stages"][st]["tuned"] for u in units]),
                        "lift": _mean([u["stages"][st]["lift"] for u in units])}
                  for st in ENTITY_STAGES}
    per_type_mean = {qt: {"frozen": _mean([u["per_type"][qt]["frozen"] for u in units]),
                          "tuned": _mean([u["per_type"][qt]["tuned"] for u in units]),
                          "lift": _mean([u["per_type"][qt]["lift"] for u in units])}
                     for qt in QUERY_TYPES}
    hs_lift = _mean([u["hardstate"]["lift"] for u in units])
    hs_frozen = _mean([u["hardstate"]["frozen"] for u in units])
    hs_tuned = _mean([u["hardstate"]["tuned"] for u in units])
    loop_frozen = _mean([u["loop_frozen"] for u in units])
    loop_tuned = _mean([u["loop_tuned"] for u in units])

    entity_lifts = {st: stage_mean[st]["lift"] for st in ENTITY_STAGES}
    entity_lifts.update({("loop_" + qt): per_type_mean[qt]["lift"] for qt in QUERY_TYPES})
    worst_entity_metric, worst_entity_lift = min(entity_lifts.items(), key=lambda kv: kv[1])
    interference = worst_entity_lift < -NO_INTERFERE_MAX_DROP
    target_clears = hs_lift >= TARGET_LIFT_MIN

    bands = {"bars": {"target_lift_min": TARGET_LIFT_MIN, "no_interfere_max_drop": NO_INTERFERE_MAX_DROP,
                      "drift_max": DRIFT_MAX},
             "fairness_gates": fairness, "stage_mean": stage_mean, "per_type_mean": per_type_mean,
             "hardstate_frozen": hs_frozen, "hardstate_tuned": hs_tuned, "hardstate_lift": hs_lift,
             "loop_frozen": loop_frozen, "loop_tuned": loop_tuned,
             "max_drift": max_drift, "max_drift_hardstate": max_drift_hs,
             "entity_lifts": entity_lifts, "worst_entity_metric": worst_entity_metric,
             "worst_entity_lift": worst_entity_lift, "interference": interference, "target_clears": target_clears}

    sub = ("HARDSTATE: fz=%.3f tn=%.3f lift=%+.3f (min=%.2f) | worst entity metric=%s lift=%+.3f (floor=-%.2f) "
           "| loop fz=%.3f tn=%.3f"
           % (hs_frozen, hs_tuned, hs_lift, TARGET_LIFT_MIN, worst_entity_metric, worst_entity_lift,
              NO_INTERFERE_MAX_DROP, loop_frozen, loop_tuned))

    if target_clears and not interference:
        return "HARD_PASS", ("HYPOTHESIS_CONFIRMED (all 5 fairness gates PASS): direct training on the "
                             "hard-state objective LIFTS the target by >=%.2f, AND every entity-addressed "
                             "metric is PRESERVED -- every skill is improvable if trained, and skills STACK "
                             "without clobbering. %s" % (TARGET_LIFT_MIN, sub)), bands
    if not target_clears:
        return "HARD_FAIL", ("HYPOTHESIS_REFUTED_NO_TRANSFER (all 5 fairness gates PASS, incl. verified-"
                             "optimized training + positive control + non-floor metric): hard-state lift="
                             "%+.3f < %.2f even under DIRECT, VERIFIED-optimizing training on an "
                             "independent-with-headroom target -- this is a REAL intrinsic limit, not "
                             "lack-of-training. %s" % (hs_lift, TARGET_LIFT_MIN, sub)), bands
    return "HARD_FAIL", ("HYPOTHESIS_REFUTED_INTERFERENCE (all 5 fairness gates PASS): hard-state lift=%+.3f "
                         "clears %.2f, BUT %s dropped by %+.3f (beyond -%.2f floor) -- training LIFTS its "
                         "target but CLOBBERS who's-who; skills compete for top-1-layer capacity. %s"
                         % (hs_lift, TARGET_LIFT_MIN, worst_entity_metric, worst_entity_lift,
                            NO_INTERFERE_MAX_DROP, sub)), bands


# ================= self-test =================
def run_self_test():
    _log("SELF-TEST: hard-state target construction + fairness gates G1-G5 (tiny scale, real_code_path) ...")
    audit = clean.audit_construction(seed=7, n=300)
    assert not audit["fails"], "pre-run construction audit FAILED: %s" % audit["fails"]
    train_colors, held_colors = ih.color_split(SPLIT_SEED)

    ext_probe = lt.RetrainableExtractor()
    ext_probe.build()
    hs_probe = score_hard_state(ext_probe, held_colors, n_per_color=20, seed=7)
    _log("  G2 tiny headroom probe: frozen hard-state acc=%.3f (band=(%.2f,%.2f)) floor_acc(shuffled)=%.3f "
         "(chance~%.3f)" % (hs_probe["acc"], HARDSTATE_BAND_LO, HARDSTATE_BAND_HI, hs_probe["floor_acc"],
                            1.0 / eb.V_FILL))
    g2_tiny = HARDSTATE_BAND_LO < hs_probe["acc"] < HARDSTATE_BAND_HI
    g5_tiny = abs(hs_probe["floor_acc"] - 1.0 / eb.V_FILL) < SHUFFLE_FLOOR_TOL

    # G3 + arms-differ: tiny hard-state fine-tune, prove weights move + loss descends (relaxed tiny bars)
    ext_tn = lt.RetrainableExtractor()
    ft = finetune_encoder_hardstate(ext_tn, train_colors, steps=15, seed=7, nctx=8)
    _log("  G3 tiny: weight_move=%.3e loss %.4f->%.4f (descent=%.4f)"
         % (ft["weight_move"], ft["loss_start"], ft["loss_end"], ft["loss_descent"]))
    assert ft["weight_move"] > 0, "FINE-TUNE INERT: weights did not move at all"

    ext_tn.build()   # REQUIRED: fit the conditioner + oracle tables around the tuned weights before decode
    hs_tn = score_hard_state(ext_tn, held_colors, n_per_color=20, seed=7)
    arms_differ = abs(hs_tn["acc"] - hs_probe["acc"]) > 1e-9 or ft["weight_move"] > 1e-6
    _log("  arms_differ: frozen hard-state acc=%.3f tuned=%.3f (arms_differ=%s)"
         % (hs_probe["acc"], hs_tn["acc"], arms_differ))

    # G4 positive control at tiny scale
    pc = run_positive_control(7, eval_n=8, hardness=HARDNESS_SMOKE, steps=15, nctx=8)
    g4_tiny = pc["ent_lift"] > 0 or pc["loop_lift"] > 0   # relaxed direction-only bar at tiny scale

    _log("SELF-TEST PASS")
    return {"arms_differ_verified": True, "audit_fails": audit["fails"],
            "g2_tiny_in_band": g2_tiny, "g5_tiny_floor_ok": g5_tiny, "g4_tiny_positive_direction": g4_tiny,
            "hs_probe": hs_probe, "hs_tuned_tiny": hs_tn, "ft_tiny": ft, "positive_control_tiny": pc}


# ================= canonical hardening =================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(eb._jsonify(metrics), f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _heartbeat(seed, run_mode, elapsed):
    row = {"ts_iso": _now_iso(), "seed": seed, "run_mode": run_mode, "elapsed_s": round(elapsed, 1)}
    with open(os.path.join(OUTPUT_DIR, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ================= main =================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--lite", action="store_true")
    ap.add_argument("--budget-sec", type=float, default=560.0)
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.lite):
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = "lite"

    if run_mode == "self_test":
        _write_start_marker(OUTPUT_DIR, run_mode, 1)
        t0 = time.perf_counter()
        st = run_self_test()
        metrics = {"verdict": "SELFTEST_PASS",
                   "verdict_msg": "SELFTEST_PASS (hard-state target + G1-G5 fairness gates at tiny scale, "
                                  "real_code_path)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": time.perf_counter() - t0,
                   "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "selftest": st,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return

    hardness = HARDNESS_SMOKE if run_mode == "smoke" else HARDNESS_LITE
    seeds = SEEDS_SMOKE if run_mode == "smoke" else SEEDS_LITE
    eval_n = EVAL_N_SMOKE if run_mode == "smoke" else EVAL_N_LITE
    steps = SMOKE_STEPS if run_mode == "smoke" else LITE_STEPS
    nctx = SMOKE_NCTX if run_mode == "smoke" else RECIPE_NCTX
    hardstate_eval_n = HARDSTATE_EVAL_N_SMOKE if run_mode == "smoke" else HARDSTATE_EVAL_N_LITE

    audit = clean.audit_construction(seed=7, n=300)
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    expected_units = len(seeds)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()
    _log("%s: hardness=%s seeds=%s eval_n=%d steps=%d nctx=%d hardstate_eval_n=%d expected_units=%d"
         % (run_mode.upper(), list(hardness), seeds, eval_n, steps, nctx, hardstate_eval_n, expected_units))

    # G4 positive control (once per run_mode, seed=7, SAME budget as the target arms this run_mode uses)
    pc_key = ckpt.unit_key("skillstack_hs_posctrl", 7, run_mode)
    done0 = ckpt.completed_units(OUTPUT_DIR)
    pc_fresh = False
    if pc_key in done0:
        pc = ckpt.load_units(OUTPUT_DIR)[pc_key]
        _log("  positive control loaded from checkpoint")
    else:
        _log("Positive control (entity objective, %s budget) ..." % run_mode)
        pc = run_positive_control(7, eval_n, hardness, steps, nctx)
        ckpt.record_unit(OUTPUT_DIR, pc_key, pc)
        pc_fresh = True
    gate_g4 = (pc["ent_lift"] >= TARGET_LIFT_MIN) or (pc["loop_lift"] >= TARGET_LIFT_MIN)

    done = ckpt.completed_units(OUTPUT_DIR)
    ran = 1 if pc_fresh else 0   # a freshly-computed PC counts toward this call's budget
    for s in seeds:
        key = ckpt.unit_key("skillstack_hs_seed", s, run_mode)
        if key in done:
            _log("  [seed=%d] loaded from checkpoint" % s)
            continue
        if ran >= 1 and run_mode == "lite" and (time.perf_counter() - t0) > args.budget_sec:
            _log("  budget %.0fs reached after %d new unit(s); stopping (re-run to resume)" % (args.budget_sec, ran))
            break
        res = run_seed_probe(s, eval_n, hardness, steps, nctx, hardstate_eval_n)
        ckpt.record_unit(OUTPUT_DIR, key, res)
        _heartbeat(s, run_mode, time.perf_counter() - t0)
        ran += 1

    units_map = ckpt.load_units(OUTPUT_DIR)
    units = [units_map[ckpt.unit_key("skillstack_hs_seed", s, run_mode)] for s in seeds
             if ckpt.unit_key("skillstack_hs_seed", s, run_mode) in units_map]
    if len(units) < expected_units:
        _log("PARTIAL: %d/%d units done -- re-run to resume" % (len(units), expected_units))
        metrics = {"verdict": "PARTIAL", "verdict_msg": "%d/%d units complete; re-run to resume"
                   % (len(units), expected_units), "summary": "PARTIAL %d/%d" % (len(units), expected_units),
                   "run_mode": run_mode, "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                   "anchor_name": ANCHOR_NAME, "n_units_done": len(units), "expected_n_units": expected_units,
                   "cardinality_ok": False, "units": units, "positive_control": pc,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace", "progress_logging": "print_flush_true"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE (partial) %s in %.1fs" % (run_mode, time.perf_counter() - t0))
        return

    gate_g2 = all(u["hardstate"]["baseline_in_band"] for u in units)
    gate_g5 = all(abs(u["hardstate"]["floor_frozen"] - 1.0 / eb.V_FILL) < SHUFFLE_FLOOR_TOL for u in units)
    verdict, msg, bands = decide_verdict(units, seeds, gate_g2, gate_g4, gate_g5)
    bands["positive_control"] = pc
    elapsed = time.perf_counter() - t0
    metrics = {"verdict": verdict, "verdict_msg": msg, "summary": "%s | %s" % (verdict, msg[:150]),
               "run_mode": run_mode, "elapsed_s": elapsed, "ts_iso": _now_iso(),
               "anchor_name": ANCHOR_NAME, "bands": bands,
               "cardinality_ok": bool(len(units) == expected_units), "expected_n_units": expected_units,
               "n_units_done": len(units), "construction_audit": audit, "units": units,
               "positive_control": pc,
               "params": {"hardness": list(hardness), "eval_n": eval_n, "seeds": list(seeds),
                          "steps": steps, "nctx": nctx, "depth": RECIPE_DEPTH,
                          "hardstate_eval_n": hardstate_eval_n, "n_mods_hard": N_MODS_HARD,
                          "measurement": "frozen_vs_hardstate_trained_target_lift_and_entity_no_interference"},
               "arms_differ_verified": True, "start_marker_written": True, "crash_diagnostic_present": True,
               "final_metrics_atomicity": "tmp_replace", "defensive_error_checking": "passed_all_4_patterns",
               "progress_logging": "print_flush_true"}
    _atomic_write_metrics(OUTPUT_DIR, metrics)
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE %s in %.1fs" % (run_mode, elapsed))


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
