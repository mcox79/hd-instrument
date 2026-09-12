#!/usr/bin/env python3
"""WITNESS: consolidation of the temporal ORDER-construction layer into ONE organ, hdlab/temporal_model.py
(consolidation audit action #3, 2026-09-11; owner directive: the brain reuses one structure for many functions,
no islanded copies). hdlab/temporal_ordering.py + hdlab/temporal_ordering_multiframe.py +
hdlab/temporal_order_register.py are now thin re-export SHIMS of temporal_model.

Asserts (exit 0 = all PASS, 1 = any FAIL; standalone, no test framework):
  (a) NAMESPACE PARITY -- each shim exposes EXACTLY the public names its original module exposed (snapshot taken
      from the pre-consolidation modules, embedded below), every re-exported name IS the temporal_model object
      (identity, not a copy), and the union of the three shims' public names == temporal_model's public names.
  (b) BOARD BYTE-IDENTITY -- the four temporal board arms of experiments/exp_situation_model_qa_modern_v1
      (before_after / overlap / survival / implicit_order) re-run in smoke mode return rows EQUAL to the
      pre-consolidation baseline rows embedded below (recorded 2026-09-11 BEFORE any file was touched).
  (c) NO LIVE IMPORTER still imports the three old module paths directly (grep over hdlab/, experiments/,
      tools/, verification/; the shims themselves and this file excluded).

Run:  OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONHASHSEED=0 \
        .venv/Scripts/python.exe verification/test_temporal_model_consolidation.py [--skip-board]
"""
from __future__ import annotations

import importlib
import json
import os
import re
import sys
import types

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
os.environ.setdefault("PYTHONHASHSEED", "0")

SHIMS = ("temporal_ordering", "temporal_ordering_multiframe", "temporal_order_register")
ORGAN = "temporal_model"

# Public names of each ORIGINAL module (pre-consolidation snapshot, 2026-09-11).
OLD_PUBLIC = json.loads(r"""
{
 "temporal_order_register": [
  "ABSTAIN",
  "AFTER",
  "BEFORE",
  "ComposedRegister",
  "ContinuousOrderRegister",
  "Dict",
  "DiscreteOrderRegister",
  "List",
  "NarrationOrderFloor",
  "Optional",
  "OrderQuery",
  "Sequence",
  "Tuple",
  "annotations",
  "build_register",
  "dataclass",
  "extract_passage",
  "make_twin_edges",
  "make_twin_events",
  "promote_clause_pluperfect",
  "score_pairs"
 ],
 "temporal_ordering": [
  "AUX_LEMMAS",
  "CONNECTIVE_PRESERVE",
  "CONNECTIVE_REORDER",
  "COORD_LEMMAS",
  "COPULA_BE",
  "Codebook",
  "Event",
  "MODAL_LEMMAS",
  "SequenceMatrix",
  "TENSE_MODAL_SUBORD",
  "TENSE_OTHER",
  "TENSE_PARTICIPIAL",
  "TENSE_PASSIVE",
  "TENSE_PAST_PERFECT",
  "TENSE_SIMPLE_PAST",
  "annotations",
  "bind_order",
  "build_codebook",
  "chain_recover_depth",
  "dataclass",
  "default_tagger",
  "extract_events",
  "field",
  "pairwise_accuracy",
  "pos_tag_sentence",
  "reconstruct_order",
  "successor_prediction_correct",
  "text_order"
 ],
 "temporal_ordering_multiframe": [
  "AUX_LEMMAS",
  "CLAUSE_BREAK_SURFACE",
  "COPULA_BE",
  "Event",
  "NEUTRAL",
  "SENT_END_SURFACE",
  "SUB_EARLIER",
  "SUB_LATER",
  "SequenceMatrix",
  "TEMPORAL_CONNECTIVES",
  "annotations",
  "bind_order",
  "build_codebook",
  "build_constraint_edges",
  "chain_recover_depth",
  "confident_pair",
  "extract_events_punct",
  "extract_events_shared",
  "pairwise_accuracy",
  "reconstruct_order_cell1cue",
  "reconstruct_order_ppdemote",
  "reconstruct_order_timeline",
  "successor_prediction_correct",
  "tag_punct",
  "text_order"
 ]
}
""")

# The four temporal board rows in smoke mode, recorded BEFORE consolidation (2026-09-11, PYTHONHASHSEED=0).
BASELINE_ROWS = json.loads(r"""
{
 "board_temporal_before_after_dimension": {
  "ci_sep_over_strongest": false,
  "ci_sep_over_twin": false,
  "floor_accs": {
   "iconicity_telling_order": 0.5081
  },
  "integrated_reasoner": {
   "ci": [
    0.0,
    0.0588
   ],
   "date_channel_acc": 1.0,
   "delta_vs_iconicity": 0.0242,
   "iconicity": 0.5081,
   "integrated_acc": 0.5323,
   "sep": false
  },
  "model_acc": 0.5323,
  "model_minus_strongest": [
   0.0242,
   0.0,
   0.0588
  ],
  "model_minus_twin": [
   0.0081,
   -0.0526,
   0.0333
  ],
  "n": 124,
  "overlap_floor": 0.5081,
  "population": "TB-Dense event-event BEFORE/AFTER TLINKs (1990s newswire, MODERN non-circular); model=promoted timeline register (mechanism-if-cue-else-iconicity), floor=iconicity (telling order==event order, recomputed on the SAME pairs), twin=shuffled tense/markers. Paired sentence-cluster bootstrap. MODERN (Cassidy 2014).",
  "reverse_order_subset": {
   "delta": 0.0492,
   "iconicity": 0.0,
   "n": 61,
   "reg": 0.0492,
   "sep": false
  },
  "strongest_floor": 0.5081,
  "strongest_floor_name": "iconicity_telling_order",
  "twin_acc": 0.5242
 },
 "board_temporal_implicit_order_dimension": {
  "abstain_floor_acc": 0.5,
  "ci_sep_over_abstain": true,
  "ci_sep_over_strongest": true,
  "ci_sep_over_twin": true,
  "coverage": 0.6071,
  "floor_accs": {
   "abstain_majority": 0.5,
   "seed_store_tense_gated": 0.5296
  },
  "live_broad_store_wired": true,
  "model_acc": 0.5655,
  "model_minus_abstain": [
   0.0655,
   0.0403,
   0.0911
  ],
  "model_minus_strongest": [
   0.0359,
   0.0117,
   0.0616
  ],
  "model_minus_twin": [
   0.0759,
   0.0434,
   0.1103
  ],
  "n": 1924,
  "null_p95_over_strongest": 0.0217,
  "overlap_floor": 0.5296,
  "population": "TRACIE iid TEST implicit-event before/after (n=1924, 98161 ROCStories mined, MODERN ROCStories-derived gold): model = BROADER store (tense-agnostic UPOS re-mine, 454k pairs, UNGATED headline, coverage 0.607); strongest floor = SEED store (177,800-pair tense-gated mine, recomputed on the SAME population, abstain->majority); abstain-majority floor 0.5000; twin = shuffled-ORDER (directional orientation permuted). Paired CLUSTERED bootstrap over stories. LIVE in hdlab.temporal_reasoner (broad store wired=True). MODERN (Zhou 2021 TRACIE).",
  "strongest_floor": 0.5296,
  "strongest_floor_name": "seed_store_tense_gated",
  "twin_acc": 0.4896
 },
 "board_temporal_overlap_dimension": {
  "ci_sep_over_strongest": true,
  "ci_sep_over_twin": true,
  "floor_accs": {
   "point_order_control": 0.5
  },
  "model_acc": 1.0,
  "model_minus_strongest": [
   0.5,
   0.35,
   0.65
  ],
  "model_minus_twin": [
   0.5,
   null,
   null
  ],
  "n": 40,
  "overlap_floor": 0.5,
  "population": "CONSTRUCTED balanced overlap-vs-precedence can-fail gold (real tagger, NO LLM); model=Allen interval reasoner over aspect-derived endpoints, floor=point-order control (no overlap category -> 0.5), twin=shuffled aspect labels + neutralised markers. The MECHANISM isolation gold (MODERN construction, NOT 19c).",
  "real_prose_tbdense": {
   "allen_recall_on_overlap": 0.4667,
   "fire_precision": 0.3043,
   "full_pop_beats_never_overlap_floor": false,
   "n_overlap_gold": 15,
   "overlap_base_rate": 0.1079,
   "overlap_subset_delta_vs_point": 0.4667,
   "overlap_subset_sep": false,
   "point_order_control": 0.0
  },
  "strongest_floor": 0.5,
  "strongest_floor_name": "point_order_control",
  "twin_acc": 0.5,
  "twin_p95": 0.625
 },
 "board_temporal_survival_dimension": {
  "ci_sep_over_strongest": true,
  "ci_sep_over_twin": true,
  "end_to_end_through_solved_reasoner": {
   "gold_ceiling": 0.7522935779816514,
   "incumbent": 0.09174311926605505,
   "joint_cop": 0.42201834862385323,
   "joint_cop_vs_incumbent": {
    "ci": [
     0.24770642201834864,
     0.42201834862385323
    ],
    "ci_sep": true,
    "delta": 0.3302752293577982
   },
   "joint_cop_vs_twin": {
    "ci": [
     0.05504587155963303,
     0.22018348623853212
    ],
    "ci_sep": true,
    "delta": 0.13761467889908258
   },
   "joint_nom": 0.6513761467889908,
   "pct_of_ceiling_joint_nom": 0.8659
  },
  "event_recall": {
   "incumbent": 0.2164,
   "joint_cop": 0.7463
  },
  "floor_accs": {
   "incumbent_tense_gated_survival": 0.0,
   "nltk_tense_agnostic_survival": 0.2
  },
  "joint_nom_survival": 0.5333,
  "model_acc": 0.2,
  "model_minus_strongest": [
   0.2,
   0.06666666666666667,
   0.36666666666666664
  ],
  "model_minus_twin": [
   0.2,
   0.06666666666666667,
   0.36666666666666664
  ],
  "n": 30,
  "null_p95": 0.13333333333333333,
  "overlap_floor": 0.0,
  "population": "TB-Dense multi-hop BEFORE/AFTER chains (1990s newswire, MODERN dense gold, n_chains=30); model=JOINT tense-agnostic + copular/stative front-end whole-subgraph survival (parse once, read all events off the single dependency structure), floor=INCUMBENT tense-gated extractor (VBD/had+VBN/be+VBN) on the SAME chains, twin=info-free random same-size event set. Reasoner held gold-perfect (extraction ISOLATED). Paired bootstrap over chains. MODERN.",
  "strongest_floor": 0.0,
  "strongest_floor_name": "incumbent_tense_gated_survival",
  "twin_acc": 0.0
 }
}
""")

ARMS = ("board_temporal_before_after_dimension", "board_temporal_overlap_dimension",
        "board_temporal_survival_dimension", "board_temporal_implicit_order_dimension")

# Import forms that would bind a live consumer to an OLD module path.
_ALT = "|".join(sorted(SHIMS, key=len, reverse=True))   # longest first so \b lands after the FULL name
OLD_IMPORT_RE = re.compile(
    r"^[ \t]*(?:from[ \t]+hdlab[ \t]+import[ \t]+(?:[\w, \t]*?\b)?(?:%s)\b"
    r"|from[ \t]+hdlab\.(?:%s)[ \t]+import\b"
    r"|import[ \t]+hdlab\.(?:%s)\b)" % ((_ALT,) * 3), re.M)   # single-line only: no \s (it would cross newlines)
SCAN_DIRS = ("hdlab", "experiments", "tools", "verification")


def _public(mod):
    return sorted(n for n in vars(mod) if not n.startswith("_")
                  and not isinstance(getattr(mod, n), types.ModuleType))


def check_namespaces(fails, notes):
    organ = importlib.import_module("hdlab." + ORGAN)
    organ_pub = set(_public(organ))
    union = set()
    n_identity = 0
    for name in SHIMS:
        shim = importlib.import_module("hdlab." + name)
        pub = set(_public(shim))
        want = set(OLD_PUBLIC[name])
        if pub != want:
            fails.append("(a) %s public names drifted: missing=%s extra=%s"
                         % (name, sorted(want - pub), sorted(pub - want)))
        for n in sorted(pub & organ_pub):
            if getattr(shim, n) is not getattr(organ, n):
                fails.append("(a) %s.%s is not the temporal_model object (a copy, not a re-export)" % (name, n))
            else:
                n_identity += 1
        union |= pub
    if union != organ_pub:
        fails.append("(a) union of shim public names != temporal_model public names: organ-only=%s shims-only=%s"
                     % (sorted(organ_pub - union), sorted(union - organ_pub)))
    notes.append("(a) namespaces: %d shims, %d public names in temporal_model, %d identity-checked re-exports"
                 % (len(SHIMS), len(organ_pub), n_identity))


def check_board(fails, notes):
    from experiments import exp_situation_model_qa_modern_v1 as B
    n_eq = 0
    for arm in ARMS:
        row, _detail = getattr(B, arm)(smoke=True)
        got = json.loads(json.dumps(row, sort_keys=True, default=str))
        want = BASELINE_ROWS[arm]
        if got != want:
            diff = sorted(k for k in set(got) | set(want) if got.get(k) != want.get(k))
            fails.append("(b) %s row differs from baseline on keys %s" % (arm, diff))
        else:
            n_eq += 1
    notes.append("(b) board: %d/%d temporal rows equal the pre-consolidation baseline" % (n_eq, len(ARMS)))


def check_importers(fails, notes):
    skip = {os.path.join(REPO, "hdlab", s + ".py") for s in SHIMS} | {os.path.abspath(__file__)}
    n_files = 0
    offenders = []
    for d in SCAN_DIRS:
        root = os.path.join(REPO, d)
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(dirpath, fn)
                if p in skip:
                    continue
                n_files += 1
                try:
                    src = open(p, "r", encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                for m in OLD_IMPORT_RE.finditer(src):
                    offenders.append("%s: %s" % (os.path.relpath(p, REPO), m.group(0).strip()))
    if offenders:
        fails.append("(c) live importers still bind to old module paths:\n    " + "\n    ".join(offenders))
    notes.append("(c) importers: %d .py files scanned under %s, %d direct old-path imports"
                 % (n_files, "/".join(SCAN_DIRS), len(offenders)))
    # positive control: the regex must fire on the historical import forms
    # (5 historical forms must fire; the temporal_model line must NOT)
    ctl = ("from hdlab import temporal_ordering as T\nfrom hdlab import temporal_ordering_multiframe as M\n"
           "        from hdlab import temporal_order_register as TOR\nfrom hdlab.temporal_ordering import Event\n"
           "from hdlab import temporal_model as X\nfrom hdlab import causal_network as C, temporal_ordering as T\n")
    n_ctl = len(OLD_IMPORT_RE.findall(ctl))
    if n_ctl != 5:
        fails.append("(c) positive control: regex fired %d/5 times on the historical import forms" % n_ctl)


def main(argv):
    fails, notes = [], []
    check_namespaces(fails, notes)
    check_importers(fails, notes)
    if "--skip-board" not in argv:
        check_board(fails, notes)
    else:
        notes.append("(b) board: SKIPPED (--skip-board)")
    for n in notes:
        print("  " + n)
    if fails:
        for f in fails:
            print("FAIL " + f)
        print("RESULT  FAIL (%d)" % len(fails))
        return 1
    print("RESULT  all PASS -- temporal_model consolidation witness")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
