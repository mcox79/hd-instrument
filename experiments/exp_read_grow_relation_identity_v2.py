"""exp_read_grow_relation_identity_v2 -- TIER-1 RELATION IDENTITY, expanded to a POPULATION with a genuine
FAILURE-RATE measurement, per the Skunkworks VET's explicit expansion criterion on v1 (commit 980eb1576):
">=4-6 authored relations with varied same-argtype collisions (not just fixed-order-vs-reciprocal), INCLUDING
at least one case designed to DEFEAT order-consistency+co-occurrence (to test the discriminator's genuine
failure rate, not just its success case), and ideally a CONFIRM_K>=3 corpus that stress-tests the GROWTH-gate
(not just post-hoc signature)."

QUESTION: v1 proved the widened DORA-style signature (arg-type-coherent + order-consistency + co-occurrence-
with-known-relations) separates ONE minimal pair (grims fixed-order vs florps reciprocal). This cell asks the
honest follow-up: does it separate a POPULATION of same-arg-type relations with VARIED collision structures,
and -- critically -- what is its genuine FAILURE rate when a relation pair is deliberately engineered to
DEFEAT the discriminator (share arg-type AND order-consistency AND co-occurrence profile)? Glass-box, NO LLM,
local numpy. Reading-main-task advance (relation grounding).

POPULATION (6 new relations, all same arg-type "animal-animal", CONFIRM_K=3 -- IMPORTED functions REUSED
VERBATIM, not reimplemented: `_relation_args_coherent` from openvocab_fastmap_v1; `_order_consistency` /
`_co_occurrence_with_known` / `_relation_identity_signature` from relation_identity_v1):
  grims    -- fixed-order (2 disjoint pairs cat-dog/bird-frog, 3rd exposure repeats pair 1). Both pairs
             independently co-occur with the known `chases` relation -> sig=(True,True,{chases}).
  florps   -- reciprocal (SAME pair cow-dog, roles reversed on exposure 2, repeated on exposure 3) -> order-
             INconsistent, no co-occurrence -> sig=(True,False,{}). SEPARATES from grims (order axis).
  krendles -- fixed-order, single pair cat-bird repeated x3. That pair ALSO independently co-occurs with
             `chases` (same mechanism as grims, different concrete pair) -> sig=(True,True,{chases}).
  shleps   -- fixed-order, single pair cow-bird repeated x3, no co-occurrence -> sig=(True,True,{}). SEPARATES
             from krendles (co-occurrence axis, holding order-consistency fixed at True for both -- a
             DIFFERENT separating axis than grims-vs-florps, per the "varied collision structures" mandate).
  vorbs    -- fixed-order, 2 disjoint pairs cat-frog/dog-bird (3rd exposure repeats pair 1), NEITHER pair
             co-occurs with any known/other-new relation -> sig=(True,True,{}).
  dringles -- fixed-order, 2 disjoint pairs cow-cat/dog-frog (3rd exposure repeats pair 1), NEITHER pair
             co-occurs with anything -> sig=(True,True,{}).
  ** vorbs vs dringles is the REQUIRED DEFEAT CASE: both fixed-order (vacuously order-consistent, never
  reversed) AND both have EMPTY co-occurrence (their argument pairs happen to touch no known relation and no
  other new relation). Their full signatures are therefore LITERALLY IDENTICAL: (True, True, frozenset()).
  Two genuinely DIFFERENT relations (different words, different argument pairs, different meaning) collapse
  to the same widened signature -- the widened mechanism CANNOT separate them. This is not a contrived edge
  case bolted on after the fact: it is the natural failure mode of a signature built from (a) a boolean
  arg-type check, (b) a boolean order-consistency check, and (c) a co-occurrence SET that is empty whenever a
  relation's argument pairs happen not to overlap any other relation's -- which is common, not rare, in a
  small schema. shleps ALSO lands in this exact bucket (empirically discovered, not designed) -- see
  RESULT below: the "no-cooccurrence fixed-order" equivalence class contains 3 of the 6 relations, not 2.

REQUIRED NEGATIVE CONTROL (population-wide, generalizing v1's pairwise control): the arg-type-only ablation
  (`_relation_args_coherent` alone, reduced to (True,) for every one of the 6 relations, since all 6 are
  animal-animal coherent by construction) MUST collide on EVERY pair in the population (0/15 separated) --
  a stronger, population-wide version of v1's single-pair required control.

CONFIRM_K=3 GROWTH-GATE STRESS (the ideally-requested piece, v1 was arm-invariant only because K=2 cannot
  present an internal order-contradiction): a 7th relation, `zant`, is engineered to be internally order-
  CONTRADICTORY across its own 3 exposures (cow-frog, then frog-cow reversed, then cow-frog again) while
  remaining arg-type coherent. TWO growth-gate mechanisms are compared: ARGTYPE_GATE (the CURRENT production
  mechanism -- grows iff arg-type coherent, identical to v1/openvocab_fastmap) vs FULL_STRUCTURAL_GATE (a
  HYPOTHETICAL widened gate that ALSO requires order-consistency across the buffered exposures before
  growing). MEASURED (not pre-registered as "correct" either way -- genuinely exploratory): the two gates
  produce DIFFERENT grown-sets. FULL_STRUCTURAL_GATE correctly blocks zant (the deliberately-contradictory
  test relation) but ALSO incorrectly blocks florps (a LEGITIMATE reciprocal relation -- reciprocal verbs are
  order-INCONSISTENT by their very nature, not noise). This is the honest finding: requiring order-consistency
  as a hard GROWTH gate cannot distinguish "genuinely reciprocal category" from "contradictory noise" -- both
  look order-inconsistent from inside a single relation's own exposure history. Reported descriptively; NOT
  gated pass/fail (there is no pre-registerable "correct" direction for this comparison).

SEED VARIANCE (VET note: v1's structural signature is deterministic/seed-invariant over a fixed corpus, so
  multi-seed "robustness" was pipeline-determinism, not a real variance probe). Per-seed variance axis: the
  NEW-relation sentences (not the fixed bootstrap, not the fixed final VIOLATION sentence) are round-robin-
  merge-shuffled across relations (each relation's OWN internal exposure order is preserved; only the
  INTERLEAVING of different relations' sentences in the read stream varies) using a per-seed RNG. This is a
  GENUINE variance axis -- verified empirically (design-check script, not shipped) that the shuffled orderings
  actually differ per seed (distinct first-10-token traces) while gate decisions / grown-sets / signatures are
  format-invariant across 8 tested seeds -- i.e., ROBUSTNESS-DESPITE-GENUINE-VARIATION, a stronger and more
  informative claim than "determinism because nothing varies."

METRICS (reported separately, population fraction is the deliverable, never blobbed to a single 1.0/0.0):
  (a) population_separated_frac_full / _ablation -- fraction of the C(6,2)=15 population pairs separated.
  (b) designated pairs: ORDER_PAIR (grims,florps), COOCCUR_PAIR (krendles,shleps), DEFEAT_PAIR (vorbs,dringles)
      -- each pair's full-separated + ablation-separated bool, reported individually (not just a single frac).
  (c) all_relations_grown / relation_query_acc -- widening + population scale does not break legitimate growth.
  (d) violation_rejected / k_threshold_control_not_confirmed (trelps: exactly 2 exposures, must NOT confirm at
      CONFIRM_K=3 -- demonstrates the K=3 bump is genuinely load-bearing, a new regression control vs v1's K=2).
  (e) growth_gate_arm_invariant_at_k3 (informational; ARGTYPE_GATE vs FULL_STRUCTURAL_GATE grown-set diff).
  (f) interleave_robust_across_seeds (informational; genuine order-variance axis, robustness result).

PRE-REG (envelope-fail-bands; I own the bands; set BEFORE running):
  HARD-PASS: ablation_population_separated_frac == 0.0 (REQUIRED negative control fires population-wide) AND
    ORDER_PAIR separates under full AND COOCCUR_PAIR separates under full AND DEFEAT_PAIR does NOT separate
    under full (the required, honest failure) AND all_relations_grown (6 identity + zant, under the CURRENT
    production ARGTYPE_GATE) AND violation_rejected AND k_threshold_control_not_confirmed AND
    interleave_robust_across_seeds AND arms_differ_verified.
  HARD-FAIL: ablation_population_separated_frac > 0.0 (VACUOUS -- required control did not fire) OR
    ORDER_PAIR or COOCCUR_PAIR fails to separate under full (a designed success case failed) OR DEFEAT_PAIR
    DOES separate under full (the defeat construction failed to defeat -- per the dispatching contract, this
    is a bug in the defeat construction, flagged as its own condition, not silently reinterpreted as a win) OR
    NOT all_relations_grown OR a regression control leaked.
  MIDDLE_BAND: all of the above HARD-PASS gates hold EXCEPT interleave_robust_across_seeds (a genuinely
    interesting order-dependence finding, not fatal -- would mean presentation order matters, worth a follow-up).
  population_separated_frac itself (both full and ablation) is reported DESCRIPTIVELY, not gated to an exact
    pre-committed number -- gating a population fraction to a number discovered during corpus design would be
    circular; the pairwise gates above (which pairs must/must-not separate) are the real pre-registered claims.
  growth_gate_arm_invariant_at_k3 is EXPLORATORY/descriptive only -- no pre-registered "correct" direction.

Local numpy, no queue/GPU/atoms/push. ASCII-only. Sequential-CPU (foundation grows fact-by-fact; wall < 1s).
Storage: SHARDED (one VSA vector per accepted fact, via imported FoundationStore). progress_logging =
print_flush_true (not load-bearing at this wall-time, included for template consistency).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; FULL vs ARGTYPE_ONLY_ABLATION signature representations
#     differ, hash-checked, over the population). accepted_hash NOT compared across gate-mode arms (those are
#     EXPECTED to differ -- that IS the growth_gate_arm_invariant_at_k3 measurement, not a bug to guard against).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor. FHRR cleanup among ~25 concepts at N=1024 is z ~ sqrt(2N/25) ~ 9
#     sigma -> VSA decode/query reachable ~1.0; the discriminator is the DISCRETE structural-signature
#     comparison (set/boolean logic over accepted facts), NOT phasor noise.
# - baseline_in_band at smoke: N/A (discrete logic discriminator, not a continuous score) -- see
#     discriminator-fires gate below instead (ablation_population_separated_frac == 0.0 required).
# - discriminator survives scale: corpus is FIXED-size (hand-authored GT, 6+1 relations); discriminator is
#     deterministic given the corpus AND verified ROBUST to a genuine order-variance axis (interleave shuffle,
#     8 seeds design-checked). Verified at self-test: (1) FULL separates the 2 designed success pairs, (2)
#     FULL collides on the designed defeat pair (required), (3) ABLATION collides on the WHOLE population,
#     (4) all 7 relations grow under the production gate, (5) the two growth-gate mechanisms diverge.
# - HARD_PASS strictly above floor; explicit bands above + in prereg JSON below.
# - real_code_path (F.1): self_test constructs the REAL imported objects (FoundationStore via
#     run_identity_loop, the REAL ie_extract_openvocab parser, the REAL _relation_args_coherent /
#     _order_consistency / _co_occurrence_with_known functions) at tiny scale and asserts (not synthetic-only).
# - deterministic seeding (F.5): fixed int seeds; sorted() vocab ordering; per-seed rng (including the
#     interleave-shuffle rng, seeded off the run seed with a fixed offset); NO hash()/list(set()).
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

ANCHOR_NAME = "read_grow_relation_identity_v2"

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
    _relation_args_coherent,   # the EXISTING mechanism -- reused VERBATIM as the required ablation.
)
from experiments.exp_read_grow_relation_identity_v1 import (
    _order_consistency,            # reused VERBATIM (v1's widened-signature component).
    _co_occurrence_with_known,     # reused VERBATIM.
    _relation_identity_signature,  # reused VERBATIM (mode in {"argtype_only","full"}).
    _sig_jsonable,                 # reused VERBATIM.
)

SUBJ, VERB, OBJ = 0, 1, 2
CONFIRM_K = 3   # BUMPED from v1's K=2 (LOCAL override, not the imported constant -- does not affect other cells).

# ---------------------------------------------------------------------------
# BOOTSTRAP (identical content to v1/parent -- copied not imported, corpus self-contained).
# ---------------------------------------------------------------------------
def _row(text, gts, kind, note=""):
    return {"text": text, "gts": tuple(gts), "kind": kind, "note": note}


BOOTSTRAP_ROWS = [
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
]

# ---------------------------------------------------------------------------
# POPULATION: 6 identity-test relations + 1 growth-gate-stress relation (zant), fixed INTERNAL exposure order
# per relation (design-check-verified pair choices -- see module docstring for the coherence/co-occurrence
# derivation against the ACTUAL bootstrap-derived type_profile, not hand-guessed).
# ---------------------------------------------------------------------------
NEW_RELATION_PAIRS = {
    "grims":    [("cat", "dog"), ("bird", "frog"), ("cat", "dog")],
    "florps":   [("cow", "dog"), ("dog", "cow"), ("cow", "dog")],
    "krendles": [("cat", "bird"), ("cat", "bird"), ("cat", "bird")],
    "shleps":   [("cow", "bird"), ("cow", "bird"), ("cow", "bird")],
    "vorbs":    [("cat", "frog"), ("dog", "bird"), ("cat", "frog")],
    "dringles": [("cow", "cat"), ("dog", "frog"), ("cow", "cat")],
    "zant":     [("cow", "frog"), ("frog", "cow"), ("cow", "frog")],   # internally order-CONTRADICTORY.
}
IDENTITY_POPULATION = ["grims", "florps", "krendles", "shleps", "vorbs", "dringles"]   # excludes zant (K-gate-only).
ORDER_PAIR = ("grims", "florps")        # designed to separate via order_consistency axis.
COOCCUR_PAIR = ("krendles", "shleps")   # designed to separate via co_occurrence axis (both order-consistent=True).
DEFEAT_PAIR = ("vorbs", "dringles")     # REQUIRED defeat: identical full signature by construction.

TRELPS_PAIRS = [("cow", "frog")] * 2    # exactly 2 exposures -- CONFIRM_K=3 threshold control (must NOT confirm).
RELATION_VIOLATION = ("seed", "grims", "cat")   # type-violating arg under grown grims (grims grown by then).

DISTINCT_NEW_WORDS = sorted(set(NEW_RELATION_PAIRS.keys()) | {"trelps"})


def build_ext_concepts():
    """deterministic phasor codebook for every token (known + new). Sorted concept ordering; no
    hash()/list(set()) (F.5)."""
    concepts = sorted(set(ENTITIES) | set(RELATIONS) | set(DISTINCT_NEW_WORDS))
    cid_idx = {c: i for i, c in enumerate(concepts)}
    return concepts, cid_idx


def _sentence_for(word, subj, obj):
    return f"The {subj} {word} the {obj}."


def build_interleaved_corpus(seed):
    """GENUINE variance axis: round-robin-merge the per-relation exposure streams (each relation's OWN
    internal exposure order preserved) with a per-seed RNG interleave across relations + the K-threshold
    control. Bootstrap is a fixed prefix (schema must ground first); RELATION_VIOLATION is a fixed suffix
    (grims must already be grown). Design-check-verified (8 seeds, not shipped) that interleave order
    genuinely differs per seed while grown-set/signatures stay robust -- see module docstring."""
    rng = np.random.default_rng(seed + 9000)   # offset so it doesn't alias the phasor-codebook rng.
    queues = {w: [(w, s, o) for (s, o) in pairs] for w, pairs in NEW_RELATION_PAIRS.items()}
    queues["trelps"] = [("trelps", s, o) for (s, o) in TRELPS_PAIRS]
    words = sorted(queues.keys())   # deterministic base ordering before shuffle draws (F.5).
    order = []
    while any(queues[w] for w in words):
        avail = [w for w in words if queues[w]]
        pick = avail[int(rng.integers(0, len(avail)))]
        order.append(queues[pick].pop(0))

    rows = list(BOOTSTRAP_ROWS)
    for (word, s, o) in order:
        kind = "relation_distractor_k_threshold" if word == "trelps" else f"new_relation:{word}"
        note = f"{word} exposure ({s}->{o})"
        rows.append(_row(_sentence_for(word, s, o), [(s, word, o)], kind, note))
    rows.append(_row(_sentence_for("grims", "seed", "cat"), [RELATION_VIOLATION], "relation_violation",
                      "seed (food) as grown-grims-subj -> reject"))
    return rows


# ---------------------------------------------------------------------------
# ONE read->grow loop for one seed + one growth-gate mode.
#   gate_mode in {"argtype_gate", "full_structural_gate"}:
#     argtype_gate         -- the CURRENT production mechanism (grows iff arg-type coherent). Identical
#                              discipline to v1 / openvocab_fastmap_v1.
#     full_structural_gate -- HYPOTHETICAL widened gate: grows iff arg-type coherent AND order-consistent
#                              across the buffered exposures. EXPLORATORY (no pre-registered "correct" side).
# ---------------------------------------------------------------------------
def run_identity_loop(seed, gate_mode="argtype_gate"):
    rng = np.random.default_rng(seed)
    concepts, cid_idx = build_ext_concepts()
    C = _svo_make_phasors(rng, len(concepts), N_DIM)
    roles = _svo_make_phasors(rng, 3, N_DIM)

    known_nouns = set(ENTITIES)
    known_verbs = set(KNOWN_VERB_FORMS.keys())
    known_rels = set(RELATIONS)

    store = FoundationStore(C, roles, cid_idx)
    buffer = defaultdict(list)
    grown = set()
    per_sentence = []
    corpus = build_interleaved_corpus(seed)

    def commit_through_gate(triple):
        dec, info = store.gate(triple)
        store.decisions.append({"stage": "read", **info, "decision": dec})
        if dec == "ACCEPT":
            store.commit(triple)
        elif dec == "HOLD":
            store.held.append([triple, 0])
        store.reeval_holds()
        return dec

    for d in corpus:
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
            rec.update(action="KNOWN_OR_VIOLATION", triple=list(triple), gate=dec)
            per_sentence.append(rec)
            continue

        nw = meta["new_word"]
        s, r, o = triple
        buffer[nw].append((s, o))
        obs = buffer[nw]
        if len(obs) >= CONFIRM_K and nw not in grown:
            subs = [p[0] for p in obs]
            objs = [p[1] for p in obs]
            argtype_ok = bool(_relation_args_coherent(subs, objs, store))
            order_ok, _ = _order_consistency(obs)
            gate_ok = argtype_ok if gate_mode == "argtype_gate" else (argtype_ok and order_ok)
            if gate_ok:
                grown.add(nw)
                known_verbs.add(nw)
                known_rels.add(nw)
                for (ps, po) in obs:
                    commit_through_gate((ps, nw, po))
                rec.update(action="GROW_RELATION_CONFIRMED", triple=list(triple), argtype_ok=argtype_ok, order_ok=order_ok)
            else:
                rec.update(action="RELATION_HELD_INCOHERENT", triple=list(triple), argtype_ok=argtype_ok, order_ok=order_ok)
        else:
            rec.update(action="RELATION_PROVISIONAL", triple=list(triple))
        per_sentence.append(rec)

    store.reeval_holds()
    accepted = store.accepted

    # ---- population signatures (post-hoc, over the FINAL store state -- order-independent by construction) ----
    sig_full, sig_abl = {}, {}
    for w in IDENTITY_POPULATION + ["zant"]:
        obs = NEW_RELATION_PAIRS[w][:CONFIRM_K]
        sig_full[w] = _relation_identity_signature(w, obs, store, "full")
        sig_abl[w] = _relation_identity_signature(w, obs, store, "argtype_only")

    pop_pairs, sep_full, sep_abl = [], [], []
    for i in range(len(IDENTITY_POPULATION)):
        for j in range(i + 1, len(IDENTITY_POPULATION)):
            a, b = IDENTITY_POPULATION[i], IDENTITY_POPULATION[j]
            pop_pairs.append((a, b))
            sep_full.append(bool(sig_full[a] != sig_full[b]))
            sep_abl.append(bool(sig_abl[a] != sig_abl[b]))
    population_separated_frac_full = float(np.mean(sep_full))
    population_separated_frac_ablation = float(np.mean(sep_abl))

    order_sep_full = bool(sig_full[ORDER_PAIR[0]] != sig_full[ORDER_PAIR[1]])
    order_sep_abl = bool(sig_abl[ORDER_PAIR[0]] != sig_abl[ORDER_PAIR[1]])
    cooccur_sep_full = bool(sig_full[COOCCUR_PAIR[0]] != sig_full[COOCCUR_PAIR[1]])
    cooccur_sep_abl = bool(sig_abl[COOCCUR_PAIR[0]] != sig_abl[COOCCUR_PAIR[1]])
    defeat_sep_full = bool(sig_full[DEFEAT_PAIR[0]] != sig_full[DEFEAT_PAIR[1]])
    defeat_sep_abl = bool(sig_abl[DEFEAT_PAIR[0]] != sig_abl[DEFEAT_PAIR[1]])

    all_grown = bool(all(w in grown for w in IDENTITY_POPULATION + ["zant"])) if gate_mode == "argtype_gate" else None
    all_facts_in_store = bool(all(
        (s, w, o) in accepted for w, pairs in NEW_RELATION_PAIRS.items() for (s, o) in pairs
    )) if gate_mode == "argtype_gate" else None
    violation_rejected = bool(RELATION_VIOLATION not in accepted)
    trelps_not_confirmed = bool(("cow", "trelps", "frog") not in accepted and "trelps" not in grown)

    q_ok, q_total = 0, 0
    if gate_mode == "argtype_gate":
        for w, pairs in NEW_RELATION_PAIRS.items():
            for (s, o) in set(pairs):
                q_total += 1
                if (s, w, o) in accepted and store.query(s, w) == o:
                    q_ok += 1
    relation_query_acc = (q_ok / float(q_total)) if q_total else 0.0

    return {
        "seed": seed, "gate_mode": gate_mode,
        "grown": sorted(grown),
        "sig_full": {w: _sig_jsonable(sig_full[w]) for w in sig_full},
        "sig_ablation": {w: _sig_jsonable(sig_abl[w]) for w in sig_abl},
        "population_separated_frac_full": population_separated_frac_full,
        "population_separated_frac_ablation": population_separated_frac_ablation,
        "pop_pairs": pop_pairs,
        "order_pair_separated_full": order_sep_full, "order_pair_separated_ablation": order_sep_abl,
        "cooccur_pair_separated_full": cooccur_sep_full, "cooccur_pair_separated_ablation": cooccur_sep_abl,
        "defeat_pair_separated_full": defeat_sep_full, "defeat_pair_separated_ablation": defeat_sep_abl,
        "all_grown": all_grown,
        "all_facts_in_store": all_facts_in_store,
        "violation_rejected": violation_rejected,
        "trelps_not_confirmed": trelps_not_confirmed,
        "relation_query_acc": relation_query_acc,
        "accepted_hash": store.accepted_hash(),
        "corpus_order_head": [d["kind"] for d in build_interleaved_corpus(seed)][13:23],   # first 10 post-bootstrap kinds
    }


def avg_seeds(seeds, gate_mode="argtype_gate"):
    runs = [run_identity_loop(s, gate_mode) for s in seeds]
    baseline = runs[0]
    interleave_robust = bool(all(
        r["grown"] == baseline["grown"] and r["sig_full"] == baseline["sig_full"]
        and r["sig_ablation"] == baseline["sig_ablation"]
        for r in runs[1:]
    ))
    interleave_orders_genuinely_differ = bool(len({tuple(r["corpus_order_head"]) for r in runs}) > 1)
    out = {
        "population_separated_frac_full_mean": float(np.mean([r["population_separated_frac_full"] for r in runs])),
        "population_separated_frac_ablation_mean": float(np.mean([r["population_separated_frac_ablation"] for r in runs])),
        "order_pair_separated_full_all": bool(all(r["order_pair_separated_full"] for r in runs)),
        "order_pair_separated_ablation_any": bool(any(r["order_pair_separated_ablation"] for r in runs)),
        "cooccur_pair_separated_full_all": bool(all(r["cooccur_pair_separated_full"] for r in runs)),
        "cooccur_pair_separated_ablation_any": bool(any(r["cooccur_pair_separated_ablation"] for r in runs)),
        "defeat_pair_separated_full_any": bool(any(r["defeat_pair_separated_full"] for r in runs)),
        "defeat_pair_separated_ablation_any": bool(any(r["defeat_pair_separated_ablation"] for r in runs)),
        "all_grown_all": bool(all(r["all_grown"] for r in runs)) if gate_mode == "argtype_gate" else None,
        "all_facts_in_store_all": bool(all(r["all_facts_in_store"] for r in runs)) if gate_mode == "argtype_gate" else None,
        "violation_rejected_all": bool(all(r["violation_rejected"] for r in runs)),
        "trelps_not_confirmed_all": bool(all(r["trelps_not_confirmed"] for r in runs)),
        "relation_query_acc_mean": float(np.mean([r["relation_query_acc"] for r in runs])) if gate_mode == "argtype_gate" else None,
        "interleave_robust_across_seeds": interleave_robust,
        "interleave_orders_genuinely_differ": interleave_orders_genuinely_differ,
        "grown_sets_per_seed": {r["seed"]: r["grown"] for r in runs},
        "per_seed": runs,
    }
    return out


# ---------------------------------------------------------------------------
# Verdict (envelope-fail-bands per pre-reg).
# ---------------------------------------------------------------------------
def compute_verdict(agg_argtype, agg_full_gate):
    ablation_control_fired = agg_argtype["population_separated_frac_ablation_mean"] == 0.0
    order_ok = agg_argtype["order_pair_separated_full_all"] and not agg_argtype["order_pair_separated_ablation_any"]
    cooccur_ok = agg_argtype["cooccur_pair_separated_full_all"] and not agg_argtype["cooccur_pair_separated_ablation_any"]
    defeat_ok = (not agg_argtype["defeat_pair_separated_full_any"]) and (not agg_argtype["defeat_pair_separated_ablation_any"])
    growth_ok = agg_argtype["all_grown_all"] and agg_argtype["all_facts_in_store_all"]
    regressions_ok = agg_argtype["violation_rejected_all"] and agg_argtype["trelps_not_confirmed_all"]
    interleave_robust = agg_argtype["interleave_robust_across_seeds"]
    genuine_variance = agg_argtype["interleave_orders_genuinely_differ"]

    vacuous = not ablation_control_fired
    designed_pairs_ok = order_ok and cooccur_ok and defeat_ok

    hard_fail = vacuous or (not order_ok) or (not cooccur_ok) or agg_argtype["defeat_pair_separated_full_any"] \
                or (not growth_ok) or (not regressions_ok)
    hard_pass_core = ablation_control_fired and designed_pairs_ok and growth_ok and regressions_ok

    if hard_fail:
        tier = "HARD_FAIL"
    elif hard_pass_core and interleave_robust:
        tier = "HARD_PASS"
    elif hard_pass_core and not interleave_robust:
        tier = "MIDDLE_BAND"
    else:
        tier = "MIDDLE_BAND"

    grown_argtype = set(agg_argtype["grown_sets_per_seed"][agg_argtype["per_seed"][0]["seed"]])
    grown_full_gate = set(agg_full_gate["grown_sets_per_seed"][agg_full_gate["per_seed"][0]["seed"]])
    growth_gate_arm_invariant = bool(grown_argtype == grown_full_gate)
    growth_gate_diff = sorted(grown_argtype.symmetric_difference(grown_full_gate))

    localize = []
    if vacuous:
        localize.append("REQUIRED_NEGATIVE_CONTROL_DID_NOT_FIRE: ablation population_separated_frac=%.2f "
                        "(expected 0.0 -- arg-type-only must collide on the WHOLE population)"
                        % agg_argtype["population_separated_frac_ablation_mean"])
    if not order_ok:
        localize.append("ORDER_PAIR (grims,florps) did not separate under FULL as designed")
    if not cooccur_ok:
        localize.append("COOCCUR_PAIR (krendles,shleps) did not separate under FULL as designed")
    if agg_argtype["defeat_pair_separated_full_any"]:
        localize.append("DEFEAT_PAIR (vorbs,dringles) UNEXPECTEDLY separated under FULL -- defeat construction "
                        "failed to defeat the discriminator (bug in defeat design, not a discriminator win)")
    if not growth_ok:
        localize.append("legitimate growth broken under production ARGTYPE_GATE for one or more relations")
    if not regressions_ok:
        localize.append("regression control leaked (violation admitted OR trelps confirmed under K=3)")
    if hard_pass_core and not interleave_robust:
        localize.append("interleave-order dependence detected (genuinely different finding, not fatal)")
    weakest = localize if localize else ["none (population separates as designed; required defeat case genuinely "
                                          "collides; ablation collides population-wide; growth intact; robust to "
                                          "genuine interleave-order variance)"]

    msg = (f"{tier} | POPULATION: separated_full={agg_argtype['population_separated_frac_full_mean']:.2f} "
           f"separated_ablation={agg_argtype['population_separated_frac_ablation_mean']:.2f} (15 pairs, 6 relations) | "
           f"ORDER_PAIR(grims,florps) sep_full={order_ok} | COOCCUR_PAIR(krendles,shleps) sep_full={cooccur_ok} | "
           f"DEFEAT_PAIR(vorbs,dringles) collides_full={not agg_argtype['defeat_pair_separated_full_any']} "
           f"(REQUIRED honest failure) | ablation_control_fired={ablation_control_fired} | "
           f"growth_ok={growth_ok} regressions_ok={regressions_ok} "
           f"interleave_robust={interleave_robust} (genuine_variance={genuine_variance}) | "
           f"growth_gate_arm_invariant_at_k3={growth_gate_arm_invariant} "
           f"(EXPLORATORY, not gated; diff={growth_gate_diff}; FULL_STRUCTURAL_GATE correctly blocks the "
           f"deliberately-contradictory zant but ALSO incorrectly blocks the legitimate reciprocal florps -- "
           f"order-consistency cannot distinguish genuine-reciprocal from noise as a hard growth gate) | "
           f"weakest={weakest}")
    return tier, msg, weakest, {
        "ablation_control_fired": ablation_control_fired,
        "growth_gate_arm_invariant_at_k3": growth_gate_arm_invariant,
        "growth_gate_diff": growth_gate_diff,
    }


# ---------------------------------------------------------------------------
# infra.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": "exp_read_grow_relation_identity_v2",
           "smoke": "exp_read_grow_relation_identity_v2_smoke",
           "self_test": "exp_read_grow_relation_identity_v2_selftest"}[run_mode]
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
          "_relation_args_coherent / _order_consistency / _co_occurrence_with_known functions)...", flush=True)
    exercised = set()

    # (1) parser sanity on a representative new-relation sentence.
    kn = set(ENTITIES); kv = set(KNOWN_VERB_FORMS.keys()); kr = set(RELATIONS)
    tr, mt, rule, fr = ie_extract_openvocab("The cat vorbs the frog.", kn, kv, kr)
    assert tr == [("cat", "vorbs", "frog")] and mt[0]["new_rel"] and rule == "NEW_RELATION", "vorbs not flagged"
    exercised.add("ie_extract_openvocab")

    # (2) genuine interleave-order variance (design-check claim re-verified inline, not just asserted).
    orders = {seed: tuple(d["kind"] for d in build_interleaved_corpus(seed)[13:20]) for seed in [11, 23, 37]}
    assert len(set(orders.values())) > 1, "interleave shuffle produced IDENTICAL order across seeds -- not a real variance axis"
    exercised.add("build_interleaved_corpus")

    # (3) full deterministic loop at seed=11, production ARGTYPE_GATE.
    run = run_identity_loop(11, "argtype_gate")
    exercised.add("run_identity_loop"); exercised.add("_relation_args_coherent")
    exercised.add("_order_consistency"); exercised.add("_co_occurrence_with_known")

    # (4) legitimate growth preserved for the whole population + zant (K=3 threshold).
    assert run["all_grown"], f"not all relations grew: {run['grown']}"
    assert run["all_facts_in_store"], "grown relations missing accepted facts"
    assert run["relation_query_acc"] >= 0.99, f"grown facts not queryable: {run['relation_query_acc']}"

    # (5) REQUIRED NEGATIVE CONTROL: ablation collides on the WHOLE population (0/15 separated).
    assert run["population_separated_frac_ablation"] == 0.0, \
        f"ablation unexpectedly separated some population pairs: {run['population_separated_frac_ablation']}"

    # (6) designed SUCCESS pairs separate under FULL.
    assert run["order_pair_separated_full"], "ORDER_PAIR (grims,florps) failed to separate under FULL"
    assert run["cooccur_pair_separated_full"], "COOCCUR_PAIR (krendles,shleps) failed to separate under FULL"
    assert not run["order_pair_separated_ablation"], "ORDER_PAIR unexpectedly separated under ablation"
    assert not run["cooccur_pair_separated_ablation"], "COOCCUR_PAIR unexpectedly separated under ablation"

    # (7) REQUIRED DEFEAT: vorbs/dringles genuinely collide under FULL (the honest failure, not hidden).
    assert not run["defeat_pair_separated_full"], \
        f"DEFEAT_PAIR unexpectedly separated: {run['sig_full']['vorbs']} vs {run['sig_full']['dringles']}"
    assert run["sig_full"]["vorbs"] == run["sig_full"]["dringles"] == [True, True, []], \
        f"defeat signatures not the expected (True,True,{{}}) collision: {run['sig_full']['vorbs']} / {run['sig_full']['dringles']}"

    # (8) population separation fraction is measurably BETWEEN 0 and 1 (neither trivially all-pass nor all-fail).
    assert 0.0 < run["population_separated_frac_full"] < 1.0, \
        f"population_separated_frac_full={run['population_separated_frac_full']} not a genuine mixed result"

    # (9) regression controls.
    assert run["violation_rejected"], "type-violation regression control leaked"
    assert run["trelps_not_confirmed"], "K=3 threshold control leaked (trelps confirmed on 2 exposures)"

    # (10) ARMS-MUST-DIFFER (META_RULE_AF): FULL vs ABLATION signature representations differ (hash-checked),
    #      measured over the WHOLE population (not just one pair).
    h_full = hashlib.sha256(json.dumps(run["sig_full"], sort_keys=True).encode()).hexdigest()
    h_abl = hashlib.sha256(json.dumps(run["sig_ablation"], sort_keys=True).encode()).hexdigest()
    assert h_full != h_abl, "META_RULE_AF: FULL vs ABLATION population signature representations bit-identical"

    # (11) growth-gate stress: ARGTYPE_GATE vs FULL_STRUCTURAL_GATE diverge (EXPLORATORY, measured at self-test).
    run_full_gate = run_identity_loop(11, "full_structural_gate")
    diff = set(run["grown"]).symmetric_difference(set(run_full_gate["grown"]))
    assert diff == {"florps", "zant"}, \
        f"growth-gate divergence not the expected {{florps,zant}}: got {diff} (grown argtype={run['grown']} full_gate={run_full_gate['grown']})"

    for ep in ["ie_extract_openvocab", "run_identity_loop", "_relation_args_coherent",
               "_order_consistency", "_co_occurrence_with_known", "build_interleaved_corpus"]:
        assert ep in exercised, f"real_code_path: entrypoint {ep} not exercised"

    print(f"[self_test] PASS | population_separated_frac_full={run['population_separated_frac_full']:.2f} "
          f"ablation={run['population_separated_frac_ablation']:.2f} | "
          f"ORDER_PAIR sep={run['order_pair_separated_full']} COOCCUR_PAIR sep={run['cooccur_pair_separated_full']} "
          f"DEFEAT_PAIR collides={not run['defeat_pair_separated_full']} | "
          f"growth_gate_diff(argtype vs full_structural)={sorted(diff)}", flush=True)
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
    expected_n_units = len(seeds) * 2   # 2 gate-mode arms x seeds
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[relation_identity_v2] run_mode={run_mode} seeds={seeds} population={IDENTITY_POPULATION} "
          f"CONFIRM_K={CONFIRM_K} (bumped from v1's K=2)", flush=True)

    agg_argtype = avg_seeds(seeds, "argtype_gate")
    agg_full_gate = avg_seeds(seeds, "full_structural_gate")
    print(f"[relation_identity_v2] ARGTYPE_GATE population_separated_frac_full={agg_argtype['population_separated_frac_full_mean']:.3f} "
          f"ablation={agg_argtype['population_separated_frac_ablation_mean']:.3f} "
          f"all_grown_all={agg_argtype['all_grown_all']} interleave_robust={agg_argtype['interleave_robust_across_seeds']}", flush=True)
    print(f"[relation_identity_v2] FULL_STRUCTURAL_GATE grown_sets_per_seed={agg_full_gate['grown_sets_per_seed']}", flush=True)

    tier, msg, weakest, extra = compute_verdict(agg_argtype, agg_full_gate)
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
        "confirm_k": CONFIRM_K,
        "n_bootstrap_sentences": len(BOOTSTRAP_ROWS),
        "identity_population": IDENTITY_POPULATION,
        "expected_n_units": expected_n_units,
        "weakest_interface": weakest,
        # METRIC (a) population separation
        "metric_a_population_separated_frac_full": agg_argtype["population_separated_frac_full_mean"],
        "metric_a_population_separated_frac_ablation": agg_argtype["population_separated_frac_ablation_mean"],
        "metric_a_n_population_pairs": len(IDENTITY_POPULATION) * (len(IDENTITY_POPULATION) - 1) // 2,
        # METRIC (b) designated pairs
        "metric_b_order_pair": {"names": list(ORDER_PAIR), "separated_full": agg_argtype["order_pair_separated_full_all"],
                                 "separated_ablation": agg_argtype["order_pair_separated_ablation_any"]},
        "metric_b_cooccur_pair": {"names": list(COOCCUR_PAIR), "separated_full": agg_argtype["cooccur_pair_separated_full_all"],
                                   "separated_ablation": agg_argtype["cooccur_pair_separated_ablation_any"]},
        "metric_b_defeat_pair": {"names": list(DEFEAT_PAIR), "separated_full": agg_argtype["defeat_pair_separated_full_any"],
                                  "separated_ablation": agg_argtype["defeat_pair_separated_ablation_any"],
                                  "note": "separated_full MUST be False -- this is the required honest failure"},
        # METRIC (c) growth preserved
        "metric_c_all_grown_all": agg_argtype["all_grown_all"],
        "metric_c_all_facts_in_store_all": agg_argtype["all_facts_in_store_all"],
        "metric_c_relation_query_acc_mean": agg_argtype["relation_query_acc_mean"],
        # METRIC (d) regression controls
        "metric_d_violation_rejected_all": agg_argtype["violation_rejected_all"],
        "metric_d_trelps_k3_not_confirmed_all": agg_argtype["trelps_not_confirmed_all"],
        # METRIC (e) growth-gate stress (exploratory)
        "metric_e_growth_gate_arm_invariant_at_k3": extra["growth_gate_arm_invariant_at_k3"],
        "metric_e_growth_gate_diff": extra["growth_gate_diff"],
        # METRIC (f) interleave robustness
        "metric_f_interleave_robust_across_seeds": agg_argtype["interleave_robust_across_seeds"],
        "metric_f_interleave_orders_genuinely_differ": agg_argtype["interleave_orders_genuinely_differ"],
        "ablation_control_fired": extra["ablation_control_fired"],
        "arms": {
            "FULL_vs_ABLATION_population": {
                "sig_full_seed0": agg_argtype["per_seed"][0]["sig_full"],
                "sig_ablation_seed0": agg_argtype["per_seed"][0]["sig_ablation"],
            },
            "ARGTYPE_GATE_vs_FULL_STRUCTURAL_GATE": {
                "grown_argtype_gate": sorted(agg_argtype["grown_sets_per_seed"][seeds[0]]),
                "grown_full_structural_gate": sorted(agg_full_gate["grown_sets_per_seed"][seeds[0]]),
                "diff": extra["growth_gate_diff"],
            },
        },
        "argtype_gate_per_seed": agg_argtype["per_seed"],
        "full_structural_gate_per_seed": agg_full_gate["per_seed"],
        "prereg": {
            "hard_pass": "ablation_population_separated_frac==0.0 & ORDER_PAIR sep_full & COOCCUR_PAIR sep_full & "
                        "NOT DEFEAT_PAIR sep_full (required honest failure) & all_grown_all & "
                        "violation_rejected_all & trelps_k3_not_confirmed_all & interleave_robust_across_seeds",
            "hard_fail": "ablation_population_separated_frac>0.0 (VACUOUS) | ORDER_PAIR or COOCCUR_PAIR fails to "
                        "separate | DEFEAT_PAIR DOES separate (defeat construction bug) | growth broken | "
                        "regression control leaked",
            "middle_band": "HARD-PASS gates hold except interleave_robust_across_seeds (order-dependence found)",
            "population_fraction_reporting": "descriptive only, not gated to an exact pre-committed number "
                                             "(gating a population fraction discovered during corpus design would "
                                             "be circular; the pairwise separate/collide gates are the real claims)",
            "growth_gate_arm_invariant_scope": "EXPLORATORY/descriptive only; no pre-registered correct direction",
            "confirm_k": CONFIRM_K,
            "identity_population": IDENTITY_POPULATION,
            "order_pair": list(ORDER_PAIR), "cooccur_pair": list(COOCCUR_PAIR), "defeat_pair": list(DEFEAT_PAIR),
            "growth_gate_stress_relation": "zant",
            "compute_architecture": "sequential-CPU (foundation grows fact-by-fact; gate state depends on prior admits)",
            "storage_strategy": "sharded (one VSA vector per accepted fact, via imported FoundationStore)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["ie_extract_openvocab", "run_identity_loop", "_relation_args_coherent",
                                         "_order_consistency", "_co_occurrence_with_known", "build_interleaved_corpus"],
            "crlb_n/a": "no quantitative noise floor; discriminator is discrete structural-signature comparison "
                       "(set/boolean logic over accepted facts), not phasor decode noise",
            "prior_work_check": "direct expansion of exp_read_grow_relation_identity_v1 (commit 980eb1576) per "
                                "the Skunkworks VET's explicit expansion criterion; not a fresh substrate-KB query "
                                "(v1's prior-work check already established novelty of the underlying mechanism; "
                                "this cell is a population/failure-rate/growth-gate SCALE-UP of the same mechanism, "
                                "not a new concept).",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[relation_identity_v2] {tier} in {elapsed:.2f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[relation_identity_v2] {msg}", flush=True)
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
