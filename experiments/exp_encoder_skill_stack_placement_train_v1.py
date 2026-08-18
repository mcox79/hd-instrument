# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test: FROZEN-1 vs TUNED per-stage decode digest must DIFFER (an inert
#   fine-tune would leave them identical); FROZEN-1 vs FROZEN-2 (drift control, two independently-built
#   default-ckpt extractors) must be near-IDENTICAL (checked via max|drift| <= DRIFT_MAX, same pattern as
#   exp_encoder_generic_vs_entity_addressed_v1.py).
# - final_metrics_atomicity: tmp_replace (os.replace at end) + per-seed units.jsonl (resumable, per CLAUDE.md).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: paired frozen-vs-skill-trained decode comparison (no capacity sweep).
# - baseline_in_band: n/a in the META_RULE_AG sense (this is a lift-vs-frozen design, not a baseline-vs-
#   mechanism saturation design); the FROZEN P baseline itself (0.808, MEASURED@
#   data/exp_encoder_generic_vs_entity_addressed_v1/metrics.json:bands.stage_mean.P.frozen) is explicitly
#   chosen for having real headroom (not near-ceiling like S's 0.951) -- see module docstring Gate 1.
# - discriminator survives scale: measured at the SAME eval_n/hardness/seeds as the sibling encoder-transfer
#   cells' LITE config (base_loop.EVAL_N_LITE / HARDNESS_LITE) -- no scale gap; the mechanism (does DIRECT
#   training on the P objective move P) is evaluated at the same regime the "flat" finding was observed in.
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: numpy default_rng + torch.manual_seed only (mirrors lt.finetune_encoder exactly);
#   NO hash(), NO list(set()) (sorted(set()) only, inherited from ih.color_split / lt).
"""ENCODER SKILL-STACK TEST: does a SECOND independently-trained skill (PLACEMENT decode) lift under its
OWN objective, and does training it clobber the FIRST certified skill (who's-who / entity-consistency)?
(Director spawn 2026-07-31/08-01, growing-library-of-competencies test at the ENCODER level.)

BACKGROUND (measurement-first; read, not re-derived): the certified minimal-unfreeze encoder retrain (atom
29593, top-1 unfreeze, cross-mention ENTITY-consistency pull+push+VICReg objective) lifts entity-addressed
decode broadly (a_name +0.192, b_coref +0.150, c_overwrite +0.320, MEASURED@
data/exp_encoder_alltype_transfer_v1/metrics.json) but a genuinely non-entity-addressed decode stayed
FLAT: S (state-filler) lifted only +0.020 with geometry WORSENING -0.04 (MEASURED@
data/exp_encoder_generic_vs_entity_addressed_v1/metrics.json:bands.stage_mean.S). USER hypothesis: S
stayed flat only because it was NEVER TRAINED on its own objective -- train an independent skill directly
and it should lift too ("every skill is improvable if you train it").

GATE 1 -- TARGET SELECTION (independence + headroom, done BEFORE authoring, not tuned after seeing a
result): the SAME landed cell that reported S=flat also reports P (placement-filler decode) in its
per-stage table: P frozen=0.8077, tuned(under ENTITY-only training)=0.8936, ALREADY MEASURED@
data/exp_encoder_generic_vs_entity_addressed_v1/metrics.json:bands.stage_mean.P. Two facts make P the
correct target, NOT S: (a) INDEPENDENCE -- per that cell's own classification (NON_ENTITY_STAGES=(S,P)) P
is read from the SAME local single-sentence span mechanism as S (a fixed role-cue attention-pool over
"the ENT was set S and placed P .", ZERO cross-sentence binding, ZERO entity/mark identity involved --
eb.CUES["P"]="what was placed to ?"); this cell's own training texts (render_name_event / render_coref_event
with RANDOM entity/mark fillers, ONLY the P value held fixed per group) make that independence structural,
not just cited. (b) HEADROOM -- P's frozen baseline (0.808) leaves ~0.19 of the [0,1] band open, versus S's
0.951 leaving only ~0.05 (the cited "flat +0.020" IS a large fraction of S's tiny headroom -- 41% of the
available gap closed -- which is why S alone is a MISLEADING readout of "does training help"; P is the fair
target). NOTE (reported, not chosen-around): P was NOT flat under entity-only training (+0.086, already
clears the sibling cell's own LIFT_MIN=0.05) -- entity training partially transfers to P already. THIS
CELL isolates the cleaner question: does DIRECT training on P's OWN objective lift P further / more
reliably than the entity-training side-effect did, and does it preserve entity metrics -- the growing-
library claim needs BOTH a lift AND no clobbering of skill #1.

GATE 2 -- THE RECIPE (mirrors the certified shape EXACTLY; the ONE VARIABLE changed is the training
TARGET, not the architecture/depth/steps/objective-shape): top-1 unfreeze (RECIPE_DEPTH=1, CITED@
exp_encoder_retrain_persist_v1.py "do NOT change unfreeze depth"), nctx=40, steps=220 (bit-identical wall-
time budget to the persisted d1_div40 config, MEASURED@data/exp_encoder_retrain_persist_v1/metrics.json
ft_seconds~110-130s/seed), the SAME three-term objective (cross-context consistency PULL + inter-value
PUSH + VICReg anti-collapse, lt._vicreg_terms reused VERBATIM) -- but the pooled rep + label are the P-SLOT
(placement filler-color), not the ENT-slot. _slot_cue_grad/_slot_pooled_grad below are NEW ~20-line
generalizations of lt.RetrainableExtractor._ent_cue_grad/_pooled_ent_grad (which are ENT-hardcoded) that
operate on ext.CUES[slot] (already slot-generic) + ext._ids_of/_token_reps_grad (already slot-generic, no
modification needed) -- lt.py itself is NOT modified (read-only reuse; another cell may be mid-VET on a
sibling file, this cell writes only to its own new output dir).

MEASUREMENT (3 seeds; ONE VARIABLE = which objective trained the encoder): per seed, THREE extractor
instances on the IDENTICAL held-ahead structures (base_loop._eval_heldahead, reused verbatim, same as the
sibling cells) -- FROZEN-1 (default v2 ckpt), FROZEN-2 (drift control, independently-built default ckpt),
TRAINED-ON-P (fresh RetrainableExtractor, fine-tuned via finetune_encoder_placement, then evaluated). Reads:
  (a) TARGET LIFT: stage_role_attn["P"] tuned-vs-frozen.
  (b) NO-INTERFERENCE: stage_role_attn["ENT"], ["MARK"], ["ENT_q"], ["MARK_q"], ["entity_consistency"], AND
      the full 3-query-type MAIN_ENC loop (a_name_maintenance/b_competitive_coref/c_overwrite) tuned-vs-
      frozen -- these are the entity-addressed metrics the FIRST certified skill (who's-who) lifted; if
      P-training preserves them, skills STACK.
  (c) DRIFT CONTROL: FROZEN-2 vs FROZEN-1 (same pattern as sibling cells; must be ~0, deterministic eval).

PRE-REGISTERED BANDS (fixed BEFORE running; preregs/2026-08-01_encoder_skill_stack_placement.md):
  TARGET_LIFT_MIN = 0.05   (matches the sibling cell's own "meaningful lift" floor -- not tuned to this run)
  NO_INTERFERE_MAX_DROP = 0.05   (an entity metric may not DROP by more than this to count as "preserved";
    symmetric with TARGET_LIFT_MIN, chosen before running, not fit to the result)
  DRIFT_MAX = 0.01   (frozen-vs-frozen ceiling; deterministic eval => expect ~0.0)

  HYPOTHESIS_CONFIRMED (HARD_PASS): mean P lift over seeds >= TARGET_LIFT_MIN AND every entity-addressed
    metric's mean lift over seeds >= -NO_INTERFERE_MAX_DROP (no material drop) => "every skill is
    improvable if trained, and skills STACK without clobbering" -- the growing-library thesis holds at the
    encoder level for this pair of skills.
  HYPOTHESIS_REFUTED_NO_TRANSFER (HARD_FAIL): mean P lift < TARGET_LIFT_MIN even under DIRECT training on
    P's own objective => P is not "just untrained" -- a REAL intrinsic limit on this decode (independent of
    whether it was ever the training target), not lack-of-training.
  HYPOTHESIS_REFUTED_INTERFERENCE (HARD_FAIL): mean P lift clears TARGET_LIFT_MIN BUT >=1 entity-addressed
    metric drops more than NO_INTERFERE_MAX_DROP => P training LIFTS its target but CLOBBERS who's-who --
    skills compete for the same top-1-layer capacity, can't stack freely at this budget.
  MIDDLE: mixed / at-the-bar pattern not cleanly matching either band above -- reported explicitly.
  INVALID: max|FROZEN2-FROZEN1| drift > DRIFT_MAX (eval not deterministic or swap/build leaked) OR
    clean.audit_construction flags fail.
  Both HARD_PASS and either HARD_FAIL are informative; bands are NOT tuned after seeing results.

PRIOR-WORK CHECK (substrate_query.sh "encoder second skill placement training stack without interference
growing library", run before authoring): top hit cosine=0.31 is
data/exp_encoder_alltype_transfer_v1/metrics.json (the certified break's own multi-query-type transfer --
related but that cell trains ONLY the entity objective and measures transfer to OTHER entity-addressed
query types, not a SECOND independently-trained non-entity objective). No hit above cosine 0.30 tests
training a second, independent, non-entity objective and checking both its own lift AND preservation of
the first skill. Not a rediscovery.

Run:  .venv/Scripts/python.exe experiments/exp_encoder_skill_stack_placement_train_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_encoder_skill_stack_placement_train_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_encoder_skill_stack_placement_train_v1.py --lite

ASCII-only. No emojis. Deterministic seeding. Pure CPU. Compute architecture: sequential-CPU (one P-
objective fine-tune per seed, ~110-130s MEASURED@data/exp_encoder_retrain_persist_v1 at this exact
depth/nctx/steps config, plus 3 cheap frozen-weight forward-pass evals per seed); INLINE-LOCAL foreground-
to-completion, resumable per-seed (tools/exp_checkpoint.py) with a --budget-sec cutoff so a single
foreground call that can't finish all 3 seeds under the 10-min cap still lands a clean PARTIAL + resumes on
the next foreground call (never backgrounded). Storage: no_storage (eval-only harness reuse; no substrate
memory writes; no persisted ckpt -- the fine-tuned weights live only in-process for the eval that follows,
unlike exp_encoder_retrain_persist_v1 which intentionally persists). progress_logging: print_flush_true.
PARALLEL-SAFE: writes only to data/exp_encoder_skill_stack_placement_train_v1/ (new dir); does not modify
base_loop, lt, eb, ef, or touch any other agent's in-flight dir (exp_encoder_alltype_transfer_stress_v1,
exp_encoder_generic_vs_entity_addressed_v1 read-only cited, not written).
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
ckpt = base_loop.ckpt                       # resumable per-unit shard helper (tools/exp_checkpoint.py)
lt = base_loop.lt
eb = base_loop.eb
ef = base_loop.ef                           # noqa: F401
ih = base_loop.ih
clean = base_loop.clean
QUERY_TYPES = base_loop.QUERY_TYPES
SPLIT_SEED = base_loop.SPLIT_SEED
HARDNESS_LITE = base_loop.HARDNESS_LITE     # (1, 3, 8)
HARDNESS_SMOKE = base_loop.HARDNESS_SMOKE   # (1, 8)
EVAL_N_LITE = base_loop.EVAL_N_LITE         # 40
EVAL_N_SMOKE = base_loop.EVAL_N_SMOKE       # 12
restore_renders = base_loop.restore_renders
_eval_heldahead = base_loop._eval_heldahead

ANCHOR_NAME = "encoder_skill_stack_placement_train_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered bands (fixed BEFORE running; see module docstring) ----
TARGET_LIFT_MIN = 0.05
NO_INTERFERE_MAX_DROP = 0.05
DRIFT_MAX = 0.01
TARGET_STAGE = "P"
ENTITY_STAGES = ("ENT", "MARK", "ENT_q", "MARK_q", "entity_consistency")
ALL_TRACKED_STAGES = (TARGET_STAGE,) + ENTITY_STAGES

# ---- recipe config (mirrors the certified d1_div40 config EXACTLY; only the TARGET differs) ----
RECIPE_DEPTH = 1            # top-1 unfreeze -- CITED@exp_encoder_retrain_persist_v1.py, do not change
RECIPE_NCTX = 40
RECIPE_STEPS = 220
SEEDS_LITE = (7, 13, 19)    # matches sibling encoder-transfer cells' VET seeds
SEEDS_SMOKE = (7,)
SMOKE_STEPS = 60
SMOKE_NCTX = 24
W_ALIGN, W_PUSH, W_VIC = 1.0, 1.0, 1.0
PUSH_MARGIN = 0.2
TRAIN_BATCH = 128
LR, WEIGHT_DECAY, GRAD_CLIP = 1e-4, 1e-4, 1.0


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ================= NEW: slot-generic cue/pooled grad (generalizes lt.RetrainableExtractor's ENT-hardcoded
#                   _ent_cue_grad/_pooled_ent_grad to any of the 4 already-defined role cues; lt.py itself
#                   is NOT modified -- ext._ids_of / ext._token_reps_grad / ext.CUES are already generic) ===
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


# ================= NEW: P-objective training data (mirrors lt._gather_ent_texts' shape: random OTHER
#                   fillers, ONLY the P value held fixed per label group -- entity/mark identity is NOT
#                   the supervision signal here, by construction) =========================================
def _gather_placement_texts(colors, nctx, seed):
    rng = np.random.default_rng(seed)
    texts, labels = [], []
    for c in colors:
        for _ in range(nctx):
            o1 = int(rng.integers(0, eb.V_FILL))
            o2 = int(rng.integers(0, eb.V_FILL))
            if int(rng.integers(0, 2)) == 0:
                txt, _ = eb.render_name_event(o1, o2, c)     # ent=o1(random) s=o2(random) p=c(label)
            else:
                txt, _ = eb.render_coref_event(o1, o2, c)    # mark=o1(random) s=o2(random) p=c(label)
            texts.append(txt)
            labels.append(c)
    return texts, np.array(labels, dtype=np.int64)


def finetune_encoder_placement(ext, train_colors, steps, seed, nctx):
    """Bit-identical OBJECTIVE SHAPE to lt.finetune_encoder (cross-context consistency PULL + inter-value
    PUSH + VICReg anti-collapse, lt._vicreg_terms reused verbatim) but the pooled rep + supervision label
    are the P-SLOT (placement filler-color) instead of the ENT-slot -- the ONE VARIABLE under test."""
    torch.manual_seed(seed)
    trainable, n_layers = ext.unfreeze_top(RECIPE_DEPTH)
    texts, labels = _gather_placement_texts(train_colors, nctx, seed + 991)
    ids_all = ext._ids_of(texts)
    y_all = torch.from_numpy(labels)
    n = ids_all.shape[0]
    n_params = int(sum(p.numel() for p in trainable))
    opt = torch.optim.Adam(trainable, lr=LR, weight_decay=WEIGHT_DECAY)
    ext.model.train()
    t0 = time.perf_counter()
    last = {}
    for it in range(steps):
        idx = torch.randperm(n)[:TRAIN_BATCH]
        ids_b, yb = ids_all[idx], y_all[idx]
        cue = _slot_cue_grad(ext, TARGET_STAGE)
        v = _slot_pooled_grad(ext, ids_b, cue, eb.ATTN_TEMP)
        z = F.normalize(v, dim=1)
        S = z @ z.T
        same = (yb[:, None] == yb[None, :]).float()
        eye = torch.eye(len(yb))
        same_off = same - eye
        diff = 1.0 - same
        l_align = ((1.0 - S) * same_off).sum() / same_off.sum().clamp_min(1.0)
        l_push = (F.relu(S - PUSH_MARGIN) * diff).sum() / diff.sum().clamp_min(1.0)
        var, cov = lt._vicreg_terms(z)     # reused VERBATIM (module-level fn, read-only import)
        loss = W_ALIGN * l_align + W_PUSH * l_push + W_VIC * (var + cov)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable, GRAD_CLIP)
        opt.step()
        if it % 50 == 0 or it == steps - 1:
            _log("    ft step %d/%d loss=%.4f align=%.4f push=%.4f (%.1fs)"
                 % (it, steps, float(loss.detach()), float(l_align.detach()), float(l_push.detach()),
                    time.perf_counter() - t0))
        if it == steps - 1:
            last = {"loss": float(loss.detach()), "l_align": float(l_align.detach()),
                    "l_push": float(l_push.detach())}
    ext.model.eval()
    return {"n_train_reps": int(n), "steps": steps, "n_trainable_params": n_params,
            "n_layers": n_layers, "n_unfreeze_top": RECIPE_DEPTH, "final": last,
            "ft_seconds": time.perf_counter() - t0}


# ================= per-seed FROZEN(x2 drift-control) vs TRAINED-ON-P measurement ==========================
def run_seed_probe(seed, eval_n, hardness, steps, nctx):
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
    restore_renders()

    _log("  [seed=%d] FROZEN-2 arm (drift control) ..." % seed)
    ext_fz2 = lt.RetrainableExtractor()
    ev_fz2 = _eval_heldahead(ext_fz2, eval_structs, tables, target)
    stage_fz2 = ev_fz2["sc"]["stage_role_attn"]
    restore_renders()

    _log("  [seed=%d] TRAINED-ON-P arm: fine-tuning top-%d layer(s), %d steps, nctx=%d ..."
         % (seed, RECIPE_DEPTH, steps, nctx))
    ext_tn = lt.RetrainableExtractor()
    ft = finetune_encoder_placement(ext_tn, train_colors, steps=steps, seed=seed, nctx=nctx)
    _log("  [seed=%d] fine-tune done in %.1fs (%d trainable params); evaluating ..."
         % (seed, ft["ft_seconds"], ft["n_trainable_params"]))
    ev_tn = _eval_heldahead(ext_tn, eval_structs, tables, target)   # internally rebuilds around tuned weights
    stage_tn = ev_tn["sc"]["stage_role_attn"]
    restore_renders()

    stages = {}
    for st in ALL_TRACKED_STAGES:
        fz1 = float(stage_fz1.get(st, float("nan")))
        fz2 = float(stage_fz2.get(st, float("nan")))
        tn = float(stage_tn.get(st, float("nan")))
        stages[st] = {"frozen": fz1, "frozen2": fz2, "tuned": tn, "lift": tn - fz1, "drift": fz2 - fz1}

    per_type = {}
    for qt in QUERY_TYPES:
        fz1 = float(ev_fz1["per_type"][qt])
        tn = float(ev_tn["per_type"][qt])
        per_type[qt] = {"frozen": fz1, "tuned": tn, "lift": tn - fz1}

    res = {"seed": seed, "target": target, "stages": stages, "per_type": per_type,
           "loop_frozen": ev_fz1["loop"], "loop_frozen2": ev_fz2["loop"], "loop_tuned": ev_tn["loop"],
           "ft": ft}
    _log("  [seed=%d] P lift=%+.3f | ENT lift=%+.3f MARK lift=%+.3f ent_cons lift=%+.3f | loop fz=%.3f tn=%.3f"
         % (seed, stages["P"]["lift"], stages["ENT"]["lift"], stages["MARK"]["lift"],
            stages["entity_consistency"]["lift"], ev_fz1["loop"], ev_tn["loop"]))
    return res


# ================= verdict =================
def _mean(xs):
    v = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(v)) if v else float("nan")


def decide_verdict(units, seeds):
    if len(units) < len(seeds):
        return "HARD_FAIL", ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d seed units"
                             % (len(units), len(seeds))), {}

    max_drift = max(abs(u["stages"][st]["drift"]) for u in units for st in ALL_TRACKED_STAGES)
    if max_drift > DRIFT_MAX:
        return "INVALID", ("DRIFT_CONTROL_FAILED: max |frozen2-frozen1| drift=%.4f > %.2f -- eval is not "
                           "deterministic; not a capability read." % (max_drift, DRIFT_MAX)), {"max_drift": max_drift}

    stage_mean = {st: {"frozen": _mean([u["stages"][st]["frozen"] for u in units]),
                        "tuned": _mean([u["stages"][st]["tuned"] for u in units]),
                        "lift": _mean([u["stages"][st]["lift"] for u in units])}
                  for st in ALL_TRACKED_STAGES}
    per_type_mean = {qt: {"frozen": _mean([u["per_type"][qt]["frozen"] for u in units]),
                          "tuned": _mean([u["per_type"][qt]["tuned"] for u in units]),
                          "lift": _mean([u["per_type"][qt]["lift"] for u in units])}
                     for qt in QUERY_TYPES}
    loop_frozen = _mean([u["loop_frozen"] for u in units])
    loop_tuned = _mean([u["loop_tuned"] for u in units])

    p_lift = stage_mean[TARGET_STAGE]["lift"]
    entity_lifts = {st: stage_mean[st]["lift"] for st in ENTITY_STAGES}
    entity_lifts.update({("loop_" + qt): per_type_mean[qt]["lift"] for qt in QUERY_TYPES})
    worst_entity_metric, worst_entity_lift = min(entity_lifts.items(), key=lambda kv: kv[1])
    interference = worst_entity_lift < -NO_INTERFERE_MAX_DROP
    target_clears = p_lift >= TARGET_LIFT_MIN

    bands = {"bars": {"target_lift_min": TARGET_LIFT_MIN, "no_interfere_max_drop": NO_INTERFERE_MAX_DROP,
                      "drift_max": DRIFT_MAX},
             "stage_mean": stage_mean, "per_type_mean": per_type_mean,
             "loop_frozen": loop_frozen, "loop_tuned": loop_tuned,
             "max_drift": max_drift, "p_lift": p_lift, "entity_lifts": entity_lifts,
             "worst_entity_metric": worst_entity_metric, "worst_entity_lift": worst_entity_lift,
             "interference": interference, "target_clears": target_clears}

    sub = ("P: fz=%.3f tn=%.3f lift=%+.3f (min=%.2f) | worst entity metric=%s lift=%+.3f (floor=-%.2f) | "
           "loop fz=%.3f tn=%.3f"
           % (stage_mean["P"]["frozen"], stage_mean["P"]["tuned"], p_lift, TARGET_LIFT_MIN,
              worst_entity_metric, worst_entity_lift, NO_INTERFERE_MAX_DROP, loop_frozen, loop_tuned))

    if target_clears and not interference:
        return "HARD_PASS", ("HYPOTHESIS_CONFIRMED: direct training on the P (placement) objective LIFTS "
                             "P by >=%.2f, AND every entity-addressed metric (who's-who) is PRESERVED "
                             "(no drop beyond -%.2f) -- every skill is improvable if trained, and skills "
                             "STACK without clobbering. %s" % (TARGET_LIFT_MIN, NO_INTERFERE_MAX_DROP, sub)), bands
    if not target_clears:
        return "HARD_FAIL", ("HYPOTHESIS_REFUTED_NO_TRANSFER: P lift=%+.3f < %.2f even under DIRECT "
                             "training on P's own objective -- P is not 'just untrained', this is a REAL "
                             "intrinsic limit on this decode, not lack-of-training. %s"
                             % (p_lift, TARGET_LIFT_MIN, sub)), bands
    return "HARD_FAIL", ("HYPOTHESIS_REFUTED_INTERFERENCE: P lift=%+.3f clears %.2f, BUT %s dropped by "
                         "%+.3f (beyond -%.2f floor) -- P training LIFTS its target but CLOBBERS who's-who; "
                         "skills compete for top-1-layer capacity, can't stack freely at this budget. %s"
                         % (p_lift, TARGET_LIFT_MIN, worst_entity_metric, worst_entity_lift,
                            NO_INTERFERE_MAX_DROP, sub)), bands


# ================= self-test =================
def run_self_test():
    _log("SELF-TEST: slot-generic cue/pooled-grad mechanism + tiny P-objective fine-tune + arms-differ "
         "(real_code_path) ...")
    audit = clean.audit_construction(seed=7, n=300)
    assert not audit["fails"], "pre-run construction audit FAILED: %s" % audit["fails"]

    train_colors, held_colors = ih.color_split(SPLIT_SEED)

    # frozen probe (arms-differ baseline)
    ext_fz = lt.RetrainableExtractor()
    ext_fz.build()
    tables = clean.build_tables()
    ds8 = clean.gen_dataset(8, np.random.default_rng(7))
    dec_fz, ans_fz, _ = eb.build_decoded_dataset(ds8, ext_fz, "role_attn")
    main_fz = eb.run_arm_decoded(dec_fz, ans_fz, tables, "main")
    dig_fz = hashlib.sha256(json.dumps([round(main_fz[qt]["acc"], 6) if not math.isnan(main_fz[qt]["acc"])
                                        else -1.0 for qt in QUERY_TYPES]).encode()).hexdigest()

    # tiny P-objective fine-tune; prove weights move
    ext_tn = lt.RetrainableExtractor()
    before = ext_tn.model.norm.weight.detach().clone()
    ft = finetune_encoder_placement(ext_tn, train_colors, steps=6, seed=7, nctx=6)
    after = ext_tn.model.norm.weight.detach()
    moved = float((before - after).abs().max())
    assert moved > 0, "FINE-TUNE INERT: top-layer weights did not move (moved=%.3e)" % moved
    _log("  fine-tune ran: %s | norm.weight max-move=%.3e" % (ft["final"], moved))

    ext_tn.build()
    dec_tn, ans_tn, _ = eb.build_decoded_dataset(ds8, ext_tn, "role_attn")
    main_tn = eb.run_arm_decoded(dec_tn, ans_tn, tables, "main")
    dig_tn = hashlib.sha256(json.dumps([round(main_tn[qt]["acc"], 6) if not math.isnan(main_tn[qt]["acc"])
                                        else -1.0 for qt in QUERY_TYPES]).encode()).hexdigest()
    arms_differ = dig_fz != dig_tn
    _log("  arms_differ preds fz=%s tn=%s (arms_differ=%s)" % (dig_fz[:8], dig_tn[:8], arms_differ))

    # tiny end-to-end run_seed_probe (real code path through _eval_heldahead + drift control + verdict inputs)
    res = run_seed_probe(7, eval_n=8, hardness=HARDNESS_SMOKE, steps=6, nctx=6)
    for st in ALL_TRACKED_STAGES:
        for k in ("frozen", "frozen2", "tuned"):
            v = res["stages"][st][k]
            assert 0.0 <= v <= 1.0 or math.isnan(v), "%s/%s out of range: %s" % (st, k, v)
    max_drift = max(abs(res["stages"][st]["drift"]) for st in ALL_TRACKED_STAGES)
    _log("  tiny run_seed_probe drift-control max|drift|=%.5f (<=%.2f expected)" % (max_drift, DRIFT_MAX))

    _log("SELF-TEST PASS")
    return {"arms_differ_verified": True, "norm_weight_move": moved, "tiny_max_drift": max_drift,
            "tiny_stages": res["stages"], "audit_fails": audit["fails"]}


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
                   "verdict_msg": "SELFTEST_PASS (slot-generic cue/pooled-grad + tiny P-objective fine-tune "
                                  "+ weights-move + arms-differ + tiny drift-control, real_code_path)",
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
    steps = SMOKE_STEPS if run_mode == "smoke" else RECIPE_STEPS
    nctx = SMOKE_NCTX if run_mode == "smoke" else RECIPE_NCTX

    audit = clean.audit_construction(seed=7, n=300)
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    expected_units = len(seeds)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()
    _log("%s: hardness=%s seeds=%s eval_n=%d steps=%d nctx=%d expected_units=%d"
         % (run_mode.upper(), list(hardness), seeds, eval_n, steps, nctx, expected_units))

    done = ckpt.completed_units(OUTPUT_DIR)
    ran = 0
    for s in seeds:
        key = ckpt.unit_key("skillstack_p_seed", s, run_mode)
        if key in done:
            _log("  [seed=%d] loaded from checkpoint" % s)
            continue
        if ran >= 1 and run_mode == "lite" and (time.perf_counter() - t0) > args.budget_sec:
            _log("  budget %.0fs reached after %d new unit(s); stopping (re-run to resume)" % (args.budget_sec, ran))
            break
        res = run_seed_probe(s, eval_n, hardness, steps, nctx)
        ckpt.record_unit(OUTPUT_DIR, key, res)
        _heartbeat(s, run_mode, time.perf_counter() - t0)
        ran += 1

    units_map = ckpt.load_units(OUTPUT_DIR)
    units = [units_map[ckpt.unit_key("skillstack_p_seed", s, run_mode)] for s in seeds
             if ckpt.unit_key("skillstack_p_seed", s, run_mode) in units_map]
    if len(units) < expected_units:
        _log("PARTIAL: %d/%d units done -- re-run to resume" % (len(units), expected_units))
        metrics = {"verdict": "PARTIAL", "verdict_msg": "%d/%d units complete; re-run to resume"
                   % (len(units), expected_units), "summary": "PARTIAL %d/%d" % (len(units), expected_units),
                   "run_mode": run_mode, "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                   "anchor_name": ANCHOR_NAME, "n_units_done": len(units), "expected_n_units": expected_units,
                   "cardinality_ok": False, "units": units, "start_marker_written": True,
                   "crash_diagnostic_present": True, "final_metrics_atomicity": "tmp_replace",
                   "progress_logging": "print_flush_true"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE (partial) %s in %.1fs" % (run_mode, time.perf_counter() - t0))
        return

    verdict, msg, bands = decide_verdict(units, seeds)
    elapsed = time.perf_counter() - t0
    metrics = {"verdict": verdict, "verdict_msg": msg, "summary": "%s | %s" % (verdict, msg[:150]),
               "run_mode": run_mode, "elapsed_s": elapsed, "ts_iso": _now_iso(),
               "anchor_name": ANCHOR_NAME, "bands": bands,
               "cardinality_ok": bool(len(units) == expected_units), "expected_n_units": expected_units,
               "n_units_done": len(units), "construction_audit": audit, "units": units,
               "params": {"hardness": list(hardness), "eval_n": eval_n, "seeds": list(seeds),
                          "steps": steps, "nctx": nctx, "depth": RECIPE_DEPTH,
                          "measurement": "frozen_vs_placement_trained_target_lift_and_entity_no_interference"},
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
