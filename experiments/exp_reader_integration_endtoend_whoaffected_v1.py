"""END-TO-END reader integration: the REAL who-is-affected accuracy on PARSER parses (kills the proxy).

CULMINATION cell. Composes the full glass-box reader end-to-end and measures the TRUE who-is-affected
accuracy = extraction x decision COMPOSED, replacing the ~0.82 candidate-recall PROXY with a real number.

PIPELINE (all PERSISTED glass-box components; NOTHING rebuilt):
  raw McGuffey sentence
    -> hdlab.pos_tagger.PosTagger        (UPOS 0.9442; data/frontend_assets/pos_tagger_ud_ewt_upos.json)
    -> hdlab.arc_parser.ArcParser        (UAS 0.7868, per-arc margins; arc_parser_hashed_ud_ewt.npz)
    -> hdlab.arc_labeler.ArcLabeler      (label-acc 0.94; keeps nsubj:pass/obl:agent; arc_labeler_hashed_ud_ewt.json)
    -> hdlab.candidate_generator         (candidates_from_parse; coordination/relcl/conj_obj rules)
    -> LABELED patient-role filter {obj, nsubj:pass} + CONJ-PROPAGATION FIX (below)
    -> INTEGRATED logistic VOTE (exp_integrated_vote_role_decision_oracle_gold_v1.train_vote/select_pick),
       RE-TRAINED on the PARSER-derived (noisy) candidate pools, verb-disjoint, no leak.
    -> graded self-monitoring (vote margin + parser arc-margin + completeness) as SOFT abstain inputs.

CONJ-PROPAGATION FIX (the labeler cell flagged coordination recall dropped 0.82->0.52 because 2nd-conjunct
  patients are tagged `conj` not `obj`): a candidate arc whose label is `conj` is kept as a patient candidate
  iff the CONJUNCT-HEAD's label is obj/nsubj:pass -> patient-hood propagates through coordination. The cell
  MEASURES whether this recovers coordination candidate-recall toward the unlabeled 0.815.

THE MEASUREMENT (kill the proxy): for each gold POS pair (v_lemma, agent, patient) on the FULL McGuffey gold
  (data/gold_mcguffey_lccp_argstruct_v1.json), does the pipeline output the CORRECT patient?
    end_to_end_accuracy = #(pipeline patient == gold patient) / #gold POS pairs
  This is BELOW the candidate-recall ceiling: the gold patient must BE in the parser pool (extraction) AND
  the vote must select it (decision) -- BOTH can fail. Reported per-construction + aggregate.

ABLATION (isolates the labeled-parser's end-to-end contribution; ONE variable per step):
  A) CRUDE          = the crude 4-feature LCCP reader end-to-end (its own extraction + cue-comp decision;
                      ~0.15 precision incumbent), re-derived LIVE via L.run_arms on the reader's native SVO.
  B) UNLABELED+VOTE = parser candidates (ALL nominal deps) + integrated vote (retrained on unlabeled pools).
  C) LABELED+CONJFIX+VOTE = parser candidates restricted to labeled {obj,nsubj:pass}+conj-propagation + vote
                      (retrained on labeled pools).  [B->C one variable = the candidate FILTER.]

DISTRIBUTION-SHIFT PROBE (the biggest risk, pre-registered): the integrated vote was originally trained on
  ORACLE gold-pairs (clean, gold guaranteed present). Here it selects among PARSER candidates (noisier). We
  report the delta between vote-trained-on-ORACLE-pools vs vote-trained-on-PARSER-pools, both evaluated on the
  SAME parser LABELED TEST pools -> does retraining on the shifted distribution matter?

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (1) REAL baseline = CRUDE arm re-derived LIVE (not a remembered number) + BEST-SINGLE via unlabeled pool.
  (2) CAN-FAIL: (a) end-to-end WILL be below the candidate-recall ceiling (extraction+decision both fail);
      (b) the labeled filter's recall cost may HURT end-to-end vs unlabeled (C < B is a live outcome).
      We do NOT frame the ceiling as end-to-end.
  (3) DIFFICULTY-ON: non-simple construction fraction (coordination/pronoun/control/relative) reported.
  (4) ONE-VARIABLE per ablation arm (B vs C differ only in the candidate FILTER; same vote protocol/seeds).

VERDICT BANDS (pre-registered; this is a MEASUREMENT cell -- the primary deliverable is the NUMBER):
  HARD_PASS_LABELED_HELPS_ENDTOEND: C >= B + 0.02 AND C >= CRUDE + 0.05, min-over-seeds (C-B) > 0.
  HARD_FAIL_LABELED_HURTS_ENDTOEND: C < B (labeled filter recall cost dominates on end-to-end).
  MIDDLE_BAND: |C - B| < 0.02 (filter neutral) but both clear CRUDE + 0.05.
  Secondary CONJ verdict: conj-propagation RECOVERS coordination candidate-recall iff labeled+conjfix
    coordination-slice gold-in-pool > labeled-noconj coordination-slice gold-in-pool + 0.05.
  Secondary ABSTAIN verdict: abstain HELPS iff committed-precision(abstain) >= forced-precision + 0.02 at
    realized abstain-rate <= 0.35.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- ~114 gold sentences parsed once + a
  mining pass for gfit/teacher (cached) + 3-seed 13-dim delta-rule vote fits (<1s each). Total wall
  < ~120s smoke / < ~240s full. Storage: no_storage (decision-precision measurement). progress_logging:
  print_flush_true. Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, numpy default_rng, sorted(set); NO
  hash()-seeded RNG. LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO remote-persist, NO git add.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke (unlabeled-vote vs labeled-vote weight vectors bit-differ per seed).
  - final_metrics_atomicity: tmp_replace
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: end-to-end decision-precision measurement; no quantitative noise floor for the discriminator.
  - baseline_in_band at smoke (CRUDE + UNLABELED+VOTE end-to-end strictly inside (0.05, 0.95)).
  - discriminator survives scale: smoke runs the SAME verdict logic; full re-verifies over 3 seeds.
  - HARD_PASS strictly above floor (+0.02 over UNLABELED, +0.05 over CRUDE; not an at-floor tie).
  - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
  - deterministic_seeding: fixed ints + default_rng + sorted(set); no hash()/list(set()) ordering.

PRIOR-WORK CHECK (substrate_query.sh "end-to-end reader who-is-affected ... integrated vote pipeline"):
  top hit cosine=0.3184 ("Pipeline integration", a routing note) -- NONE at cosine>0.30 is an actual prior
  end-to-end reader CELL. This cell is GENUINELY NOVEL: every prior reader cell measured either extraction
  (candidate recall) OR decision (on ORACLE pools) IN ISOLATION; this is the FIRST composition measuring
  extraction x decision on REAL parser parses (the true reader capability). CITED@backup-doc 2026-07-20.
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

ANCHOR_NAME = "reader_integration_endtoend_whoaffected_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_integrated_vote_role_decision_oracle_gold_v1 as IV  # noqa: E402

FRONTEND_DIR = os.path.join(REPO_ROOT, "data", "frontend_assets")
POS_PATH = os.path.join(FRONTEND_DIR, "pos_tagger_ud_ewt_upos.json")
ARC_PATH = os.path.join(FRONTEND_DIR, "arc_parser_hashed_ud_ewt.npz")
LABELER_PATH = os.path.join(FRONTEND_DIR, "arc_labeler_hashed_ud_ewt.json")

PATIENT_LABELS = {"obj", "nsubj:pass"}
PRONOUNS = {"it", "them", "him", "her", "me", "us", "you", "that", "which", "this",
            "these", "those", "himself", "herself", "itself", "themselves", "one", "he", "she", "they", "i"}


# ----------------------------------------------------------------------------------------------
# LABELED patient-role filter with CONJ-PROPAGATION FIX.
# ----------------------------------------------------------------------------------------------
def is_patient_labeled(a, labels, heads, conj_fix=True):
    """arg index a is a patient candidate iff its arc label is obj/nsubj:pass, OR (conj_fix) its label is
    `conj` and its conjunct-head's label is obj/nsubj:pass (patient-hood propagated through coordination)."""
    la = labels.get(a)
    if la in PATIENT_LABELS:
        return True
    if conj_fix and la == "conj":
        h = heads.get(a)
        if h is not None and labels.get(h) in PATIENT_LABELS:
            return True
    return False


def classify_construction(vidx, patient, toks_lc, pos, heads, labels):
    """Single primary construction bucket per gold pair (priority: relative > control > coordination >
    pronoun > simple). Heuristic over the parse; for REPORTING slices only (not used in any decision)."""
    n = len(toks_lc)
    hv = heads.get(vidx)
    lv = labels.get(vidx)
    # relative: verb modifies a nominal antecedent (acl / relcl_gap geometry).
    is_rel = (lv in ("acl",)) or (hv is not None and 1 <= hv <= n and pos[hv - 1] in ("NOUN", "PROPN", "PRON"))
    # control/xcomp: verb governed by 'to' or labeled xcomp.
    prev = toks_lc[vidx - 2] if vidx - 2 >= 0 else ""
    is_ctrl = (lv == "xcomp") or (prev == "to")
    # coordination: verb is a conjunct, OR any verb in the sentence is a conjunct (shared-arg coordination).
    is_coord = (lv == "conj") or any(pos[i - 1] == "VERB" and labels.get(i) == "conj" for i in range(1, n + 1))
    is_pron = patient in PRONOUNS
    if is_rel:
        return "relative"
    if is_ctrl:
        return "control"
    if is_coord:
        return "coordination"
    if is_pron:
        return "pronoun"
    return "simple"


# ----------------------------------------------------------------------------------------------
# Build PARSER-derived candidate-pool instances per gold verb-instance (extraction can FAIL: the gold
# patient is NOT guaranteed present -- that is the whole point vs the oracle pools).
# ----------------------------------------------------------------------------------------------
def build_parser_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, mode, conj_fix=True):
    """mode in {'unlabeled','labeled'}. Returns list of instances shaped like IV oracle instances plus
    parser provenance (construction, verb_found, gold_in_pool, per-cand arg_idx/rule/parser_margin)."""
    instances = []
    for sid in order:
        if sid not in gold:
            continue
        rec = gold[sid]
        parsed = gen.generate(sent_text[sid])          # ORIGINAL-case tokens (capitalization is a POS cue)
        toks, pos, heads = parsed.tokens, parsed.pos, parsed.heads
        margins = parsed.margins
        if not toks:
            continue
        labels = labeler.label(toks, pos, heads)
        toks_lc = [t.lower() for t in toks]
        verb_tokens = [(i, L.lemma_verb(toks_lc[i - 1])) for i in range(1, len(toks) + 1) if pos[i - 1] == "VERB"]

        def args_for(vidx):
            aa = [a for (v, a) in parsed.candidates if v == vidx]
            if mode == "labeled":
                aa = [a for a in aa if is_patient_labeled(a, labels, heads, conj_fix=conj_fix)]
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
                              "parser_margin": float(margins.get(a, 0.0)),
                              "label": labels.get(a)})
            return cands

        used = set()
        # POS instances: correct decision = output the gold patient.
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
            constr = classify_construction(vidx, patient, toks_lc, pos, heads, labels)
            instances.append({"sid": sid, "v_lemma": vlem, "v_surf": v_surf, "agent": agent,
                              "gold_patient": patient, "is_pos": True, "cands": cands,
                              "construction": constr, "verb_found": True,
                              "gold_in_pool": any(c["is_gold"] for c in cands)})
        # NOPAT instances: correct decision = keep NOTHING (used as training negatives + FP measurement).
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


# ----------------------------------------------------------------------------------------------
# Verb-disjoint split from the gold POS verbs (deterministic; applied identically to every instance set
# so oracle / unlabeled / labeled TRAIN and TEST cover the SAME verbs -> no leak, aligned comparison).
# ----------------------------------------------------------------------------------------------
def verb_split(gold, seed, frac_train=0.6):
    verbs = sorted(set(g["v"] for rec in gold.values() for g in rec["pos"]))
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(verbs))
    n_tr = max(1, int(round(frac_train * len(verbs))))
    tr = set(verbs[perm[i]] for i in range(n_tr))
    te = set(verbs) - tr
    if not te:
        te = {verbs[perm[-1]]}
        tr = tr - te
    return sorted(tr), sorted(te)


def sel_by_verb(instances, verbset):
    vs = set(verbset)
    return [i for i in instances if i["v_lemma"] in vs]


# ----------------------------------------------------------------------------------------------
# END-TO-END accuracy: vote-select top candidate; correct iff == gold patient; EMPTY pool = extraction miss
# = incorrect (this is the composition of extraction x decision -- both can fail).
# ----------------------------------------------------------------------------------------------
def endtoend_accuracy(w, pos_insts):
    if not pos_insts:
        return None, 0
    correct = 0
    for inst in pos_insts:
        if not inst["cands"]:
            continue  # extraction miss -> counted wrong (denominator includes it)
        pick = IV.select_pick(w, inst)[0]
        correct += int(pick["p"] == inst["gold_patient"])
    return round(correct / len(pos_insts), 4), len(pos_insts)


def gold_in_pool_rate(pos_insts):
    """Candidate-recall CEILING: fraction of gold POS pairs whose gold patient is in the parser pool."""
    if not pos_insts:
        return None, 0
    n_in = sum(1 for inst in pos_insts if inst["gold_in_pool"])
    return round(n_in / len(pos_insts), 4), len(pos_insts)


def giveaway_audit(pos_insts):
    """LEAK GUARD: verify NO single feature perfectly predicts the gold patient within a pool. For each pos
    instance whose gold patient IS in the pool AND the pool has >=2 candidates, check whether each single
    feature's argmax uniquely picks the gold candidate. A feature that does so on ~all instances is an
    f_func-style GIVEAWAY. Returns per-feature single-cue selection accuracy (on gold-present pools) -- any
    value ~1.0 flags a leak. Parser pools are gold-INDEPENDENT (candidates from candidates_from_parse
    structural rules; gold NEVER force-added), so this is expected to be well below 1.0."""
    usable = [i for i in pos_insts if i["gold_in_pool"] and len(i["cands"]) >= 2]
    if not usable:
        return {"n_usable_pools": 0, "max_single_feature_gold_selection_acc": None, "per_feature": {}, "leak": False}
    per_feat = {}
    for fi in range(IV.D):
        hit = 0
        for inst in usable:
            vals = [c["feat"][fi] for c in inst["cands"]]
            mx = max(vals)
            winners = [c for c in inst["cands"] if c["feat"][fi] == mx]
            if len(winners) == 1 and winners[0]["is_gold"]:
                hit += 1
        per_feat[IV.FEATURE_NAMES[fi]] = round(hit / len(usable), 4)
    mx_name = max(per_feat, key=lambda k: per_feat[k])
    mx_val = per_feat[mx_name]
    return {"n_usable_pools": len(usable), "max_single_feature_gold_selection_acc": mx_val,
            "max_single_feature": mx_name, "per_feature": per_feat, "leak": bool(mx_val >= 0.95)}


def per_construction_endtoend(w, pos_insts):
    """{construction: {n, endtoend_acc, gold_in_pool}} over a set of pos instances."""
    by = defaultdict(list)
    for inst in pos_insts:
        by[inst["construction"]].append(inst)
    out = {}
    for c, insts in sorted(by.items()):
        acc, n = endtoend_accuracy(w, insts)
        gip, _ = gold_in_pool_rate(insts)
        out[c] = {"n": n, "endtoend_acc": acc, "gold_in_pool": gip}
    return out


# ----------------------------------------------------------------------------------------------
# Graded abstain (SOFT self-monitoring): vote margin (top1-top2 sigmoid) conformal-calibrated on TRAIN pos.
# Report forced committed-precision vs abstain committed-precision + realized abstain rate. Also report the
# parser arc-margin + completeness confidence for CORRECT vs WRONG picks (graded inputs, not hard gates).
# ----------------------------------------------------------------------------------------------
def abstain_analysis(w, train_pos, test_pos, alpha, checker, sent_text):
    non_empty = [i for i in test_pos if i["cands"]]
    if not non_empty:
        return None
    cal_pos = [i for i in train_pos if i["cands"]]
    q = IV.conformal_margin_threshold(cal_pos, w, alpha) if cal_pos else None
    forced_correct = committed = committed_correct = n_abst = 0
    parser_margin_correct, parser_margin_wrong = [], []
    for inst in non_empty:
        pick, top1, top2 = IV.select_pick(w, inst)
        correct = int(pick["p"] == inst["gold_patient"])
        forced_correct += correct
        (parser_margin_correct if correct else parser_margin_wrong).append(float(pick.get("parser_margin", 0.0)))
        abstain = q is not None and -(L.sigmoid(top1) - L.sigmoid(top2)) > q
        if abstain:
            n_abst += 1
            continue
        committed += 1
        committed_correct += correct
    forced_prec = round(forced_correct / len(non_empty), 4)
    abst_prec = round(committed_correct / committed, 4) if committed else None
    abst_rate = round(n_abst / len(non_empty), 4)
    # completeness confidence for correct vs wrong (graded input; report-only).
    comp_correct, comp_wrong = [], []
    if checker is not None:
        for inst in non_empty:
            pick = IV.select_pick(w, inst)[0]
            correct = int(pick["p"] == inst["gold_patient"])
            try:
                res = checker.check(L.tokenize(sent_text.get(inst["sid"], "")))
                (comp_correct if correct else comp_wrong).append(float(res.confidence))
            except Exception:
                pass
    def m(xs):
        return round(float(np.mean(xs)), 4) if xs else None
    return {"conformal_alpha": alpha, "conformal_q": (round(q, 4) if q is not None else None),
            "forced_committed_precision": forced_prec, "abstain_committed_precision": abst_prec,
            "abstain_rate": abst_rate, "n_test_nonempty": len(non_empty), "n_abstained": n_abst,
            "parser_margin_mean_correct": m(parser_margin_correct),
            "parser_margin_mean_wrong": m(parser_margin_wrong),
            "completeness_conf_mean_correct": m(comp_correct),
            "completeness_conf_mean_wrong": m(comp_wrong)}


# ----------------------------------------------------------------------------------------------
# CRUDE 4-feature LCCP reader end-to-end (the incumbent), re-derived LIVE via L.run_arms on the reader's
# NATIVE extraction (not oracle pools). Per gold POS pair: did the crude reader output the correct patient?
# ----------------------------------------------------------------------------------------------
def crude_endtoend(order, sent_text, reader_svo, gold, epochs, keep_thr, seed, test_verbs):
    vocab = set()
    for sid in order:
        for tup in reader_svo.get(sid, []):
            vocab.update([tup[0], tup[2]])
    glove = L.load_glove_for(vocab)
    lccp_cfg = dict(sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=epochs, keep_thr=keep_thr,
                    subcat_thr=0.42, heldout_frac=0.25, k_constructions=4, kappa=1.5, seed=seed)
    dec, _a, _s, _h, _sn, _ig, _w = L.run_arms(order, reader_svo, sent_text, glove, lccp_cfg, seed)
    kept = dec["B_cuecomp"]
    kept_set = set((sid, L.lemma_verb(t[0]), t[2]) for sid, t in kept)
    tv = set(test_verbs)
    n_pos = correct = 0
    for sid, rec in gold.items():
        for g in rec["pos"]:
            if g["v"] not in tv:
                continue
            n_pos += 1
            correct += int((sid, g["v"], g["patient"]) in kept_set)
    prec = L.score_arm(kept, gold, only_verbs=tv)["precision"]
    return (round(correct / n_pos, 4) if n_pos else None), n_pos, prec


# ----------------------------------------------------------------------------------------------
# Config.
# ----------------------------------------------------------------------------------------------
def cfg_smoke():
    return dict(mode="smoke", slice_lessons=["L04", "L05", "L07"], epochs=40, lr=0.20, alpha=0.2,
                frac_train=0.6, seeds=[7, 13, 19])


def cfg_full():
    return dict(mode="full", slice_lessons=["L04", "L05", "L07", "L08", "L09", "L10", "L12"], epochs=60,
                lr=0.20, alpha=0.2, frac_train=0.6, seeds=[7, 13, 19])


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


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ----------------------------------------------------------------------------------------------
# Run.
# ----------------------------------------------------------------------------------------------
def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START slice={'+'.join(cfg['slice_lessons'])}", flush=True)

    # ---- Front-end (persisted glass-box; loaded, not retrained). ----
    from hdlab.candidate_generator import CandidateGenerator
    from hdlab.arc_labeler import ArcLabeler
    from hdlab.completeness_checker import CompletenessChecker
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    checker = CompletenessChecker.from_assets(POS_PATH, ARC_PATH, margin_floor=0.0)
    print(f"[{ANCHOR_NAME}:{mode}] front-end loaded", flush=True)

    # ---- Mining models (gfit + GloVe teacher; McGuffey gold source EXCLUDED from mining). ----
    iv_cfg = IV.cfg_smoke() if mode == "smoke" else IV.cfg_full()
    gfit_fn, sel_fn, gfit_stats, n_mine = IV.build_mining_models(iv_cfg, output_dir)
    print(f"[{ANCHOR_NAME}:{mode}] mining models: {gfit_stats['n_object_classes']} gfit classes, {n_mine} sents",
          flush=True)

    order, sent_text, reader_svo = L.load_slice_and_reader(cfg["slice_lessons"])
    gold, gold_meta = L.load_gold(cfg["slice_lessons"])

    # ---- Build the three instance sets (ORACLE for the train-shift probe; UNLABELED + LABELED parser pools).
    oracle_insts = IV.build_oracle_instances(order, sent_text, gold, gfit_fn, sel_fn)
    unlab_insts = build_parser_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "unlabeled")
    lab_insts = build_parser_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled", conj_fix=True)
    lab_noconj = build_parser_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled", conj_fix=False)

    lab_pos_all = [i for i in lab_insts if i["is_pos"]]
    n_pos = len(lab_pos_all)
    n_verb_found = sum(1 for i in lab_pos_all if i["verb_found"])
    ceiling_lab, _ = gold_in_pool_rate(lab_pos_all)
    ceiling_unlab, _ = gold_in_pool_rate([i for i in unlab_insts if i["is_pos"]])
    hard_frac = round(sum(1 for i in lab_pos_all if i["construction"] not in ("simple",)) / n_pos, 4) if n_pos else None
    # LEAK GUARD (f_func-style giveaway): no single feature may perfectly predict gold within a pool.
    leak_lab = giveaway_audit(lab_pos_all)
    leak_unlab = giveaway_audit([i for i in unlab_insts if i["is_pos"]])
    print(f"[{ANCHOR_NAME}:{mode}] gold POS pairs={n_pos} verb_found={n_verb_found} "
          f"ceiling(unlab)={ceiling_unlab} ceiling(lab+conj)={ceiling_lab} hard_frac={hard_frac}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] LEAK-GUARD lab: max_single_cue_gold_sel={leak_lab['max_single_feature_gold_selection_acc']} "
          f"({leak_lab['max_single_feature']}) leak={leak_lab['leak']} | unlab max={leak_unlab['max_single_feature_gold_selection_acc']}",
          flush=True)

    per_seed = []
    unlab_digests, lab_digests = {}, {}
    for seed in cfg["seeds"]:
        tr_v, te_v = verb_split(gold, seed, cfg["frac_train"])
        # TRAIN each vote on its OWN extraction distribution (one variable = the FILTER at eval).
        w_unlab, _, _ = IV.train_vote(sel_by_verb(unlab_insts, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])
        w_lab, _, _ = IV.train_vote(sel_by_verb(lab_insts, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])
        # Distribution-shift probe: vote trained on ORACLE pools, evaluated on parser LABELED test pools.
        w_oracle, _, _ = IV.train_vote(sel_by_verb(oracle_insts, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])

        unlab_te_pos = [i for i in sel_by_verb(unlab_insts, te_v) if i["is_pos"]]
        lab_te_pos = [i for i in sel_by_verb(lab_insts, te_v) if i["is_pos"]]
        lab_noconj_te_pos = [i for i in sel_by_verb(lab_noconj, te_v) if i["is_pos"]]
        lab_tr_pos = [i for i in sel_by_verb(lab_insts, tr_v) if i["is_pos"]]

        acc_unlab, n_u = endtoend_accuracy(w_unlab, unlab_te_pos)
        acc_lab, n_l = endtoend_accuracy(w_lab, lab_te_pos)
        acc_oracle_on_parser, _ = endtoend_accuracy(w_oracle, lab_te_pos)  # oracle-trained vote on parser test
        acc_crude, n_c, crude_prec = crude_endtoend(order, sent_text, reader_svo, gold, cfg["epochs"], 0.45,
                                                    seed, te_v)

        # Conj-propagation recovery on the coordination slice (candidate-recall + end-to-end).
        coord_conj = [i for i in lab_te_pos if i["construction"] == "coordination"]
        coord_noconj = [i for i in lab_noconj_te_pos if i["construction"] == "coordination"]
        gip_coord_conj, n_cc = gold_in_pool_rate(coord_conj)
        gip_coord_noconj, _ = gold_in_pool_rate(coord_noconj)
        acc_coord_conj, _ = endtoend_accuracy(w_lab, coord_conj)

        abst = abstain_analysis(w_lab, lab_tr_pos, lab_te_pos, cfg["alpha"], checker, sent_text)
        pc = per_construction_endtoend(w_lab, lab_te_pos)

        unlab_digests[seed] = hashlib.sha256(np.round(w_unlab, 6).tobytes()).hexdigest()[:16]
        lab_digests[seed] = hashlib.sha256(np.round(w_lab, 6).tobytes()).hexdigest()[:16]

        gain_lab_vs_unlab = round((acc_lab or 0) - (acc_unlab or 0), 4)
        gain_lab_vs_crude = round((acc_lab or 0) - (acc_crude or 0), 4)
        shift_delta = round((acc_lab or 0) - (acc_oracle_on_parser or 0), 4)  # train-on-parser minus train-on-oracle
        row = {
            "seed": seed, "n_train_verbs": len(tr_v), "n_test_verbs": len(te_v),
            "n_test_pos": n_l,
            "crude_endtoend_acc": acc_crude, "crude_precision_ref": round(crude_prec, 4),
            "unlabeled_vote_endtoend_acc": acc_unlab, "labeled_conjfix_vote_endtoend_acc": acc_lab,
            "oracle_trained_vote_on_parser_test_acc": acc_oracle_on_parser,
            "gain_labeled_vs_unlabeled": gain_lab_vs_unlab, "gain_labeled_vs_crude": gain_lab_vs_crude,
            "train_shift_delta_parser_minus_oracle": shift_delta,
            "test_ceiling_labeled_conjfix": gold_in_pool_rate(lab_te_pos)[0],
            "test_ceiling_unlabeled": gold_in_pool_rate(unlab_te_pos)[0],
            "coord_gold_in_pool_conjfix": gip_coord_conj, "coord_gold_in_pool_noconj": gip_coord_noconj,
            "coord_n": n_cc, "coord_endtoend_acc_conjfix": acc_coord_conj,
            "per_construction": pc, "abstain": abst,
            "w_labeled_conjfix": [round(x, 4) for x in w_lab.tolist()],
        }
        per_seed.append(row)
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} CRUDE={acc_crude} UNLAB+vote={acc_unlab} "
              f"LAB+conjfix+vote={acc_lab} (ceiling={row['test_ceiling_labeled_conjfix']}) "
              f"gain_vs_unlab={gain_lab_vs_unlab:+.3f} gain_vs_crude={gain_lab_vs_crude:+.3f} "
              f"shift(parser-oracle)={shift_delta:+.3f} coord_gip(conj={gip_coord_conj} noconj={gip_coord_noconj} n={n_cc})",
              flush=True)

    # ---- Aggregate + verdict. ----
    def mean(key):
        vals = [s[key] for s in per_seed if s.get(key) is not None]
        return round(float(np.mean(vals)), 4) if vals else None

    def minv(key):
        vals = [s[key] for s in per_seed if s.get(key) is not None]
        return round(float(np.min(vals)), 4) if vals else None

    m_crude = mean("crude_endtoend_acc")
    m_unlab = mean("unlabeled_vote_endtoend_acc")
    m_lab = mean("labeled_conjfix_vote_endtoend_acc")
    m_oracle_on_parser = mean("oracle_trained_vote_on_parser_test_acc")
    m_ceiling = mean("test_ceiling_labeled_conjfix")
    m_gain_unlab = mean("gain_labeled_vs_unlabeled")
    min_gain_unlab = minv("gain_labeled_vs_unlabeled")
    m_gain_crude = mean("gain_labeled_vs_crude")
    m_shift = mean("train_shift_delta_parser_minus_oracle")
    m_coord_conj = mean("coord_gold_in_pool_conjfix")
    m_coord_noconj = mean("coord_gold_in_pool_noconj")

    # Aggregate per-construction end-to-end (mean over seeds where present).
    constr_agg = defaultdict(lambda: {"acc": [], "gip": [], "n": []})
    for s in per_seed:
        for c, d in s["per_construction"].items():
            if d["endtoend_acc"] is not None:
                constr_agg[c]["acc"].append(d["endtoend_acc"])
            if d["gold_in_pool"] is not None:
                constr_agg[c]["gip"].append(d["gold_in_pool"])
            constr_agg[c]["n"].append(d["n"])
    per_construction_mean = {c: {"mean_endtoend_acc": round(float(np.mean(v["acc"])), 4) if v["acc"] else None,
                                 "mean_gold_in_pool": round(float(np.mean(v["gip"])), 4) if v["gip"] else None,
                                 "mean_n": round(float(np.mean(v["n"])), 2)}
                             for c, v in sorted(constr_agg.items())}

    # Abstain aggregate.
    abst_forced = [s["abstain"]["forced_committed_precision"] for s in per_seed if s.get("abstain")]
    abst_committed = [s["abstain"]["abstain_committed_precision"] for s in per_seed
                      if s.get("abstain") and s["abstain"]["abstain_committed_precision"] is not None]
    abst_rate = [s["abstain"]["abstain_rate"] for s in per_seed if s.get("abstain")]
    m_forced = round(float(np.mean(abst_forced)), 4) if abst_forced else None
    m_abst = round(float(np.mean(abst_committed)), 4) if abst_committed else None
    m_abst_rate = round(float(np.mean(abst_rate)), 4) if abst_rate else None

    # Primary verdict: does the labeled parser + conj-fix HELP end-to-end (vs unlabeled + vs crude)?
    if m_lab is None or m_unlab is None:
        verdict = "UNKNOWN_NO_SEEDS"
    elif m_gain_unlab >= 0.02 and (m_gain_crude is not None and m_gain_crude >= 0.05) and (min_gain_unlab or 0) > 0:
        verdict = "HARD_PASS_LABELED_HELPS_ENDTOEND"
    elif m_gain_unlab < 0.0:
        verdict = "HARD_FAIL_LABELED_HURTS_ENDTOEND"
    else:
        verdict = "MIDDLE_BAND"

    conj_recovers = bool(m_coord_conj is not None and m_coord_noconj is not None
                         and (m_coord_conj - m_coord_noconj) >= 0.05)
    if m_forced is not None and m_abst is not None and m_abst_rate is not None:
        abstain_gain = round(m_abst - m_forced, 4)
        abstain_verdict = ("HARD_PASS_ABSTAIN_HELPS" if (abstain_gain >= 0.02 and m_abst_rate <= 0.35)
                           else ("HARD_FAIL_ABSTAIN_NO_HELP" if abstain_gain <= 0.0 else "MIDDLE_BAND_ABSTAIN"))
    else:
        abstain_gain, abstain_verdict = None, "UNKNOWN_ABSTAIN"

    # Design-gate checks.
    baseline_in_band = bool(m_crude is not None and 0.05 < m_crude < 0.95
                            and m_unlab is not None and 0.05 < m_unlab < 0.95)
    arms_differ_verified = all(unlab_digests[s] != lab_digests[s] for s in cfg["seeds"])
    endtoend_below_ceiling = bool(m_lab is not None and m_ceiling is not None and m_lab < m_ceiling + 1e-9)

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | slice={'+'.join(cfg['slice_lessons'])} gold_pos={n_pos} "
           f"| END-TO-END who-affected: CRUDE={m_crude} UNLAB+vote={m_unlab} LAB+conjfix+vote={m_lab} "
           f"(ceiling={m_ceiling}, gap={round((m_ceiling or 0)-(m_lab or 0),4)}) "
           f"gain_vs_unlab={m_gain_unlab:+.3f}(min={min_gain_unlab}) gain_vs_crude={m_gain_crude} "
           f"| train-shift(parser-oracle)={m_shift} oracle_trained_on_parser={m_oracle_on_parser} "
           f"| CONJ-recovery: coord_gip conj={m_coord_conj} noconj={m_coord_noconj} recovers={conj_recovers} "
           f"| ABSTAIN: forced={m_forced} committed={m_abst} rate={m_abst_rate} -> {abstain_verdict} "
           f"| hard_frac={hard_frac} baseline_in_band={baseline_in_band} arms_differ={arms_differ_verified} "
           f"below_ceiling={endtoend_below_ceiling} no_giveaway={not leak_lab['leak'] and not leak_unlab['leak']} "
           f"(max_single_cue_gold_sel lab={leak_lab['max_single_feature_gold_selection_acc']})")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": cfg["seeds"], "slice_lessons": cfg["slice_lessons"],
        "n_gold_pos_pairs": n_pos, "n_verb_found": n_verb_found, "hard_frac": hard_frac,
        "PRIMARY_endtoend_labeled_conjfix_vote": m_lab,
        "candidate_recall_ceiling_labeled_conjfix": m_ceiling,
        "endtoend_vs_ceiling_gap": round((m_ceiling or 0) - (m_lab or 0), 4),
        "ablation": {"crude_4feat": m_crude, "unlabeled_plus_vote": m_unlab,
                     "labeled_conjfix_plus_vote": m_lab},
        "gain_labeled_vs_unlabeled_mean": m_gain_unlab, "gain_labeled_vs_unlabeled_min": min_gain_unlab,
        "gain_labeled_vs_crude_mean": m_gain_crude,
        "train_distribution_shift_delta_parser_minus_oracle": m_shift,
        "oracle_trained_vote_on_parser_test_mean": m_oracle_on_parser,
        "conj_propagation_recovers_coordination": conj_recovers,
        "coord_gold_in_pool_conjfix_mean": m_coord_conj, "coord_gold_in_pool_noconj_mean": m_coord_noconj,
        "abstain_verdict": abstain_verdict, "abstain_gain": abstain_gain,
        "abstain_forced_precision_mean": m_forced, "abstain_committed_precision_mean": m_abst,
        "abstain_rate_mean": m_abst_rate,
        "per_construction_mean": per_construction_mean,
        "baseline_in_band": baseline_in_band, "arms_differ_verified": arms_differ_verified,
        "endtoend_below_ceiling": endtoend_below_ceiling,
        "leak_guard_labeled": leak_lab, "leak_guard_unlabeled": leak_unlab,
        "no_giveaway_verified": bool(not leak_lab["leak"] and not leak_unlab["leak"]),
        "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "end-to-end decision-precision measurement",
        "progress_logging": "print_flush_true", "compute_architecture": "sequential-CPU (justified: <4min)",
        "deterministic_seeding": True, "gold_meta": gold_meta,
        "per_seed": per_seed,
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


# ----------------------------------------------------------------------------------------------
# Self-test: EXERCISE THE REAL substrate code paths at tiny scale (front-end load + label + extended_features
# + the labeled/conj filter), asserting measured behavior BEFORE any full run (F.1 real_code_path).
# ----------------------------------------------------------------------------------------------
def self_test():
    print("=== reader_integration_endtoend self-test (real code paths) ===", flush=True)
    from hdlab.candidate_generator import CandidateGenerator
    from hdlab.arc_labeler import ArcLabeler
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)

    # (1) passive: 'cake' must be nsubj:pass (labeled-patient), 'boy' obl (rejected by labeled filter).
    r = gen.generate("The cake was eaten by the boy.")
    labels = labeler.label(r.tokens, r.pos, r.heads)
    heads = r.heads
    cake_i = r.tokens.index("cake") + 1
    boy_i = r.tokens.index("boy") + 1
    assert labels[cake_i] == "nsubj:pass", f"self-test FAIL: cake label={labels[cake_i]} (want nsubj:pass)"
    assert is_patient_labeled(cake_i, labels, heads), "self-test FAIL: nsubj:pass not accepted by filter"
    assert not is_patient_labeled(boy_i, labels, heads), "self-test FAIL: obl by-agent accepted as patient"

    # (2) coordination conj-propagation: 'The boy took the blocks and pencils.' -> pencils is conj of blocks(obj).
    r2 = gen.generate("The boy took the blocks and pencils.")
    labels2 = labeler.label(r2.tokens, r2.pos, r2.heads)
    if "pencils" in r2.tokens:
        pen_i = r2.tokens.index("pencils") + 1
        if labels2.get(pen_i) == "conj":
            assert is_patient_labeled(pen_i, labels2, r2.heads, conj_fix=True), \
                "self-test FAIL: conj-propagation did not recover conjoined patient"
            assert not is_patient_labeled(pen_i, labels2, r2.heads, conj_fix=False), \
                "self-test FAIL: conj-fix flag has no effect (should differ)"
            print("[selftest] conj-propagation recovers conjoined patient: PASS", flush=True)

    # (3) extended_features real call (13-dim) on lowercased tokens.
    toks_lc = [t.lower() for t in r.tokens]
    feat, meta = IV.extended_features(toks_lc, "eaten", "cake", "eat", lambda v, p: (0.5, "x"), lambda v, p: 0.0)
    assert len(feat) == IV.D, f"self-test FAIL: feature dim {len(feat)} != {IV.D}"

    # (4) verb_split determinism + disjointness.
    gold = {"s1": {"pos": [{"v": "eat"}, {"v": "take"}, {"v": "throw"}, {"v": "build"}], "nopat": set(),
                   "pos_verbs": set()}}
    tr, te = verb_split(gold, 7, 0.6)
    tr2, te2 = verb_split(gold, 7, 0.6)
    assert tr == tr2 and te == te2, "self-test FAIL: verb_split nondeterministic"
    assert not (set(tr) & set(te)), "self-test FAIL: train/test verb overlap"
    print("[selftest] PASS: real front-end + labeled/conj filter + features + split all exercised", flush=True)
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
        _write_crash_metrics(output_dir, e)
        raise
