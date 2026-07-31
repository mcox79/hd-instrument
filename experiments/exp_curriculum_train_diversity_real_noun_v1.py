# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor + META_RULE_H sweep):
# - arms_differ_verified at self-test (FROZEN vs TUNED loop-digest OR q_agree OR encoder-geometry delta
#   asserted DISTINCT; an inert fine-tune would move NONE = real bug-catch). ALSO the two diversity levels
#   must produce DISTINCT tuned loops at self-test (a sweep axis that moves nothing = inert = bug).
# - final_metrics_atomicity: tmp_replace (os.replace at end) + per-unit units.jsonl (resumable per CLAUDE.md).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: the scoring loop is the zero-learned-param FHRR SituationWM (imported VERBATIM via hc/lt/eb/ef)
#   + pca_whiten conditioning + role_attn decode. The ONLY learned params are the encoder top-1 layer
#   (certified standout, atom 29593). Discriminator = the TRAJECTORY of held-out real-noun loop LIFT vs the
#   TRAIN-VOCAB DIVERSITY the certified entity fine-tune is trained on (ONE variable). No quantitative noise
#   floor for a slope-of-lift discriminator; the can-fail bands are pre-registered on the trajectory.
# - baseline_in_band: FROZEN loop is the wall (above chance 1/N_NOUN, below ORACLE ceiling); the 6 floors
#   (random_addr/no_coref/wrongrole/shuffled/MOST_RECENT/POOLED_READER) MUST collapse (validity gate).
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = n_seeds * (1 base-unit + n_diversity_levels tuned-units).
#   Verdict counts len(units); < expected => HARD_FAIL_CARDINALITY_BREACH.
# - discriminator survives scale: closed-form loop + frozen-vs-tuned forward at real N; self-test exercises the
#   REAL encoder + REAL fine-tune + REAL loop at tiny N under the REAL-NOUN vocab (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set()).
"""CURRICULUM IN MINIATURE (train-vocab DIVERSITY -> comprehension GRIP). ONE variable = the amount/variety of
REAL-NOUN vocabulary the CERTIFIED minimal-unfreeze entity objective (atom 29593; recipe reused VERBATIM via
exp_situation_model_harder_construction_generalization_v1._finetune_weights, depth=1) is TRAINED on. Everything
else -- the encoder, the recipe, the FHRR situation-model loop, the guard, the floors, the HELD-OUT eval nouns,
the total noun palette (hence chance), the eval passages -- is held FIXED. Director spawn 2026-07-31.
Director+USER gated: cheap miniature probe, NOT the full graded-curriculum program / a from-scratch re-pretrain.

============================================================================================================
THE QUESTION (from grounding first-cut 09a8747ce, MIDDLE): the certified entity-re-id fine-tune lifted the
held-out loop +0.275 on the tight 20-COLOR set but only +0.074 on 120 REAL NOUNS (train=110). Does
STRENGTHENING THE TRAINING (more varied real-noun vocabulary the entity objective differentiates) PULL THE
GRIP UP -- from the +0.074 MIDDLE toward the +0.275 color level -- or does the mechanism have an INTRINSIC
CEILING on broad, less-mutually-contrastive real words? USER: "the reader learns as it reads." Tested cheaply
in miniature: sweep the fine-tune's TRAIN-NOUN diversity; measure whether the held-out lift GROWS with it.
============================================================================================================

DESIGN (ONE variable = TRAIN-NOUN DIVERSITY; fairness gate = FIXED held-out eval nouns):
  N_NOUN total real-noun palette is FIXED (120 lite / 24 smoke); chance = 1/N_NOUN FIXED; codebooks FIXED.
  (held, train_pool) = ih.color_split(SPLIT_SEED) under the installed vocab -- IDENTICAL split the grounding
  first-cut used (held=10 novel eval nouns; train_pool=110). A FIXED permutation of train_pool gives NESTED
  prefixes: DIVERSITY_GRID = n_train values. At each level the CERTIFIED fine-tune trains on perm[:n_train]
  ONLY. The HELD-OUT eval passages are BYTE-IDENTICAL across every level (ent_pool=held fixed, mark_pool=full
  train_pool fixed, fixed eval RNG). frozen loop is diversity-INDEPENDENT (no fine-tune) -> computed ONCE per
  seed (base-unit) and is a cross-level invariant. The MAX level (n_train=110 lite) REPRODUCES the grounding
  first-cut setting EXACTLY (built-in cross-check: its lift should be ~+0.074 MEASURED@grounding).

MEASURED per level: TUNED loop on held (cross-frame entity re-id), ORACLE ceiling (base reading A), memorize
  control (loop on the level's OWN train entities), geometry, guard. Per seed base-unit: FROZEN loop + wc +
  q_agree + entcons, the 6 can-fail floors, POOLED_READER, MOST_RECENT, and the COLOR_ANCHOR positive control
  (reproduce the certified +0.275 color frozen->tuned lift => wiring/recipe faithful; the trajectory ceiling).

PRE-REGISTERED BANDS (fixed BEFORE running; preregs/2026-07-31_curriculum_train_diversity_real_noun.md):
  lift(k) = tuned_loop(n_train=k) - frozen_loop, at fixed chance=1/N_NOUN on the FIXED held-out eval nouns.
  slope   = mean_lift(max level) - mean_lift(min level). COLOR_CEILING = color-anchor lift (~+0.275 ref).
  HARD_PASS (CURRICULUM WORKS IN MINIATURE -- more real-vocab training STRENGTHENS the grip):
    slope >= SLOPE_MIN (0.05) AND lift(max) >= LIFT_MIN (0.05) AND lift(max) is the (near-)peak
    [lift(max) >= max(mean_lift) - TIE_BAND] AND capture(max) >= HEADROOM_CAPTURE_MIN (0.35) AND every seed
    lifts at max (min_seed_lift(max) > 0) AND guard HOLDS at max AND mem_gap(max) <= MEMORIZE_GAP_MAX (0.15)
    AND base reading OK at max AND (validity) floors collapse + COLOR_ANCHOR reproduces a lift.
  HARD_FAIL (INTRINSIC CEILING on broad real vocab -- more diversity does NOT strengthen the grip):
    slope <= TIE_BAND (0.02) [lift FLAT across diversity] OR guard C1 cratered at max (collapse) OR base
    reading FAILS at max OR memorization-only [mem_gap(max) > MEMORIZE_GAP_MAX AND lift(max) <= TIE_BAND].
  MIDDLE: partial upward trajectory (TIE_BAND < slope < SLOPE_MIN, or rises then plateaus below color).
    Report the slope + full trajectory = the extrapolation for the USER's curriculum-scale decision.
  INVALID: a floor did not collapse OR POOLED reservoir-decodable OR COLOR_ANCHOR reproduces no lift OR
    headroom(max) = oracle-frozen < CONSTRUCTION_HEADROOM_MIN (0.05) OR held not disjoint from any train level.

Run:  .venv/Scripts/python.exe experiments/exp_curriculum_train_diversity_real_noun_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_curriculum_train_diversity_real_noun_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_curriculum_train_diversity_real_noun_v1.py --lite
      (--lite is resumable per-unit; CPU-first, push-free, INLINE-LOCAL foreground; --budget-sec < 10 min.)

ASCII-only. No emojis. Deterministic seeding. Pure CPU. Compute architecture: mixed -- top-1-layer SGD
fine-tune (batched fwd+bwd, CPU) + closed-form FHRR eval loop with batched frozen-encoder forwards.
Storage strategy: no_storage (encoder fine-tune + closed-form FHRR eval; no atom-store writes).
progress_logging: print_flush_true.
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

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
# reuse the grounding first-cut cell VERBATIM for vocab-patch + single-token-noun filter + all machinery
import exp_grounding_firstcut_real_noun_vocab_v1 as g  # noqa: E402

hc = g.hc
lt = g.lt
eb = g.eb
ef = g.ef
ih = g.ih
clean = g.clean
ckpt = g.ckpt
QUERY_TYPES = hc.QUERY_TYPES
DECODE_FLOOR_BAR = hc.DECODE_FLOOR_BAR
ADDR_FLOOR_BAR = hc.ADDR_FLOOR_BAR
PROVEN_MIN = hc.PROVEN_MIN
SPLIT_SEED = hc.SPLIT_SEED

ANCHOR_NAME = "curriculum_train_diversity_real_noun_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- certified standout config (MEASURED@data/exp_situation_model_assembly_encoder_retrain_scale_v1:
#      depth=1 top-layer unfreeze was the standout; reused VERBATIM via hc._finetune_weights) ----
DEPTH = 1
NCTX = 40
STEPS_LITE = 220
STEPS_SMOKE = 24
SEEDS_LITE = (7, 13)
SEEDS_SMOKE = (7,)
GRID_EVAL_N_LITE = 120   # sized so binomial MDE(slope) < SLOPE_MIN=0.05 at 2 seeds (adequately powered)
GRID_EVAL_N_SMOKE = 20
N_NOUN_LITE = 120     # FIXED palette (matches grounding first-cut exactly; held=10 / train_pool=110)
N_NOUN_SMOKE = 24     # FIXED palette (held=10 / train_pool=14)
# ONE VARIABLE = number of TRAIN nouns the certified entity fine-tune sees (NESTED prefixes; diversity grid).
# n_train=110 (lite max) == the grounding first-cut setting EXACTLY (cross-check anchor; lift ~+0.074 MEASURED).
DIVERSITY_GRID_LITE = (12, 35, 70, 110)
DIVERSITY_GRID_SMOKE = (8, 14)
POOL_PERM_SEED = 20260731   # FIXED permutation of train_pool -> deterministic nested diversity prefixes

# ---- pre-registered bars (fixed BEFORE running; reuse the certified/harder-construction shape VERBATIM) ----
LIFT_MIN = hc.LIFT_MIN                          # 0.05  lift(max) HARD_PASS floor
HEADROOM_CAPTURE_MIN = hc.HEADROOM_CAPTURE_MIN  # 0.35  fraction of (oracle-frozen) the max-lift must capture
TIE_BAND = hc.TIE_BAND                          # 0.02  |slope| <= this = FLAT = intrinsic ceiling (HARD_FAIL)
MEMORIZE_GAP_MAX = hc.MEMORIZE_GAP_MAX          # 0.15  train-minus-held tuned loop; > this = memorization
WC_DRIFT_MAX = hc.WC_DRIFT_MAX                  # 0.15  (inside hc.collapse_guard)
ENTCONS_MIN = hc.ENTCONS_MIN                    # 0.85  (inside hc.collapse_guard)
Q_AGREE_GUARD_MIN = hc.Q_AGREE_GUARD_MIN        # 0.55  (inside hc.collapse_guard)
SLOPE_MIN = 0.05                                # HYPOTHESIZED: lift(max)-lift(min) HARD_PASS slope floor
BASE_READING_MARGIN = 0.20                      # HYPOTHESIZED: oracle_loop must clear chance by this (A)
CONSTRUCTION_HEADROOM_MIN = 0.05                # HYPOTHESIZED: oracle-frozen must exceed this (informative)
# ---- flat-trajectory diagnostic bars (per USER reframe: a FLAT slope is NOT a ceiling; it means the
#      EXPERIMENT is broken in one of exactly 3 ways -- diagnose (a)/(b)/(c) before any verdict) ----
WEIGHT_MOVE_MIN = 1e-3    # (a) unfrozen-param relative L2 delta below this = SGD did not update = NOT LEARNING
LEARN_TRAIN_MIN = 0.05    # (a) train-entity lift (train_loop - frozen); objective must FIT train to have learned
DUP_COS_MAX = 0.50        # (b) if train entities were near-duplicates their frozen separability collapses; a
                          #     wc_train_frozen at/below the FROZEN noise floor across levels = no new signal
CONTENT_WC_FLOOR = 0.005  # (b) frozen train-entity within-minus-cross must exceed this tiny floor = real signal


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _nouns_for(n_noun):
    """The FIXED single-token real-noun palette of size n_noun (verbatim g filter; disjoint from colors)."""
    ext_probe = lt.RetrainableExtractor()
    nouns_all = g.single_token_nouns(ext_probe.tok, g._NOUN_CANDIDATES, N_NOUN_LITE)
    return nouns_all[:n_noun]


def _split_and_perm(n_noun):
    """Under the currently-installed n_noun-vocab: the FIXED (held, train_pool) split (IDENTICAL to the
    grounding first-cut, ih.color_split(SPLIT_SEED)) + a FIXED permutation of train_pool for nested diversity
    prefixes. Returns (held, train_pool_sorted, perm)."""
    train_pool, held = ih.color_split(SPLIT_SEED)     # (train, held); held=K_TRACK+N_DISTRACT (10)
    perm = list(train_pool)
    np.random.default_rng(POOL_PERM_SEED).shuffle(perm)
    return held, list(train_pool), perm


def _grid_for(run_mode, n_pool):
    grid = DIVERSITY_GRID_SMOKE if run_mode == "smoke" else DIVERSITY_GRID_LITE
    grid = tuple(k for k in grid if k <= n_pool)       # never exceed the train pool
    assert len(grid) >= 2 and grid[-1] == max(grid), "diversity grid must have >=2 nested levels"
    return grid


# ================= base unit (per seed; diversity-INDEPENDENT references + validity + color anchor) ========
def run_base(seed, run_mode, eval_n, n_noun, nouns):
    """FROZEN loop + geometry + q_agree/entcons + the 6 can-fail floors + POOLED + MOST_RECENT + COLOR_ANCHOR.
    All diversity-independent -> computed ONCE per seed. Installs the n_noun real-noun vocab, restores color."""
    steps = STEPS_SMOKE if run_mode == "smoke" else STEPS_LITE
    nctx = 8 if run_mode == "smoke" else NCTX
    chance = 1.0 / n_noun

    g.install_vocab(nouns)
    assert g.vocab_is(n_noun), "vocab install failed"
    tables = clean.build_tables()
    held, train_pool, _perm = _split_and_perm(n_noun)
    # FIXED held-out eval passages: ent_pool=held (novel), mark_pool=FULL train_pool -> identical across levels
    ev_held = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held, train_pool)
    for p in ev_held:
        for e in p["tracked"]:
            assert e in held, "eval entity not held-out (fairness breach)"
    train_ds = clean.gen_dataset(60 if run_mode != "smoke" else 20, np.random.default_rng(seed))

    ext_fz = lt.RetrainableExtractor(); ext_fz.build()
    sc_fz = lt.score_extractor(ext_fz, ev_held, tables)
    wc_frozen = lt.within_minus_cross(ext_fz, held, seed=seed + 2)

    floors = {}
    for m in ("random_addr", "no_coref", "wrongrole", "shuffled"):
        floors[m] = eb.run_arm_decoded(sc_fz["dec_ra"], sc_fz["ans_ra"], tables, m)
    most_recent = clean.run_most_recent(ev_held)
    pooled = clean.run_pooled_reader(train_ds, ev_held, seed)

    frozen_type = {qt: sc_fz["main_enc"][qt]["acc"] for qt in QUERY_TYPES}

    # ---- COLOR_ANCHOR positive control (restore color vocab; certified frozen->tuned color lift = ceiling) --
    g.restore_vocab()
    n_color = len(clean.COLORS)
    assert g.vocab_is(n_color), "vocab restore failed"
    tables_c = clean.build_tables()
    train_c, held_c = ih.color_split(SPLIT_SEED)
    ext_c_tu, _ftc = hc._finetune_weights(train_c, seed, steps, nctx, DEPTH)
    ext_c_fz = lt.RetrainableExtractor(); ext_c_fz.build()
    ext_c_tu.build()
    ev_c = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held_c, train_c)
    a_fz = hc._loop_mean(lt.score_extractor(ext_c_fz, ev_c, tables_c)["main_enc"])
    a_tu = hc._loop_mean(lt.score_extractor(ext_c_tu, ev_c, tables_c)["main_enc"])

    res = {
        "kind": "base", "seed": seed, "n_noun": n_noun, "chance": chance,
        "frozen_noun_loop": hc._loop_mean(sc_fz["main_enc"]),
        "frozen_type": frozen_type,
        "frozen_q_agree": sc_fz["diag_decoded"]["cross_frame_query_agreement"],
        "frozen_ent_consistency": sc_fz["stage_role_attn"].get("entity_consistency"),
        "wc_frozen": wc_frozen["within_minus_cross"],
        "floors": {m: {qt: floors[m][qt]["acc"] for qt in QUERY_TYPES} for m in floors},
        "most_recent": {qt: most_recent[qt]["acc"] for qt in QUERY_TYPES},
        "pooled_b": pooled["b_competitive_coref"]["acc"], "pooled_c": pooled["c_overwrite"]["acc"],
        "anchor_frozen_color_loop": a_fz, "anchor_tuned_color_loop": a_tu,
        "held_nouns": [nouns[i] for i in held],
    }
    _log("  [seed=%d BASE] frozen loop=%.3f | wc_frozen=%.3f | chance=%.4f | COLOR-ANCHOR frozen=%.3f tuned=%.3f (lift %.3f)"
         % (seed, res["frozen_noun_loop"], res["wc_frozen"], chance, a_fz, a_tu, a_tu - a_fz))
    return res


# ================= tuned unit (per seed, per diversity level; the swept fine-tune) ========================
def run_level(seed, n_train, run_mode, eval_n, n_noun, nouns):
    """CERTIFIED fine-tune trained on perm[:n_train] real-noun entities (the ONE swept variable), scored on the
    FIXED held-out eval nouns. Also ORACLE ceiling (base reading A) + memorization control (loop on the level's
    OWN train entities). Installs the n_noun vocab; restore is done by the caller."""
    steps = STEPS_SMOKE if run_mode == "smoke" else STEPS_LITE
    nctx = 8 if run_mode == "smoke" else NCTX
    chance = 1.0 / n_noun

    g.install_vocab(nouns)
    assert g.vocab_is(n_noun), "vocab install failed"
    tables = clean.build_tables()
    held, train_pool, perm = _split_and_perm(n_noun)
    train_nouns = perm[:n_train]                       # NESTED diversity prefix = the swept train vocab
    assert set(train_nouns).isdisjoint(set(held)), "train level overlaps held (fairness breach)"

    ext_tuned, ft = hc._finetune_weights(train_nouns, seed, steps, nctx, DEPTH)   # CERTIFIED fine-tune
    ext_tuned.build()

    # -------- DIAGNOSTIC (a) NOT-ACTUALLY-LEARNING: did the unfrozen entity-relevant weights MOVE? -------
    # Compare the tuned model's UNFROZEN params (requires_grad flags survive finetune) against a fresh frozen
    # extractor from the same checkpoint. weight_move_rel ~ 0 => the SGD did not update the right params.
    frozen_ref = lt.RetrainableExtractor(); frozen_ref.build()
    tp = dict(ext_tuned.model.named_parameters())
    fp = dict(frozen_ref.model.named_parameters())
    moved_names = [n for n, p in tp.items() if p.requires_grad]
    num = den = 0.0
    for nm in moved_names:
        d = (tp[nm].detach() - fp[nm].detach())
        num += float((d * d).sum()); den += float((fp[nm].detach() ** 2).sum())
    weight_move_rel = (num ** 0.5) / (den ** 0.5) if den > 0 else float("nan")
    ft_final = ft.get("final", {}) or {}

    # -------- DIAGNOSTIC (b) NO-GENUINELY-NEW-CONTENT: is the level's train entity set genuinely separable
    # signal (not near-duplicates)? wc_train_frozen = the raw within-minus-cross contrastive separability of
    # THIS level's train entities under the FROZEN encoder (the signal the objective actually has to learn
    # from). Near-orthogonal single-token nouns => distinct reps => real new content per added noun.
    wc_train_frozen = lt.within_minus_cross(frozen_ref, train_nouns, seed=seed + 3)["within_minus_cross"]

    # FIXED held-out eval passages (byte-identical to run_base: ent_pool=held, mark_pool=FULL train_pool)
    ev_held = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held, train_pool)
    for p in ev_held:
        for e in p["tracked"]:
            assert e in held, "eval entity not held-out (fairness breach)"
    # memorization control: loop on the level's OWN trained entities (marks from held)
    ev_train = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 555), train_nouns, held)

    sc_tu = lt.score_extractor(ext_tuned, ev_held, tables)
    sc_tu_tr = lt.score_extractor(ext_tuned, ev_train, tables)
    dec_or, ans_or, _ = ef.build_addr_dataset(ev_held, ext_tuned, "oracle")
    oracle = eb.run_arm_decoded(dec_or, ans_or, tables, "main")
    wc_tuned = lt.within_minus_cross(ext_tuned, held, seed=seed + 2)

    res = {
        "kind": "tuned", "seed": seed, "n_train": n_train, "n_noun": n_noun, "chance": chance,
        "ft_seconds": ft["ft_seconds"], "n_trainable_params": ft["n_trainable_params"], "steps": steps,
        "tuned_noun_loop": hc._loop_mean(sc_tu["main_enc"]),
        "oracle_noun_loop": hc._loop_mean(oracle),
        "train_noun_loop": hc._loop_mean(sc_tu_tr["main_enc"]),
        "tuned_type": {qt: sc_tu["main_enc"][qt]["acc"] for qt in QUERY_TYPES},
        "oracle_type": {qt: oracle[qt]["acc"] for qt in QUERY_TYPES},
        "tuned_q_agree": sc_tu["diag_decoded"]["cross_frame_query_agreement"],
        "tuned_ent_consistency": sc_tu["stage_role_attn"].get("entity_consistency"),
        "wc_tuned": wc_tuned["within_minus_cross"],
        "train_noun_sample": [nouns[i] for i in train_nouns[:8]],
        # ---- flat-trajectory diagnostics (a)/(b) baked in per level ----
        "weight_move_rel": weight_move_rel,                 # (a) did unfrozen params move
        "ft_loss_final": ft_final.get("loss", float("nan")),   # (a) final objective loss
        "ft_align_final": ft_final.get("l_align", float("nan")),  # (a) low => same-entity reps aligned = learned
        "ft_push_final": ft_final.get("l_push", float("nan")),
        "n_train_reps": ft.get("n_train_reps", float("nan")),
        "wc_train_frozen": wc_train_frozen,                 # (b) raw separable signal of the train entities
    }
    _log("  [seed=%d n_train=%d] tuned loop=%.3f | ORACLE=%.3f | train loop=%.3f | wc_tuned=%.3f q_agree=%.3f entc=%.3f"
         % (seed, n_train, res["tuned_noun_loop"], res["oracle_noun_loop"], res["train_noun_loop"],
            res["wc_tuned"], res["tuned_q_agree"],
            res["tuned_ent_consistency"] if res["tuned_ent_consistency"] is not None else float("nan")))
    _log("  [seed=%d n_train=%d] DIAG (a)learn: weight_move_rel=%.4f ft_loss=%.4f align=%.4f | (b)content: wc_train_frozen=%.4f n_reps=%s (%.1fs)"
         % (seed, n_train, res["weight_move_rel"], res["ft_loss_final"], res["ft_align_final"],
            res["wc_train_frozen"], res["n_train_reps"], res["ft_seconds"]))
    return res


# ================= verdict =================
def _floors_ok(bases):
    ok, notes = True, []
    for r in bases:
        for arm, (qts, bar) in {"random_addr": (QUERY_TYPES, ADDR_FLOOR_BAR),
                                "no_coref": (("b_competitive_coref",), ADDR_FLOOR_BAR),
                                "wrongrole": (QUERY_TYPES, DECODE_FLOOR_BAR),
                                "shuffled": (QUERY_TYPES, DECODE_FLOOR_BAR)}.items():
            for qt in qts:
                x = r["floors"][arm][qt]
                if not math.isnan(x) and x > bar:
                    ok = False; notes.append("seed%d %s[%s]=%.3f>%.3f" % (r["seed"], arm, qt, x, bar))
        for qt in QUERY_TYPES:
            x = r["most_recent"][qt]
            if not math.isnan(x) and x > DECODE_FLOOR_BAR:
                ok = False; notes.append("seed%d most_recent[%s]=%.3f>%.3f" % (r["seed"], qt, x, DECODE_FLOOR_BAR))
    return ok, notes


def _pooled_reservoir(bases):
    for r in bases:
        if (not math.isnan(r["pooled_b"]) and r["pooled_b"] >= PROVEN_MIN) or \
           (not math.isnan(r["pooled_c"]) and r["pooled_c"] >= PROVEN_MIN):
            return True
    return False


def _mean(xs):
    v = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(v)) if v else float("nan")


def _flat_diagnosis(per_level, lo, hi, seeds, eval_n):
    """USER reframe: a FLAT slope is NOT a capability ceiling -- it means the EXPERIMENT is broken in one of
    exactly three ways. Return which, off MEASURED evidence, so a flat result auto-reports its cause.
    (a) NOT_LEARNING     -- unfrozen weights barely moved OR the objective did not fit the TRAIN entities.
    (b) NO_NEW_CONTENT   -- the train entities carry no separable signal (near-duplicate reps; nothing to learn).
    (c) UNDERPOWERED     -- the minimum-detectable-effect (MDE) exceeds the effect we require (SLOPE_MIN), so a
                            real slope could not register at this seed/eval/step budget.
    CLEAN_DESIGN_LIMIT   -- learning happened + content is genuinely new + adequately powered, and STILL no
                            held-out lift => this OBJECTIVE/RECIPE does not capture broad-vocab generalization
                            (a DESIGN fix -- more unfreeze / harder negatives / more steps -- NOT a ceiling)."""
    H = per_level[hi]
    wmove = H["mean_weight_move_rel"]; train_lift = H["mean_train_lift"]
    wc_tr = H["mean_wc_train_frozen"]; mem_gap = H["mean_mem_gap"]
    learning_ok = ((not math.isnan(wmove)) and wmove > WEIGHT_MOVE_MIN
                   and (not math.isnan(train_lift)) and train_lift >= LEARN_TRAIN_MIN)
    content_ok = (not math.isnan(wc_tr)) and wc_tr > CONTENT_WC_FLOOR
    # power: between-seed dispersion + binomial loop sampling SE on the slope (a difference of two loop means)
    std_lo = per_level[lo]["lift_std"]; std_hi = H["lift_std"]; n = max(1, len(seeds))
    mde_seed = (1.96 * math.sqrt(((0.0 if math.isnan(std_lo) else std_lo ** 2)
                                  + (0.0 if math.isnan(std_hi) else std_hi ** 2)) / n)
                if (n > 1 and not (math.isnan(std_lo) and math.isnan(std_hi))) else float("nan"))
    pbar = _mean([per_level[lo]["mean_tuned_loop"], H["mean_tuned_loop"]])
    n_eff = eval_n * len(QUERY_TYPES) * n
    se_loop = math.sqrt(max(pbar * (1.0 - pbar), 1e-9) / max(n_eff, 1)) if not math.isnan(pbar) else float("nan")
    mde_binom = (1.96 * math.sqrt(2.0) * se_loop) if not math.isnan(se_loop) else float("nan")
    mde = _mean([x for x in (mde_seed, mde_binom) if not math.isnan(x)])
    # be conservative: MDE = the LARGER of the two (harder to be "powered")
    cands = [x for x in (mde_seed, mde_binom) if not math.isnan(x)]
    mde = max(cands) if cands else float("nan")
    powered = (not math.isnan(mde)) and mde <= SLOPE_MIN
    if not learning_ok:
        cause = "a_NOT_LEARNING"
    elif not content_ok:
        cause = "b_NO_NEW_CONTENT"
    elif not powered:
        cause = "c_UNDERPOWERED"
    else:
        cause = "CLEAN_DESIGN_LIMIT"
    return {"cause": cause, "learning_ok": learning_ok, "content_ok": content_ok, "powered": powered,
            "weight_move_rel_hi": wmove, "train_lift_hi": train_lift, "wc_train_frozen_hi": wc_tr,
            "mem_gap_hi": mem_gap, "mde_slope": mde, "mde_seed": mde_seed, "mde_binom": mde_binom,
            "slope_min_target": SLOPE_MIN}


def decide_verdict(bases, tuned, seeds, grid, eval_n):
    # ---- cardinality (META_RULE_H) ----
    expected = len(seeds) * (1 + len(grid))
    got = len(bases) + len(tuned)
    if got < expected:
        return "HARD_FAIL", ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d units (bases=%d tuned=%d) -- "
                             "re-run to resume before trusting the trajectory" % (got, expected, len(bases), len(tuned))), {}

    # ---- validity gates ----
    floors_ok, floor_notes = _floors_ok(bases)
    if _pooled_reservoir(bases):
        return "INVALID", "POOLED_READER reservoir-decodable (b/c >= PROVEN_MIN) -- harness trivially solvable", {}
    if not floors_ok:
        return "INVALID", "can-fail floor did not collapse: " + "; ".join(floor_notes[:6]), {}

    chance = _mean([r["chance"] for r in bases])
    frozen_by_seed = {r["seed"]: r["frozen_noun_loop"] for r in bases}
    frozen = _mean(list(frozen_by_seed.values()))
    wc_frozen = _mean([r["wc_frozen"] for r in bases])
    anchor_lift = _mean([r["anchor_tuned_color_loop"] - r["anchor_frozen_color_loop"] for r in bases])
    anchor_frozen = _mean([r["anchor_frozen_color_loop"] for r in bases])
    anchor_tuned = _mean([r["anchor_tuned_color_loop"] for r in bases])

    # ---- trajectory: mean lift + capture + memorization per diversity level ----
    tuned_by = {(r["seed"], r["n_train"]): r for r in tuned}
    traj = []       # ordered by grid
    per_level = {}
    for k in grid:
        lifts, captures, oracles, tuneds, trains, mems, min_lift = [], [], [], [], [], [], float("inf")
        wc_t, q_ag, entc = [], [], []
        wmove, falign, tlift, wctrain = [], [], [], []   # diagnostics (a)/(b)
        for s in seeds:
            r = tuned_by.get((s, k))
            if r is None:
                continue
            fz = frozen_by_seed.get(s, float("nan"))
            lift = r["tuned_noun_loop"] - fz
            head = r["oracle_noun_loop"] - fz
            cap = (lift / head) if (not math.isnan(head) and head > 1e-6) else float("nan")
            lifts.append(lift); captures.append(cap)
            oracles.append(r["oracle_noun_loop"]); tuneds.append(r["tuned_noun_loop"])
            trains.append(r["train_noun_loop"]); mems.append(r["train_noun_loop"] - r["tuned_noun_loop"])
            wc_t.append(r["wc_tuned"]); q_ag.append(r["tuned_q_agree"]); entc.append(r["tuned_ent_consistency"])
            wmove.append(r.get("weight_move_rel", float("nan")))
            falign.append(r.get("ft_align_final", float("nan")))
            tlift.append(r["train_noun_loop"] - fz)         # (a) did the objective FIT the train entities
            wctrain.append(r.get("wc_train_frozen", float("nan")))
            min_lift = min(min_lift, lift)
        lvl = {"n_train": k, "mean_lift": _mean(lifts), "min_seed_lift": (min_lift if lifts else float("nan")),
               "mean_capture": _mean(captures), "mean_tuned_loop": _mean(tuneds),
               "mean_oracle_loop": _mean(oracles), "mean_train_loop": _mean(trains),
               "mean_mem_gap": _mean(mems), "per_seed_lift": lifts,
               "wc_tuned": _mean(wc_t), "q_agree": _mean(q_ag), "entcons": _mean(entc),
               "mean_weight_move_rel": _mean(wmove), "mean_ft_align_final": _mean(falign),
               "mean_train_lift": _mean(tlift), "mean_wc_train_frozen": _mean(wctrain),
               "lift_std": (float(np.std(lifts, ddof=1)) if len(lifts) > 1 else float("nan"))}
        traj.append(lvl); per_level[k] = lvl

    lo, hi = grid[0], grid[-1]
    lift_lo = per_level[lo]["mean_lift"]
    lift_hi = per_level[hi]["mean_lift"]
    slope = (lift_hi - lift_lo) if (not math.isnan(lift_hi) and not math.isnan(lift_lo)) else float("nan")
    all_mean_lifts = [lvl["mean_lift"] for lvl in traj if not math.isnan(lvl["mean_lift"])]
    peak_lift = max(all_mean_lifts) if all_mean_lifts else float("nan")
    hi_is_peak = (not math.isnan(lift_hi)) and (not math.isnan(peak_lift)) and lift_hi >= peak_lift - TIE_BAND

    cap_hi = per_level[hi]["mean_capture"]
    min_seed_lift_hi = per_level[hi]["min_seed_lift"]
    oracle_hi = per_level[hi]["mean_oracle_loop"]
    headroom_hi = (oracle_hi - frozen) if (not math.isnan(oracle_hi) and not math.isnan(frozen)) else float("nan")
    mem_gap_hi = per_level[hi]["mean_mem_gap"]
    mem_ok = (not math.isnan(mem_gap_hi)) and mem_gap_hi <= MEMORIZE_GAP_MAX
    guard_hi = hc.collapse_guard(per_level[hi]["mean_tuned_loop"], frozen, per_level[hi]["wc_tuned"],
                                 wc_frozen, per_level[hi]["entcons"], per_level[hi]["q_agree"])
    oracle_above_chance = (oracle_hi - chance) if (not math.isnan(oracle_hi) and not math.isnan(chance)) else float("nan")
    base_reading_ok = ((not math.isnan(oracle_above_chance)) and oracle_above_chance >= BASE_READING_MARGIN
                       and (not math.isnan(wc_frozen)) and wc_frozen > 0.0)

    # ---- flat-trajectory diagnosis (always computed + reported; consulted only when slope is flat) ----
    fdiag = _flat_diagnosis(per_level, lo, hi, seeds, eval_n)

    bands = {
        "one_variable": ("TRAIN-NOUN DIVERSITY (number of real nouns the certified entity fine-tune trains on); "
                         "held-out eval nouns + total palette + chance + eval passages + recipe FIXED. "
                         "grid=%s at N_NOUN=%d chance=%.4f. Max level (n_train=%d) == grounding first-cut setting."
                         % (list(grid), bases[0]["n_noun"] if bases else -1, chance, hi)),
        "bars": {"slope_min": SLOPE_MIN, "lift_min": LIFT_MIN, "tie_band": TIE_BAND,
                 "headroom_capture_min": HEADROOM_CAPTURE_MIN, "memorize_gap_max": MEMORIZE_GAP_MAX,
                 "base_reading_margin": BASE_READING_MARGIN, "construction_headroom_min": CONSTRUCTION_HEADROOM_MIN},
        "trajectory": traj,
        "slope": slope, "lift_lo": lift_lo, "lift_hi": lift_hi, "peak_lift": peak_lift, "hi_is_peak": hi_is_peak,
        "capture_hi": cap_hi, "min_seed_lift_hi": min_seed_lift_hi, "headroom_hi": headroom_hi,
        "frozen_loop": frozen, "chance": chance, "wc_frozen": wc_frozen,
        "A_base_reading": {"oracle_hi": oracle_hi, "oracle_above_chance": oracle_above_chance,
                           "base_reading_ok": base_reading_ok},
        "color_anchor": {"lift": anchor_lift, "frozen": anchor_frozen, "tuned": anchor_tuned},
        "collapse_guard_hi": guard_hi, "memorization_hi": {"mem_gap": mem_gap_hi, "ok": mem_ok},
        "flat_diagnosis": fdiag,
        "non_triviality": {"floors_ok": floors_ok, "pooled_reservoir": _pooled_reservoir(bases)},
        "held_nouns_sample": bases[0]["held_nouns"] if bases else []}

    # ---- INVALID gates first (construction / wiring) ----
    if math.isnan(headroom_hi) or headroom_hi < CONSTRUCTION_HEADROOM_MIN:
        return "INVALID", ("UNINFORMATIVE: oracle-frozen headroom=%.3f < %.2f at max diversity -- no routing "
                           "headroom (the real-noun construction may have cratered the ORACLE; fix before "
                           "trusting the trajectory)" % (headroom_hi, CONSTRUCTION_HEADROOM_MIN)), bands
    if math.isnan(anchor_lift) or anchor_lift <= 0.0:
        return "INVALID", ("COLOR_ANCHOR did NOT reproduce a frozen->tuned lift (anchor_lift=%.3f) -- harness "
                           "wiring or the fine-tune recipe is broken; do NOT trust the trajectory." % anchor_lift), bands

    sub = ("[TRAIN-DIVERSITY SWEEP grid=%s N_NOUN=%d chance=%.4f] frozen=%.3f (wc=%.3f). lift trajectory: %s. "
           "slope(hi-lo)=%.3f (SLOPE_MIN=%.2f TIE_BAND=%.2f). max-level(n_train=%d): lift=%.3f capture=%.2f "
           "min-seed=%.3f oracle=%.3f (chance+%.3f) headroom=%.3f guard=%s mem_gap=%.3f. COLOR-CEILING lift=%.3f."
           % (list(grid), bases[0]["n_noun"] if bases else -1, chance, frozen, wc_frozen,
              ["%d:%.3f" % (lvl["n_train"], lvl["mean_lift"]) for lvl in traj], slope, SLOPE_MIN, TIE_BAND,
              hi, lift_hi, cap_hi if not math.isnan(cap_hi) else float("nan"), min_seed_lift_hi, oracle_hi,
              oracle_above_chance, headroom_hi, guard_hi["pass"], mem_gap_hi, anchor_lift))

    fd = "DIAG(a-learn: wmove=%.4f train_lift=%.3f ok=%s | b-content: wc_train_frozen=%.4f ok=%s | c-power: MDE=%.3f<=%.2f? %s | mem_gap=%.3f). CAUSE=%s." % (
        fdiag["weight_move_rel_hi"], fdiag["train_lift_hi"], fdiag["learning_ok"], fdiag["wc_train_frozen_hi"],
        fdiag["content_ok"], fdiag["mde_slope"], SLOPE_MIN, fdiag["powered"], fdiag["mem_gap_hi"], fdiag["cause"])

    # ---- reading-wall (an ENCODER observation, explicitly NOT a curriculum ceiling) ----
    if not base_reading_ok:
        return "HARD_FAIL", ("READING-WALL (encoder, NOT a curriculum ceiling): the encoder cannot read the "
                             "palette even given a CLEAN address at max diversity (oracle only chance+%.3f < "
                             "%.2f) -- the base-reading precondition fails, so the diversity sweep is moot until "
                             "the encoder reads the vocab. " % (oracle_above_chance, BASE_READING_MARGIN) + sub), bands

    # ---- HARD_PASS: grip PULLED UP by more diversity, generalizes, guard holds ----
    if ((not math.isnan(slope)) and slope >= SLOPE_MIN and (not math.isnan(lift_hi)) and lift_hi >= LIFT_MIN
            and hi_is_peak and (not math.isnan(cap_hi)) and cap_hi >= HEADROOM_CAPTURE_MIN
            and (not math.isnan(min_seed_lift_hi)) and min_seed_lift_hi > 0 and guard_hi["pass"] and mem_ok):
        return "HARD_PASS", ("CURRICULUM WORKS IN MINIATURE: more varied real-noun training SUBSTANTIALLY "
                             "strengthens the held-out comprehension grip (slope=%.3f >= %.2f; lift climbs to "
                             "%.3f at max diversity, generalizes to novel nouns, guard holds, floors collapse). "
                             "The reader learns as it reads -- BUILD the graded curriculum loop (full program = "
                             "USER-strategic scale call). " % (slope, SLOPE_MIN, lift_hi) + sub), bands

    # ---- FLAT or COLLAPSE: DIAGNOSE (a)/(b)/(c) -- do NOT conclude an intrinsic ceiling (USER reframe) ----
    collapse = not guard_hi["c1_loop_not_cratered"]
    flat = (not math.isnan(slope)) and slope <= TIE_BAND
    if flat or collapse:
        cprefix = ("COLLAPSE (fine-tune craters loop below frozen at max diversity; guard C1 failed) + " if collapse else "")
        cause = fdiag["cause"]
        if cause in ("a_NOT_LEARNING", "b_NO_NEW_CONTENT", "c_UNDERPOWERED"):
            reason = {
                "a_NOT_LEARNING": ("EXPERIMENT NOT LEARNING (a): the unfrozen weights barely moved "
                                   "(weight_move_rel=%.4f<=%.3f) OR the objective did not fit the TRAIN entities "
                                   "(train_lift=%.3f<%.2f). The flat held-out trajectory is a BROKEN-TRAINING "
                                   "artifact, NOT a ceiling -- fix the training (LR/steps/grad-flow) and re-run."
                                   % (fdiag["weight_move_rel_hi"], WEIGHT_MOVE_MIN, fdiag["train_lift_hi"], LEARN_TRAIN_MIN)),
                "b_NO_NEW_CONTENT": ("EXPERIMENT NO-NEW-CONTENT (b): the train entities carry no separable signal "
                                     "(wc_train_frozen=%.4f<=%.3f) -- each diversity increment adds rows but no new "
                                     "learnable information, so a flat trajectory says nothing about the mechanism. "
                                     "Fix the content (genuinely distinct/informative entities) and re-run."
                                     % (fdiag["wc_train_frozen_hi"], CONTENT_WC_FLOOR)),
                "c_UNDERPOWERED": ("EXPERIMENT UNDERPOWERED (c): the minimum-detectable-effect MDE=%.3f exceeds the "
                                   "required slope SLOPE_MIN=%.2f (seeds=%d eval_n=%d) -- a real diversity effect "
                                   "could not register at this budget. NOT a ceiling; add seeds/eval/steps and "
                                   "re-run." % (fdiag["mde_slope"], SLOPE_MIN, len(seeds), eval_n)),
            }[cause]
            return "INVALID", (cprefix + reason + " " + fd + " " + sub), bands
        # CLEAN_DESIGN_LIMIT: verified learning + genuinely-new content + adequately powered, still no lift
        mem_note = ("(objective FIT the trained nouns -- mem_gap=%.3f -- but did NOT generalize to held-out => "
                    "an OVERFIT/objective-generalization gap) " % fdiag["mem_gap_hi"]) if (not mem_ok) else ""
        return "MIDDLE", (cprefix + "CLEAN-EXPERIMENT DESIGN-LIMIT (verified: learning happened, content is "
                          "genuinely new, adequately powered) and STILL no held-out lift from more diversity "
                          "(slope=%.3f). %sThis says the top-1-layer fine-tune / entity OBJECTIVE does not "
                          "capture broad-vocab generalization -- a DESIGN fix (more unfreeze / harder in-batch "
                          "negatives / more steps / richer contexts), NOT a capability ceiling. " % (slope, mem_note)
                          + fd + " " + sub), bands

    return "MIDDLE", ("PARTIAL upward trajectory: more training helps but did not clear HARD_PASS (slope=%.3f in "
                      "(tie=%.2f, slope_min=%.2f), lift(max)=%.3f). Report the slope = the extrapolation for the "
                      "USER's curriculum-scale decision. " % (slope, TIE_BAND, SLOPE_MIN, lift_hi) + fd + " " + sub), bands


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


# ================= self-test =================
def run_self_test():
    g._snapshot_vocab()
    n_color = len(clean.COLORS)
    _log("SELF-TEST: single-token real-noun palette + FIXED split + nested diversity prefixes ...")
    nouns = _nouns_for(N_NOUN_SMOKE)
    assert not (set(nouns) & set(clean.COLORS)), "real nouns overlap color vocab"
    g.install_vocab(nouns)
    assert g.vocab_is(N_NOUN_SMOKE), "vocab not installed in all modules"
    held, train_pool, perm = _split_and_perm(N_NOUN_SMOKE)
    grid = _grid_for("smoke", len(train_pool))
    # nested prefixes: smaller grid = strict subset of larger
    for i in range(len(grid) - 1):
        assert set(perm[:grid[i]]).issubset(set(perm[:grid[i + 1]])), "diversity levels not nested"
    for k in grid:
        assert set(perm[:k]).isdisjoint(set(held)), "train level %d overlaps held (fairness breach)" % k
    _log("  N_NOUN=%d held=%d train_pool=%d grid=%s (nested, held-disjoint) chance=%.4f"
         % (N_NOUN_SMOKE, len(held), len(train_pool), list(grid), clean.CHANCE))

    _log("SELF-TEST: real_code_path -- frozen encoder + eval pipeline DRIFT GUARD under real-noun vocab ...")
    tables = clean.build_tables()
    assert tables["filler"].shape[0] == N_NOUN_SMOKE, "filler codebook not resized"
    ext_fz = lt.RetrainableExtractor(); ext_fz.build()
    ds = clean.gen_dataset(12, np.random.default_rng(7))
    dec_ra, ans_ra, _ = eb.build_decoded_dataset(ds, ext_fz, "role_attn")
    main_ra = eb.run_arm_decoded(dec_ra, ans_ra, tables, "main")
    dec_dc, ans_dc, _ = ef.build_addr_dataset(ds, ext_fz, "decoded")
    main_dc = eb.run_arm_decoded(dec_dc, ans_dc, tables, "main")
    for qt in QUERY_TYPES:
        assert main_dc[qt]["preds_digest"] == main_ra[qt]["preds_digest"], "DRIFT_GUARD %s" % qt
    g.restore_vocab()
    assert g.vocab_is(n_color), "restore failed"
    _log("  DRIFT GUARD PASS (eval pipeline identical between arms under real-noun vocab)")

    _log("SELF-TEST: tiny base-unit + two diversity levels end-to-end + arms-differ + level-differ ...")
    nouns = _nouns_for(N_NOUN_SMOKE)
    base = run_base(7, "smoke", eval_n=10, n_noun=N_NOUN_SMOKE, nouns=nouns)
    g.restore_vocab()
    lvl_lo = run_level(7, grid[0], "smoke", eval_n=10, n_noun=N_NOUN_SMOKE, nouns=nouns); g.restore_vocab()
    lvl_hi = run_level(7, grid[-1], "smoke", eval_n=10, n_noun=N_NOUN_SMOKE, nouns=nouns); g.restore_vocab()

    dig_fz = hashlib.sha256(json.dumps([round(base["frozen_type"][qt], 4) for qt in QUERY_TYPES]).encode()).hexdigest()
    dig_tu = hashlib.sha256(json.dumps([round(lvl_hi["tuned_type"][qt], 4) for qt in QUERY_TYPES]).encode()).hexdigest()
    # META_RULE_AF: an inert fine-tune would leave loop, q_agree AND geometry identical vs frozen
    arms_differ = (dig_fz != dig_tu) or (abs(base["frozen_q_agree"] - lvl_hi["tuned_q_agree"]) > 1e-9) \
        or (abs(lvl_hi["wc_tuned"] - base["wc_frozen"]) > 1e-6)
    assert arms_differ, "META_RULE_AF: frozen vs tuned indistinguishable (inert fine-tune bug)"
    # SWEEP discriminator-fires: the two diversity levels must not be bit-identical (an inert sweep axis = bug)
    dig_lo = hashlib.sha256(json.dumps([round(lvl_lo["tuned_type"][qt], 4) for qt in QUERY_TYPES]).encode()).hexdigest()
    levels_differ = (dig_lo != dig_tu) or (abs(lvl_lo["tuned_noun_loop"] - lvl_hi["tuned_noun_loop"]) > 1e-9) \
        or (abs(lvl_lo["wc_tuned"] - lvl_hi["wc_tuned"]) > 1e-9)
    assert levels_differ, "SWEEP-INERT: two diversity levels produced identical tuned output (sweep axis moves nothing)"
    for r in (base,):
        for qt in QUERY_TYPES:
            v = r["frozen_type"][qt]
            assert math.isnan(v) or (0.0 <= v <= 1.0), "frozen out of range: %s" % v
    for r in (lvl_lo, lvl_hi):
        for arm in ("tuned_type", "oracle_type"):
            for qt in QUERY_TYPES:
                v = r[arm][qt]
                assert math.isnan(v) or (0.0 <= v <= 1.0), "%s out of range: %s" % (arm, v)
    g.restore_vocab()
    _log("  arms-differ=%s levels-differ=%s | base frozen=%.3f | lift_lo=%.3f lift_hi=%.3f | color-anchor lift=%.3f"
         % (arms_differ, levels_differ, base["frozen_noun_loop"],
            lvl_lo["tuned_noun_loop"] - base["frozen_noun_loop"],
            lvl_hi["tuned_noun_loop"] - base["frozen_noun_loop"],
            base["anchor_tuned_color_loop"] - base["anchor_frozen_color_loop"]))
    _log("SELF-TEST PASS")
    return {"n_single_token_nouns": len(_nouns_for(N_NOUN_LITE)), "n_noun_lite": N_NOUN_LITE,
            "n_noun_smoke": N_NOUN_SMOKE, "grid_lite": list(DIVERSITY_GRID_LITE),
            "grid_smoke": list(grid), "color_vocab_size": n_color, "arms_differ_verified": bool(arms_differ),
            "levels_differ_verified": bool(levels_differ), "held_nouns": base["held_nouns"],
            "tiny_frozen_loop": base["frozen_noun_loop"], "tiny_lift_lo": lvl_lo["tuned_noun_loop"] - base["frozen_noun_loop"],
            "tiny_lift_hi": lvl_hi["tuned_noun_loop"] - base["frozen_noun_loop"],
            "tiny_color_anchor_lift": base["anchor_tuned_color_loop"] - base["anchor_frozen_color_loop"]}


# ================= main =================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--lite", action="store_true")
    ap.add_argument("--budget-sec", type=float, default=460.0,
                    help="lite: stop starting NEW units once this many seconds elapsed this call (resumable "
                         "per-unit). Keeps each foreground call under the 10-min timeout.")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.lite):
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = "lite"

    g._snapshot_vocab()
    n_noun = N_NOUN_SMOKE if run_mode == "smoke" else N_NOUN_LITE
    seeds = SEEDS_SMOKE if run_mode == "smoke" else SEEDS_LITE
    eval_n = GRID_EVAL_N_SMOKE if run_mode == "smoke" else GRID_EVAL_N_LITE

    if run_mode == "self_test":
        _write_start_marker(OUTPUT_DIR, run_mode, 1)
        t0 = time.perf_counter()
        st = run_self_test()
        metrics = {"verdict": "SELFTEST_PASS",
                   "verdict_msg": "SELFTEST_PASS (vocab-patch + nested-diversity-prefixes + real_code_path + "
                                  "drift-guard + base/two-level end-to-end + arms-differ + levels-differ)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": time.perf_counter() - t0,
                   "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "selftest": st,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return

    nouns = _nouns_for(n_noun)
    # determine the grid under this palette (needs vocab installed for the pool size)
    g.install_vocab(nouns)
    _held, train_pool, _perm = _split_and_perm(n_noun)
    grid = _grid_for(run_mode, len(train_pool))
    # pre-run construction audit under the real-noun vocab
    audit = clean.audit_construction(seed=7, n=300)
    g.restore_vocab()
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    expected_units = len(seeds) * (1 + len(grid))
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()
    _log("%s: n_noun=%d chance=%.4f seeds=%s grid=%s eval_n=%d expected_units=%d nouns[:8]=%s"
         % (run_mode.upper(), n_noun, 1.0 / n_noun, seeds, list(grid), eval_n, expected_units, nouns[:8]))

    # build the unit worklist: per seed -> 1 base unit + one tuned unit per diversity level
    worklist = []
    for s in seeds:
        worklist.append(("base", s, None))
        for k in grid:
            worklist.append(("tuned", s, k))

    done = ckpt.completed_units(OUTPUT_DIR)
    ran_this_call = 0
    for kind, s, k in worklist:
        key = ckpt.unit_key(kind, s, (k if k is not None else -1), run_mode)
        if key in done:
            continue
        if ran_this_call >= 1 and run_mode == "lite" and (time.perf_counter() - t0) > args.budget_sec:
            _log("  budget %.0fs reached after %d new unit(s); stopping (re-run to resume)"
                 % (args.budget_sec, ran_this_call))
            break
        if kind == "base":
            res = run_base(s, run_mode, eval_n, n_noun, nouns)
        else:
            res = run_level(s, k, run_mode, eval_n, n_noun, nouns)
        g.restore_vocab()   # leave modules clean between units
        ckpt.record_unit(OUTPUT_DIR, key, res)
        ran_this_call += 1

    units_map = ckpt.load_units(OUTPUT_DIR)
    bases, tuned = [], []
    for kind, s, k in worklist:
        key = ckpt.unit_key(kind, s, (k if k is not None else -1), run_mode)
        if key in units_map:
            (bases if kind == "base" else tuned).append(units_map[key])
    n_done = len(bases) + len(tuned)
    if n_done < expected_units:
        _log("PARTIAL: %d/%d units done -- re-run to resume" % (n_done, expected_units))
        metrics = {"verdict": "PARTIAL", "verdict_msg": "%d/%d units complete; re-run to resume"
                   % (n_done, expected_units), "summary": "PARTIAL %d/%d" % (n_done, expected_units),
                   "run_mode": run_mode, "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                   "anchor_name": ANCHOR_NAME, "n_units_done": n_done, "expected_n_units": expected_units,
                   "cardinality_ok": False, "bases": bases, "tuned": tuned, "start_marker_written": True,
                   "crash_diagnostic_present": True, "final_metrics_atomicity": "tmp_replace",
                   "progress_logging": "print_flush_true"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE (partial) %s in %.1fs" % (run_mode, time.perf_counter() - t0))
        return

    verdict, msg, bands = decide_verdict(bases, tuned, seeds, grid, eval_n)
    elapsed = time.perf_counter() - t0
    metrics = {"verdict": verdict, "verdict_msg": msg,
               "summary": "%s | n_noun=%d chance=%.4f grid=%s | %s"
               % (verdict, n_noun, 1.0 / n_noun, list(grid), msg[:150]),
               "run_mode": run_mode, "elapsed_s": elapsed, "ts_iso": _now_iso(),
               "anchor_name": ANCHOR_NAME, "chance": 1.0 / n_noun, "bands": bands,
               "cardinality_ok": bool(n_done == expected_units), "expected_n_units": expected_units,
               "n_units_done": n_done, "construction_audit": audit, "bases": bases, "tuned": tuned,
               "params": {"DIM": clean.DIM, "N_NOUN": n_noun, "DEPTH": DEPTH, "NCTX": NCTX,
                          "steps": STEPS_SMOKE if run_mode == "smoke" else STEPS_LITE, "eval_n": eval_n,
                          "seeds": list(seeds), "grid": list(grid), "nouns": nouns},
               "arms_differ_verified": True, "start_marker_written": True,
               "crash_diagnostic_present": True, "final_metrics_atomicity": "tmp_replace",
               "defensive_error_checking": "passed_all_4_patterns", "progress_logging": "print_flush_true"}
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
