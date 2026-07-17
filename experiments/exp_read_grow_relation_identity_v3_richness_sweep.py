"""exp_read_grow_relation_identity_v3_richness_sweep -- CORPUS-SCALE TIER-1 vs GENUINE TIER-3, per the
Skunkworks landed-VET on v2's expansion criterion (verbatim): "vary corpus richness (more known relations /
more co-occurrence opportunities) while holding the same defeat-pair construction, to test whether the ~27%
failure rate is genuinely corpus-scale-sensitive (supporting the 'not yet Tier-3' read) or persists even as
the corpus grows (which would start to look more like the Tier-3 bound)."

BACKGROUND (v2, commit d232a06ab): a 6-relation same-arg-type population measured population_separated_
frac_full=0.733 (11/15 pairs), i.e. a genuine ~27% (4/15) FAILURE cluster where relations collide on every
structural axis the widened signature (arg-type + order-consistency + co-occurrence-with-known) measures:
{grims,krendles} (both co-occur with `chases`) and {vorbs,dringles,shleps} (all have EMPTY co-occurrence --
their argument pairs happen to touch no known/other-new relation). The REQUIRED DEFEAT_PAIR is (vorbs,
dringles): both fixed-order, both co-occurrence-empty, LITERALLY IDENTICAL signature (True,True,{}).

QUESTION: is this failure rate a property of the MECHANISM (a genuine Tier-3 meaning-wall -- structure
categorically cannot separate them, no matter how much evidence accumulates) or a property of the CORPUS
SCALE this cell happened to test at (a genuine Tier-1 identity gap that a richer corpus -- more co-occurrence
context -- would close via the SAME structural mechanism, just with more evidence)? This cell holds the
DEFEAT_PAIR's construction (vorbs/dringles's own argument pairs and sentences) BYTE-IDENTICAL to v2 and
sweeps ONLY the surrounding corpus richness, then measures the population failure rate as a function of
richness. Glass-box, NO LLM, local numpy.

KEY MANIPULATION -- corpus richness (fair-chance, non-rigged): a NEUTRAL, pre-committed, pair-identity-
INDEPENDENT rule -- the canonical ALPHABETICAL enumeration of all C(5,2)=10 unordered pairs over the FIXED
5-animal vocabulary (bird,cat,cow,dog,frog) -- decides WHICH pairs accrue differentiating co-occurrence
context, in WHAT order, as richness grows. At richness level N, the first N pairs of this canonical list each
get ONE dedicated background relation (bg_p1..bg_pN, each a normal single-pair fixed-order new relation,
grown via the SAME CONFIRM_K=3 pipeline as every other population relation -- no special-cased shortcut).
This rule was fixed BEFORE any richness-specific tuning: it enumerates the ENTIRE pair space in a
non-cherry-picked order, and at the RICH level (N=10) covers 100% of the pair space -- including BOTH of
vorbs's pairs (cat-frog, dog-bird) AND BOTH of dringles's pairs (cow-cat, dog-frog) -- so neither relation's
argument pairs are permanently excluded from a fair chance to accrue differentiating context (the HONEST
GUARD the dispatching contract requires: a richness axis that never reaches the defeat pair's own pairs would
trivially and falsely look Tier-3). The canonical pair positions of DEFEAT_PAIR happen to be positions 3 and
7 (dog-bird, cat-frog) -- neither cherry-picked toward nor away from early coverage; they land where the
alphabetical rule puts them, exactly like every other population relation's pairs.

RICHNESS LEVELS (5, cumulative canonical-pair coverage N out of 10):
  NONE (N=0)     -- byte-identical to v2's corpus (REQUIRED positive-control reproduction, Gate D).
  MINIMAL (N=1)  -- covers position 1 (bird-cat = krendles's pair only).
  SPARSE (N=3)   -- covers positions 1-3 (adds bird-cow=shleps's pair, bird-dog=ONE of vorbs's two pairs).
  MODERATE (N=6) -- covers positions 1-6 (adds bird-frog + cat-dog = grims's two pairs, cat-cow = ONE of
                    dringles's two pairs).
  RICH (N=10)    -- FULL coverage (adds cat-frog = vorbs's other pair, cow-dog = florps's pair, cow-frog
                    unused, dog-frog = dringles's other pair). 100% of the pair space, both defeat-pair
                    relations fully covered.

MEASURED (HYPOTHESIZED@this-docstring, derived by hand-tracing the imported `_co_occurrence_with_known`
mechanism against the canonical-pair positions above BEFORE running; self-test verifies against the REAL
code): population failure rate (1 - separated_frac_full) should DECREASE from 4/15 (NONE) to 3/15 (MINIMAL,
grims/krendles resolve first since krendles's sole pair is position 1) to 0/15 (SPARSE onward, once
positions 2-3 land -- shleps and one of vorbs's two pairs -- vorbs and shleps both acquire non-empty,
mutually-DISTINCT co-occurrence sets, which is enough to separate the WHOLE trio {vorbs,dringles,shleps}
because dringles remains at empty co-occurrence until position 5). DEFEAT_PAIR specifically is HYPOTHESIZED
to separate starting at SPARSE (N=3) and remain separated through MODERATE/RICH (monotonic, no regression).
This is a genuine empirical claim, not baked into the pre-reg bands as a required exact number (see PRE-REG
below -- bands gate the QUALITATIVE SHAPE, not this specific hand-derived curve).

HONEST GUARD (explicit, not just claimed): the REQUIRED negative control (arg-type-only ablation) must
collide on the population at EVERY richness level, including RICH -- if richness ever caused the ABLATION
(which never reads co-occurrence) to spuriously separate anything, that would mean the richness manipulation
leaked into arg-type coherence itself, an implementation bug, not a real finding. Also: growth + regression
controls (violation-reject, K=3-threshold) must hold at every richness level -- richness must not break
anything else in the pipeline.

PRE-REG (envelope-fail-bands; I own the bands; set BEFORE running; the dual-hypothesis contract from the
dispatching prompt -- BOTH outcomes are pre-registered as informative HARD_PASS reads, only a broken/vacuous
run is HARD_FAIL):
  BASE CONTROLS (required at ALL 5 richness levels, gate everything below):
    - ablation_population_separated_frac == 0.0 at every level (required negative control never fires).
    - all population + background relations legitimately grow; all their facts land in the store.
    - violation_rejected and K=3-threshold (trelps) regression controls hold.
    - richness=NONE level reproduces v2 EXACTLY (Gate D positive control): population_separated_frac_full ==
      11/15, ablation == 0.0, ORDER_PAIR separates, COOCCUR_PAIR separates, DEFEAT_PAIR collides.
    - failure_rate(richness) is MONOTONICALLY NON-INCREASING across the 5 ordered levels (richness must never
      make things WORSE -- a violation would indicate a corpus-construction bug, not a real finding).
    - interleave-order robustness holds at every richness level (per-seed genuine variance, per v2's method).
  If any BASE CONTROL fails -> HARD_FAIL (result_class=BROKEN_OR_REGRESSED).
  HARD-PASS / result_class=CORPUS_SCALE_TIER1_FIXABLE: BASE CONTROLS hold AND failure_rate(RICH) <
    failure_rate(NONE) (strict decrease somewhere in the sweep) AND DEFEAT_PAIR separates under FULL by RICH
    on every seed. -> supports "not yet Tier-3, a corpus-scale identity gap that more differentiating
    co-occurrence context closes via the SAME structural mechanism."
  HARD-PASS / result_class=GENUINE_TIER3_MEANING_WALL: BASE CONTROLS hold AND failure_rate(RICH) ==
    failure_rate(NONE) (ZERO improvement across the full sweep, including at 100% pair-space coverage) AND
    DEFEAT_PAIR does NOT separate under FULL at RICH on any seed. -> supports "structure is categorically
    insufficient no matter how much differentiating evidence accumulates; this specific residue matches the
    literature's Tier-3 meaning-wall, not a data-scale artifact."
  MIDDLE_BAND / result_class=AMBIGUOUS_PARTIAL_RESOLUTION: BASE CONTROLS hold but the curve is neither a
    clean strict-decrease-with-defeat-pair-resolution nor a clean flat-plateau-with-defeat-pair-persistence
    (e.g., OTHER population pairs resolve with richness but DEFEAT_PAIR specifically does not, or seeds
    disagree on DEFEAT_PAIR's fate at RICH) -- reported descriptively, a genuinely interesting partial result
    per the dispatching contract ("either outcome is informative"), not forced into either clean bucket.
  Neither the exact richness thresholds (1/3/6/10) nor the exact failure-rate values at each level are gated
  to pre-committed numbers (that would be circular, per v2's own discipline) -- the pairwise/curve-SHAPE
  claims above are the real pre-registered bands.

Local numpy, no queue/GPU/atoms/push. ASCII-only. Sequential-CPU. Storage: SHARDED (imported FoundationStore).
progress_logging = print_flush_true (template consistency; wall time sub-second).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; FULL vs ARGTYPE_ONLY_ABLATION signature representations
#     differ at richness=NONE, hash-checked, matching v2's discipline).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor. Discriminator is discrete structural-signature comparison
#     (set/boolean logic over accepted facts), NOT phasor decode noise (same as v1/v2).
# - baseline_in_band at smoke: N/A (discrete logic discriminator) -- see discriminator-fires gate instead
#     (ablation_population_separated_frac == 0.0 required at every richness level).
# - discriminator survives scale: corpus is FIXED-size per richness level (hand-designed GT); deterministic
#     given the corpus. Verified at self-test against the hand-derived curve (see HYPOTHESIZED note above).
# - HARD_PASS strictly above floor; explicit bands above + in prereg JSON below.
# - real_code_path (F.1): self_test constructs the REAL imported objects (FoundationStore via
#     run_richness_loop, the REAL ie_extract_openvocab parser, the REAL _relation_args_coherent /
#     _order_consistency / _co_occurrence_with_known functions) at tiny scale and asserts.
# - deterministic seeding (F.5): fixed int seeds; sorted() vocab ordering; per-seed interleave rng
#     (offset +9000, matching v2); NO hash()/list(set()).
# - all numbers in comments tagged HYPOTHESIZED@docstring / MEASURED@metrics.
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

ANCHOR_NAME = "read_grow_relation_identity_v3_richness_sweep"

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
    _order_consistency,            # reused VERBATIM.
    _co_occurrence_with_known,     # reused VERBATIM.
    _relation_identity_signature,  # reused VERBATIM (mode in {"argtype_only","full"}).
    _sig_jsonable,                 # reused VERBATIM.
)

SUBJ, VERB, OBJ = 0, 1, 2
CONFIRM_K = 3   # matches v2 (LOCAL override, not the imported constant).

# ---------------------------------------------------------------------------
# BOOTSTRAP (byte-identical content to v2 -- copied not imported, corpus self-contained).
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
# IDENTITY POPULATION -- byte-identical construction to v2 (DEFEAT_PAIR HELD FIXED, per contract). zant
# (v2's growth-gate-stress axis) is DROPPED -- out of scope for this cell (richness-sweep only).
# ---------------------------------------------------------------------------
NEW_RELATION_PAIRS = {
    "grims":    [("cat", "dog"), ("bird", "frog"), ("cat", "dog")],
    "florps":   [("cow", "dog"), ("dog", "cow"), ("cow", "dog")],
    "krendles": [("cat", "bird"), ("cat", "bird"), ("cat", "bird")],
    "shleps":   [("cow", "bird"), ("cow", "bird"), ("cow", "bird")],
    "vorbs":    [("cat", "frog"), ("dog", "bird"), ("cat", "frog")],
    "dringles": [("cow", "cat"), ("dog", "frog"), ("cow", "cat")],
}
IDENTITY_POPULATION = ["grims", "florps", "krendles", "shleps", "vorbs", "dringles"]
ORDER_PAIR = ("grims", "florps")
COOCCUR_PAIR = ("krendles", "shleps")
DEFEAT_PAIR = ("vorbs", "dringles")     # HELD FIXED across all richness levels, per contract.

TRELPS_PAIRS = [("cow", "frog")] * 2    # CONFIRM_K=3 threshold control (must NOT confirm), any richness.
RELATION_VIOLATION = ("seed", "grims", "cat")

# ---------------------------------------------------------------------------
# RICHNESS AXIS -- neutral, pair-identity-independent canonical enumeration (alphabetical over the FIXED
# 5-animal vocabulary), decided BEFORE any richness-specific tuning. bg_pK relations are ordinary
# single-pair fixed-order new relations grown via the SAME CONFIRM_K=3 pipeline as every population relation
# -- no special-cased shortcut. See module docstring for the position derivation.
# ---------------------------------------------------------------------------
CANONICAL_PAIRS = [
    ("bird", "cat"),   # pos1  == krendles's pair
    ("bird", "cow"),   # pos2  == shleps's pair
    ("bird", "dog"),   # pos3  == ONE of vorbs's two pairs
    ("bird", "frog"),  # pos4  == ONE of grims's two pairs
    ("cat", "cow"),    # pos5  == ONE of dringles's two pairs
    ("cat", "dog"),    # pos6  == grims's other pair
    ("cat", "frog"),   # pos7  == vorbs's other pair
    ("cow", "dog"),    # pos8  == florps's pair
    ("cow", "frog"),   # pos9  == unused by the identity population
    ("dog", "frog"),   # pos10 == dringles's other pair
]
BG_RELATION_NAMES = [f"bg_p{k}" for k in range(1, len(CANONICAL_PAIRS) + 1)]
BG_PAIR_OF = {name: CANONICAL_PAIRS[k] for k, name in enumerate(BG_RELATION_NAMES)}

RICHNESS_LEVELS = [
    ("NONE", 0),      # byte-identical to v2.
    ("MINIMAL", 1),
    ("SPARSE", 3),
    ("MODERATE", 6),
    ("RICH", 10),     # FULL pair-space coverage (both defeat-pair relations fully covered).
]

DISTINCT_NEW_WORDS = sorted(set(NEW_RELATION_PAIRS.keys()) | {"trelps"} | set(BG_RELATION_NAMES))


def build_ext_concepts():
    """deterministic phasor codebook for every token (known + new + all possible bg names, regardless of
    richness level -- unused bg names simply never appear in a given run's corpus). Sorted concept ordering;
    no hash()/list(set()) (F.5)."""
    concepts = sorted(set(ENTITIES) | set(RELATIONS) | set(DISTINCT_NEW_WORDS))
    cid_idx = {c: i for i, c in enumerate(concepts)}
    return concepts, cid_idx


def _sentence_for(word, subj, obj):
    return f"The {subj} {word} the {obj}."


def build_interleaved_corpus(seed, richness_n):
    """GENUINE variance axis (per v2): round-robin-merge the per-relation exposure streams (each relation's
    OWN internal exposure order preserved) with a per-seed RNG interleave across relations + the K-threshold
    control + the richness_n background relations. Bootstrap is a fixed prefix; RELATION_VIOLATION is a
    fixed suffix (grims must already be grown)."""
    rng = np.random.default_rng(seed + 9000)   # same offset convention as v2.
    queues = {w: [(w, s, o) for (s, o) in pairs] for w, pairs in NEW_RELATION_PAIRS.items()}
    queues["trelps"] = [("trelps", s, o) for (s, o) in TRELPS_PAIRS]
    for name in BG_RELATION_NAMES[:richness_n]:
        s, o = BG_PAIR_OF[name]
        queues[name] = [(name, s, o)] * 3   # single-pair fixed-order, 3x (same style as krendles/shleps).
    words = sorted(queues.keys())   # deterministic base ordering before shuffle draws (F.5).
    order = []
    while any(queues[w] for w in words):
        avail = [w for w in words if queues[w]]
        pick = avail[int(rng.integers(0, len(avail)))]
        order.append(queues[pick].pop(0))

    rows = list(BOOTSTRAP_ROWS)
    for (word, s, o) in order:
        if word == "trelps":
            kind = "relation_distractor_k_threshold"
        elif word.startswith("bg_p"):
            kind = f"richness_bg:{word}"
        else:
            kind = f"new_relation:{word}"
        note = f"{word} exposure ({s}->{o})"
        rows.append(_row(_sentence_for(word, s, o), [(s, word, o)], kind, note))
    rows.append(_row(_sentence_for("grims", "seed", "cat"), [RELATION_VIOLATION], "relation_violation",
                      "seed (food) as grown-grims-subj -> reject"))
    return rows


# ---------------------------------------------------------------------------
# ONE read->grow loop for one seed + one richness level.
# ---------------------------------------------------------------------------
def run_richness_loop(seed, richness_n):
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
    corpus = build_interleaved_corpus(seed, richness_n)

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
            if argtype_ok:
                grown.add(nw)
                known_verbs.add(nw)
                known_rels.add(nw)
                for (ps, po) in obs:
                    commit_through_gate((ps, nw, po))
                rec.update(action="GROW_RELATION_CONFIRMED", triple=list(triple), argtype_ok=argtype_ok)
            else:
                rec.update(action="RELATION_HELD_INCOHERENT", triple=list(triple), argtype_ok=argtype_ok)
        else:
            rec.update(action="RELATION_PROVISIONAL", triple=list(triple))
        per_sentence.append(rec)

    store.reeval_holds()
    accepted = store.accepted

    # ---- population signatures (post-hoc, over the FINAL store state) -- IDENTITY_POPULATION only ----
    sig_full, sig_abl = {}, {}
    for w in IDENTITY_POPULATION:
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

    all_grown_pop = bool(all(w in grown for w in IDENTITY_POPULATION))
    bg_names = BG_RELATION_NAMES[:richness_n]
    all_grown_bg = bool(all(w in grown for w in bg_names))
    all_facts_in_store = bool(
        all((s, w, o) in accepted for w, pairs in NEW_RELATION_PAIRS.items() for (s, o) in pairs) and
        all((BG_PAIR_OF[w][0], w, BG_PAIR_OF[w][1]) in accepted for w in bg_names)
    )
    violation_rejected = bool(RELATION_VIOLATION not in accepted)
    trelps_not_confirmed = bool(("cow", "trelps", "frog") not in accepted and "trelps" not in grown)

    q_ok, q_total = 0, 0
    for w, pairs in NEW_RELATION_PAIRS.items():
        for (s, o) in set(pairs):
            q_total += 1
            if (s, w, o) in accepted and store.query(s, w) == o:
                q_ok += 1
    relation_query_acc = (q_ok / float(q_total)) if q_total else 0.0

    return {
        "seed": seed, "richness_n": richness_n,
        "grown": sorted(grown),
        "sig_full": {w: _sig_jsonable(sig_full[w]) for w in sig_full},
        "sig_ablation": {w: _sig_jsonable(sig_abl[w]) for w in sig_abl},
        "population_separated_frac_full": population_separated_frac_full,
        "population_separated_frac_ablation": population_separated_frac_ablation,
        "pop_pairs": pop_pairs,
        "order_pair_separated_full": order_sep_full, "order_pair_separated_ablation": order_sep_abl,
        "cooccur_pair_separated_full": cooccur_sep_full, "cooccur_pair_separated_ablation": cooccur_sep_abl,
        "defeat_pair_separated_full": defeat_sep_full, "defeat_pair_separated_ablation": defeat_sep_abl,
        "all_grown_pop": all_grown_pop, "all_grown_bg": all_grown_bg,
        "all_facts_in_store": all_facts_in_store,
        "violation_rejected": violation_rejected,
        "trelps_not_confirmed": trelps_not_confirmed,
        "relation_query_acc": relation_query_acc,
        "accepted_hash": store.accepted_hash(),
        "corpus_order_head": [d["kind"] for d in build_interleaved_corpus(seed, richness_n)][13:23],
    }


def avg_seeds_at_richness(seeds, richness_n):
    runs = [run_richness_loop(s, richness_n) for s in seeds]
    baseline = runs[0]
    interleave_robust = bool(all(
        r["grown"] == baseline["grown"] and r["sig_full"] == baseline["sig_full"]
        and r["sig_ablation"] == baseline["sig_ablation"]
        for r in runs[1:]
    ))
    interleave_orders_genuinely_differ = bool(len({tuple(r["corpus_order_head"]) for r in runs}) > 1)
    out = {
        "richness_n": richness_n,
        "population_separated_frac_full_mean": float(np.mean([r["population_separated_frac_full"] for r in runs])),
        "population_separated_frac_ablation_mean": float(np.mean([r["population_separated_frac_ablation"] for r in runs])),
        "order_pair_separated_full_all": bool(all(r["order_pair_separated_full"] for r in runs)),
        "order_pair_separated_ablation_any": bool(any(r["order_pair_separated_ablation"] for r in runs)),
        "cooccur_pair_separated_full_all": bool(all(r["cooccur_pair_separated_full"] for r in runs)),
        "cooccur_pair_separated_ablation_any": bool(any(r["cooccur_pair_separated_ablation"] for r in runs)),
        "defeat_pair_separated_full_all": bool(all(r["defeat_pair_separated_full"] for r in runs)),
        "defeat_pair_separated_full_any": bool(any(r["defeat_pair_separated_full"] for r in runs)),
        "defeat_pair_separated_ablation_any": bool(any(r["defeat_pair_separated_ablation"] for r in runs)),
        "all_grown_pop_all": bool(all(r["all_grown_pop"] for r in runs)),
        "all_grown_bg_all": bool(all(r["all_grown_bg"] for r in runs)),
        "all_facts_in_store_all": bool(all(r["all_facts_in_store"] for r in runs)),
        "violation_rejected_all": bool(all(r["violation_rejected"] for r in runs)),
        "trelps_not_confirmed_all": bool(all(r["trelps_not_confirmed"] for r in runs)),
        "relation_query_acc_mean": float(np.mean([r["relation_query_acc"] for r in runs])),
        "interleave_robust_across_seeds": interleave_robust,
        "interleave_orders_genuinely_differ": interleave_orders_genuinely_differ,
        "grown_sets_per_seed": {r["seed"]: r["grown"] for r in runs},
        "per_seed": runs,
    }
    return out


def run_richness_sweep(seeds):
    aggs = []
    for name, n in RICHNESS_LEVELS:
        agg = avg_seeds_at_richness(seeds, n)
        agg["richness_name"] = name
        aggs.append(agg)
    return aggs


# ---------------------------------------------------------------------------
# Verdict (envelope-fail-bands per pre-reg; dual-hypothesis contract).
# ---------------------------------------------------------------------------
def compute_verdict(aggs):
    ablation_control_fired_all = all(a["population_separated_frac_ablation_mean"] == 0.0 for a in aggs)
    growth_ok_all = all(a["all_grown_pop_all"] and a["all_grown_bg_all"] and a["all_facts_in_store_all"] for a in aggs)
    regressions_ok_all = all(a["violation_rejected_all"] and a["trelps_not_confirmed_all"] for a in aggs)
    interleave_robust_all = all(a["interleave_robust_across_seeds"] for a in aggs)
    genuine_variance_all = all(a["interleave_orders_genuinely_differ"] for a in aggs)

    none_level = aggs[0]
    rich_level = aggs[-1]
    assert none_level["richness_name"] == "NONE" and rich_level["richness_name"] == "RICH"

    # Gate D positive control: richness=NONE must reproduce v2 EXACTLY.
    v2_reproduction_ok = (
        abs(none_level["population_separated_frac_full_mean"] - (11.0 / 15.0)) < 1e-9 and
        none_level["population_separated_frac_ablation_mean"] == 0.0 and
        none_level["order_pair_separated_full_all"] and
        none_level["cooccur_pair_separated_full_all"] and
        not none_level["defeat_pair_separated_full_any"]
    )

    failure_rate_curve = [1.0 - a["population_separated_frac_full_mean"] for a in aggs]
    monotonic_non_increasing = all(
        failure_rate_curve[i + 1] <= failure_rate_curve[i] + 1e-9 for i in range(len(failure_rate_curve) - 1)
    )
    strict_decrease = failure_rate_curve[-1] < failure_rate_curve[0] - 1e-9

    defeat_pair_resolved_by_rich = rich_level["defeat_pair_separated_full_all"]
    defeat_pair_persists_at_rich = not rich_level["defeat_pair_separated_full_any"]

    base_controls_ok = (ablation_control_fired_all and growth_ok_all and regressions_ok_all and v2_reproduction_ok)
    hard_fail = (not base_controls_ok) or (not monotonic_non_increasing)

    if hard_fail:
        tier = "HARD_FAIL"
        result_class = "BROKEN_OR_REGRESSED"
    elif strict_decrease and defeat_pair_resolved_by_rich and interleave_robust_all:
        tier = "HARD_PASS"
        result_class = "CORPUS_SCALE_TIER1_FIXABLE"
    elif (not strict_decrease) and defeat_pair_persists_at_rich and interleave_robust_all:
        tier = "HARD_PASS"
        result_class = "GENUINE_TIER3_MEANING_WALL"
    else:
        tier = "MIDDLE_BAND"
        result_class = "AMBIGUOUS_PARTIAL_RESOLUTION"

    localize = []
    if not ablation_control_fired_all:
        localize.append("REQUIRED_NEGATIVE_CONTROL_LEAKED at some richness level (ablation separated something)")
    if not growth_ok_all:
        localize.append("legitimate growth (population or background relations) broken at some richness level")
    if not regressions_ok_all:
        localize.append("regression control leaked (violation admitted OR trelps confirmed) at some richness level")
    if not v2_reproduction_ok:
        localize.append("GATE_D_POSITIVE_CONTROL_FAILED: richness=NONE did not reproduce v2's measured numbers")
    if not monotonic_non_increasing:
        localize.append("NON_MONOTONIC: failure rate INCREASED at some richness step (corpus-construction bug "
                        "suspected, not a real finding) curve=%s" % failure_rate_curve)
    if hard_fail is False and tier == "MIDDLE_BAND":
        localize.append("ambiguous curve shape: strict_decrease=%s defeat_pair_resolved_by_rich=%s "
                        "defeat_pair_persists_at_rich=%s interleave_robust_all=%s"
                        % (strict_decrease, defeat_pair_resolved_by_rich, defeat_pair_persists_at_rich,
                           interleave_robust_all))
    weakest = localize if localize else ["none (base controls hold; curve shape is a clean, decisive read)"]

    msg = (f"{tier} | result_class={result_class} | failure_rate_curve(NONE->RICH)={[round(x,3) for x in failure_rate_curve]} "
           f"| DEFEAT_PAIR(vorbs,dringles): collides_at_NONE={not none_level['defeat_pair_separated_full_any']} "
           f"resolved_by_RICH(all_seeds)={defeat_pair_resolved_by_rich} persists_at_RICH(no_seed_separates)={defeat_pair_persists_at_rich} "
           f"| ablation_control_fired_all_levels={ablation_control_fired_all} growth_ok_all={growth_ok_all} "
           f"regressions_ok_all={regressions_ok_all} v2_reproduction_ok={v2_reproduction_ok} "
           f"monotonic_non_increasing={monotonic_non_increasing} interleave_robust_all={interleave_robust_all} "
           f"(genuine_variance={genuine_variance_all}) | weakest={weakest}")
    return tier, result_class, msg, weakest, {
        "ablation_control_fired_all": ablation_control_fired_all,
        "failure_rate_curve": failure_rate_curve,
        "monotonic_non_increasing": monotonic_non_increasing,
        "strict_decrease": strict_decrease,
        "defeat_pair_resolved_by_rich": defeat_pair_resolved_by_rich,
        "defeat_pair_persists_at_rich": defeat_pair_persists_at_rich,
        "v2_reproduction_ok": v2_reproduction_ok,
    }


# ---------------------------------------------------------------------------
# infra.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": "exp_read_grow_relation_identity_v3_richness_sweep",
           "smoke": "exp_read_grow_relation_identity_v3_richness_sweep_smoke",
           "self_test": "exp_read_grow_relation_identity_v3_richness_sweep_selftest"}[run_mode]
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

    kn = set(ENTITIES); kv = set(KNOWN_VERB_FORMS.keys()); kr = set(RELATIONS)
    tr, mt, rule, fr = ie_extract_openvocab("The cat vorbs the frog.", kn, kv, kr)
    assert tr == [("cat", "vorbs", "frog")] and mt[0]["new_rel"] and rule == "NEW_RELATION", "vorbs not flagged"
    exercised.add("ie_extract_openvocab")

    orders = {seed: tuple(d["kind"] for d in build_interleaved_corpus(seed, 10)[13:20]) for seed in [11, 23, 37]}
    assert len(set(orders.values())) > 1, "interleave shuffle produced IDENTICAL order across seeds"
    exercised.add("build_interleaved_corpus")

    seeds = [11, 23]
    aggs = run_richness_sweep(seeds)
    exercised.add("run_richness_loop"); exercised.add("_relation_args_coherent")
    exercised.add("_order_consistency"); exercised.add("_co_occurrence_with_known")

    none_level = aggs[0]
    minimal_level = aggs[1]
    sparse_level = aggs[2]
    rich_level = aggs[-1]

    # (1) GATE D positive control: richness=NONE reproduces v2 EXACTLY.
    assert abs(none_level["population_separated_frac_full_mean"] - (11.0 / 15.0)) < 1e-9, \
        f"richness=NONE did not reproduce v2's 11/15: got {none_level['population_separated_frac_full_mean']}"
    assert none_level["population_separated_frac_ablation_mean"] == 0.0, "ablation control did not fire at NONE"
    assert none_level["order_pair_separated_full_all"], "ORDER_PAIR failed to separate at NONE"
    assert none_level["cooccur_pair_separated_full_all"], "COOCCUR_PAIR failed to separate at NONE"
    assert not none_level["defeat_pair_separated_full_any"], "DEFEAT_PAIR unexpectedly separated at NONE (v2 mismatch)"

    # (2) required negative control fires at EVERY richness level (including RICH -- richness must not leak
    #     into arg-type coherence).
    for a in aggs:
        assert a["population_separated_frac_ablation_mean"] == 0.0, \
            f"ablation control leaked at richness={a['richness_name']}: {a['population_separated_frac_ablation_mean']}"

    # (3) growth + regression controls hold at every richness level.
    for a in aggs:
        assert a["all_grown_pop_all"], f"population growth broken at richness={a['richness_name']}"
        assert a["all_grown_bg_all"], f"background-relation growth broken at richness={a['richness_name']}"
        assert a["all_facts_in_store_all"], f"facts missing from store at richness={a['richness_name']}"
        assert a["violation_rejected_all"], f"type-violation control leaked at richness={a['richness_name']}"
        assert a["trelps_not_confirmed_all"], f"K=3 threshold control leaked at richness={a['richness_name']}"
        assert a["relation_query_acc_mean"] >= 0.99, f"query accuracy broken at richness={a['richness_name']}"

    # (4) failure rate is monotonically non-increasing across the sweep (no regression).
    failure_curve = [1.0 - a["population_separated_frac_full_mean"] for a in aggs]
    for i in range(len(failure_curve) - 1):
        assert failure_curve[i + 1] <= failure_curve[i] + 1e-9, \
            f"NON-MONOTONIC failure rate: {failure_curve}"

    # (5) HYPOTHESIZED curve shape (hand-derived in module docstring; genuine empirical assertion, not a
    #     tautology -- verified against the REAL mechanism here): failure drops 4/15 -> 3/15 at MINIMAL
    #     (grims/krendles resolve first via position-1 = krendles's sole pair), then to 0/15 by SPARSE
    #     (positions 2-3 land, resolving the vorbs/dringles/shleps trio including DEFEAT_PAIR), then plateaus.
    assert abs(minimal_level["population_separated_frac_full_mean"] - (12.0 / 15.0)) < 1e-9, \
        f"MINIMAL level unexpected separated_frac: {minimal_level['population_separated_frac_full_mean']} (expected 12/15)"
    assert abs(sparse_level["population_separated_frac_full_mean"] - 1.0) < 1e-9, \
        f"SPARSE level unexpected separated_frac: {sparse_level['population_separated_frac_full_mean']} (expected 1.0)"
    assert abs(rich_level["population_separated_frac_full_mean"] - 1.0) < 1e-9, \
        f"RICH level unexpected separated_frac: {rich_level['population_separated_frac_full_mean']} (expected 1.0)"

    # (6) DEFEAT_PAIR specifically: collides at NONE and MINIMAL, separates from SPARSE onward, on every seed.
    assert not none_level["defeat_pair_separated_full_any"], "DEFEAT_PAIR unexpectedly separated at NONE"
    assert not minimal_level["defeat_pair_separated_full_any"], "DEFEAT_PAIR unexpectedly separated at MINIMAL"
    assert sparse_level["defeat_pair_separated_full_all"], "DEFEAT_PAIR failed to separate by SPARSE (all seeds)"
    assert rich_level["defeat_pair_separated_full_all"], "DEFEAT_PAIR failed to separate at RICH (all seeds)"

    # (7) ARMS-MUST-DIFFER (META_RULE_AF): FULL vs ABLATION population-signature hashes differ at NONE.
    h_full = hashlib.sha256(json.dumps(none_level["per_seed"][0]["sig_full"], sort_keys=True).encode()).hexdigest()
    h_abl = hashlib.sha256(json.dumps(none_level["per_seed"][0]["sig_ablation"], sort_keys=True).encode()).hexdigest()
    assert h_full != h_abl, "META_RULE_AF: FULL vs ABLATION population signature representations bit-identical"

    # (8) interleave robustness across seeds at every richness level.
    for a in aggs:
        assert a["interleave_robust_across_seeds"], f"interleave-order dependence at richness={a['richness_name']}"
        assert a["interleave_orders_genuinely_differ"], f"interleave shuffle not genuinely varying at richness={a['richness_name']}"

    tier, result_class, msg, weakest, extra = compute_verdict(aggs)
    assert tier == "HARD_PASS" and result_class == "CORPUS_SCALE_TIER1_FIXABLE", \
        f"self-test 2-seed sweep did not land HARD_PASS/CORPUS_SCALE_TIER1_FIXABLE: tier={tier} result_class={result_class} msg={msg}"

    for ep in ["ie_extract_openvocab", "run_richness_loop", "_relation_args_coherent",
               "_order_consistency", "_co_occurrence_with_known", "build_interleaved_corpus"]:
        assert ep in exercised, f"real_code_path: entrypoint {ep} not exercised"

    print(f"[self_test] PASS | failure_rate_curve={[round(x,3) for x in failure_curve]} | "
          f"DEFEAT_PAIR collides_NONE={not none_level['defeat_pair_separated_full_any']} "
          f"resolved_by_SPARSE={sparse_level['defeat_pair_separated_full_all']} | tier={tier} result_class={result_class}",
          flush=True)
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
    expected_n_units = len(seeds) * len(RICHNESS_LEVELS)
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[relation_identity_v3] run_mode={run_mode} seeds={seeds} richness_levels={RICHNESS_LEVELS} "
          f"population={IDENTITY_POPULATION} CONFIRM_K={CONFIRM_K}", flush=True)

    aggs = run_richness_sweep(seeds)
    for a in aggs:
        print(f"[relation_identity_v3] richness={a['richness_name']}(N={a['richness_n']}) "
              f"separated_full={a['population_separated_frac_full_mean']:.3f} "
              f"ablation={a['population_separated_frac_ablation_mean']:.3f} "
              f"defeat_pair_separated_all={a['defeat_pair_separated_full_all']}", flush=True)

    tier, result_class, msg, weakest, extra = compute_verdict(aggs)
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
        "result_class": result_class,
        "richness_levels": RICHNESS_LEVELS,
        # METRIC: failure-rate-vs-richness curve (the deliverable).
        "metric_failure_rate_curve": extra["failure_rate_curve"],
        "metric_monotonic_non_increasing": extra["monotonic_non_increasing"],
        "metric_strict_decrease": extra["strict_decrease"],
        "metric_defeat_pair_resolved_by_rich": extra["defeat_pair_resolved_by_rich"],
        "metric_defeat_pair_persists_at_rich": extra["defeat_pair_persists_at_rich"],
        "metric_v2_reproduction_ok": extra["v2_reproduction_ok"],
        "metric_ablation_control_fired_all_levels": extra["ablation_control_fired_all"],
        "per_richness_level": [strip(a) for a in aggs],
        "defeat_pair_names": list(DEFEAT_PAIR),
        "order_pair_names": list(ORDER_PAIR),
        "cooccur_pair_names": list(COOCCUR_PAIR),
        "canonical_pairs": CANONICAL_PAIRS,
        "per_richness_level_full": aggs,
        "prereg": {
            "hard_pass_corpus_scale": "base_controls_ok & strict_decrease & DEFEAT_PAIR separates under FULL "
                                      "by RICH on every seed -> corpus-scale Tier-1, fixable via richer context",
            "hard_pass_tier3": "base_controls_ok & NOT strict_decrease (zero improvement NONE->RICH) & "
                               "DEFEAT_PAIR does NOT separate under FULL at RICH on any seed -> genuine "
                               "Tier-3 meaning-wall, structure categorically insufficient",
            "hard_fail": "any base control fails (ablation leak, growth break, regression leak, v2-reproduction "
                        "mismatch) OR failure rate is non-monotonic (increases at some richness step)",
            "middle_band": "base controls hold but curve shape is neither clean corpus-scale nor clean Tier-3 "
                           "(e.g. other pairs resolve but DEFEAT_PAIR persists, or seeds disagree)",
            "richness_operationalization": "cumulative canonical-pair-space coverage (alphabetical over the "
                                           "fixed 5-animal vocabulary), N in {0,1,3,6,10} out of 10 total pairs; "
                                           "background relations grown via the SAME CONFIRM_K=3 pipeline as "
                                           "every population relation, no special-cased shortcut",
            "honest_guard": "RICH level covers 100% of the pair space, including BOTH of vorbs's and BOTH of "
                            "dringles's argument pairs -- neither defeat-pair relation is permanently excluded "
                            "from a fair chance to accrue differentiating co-occurrence context",
            "defeat_pair_held_fixed": "vorbs/dringles's own NEW_RELATION_PAIRS entries are byte-identical to "
                                      "v2 across all 5 richness levels; only the surrounding corpus changes",
            "compute_architecture": "sequential-CPU (foundation grows fact-by-fact; gate state depends on prior admits)",
            "storage_strategy": "sharded (one VSA vector per accepted fact, via imported FoundationStore)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "real_code_path_exercised": ["ie_extract_openvocab", "run_richness_loop", "_relation_args_coherent",
                                         "_order_consistency", "_co_occurrence_with_known", "build_interleaved_corpus"],
            "crlb_n/a": "no quantitative noise floor; discriminator is discrete structural-signature comparison, "
                       "not phasor decode noise",
            "prior_work_check": "substrate_query.sh 'relation identity corpus richness co-occurrence context "
                                "sweep failure rate' -> top hits cosine 0.30-0.32 concern LLM context-richness/"
                                "contradiction-rate correlation (mycorrhizal drill, different domain) and a "
                                "generic WordNet 'co-occurrence' term -- NOT the same mechanism. Genuinely novel "
                                "application; this cell is also a direct, Skunkworks-VET-mandated expansion of "
                                "exp_read_grow_relation_identity_v2 (commit d232a06ab), same mechanism class as "
                                "v1/v2's already-established novelty.",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[relation_identity_v3] {tier} ({result_class}) in {elapsed:.2f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[relation_identity_v3] {msg}", flush=True)
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
