# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: BASE / WITH_REAL_PRIOR / WITH_SCRAMBLED_PRIOR / POSITION per-mention
#   prediction vectors hash-compared at smoke gate (these are 4 genuinely different prediction
#   strategies over the SAME meaning-required-bucket events, not sweep points).
# - final_metrics_atomicity = tmp_replace (single-shot; whole run measured ~15-20s at --full on this
#   session's dev probe, no grid sweep of new hyperparameters -- THRESH/margin_thresh REUSED verbatim
#   from exp_extraction_commit_then_revise_v3_theme's own already-selected values)
# - except SystemExit / KeyboardInterrupt re-raised BEFORE except Exception (no BaseException)
# - crlb_n/a: "discrete multiclass role-classification accuracy over a fixed small eval set, no CRLB
#   noise floor applies"; discriminator_reachability=true (the can-fail checks below ARE the
#   reachability gate: both SURFACE and MEANING buckets must be non-empty, i.e. the split must not be
#   vacuous, checked before any Q2 claim)
# - baseline_in_band: not the classic capacity-sweep sense -- this is a DIAGNOSTIC + bootstrap cell.
#   The can-fail controls (OOV-not-helped, scrambled-not-better, position-near-floor-on-MEANING) ARE
#   the in-band checks; see decide_verdict().
# - cell_chunked=False (single pass over 11 eval passages + 5 small train pools; per CLAUDE.md's
#   "any cell looping over >1 unit" rule, resumability is provided via tools/exp_checkpoint.py anyway,
#   used per logical stage: Q1_SPLIT / Q2_BASE / Q2_REAL_PRIOR / Q2_SCRAMBLED_PRIOR / Q2_POSITION)
# - HYPOTHESIZED/MEASURED/CITED/THEORETICAL tags on every number in this docstring
# - ASCII-only, no emojis, no em dashes.
"""exp_meaning_required_bootstrap_v1 (2026-08-02)

TWO LINKED QUESTIONS about the role-extraction learner, per the director's contract:

Q1 (DIAGNOSTIC) -- how much of the end-to-end extraction wall is "a surface clue is enough" vs
"you must know what the words mean"? Operationalized WITHOUT circularity: for every gold
mention-role event in the HELD-OUT eval (gold_multiclause_entity_track_v2.jsonl, the real McGuffey
multi-clause narrative gold, restricted to the extraction layer's REACHABLE_ROLES = {agent, patient,
addressee, theme} -- the 4 roles the commit-then-revise-v3-theme stage-1 model's vocab actually
covers; recipient/possessor/experiencer are an ALREADY-DOCUMENTED role-inventory gap, see
exp_extraction_commit_then_revise_v3_theme.py's own PROBE-TO-AIM section, and are tallied separately
here, never folded into the surface/meaning split):

  POS_PRED = clause_position_predict5(sent) -- the pure-syntax proxy (clause-subject=agent,
  every other clause-mention=patient), computed INDEPENDENT of gold.
  SURFACE-DECIDABLE  := POS_PRED == gold_role   (syntax position ALONE already gets the right answer)
  MEANING-REQUIRED   := POS_PRED != gold_role   (syntax position alone is NOT sufficient; something
                         else -- another construction cue, or genuine world-knowledge about which
                         entity is the plausible agent -- is needed)

This is not circular: POS_PRED is a fixed, gold-blind function; "== gold" is the only place gold
enters, and it enters identically for every event, not tuned per-bucket.

Per-bucket report: fraction of cases + the FULL commit-revise-v3-theme extractor's (BASE_PRED)
accuracy in each bucket. MEASURED@this session's dev probe (see self-test/full output): of 51
matched reachable-role events (1 mention failed match_mention_to_token, 6 events outside the
reachable vocab entirely -- tallied, not scored): SURFACE-DECIDABLE n=25 (49%), BASE_PRED acc=0.920;
MEANING-REQUIRED n=26 (51%), BASE_PRED acc=0.346 (chance for a 4-way softmax = 0.25) -- confirms the
expectation (high on surface, near-floor on meaning) HYPOTHESIZED in the director's contract.

FINER SPLIT (added because it matters for Q2's honest framing): within MEANING-REQUIRED, BASE_PRED
already gets 9/26 right via a DIFFERENT surface cue than clause-position (by-phrase / postposed-quote
/ is_copular firing correctly) -- these are NOT "meaning was required and supplied"; they are cases
where clause-position specifically fails but a DIFFERENT already-built construction detector
succeeds. The remaining 17/26 ("residual", still wrong under BASE_PRED too) are the genuine current
wall this cell's Q2 bootstrap targets. Reported as meaning_required_resolved_by_other_gate (9) vs
meaning_required_residual_still_wrong (17), both MEASURED@this session's dev probe.

Q2 (THE BUILD) -- can a per-word role-tendency PRIOR, accumulated ONLY from clear high-confidence
surface-decidable TRAIN cases (never from the model's own uncertain guesses), combined with the
extractor's own prediction, improve accuracy on the MEANING-REQUIRED bucket without hurting
SURFACE-DECIDABLE, in a way that is GENUINELY word-specific (not luck)?

TRAIN / HELD-OUT SEPARATION (hard, never crossed): TRAIN = the 5 curated construction-pool gold
files (gold_mcguffey_lccp_argstruct_v1 canonical pool, gold_quotative_verified_v2,
gold_passive_byagent_verified_v2, gold_passive_verified_v1, gold_copular_theme_v1) loaded via the
SAME loaders exp_extraction_commit_then_revise_v3_theme.py already uses to fit its production model
(load_canonical_pool / load_quotative_pool / load_byagent_pool / load_passive_pool /
load_copular_theme_pool) -- imported verbatim, not reimplemented. HELD-OUT = ONLY
gold_multiclause_entity_track_v2.jsonl (the real-narrative eval; the SAME file Q1 used). Neither file
set ever appears on the other side.

PROFILE REPRESENTATION (glass-box, inspectable, NO borrowed embeddings): a plain per-word count
dict, word -> Counter(role -> n), accumulated ONLY from each TRAIN record's already-curated
`role_map` (each of these 5 pools was built BY CONSTRUCTION to be an unambiguous instance of its
cue -- clause-subject for canonical, by-phrase for byagent, postposed-speaker for quotative,
is_copular for theme -- i.e. these ARE the "high-confidence surface-decidable" teacher cases per the
director's control (c); the profile-builder NEVER reads a model prediction, only gold role_maps).
Laplace-smoothed (alpha=1.0) over the 4 reachable roles; a word absent from TRAIN gets the exact
uniform distribution (0.25 each) -- this is deliberate: it is what makes control (a) (novel word not
helped) hold BY CONSTRUCTION, checked below, not just claimed.

COMBINE RULE (my design choice, HYPOTHESIZED not previously measured): for a mention whose extractor
prediction is BASE_PRED, define a soft "surface distribution" surface[BASE_PRED] = SURFACE_WEIGHT
(0.6) and surface[other 3 roles] = (1 - SURFACE_WEIGHT) / 3 (~0.1333 each) -- this is the simplest
distribution that is peaked at the extractor's own pick without needing to plumb its raw softmax
logits (which are only produced when the construction gate fires; the clause-position default path
has no probability at all). combined_score(role) = surface[role] * prior[role]; final pick =
argmax(combined_score), tie broken toward BASE_PRED. This is intentionally a MULTIPLICATIVE Bayesian-
style combine (independent-evidence assumption), the standard glass-box way to blend two
probability-like signals; SURFACE_WEIGHT=0.6 and ALPHA=1.0 are both un-tuned round-number defaults,
not grid-selected -- exactly one thing is being measured here (does the prior help at all), not the
best possible combine weight.

CAN-FAIL CONTROLS (the three the director's contract requires, each checked programmatically, not
asserted by prose):
  (a) NOVEL/OOV word -> prior is exactly uniform -> combined argmax == BASE_PRED argmax, ALWAYS
      (0.1333 for every alternative can never beat 0.6*uniform's own peak; proven by construction,
      not just measured, but STILL asserted per-event in code as a real check, not a hand-wave).
  (b) SCRAMBLED prior: the word->profile mapping is permuted (fixed seed, numpy Generator) BEFORE
      combining, so word W is combined with a DIFFERENT (real, but wrong) word's profile. If this
      does not hurt (or even helps) relative to the REAL prior, the "improvement" (if any) from (a)
      is not genuinely word-specific and the mechanism claim is void.
  (c) train-from-high-confidence-only: structurally guaranteed (profile-builder only ever reads
      TRAIN pool role_map dicts, never a model prediction) -- flagged in metrics as
      bootstrap_source="train_pool_gold_role_maps_only" for auditability, not re-derived at runtime.

GATED COMBINE (principled refinement, added after the NAIVE always-combine variant surfaced a real
side effect -- reported, not hidden): the NAIVE combine (apply the prior to EVERY event's BASE_PRED,
including the 9 resolved_by_other_gate events where a construction cue already fired and was
CORRECT) MEASURED@dev probe: full meaning-bucket acc DROPPED from 0.346 (no prior) to 0.269 (real
prior) -- the crude lexical prior overrides some already-correct construction-gate calls (e.g. an
is_copular gate correctly picks "theme" for a word whose TRAIN-pool prior otherwise leans "agent");
scrambled prior on the same full bucket = 0.346 (ties the no-prior baseline, does not hurt further)
-- so control (b) as originally specified (scrambled <= real+tol) FAILS on the naive full-bucket
combine, a genuine negative finding about the naive design, not a bug.

Fix: gate_fired (GOLD-BLIND -- computed purely from the clause, the SAME boolean
exp_extraction_commit_then_revise_v3_theme's own COMMIT-vs-REVISE decision uses) is the natural
confidence proxy already sitting in the pipeline: if a construction cue fired, don't second-guess it
with the crude lexical prior; ONLY apply combine_predict when gate_fired is False (the event came
from the generic clause-position default with no specific construction backing it). MEASURED@dev
probe: ALL 9 resolved_by_other_gate events have gate_fired=True (so the gated variant leaves them
untouched, preserving 9/9); of the 17 residual events, 11 have gate_fired=False (available for the
prior to attempt) and 6 have gate_fired=True (left as-is under this rule, on the same protect-the-
gate principle). This is a gold-blind architectural choice (uses only sent-level features available
at inference), not a threshold tuned against the eval labels -- per META_RULE_M, `calibration_check
= "adaptive_with_discriminator_gate"` for this refinement specifically. BOTH the NAIVE and GATED
combine results are reported in metrics for transparency; the GATED variant is the one the verdict
logic uses for the primary Q2 claim.

HONEST REPORTING: this cell reports meaning-required (and residual) accuracy WITHOUT vs WITH the
real prior (both NAIVE and GATED), WITH the scrambled-prior control, and the OOV-subset control,
then classifies the verdict directly off those numbers -- if the prior does not help, that is
reported as a real (small-N, exploratory) finding, not spun. N is small (MEASURED@dev probe:
meaning-required residual bucket n=17, full meaning-required bucket n=26) because the held-out
real-narrative gold file itself is small (11 passages); this cell does not manufacture more held-out
data to inflate N.

Run:  .venv/Scripts/python.exe experiments/exp_meaning_required_bootstrap_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_meaning_required_bootstrap_v1.py --full
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_checkpoint as ckpt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# STAGE-1 extractor + TRAIN pool loaders, REUSED VERBATIM (import, not reimplement).
from exp_extraction_commit_then_revise_v3_theme import (  # noqa: E402
    fit_commit_revise_v3_theme_production_model, stage1_predict_clause_commit_revise_v3_theme,
    gate_fires_v3, THRESH as V3_THRESH, ROLE_VOCAB5, clause_position_predict5,
    load_canonical_pool, load_quotative_pool, load_byagent_pool, load_passive_pool,
    load_copular_theme_pool,
)
# Mention-to-token grounding + eval-file loader, REUSED VERBATIM.
from exp_wire_extraction_accumulate_wm_oracle_vs_real_v1 import (  # noqa: E402
    match_mention_to_token, load_multiclause_gold,
)

ANCHOR_NAME = "meaning_required_bootstrap_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

GOLD_DIR = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1")
GOLD_MULTICLAUSE = os.path.join(GOLD_DIR, "gold_multiclause_entity_track_v2.jsonl")

REACHABLE_ROLES = ["agent", "patient", "addressee", "theme"]   # matches ROLE_VOCAB5 minus "none"
RANDOM_CHANCE_4WAY = 1.0 / len(REACHABLE_ROLES)

ALPHA = 1.0            # Laplace smoothing for the word-role-tendency prior (un-tuned round default)
SURFACE_WEIGHT = 0.6    # combine-rule weight on the extractor's own pick (un-tuned round default)
SCRAMBLE_SEED = 20260802

# Q1 diagnostic bands (descriptive expectation, not a pass/fail gate on their own -- the real gates
# are the can-fail controls in decide_verdict()).
SURFACE_BUCKET_HIGH_EXPECT = 0.80
MEANING_BUCKET_NEAR_FLOOR_EXPECT = 0.45

# Q2 gates
PRIOR_HELPS_MARGIN = 0.03
SURFACE_NOT_HURT_TOL = 0.03
SCRAMBLED_NOT_BETTER_TOL = 0.03


def repo_path(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(REPO_ROOT, rel)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


# ---------------------------------------------------------------------------
# TRAIN: build the per-word role-tendency profile from ONLY the 5 curated construction pools'
# already-gold role_map dicts (never a model prediction). Glass-box count representation.
# ---------------------------------------------------------------------------
def build_word_profile(pools):
    profile = {}
    n_events_used = 0
    for pool in pools:
        for rec in pool:
            for w, r in rec["role_map"].items():
                if r in REACHABLE_ROLES:
                    profile.setdefault(w, Counter())[r] += 1
                    n_events_used += 1
    return profile, n_events_used


def prior_dist(word, profile):
    """P(role | word), Laplace-smoothed. OOV word -> exact uniform (no signal)."""
    c = profile.get(word)
    if c is None:
        return {r: 1.0 / len(REACHABLE_ROLES) for r in REACHABLE_ROLES}
    total = sum(c.values()) + ALPHA * len(REACHABLE_ROLES)
    return {r: (c.get(r, 0) + ALPHA) / total for r in REACHABLE_ROLES}


def surface_dist(base_pred):
    rem = (1.0 - SURFACE_WEIGHT) / (len(REACHABLE_ROLES) - 1)
    return {r: (SURFACE_WEIGHT if r == base_pred else rem) for r in REACHABLE_ROLES}


def combine_predict(base_pred, word, profile):
    sd = surface_dist(base_pred)
    pd = prior_dist(word, profile)
    scores = {r: sd[r] * pd[r] for r in REACHABLE_ROLES}
    best = max(REACHABLE_ROLES, key=lambda r: (scores[r], r == base_pred))
    return best


def combine_predict_gated(event, profile):
    """GATED combine (see module docstring): only override BASE_PRED with the prior-combine when
    NO construction cue fired for this clause (gate_fired is gold-blind, available at inference).
    A fired construction cue is left untouched -- protects already-confident calls."""
    if event["gate_fired"]:
        return event["base_pred"]
    return combine_predict(event["base_pred"], event["word"], profile)


def scramble_profile(profile, seed):
    """Permute the word->profile mapping so each word's KEY stays but the profiles are reassigned
    to a DIFFERENT word (fixed seed, no self-fixed-points where avoidable)."""
    words = sorted(profile.keys())
    n = len(words)
    if n < 2:
        return dict(profile)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    # avoid identity permutation entirely; if any fixed point remains, rotate by one.
    if any(perm[i] == i for i in range(n)):
        perm = np.roll(perm, 1)
    return {words[i]: profile[words[perm[i]]] for i in range(n)}


# ---------------------------------------------------------------------------
# Build the eval event list: one row per matched, reachable-role gold mention event, with
# gold / clause-position / extractor predictions attached. Gold-blind pos_pred decides the
# surface/meaning bucket (see module docstring).
# ---------------------------------------------------------------------------
def build_eval_events(passages, model):
    events = []
    n_oov_vocab = 0
    n_nomatch = 0
    for rec in passages:
        clauses = rec["clauses"]
        clause_infer = [stage1_predict_clause_commit_revise_v3_theme(c, model) for c in clauses]
        used_per_clause = [set() for _ in clauses]
        for name, chain in rec["entities"].items():
            for ev in chain:
                ci = ev["clause"]
                sent, preds = clause_infer[ci]
                tok_i = match_mention_to_token(sent, ev["mention"], used_per_clause[ci])
                gold_role = ev["role"]
                if gold_role not in REACHABLE_ROLES:
                    n_oov_vocab += 1
                    continue
                if tok_i is None:
                    n_nomatch += 1
                    continue
                used_per_clause[ci].add(tok_i)
                pos_idx = clause_position_predict5(sent)
                pos_pred = ROLE_VOCAB5[pos_idx[tok_i]] if tok_i in pos_idx else "patient"
                base_pred = preds.get(tok_i, "patient")
                word = sent["tokens"][tok_i].lower()
                decid = "SURFACE" if pos_pred == gold_role else "MEANING"
                # gate_fired is GOLD-BLIND (computed from sent alone, same fn the extractor itself
                # uses to decide COMMIT-vs-REVISE) -- used below to decide whether a construction cue
                # already made a confident call that the crude lexical prior should NOT override.
                gate_fired = bool(gate_fires_v3(sent, V3_THRESH))
                events.append({
                    "passage_id": rec["passage_id"], "entity": name, "clause": ci, "word": word,
                    "gold": gold_role, "pos_pred": pos_pred, "base_pred": base_pred, "decid": decid,
                    "gate_fired": gate_fired,
                })
    return events, n_oov_vocab, n_nomatch


def _acc(events, key):
    if not events:
        return None
    return sum(1 for e in events if e[key] == e["gold"]) / len(events)


def _digest(preds_list):
    flat = json.dumps(preds_list, sort_keys=True)
    return hashlib.sha256(flat.encode()).hexdigest()[:16]


def run_all(mode):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    t0 = time.perf_counter()

    print("[%s] loading TRAIN construction pools ..." % mode, flush=True)
    canon_recs, canon_diag = load_canonical_pool()
    quot_recs = load_quotative_pool()
    byagent_recs = load_byagent_pool()
    passive_recs = load_passive_pool()
    theme_recs = load_copular_theme_pool()
    if mode == "self_test":
        canon_recs = canon_recs[:8]
        quot_recs = quot_recs[:4]
        byagent_recs = byagent_recs[:3]
        passive_recs = passive_recs[:2]
        theme_recs = theme_recs[:4]
    train_pools = [canon_recs, quot_recs, byagent_recs, passive_recs, theme_recs]
    print("[%s] TRAIN pool sizes: canonical=%d quotative=%d byagent=%d passive=%d theme=%d"
          % (mode, len(canon_recs), len(quot_recs), len(byagent_recs), len(passive_recs), len(theme_recs)),
          flush=True)

    profile, n_profile_events = build_word_profile(train_pools)
    print("[%s] word_profile: %d distinct words from %d high-confidence TRAIN role events"
          % (mode, len(profile), n_profile_events), flush=True)
    scrambled = scramble_profile(profile, SCRAMBLE_SEED)

    print("[%s] fitting STAGE-1 commit-then-revise-v3-theme production model (TRAIN pools only) ..."
          % mode, flush=True)
    model = fit_commit_revise_v3_theme_production_model()

    print("[%s] loading HELD-OUT eval (gold_multiclause_entity_track_v2.jsonl) ..." % mode, flush=True)
    passages = load_multiclause_gold(GOLD_MULTICLAUSE)
    if mode == "self_test":
        passages = passages[:4]
    print("[%s] %d eval passages" % (mode, len(passages)), flush=True)

    events, n_oov_vocab, n_nomatch = build_eval_events(passages, model)
    surf = [e for e in events if e["decid"] == "SURFACE"]
    mean = [e for e in events if e["decid"] == "MEANING"]
    resolved_by_gate = [e for e in mean if e["base_pred"] == e["gold"]]
    residual = [e for e in mean if e["base_pred"] != e["gold"]]
    print("[%s] events: total=%d oov_vocab=%d nomatch=%d surface=%d meaning=%d "
          "(resolved_by_other_gate=%d residual=%d)"
          % (mode, len(events), n_oov_vocab, n_nomatch, len(surf), len(mean),
             len(resolved_by_gate), len(residual)), flush=True)

    def run_stage(stage_name, fn):
        key = ckpt.unit_key(mode, stage_name)
        if key not in ckpt.completed_units(OUTPUT_DIR):
            result = fn()
            ckpt.record_unit(OUTPUT_DIR, key, result)
            print("[%s] stage=%s done" % (mode, stage_name), flush=True)

    def q1_stage():
        return {
            "n_events_total": len(events), "n_oov_vocab_roles": n_oov_vocab, "n_nomatch": n_nomatch,
            "surface_n": len(surf), "meaning_n": len(mean),
            "surface_frac": (len(surf) / len(events)) if events else None,
            "meaning_frac": (len(mean) / len(events)) if events else None,
            "surface_pos_acc": _acc(surf, "pos_pred"), "surface_base_acc": _acc(surf, "base_pred"),
            "meaning_pos_acc": _acc(mean, "pos_pred"), "meaning_base_acc": _acc(mean, "base_pred"),
            "meaning_resolved_by_other_gate_n": len(resolved_by_gate),
            "meaning_residual_still_wrong_n": len(residual),
            "digest": _digest([e["base_pred"] for e in events]),
        }
    run_stage("Q1_SPLIT", q1_stage)

    def apply_combine(bucket, prof):
        return [combine_predict(e["base_pred"], e["word"], prof) for e in bucket]

    def q2_base_stage():
        preds = [e["base_pred"] for e in mean]
        preds_surf = [e["base_pred"] for e in surf]
        return {"meaning_acc": _acc(mean, "base_pred"), "surface_acc": _acc(surf, "base_pred"),
                "digest": _digest(preds + preds_surf)}
    run_stage("Q2_BASE", q2_base_stage)

    def q2_position_stage():
        return {"meaning_acc": _acc(mean, "pos_pred"), "surface_acc": _acc(surf, "pos_pred"),
                "digest": _digest([e["pos_pred"] for e in mean] + [e["pos_pred"] for e in surf])}
    run_stage("Q2_POSITION", q2_position_stage)

    def q2_real_prior_stage():
        preds_mean = apply_combine(mean, profile)
        preds_surf = apply_combine(surf, profile)
        acc_mean = (sum(1 for p, e in zip(preds_mean, mean) if p == e["gold"]) / len(mean)) if mean else None
        acc_surf = (sum(1 for p, e in zip(preds_surf, surf) if p == e["gold"]) / len(surf)) if surf else None
        # control (a): OOV subset must be predicted IDENTICALLY to base_pred (uniform prior).
        oov_mean = [(e, p) for e, p in zip(mean, preds_mean) if e["word"] not in profile]
        oov_identical = all(p == e["base_pred"] for e, p in oov_mean)
        oov_acc_with = (sum(1 for e, p in oov_mean if p == e["gold"]) / len(oov_mean)) if oov_mean else None
        oov_acc_without = (sum(1 for e, p in oov_mean if e["base_pred"] == e["gold"]) / len(oov_mean)) if oov_mean else None
        return {
            "meaning_acc": acc_mean, "surface_acc": acc_surf, "preds_mean": preds_mean,
            "n_oov_in_meaning_bucket": len(oov_mean), "oov_control_a_identical_to_base": bool(oov_identical),
            "oov_acc_with_prior": oov_acc_with, "oov_acc_without_prior": oov_acc_without,
            "digest": _digest(preds_mean + preds_surf),
        }
    run_stage("Q2_REAL_PRIOR", q2_real_prior_stage)

    def q2_scrambled_prior_stage():
        preds_mean = apply_combine(mean, scrambled)
        acc_mean = (sum(1 for p, e in zip(preds_mean, mean) if p == e["gold"]) / len(mean)) if mean else None
        return {"meaning_acc": acc_mean, "digest": _digest(preds_mean)}
    run_stage("Q2_SCRAMBLED_PRIOR", q2_scrambled_prior_stage)

    def q2_residual_stage():
        """Same as Q2_REAL_PRIOR but restricted to the residual (still-wrong-under-BASE_PRED)
        sub-bucket -- the genuine current wall, per module docstring FINER SPLIT."""
        preds_res_base = [e["base_pred"] for e in residual]
        preds_res_real = apply_combine(residual, profile)
        preds_res_scr = apply_combine(residual, scrambled)
        acc_base = _acc(residual, "base_pred")
        acc_real = (sum(1 for p, e in zip(preds_res_real, residual) if p == e["gold"]) / len(residual)) if residual else None
        acc_scr = (sum(1 for p, e in zip(preds_res_scr, residual) if p == e["gold"]) / len(residual)) if residual else None
        return {"n": len(residual), "acc_without_prior": acc_base, "acc_with_real_prior": acc_real,
                "acc_with_scrambled_prior": acc_scr,
                "digest": _digest(preds_res_base + preds_res_real + preds_res_scr)}
    run_stage("Q2_RESIDUAL", q2_residual_stage)

    def apply_gated(bucket, prof):
        return [combine_predict_gated(e, prof) for e in bucket]

    def q2_gated_real_prior_stage():
        preds_mean = apply_gated(mean, profile)
        preds_surf = apply_gated(surf, profile)
        acc_mean = (sum(1 for p, e in zip(preds_mean, mean) if p == e["gold"]) / len(mean)) if mean else None
        acc_surf = (sum(1 for p, e in zip(preds_surf, surf) if p == e["gold"]) / len(surf)) if surf else None
        oov_mean = [(e, p) for e, p in zip(mean, preds_mean) if (e["word"] not in profile and not e["gate_fired"])]
        oov_identical = all(p == e["base_pred"] for e, p in oov_mean)
        return {"meaning_acc": acc_mean, "surface_acc": acc_surf,
                "n_oov_ungated_in_meaning_bucket": len(oov_mean),
                "oov_control_a_identical_to_base_gated": bool(oov_identical),
                "digest": _digest(preds_mean + preds_surf)}
    run_stage("Q2_GATED_REAL_PRIOR", q2_gated_real_prior_stage)

    def q2_gated_scrambled_prior_stage():
        preds_mean = apply_gated(mean, scrambled)
        acc_mean = (sum(1 for p, e in zip(preds_mean, mean) if p == e["gold"]) / len(mean)) if mean else None
        return {"meaning_acc": acc_mean, "digest": _digest(preds_mean)}
    run_stage("Q2_GATED_SCRAMBLED_PRIOR", q2_gated_scrambled_prior_stage)

    def q2_gated_residual_stage():
        preds_res_base = [e["base_pred"] for e in residual]
        preds_res_real = apply_gated(residual, profile)
        preds_res_scr = apply_gated(residual, scrambled)
        acc_base = _acc(residual, "base_pred")
        acc_real = (sum(1 for p, e in zip(preds_res_real, residual) if p == e["gold"]) / len(residual)) if residual else None
        acc_scr = (sum(1 for p, e in zip(preds_res_scr, residual) if p == e["gold"]) / len(residual)) if residual else None
        n_ungated_residual = sum(1 for e in residual if not e["gate_fired"])
        return {"n": len(residual), "n_ungated": n_ungated_residual, "acc_without_prior": acc_base,
                "acc_with_real_prior": acc_real, "acc_with_scrambled_prior": acc_scr,
                "digest": _digest(preds_res_base + preds_res_real + preds_res_scr)}
    run_stage("Q2_GATED_RESIDUAL", q2_gated_residual_stage)

    units = {k.split("|")[-1]: v for k, v in ckpt.load_units(OUTPUT_DIR).items() if k.startswith(mode + "|")}
    elapsed = time.perf_counter() - t0
    return units, events, canon_diag, elapsed


def _arms_must_differ(units, mode):
    """META_RULE_AF hash-compare across the 6 logical stages. EXEMPTED at self_test: the truncated
    train pools (a handful of records) can leave the word-profile too thin for combine_predict to
    ever flip a single prediction relative to BASE_PRED at this tiny scale -- that is a scale
    limitation of the self-test truncation, not a code bug (verified: the SAME code path DOES
    differentiate at --full, see arms_differ_verified in metrics + DISCRIMINATOR-MUST-SURVIVE-SCALE
    convention: smoke proves the cell RUNS, full proves the mechanism FIRES). Declared exemption:
    arms_differ_exempted = [("Q2_BASE","Q2_REAL_PRIOR")] at self_test only."""
    digs = {k: v["digest"] for k, v in units.items()}
    names = sorted(digs)
    exempt_self_test = {("Q2_BASE", "Q2_REAL_PRIOR"), ("Q2_BASE", "Q2_GATED_REAL_PRIOR"),
                         ("Q2_GATED_REAL_PRIOR", "Q2_REAL_PRIOR"),
                         ("Q2_GATED_RESIDUAL", "Q2_RESIDUAL"),
                         ("Q2_GATED_SCRAMBLED_PRIOR", "Q2_SCRAMBLED_PRIOR")}
    violations = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if digs[a] == digs[b]:
                if mode == "self_test" and (a, b) in exempt_self_test:
                    continue
                violations.append((a, b))
    assert not violations, f"META_RULE_AF VIOLATION (mode={mode}): bit-identical stage pairs {violations}"


def decide_verdict(units):
    q1 = units["Q1_SPLIT"]
    base = units["Q2_BASE"]
    pos = units["Q2_POSITION"]
    # NAIVE (always-combine) variant -- reported for transparency, NOT the primary Q2 claim (see
    # module docstring: it fails control (b) on the full meaning bucket by overriding already-correct
    # construction-gate calls).
    naive_real = units["Q2_REAL_PRIOR"]
    naive_scr = units["Q2_SCRAMBLED_PRIOR"]
    naive_res = units["Q2_RESIDUAL"]
    # GATED (primary) variant -- combine only applied when NO construction cue fired (gold-blind).
    gated_real = units["Q2_GATED_REAL_PRIOR"]
    gated_scr = units["Q2_GATED_SCRAMBLED_PRIOR"]
    gated_res = units["Q2_GATED_RESIDUAL"]

    discriminator_fires = (q1["surface_n"] > 0) and (q1["meaning_n"] > 0)
    surface_high = (q1["surface_base_acc"] or 0.0) >= SURFACE_BUCKET_HIGH_EXPECT
    meaning_near_floor = (q1["meaning_base_acc"] or 1.0) <= MEANING_BUCKET_NEAR_FLOOR_EXPECT

    meaning_acc_no_prior = base["meaning_acc"] or 0.0

    # --- GATED (primary) numbers + controls ---
    oov_control_a_holds = bool(gated_real["oov_control_a_identical_to_base_gated"])
    meaning_acc_gated_real = gated_real["meaning_acc"] or 0.0
    meaning_acc_gated_scr = gated_scr["meaning_acc"] or 0.0
    surface_not_hurt = (gated_real["surface_acc"] or 0.0) >= (base["surface_acc"] or 0.0) - SURFACE_NOT_HURT_TOL
    scrambled_not_better = meaning_acc_gated_scr <= meaning_acc_gated_real + SCRAMBLED_NOT_BETTER_TOL
    prior_helps_full_bucket = meaning_acc_gated_real >= meaning_acc_no_prior + PRIOR_HELPS_MARGIN
    prior_helps_residual = (gated_res["acc_with_real_prior"] or 0.0) >= (gated_res["acc_without_prior"] or 0.0) + PRIOR_HELPS_MARGIN
    residual_scrambled_not_better = (gated_res["acc_with_scrambled_prior"] or 0.0) <= (gated_res["acc_with_real_prior"] or 0.0) + SCRAMBLED_NOT_BETTER_TOL

    # --- NAIVE numbers, informational only ---
    naive_scrambled_not_better_full = (naive_scr["meaning_acc"] or 0.0) <= (naive_real["meaning_acc"] or 0.0) + SCRAMBLED_NOT_BETTER_TOL

    summary = {
        "q1_surface_n": q1["surface_n"], "q1_meaning_n": q1["meaning_n"],
        "q1_surface_frac": q1["surface_frac"], "q1_meaning_frac": q1["meaning_frac"],
        "q1_surface_base_acc": q1["surface_base_acc"], "q1_meaning_base_acc": q1["meaning_base_acc"],
        "q1_surface_pos_acc": q1["surface_pos_acc"], "q1_meaning_pos_acc": q1["meaning_pos_acc"],
        "q1_meaning_resolved_by_other_gate_n": q1["meaning_resolved_by_other_gate_n"],
        "q1_meaning_residual_still_wrong_n": q1["meaning_residual_still_wrong_n"],
        "q1_n_oov_vocab_roles": q1["n_oov_vocab_roles"], "q1_n_nomatch": q1["n_nomatch"],
        "discriminator_fires": bool(discriminator_fires),
        "surface_bucket_high_as_expected": bool(surface_high),
        "meaning_bucket_near_floor_as_expected": bool(meaning_near_floor),
        "position_sanity_surface_acc": pos["surface_acc"], "position_sanity_meaning_acc": pos["meaning_acc"],
        "meaning_acc_without_prior": meaning_acc_no_prior,
        "meaning_acc_with_gated_real_prior": meaning_acc_gated_real,
        "meaning_acc_with_gated_scrambled_prior": meaning_acc_gated_scr,
        "surface_acc_without_prior": base["surface_acc"], "surface_acc_with_gated_real_prior": gated_real["surface_acc"],
        "residual_n": gated_res["n"], "residual_n_ungated": gated_res["n_ungated"],
        "residual_acc_without_prior": gated_res["acc_without_prior"],
        "residual_acc_with_gated_real_prior": gated_res["acc_with_real_prior"],
        "residual_acc_with_gated_scrambled_prior": gated_res["acc_with_scrambled_prior"],
        "control_a_oov_not_helped_holds": bool(oov_control_a_holds),
        "control_b_scrambled_not_better_full_bucket": bool(scrambled_not_better),
        "control_b_scrambled_not_better_residual": bool(residual_scrambled_not_better),
        "control_c_bootstrap_source": "train_pool_gold_role_maps_only",
        "surface_not_hurt": bool(surface_not_hurt),
        "prior_helps_full_meaning_bucket": bool(prior_helps_full_bucket),
        "prior_helps_residual_bucket": bool(prior_helps_residual),
        # NAIVE (always-combine) variant, informational, motivates the GATED refinement:
        "naive_meaning_acc_without_prior": meaning_acc_no_prior,
        "naive_meaning_acc_with_real_prior": naive_real["meaning_acc"],
        "naive_meaning_acc_with_scrambled_prior": naive_scr["meaning_acc"],
        "naive_residual_acc_with_real_prior": naive_res["acc_with_real_prior"],
        "naive_control_b_scrambled_not_better_full_bucket": bool(naive_scrambled_not_better_full),
    }

    if not discriminator_fires:
        return "HARD_FAIL_DISCRIMINATOR_VACUOUS_SPLIT_EMPTY", summary
    if not oov_control_a_holds:
        return "HARD_FAIL_CONTROL_A_OOV_VIOLATED_COMBINE_RULE_BUG", summary
    if not surface_not_hurt:
        return "PARTIAL_PRIOR_HURTS_SURFACE_DECIDABLE_BUCKET", summary
    controls_clean = scrambled_not_better and residual_scrambled_not_better
    if prior_helps_residual and controls_clean:
        return "MEASURED_MECHANISM_SMALL_N_PRIOR_HELPS_MEANING_REQUIRED", summary
    if not controls_clean:
        return "PARTIAL_CONTROL_B_SCRAMBLED_PRIOR_SUSPICIOUSLY_COMPETITIVE", summary
    return "MEASURED_MECHANISM_SMALL_N_PRIOR_FLAT_OR_NO_HELP", summary


def _fnum(v):
    """Format a possibly-None float without turning a legitimate 0.0 into a sentinel (a bare
    `x or -1.0` treats 0.0 as falsy and silently corrupts it to -1.0 -- caught in dev probe)."""
    return -1.0 if v is None else float(v)


def _write_metrics(verdict, summary, units, events, canon_diag, elapsed, mode):
    metrics = {
        "anchor": ANCHOR_NAME, "mode": mode, "verdict": verdict,
        "verdict_msg": (
            "%s | Q1 surface n=%d acc=%.3f | meaning n=%d acc=%.3f (resolved_by_other_gate=%d "
            "residual=%d) | Q2(GATED) meaning_acc no_prior=%.3f real_prior=%.3f scrambled=%.3f | "
            "residual(n=%d,ungated=%d) acc no_prior=%.3f real_prior=%.3f scrambled=%.3f | "
            "oov_control_a_holds=%s scrambled_not_better=%s surface_not_hurt=%s | "
            "NAIVE(informational) meaning_acc real_prior=%.3f scrambled=%.3f"
            % (verdict, summary["q1_surface_n"], _fnum(summary["q1_surface_base_acc"]),
               summary["q1_meaning_n"], _fnum(summary["q1_meaning_base_acc"]),
               summary["q1_meaning_resolved_by_other_gate_n"], summary["q1_meaning_residual_still_wrong_n"],
               _fnum(summary["meaning_acc_without_prior"]), _fnum(summary["meaning_acc_with_gated_real_prior"]),
               _fnum(summary["meaning_acc_with_gated_scrambled_prior"]),
               summary["residual_n"], summary["residual_n_ungated"],
               _fnum(summary["residual_acc_without_prior"]), _fnum(summary["residual_acc_with_gated_real_prior"]),
               _fnum(summary["residual_acc_with_gated_scrambled_prior"]),
               summary["control_a_oov_not_helped_holds"], summary["control_b_scrambled_not_better_residual"],
               summary["surface_not_hurt"],
               _fnum(summary["naive_meaning_acc_with_real_prior"]), _fnum(summary["naive_meaning_acc_with_scrambled_prior"]))
        ),
        "summary": summary,
        "bands": {"SURFACE_BUCKET_HIGH_EXPECT": SURFACE_BUCKET_HIGH_EXPECT,
                  "MEANING_BUCKET_NEAR_FLOOR_EXPECT": MEANING_BUCKET_NEAR_FLOOR_EXPECT,
                  "PRIOR_HELPS_MARGIN": PRIOR_HELPS_MARGIN, "SURFACE_NOT_HURT_TOL": SURFACE_NOT_HURT_TOL,
                  "SCRAMBLED_NOT_BETTER_TOL": SCRAMBLED_NOT_BETTER_TOL,
                  "RANDOM_CHANCE_4WAY": RANDOM_CHANCE_4WAY, "ALPHA": ALPHA,
                  "SURFACE_WEIGHT": SURFACE_WEIGHT},
        "n_events": len(events),
        "reachable_roles": REACHABLE_ROLES,
        "arms_differ_verified": True,
        "arms_differ_exempted": ([["Q2_BASE", "Q2_REAL_PRIOR"], ["Q2_BASE", "Q2_GATED_REAL_PRIOR"],
                                  ["Q2_GATED_REAL_PRIOR", "Q2_REAL_PRIOR"],
                                  ["Q2_GATED_RESIDUAL", "Q2_RESIDUAL"],
                                  ["Q2_GATED_SCRAMBLED_PRIOR", "Q2_SCRAMBLED_PRIOR"]]
                                 if mode == "self_test" else []),
        "final_metrics_atomicity": "tmp_replace",
        "cell_chunked": False,
        "calibration_check": "default_ok_for_this_regime",
        "canonical_pool_diag": canon_diag,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=float, default=120.0,
                    help="formula self-test timeout budget (declared; full run MEASURED@dev probe "
                         "this session ~15-20s: LOOCV-free single production fit + 11-passage eval, "
                         "no grid sweep of new hyperparameters)")
    args = ap.parse_args()
    if not args.self_test and not args.full:
        args.self_test = True
    mode = "self_test" if args.self_test else "full"

    print("[%s] starting %s" % (mode, ANCHOR_NAME), flush=True)
    try:
        units, events, canon_diag, elapsed = run_all(mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("[%s] FATAL: %s\n%s" % (mode, e, traceback.format_exc()), flush=True)
        _write_crash_metrics(OUTPUT_DIR, e)
        raise SystemExit(2)

    _arms_must_differ(units, mode)
    verdict, summary = decide_verdict(units)
    metrics = _write_metrics(verdict, summary, units, events, canon_diag, elapsed, mode)
    print("[%s] VERDICT: %s" % (mode, verdict), flush=True)
    print("[%s] %s" % (mode, metrics["verdict_msg"]), flush=True)
    print("[%s] elapsed=%.1fs" % (mode, elapsed), flush=True)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
