"""INTEGRATED weighted-vote role decision on PARSER-INDEPENDENT oracle gold-pairs (Step 2).

QUESTION (the real science): does INTEGRATING multiple role cues in ONE jointly-trained logistic vote beat
  the BEST SINGLE cue? Every prior reader cell tested cues ONE AT A TIME (the ~0.557 / 29375 wall). This
  cell MERGES the three already-built-but-never-jointly-trained cue families into one feature vector and
  measures whether integration is COMPLEMENTARY (beats best-single) or REDUNDANT (word-order already
  captures it). Brain-check (MacWhinney & Bates Competition Model, CITED@research note) warns English is
  WORD-ORDER-DOMINANT, so redundancy is the pre-registered MOST-LIKELY outcome (P=0.35, a genuine can-fail).

REUSE (nothing rebuilt from scratch; the three half-built pieces named in the design note):
  - exp_learned_argstruct_parser_lccp_independent_gold_v1 (L): 6 crude STRUCTURAL cues + candidate_features
    + find_pair_positions + build_semantic_teacher (GloVe selectional-coherence) + run_arms (the crude
    reader baseline, reproduced LIVE) + score_arm (P/R/F1 vs the same independent gold) + lexicons.
  - exp_graded_thematic_fit_integrated_reader_gate_v1 (G): build_gfit_model (VerbNet-supersense +
    class-smoothed distributional object-typicality, Clark & Weir 2002) = the graded thematic-fit cue.
  - exp_explicit_grammar_role_assigner_lccp_gold_v1 (EG): detect_passive (passive-flip / UD obl:agent),
    prep_sense / PREP_SENSE / PATIENT_ALLOWED_SENSES / NON_PATIENT_SENSES, ALTERNATING_VERBS.
  - exp_scene_coherence_verifier_contrastive_scv_v1 (SCV): mining-corpus reader run (gfit + teacher are
    built on the MINING corpus; the McGuffey GOLD source is EXCLUDED from mining -> no ground-by-X-grade-by-X).
  - hdlab.conformal (calibrate_quantile): split-conformal calibrated abstain (atom 29367 machinery, reused).

PARSER-INDEPENDENT ORACLE PAIRS: the decision runs on ORACLE candidate pools built directly from the gold
  (data/gold_mcguffey_lccp_argstruct_v1.json). For each gold verb-instance the candidate patient set = the
  sentence's content-noun/pronoun heads (funcwords + bare prepositions removed), with the GOLD patient
  GUARANTEED present -> extraction is PERFECT, so the cell isolates the DECISION from extraction noise.

FEATURE VECTOR (12-dim, ONE jointly-trained logistic; FEATURE_NAMES below):
  [bias, f_adj, f_postv, f_prep, f_func, f_clause,          # 6 crude LCCP structural (word-order family)
   f_passive_flip,                                          # EG passive detector -> continuous feature
   f_prep_patient_sense, f_prep_nonpatient_sense,          # EG prep-SENSE (replaces crude binary f_prep)
   f_alternation,                                           # EG locative-alternation frame (signed {-1,0,+1})
   f_gfit,                                                  # G graded thematic-fit / type-facts
   f_plaus]                                                 # L GloVe selectional coherence, PROMOTED to a
                                                            #   vote FEATURE (was only the teacher signal)

McGUFFEY 0-GRAMMAR-INCIDENCE CAVEAT (stated in metrics, load-bearing): the coverage audit shows McGuffey has
  0 by-agent passives and 0 preposition-governed gold patients -> the f_passive_flip + f_prep_*_sense +
  f_alternation cues have ZERO incidence on THIS data and CANNOT contribute here. On THIS corpus the test
  only adjudicates WORD-ORDER vs GRADED-FIT vs PLAUSIBILITY. The zero-incidence cues are reported as
  UNTESTED-HERE, NOT "useless" (see grammar_zero_incidence_caveat in metrics). A CANARY of synthetic
  passive/alternation sentences proves those cues FIRE (mechanism real, corpus-independent).

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (1) REAL baseline, two-part: (i) BEST-SINGLE-CUE standalone precision per cue (recovers the one-at-a-time
      wall; expected word-order-dominated); (ii) the crude multi-cue LCCP reader reproduced LIVE via
      L.run_arms on the SAME oracle pools (not a remembered number).
  (2) CAN-FAIL: integration may NOT beat best-single-cue (REDUNDANCY, the live risk).
  (3) DIFFICULTY-ON as separate slices: CUE-CONFLICT (>=2 cues disagree on the top candidate),
      GENUINE-AMBIGUITY (near-tied margin -> abstain candidates), GRAMMAR-RESOLVABLE (EG coverage audit).
  (4) ONE VARIABLE: word-order-only VOTE vs full-integrated VOTE (same oracle pools, same supervised
      training protocol, same verb-disjoint splits, same seeds); the only difference is the feature MASK.
  (5) LEARNING CURVE: vary the fraction of oracle TRAIN pairs used to fit the joint weights (flexible/
      improving property; rising@100% => data-gated, flat => cue-set-gated).

VERDICT BANDS (pre-registered):
  HARD_PASS_INTEGRATION_COMPLEMENTARY: full-vote TEST precision >= best-single-cue + 0.05 AND >= crude
    reader + 0.02, min-over-seeds gain > 0 (consistent sign).
  HARD_FAIL_CUES_REDUNDANT: full-vote precision <= best-single-cue (the 29375-family wall reasserts on clean
    oracle pairs; the pre-registered MOST-LIKELY outcome per the brain-check).
  MIDDLE_BAND: 0 < gain < 0.05, OR gain concentrates only in the (near-empty here) grammar-resolvable subset.
  ABSTAIN sub-verdict (secondary; reuses conformal): HARD_PASS if abstain raises forced-choice precision by
    >= 0.02 at realized abstain rate <= 0.35 on the cue-conflict subset, CAL->TEST verb-disjoint.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- ~100 sentences of gold + a mining pass
  for gfit/teacher (SCV reader ~0.1 s/sent, cached); the logistic votes are 12-dim delta-rule fits over a
  few hundred candidates (<1s each). Total wall < ~120s smoke / < ~240s full. Storage: no_storage
  (decision-precision measurement). progress_logging: print_flush_true. Determinism: OMP/MKL/OPENBLAS=1,
  fixed int seeds, numpy default_rng, sorted(set); NO hash()-seeded RNG. LOCAL-ONLY, foreground-to-
  completion; NO queue, NO push, NO remote-persist, NO git add -A (per task).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke (word-order-only vs full-integrated weight vectors bit-differ per seed;
    canary proves the zero-incidence grammar cues fire independent of corpus coverage).
  - final_metrics_atomicity: tmp_replace
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: decision-precision measurement; no quantitative noise floor for the discriminator.
  - baseline_in_band at smoke (best-single-cue precision strictly inside (0.05, 0.95)).
  - discriminator survives scale: smoke runs the SAME verdict logic; full re-verifies over 3 seeds.
  - HARD_PASS strictly above floor (+0.05 over best-single-cue; not an at-floor tie).
  - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
  - deterministic_seeding: fixed ints + default_rng + sorted(set); no hash()/list(set()) ordering.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "integrated_vote_role_decision_oracle_gold_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_graded_thematic_fit_integrated_reader_gate_v1 as G  # noqa: E402
from experiments import exp_explicit_grammar_role_assigner_lccp_gold_v1 as EG  # noqa: E402
from experiments import exp_scene_coherence_verifier_contrastive_scv_v1 as SCV  # noqa: E402

FEATURE_NAMES = ["bias", "f_adj", "f_postv", "f_prep", "f_func", "f_clause",
                 "f_passive_flip", "f_prep_patient_sense", "f_prep_nonpatient_sense",
                 "f_alternation", "f_gfit", "f_plaus", "f_passive_subject"]
D = len(FEATURE_NAMES)
# Index groups for the ONE-VARIABLE comparison + single-cue baselines.
IDX_BIAS = 0
IDX_WORDORDER = [0, 1, 2]                 # bias + f_adj + f_postv  (word-order-only vote)
IDX_STRUCTURAL = [0, 1, 2, 3, 4, 5]       # the 6 crude LCCP structural cues (crude multi-cue vote)
IDX_ALL = list(range(D))                  # full integrated vote
# Single-cue standalone rankers: (name, feat_index, direction) where +1 = argmax(more-patient),
# -1 = argmin (cue signals NON-patient, e.g. prep-governed / funcword).
SINGLE_CUES = [
    ("f_postv", 2, +1), ("f_adj", 1, +1), ("f_prep", 3, -1), ("f_func", 4, -1),
    ("f_prep_patient_sense", 7, +1), ("f_gfit", 10, +1), ("f_plaus", 11, +1),
]


# ----------------------------------------------------------------------------------------------
# Extended 12-dim feature for one (v_surf, agent, p) candidate.
# ----------------------------------------------------------------------------------------------
def extended_features(toks, v_surf, p, v_lemma, gfit_fn, sel_fn):
    """Return (feat[12], meta). Reuses L.candidate_features (6 structural) + EG grammar signals +
    G gfit + L GloVe plausibility. Pure function of tokens + the two mining-built models."""
    feat6, _pos = L.candidate_features(toks, v_surf, p)
    iv, ip = L.find_pair_positions(toks, v_surf, p)
    passive = EG.detect_passive(toks, iv, v_surf) if iv is not None else False
    prev1 = toks[ip - 1] if (ip is not None and ip - 1 >= 0) else ""
    prev2 = toks[ip - 2] if (ip is not None and ip - 2 >= 0) else ""
    governing_prep = prev1 if prev1 in L.PREPS else (prev2 if prev2 in L.PREPS else None)

    f_passive_flip = 1.0 if (passive and governing_prep == "by") else 0.0
    sense = EG.prep_sense(governing_prep) if governing_prep else None
    f_prep_patient = 1.0 if sense in EG.PATIENT_ALLOWED_SENSES else 0.0
    f_prep_nonpatient = 1.0 if sense in EG.NON_PATIENT_SENSES else 0.0

    # locative-alternation frame (VerbNet-style): with-frame bare NP = holistic patient (+1);
    # a with/onto/into-governed NP in an alternating verb's frame = non-patient (-1); else 0.
    f_alt = 0.0
    if v_lemma in EG.ALTERNATING_VERBS and governing_prep in ("with", "onto", "into"):
        f_alt = -1.0
    elif v_lemma in EG.ALTERNATING_VERBS and ip is not None and iv is not None and ip > iv \
            and governing_prep is None:
        f_alt = 1.0

    # PASSIVE-SUBJECT positive signal (the passive RESCUE): in a detected passive clause, a pre-verbal,
    # non-prep-governed noun head is the AFFECTED nsubj:pass subject (the true patient) -- exactly the case
    # word-order-alone gets WRONG (word-order favours the post-verbal by-agent). Zero on active clauses.
    f_passive_subject = 1.0 if (passive and ip is not None and iv is not None and ip < iv
                                and governing_prep is None) else 0.0

    g, kind = gfit_fn(v_lemma, p)
    f_gfit = float(g) if g is not None else 0.5
    gfit_defined = g is not None
    s = sel_fn(v_lemma, p)
    f_plaus = float(s) if s is not None else 0.0

    feat = np.array([feat6[0], feat6[1], feat6[2], feat6[3], feat6[4], feat6[5],
                     f_passive_flip, f_prep_patient, f_prep_nonpatient, f_alt, f_gfit, f_plaus,
                     f_passive_subject], dtype=np.float64)
    meta = {"gfit_defined": bool(gfit_defined), "gfit_kind": kind, "prep_sense": sense,
            "governing_prep": governing_prep, "passive": bool(passive),
            "f_passive_flip": f_passive_flip, "f_alternation": f_alt,
            "f_passive_subject": f_passive_subject}
    return feat, meta


# ----------------------------------------------------------------------------------------------
# ORACLE candidate-pool construction from gold (extraction perfect; gold patient guaranteed present).
# ----------------------------------------------------------------------------------------------
def _surface_verb(toks, v_lemma):
    surfs = [t for t in toks if L.lemma_verb(t) == v_lemma]
    return surfs[0] if surfs else None


# Auxiliary / modal / copula verbs: NEVER a patient head, and gold-INDEPENDENT (fixed lexical set). Excluding
# them is safe (no gold patient is an aux, so no force-add asymmetry) and removes the pollution where an
# aux adjacent to the main verb (e.g. "was made") wins on raw proximity (f_adj) over the true patient.
_AUX_TOKENS = {"was", "were", "is", "are", "been", "being", "be", "am", "has", "have", "had", "having",
               "do", "does", "did", "doing", "will", "would", "shall", "should", "can", "could",
               "may", "might", "must", "ought"}


def _candidate_heads(toks):
    """Candidate argument tokens = all distinct alpha tokens EXCEPT auxiliaries/modals (uniform rule for
    gold and non-gold). Do NOT exclude funcwords/preps -- excluding them while force-adding a funcword/
    pronoun gold patient (e.g. 'i','that','which') would make f_func a by-construction GOLD GIVEAWAY
    (f_func=1 => gold). Auxiliaries ARE excluded because they are never patients and the exclusion is
    gold-independent (no leak) -- it removes the 'was/were/be' proximity distractor that otherwise wins on
    f_adj alone. f_func/f_prep stay honest cues the vote must LEARN to down-weight."""
    out = []
    seen = set()
    for t in toks:
        if t in seen:
            continue
        seen.add(t)
        if not t.replace("'", "").isalpha() or t in _AUX_TOKENS:
            continue
        out.append(t)
    return out


def build_oracle_instances(order, sent_text, gold, gfit_fn, sel_fn):
    """One dict per (sid, v_lemma) gold verb-instance with the ORACLE candidate pool.
    Returns list of instances: {sid, v_lemma, v_surf, agent, gold_patient(or None for nopat),
    is_pos, cands:[{p, feat, meta, is_gold}]}."""
    instances = []
    for sid in order:
        if sid not in gold:
            continue
        toks = L.tokenize(sent_text[sid])
        heads = _candidate_heads(toks)
        rec = gold[sid]
        used_verbs = set()
        # POS instances (a gold patient exists; correct decision = pick it).
        for g in rec["pos"]:
            v_lemma = g["v"]
            v_surf = _surface_verb(toks, v_lemma)
            if v_surf is None:
                continue
            used_verbs.add(v_lemma)
            patient = g["patient"]
            pool = sorted(set(heads) | {patient})
            cands = []
            for p in pool:
                if p == v_surf:
                    continue
                feat, meta = extended_features(toks, v_surf, p, v_lemma, gfit_fn, sel_fn)
                cands.append({"p": p, "feat": feat, "meta": meta, "is_gold": bool(p == patient)})
            if not any(c["is_gold"] for c in cands):
                continue  # gold patient not realizable as a token head -> skip (rare)
            instances.append({"sid": sid, "v_lemma": v_lemma, "v_surf": v_surf, "agent": g["agent"],
                              "gold_patient": patient, "is_pos": True, "cands": cands})
        # NOPAT instances (no gold patient; correct decision = keep NOTHING).
        for v_lemma in rec["nopat"]:
            if v_lemma in used_verbs or v_lemma in rec["pos_verbs"]:
                continue
            v_surf = _surface_verb(toks, v_lemma)
            if v_surf is None:
                continue
            cands = []
            for p in sorted(heads):
                if p == v_surf:
                    continue
                feat, meta = extended_features(toks, v_surf, p, v_lemma, gfit_fn, sel_fn)
                cands.append({"p": p, "feat": feat, "meta": meta, "is_gold": False})
            if cands:
                instances.append({"sid": sid, "v_lemma": v_lemma, "v_surf": v_surf, "agent": "",
                                  "gold_patient": None, "is_pos": False, "cands": cands})
    return instances


CONSTRUCTION_GOLD_PATH = os.path.join(REPO_ROOT, "data", "gold_construction_argstruct_ewt_v1",
                                      "gold_construction_argstruct_ewt_v1.json")


def build_construction_oracle_instances(gfit_fn, sel_fn):
    """ORACLE instances from the construction hard gold (UD-EWT, real by-agent passives / prep-governed /
    cue-conflict / relative / control). One patient per item (gold-parse-derived). Candidate pool = sentence
    content-token heads with the gold patient guaranteed present. Carries construction + split + ambiguity."""
    with open(CONSTRUCTION_GOLD_PATH, encoding="utf-8") as f:
        obj = json.load(f)
    insts = []
    for sid, item in obj["gold"].items():
        toks = L.tokenize(item["text"])
        v_form = item["verb"]["form"].lower()
        v_lemma = L.lemma_verb(item["verb"]["lemma"].lower())
        patient = item["patient"]["form"].lower()
        agent = (item.get("agent") or {}).get("form", "") or ""
        v_surf = v_form if v_form in toks else (_surface_verb(toks, v_lemma) or v_form)
        pool = sorted(set(_candidate_heads(toks)) | {patient})
        cands = []
        for p in pool:
            if p == v_surf:
                continue
            feat, meta = extended_features(toks, v_surf, p, v_lemma, gfit_fn, sel_fn)
            cands.append({"p": p, "feat": feat, "meta": meta, "is_gold": bool(p == patient)})
        if not any(c["is_gold"] for c in cands):
            feat, meta = extended_features(toks, v_surf, patient, v_lemma, gfit_fn, sel_fn)
            cands.append({"p": patient, "feat": feat, "meta": meta, "is_gold": True})
        insts.append({"sid": sid, "v_lemma": v_lemma, "v_surf": v_surf, "agent": agent.lower(),
                      "gold_patient": patient, "is_pos": True, "cands": cands,
                      "construction": item.get("construction"), "split": item.get("split"),
                      "genuine_ambiguity": bool(item.get("genuine_ambiguity")),
                      "cue_conflict": bool(item.get("cue_conflict"))})
    return insts, obj["_meta"]


# ----------------------------------------------------------------------------------------------
# Supervised logistic vote (delta-rule) over a feature MASK. Gold-supervised on TRAIN instances ONLY.
# ----------------------------------------------------------------------------------------------
def train_vote(train_insts, feat_idx, seed, epochs, lr, frac=1.0):
    rng = np.random.default_rng(seed)
    mask = np.zeros(D)
    for i in feat_idx:
        mask[i] = 1.0
    insts = list(train_insts)
    if frac < 1.0:
        k = max(1, int(round(frac * len(insts))))
        sel = rng.permutation(len(insts))[:k]
        insts = [insts[i] for i in sorted(sel.tolist())]
    work = []
    for inst in insts:
        for c in inst["cands"]:
            work.append((c["feat"] * mask, 1.0 if c["is_gold"] else 0.0))
    w = np.zeros(D)
    if not work:
        return w, 0, len(insts)
    for _ in range(epochs):
        for k in rng.permutation(len(work)):
            x, t = work[k]
            pred = L.sigmoid(float(np.dot(w, x)))
            w = w + lr * (t - pred) * x
    return w, len(work), len(insts)


def keep_best(w, insts, keep_thr):
    """keep single best candidate per instance iff sigmoid(score) >= keep_thr. Returns kept list of
    (sid, tup=(v_surf, agent, p)) and a per-instance decision log."""
    kept = []
    log = []
    for inst in insts:
        scored = [(L.sigmoid(float(np.dot(w, c["feat"]))), c) for c in inst["cands"]]
        scored.sort(key=lambda sc: sc[0], reverse=True)
        best_s, best_c = scored[0]
        second_s = scored[1][0] if len(scored) > 1 else 0.0
        keptflag = best_s >= keep_thr
        if keptflag:
            kept.append((inst["sid"], (inst["v_surf"], inst["agent"], best_c["p"])))
        log.append({"inst": inst, "best_c": best_c, "best_s": best_s, "second_s": second_s,
                    "kept": keptflag})
    return kept, log


def single_cue_keep(insts, feat_index, direction, keep_thr_quantile=None):
    """Standalone single-cue ranker: pick the candidate optimizing ONE raw feature (no learning)."""
    kept = []
    for inst in insts:
        vals = [(c["feat"][feat_index] * direction, c) for c in inst["cands"]]
        vals.sort(key=lambda vc: vc[0], reverse=True)
        best_val, best_c = vals[0]
        # keep-all single-cue (no threshold): the standalone cue always commits its top pick.
        kept.append((inst["sid"], (inst["v_surf"], inst["agent"], best_c["p"])))
    return kept


# ----------------------------------------------------------------------------------------------
# PRIMARY metric: forced-choice patient-SELECTION ACCURACY on POS instances (threshold-free, apples-to-
# apples across single-cue rankers and learned votes; isolates the DECISION from the keep/reject threshold).
# ----------------------------------------------------------------------------------------------
def select_pick(w, inst):
    """Argmax candidate under the learned weight; return (pick, top1_raw_score, top2_raw_score)."""
    scored = sorted(((float(np.dot(w, c["feat"])), c) for c in inst["cands"]),
                    key=lambda sc: sc[0], reverse=True)
    top1, pick = scored[0]
    top2 = scored[1][0] if len(scored) > 1 else -1e9
    return pick, top1, top2


def selection_accuracy(w, pos_insts):
    if not pos_insts:
        return None, 0
    correct = sum(1 for inst in pos_insts if select_pick(w, inst)[0]["p"] == inst["gold_patient"])
    return round(correct / len(pos_insts), 4), len(pos_insts)


def single_cue_accuracy(pos_insts, feat_index, direction):
    if not pos_insts:
        return None
    correct = 0
    for inst in pos_insts:
        pick = max(inst["cands"], key=lambda c: c["feat"][feat_index] * direction)
        correct += (pick["p"] == inst["gold_patient"])
    return round(correct / len(pos_insts), 4)


def conformal_margin_threshold(cal_pos, w, alpha):
    """Chow (1970) reject calibrated by split-conformal quantile (hdlab.conformal). Nonconformity of a
    pick = -(sigmoid(top1) - sigmoid(top2)) (small margin = less confident = more likely to abstain).
    Returns q; abstain a test pick iff its nonconformity > q (i.e. margin < -q). None if no CAL pos."""
    if not cal_pos:
        return None
    import torch
    noncon = []
    for inst in cal_pos:
        _pick, top1, top2 = select_pick(w, inst)
        noncon.append(-(L.sigmoid(top1) - L.sigmoid(top2)))
    from hdlab.conformal import calibrate_quantile
    return float(calibrate_quantile(torch.tensor(noncon, dtype=torch.float64), alpha))


def accuracy_with_abstain(pos_insts, w, q):
    """Forced-choice accuracy (all pos) vs abstain accuracy (only confident picks) + realized abstain rate."""
    if not pos_insts:
        return None, None, 0.0, 0
    forced_correct, kept, n_abst = 0, [], 0
    for inst in pos_insts:
        pick, top1, top2 = select_pick(w, inst)
        correct = int(pick["p"] == inst["gold_patient"])
        forced_correct += correct
        if q is not None and -(L.sigmoid(top1) - L.sigmoid(top2)) > q:
            n_abst += 1
            continue
        kept.append(correct)
    forced_acc = round(forced_correct / len(pos_insts), 4)
    abst_acc = round(sum(kept) / len(kept), 4) if kept else None
    abst_rate = round(n_abst / len(pos_insts), 4)
    return forced_acc, abst_acc, abst_rate, n_abst


# ----------------------------------------------------------------------------------------------
# Verb-disjoint 3-way split (TRAIN fit / CAL conformal / TEST eval). Deterministic.
# ----------------------------------------------------------------------------------------------
def split_verbs(instances, seed, frac_train=0.5, frac_cal=0.2):
    verbs = sorted(set(inst["v_lemma"] for inst in instances))
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(verbs))
    n_tr = max(1, int(round(frac_train * len(verbs))))
    n_ca = max(1, int(round(frac_cal * len(verbs))))
    tr = set(verbs[perm[i]] for i in range(n_tr))
    ca = set(verbs[perm[i]] for i in range(n_tr, min(n_tr + n_ca, len(verbs))))
    te = set(verbs) - tr - ca
    if not te:  # tiny-corpus guard: steal one verb back for TEST
        te = {verbs[perm[-1]]}
        ca = ca - te
        tr = tr - te
    def sel(vs):
        return [inst for inst in instances if inst["v_lemma"] in vs]
    return sel(tr), sel(ca), sel(te), sorted(tr), sorted(ca), sorted(te)


# ----------------------------------------------------------------------------------------------
# Difficulty slices.
# ----------------------------------------------------------------------------------------------
def cue_conflict_instances(insts):
    """Instances where >=2 single cues disagree on the top candidate (the hard cases where integration
    could pay off). Uses word-order (f_postv) vs gfit vs plausibility vs prep_patient_sense."""
    conflict = []
    for inst in insts:
        picks = set()
        for _name, idx, direction in [("wo", 2, +1), ("gfit", 10, +1), ("plaus", 11, +1),
                                       ("prep", 7, +1)]:
            vals = sorted(inst["cands"], key=lambda c: c["feat"][idx] * direction, reverse=True)
            picks.add(vals[0]["p"])
        if len(picks) >= 2:
            conflict.append(inst)
    return conflict


# ----------------------------------------------------------------------------------------------
# Conformal calibrated abstain (hdlab.conformal, split-conformal; atom 29367 machinery).
# ----------------------------------------------------------------------------------------------
def conformal_threshold(cal_insts, w, keep_thr, alpha):
    """Nonconformity of a CAL pos-instance = 1 - sigmoid(score of its GOLD-patient candidate).
    Lower = more conformal. Returns q or None if no calibratable instances."""
    import torch
    scores = []
    for inst in cal_insts:
        if not inst["is_pos"]:
            continue
        gc = next((c for c in inst["cands"] if c["is_gold"]), None)
        if gc is None:
            continue
        s = L.sigmoid(float(np.dot(w, gc["feat"])))
        scores.append(1.0 - s)
    if not scores:
        return None
    from hdlab.conformal import calibrate_quantile
    return float(calibrate_quantile(torch.tensor(scores, dtype=torch.float64), alpha))


def eval_with_abstain(insts, w, gold, keep_thr, q, only_verbs):
    """Forced-choice precision vs abstain precision (drop kept preds whose nonconformity > q)."""
    kept_forced, _ = keep_best(w, insts, keep_thr)
    m_forced = L.score_arm(kept_forced, gold, only_verbs=only_verbs)
    if q is None:
        return m_forced, m_forced, 0.0, 0
    kept_abstain = []
    n_abstained = 0
    n_total_kept = 0
    for inst in insts:
        scored = [(L.sigmoid(float(np.dot(w, c["feat"]))), c) for c in inst["cands"]]
        scored.sort(key=lambda sc: sc[0], reverse=True)
        best_s, best_c = scored[0]
        if best_s < keep_thr:
            continue
        n_total_kept += 1
        nonconf = 1.0 - best_s
        if nonconf > q:
            n_abstained += 1
            continue
        kept_abstain.append((inst["sid"], (inst["v_surf"], inst["agent"], best_c["p"])))
    m_abstain = L.score_arm(kept_abstain, gold, only_verbs=only_verbs)
    abstain_rate = n_abstained / n_total_kept if n_total_kept else 0.0
    return m_forced, m_abstain, round(abstain_rate, 4), n_abstained


# ----------------------------------------------------------------------------------------------
# Pure-decision-error list (the deliverable): every TEST gold pair the vote gets WRONG under oracle extraction.
# ----------------------------------------------------------------------------------------------
def dominant_cue(w, feat):
    contribs = [(FEATURE_NAMES[i], float(w[i] * feat[i])) for i in range(D) if i != IDX_BIAS]
    contribs.sort(key=lambda nc: nc[1], reverse=True)
    return contribs[0][0] if contribs else "bias"


def pure_decision_errors(w, insts, sent_text):
    """Rows for legible human annotation: decision failures under PERFECT (oracle) extraction."""
    rows = []
    for inst in insts:
        scored = [(L.sigmoid(float(np.dot(w, c["feat"]))), c) for c in inst["cands"]]
        scored.sort(key=lambda sc: sc[0], reverse=True)
        best_s, best_c = scored[0]
        second_s = scored[1][0] if len(scored) > 1 else 0.0
        pred_p = best_c["p"] if best_s >= 0.0 else None
        margin = round(best_s - second_s, 4)
        if inst["is_pos"]:
            correct = (best_c["p"] == inst["gold_patient"])
            if correct:
                continue
            rows.append({
                "sid": inst["sid"], "sentence": sent_text.get(inst["sid"], ""),
                "gold_agent": inst["agent"], "gold_verb": inst["v_lemma"],
                "gold_patient": inst["gold_patient"],
                "predicted_patient": best_c["p"],
                "error_type": "wrong_patient",
                "dominant_cue": dominant_cue(w, best_c["feat"]),
                "vote_confidence": round(best_s, 4), "margin_top1_top2": margin,
                "gold_patient_score": round(
                    L.sigmoid(float(np.dot(w, next(c for c in inst["cands"] if c["is_gold"])["feat"]))), 4),
            })
        else:
            # nopat instance: a decision error is keeping ANY patient (false positive).
            if best_s >= 0.45:
                rows.append({
                    "sid": inst["sid"], "sentence": sent_text.get(inst["sid"], ""),
                    "gold_agent": "", "gold_verb": inst["v_lemma"], "gold_patient": None,
                    "predicted_patient": best_c["p"], "error_type": "spurious_patient_on_nopat_verb",
                    "dominant_cue": dominant_cue(w, best_c["feat"]),
                    "vote_confidence": round(best_s, 4), "margin_top1_top2": margin,
                    "gold_patient_score": None,
                })
    return rows


# ----------------------------------------------------------------------------------------------
# Canary: the zero-incidence grammar cues MUST fire on synthetic sentences (mechanism real, corpus-indep).
# ----------------------------------------------------------------------------------------------
def canary_grammar_fires(gfit_fn, sel_fn):
    checks = []
    # passive-by-agent: f_passive_flip must be 1.0 on 'boy' in "the cake was eaten by the boy".
    toks = L.tokenize("the cake was eaten by the boy")
    feat, meta = extended_features(toks, "eaten", "boy", "eat", gfit_fn, sel_fn)
    checks.append(("passive_flip_fires", feat[6] == 1.0))
    # passive-subject RESCUE: f_passive_subject must be 1.0 on the pre-verbal affected subject 'cake'.
    feat_subj, _ = extended_features(toks, "eaten", "cake", "eat", gfit_fn, sel_fn)
    checks.append(("passive_subject_fires", feat_subj[12] == 1.0))
    # active SVO: pre-verbal subject must NOT get passive_subject (it is the agent, not patient).
    feat_act, _ = extended_features(L.tokenize("the boy ate the cake"), "ate", "boy", "eat", gfit_fn, sel_fn)
    checks.append(("active_subject_no_passive_signal", feat_act[12] == 0.0))
    # by=location (active) must NOT set passive flip.
    toks2 = L.tokenize("papa sat down by the pile")
    feat2, _ = extended_features(toks2, "sat", "pile", "sit", gfit_fn, sel_fn)
    checks.append(("by_location_no_flip", feat2[6] == 0.0))
    # prep-sense: 'with' -> nonpatient sense feature on "pleased with the gift".
    toks3 = L.tokenize("he was pleased with the gift")
    feat3, _ = extended_features(toks3, "pleased", "gift", "please", gfit_fn, sel_fn)
    checks.append(("prep_nonpatient_sense_fires", feat3[8] == 1.0))
    # alternation: 'onto'-governed NP in an alternating verb -> f_alternation negative.
    toks4 = L.tokenize("she loaded hay onto the truck")
    feat4, _ = extended_features(toks4, "loaded", "truck", "load", gfit_fn, sel_fn)
    checks.append(("alternation_fires", feat4[9] == -1.0))
    ok = all(v for _n, v in checks)
    return {"all_pass": bool(ok), "checks": [{"name": n, "pass": bool(v)} for n, v in checks]}


# ----------------------------------------------------------------------------------------------
# gfit + GloVe teacher, built on the MINING corpus (McGuffey gold source EXCLUDED). Reuses G + SCV + L.
# ----------------------------------------------------------------------------------------------
def build_mining_models(cfg, output_dir):
    mine_data = SCV.run_reader_on_files(cfg["mining_files"],
                                        os.path.join(output_dir, "_mining_cache.json"),
                                        max_sents=cfg["mining_max_sents"])
    bare = []
    for sid, rec in mine_data.items():
        toks = L.tokenize(rec["sent"])
        for tup in rec["svo"]:
            v_surf, a, p = tup
            feat6, _ = L.candidate_features(toks, v_surf, p)
            bare.append({"sid": sid, "v": L.lemma_verb(v_surf), "a": a, "p": p,
                         "tup": (v_surf, a, p), "feat6": np.asarray(feat6, dtype=np.float64)})
    gfit_fn, gfit_stats = G.build_gfit_model(bare)
    # GloVe selectional-coherence teacher over mining candidates (feat = feat6 for the teacher bootstrap).
    toks_vocab = set()
    for c in bare:
        toks_vocab.update([c["p"], c["v"]])
    glove = L.load_glove_for(toks_vocab)
    mining_cands = [{"sid": c["sid"], "v": c["v"], "a": c["a"], "p": c["p"], "feat": c["feat6"]}
                    for c in bare]
    sel_fn, _vc, _gc = L.build_semantic_teacher(mining_cands, glove)
    return gfit_fn, sel_fn, gfit_stats, len(mine_data)


# ----------------------------------------------------------------------------------------------
# Config.
# ----------------------------------------------------------------------------------------------
def cfg_smoke():
    return dict(mode="smoke", slice_lessons=["L04", "L05", "L07"], mining_files=list(G.MINING_FILES_SMOKE),
                mining_max_sents=600, epochs=40, lr=0.20, keep_thr=0.45, alpha=0.2,
                curve_fracs=[0.25, 0.5, 1.0], seeds=[7, 13, 19])


def cfg_full():
    return dict(mode="full", slice_lessons=["L04", "L05", "L07", "L08", "L09", "L10", "L12"],
                mining_files=list(G.MINING_FILES_FULL), mining_max_sents=None, epochs=60, lr=0.20,
                keep_thr=0.45, alpha=0.2, curve_fracs=[0.1, 0.25, 0.5, 0.75, 1.0], seeds=[7, 13, 19])


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


def write_errors(output_dir, rows):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "pure_decision_errors.jsonl.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=True) + "\n")
    os.replace(tmp, os.path.join(output_dir, "pure_decision_errors.jsonl"))


# ----------------------------------------------------------------------------------------------
# Run.
# ----------------------------------------------------------------------------------------------
def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START", flush=True)

    gfit_fn, sel_fn, gfit_stats, n_mine = build_mining_models(cfg, output_dir)
    print(f"[{ANCHOR_NAME}:{mode}] mining models built: {gfit_stats['n_object_classes']} gfit classes, "
          f"{n_mine} mining sents", flush=True)

    order, sent_text, _reader_svo = L.load_slice_and_reader(cfg["slice_lessons"])
    gold, gold_meta = L.load_gold(cfg["slice_lessons"])
    instances = build_oracle_instances(order, sent_text, gold, gfit_fn, sel_fn)
    n_pos = sum(1 for i in instances if i["is_pos"])
    n_nopat = sum(1 for i in instances if not i["is_pos"])
    print(f"[{ANCHOR_NAME}:{mode}] oracle instances: {len(instances)} ({n_pos} pos, {n_nopat} nopat)",
          flush=True)

    # Grammar coverage audit (EG) -> 0-incidence caveat + grammar-resolvable subset.
    coverage = EG.coverage_audit(order, sent_text, gold)
    canary = canary_grammar_fires(gfit_fn, sel_fn)

    # ---- Multi-seed evaluation over verb-disjoint splits. ----
    per_seed = []
    wo_digests, full_digests = {}, {}
    for seed in cfg["seeds"]:
        tr, ca, te, tr_v, ca_v, te_v = split_verbs(instances, seed)
        tr_pos = [i for i in tr if i["is_pos"]]
        te_pos = [i for i in te if i["is_pos"]]
        ca_pos = [i for i in ca if i["is_pos"]]

        # PRIMARY metric = forced-choice patient-SELECTION ACCURACY on TEST pos instances (threshold-free).
        # (i) Best-single-cue standalone (the one-at-a-time wall; argmax of one raw cue, no learning).
        single = {}
        for name, idx, direction in SINGLE_CUES:
            single[name] = single_cue_accuracy(te_pos, idx, direction)
        best_single_name = max(single, key=lambda k: (single[k] if single[k] is not None else -1))
        best_single_acc = single[best_single_name] if single[best_single_name] is not None else 0.0

        # (ii) Learned VOTES over feature masks (SAME supervised delta-rule, SAME seeds/splits).
        w_wo, _, _ = train_vote(tr, IDX_WORDORDER, seed, cfg["epochs"], cfg["lr"])
        w_struct, _, _ = train_vote(tr, IDX_STRUCTURAL, seed, cfg["epochs"], cfg["lr"])
        w_full, _, n_train_insts = train_vote(tr, IDX_ALL, seed, cfg["epochs"], cfg["lr"])
        wo_acc, _ = selection_accuracy(w_wo, te_pos)
        struct_acc, _ = selection_accuracy(w_struct, te_pos)
        full_acc, _ = selection_accuracy(w_full, te_pos)

        # Crude multi-cue LCCP reader reproduced LIVE via L.run_arms on the SAME oracle pools (reader-style
        # precision reference; DIFFERENT metric from selection-accuracy -- reported as the incumbent number).
        oracle_reader_svo = defaultdict(list)
        for inst in te:
            for c in inst["cands"]:
                oracle_reader_svo[inst["sid"]].append((inst["v_surf"], inst["agent"], c["p"]))
        order_te = sorted(set(inst["sid"] for inst in te))
        crude_prec = -1.0
        crude_err = None
        try:
            gl_vocab = set()
            for inst in te:
                for c in inst["cands"]:
                    gl_vocab.update([c["p"], inst["v_lemma"]])
            glove_te = L.load_glove_for(gl_vocab)
            lccp_cfg = dict(sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=cfg["epochs"], keep_thr=cfg["keep_thr"],
                            subcat_thr=0.42, heldout_frac=0.25, k_constructions=4, kappa=1.5, seed=seed)
            dec_lccp, _a, _s, _h, _sn, _ig, _w = L.run_arms(order_te, oracle_reader_svo, sent_text,
                                                            glove_te, lccp_cfg, seed)
            crude_prec = L.score_arm(dec_lccp["B_cuecomp"], gold, only_verbs=set(te_v))["precision"]
        except Exception as ce:  # reference baseline, not the discriminator
            crude_err = f"{type(ce).__name__}: {str(ce)[:200]}"

        # Cue-conflict slice (TEST pos): where >=2 single cues disagree on the top candidate.
        te_conflict = [i for i in cue_conflict_instances(te) if i["is_pos"]]
        conf_full_acc, _ = selection_accuracy(w_full, te_conflict)
        conf_wo_acc, _ = selection_accuracy(w_wo, te_conflict)
        conf_best_single = (max((single_cue_accuracy(te_conflict, idx, d) or 0.0)
                                 for _n, idx, d in SINGLE_CUES) if te_conflict else None)

        # Calibrated abstain (conformal margin-reject; CAL->TEST verb-disjoint), on full TEST + conflict subset.
        q = conformal_margin_threshold(ca_pos, w_full, cfg["alpha"])
        f_forced, f_abst, f_rate, f_nabst = accuracy_with_abstain(te_pos, w_full, q)
        c_forced, c_abst, c_rate, c_nabst = accuracy_with_abstain(te_conflict, w_full, q)

        # Learning curve (full-vote TEST selection accuracy vs fraction of TRAIN instances).
        curve = {}
        for fr in cfg["curve_fracs"]:
            w_fr, _, _ = train_vote(tr, IDX_ALL, seed, cfg["epochs"], cfg["lr"], frac=fr)
            acc_fr, _ = selection_accuracy(w_fr, te_pos)
            curve[f"{fr:.2f}"] = acc_fr

        wo_digests[seed] = hashlib.sha256(np.round(w_wo, 6).tobytes()).hexdigest()[:16]
        full_digests[seed] = hashlib.sha256(np.round(w_full, 6).tobytes()).hexdigest()[:16]

        gain_single = round(full_acc - best_single_acc, 4)
        gain_struct = round(full_acc - struct_acc, 4)
        row = {
            "seed": seed, "n_train_verbs": len(tr_v), "n_cal_verbs": len(ca_v), "n_test_verbs": len(te_v),
            "n_train_pos_insts": len(tr_pos), "n_test_pos_insts": len(te_pos),
            "n_test_conflict_pos_insts": len(te_conflict),
            "single_cue_accuracy": {k: (round(v, 4) if v is not None else None) for k, v in single.items()},
            "best_single_cue": best_single_name, "best_single_accuracy": round(best_single_acc, 4),
            "wordorder_vote_accuracy": wo_acc, "structural_vote_accuracy": struct_acc,
            "full_vote_accuracy": full_acc,
            "crude_reader_precision_ref": round(crude_prec, 4),
            "gain_full_minus_best_single": gain_single,
            "gain_full_minus_structural_vote": gain_struct,
            "gain_full_minus_wordorder_vote": round(full_acc - wo_acc, 4),
            "conflict_full_vote_accuracy": conf_full_acc, "conflict_wordorder_vote_accuracy": conf_wo_acc,
            "conflict_best_single_accuracy": (round(conf_best_single, 4) if conf_best_single is not None else None),
            "abstain_alpha": cfg["alpha"], "conformal_q": (round(q, 4) if q is not None else None),
            "test_forced_accuracy": f_forced, "test_abstain_accuracy": f_abst,
            "test_abstain_rate": f_rate, "test_n_abstained": f_nabst,
            "conflict_forced_accuracy": c_forced, "conflict_abstain_accuracy": c_abst,
            "conflict_abstain_rate": c_rate, "conflict_n_abstained": c_nabst,
            "learning_curve_accuracy": curve,
            "w_wordorder": [round(x, 4) for x in w_wo.tolist()],
            "w_structural": [round(x, 4) for x in w_struct.tolist()],
            "w_full": [round(x, 4) for x in w_full.tolist()],
        }
        if crude_err is not None:
            row["crude_reader_error"] = crude_err
        per_seed.append(row)
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} best_single={best_single_name}={best_single_acc:.3f} "
              f"struct_vote={struct_acc:.3f} wo_vote={wo_acc:.3f} full_vote={full_acc:.3f} "
              f"gain_vs_single={gain_single:+.3f} gain_vs_struct={gain_struct:+.3f} crude_P_ref={crude_prec:.3f} "
              f"conflict(full={conf_full_acc} wo={conf_wo_acc} n={len(te_conflict)}) "
              f"abstain(forced={f_forced} abst={f_abst} rate={f_rate})", flush=True)

    # ---- Aggregate + verdict. ----
    def mean(key):
        vals = [s[key] for s in per_seed if s.get(key) is not None]
        return round(float(np.mean(vals)), 4) if vals else None

    def minv(key):
        vals = [s[key] for s in per_seed if s.get(key) is not None]
        return round(float(np.min(vals)), 4) if vals else None

    mean_best_single = mean("best_single_accuracy")
    mean_full = mean("full_vote_accuracy")
    mean_struct = mean("structural_vote_accuracy")
    mean_wo = mean("wordorder_vote_accuracy")
    mean_crude = mean("crude_reader_precision_ref")
    mean_gain_single = mean("gain_full_minus_best_single")
    min_gain_single = minv("gain_full_minus_best_single")
    mean_gain_struct = mean("gain_full_minus_structural_vote")

    n_resolvable = len(coverage["grammar_resolvable_gold_pos_ids"])

    if mean_gain_single is None or mean_full is None:
        verdict = "UNKNOWN_NO_SEEDS"
    elif mean_gain_single >= 0.05 and (mean_gain_struct is None or mean_gain_struct >= 0.02) and min_gain_single > 0.0:
        verdict = "HARD_PASS_INTEGRATION_COMPLEMENTARY"
    elif mean_gain_single <= 0.0:
        verdict = "HARD_FAIL_CUES_REDUNDANT"
    else:
        verdict = "MIDDLE_BAND"

    # Abstain sub-verdict on the cue-conflict subset.
    conf_forced = mean("conflict_forced_accuracy")
    conf_abst = mean("conflict_abstain_accuracy")
    conf_rate = mean("conflict_abstain_rate")
    if conf_forced is not None and conf_abst is not None and conf_rate is not None:
        abstain_gain = round(conf_abst - conf_forced, 4)
        if abstain_gain >= 0.02 and conf_rate <= 0.35:
            abstain_verdict = "HARD_PASS_ABSTAIN_HELPS_ON_CONFLICT"
        elif abstain_gain <= 0.0:
            abstain_verdict = "HARD_FAIL_ABSTAIN_NO_HELP"
        else:
            abstain_verdict = "MIDDLE_BAND_ABSTAIN"
    else:
        abstain_gain, abstain_verdict = None, "UNKNOWN_ABSTAIN"

    # Design-gate checks.
    baseline_in_band = bool(mean_best_single is not None and 0.05 < mean_best_single < 0.95)
    arms_differ_verified = all(wo_digests[s] != full_digests[s] for s in cfg["seeds"])
    discriminator_fires = bool(canary["all_pass"])  # zero-incidence grammar cues provably fire on canary

    # Pure-decision-error list on seed[0]'s TEST split (deterministic, legible).
    seed0 = cfg["seeds"][0]
    tr0, ca0, te0, _tv, _cv, tev0 = split_verbs(instances, seed0)
    w_full0, _, _ = train_vote(tr0, IDX_ALL, seed0, cfg["epochs"], cfg["lr"])
    err_rows = pure_decision_errors(w_full0, te0, sent_text)
    write_errors(output_dir, err_rows)

    elapsed = time.perf_counter() - t0
    grammar_zero = (coverage["n_by_agent"] == 0 and coverage["n_prep_governed_gold_patients"] == 0)
    msg = (f"{verdict} | slice={'+'.join(cfg['slice_lessons'])} n_inst={len(instances)}({n_pos}pos/{n_nopat}nopat) "
           f"| PRIMARY=selection-accuracy: best_single={mean_best_single} struct_vote={mean_struct} "
           f"wo_vote={mean_wo} full_vote={mean_full} gain_vs_single={mean_gain_single:+.3f}(min={min_gain_single:+.3f}) "
           f"gain_vs_struct={mean_gain_struct} | crude_reader_P_ref={mean_crude} "
           f"| conflict: forced={conf_forced} abstain={conf_abst} rate={conf_rate} -> {abstain_verdict} "
           f"| grammar_resolvable={n_resolvable} zero_incidence={grammar_zero} canary_all_pass={canary['all_pass']} "
           f"| baseline_in_band={baseline_in_band} arms_differ={arms_differ_verified} n_decision_errors={len(err_rows)}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
        "central_hypothesis": ("Does a jointly-trained integrated vote over {word-order, passive, prep-sense, "
                               "alternation, graded-thematic-fit, plausibility} beat the BEST SINGLE cue on "
                               "parser-independent oracle gold-pairs, or are the cues REDUNDANT (word-order "
                               "dominant, per MacWhinney & Bates)?"),
        "primary_metric": ("forced-choice patient-SELECTION ACCURACY on POS instances (argmax candidate == gold "
                           "patient; threshold-free; apples-to-apples across single-cue rankers and learned "
                           "votes). crude_reader_precision_ref is the incumbent reader's keep/reject PRECISION "
                           "via L.run_arms -- a DIFFERENT (reader-style) metric, reported as a reference only."),
        "feature_names": FEATURE_NAMES,
        "mean_best_single_accuracy": mean_best_single,
        "mean_structural_vote_accuracy": mean_struct,
        "mean_wordorder_vote_accuracy": mean_wo,
        "mean_full_vote_accuracy": mean_full,
        "mean_crude_reader_precision_ref": mean_crude,
        "mean_gain_full_minus_best_single": mean_gain_single,
        "min_gain_full_minus_best_single": min_gain_single,
        "mean_gain_full_minus_structural_vote": mean_gain_struct,
        "mean_gain_full_minus_wordorder_vote": mean("gain_full_minus_wordorder_vote"),
        "abstain_subverdict": abstain_verdict, "abstain_gain_on_conflict": abstain_gain,
        "per_seed": per_seed,
        "grammar_coverage_audit": {k: coverage[k] for k in
                                   ["n_gold_pos_total", "n_by_agent", "n_prep_governed_gold_patients",
                                    "n_alternation_verb_occurrences"]},
        "n_grammar_resolvable_gold_pos": n_resolvable,
        "grammar_zero_incidence_caveat": (
            "McGuffey has %d by-agent passives and %d preposition-governed gold patients -> the "
            "f_passive_flip / f_prep_patient_sense / f_prep_nonpatient_sense / f_alternation cues have ZERO "
            "incidence on THIS corpus and CANNOT contribute here. On THIS data the vote only adjudicates "
            "WORD-ORDER vs GRADED-FIT vs PLAUSIBILITY. Those zero-incidence cues are UNTESTED-HERE, NOT "
            "shown useless. The canary_grammar_fires check proves they FIRE correctly on synthetic "
            "passive/alternation/prep-sense sentences (mechanism real, corpus-independent)."
            % (coverage["n_by_agent"], coverage["n_prep_governed_gold_patients"])),
        "canary_grammar_fires": canary,
        "baseline_in_band": baseline_in_band,
        "arms_differ_verified": arms_differ_verified,
        "arms_differ_note": ("ONE VARIABLE = feature mask. word-order-only vote (bias+f_adj+f_postv) vs "
                             "full-integrated vote (all 12 features); same TRAIN instances, same supervised "
                             "delta-rule, same seeds, same verb-disjoint splits."),
        "wordorder_vote_weight_digests": wo_digests, "full_vote_weight_digests": full_digests,
        "discriminator_fires": discriminator_fires,
        "n_decision_errors_seed0": len(err_rows),
        "pure_decision_errors_path": os.path.join(output_dir, "pure_decision_errors.jsonl"),
        "gfit_model_stats": gfit_stats, "n_mining_sentences": n_mine,
        "gold_meta_independence": gold_meta.get("independence", ""),
        "training_protocol": ("SUPERVISED logistic on ORACLE gold-pairs (target=is-gold-patient), verb-DISJOINT "
                              "3-way split TRAIN(fit)/CAL(conformal)/TEST(eval); no verb overlap -> no leak. "
                              "gfit + GloVe teacher built on the MINING corpus (McGuffey gold source EXCLUDED "
                              "from mining) -> no ground-by-X-grade-by-X. Parser-independent: candidate pools "
                              "built from gold (gold patient guaranteed present) not from a reader/parser."),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "decision-precision measurement; no quantitative noise floor for the discriminator",
        "deterministic_seeding": "fixed int seeds + numpy default_rng + sorted(set); no hash()-seeded RNG",
        "REQUIRED_FIELDS": ["verdict", "mean_best_single_accuracy", "mean_structural_vote_accuracy",
                            "mean_full_vote_accuracy", "mean_gain_full_minus_best_single", "per_seed",
                            "grammar_zero_incidence_caveat", "canary_grammar_fires", "abstain_subverdict",
                            "n_decision_errors_seed0", "training_protocol", "primary_metric"],
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] errors -> {os.path.join(output_dir, 'pure_decision_errors.jsonl')} "
          f"({len(err_rows)} rows)", flush=True)
    return payload


# ----------------------------------------------------------------------------------------------
# Self-test (constructs the REAL feature builder + a tiny supervised vote; asserts discriminators fire).
# ----------------------------------------------------------------------------------------------
def self_test():
    # toy gfit + teacher (real closures, not stubs).
    toy = [
        {"sid": "t", "v": "build", "a": "he", "p": "hut", "feat6": np.array([1., .5, 1., 0., 0., 0.])},
        {"sid": "t", "v": "build", "a": "he", "p": "wall", "feat6": np.array([1., .5, 1., 0., 0., 0.])},
        {"sid": "t", "v": "eat", "a": "she", "p": "apple", "feat6": np.array([1., .5, 1., 0., 0., 0.])},
    ]
    gfit_fn, _ = G.build_gfit_model(toy)
    sel_fn, _, _ = L.build_semantic_teacher(
        [{"sid": "t", "v": c["v"], "a": c["a"], "p": c["p"], "feat": c["feat6"]} for c in toy], {})

    # extended feature dimensionality + grammar cues fire on canary.
    feat, meta = extended_features(L.tokenize("he built a hut"), "built", "hut", "build", gfit_fn, sel_fn)
    assert feat.shape[0] == D, f"feature dim must be {D}, got {feat.shape[0]}"
    canary = canary_grammar_fires(gfit_fn, sel_fn)
    assert canary["all_pass"], f"grammar canary must fire: {canary}"

    # oracle instance construction guarantees gold patient present.
    sent_text = {"s0": "he built a hut on the hill"}
    gold = {"s0": {"pos": [{"v": "build", "agent": "he", "patient": "hut", "refs": {"he"}}],
                   "nopat": set(), "pos_verbs": {"build"}}}
    insts = build_oracle_instances(["s0"], sent_text, gold, gfit_fn, sel_fn)
    assert len(insts) == 1 and any(c["is_gold"] for c in insts[0]["cands"]), "gold patient must be a candidate"
    assert any(c["p"] == "hill" for c in insts[0]["cands"]), "rival noun 'hill' must be a candidate (real decision)"

    # supervised vote: word-order-only vs full-integrated weight vectors must DIFFER (one variable = mask).
    train = build_oracle_instances(
        ["s0", "s1", "s2"],
        {"s0": "he built a hut", "s1": "she ate an apple", "s2": "they crossed the field"},
        {"s0": {"pos": [{"v": "build", "agent": "he", "patient": "hut", "refs": {"he"}}], "nopat": set(),
                "pos_verbs": {"build"}},
         "s1": {"pos": [{"v": "eat", "agent": "she", "patient": "apple", "refs": {"she"}}], "nopat": set(),
                "pos_verbs": {"eat"}},
         "s2": {"pos": [{"v": "cross", "agent": "they", "patient": "field", "refs": {"they"}}], "nopat": set(),
                "pos_verbs": {"cross"}}},
        gfit_fn, sel_fn)
    w_wo, _, _ = train_vote(train, IDX_WORDORDER, 7, 30, 0.2)
    w_full, _, _ = train_vote(train, IDX_ALL, 7, 30, 0.2)
    assert not np.allclose(w_wo, w_full), "word-order-only and full vote weights must differ (one variable)"
    # word-order mask must zero the non-word-order weights.
    assert abs(w_wo[10]) < 1e-9 and abs(w_wo[6]) < 1e-9, "word-order-only vote must not touch gfit/passive weights"

    # keep_best + score_arm round-trip.
    kept, log = keep_best(w_full, train, 0.45)
    assert isinstance(kept, list), "keep_best must return a list"

    print(f"[{ANCHOR_NAME}] self-test PASS | D={D} canary_all_pass={canary['all_pass']} "
          f"w_wo!=w_full={not np.allclose(w_wo, w_full)} n_train_insts={len(train)}", flush=True)


def run_construction(mode):
    """DECISIVE hard-case arm: the SAME integrated vote on the construction hard gold (real passives /
    prep-governed / cue-conflict). Respects the gold's OWN train/test/ambiguity split. Per-construction."""
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_construction"
                              + ("_smoke" if mode == "smoke" else ""))
    _write_start_marker(output_dir, "construction_" + mode)
    print(f"[{ANCHOR_NAME}:construction:{mode}] START", flush=True)

    gfit_fn, sel_fn, gfit_stats, n_mine = build_mining_models(cfg, output_dir)
    insts, cmeta = build_construction_oracle_instances(gfit_fn, sel_fn)
    tr = [i for i in insts if i["split"] == "train"]
    te = [i for i in insts if i["split"] == "test"]
    amb = [i for i in insts if i["split"] == "ambiguity"]
    print(f"[{ANCHOR_NAME}:construction:{mode}] instances: {len(insts)} "
          f"(train={len(tr)} test={len(te)} ambiguity={len(amb)}); mining={n_mine} sents", flush=True)

    constructions = sorted(set(i["construction"] for i in te))
    canary = canary_grammar_fires(gfit_fn, sel_fn)

    per_seed = []
    for seed in cfg["seeds"]:
        w_wo, _, _ = train_vote(tr, IDX_WORDORDER, seed, cfg["epochs"], cfg["lr"])
        w_struct, _, _ = train_vote(tr, IDX_STRUCTURAL, seed, cfg["epochs"], cfg["lr"])
        w_full, _, _ = train_vote(tr, IDX_ALL, seed, cfg["epochs"], cfg["lr"])

        full_acc, _ = selection_accuracy(w_full, te)
        wo_acc, _ = selection_accuracy(w_wo, te)
        struct_acc, _ = selection_accuracy(w_struct, te)
        single_postv = single_cue_accuracy(te, 2, +1)  # word-order-alone (raw f_postv, no learning)

        per_constr = {}
        for c in constructions:
            sub = [i for i in te if i["construction"] == c]
            per_constr[c] = {
                "n": len(sub),
                "single_wordorder_postv": single_cue_accuracy(sub, 2, +1),
                "wordorder_vote": selection_accuracy(w_wo, sub)[0],
                "full_vote": selection_accuracy(w_full, sub)[0],
            }

        # Ambiguity items = abstain targets (NOT scored as hard failures): report the vote margin so we can
        # see whether the vote is appropriately UNSURE (small margin) on them vs confident on test.
        amb_margins = []
        for i in amb:
            _pick, top1, top2 = select_pick(w_full, i)
            amb_margins.append(round(L.sigmoid(top1) - L.sigmoid(top2), 4))

        per_seed.append({
            "seed": seed, "test_full_vote": full_acc, "test_wordorder_vote": wo_acc,
            "test_structural_vote": struct_acc, "test_single_wordorder_postv": single_postv,
            "gain_full_minus_wordorder_vote": round(full_acc - wo_acc, 4),
            "gain_full_minus_single_wordorder": round(full_acc - (single_postv or 0.0), 4),
            "per_construction": per_constr,
            "w_full": {FEATURE_NAMES[k]: round(float(w_full[k]), 4) for k in range(D)},
            "ambiguity_margins": amb_margins,
        })
        pv = per_constr.get("passive_by_agent", {})
        print(f"[{ANCHOR_NAME}:construction:{mode}] seed={seed} test full={full_acc} wo={wo_acc} "
              f"single_wo={single_postv} | PASSIVE(n={pv.get('n')}): single_wo={pv.get('single_wordorder_postv')} "
              f"wo_vote={pv.get('wordorder_vote')} full={pv.get('full_vote')} | "
              f"w[passive_flip]={per_seed[-1]['w_full']['f_passive_flip']} "
              f"w[passive_subject]={per_seed[-1]['w_full']['f_passive_subject']}", flush=True)

    def mean_over(fn):
        vals = [fn(s) for s in per_seed if fn(s) is not None]
        return round(float(np.mean(vals)), 4) if vals else None

    mean_full = mean_over(lambda s: s["test_full_vote"])
    mean_wo = mean_over(lambda s: s["test_wordorder_vote"])
    mean_single_wo = mean_over(lambda s: s["test_single_wordorder_postv"])
    mean_gain_wo = mean_over(lambda s: s["gain_full_minus_wordorder_vote"])

    # Per-construction aggregate (mean over seeds).
    constr_agg = {}
    for c in constructions:
        constr_agg[c] = {
            "n": per_seed[0]["per_construction"][c]["n"],
            "single_wordorder_postv": mean_over(lambda s: s["per_construction"][c]["single_wordorder_postv"]),
            "wordorder_vote": mean_over(lambda s: s["per_construction"][c]["wordorder_vote"]),
            "full_vote": mean_over(lambda s: s["per_construction"][c]["full_vote"]),
        }

    # Mean learned weights (the load-bearing "do the grammar/semantic cues EARN nonzero weight" test).
    mean_w = {FEATURE_NAMES[k]: round(float(np.mean([s["w_full"][FEATURE_NAMES[k]] for s in per_seed])), 4)
              for k in range(D)}

    # Passive verdict (the decisive sub-test).
    pv = constr_agg.get("passive_by_agent", {})
    passive_gain_full_vs_single = (round((pv.get("full_vote") or 0) - (pv.get("single_wordorder_postv") or 0), 4)
                                   if pv else None)
    passive_gain_full_vs_wovote = (round((pv.get("full_vote") or 0) - (pv.get("wordorder_vote") or 0), 4)
                                   if pv else None)
    passive_weights_nonzero = bool(abs(mean_w["f_passive_flip"]) > 0.1 or abs(mean_w["f_passive_subject"]) > 0.1)

    if mean_gain_wo is None:
        verdict = "UNKNOWN"
    elif passive_gain_full_vs_single is not None and passive_gain_full_vs_single >= 0.15 and passive_weights_nonzero:
        verdict = "HARD_PASS_GRAMMAR_CUES_RESCUE_PASSIVES"
    elif mean_gain_wo <= 0.0 and (passive_gain_full_vs_single is None or passive_gain_full_vs_single <= 0.0):
        verdict = "HARD_FAIL_DEEP_REDUNDANCY_EVEN_ON_HARD_CASES"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_CUE_PAYOFF"

    # Pure-decision-errors on the test split (seed0 weights).
    with open(CONSTRUCTION_GOLD_PATH, encoding="utf-8") as f:
        _sid_text = {k: v["text"] for k, v in json.load(f)["gold"].items()}
    w_full0, _, _ = train_vote(tr, IDX_ALL, cfg["seeds"][0], cfg["epochs"], cfg["lr"])
    err_rows = []
    for i in te:
        pick, top1, top2 = select_pick(w_full0, i)
        if pick["p"] != i["gold_patient"]:
            err_rows.append({
                "sid": i["sid"], "sentence": _sid_text.get(i["sid"], ""),
                "construction": i["construction"], "gold_agent": i["agent"], "gold_verb": i["v_lemma"],
                "gold_patient": i["gold_patient"], "predicted_patient": pick["p"], "error_type": "wrong_patient",
                "dominant_cue": dominant_cue(w_full0, pick["feat"]),
                "vote_confidence": round(L.sigmoid(top1), 4),
                "margin_top1_top2": round(L.sigmoid(top1) - L.sigmoid(top2), 4),
                "cue_conflict": i["cue_conflict"]})
    write_errors(output_dir, err_rows)

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | construction-hard-gold(UD-EWT) test={len(te)} train={len(tr)} amb={len(amb)} "
           f"| TEST selection-acc: full={mean_full} wo_vote={mean_wo} single_wo={mean_single_wo} "
           f"gain_full_vs_wo_vote={mean_gain_wo} "
           f"| PASSIVE(n={pv.get('n')}): single_wo={pv.get('single_wordorder_postv')} wo_vote={pv.get('wordorder_vote')} "
           f"full={pv.get('full_vote')} gain_full_vs_single={passive_gain_full_vs_single} "
           f"| learned w[passive_flip]={mean_w['f_passive_flip']} w[passive_subject]={mean_w['f_passive_subject']} "
           f"w[prep_patient]={mean_w['f_prep_patient_sense']} w[gfit]={mean_w['f_gfit']} w[plaus]={mean_w['f_plaus']} "
           f"| canary_all_pass={canary['all_pass']} n_test_errors={len(err_rows)}")

    payload = {
        "anchor_name": ANCHOR_NAME + "_construction", "run_mode": mode, "verdict": verdict,
        "verdict_msg": msg, "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": cfg, "feature_names": FEATURE_NAMES,
        "gold_source": CONSTRUCTION_GOLD_PATH, "gold_meta_register_caveat": cmeta.get("register_caveat", ""),
        "split_respected": {"train": len(tr), "test": len(te), "ambiguity": len(amb),
                            "note": "vote weights trained on split==train ONLY; evaluated on split==test; "
                                    "ambiguity items are ABSTAIN TARGETS, not scored as hard failures."},
        "primary_metric": "forced-choice patient-selection accuracy on the gold's held-out TEST split.",
        "mean_test_full_vote_accuracy": mean_full,
        "mean_test_wordorder_vote_accuracy": mean_wo,
        "mean_test_single_wordorder_accuracy": mean_single_wo,
        "mean_gain_full_minus_wordorder_vote": mean_gain_wo,
        "per_construction_accuracy": constr_agg,
        "PASSIVE_SUBTEST": {
            "n_test_passives": pv.get("n"),
            "single_wordorder_alone": pv.get("single_wordorder_postv"),
            "wordorder_vote": pv.get("wordorder_vote"),
            "full_integrated_vote": pv.get("full_vote"),
            "gain_full_minus_single_wordorder": passive_gain_full_vs_single,
            "gain_full_minus_wordorder_vote": passive_gain_full_vs_wovote,
            "passive_cue_weights_nonzero": passive_weights_nonzero,
        },
        "mean_learned_weights": mean_w,
        "per_seed": per_seed,
        "constructions_tested": constructions,
        "canary_grammar_fires": canary,
        "ambiguity_abstain_targets": [{"sid": i["sid"], "construction": i["construction"]} for i in amb],
        "n_test_decision_errors": len(err_rows),
        "pure_decision_errors_path": os.path.join(output_dir, "pure_decision_errors.jsonl"),
        "gfit_model_stats": gfit_stats, "n_mining_sentences": n_mine,
        "training_protocol": ("SUPERVISED logistic on the construction gold's OWN split==train (oracle pairs, "
                              "target=is-gold-patient); evaluated on split==test; ambiguity=abstain targets. "
                              "gfit+plaus built on the MINING corpus (no gold leak). ORACLE candidate pools "
                              "(gold patient guaranteed present) -> parser-independent."),
        "register_caveat": ("UD-EWT is MODERN WEB TEXT (blogs/reviews/email), NOT narrative -- this arm tests "
                            "CONSTRUCTION handling (real passives etc.), NOT register transfer to McGuffey. "
                            "Small per-construction N (test has ~%d items across %d constructions); treat "
                            "per-construction numbers as smoke-not-fact." % (len(te), len(constructions))),
        "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": "fixed int seeds + numpy default_rng; gold-provided split (not random)",
        "REQUIRED_FIELDS": ["verdict", "mean_test_full_vote_accuracy", "mean_test_wordorder_vote_accuracy",
                            "per_construction_accuracy", "PASSIVE_SUBTEST", "mean_learned_weights",
                            "register_caveat", "training_protocol", "split_respected"],
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:construction:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:construction:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"[{ANCHOR_NAME}:construction:{mode}] errors -> "
          f"{os.path.join(output_dir, 'pure_decision_errors.jsonl')} ({len(err_rows)} rows)", flush=True)
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--construction", action="store_true")
    ap.add_argument("--construction-smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    if args.construction_smoke:
        run_construction("smoke"); return
    if args.construction:
        run_construction("full"); return
    ap.error("specify one of --self-test | --smoke | --full | --construction | --construction-smoke")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat()}
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
