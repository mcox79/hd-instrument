"""LABELER patient-role recalibration -- fix the arc_labeler (the diagnosed root-cause of the extraction-bound
reader) so it tags true patients as obj MORE OFTEN without inflating false-obj, improving BOTH candidate-recall
AND precision (breaking the recall/precision coupling that the v2 accept-rule BACKOFF could not).

CONTEXT (from exp_reader_integration_endtoend_whoaffected_v2_extraction_hardened diagnosis):
  The reader is EXTRACTION-BOUND. 70% (16/23) of the labeled-arm extraction loss is the arc_labeler MIS-TAGGING
  patients: a correctly-ATTACHED true object gets label obl/iobj/nsubj/ccomp instead of obj, so the strict
  {obj,nsubj:pass}+conj filter DROPS it (recall loss). The v2 fix ADDED accept-rules (R1/R2/R3 backoff) and got
  only +0.020 (MIDDLE_BAND) because recovering candidates via accept-rules TRADES recall for precision
  (coordination went negative). The RIGHT lever (per diagnosis) = improve the LABELER's patient-role accuracy so
  the true patient is tagged obj at SOURCE -> recall up (true patient enters the strict pool) AND precision up
  (a well-tuned labeler still tags genuine obliques obl, so no distractor added) = coupling broken.

PHASE 1 -- DIAGNOSE the mislabel source (domain-shift vs general labeler limitation):
  obj-row confusion of the persisted labeler on (a) UD-EWT TEST held-out (in-domain, under GOLD heads) vs
  (b) McGuffey gold patients (out-of-domain, under PARSER heads restricted to correctly-attached, isolating the
  labeler from parser mis-attach). If the true-patient-tagged-obj rate is MUCH lower on McGuffey = DOMAIN-SHIFT
  (labeler trained on modern UD-EWT web text, its discriminative SURFACE-WORD features are OOV on 1879 archaic
  McGuffey, so the obj-vs-obl decision falls back to structure + spurious priors); if similar = general labeler
  limitation. Reports the per-predicted-label distribution for the patient-relevant gold roles.

PHASE 2 -- FIX (two cheap gold-INDEPENDENT-of-McGuffey labeler changes; UD-EWT is the labeler's own supervision):
  RECAL  = obj-vs-competitor DECISION-BOUNDARY recalibration. Hypothesis: the labeler systematically
           UNDER-predicts obj for post-verbal direct nominals -> add a scalar bias b_obj to the obj score, TUNED
           on UD-EWT DEV (never McGuffey) to maximize obj-F1 subject to overall-label-acc not regressing.
           Cheapest (no retrain). Tests the systematic-OFFSET hypothesis. A scalar cannot ADD discriminative
           info, so if domain-shift zeroed the discriminative features it may only trade recall<->precision.
  ROBUST = RETRAIN the labeler with register-INVARIANT patient-discriminative features (governing-preposition
           flag, post-verbal-direct-nominal-no-prep flag) added to the existing feature set. These features
           TRANSFER to archaic text (POS + preposition-list + position, no surface vocab) and ADD the exact
           obj-vs-obl information the diagnosis identified -> the perceptron learns obj for prep-free post-verbal
           direct nominals and KEEPS obl for prep-governed ones. This is the information-adding fix that CAN
           break the coupling. Trained on UD-EWT TRAIN only.
  NOTE: neither labeler EVER sees the McGuffey who-affected gold. The canonical frontend labeler asset is NEVER
  overwritten -- both variants live in-memory only (NO store write).

PHASE 3 -- RE-MEASURE end-to-end who-affected on McGuffey gold, ONE-VARIABLE = the labeler:
  V1      = ORIGINAL labeler + strict {obj,nsubj:pass}+conj filter + vote  (the REAL baseline, re-derived LIVE).
  BACKOFF = ORIGINAL labeler + v2 accept-rule backoff + vote               (the incumbent 0.762 accept-rule fix).
  RECAL   = RECAL labeler    + strict filter + vote                        (labeler fix A).
  ROBUST  = ROBUST labeler   + strict filter + vote                        (labeler fix B).
  RECAL/ROBUST vs V1 differ ONLY in the labeler (same strict filter / vote / verb-split / seeds). Report per arm:
  candidate-recall (gold_in_pool ceiling) AND mean_pool_size (inverse-precision proxy) AND end-to-end accuracy;
  per-construction (pronoun / coordination = the losing slices); residual EXTRACTION:DECISION partition; and each
  variant's IN-DOMAIN UD-EWT label-accuracy (regression guard: do NOT break UD-EWT to fix McGuffey).

DESIGN-GATE (pre-registered; verified at smoke BEFORE any full):
  (1) REAL baseline = V1 (original labeler strict filter+vote) re-derived LIVE + BACKOFF 0.762 re-derived LIVE.
  (2) CAN-FAIL: RECAL's scalar bias may flip GENUINE obliques/nsubj (re-adding distractors -> precision loss ->
      coupling reasserts -> RECAL <= V1); ROBUST's added obj-recall may inflate false-obj; OR domain-shift is
      IRREDUCIBLE without McGuffey gold parses (the discriminative features are OOV and structure alone cannot
      separate obj from obl on archaic text) -> both fixes <= V1 = an INFORMATIVE BOUND, not a win. C>B not
      guaranteed. Also: a fix that raises McGuffey obj-recall by REGRESSING in-domain UD-EWT label-acc is
      rejected (broke the labeler globally).
  (3) DIFFICULTY-ON: pronoun + coordination slices reported per-construction; hard_frac asserted > 0 at smoke.
  (4) ONE-VARIABLE: V1 vs RECAL vs ROBUST differ ONLY in which labeler produces the arc labels.

VERDICT BANDS (pre-registered; MEASUREMENT cell -- primary deliverable = the numbers + the coupling test):
  HARD_PASS_LABELER_FIX_BREAKS_COUPLING: best_fix_endtoend (= max(RECAL,ROBUST)) >= V1 + 0.02 AND that variant's
      candidate-recall >= V1 recall AND that variant's mean_pool_size <= V1 mean_pool_size + 0.15 (precision NOT
      degraded) AND min-over-seed gain >= 0 AND leak clean AND that variant's in-domain label-acc drop <= 0.01.
  HARD_FAIL_LABELER_FIX_HURTS: best_fix_endtoend < V1 - 0.01, OR both variants regress in-domain label-acc > 0.02.
  MIDDLE_BAND: otherwise (fix neutral / trades recall<->precision without breaking the coupling / domain-bound).

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified). ROBUST retrain = dict-keyed averaged perceptron on
  UD-EWT train (~12.5k sents, ~48s/epoch; smoke = 2500-sent subset x3 epochs ~30s; full ~6min). RECAL = bias grid
  over UD-EWT dev (seconds). Mining + 5 parse-build passes over ~114 McGuffey sents + 3-seed 13-dim vote fits
  (reuse v1/v2). Wall < ~5min smoke / < ~15min full. Storage: no_storage; NO frontend-asset overwrite.
  progress_logging: print_flush_true. Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, default_rng, sorted(set);
  NO hash()-seeded RNG. LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO remote-persist, NO git add,
  NO canonical store write.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke (RECAL/ROBUST labels differ from ORIGINAL on >=1 McGuffey patient arc = the
    discriminator-fires check; vote weight vectors also bit-differ per seed).
  - final_metrics_atomicity: tmp_replace.  except SystemExit: raise BEFORE except Exception (no BaseException).
  - crlb_n_a: end-to-end decision-precision + label-accuracy measurement; no quantitative noise floor.
  - baseline_in_band at smoke (V1 + UNLABELED strictly inside (0.05, 0.95)).
  - discriminator survives scale: smoke runs the SAME verdict logic; full re-verifies over 3 seeds.
  - HARD_PASS strictly above floor (+0.02 over V1; min-over-seed non-negative; recall AND precision guards).
  - calibration_check: adaptive_with_discriminator_gate -- RECAL bias tuned on UD-EWT DEV by obj-F1, guarded by
    overall-label-acc non-regression, curve logged. ROBUST features are structural (register-invariant).
  - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
  - deterministic_seeding: fixed ints + default_rng + sorted(set); no hash()/list(set()) ordering.
  - LEAK-HUNT: giveaway_audit re-run on RECAL/ROBUST pools (no single feature >=0.95 gold-selection); the
    labelers are trained/tuned on UD-EWT ONLY; the McGuffey gold is consulted ONLY to LOCATE the patient arc for
    measurement + as the who-affected eval target (identical to v1/v2) -- NEVER inside any labeler.

PRIOR-WORK CHECK (substrate_query.sh "labeler patient role obj recalibration dependency label extraction reader"):
  top hit cosine=0.3076 is the generic WordNet/notes token 'calibration'; the argstruct/dependency-parser design
  note is at 0.3027 (relevant background, the parser+labeler line this continues). NONE at cosine>0.30 is a prior
  labeler-patient-role-recalibration CELL. This is a NOVEL continuation: v2 fixed the FILTER (accept-rules); this
  fixes the LABELER itself. CITED@backup-doc 2026-07-20; MEASURED@diag_extraction/diag_fix 2026-07-20.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import inspect
import json
import platform
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "labeler_patient_role_recalibration_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_reader_integration_endtoend_whoaffected_v1 as E  # noqa: E402
from experiments import exp_reader_integration_endtoend_whoaffected_v2_extraction_hardened as HARD  # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_integrated_vote_role_decision_oracle_gold_v1 as IV  # noqa: E402
from experiments._ud_loader import load_conllu  # noqa: E402
from hdlab.arc_labeler import ArcLabeler, arc_features, norm_label, train_label  # noqa: E402

POS_PATH = E.POS_PATH
ARC_PATH = E.ARC_PATH
LABELER_PATH = E.LABELER_PATH
PATIENT_LABELS = E.PATIENT_LABELS
PREPS = L.PREPS

# Patient-relevant gold-label rows for the Phase-1 confusion matrix.
PATIENT_ROLE_ROWS = ("obj", "nsubj:pass", "iobj")
NOMINAL_POS = ("NOUN", "PROPN", "PRON", "NUM")


# ==============================================================================================
# REGISTER-INVARIANT patient-discriminative features (the ROBUST fix). Structural only -- POS +
# preposition-list + position; NO surface vocab -> transfers to archaic text.
# ==============================================================================================
def arc_features_robust(tokens, pos, i, h):
    """arc_features(...) PLUS register-invariant obj-vs-obl cues (governing-prep, post-verbal-direct-no-prep)."""
    F = list(arc_features(tokens, pos, i, h))
    n = len(tokens)
    dp = pos[i - 1]
    prevw = tokens[i - 2].lower() if i - 2 >= 0 else ""
    prev2w = tokens[i - 3].lower() if i - 3 >= 0 else ""
    gov_prep = (prevw in PREPS) or (prev2w in PREPS)
    is_nom = dp in NOMINAL_POS
    hp = pos[h - 1] if 1 <= h <= n else "ROOT"
    postverb_direct = (hp == "VERB") and (i > h) and is_nom and (not gov_prep)
    F.append("rb_govprep:%d" % int(gov_prep))
    F.append("rb_nom_govprep:%s_%d" % (dp, int(gov_prep)))
    F.append("rb_pvdirect:%d" % int(postverb_direct))
    F.append("rb_pvdirect_hp:%s_%d" % (hp, int(postverb_direct)))
    return F


# ==============================================================================================
# Labeler variants. Uniform interface: .label(tokens,pos,heads), .label_accuracy(gold_sents),
# ._predict_label(feats), attribute .feat_fn (feature function used for per-arc prediction).
# ==============================================================================================
class RecalLabeler(ArcLabeler):
    """Original labeler + a per-label additive score bias (the obj-decision-boundary recalibration)."""

    def __init__(self, base, bias):
        super().__init__(base.labels, base.weights)  # SHARES base weights (read-only use); NO retrain
        self.bias = dict(bias)
        self.feat_fn = arc_features

    def _predict_label(self, feats):
        best_l = self.labels[0]
        best_s = float("-inf")
        for lab in self.labels:
            s = self._score(feats, lab) + self.bias.get(lab, 0.0)
            if s > best_s:
                best_s = s
                best_l = lab
        return best_l


class RobustLabeler(ArcLabeler):
    """Retrained labeler using register-invariant features (feat_fn); own weights."""

    def __init__(self, labels, weights, feat_fn):
        super().__init__(labels, weights)
        self.feat_fn = feat_fn

    def label(self, tokens, pos, heads):
        out = {}
        n = len(tokens)
        for i in range(1, n + 1):
            h = heads.get(i, 0)
            if h is None or h < 0 or h > n:
                h = 0
            out[i] = self._predict_label(self.feat_fn(tokens, pos, i, h))
        return out

    def label_accuracy(self, gold_sents, maxlen=50):
        c = t = 0
        for s in gold_sents:
            if not (1 <= len(s) <= maxlen):
                continue
            tokens = [x[1] for x in s]
            pos = [x[2] for x in s]
            for i in range(1, len(s) + 1):
                gh = s[i - 1][3]
                if gh < 0 or gh > len(s):
                    continue
                pred = self._predict_label(self.feat_fn(tokens, pos, i, gh))
                c += int(pred == norm_label(s[i - 1][4]))
                t += 1
        return (c / t if t else 0.0, c, t)


def train_robust(train_sents, epochs, seed, maxlen=50, min_label_count=30):
    """Averaged multiclass perceptron (same discipline as hdlab.train_label) using arc_features_robust."""
    train = [s for s in train_sents if 1 <= len(s) <= maxlen]
    freq = defaultdict(int)
    for s in train:
        for tt in s:
            if 0 <= tt[3] <= len(s):
                freq[norm_label(tt[4])] += 1
    keep = {lab for lab, c in freq.items() if c >= min_label_count}
    keep |= {"obj", "nsubj", "nsubj:pass", "obl", "obl:agent", "iobj", "dep", "root"}
    labels = sorted(keep)

    def lab_of(deprel):
        nl = norm_label(deprel)
        return nl if nl in keep else "dep"

    data = []
    for s in train:
        tokens = [tt[1] for tt in s]
        pos = [tt[2] for tt in s]
        arcs = []
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > len(s):
                continue
            arcs.append((arc_features_robust(tokens, pos, i, gh), lab_of(s[i - 1][4])))
        data.append(arcs)

    w = defaultdict(float)
    cw = defaultdict(float)
    c = 1
    rng = np.random.default_rng(seed)
    lab = RobustLabeler(labels, None, arc_features_robust)
    lab.weights = w  # share the LIVE dict during training (ArcLabeler.__init__ COPIES weights; must reassign)
    for ep in range(epochs):
        for si in rng.permutation(len(data)):
            for feats, gold in data[si]:
                pred = lab._predict_label(feats)
                if pred != gold:
                    for f in feats:
                        kg = f + "~" + gold
                        kp = f + "~" + pred
                        w[kg] += 1.0
                        cw[kg] += c
                        w[kp] -= 1.0
                        cw[kp] -= c
                c += 1
    averaged = {f: w[f] - cw[f] / c for f in w}
    return RobustLabeler(labels, averaged, arc_features_robust)


# ==============================================================================================
# Phase-1: obj-row confusion (in-domain UD gold-heads vs out-of-domain McGuffey parser-heads-correct-attach).
# ==============================================================================================
def confusion_indomain(labeler, ud_sents, maxlen=50):
    """Per patient-relevant gold-label: predicted-label distribution under GOLD heads (isolates labeling)."""
    conf = {r: Counter() for r in PATIENT_ROLE_ROWS}
    feat_fn = getattr(labeler, "feat_fn", arc_features)
    for s in ud_sents:
        if not (1 <= len(s) <= maxlen):
            continue
        tokens = [t[1] for t in s]
        pos = [t[2] for t in s]
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > len(s):
                continue
            gold = norm_label(s[i - 1][4])
            if gold not in PATIENT_ROLE_ROWS:
                continue
            conf[gold][labeler._predict_label(feat_fn(tokens, pos, i, gh))] += 1
    return _summ_conf(conf)


def confusion_mcguffey(labeler, gen, order, sent_text, gold):
    """For each McGuffey gold patient: locate the patient arc; if correctly-attached (head==verb), tally the
    labeler's predicted label. Partition parser-attach-miss + token-not-found separately (isolates the labeler).
    'obj-row' here = the true patients (whatever their surface form); recovered = pred in {obj, nsubj:pass}."""
    pred_dist = Counter()
    n_attach_ok = n_attach_miss = n_token_missing = 0
    for sid in order:
        if sid not in gold:
            continue
        rec = gold[sid]
        parsed = gen.generate(sent_text[sid])
        toks, pos, heads = parsed.tokens, parsed.pos, parsed.heads
        if not toks:
            continue
        toks_lc = [t.lower() for t in toks]
        labels = labeler.label(toks, pos, heads)
        verb_tokens = [(i, L.lemma_verb(toks_lc[i - 1])) for i in range(1, len(toks) + 1) if pos[i - 1] == "VERB"]
        used = set()
        for g in rec["pos"]:
            vlem, patient = g["v"], g["patient"]
            vidx = next((i for (i, lm) in verb_tokens if lm == vlem and i not in used), None)
            if vidx is None:
                continue
            used.add(vidx)
            # candidate patient token indices (surface match), prefer the one attached to the target verb.
            occ = [k for k in range(1, len(toks) + 1) if toks_lc[k - 1] == patient]
            if not occ:
                n_token_missing += 1
                continue
            attached = [k for k in occ if heads.get(k) == vidx]
            if not attached:
                n_attach_miss += 1
                continue
            a = attached[0]
            n_attach_ok += 1
            pred_dist[labels.get(a)] += 1
    tot = sum(pred_dist.values())
    recovered = pred_dist.get("obj", 0) + pred_dist.get("nsubj:pass", 0)
    return {"n_patient_arcs_correctly_attached": n_attach_ok, "n_parser_attach_miss": n_attach_miss,
            "n_token_not_found": n_token_missing, "predicted_label_dist": dict(pred_dist.most_common()),
            "patient_tagged_obj_or_pass": recovered,
            "patient_role_recall": (round(recovered / tot, 4) if tot else None)}


def _summ_conf(conf):
    out = {}
    for role, ctr in conf.items():
        tot = sum(ctr.values())
        out[role] = {"n": tot, "dist": dict(ctr.most_common()),
                     "recall_as_self": (round(ctr.get(role, 0) / tot, 4) if tot else None)}
    # cross-cut: obj mis-routed to the diagnosis-named competitors
    ctr = conf["obj"]
    tot = sum(ctr.values())
    if tot:
        out["obj_confusion_summary"] = {
            "obj->obj": round(ctr.get("obj", 0) / tot, 4),
            "obj->obl": round(ctr.get("obl", 0) / tot, 4),
            "obj->nsubj": round(ctr.get("nsubj", 0) / tot, 4),
            "obj->iobj": round(ctr.get("iobj", 0) / tot, 4),
            "obj->ccomp": round(ctr.get("ccomp", 0) / tot, 4),
            "obj->dep": round(ctr.get("dep", 0) / tot, 4)}
    return out


# ==============================================================================================
# Phase-2: RECAL bias tuning on UD-EWT DEV (obj-F1, guarded by overall-label-acc non-regression).
# ==============================================================================================
def obj_prf_and_acc(labeler, ud_sents, maxlen=50):
    """obj precision/recall/F1 + overall label-acc under GOLD heads."""
    feat_fn = getattr(labeler, "feat_fn", arc_features)
    tp = fp = fn = 0
    corr = tot = 0
    for s in ud_sents:
        if not (1 <= len(s) <= maxlen):
            continue
        tokens = [t[1] for t in s]
        pos = [t[2] for t in s]
        for i in range(1, len(s) + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > len(s):
                continue
            gold = norm_label(s[i - 1][4])
            pred = labeler._predict_label(feat_fn(tokens, pos, i, gh))
            corr += int(pred == gold)
            tot += 1
            if gold == "obj" and pred == "obj":
                tp += 1
            elif gold != "obj" and pred == "obj":
                fp += 1
            elif gold == "obj" and pred != "obj":
                fn += 1
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"obj_precision": round(prec, 4), "obj_recall": round(rec, 4), "obj_f1": round(f1, 4),
            "label_acc": round(corr / tot, 4) if tot else None}


def tune_recal_bias(base, ud_dev, grid, acc_tol=0.01, maxlen=50):
    """Grid the obj-score bias on UD-EWT DEV; pick argmax obj-F1 subject to overall-acc drop <= acc_tol."""
    base_acc = obj_prf_and_acc(base, ud_dev, maxlen)["label_acc"]
    curve = []
    best = {"b": 0.0, "obj_f1": -1.0}
    for b in grid:
        lab = RecalLabeler(base, {"obj": float(b)})
        m = obj_prf_and_acc(lab, ud_dev, maxlen)
        row = {"b_obj": float(b), **m, "acc_drop": round(base_acc - m["label_acc"], 4)}
        curve.append(row)
        if (base_acc - m["label_acc"]) <= acc_tol and m["obj_f1"] > best["obj_f1"]:
            best = {"b": float(b), "obj_f1": m["obj_f1"]}
    return best["b"], base_acc, curve


# ==============================================================================================
# Small end-to-end helpers.
# ==============================================================================================
def mean_pool_size(pos_insts):
    ps = [len(i["cands"]) for i in pos_insts]
    return round(float(np.mean(ps)), 4) if ps else None


def _labeler_asset_hash():
    h = hashlib.sha256()
    with open(LABELER_PATH, "rb") as f:
        h.update(f.read())
    return h.hexdigest()[:16]


# ==============================================================================================
# Config.
# ==============================================================================================
def cfg_local(mode):
    if mode == "smoke":
        return dict(robust_train_sents=2500, robust_epochs=3, dev_cap=1500, test_cap=1500,
                    recal_grid=[0.0, 0.5, 1.0, 2.0, 4.0, 8.0])
    return dict(robust_train_sents=None, robust_epochs=8, dev_cap=None, test_cap=None,
                recal_grid=[0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0])


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = E.cfg_smoke() if mode == "smoke" else E.cfg_full()
    lcfg = cfg_local(mode)
    output_dir = _out_dir(mode)
    E._write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START slice={'+'.join(cfg['slice_lessons'])}", flush=True)

    from hdlab.candidate_generator import CandidateGenerator
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    orig = ArcLabeler.load(LABELER_PATH)
    orig.feat_fn = arc_features
    asset_hash_before = _labeler_asset_hash()
    print(f"[{ANCHOR_NAME}:{mode}] front-end loaded; labeler asset {asset_hash_before}", flush=True)

    # ---- UD-EWT held-out for in-domain confusion + regression + recal tuning ----
    ud_train = load_conllu("train")
    ud_dev = load_conllu("dev")
    ud_test = load_conllu("test")
    if lcfg["dev_cap"]:
        ud_dev = ud_dev[: lcfg["dev_cap"]]
    if lcfg["test_cap"]:
        ud_test = ud_test[: lcfg["test_cap"]]
    train_used = ud_train if lcfg["robust_train_sents"] is None else ud_train[: lcfg["robust_train_sents"]]

    # ---- PHASE 2 build the fixed labelers (UD-only supervision; McGuffey NEVER seen) ----
    b_obj, base_dev_acc, recal_curve = tune_recal_bias(orig, ud_dev, lcfg["recal_grid"])
    recal = RecalLabeler(orig, {"obj": b_obj})
    print(f"[{ANCHOR_NAME}:{mode}] RECAL b_obj={b_obj} (dev base_acc={base_dev_acc})", flush=True)
    robust = train_robust(train_used, epochs=lcfg["robust_epochs"], seed=1031)
    print(f"[{ANCHOR_NAME}:{mode}] ROBUST retrained on {len(train_used)} UD sents x{lcfg['robust_epochs']}ep",
          flush=True)

    # ---- PHASE 1 confusion (in-domain gold-heads) + in-domain label-acc regression per variant ----
    conf_in_orig = confusion_indomain(orig, ud_test)
    conf_in_recal = confusion_indomain(recal, ud_test)
    conf_in_robust = confusion_indomain(robust, ud_test)
    acc_orig = orig.label_accuracy(ud_test)[0]
    acc_recal = recal.label_accuracy(ud_test)[0]
    acc_robust = robust.label_accuracy(ud_test)[0]
    print(f"[{ANCHOR_NAME}:{mode}] IN-DOMAIN label-acc orig={round(acc_orig,4)} recal={round(acc_recal,4)} "
          f"robust={round(acc_robust,4)} | obj-recall orig={conf_in_orig['obj']['recall_as_self']} "
          f"recal={conf_in_recal['obj']['recall_as_self']} robust={conf_in_robust['obj']['recall_as_self']}",
          flush=True)

    # ---- McGuffey slice + gold ----
    order, sent_text, reader_svo = L.load_slice_and_reader(cfg["slice_lessons"])
    gold, gold_meta = L.load_gold(cfg["slice_lessons"])

    # PHASE 1 out-of-domain confusion (McGuffey patients, correctly-attached) per variant.
    conf_mcg_orig = confusion_mcguffey(orig, gen, order, sent_text, gold)
    conf_mcg_recal = confusion_mcguffey(recal, gen, order, sent_text, gold)
    conf_mcg_robust = confusion_mcguffey(robust, gen, order, sent_text, gold)
    dom_orig = conf_mcg_orig["patient_role_recall"]
    ind_orig = conf_in_orig["obj"]["recall_as_self"]
    domain_shift = bool(dom_orig is not None and ind_orig is not None and (ind_orig - dom_orig) >= 0.10)
    print(f"[{ANCHOR_NAME}:{mode}] DOMAIN-SHIFT check: in-domain obj-recall={ind_orig} vs "
          f"McGuffey patient-role-recall={dom_orig} -> domain_shift={domain_shift}", flush=True)

    # discriminator-fires: RECAL/ROBUST must change >=1 McGuffey patient label vs ORIGINAL.
    recal_fires = conf_mcg_recal["predicted_label_dist"] != conf_mcg_orig["predicted_label_dist"]
    robust_fires = conf_mcg_robust["predicted_label_dist"] != conf_mcg_orig["predicted_label_dist"]

    # ---- mining (reuse IV) ----
    iv_cfg = IV.cfg_smoke() if mode == "smoke" else IV.cfg_full()
    gfit_fn, sel_fn, gfit_stats, n_mine = IV.build_mining_models(iv_cfg, output_dir)
    print(f"[{ANCHOR_NAME}:{mode}] mining: {gfit_stats['n_object_classes']} gfit classes, {n_mine} sents", flush=True)

    # ---- PHASE 3 build instances (ONE-VARIABLE = the labeler) ----
    unlab = HARD.build_instances(order, sent_text, gold, gen, orig, gfit_fn, sel_fn, "unlabeled")
    v1 = HARD.build_instances(order, sent_text, gold, gen, orig, gfit_fn, sel_fn, "labeled_v1")
    backoff = HARD.build_instances(order, sent_text, gold, gen, orig, gfit_fn, sel_fn, "labeled_backoff")
    recal_ins = HARD.build_instances(order, sent_text, gold, gen, recal, gfit_fn, sel_fn, "labeled_v1")
    robust_ins = HARD.build_instances(order, sent_text, gold, gen, robust, gfit_fn, sel_fn, "labeled_v1")

    v1_pos = [i for i in v1 if i["is_pos"]]
    n_pos = len(v1_pos)
    ceil = {"unlabeled": E.gold_in_pool_rate([i for i in unlab if i["is_pos"]])[0],
            "v1": E.gold_in_pool_rate(v1_pos)[0],
            "backoff": E.gold_in_pool_rate([i for i in backoff if i["is_pos"]])[0],
            "recal": E.gold_in_pool_rate([i for i in recal_ins if i["is_pos"]])[0],
            "robust": E.gold_in_pool_rate([i for i in robust_ins if i["is_pos"]])[0]}
    pool = {"v1": mean_pool_size(v1_pos),
            "backoff": mean_pool_size([i for i in backoff if i["is_pos"]]),
            "recal": mean_pool_size([i for i in recal_ins if i["is_pos"]]),
            "robust": mean_pool_size([i for i in robust_ins if i["is_pos"]])}
    hard_frac = round(sum(1 for i in v1_pos if i["construction"] != "simple") / n_pos, 4) if n_pos else None
    leak_recal = E.giveaway_audit([i for i in recal_ins if i["is_pos"]])
    leak_robust = E.giveaway_audit([i for i in robust_ins if i["is_pos"]])
    print(f"[{ANCHOR_NAME}:{mode}] gold POS={n_pos} hard_frac={hard_frac} CEILING(recall) {ceil} "
          f"POOLSIZE {pool}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] LEAK recal max_cue={leak_recal['max_single_feature_gold_selection_acc']} "
          f"leak={leak_recal['leak']} | robust max_cue={leak_robust['max_single_feature_gold_selection_acc']} "
          f"leak={leak_robust['leak']}", flush=True)

    per_seed = []
    v1_digests, recal_digests, robust_digests = {}, {}, {}
    for seed in cfg["seeds"]:
        tr_v, te_v = E.verb_split(gold, seed, cfg["frac_train"])
        w_unlab, _, _ = IV.train_vote(E.sel_by_verb(unlab, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])
        w_v1, _, _ = IV.train_vote(E.sel_by_verb(v1, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])
        w_bk, _, _ = IV.train_vote(E.sel_by_verb(backoff, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])
        w_rc, _, _ = IV.train_vote(E.sel_by_verb(recal_ins, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])
        w_rb, _, _ = IV.train_vote(E.sel_by_verb(robust_ins, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])

        unlab_te = [i for i in E.sel_by_verb(unlab, te_v) if i["is_pos"]]
        v1_te = [i for i in E.sel_by_verb(v1, te_v) if i["is_pos"]]
        bk_te = [i for i in E.sel_by_verb(backoff, te_v) if i["is_pos"]]
        rc_te = [i for i in E.sel_by_verb(recal_ins, te_v) if i["is_pos"]]
        rb_te = [i for i in E.sel_by_verb(robust_ins, te_v) if i["is_pos"]]

        acc_unlab, _ = E.endtoend_accuracy(w_unlab, unlab_te)
        acc_v1, ntp = E.endtoend_accuracy(w_v1, v1_te)
        acc_bk, _ = E.endtoend_accuracy(w_bk, bk_te)
        acc_rc, _ = E.endtoend_accuracy(w_rc, rc_te)
        acc_rb, _ = E.endtoend_accuracy(w_rb, rb_te)

        v1_digests[seed] = hashlib.sha256(np.round(w_v1, 6).tobytes()).hexdigest()[:16]
        recal_digests[seed] = hashlib.sha256(np.round(w_rc, 6).tobytes()).hexdigest()[:16]
        robust_digests[seed] = hashlib.sha256(np.round(w_rb, 6).tobytes()).hexdigest()[:16]

        row = {"seed": seed, "n_test_pos": ntp,
               "unlabeled_endtoend": acc_unlab, "v1_endtoend": acc_v1, "backoff_endtoend": acc_bk,
               "recal_endtoend": acc_rc, "robust_endtoend": acc_rb,
               "gain_recal_vs_v1": round((acc_rc or 0) - (acc_v1 or 0), 4),
               "gain_robust_vs_v1": round((acc_rb or 0) - (acc_v1 or 0), 4),
               "gain_backoff_vs_v1": round((acc_bk or 0) - (acc_v1 or 0), 4),
               "test_ceiling_v1": E.gold_in_pool_rate(v1_te)[0],
               "test_ceiling_recal": E.gold_in_pool_rate(rc_te)[0],
               "test_ceiling_robust": E.gold_in_pool_rate(rb_te)[0],
               "residual_partition_v1": HARD.residual_partition(w_v1, v1_te),
               "residual_partition_recal": HARD.residual_partition(w_rc, rc_te),
               "residual_partition_robust": HARD.residual_partition(w_rb, rb_te),
               "per_construction_v1": E.per_construction_endtoend(w_v1, v1_te),
               "per_construction_recal": E.per_construction_endtoend(w_rc, rc_te),
               "per_construction_robust": E.per_construction_endtoend(w_rb, rb_te)}
        per_seed.append(row)
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} UNLAB={acc_unlab} V1={acc_v1} BACKOFF={acc_bk} "
              f"RECAL={acc_rc}(g={row['gain_recal_vs_v1']:+.3f}) ROBUST={acc_rb}(g={row['gain_robust_vs_v1']:+.3f})",
              flush=True)

    def mean(key):
        vals = [s[key] for s in per_seed if s.get(key) is not None]
        return round(float(np.mean(vals)), 4) if vals else None

    def minv(key):
        vals = [s[key] for s in per_seed if s.get(key) is not None]
        return round(float(np.min(vals)), 4) if vals else None

    m = {k: mean(k) for k in ("unlabeled_endtoend", "v1_endtoend", "backoff_endtoend",
                              "recal_endtoend", "robust_endtoend",
                              "gain_recal_vs_v1", "gain_robust_vs_v1", "gain_backoff_vs_v1")}
    min_gain_recal = minv("gain_recal_vs_v1")
    min_gain_robust = minv("gain_robust_vs_v1")

    # best fix by mean end-to-end
    fixes = {"recal": (m["recal_endtoend"], min_gain_recal, ceil["recal"], pool["recal"], acc_recal, leak_recal),
             "robust": (m["robust_endtoend"], min_gain_robust, ceil["robust"], pool["robust"], acc_robust, leak_robust)}
    best_name = max(fixes, key=lambda k: (fixes[k][0] if fixes[k][0] is not None else -1))
    best_e2e, best_min_gain, best_recall, best_pool, best_indom_acc, best_leak = fixes[best_name]
    v1_e2e = m["v1_endtoend"]
    v1_recall = ceil["v1"]
    v1_pool = pool["v1"]

    def agg_partition(subkey):
        ext = sum(s[subkey]["extraction_err"] for s in per_seed)
        dec = sum(s[subkey]["decision_err"] for s in per_seed)
        cor = sum(s[subkey]["correct"] for s in per_seed)
        resid = ext + dec
        return {"correct": cor, "extraction_err": ext, "decision_err": dec, "residual": resid,
                "ext_to_dec_ratio": f"{ext}:{dec}",
                "extraction_frac_of_residual": (round(ext / resid, 4) if resid else None)}

    part_v1 = agg_partition("residual_partition_v1")
    part_recal = agg_partition("residual_partition_recal")
    part_robust = agg_partition("residual_partition_robust")

    def per_constr_agg(subkey):
        acc = defaultdict(list)
        gip = defaultdict(list)
        for s in per_seed:
            for c, d in s[subkey].items():
                if d["endtoend_acc"] is not None:
                    acc[c].append(d["endtoend_acc"])
                if d["gold_in_pool"] is not None:
                    gip[c].append(d["gold_in_pool"])
        return {c: {"mean_endtoend_acc": round(float(np.mean(acc[c])), 4) if acc[c] else None,
                    "mean_gold_in_pool": round(float(np.mean(gip[c])), 4) if gip[c] else None}
                for c in sorted(set(list(acc) + list(gip)))}

    baseline_in_band = bool(v1_e2e is not None and 0.05 < v1_e2e < 0.95
                            and m["unlabeled_endtoend"] is not None and 0.05 < m["unlabeled_endtoend"] < 0.95)
    arms_differ = bool(recal_fires or robust_fires) and all(
        v1_digests[s] != recal_digests[s] or v1_digests[s] != robust_digests[s] for s in cfg["seeds"])
    indom_drop_recal = round((acc_orig - acc_recal), 4)
    indom_drop_robust = round((acc_orig - acc_robust), 4)
    best_indom_drop = round((acc_orig - best_indom_acc), 4)
    leak_clean = bool(not best_leak["leak"])

    recall_up = bool(best_recall is not None and v1_recall is not None and best_recall >= v1_recall - 1e-9)
    precision_ok = bool(best_pool is not None and v1_pool is not None and best_pool <= v1_pool + 0.15)
    coupling_broken = bool(best_e2e is not None and v1_e2e is not None and best_e2e >= v1_e2e + 0.02
                           and recall_up and precision_ok and (best_min_gain or -1) >= 0 and leak_clean
                           and best_indom_drop <= 0.01)

    if v1_e2e is None or best_e2e is None:
        verdict = "UNKNOWN_NO_SEEDS"
    elif coupling_broken:
        verdict = "HARD_PASS_LABELER_FIX_BREAKS_COUPLING"
    elif best_e2e < v1_e2e - 0.01 or (indom_drop_recal > 0.02 and indom_drop_robust > 0.02):
        verdict = "HARD_FAIL_LABELER_FIX_HURTS"
    else:
        verdict = "MIDDLE_BAND"

    asset_hash_after = _labeler_asset_hash()
    asset_untouched = bool(asset_hash_before == asset_hash_after)

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | slice={'+'.join(cfg['slice_lessons'])} gold_pos={n_pos} hard_frac={hard_frac} "
           f"| PHASE1 domain_shift={domain_shift} (in-domain obj-recall={ind_orig} McGuffey patient-role-recall="
           f"{dom_orig}; obj_confusion={conf_in_orig.get('obj_confusion_summary')}) "
           f"| PHASE3 END-TO-END UNLAB={m['unlabeled_endtoend']} V1(baseline)={v1_e2e} BACKOFF={m['backoff_endtoend']}"
           f"(g={m['gain_backoff_vs_v1']:+.3f}) RECAL={m['recal_endtoend']}(g={m['gain_recal_vs_v1']:+.3f},min="
           f"{min_gain_recal}) ROBUST={m['robust_endtoend']}(g={m['gain_robust_vs_v1']:+.3f},min={min_gain_robust}) "
           f"| best_fix={best_name} recall {v1_recall}->{best_recall} pool {v1_pool}->{best_pool} "
           f"coupling_broken={coupling_broken} recall_up={recall_up} precision_ok={precision_ok} "
           f"| IN-DOMAIN label-acc orig={round(acc_orig,4)} recal={round(acc_recal,4)}(drop={indom_drop_recal}) "
           f"robust={round(acc_robust,4)}(drop={indom_drop_robust}) "
           f"| RESIDUAL v1 ext:dec={part_v1['ext_to_dec_ratio']} best ext:dec="
           f"{(part_recal if best_name=='recal' else part_robust)['ext_to_dec_ratio']} "
           f"| recal_b_obj={b_obj} recal_fires={recal_fires} robust_fires={robust_fires} "
           f"baseline_in_band={baseline_in_band} arms_differ={arms_differ} leak_clean={leak_clean} "
           f"asset_untouched={asset_untouched}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": cfg["seeds"], "slice_lessons": cfg["slice_lessons"], "n_gold_pos_pairs": n_pos,
        "hard_frac": hard_frac,
        "PHASE1_domain_shift": domain_shift,
        "PHASE1_in_domain_obj_recall": ind_orig,
        "PHASE1_mcguffey_patient_role_recall": dom_orig,
        "PHASE1_confusion_in_domain_orig": conf_in_orig,
        "PHASE1_confusion_in_domain_recal": conf_in_recal,
        "PHASE1_confusion_in_domain_robust": conf_in_robust,
        "PHASE1_confusion_mcguffey_orig": conf_mcg_orig,
        "PHASE1_confusion_mcguffey_recal": conf_mcg_recal,
        "PHASE1_confusion_mcguffey_robust": conf_mcg_robust,
        "PHASE2_recal_b_obj": b_obj, "PHASE2_recal_dev_base_acc": base_dev_acc, "PHASE2_recal_curve": recal_curve,
        "PHASE2_robust_train_sents": len(train_used), "PHASE2_robust_epochs": lcfg["robust_epochs"],
        "PHASE3_endtoend_mean": m,
        "PHASE3_gain_recal_vs_v1_min": min_gain_recal, "PHASE3_gain_robust_vs_v1_min": min_gain_robust,
        "candidate_recall_ceiling": ceil, "mean_pool_size": pool,
        "IN_DOMAIN_label_acc": {"orig": round(acc_orig, 4), "recal": round(acc_recal, 4),
                                "robust": round(acc_robust, 4),
                                "recal_drop": indom_drop_recal, "robust_drop": indom_drop_robust},
        "best_fix": best_name, "coupling_broken": coupling_broken, "recall_up": recall_up,
        "precision_ok": precision_ok,
        "RESIDUAL_PARTITION_v1": part_v1, "RESIDUAL_PARTITION_recal": part_recal,
        "RESIDUAL_PARTITION_robust": part_robust,
        "per_construction_v1": per_constr_agg("per_construction_v1"),
        "per_construction_recal": per_constr_agg("per_construction_recal"),
        "per_construction_robust": per_constr_agg("per_construction_robust"),
        "baseline_in_band": baseline_in_band, "arms_differ_verified": arms_differ,
        "recal_fires": recal_fires, "robust_fires": robust_fires,
        "leak_guard_recal": leak_recal, "leak_guard_robust": leak_robust, "leak_clean_best": leak_clean,
        "labeler_asset_hash_before": asset_hash_before, "labeler_asset_hash_after": asset_hash_after,
        "labeler_asset_untouched": asset_untouched,
        "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "end-to-end + label-accuracy measurement",
        "calibration_check": "adaptive_with_discriminator_gate: RECAL b_obj tuned on UD-EWT DEV by obj-F1, "
                             "guarded by overall-label-acc non-regression; ROBUST features register-invariant",
        "progress_logging": "print_flush_true", "compute_architecture": "sequential-CPU (justified)",
        "deterministic_seeding": True, "gold_meta": gold_meta, "per_seed": per_seed,
    }
    E.write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


def self_test():
    print("=== labeler_patient_role_recalibration self-test (real code paths) ===", flush=True)
    from hdlab.candidate_generator import CandidateGenerator
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    orig = ArcLabeler.load(LABELER_PATH)
    orig.feat_fn = arc_features
    h0 = _labeler_asset_hash()

    # (1) robust features are register-invariant: prep-governed obl vs prep-free post-verbal direct object differ.
    r = gen.generate("He showed him the seeds.")
    tl = [t.lower() for t in r.tokens]
    vidx = next(i for i in range(1, len(r.tokens) + 1) if r.pos[i - 1] == "VERB")
    seeds_i = tl.index("seeds") + 1
    fr = arc_features_robust(r.tokens, r.pos, seeds_i, vidx)
    assert any(x == "rb_pvdirect:1" for x in fr), "self-test FAIL: post-verbal direct obj did not fire rb_pvdirect"
    r2 = gen.generate("The cat rubbed against the wall.")
    tl2 = [t.lower() for t in r2.tokens]
    v2 = next(i for i in range(1, len(r2.tokens) + 1) if r2.pos[i - 1] == "VERB")
    wall_i = tl2.index("wall") + 1
    fr2 = arc_features_robust(r2.tokens, r2.pos, wall_i, v2)
    assert any(x == "rb_govprep:1" for x in fr2), "self-test FAIL: prep-governed oblique did not fire rb_govprep"
    assert not any(x == "rb_pvdirect:1" for x in fr2), "self-test FAIL: prep-governed oblique wrongly pvdirect"

    # (2) train a TINY robust labeler on a UD subset; RobustLabeler.label runs + persistence-free.
    ud = load_conllu("train")[:400]
    rob = train_robust(ud, epochs=2, seed=1031, min_label_count=5)
    labs = rob.label(r.tokens, r.pos, r.heads)
    assert isinstance(labs, dict) and len(labs) == len(r.tokens), "self-test FAIL: RobustLabeler.label shape"
    accr = rob.label_accuracy(load_conllu("test")[:100])[0]
    assert accr is not None, "self-test FAIL: RobustLabeler.label_accuracy"

    # (3) recal wrapper adds bias; a large b_obj must NOT decrease obj predictions on dev.
    dev = load_conllu("dev")[:300]
    m0 = obj_prf_and_acc(orig, dev)
    mbig = obj_prf_and_acc(RecalLabeler(orig, {"obj": 1000.0}), dev)
    assert mbig["obj_recall"] >= m0["obj_recall"], "self-test FAIL: obj bias did not raise obj-recall"
    b, base_acc, curve = tune_recal_bias(orig, dev, [0.0, 1.0, 4.0], acc_tol=0.02)
    assert len(curve) == 3 and base_acc is not None, "self-test FAIL: recal tuning curve"

    # (4) gold-independence: neither labeler constructor takes a McGuffey-gold argument.
    for fn in (RecalLabeler.__init__, train_robust):
        params = set(inspect.signature(fn).parameters)
        assert "gold" not in params and "patient" not in params, f"self-test FAIL: {fn} sees gold (LEAK)"

    # (5) confusion helpers run on a tiny slice.
    order, sent_text, _ = L.load_slice_and_reader(["L04"])
    gold, _ = L.load_gold(["L04"])
    cm = confusion_mcguffey(orig, gen, order, sent_text, gold)
    assert "patient_role_recall" in cm, "self-test FAIL: confusion_mcguffey shape"
    ci = confusion_indomain(orig, dev)
    assert "obj" in ci, "self-test FAIL: confusion_indomain shape"

    # (6) canonical labeler asset NEVER overwritten by any of the above.
    assert _labeler_asset_hash() == h0, "self-test FAIL: canonical labeler asset was modified (store write)"
    print("[selftest] PASS: robust features + robust/recal labelers + confusion + gold-independence + "
          "asset-untouched all exercised", flush=True)
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
        E._write_crash_metrics(output_dir, e)
        raise
