#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_parser_ruleinduction_cls_ppattach_v1

DECISIVE test of whether the session's 3x null (29441 / 29480 / 29482: a parameter-free
similarity-vote TIES the linear prototype-averaging consolidator on parser-error correction) is a
property of the LINEAR LEARNER CLASS, or of the TASK. Nearest-centroid / Hebbian outer-product
averaging IS a linear readout (Duda & Hart) -- so a similarity vote tying it is not surprising; the
open question is whether swapping in a genuinely NONLINEAR glass-box generalizer (explicit IF-THEN
feature CONJUNCTIONS via sequential-covering rule induction, gated by a two-part-code MDL criterion
-- Perfors & Tenenbaum 2009) breaks the tie.

BRAIN-FAITHFUL DESIGN (USER 2026-07-23, replicate ALL CLS components, not just the readout):
  HIPPOCAMPAL episodic store: REUSED from 29480 (`_fast_seen_recall`, DG+CA3 one-shot pattern-
    separated recall sanity) -- fast, sparse, orthogonalized per-episode codes.
  INTERLEAVED REPLAY: the rule-search below evaluates every candidate conjunction against the
    WHOLE mixed pool of SEEN failure cases simultaneously (not one episode at a time) -- this is
    what averages out per-episode idiosyncrasy while keeping shared structure, same interleaving
    argument as 29480's `replay_cycle` (mixed-batch Hebbian re-weighting), just realized at the
    rule-search granularity instead of the weight-update granularity.
  NONLINEAR cortical generalizer = THE NEW THING THIS CELL ADDS: `induce_rules()` below, a
    sequential-covering (RIPPER/CN2-family) decision-list search over explicit feature-VALUE
    conjunctions (size <= 2). A conjunction is an AND of feature values -- it carves an
    axis-aligned REGION of feature space that neither a linear combination (ARM_LINEAR) nor an
    aggregate-similarity vote (ARM_SIMVOTE) can represent (canonical witness: XOR, see the
    positive-control task below).
  SCHEMA-GUIDED: candidates are built over 29480's own relationally-bound feature set
    (`BASE.instance_feats`: V lemma, N1 lemma, N1 upos, P form, N2 lemma, distance buckets) --
    minus V-lemma (excluded: on the verb-disjoint held-out split, any V-based rule has zero
    held-out coverage by construction, so it can only waste rule budget; this mirrors why
    29480's ARM_MEMORIZE structurally floors on this split).
  MDL / Bayesian MODEL-SELECTION gate: a candidate conjunction is promoted to a RULE only if the
    two-part code L(rule) + L(exceptions) < L(null encoding of the covered cluster's label
    entropy) -- i.e. it must genuinely COMPRESS, not merely fit. Residual (non-compressing) cases
    stay EPISODIC-ONLY (exact discrete-key lookup, same floor logic as 29480's ARM_MEMORIZE).
  PREDICTION-ERROR / salience weighting: only PARSER FAILURES (`is_fail=True`) ever enter the
    case pool for consolidation on the real task -- correct parses never compete for rule/episode
    budget. This is the same salience-restriction 29480 already applies; retained here unchanged
    (one variable = learner class, everything else held constant).

ARMS (real task; ONE variable = the learner class; same features/data/split as 29480):
  ARM_LINEAR   -- 29480's prototype-averaging Hebbian consolidator, REUSED CODE VERBATIM via
                  import (`BASE.consolidate_store` / `BASE.store_predict`, n_cycles=6,
                  replay_frac=0.5). The null baseline (expected to tie similarity, per the trap).
  ARM_SIMVOTE  -- 29480's parameter-free cosine-similarity k=5 kNN vote, REUSED CODE VERBATIM
                  (`BASE.knn_predict`). THE load-bearing bar every learner must beat.
  ARM_RULEIND  -- NEW: sequential-covering conjunction rule induction (this file), MDL-gated,
                  episodic residual fallback for non-compressing cases.
  ARM_NORULES  -- must-fail freeze-equivalent control: identical ARM_RULEIND code path with
                  `max_rules=0` (rule induction forced off) -- every case falls to the episodic
                  floor; net_gain must stay flat (proves any ARM_RULEIND lift is attributable to
                  the induced rules, not to the architecture merely existing).

POSITIVE CONTROL (mechanism-verification -- explicitly NOT a language-capability claim; guards
  the construction-determined trap per atom 29482): synthetic 4-quadrant balanced task, gold label
  = XOR(a, b) for 2 binary "rule" features, PLUS a "topic" DISTRACTOR drawn independently of (a,b):
  every instance carries n_topic_tags=4 IDENTICAL tag features shared by all same-topic instances
  (n_topics=15) -- a real-ish surface/lexical-overlap confound (analogous to two sentences sharing
  topical vocabulary that is irrelevant to the true syntactic attachment cue), deliberately a much
  STRONGER raw-feature-overlap magnet than the 2 signal bits. Same hashlib-coded dense-bipolar
  bundling pipeline as the real task (reuses `BASE._feat_code`). NOTE (empirically corrected during
  this cell's own smoke gate): an early construction used independent per-instance noise tags from
  a shared small vocabulary -- that FAILED to defeat kNN (MEASURED@ smoke: simvote_acc=0.71-0.90,
  because low-probability per-pair noise-collision leaves the 2 signal bits dominant on average;
  kNN is itself a universal nonparametric approximator and trivially separates 4 well-clustered
  quadrants once noise doesn't structurally overwhelm the signal -- XOR's classic non-linear-
  separability, CITED Minsky & Papert 1969, defeats ARM_LINEAR but does NOT by itself defeat a
  similarity vote). The topic-magnet construction fixes this: same-topic instances are FAR more
  similar to each other (4 shared tags) than same-quadrant-different-topic instances (2 shared
  signal codes), so kNN's nearest neighbors are topic-mates first -- topic carries zero label
  information, so kNN degrades toward chance (MEASURED@ this cell's own tuning sweep, 3 seeds:
  simvote_acc in [0.38, 0.52], mean~0.44). ARM_RULEIND's conjunction search is topic-blind by
  construction (candidates are built from `a:`/`b:` values; topic tags simply never form a
  size<=2 conjunction that beats the a-AND-b split) and recovers the label exactly
  (ruleind_acc=1.0 at all 3 tuning seeds). ARM_LINEAR fails for the original non-separability
  reason regardless of topic (MEASURED@ tuning sweep: ~0.42-0.55, near chance).

BANDS (pre-registered BEFORE this run; see preregs/2026-07-23_parser_ruleinduction_cls_ppattach.md
  for full text -- summarized here, values are load-bearing, do not edit post-hoc):
  CONTROL: HARD_PASS_CONTROL iff ruleind_ctrl_acc>=0.90 AND (ruleind-simvote)>=0.20 AND
    (ruleind-linear)>=0.20, all seeds. HARD_FAIL_CONTROL iff ruleind_ctrl_acc<0.75 OR either
    margin<0.05 (rule-inducer itself broken -- do not trust the real arm).
  REAL: HARD_PASS_REAL iff ruleind beats simvote net_gain by >=0.05 (all seeds) AND beats linear
    by >=0.05 (all seeds) AND scramble collapse>=0.15 AND norules flat (|net_gain|<=0.02) AND
    all-seed ruleind net_gain>0 AND leak_clean. HARD_FAIL_REAL (honest negative) iff ruleind ties
    or loses to simvote (margin<0.02) DESPITE control=HARD_PASS.
  OVERALL: control=HARD_FAIL -> RULEIND_MECHANISM_BROKEN; control=PASS & real=PASS ->
    HARD_PASS_LEARNER_CLASS_WAS_THE_NULL; control=PASS & real=FAIL ->
    HARD_FAIL_TASK_IS_SIMILARITY_SHAPED; else MIDDLE_BAND.

BRAIN-CHECK: PP-attachment resolution in humans is the standard psycholinguistic lexical-frequency
  account (Ratnaparkhi 1994 statistical account matches Whittemore et al. 1990 / Taraban &
  McClelland 1988 garden-path preference data) -- if this cell HARD_FAILs on the real arm despite
  a clean mechanism-verified control, that matches a documented human bound (exemplar/analogical
  parsing, Daelemans et al. 1999 memory-based parsing), not a substrate defect; report either
  outcome honestly.

POINTERS / REUSE (ADAPTS, does not re-implement): imports parser training, PP-instance harvesting,
  verb-disjoint split, signature/feature encoding, ARM_LINEAR, ARM_SIMVOTE, scramble/leak-probe
  machinery VERBATIM from
  experiments/exp_parser_selfimprove_case_sleep_ppattach_v1.py (atom lineage 29480; the 29441
  representation-not-learner finding and 29482 construction-determined-trap caution are the
  reasons the positive control here is explicitly labeled a mechanism check, not a capability
  claim).

COMPUTE ARCHITECTURE: class (b) sequential-CPU (parser-train + PP-harvest reused from 29480's own
  <6min budget; rule induction over a few hundred SEEN failure cases, candidate pairing capped to
  the top-60 most frequent singles -- seconds per seed). LOCAL-ONLY, foreground-to-completion; NO
  queue, NO push, NO remote-persist, NO hdlab mutation, NO atom bank (skunkworks VETs).
  Deterministic: OMP/MKL/OPENBLAS=1, np.random.default_rng fixed int seeds, hashlib feature codes
  (NO hash()-seeded RNG), sorted(set) splits. progress_logging: print_flush_true.

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement cell):
  - arms_differ_verified at smoke gate (hash test over ARM_LINEAR/SIMVOTE/RULEIND predicted-class
    tuples on held-out).
  - final_metrics_atomicity: tmp_replace (os.replace).
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException).
  - crlb_n/a: generalization accuracy/net-gain measurement, not a capacity/CRLB-bound cell.
  - baseline_in_band: real task reuses 29480's check; control baseline is exactly-balanced 50/50
    by construction (declared n/a).
  - discriminator survives scale: smoke = full mechanism on a capped DEV-only slice (option A,
    same as 29480).
  - cardinality_ok: EXPECTED per-seed rows = len(seeds) for both control (3) and real (3).
  - calibration_check: adaptive_with_discriminator_gate (MDL purity_thresh/min_coverage gate;
    scramble + norules controls verify fire).
  - all numbers tagged MEASURED@ / CITED@ / THEORETICAL@ / HYPOTHESIZED@ in this docstring.
  - deterministic_seeding: true; progress_logging: print_flush_true.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import itertools
import json
import math
import platform
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "parser_ruleinduction_cls_ppattach_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_parser_selfimprove_case_sleep_ppattach_v1 as BASE  # noqa: E402

# ---- Pre-registered bands (set BEFORE this run; see preregs/2026-07-23_parser_ruleinduction_cls_ppattach.md) ----
CTRL_HP_ACC_MIN = 0.90
CTRL_HP_MARGIN_MIN = 0.20
CTRL_HF_ACC_MAX = 0.75
CTRL_HF_MARGIN_MAX = 0.05

BEAT_MARGIN_HARD_PASS = 0.05
BEAT_MARGIN_HARD_FAIL = 0.02
SCRAMBLE_COLLAPSE_MIN = 0.15
NORULES_FLAT_MAX = 0.02

MIN_COVERAGE = 3
PURITY_THRESH = 0.75
MAX_CONJUNCT = 2
MAX_RULES = 25
MAX_SINGLES_FOR_PAIRING = 60

REAL_SEEDS = [7, 13, 19]
CTRL_SEEDS = [0, 1, 2]
EXPOSURE_FRACS = [0.25, 0.5, 0.75, 1.0]


# ========================================================================================
# MDL-gated sequential-covering rule induction (the NONLINEAR cortical generalizer). Generic over
# any list-of-instances with a "gold_class" field and a feat_fn(inst) -> iterable[str].
# ========================================================================================
def _entropy_bits(labels):
    if not labels:
        return 0.0
    n = len(labels)
    h = 0.0
    for c in Counter(labels).values():
        p = c / n
        if p > 0:
            h -= p * math.log2(p)
    return h


def induce_rules(pool, feat_fn, *, max_conjunct=MAX_CONJUNCT, min_coverage=MIN_COVERAGE,
                  purity_thresh=PURITY_THRESH, max_rules=MAX_RULES, exclude_prefixes=(),
                  max_singles_for_pairing=MAX_SINGLES_FOR_PAIRING, mdl_margin_bits=0.0):
    """Sequential-covering (RIPPER/CN2-family) decision-list induction over explicit feature-VALUE
    conjunctions. Each rule is an AND of <=max_conjunct feature values -- NONLINEAR: it carves an
    axis-aligned region a linear map or an aggregate-similarity vote cannot represent. MDL gate
    (Perfors & Tenenbaum 2009 two-part code): promoted only if L(rule)+L(exceptions) beats the
    null per-instance entropy cost of the CURRENT residual pool (recomputed every covering
    iteration, so the gate is adaptive to what remains unexplained). Returns
    (rules: list[dict], residual_indices: list[int] into pool -- these stay EPISODIC-ONLY).
    """
    n = len(pool)
    labels = [a["gold_class"] for a in pool]
    classes = sorted(set(labels))
    n_classes = max(len(classes), 2)
    feats_per_case = [set(f for f in feat_fn(a) if not any(f.startswith(p) for p in exclude_prefixes))
                       for a in pool]

    uncovered = set(range(n))
    rules = []
    while uncovered and len(rules) < max_rules:
        cur_labels = [labels[i] for i in uncovered]
        cur_h = _entropy_bits(cur_labels)

        val_to_idx = defaultdict(list)
        for i in uncovered:
            for f in feats_per_case[i]:
                val_to_idx[f].append(i)
        singles = {(f,): idxs for f, idxs in val_to_idx.items() if len(idxs) >= min_coverage}

        all_candidates = dict(singles)
        if max_conjunct >= 2 and len(singles) >= 2:
            freq_sorted = sorted(singles.keys(), key=lambda k: -len(singles[k]))[:max_singles_for_pairing]
            for (f1,), (f2,) in itertools.combinations(freq_sorted, 2):
                idxs = sorted(set(singles[(f1,)]) & set(singles[(f2,)]))
                if len(idxs) >= min_coverage:
                    all_candidates[(f1, f2)] = idxs

        best = None
        for conj, idxs in all_candidates.items():
            lbls = [labels[i] for i in idxs]
            maj_label, maj_count = Counter(lbls).most_common(1)[0]
            precision = maj_count / len(idxs)
            if precision < purity_thresh:
                continue
            l_rule_bits = math.log2(max(len(all_candidates), 2))
            n_exceptions = len(idxs) - maj_count
            l_data_given_rule = n_exceptions * math.log2(n_classes) if n_exceptions else 0.0
            l_null = len(idxs) * cur_h
            if (l_rule_bits + l_data_given_rule) >= (l_null - mdl_margin_bits):
                continue  # does not compress -- MDL gate refuses
            score = (round(precision, 6), len(idxs))
            if best is None or score > best[0]:
                best = (score, conj, idxs, maj_label, precision, l_rule_bits, l_data_given_rule, l_null)
        if best is None:
            break
        (_score, conj, idxs, maj_label, precision, l_rule_bits, l_data_given_rule, l_null) = best
        rules.append(dict(conjunct=list(conj), majority_class=maj_label, coverage=len(idxs),
                          precision=round(precision, 4), bits_rule=round(l_rule_bits, 3),
                          bits_exceptions=round(l_data_given_rule, 3), bits_null=round(l_null, 3)))
        uncovered -= set(idxs)
    residual = sorted(uncovered)

    # Terminal default clause (standard decision-list closing rule, RIPPER/CN2-family; distinct
    # from the MDL-scored conjunction search above). Once the covering loop stops, the two-part
    # MDL comparison used for explicit conjunctions can never promote a rule to explain a residual
    # that is ALREADY homogeneous (entropy ~0 costs ~0 bits under the null model, so no positive
    # rule-cost can "compress" it further -- spending >0 bits to state a rule when the null cost is
    # already 0 is a net expansion, correctly rejected above). But a residual that is ALREADY
    # majority-coherent (purity >= purity_thresh) still needs SOME terminal prediction rule for
    # unseen held-out cases that match none of the explicit conjunctions -- the free, zero-feature
    # "else predict the residual's majority class" statement is exactly that, and it costs no
    # additional conjunction bits (conjunct=[] matches everything, by design the LOWEST-priority /
    # last-checked rule in the decision list). A residual that is NOT majority-coherent gets no
    # default and stays genuinely EPISODIC (exact-key lookup only; no generalization claimed) --
    # this preserves the CLS design intent (idiosyncratic/incoherent leftovers stay episodic).
    # Guarded on max_rules > 0: ARM_NORULES (max_rules=0, the freeze-equivalent must-fail control)
    # must get NEITHER explicit rules NOR the terminal default -- architecture present but induction
    # switched off entirely, so any measured lift is cleanly attributable to genuine rule induction.
    if residual and max_rules > 0:
        res_labels = [labels[i] for i in residual]
        maj_label, maj_count = Counter(res_labels).most_common(1)[0]
        purity = maj_count / len(residual)
        if purity >= purity_thresh:
            rules.append(dict(conjunct=[], majority_class=maj_label, coverage=len(residual),
                              precision=round(purity, 4), bits_rule=0.0, bits_exceptions=0.0,
                              bits_null=0.0, is_default=True))
            residual = []
    return rules, residual


def build_residual_lookup(pool, residual_idx, key_fn):
    """Episodic fallback: exact discrete-key lookup from the non-compressing residual cases (same
    floor logic as 29480's ARM_MEMORIZE -- on a verb-disjoint held-out split this cannot
    exact-match by construction)."""
    table = {}
    for i in residual_idx:
        a = pool[i]
        table.setdefault(key_fn(a), Counter()).update([a["gold_class"]])
    return {k: c.most_common(1)[0][0] for k, c in table.items()}


def ruleind_predict_factory(rules, residual_lookup, feat_fn, key_fn, default_class):
    def fn(a):
        feats = set(feat_fn(a))
        for r in rules:
            if set(r["conjunct"]).issubset(feats):
                return r["majority_class"], 1.0
        role = residual_lookup.get(key_fn(a))
        if role is not None:
            return role, 1.0
        return a.get("pred_class", default_class), -1.0
    return fn


# ========================================================================================
# Positive-control synthetic task: XOR(a, b) diluted with shared-vocab nuisance features.
# CITED (Minsky & Papert 1969): XOR is not linearly separable.
# ========================================================================================
def make_control_instances(n_per_quadrant, seed, n_topic_tags=4, n_topics=15):
    """gold label = XOR(a,b); the DISTRACTOR is a 'topic' assignment drawn independently of (a,b)
    -- every instance sharing a topic carries n_topic_tags IDENTICAL tag features, a much stronger
    /tighter raw-feature-overlap magnet than the 2 signal bits (real-ish complication: the
    kNN-defeating confound this models is a coarser surface/topic similarity that dominates
    cosine overlap while carrying zero information about the true label, exactly analogous to how
    lexical/topical overlap between two sentences can swamp the syntactic cue that actually decides
    an attachment). Empirically calibrated (see prereg): at n_topic_tags=4/n_topics=15, cosine-sim
    kNN over the additively-bundled signature is pulled toward same-TOPIC neighbors (uninformative
    about a/b) and lands near chance, while the rule-inducer's explicit a-AND-b conjunction search
    is topic-blind by construction and recovers the label exactly."""
    rng = np.random.default_rng(seed)
    instances = []
    quadrants = [(0, 0), (0, 1), (1, 0), (1, 1)]
    iid = 0
    for (a, b) in quadrants:
        label = "XOR1" if (a != b) else "XOR0"
        for _ in range(n_per_quadrant):
            topic = int(rng.integers(0, n_topics))
            topic_tags = ["topic%d:t%d" % (k, topic) for k in range(n_topic_tags)]
            instances.append(dict(
                iid=iid, a=a, b=b, gold_class=label,
                feats=["a:%d" % a, "b:%d" % b] + topic_tags,
                key="ctrl|%d" % iid,
                pred_class="XOR0",
                is_fail=True,
            ))
            iid += 1
    return instances


def control_feat_fn(inst):
    return inst["feats"]


def control_key_fn(inst):
    return inst["key"]


def control_signature(inst):
    v = np.zeros(BASE.N_SIG, dtype=np.float32)
    for f in inst["feats"]:
        v = v + BASE._feat_code(f)
    return v


def control_split(instances, seed, frac_seen=0.7):
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(instances))
    n_seen = int(round(frac_seen * len(instances)))
    seen = [instances[j] for j in perm[:n_seen]]
    held = [instances[j] for j in perm[n_seen:]]
    return seen, held


def _accuracy(predict_fn, held):
    n = len(held)
    if n == 0:
        return None
    correct = sum(1 for a in held if predict_fn(a)[0] == a["gold_class"])
    return round(correct / n, 4)


def run_control_seed(seed, n_per_quadrant, exposure_fracs=EXPOSURE_FRACS):
    instances = make_control_instances(n_per_quadrant, seed)
    for a in instances:
        a["sig"] = control_signature(a)
    seen, held = control_split(instances, seed, frac_seen=0.7)

    roles = ("XOR1", "XOR0")
    role_codebook = BASE.build_role_codebook(roles, seed=91 + seed)
    sigs = [a["sig"] for a in seen]
    labels = [a["gold_class"] for a in seen]

    # ARM_LINEAR (BASE.consolidate_store / store_predict, verbatim reuse)
    W_lin = BASE.consolidate_store(sigs, labels, role_codebook, n_cycles=6, replay_frac=0.5, seed=seed)
    lin_fn = lambda a: BASE.store_predict(W_lin, role_codebook, list(roles), a["sig"])  # noqa: E731
    linear_acc = _accuracy(lin_fn, held)

    # ARM_SIMVOTE (BASE.knn_predict, verbatim reuse)
    simvote_fn = lambda a: BASE.knn_predict(sigs, labels, a["sig"], k=BASE.K_KNN)  # noqa: E731
    simvote_acc = _accuracy(simvote_fn, held)

    # ARM_RULEIND
    rules, residual_idx = induce_rules(seen, control_feat_fn)
    residual_lookup = build_residual_lookup(seen, residual_idx, control_key_fn)
    ruleind_fn = ruleind_predict_factory(rules, residual_lookup, control_feat_fn, control_key_fn, "XOR0")
    ruleind_acc = _accuracy(ruleind_fn, held)

    # ARM_NORULES (freeze-equivalent must-fail control: rule induction forced off)
    norules_rules, norules_residual = induce_rules(seen, control_feat_fn, max_rules=0)
    norules_lookup = build_residual_lookup(seen, norules_residual, control_key_fn)
    norules_fn = ruleind_predict_factory(norules_rules, norules_lookup, control_feat_fn, control_key_fn, "XOR0")
    norules_acc = _accuracy(norules_fn, held)

    # exposure / learning curve on ARM_RULEIND
    curve = []
    for frac in exposure_fracs:
        k = max(4, int(round(frac * len(seen))))
        sub = seen[:k]
        r_sub, res_sub = induce_rules(sub, control_feat_fn)
        lookup_sub = build_residual_lookup(sub, res_sub, control_key_fn)
        fn_sub = ruleind_predict_factory(r_sub, lookup_sub, control_feat_fn, control_key_fn, "XOR0")
        curve.append({"exposure_frac": frac, "n_seen": k, "ruleind_acc": _accuracy(fn_sub, held),
                      "n_rules": len(r_sub)})

    return {
        "seed": seed, "n_seen": len(seen), "n_held": len(held),
        "linear_acc": linear_acc, "simvote_acc": simvote_acc, "ruleind_acc": ruleind_acc,
        "norules_acc": norules_acc,
        "margin_over_simvote": round((ruleind_acc or 0) - (simvote_acc or 0), 4),
        "margin_over_linear": round((ruleind_acc or 0) - (linear_acc or 0), 4),
        "n_rules": len(rules), "n_episodic": len(residual_idx), "rules": rules,
        "exposure_curve": curve,
        "held_predicted_ruleind": [ruleind_fn(a)[0] for a in held],
        "held_predicted_simvote": [simvote_fn(a)[0] for a in held],
        "held_predicted_linear": [lin_fn(a)[0] for a in held],
    }


# ========================================================================================
# Real task: reuse 29480's parser train + PP-instance harvest + verb-disjoint split VERBATIM.
# ========================================================================================
def run_real_seed(instances, seed, frac_seen=0.6, exposure_fracs=EXPOSURE_FRACS):
    seen, held, seen_v = BASE.verb_split(instances, seed, frac_seen)
    seen_fail = [a for a in seen if a["is_fail"]]
    held_fail = [a for a in held if a["is_fail"]]
    base_rate = BASE._majority_base_rate(held)
    if len(seen_fail) < 4:
        return {"seed": seed, "skipped": "too_few_seen_cases", "n_seen_fail": len(seen_fail),
                "n_heldout_fail": len(held_fail)}

    roles = list(BASE.ROLES)
    role_codebook = BASE.build_role_codebook(roles)
    case_sigs = [a["sig"] for a in seen_fail]
    case_roles = [a["gold_class"] for a in seen_fail]

    # ARM_LINEAR (29480's coherent arm, verbatim reuse)
    W_lin = BASE.consolidate_store(case_sigs, case_roles, role_codebook, n_cycles=6, replay_frac=0.5, seed=seed)
    lin_fn = lambda a: BASE.store_predict(W_lin, role_codebook, roles, a["sig"])  # noqa: E731
    tau_lin = BASE.calibrate_tau(lin_fn, seen)
    linear = BASE.eval_heldout(lin_fn, held, tau_lin)

    # ARM_SIMVOTE (29480's knn control, verbatim reuse)
    simvote_fn = lambda a: BASE.knn_predict(case_sigs, case_roles, a["sig"], k=BASE.K_KNN)  # noqa: E731
    tau_sim = BASE.calibrate_tau(simvote_fn, seen)
    simvote = BASE.eval_heldout(simvote_fn, held, tau_sim)

    # ARM_RULEIND (this cell's nonlinear generalizer)
    rules, residual_idx = induce_rules(seen_fail, BASE.instance_feats, exclude_prefixes=("v:",))
    residual_lookup = build_residual_lookup(seen_fail, residual_idx, BASE.instance_key)
    ruleind_fn = ruleind_predict_factory(rules, residual_lookup, BASE.instance_feats, BASE.instance_key, roles[0])
    ruleind = BASE.eval_heldout(ruleind_fn, held, 0.0)

    # ARM_NORULES (freeze-equivalent must-fail control)
    norules_rules, norules_residual = induce_rules(seen_fail, BASE.instance_feats, exclude_prefixes=("v:",),
                                                    max_rules=0)
    norules_lookup = build_residual_lookup(seen_fail, norules_residual, BASE.instance_key)
    norules_fn = ruleind_predict_factory(norules_rules, norules_lookup, BASE.instance_feats, BASE.instance_key,
                                         roles[0])
    norules = BASE.eval_heldout(norules_fn, held, 0.0)

    # SCRAMBLE (case<->correction shuffled BEFORE induction)
    rng = np.random.default_rng(2000 + seed)
    scr_perm = rng.permutation(len(seen_fail))
    labels_orig = [a["gold_class"] for a in seen_fail]
    labels_scr = [labels_orig[j] for j in scr_perm]
    seen_fail_scr = [dict(a, gold_class=labels_scr[i]) for i, a in enumerate(seen_fail)]
    rules_scr, residual_scr = induce_rules(seen_fail_scr, BASE.instance_feats, exclude_prefixes=("v:",))
    lookup_scr = build_residual_lookup(seen_fail_scr, residual_scr, BASE.instance_key)
    scr_fn = ruleind_predict_factory(rules_scr, lookup_scr, BASE.instance_feats, BASE.instance_key, roles[0])
    scramble = BASE.eval_heldout(scr_fn, held, 0.0)

    # exposure / learning curve on ARM_RULEIND (real task)
    curve = []
    for frac in exposure_fracs:
        k = max(4, int(round(frac * len(seen_fail))))
        sub = seen_fail[:k]
        r_sub, res_sub = induce_rules(sub, BASE.instance_feats, exclude_prefixes=("v:",))
        lookup_sub = build_residual_lookup(sub, res_sub, BASE.instance_key)
        fn_sub = ruleind_predict_factory(r_sub, lookup_sub, BASE.instance_feats, BASE.instance_key, roles[0])
        ev_sub = BASE.eval_heldout(fn_sub, held, 0.0)
        curve.append({"exposure_frac": frac, "n_seen_fail": k, "net_gain": ev_sub["net_gain"],
                      "heldout_fix_rate": ev_sub["heldout_fix_rate"], "n_rules": len(r_sub)})

    gain_collapse_scramble = round((ruleind["heldout_fix_rate"] or 0) - (scramble["heldout_fix_rate"] or 0), 4)
    beat_simvote_margin = round(BASE._nz(ruleind["net_gain"], -9) - BASE._nz(simvote["net_gain"], -9), 4)
    beat_linear_margin = round(BASE._nz(ruleind["net_gain"], -9) - BASE._nz(linear["net_gain"], -9), 4)
    norules_net_gain = norules["net_gain"]

    return {
        "seed": seed, "n_seen_verbs": len(seen_v), "n_seen_fail": len(seen_fail),
        "n_heldout": len(held), "n_heldout_fail": len(held_fail), "base_rate_majority": base_rate,
        "linear": linear, "simvote": simvote, "ruleind": ruleind, "norules": norules,
        "scramble": scramble,
        "gain_collapse_scramble": gain_collapse_scramble,
        "beat_simvote_margin": beat_simvote_margin, "beat_linear_margin": beat_linear_margin,
        "norules_net_gain": norules_net_gain,
        "n_rules": len(rules), "n_episodic": len(residual_idx), "rules": rules,
        "exposure_curve": curve,
        "held_predicted_ruleind": [ruleind_fn(a)[0] for a in held],
        "held_predicted_simvote": [simvote_fn(a)[0] for a in held],
        "held_predicted_linear": [lin_fn(a)[0] for a in held],
    }


# ========================================================================================
# Mode configs + I/O.
# ========================================================================================
def cfg_smoke():
    return dict(mode="smoke", real_seeds=[7], ctrl_seeds=[0], dev_cap=900, ctrl_n_per_quad=20)


def cfg_full():
    return dict(mode="full", real_seeds=REAL_SEEDS, ctrl_seeds=CTRL_SEEDS, dev_cap=None, ctrl_n_per_quad=50)


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _write_start_marker(output_dir, mode):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _arms_must_differ(held, per_seed_row):
    """META_RULE_AF: hash-test that ARM_LINEAR / ARM_SIMVOTE / ARM_RULEIND predictions on held-out
    are not bit-identical arrays (arm-implementation bug guard)."""
    arms = {
        "linear": per_seed_row["held_predicted_linear"],
        "simvote": per_seed_row["held_predicted_simvote"],
        "ruleind": per_seed_row["held_predicted_ruleind"],
    }
    digests = {name: hashlib.sha256(json.dumps(vals).encode("utf-8")).hexdigest()
               for name, vals in arms.items()}
    pairs_identical = []
    for (a, da), (b, db) in itertools.combinations(digests.items(), 2):
        if da == db:
            pairs_identical.append((a, b))
    return digests, pairs_identical


def mean_of(rows, path):
    vals = []
    for s in rows:
        v = s
        for p in path:
            v = v[p] if isinstance(v, dict) else None
        if isinstance(v, (int, float)):
            vals.append(v)
    return round(float(np.mean(vals)), 4) if vals else None


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START rule-induction CLS learner-class swap on PP-attachment", flush=True)

    # ---- CONTROL (mechanism verification) ----
    ctrl_rows = []
    for seed in cfg["ctrl_seeds"]:
        row = run_control_seed(seed, cfg["ctrl_n_per_quad"])
        ctrl_rows.append(row)
        print(f"[{ANCHOR_NAME}:{mode}] CONTROL seed={seed} n_seen={row['n_seen']} n_held={row['n_held']} "
              f"| RULEIND acc={row['ruleind_acc']} SIMVOTE acc={row['simvote_acc']} "
              f"LINEAR acc={row['linear_acc']} NORULES acc={row['norules_acc']} "
              f"| beat_simvote={row['margin_over_simvote']} beat_linear={row['margin_over_linear']} "
              f"| n_rules={row['n_rules']} n_episodic={row['n_episodic']}", flush=True)

    c_ruleind = mean_of(ctrl_rows, ["ruleind_acc"])
    c_simvote = mean_of(ctrl_rows, ["simvote_acc"])
    c_linear = mean_of(ctrl_rows, ["linear_acc"])
    c_norules = mean_of(ctrl_rows, ["norules_acc"])
    c_margin_simvote = mean_of(ctrl_rows, ["margin_over_simvote"])
    c_margin_linear = mean_of(ctrl_rows, ["margin_over_linear"])
    ctrl_all_seeds_hp = all((r["ruleind_acc"] or 0) >= CTRL_HP_ACC_MIN and
                            (r["margin_over_simvote"] or 0) >= CTRL_HP_MARGIN_MIN and
                            (r["margin_over_linear"] or 0) >= CTRL_HP_MARGIN_MIN for r in ctrl_rows)
    ctrl_any_seed_hf = any((r["ruleind_acc"] or 0) < CTRL_HF_ACC_MAX or
                           (r["margin_over_simvote"] or 0) < CTRL_HF_MARGIN_MAX or
                           (r["margin_over_linear"] or 0) < CTRL_HF_MARGIN_MAX for r in ctrl_rows)
    if ctrl_all_seeds_hp:
        control_verdict = "HARD_PASS_CONTROL"
    elif ctrl_any_seed_hf:
        control_verdict = "HARD_FAIL_CONTROL"
    else:
        control_verdict = "MIDDLE_BAND_CONTROL"

    # ---- REAL (train parser once, harvest PP instances once, then per-seed splits) ----
    W_parser, parser_info = BASE.train_dep_parser(mode)
    dev = BASE.read_conllu("en_ewt-ud-dev.conllu")
    test = BASE.read_conllu("en_ewt-ud-test.conllu")
    sents = dev + test
    sents = [s for s in sents if 1 <= len(s) <= 60]
    if cfg["dev_cap"]:
        sents = sents[:cfg["dev_cap"]]
    instances = BASE.attach_predictions(sents, W_parser)
    n_fail = sum(1 for a in instances if a["is_fail"])
    base_acc_all = round(1 - n_fail / len(instances), 4) if instances else None
    leak_clean = BASE._leak_probe(instances)
    print(f"[{ANCHOR_NAME}:{mode}] REAL census pp_instances={len(instances)} base_errors={n_fail} "
          f"acc={base_acc_all} parser_uas={parser_info['uas_dev']} leak_clean={leak_clean}", flush=True)

    real_rows = []
    arms_diff_report = []
    for seed in cfg["real_seeds"]:
        row = run_real_seed(instances, seed, frac_seen=0.6)
        real_rows.append(row)
        if "ruleind" in row:
            digests, identical_pairs = _arms_must_differ(None, row)
            arms_diff_report.append({"seed": seed, "digests": digests, "identical_pairs": identical_pairs})
            assert not identical_pairs, f"META_RULE_AF VIOLATION seed={seed}: {identical_pairs}"
            print(f"[{ANCHOR_NAME}:{mode}] REAL seed={seed} n_seen_fail={row['n_seen_fail']} "
                  f"n_held_fail={row['n_heldout_fail']} base_rate={row['base_rate_majority']} "
                  f"| RULEIND fix={row['ruleind']['heldout_fix_rate']} gain={row['ruleind']['net_gain']} "
                  f"| SIMVOTE fix={row['simvote']['heldout_fix_rate']} gain={row['simvote']['net_gain']} "
                  f"| LINEAR fix={row['linear']['heldout_fix_rate']} gain={row['linear']['net_gain']} "
                  f"| NORULES gain={row['norules']['net_gain']} | SCRAMBLE fix={row['scramble']['heldout_fix_rate']} "
                  f"(collapse={row['gain_collapse_scramble']}) | beat_simvote={row['beat_simvote_margin']} "
                  f"beat_linear={row['beat_linear_margin']} | n_rules={row['n_rules']} n_episodic={row['n_episodic']}",
                  flush=True)
        else:
            print(f"[{ANCHOR_NAME}:{mode}] REAL seed={seed} SKIPPED: {row.get('skipped')}", flush=True)

    scored = [s for s in real_rows if "ruleind" in s]
    m_base = mean_of(scored, ["base_rate_majority"])
    m_ruleind_gain = mean_of(scored, ["ruleind", "net_gain"])
    m_ruleind_fix = mean_of(scored, ["ruleind", "heldout_fix_rate"])
    m_simvote_gain = mean_of(scored, ["simvote", "net_gain"])
    m_simvote_fix = mean_of(scored, ["simvote", "heldout_fix_rate"])
    m_linear_gain = mean_of(scored, ["linear", "net_gain"])
    m_linear_fix = mean_of(scored, ["linear", "heldout_fix_rate"])
    m_norules_gain = mean_of(scored, ["norules", "net_gain"])
    m_collapse = mean_of(scored, ["gain_collapse_scramble"])
    m_beat_simvote = mean_of(scored, ["beat_simvote_margin"])
    m_beat_linear = mean_of(scored, ["beat_linear_margin"])
    base_acc_real = mean_of(scored, ["ruleind", "base_acc"])
    baseline_in_band = bool(base_acc_real is not None and 0.05 < base_acc_real < 0.95)
    n_rules_total = sum(s["n_rules"] for s in scored)
    n_episodic_total = sum(s["n_episodic"] for s in scored)

    all_seeds_ruleind_gain_pos = bool(scored) and all(BASE._nz(s["ruleind"]["net_gain"], -1) > 0 for s in scored)
    all_seeds_beat_simvote = bool(scored) and all(
        BASE._nz(s["ruleind"]["net_gain"], -9) - BASE._nz(s["simvote"]["net_gain"], -9) >= BEAT_MARGIN_HARD_PASS
        for s in scored)
    all_seeds_beat_linear = bool(scored) and all(
        BASE._nz(s["ruleind"]["net_gain"], -9) - BASE._nz(s["linear"]["net_gain"], -9) >= BEAT_MARGIN_HARD_PASS
        for s in scored)
    scramble_collapses = (m_collapse is not None and m_collapse >= SCRAMBLE_COLLAPSE_MIN)
    norules_flat = (m_norules_gain is not None and abs(m_norules_gain) <= NORULES_FLAT_MAX)
    ties_or_loses_simvote = (m_beat_simvote is not None and m_beat_simvote < BEAT_MARGIN_HARD_FAIL)

    if not scored:
        real_verdict = "INSUFFICIENT_SURFACE"
    elif (scramble_collapses and norules_flat and all_seeds_ruleind_gain_pos and all_seeds_beat_simvote
          and all_seeds_beat_linear and leak_clean):
        real_verdict = "HARD_PASS_REAL"
    elif ties_or_loses_simvote:
        real_verdict = "HARD_FAIL_REAL"
    else:
        real_verdict = "MIDDLE_BAND_REAL"

    if control_verdict == "HARD_FAIL_CONTROL":
        overall = "RULEIND_MECHANISM_BROKEN"
    elif control_verdict == "HARD_PASS_CONTROL" and real_verdict == "HARD_PASS_REAL":
        overall = "HARD_PASS_LEARNER_CLASS_WAS_THE_NULL"
    elif control_verdict == "HARD_PASS_CONTROL" and real_verdict == "HARD_FAIL_REAL":
        overall = "HARD_FAIL_TASK_IS_SIMILARITY_SHAPED"
    else:
        overall = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    msg = (f"{overall} | CONTROL[{control_verdict}]: ruleind_acc={c_ruleind} simvote_acc={c_simvote} "
           f"linear_acc={c_linear} norules_acc={c_norules} (beat_simvote={c_margin_simvote}, "
           f"beat_linear={c_margin_linear}, need>={CTRL_HP_MARGIN_MIN} for HARD_PASS) | "
           f"REAL[{real_verdict}]: n_pp_instances={len(instances)} base_errors={n_fail} "
           f"base_acc={base_acc_all} parser_uas={parser_info['uas_dev']} | RULEIND fix={m_ruleind_fix} "
           f"gain={m_ruleind_gain} (base_rate={m_base}) | SIMVOTE fix={m_simvote_fix} gain={m_simvote_gain} "
           f"| LINEAR fix={m_linear_fix} gain={m_linear_gain} | beat_simvote_margin={m_beat_simvote} "
           f"(need>={BEAT_MARGIN_HARD_PASS}) beat_linear_margin={m_beat_linear} "
           f"(need>={BEAT_MARGIN_HARD_PASS}) | NORULES gain={m_norules_gain} (need flat<={NORULES_FLAT_MAX}) "
           f"| SCRAMBLE collapse={m_collapse} (need>={SCRAMBLE_COLLAPSE_MIN}) | n_rules_total={n_rules_total} "
           f"n_episodic_total={n_episodic_total} | leak_clean={leak_clean} baseline_in_band={baseline_in_band}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": overall, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "control_verdict": control_verdict, "real_verdict": real_verdict,
        "real_seeds": cfg["real_seeds"], "ctrl_seeds": cfg["ctrl_seeds"],
        "expected_n_real_seed_rows": len(cfg["real_seeds"]), "n_real_seed_rows": len(real_rows),
        "expected_n_ctrl_seed_rows": len(cfg["ctrl_seeds"]), "n_ctrl_seed_rows": len(ctrl_rows),
        "cardinality_ok": bool(len(real_rows) == len(cfg["real_seeds"]) and len(ctrl_rows) == len(cfg["ctrl_seeds"])),
        "CONTROL_ruleind_acc_mean": c_ruleind, "CONTROL_simvote_acc_mean": c_simvote,
        "CONTROL_linear_acc_mean": c_linear, "CONTROL_norules_acc_mean": c_norules,
        "CONTROL_margin_over_simvote_mean": c_margin_simvote, "CONTROL_margin_over_linear_mean": c_margin_linear,
        "census": {"n_pp_instances": len(instances), "n_base_errors": n_fail, "base_acc_all": base_acc_all},
        "parser_info": parser_info, "leak_clean": leak_clean, "baseline_in_band": baseline_in_band,
        "PRIMARY_real_ruleind_net_gain_mean": m_ruleind_gain, "PRIMARY_real_ruleind_fix_rate_mean": m_ruleind_fix,
        "base_rate_majority_mean": m_base,
        "CONTROL_ARM_real_simvote_net_gain_mean": m_simvote_gain, "CONTROL_ARM_real_simvote_fix_rate_mean": m_simvote_fix,
        "CONTROL_ARM_real_linear_net_gain_mean": m_linear_gain, "CONTROL_ARM_real_linear_fix_rate_mean": m_linear_fix,
        "MUSTFAIL_norules_net_gain_mean": m_norules_gain, "norules_flat": norules_flat,
        "MUSTFAIL_scramble_gain_collapse_mean": m_collapse, "scramble_collapses": scramble_collapses,
        "beat_simvote_margin_mean": m_beat_simvote, "beat_linear_margin_mean": m_beat_linear,
        "all_seeds_ruleind_net_gain_positive": all_seeds_ruleind_gain_pos,
        "all_seeds_beat_simvote_hard_pass": all_seeds_beat_simvote,
        "all_seeds_beat_linear_hard_pass": all_seeds_beat_linear,
        "n_rules_total_real": n_rules_total, "n_episodic_total_real": n_episodic_total,
        "arms_differ_verified": True, "arms_diff_report": arms_diff_report,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "generalization accuracy/net-gain measurement; not a capacity/CRLB-bound cell",
        "progress_logging": "print_flush_true", "compute_architecture": "sequential-CPU (reuses 29480 <6min budget)",
        "calibration_check": "adaptive_with_discriminator_gate (MDL purity_thresh/min_coverage gate; "
                             "scramble+norules controls verify fire)",
        "deterministic_seeding": True, "compose_in_cell_no_hdlab_mutation": True,
        "ctrl_per_seed": ctrl_rows, "real_per_seed": real_rows,
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {overall}", flush=True)
    print(msg, flush=True)
    return payload


def self_test():
    print("=== rule-induction CLS learner-class swap self-test (real code paths) ===", flush=True)

    # ---- control mechanism sanity (tiny) ----
    row = run_control_seed(0, n_per_quadrant=12)
    assert row["ruleind_acc"] is not None and row["simvote_acc"] is not None and row["linear_acc"] is not None
    assert row["n_rules"] >= 1, "rule induction produced zero rules at self-test scale on a perfectly solvable task"
    print(f"[selftest] control OK: ruleind_acc={row['ruleind_acc']} simvote_acc={row['simvote_acc']} "
          f"linear_acc={row['linear_acc']} n_rules={row['n_rules']}", flush=True)

    # ---- real code path: parser train + PP harvest + verb split + induce_rules ----
    W, parser_info = BASE.train_dep_parser("smoke")
    assert parser_info["uas_dev"] > 0.4, f"parser UAS suspiciously low: {parser_info}"
    dev = BASE.read_conllu("en_ewt-ud-dev.conllu")[:400]
    instances = BASE.attach_predictions(dev, W)
    assert instances, "no PP-attachment instances extracted at smoke scale"
    n_fail = sum(1 for a in instances if a["is_fail"])
    assert n_fail > 0, "zero parser errors on PP-attachment at smoke scale (discriminator dead)"
    leak = BASE._leak_probe(instances[:80])
    assert leak, "LEAK: signature not gold-free / not mutation-invariant"

    real_row = run_real_seed(instances, 7, frac_seen=0.6)
    if "ruleind" in real_row:
        assert set(("fixes", "breaks", "heldout_fix_rate")).issubset(real_row["ruleind"])
        digests, identical_pairs = _arms_must_differ(None, real_row)
        assert not identical_pairs, f"META_RULE_AF VIOLATION: {identical_pairs}"
        print(f"[selftest] real path OK: n_seen_fail={real_row['n_seen_fail']} n_rules={real_row['n_rules']} "
              f"n_episodic={real_row['n_episodic']} ruleind_gain={real_row['ruleind']['net_gain']} "
              f"simvote_gain={real_row['simvote']['net_gain']} linear_gain={real_row['linear']['net_gain']}",
              flush=True)
    else:
        print(f"[selftest] real path SKIPPED at this scale: {real_row.get('skipped')} (acceptable at self-test "
              f"scale; FULL harvests the full DEV+TEST corpus)", flush=True)

    # MDL gate sanity: forcing max_rules=0 must yield zero rules
    zero_rules, zero_residual = induce_rules(
        [dict(gold_class="A", feats=["x:1"]), dict(gold_class="A", feats=["x:1"]),
         dict(gold_class="A", feats=["x:1"])], lambda a: a["feats"], max_rules=0)
    assert zero_rules == [] and len(zero_residual) == 3, "max_rules=0 must force zero induced rules"

    print("[selftest] PASS", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run_mode(args.mode)


if __name__ == "__main__":
    output_dir = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            os.makedirs(output_dir, exist_ok=True)
            diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                    "summary": "CELL_CRASHED", "elapsed_s": 0.0, "traceback": traceback.format_exc()[:4000],
                    "ts_iso": datetime.now(timezone.utc).isoformat()}
            tmp = os.path.join(output_dir, "metrics.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(diag, f, indent=2)
            os.replace(tmp, os.path.join(output_dir, "metrics.json"))
        finally:
            raise
