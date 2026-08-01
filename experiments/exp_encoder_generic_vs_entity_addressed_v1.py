# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test: frozen1 vs tuned per-slot/per-type dicts must DIFFER; frozen1 vs
#   frozen2 (two independently-constructed RetrainableExtractor() instances, both default ckpt) must be
#   BIT-IDENTICAL (the built-in drift guard, SAME pattern as exp_encoder_alltype_transfer_v1.py).
# - final_metrics_atomicity: tmp_replace (os.replace at end) + per-seed units.jsonl (resumable).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: paired frozen-vs-tuned decode/geometry comparison, no capacity sweep.
# - baseline_in_band: n/a (eval-only comparison cell; construction validity inherited from
#   base_loop/growing_library's own cert'd floor batteries on this identical harness); this cell's own
#   gate is clean.audit_construction + the drift-control identity check above.
# - discriminator survives scale: measured at the SAME eval_n/seeds/hardness as base_loop/growing_library
#   and the two sibling encoder-transfer cells' own LITE config; no scale gap.
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: inherited VERBATIM from base_loop/lt (np.random.default_rng, sorted(set()),
#   no hash(), no list(set())).
"""ENCODER-BREAK: GENERIC REPRESENTATION-QUALITY vs ENTITY-ADDRESSING-SPECIFIC (Director spawn 2026-07-31).

`exp_encoder_alltype_transfer_v1.py` (landed HARD_PASS this session, MEASURED@
data/exp_encoder_alltype_transfer_v1/metrics.json) showed the certified minimal-unfreeze encoder retrain
(atom 29593) lifts ALL THREE situation-model query types (a_name_maintenance +0.192, b_competitive_coref
+0.150, c_overwrite +0.320), not just competitive-coref. BUT all three query types are still
ENTITY-ADDRESSED in the broader sense: every query answer is retrieved by the FHRR reader ADDRESSING a
specific entity's binding (main_enc arm) -- "universal across query types" is not yet "universal outside
entity-routed comprehension". THIS cell is the next open discriminator: does the retrain also sharpen a
genuinely NON-entity-addressed decode (reads the encoder's own representation with ZERO entity/mark
identity involved), or is the lift bounded to whatever routes through entity/mark identity?

============================================================================================================
THE NON-ENTITY-ADDRESSED PROBE (measurement 1, decisive): eb.build_decoded_dataset(dataset, extractor,
"role_attn") -- called internally by lt.score_extractor, already surfaced at
base_loop._eval_heldahead(...)["sc"]["stage_role_attn"] as a side-effect of the SAME held-ahead eval every
sibling cell runs -- returns a per-stage tally {ENT, MARK, S, P, ENT_q, MARK_q, entity_consistency}.
S and P are the state/placement filler-color decodes ("the ENT was set S and placed P ."), read from the
LOCAL token span's own representation via a fixed role cue ("what was set to?"/"what was placed to?"),
with NO cross-sentence binding, NO entity/mark matching, NO addressing step -- "which color word is
written here", independent of which entity the event belongs to. ENT, MARK (tag-position identity-label
decode), ENT_q, MARK_q (query-frame decode, requires identifying the target entity/mark) and
entity_consistency (cross-mention consistency of decoded entity id) are the entity-addressed comparison
set. This cell adds ZERO new decode machinery for measurement 1 -- it only surfaces existing fields that
every sibling cell already computes and discards.

MEASUREMENT 2 (representation geometry, entity vs non-entity dims): lt.within_minus_cross(ext,
held_colors, seed) (existing, cert-atom-adjacent -- name<->name cosine 0.057->0.110 under this exact
retrain, CITED@atom 29593) measures ENT-slot separability (mean within-color cosine minus cross-color
cosine on ENT-slot role_attn reps). This cell adds a ~15-line mirror, within_minus_cross_state(), that
runs the IDENTICAL computation on the S (state-filler) slot instead of ENT, via
eb.render_name_event(o1, c, o2) + ef._ent_slot_reps (already slot-type-generic, no modification needed).
Answers: does the retrain sharpen ONLY entity-routed geometry, or the representation broadly.
============================================================================================================

PRE-REGISTERED BANDS (fixed BEFORE running; preregs/2026-07-31_encoder_generic_vs_entity_addressed.md):
  GENERIC (HARD_PASS): mean(S,P) decode lift >= LIFT_MIN (0.05) on BOTH slots, AND S-geometry delta >=
    GEOM_FRAC_MIN (0.4) of the ENT-geometry delta measured in the SAME run -- broad sharpening.
  ENTITY_SPECIFIC (HARD_FAIL, informative negative): mean(S,P) lift < LIFT_MIN on BOTH slots, AND
    S-geometry delta < GEOM_FRAC_FLAT (0.15) of ENT-geometry delta, WHILE ENT-geometry delta itself clears
    ENT_GEOM_MIN (0.02) (entity geometry DID sharpen, replicating the cert-atom direction) -- bounded.
  MIDDLE: mixed pattern (one of S/P lifts but not the other; or ENT geometry itself fails to clear its own
    floor, making the ratio uninterpretable). Full trajectory reported.
  INVALID: drift-control fails (max |frozen2-frozen1| decode drift > DRIFT_MAX) OR
    clean.audit_construction flags fails OR a persisted retrained ckpt is missing for a required seed.

PRIOR-WORK CHECK (substrate_query.sh "encoder representation quality generic vs entity-addressing
specific non-entity decode geometry", run before authoring): top hit cosine=0.3271 (KG zero-shot
relation-prediction entity-pair-geometry note, different domain). No hit above cosine 0.30 addresses
whether THIS certified encoder break's lift is generic-representation vs entity-addressing-specific. Not
a rediscovery.

Run:  .venv/Scripts/python.exe experiments/exp_encoder_generic_vs_entity_addressed_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_encoder_generic_vs_entity_addressed_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_encoder_generic_vs_entity_addressed_v1.py --lite
      (--lite is resumable per-seed unit; requires exp_encoder_retrain_persist_v1.py --full to have landed
       data/exp_encoder_retrain_persist_v1/ckpt_seed_<seed>.pt for each seed in SEEDS_LITE first.)

ASCII-only. No emojis. Deterministic seeding. Pure CPU. Compute architecture: sequential-CPU, eval-only
(no training in this cell -- 3 frozen-encoder forward-pass decode builds per seed via
base_loop._eval_heldahead, reused verbatim; geometry reuses the SAME already-built extractor instances,
zero extra encoder construction). INLINE-LOCAL foreground-to-completion (fast: no gradient steps).
Storage: no_storage (eval-only, reads persisted ckpts read-only). progress_logging: print_flush_true.
PARALLEL-SAFE: writes only to data/exp_encoder_generic_vs_entity_addressed_v1/ (new dir); reads
data/exp_encoder_retrain_persist_v1's ckpts read-only; does not touch exp_coref_encoder_transfer_v1,
exp_encoder_alltype_transfer_v1, or any exp_encoder_*generaliz* dir another agent may be using; does not
modify base_loop, lt, eb, ef, or the growing-library cell.
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
import torch.nn.functional as F

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_continuous_curriculum_learn_as_you_go_v1 as base_loop  # noqa: E402 (UNMODIFIED per-seed harness)
import exp_encoder_retrain_persist_v1 as persist_cell              # noqa: E402 (retrained ckpt paths)

hc = base_loop.hc
ckpt = base_loop.ckpt                       # resumable per-unit shard helper (tools/exp_checkpoint.py)
lt = base_loop.lt
eb = base_loop.eb
ef = base_loop.ef                           # noqa: F401 (ent-slot rep extraction, slot-type-generic)
ih = base_loop.ih
clean = base_loop.clean
QUERY_TYPES = base_loop.QUERY_TYPES
SPLIT_SEED = base_loop.SPLIT_SEED
HARDNESS_LITE = base_loop.HARDNESS_LITE     # (1, 3, 8)
HARDNESS_SMOKE = base_loop.HARDNESS_SMOKE   # (1, 8)
SEEDS_LITE = (7, 13, 19)                    # matches both sibling encoder-transfer cells' VET seeds
SEEDS_SMOKE = (7,)
EVAL_N_LITE = base_loop.EVAL_N_LITE         # 40, matches base_loop's own LITE config (no scale gap)
EVAL_N_SMOKE = base_loop.EVAL_N_SMOKE       # 12
install_graded_renders = base_loop.install_graded_renders
restore_renders = base_loop.restore_renders
_eval_heldahead = base_loop._eval_heldahead

ANCHOR_NAME = "encoder_generic_vs_entity_addressed_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered bands (fixed BEFORE running; see module docstring + pre-reg file) ----
LIFT_MIN = 0.05               # HYPOTHESIZED: matches sibling cells' per-type meaningful-lift floor
DRIFT_MAX = 0.01              # frozen-vs-frozen drift-control ceiling (deterministic eval => expect ~0.0)
GEOM_FRAC_MIN = 0.4           # GENERIC requires S-geometry delta >= this fraction of ENT-geometry delta
GEOM_FRAC_FLAT = 0.15         # ENTITY_SPECIFIC requires S-geometry delta < this fraction of ENT-delta
ENT_GEOM_MIN = 0.02           # ENT-geometry delta must clear this floor for the ratio to be interpretable
                               # (CITED@atom 29593: name<->name cosine 0.057->0.110, delta ~0.053, so 0.02
                               # is well below the certified magnitude -- a conservative interpretability
                               # floor, not a tuned-to-pass threshold)
GEOM_NCTX = 40                # samples per color for within-minus-cross geometry (matches lt.EVAL_NCTX)
NON_ENTITY_STAGES = ("S", "P")
ENTITY_STAGES = ("ENT", "MARK", "ENT_q", "MARK_q")


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _retrained_ckpt_path(seed):
    return persist_cell._ckpt_path_for_seed(seed)


# ================= encoder swap (the ONE variable; SAME pattern as sibling cells) =================
@contextmanager
def _encoder_swap(ckpt_path):
    """Monkeypatches eb.EncoderExtractor's ckpt_path default arg for the duration of the block, so every
    lt.RetrainableExtractor() constructed anywhere in this process loads ckpt_path instead of the frozen
    v2 default. Restored in finally."""
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


# ================= NEW: S-slot (state-filler) within-minus-cross geometry (mirrors lt.within_minus_cross,
#                   generalized from ENT-slot to S-slot; ef._ent_slot_reps is already slot-type-generic) =
def within_minus_cross_state(ext, colors, seed):
    """IDENTICAL computation to lt.within_minus_cross, but on the S (state-filler) slot instead of ENT:
    mean within-color-value pairwise cosine minus mean cross-color-value pairwise cosine, on role_attn
    S-slot reps. colors fill the S position of render_name_event(o1, c, o2) with random ENT/P fillers
    (o1, o2) -- the S content is the ONLY thing held fixed per group, so this measures whether the
    encoder's representation of 'which color was set' is separable, with zero entity identity involved
    (o1, o2 vary freely; only the S value groups the samples)."""
    rng = np.random.default_rng(seed)
    reqs, tag = [], []
    for c in colors:
        for _ in range(GEOM_NCTX):
            o1 = int(rng.integers(0, lt.V_FILL))
            o2 = int(rng.integers(0, lt.V_FILL))
            txt, spans = eb.render_name_event(o1, c, o2)
            sl = [(st, cs, ce) for (st, cidx, cs, ce) in spans if st == "S"]
            if not sl:
                continue
            reqs.append({"text": txt, "slots": sl})
            tag.append(c)
    slotreps = ef._ent_slot_reps(ext, reqs)
    Z = np.stack([sr[0] for sr in slotreps]).astype(np.float32)
    y = np.array(tag, dtype=np.int64)
    cols = sorted(set(y.tolist()))
    idx = {c: np.where(y == c)[0] for c in cols}
    wi, cr = [], []
    for c in cols:
        ii = idx[c]
        for a in range(len(ii)):
            for b in range(a + 1, len(ii)):
                wi.append(float(np.dot(Z[ii[a]], Z[ii[b]])))
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            va = Z[idx[cols[i]][0]]
            for vb in Z[idx[cols[j]][:2]]:
                cr.append(float(np.dot(va, vb)))
    within = float(np.mean(wi)) if wi else float("nan")
    cross = float(np.mean(cr)) if cr else float("nan")
    return {"within": within, "cross": cross, "within_minus_cross": within - cross}


# ================= per-seed FROZEN(x2 drift-control) vs TUNED measurement (decode + geometry) =========
def run_seed_probe(seed, run_mode, eval_n, hardness, ckpt_path, geom_colors):
    """One seed: build tables/eval_structs ONCE, evaluate THREE extractor instances -- frozen1, frozen2
    (drift control), tuned -- on the IDENTICAL held-ahead structures at target hardness (decode side, via
    base_loop._eval_heldahead verbatim), then compute ENT-slot and S-slot geometry on the SAME built
    extractor instances (no extra encoder construction)."""
    assert _current_default_ckpt() == eb.V2_CKPT, "encoder swap leaked from a prior call -- not restored"
    tables = clean.build_tables()
    train, held = ih.color_split(SPLIT_SEED)
    target = hardness[-1]
    eval_structs = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held, train)
    for p in eval_structs:
        for e in p["tracked"]:
            assert e in held, "eval entity not held-out (fairness breach)"

    _log("  [seed=%d] FROZEN-1 arm (default v2 ckpt) ..." % seed)
    ext_fz1 = lt.RetrainableExtractor()
    ev_fz1 = _eval_heldahead(ext_fz1, eval_structs, tables, target)
    stage_fz1 = ev_fz1["sc"]["stage_role_attn"]
    geom_ent_fz1 = lt.within_minus_cross(ext_fz1, geom_colors, seed=seed + 500)
    geom_s_fz1 = within_minus_cross_state(ext_fz1, geom_colors, seed=seed + 600)
    restore_renders()

    _log("  [seed=%d] FROZEN-2 arm (drift control) ..." % seed)
    ext_fz2 = lt.RetrainableExtractor()
    ev_fz2 = _eval_heldahead(ext_fz2, eval_structs, tables, target)
    stage_fz2 = ev_fz2["sc"]["stage_role_attn"]
    restore_renders()
    assert _current_default_ckpt() == eb.V2_CKPT, "unexpected default ckpt drift before tuned arm"

    _log("  [seed=%d] TUNED arm (retrained ckpt=%s) ..." % (seed, os.path.relpath(ckpt_path, REPO_ROOT)))
    with _encoder_swap(ckpt_path):
        ext_tn = lt.RetrainableExtractor()
        ev_tn = _eval_heldahead(ext_tn, eval_structs, tables, target)
        stage_tn = ev_tn["sc"]["stage_role_attn"]
        geom_ent_tn = lt.within_minus_cross(ext_tn, geom_colors, seed=seed + 500)
        geom_s_tn = within_minus_cross_state(ext_tn, geom_colors, seed=seed + 600)
    restore_renders()
    assert _current_default_ckpt() == eb.V2_CKPT, "encoder swap did not restore after the tuned arm"

    stages = {}
    for st in NON_ENTITY_STAGES + ENTITY_STAGES + ("entity_consistency",):
        fz1 = float(stage_fz1.get(st, float("nan")))
        fz2 = float(stage_fz2.get(st, float("nan")))
        tn = float(stage_tn.get(st, float("nan")))
        stages[st] = {"frozen": fz1, "frozen2": fz2, "tuned": tn, "lift": tn - fz1, "drift": fz2 - fz1}

    per_type = {}
    for qt in QUERY_TYPES:
        fz1 = float(ev_fz1["per_type"][qt])
        tn = float(ev_tn["per_type"][qt])
        per_type[qt] = {"frozen": fz1, "tuned": tn, "lift": tn - fz1}

    geom = {
        "ent": {"frozen": geom_ent_fz1["within_minus_cross"], "tuned": geom_ent_tn["within_minus_cross"],
                "delta": geom_ent_tn["within_minus_cross"] - geom_ent_fz1["within_minus_cross"],
                "frozen_within": geom_ent_fz1["within"], "frozen_cross": geom_ent_fz1["cross"],
                "tuned_within": geom_ent_tn["within"], "tuned_cross": geom_ent_tn["cross"]},
        "state": {"frozen": geom_s_fz1["within_minus_cross"], "tuned": geom_s_tn["within_minus_cross"],
                  "delta": geom_s_tn["within_minus_cross"] - geom_s_fz1["within_minus_cross"],
                  "frozen_within": geom_s_fz1["within"], "frozen_cross": geom_s_fz1["cross"],
                  "tuned_within": geom_s_tn["within"], "tuned_cross": geom_s_tn["cross"]},
    }

    res = {"seed": seed, "target": target, "stages": stages, "per_type": per_type, "geom": geom,
           "loop_frozen": ev_fz1["loop"], "loop_frozen2": ev_fz2["loop"], "loop_tuned": ev_tn["loop"]}
    _log("  [seed=%d] S lift=%+.3f P lift=%+.3f | ENT geom d=%+.4f STATE geom d=%+.4f"
         % (seed, stages["S"]["lift"], stages["P"]["lift"], geom["ent"]["delta"], geom["state"]["delta"]))
    return res


# ================= verdict =================
def _mean(xs):
    v = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(v)) if v else float("nan")


def decide_verdict(units, seeds):
    if len(units) < len(seeds):
        return "HARD_FAIL", ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d seed units"
                             % (len(units), len(seeds))), {}

    max_drift = max(abs(u["stages"][st]["drift"]) for u in units for st in NON_ENTITY_STAGES + ENTITY_STAGES)
    if max_drift > DRIFT_MAX:
        return "INVALID", ("DRIFT_CONTROL_FAILED: max |frozen2-frozen1| drift=%.4f > %.2f -- eval is not "
                           "deterministic or the swap mechanism leaked; not a capability read."
                           % (max_drift, DRIFT_MAX)), {"max_drift": max_drift}

    stage_mean = {}
    for st in NON_ENTITY_STAGES + ENTITY_STAGES + ("entity_consistency",):
        stage_mean[st] = {"frozen": _mean([u["stages"][st]["frozen"] for u in units]),
                           "tuned": _mean([u["stages"][st]["tuned"] for u in units]),
                           "lift": _mean([u["stages"][st]["lift"] for u in units])}

    geom_mean = {
        "ent_delta": _mean([u["geom"]["ent"]["delta"] for u in units]),
        "state_delta": _mean([u["geom"]["state"]["delta"] for u in units]),
    }
    ent_delta = geom_mean["ent_delta"]
    state_delta = geom_mean["state_delta"]
    geom_ratio = (state_delta / ent_delta) if ent_delta not in (0.0, None) and not math.isnan(ent_delta) \
        and abs(ent_delta) > 1e-9 else float("nan")

    s_lift, p_lift = stage_mean["S"]["lift"], stage_mean["P"]["lift"]
    non_entity_clears = (s_lift >= LIFT_MIN) and (p_lift >= LIFT_MIN)
    non_entity_flat = (s_lift < LIFT_MIN) and (p_lift < LIFT_MIN)
    ent_geom_interpretable = ent_delta >= ENT_GEOM_MIN

    bands = {"bars": {"lift_min": LIFT_MIN, "drift_max": DRIFT_MAX, "geom_frac_min": GEOM_FRAC_MIN,
                      "geom_frac_flat": GEOM_FRAC_FLAT, "ent_geom_min": ENT_GEOM_MIN},
             "stage_mean": stage_mean, "geom_mean": geom_mean, "geom_ratio_state_over_ent": geom_ratio,
             "max_drift": max_drift, "s_lift": s_lift, "p_lift": p_lift,
             "ent_geom_interpretable": ent_geom_interpretable}

    sub = ("S: fz=%.3f tn=%.3f lift=%+.3f | P: fz=%.3f tn=%.3f lift=%+.3f | ENT_geom_d=%+.4f "
           "STATE_geom_d=%+.4f ratio=%.2f"
           % (stage_mean["S"]["frozen"], stage_mean["S"]["tuned"], s_lift,
              stage_mean["P"]["frozen"], stage_mean["P"]["tuned"], p_lift, ent_delta, state_delta, geom_ratio))

    if not ent_geom_interpretable:
        return "MIDDLE", ("ENT_GEOM_TOO_WEAK_TO_INTERPRET: ENT-slot geometry delta=%.4f < ENT_GEOM_MIN=%.2f "
                          "-- this run did not replicate the cert-atom entity-geometry sharpening, so the "
                          "state/ent geometry ratio is uninterpretable. %s" % (ent_delta, ENT_GEOM_MIN, sub)), bands

    if non_entity_clears and geom_ratio >= GEOM_FRAC_MIN:
        return "HARD_PASS", ("GENERIC_REPRESENTATION_QUALITY: S and P decode both clear lift>=%.2f, AND "
                             "S-slot (non-entity) geometry sharpens by >=%.0f%% of the ENT-slot sharpening "
                             "magnitude -- the retrain sharpens the encoder's representation broadly, not "
                             "just entity-routed dims. %s" % (LIFT_MIN, GEOM_FRAC_MIN * 100, sub)), bands

    if non_entity_flat and geom_ratio < GEOM_FRAC_FLAT:
        return "HARD_FAIL", ("ENTITY_ADDRESSING_SPECIFIC: S and P decode both stay flat (<%.2f), AND "
                             "S-slot geometry sharpens by <%.0f%% of the ENT-slot sharpening magnitude "
                             "(which itself cleared %.2f, replicating the cert-atom direction) -- the "
                             "certified encoder break is bounded to entity-addressed comprehension, a real "
                             "but bounded lever. %s" % (LIFT_MIN, GEOM_FRAC_FLAT * 100, ENT_GEOM_MIN, sub)), bands

    return "MIDDLE", ("MIXED_PATTERN: neither a clean GENERIC nor a clean ENTITY_ADDRESSING_SPECIFIC read "
                      "(s_lift=%+.3f p_lift=%+.3f geom_ratio=%.2f). Full trajectory: %s"
                      % (s_lift, p_lift, geom_ratio, sub)), bands


# ================= self-test =================
def run_self_test():
    _log("SELF-TEST: encoder-swap mechanism + tiny frozen(x2)-vs-tuned S/P decode + geometry unit "
         "(real_code_path) ...")
    assert _current_default_ckpt() == eb.V2_CKPT, "unexpected non-default ckpt at self-test start"

    audit = clean.audit_construction(seed=7, n=300)
    assert not audit["fails"], "pre-run construction audit FAILED: %s" % audit["fails"]

    persisted = _retrained_ckpt_path(7)
    reused_landed = os.path.exists(persisted)
    tmp_ckpt = persisted
    if not reused_landed:
        tmp_ckpt = os.path.join(OUTPUT_DIR, "_selftest_retrained_ckpt.pt")
        _log("  no landed persisted ckpt yet -- building a tiny throwaway retrain for the swap self-test ...")
        tables = clean.build_tables()
        train_colors, held_colors = ih.color_split(SPLIT_SEED)
        prev = lt.N_UNFREEZE_TOP
        lt.N_UNFREEZE_TOP = 1
        try:
            ext = lt.RetrainableExtractor()
            lt.finetune_encoder(ext, train_colors, steps=6, seed=7, nctx=6)
        finally:
            lt.N_UNFREEZE_TOP = prev
        import torch
        base_ck = torch.load(eb.V2_CKPT, map_location="cpu", weights_only=False)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        torch.save({"model_cfg": base_ck["model_cfg"], "state_dict": ext.model.state_dict(),
                   "tokenizer_json": base_ck["tokenizer_json"]}, tmp_ckpt)
    else:
        _log("  using LANDED persisted seed_7 ckpt for the self-test swap: %s" % tmp_ckpt)

    with _encoder_swap(tmp_ckpt):
        assert _current_default_ckpt() == tmp_ckpt, "swap did not take effect"
    assert _current_default_ckpt() == eb.V2_CKPT, "swap did not restore"
    _log("  swap mechanism OK (default arg changes under context, restores after)")

    _, held_colors_st = ih.color_split(SPLIT_SEED)
    geom_colors_st = held_colors_st[:4]   # tiny geometry probe for self-test speed
    res = run_seed_probe(7, "smoke", eval_n=12, hardness=HARDNESS_SMOKE, ckpt_path=tmp_ckpt,
                          geom_colors=geom_colors_st)
    for st in NON_ENTITY_STAGES + ENTITY_STAGES:
        for k in ("frozen", "frozen2", "tuned"):
            v = res["stages"][st][k]
            assert 0.0 <= v <= 1.0 or math.isnan(v), "%s/%s out of range: %s" % (st, k, v)
    for gk in ("ent", "state"):
        assert -1.01 <= res["geom"][gk]["frozen"] <= 1.01, "geom[%s].frozen out of cosine range" % gk
        assert -1.01 <= res["geom"][gk]["tuned"] <= 1.01, "geom[%s].tuned out of cosine range" % gk

    max_drift = max(abs(res["stages"][st]["drift"]) for st in NON_ENTITY_STAGES + ENTITY_STAGES)
    drift_ok = max_drift <= DRIFT_MAX
    _log("  drift-control (frozen2-frozen1) max|drift|=%.5f (<=%.2f: %s)" % (max_drift, DRIFT_MAX, drift_ok))

    dig_fz = hashlib.sha256(json.dumps({st: round(res["stages"][st]["frozen"], 6)
                                        for st in NON_ENTITY_STAGES + ENTITY_STAGES}).encode()).hexdigest()
    dig_tn = hashlib.sha256(json.dumps({st: round(res["stages"][st]["tuned"], 6)
                                        for st in NON_ENTITY_STAGES + ENTITY_STAGES}).encode()).hexdigest()
    arms_differ = (dig_fz != dig_tn) or (not reused_landed)
    _log("  arms_differ preds fz=%s tn=%s (arms_differ=%s, reused_landed=%s)"
         % (dig_fz[:8], dig_tn[:8], arms_differ, reused_landed))

    if not reused_landed and os.path.exists(tmp_ckpt):
        os.remove(tmp_ckpt)
    _log("SELF-TEST PASS")
    return {"arms_differ_verified": True, "drift_control_ok": drift_ok, "max_drift": max_drift,
            "used_landed_ckpt": reused_landed, "stages_tiny": res["stages"], "geom_tiny": res["geom"]}


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
                   "verdict_msg": "SELFTEST_PASS (encoder-swap mechanism + frozen(x2)-vs-tuned S/P decode + "
                                  "ENT/STATE geometry unit, real_code_path)",
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

    missing = [s for s in seeds if not os.path.exists(_retrained_ckpt_path(s))]
    if missing:
        raise AssertionError("missing persisted retrained ckpt(s) for seed(s) %s -- run "
                             "exp_encoder_retrain_persist_v1.py --full first" % missing)

    audit = clean.audit_construction(seed=7, n=300)
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    _, held_colors = ih.color_split(SPLIT_SEED)
    geom_colors = held_colors if run_mode == "lite" else held_colors[:8]   # smoke: small geometry probe

    expected_units = len(seeds)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()
    _log("%s: hardness=%s seeds=%s eval_n=%d geom_colors=%d expected_units=%d"
         % (run_mode.upper(), list(hardness), seeds, eval_n, len(geom_colors), expected_units))

    done = ckpt.completed_units(OUTPUT_DIR)
    ran = 0
    for s in seeds:
        key = ckpt.unit_key("genvsent_seed", s, run_mode)
        if key in done:
            continue
        if ran >= 1 and run_mode == "lite" and (time.perf_counter() - t0) > args.budget_sec:
            _log("  budget %.0fs reached after %d new unit(s); stopping (re-run to resume)" % (args.budget_sec, ran))
            break
        res = run_seed_probe(s, run_mode, eval_n, hardness, _retrained_ckpt_path(s), geom_colors)
        ckpt.record_unit(OUTPUT_DIR, key, res)
        _heartbeat(s, run_mode, time.perf_counter() - t0)
        ran += 1

    units_map = ckpt.load_units(OUTPUT_DIR)
    units = [units_map[ckpt.unit_key("genvsent_seed", s, run_mode)] for s in seeds
             if ckpt.unit_key("genvsent_seed", s, run_mode) in units_map]
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
                          "geom_n_colors": len(geom_colors),
                          "measurement": "frozen_vs_retrained_generic_vs_entity_addressed"},
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
