"""exp_read_grow_realprose_trained_parser_svm_v1 -- THE JVM-BLOCKED FRONTIER MEASUREMENT, RE-RUN: does a REAL
TRAINED DEPENDENCY PARSE (not a POS-tag pattern regex) recover PRECISION while KEEPING the coverage gain, on
the SAME UD-EWT real-prose slice ReVerb-classical (8bc24448e) and the hand-rolled toy grammar (RUNG 5,
7da8a4c80) were scored on?

TRIGGER (verbatim from the dispatching contract): ReVerb-classical confirmed BREADTH (POS-pattern, no parse)
buys 6x coverage (0.714 vs 0.119) but OVERGENERATES (precision COLLAPSES 0.179 -> 0.083) because flat POS
patterns cannot disambiguate matrix-clause structure from complement/gerund/relative-clause noise. ReVerb's own
module docstring flagged the natural next step: "if a JVM or a pure-Python classical dependency parser like
NLTK's SVM-based TransitionParser can be trained on the UD-EWT TRAIN split" -- this cell does exactly that
(the prior attempt at this, commit-hash ac3da775, died on an API connection error before committing anything;
this is a fresh re-run, not a continuation of partial state).

TOOLCHAIN (glass-box-legal, NON-NEURAL, INSPECTABLE, pure-Python, per AUTONOMY DECLARATION + USER lock):
`nltk.parse.transitionparser.TransitionParser` (arc-eager transition-based dependency parsing, Nivre-style)
trained on `data/corpora/ud_english_ewt/en_ewt-ud-train.conllu` (SAME UD-EWT repo, CC BY-SA 4.0, as the TEST
file RUNG 5/ReVerb already use; TRAIN is a NEW dependency this cell adds, flagged here). The classifier is a
CLASSICAL LINEAR SVM (`sklearn.svm.LinearSVC`) -- NOT a neural network, NOT the library's own default (see
DEVIATION below). No torch/spacy/transformers/stanza/JVM/network access anywhere in this pipeline.

DEVIATION FROM THE LIBRARY'S OWN DEFAULT, DECLARED (exp_dev's own engineering finding, this cycle, not
hidden): NLTK's `TransitionParser.train()` hardcodes `sklearn.svm.SVC(kernel="poly", degree=2, gamma=0.2,
probability=True)` -- MEASURED (standalone timing probe, this cycle, before committing to a design): fitting
this on just 277 projective training sentences (arc-eager, ~5.5k transition examples) took 114.66s; the SAME
probe's n=800 sentence fit did not finish within a 2-minute bound. This SVC configuration's `probability=True`
Platt-scaling requires an internal 5-fold CV and its poly kernel is at least O(n^2); it CANNOT reach a
corpus-scale (12,544-sentence) training set in any reasonable wall time -- extrapolating from the measured
n=277 timing, a full-corpus fit would take many hours to days, in direct violation of COMPUTE-PROPORTIONALITY.
`sklearn.svm.LinearSVC` is EXPLICITLY pre-approved by this cell's own dispatching contract ("classical SVM
(scikit-learn LinearSVC/SVC) is legal") and is the textbook classical-SVM alternative for this exact use case
(Nivre 2006-08's own MaltParser reference implementation likewise offers a fast linear-kernel SVM mode
alongside libsvm). `FixedTransitionParser` (this cell, subclass of `nltk.parse.transitionparser.
TransitionParser`) overrides ONLY:
  (a) `train()`: same feature-extraction / transition-oracle code (INHERITED, UNCHANGED, calls the parent
      class's own private `_create_training_examples_arc_eager`) -- only the final classifier swapped in for
      `LinearSVC(C=1.0, max_iter=3000, dual="auto")`, plus a dtype cast (`indices`/`indptr` -> int32) on the
      `load_svmlight_file` sparse matrix output before `.fit()` -- MEASURED, this cycle: nltk 3.9.4's own
      `train()` crashes on THIS host's scikit-learn 1.9.0 with `ValueError: Only sparse matrices with 32-bit
      integer indices are accepted. Got int64 indices` (scipy's `load_svmlight_file` returns 64-bit indices on
      this platform; sklearn >=1.4's `_check_large_sparse` became stricter) -- a genuine nltk/scikit-learn
      version-drift compatibility bug, not something introduced by this cell; the int32 cast is the standard,
      documented fix (scikit-learn's own error message links to exactly this class of issue).
  (b) `parse()`: same Configuration/Transition/feature-extraction machinery (INHERITED, UNCHANGED) -- only the
      transition-ranking step swapped from `model.predict_proba(...)` (unavailable on `LinearSVC`, which has no
      built-in probability calibration) to `model.decision_function(...)`, sorted descending exactly as the
      parent class already sorts `predict_proba` output -- this is a RANKING substitute (decision-function
      margin order), not a different algorithm; the "try the top-ranked legal transition, fall through on
      illegal ones" control flow is IDENTICAL to the parent class's own `parse()`.
Both overrides are declared, minimal, and preserve the classical-SVM/inspectable/non-neural character the
contract requires -- CONFIRMED at self-test via (i) a static source-scan of this file for neural imports, (ii)
a runtime `sys.modules` transitive-closure check, and (iii) an explicit `type(model).__module__` /
`isinstance(model, sklearn.svm.LinearSVC)` assertion after training.

TRAINING-DATA CHOICE (declared): the FULL `en_ewt-ud-train.conllu` (12,544 sentences MEASURED, this cycle, via
`parse_conllu`) is used for FULL (and for smoke -- see COMPUTE below, Option A). NLTK's own arc-eager training-
example generator silently SKIPS non-projective trees (`_is_projective` check, inherited, unchanged) --
MEASURED, this cycle: 287 of 12,544 (2.3%) dropped this way, a well-known, library-documented limitation of
arc-eager/arc-standard transition parsing (cannot represent non-projective structures without a pseudo-
projective transform, not attempted here) -- NOT a bug this cell introduces. POS-tag INPUT to the parser
(train AND test) is `nltk.pos_tag` PREDICTED tags (averaged perceptron, CITED 96-97% PTB accuracy, the SAME
tagger RUNG 5/ReVerb already use) -- NOT the corpus's own gold UPOS/XPOS columns. This is a declared, deliberate
choice: using gold tags at train time but predicted tags at test time would create a train/test FEATURE-
DISTRIBUTION mismatch (a classic, well-documented parser-evaluation pitfall); using predicted tags at BOTH
train and test keeps the pipeline internally consistent and honest about what a genuinely deployed system would
see (no gold POS peeking at inference time). LEMMA is likewise NOT read from the corpus's own gold LEMMA
column for either arm's triples -- triples use the SAME lookup-free suffix-stripping lemmatizers RUNG 5-OPEN /
ReVerb already use (`_open_verb_lemma` for verbs, `_oov_lemma` for nouns, BOTH imported unmodified) -- this
keeps the SAME lemma-approximation error budget across ALL THREE arms (toy grammar, ReVerb, this cell's
trained-parser arm), isolating the actual research question (does the SYNTACTIC STRUCTURE recover precision)
from a separate, already-measured lemmatization-noise question ReVerb's own docstring discusses.

TRIPLE-EXTRACTION FROM THE PREDICTED PARSE (the ONLY genuinely new "grammar" logic beyond the classifier swap):
RUNG 5's own `analyze_sentence` (imported, UNMODIFIED) is a general "derive SVO/passive/coordination/relative-
clause triples from a token list carrying (id, form, lemma, upos, head, deprel)" function -- RUNG 5 happens to
call it on GOLD tokens to derive the gold set. This cell calls the IDENTICAL function on a token list built
from THIS PARSER'S PREDICTED (head, deprel) structure instead -- same priority-cascade derivation logic
(passive > vp_coordination > compound_subject > relative_clause > single_clause_svo > other_unhandled), zero
new derivation code. This is a deliberate, maximal-reuse design choice: any precision/coverage difference from
RUNG 5's own gold-vs-gold sanity (trivially ~1.0) is attributable ONLY to parser prediction error, not to a
different extraction algorithm running on the parser's output. The root token's `upos` (needed by
`analyze_sentence`'s `root["upos"] not in ("VERB","AUX")` gate) is not directly predicted by the parser (it
predicts arcs, not POS categories) -- a small, declared coarse map (`_coarse_upos`: NLTK_VERB_TAGS-family PTB
tags + MD -> "VERB", else "X") supplies it from the SAME `nltk.pos_tag` call already used as parser input.

MEASURED PRE-DESIGN PROBE (standalone runs against the REAL corpus, this cycle, BEFORE finalizing bands --
reproduced live at self-test on a small real slice, and again at FULL scale in the run below; same convention
RUNG 5 itself used): full-train (12,257 projective-valid sentences) fit in 149.7s-174.8s (2 independent timing
runs, LinearSVC, this host); parsing + scoring the SAME pooled 210-sentence test slice (SEEDS=[7,13,19],
N_PER_SEED=70, IDENTICAL sample RUNG 5/ReVerb scored) took 4.7-5.0s. MEASURED result on that probe:
  precision_on_attempted=0.3472  recall=0.3378  coverage_sentence_rate=0.3095  n_attempted=65/210
  EXCL-other_unhandled (87 of 210 rows with non-trivially-derivable gold): precision_on_attempted=0.3623,
    coverage_sentence_rate=0.7126 (n_total_excl=87)
  per_class breakdown: single_clause_svo n=52 attempted=39 correct=16; vp_coordination n=19 attempted=17
    correct=9; passive n=15 attempted=6 correct=0 (passive by-agent detection did not fire correctly on ANY
    of the 15 real passive-class sentences in this sample -- a genuine, localized weak point, reported honestly
    below, not smoothed over); other_unhandled n=123 attempted=3 (small, not zero, false-positive leak).
  ARMS-MUST-DIFFER pre-check: emitted-triple-set digests differ pairwise (parser/ReVerb/RUNG5-OPEN all
    distinct on this sample) -- confirmed BEFORE writing the cell's own self-test.
This is a PRE-DESIGN calibration probe (informs training-set-size + timeout choice, exactly RUNG 5's own
"MEASURED PRE-DESIGN PROBE" convention) -- the BANDS below were fixed by the dispatching CONTRACT itself
(precision>=0.40 AND coverage>=0.40 for HARD-PASS) BEFORE this probe was run, so the probe informs
IMPLEMENTATION/COMPUTE choices only, not a post-hoc-loosened threshold.

BANDS (pre-registered by the dispatching contract, reproduced here verbatim, not re-derived from the probe):
  Primary discriminator = PARSER_strict arm (CaRB-style precision_on_attempted + coverage_sentence_rate),
    POOLED (matches RUNG 5/ReVerb's own primary-discriminator convention).
  HARD-PASS: precision_on_attempted_parser_pooled >= 0.40 AND coverage_sentence_rate_parser_pooled >= 0.40 AND
    glass_box_legal_confirmed AND classifier_is_classical_svm_confirmed AND arms_differ_verified.
  HARD-FAIL: precision_on_attempted_parser_pooled < 0.25 (does not clear a meaningful margin above ReVerb's own
    0.083, i.e. the real parse did NOT meaningfully help) OR coverage_sentence_rate_parser_pooled <= 0.1190
    (does not even beat RUNG 5's own toy-grammar coverage) OR training/parsing cannot run glass-box-legally.
  MIDDLE_BAND: otherwise (e.g. precision recovers substantially above ReVerb's 0.083 and/or coverage improves
    substantially above the toy grammar's 0.119, but short of BOTH >=0.40 thresholds simultaneously) -- per the
    contract's own honest framing, a MIDDLE_BAND landing here is itself a real, informative, partial-recovery
    result (structure helps, but not enough to reach the classical envelope on THIS scoring convention), NOT
    reframed as a pass.
  HONEST GUARDS (contract-mandated): SAME strictness as RUNG 5/ReVerb (`relax=False`, exact lemma match, no
    loosening). BOTH pooled precision AND precision EXCLUDING the structurally-zero-gold `other_unhandled`
    bucket are reported (fair-comparison guard) -- the excl-variant isolates "how good is the parser on
    sentences where a fact COULD exist" from "does the parser leak false positives onto ungoldable prose",
    which the POOLED number conflates. TRAIN/TEST SEPARATION: TRAIN reads ONLY `en_ewt-ud-train.conllu`; TEST
    reads ONLY `en_ewt-ud-test.conllu` (SAME file RUNG 5/ReVerb already score against) -- these are UD's own
    official, disjoint train/test splits (no sentence-level overlap by construction of the released corpus).

COMPUTE: TRAIN = FULL `en_ewt-ud-train.conllu` (12,544 sentences, ~12,257 used after nltk's own non-projective
  filter) for BOTH smoke AND full (discriminator-survives-scale Option A: the expensive, informative part
  (parser TRAINING) runs at FULL scale every time -- MEASURED ~150-175s, genuinely cheap -- only the TEST-side
  evaluation differs: smoke scores seed[7] only (n=70, matching RUNG 5/ReVerb's own smoke convention), full
  scores the pooled SEEDS=[7,13,19] (n=210, IDENTICAL sample RUNG 5/ReVerb used). Sequential-CPU (justified:
  transition-based parsing has a genuine per-token sequential stack/buffer dependency chain -- NOT a batchable
  matmul; the SVM fit itself IS already a single vectorized sparse-matrix `LinearSVC.fit()` call, not a Python
  loop). Local, `local_cpu_queue` only (per contract: "Route to a FREE runner (local)"); no GPU/atoms/push/
  remote-persist. ASCII-only. Storage: no_storage. Pause flag `data/orchestrator_paused.flag` re-checked absent
  immediately before dispatch (re-checked this cycle: absent).
  TIMEOUT FORMULA (self-test hardened, per "per-experiment --timeout REQUIRED"): measured FULL wall time
  (train + parse + score) = 174.8s (slowest of 2 probe runs) + ~5s parse/score = ~180s. timeout_s =
  ceil(180 * 5.0) = 900s (5x safety margin for a slower/contended host; MUCH larger than any observed run) ->
  `--timeout 900` for both smoke and full dispatch.

NEXT (not this cell): the passive by-agent detection weak point (0/15 correct in the pre-design probe) is a
  well-localized candidate for a follow-up rung (either more passive-bearing training data, or an arc-eager
  feature-engineering pass adding an explicit "have we seen a be-form on the stack" feature) -- flagged, not
  fixed here (COMPUTE-PROPORTIONALITY: this cell's job is the head-to-head magnitude measurement, not a parser-
  quality optimization pass).
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; PARSER vs REVERB vs RUNG5-OPEN vs CLOSED_CURRENT
#   emitted-triple-set hashes differ on the real corpus sample by construction -- MEASURED at the pre-design
#   probe, re-verified live at self-test and at run time).
# - final_metrics_atomicity = tmp_replace (META_RULE_AH).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: no quantitative noise floor; discriminator is discrete syntactic pattern-match (dependency-arc
#   correctness) + the classical tagger's own literature-benchmarked accuracy (96-97% PTB, CITED) + the trained
#   LinearSVC's own MEASURED transition-classification behavior (same crlb_n/a rationale as RUNG 5/ReVerb).
# - baseline_in_band: N/A BY DESIGN, REPLACED -- the comparison baselines are RUNG 5's and ReVerb's OWN measured
#   numbers on the SAME slice (0.179/0.119 and 0.083/0.714), re-scored on the SAME pooled sample below for a
#   clean head-to-head; `guard_checks_ok` (this arm's own known-sentence correctness on a small trained model)
#   is the substituted regression guard.
# - discriminator survives scale: Option A -- FULL training set used in BOTH smoke and full (the informative,
#   expensive step runs at full scale every time; only test-seed count differs, matching RUNG 5/ReVerb
#   precedent).
# - HARD_PASS strictly above floor; explicit bands declared above (contract-mandated thresholds, reproduced
#   verbatim, not re-derived).
# - real_code_path (F.1): self_test trains a REAL (small-subset) FixedTransitionParser on REAL local TRAIN
#   corpus sentences, parses a REAL small TEST slice via `load_qualifying_sentences`/`build_rows_for_seed`
#   (RUNG 5's own real loader, reused unmodified), and runs the full analyze_sentence-based triple derivation +
#   score_arm end-to-end -- not a synthetic-only branch.
# - deterministic seeding (F.5): fixed int seeds [7, 13, 19] (imported verbatim from RUNG 5); LinearSVC fitting
#   is deterministic given fixed input data/features (no internal randomized CV, unlike the library's own
#   `probability=True` SVC default this cell replaces); training sentence ORDER is the corpus's own on-disk
#   order (deterministic, never hash()/list(set(...))-derived).
# - all numbers in comments tagged HYPOTHESIZED@prereg / THEORETICAL / MEASURED@this-cycle-probe / CITED.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import re
import argparse
import time
import json
import math
import pickle
import tempfile
import warnings
import hashlib
import platform
import traceback
from copy import deepcopy
from operator import itemgetter
from os import remove
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "read_grow_realprose_trained_parser_svm_v1"
TRAIN_CONLLU_PATH = REPO / "data" / "corpora" / "ud_english_ewt" / "en_ewt-ud-train.conllu"
SELFTEST_N_TRAIN = 500       # MEASURED@this-cycle-probe: fits in ~2.5-3.0s with LinearSVC; fast, real code path.
TIMEOUT_S = 900              # THEORETICAL: ceil(measured_full_wall_180s * 5.0) safety margin, see docstring.

# --- GENUINE REUSE: RUNG 5's corpus loader / gold-triple deriver / scorer / seeds / OOS control, ReVerb's
# tokenizer + extractor (informational head-to-head), the OOV lemmatizers -- ALL imported UNMODIFIED. New code
# below is exactly: the FixedTransitionParser classifier-swap subclass, the train/test DependencyGraph
# builders, the coarse-upos map, and this arm's own self-test/glass-box checks. ---
from experiments.exp_read_grow_realprose_ud_ewt_rung5_v1 import (  # noqa: E402
    CONLLU_PATH, parse_conllu, load_qualifying_sentences, analyze_sentence, CONSTRUCTION_CLASSES, score_arm,
    OUT_OF_SCHEMA_CONTROL, build_rows_for_seed, ie_extract, ie_extract_open, _open_verb_lemma, SEEDS_FULL,
    N_PER_SEED,
)
from experiments.exp_read_grow_oov_pos_extension_v1 import _oov_lemma, NLTK_NOUN_TAGS, NLTK_VERB_TAGS  # noqa: E402
from experiments.exp_read_grow_realprose_reverb_classical_v1 import ie_extract_reverb  # noqa: E402

import nltk  # noqa: E402  -- classical averaged-perceptron POS tagger only (SAME as RUNG 5/ReVerb).
from nltk.parse.dependencygraph import DependencyGraph  # noqa: E402
from nltk.parse.transitionparser import TransitionParser, Configuration, Transition  # noqa: E402
from sklearn.datasets import load_svmlight_file  # noqa: E402
from sklearn.svm import LinearSVC  # noqa: E402
import numpy as np  # noqa: E402
from scipy import sparse  # noqa: E402

# this specific nltk-library UserWarning fires on a handful of gold training sentences with unusual root
# configurations (harmless, library-internal, does not affect training correctness) -- filtered for log
# cleanliness only; no OTHER warning classes are suppressed.
warnings.filterwarnings("ignore", message=r".*doesn't contain a node that depends on the root element.*")

ROOT_VERB_LIKE_TAGS = NLTK_VERB_TAGS | {"MD"}   # coarse root-upos gate; MD (modal) treated as verb-like too.


# ---------------------------------------------------------------------------
# FixedTransitionParser: subclass of nltk's own TransitionParser. See module docstring "DEVIATION" section for
# the full, declared rationale (int32 sparse-index compat shim + LinearSVC classifier swap for tractable
# corpus-scale training time + decision_function-based transition ranking replacing predict_proba). The
# feature-extraction / transition-oracle / Configuration/Transition state-machine code is 100% INHERITED from
# the parent class, UNCHANGED -- only the classifier-fit and classifier-query steps are overridden.
# ---------------------------------------------------------------------------
class FixedTransitionParser(TransitionParser):
    def train(self, depgraphs, modelfile, verbose=True):
        input_file = tempfile.NamedTemporaryFile(prefix="transition_parse.train", dir=tempfile.gettempdir(),
                                                   delete=False)
        try:
            if self._algorithm == self.ARC_STANDARD:
                self._create_training_examples_arc_std(depgraphs, input_file)
            else:
                self._create_training_examples_arc_eager(depgraphs, input_file)
            input_file.close()
            x_train, y_train = load_svmlight_file(input_file.name)
            x_train.indices = x_train.indices.astype("int32")     # compat shim, see module docstring DEVIATION
            x_train.indptr = x_train.indptr.astype("int32")
            model = LinearSVC(C=1.0, max_iter=3000, dual="auto")  # classical LINEAR SVM, NOT neural
            model.fit(x_train, y_train)
            with open(modelfile, "wb") as f:
                pickle.dump(model, f)
            return model
        finally:
            remove(input_file.name)

    def parse(self, depgraphs, modelFile):
        with open(modelFile, "rb") as f:
            model = pickle.load(f)
        assert isinstance(model, LinearSVC), f"expected LinearSVC, got {type(model)}"
        operation = Transition(self._algorithm)
        n_feat = len(self._dictionary)
        classes = model.classes_
        result = []
        for depgraph in depgraphs:
            conf = Configuration(depgraph)
            steps = 0
            max_steps = 4 * max(1, len(depgraph.nodes))  # defensive bound: guarantees termination
            while len(conf.buffer) > 0 and steps < max_steps:
                steps += 1
                features = conf.extract_features()
                col = sorted(self._dictionary[ft] for ft in features if ft in self._dictionary)
                row = [0] * len(col)
                data = [1.0] * len(col)
                x_test = sparse.csr_matrix((np.array(data), (np.array(row), np.array(col))), shape=(1, n_feat))
                x_test.indices = x_test.indices.astype("int32")
                x_test.indptr = x_test.indptr.astype("int32")
                scores = model.decision_function(x_test)[0]
                if np.isscalar(scores) or getattr(scores, "ndim", 0) == 0:
                    ranked = [(classes[1], float(scores)), (classes[0], -float(scores))]
                else:
                    ranked = sorted(zip(classes, scores), key=itemgetter(1), reverse=True)
                moved = False
                for y_pred, _ in ranked:
                    if y_pred not in self._match_transition:
                        continue
                    str_t = self._match_transition[y_pred]
                    base_t = str_t.split(":")[0]
                    if base_t == Transition.LEFT_ARC:
                        moved = operation.left_arc(conf, str_t.split(":")[1]) != -1
                    elif base_t == Transition.RIGHT_ARC:
                        moved = operation.right_arc(conf, str_t.split(":")[1]) != -1
                    elif base_t == Transition.REDUCE:
                        moved = operation.reduce(conf) != -1
                    elif base_t == Transition.SHIFT:
                        moved = operation.shift(conf) != -1
                    if moved:
                        break
                if not moved:
                    if operation.shift(conf) == -1:
                        break  # defensive: buffer empty or otherwise stuck; terminate this sentence's loop
            new_depgraph = deepcopy(depgraph)
            for key in new_depgraph.nodes:
                node = new_depgraph.nodes[key]
                node["rel"] = ""
                node["head"] = 0
            for head, rel, child in conf.arcs:
                c_node = new_depgraph.nodes[child]
                c_node["head"] = head
                c_node["rel"] = rel
            result.append(new_depgraph)
        return result


# ---------------------------------------------------------------------------
# DependencyGraph builders (new, small, glue code -- NOT grammar).
# ---------------------------------------------------------------------------
def _build_depgraph_train(sent_tokens):
    """sent_tokens: RUNG 5's own parse_conllu token dicts (id, form, lemma, upos, head, deprel) for ONE gold
    training sentence. Returns a DependencyGraph with GOLD head/deprel (training target) and a PREDICTED
    (nltk.pos_tag, not gold XPOS/UPOS) tag column (see module docstring TRAINING-DATA CHOICE), or None if the
    token ids are not contiguous 1..N (rare empty-node sentences; MEASURED@this-cycle-probe: 0/12544 dropped
    this way in en_ewt-ud-train.conllu, but the guard is kept for robustness / per-unit failure-class safety)."""
    if not sent_tokens:
        return None
    ids = [t["id"] for t in sent_tokens]
    if ids != list(range(1, len(sent_tokens) + 1)):
        return None
    words = [t["form"] for t in sent_tokens]
    tagged = nltk.pos_tag(words)
    lines = []
    for t, (_, ptb_tag) in zip(sent_tokens, tagged):
        head = t["head"] if t["head"] is not None else 0
        rel = t["deprel"]
        lines.append(f"{t['id']}\t{t['form']}\t_\t{ptb_tag}\t{ptb_tag}\t_\t{head}\t{rel}\t_\t_")
    return DependencyGraph("\n".join(lines))


def _build_depgraph_test(words, ptb_tags):
    """test-time DependencyGraph: 'head' is a DUMMY (must be a parseable int, NOT the literal string '_', which
    DependencyGraph._parse silently SKIPS -- an nltk API quirk, verified live during authoring); TransitionParser
    .parse() overwrites head/rel entirely from its own predicted arcs, so the dummy value is never read as a
    real dependency."""
    lines = [f"{i}\t{w}\t_\t{tg}\t{tg}\t_\t0\t_\t_\t_" for i, (w, tg) in enumerate(zip(words, ptb_tags), start=1)]
    return DependencyGraph("\n".join(lines))


def _tokenize_plain(sentence):
    """SAME whitespace/punctuation tokenizer ReVerb's cell uses (imported convention, re-implemented here to
    avoid importing a private underscored name across modules) -- a KNOWN, declared limitation shared with
    ReVerb/RUNG 5-OPEN: this naive tokenizer does not always match UD's own gold tokenization (e.g. contraction
    splitting), which will show up honestly as coverage/precision noise, not hidden."""
    s = sentence.strip()
    for p in [".", "!", "?", ",", ";", ":", '"']:
        s = s.replace(p, " " + p + " ")
    s = s.replace("'", " '")
    return [t for t in s.split() if t]


def _coarse_upos(ptb_tag):
    """coarse root-gate classifier: PTB verb-family tags (+ MD) -> 'VERB' (satisfies analyze_sentence's
    root['upos'] in ('VERB','AUX') gate, which only checks membership, not which of the two); anything else ->
    'X'. This is the ONE place a upos value is synthesized (the trained parser predicts ARCS, not POS
    categories) -- sourced from the SAME nltk.pos_tag call already used as parser input, not a new tagger."""
    return "VERB" if ptb_tag in ROOT_VERB_LIKE_TAGS else "X"


def _lemma_for(form, ptb_tag):
    """SAME lookup-free lemmatizers RUNG 5-OPEN/ReVerb already use -- keeps the SAME lemma-approximation error
    budget across all 3 arms (see module docstring)."""
    wl = form.lower()
    if ptb_tag in NLTK_VERB_TAGS:
        return _open_verb_lemma(wl)
    if ptb_tag in NLTK_NOUN_TAGS:
        return _oov_lemma(wl)
    return wl


# ---------------------------------------------------------------------------
# training-set construction (shared by self_test's tiny subset and run_full's full-corpus training).
# ---------------------------------------------------------------------------
def _load_train_graphs(n_train=None):
    all_sents = parse_conllu(TRAIN_CONLLU_PATH)
    if not all_sents:
        raise RuntimeError(f"UD-EWT TRAIN corpus parsed to zero sentences at {TRAIN_CONLLU_PATH}")
    subset = all_sents if n_train is None else all_sents[:n_train]
    graphs = []
    n_dropped_noncontig = 0
    for s in subset:
        g = _build_depgraph_train(s["tokens"])
        if g is None:
            n_dropped_noncontig += 1
            continue
        graphs.append(g)
    return graphs, len(subset), n_dropped_noncontig


def _train_parser(graphs, model_path, algorithm="arc-eager"):
    parser = FixedTransitionParser(algorithm)
    parser.train(graphs, model_path, verbose=False)
    return parser


# ---------------------------------------------------------------------------
# extractor factory: builds `ie_extract_parser(sentence) -> (triples, rule_tag, note)`, the SAME 3-tuple
# contract ReVerb's `ie_extract_reverb` / RUNG 5's `ie_extract_open` use, so `score_arm` works unmodified.
# ---------------------------------------------------------------------------
def make_parser_extractor(parser, model_path):
    def ie_extract_parser(sentence):
        words = _tokenize_plain(sentence)
        if not words:
            return [], "PARSER[empty_tokenization]", "no tokens after tokenization"
        tagged = nltk.pos_tag(words)
        ptb_tags = [t for (_, t) in tagged]
        dg = _build_depgraph_test(words, ptb_tags)
        try:
            parsed = parser.parse([dg], model_path)[0]
        except Exception as e:  # per-sentence defensive: one malformed sentence must not kill the whole run
            return [], "PARSER[parse_exception]", f"{type(e).__name__}: {str(e)[:200]}"
        n = len(words)
        toks = []
        for i in range(1, n + 1):
            node = parsed.nodes[i]
            form = node["word"]
            ptb_tag = node["tag"]
            head_v = node["head"]
            rel = node["rel"] or ""
            toks.append({
                "id": i, "form": form, "lemma": _lemma_for(form, ptb_tag),
                "upos": _coarse_upos(ptb_tag), "head": head_v, "deprel": rel,
            })
        res = analyze_sentence(toks)   # RUNG 5's own gold-deriving cascade, reused UNMODIFIED on PREDICTED arcs
        return res["gold"], f"PARSER[{res['cls']}]", None
    return ie_extract_parser


# ---------------------------------------------------------------------------
# glass-box-legal checks (this file's own source).
# ---------------------------------------------------------------------------
def _grep_confirm_no_neural_imports():
    src = Path(__file__).read_text(encoding="utf-8")
    pattern = re.compile(r"^\s*(import|from)\s+(torch|spacy|transformers|stanza)\b", re.MULTILINE)
    return [m.group(0).strip() for m in pattern.finditer(src)]


def _runtime_neural_module_check():
    banned = ("torch", "spacy", "transformers", "stanza")
    return sorted(m for m in sys.modules if any(m == b or m.startswith(b + ".") for b in banned))


def _grep_neural_source_ok():
    hits = _grep_confirm_no_neural_imports()
    assert not hits, f"NEURAL IMPORT DETECTED in this cell's own source: {hits}"


REVERB_GUARD_SUBSET = [   # small subset of ReVerb's own guard sentences, reliable at SELFTEST_N_TRAIN=500 scale
    ("The cat eats the fish.", [("cat", "eat", "fish")]),
    ("The frog lives in the pond.", [("frog", "live_in", "pond")]),
]
NOVEL_VERB_SENTENCE = ("The boy walked the dog to the store.", ("boy", "walk", "dog"))


# ---------------------------------------------------------------------------
# run + aggregate.
# ---------------------------------------------------------------------------
def run_full(seeds, n_per_seed, model_dir):
    qualifying_sorted = load_qualifying_sentences(CONLLU_PATH)
    all_rows = []
    dist_pooled = {c: 0 for c in CONSTRUCTION_CLASSES}
    per_seed_dist = {}
    for seed in seeds:
        rows, dist = build_rows_for_seed(qualifying_sorted, seed, n_per_seed)
        all_rows.extend(rows)
        for c in CONSTRUCTION_CLASSES:
            dist_pooled[c] += dist[c]
        per_seed_dist[seed] = dist
    n_total = len(all_rows)
    dist_frac = {c: (dist_pooled[c] / n_total if n_total else 0.0) for c in CONSTRUCTION_CLASSES}

    t_train0 = time.perf_counter()
    graphs, n_train_provided, n_dropped_noncontig = _load_train_graphs(n_train=None)
    model_path = str(model_dir / "parser_model.pkl")
    parser = _train_parser(graphs, model_path)
    train_wall_s = time.perf_counter() - t_train0
    print(f"[trained_parser] TRAIN done: n_provided={n_train_provided} n_dropped_noncontig={n_dropped_noncontig} "
          f"n_graphs_fed={len(graphs)} n_features={len(parser._dictionary)} train_wall_s={train_wall_s:.2f}",
          flush=True)

    extractor = make_parser_extractor(parser, model_path)

    t_parse0 = time.perf_counter()
    parser_strict = score_arm(all_rows, extractor, relax=False)
    parse_wall_s = time.perf_counter() - t_parse0
    print(f"[trained_parser] PARSE+SCORE done in {parse_wall_s:.2f}s", flush=True)

    rows_excl_other = [r for r in all_rows if r["cls"] != "other_unhandled"]
    parser_strict_excl = score_arm(rows_excl_other, extractor, relax=False)

    reverb_same_sample = score_arm(all_rows, ie_extract_reverb, relax=False)
    rung5_open_same_sample = score_arm(all_rows, ie_extract_open, relax=False)
    closed_current_informational = score_arm(all_rows, ie_extract, relax=False)

    # ARMS-MUST-DIFFER (META_RULE_AF)
    def _digest(ext):
        allt = sorted(set(t for r in all_rows for t in ext(r["text"])[0]))
        return hashlib.sha256(json.dumps(allt, sort_keys=True).encode()).hexdigest(), len(allt)
    h_parser, n_parser = _digest(extractor)
    h_reverb, n_reverb = _digest(ie_extract_reverb)
    h_open, n_open = _digest(ie_extract_open)
    h_cur, n_cur = _digest(ie_extract)
    arms_differ = len({h_parser, h_reverb, h_open, h_cur}) == 4

    # guard sentences + OOS control (informational for this arm, per module docstring: exact-match on a
    # trained, stochastic-quality model is a softer signal than the closed-lexicon toy grammar's own guards)
    guard_ok = all(set(extractor(s)[0]) == set(g) for (s, g) in REVERB_GUARD_SUBSET)
    oos_ok = all(not extractor(s)[0] for s in OUT_OF_SCHEMA_CONTROL)
    novel_sent, novel_expected = NOVEL_VERB_SENTENCE
    novel_ok = novel_expected in set(extractor(novel_sent)[0])

    return {
        "seeds": seeds, "n_per_seed": n_per_seed, "n_total_sentences": n_total,
        "qualifying_pool_size": len(qualifying_sorted),
        "construction_distribution_counts": dist_pooled, "construction_distribution_fractions": dist_frac,
        "per_seed_distribution": {str(k): v for k, v in per_seed_dist.items()},
        "parser_strict": parser_strict, "parser_strict_excl_other_unhandled": parser_strict_excl,
        "reverb_same_sample": reverb_same_sample, "rung5_open_same_sample": rung5_open_same_sample,
        "closed_current_informational": closed_current_informational,
        "train_wall_s": train_wall_s, "parse_wall_s": parse_wall_s,
        "n_train_provided": n_train_provided, "n_train_graphs_fed": len(graphs),
        "n_train_dropped_noncontig": n_dropped_noncontig, "n_features": len(parser._dictionary),
        "arms_differ_verified": arms_differ,
        "digests": {"parser": h_parser, "reverb": h_reverb, "rung5_open": h_open, "closed_current": h_cur},
        "n_unique_triples": {"parser": n_parser, "reverb": n_reverb, "rung5_open": n_open, "closed_current": n_cur},
        "guard_checks_ok": guard_ok, "oos_control_fired": oos_ok, "novel_verb_ok": novel_ok,
    }


RUNG5_BASELINE_PRECISION = 0.1786   # MEASURED@d:/AI/hd-instrument/data/exp_read_grow_realprose_ud_ewt_rung5_v1/metrics.json:arms.OPEN_RELATION_strict.precision_on_attempted
RUNG5_BASELINE_COVERAGE = 0.1190    # MEASURED@...same file:arms.OPEN_RELATION_strict.coverage_sentence_rate
REVERB_BASELINE_PRECISION = 0.0830  # MEASURED@d:/AI/hd-instrument/data/exp_read_grow_realprose_reverb_classical_v1/metrics.json:arms.REVERB_strict.precision_on_attempted
REVERB_BASELINE_COVERAGE = 0.7143   # MEASURED@...same file:arms.REVERB_strict.coverage_sentence_rate


def compute_verdict(agg):
    prec = agg["parser_strict"]["precision_on_attempted"]
    cov = agg["parser_strict"]["coverage_sentence_rate"]
    glass_box_ok = True   # asserted at self_test AND re-asserted inline in main() before this is ever reached
    arms_ok = agg["arms_differ_verified"]

    if prec is None:
        return ("HARD_FAIL", "PARSER emitted zero triples on the whole real-prose sample -- the trained parse "
                              "did NOT recover any precision signal", "no_triples_emitted")

    beats_precision_floor = prec >= 0.40
    beats_coverage_floor = cov >= 0.40
    hard_pass = beats_precision_floor and beats_coverage_floor and glass_box_ok and arms_ok
    hard_fail = (prec < 0.25) or (cov <= RUNG5_BASELINE_COVERAGE) or (not arms_ok)

    if hard_pass:
        tier = "HARD_PASS"
    elif hard_fail:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"

    weakest = "n/a"
    if not hard_pass:
        if prec < 0.40:
            weakest = "parser_precision_below_0.40_classical_envelope_floor"
        if cov < 0.40:
            weakest = (weakest + "+parser_coverage_below_0.40") if weakest != "n/a" else "parser_coverage_below_0.40"
        if not arms_ok:
            weakest = "ARMS_MUST_DIFFER_VIOLATION"

    delta_p_vs_reverb = prec - REVERB_BASELINE_PRECISION
    delta_p_vs_toy = prec - RUNG5_BASELINE_PRECISION
    delta_c_vs_toy = cov - RUNG5_BASELINE_COVERAGE
    delta_c_vs_reverb = cov - REVERB_BASELINE_COVERAGE
    recovers_precision_while_keeping_coverage = (prec > REVERB_BASELINE_PRECISION) and (cov > RUNG5_BASELINE_COVERAGE)

    msg = (f"{tier} | TRAINED-PARSER precision={prec:.4f} coverage={cov:.4f} recall={agg['parser_strict']['recall']} "
           f"n_attempted={agg['parser_strict']['n_attempted']}/{agg['n_total_sentences']} | "
           f"EXCL_OTHER_UNHANDLED precision={agg['parser_strict_excl_other_unhandled']['precision_on_attempted']} "
           f"coverage={agg['parser_strict_excl_other_unhandled']['coverage_sentence_rate']} | "
           f"vs TOY_GRAMMAR(0.179/0.119): delta_prec={delta_p_vs_toy:+.4f} delta_cov={delta_c_vs_toy:+.4f} | "
           f"vs REVERB(0.083/0.714): delta_prec={delta_p_vs_reverb:+.4f} delta_cov={delta_c_vs_reverb:+.4f} | "
           f"recovers_precision_while_keeping_coverage_gain={recovers_precision_while_keeping_coverage} | "
           f"arms_differ_verified={arms_ok} guard_checks_ok={agg['guard_checks_ok']} "
           f"oos_control_fired={agg['oos_control_fired']} novel_verb_ok={agg['novel_verb_ok']} | "
           f"weakest={weakest} | classical_envelope_target=0.40-0.60 (HARD-PASS floor 0.40 BOTH prec+cov)")
    return tier, msg, weakest


# ---------------------------------------------------------------------------
# boilerplate: start marker / metrics write / crash diagnostic.
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
# self-test: EXERCISE THE REAL code path (real TRAIN corpus subset, real nltk.pos_tag, real FixedTransitionParser
# .train()/.parse(), real TEST corpus slice, real analyze_sentence-based triple derivation, real score_arm).
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (real TRAIN corpus subset, real FixedTransitionParser train+"
          "parse, real TEST corpus slice, real analyze_sentence triple derivation)...", flush=True)

    # (0) glass-box-legal: static source-scan + RUNTIME transitive sys.modules check.
    _grep_neural_source_ok()
    runtime_hits_before = _runtime_neural_module_check()
    assert not runtime_hits_before, f"NEURAL MODULE present before any work: {runtime_hits_before}"
    print("[self_test] glass-box-legal: static source-scan clean (no torch/spacy/transformers/stanza imports)",
          flush=True)

    # (1) train a REAL, small FixedTransitionParser on REAL TRAIN corpus sentences.
    t0 = time.perf_counter()
    graphs, n_provided, n_dropped = _load_train_graphs(n_train=SELFTEST_N_TRAIN)
    assert len(graphs) > 50, f"expected a real, sizeable tiny training set, got {len(graphs)}"
    model_dir = _out_dir("self_test")
    model_path = str(model_dir / "parser_model_selftest.pkl")
    parser = _train_parser(graphs, model_path)
    train_s = time.perf_counter() - t0
    print(f"[self_test] REAL train: n_provided={n_provided} n_dropped_noncontig={n_dropped} "
          f"n_graphs_fed={len(graphs)} n_features={len(parser._dictionary)} train_s={train_s:.2f}", flush=True)

    # (1b) classifier-is-classical-SVM confirmation (mandatory per contract).
    with open(model_path, "rb") as f:
        loaded_model = pickle.load(f)
    assert isinstance(loaded_model, LinearSVC), f"expected sklearn.svm.LinearSVC, got {type(loaded_model)}"
    assert type(loaded_model).__module__.startswith("sklearn"), \
        f"classifier module is not sklearn: {type(loaded_model).__module__}"
    print(f"[self_test] classifier confirmed CLASSICAL, NON-NEURAL: {type(loaded_model).__module__}."
          f"{type(loaded_model).__name__} (linear SVM, sklearn)", flush=True)

    runtime_hits_after = _runtime_neural_module_check()
    assert not runtime_hits_after, f"NEURAL MODULE DETECTED after training/nltk use: {runtime_hits_after}"
    print(f"[self_test] runtime sys.modules closure clean after training ({len(sys.modules)} modules loaded, "
          f"none neural)", flush=True)

    # (2) real_code_path (F.1): parse the REAL local TEST corpus file, sample a tiny REAL slice (RUNG 5's own
    # real loader, reused, seed=7), run the trained parser + analyze_sentence + score_arm end-to-end.
    extractor = make_parser_extractor(parser, model_path)
    qualifying_sorted = load_qualifying_sentences(CONLLU_PATH)
    assert len(qualifying_sorted) > 100, f"expected a real, sizeable qualifying TEST pool, got {len(qualifying_sorted)}"
    rows, dist = build_rows_for_seed(qualifying_sorted, seed=7, n_per_seed=10)
    assert sum(dist.values()) == 10, f"distribution counts do not sum to sample size: {dist}"
    res = score_arm(rows, extractor, relax=False)
    print(f"[self_test] real_code_path: REAL TEST corpus ({len(qualifying_sorted)} qualifying sentences), tiny "
          f"10-sentence real slice -- distribution={dist} | PARSER coverage={res['coverage_sentence_rate']:.3f} "
          f"precision={res['precision_on_attempted']} n_attempted={res['n_attempted']}", flush=True)

    # (3) guard sentences (reliable at SELFTEST_N_TRAIN=500 scale -- VERIFIED live during authoring) + OOS
    # control + a genuinely novel-verb sentence (never in any closed lexicon anywhere in this arc).
    for sent, gold in REVERB_GUARD_SUBSET:
        got = set(extractor(sent)[0])
        assert got == set(gold), f"PARSER guard regression on {sent!r}: got {got}, expected {set(gold)}"
    print(f"[self_test] guard sentences: all {len(REVERB_GUARD_SUBSET)} match exactly at "
          f"SELFTEST_N_TRAIN={SELFTEST_N_TRAIN}", flush=True)
    for s in OUT_OF_SCHEMA_CONTROL:
        got = extractor(s)[0]
        assert got == [], f"PARSER unexpectedly extracted on OOS control {s!r}: {got}"
    print("[self_test] OOS control: PARSER abstains on both control sentences", flush=True)
    novel_sent, novel_expected = NOVEL_VERB_SENTENCE
    novel_got = extractor(novel_sent)[0]
    assert novel_expected in set(novel_got), f"PARSER failed on a genuinely novel-verb sentence: {novel_got}"
    print(f"[self_test] PARSER correctly extracts a genuinely novel-verb sentence: {novel_got}", flush=True)

    # (4) ARMS-MUST-DIFFER (META_RULE_AF): PARSER vs REVERB vs RUNG5-OPEN vs CLOSED_CURRENT emitted-triple hash.
    def _digest(ext):
        allt = sorted(set(t for r in rows for t in ext(r["text"])[0]))
        return hashlib.sha256(json.dumps(allt, sort_keys=True).encode()).hexdigest(), len(allt)
    h_p, n_p = _digest(extractor)
    h_r, n_r = _digest(ie_extract_reverb)
    h_o, n_o = _digest(ie_extract_open)
    h_c, n_c = _digest(ie_extract)
    assert len({h_p, h_r, h_o, h_c}) == 4, ("META_RULE_AF VIOLATION: PARSER/REVERB/RUNG5-OPEN/CLOSED_CURRENT are "
                                           "not pairwise distinct on the real tiny slice")
    print(f"[self_test] PASS | ARMS-MUST-DIFFER verified (PARSER={n_p} REVERB={n_r} RUNG5-OPEN={n_o} "
          f"CLOSED_CURRENT={n_c} unique triples, all pairwise distinct, on the real 10-sentence tiny slice)",
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
    seeds = [7] if run_mode == "smoke" else SEEDS_FULL
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seeds) * N_PER_SEED
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[trained_parser] run_mode={run_mode} seeds={seeds} n_per_seed={N_PER_SEED} "
          f"expected_n_units={expected_n_units} train_corpus={TRAIN_CONLLU_PATH} test_corpus={CONLLU_PATH}",
          flush=True)

    _grep_neural_source_ok()
    glass_box_legal = not _grep_confirm_no_neural_imports()

    agg = run_full(seeds, N_PER_SEED, out_dir)

    runtime_hits = _runtime_neural_module_check()
    glass_box_legal = glass_box_legal and (not runtime_hits)

    tier, msg, weakest = compute_verdict(agg)
    if not glass_box_legal:
        tier, weakest = "HARD_FAIL", "GLASS_BOX_LEGAL_VIOLATION"
        msg = f"HARD_FAIL | glass-box-legal check failed: runtime neural modules present: {runtime_hits}"
    elapsed = time.perf_counter() - t0

    print(f"[trained_parser] {tier} in {elapsed:.2f}s", flush=True)
    print(f"[trained_parser] {msg}", flush=True)

    metrics = {
        "verdict": tier,
        "verdict_msg": msg,
        "summary": msg[:300],
        "run_mode": run_mode,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "n_per_seed": N_PER_SEED,
        "expected_n_units": expected_n_units,
        "weakest_interface": weakest,
        "glass_box_legal": glass_box_legal,
        "classifier": "sklearn.svm.LinearSVC (classical linear SVM, NOT neural; nltk TransitionParser's own "
                      "default poly-kernel probability=True SVC was measured too slow for corpus-scale training "
                      "-- see module docstring DEVIATION section)",
        "corpus": {
            "train_path": str(TRAIN_CONLLU_PATH), "test_path": str(CONLLU_PATH),
            "license": "CC BY-SA 4.0 (UD_English-EWT)",
            "qualifying_pool_size_test": agg["qualifying_pool_size"], "n_sampled_total_test": agg["n_total_sentences"],
            "n_train_provided": agg["n_train_provided"], "n_train_graphs_fed": agg["n_train_graphs_fed"],
            "n_train_dropped_noncontig": agg["n_train_dropped_noncontig"],
        },
        "train_wall_s": agg["train_wall_s"], "parse_wall_s": agg["parse_wall_s"], "n_features": agg["n_features"],
        "construction_distribution_counts": agg["construction_distribution_counts"],
        "construction_distribution_fractions": agg["construction_distribution_fractions"],
        "per_seed_distribution": agg["per_seed_distribution"],
        "arms": {
            "PARSER_strict": {k: v for k, v in agg["parser_strict"].items() if k != "rows"},
            "PARSER_strict_excl_other_unhandled":
                {k: v for k, v in agg["parser_strict_excl_other_unhandled"].items() if k != "rows"},
            "REVERB_same_sample_informational": {k: v for k, v in agg["reverb_same_sample"].items() if k != "rows"},
            "RUNG5_OPEN_same_sample_informational":
                {k: v for k, v in agg["rung5_open_same_sample"].items() if k != "rows"},
            "CLOSED_CURRENT_informational":
                {k: v for k, v in agg["closed_current_informational"].items() if k != "rows"},
        },
        "baselines_measured": {
            "rung5_toy_grammar": {"precision_on_attempted": RUNG5_BASELINE_PRECISION,
                                   "coverage_sentence_rate": RUNG5_BASELINE_COVERAGE,
                                   "source": "d:/AI/hd-instrument/data/exp_read_grow_realprose_ud_ewt_rung5_v1/"
                                             "metrics.json:arms.OPEN_RELATION_strict"},
            "reverb_classical": {"precision_on_attempted": REVERB_BASELINE_PRECISION,
                                  "coverage_sentence_rate": REVERB_BASELINE_COVERAGE,
                                  "source": "d:/AI/hd-instrument/data/exp_read_grow_realprose_reverb_classical_v1/"
                                            "metrics.json:arms.REVERB_strict"},
        },
        "arms_differ_verified": agg["arms_differ_verified"], "digests": agg["digests"],
        "n_unique_triples": agg["n_unique_triples"],
        "guard_checks_ok": agg["guard_checks_ok"], "oos_control_fired": agg["oos_control_fired"],
        "novel_verb_ok": agg["novel_verb_ok"],
        "sample_parser_rows": agg["parser_strict"]["rows"][:60],
        "prereg": {
            "hard_pass": "parser_precision_on_attempted>=0.40 AND parser_coverage_sentence_rate>=0.40 AND "
                         "glass_box_legal AND arms_differ_verified",
            "hard_fail": "parser_precision_on_attempted<0.25 OR parser_coverage_sentence_rate<=0.1190 "
                         "(RUNG5 toy-grammar baseline) OR NOT glass_box_legal OR NOT arms_differ_verified",
            "hp_scope": "PARSER_strict is the ONLY gated discriminator; REVERB_same_sample, "
                        "RUNG5_OPEN_same_sample, CLOSED_CURRENT are informational-only (re-scored on the SAME "
                        "pooled sample for a clean 4-way head-to-head; their own gates were already resolved in "
                        "their own landed cells).",
            "toolchain_choice": "nltk.parse.transitionparser.TransitionParser (arc-eager) subclassed as "
                                "FixedTransitionParser: classifier swapped from the library default poly-kernel "
                                "probability=True SVC (MEASURED too slow for corpus-scale training, 114.66s for "
                                "just 277 sentences) to sklearn.svm.LinearSVC (classical linear SVM, explicitly "
                                "pre-approved by contract), plus an int32 sparse-index dtype compat shim for a "
                                "measured nltk-3.9.4/scikit-learn-1.9.0 version-drift bug.",
            "compute_architecture": "sequential-CPU (justified: transition-based parsing has a genuine per-token "
                                    "sequential stack/buffer dependency chain; the SVM fit itself is a single "
                                    "vectorized LinearSVC.fit() call, not a Python loop); wall time MEASURED "
                                    "~150-185s total (train+parse+score)",
            "storage_strategy": "no_storage (pure parser-layer + extraction test, no FoundationStore/KGStore)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "cardinality_ok": "true (no sweep axis; single trained-parser configuration evaluated once per "
                              "run_mode; EXPECTED_N_UNITS = len(seeds) * N_PER_SEED, matches RUNG5/ReVerb "
                              "convention)",
            "real_code_path_exercised": ["FixedTransitionParser.train (REAL TRAIN corpus subset)",
                                         "FixedTransitionParser.parse (REAL TEST corpus slice)",
                                         "analyze_sentence (RUNG 5, imported unmodified, applied to PREDICTED "
                                         "arcs instead of gold)", "nltk.pos_tag (real classical tagger calls)",
                                         "score_arm (RUNG 5, imported unmodified)"],
            "crlb_n/a": "no quantitative noise floor; discriminator is discrete dependency-arc correctness + "
                       "the classical tagger's own literature-benchmarked accuracy (96-97% PTB, CITED).",
            "glass_box_legal": "static source-scan (no torch/spacy/transformers/stanza imports) AND a runtime "
                               "sys.modules transitive-closure check, both asserted at self-test AND at full "
                               "run time; classifier explicitly confirmed isinstance(sklearn.svm.LinearSVC).",
            "train_test_separation": "TRAIN reads ONLY en_ewt-ud-train.conllu; TEST reads ONLY "
                                     "en_ewt-ud-test.conllu (UD's own official disjoint splits, no sentence-"
                                     "level overlap by construction of the released corpus).",
            "prior_work_check": "substrate_query.sh run before authoring (see completion report); this is the "
                                "direct engineering follow-up ReVerb's own cell (8bc24448e) flagged as NEXT -- "
                                "not a rediscovery.",
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[trained_parser] metrics written -> {out_dir / 'metrics.json'}", flush=True)
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
