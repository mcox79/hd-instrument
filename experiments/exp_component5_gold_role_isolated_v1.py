"""exp_component5_gold_role_isolated_v1 -- Component-5 GOLD-ROLE-ISOLATED goal-owner + outcome-
binding eval: given GOLD (Component-3-shaped) role labels, does a role-content-aware candidate
generator + the existing gold-free route_passage/decode_coherence_margins/decide_keep_or_revert
selector (hdlab/self_improving_loop.py, promoted 2026-08-02) beat pure recency on goal-owner /
outcome binding? This is the make-or-break density-gating check named by BOTH design docs:
notes/research_component5_goal_owner_selection_binding_2026-08-04.md (mechanism/reuse map) and
notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md (Section 6, "Instance C
(goal-outcome) -- first buildable step ... has NOT been ruled out for goal-outcome" per Section 7's
named risk: decode_coherence_margins is PROVEN wrong for causal antecedent selection because
CausalLinkRegister write-then-read is symmetric; whether goal-outcome binding shares that same
symmetric-write failure is exactly what this cell settles).

PRE-REG: preregs/2026-08-04_component5_gold_role_isolated_v1.md

Prior-work check (SUBSTRATE-KB, mandatory before authoring): `tools/substrate_query.sh "goal owner
selection coherence binding recency outcome"` returned notes/WHERE_WE_ARE_NOW.md (cosine=0.4014),
notes/director_POST_COMPACTION_BACKUP_2026-08-04.md (cosine=0.3965/0.3906), and
notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md (cosine=0.3877) -- all
above the 0.30 threshold. Both notes/*_2026-08-04.md docs were READ IN FULL before writing this
cell: this eval IS the "first buildable step" the build-spec names (Section 6.1: "Instance C
(goal-outcome) -- zero new hdlab code, only a harness wiring decode_coherence_margins to the
goal-outcome role vocab + candidate-owner cluster_ids ... first harden the item set into a true
recency-trap before scoring it") -- NOT a rediscovery. The RECENCY item set in
exp_situation_model_goal_outcome_dimension_v1.py already satisfies the "harden into a true
recency-trap" prerequisite (2 genuine traps + 1 sanity item, verified by reading the item texts).

GOLD-ROLE ISOLATION (per task brief): Component-3's thematic-role perceptron is still in flight
(3c). This eval bypasses it entirely -- role labels come from the SAME lexicon-based typing
(type_sentence_events, GO_ROLES) the fb5b2a188 cell already uses, reused bit-identical, which is a
GOLD (hand/lexicon-derived, not learned/noisy) role signal for these items. This isolates
Component-5's SELECTION mechanism from Component-3's OWN accuracy, per the design drill's explicit
recommendation (Section (e): "Recommend running the gold-role isolation FIRST regardless of
Component-3's 3c status").

MECHANISM (glass-box, reuses 3 organs bit-identical, adds ONE new ~30-line candidate generator):
  1. BASELINE candidate = RecencyEntityResolver (reused verbatim from fb5b2a188, unchanged):
     backward-search, first gender-compatible entity by recency -- the KNOWN falsified failure
     mode (MEMORY 2026-08-03, coref 0/4).
  2. CONTENT candidate = NEW ContentMatchResolver (this cell): tracks entities carrying an OPEN
     GOAL (a GOAL-role event with no OUTCOME yet bound); on an ambiguous pronoun, prefers a
     gender-compatible OPEN-GOAL entity over recency; falls back to recency if none (honest
     fallback, not a forced win).
  3. SELECTOR = hdlab.self_improving_loop.route_passage (reused verbatim): scores both candidates'
     whole-passage resolutions via decode_coherence_margins over role_vocab=GO_ROLES (the 4-symbol
     GOAL/ACTION_AGAINST/OUTCOME_UNMET/OUTCOME_MET vocab -- the richer role-content signal named as
     the missing wire in both design docs, vs the 2-symbol agent/mentioned vocab route_passage was
     validated on before), adopts CONTENT iff its aggregate coherence-margin delta clears the
     abstain band (0.02, unchanged default).

CONTROLS: anti-recency (both real traps have gold-owner != most-recent entity, by construction);
role-scramble (mislabel the GOAL holder as the foil, text/gold unchanged -- must COLLAPSE accuracy
if the selector is genuinely content-driven, else it is the same positional-confound failure mode
as _pick_strict_cb); control false-fire (unchanged CONTROLS items must stay 0/6); sign check
(route_passage's own gold-free agg_coherence_delta must be positive on genuine traps).

BANDS (VERBATIM per task brief + pre-reg):
  HARD-PASS  -> outcome_binding_accuracy>=0.67 AND role_scramble_collapse holds AND
                control_false_fire_rate==0 AND goal_owner_binding_accuracy>=5/6.
  MIDDLE     -> outcome_binding_accuracy in [0.334,0.66] OR scramble partially collapses.
  HARD-FAIL  -> outcome_binding_accuracy<=0.333 OR role_scramble_collapse fails.
  SMALL-N CAP (VET-as-hard-as-negative): N=3 recency items -> a formal HARD-PASS is REPORTED as
  MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS (mechanism-class license, not landed statistical result);
  HARD-FAIL is NOT capped (a clean small-N negative is still informative evidence).

GUARDS: glass-box; RecencyEntityResolver / type_sentence_events / GO_ROLES / route_passage /
decode_coherence_margins / decide_keep_or_revert reused bit-identical; deterministic given seed;
ASCII-only; atomic metrics write; NOT dispatched to any queue (LOCAL-ONLY, in-process foreground
per task brief, no push).

Cites: notes/research_component5_goal_owner_selection_binding_2026-08-04.md;
notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md;
experiments/exp_situation_model_goal_outcome_dimension_v1.py (item bank, fb5b2a188, 0.333 recency
floor); hdlab/self_improving_loop.py (route_passage, promoted 2026-08-02).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "component5_gold_role_isolated_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import torch  # noqa: E402

# ---- REUSED BIT-IDENTICAL: item bank, lexicon typing, recency resolver, register ---------------
from exp_situation_model_goal_outcome_dimension_v1 import (  # noqa: E402
    GOAL_BLOCK, CONTROLS, RECENCY, GO_ROLES, R_GOAL, R_UNMET, R_MET,
    RecencyEntityResolver, type_sentence_events, treatment_fires, _sentences, _ordered_tokens,
    GENDER, ANIMATE_NAMES, PRON_F, PRON_M,
)
# ---- REUSED BIT-IDENTICAL: the gold-free coherence-margin selector (2026-08-02 promotion) -------
from hdlab.self_improving_loop import route_passage, ABSTAIN_BAND_DEFAULT  # noqa: E402

D2 = 1024
SEEDS = [0, 1, 2]

# GOLD foil (the entity mentioned more recently than the true goal-owner) for each real trap item.
FOILS = {
    "recency_amy_blocked_pronoun_foil_jo": "jo",
    "recency_tom_blocked_pronoun_foil_sid": "sid",
}


# ============================================================================ NEW candidate generator
class ContentMatchResolver:
    """The ONE genuinely new piece (per both design docs): tracks entities carrying an OPEN GOAL
    (a GOAL-role event with no OUTCOME bound yet, GOLD-typed via type_sentence_events reused
    bit-identical) and prefers such an entity over pure recency when resolving an ambiguous
    pronoun. Falls back to recency if no open-goal entity is gender-compatible (honest fallback --
    this resolver does NOT force a non-recency answer, it only makes one constructible when
    content supports it, per design drill (d).2)."""

    def __init__(self):
        self._recent = []       # entity names in mention order (mirrors RecencyEntityResolver)
        self._open_goal = set()  # entities with an unresolved (no-outcome-yet) GOAL event

    def subject_entity(self, sentence: str):
        toks = _ordered_tokens(sentence)
        for t in toks:                                   # explicit NAME = subject (unambiguous)
            if t in ANIMATE_NAMES:
                self._note(t)
                return t
        for t in toks:                                   # pronoun -> content-match, else recency
            if t in PRON_F or t in PRON_M:
                want = "f" if t in PRON_F else "m"
                compatible = [e for e in self._recent if GENDER.get(e) == want]
                open_goal_compatible = [e for e in compatible if e in self._open_goal]
                if open_goal_compatible:
                    return open_goal_compatible[-1]       # prefer content (open-goal), not position
                for e in reversed(compatible):             # honest fallback: recency within pool
                    return e
                return None
        return None

    def _note(self, entity: str):
        if entity not in self._recent:
            self._recent.append(entity)

    def mark_role(self, entity: str, role: str):
        """Called by the caller AFTER typing a sentence's events, so later pronouns see the
        updated open-goal state (causal order matches the design: resolve subject -> type events
        -> update state -> next sentence)."""
        if role == R_GOAL:
            self._open_goal.add(entity)
        elif role in (R_UNMET, R_MET):
            self._open_goal.discard(entity)


def build_positions(item: dict, resolver, scramble_owner_to_foil: str | None = None):
    """Walk item['text'] sentence-by-sentence, resolving subject via `resolver` and typing events
    via type_sentence_events (reused bit-identical). Returns (role_seq, cluster_ids, event_slots).
    event_slots = GLOBAL POSITION INDEX (deliberate, see pre-reg "Mechanism" #4): candidate
    reassignment changes an entity's own next-slot number under a per-entity scheme, so global-
    position slotting keeps role_seq/event_slots identical across candidates -- only cluster_ids
    (the entity assignment) varies, matching route_passage's documented contract.
    If scramble_owner_to_foil is set, any GOAL-role event whose true subject is the item's owner
    is relabeled to that foil entity instead (role-scramble control -- text/gold unchanged)."""
    owner = item.get("owner")
    role_seq, cluster_ids = [], []
    for sent in _sentences(item["text"]):
        subj = resolver.subject_entity(sent)
        ev, _info = type_sentence_events(sent, subj)
        for (entity, role) in ev:
            eff_entity = entity
            if scramble_owner_to_foil is not None and role == R_GOAL and entity == owner:
                eff_entity = scramble_owner_to_foil
            role_seq.append(role)
            cluster_ids.append(eff_entity)
            if hasattr(resolver, "mark_role"):
                resolver.mark_role(eff_entity, role)
    event_slots = list(range(len(role_seq)))
    return role_seq, cluster_ids, event_slots


# ============================================================================ per-item eval
def run_recency_item(item: dict, seed: int, scrambled: bool):
    """Run the selector on one RECENCY item. If scrambled, the CONTENT candidate's GOAL label is
    mislabeled onto the foil (role-scramble control)."""
    role_seq_b, cluster_ids_b, event_slots_b = build_positions(item, RecencyEntityResolver())
    foil = FOILS.get(item["id"])
    scramble_target = foil if (scrambled and foil is not None) else None
    role_seq_c, cluster_ids_c, event_slots_c = build_positions(
        item, ContentMatchResolver(), scramble_owner_to_foil=scramble_target)

    assert role_seq_b == role_seq_c, (
        f"role sequences diverged between resolvers on {item['id']!r}: "
        f"{role_seq_b} vs {role_seq_c} (lexicon typing must be resolver-independent)")
    assert event_slots_b == event_slots_c

    outcome_positions = [i for i, r in enumerate(role_seq_b) if r in (R_UNMET, R_MET)]
    flagged = [i for i in outcome_positions if cluster_ids_b[i] != cluster_ids_c[i]]
    if not flagged:
        flagged = list(outcome_positions)  # no disagreement (e.g. the sanity item); route trivially

    gen_factory = (lambda: torch.Generator().manual_seed(3000 + int(seed)))
    result = route_passage(
        role_seq=role_seq_b, event_slots=event_slots_b, baseline_cluster_ids=cluster_ids_b,
        candidate_cluster_ids={"content_match": cluster_ids_c}, flagged_positions=flagged,
        role_vocab=list(GO_ROLES), d=D2, generator_factory=gen_factory,
        max_event_slots=len(role_seq_b) + 1, abstain_band=ABSTAIN_BAND_DEFAULT,
    )
    adopted = result["adopted_cluster_ids"]
    final_owner = adopted[outcome_positions[-1]] if outcome_positions else None
    baseline_owner = cluster_ids_b[outcome_positions[-1]] if outcome_positions else None
    content_owner = cluster_ids_c[outcome_positions[-1]] if outcome_positions else None
    gold = item["gold_outcome_owner"]
    return dict(
        id=item["id"], scrambled=scrambled, gold_outcome_owner=gold,
        baseline_owner=baseline_owner, content_owner=content_owner, final_owner=final_owner,
        matches_gold=(final_owner == gold),
        recency_alone_matches_gold=(baseline_owner == gold),
        overrode_recency=(final_owner != baseline_owner),
        adopt=result["adopt"], per_candidate=result["per_candidate"],
        agg_coherence_delta=result["per_candidate"].get("content_match", {}).get("agg_coherence_delta"),
        n_changed_flagged=result["per_candidate"].get("content_match", {}).get("n_changed_flagged"),
    )


def run_goal_owner_binding(item: dict):
    """goal_owner_binding_accuracy (GOAL_BLOCK, gold explicit-name attribution): same-clause
    binding, GIVEN not EARNED -- Component-3 already solves this (no cross-sentence search), per
    the design drill. Reported honestly as a supplied-not-mechanism-tested number."""
    role_seq, cluster_ids, _ = build_positions(item, RecencyEntityResolver())
    goal_positions = [i for i, r in enumerate(role_seq) if r == R_GOAL]
    if not goal_positions:
        return dict(id=item["id"], has_goal_event=False, matches_owner=None)
    holder = cluster_ids[goal_positions[0]]
    return dict(id=item["id"], has_goal_event=True, matches_owner=(holder == item["owner"]))


# ============================================================================ per-seed unit
def run_seed(seed: int):
    recency_rows = [run_recency_item(it, seed, scrambled=False) for it in RECENCY]
    scramble_rows = [run_recency_item(it, seed, scrambled=True) for it in RECENCY if it["id"] in FOILS]
    goal_owner_rows = [run_goal_owner_binding(it) for it in GOAL_BLOCK]
    control_rows = []
    for it in CONTROLS:
        owner = it["owner"] if it["owner"] is not None else "__none__"
        fired, _ap, _per_sent = treatment_fires(it["text"], owner, seed)
        control_rows.append(dict(id=it["id"], cls=it["cls"], fired=bool(fired)))

    n_rec = len(recency_rows)
    outcome_binding_accuracy = round(sum(r["matches_gold"] for r in recency_rows) / n_rec, 4)
    n_scr = len(scramble_rows)
    scrambled_outcome_binding_accuracy = (
        round(sum(r["matches_gold"] for r in scramble_rows) / n_scr, 4) if n_scr else None)
    n_owner = sum(1 for r in goal_owner_rows if r["has_goal_event"])
    goal_owner_binding_accuracy = (
        round(sum(1 for r in goal_owner_rows if r["matches_owner"]) / n_owner, 4) if n_owner else None)
    control_false_fire_rate = round(sum(r["fired"] for r in control_rows) / len(control_rows), 4)

    trap_rows = [r for r in recency_rows if r["id"] in FOILS]
    anti_recency_holds = all(r["matches_gold"] for r in trap_rows) if trap_rows else None
    deltas = [r["agg_coherence_delta"] for r in trap_rows if r["agg_coherence_delta"] is not None]
    coherence_margin_delta_sign_positive = (all(d_ > 0 for d_ in deltas) if deltas else None)

    return dict(
        seed=seed,
        outcome_binding_accuracy=outcome_binding_accuracy,
        scrambled_outcome_binding_accuracy=scrambled_outcome_binding_accuracy,
        goal_owner_binding_accuracy=goal_owner_binding_accuracy,
        control_false_fire_rate=control_false_fire_rate,
        anti_recency_holds=anti_recency_holds,
        coherence_margin_delta_sign_positive=coherence_margin_delta_sign_positive,
        recency_rows=recency_rows, scramble_rows=scramble_rows,
        goal_owner_rows=goal_owner_rows, control_rows=control_rows,
    )


# ============================================================================ aggregate + verdict
def aggregate(per_seed: dict):
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def all_equal(key):
        vals = [per_seed[s][key] for s in seeds]
        return vals[0] if len(set(vals)) == 1 else None  # mechanism is deterministic given seed;
                                                            # margin ties could vary -- surface if so

    outcome_acc_per_seed = [per_seed[s]["outcome_binding_accuracy"] for s in seeds]
    scramble_acc_per_seed = [per_seed[s]["scrambled_outcome_binding_accuracy"] for s in seeds]
    outcome_binding_accuracy = round(sum(outcome_acc_per_seed) / n, 4)
    scrambled_outcome_binding_accuracy = (
        round(sum(v for v in scramble_acc_per_seed if v is not None) /
              max(1, sum(1 for v in scramble_acc_per_seed if v is not None)), 4)
        if any(v is not None for v in scramble_acc_per_seed) else None)
    goal_owner_binding_accuracy = all_equal("goal_owner_binding_accuracy")
    control_false_fire_rate = all_equal("control_false_fire_rate")
    anti_recency_holds = all_equal("anti_recency_holds")
    coherence_margin_delta_sign_positive = all_equal("coherence_margin_delta_sign_positive")

    role_scramble_collapse = (
        scrambled_outcome_binding_accuracy is not None and scrambled_outcome_binding_accuracy <= 0.5)
    # 0.5 = <=1/2 trap items correct post-scramble (N=2 traps -> discrete {0, 0.5, 1.0});
    # 0.333 floor doesn't map onto N=2 cleanly, so use "no better than chance among 2 traps" (<=0.5)
    # as the discrete equivalent, documented here (not silently substituted).
    # VACUOUS-COLLAPSE FLAG: if the UNSCRAMBLED mechanism already never produced a positive delta
    # (coherence_margin_delta_sign_positive is not True), role_scramble_collapse is trivially True
    # for the wrong reason -- there was nothing content-driven to break. Surface this explicitly so
    # a HARD-PASS-looking scramble result is never read as "proves content-use" when the base
    # mechanism was already blind.
    role_scramble_collapse_vacuous = (
        role_scramble_collapse and coherence_margin_delta_sign_positive is not True)

    formal_hard_pass = (
        outcome_binding_accuracy >= 0.67 and role_scramble_collapse and
        control_false_fire_rate == 0 and
        (goal_owner_binding_accuracy is not None and goal_owner_binding_accuracy >= (5 / 6 - 1e-9)))
    formal_hard_fail = (outcome_binding_accuracy <= 0.334 or not role_scramble_collapse)

    if formal_hard_fail:
        verdict = "HARD_FAIL_NO_LIFT_OR_ROLE_CONTENT_BLIND"
    elif formal_hard_pass:
        verdict = "MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS"  # small-N cap, mandatory per pre-reg
    else:
        verdict = "MIDDLE_BAND"

    summary = (
        f"N=3 recency items (2 traps+1 sanity), 3 seeds. outcome_binding_accuracy={outcome_binding_accuracy} "
        f"(recency floor=0.3333) scrambled={scrambled_outcome_binding_accuracy} "
        f"role_scramble_collapse={role_scramble_collapse} (vacuous={role_scramble_collapse_vacuous}) "
        f"goal_owner_binding_accuracy={goal_owner_binding_accuracy} "
        f"(GIVEN not EARNED) control_false_fire_rate={control_false_fire_rate} "
        f"anti_recency_holds={anti_recency_holds} coherence_delta_sign_positive={coherence_margin_delta_sign_positive} "
        f"formal_hard_pass={formal_hard_pass} formal_hard_fail={formal_hard_fail}")

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary, n_seeds=n,
        outcome_binding_accuracy=outcome_binding_accuracy,
        recency_baseline=0.3333,
        beats_recency=(outcome_binding_accuracy > 0.3333),
        scrambled_outcome_binding_accuracy=scrambled_outcome_binding_accuracy,
        role_scramble_collapse=role_scramble_collapse,
        role_scramble_collapse_vacuous=role_scramble_collapse_vacuous,
        goal_owner_binding_accuracy=goal_owner_binding_accuracy,
        control_false_fire_rate=control_false_fire_rate,
        anti_recency_holds=anti_recency_holds,
        coherence_margin_delta_sign_positive=coherence_margin_delta_sign_positive,
        # BLINDNESS is diagnosed from the UNSCRAMBLED (correct-role) delta sign, not from
        # role_scramble_collapse: if the mechanism never produces a positive delta even when fed
        # the TRUE roles, scrambling trivially "collapses" it too (nothing to break) -- that would
        # be a false-negative for blindness if role_scramble_collapse were used as the sole test.
        # Disk-verified this session: delta==0.0 exactly on both genuine traps (not just below the
        # abstain band) -- the same symmetric-write-then-read signature that sank CausalLinkRegister.
        is_route_passage_role_content_blind_at_c5=(coherence_margin_delta_sign_positive is not True),
        formal_hard_pass=formal_hard_pass, formal_hard_fail=formal_hard_fail,
        per_seed=per_seed,
    )


# ============================================================================ infra
def _write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, path)


def run(run_mode: str):
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _write_json(os.path.join(OUTPUT_DIR, "_start_marker.json"),
                {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                 "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()})
    per_seed = {}
    for seed in SEEDS:
        ts = time.perf_counter()
        res = run_seed(seed)
        per_seed[seed] = res
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s "
              f"outcome_acc={res['outcome_binding_accuracy']} "
              f"scrambled={res['scrambled_outcome_binding_accuracy']} "
              f"ctrl_fire={res['control_false_fire_rate']}", flush=True)
    agg = aggregate(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(D2=D2, seeds=SEEDS, role_vocab=GO_ROLES, abstain_band=ABSTAIN_BAND_DEFAULT,
                         n_recency=len(RECENCY), n_scramble=len(FOILS), n_goal_block=len(GOAL_BLOCK),
                         n_controls=len(CONTROLS))
    agg["prereg"] = "preregs/2026-08-04_component5_gold_role_isolated_v1.md"
    agg["cites"] = [
        "notes/research_component5_goal_owner_selection_binding_2026-08-04.md",
        "notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md",
        "experiments/exp_situation_model_goal_outcome_dimension_v1.py (item bank, fb5b2a188)",
        "hdlab/self_improving_loop.py (route_passage, promoted 2026-08-02)",
    ]
    agg["dispatch"] = "LOCAL-ONLY, in-process foreground, not queue-dispatched (per task brief)"
    _write_json(os.path.join(OUTPUT_DIR, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    # (0) ContentMatchResolver: names resolve to self; unambiguous pronoun resolves to the only
    # gender-compatible entity (no ambiguity yet -> exercises the fallback path).
    r = ContentMatchResolver()
    assert r.subject_entity("Amy longed for the ice") == "amy"
    r.mark_role("amy", R_GOAL)
    assert "amy" in r._open_goal
    assert r.subject_entity("Jo raced ahead") == "jo"
    # "she" is compatible with amy (open-goal) and jo (recency) -- content-match must prefer amy
    assert r.subject_entity("she was lost") == "amy", "ContentMatchResolver did not prefer open-goal over recency"

    # (1) build_positions: role_seq/event_slots must be resolver-independent (lexicon-only typing)
    item = next(it for it in RECENCY if it["id"] == "recency_amy_blocked_pronoun_foil_jo")
    rs_b, cid_b, es_b = build_positions(item, RecencyEntityResolver())
    rs_c, cid_c, es_c = build_positions(item, ContentMatchResolver())
    assert rs_b == rs_c and es_b == es_c, "role/slot sequence must not depend on resolver"
    assert cid_b != cid_c, "recency and content-match must disagree on this genuine trap item"
    # recency grabs the foil (jo); content-match must grab the true owner (amy)
    unmet_pos = [i for i, r_ in enumerate(rs_b) if r_ in (R_UNMET, R_MET)][-1]
    assert cid_b[unmet_pos] == "jo", f"recency baseline expected foil jo, got {cid_b[unmet_pos]}"
    assert cid_c[unmet_pos] == "amy", f"content-match expected owner amy, got {cid_c[unmet_pos]}"

    # (2) role-scramble: mislabeling the GOAL holder as the foil must flip the content candidate's
    # pick away from the true owner.
    rs_s, cid_s, es_s = build_positions(item, ContentMatchResolver(), scramble_owner_to_foil="jo")
    assert cid_s[unmet_pos] == "jo", f"scrambled content-match expected foil jo, got {cid_s[unmet_pos]}"

    # (3) one full seed sanity + arms-must-differ (recency vs content-match resolutions differ)
    res = run_seed(0)
    assert res["outcome_binding_accuracy"] is not None
    assert res["control_false_fire_rate"] == 0.0, f"controls false-fired: {res['control_rows']}"
    rec_trap_row = next(r_ for r_ in res["recency_rows"] if r_["id"] == item["id"])
    assert rec_trap_row["baseline_owner"] != rec_trap_row["content_owner"], (
        "META_RULE_AF-style check: baseline and content candidates must differ on a genuine trap")

    print(f"[SELFTEST PASS] ContentMatchResolver prefers open-goal over recency; role/slot sequence "
          f"resolver-independent; role-scramble flips the pick; seed0 "
          f"outcome_acc={res['outcome_binding_accuracy']} scrambled={res['scrambled_outcome_binding_accuracy']} "
          f"ctrl_fire={res['control_false_fire_rate']}", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_json(os.path.join(OUTPUT_DIR, "metrics.json"),
                    {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                     "traceback": traceback.format_exc()[:5000],
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
