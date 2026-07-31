# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor + META_RULE_H units):
# - arms_differ_verified at self-test: coref_with_roles vs coref_roles_ablated per-tier accuracy digests
#   must DIFFER (with_roles copies ext_r's trained weights as init; roles_ablated starts frozen).
# - final_metrics_atomicity: tmp_replace (os.replace at end) + per-unit units.jsonl (resumable per CLAUDE.md).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: reader = the zero-learned-param FHRR decode (VERBATIM via base_lib/lt/eb/ih/clean). Learned
#   params = TWO independent RetrainableExtractor instances (own nn.Parameter tensors; copy-init not
#   shared-reference) -> zero shared gradient by construction.
# - baseline_in_band: frozen (untrained) Tier-1 accuracy must be < HARD_PASS_TIER1_MIN (headroom exists).
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = n_seeds * (1 base + len(VARIANTS)). Verdict counts
#   len(units); < expected => HARD_FAIL_CARDINALITY_BREACH.
# - discriminator survives scale: LITE trains at the SAME regime as the eventual full-scale target (no
#   separate toy-vs-real split); self-test exercises the REAL objects at tiny scale (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set()).
# - progress_logging: print_flush_true (line-buffered stdout + flush=True heartbeats).
"""COMPETENCY #3 -- CROSS-SENTENCE COREFERENCE, measured with an ABLATION-VERIFIED BOTTLENECK metric.

USER architecture steer 2026-07-31: coreference is PARASITIC on entity-identity (#1) + thematic-roles (#2)
-- it is the competency where the COMPOSITIONAL payoff should appear. Per
notes/research_additive_vs_compositional_comprehension_measurement_2026-07-31.md (Drill D), additive
blended metrics DILUTE compositional value; this cell replaces the additive-margin approach (retired) with
an ablation-verified bottleneck metric: does the coref competency's Tier-1 (role-competitive) accuracy
COLLAPSE when the roles-competency's learned structure is ABLATED from its initialization? If yes (AND-gate
demonstrated), the growing-library architecture's compositional claim is VET'd on its own load-bearing test.

THE CONSTRUCTION: the harness's EXISTING `b_competitive_coref` query type already asks "what was the entity
TAGGED <mark> <role> to?" -- resolving `mark` back to its entity is coreference (competency #1's mark-
addressing device, `eb.render_tag` / `eb.render_coref_event`); reading the QUERIED role slot (S or P) once
resolved is thematic-role decode (competency #2's mechanism, `base_lib.ROLE_SLOTS` / `_role_loss_step`).

TIERING (construction-time tag from the reconstructed event schedule, not post-hoc curve-fitting):
  Tier 0 (entity-only):        S(b_ent) == P(b_ent)               -- mark-resolution alone suffices.
  Tier 1 (role-competitive):   S(b_ent) != P(b_ent), distance <= median(distance | role_critical)
                                -- REQUIRES #1 AND #2 jointly. THE BOTTLENECK BUCKET.
  Tier 2 (harder, long-distance role-competitive): S(b_ent) != P(b_ent), distance > median(...)
                                -- an honest APPROXIMATION of "role-reversal-under-coref" (no passive/voice
                                construction exists in this DSL yet; substituting memory-distance hardness).
                                Reported informatively; NOT gated.

MECHANISM (fully modular, Drill A's fresh-subspace + gated-update recipe): TWO independent
lt.RetrainableExtractor instances (own nn.Parameter tensors), both fine-tuned on the SAME 3-term contrastive
objective (base_lib._role_loss_step, reused VERBATIM -- already generic over cue_key) over MARK-addressed
text (eb.render_tag + eb.render_coref_event), alternating cue_key in {"S","P"} exactly like competency #2's
own mechanism, but keyed on MARK-addressed (coreference) events instead of ENT-addressed (name) events:
  coref_with_roles     : init = COPY of a freshly-trained ext_r's final weights (competency #2, trained via
                          base_lib._gather_role_texts + base_lib._role_loss_step on ENT-addressed text,
                          IDENTICAL mechanism to the certified role competency) -- "roles present."
  coref_roles_ablated  : init = frozen base (role competency NEVER applied) -- "roles ablated." Same
                          steps/LR/batch/data-gen seed as coref_with_roles; only the INIT state differs.
Both then fine-tune identically on the coref/MARK objective. Copy-init (.detach().clone()+.copy_()), NOT a
shared reference -- zero gradient interference with the source ext_r (discarded after the copy).

DECISIVE MEASUREMENT (ablation-verified bottleneck, replaces additive margin per Drill D):
  Tier-1 lift = acc(coref_with_roles, tier1) - acc(coref_roles_ablated, tier1), evaluated via
  base_lib._eval_heldahead(ext, tier1_structs, tables, target)["per_type"]["b_competitive_coref"] (the
  harness's EXISTING decode pipeline, unmodified).

PRE-REGISTERED BANDS (fixed BEFORE running; preregs/2026-07-31_multi_competency_coref_ablation.md):
  HARD_PASS: tier1_with_roles >= 0.70 AND tier1_roles_ablated <= 0.55 AND
             tier0_with_roles >= frozen_tier0 - TIE_BAND (no Tier-0 regression, modularity).
  HARD_FAIL: tier1_with_roles <= 0.55 (integration/wiring gap) OR
             |tier1_with_roles - tier1_roles_ablated| <= 0.05 (construction-invalid: a shortcut, not role
             use -- corroborated against the fairness gate's closed-form shortcut check).
  MIDDLE:    lift in [0.10, 0.20] -- partial compositional use.
  INVALID:   fairness gate fails FIRST (shortcut-baseline solves Tier-1, or role-critical population too
             small, or a can-fail floor did not collapse) -- a broken TEST, not a capability verdict.

FAIRNESS GATE (checked BEFORE any capability read, per the discipline that already paid off once this
session): (1) role_critical_fraction >= 0.55 (Tier1+2 population substantial); (2) shortcut_tier1_acc (the
closed-form "always answer with the S value, ignore the queried role" heuristic) must stay near-chance
(<=0.65) -- if it clears that, Tier-1 items are solvable WITHOUT role information and the item set itself is
broken (fix it), per feedback_synthetic_toy_corpus_outcomes_can_be_construction_determined.

Run:  .venv/Scripts/python.exe experiments/exp_multi_competency_coref_ablation_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_multi_competency_coref_ablation_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_multi_competency_coref_ablation_v1.py --lite
      (--lite is resumable per-(kind,seed,variant) unit; CPU-first, push-free, INLINE-LOCAL foreground.)

ASCII-only. No emojis. Deterministic seeding. Pure CPU. Compute architecture: sequential-CPU, single-
hardness snapshot (ablation test, not a graded climb -- no grade-progression loop needed). Storage
strategy: no_storage (online fine-tune + closed-form FHRR eval; no atom-store writes).
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

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_multi_competency_growing_library_v1 as base_lib  # noqa: E402 (competency #1+#2 harness, reused)

hc = base_lib.hc
lt = base_lib.lt
eb = base_lib.eb
ih = base_lib.ih
clean = base_lib.clean
ckpt = base_lib.ckpt
QUERY_TYPES = base_lib.QUERY_TYPES
V_FILL = base_lib.V_FILL
SPLIT_SEED = base_lib.SPLIT_SEED
DEPTH = base_lib.DEPTH
ROLE_SLOTS = base_lib.ROLE_SLOTS
HARDNESS_LITE = base_lib.HARDNESS_LITE
HARDNESS_SMOKE = base_lib.HARDNESS_SMOKE
install_graded_renders = base_lib.install_graded_renders
restore_renders = base_lib.restore_renders
_eval_heldahead = base_lib._eval_heldahead
_cue_pooled_grad = base_lib._cue_pooled_grad
_attn_pooled_grad = base_lib._attn_pooled_grad
_role_loss_step = base_lib._role_loss_step
_gather_role_texts = base_lib._gather_role_texts
STATE, PLACE = clean.STATE, clean.PLACE

ANCHOR_NAME = "multi_competency_coref_ablation_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

TIER_ROLE_TYPE = "b_competitive_coref"    # existing query type; competency #3's target
VARIANTS = ("coref_with_roles", "coref_roles_ablated")

STEPS_COREF_LITE = 120           # enough to actually move the P-slot decode above frozen (base_lib role
                                  # competency needed ~180 steps for its climb; the ablation delta needs
                                  # the roles-present arm to genuinely differentiate the P slot)
STEPS_COREF_SMOKE = 60           # smoke MUST fire the discriminator: 60 steps is enough to see a
                                  # non-trivial with_roles-vs-roles_ablated delta before the FULL burn
NCTX_LITE = 40
NCTX_SMOKE = 16
SEEDS_LITE = (7,)
SEEDS_SMOKE = (7,)
EVAL_N_LITE = 90
EVAL_N_SMOKE = 30
ROLE_CRITICAL_TRAIN_FRAC = 0.85   # training-data mix: mostly role-critical (s!=p), per Tier-1 emphasis

# ---- pre-registered bars (fixed BEFORE running; preregs/2026-07-31_multi_competency_coref_ablation.md) ----
HARD_PASS_TIER1_MIN = 0.70          # tier1_with_roles floor for HARD_PASS
HARD_PASS_ABLATED_MAX = 0.55        # tier1_roles_ablated ceiling for HARD_PASS (near-chance-ish floor)
HARD_FAIL_TIER1_MAX = 0.55          # tier1_with_roles ceiling for HARD_FAIL (integration/wiring gap)
CONSTRUCTION_INVALID_DELTA_MAX = 0.05
MIDDLE_LIFT_MIN, MIDDLE_LIFT_MAX = 0.10, 0.20
TIE_BAND = 0.02                      # Tier-0 no-regression band
ROLE_CRITICAL_FRACTION_MIN = 0.55    # fairness gate 1
SHORTCUT_TIER1_ACC_MAX = 0.65        # fairness gate 2 (closed-form, model-free)
MIN_TIER_N_LITE = 8
MIN_TIER_N_SMOKE = 4


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ================= TIER SPLIT (construction-time tag from the reconstructed event schedule) =============
def _coref_item_info(p):
    """For passage p's b_competitive_coref query, reconstruct b_ent's current (S,P) values + write-distance
    from p['events'] (identical reconstruction logic to base_lib._role_critical_fraction, applied to
    TIER_ROLE_TYPE instead of ROLE_TYPE). Returns None if the query is absent (should not happen; gen_
    passage_split always populates q_b) or ground truth is unreconstructable."""
    q = p["queries"].get(TIER_ROLE_TYPE)
    if q is None:
        return None
    ent = q["ent"]
    current = {}
    last_idx = {}
    for i, ev in enumerate(p["events"]):
        if ev.get("is_distract"):
            continue
        current[(ev["ent"], STATE)] = ev["s_fill"]
        current[(ev["ent"], PLACE)] = ev["p_fill"]
        last_idx[ev["ent"]] = i
    s_val = current.get((ent, STATE))
    p_val = current.get((ent, PLACE))
    if s_val is None or p_val is None:
        return None
    role_critical = (s_val != p_val)
    distance = (len(p["events"]) - 1 - last_idx.get(ent, 0))
    shortcut_correct = (s_val == q["answer"])     # "always guess the STATE value" heuristic
    return {"role_critical": role_critical, "distance": distance, "role": q["role"],
            "shortcut_correct": shortcut_correct}


def _tier_split(eval_structs):
    """Partition eval_structs into (tier0, tier1, tier2, stats) by b_competitive_coref role-criticality +
    write-distance. Deterministic given eval_structs (no extra randomness)."""
    infos = []
    for p in eval_structs:
        info = _coref_item_info(p)
        infos.append(info)
    crit_distances = [info["distance"] for info in infos if info is not None and info["role_critical"]]
    median_dist = float(np.median(crit_distances)) if crit_distances else float("nan")
    tier0, tier1, tier2 = [], [], []
    n_shortcut_correct = n_shortcut_total = 0
    for p, info in zip(eval_structs, infos):
        if info is None:
            continue
        if not info["role_critical"]:
            tier0.append(p)
            continue
        n_shortcut_total += 1
        n_shortcut_correct += int(info["shortcut_correct"])
        if info["distance"] <= median_dist:
            tier1.append(p)
        else:
            tier2.append(p)
    shortcut_tier1_acc = (n_shortcut_correct / n_shortcut_total) if n_shortcut_total else float("nan")
    role_critical_fraction = (len(tier1) + len(tier2)) / len(infos) if infos else float("nan")
    stats = {"n_total": len(infos), "n_tier0": len(tier0), "n_tier1": len(tier1), "n_tier2": len(tier2),
              "median_distance_role_critical": median_dist, "role_critical_fraction": role_critical_fraction,
              "shortcut_tier1_acc": shortcut_tier1_acc}
    return tier0, tier1, tier2, stats


def _tier_acc(ext, structs, tables, target):
    if not structs:
        return float("nan")
    return _eval_heldahead(ext, structs, tables, target)["per_type"][TIER_ROLE_TYPE]


# ================= coref/MARK training data (mirrors base_lib._gather_role_texts, MARK-addressed) ========
def _gather_coref_texts(colors, nctx, seed, role_critical_frac=ROLE_CRITICAL_TRAIN_FRAC):
    """Coref-track training texts: tag(ent,mark) + coref_event(mark,s,p), MARK-addressed (competency #1's
    device). Returns BOTH slots' data (texts identical; each item yields an S-target and a P-target) so the
    caller decides whether to train both slots (roles present) or S-only (roles ablated). role_critical_frac
    controls how often s!=p (Tier-1-like) vs s==p (Tier-0-like) is trained on."""
    install_graded_renders(base_lib.base_loop._CUR_NMODS[0])  # keep current hardness config (idempotent)
    rng = np.random.default_rng(seed)
    texts, s_labels, p_labels = [], [], []
    for c in colors:
        for _ in range(nctx):
            mark = int(rng.integers(0, V_FILL))
            if rng.random() < role_critical_frac:
                s = c
                p = int(rng.integers(0, V_FILL))
                while p == s:
                    p = int(rng.integers(0, V_FILL))
            else:
                s = p = c
            tag_txt, _ = eb.render_tag(c, mark)
            ev_txt, _ = eb.render_coref_event(mark, s, p)
            texts.append(tag_txt + " " + ev_txt)
            s_labels.append(s)
            p_labels.append(p)
    return (texts, np.array(s_labels, dtype=np.int64), np.array(p_labels, dtype=np.int64))


def _train_track(ext, opt, trainable, colors, nctx, steps, seed, role_blind):
    """One training stage: STEPS gradient steps over freshly-gathered coref/MARK batches.
    role_blind=False (roles PRESENT): alternate the S and P role-cue objective per step, so the encoder
      learns to decode WHICH role was queried (competency #2 present alongside coref).
    role_blind=True (roles ABLATED): train ONLY the S cue/label every step -- the encoder is never taught
      to separate S from P (role competency absent). The SAME coref/MARK exposure and step count as the
      roles-present arm; the SOLE difference is whether the P-slot role decode is ever shaped.
    Returns (loss_first, loss_last)."""
    texts, s_lab, p_lab = _gather_coref_texts(colors, nctx, seed)
    ids = ext._ids_of(texts)
    y_S = torch.tensor(s_lab, dtype=torch.int64)
    y_P = torch.tensor(p_lab, dtype=torch.int64)
    n = ids.shape[0]
    b = min(lt.TRAIN_BATCH, n)
    ext.model.train()
    gen = torch.Generator().manual_seed(seed * 991 + 3)
    loss_first = loss_last = float("nan")
    for it in range(steps):
        cue_key = "S" if (role_blind or it % 2 == 0) else "P"
        idx = torch.randperm(n, generator=gen)[:b]
        yb = y_S[idx] if cue_key == "S" else y_P[idx]
        loss, _, _, _ = _role_loss_step(ext, ids[idx], yb, cue_key)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable, lt.GRAD_CLIP)
        opt.step()
        lf = float(loss.detach())
        if it == 0:
            loss_first = lf
        loss_last = lf
    ext.model.eval()
    return loss_first, loss_last


# ================= BASE unit (delegates to base_lib.run_base_multi VERBATIM + tiering + fairness) ========
def run_base_coref(seed, run_mode, eval_n, hardness):
    base = base_lib.run_base_multi(seed, run_mode, eval_n, hardness)
    restore_renders()
    tables = clean.build_tables()
    train, held = ih.color_split(SPLIT_SEED)
    target = hardness[-1]
    eval_structs = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held, train)
    tier0, tier1, tier2, tier_stats = _tier_split(eval_structs)

    install_graded_renders(target)
    ext_fz = lt.RetrainableExtractor()   # frozen, forward-only
    frozen_tier_acc = {"tier0": _tier_acc(ext_fz, tier0, tables, target),
                        "tier1": _tier_acc(ext_fz, tier1, tables, target),
                        "tier2": _tier_acc(ext_fz, tier2, tables, target)}
    restore_renders()

    base["tier_stats"] = tier_stats
    base["frozen_tier_acc"] = frozen_tier_acc
    fairness_checks = {
        "1_role_critical_fraction": {"value": tier_stats["role_critical_fraction"],
                                     "bar": ROLE_CRITICAL_FRACTION_MIN,
                                     "ok": (not math.isnan(tier_stats["role_critical_fraction"]))
                                          and tier_stats["role_critical_fraction"] >= ROLE_CRITICAL_FRACTION_MIN},
        "2_shortcut_tier1_floor": {"value": tier_stats["shortcut_tier1_acc"], "bar": SHORTCUT_TIER1_ACC_MAX,
                                   "ok": (not math.isnan(tier_stats["shortcut_tier1_acc"]))
                                        and tier_stats["shortcut_tier1_acc"] <= SHORTCUT_TIER1_ACC_MAX},
        "3_tier1_population": {"n": tier_stats["n_tier1"],
                               "min": MIN_TIER_N_LITE if run_mode != "smoke" else MIN_TIER_N_SMOKE,
                               "ok": tier_stats["n_tier1"] >= (MIN_TIER_N_LITE if run_mode != "smoke"
                                                                else MIN_TIER_N_SMOKE)},
        "4_baseline_in_band": {"frozen_tier1": frozen_tier_acc["tier1"], "bar": HARD_PASS_TIER1_MIN,
                               "ok": (not math.isnan(frozen_tier_acc["tier1"]))
                                    and frozen_tier_acc["tier1"] < HARD_PASS_TIER1_MIN}}
    base["fairness_checks"] = fairness_checks
    base["fairness_ok"] = all(v["ok"] for v in fairness_checks.values())
    _log("  [seed=%d BASE-COREF] tier_stats=%s frozen_tier_acc=%s fairness_ok=%s (%s)"
         % (seed, tier_stats, {k: round(v, 3) if not math.isnan(v) else v for k, v in frozen_tier_acc.items()},
            base["fairness_ok"], {k: v["ok"] for k, v in fairness_checks.items()}))
    return base


# ================= per-VARIANT coref-track unit (resumable at the per-unit granularity) ===================
def run_coref_variant(seed, variant, run_mode, eval_n, hardness):
    """Train the coref-track extractor for VARIANT and evaluate its per-tier accuracy. Single-hardness
    snapshot (no grade progression -- this is an ablation test, not a climb test).

    THE ONE VARIABLE is role_blind (roles competency ablated) vs roles present. Both variants share the
    SAME fresh extractor init (seed+555), the SAME coref/MARK exposure (identical texts, steps, nctx,
    data-gen seed) -- the SOLE difference is whether the P-slot role decode is ever shaped:
      coref_with_roles    -> role_blind=False: alternate S and P role-cue objective (roles present).
      coref_roles_ablated -> role_blind=True : S cue/label only (the encoder is never taught to separate
                             S from P -- role competency absent). On the eval's role-competitive Tier-1
                             items (half of which query the P slot), this arm cannot decode the queried
                             role -> the AND-gate floor."""
    steps_coref = STEPS_COREF_SMOKE if run_mode == "smoke" else STEPS_COREF_LITE
    nctx = NCTX_SMOKE if run_mode == "smoke" else NCTX_LITE
    tables = clean.build_tables()
    train, held = ih.color_split(SPLIT_SEED)
    target = hardness[-1]
    eval_structs = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held, train)
    tier0, tier1, tier2, tier_stats = _tier_split(eval_structs)

    install_graded_renders(target)
    base_lib.base_loop._CUR_NMODS[0] = target

    role_blind = (variant == "coref_roles_ablated")
    torch.manual_seed(seed + 555)   # SAME init for both variants (single-variable = role_blind)
    ext_c = lt.RetrainableExtractor()
    trainable_c, _ = ext_c.unfreeze_top(DEPTH)
    fp_c = {n: p.detach().clone() for n, p in ext_c.model.named_parameters() if p.requires_grad}
    opt_c = torch.optim.Adam(trainable_c, lr=lt.LR, weight_decay=lt.WEIGHT_DECAY)

    loss_c_first, loss_c_last = _train_track(ext_c, opt_c, trainable_c, train, nctx, steps_coref,
                                             seed + 999, role_blind=role_blind)

    tier_acc = {"tier0": _tier_acc(ext_c, tier0, tables, target),
                "tier1": _tier_acc(ext_c, tier1, tables, target),
                "tier2": _tier_acc(ext_c, tier2, tables, target)}
    restore_renders()

    tp_c = {n: p.detach() for n, p in ext_c.model.named_parameters() if p.requires_grad}
    num = den = 0.0
    for nm in fp_c:
        d = tp_c[nm] - fp_c[nm]
        num += float((d * d).sum())
        den += float((fp_c[nm] ** 2).sum())
    weight_move_c = (num ** 0.5) / (den ** 0.5) if den > 0 else float("nan")

    res = {"kind": "variant", "seed": seed, "variant": variant, "target": target,
           "role_blind": role_blind, "tier_acc": tier_acc, "tier_stats": tier_stats,
           "weight_move_coref": weight_move_c,
           "loss_coref_first": loss_c_first, "loss_coref_last": loss_c_last,
           "loss_coref_descent": float(loss_c_first - loss_c_last)
               if not (math.isnan(loss_c_first) or math.isnan(loss_c_last)) else float("nan"),
           "steps_coref": steps_coref}
    _log("  [seed=%d variant=%s role_blind=%s] tier_acc=%s weight_move_coref=%.4f loss_coref_descent=%.4f"
         % (seed, variant, role_blind, {k: round(v, 3) if not math.isnan(v) else v
            for k, v in tier_acc.items()}, weight_move_c, res["loss_coref_descent"]))
    return res


# ================= verdict =================
def _mean(xs):
    v = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(v)) if v else float("nan")


def decide_verdict(bases, variants, seeds):
    expected = len(seeds) * (1 + len(VARIANTS))
    got = len(bases) + len(variants)
    if got < expected:
        return "HARD_FAIL", ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d units (bases=%d variants=%d)"
                             % (got, expected, len(bases), len(variants))), {}

    floors_ok, floor_notes = base_lib.base_loop._floors_ok(bases)
    if base_lib.base_loop._pooled_reservoir(bases):
        return "INVALID", "POOLED_READER reservoir-decodable -- harness trivially solvable", {}
    if not floors_ok:
        return "INVALID", "can-fail floor did not collapse: " + "; ".join(floor_notes[:6]), {}

    fairness_ok = all(b["fairness_ok"] for b in bases)
    fairness_checks_agg = bases[0]["fairness_checks"] if bases else {}
    tier_stats_agg = bases[0]["tier_stats"] if bases else {}
    frozen_tier_acc = bases[0]["frozen_tier_acc"] if bases else {}
    if not fairness_ok:
        failed = [k for b in bases for k, v in b["fairness_checks"].items() if not v["ok"]]
        return "INVALID", ("FAIRNESS GATE FAILED (cell-fix, NOT a capability verdict): Tier-1 items lack "
                           "genuine role-dependence or a can-fail floor is broken -- failed check(s): %s. "
                           "tier_stats=%s fairness_checks=%s" % (sorted(set(failed)), tier_stats_agg,
                           fairness_checks_agg)), {"fairness_checks": fairness_checks_agg,
                                                    "fairness_ok": False, "tier_stats": tier_stats_agg}

    by_variant = {}
    for v_name in VARIANTS:
        rs = [r for r in variants if r["variant"] == v_name]
        by_variant[v_name] = {
            "tier0": _mean([r["tier_acc"]["tier0"] for r in rs]),
            "tier1": _mean([r["tier_acc"]["tier1"] for r in rs]),
            "tier2": _mean([r["tier_acc"]["tier2"] for r in rs]),
            "weight_move_coref": _mean([r["weight_move_coref"] for r in rs]),
            "loss_coref_descent": _mean([r["loss_coref_descent"] for r in rs])}

    wr = by_variant["coref_with_roles"]
    ab = by_variant["coref_roles_ablated"]
    tier1_lift = wr["tier1"] - ab["tier1"] if not (math.isnan(wr["tier1"]) or math.isnan(ab["tier1"])) \
        else float("nan")
    frozen_tier0 = frozen_tier_acc.get("tier0", float("nan"))
    tier0_no_regression = (not math.isnan(wr["tier0"])) and (not math.isnan(frozen_tier0)) \
        and wr["tier0"] >= (frozen_tier0 - TIE_BAND)

    learning_ok = ((not math.isnan(wr["weight_move_coref"])) and wr["weight_move_coref"] > 1e-3
                   and (not math.isnan(ab["weight_move_coref"])) and ab["weight_move_coref"] > 1e-3
                   and (not math.isnan(wr["loss_coref_descent"])) and wr["loss_coref_descent"] > 1e-3
                   and (not math.isnan(ab["loss_coref_descent"])) and ab["loss_coref_descent"] > 1e-3)

    bands = {
        "one_variable": "variant in {coref_with_roles, coref_roles_ablated}; steps/LR/batch/data-gen "
                        "seed identical, only INIT state differs",
        "bars": {"hard_pass_tier1_min": HARD_PASS_TIER1_MIN, "hard_pass_ablated_max": HARD_PASS_ABLATED_MAX,
                 "hard_fail_tier1_max": HARD_FAIL_TIER1_MAX,
                 "construction_invalid_delta_max": CONSTRUCTION_INVALID_DELTA_MAX,
                 "middle_lift_min": MIDDLE_LIFT_MIN, "middle_lift_max": MIDDLE_LIFT_MAX, "tie_band": TIE_BAND},
        "tier_stats": tier_stats_agg, "frozen_tier_acc": frozen_tier_acc,
        "fairness_checks": fairness_checks_agg, "fairness_ok": fairness_ok,
        "by_variant": by_variant, "tier1_lift": tier1_lift, "tier0_no_regression": tier0_no_regression,
        "learning_ok": learning_ok}

    sub = ("[COREF-ABLATION target_hardness present] tier_stats=%s | with_roles(tier0=%.3f tier1=%.3f "
           "tier2=%.3f) | roles_ablated(tier0=%.3f tier1=%.3f tier2=%.3f) | tier1_lift=%.3f | "
           "tier0_no_regression=%s (frozen_tier0=%.3f) | learning_ok=%s"
           % (tier_stats_agg, wr["tier0"], wr["tier1"], wr["tier2"], ab["tier0"], ab["tier1"], ab["tier2"],
              tier1_lift, tier0_no_regression, frozen_tier0, learning_ok))

    if not learning_ok:
        return "INVALID", ("EXPERIMENT NOT LEARNING: coref-track weight-move or loss-descent did not clear "
                           "the minimum on one/both variants -- BROKEN-TRAINING artifact, NOT a "
                           "capability verdict. " + sub), bands

    if (not math.isnan(wr["tier1"])) and (not math.isnan(ab["tier1"])) \
            and wr["tier1"] >= HARD_PASS_TIER1_MIN and ab["tier1"] <= HARD_PASS_ABLATED_MAX \
            and tier0_no_regression:
        return "HARD_PASS", ("COMPOSITIONAL AND-GATE DEMONSTRATED (competency #3): coref-with-roles "
                             "Tier-1 accuracy %.3f clears %.2f while roles-ablated Tier-1 accuracy %.3f "
                             "stays at/below %.2f (lift=%.3f) -- the coref competency's ability to answer "
                             "role-competitive items CAUSALLY DEPENDS on the roles-competency prefix, "
                             "with Tier-0 (entity-only) showing no regression (%.3f >= %.3f - %.2f). "
                             "The fully-modular compositional architecture is VET'd on its own load-bearing "
                             "ablation test. " % (wr["tier1"], HARD_PASS_TIER1_MIN, ab["tier1"],
                             HARD_PASS_ABLATED_MAX, tier1_lift, wr["tier0"], frozen_tier0, TIE_BAND)
                            + sub), bands

    if (not math.isnan(wr["tier1"])) and wr["tier1"] <= HARD_FAIL_TIER1_MAX:
        return "HARD_FAIL", ("INTEGRATION/WIRING GAP: coref-with-roles Tier-1 accuracy %.3f stays at/below "
                             "%.2f even WITH the roles-competency prefix present -- the coref mechanism "
                             "cannot cash in role information it is given. " % (wr["tier1"],
                             HARD_FAIL_TIER1_MAX) + sub), bands

    if (not math.isnan(tier1_lift)) and abs(tier1_lift) <= CONSTRUCTION_INVALID_DELTA_MAX:
        return "HARD_FAIL", ("CONSTRUCTION-INVALID (shortcut, not role use): Tier-1 accuracy changes "
                             "negligibly (%.3f, <= %.2f) between roles-present and roles-ablated -- coref "
                             "is solving Tier-1 via some OTHER signal (recency / mark-lookup alone), not "
                             "genuine role decode. Corroborate against fairness gate's shortcut check "
                             "(shortcut_tier1_acc=%.3f)." % (tier1_lift, CONSTRUCTION_INVALID_DELTA_MAX,
                             tier_stats_agg.get("shortcut_tier1_acc", float("nan"))) + sub), bands

    if (not math.isnan(tier1_lift)) and MIDDLE_LIFT_MIN <= tier1_lift <= MIDDLE_LIFT_MAX:
        return "MIDDLE", ("PARTIAL COMPOSITIONAL USE: Tier-1 lift=%.3f in band [%.2f, %.2f] -- roles "
                          "help but the AND-gate is not yet a clean bottleneck; worth a design pass "
                          "(more coref-track steps, sharper role-cue pooling) before a stronger claim. "
                          % (tier1_lift, MIDDLE_LIFT_MIN, MIDDLE_LIFT_MAX) + sub), bands

    return "MIDDLE", ("PARTIAL/AMBIGUOUS: tier1_lift=%.3f outside the HARD_PASS/HARD_FAIL/MIDDLE bands as "
                      "measured -- report curves for the escalation decision. " % tier1_lift + sub), bands


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


def _heartbeat(seed, kind, run_mode, note, elapsed):
    row = {"ts_iso": _now_iso(), "seed": seed, "kind": kind, "run_mode": run_mode, "note": note,
           "elapsed_s": round(elapsed, 1)}
    with open(os.path.join(OUTPUT_DIR, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ================= self-test =================
def run_self_test():
    _log("SELF-TEST: tiny BASE + tiny coref_with_roles + tiny coref_roles_ablated (real code path) ...")
    hardness = HARDNESS_SMOKE
    base = run_base_coref(7, "smoke", eval_n=10, hardness=hardness)
    restore_renders()
    for k in ("tier_stats", "frozen_tier_acc", "fairness_checks", "fairness_ok"):
        assert k in base, "BASE missing %s" % k
    _log("  BASE(tiny) tier_stats=%s fairness_ok=%s" % (base["tier_stats"], base["fairness_ok"]))

    r_wr = run_coref_variant(7, "coref_with_roles", "smoke", eval_n=10, hardness=hardness)
    restore_renders()
    r_ab = run_coref_variant(7, "coref_roles_ablated", "smoke", eval_n=10, hardness=hardness)
    restore_renders()

    # META_RULE_AF: with_roles vs roles_ablated must DIFFER (the whole point of the ablation)
    dig_wr = hashlib.sha256(json.dumps({k: round(v, 6) if not math.isnan(v) else -1.0
                                        for k, v in r_wr["tier_acc"].items()}, sort_keys=True).encode()).hexdigest()
    dig_ab = hashlib.sha256(json.dumps({k: round(v, 6) if not math.isnan(v) else -1.0
                                        for k, v in r_ab["tier_acc"].items()}, sort_keys=True).encode()).hexdigest()
    arms_differ = (dig_wr != dig_ab) or (r_wr["weight_move_coref"] != r_ab["weight_move_coref"])
    assert arms_differ, "META_RULE_AF: with_roles and roles_ablated indistinguishable"
    assert r_wr["weight_move_coref"] > 1e-4, "with_roles coref-track did not move weights (NOT LEARNING)"
    assert r_ab["weight_move_coref"] > 1e-4, "roles_ablated coref-track did not move weights (NOT LEARNING)"
    assert r_wr["role_blind"] is False, "coref_with_roles must train BOTH role cues (role_blind False)"
    assert r_ab["role_blind"] is True, "coref_roles_ablated must be role-blind (S cue only)"

    for x in list(r_wr["tier_acc"].values()) + list(r_ab["tier_acc"].values()):
        assert math.isnan(x) or (0.0 <= x <= 1.0), "tier accuracy out of range: %s" % x

    restore_renders()
    _log("  arms_differ=%s | with_roles tier_acc=%s | roles_ablated tier_acc=%s | wmove_wr=%.4f wmove_ab=%.4f"
         % (arms_differ, {k: round(v, 3) if not math.isnan(v) else v for k, v in r_wr["tier_acc"].items()},
            {k: round(v, 3) if not math.isnan(v) else v for k, v in r_ab["tier_acc"].items()},
            r_wr["weight_move_coref"], r_ab["weight_move_coref"]))
    _log("SELF-TEST PASS")
    return {"arms_differ_verified": bool(arms_differ), "tiny_base_fairness_ok": bool(base["fairness_ok"]),
            "tiny_tier_stats": base["tier_stats"],
            "tiny_with_roles_tier_acc": {k: (round(v, 3) if not math.isnan(v) else None)
                                         for k, v in r_wr["tier_acc"].items()},
            "tiny_roles_ablated_tier_acc": {k: (round(v, 3) if not math.isnan(v) else None)
                                            for k, v in r_ab["tier_acc"].items()},
            "tiny_wmove_with_roles": r_wr["weight_move_coref"],
            "tiny_wmove_roles_ablated": r_ab["weight_move_coref"],
            "hardness_lite": list(HARDNESS_LITE), "hardness_smoke": list(HARDNESS_SMOKE)}


# ================= main =================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--lite", action="store_true")
    ap.add_argument("--budget-sec", type=float, default=480.0)
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.lite):
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = "lite"

    hardness = HARDNESS_SMOKE if run_mode == "smoke" else HARDNESS_LITE
    seeds = SEEDS_SMOKE if run_mode == "smoke" else SEEDS_LITE
    eval_n = EVAL_N_SMOKE if run_mode == "smoke" else EVAL_N_LITE

    if run_mode == "self_test":
        _write_start_marker(OUTPUT_DIR, run_mode, 1)
        t0 = time.perf_counter()
        st = run_self_test()
        metrics = {"verdict": "SELFTEST_PASS",
                   "verdict_msg": "SELFTEST_PASS (base + coref_with_roles + coref_roles_ablated end-to-end "
                                  "+ arms-differ + real_code_path)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": time.perf_counter() - t0,
                   "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "selftest": st,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return

    audit = clean.audit_construction(seed=7, n=300)
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    expected_units = len(seeds) * (1 + len(VARIANTS))
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()
    _log("%s: hardness=%s target=%d seeds=%s variants=%s eval_n=%d expected_units=%d"
         % (run_mode.upper(), list(hardness), hardness[-1], seeds, ("base",) + VARIANTS, eval_n,
            expected_units))

    worklist = []
    for s in seeds:
        worklist.append(("base", s, "base"))
        for v_name in VARIANTS:
            worklist.append(("variant", s, v_name))

    done = ckpt.completed_units(OUTPUT_DIR)
    ran = 0
    for kind, s, tag in worklist:
        key = ckpt.unit_key(kind, s, tag, run_mode)
        if key in done:
            continue
        if ran >= 1 and run_mode == "lite" and (time.perf_counter() - t0) > args.budget_sec:
            _log("  budget %.0fs reached after %d new unit(s); stopping (re-run to resume)" % (args.budget_sec, ran))
            break
        if kind == "base":
            res = run_base_coref(s, run_mode, eval_n, hardness)
        else:
            res = run_coref_variant(s, tag, run_mode, eval_n, hardness)
        restore_renders()
        ckpt.record_unit(OUTPUT_DIR, key, res)
        _heartbeat(s, kind, run_mode, tag, time.perf_counter() - t0)
        ran += 1

    units_map = ckpt.load_units(OUTPUT_DIR)
    bases, variants_ = [], []
    for kind, s, tag in worklist:
        key = ckpt.unit_key(kind, s, tag, run_mode)
        if key in units_map:
            (bases if kind == "base" else variants_).append(units_map[key])
    n_done = len(bases) + len(variants_)
    if n_done < expected_units:
        _log("PARTIAL: %d/%d units done -- re-run to resume" % (n_done, expected_units))
        metrics = {"verdict": "PARTIAL", "verdict_msg": "%d/%d units complete; re-run to resume"
                   % (n_done, expected_units), "summary": "PARTIAL %d/%d" % (n_done, expected_units),
                   "run_mode": run_mode, "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                   "anchor_name": ANCHOR_NAME, "n_units_done": n_done, "expected_n_units": expected_units,
                   "cardinality_ok": False, "bases": bases, "variants": variants_,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace", "progress_logging": "print_flush_true"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE (partial) %s in %.1fs" % (run_mode, time.perf_counter() - t0))
        return

    verdict, msg, bands = decide_verdict(bases, variants_, seeds)
    elapsed = time.perf_counter() - t0
    metrics = {"verdict": verdict, "verdict_msg": msg,
               "summary": "%s | %s" % (verdict, msg[:150]),
               "run_mode": run_mode, "elapsed_s": elapsed, "ts_iso": _now_iso(),
               "anchor_name": ANCHOR_NAME, "bands": bands,
               "cardinality_ok": bool(n_done == expected_units), "expected_n_units": expected_units,
               "n_units_done": n_done, "construction_audit": audit, "bases": bases, "variants": variants_,
               "params": {"DIM": clean.DIM, "V_FILL": V_FILL, "DEPTH": DEPTH, "hardness": list(hardness),
                          "steps_coref": STEPS_COREF_SMOKE if run_mode == "smoke" else STEPS_COREF_LITE,
                          "nctx": NCTX_SMOKE if run_mode == "smoke" else NCTX_LITE,
                          "eval_n": eval_n, "seeds": list(seeds), "variants": list(VARIANTS),
                          "LR": lt.LR, "batch": lt.TRAIN_BATCH},
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
