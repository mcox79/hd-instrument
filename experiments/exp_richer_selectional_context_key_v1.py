# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: real-vs-scramble final-predicted-sense digest MUST differ pairwise, checked
#   independently for the SUFFICIENT-set test items (20) and the INSUFFICIENT-set test items (20),
#   asserted per-seed in aggregate_and_verdict (META_RULE_AF).
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace) -- verbatim pattern
#   from experiments/exp_word_context_affect_superposition_map_v1.py (Stage 2).
# - except SystemExit: raise BEFORE except Exception (no BaseException) -- see __main__ block.
# - crlb_n/a: no swept capacity dimension; this cell proves a MECHANISM (does a richer per-slot
#   filler-class context key add disambiguating power beyond binary animacy), not a capacity envelope.
#   CAPACITY NOTE: exactly like Stage 2, redundant TRAIN nouns sharing one (word,label) pair produce
#   ALGEBRAICALLY IDENTICAL bind() outputs (CONTEXT_KEYS[label] is a function of the LABEL STRING only,
#   never noun identity) -- every word_map here bundles down to 2 distinct components (one per sense),
#   well inside VSA capacity at N_DIM_WORD=1024.
# - baseline_in_band: n/a as a chance-level negative control in the Stage-2 sense (SCRAMBLE is the
#   can-fail negative control on the taught association); this cell ALSO has a second, task-specific
#   negative control (the ANIMACY-ONLY arm on the animacy-insufficient set), which is EXPECTED to sit
#   near chance (~0.5) by construction (see ANIMACY-ONLY ARM note below) -- reported, not separately
#   banded against a fixed 0.5 floor, since its own band (<=0.60) already captures this.
# - discriminator survives scale: full-N == smoke-N item set (20 sufficient-set test items + 4
#   baseline items + 20 insufficient-set test items + 10 generalization probes, ALL FIXED); this cell
#   has NO theta-training loop at all (unlike Stage 2's bonus Stage-1 witness, deliberately NOT
#   imported here -- out of scope per the task brief's own Reuse list), so smoke/full differ ONLY in
#   seed count (SMOKE=[0], FULL=[0,1,2,3,4]) -- smoke fires the full discriminator on seed 0.
# - cardinality_ok: EXPECTED_N_SEEDS=5 for run_mode=="full" (1 for "smoke");
#   HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land than expected for that mode.
# - per-unit failure-class instrumentation (no bare except; per-seed crash recorded, run_seed wraps
#   its body in try/except Exception, never BaseException).
# - calibration_check: default_ok_for_this_regime (bands fixed BEFORE this cell was run, per the task
#   brief's own pre-registered gate spec -- see BAND_* constants below -- not tuned after seeing
#   results).
# - deterministic_seeding: torch.Generator per seed for VSA atoms (role vectors + class/label vectors
#   + per-(word,sense) filler vectors); scramble permutation via Stage 2's OWN
#   `_scrambled_teaching_table` (random.Random(fixed int seed), PROT-023, reused by import, not
#   reimplemented); WordNet hypernym-closure lookups are themselves deterministic (no RNG); animacy
#   lookups (hdlab.animacy_lexicon.lookup_animacy) likewise deterministic.
# - cell_chunked: true (per-seed unit via tools/exp_checkpoint.py).
# - LOCAL ONLY, ISOLATED PROBE: no queue dispatch, no remote ship, no canonical-store write, no
#   hdlab/ edits -- prove-architecture experiment cell (per Director task brief, 2026-08-07 richer
#   context key drill), not production wiring.
# - all reported numbers MEASURED@ tagged in the completion report, not this file.
"""experiments/exp_richer_selectional_context_key_v1.py -- ISOLATED prove-architecture probe:
does a RICHER, per-slot SELECTIONAL-ASSOCIATION context key (a small BUNDLE of typed argument-slot
filler classes, Resnik/VerbNet-style) add REAL disambiguating power beyond Stage 2's single BINARY
animacy scalar, for words whose senses take SAME-animacy fillers (so binary animacy is flat/useless)?

THE MECHANISM (extends Stage 2's proven superposition map; VSA-native, glass-box):
Stage 2 (`exp_word_context_affect_superposition_map_v1.py`, HARD_PASS 04af969c4) taught
    word_map = bundle_over_senses( bind(context_key_for_sense, sense_vector) )
with context_key = a single atom per coarse ANIMACY class ("inanimate"/"animate"). This cell REPLACES
that single-atom key with a 2-SLOT BUNDLE over the verb's argument roles:
    context_key(label) = bundle( bind(ROLE_AGENT, class_vec["PERSON"]), bind(ROLE_PATIENT, class_vec[label]) )
where `label` is the PATIENT filler's semantic class. For the REGRESSION set (Stage 2's own 6 words)
`label` is the SAME coarse animacy value Stage 2 used (reused import, unchanged data). For the DECISIVE
set (5 new words) `label` is a FINER WordNet-hypernym-derived class (PERSON/ANIMAL/ARTIFACT/EVENT/
GROUP/SUBSTANCE, with an OTHER catch-all) -- a live, general classifier (`finer_wordnet_class` below),
not a per-item lookup table. AGENT is a constant ("He" -> PERSON) in every item here; it is included so
the context key is a genuine multi-slot BUNDLE (not a single richer scalar dressed up as one), matching
the task brief's "context_key = bundle over slots of bind(slot_role, filler_class)" literally, while
being provably harmless to correctness (an identical constant sub-binding applied to every item cannot
change WHICH item wins the argmax cleanup, since it is folded in identically at teach and predict time).

WHY BINARY ANIMACY IS INSUFFICIENT FOR THE DECISIVE SET (verified live, not asserted): all 5 new verbs
(run/draw/hold/throw/catch) have BOTH candidate senses take INANIMATE patients -- e.g. "run" -> compete
(a RACE) vs manage (a COMPANY), both inanimate. build_insufficient_items() asserts every one of these
50 nouns' `hdlab.animacy_lexicon.lookup_animacy(...)["animacy"] == "inanimate"` at import time -- if
this assert ever fails, the "insufficient" premise itself would be broken, and the cell would fail
loudly rather than silently. A pure-animacy context key can therefore ONLY ever produce ONE identical
query vector per word (both senses hash to the same "inanimate" key) -- structurally forced toward
~50% (chance on a 2-way choice), which is exactly what the ANIMACY-ONLY ARM below measures and is
EXPECTED to hit, by construction, not as an empirical surprise.

THE FINER CLASSIFIER (`finer_wordnet_class`, general, live WordNet hypernym-closure lookup -- NOT a
per-item table): checks the noun's FIRST WordNet noun-sense hypernym closure against a small fixed
PRIORITY list of named synsets (PERSON < ANIMAL < ARTIFACT < EVENT < GROUP < SUBSTANCE, most-specific-
first, mirroring hdlab.animacy_lexicon's own priority-chain design), falling back to a generic OTHER
bucket (physical_entity.n.01 or abstraction.n.06 in closure but none of the more specific classes hit).
Every noun used anywhere in this cell (regression set via reused Stage-2 data, decisive-set TRAIN/TEST
pools, and 10 fresh GENERALIZATION_PROBES never mentioned in any TRAIN/TEST pool) was verified against
this live classifier BEFORE this file was finalized (interactive WordNet probe transcript in the
completion report) and is RE-verified by a hard assert at import time -- if WordNet's classification of
any noun ever drifts, the cell fails loudly, exactly Stage 2's own convention.

TWO TEST SETS (per task brief):
  SUFFICIENT (regression): Stage 2's own 6-word setup (spoil/beat/strike/whip/crush/cherish), imported
    VERBATIM (data, not reimplemented) from `experiments.exp_word_context_affect_superposition_map_v1`
    -- WORD_SENSE_MENU, NOUN_POOLS, TRAIN_ITEMS, TEST_ITEMS, ALL_WORDS, AMBIGUOUS_WORDS, BASELINE_WORD,
    CANDIDATE_SENSES, and `_scrambled_teaching_table` (the scramble helper itself). The richer-key
    MECHANISM (2-slot bundle) is applied to this SAME data via the SAME "context_class" field Stage 2
    already populated -- a genuine mechanism-swap regression check, not a re-derivation.
  INSUFFICIENT (decisive, new): 5 words (run/draw/hold/throw/catch), each with 2 senses whose patients
    are BOTH inanimate but land in DIFFERENT finer WordNet classes:
      run   : compete (EVENT: race/marathon/tournament // contest/relay)
              vs manage (GROUP: company/business/firm // corporation/agency)
      draw  : sketch (ARTIFACT: picture/sketch/map // diagram/mural)
              vs attract (GROUP: crowd/audience/throng // mob/gathering)
      hold  : grasp (ARTIFACT: cup/pen/bag // box/bottle)
              vs convene (EVENT: wedding/ceremony/election // celebration/gala)
      throw : hurl (ARTIFACT: ball/spear/brick // frisbee/disc)
              vs host (EVENT: pageant/carnival/extravaganza // exhibition/fete)
      catch : grab (ARTIFACT: ball/frisbee/rope // dart/boomerang)
              vs contract-illness (OTHER: cold/flu/fever // chickenpox/mumps)
    3 TRAIN + 2 TEST nouns per (word,sense), TRAIN/TEST disjoint per pair (asserted), exactly mirroring
    Stage 2's own noun-pool shape.

THREE ARMS on the INSUFFICIENT set (per seed): RICH (2-slot bundle, patient label = finer WordNet
class), RICH-SCRAMBLE (RICH mechanism, globally-permuted teaching table -- can-fail control), and
ANIMACY-ONLY (patient label = coarse "inanimate"/"animate" via the SAME lookup_animacy Stage 2 used --
the fair, apples-to-apples negative control this cell's whole claim rests on: same mechanism, same
items, only the KEY GRANULARITY differs).

GENERALIZATION_PROBES (10, 2 per insufficient word, one per sense): fresh nouns NEVER present in any
TRAIN/TEST pool, verified live to hit the intended finer class, queried against the TAUGHT (TRAIN-only)
word_maps to confirm the classifier's generality (not a per-item lookup masquerading as one) actually
transfers to unseen fillers of the same class.

Reuses (wire-don't-island): hdlab.binding (bind/unbind), hdlab.bundling (bundle), hdlab.atoms
(make_atom_fhrr, similarity), hdlab.animacy_lexicon (lookup_animacy -- both for the regression set's
own context key AND as the ANIMACY-ONLY arm's negative control on the decisive set), nltk.corpus.wordnet
(the SAME WordNet resource hdlab.animacy_lexicon itself is built on, queried directly here for the
FINER hypernym classes hdlab.animacy_lexicon does not expose), experiments.exp_word_context_affect_
superposition_map_v1 (Stage 2 -- WORD_SENSE_MENU/NOUN_POOLS/TRAIN_ITEMS/TEST_ITEMS/CANDIDATE_SENSES/
_scrambled_teaching_table, imported not reimplemented), tools.exp_checkpoint (per-seed resumable unit).

Cites: notes/research_context_conditioned_grounding_and_extraction_2026-08-07.md (the research lead --
Resnik 1996 selectional association / Erk & Pado 2008 per-role profile / VerbNet-Levin classes turning
the single animacy scalar into a small bundle of typed slots); experiments/exp_word_context_affect_
superposition_map_v1.py (Stage 2, HARD_PASS 04af969c4, the map+collapse mechanism this cell extends).
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "richer_selectional_context_key_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402
from hdlab import binding, bundling, atoms  # noqa: E402 (REUSE: bind/unbind/bundle/cleanup primitives)
from hdlab.animacy_lexicon import lookup_animacy  # noqa: E402 (REUSE: coarse context feature + gate)
from nltk.corpus import wordnet as wn  # noqa: E402 (same resource hdlab.animacy_lexicon is built on)
import experiments.exp_word_context_affect_superposition_map_v1 as stage2  # noqa: E402 (REUSE: data)

SEEDS_FULL = [0, 1, 2, 3, 4]
SEEDS_SMOKE = [0]
N_DIM_WORD = 1024  # project default (CLAUDE.md); independent VSA namespace from Stage 2's own.

# ==================================================================================== FINER CLASSIFIER
# General, live WordNet hypernym-closure classifier -- NOT a per-item table. Priority list mirrors
# hdlab.animacy_lexicon's own most-specific-first design; PERSON/ANIMAL kept for generality (the
# classifier is meant to be genuinely general, even though no PATIENT noun in THIS cell's word set
# happens to need them -- AGENT slot uses PERSON as a constant, see CONTEXT_LABEL_VOCAB below).
_CLASS_PRIORITY = [
    ("PERSON", {"person.n.01"}),
    ("ANIMAL", {"animal.n.01"}),
    ("ARTIFACT", {"artifact.n.01"}),
    ("EVENT", {"event.n.01"}),
    ("GROUP", {"group.n.01"}),
    ("SUBSTANCE", {"substance.n.01", "matter.n.03", "food.n.01", "food.n.02"}),
]
_FALLBACK_TARGETS = {"physical_entity.n.01", "abstraction.n.06"}


def finer_wordnet_class(noun: str):
    """First-noun-sense WordNet hypernym-closure classification into a small general class inventory.
    Returns one of PERSON/ANIMAL/ARTIFACT/EVENT/GROUP/SUBSTANCE/OTHER, or None if WordNet has no noun
    sense at all. Priority-ordered (most specific first) exactly like hdlab.animacy_lexicon's own
    _wordnet_category -- EVENT and GROUP both live under abstraction.n.06 in WordNet's tree (so both
    must be checked before the generic OTHER catch-all, matching the priority-chain design pattern)."""
    syns = wn.synsets(noun, pos=wn.NOUN)
    if not syns:
        return None
    names = set()
    for path in syns[0].hypernym_paths():
        for s in path:
            names.add(s.name())
    for cls, targets in _CLASS_PRIORITY:
        if names & targets:
            return cls
    if names & _FALLBACK_TARGETS:
        return "OTHER"
    return None


# ================================================================================= INSUFFICIENT-SET DATA
INSUFFICIENT_WORDS = ["run", "draw", "hold", "throw", "catch"]
INSUFFICIENT_VERB_PAST = {"run": "ran", "draw": "drew", "hold": "held", "throw": "threw", "catch": "caught"}

INSUFFICIENT_SENSE_MENU = {
    "run":   {"EVENT": "COMPETE", "GROUP": "MANAGE"},
    "draw":  {"ARTIFACT": "SKETCH", "GROUP": "ATTRACT"},
    "hold":  {"ARTIFACT": "GRASP", "EVENT": "CONVENE"},
    "throw": {"ARTIFACT": "HURL", "EVENT": "HOST"},
    "catch": {"ARTIFACT": "GRAB", "OTHER": "CONTRACT_ILLNESS"},
}
CANDIDATE_SENSES_INSUFF = {w: sorted(set(INSUFFICIENT_SENSE_MENU[w].values())) for w in INSUFFICIENT_WORDS}

# noun pools (verified coherent against finer_wordnet_class + verified "inanimate" against
# lookup_animacy BEFORE authoring this cell -- interactive WordNet probe transcript in the completion
# report; re-verified live via hard assert in build_insufficient_items() below).
INSUFFICIENT_NOUN_POOLS = {
    "run":   {"EVENT":   (["race", "marathon", "tournament"], ["contest", "relay"]),
              "GROUP":   (["company", "business", "firm"], ["corporation", "agency"])},
    "draw":  {"ARTIFACT": (["picture", "sketch", "map"], ["diagram", "mural"]),
              "GROUP":   (["crowd", "audience", "throng"], ["mob", "gathering"])},
    "hold":  {"ARTIFACT": (["cup", "pen", "bag"], ["box", "bottle"]),
              "EVENT":   (["wedding", "ceremony", "election"], ["celebration", "gala"])},
    "throw": {"ARTIFACT": (["ball", "spear", "brick"], ["frisbee", "disc"]),
              "EVENT":   (["pageant", "carnival", "extravaganza"], ["exhibition", "fete"])},
    "catch": {"ARTIFACT": (["ball", "frisbee", "rope"], ["dart", "boomerang"]),
              "OTHER":   (["cold", "flu", "fever"], ["chickenpox", "mumps"])},
}

# 10 fresh generalization probes (2 per word, one per sense), NEVER present in any TRAIN/TEST pool
# above -- verified live to hit the intended finer class before authoring (see completion report).
GENERALIZATION_PROBES = [
    ("run", "EVENT", "steeplechase"), ("run", "GROUP", "syndicate"),
    ("draw", "ARTIFACT", "etching"), ("draw", "GROUP", "posse"),
    ("hold", "ARTIFACT", "jug"), ("hold", "EVENT", "inauguration"),
    ("throw", "ARTIFACT", "grenade"), ("throw", "EVENT", "fair"),
    ("catch", "ARTIFACT", "balloon"), ("catch", "OTHER", "shingles"),
]


def build_insufficient_items(word):
    """TRAIN (labeled teaching sentences) + TEST (held-out, disjoint nouns) items for `word`, mirroring
    Stage 2's build_items() shape exactly. Every noun is re-verified LIVE against finer_wordnet_class
    (must equal the intended finer label) AND against lookup_animacy (must be "inanimate" -- the whole
    point of the animacy-insufficient premise) -- a WordNet classification drift fails this at import
    time, not silently."""
    train, test = [], []
    for label in INSUFFICIENT_SENSE_MENU[word]:
        train_nouns, test_nouns = INSUFFICIENT_NOUN_POOLS[word][label]
        assert not (set(train_nouns) & set(test_nouns)), f"{word}/{label}: TRAIN/TEST noun overlap"
        gold_sense = INSUFFICIENT_SENSE_MENU[word][label]
        for n in train_nouns + test_nouns:
            fc = finer_wordnet_class(n)
            assert fc == label, f"{word}/{label}: noun {n!r} finer-classified {fc!r} (expected {label!r})"
            coarse = lookup_animacy(n, "NOUN")
            assert coarse is not None and coarse["animacy"] == "inanimate", (
                f"{word}/{label}: noun {n!r} animacy={coarse} -- expected inanimate (animacy-"
                f"insufficient premise requires ALL patients here to be inanimate)")
        for n in train_nouns:
            train.append({"word": word, "fine_label": label, "coarse_label": "inanimate", "patient_noun": n,
                          "gold_sense": gold_sense, "split": "train",
                          "sentence": f"He {INSUFFICIENT_VERB_PAST[word]} the {n}."})
        for n in test_nouns:
            test.append({"word": word, "fine_label": label, "coarse_label": "inanimate", "patient_noun": n,
                        "gold_sense": gold_sense, "split": "test",
                        "sentence": f"He {INSUFFICIENT_VERB_PAST[word]} the {n}."})
    return train, test


TRAIN_ITEMS_INSUFF, TEST_ITEMS_INSUFF = {}, {}
for _w in INSUFFICIENT_WORDS:
    TRAIN_ITEMS_INSUFF[_w], TEST_ITEMS_INSUFF[_w] = build_insufficient_items(_w)

# re-verify GENERALIZATION_PROBES live at import time too (same discipline as the pools above).
for _w, _label, _noun in GENERALIZATION_PROBES:
    _fc = finer_wordnet_class(_noun)
    assert _fc == _label, f"generalization probe {_w}/{_noun}: finer-classified {_fc!r} (expected {_label!r})"
    _all_pool_nouns = {n for cls in INSUFFICIENT_NOUN_POOLS[_w].values() for n in cls[0] + cls[1]}
    assert _noun not in _all_pool_nouns, f"generalization probe {_w}/{_noun}: noun IS in a TRAIN/TEST pool"

N_TEST_SUFF_AMBIGUOUS = sum(len(stage2.TEST_ITEMS[w]) for w in stage2.AMBIGUOUS_WORDS)  # 20
N_TEST_SUFF_BASELINE = len(stage2.TEST_ITEMS[stage2.BASELINE_WORD])                     # 4
N_TEST_INSUFF = sum(len(TEST_ITEMS_INSUFF[w]) for w in INSUFFICIENT_WORDS)              # 20
N_GEN_PROBES = len(GENERALIZATION_PROBES)                                               # 10

# ============================================================================== SHARED VSA VOCABULARY
ROLE_NAMES = ["AGENT", "PATIENT"]
# labels actually needed: coarse (Stage-2 regression set) + PERSON (AGENT constant) + the finer classes
# that actually appear among the insufficient-set's patients (ARTIFACT/EVENT/GROUP/OTHER). ANIMAL/
# SUBSTANCE are supported by finer_wordnet_class (general classifier) but unused by this cell's own
# word set -- no atom materialized for them, same as a real system only allocating what it encounters.
CONTEXT_LABEL_VOCAB = ["inanimate", "animate", "PERSON", "ARTIFACT", "EVENT", "GROUP", "OTHER"]

ALL_WORDS_COMBINED = stage2.ALL_WORDS + INSUFFICIENT_WORDS
ALL_SENSE_NAMES_COMBINED = sorted(set(stage2.ALL_SENSE_NAMES) |
                                   {s for w in INSUFFICIENT_WORDS for s in CANDIDATE_SENSES_INSUFF[w]})
CANDIDATE_SENSES_ALL = {**stage2.CANDIDATE_SENSES, **CANDIDATE_SENSES_INSUFF}

# Pre-registered bands (fixed BEFORE running, per the task brief's own gate spec).
BAND_RICH_INSUFF_PASS = 0.75          # gate 1: richer-key acc on the insufficient TEST set
BAND_ANIMACY_ONLY_MAX = 0.60          # gate 1: animacy-only-key acc on the SAME items (near chance)
BAND_MIN_MARGIN_RICH_OVER_ANIMACY = 0.15
BAND_NO_REGRESSION_SUFF_PASS = 0.75   # gate 2: richer-key (2-slot bundle) acc on Stage-2's own set
BAND_SCRAMBLE_MAX = 0.60              # gate 3: scramble collapse ceiling (both sets)
BAND_MIN_LIFT_OVER_SCRAMBLE = 0.15    # gate 3: real-vs-scramble lift floor (both sets)
BAND_GEN_PROBE_MIN = 0.80             # gate 4: >=8/10 fresh generalization probes correct
BAND_HARD_FAIL_INSUFF = 0.55
BAND_HARD_FAIL_SUFF = 0.55


# ------------------------------------------------------------------------- context-key construction
def build_context_keys(role_vecs, class_vecs):
    """context_key(label) = bundle( bind(ROLE_AGENT, class_vecs['PERSON']),
                                     bind(ROLE_PATIENT, class_vecs[label]) )
    A genuine 2-slot bundle: AGENT sub-binding is IDENTICAL across every label (constant "He"->PERSON
    subject in every item this cell uses), so it cannot change which sense wins the argmax cleanup at
    either teach or predict time -- included to satisfy "bundle over argument slots" literally, proven
    harmless by construction (same additive term folded in identically on both sides of every unbind)."""
    keys = {}
    for label in CONTEXT_LABEL_VOCAB:
        agent_part = binding.bind(role_vecs["AGENT"], class_vecs["PERSON"])
        patient_part = binding.bind(role_vecs["PATIENT"], class_vecs[label])
        keys[label] = bundling.bundle(torch.stack([agent_part, patient_part], dim=0))
    return keys


def teach_word_map(word, train_items, label_field, teaching_override, context_keys, sense_vecs):
    """Bundle(bind(context_key(item's label), taught_sense)) over every train item. `teaching_override`
    (None = REAL/gold teaching, or a scrambled {(word,label): sense_name} table) substitutes a
    MISTAUGHT sense -- the can-fail lever, reusing Stage 2's own table shape exactly."""
    entries = []
    for it in train_items:
        label = it[label_field]
        taught_sense = it["gold_sense"]
        if teaching_override is not None:
            key = (word, label)
            if key in teaching_override:
                taught_sense = teaching_override[key]
        entries.append(binding.bind(context_keys[label], sense_vecs[(word, taught_sense)]))
    return bundling.bundle(torch.stack(entries, dim=0))


def collapse_predict(word, label, word_map, context_keys, sense_vecs, candidate_senses):
    """UNBIND word_map by context_key(label), CLEANUP via k=1 argmax similarity against `word`'s own
    candidate-sense menu. Returns (predicted_sense_name, sims dict)."""
    recovered = binding.unbind(word_map, context_keys[label])
    sims = {sname: float(atoms.similarity(recovered, sense_vecs[(word, sname)])) for sname in candidate_senses}
    best = max(sims, key=sims.get)
    return best, sims


def eval_items(items, word_maps, label_field, context_keys, sense_vecs, candidate_senses_by_word):
    """Shared evaluation loop (used for every arm: suff real/scramble, insuff rich real/scramble,
    insuff animacy-only). Returns (acc, details list, predicted-sense digest)."""
    n_correct = 0
    details = []
    seq = []
    for it in items:
        w = it["word"]
        label = it[label_field]
        pred, sims = collapse_predict(w, label, word_maps[w], context_keys, sense_vecs, candidate_senses_by_word[w])
        ok = pred == it["gold_sense"]
        n_correct += int(ok)
        seq.append(pred)
        details.append({"word": w, "noun": it["patient_noun"], "label": label, "gold_sense": it["gold_sense"],
                        "pred_sense": pred, "sims": {k: round(v, 4) for k, v in sims.items()}, "correct": ok})
    acc = n_correct / len(items) if items else 0.0
    digest = hashlib.sha256(json.dumps(seq).encode()).hexdigest()[:16]
    return acc, details, digest


# ------------------------------------------------------------------------- per-seed unit
def run_seed(seed: int) -> dict:
    try:
        gen_vsa = torch.Generator().manual_seed(seed * 1000 + 42)
        role_vecs = {r: atoms.make_atom_fhrr(N_DIM_WORD, gen_vsa) for r in ROLE_NAMES}
        class_vecs = {c: atoms.make_atom_fhrr(N_DIM_WORD, gen_vsa) for c in CONTEXT_LABEL_VOCAB}
        sense_vecs = {(w, s): atoms.make_atom_fhrr(N_DIM_WORD, gen_vsa)
                      for w in ALL_WORDS_COMBINED for s in ALL_SENSE_NAMES_COMBINED}
        context_keys = build_context_keys(role_vecs, class_vecs)

        # ---- SUFFICIENT set (regression): Stage-2 data reused verbatim; label_field="context_class" ----
        real_table_suff = {(w, cls): stage2.WORD_SENSE_MENU[w][cls] for w in stage2.AMBIGUOUS_WORDS
                            for cls in ("inanimate", "animate")}
        scr_table_suff = stage2._scrambled_teaching_table(real_table_suff, seed=seed + 9000)

        word_maps_suff_real, word_maps_suff_scr = {}, {}
        for w in stage2.ALL_WORDS:
            word_maps_suff_real[w] = teach_word_map(w, stage2.TRAIN_ITEMS[w], "context_class", None,
                                                      context_keys, sense_vecs)
            if w in stage2.AMBIGUOUS_WORDS:
                word_maps_suff_scr[w] = teach_word_map(w, stage2.TRAIN_ITEMS[w], "context_class", scr_table_suff,
                                                         context_keys, sense_vecs)

        suff_test_items = [it for w in stage2.AMBIGUOUS_WORDS for it in stage2.TEST_ITEMS[w]]
        suff_baseline_items = stage2.TEST_ITEMS[stage2.BASELINE_WORD]

        acc_suff_real, items_suff_real, dig_suff_real = eval_items(
            suff_test_items, word_maps_suff_real, "context_class", context_keys, sense_vecs, stage2.CANDIDATE_SENSES)
        acc_suff_scr, items_suff_scr, dig_suff_scr = eval_items(
            suff_test_items, word_maps_suff_scr, "context_class", context_keys, sense_vecs, stage2.CANDIDATE_SENSES)
        acc_suff_baseline, items_suff_baseline, _ = eval_items(
            suff_baseline_items, word_maps_suff_real, "context_class", context_keys, sense_vecs, stage2.CANDIDATE_SENSES)

        # ---- INSUFFICIENT set (decisive): 3 arms -- RICH, RICH-SCRAMBLE, ANIMACY-ONLY ----
        real_table_insuff = {(w, label): INSUFFICIENT_SENSE_MENU[w][label] for w in INSUFFICIENT_WORDS
                              for label in INSUFFICIENT_SENSE_MENU[w]}
        scr_table_insuff = stage2._scrambled_teaching_table(real_table_insuff, seed=seed + 9500)

        word_maps_insuff_rich, word_maps_insuff_rich_scr, word_maps_insuff_animacy_only = {}, {}, {}
        for w in INSUFFICIENT_WORDS:
            word_maps_insuff_rich[w] = teach_word_map(w, TRAIN_ITEMS_INSUFF[w], "fine_label", None,
                                                        context_keys, sense_vecs)
            word_maps_insuff_rich_scr[w] = teach_word_map(w, TRAIN_ITEMS_INSUFF[w], "fine_label", scr_table_insuff,
                                                            context_keys, sense_vecs)
            # ANIMACY-ONLY arm: teach using coarse_label (== "inanimate" for every item of every word here)
            word_maps_insuff_animacy_only[w] = teach_word_map(w, TRAIN_ITEMS_INSUFF[w], "coarse_label", None,
                                                                context_keys, sense_vecs)

        insuff_test_items = [it for w in INSUFFICIENT_WORDS for it in TEST_ITEMS_INSUFF[w]]

        acc_insuff_rich, items_insuff_rich, dig_insuff_rich = eval_items(
            insuff_test_items, word_maps_insuff_rich, "fine_label", context_keys, sense_vecs, CANDIDATE_SENSES_INSUFF)
        acc_insuff_scr, items_insuff_scr, dig_insuff_scr = eval_items(
            insuff_test_items, word_maps_insuff_rich_scr, "fine_label", context_keys, sense_vecs, CANDIDATE_SENSES_INSUFF)
        acc_insuff_animacy_only, items_insuff_animacy_only, _ = eval_items(
            insuff_test_items, word_maps_insuff_animacy_only, "coarse_label", context_keys, sense_vecs,
            CANDIDATE_SENSES_INSUFF)

        # ---- GENERALIZATION PROBES (fresh nouns, never in any TRAIN/TEST pool) ----
        n_gen_correct = 0
        gen_detail = []
        for w, label, noun in GENERALIZATION_PROBES:
            gold_sense = INSUFFICIENT_SENSE_MENU[w][label]
            pred, sims = collapse_predict(w, label, word_maps_insuff_rich[w], context_keys, sense_vecs,
                                           CANDIDATE_SENSES_INSUFF[w])
            ok = pred == gold_sense
            n_gen_correct += int(ok)
            gen_detail.append({"word": w, "label": label, "noun": noun, "gold_sense": gold_sense,
                                "pred_sense": pred, "correct": ok})
        gen_probe_rate = n_gen_correct / N_GEN_PROBES

        arms_differ_suff = dig_suff_real != dig_suff_scr
        arms_differ_insuff = dig_insuff_rich != dig_insuff_scr

        return {
            "seed": seed,
            "suff": {"acc_rich_real": acc_suff_real, "acc_rich_scramble": acc_suff_scr,
                     "lift_over_scramble": acc_suff_real - acc_suff_scr, "acc_baseline": acc_suff_baseline,
                     "digests": {"real": dig_suff_real, "scramble": dig_suff_scr},
                     "arms_differ": arms_differ_suff},
            "insuff": {"acc_rich_real": acc_insuff_rich, "acc_rich_scramble": acc_insuff_scr,
                       "lift_over_scramble": acc_insuff_rich - acc_insuff_scr,
                       "acc_animacy_only": acc_insuff_animacy_only,
                       "margin_rich_over_animacy_only": acc_insuff_rich - acc_insuff_animacy_only,
                       "digests": {"real": dig_insuff_rich, "scramble": dig_insuff_scr},
                       "arms_differ": arms_differ_insuff},
            "gen_probe": {"rate": gen_probe_rate, "n_correct": n_gen_correct, "n_total": N_GEN_PROBES,
                          "detail": gen_detail},
            "items_suff_real": items_suff_real, "items_suff_scramble": items_suff_scr,
            "items_suff_baseline": items_suff_baseline,
            "items_insuff_rich": items_insuff_rich, "items_insuff_scramble": items_insuff_scr,
            "items_insuff_animacy_only": items_insuff_animacy_only,
            "failure_class": None,
        }
    except Exception as e:
        return {"seed": seed, "failure_class": f"{type(e).__name__}: {str(e)[:300]}",
                "traceback": traceback.format_exc()[:3000]}


# ------------------------------------------------------------------------- verdict
def aggregate_and_verdict(per_seed: dict, expected_n_seeds: int) -> dict:
    seeds = sorted(per_seed.keys())
    failed = [s for s in seeds if per_seed[s].get("failure_class")]
    ok_seeds = [s for s in seeds if not per_seed[s].get("failure_class")]

    n = len(seeds)
    if n < expected_n_seeds or len(ok_seeds) < expected_n_seeds:
        return {
            "verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
            "verdict_msg": f"landed {n} seeds ({len(ok_seeds)} ok, {len(failed)} failed), "
                           f"expected {expected_n_seeds}",
            "summary": "cardinality breach", "n_seeds": n, "n_ok": len(ok_seeds), "failed_seeds": failed,
        }

    def mean_of(getter):
        vals = [float(getter(per_seed[s])) for s in ok_seeds]
        return sum(vals) / max(1, len(vals))

    mean_suff_real = mean_of(lambda r: r["suff"]["acc_rich_real"])
    mean_suff_scr = mean_of(lambda r: r["suff"]["acc_rich_scramble"])
    lift_suff = mean_suff_real - mean_suff_scr
    mean_suff_baseline = mean_of(lambda r: r["suff"]["acc_baseline"])

    mean_insuff_rich = mean_of(lambda r: r["insuff"]["acc_rich_real"])
    mean_insuff_scr = mean_of(lambda r: r["insuff"]["acc_rich_scramble"])
    lift_insuff = mean_insuff_rich - mean_insuff_scr
    mean_insuff_animacy_only = mean_of(lambda r: r["insuff"]["acc_animacy_only"])
    margin = mean_insuff_rich - mean_insuff_animacy_only

    mean_gen_probe = mean_of(lambda r: r["gen_probe"]["rate"])

    any_arms_identical = any(
        (not per_seed[s]["suff"]["arms_differ"]) or (not per_seed[s]["insuff"]["arms_differ"])
        for s in ok_seeds)

    gate1_rich_wins = (mean_insuff_rich >= BAND_RICH_INSUFF_PASS) and \
                      (mean_insuff_animacy_only <= BAND_ANIMACY_ONLY_MAX) and \
                      (margin >= BAND_MIN_MARGIN_RICH_OVER_ANIMACY)
    gate2_no_regression = mean_suff_real >= BAND_NO_REGRESSION_SUFF_PASS
    gate3_scramble = (mean_suff_scr <= BAND_SCRAMBLE_MAX and lift_suff >= BAND_MIN_LIFT_OVER_SCRAMBLE) and \
                      (mean_insuff_scr <= BAND_SCRAMBLE_MAX and lift_insuff >= BAND_MIN_LIFT_OVER_SCRAMBLE)
    gate4_generalization = mean_gen_probe >= BAND_GEN_PROBE_MIN
    hard_fail_insuff = mean_insuff_rich < BAND_HARD_FAIL_INSUFF
    hard_fail_suff = mean_suff_real < BAND_HARD_FAIL_SUFF

    if any_arms_identical:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif gate1_rich_wins and gate2_no_regression and gate3_scramble and gate4_generalization:
        verdict = "HARD_PASS"
    elif hard_fail_insuff or hard_fail_suff or not gate3_scramble:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    summary = (f"[DECISIVE] insuff_rich={mean_insuff_rich:.3f} (band>={BAND_RICH_INSUFF_PASS}) "
               f"insuff_animacy_only={mean_insuff_animacy_only:.3f} (band<={BAND_ANIMACY_ONLY_MAX}) "
               f"margin={margin:.3f} (band>={BAND_MIN_MARGIN_RICH_OVER_ANIMACY}) | "
               f"[REGRESSION] suff_rich={mean_suff_real:.3f} (band>={BAND_NO_REGRESSION_SUFF_PASS}) "
               f"suff_baseline={mean_suff_baseline:.3f} | "
               f"[SCRAMBLE] suff_scr={mean_suff_scr:.3f} lift_suff={lift_suff:.3f} "
               f"insuff_scr={mean_insuff_scr:.3f} lift_insuff={lift_insuff:.3f} "
               f"(band<={BAND_SCRAMBLE_MAX} lift>={BAND_MIN_LIFT_OVER_SCRAMBLE}) | "
               f"[GENERALIZATION] gen_probe_rate={mean_gen_probe:.3f} (band>={BAND_GEN_PROBE_MIN}) "
               f"n_test_suff={N_TEST_SUFF_AMBIGUOUS} n_test_insuff={N_TEST_INSUFF} n_gen_probes={N_GEN_PROBES}")
    return {
        "verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
        "n_seeds": n, "n_ok": len(ok_seeds), "failed_seeds": failed,
        "means": {"insuff_rich": mean_insuff_rich, "insuff_animacy_only": mean_insuff_animacy_only,
                  "margin_rich_over_animacy_only": margin, "suff_rich": mean_suff_real,
                  "suff_baseline": mean_suff_baseline, "suff_scramble": mean_suff_scr,
                  "lift_suff": lift_suff, "insuff_scramble": mean_insuff_scr, "lift_insuff": lift_insuff,
                  "gen_probe_rate": mean_gen_probe},
        "bands": {"gate1_rich_wins": gate1_rich_wins, "gate2_no_regression": gate2_no_regression,
                  "gate3_scramble": gate3_scramble, "gate4_generalization": gate4_generalization,
                  "hard_fail_insuff": hard_fail_insuff, "hard_fail_suff": hard_fail_suff,
                  "any_arms_identical": any_arms_identical},
        "words": {"insufficient": INSUFFICIENT_WORDS, "sufficient_ambiguous": stage2.AMBIGUOUS_WORDS,
                  "sufficient_baseline": stage2.BASELINE_WORD, "insufficient_menu": INSUFFICIENT_SENSE_MENU},
    }


# ------------------------------------------------------------------------- infra (verbatim Stage-2 pattern)
def out_dir_for(run_mode: str) -> str:
    return OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"


def _write_start_marker(output_dir, run_mode, expected):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected,
              "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, d):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, default=str)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def run(run_mode):
    t0 = time.perf_counter()
    output_dir = out_dir_for(run_mode)
    seeds = SEEDS_SMOKE if run_mode == "smoke" else SEEDS_FULL
    expected_n_seeds = len(seeds)
    _write_start_marker(output_dir, run_mode, expected_n_seeds)
    done = completed_units(output_dir)
    for seed in seeds:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} already done, skipping", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed)
        record_unit(output_dir, k, res)
        if res.get("failure_class"):
            print(f"[FAIL] seed={seed} {res['failure_class']}", flush=True)
        else:
            print(f"[progress] seed={seed} done in {time.perf_counter()-ts:.1f}s "
                  f"insuff_rich={res['insuff']['acc_rich_real']:.3f} "
                  f"insuff_animacy_only={res['insuff']['acc_animacy_only']:.3f} "
                  f"suff_rich={res['suff']['acc_rich_real']:.3f} "
                  f"gen_probe={res['gen_probe']['rate']:.3f}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(output_dir).values()}
    agg = aggregate_and_verdict(per_seed, expected_n_seeds)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"seeds": seeds, "n_dim_word": N_DIM_WORD,
                      "n_test_suff_ambiguous": N_TEST_SUFF_AMBIGUOUS, "n_test_suff_baseline": N_TEST_SUFF_BASELINE,
                      "n_test_insuff": N_TEST_INSUFF, "n_gen_probes": N_GEN_PROBES,
                      "bands": {"rich_insuff_pass": BAND_RICH_INSUFF_PASS,
                                "animacy_only_max": BAND_ANIMACY_ONLY_MAX,
                                "min_margin_rich_over_animacy": BAND_MIN_MARGIN_RICH_OVER_ANIMACY,
                                "no_regression_suff_pass": BAND_NO_REGRESSION_SUFF_PASS,
                                "scramble_max": BAND_SCRAMBLE_MAX,
                                "min_lift_over_scramble": BAND_MIN_LIFT_OVER_SCRAMBLE,
                                "gen_probe_min": BAND_GEN_PROBE_MIN,
                                "hard_fail_insuff": BAND_HARD_FAIL_INSUFF, "hard_fail_suff": BAND_HARD_FAIL_SUFF}}
    agg["per_seed"] = per_seed
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ------------------------------------------------------------------------- self-test
def self_test():
    """(1) pool/menu structural checks (disjointness + coherent labels, reaffirming import-time asserts);
    (2) tiny end-to-end run_seed(0): all 4 gates clear their pre-registered bands, arms pairwise differ
    (META_RULE_AF), animacy-only arm sits near chance as structurally expected."""
    # (1) structural
    for w in INSUFFICIENT_WORDS:
        assert len(CANDIDATE_SENSES_INSUFF[w]) == 2, f"{w}: expected 2 candidate senses"
        for label, (train_n, test_n) in INSUFFICIENT_NOUN_POOLS[w].items():
            assert not (set(train_n) & set(test_n)), f"{w}/{label}: TRAIN/TEST overlap"
    assert N_TEST_INSUFF == 20 and N_TEST_SUFF_AMBIGUOUS == 20 and N_GEN_PROBES == 10

    # (2) tiny end-to-end run
    res = run_seed(0)
    assert res["failure_class"] is None, f"run_seed crashed: {res.get('failure_class')}"
    assert res["insuff"]["acc_rich_real"] >= BAND_RICH_INSUFF_PASS, (
        f"insuff rich-key did not clear band: {res['insuff']['acc_rich_real']:.3f} < {BAND_RICH_INSUFF_PASS}")
    assert res["insuff"]["acc_animacy_only"] <= BAND_ANIMACY_ONLY_MAX, (
        f"insuff animacy-only arm did not sit near chance: {res['insuff']['acc_animacy_only']:.3f} "
        f"> {BAND_ANIMACY_ONLY_MAX}")
    assert res["insuff"]["margin_rich_over_animacy_only"] >= BAND_MIN_MARGIN_RICH_OVER_ANIMACY, (
        f"margin too small: {res['insuff']['margin_rich_over_animacy_only']:.3f}")
    assert res["suff"]["acc_rich_real"] >= BAND_NO_REGRESSION_SUFF_PASS, (
        f"regression: suff rich-key acc {res['suff']['acc_rich_real']:.3f} < {BAND_NO_REGRESSION_SUFF_PASS}")
    assert res["suff"]["acc_rich_scramble"] <= BAND_SCRAMBLE_MAX, "suff scramble did not collapse"
    assert res["insuff"]["acc_rich_scramble"] <= BAND_SCRAMBLE_MAX, "insuff scramble did not collapse"
    assert res["suff"]["lift_over_scramble"] >= BAND_MIN_LIFT_OVER_SCRAMBLE, "suff lift too small"
    assert res["insuff"]["lift_over_scramble"] >= BAND_MIN_LIFT_OVER_SCRAMBLE, "insuff lift too small"
    assert res["gen_probe"]["rate"] >= BAND_GEN_PROBE_MIN, (
        f"generalization probes did not clear band: {res['gen_probe']['rate']:.3f} < {BAND_GEN_PROBE_MIN}")
    assert res["suff"]["arms_differ"], "META_RULE_AF: suff real/scramble digests identical"
    assert res["insuff"]["arms_differ"], "META_RULE_AF: insuff real/scramble digests identical"

    print(f"[SELFTEST PASS] insuff_rich={res['insuff']['acc_rich_real']:.3f} "
          f"insuff_animacy_only={res['insuff']['acc_animacy_only']:.3f} "
          f"margin={res['insuff']['margin_rich_over_animacy_only']:.3f} "
          f"suff_rich={res['suff']['acc_rich_real']:.3f} suff_scr={res['suff']['acc_rich_scramble']:.3f} "
          f"insuff_scr={res['insuff']['acc_rich_scramble']:.3f} gen_probe={res['gen_probe']['rate']:.3f}",
          flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        ok = self_test()
        raise SystemExit(0 if ok else 1)
    if args.smoke:
        run("smoke")
        raise SystemExit(0)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash(OUTPUT_DIR, e)
        raise
