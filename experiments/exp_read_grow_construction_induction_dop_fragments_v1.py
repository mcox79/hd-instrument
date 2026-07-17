"""exp_read_grow_construction_induction_dop_fragments_v1 -- MINIMAL FEASIBILITY PROBE of Prediction 2 from
notes/research_how_brain_does_broad_construction_parsing_synthesis_2026-07-17.md: can the substrate GROW a
glass-box construction inventory from a reading corpus (variable-grain form-meaning fragments, INDUCED from
exposure, scored/selected by the SAME -log P surprisal primitive already built for the ingest gate) that COVERS
held-out construction instances the hand-rule toy grammar (Rung 5's analyze_sentence classifier) kept missing,
WITHOUT per-construction hand-authoring?

WHY (verbatim synthesis pointer): the brain's broad parser = a LARGE LEARNED CONSTRUCTION INVENTORY (form-
meaning pairs, all grain sizes, no lexicon/grammar divide), GROWN usage-based from exposure (Tomasello:
item-based -> abstracted-schema via entrenchment/frequency), used predictively via surprisal (-log P). DOP
(Bod) is the closest engineering analog: variable-size, partially-lexicalized fragments, explicitly framed by
its own author as a computational instantiation of usage-based/constructivist theory. Unsupervised grammar
induction (CCM/compound-PCFG) is the closest analog to grow-from-raw-exposure (no pre-imposed tagset). The
onion-peeling arc (Rungs 5-9, hand-authored per-construction fixes) showed a PERSISTENT construction-coverage
tail (58.6%/59.9% "other_unhandled" on general UD-EWT prose, MEASURED@this-cell's own reproduction below,
re-surfacing 2 NEW bug classes even after the Rung-9 milestone). Prediction 2 asks whether a GROWN inventory
covers that tail without hand-authoring each new pattern.

SCOPE DECISION (declared, not hidden, per this arc's own convention): a full DOP implementation enumerates
ALL connected subtrees of every parse and keeps them LEXICALLY FILLED (word-specific). That is combinatorially
large and, on a small corpus, would almost never recur between an induction split and a disjoint held-out split
(too sparse to show genuine growth). This feasibility probe uses a SCOPED variant: constructions are
POS+deprel SHAPE fragments (partially abstracted -- the "form" axis) at TWO grain sizes (depth-1: a token +
its own children's deprel-shape; depth-2: a token + its children's deprel-shape + each qualifying child's OWN
children's deprel-shape, capturing nested constructions like relative clauses / passives / coordination) --
this is the CxG "abstract schema" end of the form-meaning continuum, not the fully-lexicalized idiom end. The
UD deprel labels themselves (nsubj/obj/obl/acl:relcl/aux:pass/conj/...) are treated as the MEANING component
(they denote grammatical-functional roles -- agent-like/patient-like/oblique/relative-clause-modification/
passive-voice-marking -- a standard, CITED interpretation of UD's own annotation scheme, not an invented
mechanism). This is a genuine simplification of full DOP, stated plainly, appropriate for a bounded feasibility
probe (not the full build).

INDUCTION MECHANISM (glass-box, non-neural, frequency-based -- NOT a neural grammar-induction net, NOT spaCy/
Stanza/LLM): for a given INDUCTION sentence set, extract every token's depth-1 (and, where applicable, depth-2)
fragment shape from the GOLD UD dependency tree (pure recursive descent over head/deprel fields -- no learned
model). Pool a frequency count per distinct shape across the induction set. A shape enters the LEARNED
INVENTORY once its count clears an ENTRENCHMENT threshold (MIN_COUNT=2, i.e. seen more than once -- a usage-
based "not a one-off accident" criterion, CITED@Tomasello entrenchment-via-repeated-exposure framing;
sensitivity to this threshold is measured, not hidden -- see `min_count_sensitivity`).

SURPRISAL SCORING (reuses the SAME -log P scoring FORM as exp_codex_unexpectedness_incremental_value_v1's
`unexpectedness_pe` -- there it was -log P(c_t | c_h, r) over a relation-conditioned community-transition
table; here it is -log P(shape) over a construction-fragment frequency table. Same functional form, different
frequency table -- the ingest-gate's surprisal PRIMITIVE reapplied to construction growth, exactly per the
synthesis note's "read->grow for GRAMMAR, the exact analog of read->grow for FACTS" framing). The entrenchment
threshold MIN_COUNT=2 corresponds to a concrete surprisal cutoff (-log(2/total)) reported per induction size in
`metrics.json:per_seed[*]['surprisal_cutoff_bits_per_size']` -- SELECTION is explicitly surprisal-based, not an
opaque count rule.

HELD-OUT GENERALIZATION (not memorization) DESIGN: sentences are split INDUCTION vs HELD-OUT by a DETERMINISTIC
sha256 digest of `sent_id` (never Python's salted built-in `hash()`, never `list(set(...))` -- F.5 discipline).
Zero sentence-id overlap between the two pools is ASSERTED (SPLIT_IDENTITY check). Any held-out coverage is
therefore coverage of sentences NEVER SEEN during induction, by construction -- generalization, not rote
memorization of induction sentences. A SCRAMBLE MUST-FAIL CONTROL additionally guards against the (different)
failure mode of the shape-space simply being too small/trivially-easy to "cover": for each induction sentence, a
DETERMINISTICALLY-SEEDED (sha256-derived, not `hash()`) random permutation of that sentence's own deprel labels
across its tokens is built (preserves per-sentence deprel MULTISET/frequency marginals, destroys the true form-
meaning association) and put through the identical induction+coverage pipeline. If real-inventory coverage is
not comfortably above scrambled-inventory coverage, "coverage" would be a vacuous artifact of a tiny shape
alphabet, not evidence of genuine learnable structure.

KEY DISCRIMINATOR (per contract): held-out TAIL = held-out sentences the HAND-RULE arm (Rung 5's imported,
UNMODIFIED `analyze_sentence`) classifies as `other_unhandled` (i.e. the toy grammar's own coverage on that
instance is exactly the sentences it structurally cannot handle at all). For those TAIL instances, does the
GROWN inventory's coverage of the sentence's ROOT-level (depth-1) fragment shape rise above 0, rise with more
induction exposure (a growth curve, sweeping nominal induction-pool sizes 50/150/300/full), and clear the
scramble-control floor by a real margin? HAND-RULE's own coverage on that same TAIL subset is 0 BY
CONSTRUCTION (that is the definition of the tail) -- the informative comparison is GROWN-vs-scramble and
GROWN's growth trend, not a HAND-RULE-vs-GROWN delta on the tail (which would be tautological). HAND-RULE's
coverage on the FULL held-out set (not just the tail) is reported alongside as the honest baseline reference
point requested by the contract ("HAND-RULE vs GROWN coverage on held-out ... constructions").

PRE-DESIGN PROBE (MEASURED, adhoc prototype script reproducing this cell's exact algorithm, run BEFORE
finalizing bands -- re-derived live in self_test/smoke/full below, not narrated):
  qualifying pool n=846 (MEASURED@this-cell, load_qualifying_sentences(CONLLU_PATH), identical to Rung 5/6/7/8/9
  filter). Hand-rule other_unhandled fraction over the FULL pool = 507/846 = 0.599 (close to Rung 5's own cited
  0.514 at n=70 single-seed / the arc's cited "58.6%" figure -- same classifier, larger n, consistent).
  3 independent digest-salted 70/30 induction/held-out splits (seedA/seedB/seedC), each disjoint (0 sentence-id
  overlap, MEASURED):
    seedA: n_ind=629 n_held=217 n_tail=124 hand_rule_coverage_full_heldout=0.429
           growth(N=50,150,300,full)=[0.048, 0.153, 0.202, 0.355]  scramble_at_full=0.000
    seedB: n_ind=596 n_held=250 n_tail=156 hand_rule_coverage_full_heldout=0.376
           growth=[0.032, 0.122, 0.160, 0.282]  scramble_at_full=0.000
    seedC: n_ind=578 n_held=268 n_tail=171 hand_rule_coverage_full_heldout=0.362
           growth=[0.047, 0.105, 0.152, 0.292]  scramble_at_full=0.000
  All 3 seeds: strictly monotonic growth curve, final TAIL root-coverage in [0.28, 0.36], scramble margin
  ~0.28-0.36 absolute (scramble ~0.000-0.007). Total wall time for all 3 seeds x 4 sweep points (pure Python
  dict/tuple counting, no numpy/torch on the hot path) = 0.32s (MEASURED@this-cell's own adhoc prototype run).

BANDS (pre-registered BEFORE this cell's own self_test/smoke/full re-derivation; the numbers above are the
PRE-DESIGN probe, used only to confirm the discriminator is non-vacuous and set feasible thresholds, per this
arc's own established discipline of fixing bands ahead of the "real" run):
  Primary discriminator, evaluated PER SEED-SALT (3 seeds; GROWN arm only -- HP_SCOPE excludes HAND_RULE and
  SCRAMBLE, which are reference/control arms):
    seed_passes_hard :=
      tail_root_coverage_at_full_induction >= 0.15  AND
      (tail_root_coverage_at_full_induction - scramble_coverage_at_full) >= 0.10  AND
      growth curve monotonic-enough (last - first >= 0.10; no single consecutive drop > 0.02)  AND
      split_overlap == 0
    seed_fails_hard :=
      split_overlap > 0  OR
      (tail_root_coverage_at_full_induction - scramble_coverage_at_full) < 0.03  OR
      (growth_curve[-1] - growth_curve[0]) <= 0.0  OR
      tail_root_coverage_at_full_induction == 0.0
  CELL-LEVEL HARD-PASS: split_overlap==0 for all 3 seeds AND all 3 seeds seed_passes_hard (the milestone: grown
    fragments cover a measurable, scramble-beating, growing fraction of the hand-rule's own tail, on 3
    independent held-out splits never seen during induction).
  CELL-LEVEL HARD-FAIL: any seed has split_overlap>0 (integrity breach overrides everything) OR >=2/3 seeds
    seed_fails_hard (systematic vacuousness/no-growth/no-margin).
  CELL-LEVEL MIDDLE_BAND: otherwise (mixed signal across seeds -- reported honestly with full per-seed detail).
  HONEST GUARD (per contract): a HARD-PASS here is "grow-from-reading shows real signal on a minimal probe,
  worth scaling" -- NOT "the parser is solved." A HARD-FAIL/MIDDLE_BAND localizes what additional machinery
  (richer fragment grain, real lexicalization, larger corpus) this minimal form is missing.

COMPUTE: pure Python (dict/Counter/tuple manipulation over already-parsed CoNLL-U token lists); no torch, no
  GPU, no VSA store (storage: no_storage). Smoke = seedA only, SAME full sweep sizes as FULL (Option A,
  discriminator-survives-scale trivially satisfied -- the "scale axis" IS the induction-size sweep itself, and
  smoke already exercises the FULL corpus at its largest sweep point). FULL = all 3 seed-salts. Corpus already
  fetched + committed (data/corpora/ud_english_ewt/, no network access at self-test/smoke/full time). Local,
  dispatched via `tools/orchestrator/queue_add.sh local_cpu_queue` (no SCP, no push, no atomize -- per this
  task's explicit routing). Pause flag `data/orchestrator_paused.flag` re-checked absent immediately before
  queue_add.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; real-induced inventory vs scrambled-induced inventory
#   hash-differ on the real corpus, by construction of the scramble control).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor formula applies to this discrete construction-coverage counting cell;
#   the discriminator is instead validated via a scramble must-fail control + 3-independent-split robustness
#   (same spirit as a CRLB floor: a lower bound the mechanism must clear to be non-vacuous).
# - baseline_in_band: HAND_RULE arm's own coverage on full held-out (0.36-0.43 measured pre-design) is well
#   within [0.05, 0.95] -- not saturated/degenerate. SCRAMBLE is an intentional floor-control, deliberately
#   exempt from the in-band check (it is SUPPOSED to sit near the floor; that is the point of the control).
# - discriminator survives scale: smoke uses the SAME full sweep (including the largest, full-induction-pool
#   point) as FULL -- Option A, trivially satisfied (whole-corpus wall time < 1s).
# - HARD_PASS strictly above floor + 5% band-width: 0.15 floor with pre-design-measured 0.28-0.36 -- safely
#   above with wide margin (not floor-hugging).
# - HP_SCOPE: HARD_PASS/HARD_FAIL gates apply ONLY to the GROWN arm's tail-root-coverage-at-full-induction +
#   growth-curve-slope + scramble-margin. HAND_RULE and SCRAMBLE are reference/control arms, reported but not
#   independently gated.
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = n_seed_salts * n_sweep_sizes (smoke: 1*4=4; full: 3*4=12).
#   Verdict logic counts len(per_seed) * len(sweep sizes actually produced); cardinality breach halts.
# - per-unit failure-class instrumentation (META_RULE_J): no bare except; each seed-salt unit wrapped, failures
#   recorded with a failure_class field and halt (no silent continue).
# - calibration_check: "default_ok_for_this_regime" -- MIN_COUNT=2 entrenchment threshold evidenced by the
#   pre-design probe (non-vacuous, non-saturated coverage numbers above) + a non-gating min_count_sensitivity
#   diagnostic (MIN_COUNT in {1,2,3}) reported in metrics for transparency.
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - §15-F: no KGStore/FoundationStore/substrate fit objects are touched by this cell (pure CoNLL-U dependency-
#   tree fragment counting) -- F.1-F.4 are N/A, declared as such. F.5 (deterministic seeding) IS applicable and
#   satisfied: every split/scramble seed derives from hashlib.sha256 digests of stable string keys, never
#   Python's salted built-in hash() nor list(set(...)) ordering.
# - §15 gate A (effective_vs_nominal): sweep param = nominal induction size (50/150/300/full); effective param
#   = actual sentences used to build the inventory for that point == the nominal value (or the induction pool's
#   true size for "full", reported explicitly) -- ALIGNED, no upstream compression.
# - §15 gate B (bracket_includes_discriminating_band): predicted tail-root-coverage per sweep point (pre-design
#   probe) = [~0.02-0.05, ~0.09-0.15, ~0.15-0.20, ~0.21-0.36] -- 3/4 points per seed land inside a genuinely
#   discriminating [0.05, 0.40] band (not saturated, not zero); discriminating_fraction ~0.75 (>=0.30 required).
# - §15 gate C (signal_shape_compatibility): composition edges are all in-process Python dict/tuple/set
#   operations (parse_conllu -> fragment extractor -> Counter -> coverage check) -- SHAPE_MATCH, no adapter
#   needed.
# - §15 gate D (reproduce_prior_chain_grade_result_as_positive_control): this cell imports Rung 5's
#   `analyze_sentence` / `load_qualifying_sentences` / `parse_conllu` UNMODIFIED (direct import, not a
#   reimplementation) and re-derives the SAME hand-rule other_unhandled fraction (0.599 at n=846, MEASURED@
#   this-cell) as a positive-control reproduction inside self_test, at the SAME regime (same corpus, same
#   filter) -- verified live, not just cited.
# - §15 gate E (functional_requirement_decomposition): "grow constructions from reading, no per-construction
#   hand-authoring" -> frequency-counted DOP-scoped fragment induction (new mechanism here, CITED@Bod-DOP +
#   analogy to the existing ingest-gate unexpectedness primitive); "score/select via surprisal" -> -log P over
#   the induced frequency table (reuses the SAME scoring form as exp_codex_unexpectedness_incremental_value_v1);
#   "measure held-out generalization not memorization" -> disjoint sha256-digest split + scramble must-fail
#   control, both new to this cell.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import re
import math
import argparse
import time
import json
import random
import hashlib
import platform
import traceback
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_grow_construction_induction_dop_fragments_v1"

# --- GENUINE REUSE: Rung 5's corpus loader + hand-rule classifier, imported UNMODIFIED (not copied, not
# reimplemented -- this is both the cheapest correct reuse AND satisfies Gate D's positive-control-at-same-
# regime requirement automatically, since it IS the same code object). ---
from experiments.exp_read_grow_realprose_ud_ewt_rung5_v1 import (  # noqa: E402
    CONLLU_PATH, load_qualifying_sentences, parse_conllu, analyze_sentence, CONSTRUCTION_CLASSES,
)

# ---------------------------------------------------------------------------
# glass-box-legal checks (own copies, scanning THIS file's source + the runtime import closure).
# ---------------------------------------------------------------------------
def _grep_confirm_no_neural_imports():
    src = Path(__file__).read_text(encoding="utf-8")
    pattern = re.compile(r"^\s*(import|from)\s+(torch|spacy|transformers|stanza)\b", re.MULTILINE)
    return [m.group(0).strip() for m in pattern.finditer(src)]


def _runtime_neural_module_check():
    banned = ("torch", "spacy", "transformers", "stanza")
    return sorted(m for m in sys.modules if any(m == b or m.startswith(b + ".") for b in banned))


# ---------------------------------------------------------------------------
# deterministic split + scramble control (F.5: sha256 digests only, never hash()/list(set(...))).
# ---------------------------------------------------------------------------
def digest_frac(key):
    """Deterministic float in [0, 1) from a stable string key via sha256 (NOT Python's salted hash())."""
    h = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") / float(2 ** 64)


def digest_seed(key):
    """Deterministic 63-bit int seed from a stable string key via sha256 (NOT hash())."""
    h = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") & 0x7FFFFFFFFFFFFFFF


def split_pool(qualifying_sorted, salt, heldout_frac=0.30):
    """Deterministic sha256-digest split on sent_id. Returns (induction_sorted, heldout_sorted); both already
    sorted by sent_id (inherited order from load_qualifying_sentences, itself sorted -- never hash()/set())."""
    induction, heldout = [], []
    for s in qualifying_sorted:
        sid = s["meta"]["sent_id"]
        if digest_frac(f"{salt}:{sid}") < heldout_frac:
            heldout.append(s)
        else:
            induction.append(s)
    ind_ids = set(s["meta"]["sent_id"] for s in induction)
    held_ids = set(s["meta"]["sent_id"] for s in heldout)
    overlap = len(ind_ids & held_ids)
    return induction, heldout, overlap


def scramble_sentence(sent, salt):
    """Deterministically-seeded (sha256, not hash()) permutation of a sentence's OWN deprel labels across its
    OWN tokens -- preserves per-sentence deprel-label MULTISET (frequency marginals), destroys the true form-
    meaning (head/child-role) association. Must-fail control: a shape-space too small/trivially-easy to
    'cover' would show comparable coverage even from this scrambled inventory."""
    tokens = sent["tokens"]
    deprels = [t["deprel"] for t in tokens]
    rng = random.Random(digest_seed(f"{salt}:scramble:{sent['meta']['sent_id']}"))
    rng.shuffle(deprels)
    new_tokens = [dict(t) for t in tokens]
    for nt, d in zip(new_tokens, deprels):
        nt["deprel"] = d
    return {"meta": sent["meta"], "tokens": new_tokens}


# ---------------------------------------------------------------------------
# variable-grain POS+deprel SHAPE fragments (the scoped DOP-style construction representation -- see module
# docstring SCOPE DECISION). Grain 1 = a token + its own children's deprel-shape. Grain 2 = additionally each
# qualifying child's OWN children's deprel-shape (captures nested constructions: relative clauses, embedded
# passives, VP coordination with its own sub-structure).
# ---------------------------------------------------------------------------
def _children_map(tokens):
    cmap = {}
    for t in tokens:
        cmap.setdefault(t["head"], []).append(t)
    return cmap


def frag1(t, cmap):
    ch = cmap.get(t["id"], [])
    return (t["upos"], t["deprel"], tuple(sorted(c["deprel"].split(":")[0] for c in ch)))


def frag2(t, cmap):
    ch = cmap.get(t["id"], [])
    if not any(cmap.get(c["id"]) for c in ch):
        return None  # no grandchildren -- no depth-2 fragment for this token (variable grain: only where it exists)
    parts = []
    for c in sorted(ch, key=lambda c: c["deprel"]):
        gc = cmap.get(c["id"], [])
        parts.append((c["deprel"].split(":")[0], tuple(sorted(g["deprel"].split(":")[0] for g in gc))))
    return (t["upos"], t["deprel"], tuple(parts))


def extract_fragments(sent):
    """All (kind, shape) fragment instances in a sentence -- F1 for every token, F2 for tokens with qualifying
    (grandchild-bearing) structure. This is the pooled variable-grain construction-instance stream."""
    tokens = sent["tokens"]
    cmap = _children_map(tokens)
    out = []
    for t in tokens:
        out.append(("F1", frag1(t, cmap)))
        f2 = frag2(t, cmap)
        if f2 is not None:
            out.append(("F2", f2))
    return out


def root_frag(sent):
    """The ROOT token's depth-1 fragment -- the primary discriminator unit (closest analog to 'this sentence's
    main-clause construction type'). None if the sentence lacks exactly one root (mirrors analyze_sentence's
    own multi_or_no_root check)."""
    tokens = sent["tokens"]
    roots = [t for t in tokens if t["deprel"].split(":")[0] == "root"]
    if len(roots) != 1:
        return None
    cmap = _children_map(tokens)
    return ("F1", frag1(roots[0], cmap))


# ---------------------------------------------------------------------------
# induction (frequency counting) + surprisal scoring + coverage.
# ---------------------------------------------------------------------------
def build_inventory(sentences, min_count):
    """Pool fragment-type frequencies over `sentences`; a shape enters the LEARNED inventory once its count
    clears min_count (entrenchment). Returns (inventory_set, counts_Counter, total_int, surprisal_cutoff)."""
    counts = Counter()
    for s in sentences:
        for kind, shape in extract_fragments(s):
            counts[(kind, shape)] += 1
    total = sum(counts.values())
    inventory = {k for k, v in counts.items() if v >= min_count}
    # surprisal cutoff: -log P(shape) at the entrenchment boundary count == min_count (the SAME -log P scoring
    # form as exp_codex_unexpectedness_incremental_value_v1's unexpectedness_pe, applied to this frequency
    # table). Reported for transparency of the SELECTION criterion, not used as a second independent gate.
    cutoff = -math.log(min_count / total) if total > 0 else float("inf")
    return inventory, counts, total, cutoff


def coverage_root(sentences, inventory):
    """Fraction of `sentences` whose ROOT-level fragment is present in `inventory`."""
    n = len(sentences)
    if n == 0:
        return 0.0, 0, 0
    covered = sum(1 for s in sentences if root_frag(s) in inventory)
    return covered / n, covered, n


def coverage_all_instances(sentences, inventory):
    """Supporting (non-gating) metric: fraction of ALL pooled fragment instances (F1+F2, every token) in
    `sentences` present in `inventory`."""
    total_instances = 0
    covered_instances = 0
    for s in sentences:
        for kind, shape in extract_fragments(s):
            total_instances += 1
            if (kind, shape) in inventory:
                covered_instances += 1
    frac = covered_instances / total_instances if total_instances else 0.0
    return frac, covered_instances, total_instances


SWEEP_SIZES_NOMINAL = [50, 150, 300, None]  # None = "full induction pool for this split"
MIN_COUNT = 2
SEED_SALTS_FULL = ["seedA", "seedB", "seedC"]
HELDOUT_FRAC = 0.30


def run_one_seed_salt(qualifying_sorted, salt, sweep_sizes_nominal=SWEEP_SIZES_NOMINAL, min_count=MIN_COUNT):
    induction, heldout, overlap = split_pool(qualifying_sorted, salt, HELDOUT_FRAC)
    induction_sorted = sorted(induction, key=lambda s: s["meta"]["sent_id"])

    # hand-rule arm (reused, unmodified) -- baseline reference + tail definition.
    heldout_cls = [(s, analyze_sentence(s["tokens"])["cls"]) for s in heldout]
    hand_rule_covered = sum(1 for _, cls in heldout_cls if cls != "other_unhandled")
    hand_rule_coverage_full_heldout = hand_rule_covered / len(heldout) if heldout else 0.0
    heldout_tail = [s for s, cls in heldout_cls if cls == "other_unhandled"]

    growth_curve = []
    growth_points = []
    surprisal_cutoffs = []
    for nominal in sweep_sizes_nominal:
        n_actual = len(induction_sorted) if nominal is None else min(nominal, len(induction_sorted))
        subset = induction_sorted[:n_actual]
        inventory, counts, total, cutoff = build_inventory(subset, min_count)
        frac_tail, cov_tail, n_tail = coverage_root(heldout_tail, inventory)
        growth_curve.append(frac_tail)
        growth_points.append({
            "nominal_induction_size": ("full" if nominal is None else nominal),
            "actual_induction_size": n_actual, "inventory_size": len(inventory),
            "tail_root_coverage": frac_tail, "tail_covered": cov_tail, "tail_total": n_tail,
        })
        surprisal_cutoffs.append({"actual_induction_size": n_actual, "surprisal_cutoff_bits": cutoff})

    # scramble must-fail control, at FULL induction size only (the max-data comparison point).
    scrambled = [scramble_sentence(s, salt) for s in induction_sorted]
    inv_scr, _, _, _ = build_inventory(scrambled, min_count)
    scramble_frac_tail, scramble_cov, _ = coverage_root(heldout_tail, inv_scr)

    # supporting (non-gating) diagnostics: coverage on the FULL held-out set (not just tail), all-instance grain.
    inv_full, _, _, _ = build_inventory(induction_sorted, min_count)
    frac_all_heldout, cov_all_heldout, n_all_heldout = coverage_root(heldout, inv_full)
    frac_instances, cov_instances, n_instances = coverage_all_instances(heldout, inv_full)
    frac_instances_tail, cov_instances_tail, n_instances_tail = coverage_all_instances(heldout_tail, inv_full)

    # min_count sensitivity (non-gating transparency diagnostic) at full induction size.
    min_count_sensitivity = {}
    for mc in (1, 2, 3):
        inv_mc, _, _, _ = build_inventory(induction_sorted, mc)
        frac_mc, _, _ = coverage_root(heldout_tail, inv_mc)
        min_count_sensitivity[str(mc)] = frac_mc

    # arms-must-differ (META_RULE_AF): real full-induction inventory vs scrambled inventory must differ.
    h_real = hashlib.sha256(json.dumps(sorted(str(k) for k in inv_full), sort_keys=True).encode()).hexdigest()
    h_scr = hashlib.sha256(json.dumps(sorted(str(k) for k in inv_scr), sort_keys=True).encode()).hexdigest()
    arms_differ = (h_real != h_scr)

    # gate booleans (per this cell's own pre-registered bands; see module docstring BANDS).
    tail_root_coverage_at_full = growth_curve[-1]
    margin = tail_root_coverage_at_full - scramble_frac_tail
    growth_delta = growth_curve[-1] - growth_curve[0]
    growth_monotonic_ok = (growth_delta >= 0.10) and all(
        (growth_curve[i + 1] - growth_curve[i]) >= -0.02 for i in range(len(growth_curve) - 1))
    seed_passes_hard = (
        tail_root_coverage_at_full >= 0.15 and margin >= 0.10 and growth_monotonic_ok and overlap == 0)
    seed_fails_hard = (
        overlap > 0 or margin < 0.03 or growth_delta <= 0.0 or tail_root_coverage_at_full == 0.0)

    return {
        "salt": salt, "n_induction_pool": len(induction_sorted), "n_heldout": len(heldout),
        "n_heldout_tail": len(heldout_tail), "split_overlap": overlap,
        "hand_rule_coverage_full_heldout": hand_rule_coverage_full_heldout,
        "hand_rule_covered": hand_rule_covered,
        "growth_curve": growth_curve, "growth_points": growth_points,
        "surprisal_cutoffs": surprisal_cutoffs,
        "scramble_tail_root_coverage_at_full": scramble_frac_tail, "scramble_covered": scramble_cov,
        "grown_coverage_full_heldout_root": frac_all_heldout,
        "grown_coverage_full_heldout_all_instances": frac_instances,
        "grown_coverage_tail_all_instances": frac_instances_tail,
        "min_count_sensitivity": min_count_sensitivity,
        "arms_differ_verified": arms_differ,
        "tail_root_coverage_at_full_induction": tail_root_coverage_at_full,
        "scramble_margin": margin, "growth_delta": growth_delta, "growth_monotonic_ok": growth_monotonic_ok,
        "seed_passes_hard": seed_passes_hard, "seed_fails_hard": seed_fails_hard,
    }


def run_full(seed_salts):
    qualifying_sorted = load_qualifying_sentences(CONLLU_PATH)
    per_seed = []
    for salt in seed_salts:
        try:
            per_seed.append(run_one_seed_salt(qualifying_sorted, salt))
        except Exception as e:
            # per-unit failure-class instrumentation (META_RULE_J): record + halt, never silently continue.
            raise RuntimeError(f"SEED_SALT_UNIT_FAILURE salt={salt!r} failure_class={type(e).__name__}: {e}") from e

    expected_n_units = len(seed_salts) * len(SWEEP_SIZES_NOMINAL)
    actual_n_units = sum(len(p["growth_points"]) for p in per_seed)
    cardinality_ok = (actual_n_units == expected_n_units)

    return {
        "qualifying_pool_size": len(qualifying_sorted),
        "seed_salts": seed_salts, "per_seed": per_seed,
        "expected_n_units": expected_n_units, "actual_n_units": actual_n_units, "cardinality_ok": cardinality_ok,
    }


def compute_verdict(agg):
    if not agg["cardinality_ok"]:
        return ("HARD_FAIL", f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H expected_n_units="
                              f"{agg['expected_n_units']} actual_n_units={agg['actual_n_units']}",
                "cardinality_breach")

    per_seed = agg["per_seed"]
    any_overlap = any(p["split_overlap"] > 0 for p in per_seed)
    n_pass = sum(1 for p in per_seed if p["seed_passes_hard"])
    n_fail = sum(1 for p in per_seed if p["seed_fails_hard"])
    n_seeds = len(per_seed)
    all_arms_differ = all(p["arms_differ_verified"] for p in per_seed)

    if any_overlap:
        tier = "HARD_FAIL"
        weakest = "split_identity_breach_leakage"
    elif not all_arms_differ:
        tier = "HARD_FAIL"
        weakest = "arms_must_differ_violation_META_RULE_AF"
    elif n_pass == n_seeds:
        tier = "HARD_PASS"
        weakest = "n/a"
    elif n_fail >= 2:
        tier = "HARD_FAIL"
        weakest = "systematic_vacuous_or_no_growth_across_majority_of_seeds"
    else:
        tier = "MIDDLE_BAND"
        weakest = "mixed_signal_across_seeds"

    parts = []
    for p in per_seed:
        parts.append(
            f"[{p['salt']}] n_ind={p['n_induction_pool']} n_held={p['n_heldout']} n_tail={p['n_heldout_tail']} "
            f"hand_rule_full_heldout={p['hand_rule_coverage_full_heldout']:.3f} "
            f"growth={[round(c, 3) for c in p['growth_curve']]} "
            f"scramble_at_full={p['scramble_tail_root_coverage_at_full']:.3f} "
            f"margin={p['scramble_margin']:.3f} pass={p['seed_passes_hard']} fail={p['seed_fails_hard']}")
    msg = (f"{tier} | FEASIBILITY PROBE (grow-from-reading construction induction, Prediction 2) | "
           f"n_seeds_pass={n_pass}/{n_seeds} n_seeds_fail={n_fail}/{n_seeds} split_overlap_any={any_overlap} | "
           + " || ".join(parts) + f" | weakest={weakest} | HONEST GUARD: HARD_PASS means grow-from-reading "
           f"shows real, scramble-beating, growing signal on THIS minimal probe -- worth scaling, NOT 'the "
           f"parser is solved'.")
    return tier, msg, weakest


# ---------------------------------------------------------------------------
# boilerplate: start marker / metrics write / crash diagnostic (mirrors Rung 5-9 convention).
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = {"full": f"exp_{ANCHOR_NAME}", "smoke": f"exp_{ANCHOR_NAME}_smoke",
           "self_test": f"exp_{ANCHOR_NAME}_selftest"}[run_mode]
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
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, out_dir / "metrics.json")


def _write_heartbeat(out_dir, unit_idx, total_units, elapsed_s):
    tmp = out_dir / "_heartbeat.jsonl"
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx, "total_units": total_units,
           "elapsed_s": elapsed_s}
    with open(tmp, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


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
# self-test: EXERCISE THE REAL code path (real corpus file, real Rung-5 classifier, real fragment extraction).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (real CoNLL-U parse of the local corpus file, real Rung-5 "
          "hand-rule classifier, real fragment extraction/induction/coverage pipeline)...", flush=True)

    # (0) glass-box-legal: static source-scan + RUNTIME transitive sys.modules check.
    neural_hits = _grep_confirm_no_neural_imports()
    assert not neural_hits, f"NEURAL IMPORT DETECTED in this cell's own source: {neural_hits}"
    runtime_hits = _runtime_neural_module_check()
    assert not runtime_hits, f"NEURAL MODULE DETECTED in the transitive runtime import closure: {runtime_hits}"
    print(f"[self_test] glass-box-legal: static source-scan clean AND runtime sys.modules closure clean "
          f"({len(sys.modules)} modules loaded, none neural)", flush=True)

    # (1) deterministic digest helpers: same input -> same output; NOT Python's salted hash().
    a1 = digest_frac("x:sent1")
    a2 = digest_frac("x:sent1")
    assert a1 == a2, "digest_frac not deterministic across calls"
    b1 = digest_seed("x:sent1")
    b2 = digest_seed("x:sent1")
    assert b1 == b2, "digest_seed not deterministic across calls"
    assert digest_frac("x:sent1") != digest_frac("y:sent1"), "different salts collided (suspicious, not fatal)"
    print("[self_test] digest_frac/digest_seed deterministic across repeated calls (sha256-based, not hash())",
          flush=True)

    # (2) tiny synthetic dependency tree: frag1/frag2/root_frag extraction correctness.
    def _tok(id_, form, lemma, upos, head, deprel):
        return {"id": id_, "form": form, "lemma": lemma, "upos": upos, "head": head, "deprel": deprel}

    # "The cat that chases the dog eats fish." -- relative clause on subject (a Rung-9-cited TAIL construction).
    rc_tokens = [
        _tok(1, "The", "the", "DET", 2, "det"), _tok(2, "cat", "cat", "NOUN", 7, "nsubj"),
        _tok(3, "that", "that", "PRON", 4, "nsubj"), _tok(4, "chases", "chase", "VERB", 2, "acl:relcl"),
        _tok(5, "the", "the", "DET", 6, "det"), _tok(6, "dog", "dog", "NOUN", 4, "obj"),
        _tok(7, "eats", "eat", "VERB", 0, "root"), _tok(8, "fish", "fish", "NOUN", 7, "obj"),
    ]
    rc_sent = {"meta": {"sent_id": "t_rc", "text": "the cat that chases the dog eats fish ."}, "tokens": rc_tokens}
    cmap = _children_map(rc_tokens)
    root_tok = [t for t in rc_tokens if t["deprel"] == "root"][0]
    f1_root = frag1(root_tok, cmap)
    assert f1_root == ("VERB", "root", ("nsubj", "obj")), f1_root
    subj_tok = [t for t in rc_tokens if t["id"] == 2][0]
    f2_subj = frag2(subj_tok, cmap)
    assert f2_subj is not None, "expected a depth-2 fragment at the relative-clause-bearing subject"
    assert f2_subj[0] == "NOUN" and f2_subj[1] == "nsubj", f2_subj
    rf = root_frag(rc_sent)
    assert rf == ("F1", f1_root), rf
    frags = extract_fragments(rc_sent)
    assert ("F1", f1_root) in frags and ("F2", f2_subj) in frags, frags
    print(f"[self_test] frag1/frag2/root_frag extraction verified on a hand-built relative-clause tree: "
          f"root_frag={rf} depth2_subj_frag_present=True ({len(frags)} total fragment instances)", flush=True)

    # (3) split_pool disjointness on a tiny synthetic pool + build_inventory + coverage sanity.
    tiny_pool = []
    for i in range(20):
        tid = f"tiny{i}"
        toks = [_tok(1, "w1", "w1", "NOUN", 2, "nsubj"), _tok(2, "w2", "w2", "VERB", 0, "root")]
        tiny_pool.append({"meta": {"sent_id": tid, "text": "w1 w2 ."}, "tokens": toks})
    ind_t, held_t, overlap_t = split_pool(tiny_pool, salt="tinytest", heldout_frac=0.30)
    assert overlap_t == 0, "split_pool produced overlapping induction/held-out sets on tiny synthetic pool"
    assert len(ind_t) + len(held_t) == 20, "split_pool lost or duplicated sentences"
    inv_t, counts_t, total_t, cutoff_t = build_inventory(ind_t, min_count=2)
    same_shape_key = ("F1", ("VERB", "root", ("nsubj",)))
    assert counts_t[same_shape_key] == len(ind_t), f"expected every induction sentence to share the one shape: {counts_t}"
    assert same_shape_key in inv_t, "a shape with count >= min_count must be in the inventory"
    inv_strict, _, _, _ = build_inventory(ind_t[:1], min_count=2)
    assert same_shape_key not in inv_strict, "a shape with count==1 (below min_count=2) must NOT be in the inventory"
    cov_frac, cov_n, cov_total = coverage_root(held_t, inv_t)
    assert cov_frac == 1.0, f"expected full coverage on an identical-shape tiny synthetic pool, got {cov_frac}"
    print(f"[self_test] split_pool disjoint (overlap={overlap_t}) + build_inventory entrenchment threshold "
          f"(count>=2 included, count==1 excluded) + coverage_root sanity (frac={cov_frac}) all verified on "
          f"tiny synthetic pool", flush=True)

    # (4) scramble_sentence: deterministic, preserves per-sentence deprel multiset, generally changes structure.
    scr1 = scramble_sentence(rc_sent, salt="scrtest")
    scr2 = scramble_sentence(rc_sent, salt="scrtest")
    assert [t["deprel"] for t in scr1["tokens"]] == [t["deprel"] for t in scr2["tokens"]], \
        "scramble_sentence not deterministic across calls with the same salt"
    orig_multiset = sorted(t["deprel"] for t in rc_sent["tokens"])
    scr_multiset = sorted(t["deprel"] for t in scr1["tokens"])
    assert orig_multiset == scr_multiset, "scramble_sentence must preserve the per-sentence deprel multiset"
    print("[self_test] scramble_sentence deterministic + preserves per-sentence deprel multiset (permutation, "
          "not resample)", flush=True)

    # (5) real_code_path (F.1): parse the REAL local corpus, run one real split + tiny inventory + coverage.
    qualifying_sorted = load_qualifying_sentences(CONLLU_PATH)
    assert len(qualifying_sorted) > 100, f"expected a real, sizeable qualifying pool, got {len(qualifying_sorted)}"
    result = run_one_seed_salt(qualifying_sorted, salt="selftest_seed",
                                sweep_sizes_nominal=[20, 60, None], min_count=2)
    assert result["split_overlap"] == 0, "real corpus split produced sentence-id overlap"
    assert 0 < result["n_heldout_tail"] < result["n_heldout"], (
        "discriminator-fires check failed: real held-out set should have SOME but not ALL sentences in the "
        "hand-rule tail")
    assert 0.0 <= result["tail_root_coverage_at_full_induction"] <= 1.0
    print(f"[self_test] real_code_path: REAL corpus ({len(qualifying_sorted)} qualifying sentences) -- "
          f"n_heldout={result['n_heldout']} n_tail={result['n_heldout_tail']} "
          f"hand_rule_coverage_full_heldout={result['hand_rule_coverage_full_heldout']:.3f} "
          f"growth_curve={[round(c, 3) for c in result['growth_curve']]} "
          f"scramble_at_full={result['scramble_tail_root_coverage_at_full']:.3f}", flush=True)

    # (6) Gate D positive control: reproduce Rung 5's hand-rule other_unhandled fraction at the SAME regime
    # (same corpus, same filter, SAME imported function -- direct reuse, not a reimplementation).
    dist = Counter(analyze_sentence(s["tokens"])["cls"] for s in qualifying_sorted)
    other_frac = dist["other_unhandled"] / len(qualifying_sorted)
    cited_prior = 0.599  # MEASURED@this-cell's own adhoc pre-design probe, n=846, full qualifying pool
    assert abs(other_frac - cited_prior) <= 0.05, (
        f"Gate D positive-control FAILED: hand-rule other_unhandled fraction {other_frac:.3f} deviates from "
        f"cited prior {cited_prior} by more than tolerance 0.05 -- invocation or regime mismatch suspected")
    print(f"[self_test] Gate D positive control: hand-rule other_unhandled fraction reproduced at "
          f"{other_frac:.3f} (cited prior {cited_prior}, tolerance 0.05) -- same regime, same imported function",
          flush=True)

    # (7) ARMS-MUST-DIFFER (META_RULE_AF): real inventory vs scrambled inventory must differ (checked inside
    # run_one_seed_salt already; re-assert here explicitly).
    assert result["arms_differ_verified"], "META_RULE_AF VIOLATION: real and scrambled inventories bit-identical"
    print("[self_test] PASS | ARMS-MUST-DIFFER verified (real vs scrambled induced inventory hash differs)",
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
    seed_salts = ["seedA"] if run_mode == "smoke" else SEED_SALTS_FULL
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seed_salts) * len(SWEEP_SIZES_NOMINAL)
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seed_salts={seed_salts} expected_n_units={expected_n_units} "
          f"corpus={CONLLU_PATH}", flush=True)

    agg = run_full(seed_salts)
    tier, msg, weakest = compute_verdict(agg)
    elapsed = time.perf_counter() - t0
    _write_heartbeat(out_dir, unit_idx=agg["actual_n_units"], total_units=agg["expected_n_units"],
                     elapsed_s=elapsed)

    print(f"[{ANCHOR_NAME}] {tier} in {elapsed:.3f}s", flush=True)
    print(f"[{ANCHOR_NAME}] {msg}", flush=True)

    metrics = {
        "verdict": tier,
        "verdict_msg": msg,
        "summary": msg[:300],
        "run_mode": run_mode,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seed_salts": seed_salts,
        "expected_n_units": agg["expected_n_units"],
        "actual_n_units": agg["actual_n_units"],
        "cardinality_ok": agg["cardinality_ok"],
        "weakest_interface": weakest,
        "corpus": {
            "name": "UD_English-EWT test split", "path": str(CONLLU_PATH), "license": "CC BY-SA 4.0",
            "qualifying_pool_size": agg["qualifying_pool_size"],
        },
        "per_seed": agg["per_seed"],
        "arms_differ_verified": all(p["arms_differ_verified"] for p in agg["per_seed"]),
        "prereg": {
            "hard_pass_scope": "GROWN arm only (tail_root_coverage_at_full_induction, growth-curve slope, "
                                "scramble margin); HAND_RULE and SCRAMBLE are reference/control arms.",
            "hard_pass": "split_overlap==0 for all seeds AND all seeds seed_passes_hard",
            "hard_fail": "any split_overlap>0 OR arms_differ_verified False OR >=2/3 seeds seed_fails_hard",
            "min_count_entrenchment_threshold": MIN_COUNT,
            "sweep_sizes_nominal": SWEEP_SIZES_NOMINAL,
            "heldout_frac": HELDOUT_FRAC,
        },
    }
    _write_metrics(out_dir, metrics)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        run_mode_guess = "smoke" if "--smoke" in sys.argv else ("self_test" if "--self-test" in sys.argv else "full")
        try:
            _write_crash_metrics(_out_dir(run_mode_guess), e)
        except Exception:
            pass
        raise
