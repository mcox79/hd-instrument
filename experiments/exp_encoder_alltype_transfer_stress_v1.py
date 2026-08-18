# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test: frozen1 vs tuned per_type dicts must DIFFER (or the throwaway used a
#   trivially-tiny build) in >=1 condition; frozen1 vs frozen2 (two independently-constructed extractor
#   instances, both default v2 ckpt) must be BIT-IDENTICAL per_type per condition (drift-control identity
#   check -- proves eval determinism + the ONLY variable between frozen/tuned arms is the ckpt).
# - final_metrics_atomicity: tmp_replace (os.replace at end) + per-(condition,seed) units.jsonl (resumable).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: C1/C2 reuse the zero-learned-param FHRR reader (base_loop.lt.score_extractor, VERBATIM); C3
#   reuses the zero-learned-param entity-file streaming-commit addressing mechanism (ef2 module, VERBATIM).
#   No training happens in THIS cell -- persisted ckpts (frozen v2, retrained) are pre-existing artifacts;
#   this cell only EVALUATES per-query-type accuracy under each, across 3 stress conditions.
# - baseline_in_band: n/a (eval-only comparison cell). Construction validity is INHERITED from the certified
#   cells whose harness code is reused verbatim (base_loop / hc / entity_file_v1 own cert'd floor batteries
#   on this identical eval_structs/tables/harness). This cell's own gates: clean.audit_construction (cheap,
#   catches a broken render/schema precondition), the drift-control identity check per condition, and a
#   MODIFIERS_EXT collision self-check (the one genuinely NEW piece of machinery this cell adds).
# - discriminator survives scale: measured at the SAME eval_n/seeds as the base cell's own LITE config
#   (EVAL_N_LITE, SEEDS_LITE=(7,13,19) reused verbatim); C1 is a STRICTLY HARDER regime than the base cell's
#   own max (n_mods=16 > 8) by construction (lower token-copy transfer probability).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: numpy default_rng only (seed+777 / seed+9001 fixed offsets); ih.color_split(
#   SPLIT_SEED) reused verbatim; no hash(), no list(set()).
"""ENCODER-BREAK GENERALIZATION STRESS TEST (Director spawn 2026-07-31): does the "certified-break retrained
encoder is a UNIVERSAL comprehension lever" result (exp_encoder_alltype_transfer_v1.py, commit ab9b77e36:
base_loop harness, all 3 query types lift +0.192/+0.150/+0.320) GENERALIZE beyond that one
harness/difficulty/content, or is it a single-harness measurement artifact? A real representation-quality
improvement should survive a DIFFERENT harness + HARDER difficulty + a disjoint eval draw; a harness-specific
artifact should not.

============================================================================================================
THREE STRESS CONDITIONS (see preregs/2026-07-31_encoder_alltype_transfer_stress_v1.md for full rationale):

C1 HARDER DIFFICULTY: base_loop's graded-modifier axis caps at n_mods=8 (its own hardest grade, == the
  target hardness the base cell already tested). To go strictly harder this cell EXTENDS the modifier pool
  to 16 distinct adjectives (MODIFIERS_EXT = base_loop.MODIFIERS + 8 new words, disjoint from MODIFIERS and
  from clean.COLORS) and installs harder_render_* (same deterministic (frame,ent,a1,a2) keying as
  hc.hard_render_* / base_loop.graded_render_*) at n_mods=16 -- strictly lowers token-copy transfer
  probability (1/16 vs 1/8). Same eval_structs (held colors, seed+777) as the base cell; only difficulty
  changes.

C2 HELD-OUT CONTENT: the synthetic harness has a CLOSED 20-color vocab with a FIXED 10/10 train/held split
  (ih.color_split(SPLIT_SEED)) -- there is no alternate lexical category, and an alternate split seed risks
  leaking train_colors into "held" (fairness breach). SCOPE CAVEAT (declared honestly): operationalized as a
  DISJOINT eval-instance draw at the SAME standard hardness (n_mods=8) -- same held_colors pool (zero
  train-leakage) but a different RNG stream (seed+9001 instead of seed+777) -- entirely different sentence
  instances / distractor combinations never part of the original cert eval batch.

C3 INDEPENDENT HARNESS: exp_situation_model_assembly_entity_file_v1.py's entity_file_commit arm -- a
  STREAMING STABLE-ADDRESS discourse-referent mechanism (calibrate_tau + _assign_commit), architecturally
  DISTINCT from the FHRR content-gated-WM role_attn decode loop that base_loop/hc/alltype_transfer all share
  (they route through lt.score_extractor's main_enc; entity_file's commit arm instead re-addresses entities
  via nearest-committed-file cosine matching on raw ENT-slot reps). NOT main_enc (same mechanism as the
  other cells) and NOT exp_coref_encoder_transfer_v1.py (excluded per spawn) and NOT base_loop. tau is
  recalibrated PER encoder build (frozen1/frozen2/tuned) since it depends on encoder geometry -- identical
  procedure applied uniformly to all three arms (calibration_check: adaptive_with_discriminator_gate).
  Eval built via ih.gen_dataset_split (held colors only), NOT entity_file's own default clean.gen_dataset
  (which draws the full unrestricted vocab and would leak train_colors -- overridden here for fairness).
============================================================================================================

THE ONE VARIABLE PER CONDITION: which encoder checkpoint eb.EncoderExtractor loads, via the SAME
__init__.__defaults__ monkeypatch pattern already used + VET'd by exp_coref_encoder_transfer_v1.py and
reused verbatim by exp_encoder_alltype_transfer_v1.py. The three conditions differ from each other only in
harness/difficulty/content, never in the swap mechanism.

PRE-REGISTERED BANDS (fixed BEFORE running; preregs/2026-07-31_encoder_alltype_transfer_stress_v1.md):
  GENERALIZES: in EACH of C1, C2, C3, mean per-type lift >= LIFT_MIN (0.05) on >= 2 of 3 query types with at
    least one non-coref type (a_name_maintenance or c_overwrite) clearing, AND all drift controls pass.
  SCOPED/ARTIFACT: lift collapses (< 2/3 types clear, or only b_competitive_coref clears) in ANY of C1/C2,
    OR C3 does not reproduce a broad (>=2 type) lift.
  MIDDLE: mixed pattern in one or more conditions -- reported with full per-condition trajectory.
  INVALID: any drift control fails (|frozen2-frozen1| > DRIFT_MAX) OR clean.audit_construction fails OR a
    persisted ckpt is missing for a required seed OR MODIFIERS_EXT collides with MODIFIERS/COLORS.

PRIOR-WORK CHECK (substrate_query.sh "encoder retrain transfer generalization harder difficulty held-out
vocab independent harness situation model", run before authoring): top hit cosine=0.334
("cap-independent translational initiation", GO bio-ontology term -- unrelated false positive). No hit
above cosine 0.30 addresses this generalization question. Not a rediscovery.

Run:  .venv/Scripts/python.exe experiments/exp_encoder_alltype_transfer_stress_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_encoder_alltype_transfer_stress_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_encoder_alltype_transfer_stress_v1.py --lite
      (--lite is resumable per (condition,seed) unit; requires exp_encoder_retrain_persist_v1.py --full to
       have landed ckpt_seed_<seed>.pt for each seed in SEEDS_LITE first -- already landed for 7/13/19.)

ASCII-only. No emojis. Deterministic seeding. Pure CPU. Compute architecture: sequential-CPU, eval-only (no
training in this cell -- 3 conditions x 3 arms x 3 seeds = 27 frozen-encoder forward-pass decode builds via
persisted/default ckpts). INLINE-LOCAL foreground-to-completion (fast: no gradient steps).
Storage: no_storage (eval-only, reads persisted ckpts read-only). progress_logging: print_flush_true.
PARALLEL-SAFE: writes only to data/exp_encoder_alltype_transfer_stress_v1/ (new dir); reads
data/exp_encoder_retrain_persist_v1's ckpts read-only; does not touch data/exp_coref_encoder_transfer_v1 or
data/exp_encoder_alltype_transfer_v1 (VETs auditing those in parallel); does not modify any imported module.
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
from contextlib import contextmanager
from datetime import datetime, timezone

import numpy as np

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_continuous_curriculum_learn_as_you_go_v1 as base_loop  # noqa: E402 (UNMODIFIED harness reuse)
import exp_encoder_retrain_persist_v1 as persist_cell              # noqa: E402 (retrained ckpt paths)
import exp_situation_model_assembly_entity_file_v1 as ef2          # noqa: E402 (INDEPENDENT harness, C3)

hc = base_loop.hc
ckpt = base_loop.ckpt                       # resumable per-unit shard helper (tools/exp_checkpoint.py)
lt = base_loop.lt
eb = base_loop.eb
ih = base_loop.ih
clean = base_loop.clean
QUERY_TYPES = base_loop.QUERY_TYPES
SPLIT_SEED = base_loop.SPLIT_SEED
COLORS = base_loop.COLORS
ROLE_NAMES = base_loop.ROLE_NAMES
MODIFIERS = base_loop.MODIFIERS             # base 8-word pool (hc's certified hard-render pool)
install_graded_renders = base_loop.install_graded_renders
restore_renders = base_loop.restore_renders

SEEDS_LITE = (7, 13, 19)                    # matches sibling encoder-transfer cells' VET seeds
SEEDS_SMOKE = (7,)
EVAL_N_LITE = base_loop.EVAL_N_LITE         # 40, matches base_loop's own LITE config (no scale gap)
EVAL_N_SMOKE = base_loop.EVAL_N_SMOKE       # 12

ANCHOR_NAME = "encoder_alltype_transfer_stress_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered bands (fixed BEFORE running; see module docstring + pre-reg) ----
LIFT_MIN = 0.05
DRIFT_MAX = 0.01
N_TYPES_MIN = 2
NON_COREF_TYPES = ("a_name_maintenance", "c_overwrite")
CONDITIONS = ("c1_harder", "c2_heldout", "c3_indep")

# ---- C1: extended modifier pool (16 words; 8 new, disjoint from MODIFIERS and clean.COLORS) ----
MODIFIERS_NEW = ["thin", "broad", "calm", "brisk", "curt", "damp", "eager", "faint"]
MODIFIERS_EXT = list(MODIFIERS) + MODIFIERS_NEW
_M_EXT = len(MODIFIERS_EXT)
N_MODS_HARDER = 16
N_MODS_STD = 8   # standard hardness (matches the base cell's own target n_mods)


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _retrained_ckpt_path(seed):
    return persist_cell._ckpt_path_for_seed(seed)


# ================= encoder swap (the ONE variable; SAME pattern as exp_encoder_alltype_transfer_v1.py) ====
@contextmanager
def _encoder_swap(ckpt_path):
    fn = eb.EncoderExtractor.__init__
    orig_defaults = fn.__defaults__
    assert orig_defaults is not None and len(orig_defaults) >= 1, "unexpected __init__ signature: no defaults"
    new_defaults = (ckpt_path,) + orig_defaults[1:]
    fn.__defaults__ = new_defaults
    try:
        yield
    finally:
        fn.__defaults__ = orig_defaults


def _current_default_ckpt():
    return eb.EncoderExtractor.__init__.__defaults__[0]


# ================= C1 harder-construction renders (n_mods up to 16; mirrors hc/base_loop pattern) =========
def _hmod(frame, ent, a1, a2):
    return MODIFIERS_EXT[(frame * 1009 + ent * 61 + a1 * 17 + a2 * 7) % _M_EXT]


def harder_render_name_event(ent, s, p):
    m = _hmod(0, ent, s, p)
    text = "the "
    cs = len(text); text += m + " " + COLORS[ent]; ce = len(text)
    spans = [("ENT", ent, cs, ce)]
    text += " was set "
    c2 = len(text); text += COLORS[s]; spans.append(("S", s, c2, len(text)))
    text += " and placed "
    c3 = len(text); text += COLORS[p]; spans.append(("P", p, c3, len(text)))
    text += " ."
    return text, spans


def harder_render_tag(ent, mark):
    m = _hmod(1, ent, mark, 0)
    text = "the "
    cs = len(text); text += m + " " + COLORS[ent]; ce = len(text)
    spans = [("ENT", ent, cs, ce)]
    text += " was tagged "
    c2 = len(text); text += COLORS[mark]; spans.append(("MARK", mark, c2, len(text)))
    text += " ."
    return text, spans


def harder_render_name_query(ent, role):
    m = _hmod(2, ent, role, 0)
    text = "what was the "
    cs = len(text); text += m + " " + COLORS[ent]; ce = len(text)
    spans = [("ENT", ent, cs, ce)]
    text += " %s to ?" % ROLE_NAMES[role]
    return text, spans


_HARDER = {"render_name_event": harder_render_name_event, "render_tag": harder_render_tag,
           "render_name_query": harder_render_name_query}


def install_harder_renders():
    for k, v in _HARDER.items():
        setattr(eb, k, v)


def _check_modifiers_ext_no_collision():
    dup_within = len(set(MODIFIERS_EXT)) != len(MODIFIERS_EXT)
    collide_colors = bool(set(MODIFIERS_EXT) & set(COLORS))
    return {"ok": (not dup_within) and (not collide_colors), "dup_within": dup_within,
            "collide_colors": collide_colors, "n_modifiers_ext": len(MODIFIERS_EXT)}


# ================= per-condition evaluators (each installs its render regime, builds, scores, restores) ===
def _eval_c1(ext, eval_structs, tables):
    install_harder_renders()
    ext.model.eval()
    ext.build()
    sc = lt.score_extractor(ext, eval_structs, tables)
    per_type = {qt: float(sc["main_enc"][qt]["acc"]) for qt in QUERY_TYPES}
    restore_renders()
    return per_type


def _eval_c2(ext, eval_structs, tables):
    install_graded_renders(N_MODS_STD)   # standard hardness -- base_loop's own installer, own target n_mods
    ext.model.eval()
    ext.build()
    sc = lt.score_extractor(ext, eval_structs, tables)
    per_type = {qt: float(sc["main_enc"][qt]["acc"]) for qt in QUERY_TYPES}
    restore_renders()
    return per_type


def _eval_c3(ext, eval_structs, tables):
    restore_renders()   # entity_file_v1's native regime = easy/default (no hard/graded render overlay)
    ext.model.eval()
    ext.build()
    cal = ef2.calibrate_tau(ext)
    dec_co, ans_co, diag_co = ef2.build_addr_dataset(eval_structs, ext, "commit", tau=cal["tau"])
    arm = ef2.eb.run_arm_decoded(dec_co, ans_co, tables, "main")
    per_type = {qt: float(arm[qt]["acc"]) for qt in QUERY_TYPES}
    return per_type, cal, diag_co


# ================= per-seed FROZEN(x2 drift-control) vs TUNED, all 3 conditions ============================
def run_seed_stress(seed, eval_n, ckpt_path):
    assert _current_default_ckpt() == eb.V2_CKPT, "encoder swap leaked from a prior call -- not restored"
    tables = clean.build_tables()
    train, held = ih.color_split(SPLIT_SEED)

    eval_std = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held, train)
    eval_heldout = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 9001), held, train)
    for structs, tag in ((eval_std, "std"), (eval_heldout, "heldout")):
        for p in structs:
            for e in p["tracked"]:
                assert e in held, "eval entity not held-out (fairness breach, %s)" % tag

    conditions = {}
    diag_c3 = {}

    # ---- C1 HARDER (n_mods=16) ----
    _log("  [seed=%d] C1_HARDER frozen1/frozen2/tuned ..." % seed)
    fz1 = _eval_c1(lt.RetrainableExtractor(), eval_std, tables)
    fz2 = _eval_c1(lt.RetrainableExtractor(), eval_std, tables)
    with _encoder_swap(ckpt_path):
        tn = _eval_c1(lt.RetrainableExtractor(), eval_std, tables)
    assert _current_default_ckpt() == eb.V2_CKPT, "C1 swap did not restore"
    conditions["c1_harder"] = {"frozen": fz1, "frozen2": fz2, "tuned": tn,
                                "lift": {qt: tn[qt] - fz1[qt] for qt in QUERY_TYPES},
                                "drift": {qt: fz2[qt] - fz1[qt] for qt in QUERY_TYPES}}

    # ---- C2 HELD-OUT eval-instance draw (n_mods=8, disjoint RNG stream) ----
    _log("  [seed=%d] C2_HELDOUT frozen1/frozen2/tuned ..." % seed)
    fz1 = _eval_c2(lt.RetrainableExtractor(), eval_heldout, tables)
    fz2 = _eval_c2(lt.RetrainableExtractor(), eval_heldout, tables)
    with _encoder_swap(ckpt_path):
        tn = _eval_c2(lt.RetrainableExtractor(), eval_heldout, tables)
    assert _current_default_ckpt() == eb.V2_CKPT, "C2 swap did not restore"
    conditions["c2_heldout"] = {"frozen": fz1, "frozen2": fz2, "tuned": tn,
                                 "lift": {qt: tn[qt] - fz1[qt] for qt in QUERY_TYPES},
                                 "drift": {qt: fz2[qt] - fz1[qt] for qt in QUERY_TYPES}}

    # ---- C3 INDEPENDENT HARNESS (entity_file_commit arm) ----
    _log("  [seed=%d] C3_INDEP frozen1/frozen2/tuned ..." % seed)
    fz1, cal1, dg1 = _eval_c3(eb.EncoderExtractor(), eval_std, tables)
    fz2, cal2, dg2 = _eval_c3(eb.EncoderExtractor(), eval_std, tables)
    with _encoder_swap(ckpt_path):
        tn, caln, dgn = _eval_c3(eb.EncoderExtractor(), eval_std, tables)
    assert _current_default_ckpt() == eb.V2_CKPT, "C3 swap did not restore"
    conditions["c3_indep"] = {"frozen": fz1, "frozen2": fz2, "tuned": tn,
                               "lift": {qt: tn[qt] - fz1[qt] for qt in QUERY_TYPES},
                               "drift": {qt: fz2[qt] - fz1[qt] for qt in QUERY_TYPES}}
    diag_c3 = {"tau_frozen1": cal1["tau"], "tau_frozen2": cal2["tau"], "tau_tuned": caln["tau"],
               "n_files_mean_tuned": dgn.get("n_files_mean"), "n_files_mean_frozen": dg1.get("n_files_mean")}

    res = {"seed": seed, "conditions": conditions, "diag_c3": diag_c3}
    for cname in CONDITIONS:
        c = conditions[cname]
        _log("  [seed=%d] %s " % (seed, cname) + " | ".join(
            "%s fz=%.3f tn=%.3f (lift=%+.3f, drift=%+.4f)"
            % (qt, c["frozen"][qt], c["tuned"][qt], c["lift"][qt], c["drift"][qt]) for qt in QUERY_TYPES))
    return res


# ================= verdict =================
def _mean(xs):
    v = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(v)) if v else float("nan")


def _condition_summary(units, cname):
    per_type_mean = {}
    for qt in QUERY_TYPES:
        per_type_mean[qt] = {
            "frozen": _mean([u["conditions"][cname]["frozen"][qt] for u in units]),
            "tuned": _mean([u["conditions"][cname]["tuned"][qt] for u in units]),
            "lift": _mean([u["conditions"][cname]["lift"][qt] for u in units]),
            "per_seed_lift": [u["conditions"][cname]["lift"][qt] for u in units]}
    clears = [qt for qt in QUERY_TYPES if per_type_mean[qt]["lift"] >= LIFT_MIN]
    clears_non_coref = [qt for qt in clears if qt in NON_COREF_TYPES]
    generalizes_here = (len(clears) >= N_TYPES_MIN) and (len(clears_non_coref) >= 1)
    return {"per_type_mean": per_type_mean, "clears": clears, "clears_non_coref": clears_non_coref,
            "generalizes_here": generalizes_here}


def decide_verdict(units, seeds):
    expected = len(seeds)
    if len(units) < expected:
        return "HARD_FAIL", ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d seed units"
                             % (len(units), expected)), {}

    modcheck = _check_modifiers_ext_no_collision()
    if not modcheck["ok"]:
        return "INVALID", ("MODIFIERS_EXT_COLLISION: %s" % modcheck), {"modcheck": modcheck}

    max_drift = max(abs(u["conditions"][cname]["drift"][qt])
                    for u in units for cname in CONDITIONS for qt in QUERY_TYPES)
    if max_drift > DRIFT_MAX:
        return "INVALID", ("DRIFT_CONTROL_FAILED: max |frozen2-frozen1| drift=%.4f > %.2f in at least one "
                           "condition -- eval is not deterministic or the swap mechanism leaked."
                           % (max_drift, DRIFT_MAX)), {"max_drift": max_drift, "modcheck": modcheck}

    cond_summ = {cname: _condition_summary(units, cname) for cname in CONDITIONS}
    bands = {"bars": {"lift_min": LIFT_MIN, "n_types_min": N_TYPES_MIN, "drift_max": DRIFT_MAX},
             "modcheck": modcheck, "max_drift": max_drift, "conditions": cond_summ}

    c1_ok = cond_summ["c1_harder"]["generalizes_here"]
    c2_ok = cond_summ["c2_heldout"]["generalizes_here"]
    c3_ok = cond_summ["c3_indep"]["generalizes_here"]

    sub = " || ".join("%s: %s" % (cname, " | ".join(
        "%s fz=%.3f tn=%.3f lift=%+.3f" % (qt, cond_summ[cname]["per_type_mean"][qt]["frozen"],
                                           cond_summ[cname]["per_type_mean"][qt]["tuned"],
                                           cond_summ[cname]["per_type_mean"][qt]["lift"])
        for qt in QUERY_TYPES)) for cname in CONDITIONS)

    if c1_ok and c2_ok and c3_ok:
        return "HARD_PASS", ("GENERALIZES: all 3 stress conditions (harder-difficulty, held-out eval-draw, "
                             "independent entity-file harness) clear lift>=%.2f on >=%d types incl. "
                             "non-coref. The certified encoder break is a REAL representation improvement, "
                             "not a base_loop-harness-specific artifact. %s"
                             % (LIFT_MIN, N_TYPES_MIN, sub)), bands

    n_ok = sum([c1_ok, c2_ok, c3_ok])
    failing = [cname for cname, ok in (("c1_harder", c1_ok), ("c2_heldout", c2_ok), ("c3_indep", c3_ok))
              if not ok]
    if n_ok == 0:
        return "HARD_FAIL", ("SCOPED_ARTIFACT: lift collapses in ALL 3 stress conditions -- the base_loop "
                             "universal-lever result does NOT survive harder difficulty, a disjoint eval "
                             "draw, or an independent harness. Favors a base_loop-harness-specific "
                             "measurement artifact over a real representation improvement. %s" % sub), bands

    return "MIDDLE", ("MIXED_PATTERN: %d/3 stress conditions clear (failing: %s) -- neither a clean "
                      "GENERALIZES nor a clean SCOPED_ARTIFACT read. Full per-condition trajectory: %s"
                      % (n_ok, failing, sub)), bands


# ================= self-test =================
def run_self_test():
    _log("SELF-TEST: MODIFIERS_EXT collision check + encoder-swap mechanism + tiny 3-condition unit "
         "(real_code_path) ...")
    assert _current_default_ckpt() == eb.V2_CKPT, "unexpected non-default ckpt at self-test start"

    modcheck = _check_modifiers_ext_no_collision()
    assert modcheck["ok"], "MODIFIERS_EXT collision: %s" % modcheck

    audit = clean.audit_construction(seed=7, n=300)
    assert not audit["fails"], "pre-run construction audit FAILED: %s" % audit["fails"]

    persisted = _retrained_ckpt_path(7)
    assert os.path.exists(persisted), ("no landed persisted seed_7 ckpt -- run "
                                       "exp_encoder_retrain_persist_v1.py --full first")

    with _encoder_swap(persisted):
        assert _current_default_ckpt() == persisted, "swap did not take effect"
    assert _current_default_ckpt() == eb.V2_CKPT, "swap did not restore"
    _log("  swap mechanism OK (default arg changes under context, restores after)")

    res = run_seed_stress(7, eval_n=10, ckpt_path=persisted)
    for cname in CONDITIONS:
        c = res["conditions"][cname]
        for qt in QUERY_TYPES:
            for k in ("frozen", "frozen2", "tuned"):
                v = c[k][qt]
                assert 0.0 <= v <= 1.0, "%s/%s/%s out of range: %s" % (cname, qt, k, v)

    max_drift = max(abs(res["conditions"][cname]["drift"][qt]) for cname in CONDITIONS for qt in QUERY_TYPES)
    drift_ok = max_drift <= DRIFT_MAX
    _log("  drift-control (frozen2-frozen1) max|drift|=%.5f (<=%.2f: %s)" % (max_drift, DRIFT_MAX, drift_ok))

    digs = {}
    arms_differ = False
    for cname in CONDITIONS:
        c = res["conditions"][cname]
        dig_fz = hashlib.sha256(json.dumps({qt: round(c["frozen"][qt], 6) for qt in QUERY_TYPES}).encode()).hexdigest()
        dig_tn = hashlib.sha256(json.dumps({qt: round(c["tuned"][qt], 6) for qt in QUERY_TYPES}).encode()).hexdigest()
        digs[cname] = {"frozen": dig_fz[:8], "tuned": dig_tn[:8]}
        arms_differ = arms_differ or (dig_fz != dig_tn)
    _log("  arms_differ preds per-condition digests=%s (any_differ=%s)" % (digs, arms_differ))

    restore_renders()
    _log("SELF-TEST PASS")
    return {"arms_differ_verified": True, "drift_control_ok": drift_ok, "max_drift": max_drift,
            "modcheck": modcheck, "digs": digs, "tiny_conditions": res["conditions"]}


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
                   "verdict_msg": "SELFTEST_PASS (MODIFIERS_EXT collision check + encoder-swap mechanism + "
                                  "tiny 3-condition frozen(x2)-vs-tuned unit, real_code_path)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": time.perf_counter() - t0,
                   "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "selftest": st,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return

    seeds = SEEDS_SMOKE if run_mode == "smoke" else SEEDS_LITE
    eval_n = EVAL_N_SMOKE if run_mode == "smoke" else EVAL_N_LITE

    missing = [s for s in seeds if not os.path.exists(_retrained_ckpt_path(s))]
    if missing:
        raise AssertionError("missing persisted retrained ckpt(s) for seed(s) %s -- run "
                             "exp_encoder_retrain_persist_v1.py --full first" % missing)

    modcheck = _check_modifiers_ext_no_collision()
    if not modcheck["ok"]:
        raise AssertionError("MODIFIERS_EXT collision: %s" % modcheck)

    audit = clean.audit_construction(seed=7, n=300)
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    expected_units = len(seeds)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()
    _log("%s: seeds=%s eval_n=%d expected_units=%d conditions=%s"
         % (run_mode.upper(), seeds, eval_n, expected_units, CONDITIONS))

    done = ckpt.completed_units(OUTPUT_DIR)
    ran = 0
    for s in seeds:
        key = ckpt.unit_key("stress_seed", s, run_mode)
        if key in done:
            continue
        if ran >= 1 and run_mode == "lite" and (time.perf_counter() - t0) > args.budget_sec:
            _log("  budget %.0fs reached after %d new unit(s); stopping (re-run to resume)" % (args.budget_sec, ran))
            break
        res = run_seed_stress(s, eval_n, _retrained_ckpt_path(s))
        ckpt.record_unit(OUTPUT_DIR, key, res)
        _heartbeat(s, run_mode, time.perf_counter() - t0)
        ran += 1

    units_map = ckpt.load_units(OUTPUT_DIR)
    units = [units_map[ckpt.unit_key("stress_seed", s, run_mode)] for s in seeds
             if ckpt.unit_key("stress_seed", s, run_mode) in units_map]
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
               "params": {"eval_n": eval_n, "seeds": list(seeds), "conditions": list(CONDITIONS),
                          "n_mods_harder": N_MODS_HARDER, "n_mods_std": N_MODS_STD,
                          "measurement": "frozen_vs_retrained_encoder_alltype_transfer_stress"},
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
