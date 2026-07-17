"""exp_read_grow_relation_identity_v1 -- TIER-1 RELATION IDENTITY: is a newly-grown relation a real, stable,
DISTINCT category, not confusable with another new relation that shares its argument-type signature?

QUESTION (drill-then-build follow-up on notes/research_new_relation_grounding_argument_structure_analogy_2026-07-16.md):
`exp_read_grow_openvocab_fastmap_v1` grows a new relation ("grims") and type-guards its arguments via
`_relation_args_coherent`, which reads ONLY `store.type_profile` (arg-type membership -- "animal-animal").
That cell's own docstring pre-registers the honest gap: "any two new verbs with the same arg-types are
indistinguishable by grounding." This cell tests that gap DIRECTLY: introduce a SECOND new relation
("florps") that shares grims's exact arg-type signature (animal-animal, drawn from the same grounded
schema) but is STRUCTURALLY DISTINCT -- grims is fixed-order/asymmetric (two disjoint argument pairs, never
repeated), florps is RECIPROCAL/order-swapping (the SAME argument pair observed with roles reversed across
its two exposures). Per the research note's cited mechanism (DORA / Doumas & Hummel 2008; progressive
alignment, Kotovsky & Gentner), this is the exact case argument-type-only comparison cannot resolve, and the
exact case a widened structural signature (order/symmetry-consistency + co-occurrence-with-known-relations
for the same argument pair) should resolve. Glass-box, NO LLM, local numpy. Tier-1 IDENTITY only (per the
research note's own tiering) -- Tier-2 class-mapping and Tier-3 meaning-verification are explicitly OUT OF
SCOPE for this cell (see hand-off notes/exp_dev_handoff_research_new_relation_grounding_2026-07-16.md).

REQUIRED NEGATIVE CONTROL (this IS the discriminator, not optional, per dispatching contract): the
arg-type-only ablation (the EXISTING `_relation_args_coherent`, reused VERBATIM, imported not reimplemented)
MUST FAIL to separate grims from florps -- both produce the IDENTICAL arg-type-only signature (True,) since
both pass the SAME coherent-animal-animal check. The WIDENED signature (arg-type-coherent AND
order-consistency AND co-occurrence-with-known-relations for the shared argument pair) MUST separate them,
because grims never repeats an argument pair (vacuously order-consistent) while florps repeats its ONE
argument pair with roles reversed (order-INconsistent -- the reciprocal/symmetric pattern) and the two
relations' argument pairs co-occur with different (or no) already-known relations. The failure-then-fix
pairing (ablation collides -> widened separates) IS the result; if the ablation also separates, the control
did not fire and the run is vacuous (flagged as its own HARD_FAIL condition below, not silently passed).

HONEST SCOPE NOTE (declared up front, not discovered post-hoc): at CONFIRM_K=2, a 2-exposure buffer can
never present an internally-CONTRADICTORY order pattern (that needs >=3 exposures: same pair same-order
twice, then reversed a third time). So at this corpus scale the GROWTH accept/reject decision is IDENTICAL
under both the ablation and the widened mechanism (both legitimately grow both relations) -- the widening's
measurable effect is entirely on the SEPARABILITY of the post-hoc IDENTITY signature, which is exactly the
Tier-1 question asked (is grims a real, distinct category from florps), not a claim about growth-gating.
Extending to gate-level rejection of an internally-incoherent relation would need a 3-exposure corpus and is
out of scope here (a natural follow-up, not attempted).

MECHANISM (glass-box, reuses the EXISTING accepted-facts store -- no new subsystem):
  1. Parser: `ie_extract_openvocab` (IMPORTED verbatim from exp_read_grow_openvocab_fastmap_v1). Elimination
     fast-map: exactly one unknown token between two known nouns -> candidate new relation.
  2. Confirm-buffer: CONFIRM_K (=2, IMPORTED) coherent exposures before commit (same discipline as the
     entity/relation tracks in the parent cell).
  3. ABLATION signature = `_relation_args_coherent(subs, objs, store)` (IMPORTED verbatim) reduced to a
     single boolean -- "is this a coherent animal-animal-ish relation." This is the CURRENT mechanism.
  4. FULL signature = (arg_type_coherent_bool, order_consistent_bool, co_occurrence_frozenset). order_consistent
     = False iff some UNORDERED argument pair is observed with BOTH role-orders across the relation's own
     exposures (a genuine role-swap). co_occurrence = the set of already-KNOWN relations (excluding the new
     relation itself) that independently link the SAME argument pair, in either order, among accepted facts
     (the DORA-style "compare against known relational context" move).
  5. SEPARATED(rel_a, rel_b) = signature(rel_a) != signature(rel_b), computed under each mechanism.

ARMS (views over the SAME deterministic run -- see HONEST SCOPE NOTE above for why growth is arm-invariant):
  FULL_STRUCTURAL        -- widened signature (arg-type + order-consistency + co-occurrence).
  ARGTYPE_ONLY_ABLATION  -- the CURRENT mechanism (`_relation_args_coherent` alone), REQUIRED negative control.

METRICS (reported separately):
  (a) separated_frac_full / separated_frac_ablation -- fraction of seeds where grims != florps signature.
  (b) identity_control_fired -- bool: did the REQUIRED negative control genuinely fail (ablation did NOT
      separate)? False = vacuous run (flag, do not claim HARD_PASS).
  (c) a_grown_all / b_grown_all -- both relations legitimately grown + queryable (widening does not break
      legitimate growth of a structurally-different-but-coherent relation).
  (d) violation_rejected_all / distractor_not_grown_all -- regression controls carried over from the parent
      cell's precision-guard discipline (type-violation reject; single-exposure relation never confirmed).

PRE-REG (envelope-fail-bands; I own the bands; set BEFORE running; matches research note section (b)/(c)):
  HARD-PASS (Tier-1 identity): separated_frac_full >= 0.90 AND separated_frac_ablation <= 0.10 (required
    negative control genuinely fires) AND a_grown_all AND b_grown_all AND violation_rejected_all AND
    distractor_not_grown_all.
  HARD-FAIL: separated_frac_full < 0.50 (widened mechanism carries no separating signal at this corpus
    scale -- a scale/data-richness finding per the research note, not a refutation of the mechanism class)
    OR separated_frac_full <= separated_frac_ablation + 0.05 (the required negative control did NOT
    genuinely fail -- VACUOUS run, the ablation-fails-then-fix-succeeds pairing did not occur)
    OR NOT a_grown_all OR NOT b_grown_all (widening broke legitimate growth).
  MIDDLE_BAND: separated_frac_full in band but a regression control (violation/distractor) failed.
  Tier-2 (class-mapping) and Tier-3 (meaning-verification) are OUT OF SCOPE -- not attempted, not scored.

Local numpy, no queue/GPU/atoms/push. ASCII-only. Sequential-CPU (foundation grows fact-by-fact; wall < 1s).
Storage: SHARDED (one VSA vector per accepted fact, via the imported FoundationStore). progress_logging =
print_flush_true (not load-bearing at this wall-time, included for template consistency).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; FULL_STRUCTURAL vs ARGTYPE_ONLY_ABLATION signature
#     representations differ -- hash-checked). accepted_hash is DECLARED EXEMPT for this arm pair (both
#     mechanisms grow the identical facts at CONFIRM_K=2 by design -- see HONEST SCOPE NOTE above; the
#     widening's effect is on the SEPARABILITY signature, not the accepted-facts set).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor. FHRR cleanup among ~20 concepts at N=1024 is z ~ sqrt(2N/20) ~ 10
#     sigma -> VSA decode/query reachable ~1.0; the discriminator is the DISCRETE structural-signature
#     comparison (set/boolean logic over accepted facts), NOT phasor noise.
# - baseline_in_band at smoke: N/A (discrete logic discriminator, not a continuous score) -- see
#     discriminator-fires gate below instead (identity_control_fired).
# - discriminator survives scale: corpus is FIXED-size (hand-authored GT); discriminator is deterministic
#     given the corpus (does not depend on N or corpus scale to fire). Verified at self-test: (1) FULL
#     separates grims/florps, (2) ABLATION collides (required negative control), (3) both relations grow.
# - HARD_PASS strictly above floor; explicit bands above + in prereg JSON below.
# - real_code_path (F.1): self_test constructs the REAL imported objects (FoundationStore via
#     run_identity_loop, the REAL ie_extract_openvocab parser, the REAL _relation_args_coherent ablation
#     function) at tiny scale and asserts (not synthetic-only).
# - deterministic seeding (F.5): fixed int seeds; sorted() vocab ordering; per-seed rng; NO hash()/list(set()).
# - all numbers in comments tagged HYPOTHESIZED@prereg / THEORETICAL / MEASURED@metrics.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import argparse
import time
import json
import hashlib
import platform
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_grow_relation_identity_v1"

# --- GENUINE REUSE of the proven downstream (imported, not rebuilt). No new subsystem. ---
from experiments.exp_read_grow_foundation_endtoend_v1 import (
    N_DIM,
    RELATIONS,
    ENTITIES,
    FoundationStore,
    _svo_make_phasors,
)
from experiments.exp_read_grow_openvocab_fastmap_v1 import (
    ie_extract_openvocab,
    KNOWN_VERB_FORMS,
    CONFIRM_K,
    _relation_args_coherent,   # the EXISTING mechanism -- reused VERBATIM as the required ablation.
)

SUBJ, VERB, OBJ = 0, 1, 2


def _row(text, gts, kind, note=""):
    return {"text": text, "gts": tuple(gts), "kind": kind, "note": note}


# ---------------------------------------------------------------------------
# CORPUS: bootstrap (grounds cat/dog/cow/bird/frog/fish argument-type profiles, identical content to the
# parent cell's bootstrap block -- copied, not imported, to keep this cell's corpus self-contained and
# insulated from unrelated edits to the parent file's row set/order), then the two same-arg-type new
# relations (grims = fixed-order/asymmetric; florps = reciprocal/order-swapping), plus regression controls
# (type-violation reject; single-exposure relation never confirmed).
# ---------------------------------------------------------------------------
RELATION_IDENTITY_CORPUS = [
    # -- bootstrap (KNOWN; establishes eats/lives_in/chases argument-type profiles) --
    _row("The cat eats the fish.", [("cat", "eats", "fish")], "known"),
    _row("The dog eats the bread.", [("dog", "eats", "bread")], "known"),
    _row("The cow eats grass.", [("cow", "eats", "grass")], "known"),
    _row("The bird eats a seed.", [("bird", "eats", "seed")], "known"),
    _row("The frog eats the worm.", [("frog", "eats", "worm")], "known"),
    _row("The cat lives in the barn.", [("cat", "lives_in", "barn")], "known"),
    _row("The dog lives in the barn.", [("dog", "lives_in", "barn")], "known"),
    _row("The bird lives in the nest.", [("bird", "lives_in", "nest")], "known"),
    _row("The fish lives in the pond.", [("fish", "lives_in", "pond")], "known"),
    _row("The frog lives in the pond.", [("frog", "lives_in", "pond")], "known"),
    _row("The cat chases the bird.", [("cat", "chases", "bird")], "known"),
    _row("The dog chases the cat.", [("dog", "chases", "cat")], "known"),
    _row("The bird chases the frog.", [("bird", "chases", "frog")], "known"),
    # -- NEW-RELATION A ("grims"): fixed-order/asymmetric -- two DISJOINT argument pairs, never repeated --
    _row("The cat grims the dog.", [("cat", "grims", "dog")], "new_relation_a", "grims exposure 1 (animal-animal, cat->dog)"),
    _row("The bird grims the frog.", [("bird", "grims", "frog")], "new_relation_a", "grims exposure 2 (animal-animal, bird->frog) -> GROW"),
    # -- arg-type guard regression control: type-violating arg under the grown relation -> must reject --
    _row("The seed grims the cat.", [("seed", "grims", "cat")], "relation_violation", "seed (food) as grims-subj -> reject"),
    # -- NEW-RELATION B ("florps"): reciprocal/order-swapping -- the SAME argument pair, roles REVERSED.
    #    Uses cow+dog (both grounded via bootstrap eats-SUBJ; NOTE: fish is deliberately NOT reused here --
    #    "The fish lives in the pond." is REJECTED by the schema gate upstream (fish's only established slot
    #    is eats-OBJECT, so it does not FIT the lives_in-SUBJECT slot -- an honest, pre-existing gate decision
    #    of the shared FoundationStore, not introduced by this cell), so fish never accrues a lives_in-SUBJECT
    #    type-profile entry and would make the arg-type-only ablation REJECT florps outright rather than
    #    COLLIDE with grims -- a different, less clean failure mode than the one under test here) --
    _row("The cow florps the dog.", [("cow", "florps", "dog")], "new_relation_b", "florps exposure 1 (animal-animal, cow->dog)"),
    _row("The dog florps the cow.", [("dog", "florps", "cow")], "new_relation_b", "florps exposure 2 -- SAME pair, roles SWAPPED -> GROW"),
    # -- CONFIRM_K regression control: single-exposure new relation must NOT be confirmed regardless of
    #    mechanism (the widening never bypasses the cross-situational confirm requirement) --
    _row("The cow trelps the frog.", [("cow", "trelps", "frog")], "relation_distractor_single", "trelps single exposure -> must stay unconfirmed"),
]

NEW_RELATION_A = "grims"
NEW_RELATION_B = "florps"
RELATION_A_FACTS = [("cat", "grims", "dog"), ("bird", "grims", "frog")]
RELATION_B_FACTS = [("cow", "florps", "dog"), ("dog", "florps", "cow")]
RELATION_VIOLATION = ("seed", "grims", "cat")
SINGLE_EXPOSURE_DISTRACTOR = ("cow", "trelps", "frog")
SHOULD_REJECT_RELATION = {RELATION_VIOLATION, SINGLE_EXPOSURE_DISTRACTOR}

DISTINCT_NEW_WORDS = sorted({NEW_RELATION_A, NEW_RELATION_B, "trelps"})


def build_ext_concepts():
    """deterministic phasor codebook for every token (known + new). Sorted concept ordering; no
    hash()/list(set()) (F.5)."""
    concepts = sorted(set(ENTITIES) | set(RELATIONS) | set(DISTINCT_NEW_WORDS))
    cid_idx = {c: i for i, c in enumerate(concepts)}
    return concepts, cid_idx


# ---------------------------------------------------------------------------
# Structural-signature functions (the widened mechanism). The ablation is `_relation_args_coherent`,
# imported verbatim -- NOT reimplemented here (genuine reuse, per contract).
# ---------------------------------------------------------------------------
def _order_consistency(pairs):
    """pairs: list of (subj, obj) tuples in exposure order for one relation. Returns (order_consistent,
    reversal_detected). order_consistent=False iff some UNORDERED argument pair is observed with BOTH role
    orders across the relation's own exposures (a genuine role-swap -> reciprocal/symmetric pattern).
    Vacuously True (no repeated pair observed at all) counts as the fixed-order/asymmetric class -- no
    counter-evidence of swapping was ever seen."""
    seen = defaultdict(set)
    for (s, o) in pairs:
        seen[frozenset((s, o))].add((s, o))
    reversal = any(len(v) >= 2 for v in seen.values())
    return (not reversal), reversal


def _co_occurrence_with_known(pairs, store, exclude_rel):
    """DORA-style context: which already-KNOWN relations (excluding the new relation itself) independently
    link the SAME (unordered) argument pair, in EITHER order, among currently accepted facts? Glass-box;
    reads only store.accepted."""
    rels = set()
    for (s, o) in pairs:
        pair_set = {s, o}
        for (a, r, b) in store.accepted:
            if r == exclude_rel:
                continue
            if {a, b} == pair_set:
                rels.add(r)
    return frozenset(rels)


def _relation_identity_signature(word, pairs, store, mode):
    """mode in {"argtype_only", "full"}. Returns a hashable signature tuple. "argtype_only" reduces to the
    EXISTING `_relation_args_coherent` boolean alone (the CURRENT mechanism, required ablation). "full"
    widens with order-consistency + co-occurrence-with-known-relations (the DORA-motivated fix)."""
    subs = [s for s, o in pairs]
    objs = [o for s, o in pairs]
    argtype_coherent = bool(_relation_args_coherent(subs, objs, store))
    if mode == "argtype_only":
        return (argtype_coherent,)
    order_consistent, _ = _order_consistency(pairs)
    co_occ = _co_occurrence_with_known(pairs, store, word)
    return (argtype_coherent, bool(order_consistent), co_occ)


def _sig_jsonable(sig):
    return [sorted(x) if isinstance(x, frozenset) else x for x in sig]


# ---------------------------------------------------------------------------
# ONE read->grow loop for one seed. Growth is ARM-INVARIANT at CONFIRM_K=2 (see HONEST SCOPE NOTE in the
# module docstring) -- both signature mechanisms are computed as VIEWS over this single deterministic run.
# ---------------------------------------------------------------------------
def run_identity_loop(seed):
    rng = np.random.default_rng(seed)
    concepts, cid_idx = build_ext_concepts()
    C = _svo_make_phasors(rng, len(concepts), N_DIM)
    roles = _svo_make_phasors(rng, 3, N_DIM)

    known_nouns = set(ENTITIES)
    known_verbs = set(KNOWN_VERB_FORMS.keys())
    known_rels = set(RELATIONS)

    store = FoundationStore(C, roles, cid_idx)
    buffer = defaultdict(list)     # new_word -> list of (subj, obj) in exposure order
    grown = set()
    per_sentence = []

    def commit_through_gate(triple):
        dec, info = store.gate(triple)
        store.decisions.append({"stage": "read", **info, "decision": dec})
        if dec == "ACCEPT":
            store.commit(triple)
        elif dec == "HOLD":
            store.held.append([triple, 0])
        store.reeval_holds()
        return dec

    for d in RELATION_IDENTITY_CORPUS:
        text = d["text"]
        triples, metas, rule, freason = ie_extract_openvocab(text, known_nouns, known_verbs, known_rels)
        rec = {"text": text, "kind": d["kind"], "rule": rule, "fail_reason": freason}
        if not triples:
            rec.update(action="ABSTAIN")
            per_sentence.append(rec)
            continue
        triple, meta = triples[0], metas[0]

        if not meta["new_rel"]:
            dec = commit_through_gate(triple)
            rec.update(action="KNOWN", triple=list(triple), gate=dec)
            per_sentence.append(rec)
            continue

        nw = meta["new_word"]
        s, r, o = triple
        buffer[nw].append((s, o))
        obs = buffer[nw]
        if len(obs) >= CONFIRM_K:
            subs = [p[0] for p in obs]
            objs = [p[1] for p in obs]
            argtype_ok = bool(_relation_args_coherent(subs, objs, store))
            # ARM-INVARIANT growth gate at CONFIRM_K=2 (see HONEST SCOPE NOTE): both mechanisms use the
            # same arg-type-coherence criterion to admit growth; the widening's effect is downstream, on
            # the post-hoc identity SIGNATURE, not on this accept/reject decision.
            if argtype_ok and nw not in grown:
                grown.add(nw)
                known_verbs.add(nw)
                known_rels.add(nw)
                for (ps, po) in obs:
                    commit_through_gate((ps, nw, po))
                rec.update(action="GROW_RELATION_CONFIRMED", triple=list(triple))
            else:
                rec.update(action="RELATION_HELD_INCOHERENT", triple=list(triple))
        else:
            rec.update(action="RELATION_PROVISIONAL", triple=list(triple))
        per_sentence.append(rec)

    store.reeval_holds()
    accepted = store.accepted

    obs_a = buffer[NEW_RELATION_A][:CONFIRM_K]
    obs_b = buffer[NEW_RELATION_B][:CONFIRM_K]
    sig_a_full = _relation_identity_signature(NEW_RELATION_A, obs_a, store, "full")
    sig_b_full = _relation_identity_signature(NEW_RELATION_B, obs_b, store, "full")
    sig_a_abl = _relation_identity_signature(NEW_RELATION_A, obs_a, store, "argtype_only")
    sig_b_abl = _relation_identity_signature(NEW_RELATION_B, obs_b, store, "argtype_only")
    separated_full = bool(sig_a_full != sig_b_full)
    separated_abl = bool(sig_a_abl != sig_b_abl)

    a_grown = bool(all(f in accepted for f in RELATION_A_FACTS) and NEW_RELATION_A in grown)
    b_grown = bool(all(f in accepted for f in RELATION_B_FACTS) and NEW_RELATION_B in grown)
    violation_rejected = bool(RELATION_VIOLATION not in accepted)
    distractor_not_grown = bool(SINGLE_EXPOSURE_DISTRACTOR not in accepted and "trelps" not in grown)
    relation_false = accepted & SHOULD_REJECT_RELATION
    relation_false_fact_rate = len(relation_false) / float(len(SHOULD_REJECT_RELATION))

    # queryability sanity (VSA retrieval genuinely round-trips the grown facts, not just set-membership).
    q_ok, q_total = 0, 0
    for (s, r, o) in RELATION_A_FACTS + RELATION_B_FACTS:
        q_total += 1
        if (s, r, o) in accepted and store.query(s, r) == o:
            q_ok += 1
    relation_query_acc = q_ok / float(q_total) if q_total else 0.0

    return {
        "seed": seed,
        "sig_a_full": _sig_jsonable(sig_a_full), "sig_b_full": _sig_jsonable(sig_b_full),
        "sig_a_ablation": _sig_jsonable(sig_a_abl), "sig_b_ablation": _sig_jsonable(sig_b_abl),
        "separated_full": separated_full,
        "separated_ablation": separated_abl,
        "a_grown": a_grown, "b_grown": b_grown,
        "violation_rejected": violation_rejected,
        "distractor_not_grown": distractor_not_grown,
        "relation_false_fact_rate": relation_false_fact_rate,
        "relation_query_acc": relation_query_acc,
        "n_grown_relations": len(grown),
        "accepted_hash": store.accepted_hash(),
    }


def avg_seeds(seeds):
    runs = [run_identity_loop(s) for s in seeds]
    out = {
        "separated_frac_full": float(np.mean([r["separated_full"] for r in runs])),
        "separated_frac_ablation": float(np.mean([r["separated_ablation"] for r in runs])),
        "a_grown_all": bool(all(r["a_grown"] for r in runs)),
        "b_grown_all": bool(all(r["b_grown"] for r in runs)),
        "violation_rejected_all": bool(all(r["violation_rejected"] for r in runs)),
        "distractor_not_grown_all": bool(all(r["distractor_not_grown"] for r in runs)),
        "relation_false_fact_rate_mean": float(np.mean([r["relation_false_fact_rate"] for r in runs])),
        "relation_query_acc_mean": float(np.mean([r["relation_query_acc"] for r in runs])),
        "per_seed": runs,
    }
    return out


# ---------------------------------------------------------------------------
# Verdict (envelope-fail-bands per pre-reg).
# ---------------------------------------------------------------------------
def compute_verdict(agg):
    identity_control_fired = agg["separated_frac_ablation"] <= 0.10   # required negative control genuinely fails
    vacuous = agg["separated_frac_full"] <= agg["separated_frac_ablation"] + 0.05

    identity_hp = (
        agg["separated_frac_full"] >= 0.90 and
        identity_control_fired and
        agg["a_grown_all"] and agg["b_grown_all"] and
        agg["violation_rejected_all"] and agg["distractor_not_grown_all"]
    )
    hard_fail = (
        agg["separated_frac_full"] < 0.50 or
        vacuous or
        not agg["a_grown_all"] or not agg["b_grown_all"]
    )

    if hard_fail:
        tier = "HARD_FAIL"
    elif identity_hp:
        tier = "HARD_PASS"
    else:
        tier = "MIDDLE_BAND"

    localize = []
    if vacuous:
        localize.append("REQUIRED_NEGATIVE_CONTROL_DID_NOT_FIRE: ablation separated_frac=%.2f is within 0.05 "
                        "of full separated_frac=%.2f -- the ablation-fails-then-widened-succeeds pairing did "
                        "NOT occur; this run is VACUOUS, not a genuine positive result"
                        % (agg["separated_frac_ablation"], agg["separated_frac_full"]))
    if not agg["a_grown_all"]:
        localize.append("grims (relation A) did not grow on all seeds")
    if not agg["b_grown_all"]:
        localize.append("florps (relation B) did not grow on all seeds")
    if identity_hp is False and not vacuous and agg["a_grown_all"] and agg["b_grown_all"]:
        if not agg["violation_rejected_all"]:
            localize.append("type-violation regression control leaked (relation_violation admitted)")
        if not agg["distractor_not_grown_all"]:
            localize.append("single-exposure regression control leaked (trelps confirmed on <2 exposures)")
        if agg["separated_frac_full"] < 0.90:
            localize.append("full separation below HARD-PASS bar (%.2f < 0.90)" % agg["separated_frac_full"])
    weakest = localize if localize else ["none (widened signature separates; required ablation genuinely fails; both relations grown + regression controls hold)"]

    msg = (f"{tier} | Tier-1 IDENTITY: separated_full={agg['separated_frac_full']:.2f} "
           f"separated_ablation={agg['separated_frac_ablation']:.2f} "
           f"identity_control_fired={identity_control_fired} (REQUIRED negative control: ablation must fail) | "
           f"a_grown={agg['a_grown_all']} b_grown={agg['b_grown_all']} "
           f"violation_rejected={agg['violation_rejected_all']} distractor_not_grown={agg['distractor_not_grown_all']} | "
           f"Tier-2 (class-mapping) / Tier-3 (meaning-verification) OUT OF SCOPE, not attempted | weakest={weakest}")
    return tier, msg, weakest, identity_control_fired


# ---------------------------------------------------------------------------
# infra.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": "exp_read_grow_relation_identity_v1",
           "smoke": "exp_read_grow_relation_identity_v1_smoke",
           "self_test": "exp_read_grow_relation_identity_v1_selftest"}[run_mode]
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert the discriminators FIRE (F.1).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (open-vocab parser + FoundationStore + the REAL "
          "_relation_args_coherent ablation function)...", flush=True)
    exercised = set()

    # (1) parser: exercise ie_extract_openvocab directly on the grims + florps sentences.
    kn = set(ENTITIES); kv = set(KNOWN_VERB_FORMS.keys()); kr = set(RELATIONS)
    tr, mt, rule, fr = ie_extract_openvocab("The cat grims the dog.", kn, kv, kr)
    assert tr == [("cat", "grims", "dog")] and mt[0]["new_rel"] and rule == "NEW_RELATION", "grims not flagged"
    tr, mt, rule, fr = ie_extract_openvocab("The cow florps the dog.", kn, kv, kr)
    assert tr == [("cow", "florps", "dog")] and mt[0]["new_rel"], "florps not flagged"
    tr, mt, rule, fr = ie_extract_openvocab("The dog florps the cow.", kn, kv, kr)
    assert tr == [("dog", "florps", "cow")] and mt[0]["new_rel"], "florps reversed-role exposure not flagged"
    exercised.add("ie_extract_openvocab")

    # (2) full deterministic loop at seed=11.
    run = run_identity_loop(11)
    exercised.add("run_identity_loop")
    exercised.add("_relation_args_coherent")   # invoked inside run_identity_loop + _relation_identity_signature

    # (3) both relations legitimately grown + queryable (widening does not break legitimate growth).
    assert run["a_grown"], "grims (relation A) did not grow"
    assert run["b_grown"], "florps (relation B) did not grow"
    assert run["relation_query_acc"] >= 0.99, f"grown relation facts not queryable: {run['relation_query_acc']}"

    # (4) REQUIRED NEGATIVE CONTROL: the arg-type-only ablation MUST FAIL to separate grims from florps
    #     (both produce the identical (True,) signature -- a genuine collision, not a vacuous non-difference).
    assert run["sig_a_ablation"] == run["sig_b_ablation"], \
        f"ablation unexpectedly differs (should collide): a={run['sig_a_ablation']} b={run['sig_b_ablation']}"
    assert run["separated_ablation"] is False, "ABLATION unexpectedly separated grims/florps -- control did not fire"
    assert run["sig_a_ablation"] == [True] and run["sig_b_ablation"] == [True], \
        f"ablation signatures not both coherent-True as designed: a={run['sig_a_ablation']} b={run['sig_b_ablation']}"

    # (5) THE FIX: the widened structural signature DOES separate them (order-consistency differs).
    assert run["separated_full"] is True, f"FULL signature failed to separate grims/florps: a={run['sig_a_full']} b={run['sig_b_full']}"
    assert run["sig_a_full"][1] is True, f"grims expected order_consistent=True (fixed-order): {run['sig_a_full']}"
    assert run["sig_b_full"][1] is False, f"florps expected order_consistent=False (reciprocal): {run['sig_b_full']}"

    # (6) ARMS-MUST-DIFFER (META_RULE_AF): FULL vs ABLATION signature representations differ (hash-checked).
    #     accepted_hash is DECLARED EXEMPT (growth is arm-invariant at CONFIRM_K=2 -- see module docstring).
    h_full = hashlib.sha256(json.dumps([run["sig_a_full"], run["sig_b_full"]], sort_keys=True).encode()).hexdigest()
    h_abl = hashlib.sha256(json.dumps([run["sig_a_ablation"], run["sig_b_ablation"]], sort_keys=True).encode()).hexdigest()
    assert h_full != h_abl, "META_RULE_AF: FULL vs ABLATION signature representations bit-identical"

    # (7) regression controls (carried over precision-guard discipline from the parent cell).
    assert run["violation_rejected"], "type-violation regression control leaked (relation_violation admitted)"
    assert run["distractor_not_grown"], "single-exposure regression control leaked (trelps confirmed early)"
    assert run["relation_false_fact_rate"] == 0.0, f"relation false-fact leak: {run['relation_false_fact_rate']}"

    for ep in ["ie_extract_openvocab", "run_identity_loop", "_relation_args_coherent"]:
        assert ep in exercised, f"real_code_path: entrypoint {ep} not exercised"

    print(f"[self_test] PASS | separated_full={run['separated_full']} separated_ablation={run['separated_ablation']} "
          f"(REQUIRED negative control fired: ablation collided as {run['sig_a_ablation']}=={run['sig_b_ablation']}) | "
          f"sig_a_full={run['sig_a_full']} sig_b_full={run['sig_b_full']} | "
          f"a_grown={run['a_grown']} b_grown={run['b_grown']} query_acc={run['relation_query_acc']:.2f}", flush=True)
    return True


# ---------------------------------------------------------------------------
# main.
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)

    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    seeds = [11, 23] if run_mode == "smoke" else [11, 23, 37, 41, 53]
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[relation_identity] run_mode={run_mode} seeds={seeds} corpus={len(RELATION_IDENTITY_CORPUS)} "
          f"sentences (2 new relations: grims=fixed-order, florps=reciprocal)", flush=True)

    agg = avg_seeds(seeds)
    print(f"[relation_identity] separated_frac_full={agg['separated_frac_full']:.3f} "
          f"separated_frac_ablation={agg['separated_frac_ablation']:.3f} "
          f"a_grown_all={agg['a_grown_all']} b_grown_all={agg['b_grown_all']}", flush=True)

    tier, msg, weakest, identity_control_fired = compute_verdict(agg)
    elapsed = time.perf_counter() - t0

    def strip(a):
        return {k: v for k, v in a.items() if k != "per_seed"}

    metrics = {
        "verdict": tier,
        "verdict_msg": msg,
        "summary": msg[:300],
        "run_mode": run_mode,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "n_read_sentences": len(RELATION_IDENTITY_CORPUS),
        "expected_n_units": expected_n_units,
        "weakest_interface": weakest,
        # METRIC (a) separation
        "metric_a_separated_frac_full": agg["separated_frac_full"],
        "metric_a_separated_frac_ablation": agg["separated_frac_ablation"],
        # METRIC (b) required negative control
        "metric_b_identity_control_fired": identity_control_fired,
        # METRIC (c) legitimate growth preserved
        "metric_c_a_grown_all": agg["a_grown_all"],
        "metric_c_b_grown_all": agg["b_grown_all"],
        "metric_c_relation_query_acc_mean": agg["relation_query_acc_mean"],
        # METRIC (d) regression controls
        "metric_d_violation_rejected_all": agg["violation_rejected_all"],
        "metric_d_distractor_not_grown_all": agg["distractor_not_grown_all"],
        "metric_d_relation_false_fact_rate_mean": agg["relation_false_fact_rate_mean"],
        "arms": {
            "FULL_STRUCTURAL": {
                "separated_frac": agg["separated_frac_full"],
                "sig_a_examples": [r["sig_a_full"] for r in agg["per_seed"][:1]],
                "sig_b_examples": [r["sig_b_full"] for r in agg["per_seed"][:1]],
            },
            "ARGTYPE_ONLY_ABLATION": {
                "separated_frac": agg["separated_frac_ablation"],
                "sig_a_examples": [r["sig_a_ablation"] for r in agg["per_seed"][:1]],
                "sig_b_examples": [r["sig_b_ablation"] for r in agg["per_seed"][:1]],
            },
            "arms_differ_exempted": [["FULL_STRUCTURAL", "ARGTYPE_ONLY_ABLATION", "accepted_hash",
                                      "growth is arm-invariant at CONFIRM_K=2 by design; widening affects "
                                      "the post-hoc identity signature only -- see module HONEST SCOPE NOTE"]],
        },
        "per_seed": agg["per_seed"],
        "prereg": {
            "tier1_identity_hard_pass": "separated_frac_full>=0.90 & separated_frac_ablation<=0.10 "
                                        "(identity_control_fired) & a_grown_all & b_grown_all & "
                                        "violation_rejected_all & distractor_not_grown_all",
            "tier1_identity_hard_fail": "separated_frac_full<0.50 | separated_frac_full<=separated_frac_ablation+0.05 "
                                        "(VACUOUS -- required negative control did not fire) | NOT a_grown_all | "
                                        "NOT b_grown_all",
            "confirm_k": CONFIRM_K,
            "new_relation_a_fixed_order": NEW_RELATION_A,
            "new_relation_b_reciprocal": NEW_RELATION_B,
            "scope": "Tier-1 IDENTITY only. Tier-2 (class-mapping via structure-mapping/systematicity) and "
                    "Tier-3 (fine-grained meaning-verification) are OUT OF SCOPE per "
                    "notes/exp_dev_handoff_research_new_relation_grounding_2026-07-16.md -- not attempted.",
            "honest_scope_note": "growth accept/reject is ARM-INVARIANT at CONFIRM_K=2 (2-exposure buffers "
                                 "cannot present an internal order-contradiction); the widening's measurable "
                                 "effect is on the post-hoc identity-signature SEPARABILITY, not the growth gate.",
            "compute_architecture": "sequential-CPU (foundation grows fact-by-fact; gate state depends on prior "
                                    "admits); wall < 1s total (tiny corpus, discrete logic discriminator)",
            "storage_strategy": "sharded (one VSA vector per accepted fact, via imported FoundationStore)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["ie_extract_openvocab", "run_identity_loop", "_relation_args_coherent"],
            "crlb_n/a": "no quantitative noise floor; discriminator is discrete structural-signature "
                       "comparison (set/boolean logic over accepted facts), not phasor decode noise",
            "prior_work_check": "substrate_query.sh top hits at cosine 0.31-0.33 concern Gentner SME "
                                "structural-alignment in OTHER contexts (P9 cross-domain KGE gap; slipnet "
                                "relation-TYPE routing interference) -- conceptually adjacent (same Gentner/"
                                "SME lineage) but NOT the same cell/test; this cell (new-relation IDENTITY "
                                "individuation via order/symmetry+co-occurrence widening in the read-grow "
                                "pipeline) is genuinely novel, not a rediscovery.",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[relation_identity] {tier} in {elapsed:.2f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[relation_identity] {msg}", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _md = "full"
    try:
        if "--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv):
            _md = "smoke"
        elif "--self-test" in sys.argv or "self_test" in sys.argv:
            _md = "self_test"
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
