#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_pragmatic_curriculum_dialogue_role_sharded_binding_v1

OVERNIGHT DRILL (USER-authorized, "different ways to overcome the wall"). The wall this drill
attacks: exp_pragmatic_curriculum_dialogue_request_response_dailydialog_v1.py's arm2 (naive flat
superposition) COLLAPSES via COMMON-MODE SWAMPING -- near-universal filler cues (hand_list_verdict=
NA, response_starts_with_quote=True, response_len_bucket=...) dominate the equal-weight flat cue-
bundle, drowning the sparse discriminative cue that actually carries the MET/UNMET label. arm3
(commit eaa07289a, landed HARD_PASS-shaped/MODEST) fixed this PARTIALLY by WEIGHTING cues in the
SAME flat bundle by TRAIN discriminativeness -> held_out_acc=0.667 (modest, +1/15 item above the
majority/MDL floor of 0.600). This cell tests a STRUCTURALLY DIFFERENT fix: SHARD the cues into
named ROLES so filler cues physically cannot compete with the discriminative cue for the SAME
bundle's similarity budget -- reusing the SHARDED-storage architecture already validated at
hdlab/role_slot_summarizer.py (M1.7: FLAT top1=0.000 vs ROLE top1=0.500 at K=1600, per-slot
alpha=K/(S*N) vs FLAT alpha=K/N -- a factor-S capacity multiplier; alpha_wall=0.138, Amit-Gutfreund-
Sompolinsky Hopfield critical load) and hdlab/event_bundle.py's role-keyed bind-then-query pattern
(query_role_vec: unbind by role key, cleanup-argmax). Brain basis: hippocampal pattern-separated /
sharded storage (DG/CA3 pattern separation prevents interference between co-active memory traces).

SUBSTRATE NOTE (apples-to-apples > byte-identical low-level dtype): role_slot_summarizer/
event_bundle's validated SHARDED architecture is implemented on a BIPOLAR {-1,+1} substrate
(N_DIM=8192). arm2/arm3 (the numbers this cell must be compared against) run on FHRR complex64
(N_DIM=1024, hdlab.binding/bundling/atoms) via VSA_BASE. To keep this comparison apples-to-apples
(same vocab atoms, same outcome atoms, same bind/bundle/unbind/similarity primitives, same accuracy/
scramble helpers) the SHARD-BY-ROLE topology is reimplemented here on VSA_BASE's own FHRR substrate
-- the REUSED organ is the ARCHITECTURE (partition items/cues into named-role buffers so they cannot
swamp each other's shared bundle capacity; route or combine via role-addressed readout, exactly
role_slot_summarizer.read_role / event_bundle.query_role_vec's pattern), not the specific tensor
dtype. This is a structural, not a mechanistic, substitution: bind/bundle/unbind/cleanup-argmax are
the SAME four operations in both substrates (elementwise multiply / magnitude-renormalized sum /
elementwise multiply-by-conjugate / similarity-argmax vs bipolar's multiply / sign-quantized-sum /
multiply / k-NN-argmax).

DATA + FEATURES + SPLIT (byte-identical reuse, not re-authored): the EXACT 27-item cleaned DailyDialog
set (DD.clean_items(), DROP_INDICES=[2,3,20]), the EXACT stratified split (DD.find_split(), seed
search base 20260808100, TRAIN n=12 / TEST n=15), and the EXACT feat_fn cue extractor (MDL_BASE.
feat_fn) -- all imported from experiments.exp_pragmatic_curriculum_dialogue_request_response_
dailydialog_v1 (DD) and experiments.exp_pragmatic_curriculum_dialogue_request_response_first_test_v1
(MDL_BASE), called not copied. VSA vocab/outcome atoms are built via the SAME VSA_BASE.build_vocab /
build_outcome_vecs (same seeds -> bit-identical atoms to arm2/arm3). This makes the accuracy
comparison to arm3's 0.667 exact -- same data, same split, same vocabulary, same outcome atoms, same
accuracy/scramble helpers; only the cue-composition topology (flat weighted bundle vs role-sharded
buffers) differs.

ROLE MAP (~30 feature FAMILIES partitioned into 4 named roles; every feat_fn family is assigned,
verified by an exhaustive coverage self-test so no cue can silently fall through unassigned):
  REQUEST         (1 family):  request_pattern
                   -- which syntactic request construction was recognized (REQUEST_LET/MODAL_1P/...).
  RESPONSE_POLARITY (19 families): explicit_yes_present, explicit_no_present,
                   response_negation_present, grant_verb_present, narrated_resolution_verb_present,
                   request_verb_echoed, + all 13 idiom_phrase_* multi-word formula cues ('of course',
                   'all right', 'not likely', 'certainly not', 'guess so', ...)
                   -- THE discriminative cues: the ones that actually carry the MET/UNMET label.
  DISCOURSE       (7 families):  contrast_cue_present (Kehler/Hobbs CONTRAST, the concession-tier
                   signal) + all 6 idiom_token_* single-token weak cues (indeed/truly/really/guess/
                   suppose/why-initial) -- softer discourse-register markers, own shard so they don't
                   dilute RESPONSE_POLARITY's signal nor get swamped by FILLER_META.
  FILLER_META     (5 families):  hand_list_verdict, hand_list_kind, response_is_question,
                   response_starts_with_quote, response_len_bucket
                   -- THE identified common-mode swampers (diagnosed in exp_pragmatic_curriculum_vsa_
                   superposition_map_v1.py's run_common_mode_ablation_probe: hand_list_verdict=NA /
                   hand_list_kind=none fire on 22/24 items, response_starts_with_quote=True on 20/24
                   in the source 24-item corpus) -- always active (categorical fields always emit
                   SOME value) but quarantined to their OWN shard so they cannot dilute the
                   discriminative shards' bundle capacity.

MECHANISM: for item i, build ONE FHRR sub-bundle PER ROLE (only that role's active cue-terms,
weight=1 unless the COMPOSED variant is in effect): role_subbundle_i[r] = bundle([vocab_vec[f] for f
in feat_fn(item_i) if family(f) in role r]) (empty shard -> the zero vector; an honest "no signal
from this shard," not a crash). Two TYPE met/unmet readouts (both tried, per the task brief):
  (i)  ROLE_ROUTE: route via the RESPONSE_POLARITY shard alone -- sup_map = bundle(bind(role_
       subbundle_i[RESPONSE_POLARITY], outcome_vec[gold_i])) over TRAIN (literally VSA_BASE.build_map
       called with a role-restricted cue_bundles dict, reused unmodified); predict via VSA_BASE.
       collapse_predict (also reused unmodified) on the SAME role-restricted dict. Structurally
       excludes FILLER_META/DISCOURSE/REQUEST from ever entering the discriminative shard's bundle.
  (ii) ROLE_MULTI_COMBINE: build FOUR separate per-role sup_maps (each via VSA_BASE.build_map on that
       role's cue_bundles dict); at test, unbind+similarity against EACH role's own map, then SUM the
       four roles' MET/UNMET similarity scores and argmax. An empty shard contributes similarity 0.0
       to BOTH labels (no bias), so it neither votes nor gets swamped -- the "sharded MAP: bind(
       sharded_construction_vec (x) outcome_vec), collapse at test" variant from the task brief.
  COMPOSED (role-sharding + WITHIN-shard discriminativeness weighting, "the plausible bigger lift"):
       reuses DD.compute_cue_weights (TRAIN-only weight_c = |P(MET|c present) - P(MET|c absent)|,
       UNCHANGED formula) but applies it INSIDE each role's own sub-bundle (weight_c * vocab_vec[c]
       for c in THAT shard only) instead of across one flat item-level bundle -- each shard's own
       weighting competes only within its own shard's cue population, never against another shard's
       cues. Per-shard degenerate guard (glass-box, mirrors arm3's per-item guard): if a shard's
       active cues ALL have TRAIN-weight 0, fall back to equal-weight WITHIN that shard rather than a
       zero vector. Composed is measured on BOTH readouts (route + multi-combine); the multi-combine+
       weighted variant is the headline COMPOSED arm (uses every role's signal, weighted).

ARMS MEASURED (all on the SAME 27-item data / stratified split / vocab atoms):
  role_route_unweighted        (i, unweighted)      -- + per-role isolation diagnostic (route via
                                                         EACH of the 4 roles individually, glass-box
                                                         "which role carries the signal")
  role_multi_combine_unweighted (ii, unweighted)
  role_route_weighted          (i, composed)
  role_multi_combine_weighted  (ii, composed)         <- HEADLINE "COMPOSED" arm
  Cited/re-printed incumbents (re-measured LIVE via DD.run_pipeline(), not stale numbers): arm3
  attention-weighted-flat (expect ~0.667), arm2 naive-flat (expect ~0.533), MDL (expect ~0.600
  KEEP_EPISODIC), majority floor (expect ~0.600).
  SCRAMBLE control on every role-sharded/composed arm (MDL_BASE.scramble_train_labels, fixed
  DD.SCRAMBLE_SEED; COMPOSED variants recompute BOTH the weights AND the maps from the permuted-label
  TRAIN, matching arm3's own rigor) -- expect collapse toward the DD.SCRAMBLE_BAND<=0.60 floor.

GATE (pre-registered; anti-premature-HARD_FAIL protocol governs any non-pass; brain=existence-proof
so a miss is a fidelity-gap diagnosis, not a ceiling claim):
  HARD-PASS: best role-sharded/composed arm's held-out acc > arm3's LIVE acc, non-constant predictions
    (n_distinct_preds > 1), AND its scramble control collapses (acc_scramble <= DD.SCRAMBLE_BAND) ->
    role-structure is the better brain-faithful mechanism.
  PARTIAL: best arm matches arm3 (>= arm3_acc - EPS) and is non-constant -> role-structure is an
    equally-valid, more-scalable topology (sharding's capacity advantage grows with S*n; flat cue-
    weighting's does not) even without a strict accuracy win at this n.
  HARD-FAIL band: best arm <= arm2's LIVE acc AND digest_real == digest_scramble for that arm
    (constant collapse, unresolved by scramble differencing) -> role structure alone does not help at
    THIS data density; diagnose (n=12 TRAIN too sparse per 4-way shard? role-assignment error?
    coverage gap?) -- NOT declared a ceiling.
  Anything between PARTIAL and HARD-FAIL band is reported as MIDDLE_BAND with the specific failing
  gate condition named (never silently rounded up to a pass).

COMPUTE: n=27 items, N_DIM=1024 dense complex64 (same as arm2/arm3), closed-form tensor ops only, no
training loop. Wall time sub-second. LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO
remote-persist, NO hdlab mutation, NO atom bank (skunkworks VETs). Deterministic:
OMP/MKL/OPENBLAS_NUM_THREADS=1, fixed torch.Generator seeds (VSA_BASE.VOCAB_SEED/OUTCOME_SEED, reused
unmodified), fixed-int random.Random seed (DD.SCRAMBLE_SEED, reused unmodified) for every scramble
permutation, fixed-sequence seed search for the split (DD.find_split, reused unmodified).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "pragmatic_curriculum_dialogue_role_sharded_binding_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import binding, bundling, atoms  # noqa: E402  (REUSE: bind/unbind/bundle/similarity primitives)
import experiments.exp_pragmatic_curriculum_dialogue_request_response_first_test_v1 as MDL_BASE  # noqa: E402
import experiments.exp_pragmatic_curriculum_vsa_superposition_map_v1 as VSA_BASE  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_request_response_dailydialog_v1 as DD  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
EPS = 1e-9

# ========================================================================================
# ROLE MAP (see module docstring for rationale). Every feat_fn cue FAMILY must appear exactly
# once below; coverage is verified by an exhaustive assertion in the instrumentation self-test.
# ========================================================================================
ROLE_REQUEST = "REQUEST"
ROLE_RESPONSE_POLARITY = "RESPONSE_POLARITY"
ROLE_DISCOURSE = "DISCOURSE"
ROLE_FILLER_META = "FILLER_META"
ROLES = [ROLE_REQUEST, ROLE_RESPONSE_POLARITY, ROLE_DISCOURSE, ROLE_FILLER_META]

FAMILY_ROLE = {
    "request_pattern": ROLE_REQUEST,
    "explicit_yes_present": ROLE_RESPONSE_POLARITY,
    "explicit_no_present": ROLE_RESPONSE_POLARITY,
    "response_negation_present": ROLE_RESPONSE_POLARITY,
    "grant_verb_present": ROLE_RESPONSE_POLARITY,
    "narrated_resolution_verb_present": ROLE_RESPONSE_POLARITY,
    "request_verb_echoed": ROLE_RESPONSE_POLARITY,
    "contrast_cue_present": ROLE_DISCOURSE,
    "hand_list_verdict": ROLE_FILLER_META,
    "hand_list_kind": ROLE_FILLER_META,
    "response_is_question": ROLE_FILLER_META,
    "response_starts_with_quote": ROLE_FILLER_META,
    "response_len_bucket": ROLE_FILLER_META,
}
for _phrase in MDL_BASE.IDIOM_PHRASES:
    FAMILY_ROLE["idiom_phrase_" + MDL_BASE._slug(_phrase)] = ROLE_RESPONSE_POLARITY
for _tok in MDL_BASE.IDIOM_TOKENS:
    FAMILY_ROLE["idiom_token_" + _tok] = ROLE_DISCOURSE
FAMILY_ROLE["idiom_token_why_initial"] = ROLE_DISCOURSE

ROLE_MAP_REPORT = {
    r: sorted(fam for fam, rr in FAMILY_ROLE.items() if rr == r) for r in ROLES
}


def cue_family(term):
    """'name=value' or 'name=True' -> 'name'."""
    return term.split("=", 1)[0]


def role_of_term(term):
    fam = cue_family(term)
    role = FAMILY_ROLE.get(fam)
    if role is None:
        raise KeyError("UNASSIGNED cue family %r (term=%r) -- role map coverage gap" % (fam, term))
    return role


def assert_full_role_coverage(vocab_terms):
    missing = [t for t in vocab_terms if cue_family(t) not in FAMILY_ROLE]
    if missing:
        raise AssertionError("INSTRUMENTATION_SUSPECT: %d vocab term(s) have no role assignment: %r"
                              % (len(missing), missing))


# ========================================================================================
# Per-item per-role FHRR sub-bundles (the SHARDED storage: filler cues in FILLER_META can never
# enter the RESPONSE_POLARITY shard's own bundle capacity -- role_slot_summarizer's architecture,
# reimplemented on VSA_BASE's FHRR substrate; see module docstring "SUBSTRATE NOTE").
# ========================================================================================
def item_role_subbundles(item, vocab_vecs, feat_fn=None, weights=None):
    """Returns {role: (n_dim,) FHRR sub-bundle}. weights=None -> equal-weight (role-sharded,
    unweighted). weights={term: w} -> COMPOSED (within-shard discriminativeness weighting, arm3's
    formula applied per-shard); per-shard degenerate guard: if every active cue in a shard has
    weight 0, fall back to equal-weight WITHIN that shard (mirrors arm3's per-item fallback, but
    scoped to the shard, not the whole item). Empty shard (no active cues of that role for this
    item) -> zero vector (honest 'no signal offered'), not a crash; similarity() handles zero
    vectors safely (returns 0.0, no divide-by-zero -- see hdlab.atoms.similarity)."""
    ff = feat_fn or MDL_BASE.feat_fn
    feats = ff(item)
    by_role = {r: [] for r in ROLES}
    for f in feats:
        by_role[role_of_term(f)].append(f)
    n_dim = next(iter(vocab_vecs.values())).shape[0]
    out = {}
    fallback_roles = []
    for r in ROLES:
        terms = by_role[r]
        if not terms:
            out[r] = torch.zeros(n_dim, dtype=torch.complex64)
            continue
        if weights is None:
            vecs = torch.stack([vocab_vecs[f] for f in terms], dim=0)
        else:
            w = [weights.get(f, 0.0) for f in terms]
            if sum(w) <= 0.0:
                vecs = torch.stack([vocab_vecs[f] for f in terms], dim=0)
                fallback_roles.append(r)
            else:
                vecs = torch.stack([wi * vocab_vecs[f] for f, wi in zip(terms, w)], dim=0)
        out[r] = bundling.bundle(vecs)
    return out, fallback_roles


def build_role_subbundles(items, vocab_vecs, feat_fn=None, weights=None):
    subb, fallbacks = {}, {}
    for it in items:
        s, fb = item_role_subbundles(it, vocab_vecs, feat_fn=feat_fn, weights=weights)
        subb[it["id"]] = s
        if fb:
            fallbacks[it["id"]] = fb
    return subb, fallbacks


def role_cue_bundles_dict(subbundles_by_id, role):
    """Adapter: {item_id: role_subbundle} for ONE role -- lets us call VSA_BASE.build_map /
    collapse_predict (reused, unmodified) exactly as arm2/arm3 do, just fed a role-restricted
    bundle instead of the flat whole-item bundle."""
    return {iid: subb[role] for iid, subb in subbundles_by_id.items()}


# ========================================================================================
# Variant (i): ROLE_ROUTE -- route via ONE named role's shard (RESPONSE_POLARITY by default; also
# used per-role for the glass-box "which role carries the signal" isolation diagnostic).
# Reuses VSA_BASE.build_map / collapse_predict / _pred_digest UNMODIFIED.
# ========================================================================================
def run_role_route_arm(role, train_items, test_items, subbundles_real, subbundles_scr, outcome_vecs):
    gold = [it["gold_class"] for it in test_items]
    cue_bundles_real = role_cue_bundles_dict(subbundles_real, role)
    cue_bundles_scr = role_cue_bundles_dict(subbundles_scr, role)

    sup_map = VSA_BASE.build_map(train_items, cue_bundles_real, outcome_vecs)
    preds, sims_list, margins = [], [], []
    for it in test_items:
        pred, sims, margin = VSA_BASE.collapse_predict(it, sup_map, cue_bundles_real, outcome_vecs)
        preds.append(pred)
        sims_list.append(sims)
        margins.append(margin)
    acc = MDL_BASE.accuracy(preds, gold)

    train_scr = MDL_BASE.scramble_train_labels(train_items, seed=DD.SCRAMBLE_SEED)
    sup_map_scr = VSA_BASE.build_map(train_scr, cue_bundles_scr, outcome_vecs)
    preds_scr = [VSA_BASE.collapse_predict(it, sup_map_scr, cue_bundles_scr, outcome_vecs)[0] for it in test_items]
    acc_scr = MDL_BASE.accuracy(preds_scr, gold)

    dig_real, _ = VSA_BASE._pred_digest(test_items, sup_map, cue_bundles_real, outcome_vecs)
    dig_scr, _ = VSA_BASE._pred_digest(test_items, sup_map_scr, cue_bundles_scr, outcome_vecs)

    per_item = [{"id": it["id"], "subtype": it["subtype"], "gold": it["gold_class"], "pred": p,
                 "correct": bool(p == it["gold_class"]), "margin": round(m, 5)}
                for it, p, m in zip(test_items, preds, margins)]
    return {
        "role": role, "n_train": len(train_items), "n_test": len(test_items),
        "acc": acc, "acc_scramble": acc_scr, "scramble_delta": acc - acc_scr,
        "digest_real": dig_real, "digest_scramble": dig_scr,
        "arms_differ_real_vs_scramble": dig_real != dig_scr,
        "n_distinct_preds": len(set(preds)), "collapsed_to_constant": len(set(preds)) <= 1,
        "per_item": per_item,
    }


# ========================================================================================
# Variant (ii): ROLE_MULTI_COMBINE -- S separate per-role sup_maps; test-time similarity SUMMED
# across all 4 roles then argmax. An empty shard contributes 0.0 to BOTH labels (no vote, no bias).
# ========================================================================================
def build_multi_role_maps(train_items, subbundles, outcome_vecs):
    return {r: VSA_BASE.build_map(train_items, role_cue_bundles_dict(subbundles, r), outcome_vecs)
            for r in ROLES}


def collapse_predict_multi_role(item, sup_maps_by_role, subbundles, outcome_vecs):
    combined = {lbl: 0.0 for lbl in VSA_BASE.LABELS}
    per_role_sims = {}
    for r in ROLES:
        q = subbundles[item["id"]][r]
        recovered = binding.unbind(sup_maps_by_role[r], q)
        sims = {lbl: float(atoms.similarity(recovered, outcome_vecs[lbl])) for lbl in VSA_BASE.LABELS}
        per_role_sims[r] = sims
        for lbl in VSA_BASE.LABELS:
            combined[lbl] += sims[lbl]
    best = max(combined, key=combined.get)
    other = [l for l in VSA_BASE.LABELS if l != best][0]
    margin = combined[best] - combined[other]
    return best, combined, margin, per_role_sims


def run_role_multi_combine_arm(train_items, test_items, subbundles_real, subbundles_scr, outcome_vecs):
    gold = [it["gold_class"] for it in test_items]

    sup_maps = build_multi_role_maps(train_items, subbundles_real, outcome_vecs)
    preds, margins, role_sims_all = [], [], []
    for it in test_items:
        pred, _combined, margin, per_role_sims = collapse_predict_multi_role(it, sup_maps, subbundles_real, outcome_vecs)
        preds.append(pred)
        margins.append(margin)
        role_sims_all.append(per_role_sims)
    acc = MDL_BASE.accuracy(preds, gold)

    train_scr = MDL_BASE.scramble_train_labels(train_items, seed=DD.SCRAMBLE_SEED)
    sup_maps_scr = build_multi_role_maps(train_scr, subbundles_scr, outcome_vecs)
    preds_scr = [collapse_predict_multi_role(it, sup_maps_scr, subbundles_scr, outcome_vecs)[0] for it in test_items]
    acc_scr = MDL_BASE.accuracy(preds_scr, gold)

    def _digest(preds_seq):
        import hashlib
        return hashlib.sha256(json.dumps(preds_seq).encode()).hexdigest()[:16]

    dig_real, dig_scr = _digest(preds), _digest(preds_scr)

    per_item = [{"id": it["id"], "subtype": it["subtype"], "gold": it["gold_class"], "pred": p,
                 "correct": bool(p == it["gold_class"]), "margin": round(m, 5),
                 "per_role_sims": {r: {k: round(v, 5) for k, v in sims.items()} for r, sims in rs.items()}}
                for it, p, m, rs in zip(test_items, preds, margins, role_sims_all)]
    return {
        "n_train": len(train_items), "n_test": len(test_items),
        "acc": acc, "acc_scramble": acc_scr, "scramble_delta": acc - acc_scr,
        "digest_real": dig_real, "digest_scramble": dig_scr,
        "arms_differ_real_vs_scramble": dig_real != dig_scr,
        "n_distinct_preds": len(set(preds)), "collapsed_to_constant": len(set(preds)) <= 1,
        "per_item": per_item,
    }


# ========================================================================================
# Crash diagnostics + atomic write (project convention)
# ========================================================================================
def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
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
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


# ========================================================================================
# Main pipeline
# ========================================================================================
def run_pipeline(run_mode):
    t0 = time.perf_counter()

    mdl_ctrl = MDL_BASE.run_positive_control()
    vsa_ctrl = VSA_BASE.run_positive_control()

    # ---- IDENTICAL data / split to arm2/arm3 (reused, not re-derived) ----
    items_cleaned = DD.clean_items()
    split_seed, episodes, _hard_missed = DD.find_split(items_cleaned)
    assert len(episodes) == 27
    train = [it for it in episodes if it["split"] == "train"]
    test = [it for it in episodes if it["split"] == "test"]
    assert len(train) == 12 and len(test) == 15

    # ---- IDENTICAL vocab / outcome atoms to arm2/arm3 (same seeds, via VSA_BASE unmodified) ----
    vocab_vecs, vocab_terms = VSA_BASE.build_vocab(episodes)
    outcome_vecs = VSA_BASE.build_outcome_vecs()
    assert_full_role_coverage(vocab_terms)

    # ---- role-sharded sub-bundles: unweighted (role-sharded arms) ----
    subb_real_unw, fb_real_unw = build_role_subbundles(episodes, vocab_vecs)
    train_scr_labels_only = MDL_BASE.scramble_train_labels(train, seed=DD.SCRAMBLE_SEED)
    # cue sub-bundles do not depend on labels, so the "scrambled" sub-bundle dict is the SAME
    # per-item content as the real one; scrambling only changes which OUTCOME each id is bound to
    # when build_map is called with train_scr (handled inside run_role_route_arm/multi_combine).
    subb_scr_unw = subb_real_unw

    # ---- per-role ISOLATION diagnostic (glass-box: which role carries the signal alone) ----
    role_isolation = {r: run_role_route_arm(r, train, test, subb_real_unw, subb_scr_unw, outcome_vecs)
                       for r in ROLES}
    role_route_unweighted = role_isolation[ROLE_RESPONSE_POLARITY]  # variant (i), unweighted

    role_multi_combine_unweighted = run_role_multi_combine_arm(
        train, test, subb_real_unw, subb_scr_unw, outcome_vecs)

    # ---- COMPOSED: within-shard discriminativeness weighting (arm3's formula, applied per-shard) ----
    weights = DD.compute_cue_weights(train, feat_fn=MDL_BASE.feat_fn)
    subb_real_w, fb_real_w = build_role_subbundles(episodes, vocab_vecs, weights=weights)
    weights_scr = DD.compute_cue_weights(train_scr_labels_only, feat_fn=MDL_BASE.feat_fn)
    subb_scr_w, fb_scr_w = build_role_subbundles(episodes, vocab_vecs, weights=weights_scr)

    role_route_weighted = run_role_route_arm(
        ROLE_RESPONSE_POLARITY, train, test, subb_real_w, subb_scr_w, outcome_vecs)
    role_multi_combine_weighted = run_role_multi_combine_arm(
        train, test, subb_real_w, subb_scr_w, outcome_vecs)  # <- HEADLINE COMPOSED arm

    # ---- cited/re-printed incumbents: RE-MEASURED LIVE (not stale numbers) ----
    dd_metrics = DD.run_pipeline(run_mode="role_sharded_comparison_reference")
    arm2_acc = dd_metrics["naive_superposition_arm2"]["acc"]
    arm2_acc_scr = dd_metrics["naive_superposition_arm2"]["acc_scramble"]
    arm3_acc = dd_metrics["refined_superposition_arm3"]["acc"]
    arm3_acc_scr = dd_metrics["refined_superposition_arm3"]["acc_scramble"]
    mdl_acc = dd_metrics["mdl_arm"]["held_out_accuracy"]
    maj_acc = dd_metrics["majority_class_floor"]["held_out_accuracy"]
    assert dd_metrics["split"]["seed_used"] == split_seed, (
        "INSTRUMENTATION_SUSPECT: split seed drift between this cell's own find_split() call and "
        "DD.run_pipeline()'s internal call -- not apples-to-apples any more")

    candidate_arms = {
        "role_route_unweighted": role_route_unweighted,
        "role_multi_combine_unweighted": role_multi_combine_unweighted,
        "role_route_weighted": role_route_weighted,
        "role_multi_combine_weighted_COMPOSED": role_multi_combine_weighted,
    }
    best_name = max(candidate_arms, key=lambda k: candidate_arms[k]["acc"])
    best_arm = candidate_arms[best_name]

    # ---- gate ----
    best_non_constant = not best_arm["collapsed_to_constant"]
    best_scramble_collapses = best_arm["acc_scramble"] <= DD.SCRAMBLE_BAND + EPS
    beats_arm3 = best_arm["acc"] > arm3_acc + EPS
    matches_arm3 = best_arm["acc"] >= arm3_acc - EPS
    at_or_below_arm2 = best_arm["acc"] <= arm2_acc + EPS
    best_constant_collapse = best_arm["digest_real"] == best_arm["digest_scramble"]

    ctrl_ok = mdl_ctrl["passed"] and vsa_ctrl["passed"]

    hard_pass = ctrl_ok and beats_arm3 and best_non_constant and best_scramble_collapses
    partial = ctrl_ok and (not hard_pass) and matches_arm3 and best_non_constant
    hard_fail_band = ctrl_ok and at_or_below_arm2 and best_constant_collapse

    if not ctrl_ok:
        verdict = "HARD_FAIL_MECHANISM"
        msg = ("Positive control failed: mdl_ctrl passed=%s vsa_ctrl passed=%s -- do not trust the "
               "real-data numbers below." % (mdl_ctrl["passed"], vsa_ctrl["passed"]))
    elif hard_pass:
        verdict = "HARD_PASS"
        msg = ("HARD_PASS: best role-sharded arm (%s, acc=%.4f) BEATS arm3's live acc=%.4f, "
               "non-constant (n_distinct_preds=%d), scramble collapses (acc_scr=%.4f <= band=%.2f) "
               "-> role-structure is the better brain-faithful mechanism at this data density." %
               (best_name, best_arm["acc"], arm3_acc, best_arm["n_distinct_preds"],
                best_arm["acc_scramble"], DD.SCRAMBLE_BAND))
    elif partial:
        verdict = "PARTIAL_MATCHES_ARM3"
        msg = ("PARTIAL: best role-sharded arm (%s, acc=%.4f) MATCHES arm3's live acc=%.4f "
               "(non-constant, n_distinct_preds=%d) without a strict accuracy win -- role-structure "
               "is an equally-valid, more-scalable topology (sharding's capacity advantage grows "
               "with S*n; flat cue-weighting's does not). Scramble collapse=%s (acc_scr=%.4f)." %
               (best_name, best_arm["acc"], arm3_acc, best_arm["n_distinct_preds"],
                best_scramble_collapses, best_arm["acc_scramble"]))
    elif hard_fail_band:
        verdict = "HARD_FAIL_ROLE_STRUCTURE_NO_HELP_AT_THIS_DENSITY"
        msg = ("HARD-FAIL band: best role-sharded arm (%s, acc=%.4f) is AT OR BELOW arm2's live "
               "naive-flat acc=%.4f, with digest_real==digest_scramble (constant collapse, unresolved "
               "by scramble differencing) -- role structure alone does not help at n_train=%d split "
               "4 ways (~3 items/shard). Diagnose: per-shard TRAIN density, role-assignment error, or "
               "coverage gap -- NOT a ceiling claim." % (best_name, best_arm["acc"], arm2_acc, len(train)))
    else:
        verdict = "MIDDLE_BAND"
        msg = ("MIDDLE_BAND: best role-sharded arm (%s, acc=%.4f) neither clears the PARTIAL bar "
               "(matches arm3=%.4f, non-constant=%s) nor lands in the HARD-FAIL band (<= arm2=%.4f "
               "AND constant-collapse=%s). See gate booleans / per-arm detail." %
               (best_name, best_arm["acc"], arm3_acc, best_non_constant, arm2_acc, best_constant_collapse))

    which_role_carried_signal = max(role_isolation, key=lambda r: role_isolation[r]["acc"])

    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": round(elapsed, 4),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "positive_controls": {"mdl_xor_control": mdl_ctrl, "vsa_synthetic_control": vsa_ctrl},
        "role_map": ROLE_MAP_REPORT,
        "n_vocab_terms": len(vocab_terms),
        "split": {"seed_used": split_seed, "n_train": len(train), "n_test": len(test),
                   "train_ids": [it["id"] for it in train], "test_ids": [it["id"] for it in test]},
        "incumbents_live": {
            "arm2_naive_flat": {"acc": arm2_acc, "acc_scramble": arm2_acc_scr},
            "arm3_attention_weighted_flat": {"acc": arm3_acc, "acc_scramble": arm3_acc_scr},
            "mdl": {"acc": mdl_acc}, "majority": {"acc": maj_acc},
        },
        "role_isolation_diagnostic": {
            r: {"acc": role_isolation[r]["acc"], "acc_scramble": role_isolation[r]["acc_scramble"],
                "n_distinct_preds": role_isolation[r]["n_distinct_preds"],
                "collapsed_to_constant": role_isolation[r]["collapsed_to_constant"]}
            for r in ROLES
        },
        "which_role_carried_signal_alone": which_role_carried_signal,
        "fallback_shards_used_real_unweighted": fb_real_unw,
        "fallback_shards_used_real_weighted": fb_real_w,
        "fallback_shards_used_scramble_weighted": fb_scr_w,
        "learned_cue_weights_top10": dict(list(sorted(weights.items(), key=lambda kv: -kv[1]))[:10]),
        "arms": {
            "role_route_unweighted": role_route_unweighted,
            "role_multi_combine_unweighted": role_multi_combine_unweighted,
            "role_route_weighted": role_route_weighted,
            "role_multi_combine_weighted_COMPOSED": role_multi_combine_weighted,
        },
        "best_arm_name": best_name, "best_arm_acc": best_arm["acc"],
        "gates": {
            "positive_controls_passed": ctrl_ok,
            "best_beats_arm3": beats_arm3, "best_matches_arm3": matches_arm3,
            "best_non_constant": best_non_constant, "best_scramble_collapses": best_scramble_collapses,
            "best_at_or_below_arm2": at_or_below_arm2, "best_constant_collapse": best_constant_collapse,
            "hard_pass": hard_pass, "partial": partial, "hard_fail_band": hard_fail_band,
            "scramble_band": DD.SCRAMBLE_BAND,
        },
        "cell_chunked": False, "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": True, "scramble_seed": DD.SCRAMBLE_SEED, "split_seed": split_seed,
        "cardinality_ok": True, "expected_n_units": 1,
    }
    return metrics


# ========================================================================================
# Instrumentation self-test (MANDATORY at module scope before any dispatch)
# ========================================================================================
def _instrumentation_selftest():
    mdl_ctrl = MDL_BASE.run_positive_control()
    assert mdl_ctrl["passed"], "SELFTEST FAIL: MDL XOR positive control did not pass: %r" % mdl_ctrl
    vsa_ctrl = VSA_BASE.run_positive_control()
    assert vsa_ctrl["passed"], "SELFTEST FAIL: VSA synthetic positive control did not pass: %r" % vsa_ctrl

    items_cleaned = DD.clean_items()
    split_seed, episodes, _ = DD.find_split(items_cleaned)
    train = [it for it in episodes if it["split"] == "train"]
    test = [it for it in episodes if it["split"] == "test"]
    assert len(train) == 12 and len(test) == 15, "SELFTEST FAIL: split sizes wrong"

    vocab_vecs, vocab_terms = VSA_BASE.build_vocab(episodes)
    assert_full_role_coverage(vocab_terms)  # must not raise
    # every ROLE must have >=1 assigned family (a role with zero coverage is a design bug)
    for r in ROLES:
        assert len(ROLE_MAP_REPORT[r]) >= 1, "SELFTEST FAIL: role %r has zero assigned cue families" % r
    # role map partitions (no family double-assigned)
    all_assigned = [fam for r in ROLES for fam in ROLE_MAP_REPORT[r]]
    assert len(all_assigned) == len(set(all_assigned)), "SELFTEST FAIL: a cue family assigned to >1 role"

    outcome_vecs = VSA_BASE.build_outcome_vecs()

    # sub-bundle determinism
    subb1, _ = build_role_subbundles(episodes, vocab_vecs)
    subb2, _ = build_role_subbundles(episodes, vocab_vecs)
    for iid in subb1:
        for r in ROLES:
            assert torch.allclose(subb1[iid][r], subb2[iid][r]), \
                "SELFTEST FAIL: role sub-bundle nondeterministic for %s/%s" % (iid, r)
    # shapes
    n_dim = next(iter(vocab_vecs.values())).shape[0]
    for r in ROLES:
        assert subb1[episodes[0]["id"]][r].shape == (n_dim,), "SELFTEST FAIL: sub-bundle shape wrong"

    # ROLE_ROUTE determinism + glass-box fields present
    r1 = run_role_route_arm(ROLE_RESPONSE_POLARITY, train, test, subb1, subb1, outcome_vecs)
    r2 = run_role_route_arm(ROLE_RESPONSE_POLARITY, train, test, subb1, subb1, outcome_vecs)
    assert r1["digest_real"] == r2["digest_real"], "SELFTEST FAIL: role_route not deterministic"
    assert len(r1["per_item"]) == 15
    assert all("margin" in p for p in r1["per_item"])

    # ROLE_MULTI_COMBINE determinism
    m1 = run_role_multi_combine_arm(train, test, subb1, subb1, outcome_vecs)
    m2 = run_role_multi_combine_arm(train, test, subb1, subb1, outcome_vecs)
    assert m1["digest_real"] == m2["digest_real"], "SELFTEST FAIL: multi_combine not deterministic"
    assert len(m1["per_item"]) == 15

    # empty-shard handling: an item with zero DISCOURSE cues must get a zero sub-bundle, not crash
    zero_count = sum(1 for iid in subb1 if torch.count_nonzero(subb1[iid][ROLE_DISCOURSE]) == 0)
    # (not asserted >0 -- just proves the code path is exercised without raising if it occurs)

    # weighted (COMPOSED) path: weights determinism + fallback bookkeeping is a list
    w1 = DD.compute_cue_weights(train, feat_fn=MDL_BASE.feat_fn)
    w2 = DD.compute_cue_weights(train, feat_fn=MDL_BASE.feat_fn)
    assert w1 == w2, "SELFTEST FAIL: compute_cue_weights not deterministic"
    subbw, fbw = build_role_subbundles(episodes, vocab_vecs, weights=w1)
    assert isinstance(fbw, dict)
    rw1 = run_role_route_arm(ROLE_RESPONSE_POLARITY, train, test, subbw, subbw, outcome_vecs)
    rw2 = run_role_route_arm(ROLE_RESPONSE_POLARITY, train, test, subbw, subbw, outcome_vecs)
    assert rw1["digest_real"] == rw2["digest_real"], "SELFTEST FAIL: weighted role_route not deterministic"


_instrumentation_selftest()  # Called at module scope before the main pipeline


def self_test():
    metrics = run_pipeline(run_mode="self_test")
    _write_metrics(OUTPUT_DIR + "_selftest", metrics)
    print("[self_test] verdict=%s" % metrics["verdict"])
    print("[self_test] " + metrics["verdict_msg"])
    return metrics["verdict"] not in ("CELL_CRASHED",)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run-mode", choices=["full", "self_test"], default="full")
    args = ap.parse_args()

    if args.self_test:
        ok = self_test()
        print("[SELFTEST] %s" % ("PASS" if ok else "FAIL"))
        sys.exit(0 if ok else 1)

    metrics = run_pipeline(run_mode=args.run_mode)
    _write_metrics(OUTPUT_DIR, metrics)
    print("[%s] verdict=%s" % (args.run_mode, metrics["verdict"]))
    print("[%s] " % args.run_mode + metrics["verdict_msg"])
    print(json.dumps({k: v for k, v in metrics.items() if k != "arms"}, indent=2, default=str))
    print("---- arms (full per-item detail) ----")
    for name, arm in metrics["arms"].items():
        print("== %s ==" % name)
        for p in arm["per_item"]:
            print(json.dumps(p, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
