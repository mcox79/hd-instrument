# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: real-vs-scramble final-predicted-sense digest over the 20 ambiguous held-out
#   TEST items MUST differ pairwise (asserted per-seed in aggregate_and_verdict, META_RULE_AF).
# - final_metrics_atomicity: tmp_replace (write metrics.json.tmp then os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no swept capacity dimension; this cell proves a MECHANISM (superposition collapse), not a
#   capacity envelope -- the VSA layer runs 2-component bundles (well inside any capacity floor at
#   N_DIM_WORD=1024; see module docstring CAPACITY NOTE).
# - baseline_in_band: n/a (no chance-level negative-control arm; SCRAMBLE is the can-fail negative
#   control here, gated on its own band per the task brief, not a 0.5-chance floor).
# - discriminator survives scale: full-N == smoke-N item set (20 ambiguous held-out items + 4 baseline
#   items, fixed); only theta-training steps for the bonus grounded-affect witness differ (reused
#   verbatim from Stage-1: SMOKE_N_TRAIN_THETA=4000, FULL=8000). The VSA collapse mechanism itself does
#   not depend on n_train_theta at all (self-contained tensor ops); smoke fires the full discriminator.
# - cardinality_ok: EXPECTED_N_SEEDS=5; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land.
# - per-unit failure-class instrumentation (no bare except; per-seed crash recorded).
# - calibration_check: default_ok_for_this_regime (bands fixed BEFORE this cell was run per the task
#   brief's own gate: held-out >=0.75, scramble<=0.60 with lift>=0.15, context-driven==1.0, baseline
#   >=0.75 -- not tuned after seeing results).
# - deterministic_seeding: torch.Generator per seed for VSA atoms (context-class role vectors + per-
#   (word,sense) fillers) AND for Stage-1's frozen theta (reused verbatim); scramble permutation via
#   random.Random(fixed int seed) (PROT-023, not builtin hash()); animacy lookups are themselves
#   deterministic (WordNet first-noun-sense), no RNG.
# - cell_chunked: true (per-seed unit via tools/exp_checkpoint.py).
# - LOCAL ONLY, ISOLATED PROBE: no queue dispatch, no remote ship, no canonical-store write, no
#   hdlab/ edits -- prove-architecture experiment cell (Stage 2 of notes/PLAN_B_grounding_word_
#   context_affect_superposition_map_2026-08-07.md), not production wiring.
# - all reported numbers MEASURED@ tagged in the completion report, not this file.
"""experiments/exp_word_context_affect_superposition_map_v1.py -- ISOLATED prove-architecture probe for
notes/PLAN_B_grounding_word_context_affect_superposition_map_2026-08-07.md STAGE 2 (Layer 2): the WORD
-> CONTEXT -> AFFECT SUPERPOSITION MAP with TAUGHT context-collapse.

THE MECHANISM (USER's design, VSA-native, glass-box):
A word's meaning+affect is a SUPERPOSITION of its candidate senses:
    word_map = bundle_over_senses( bind(context_key_for_sense, sense_and_affect_vector) )
At read time: form the context key from the situation (here: the direct-object patient's WordNet
ANIMACY, reusing hdlab.animacy_lexicon.lookup_animacy -- the SAME context feature the certified
physical-harm axis, hdlab/context_grounded_valence.py, already uses to override event type), UNBIND
(word_map (X) context_key^-1), CLEANUP against the word's own small candidate-sense menu -> the entry
whose context matches COLLAPSES out. All three primitives (bind/unbind/bundle) are the owned hdlab
ones (hdlab.binding, hdlab.bundling, hdlab.atoms.similarity for cleanup) -- FHRR (complex64), N_DIM_
WORD=1024 (project default per CLAUDE.md), unmodified, imported not reimplemented.

SUPPLIED vs LEARNED (the line the plan draws, USER emphatic -- "the use of spoil in that context needs
to be TAUGHT"):
  SUPPLIED (MENU, invariant-OK DATA, same status as a WordNet sense list or the physical-harm axis's
    animacy feature): WORD_SENSE_MENU (word -> {context_class: candidate sense NAME}, 1-2 candidates
    per word) and SENSE_AFFECT_TYPE (sense name -> which of Stage-1's two validated signed poles,
    RECIPROCITY=positive / BLOCK_HIGH=negative, it belongs to). This is the "dictionary" -- it says
    WHAT the candidate senses of a word ARE and which pole each carries, not which context selects
    which sense.
  LEARNED (TAUGHT from labeled TRAIN sentences, can-fail): the (context_class -> WHICH candidate
    sense) binding baked into each word's word_map by teach_word_map() reading TRAIN_ITEMS (3 labeled
    example sentences per context class per word, built from noun pools DISJOINT from the 2 held-out
    TEST nouns per context class -- generalization to unseen lexical instances of the same context
    class, not sentence memorization). The SCRAMBLE control (the decisive gate) rebuilds the word_maps
    from a GLOBALLY PERMUTED teaching table (Stage-1's own `_scrambled_polarity` pattern, reused
    verbatim in spirit: sorted keys, random.Random(seed).shuffle values, zip back) -- if collapse
    accuracy survives that permutation, the map is a fixed lookup, not a taught association; if it
    collapses, the map genuinely encodes what was TAUGHT.
  Stage-1's grounded valuation (exp_social_relational_grounding_axis_v1, HARD_PASS ca1d70d1a) supplies
    each sense's numeric AFFECT: SENSE_AFFECT_TYPE maps a sense to RECIPROCITY or BLOCK_HIGH, and this
    cell calls Stage-1's own `social_valence(cb, theta, type)` (imported, not reimplemented) on the SAME
    frozen appraisal-sim theta to report the actual signed value each pole carries (theta_witness,
    per-seed). Sense-identity accuracy IS affect-sign accuracy here (SENSE_AFFECT_TYPE is a fixed
    deterministic map), so one collapse-accuracy number answers both "which sense" and "which affect".

WORDS (6 total -- 5 ambiguous + 1 single-sense baseline; context key = patient animacy, reusing
hdlab.animacy_lexicon.lookup_animacy verbatim; every noun's real WordNet animacy was verified against
its intended class before authoring, see coverage check in the completion report):
  spoil   inanimate(food) -> RUIN   (NEG/BLOCK_HIGH)   | animate(child/animal) -> PAMPER (POS/RECIP)
  beat    inanimate(abstract/object, "the record") -> BENIGN (POS) | animate -> HARM (NEG)
  strike  inanimate(object, "a match/bell/coin") -> BENIGN (POS)   | animate -> HARM (NEG)
  whip    inanimate(cooking, "the cream/eggs") -> BENIGN (POS)     | animate(animal) -> HARM (NEG)
  crush   inanimate(object, "the grapes/cans") -> BENIGN (POS)     | animate -> HARM (NEG)
  cherish SINGLE-SENSE BASELINE: inanimate AND animate both -> CHERISH (POS) -- an unambiguous word,
    taught the SAME sense under both context classes; tests that the map gracefully degrades to
    Stage-1-style flat behavior when there is nothing to disambiguate (no special-cased code path --
    same teach/collapse functions as the ambiguous words).
`spoil` is DELIBERATELY the reverse polarity of beat/strike/whip/crush (inanimate=NEG, animate=POS
vs the other four's inanimate=POS, animate=NEG) -- this rules out the confound "the map just learned a
universal animate->positive heuristic"; the SAME context feature must select OPPOSITE senses for
different words, which only a genuinely per-word TAUGHT association (not a generic animacy rule) can
produce. See CAN-FAIL GATES below for how this is measured (context-driven divergence, gate 3).

CAPACITY NOTE: each word_map bundles exactly 2 distinct components (one per context class; the 3
redundant TRAIN nouns per class produce algebraically IDENTICAL bind() outputs since context_class and
taught_sense -- not noun identity -- are the only inputs to bind(), so a word_map is a bundle-of-2, well
inside VSA capacity at N_DIM_WORD=1024; this is not a capacity-stress cell, TRAIN nouns are held-out-
vs-TEST for the "taught from labeled examples, generalizes to unseen lexical instances" narrative, not
because bundling load is the stressor here. The stressor this cell measures is TAUGHT-vs-SCRAMBLED, not
bundle capacity.

CAN-FAIL GATES (bands fixed before running, per task brief):
  1. HELD-OUT COLLAPSE: mean acc_real >= 0.75 over the 20 ambiguous held-out TEST items (5 words x 2
     context classes x 2 held-out nouns each), REAL teaching.
  2. TAUGHT-vs-SCRAMBLED (decisive): mean acc_scramble <= 0.60 AND lift (acc_real - acc_scramble) >=
     0.15 on the SAME 20 items, word_maps rebuilt from the globally-permuted teaching table.
  3. CONTEXT-DRIVEN: for each of the 5 ambiguous words, querying the SAME REAL word_map with the
     inanimate vs animate context key must collapse to DIFFERENT (and each individually CORRECT)
     senses -- mean context_driven_rate == 1.0 required for HARD-PASS.
  4. SINGLE-SENSE BASELINE: cherish's 4 held-out items collapse correctly (acc_baseline >= 0.75)
     AND its two context queries return the SAME sense (baseline_stable_rate == 1.0) -- graceful
     degradation, not a broken/divergent read on an unambiguous word.

Reuses (wire-don't-island): hdlab.binding (bind/unbind), hdlab.bundling (bundle), hdlab.atoms
(make_atom_fhrr, similarity -- k=1 argmax cleanup over each word's own small candidate menu, the
FHRR/complex64-native sibling of hdlab.cleanup_family.k_NN_lookup's contract), hdlab.animacy_lexicon
(lookup_animacy -- the context-key feature extractor, same primitive hdlab/context_grounded_valence.py
uses for its animacy-axis event override), experiments.exp_social_relational_grounding_axis_v1 (Stage
1, imported verbatim for sim.Codebook / sim.train_theta / social_valence -- the grounded-affect witness).

Cites: notes/PLAN_B_grounding_word_context_affect_superposition_map_2026-08-07.md (Layer 2, the plan
this cell tests); experiments/exp_social_relational_grounding_axis_v1.py (Stage 1, HARD_PASS ca1d70d1a,
reused for grounded affect); hdlab/context_grounded_valence.py (the certified physical-harm organ this
cell's context-key choice parallels); hdlab/animacy_lexicon.py (reused context feature); hdlab/binding.py,
hdlab/bundling.py, hdlab/atoms.py (reused VSA primitives).
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import random
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "word_context_affect_superposition_map_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402
from hdlab import binding, bundling, atoms  # noqa: E402 (REUSE: bind/unbind/bundle/cleanup primitives)
from hdlab.animacy_lexicon import lookup_animacy  # noqa: E402 (REUSE: context-key feature extractor)
import experiments.exp_social_relational_grounding_axis_v1 as stage1  # noqa: E402 (REUSE: sim/theta/social_valence)

SEEDS = [0, 1, 2, 3, 4]
EXPECTED_N_SEEDS = len(SEEDS)
FULL_N_TRAIN_THETA = stage1.FULL_N_TRAIN_THETA
SMOKE_N_TRAIN_THETA = stage1.SMOKE_N_TRAIN_THETA
N_DIM_WORD = 1024  # project default (CLAUDE.md); this cell's OWN word-level VSA layer dimension,
                    # independent of Stage-1's internal appraisal-sim N_DIM=256 (separate namespaces).

# ------------------------------------------------------------------------- MENU (supplied, invariant-OK)
WORD_SENSE_MENU = {
    "spoil":   {"inanimate": "RUIN",   "animate": "PAMPER"},
    "beat":    {"inanimate": "BENIGN", "animate": "HARM"},
    "strike":  {"inanimate": "BENIGN", "animate": "HARM"},
    "whip":    {"inanimate": "BENIGN", "animate": "HARM"},
    "crush":   {"inanimate": "BENIGN", "animate": "HARM"},
    "cherish": {"inanimate": "CHERISH", "animate": "CHERISH"},  # single-sense baseline
}
AMBIGUOUS_WORDS = ["spoil", "beat", "strike", "whip", "crush"]
BASELINE_WORD = "cherish"
ALL_WORDS = AMBIGUOUS_WORDS + [BASELINE_WORD]

SENSE_AFFECT_TYPE = {          # sense name -> Stage-1's validated signed pole (imported types, unmodified)
    "RUIN": "BLOCK_HIGH", "PAMPER": "RECIPROCITY",
    "BENIGN": "RECIPROCITY", "HARM": "BLOCK_HIGH",
    "CHERISH": "RECIPROCITY",
}
ALL_SENSE_NAMES = sorted(SENSE_AFFECT_TYPE.keys())  # cross-product sense-vector pool (see CAPACITY NOTE
                                                     # on why a scrambled binding needs an off-menu vector
                                                     # to exist for every (word, foreign-sense) pair)

VERB_PAST = {"spoil": "spoiled", "beat": "beat", "strike": "struck", "whip": "whipped",
             "crush": "crushed", "cherish": "cherished"}

CANDIDATE_SENSES = {w: sorted(set(WORD_SENSE_MENU[w].values())) for w in ALL_WORDS}

# ------------------------------------------------------------------------- noun pools (verified coverage)
# Every noun below was checked against hdlab.animacy_lexicon.lookup_animacy BEFORE authoring this cell
# (coverage probe run interactively; re-verified live in build_items() below via a hard assert -- if
# WordNet's classification of any noun ever drifts, this cell fails loudly at import time, not silently).
NOUN_POOLS = {
    "spoil":   {"inanimate": (["milk", "meat", "bread"], ["cheese", "fruit"]),
                "animate":   (["child", "boy", "girl"], ["kitten", "son"])},
    "beat":    {"inanimate": (["record", "deadline", "odds"], ["buzzer", "clock"]),
                "animate":   (["dog", "man", "opponent"], ["guard", "stranger"])},
    "strike":  {"inanimate": (["match", "bell", "coin"], ["gong", "anvil"]),
                "animate":   (["boy", "girl", "dog"], ["mule", "man"])},
    "whip":    {"inanimate": (["cream", "eggs", "custard"], ["icing", "meringue"]),
                "animate":   (["horse", "mule", "dog"], ["puppy", "calf"])},
    "crush":   {"inanimate": (["grapes", "cans", "ice"], ["rocks", "leaves"]),
                "animate":   (["ant", "beetle", "spider"], ["rival", "opponent"])},
    "cherish": {"inanimate": (["photo", "letter", "gift"], ["ring", "painting"]),
                "animate":   (["daughter", "friend", "grandmother"], ["wife", "husband"])},
}


def build_items(word):
    """TRAIN (labeled teaching sentences) + TEST (held-out, disjoint nouns) items for `word`. The
    context_class actually used is DERIVED live from hdlab.animacy_lexicon.lookup_animacy(noun) --
    not merely trusted from the pool's own label -- so this is a genuine re-use of the owned context
    feature, not a hardcoded shortcut; a WordNet classification drift fails this assert at import time."""
    train, test = [], []
    for cls in ("inanimate", "animate"):
        train_nouns, test_nouns = NOUN_POOLS[word][cls]
        assert not (set(train_nouns) & set(test_nouns)), f"{word}/{cls}: TRAIN/TEST noun overlap"
        gold_sense = WORD_SENSE_MENU[word][cls]
        for n in train_nouns + test_nouns:
            real = lookup_animacy(n, "NOUN")
            assert real is not None and real["animacy"] == cls, (
                f"{word}/{cls}: noun {n!r} classified {real} (expected animacy={cls!r})")
        for n in train_nouns:
            train.append({"word": word, "context_class": cls, "patient_noun": n,
                          "gold_sense": gold_sense, "split": "train",
                          "sentence": f"He {VERB_PAST[word]} the {n}."})
        for n in test_nouns:
            test.append({"word": word, "context_class": cls, "patient_noun": n,
                        "gold_sense": gold_sense, "split": "test",
                        "sentence": f"He {VERB_PAST[word]} the {n}."})
    return train, test


TRAIN_ITEMS = {}
TEST_ITEMS = {}
for _w in ALL_WORDS:
    TRAIN_ITEMS[_w], TEST_ITEMS[_w] = build_items(_w)

N_TEST_AMBIGUOUS = sum(len(TEST_ITEMS[w]) for w in AMBIGUOUS_WORDS)   # 20 (5 words x 2 cls x 2 nouns)
N_TEST_BASELINE = len(TEST_ITEMS[BASELINE_WORD])                     # 4

# HARD-PASS / HARD-FAIL bands (fixed BEFORE the full 5-seed run per the task brief's own gate spec).
BAND_HELDOUT_PASS = 0.75
BAND_SCRAMBLE_MAX_FOR_COLLAPSE = 0.60
BAND_MIN_LIFT_OVER_SCRAMBLE = 0.15
BAND_CONTEXT_DRIVEN_MIN = 1.0
BAND_BASELINE_PASS = 0.75
BAND_BASELINE_STABLE_MIN = 1.0
BAND_HARD_FAIL_HELDOUT = 0.55


def _scrambled_teaching_table(table: dict, seed: int) -> dict:
    """Stage-1 pattern (`_scrambled_polarity`), reused verbatim in spirit: GLOBAL permutation of VALUES
    across KEYS (random.Random fixed-int-seeded, NOT builtin hash() -- PROT-023). table keys are
    (word, context_class) tuples over the 5 AMBIGUOUS words only (10 keys); values are sense names.
    A permuted key may land on: (a) its own word's OTHER sense (deterministic wrong-collapse, a clean
    within-word inversion) or (b) another word's sense name entirely (off-menu -- collapse against that
    word's own 2-item candidate menu degrades toward chance, since the bound content matches neither
    real candidate well). Both outcomes are legitimate "mistaught" evidence; see module CAN-FAIL GATES."""
    keys_sorted = sorted(table.keys())
    vals_sorted = [table[k] for k in keys_sorted]
    rng = random.Random(seed)
    permuted = vals_sorted[:]
    rng.shuffle(permuted)
    return dict(zip(keys_sorted, permuted))


def teach_word_map(word, train_items, teaching_override, ctx_vecs, sense_vecs):
    """Build word's superposition map from labeled TRAIN sentences: bundle(bind(context_key, taught_
    sense)) over every train item. `teaching_override` (None = REAL/gold teaching, or a scrambled
    {(word,cls): sense_name} table) substitutes a MISTAUGHT sense for the item's own gold_sense -- the
    can-fail lever. Multiple train nouns per context class produce algebraically identical bind()
    outputs (only context_class + taught_sense feed bind(), not noun identity -- see CAPACITY NOTE);
    this is honest by design, not a bug: the map is taught the CONTEXT-CLASS association, at the
    granularity the task brief's own context feature (animacy) supports."""
    entries = []
    for it in train_items:
        cls = it["context_class"]
        taught_sense = it["gold_sense"]
        if teaching_override is not None:
            key = (word, cls)
            if key in teaching_override:
                taught_sense = teaching_override[key]
        entries.append(binding.bind(ctx_vecs[cls], sense_vecs[(word, taught_sense)]))
    stacked = torch.stack(entries, dim=0)
    return bundling.bundle(stacked)


def collapse_predict(word, context_class, word_map, ctx_vecs, sense_vecs, candidate_senses):
    """UNBIND word_map by the context key, CLEANUP via k=1 argmax similarity against `word`'s own
    candidate-sense menu (hdlab.atoms.similarity -- the FHRR/complex64-native sibling of hdlab.
    cleanup_family.k_NN_lookup's k=1 argmax contract). Returns (predicted_sense_name, sims dict)."""
    recovered = binding.unbind(word_map, ctx_vecs[context_class])
    sims = {sname: float(atoms.similarity(recovered, sense_vecs[(word, sname)]))
            for sname in candidate_senses}
    best = max(sims, key=sims.get)
    return best, sims


def _predicted_seq_digest(word_maps, ctx_vecs, sense_vecs, items_by_word, words):
    seq = []
    for w in words:
        for it in items_by_word[w]:
            pred, _sims = collapse_predict(w, it["context_class"], word_maps[w], ctx_vecs, sense_vecs,
                                            CANDIDATE_SENSES[w])
            seq.append(pred)
    return hashlib.sha256(json.dumps(seq).encode()).hexdigest()[:16], seq


# ------------------------------------------------------------------------- per-seed unit
def run_seed(seed: int, n_train_theta: int) -> dict:
    try:
        # ---- VSA atoms for this seed: context-class role vectors + full (word, sense-name) fillers ----
        gen_vsa = torch.Generator().manual_seed(seed * 1000 + 42)
        ctx_vecs = {cls: atoms.make_atom_fhrr(N_DIM_WORD, gen_vsa) for cls in ("inanimate", "animate")}
        sense_vecs = {}
        for word in ALL_WORDS:
            for sname in ALL_SENSE_NAMES:
                sense_vecs[(word, sname)] = atoms.make_atom_fhrr(N_DIM_WORD, gen_vsa)
        gen_noise = torch.Generator().manual_seed(seed * 1000 + 99)
        untrained_probe = atoms.make_atom_fhrr(N_DIM_WORD, gen_noise)  # bonus witness, never taught

        # ---- teaching tables: REAL (gold, implicit via teach_word_map default) + SCRAMBLE (permuted) ----
        real_table = {(w, cls): WORD_SENSE_MENU[w][cls] for w in AMBIGUOUS_WORDS
                      for cls in ("inanimate", "animate")}
        scr_table = _scrambled_teaching_table(real_table, seed=seed + 9000)

        # ---- build word_maps: REAL (all 6 words), SCRAMBLE (5 ambiguous words only) ----
        word_maps_real, word_maps_scr = {}, {}
        for word in ALL_WORDS:
            word_maps_real[word] = teach_word_map(word, TRAIN_ITEMS[word], None, ctx_vecs, sense_vecs)
            if word in AMBIGUOUS_WORDS:
                word_maps_scr[word] = teach_word_map(word, TRAIN_ITEMS[word], scr_table, ctx_vecs, sense_vecs)

        # ---- gate 1+2: held-out collapse (REAL) + scramble control, over the same 20 ambiguous items ----
        items_real, items_scr = [], []
        n_correct_real = n_correct_scr = 0
        for word in AMBIGUOUS_WORDS:
            for it in TEST_ITEMS[word]:
                pred_r, sims_r = collapse_predict(word, it["context_class"], word_maps_real[word],
                                                   ctx_vecs, sense_vecs, CANDIDATE_SENSES[word])
                ok_r = pred_r == it["gold_sense"]
                n_correct_real += int(ok_r)
                items_real.append({"word": word, "noun": it["patient_noun"], "context_class": it["context_class"],
                                    "gold_sense": it["gold_sense"], "pred_sense": pred_r,
                                    "sims": {k: round(v, 4) for k, v in sims_r.items()}, "correct": ok_r})
                pred_s, sims_s = collapse_predict(word, it["context_class"], word_maps_scr[word],
                                                   ctx_vecs, sense_vecs, CANDIDATE_SENSES[word])
                ok_s = pred_s == it["gold_sense"]
                n_correct_scr += int(ok_s)
                items_scr.append({"word": word, "noun": it["patient_noun"], "context_class": it["context_class"],
                                   "gold_sense": it["gold_sense"], "pred_sense": pred_s,
                                   "sims": {k: round(v, 4) for k, v in sims_s.items()}, "correct": ok_s})
        acc_real = n_correct_real / N_TEST_AMBIGUOUS
        acc_scramble = n_correct_scr / N_TEST_AMBIGUOUS

        # ---- gate 4: single-sense baseline (cherish), REAL teaching only ----
        items_baseline = []
        n_correct_baseline = 0
        for it in TEST_ITEMS[BASELINE_WORD]:
            pred_b, sims_b = collapse_predict(BASELINE_WORD, it["context_class"], word_maps_real[BASELINE_WORD],
                                               ctx_vecs, sense_vecs, CANDIDATE_SENSES[BASELINE_WORD])
            ok_b = pred_b == it["gold_sense"]
            n_correct_baseline += int(ok_b)
            items_baseline.append({"noun": it["patient_noun"], "context_class": it["context_class"],
                                    "gold_sense": it["gold_sense"], "pred_sense": pred_b, "correct": ok_b})
        acc_baseline = n_correct_baseline / N_TEST_BASELINE

        # ---- gate 3: context-driven divergence (query context classes directly, REAL word_maps) ----
        divergence_detail = {}
        n_divergent_correct = 0
        for word in AMBIGUOUS_WORDS:
            pred_in, _ = collapse_predict(word, "inanimate", word_maps_real[word], ctx_vecs, sense_vecs,
                                           CANDIDATE_SENSES[word])
            pred_an, _ = collapse_predict(word, "animate", word_maps_real[word], ctx_vecs, sense_vecs,
                                           CANDIDATE_SENSES[word])
            gold_in, gold_an = WORD_SENSE_MENU[word]["inanimate"], WORD_SENSE_MENU[word]["animate"]
            diverges = pred_in != pred_an
            correct_both = (pred_in == gold_in) and (pred_an == gold_an)
            divergence_detail[word] = {"pred_in": pred_in, "pred_an": pred_an, "gold_in": gold_in,
                                        "gold_an": gold_an, "diverges": diverges, "correct_both": correct_both}
            n_divergent_correct += int(diverges and correct_both)
        context_driven_rate = n_divergent_correct / len(AMBIGUOUS_WORDS)

        # ---- baseline stability (single-sense word must NOT diverge across context) ----
        b_pred_in, _ = collapse_predict(BASELINE_WORD, "inanimate", word_maps_real[BASELINE_WORD],
                                         ctx_vecs, sense_vecs, CANDIDATE_SENSES[BASELINE_WORD])
        b_pred_an, _ = collapse_predict(BASELINE_WORD, "animate", word_maps_real[BASELINE_WORD],
                                         ctx_vecs, sense_vecs, CANDIDATE_SENSES[BASELINE_WORD])
        baseline_stable = (b_pred_in == b_pred_an == WORD_SENSE_MENU[BASELINE_WORD]["inanimate"])

        # ---- bonus (non-gated) witness: untrained/never-taught probe vs spoil's 2 candidates ----
        untrained_sims = {sname: float(atoms.similarity(untrained_probe, sense_vecs[("spoil", sname)]))
                          for sname in CANDIDATE_SENSES["spoil"]}

        # ---- arms-differ digest (META_RULE_AF): REAL vs SCRAMBLE predicted-sense sequence ----
        dig_real, seq_real = _predicted_seq_digest(word_maps_real, ctx_vecs, sense_vecs, TEST_ITEMS,
                                                     AMBIGUOUS_WORDS)
        dig_scr, seq_scr = _predicted_seq_digest(word_maps_scr, ctx_vecs, sense_vecs, TEST_ITEMS,
                                                   AMBIGUOUS_WORDS)

        # ---- Stage-1 grounded-affect witness (imported verbatim, not reimplemented) ----
        gen_theta = torch.Generator().manual_seed(seed)
        cb = stage1.sim.Codebook(gen_theta)
        g_theta = torch.Generator().manual_seed(seed * 100 + stage1.sim.hash_variant("FULL"))
        theta = stage1.sim.train_theta(cb, g_theta, "FULL", n_train_theta)
        v_pos = stage1.social_valence(cb, theta, "RECIPROCITY")
        v_neg = stage1.social_valence(cb, theta, "BLOCK_HIGH")

        return {
            "seed": seed,
            "acc_real": acc_real, "acc_scramble": acc_scramble, "acc_baseline": acc_baseline,
            "lift_over_scramble": acc_real - acc_scramble,
            "context_driven_rate": context_driven_rate, "baseline_stable": bool(baseline_stable),
            "divergence_detail": divergence_detail,
            "baseline_detail": {"pred_in": b_pred_in, "pred_an": b_pred_an},
            "digests": {"real": dig_real, "scramble": dig_scr},
            "arms_differ_real_vs_scramble": dig_real != dig_scr,
            "theta_witness": {"RECIPROCITY": v_pos, "BLOCK_HIGH": v_neg,
                              "signs_ok": (v_pos > 0) and (v_neg < 0)},
            "untrained_probe_sims": {k: round(v, 4) for k, v in untrained_sims.items()},
            "items_real": items_real, "items_scramble": items_scr, "items_baseline": items_baseline,
            "failure_class": None,
        }
    except Exception as e:
        return {"seed": seed, "failure_class": f"{type(e).__name__}: {str(e)[:300]}",
                "traceback": traceback.format_exc()[:3000]}


# ------------------------------------------------------------------------- verdict
def aggregate_and_verdict(per_seed: dict) -> dict:
    seeds = sorted(per_seed.keys())
    failed = [s for s in seeds if per_seed[s].get("failure_class")]
    ok_seeds = [s for s in seeds if not per_seed[s].get("failure_class")]

    def mean_key(key):
        vals = [float(per_seed[s][key]) for s in ok_seeds]
        return sum(vals) / max(1, len(vals))

    n = len(seeds)
    if n < EXPECTED_N_SEEDS or len(ok_seeds) < EXPECTED_N_SEEDS:
        return {
            "verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
            "verdict_msg": f"landed {n} seeds ({len(ok_seeds)} ok, {len(failed)} failed), "
                           f"expected {EXPECTED_N_SEEDS}",
            "summary": "cardinality breach", "n_seeds": n, "n_ok": len(ok_seeds), "failed_seeds": failed,
        }

    mean_real = mean_key("acc_real")
    mean_scramble = mean_key("acc_scramble")
    mean_baseline = mean_key("acc_baseline")
    mean_context_driven = mean_key("context_driven_rate")
    mean_baseline_stable = sum(1.0 for s in ok_seeds if per_seed[s]["baseline_stable"]) / len(ok_seeds)
    lift = mean_real - mean_scramble

    any_arms_identical = any(not per_seed[s]["arms_differ_real_vs_scramble"] for s in ok_seeds)

    open_pass = mean_real >= BAND_HELDOUT_PASS
    scramble_collapsed = (mean_scramble <= BAND_SCRAMBLE_MAX_FOR_COLLAPSE) and (lift >= BAND_MIN_LIFT_OVER_SCRAMBLE)
    context_pass = mean_context_driven >= BAND_CONTEXT_DRIVEN_MIN
    baseline_pass = (mean_baseline >= BAND_BASELINE_PASS) and (mean_baseline_stable >= BAND_BASELINE_STABLE_MIN)
    open_hard_fail = mean_real < BAND_HARD_FAIL_HELDOUT

    if any_arms_identical:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif open_pass and scramble_collapsed and context_pass and baseline_pass:
        verdict = "HARD_PASS"
    elif open_hard_fail or not scramble_collapsed or not context_pass:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    summary = (f"held_out_collapse(real)={mean_real:.3f} (band>={BAND_HELDOUT_PASS}) "
               f"scramble_acc={mean_scramble:.3f} (band<={BAND_SCRAMBLE_MAX_FOR_COLLAPSE}) "
               f"lift_over_scramble={lift:.3f} (band>={BAND_MIN_LIFT_OVER_SCRAMBLE}) "
               f"context_driven_rate={mean_context_driven:.3f} (band>={BAND_CONTEXT_DRIVEN_MIN}) "
               f"baseline_acc={mean_baseline:.3f} (band>={BAND_BASELINE_PASS}) "
               f"baseline_stable_rate={mean_baseline_stable:.3f} (band>={BAND_BASELINE_STABLE_MIN}) "
               f"n_test_ambiguous={N_TEST_AMBIGUOUS} n_test_baseline={N_TEST_BASELINE}")
    return {
        "verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
        "n_seeds": n, "n_ok": len(ok_seeds), "failed_seeds": failed,
        "means": {"acc_real": mean_real, "acc_scramble": mean_scramble, "lift_over_scramble": lift,
                  "context_driven_rate": mean_context_driven, "acc_baseline": mean_baseline,
                  "baseline_stable_rate": mean_baseline_stable},
        "bands": {"open_pass": open_pass, "scramble_collapsed": scramble_collapsed,
                  "context_pass": context_pass, "baseline_pass": baseline_pass,
                  "open_hard_fail": open_hard_fail, "any_arms_identical": any_arms_identical},
        "words": {"ambiguous": AMBIGUOUS_WORDS, "baseline": BASELINE_WORD, "menu": WORD_SENSE_MENU,
                  "sense_affect_type": SENSE_AFFECT_TYPE},
    }


# ------------------------------------------------------------------------- infra
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


def run(n_train_theta, run_mode):
    t0 = time.perf_counter()
    output_dir = out_dir_for(run_mode)
    _write_start_marker(output_dir, run_mode, EXPECTED_N_SEEDS)
    done = completed_units(output_dir)
    for seed in SEEDS:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} already done, skipping", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed, n_train_theta)
        record_unit(output_dir, k, res)
        if res.get("failure_class"):
            print(f"[FAIL] seed={seed} {res['failure_class']}", flush=True)
        else:
            print(f"[progress] seed={seed} done in {time.perf_counter()-ts:.1f}s "
                  f"real={res['acc_real']:.3f} scramble={res['acc_scramble']:.3f} "
                  f"context_driven={res['context_driven_rate']:.3f} baseline={res['acc_baseline']:.3f}",
                  flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(output_dir).values()}
    agg = aggregate_and_verdict(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"seeds": SEEDS, "n_train_theta": n_train_theta, "n_dim_word": N_DIM_WORD,
                      "n_test_ambiguous": N_TEST_AMBIGUOUS, "n_test_baseline": N_TEST_BASELINE,
                      "bands": {"heldout_pass": BAND_HELDOUT_PASS,
                                "scramble_max_for_collapse": BAND_SCRAMBLE_MAX_FOR_COLLAPSE,
                                "min_lift_over_scramble": BAND_MIN_LIFT_OVER_SCRAMBLE,
                                "context_driven_min": BAND_CONTEXT_DRIVEN_MIN,
                                "baseline_pass": BAND_BASELINE_PASS,
                                "baseline_stable_min": BAND_BASELINE_STABLE_MIN,
                                "hard_fail_heldout": BAND_HARD_FAIL_HELDOUT}}
    agg["per_seed"] = per_seed
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ------------------------------------------------------------------------- self-test
def self_test():
    """(1) menu composition: 5 ambiguous words with 2 candidates each, 1 baseline word with 1 candidate;
    (2) TRAIN/TEST noun pools disjoint per (word,class), already asserted at import time via build_items,
    reaffirmed here; (3) tiny end-to-end run at SMOKE_N_TRAIN_THETA: all 4 gates clear their pre-
    registered bands, arms pairwise differ (META_RULE_AF), theta witness sign convention holds."""
    # (1) menu composition
    for w in AMBIGUOUS_WORDS:
        assert len(CANDIDATE_SENSES[w]) == 2, f"{w}: expected 2 candidate senses, got {CANDIDATE_SENSES[w]}"
    assert len(CANDIDATE_SENSES[BASELINE_WORD]) == 1, (
        f"{BASELINE_WORD}: expected 1 candidate sense (single-sense baseline), got "
        f"{CANDIDATE_SENSES[BASELINE_WORD]}")
    assert len(AMBIGUOUS_WORDS) == 5 and len(ALL_WORDS) == 6

    # (2) TRAIN/TEST disjointness (reaffirm; build_items already asserted this at import time)
    for w in ALL_WORDS:
        for cls in ("inanimate", "animate"):
            train_n, test_n = NOUN_POOLS[w][cls]
            assert not (set(train_n) & set(test_n)), f"{w}/{cls}: TRAIN/TEST overlap"
    assert N_TEST_AMBIGUOUS == 20 and N_TEST_BASELINE == 4

    # (3) tiny end-to-end run
    res = run_seed(0, n_train_theta=SMOKE_N_TRAIN_THETA)
    assert res["failure_class"] is None, f"run_seed crashed: {res.get('failure_class')}"
    assert res["acc_real"] >= BAND_HELDOUT_PASS, (
        f"held-out collapse did not clear band: {res['acc_real']:.3f} < {BAND_HELDOUT_PASS}")
    assert res["acc_scramble"] <= BAND_SCRAMBLE_MAX_FOR_COLLAPSE, (
        f"scramble control did not collapse: {res['acc_scramble']:.3f} > {BAND_SCRAMBLE_MAX_FOR_COLLAPSE}")
    assert res["lift_over_scramble"] >= BAND_MIN_LIFT_OVER_SCRAMBLE, (
        f"lift over scramble too small: {res['lift_over_scramble']:.3f} < {BAND_MIN_LIFT_OVER_SCRAMBLE}")
    assert res["context_driven_rate"] >= BAND_CONTEXT_DRIVEN_MIN, (
        f"context-driven divergence did not clear band: {res['context_driven_rate']:.3f}")
    assert res["acc_baseline"] >= BAND_BASELINE_PASS, (
        f"single-sense baseline did not clear band: {res['acc_baseline']:.3f} < {BAND_BASELINE_PASS}")
    assert res["baseline_stable"], "single-sense baseline diverged across context (should be stable)"
    assert res["arms_differ_real_vs_scramble"], (
        f"META_RULE_AF: real/scramble predicted-sense digests identical: {res['digests']}")
    assert res["theta_witness"]["signs_ok"], (
        f"sign convention violated: {res['theta_witness']}")

    print(f"[SELFTEST PASS] real={res['acc_real']:.3f} scramble={res['acc_scramble']:.3f} "
          f"lift={res['lift_over_scramble']:.3f} context_driven={res['context_driven_rate']:.3f} "
          f"baseline={res['acc_baseline']:.3f} baseline_stable={res['baseline_stable']} "
          f"digests={res['digests']} theta_witness={res['theta_witness']}", flush=True)
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
        run(SMOKE_N_TRAIN_THETA, "smoke")
        raise SystemExit(0)
    run(FULL_N_TRAIN_THETA, "full")
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
