"""PATIENT-SPECIFIC binary classifier as the reader's patient-candidate FILTER -- the last untried lever
for the who-is-affected reader's confirmed EXTRACTION bottleneck.

CONTEXT (VET-confirmed): the backoff+MST reader is ~0.79, EXTRACTION-BOUND. The dominant extraction-loss
bucket is the LABELER: the verb->gold-patient ARC EXISTS (correctly attached by the parser) but the general
36-way UD arc_labeler (hdlab.arc_labeler, ~0.94 label-acc / optimizes OVERALL LAS) tags the patient
obl/nsubj/nmod/ccomp/compound -> the strict {obj,nsubj:pass} filter DROPS it. Cheap fixes already FAILED:
recal-bias a dead no-op; robust-features +~0.009 (within-noise) -- MEASURED@data/exp_labeler_patient_role_
recalibration_v1/metrics.json (RECAL g=+0.000, ROBUST g=+0.009). The parser is NOT the lever
(parser-attach is a proven-small bucket). CITED@Director spawn 2026-07-21.

THE UNTRIED APPROACH: a PATIENT-SPECIFIC BINARY classifier ("is this arc a patient = obj|nsubj:pass?") --
NOT the general 36-way labeler. Trained on UD-EWT (positive = deprel in {obj, nsubj:pass}; negative =
everything else) with PATIENT-DISCRIMINATIVE + REGISTER-ROBUST structural features the general LAS-optimized
labeler does not prioritize: post-verbal direct-dependency, head-is-the-verb, no-governing-preposition,
verb-adjacency, dependent POS (animacy proxy), direct-vs-oblique attachment. Class-cost knob (pos_weight)
pushes patient RECALL, picked by UD-EWT DEV patient-F1 (in-domain; McGuffey NEVER enters training or tuning).
HYPOTHESIS: a task-specific binary patient-detector beats the general labeler on the reader's ACTUAL need
(patient vs not), recovering some of the labeler-dropped golds WITHOUT re-adding enough distractors to lose
the decision (the coupling).

PHASE 1 -- DIAGNOSE the labeler-mislabel cases. For each backoff extraction MISS, classify:
  VERB_NOT_FOUND | POS_MISS (gold token not tagged nominal) | PARSER_ATTACH (nominal gold token exists but
  (vidx, gold_arg) not in the UNLABELED parser pool) | LABELER (gold IN unlabeled pool -> parser attached it,
  but the general labeler tagged the arc non-patient so backoff dropped it). For each LABELER case record the
  general label + whether it is PATIENT-SHAPED (post-verbal, direct dep of the target verb, nominal POS,
  no governing preposition = a mislabeled obj a binary detector could catch) vs GENUINELY-HARD, and whether
  the trained patient-clf RECOVERS it (gold enters the clf pool).

PHASE 2 -- BUILD + PERSIST the patient-clf. Report in-domain patient-detection P/R/F1 (UD-EWT test, under
  gold heads) vs the general labeler's patient(obj|nsubj:pass)-F1 at the SAME setting.

PHASE 3 -- RE-MEASURE the reader end-to-end on full McGuffey gold (100 pairs, 3 verb-disjoint seeds),
  swapping ONLY the patient-filter. Arms (identical vote / verb-split / seeds / parser across arms):
    UNLAB            = all nominal deps (recall ceiling, distractor-heavy).
    LABELED_V1       = strict {obj,nsubj:pass}+conjfix (the pure general-labeler-obj filter).
    BACKOFF          = strict {obj,nsubj:pass}+conjfix, else v2 hardened R1/R2/R3 hand-rules  (THE ~0.79 baseline).
    CLF_REPLACE      = patient-clf score > thr as the PRIMARY filter        [vs LABELED_V1: pure primary swap].
    CLF_BACKOFF      = strict {obj,nsubj:pass}+conjfix, else patient-clf     [vs BACKOFF: swap the fallback = the deployed swap].
  Report recall (gold-in-pool ceiling) AND precision (mean pool size + nopat false-patient rate) AND the
  residual EXTRACTION:DECISION partition AND how many LABELER cases are recovered end-to-end.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (1) REAL baseline = BACKOFF re-derived LIVE this run (not remembered) on the SAME parser both arms use.
      Positive control: BACKOFF e2e must land in [0.72, 0.83] (documented 0.762 hashed / ~0.79 MST).
  (2) CAN-FAIL, three ways: (a) the binary clf trained on the SAME UD-EWT features may just REPRODUCE the
      general labeler's obj decisions -> ~0 lift; (b) it may lift IN-DOMAIN patient-F1 but the labeler
      mislabels are ARCHAIC-DOMAIN-irreducible (UD-EWT web clf also mislabels McGuffey) -> ~0 reader lift
      (the plateau); (c) recovering the labeler golds RE-ADDS distractors -> the vote picks a wrong recovered
      cand (decision error) / nopat false-patients rise -> CLF_BACKOFF <= BACKOFF (coupling reasserts).
      CLF > BACKOFF is NOT guaranteed.
  (3) DIFFICULTY-ON: pronoun + coordination slices reported per-construction; hard_frac reported.
  (4) ONE-VARIABLE: CLF_BACKOFF vs BACKOFF differ ONLY in the empty-pool fallback (hand-rules vs learned clf);
      CLF_REPLACE vs LABELED_V1 differ ONLY in the primary filter (label-lookup vs clf-score). Same
      vote/split/seeds/parser/mining across arms.

VERDICT BANDS (pre-registered; MEASUREMENT cell -- deliverable = the NUMBER + the 11-recovery + the taxonomy):
  primary = CLF_BACKOFF - BACKOFF (3-seed mean end-to-end).
  HARD_PASS_CLF_LIFTS_READER: mean(CLF_BACKOFF - BACKOFF) >= +0.02 AND min-over-seeds >= 0 AND leak clean AND
    n_labeler_recovered_endtoend > 0 AND nopat false-patient rate not worse than BACKOFF by > 0.05.
  HARD_FAIL_CLF_HURTS: mean(CLF_BACKOFF - BACKOFF) <= -0.01 (coupling reasserts / false-patients).
  MIDDLE_BAND_LABELER_ARCHAIC_BOUND: |mean(CLF_BACKOFF - BACKOFF)| < 0.02 (clf neutral -> the labeler is
    archaic-domain-bound = the plateau; the liftable-lever hypothesis is REFUTED for the reader).
  secondary PHASE2: CLF_BEATS_LABELER_INDOMAIN iff clf patient-F1 >= labeler patient-F1 + 0.01 (UD-EWT test).

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified). Binary averaged-perceptron fit on UD-EWT train
  (~12.5k sents) ~<90s; patient-F1 eval on UD-EWT test ~<20s; reader = ~100 gold sentences parsed once + 3-seed
  13-dim vote fits (<1s each) over 5 arms ~<600s. Total full wall < ~15min; smoke < ~150s. Storage: no_storage
  for substrate (the patient-clf is PERSISTED as a glass-box json artifact for RESUME; NOT a substrate atom, NOT
  a frontend asset overwrite). progress_logging: print_flush_true. Determinism: OMP/MKL/OPENBLAS=1, fixed int
  seeds, numpy default_rng, sorted(set); NO hash()-seeded RNG. LOCAL-ONLY, foreground-to-completion; NO queue,
  NO push, NO remote-persist, NO store write, NO git add.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke (CLF_BACKOFF vote weights bit-differ from BACKOFF per seed).
  - final_metrics_atomicity: tmp_replace.  except SystemExit: raise BEFORE except Exception (no BaseException).
  - crlb_n_a: end-to-end decision-precision + binary-detection F1 measurement; no quantitative noise floor.
  - baseline_in_band at smoke (BACKOFF + UNLAB strictly inside (0.05, 0.95)).
  - discriminator survives scale: smoke runs the SAME verdict logic; full re-verifies over 3 seeds.
  - HARD_PASS strictly above floor (+0.02 over BACKOFF; min-over-seed non-negative -- not an at-floor tie).
  - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
  - deterministic_seeding: fixed ints + default_rng + sorted(set); no hash()/list(set()) ordering.
  - LEAK-HUNT: patient-clf trained on UD-EWT deprel ONLY (structural target; McGuffey who-affected gold NEVER
    in training or pos_weight tuning); accept() signature takes NO gold; giveaway_audit re-run on clf pools
    (no single vote-feature >=0.95 gold-selection); self-test asserts gold-independence.
  - RESUME: patient-clf persisted to data/exp_<anchor>[_smoke]/patient_clf.json + intermediate phase1/phase2
    json written before the long reader loop -> a reader-phase crash resumes without retraining.

PRIOR-WORK CHECK (substrate_query.sh "patient-specific binary classifier arc labeler obj nsubj:pass
  who-affected reader extraction"): top KB hit cosine=0.2812 ('classifier'); NONE at cosine>0.30 is a prior
  patient-specific-classifier reader CELL. Directly-adjacent LOCAL prior cells (build-on, credited): the
  general labeler hdlab/arc_labeler.py (train_label 36-way), exp_reader_integration_endtoend_whoaffected_v2
  (BACKOFF arm + accept_hardened + residual partition), exp_labeler_patient_role_recalibration_v1 (recal/robust
  fixes that FAILED -> this cell is the untried BINARY-detector lever, genuinely novel). CITED@Director spawn
  2026-07-21; MEASURED@disk paths above.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "patient_specific_classifier_reader_filter_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_reader_integration_endtoend_whoaffected_v1 as E  # noqa: E402
from experiments import exp_reader_integration_endtoend_whoaffected_v2_extraction_hardened as V2  # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_integrated_vote_role_decision_oracle_gold_v1 as IV  # noqa: E402
from experiments._ud_loader import load_conllu  # noqa: E402
from hdlab.arc_labeler import ArcLabeler, arc_features, norm_label  # noqa: E402
from hdlab.candidate_generator import NOMINAL  # noqa: E402

FRONTEND_DIR = os.path.join(REPO_ROOT, "data", "frontend_assets")
POS_PATH = E.POS_PATH
LABELER_PATH = E.LABELER_PATH
# Task baseline = "backoff + MST parser 0.790"; use the MST-retrained parser so the BASELINE arm re-derives
# the documented number and the clf arm shares the SAME parser (ONE-VARIABLE). Configurable via --parser.
PARSER_ASSET_MST = os.path.join(FRONTEND_DIR, "arc_parser_mst_retrain_ud_ewt.npz")
PARSER_ASSET_HASHED = os.path.join(FRONTEND_DIR, "arc_parser_hashed_ud_ewt.npz")

PATIENT_SET = frozenset({"obj", "nsubj:pass"})


# ==================================================================================================
# PATIENT-DISCRIMINATIVE feature map: general arc_features + register-robust structural augmentation.
# ==================================================================================================
def patient_arc_features(tokens, pos, i, h):
    """Features for arc (dependent i -> head h), 1-based; h==0 = ROOT. General arc_features + patient cues."""
    F = list(arc_features(tokens, pos, i, h))
    n = len(tokens)
    dp = pos[i - 1]
    if h == 0:
        postverbal = False
        head_is_verb = False
        dist = 0
    else:
        hp = pos[h - 1]
        postverbal = i > h              # dependent AFTER its head (direct objects follow the verb in English)
        head_is_verb = hp == "VERB"     # patient attaches to a VERB, not a noun (nmod) or prep
        dist = abs(h - i)
    prevp = pos[i - 2] if i >= 2 else "<S>"
    prev2p = pos[i - 3] if i >= 3 else "<S>"
    prevw = tokens[i - 2].lower() if i >= 2 else "<S>"
    prev2w = tokens[i - 3].lower() if i >= 3 else "<S>"
    # governing preposition proxy (POS ADP or a lexicon prep immediately before the dependent) -> OBLIQUE, not
    # a patient. Mirrors v2's R2 prep-gate; POS-based -> register-robust across UD-EWT web and McGuffey.
    gov_prep = (prevp == "ADP") or (prev2p == "ADP") or (prevw in L.PREPS) or (prev2w in L.PREPS)
    animate = dp == "PRON"              # animacy proxy: pronouns are frequent affected entities
    F += [
        "PV:%d" % int(postverbal),
        "HV:%d" % int(head_is_verb),
        "PVHV:%d%d" % (int(postverbal), int(head_is_verb)),
        "GP:%d" % int(gov_prep),
        "HVGP:%d%d" % (int(head_is_verb), int(gov_prep)),
        "PVHVGP:%d%d%d" % (int(postverbal), int(head_is_verb), int(gov_prep)),
        "ADJ:%d" % int(dist <= 2),
        "dpPV:%s_%d" % (dp, int(postverbal)),
        "dpHV:%s_%d" % (dp, int(head_is_verb)),
        "dpHVGP:%s_%d_%d" % (dp, int(head_is_verb), int(gov_prep)),
        "ANIM_PV:%d%d" % (int(animate), int(postverbal)),
    ]
    return F


# ==================================================================================================
# Binary averaged-perceptron patient classifier (glass-box; json-persistable). Single weight vector;
# predict patient iff score(feats) > thr. Cost-sensitive: false-negatives updated x pos_weight -> recall knob.
# ==================================================================================================
class PatientClassifier:
    def __init__(self, weights=None, pos_weight=1.0, thr=0.0, meta=None):
        self.weights = dict(weights) if weights else {}
        self.pos_weight = float(pos_weight)
        self.thr = float(thr)
        self.meta = dict(meta) if meta else {}

    def score(self, feats):
        w = self.weights
        s = 0.0
        for f in feats:
            v = w.get(f)
            if v is not None:
                s += v
        return s

    def accept_idx(self, tokens, pos, i, h):
        """True iff arc (i -> h) is scored patient. Takes NO gold argument (leak-guard)."""
        return self.score(patient_arc_features(tokens, pos, i, h)) > self.thr

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"weights": self.weights, "pos_weight": self.pos_weight, "thr": self.thr,
                       "meta": self.meta}, f)
        os.replace(tmp, path)

    @classmethod
    def load(cls, path):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return cls({k: float(v) for k, v in d["weights"].items()}, d.get("pos_weight", 1.0),
                   d.get("thr", 0.0), d.get("meta"))


def train_patient_clf(train_sents, epochs=8, seed=1031, pos_weight=1.0, maxlen=50):
    """Binary averaged perceptron: positive = deprel in {obj, nsubj:pass} under GOLD heads."""
    train = [s for s in train_sents if 1 <= len(s) <= maxlen]
    data = []  # list per sentence of (feats, is_patient)
    for s in train:
        tokens = [t[1] for t in s]
        pos = [t[2] for t in s]
        arcs = []
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > len(s):
                continue
            is_pat = norm_label(s[i - 1][4]) in PATIENT_SET
            arcs.append((patient_arc_features(tokens, pos, i, gh), is_pat))
        data.append(arcs)

    w = defaultdict(float)
    cw = defaultdict(float)
    c = 1
    rng = np.random.default_rng(seed)
    for ep in range(epochs):
        for si in rng.permutation(len(data)):
            for feats, is_pat in data[si]:
                s = 0.0
                for f in feats:
                    s += w.get(f, 0.0)
                pred = s > 0.0
                if pred != is_pat:
                    sign = 1.0 if is_pat else -1.0
                    mult = pos_weight if is_pat else 1.0
                    for f in feats:
                        w[f] += sign * mult
                        cw[f] += sign * mult * c
                c += 1
    averaged = {f: w[f] - cw[f] / c for f in w}
    return PatientClassifier(averaged, pos_weight=pos_weight, thr=0.0,
                             meta={"epochs": epochs, "seed": seed, "n_train_sents": len(train),
                                   "pos_weight": pos_weight})


# ==================================================================================================
# Patient-detection P/R/F1 under GOLD heads (binary: patient=obj|nsubj:pass vs not). Same setting for both
# the general labeler (pred label in PATIENT_SET) and the patient-clf (accept_idx).
# ==================================================================================================
def _patient_prf(tp, fp, fn):
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4),
            "tp": tp, "fp": fp, "fn": fn}


def eval_labeler_patient(labeler, gold_sents, maxlen=50):
    tp = fp = fn = 0
    for s in gold_sents:
        if not (1 <= len(s) <= maxlen):
            continue
        tokens = [t[1] for t in s]
        pos = [t[2] for t in s]
        heads = {i: s[i - 1][3] for i in range(1, len(s) + 1) if 0 <= s[i - 1][3] <= len(s)}
        pred = labeler.label(tokens, pos, heads)
        for i in range(1, len(s) + 1):
            if i not in heads:
                continue
            g = norm_label(s[i - 1][4]) in PATIENT_SET
            p = pred.get(i) in PATIENT_SET
            tp += int(p and g)
            fp += int(p and not g)
            fn += int((not p) and g)
    return _patient_prf(tp, fp, fn)


def eval_clf_patient(clf, gold_sents, maxlen=50):
    tp = fp = fn = 0
    for s in gold_sents:
        if not (1 <= len(s) <= maxlen):
            continue
        tokens = [t[1] for t in s]
        pos = [t[2] for t in s]
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > len(s):
                continue
            g = norm_label(s[i - 1][4]) in PATIENT_SET
            p = clf.accept_idx(tokens, pos, i, gh)
            tp += int(p and g)
            fp += int(p and not g)
            fn += int((not p) and g)
    return _patient_prf(tp, fp, fn)


# ==================================================================================================
# Reader candidate-pool builder with pluggable patient-filter mode. Mirrors V2.build_instances; adds the
# clf modes. GOLD-INDEPENDENT: every accept path consults ONLY parser labels/heads/POS/positions.
# ==================================================================================================
def _accept(mode, a, vidx, labels, heads, pos, toks, toks_lc, clf, aa):
    """aa = the strict pool (for backoff empty-check). Return bool for arg a under `mode`."""
    la = labels.get(a)
    if mode == "labeled_v1":
        return E.is_patient_labeled(a, labels, heads, conj_fix=True)
    if mode == "labeled_backoff":
        # handled at pool level (strict-first-then-hardened); this branch unused (see build_instances).
        return E.is_patient_labeled(a, labels, heads, conj_fix=True)
    if mode == "clf_replace":
        return clf.accept_idx(toks, pos, a, heads.get(a, 0))
    return False


def build_instances(order, sent_text, gold, gen, labeler, clf, gfit_fn, sel_fn, mode):
    instances = []
    for sid in order:
        if sid not in gold:
            continue
        rec = gold[sid]
        parsed = gen.generate(sent_text[sid])
        toks, pos, heads = parsed.tokens, parsed.pos, parsed.heads
        margins = parsed.margins
        if not toks:
            continue
        labels = labeler.label(toks, pos, heads)
        toks_lc = [t.lower() for t in toks]
        verb_tokens = [(i, L.lemma_verb(toks_lc[i - 1])) for i in range(1, len(toks) + 1) if pos[i - 1] == "VERB"]

        def args_for(vidx):
            base = [a for (v, a) in parsed.candidates if v == vidx]
            if mode == "unlabeled":
                aa = base
            elif mode == "labeled_v1":
                aa = [a for a in base if E.is_patient_labeled(a, labels, heads, conj_fix=True)]
            elif mode == "clf_replace":
                aa = [a for a in base if clf.accept_idx(toks, pos, a, heads.get(a, 0))]
            elif mode == "labeled_backoff":
                strict = [a for a in base if E.is_patient_labeled(a, labels, heads, conj_fix=True)]
                aa = strict if strict else [a for a in base
                                            if V2.accept_hardened(a, vidx, labels, heads, pos, toks_lc)]
            elif mode == "clf_backoff":
                strict = [a for a in base if E.is_patient_labeled(a, labels, heads, conj_fix=True)]
                aa = strict if strict else [a for a in base if clf.accept_idx(toks, pos, a, heads.get(a, 0))]
            else:
                raise ValueError("unknown mode %r" % mode)
            return sorted(set(aa))

        def build_cands(vidx, v_surf, vlem, gold_patient):
            cands = []
            for a in args_for(vidx):
                p = toks_lc[a - 1]
                if p == v_surf:
                    continue
                feat, meta = IV.extended_features(toks_lc, v_surf, p, vlem, gfit_fn, sel_fn)
                cands.append({"p": p, "feat": feat, "meta": meta,
                              "is_gold": bool(gold_patient is not None and p == gold_patient),
                              "arg_idx": a, "rule": parsed.cand_rules.get((vidx, a)),
                              "parser_margin": float(margins.get(a, 0.0)), "label": labels.get(a)})
            return cands

        used = set()
        for g in rec["pos"]:
            vlem, patient, agent = g["v"], g["patient"], g["agent"]
            vidx = next((i for (i, lm) in verb_tokens if lm == vlem and i not in used), None)
            if vidx is None:
                instances.append({"sid": sid, "v_lemma": vlem, "v_surf": None, "agent": agent,
                                  "gold_patient": patient, "is_pos": True, "cands": [],
                                  "construction": "verb_not_found", "verb_found": False, "gold_in_pool": False})
                continue
            used.add(vidx)
            v_surf = toks_lc[vidx - 1]
            cands = build_cands(vidx, v_surf, vlem, patient)
            constr = E.classify_construction(vidx, patient, toks_lc, pos, heads, labels)
            instances.append({"sid": sid, "v_lemma": vlem, "v_surf": v_surf, "agent": agent,
                              "gold_patient": patient, "is_pos": True, "cands": cands,
                              "construction": constr, "verb_found": True,
                              "gold_in_pool": any(c["is_gold"] for c in cands)})
        for vlem in rec["nopat"]:
            if vlem in rec["pos_verbs"]:
                continue
            vidx = next((i for (i, lm) in verb_tokens if lm == vlem and i not in used), None)
            if vidx is None:
                continue
            used.add(vidx)
            v_surf = toks_lc[vidx - 1]
            cands = build_cands(vidx, v_surf, vlem, None)
            instances.append({"sid": sid, "v_lemma": vlem, "v_surf": v_surf, "agent": "",
                              "gold_patient": None, "is_pos": False, "cands": cands,
                              "construction": "nopat", "verb_found": True, "gold_in_pool": False})
    return instances


# ==================================================================================================
# PHASE 1: extraction-loss taxonomy on the BACKOFF baseline + LABELER-case patient-shape + clf-recovery.
# Recomputed from the parse geometry directly (verb-instance level, NOT split) over ALL gold POS pairs.
# ==================================================================================================
def diagnose(order, sent_text, gold, gen, labeler, clf):
    buckets = defaultdict(int)
    labeler_cases = []       # detailed per LABELER mislabel
    n_pos = 0
    recovered_extraction = 0
    for sid in order:
        if sid not in gold:
            continue
        rec = gold[sid]
        parsed = gen.generate(sent_text[sid])
        toks, pos, heads = parsed.tokens, parsed.pos, parsed.heads
        if not toks:
            continue
        labels = labeler.label(toks, pos, heads)
        toks_lc = [t.lower() for t in toks]
        verb_tokens = [(i, L.lemma_verb(toks_lc[i - 1])) for i in range(1, len(toks) + 1) if pos[i - 1] == "VERB"]
        cand_by_verb = defaultdict(list)
        for (v, a) in parsed.candidates:
            cand_by_verb[v].append(a)
        used = set()
        for g in rec["pos"]:
            n_pos += 1
            vlem, patient = g["v"], g["patient"]
            vidx = next((i for (i, lm) in verb_tokens if lm == vlem and i not in used), None)
            if vidx is None:
                buckets["VERB_NOT_FOUND"] += 1
                continue
            used.add(vidx)
            # tokens matching the gold patient surface
            gold_tok_idxs = [i for i in range(1, len(toks) + 1) if toks_lc[i - 1] == patient]
            unlab_pool = set(cand_by_verb.get(vidx, []))
            # backoff pool (strict-then-hardened)
            strict = [a for a in unlab_pool if E.is_patient_labeled(a, labels, heads, conj_fix=True)]
            backoff = set(strict) if strict else set(
                a for a in unlab_pool if V2.accept_hardened(a, vidx, labels, heads, pos, toks_lc))
            clf_pool = set(strict) if strict else set(
                a for a in unlab_pool if clf.accept_idx(toks, pos, a, heads.get(a, 0)))
            gold_in_backoff = any(toks_lc[a - 1] == patient for a in backoff)
            if gold_in_backoff:
                continue  # not an extraction miss for the baseline
            # classify the miss
            gold_in_unlab = any(a in unlab_pool for a in gold_tok_idxs)
            nominal_gold = any(pos[i - 1] in NOMINAL for i in gold_tok_idxs)
            if not gold_tok_idxs or not nominal_gold:
                buckets["POS_MISS"] += 1
                continue
            if not gold_in_unlab:
                buckets["PARSER_ATTACH"] += 1
                continue
            # LABELER case: gold IN unlabeled pool (parser attached it) but backoff dropped it (label filter).
            buckets["LABELER"] += 1
            ga = next(a for a in gold_tok_idxs if a in unlab_pool)
            la = labels.get(ga)
            prevw = toks_lc[ga - 2] if ga - 2 >= 0 else ""
            prev2w = toks_lc[ga - 3] if ga - 3 >= 0 else ""
            gov_prep = (prevw in L.PREPS) or (prev2w in L.PREPS) or \
                       (pos[ga - 2] == "ADP" if ga - 2 >= 0 else False)
            patient_shaped = bool(ga > vidx and heads.get(ga) == vidx and pos[ga - 1] in NOMINAL and not gov_prep)
            clf_recovers = ga in clf_pool
            recovered_extraction += int(clf_recovers)
            labeler_cases.append({"sid": sid, "v": vlem, "gold_patient": patient, "gold_label": la,
                                  "post_verbal": bool(ga > vidx), "direct_dep_of_verb": bool(heads.get(ga) == vidx),
                                  "gov_prep": bool(gov_prep), "patient_shaped": patient_shaped,
                                  "clf_recovers": bool(clf_recovers), "construction": E.classify_construction(
                                      vidx, patient, toks_lc, pos, heads, labels)})
    n_labeler = buckets["LABELER"]
    n_shaped = sum(1 for c in labeler_cases if c["patient_shaped"])
    n_clf_rec = sum(1 for c in labeler_cases if c["clf_recovers"])
    total_miss = sum(buckets.values())
    return {"n_gold_pos": n_pos, "n_extraction_miss_backoff": total_miss,
            "loss_buckets": dict(buckets),
            "loss_fracs": {k: round(v / total_miss, 4) for k, v in buckets.items()} if total_miss else {},
            "n_labeler_cases": n_labeler, "n_patient_shaped_fixable": n_shaped,
            "n_genuinely_hard": n_labeler - n_shaped, "n_labeler_clf_recovers_extraction": n_clf_rec,
            "labeler_case_labels": dict(defaultdict(int, {c["gold_label"]: 1 for c in labeler_cases}))
            if labeler_cases else {},
            "labeler_cases": labeler_cases}


# ==================================================================================================
def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def cfg_smoke():
    return dict(mode="smoke", slice_lessons=["L04", "L05", "L07"], epochs=40, lr=0.20, alpha=0.2,
                frac_train=0.6, seeds=[7, 13, 19], clf_epochs=4, ud_train_cap=2500,
                pos_weight_grid=[1.0, 2.0])


def cfg_full():
    return dict(mode="full", slice_lessons=["L04", "L05", "L07", "L08", "L09", "L10", "L12"], epochs=60,
                lr=0.20, alpha=0.2, frac_train=0.6, seeds=[7, 13, 19], clf_epochs=8, ud_train_cap=None,
                pos_weight_grid=[1.0, 2.0, 3.0])


def _pool_precision_stats(pos_insts, nopat_insts):
    """Precision-side telemetry: mean pool size on POS pools + false-patient rate on NOPAT pools."""
    pos_sizes = [len(i["cands"]) for i in pos_insts]
    nopat_nonempty = sum(1 for i in nopat_insts if i["cands"])
    return {"mean_pos_pool": round(float(np.mean(pos_sizes)), 4) if pos_sizes else None,
            "nopat_false_patient_rate": round(nopat_nonempty / len(nopat_insts), 4) if nopat_insts else None,
            "n_nopat": len(nopat_insts)}


def run_mode(mode, parser_asset):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = _out_dir(mode)
    E._write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START parser={os.path.basename(parser_asset)} "
          f"slice={'+'.join(cfg['slice_lessons'])}", flush=True)

    # ---- PHASE 2a: train patient-clf on UD-EWT (pos_weight picked by UD-EWT DEV patient-F1; McGuffey-free) ----
    ud_train = load_conllu("train")
    if cfg["ud_train_cap"]:
        ud_train = ud_train[: cfg["ud_train_cap"]]
    try:
        ud_dev = load_conllu("dev")
    except Exception:
        ud_dev = ud_train[-500:]
    try:
        ud_test = load_conllu("test")
    except Exception:
        ud_test = ud_dev
    print(f"[{ANCHOR_NAME}:{mode}] UD-EWT train={len(ud_train)} dev={len(ud_dev)} test={len(ud_test)}", flush=True)

    clf_path = os.path.join(output_dir, "patient_clf.json")
    grid = []
    best_clf = None
    best_dev_f1 = -1.0
    for pw in cfg["pos_weight_grid"]:
        clf_pw = train_patient_clf(ud_train, epochs=cfg["clf_epochs"], seed=1031, pos_weight=pw)
        dev_prf = eval_clf_patient(clf_pw, ud_dev)
        grid.append({"pos_weight": pw, "dev": dev_prf})
        print(f"[{ANCHOR_NAME}:{mode}] pos_weight={pw} DEV patient P/R/F1="
              f"{dev_prf['precision']}/{dev_prf['recall']}/{dev_prf['f1']}", flush=True)
        if dev_prf["f1"] > best_dev_f1:
            best_dev_f1 = dev_prf["f1"]
            best_clf = clf_pw
    best_clf.meta["selected_by"] = "ud_ewt_dev_patient_f1"
    best_clf.meta["dev_f1"] = best_dev_f1
    best_clf.save(clf_path)  # PERSIST for RESUME
    print(f"[{ANCHOR_NAME}:{mode}] persisted patient-clf pos_weight={best_clf.pos_weight} -> {clf_path}", flush=True)

    # ---- PHASE 2b: in-domain patient-detection F1: clf vs general labeler (UD-EWT test, gold heads) ----
    labeler = ArcLabeler.load(LABELER_PATH)
    clf_test = eval_clf_patient(best_clf, ud_test)
    lab_test = eval_labeler_patient(labeler, ud_test)
    phase2 = {"clf_patient_test": clf_test, "labeler_patient_test": lab_test,
              "clf_minus_labeler_f1": round(clf_test["f1"] - lab_test["f1"], 4),
              "clf_beats_labeler_indomain": bool(clf_test["f1"] >= lab_test["f1"] + 0.01),
              "pos_weight_grid": grid, "selected_pos_weight": best_clf.pos_weight}
    # lightweight intermediate persist (RESUME) without runner-schema noise:
    with open(os.path.join(output_dir, "_phase2_intermediate.json"), "w", encoding="utf-8") as f:
        json.dump(phase2, f, indent=2)
    print(f"[{ANCHOR_NAME}:{mode}] PHASE2 in-domain patient-F1 clf={clf_test['f1']} "
          f"labeler={lab_test['f1']} (clf-lab={phase2['clf_minus_labeler_f1']:+.4f})", flush=True)

    # ---- Load reader front-end (parser + gold) ----
    from hdlab.candidate_generator import CandidateGenerator
    gen = CandidateGenerator.load(POS_PATH, parser_asset)
    iv_cfg = IV.cfg_smoke() if mode == "smoke" else IV.cfg_full()
    gfit_fn, sel_fn, gfit_stats, n_mine = IV.build_mining_models(iv_cfg, output_dir)
    order, sent_text, reader_svo = L.load_slice_and_reader(cfg["slice_lessons"])
    gold, gold_meta = L.load_gold(cfg["slice_lessons"])
    print(f"[{ANCHOR_NAME}:{mode}] reader front-end loaded ({gfit_stats['n_object_classes']} gfit classes)", flush=True)

    # ---- PHASE 1: extraction-loss taxonomy + labeler-case patient-shape + clf recovery ----
    diag = diagnose(order, sent_text, gold, gen, labeler, best_clf)
    with open(os.path.join(output_dir, "_phase1_intermediate.json"), "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    print(f"[{ANCHOR_NAME}:{mode}] PHASE1 gold_pos={diag['n_gold_pos']} extraction_miss={diag['n_extraction_miss_backoff']} "
          f"buckets={diag['loss_buckets']} | LABELER n={diag['n_labeler_cases']} shaped/fixable="
          f"{diag['n_patient_shaped_fixable']} hard={diag['n_genuinely_hard']} "
          f"clf_recovers_extraction={diag['n_labeler_clf_recovers_extraction']}", flush=True)

    # ---- PHASE 3: reader end-to-end, 5 arms, 3 verb-disjoint seeds ----
    modes = ["unlabeled", "labeled_v1", "labeled_backoff", "clf_replace", "clf_backoff"]
    insts = {m: build_instances(order, sent_text, gold, gen, labeler, best_clf, gfit_fn, sel_fn, m) for m in modes}
    n_pos = len([i for i in insts["labeled_backoff"] if i["is_pos"]])
    hard_frac = round(sum(1 for i in insts["labeled_backoff"] if i["is_pos"] and i["construction"] != "simple")
                      / n_pos, 4) if n_pos else None
    ceilings = {m: E.gold_in_pool_rate([i for i in insts[m] if i["is_pos"]])[0] for m in modes}
    leak_clf = E.giveaway_audit([i for i in insts["clf_backoff"] if i["is_pos"]])
    print(f"[{ANCHOR_NAME}:{mode}] ceilings(gold-in-pool)={ceilings} hard_frac={hard_frac} "
          f"leak_clf max_single_cue={leak_clf['max_single_feature_gold_selection_acc']} leak={leak_clf['leak']}",
          flush=True)

    per_seed = []
    bk_digests, clfbk_digests = {}, {}
    for seed in cfg["seeds"]:
        tr_v, te_v = E.verb_split(gold, seed, cfg["frac_train"])
        w = {}
        for m in modes:
            w[m], _, _ = IV.train_vote(E.sel_by_verb(insts[m], tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])
        te = {m: [i for i in E.sel_by_verb(insts[m], te_v) if i["is_pos"]] for m in modes}
        nopat_te = {m: [i for i in E.sel_by_verb(insts[m], te_v) if not i["is_pos"]] for m in modes}
        acc = {m: E.endtoend_accuracy(w[m], te[m])[0] for m in modes}
        part = {m: V2.residual_partition(w[m], te[m]) for m in modes}
        prec = {m: _pool_precision_stats(te[m], nopat_te[m]) for m in modes}
        # LABELER recovery end-to-end: pos instances backoff got wrong-by-extraction but clf_backoff gets right.
        bk_map = {(i["sid"], i["v_lemma"]): i for i in te["labeled_backoff"]}
        rec_e2e = 0
        for i in te["clf_backoff"]:
            key = (i["sid"], i["v_lemma"])
            b = bk_map.get(key)
            if b is None or not i["cands"]:
                continue
            b_wrong_ext = (not b["gold_in_pool"])  # backoff extraction miss
            pick = IV.select_pick(w["clf_backoff"], i)[0]
            if b_wrong_ext and pick["p"] == i["gold_patient"]:
                rec_e2e += 1
        bk_digests[seed] = hashlib.sha256(np.round(w["labeled_backoff"], 6).tobytes()).hexdigest()[:16]
        clfbk_digests[seed] = hashlib.sha256(np.round(w["clf_backoff"], 6).tobytes()).hexdigest()[:16]
        row = {"seed": seed, "n_test_pos": len(te["labeled_backoff"]),
               "endtoend": acc,
               "gain_clf_backoff_vs_backoff": round((acc["clf_backoff"] or 0) - (acc["labeled_backoff"] or 0), 4),
               "gain_clf_replace_vs_v1": round((acc["clf_replace"] or 0) - (acc["labeled_v1"] or 0), 4),
               "test_ceilings": {m: E.gold_in_pool_rate(te[m])[0] for m in modes},
               "precision_stats": prec,
               "residual_backoff": part["labeled_backoff"], "residual_clf_backoff": part["clf_backoff"],
               "labeler_recovered_endtoend": rec_e2e,
               "per_construction_clf_backoff": E.per_construction_endtoend(w["clf_backoff"], te["clf_backoff"]),
               "per_construction_backoff": E.per_construction_endtoend(w["labeled_backoff"], te["labeled_backoff"])}
        per_seed.append(row)
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} e2e UNLAB={acc['unlabeled']} V1={acc['labeled_v1']} "
              f"BACKOFF={acc['labeled_backoff']} CLF_REP={acc['clf_replace']} CLF_BK={acc['clf_backoff']} "
              f"| gain_CLFBK_vs_BK={row['gain_clf_backoff_vs_backoff']:+.3f} "
              f"gain_CLFREP_vs_V1={row['gain_clf_replace_vs_v1']:+.3f} | labeler_recovered_e2e={rec_e2e} "
              f"| nopat_FP bk={prec['labeled_backoff']['nopat_false_patient_rate']} "
              f"clfbk={prec['clf_backoff']['nopat_false_patient_rate']}", flush=True)

    def mean(fn):
        vals = [fn(s) for s in per_seed if fn(s) is not None]
        return round(float(np.mean(vals)), 4) if vals else None

    def minv(fn):
        vals = [fn(s) for s in per_seed if fn(s) is not None]
        return round(float(np.min(vals)), 4) if vals else None

    m_e2e = {m: mean(lambda s, m=m: s["endtoend"][m]) for m in modes}
    m_gain_clfbk = mean(lambda s: s["gain_clf_backoff_vs_backoff"])
    min_gain_clfbk = minv(lambda s: s["gain_clf_backoff_vs_backoff"])
    m_gain_clfrep = mean(lambda s: s["gain_clf_replace_vs_v1"])
    total_rec_e2e = sum(s["labeler_recovered_endtoend"] for s in per_seed)
    fp_bk = mean(lambda s: s["precision_stats"]["labeled_backoff"]["nopat_false_patient_rate"])
    fp_clfbk = mean(lambda s: s["precision_stats"]["clf_backoff"]["nopat_false_patient_rate"])
    fp_worse = (fp_clfbk is not None and fp_bk is not None and (fp_clfbk - fp_bk) > 0.05)

    def agg_part(key):
        ext = sum(s[key]["extraction_err"] for s in per_seed)
        dec = sum(s[key]["decision_err"] for s in per_seed)
        cor = sum(s[key]["correct"] for s in per_seed)
        resid = ext + dec
        return {"correct": cor, "extraction_err": ext, "decision_err": dec,
                "ext_to_dec_ratio": f"{ext}:{dec}",
                "extraction_frac_of_residual": round(ext / resid, 4) if resid else None}

    part_bk_agg = agg_part("residual_backoff")
    part_clfbk_agg = agg_part("residual_clf_backoff")

    baseline_in_band = bool(m_e2e["labeled_backoff"] is not None and 0.05 < m_e2e["labeled_backoff"] < 0.95
                            and m_e2e["unlabeled"] is not None and 0.05 < m_e2e["unlabeled"] < 0.95)
    arms_differ = all(bk_digests[s] != clfbk_digests[s] for s in cfg["seeds"])
    pos_control_ok = bool(m_e2e["labeled_backoff"] is not None and 0.72 <= m_e2e["labeled_backoff"] <= 0.83)

    if m_e2e["clf_backoff"] is None or m_e2e["labeled_backoff"] is None:
        verdict = "UNKNOWN_NO_SEEDS"
    elif (m_gain_clfbk >= 0.02 and (min_gain_clfbk or 0) >= 0 and not leak_clf["leak"]
          and total_rec_e2e > 0 and not fp_worse):
        verdict = "HARD_PASS_CLF_LIFTS_READER"
    elif m_gain_clfbk <= -0.01:
        verdict = "HARD_FAIL_CLF_HURTS"
    else:
        verdict = "MIDDLE_BAND_LABELER_ARCHAIC_BOUND"

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | parser={os.path.basename(parser_asset)} slice={'+'.join(cfg['slice_lessons'])} "
           f"gold_pos={n_pos} hard_frac={hard_frac} "
           f"| PHASE1 extraction_miss={diag['n_extraction_miss_backoff']} buckets={diag['loss_buckets']} "
           f"LABELER n={diag['n_labeler_cases']}(shaped/fixable={diag['n_patient_shaped_fixable']} "
           f"hard={diag['n_genuinely_hard']} clf_recovers_ext={diag['n_labeler_clf_recovers_extraction']}) "
           f"| PHASE2 in-domain patient-F1 clf={clf_test['f1']} labeler={lab_test['f1']} "
           f"(clf-lab={phase2['clf_minus_labeler_f1']:+.4f} pos_weight={best_clf.pos_weight}) "
           f"| PHASE3 e2e UNLAB={m_e2e['unlabeled']} V1={m_e2e['labeled_v1']} BACKOFF={m_e2e['labeled_backoff']} "
           f"CLF_REPLACE={m_e2e['clf_replace']}(g_vs_V1={m_gain_clfrep:+.3f}) "
           f"CLF_BACKOFF={m_e2e['clf_backoff']}(g_vs_BK={m_gain_clfbk:+.3f} min={min_gain_clfbk}) "
           f"| ceilings clf_bk={ceilings['clf_backoff']} bk={ceilings['labeled_backoff']} "
           f"| labeler_recovered_e2e(sum)={total_rec_e2e} "
           f"| nopat_FP bk={fp_bk} clfbk={fp_clfbk}(worse>{0.05}={fp_worse}) "
           f"| residual BACKOFF ext:dec={part_bk_agg['ext_to_dec_ratio']} CLF_BK ext:dec={part_clfbk_agg['ext_to_dec_ratio']} "
           f"| baseline_in_band={baseline_in_band} pos_control_ok={pos_control_ok} arms_differ={arms_differ} "
           f"leak_clean={not leak_clf['leak']}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "parser_asset": os.path.basename(parser_asset), "seeds": cfg["seeds"],
        "slice_lessons": cfg["slice_lessons"], "n_gold_pos_pairs": n_pos, "hard_frac": hard_frac,
        "PHASE1_diagnosis": diag,
        "PHASE2_patient_detection": phase2,
        "PHASE3_endtoend_mean": m_e2e,
        "PRIMARY_gain_clf_backoff_vs_backoff_mean": m_gain_clfbk,
        "gain_clf_backoff_vs_backoff_min": min_gain_clfbk,
        "gain_clf_replace_vs_v1_mean": m_gain_clfrep,
        "candidate_recall_ceilings": ceilings,
        "labeler_recovered_endtoend_sum": total_rec_e2e,
        "nopat_false_patient_rate_backoff_mean": fp_bk,
        "nopat_false_patient_rate_clf_backoff_mean": fp_clfbk,
        "nopat_fp_worse_than_backoff": bool(fp_worse),
        "RESIDUAL_PARTITION_backoff": part_bk_agg,
        "RESIDUAL_PARTITION_clf_backoff": part_clfbk_agg,
        "baseline_in_band": baseline_in_band, "positive_control_backoff_ok": pos_control_ok,
        "arms_differ_verified": arms_differ, "leak_guard_clf": leak_clf,
        "no_giveaway_verified": bool(not leak_clf["leak"]),
        "patient_clf_path": clf_path, "patient_clf_pos_weight": best_clf.pos_weight,
        "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "binary-detection F1 + e2e decision precision",
        "progress_logging": "print_flush_true", "compute_architecture": "sequential-CPU (justified: <15min)",
        "deterministic_seeding": True, "gold_meta": gold_meta, "per_seed": per_seed,
    }
    E.write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


# ==================================================================================================
def self_test():
    print("=== patient-specific classifier reader-filter self-test (real code paths) ===", flush=True)
    # (1) tiny UD-shaped train: 'dog bit man' obj=man; classifier separates post-verbal obj from pre-verbal subj.
    def mk(triples):
        return [(k + 1, w, p, h, r) for k, (w, p, h, r) in enumerate(triples)]
    train = []
    for subj, obj in [("dog", "man"), ("cat", "bird"), ("boy", "ball"), ("girl", "cup"), ("man", "dog"),
                      ("fox", "hen"), ("kid", "toy"), ("cow", "grass")]:
        train.append(mk([(subj, "NOUN", 2, "nsubj"), ("bit", "VERB", 0, "root"), (obj, "NOUN", 2, "obj")]))
        train.append(mk([("the", "DET", 2, "det"), (subj, "NOUN", 3, "nsubj"),
                         ("ran", "VERB", 0, "root"), ("to", "ADP", 6, "case"),
                         ("the", "DET", 6, "det"), (obj, "NOUN", 3, "obl")]))
    clf = train_patient_clf(train, epochs=20, seed=7, pos_weight=1.0)
    toks = ["fox", "bit", "hen"]
    pos = ["NOUN", "VERB", "NOUN"]
    acc_subj = clf.accept_idx(toks, pos, 1, 2)   # fox (pre-verbal subject) -> NOT patient
    acc_obj = clf.accept_idx(toks, pos, 3, 2)    # hen (post-verbal object) -> patient
    print(f"[selftest] accept(subj)={acc_subj} accept(obj)={acc_obj} "
          f"score_obj={clf.score(patient_arc_features(toks, pos, 3, 2)):.3f}", flush=True)
    assert acc_obj and not acc_subj, "SELF-TEST FAIL: clf did not separate post-verbal obj from pre-verbal subj"

    # (2) prep-governed oblique must NOT be patient: 'ran to the hen' -> hen governed by 'to' (ADP) -> reject.
    toks2 = ["dog", "ran", "to", "the", "hen"]
    pos2 = ["NOUN", "VERB", "ADP", "DET", "NOUN"]
    acc_obl = clf.accept_idx(toks2, pos2, 5, 2)
    print(f"[selftest] accept(prep-oblique 'hen')={acc_obl}", flush=True)
    assert not acc_obl, "SELF-TEST FAIL: prep-governed oblique wrongly accepted as patient"

    # (3) persistence round-trips.
    import tempfile
    tp = os.path.join(tempfile.gettempdir(), "patient_clf_selftest.json")
    clf.save(tp)
    clf2 = PatientClassifier.load(tp)
    assert clf2.accept_idx(toks, pos, 3, 2) == acc_obj, "SELF-TEST FAIL: persistence changed decision"
    os.remove(tp)

    # (4) LEAK-GUARD: accept_idx / patient_arc_features take NO gold argument.
    import inspect
    for fn in (PatientClassifier.accept_idx, patient_arc_features):
        params = set(inspect.signature(fn).parameters)
        assert "gold" not in params and "patient" not in params, f"SELF-TEST FAIL: {fn.__name__} sees gold (LEAK)"

    # (5) F1 harness sanity on the tiny set: clf recall on obj should be high.
    prf = eval_clf_patient(clf, train)
    print(f"[selftest] tiny-train patient P/R/F1={prf['precision']}/{prf['recall']}/{prf['f1']}", flush=True)
    assert prf["recall"] >= 0.5, "SELF-TEST FAIL: clf recall on training patients too low"

    # (6) verb_split determinism (reuse E).
    gold = {"s1": {"pos": [{"v": "eat"}, {"v": "take"}, {"v": "throw"}, {"v": "build"}],
                   "nopat": set(), "pos_verbs": set()}}
    tr, te = E.verb_split(gold, 7, 0.6)
    assert not (set(tr) & set(te)), "SELF-TEST FAIL: train/test verb overlap"
    print("[selftest] PASS: clf separates obj/subj + prep-gate + persistence + gold-independence + F1 harness",
          flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--parser", choices=["mst", "hashed"], default="mst")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    parser_asset = PARSER_ASSET_MST if args.parser == "mst" else PARSER_ASSET_HASHED
    run_mode(args.mode, parser_asset)


if __name__ == "__main__":
    output_dir = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        E._write_crash_metrics(output_dir, e)
        raise
