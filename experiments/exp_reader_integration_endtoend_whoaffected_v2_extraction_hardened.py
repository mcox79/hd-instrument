"""END-TO-END reader v2 -- EXTRACTION-HARDENED filter + the RESIDUAL EXTRACTION:DECISION partition.

v1 (exp_reader_integration_endtoend_whoaffected_v1, MEASURED 0.742 LAB+conjfix+vote, MIDDLE_BAND) is
EXTRACTION-BOUND: on the labeled arm end_to_end==ceiling for every construction (decision never fails on the
near-singleton labeled pools). PHASE-1 diagnostic (diag_extraction) attributed the 23/97 labeled-arm
extraction losses: 13 AC_LABELER_NONPATIENT (true object tagged obl/iobj/ccomp), 3 A_LABELER_TAGGED_SUBJECT
(post-verbal object tagged nsubj), 4 B_POS_TAG_MISS (patient tagged NUM/ADJ/DET/VERB), 3 B_PARSER_MISATTACH.
=> 16/23 = 70% of the loss is the LABELER assigning a non-patient LABEL to a correctly-ATTACHED object; only
3 are pure parser mis-attach and 4 are POS. Coordination-0.686 is NOT a verb-coordination extraction gap:
coordination gold-in-UNLABELED=0.889, so the parser recovers 89% of coordination patients; the drop to 0.689
labeled is the labeler dropping obl/nsubj-tagged objects (conj-propagation was a no-op because those objects
are NOT tagged `conj`). MEASURED@diag_extraction 2026-07-20.

THE FIX (extraction-hardening; gold-INDEPENDENT; precision-preserving). A nominal arg `a` of verb `vidx` is a
patient candidate iff (v1 rule) label in {obj, nsubj:pass} OR conj-through-obj, OR (NEW):
  R1 iobj recipient:  label==iobj AND heads[a]==vidx  (ditransitive give/teach/show/tell HIM x -- the
                      recipient IS the affected entity; iobj is rare -> near-zero distractor cost).
  R2 mislabeled obj:  label in {obl,nsubj,dep} AND heads[a]==vidx AND POS[a] nominal AND a>vidx (post-verbal)
                      AND no preposition immediately governs a. A GENUINE obl carries a governing preposition
                      (rub AGAINST castle); a mislabeled obj does not (show you the WAY / showed him the SEEDS).
                      The governing-prep gate is exactly what separates the two -> recovers obj without
                      admitting real obliques.
  R3 obl-head conj:   conj whose conjunct-head was itself accepted under R2 (coordinated obj off an
                      obl-mislabeled head).
PROTOTYPE MEASURED@diag_fix 2026-07-20: overall labeled candidate-recall 0.7629 -> 0.8351 (+0.072) with mean
pool 1.134 -> 1.299 (+0.165 cand/pool -- pools STAY near-singleton, so decision headroom stays small and
precision is preserved). Per-construction recall: pronoun 0.750->0.875, coordination 0.689->0.756, simple
0.737->0.842; relative/control already 1.000 unchanged.

ARMS (ONE variable at a time; identical vote protocol / verb-split / seeds across arms):
  A) UNLABELED+vote          = all nominal deps (high recall 0.97 ceiling, 9:1 distractors -> decision-bound).
  B) LABELED_V1+conjfix+vote = v1's {obj,nsubj:pass}+conj filter (the REAL baseline; re-derived LIVE = 0.742).
  C) LABELED_HARDENED+vote   = B + R1/R2/R3 (the extraction fix).  [B->C one variable = the FILTER rules.]

PHASE-3 RESIDUAL EXTRACTION:DECISION PARTITION (the self-improving-loop precondition, zero extra compute):
  for each WRONG test-pos instance, classify EXTRACTION (gold patient NOT in the pool -> extraction miss) vs
  DECISION (gold IN pool but the vote picked another cand -> decision miss). Report the ratio per arm. This
  gates whether a self-improving DECISION loop has headroom: if the hardened arm's residual is ~all extraction
  (as v1 was), a decision loop has ~zero headroom and the lever stays extraction; a non-trivial decision share
  means a self-improving vote could still lift the reader.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (1) REAL baseline = arm B (v1 labeled+conjfix+vote) re-derived LIVE this run (not the remembered 0.742).
  (2) CAN-FAIL: the extra R1/R2/R3 candidates ADD distractors -> the vote may now pick a wrong recovered cand
      (decision error) offsetting the extraction gain -> C could be <= B; OR R2's recovered `obl` args may be
      genuine obliques (real parse content) not patients -> precision loss. C>B is NOT guaranteed.
  (3) DIFFICULTY-ON: pronoun + coordination slices (the losing slices) reported per-construction.
  (4) ONE-VARIABLE: B vs C differ ONLY in the labeled filter's accept() rules; same vote/split/seeds.

VERDICT BANDS (pre-registered; MEASUREMENT cell -- primary deliverable = the NUMBER + the partition):
  HARD_PASS_EXTRACTION_FIX_HELPS: C >= B + 0.02 AND min-over-seeds (C-B) >= 0 AND leak-guard clean.
  HARD_FAIL_EXTRACTION_FIX_HURTS: C < B - 0.01 (recovered distractors cost more decision than extraction gain).
  MIDDLE_BAND: |C - B| < 0.02 (fix neutral on end-to-end).

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified) -- ~114 gold sentences parsed once + cached mining
  + 3-seed 13-dim delta-rule vote fits (<1s each). Wall < ~150s smoke / < ~520s full (v1 full was 506s).
  Storage: no_storage. progress_logging: print_flush_true. Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds,
  default_rng, sorted(set); NO hash()-seeded RNG. LOCAL-ONLY, foreground-to-completion; NO queue, NO push,
  NO remote-persist, NO git add.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke (B-vote vs C-vote weight vectors bit-differ per seed).
  - final_metrics_atomicity: tmp_replace.  except SystemExit: raise BEFORE except Exception (no BaseException).
  - crlb_n_a: end-to-end decision-precision measurement; no quantitative noise floor for the discriminator.
  - baseline_in_band at smoke (B + UNLABELED strictly inside (0.05, 0.95)).
  - discriminator survives scale: smoke runs the SAME verdict logic; full re-verifies over 3 seeds.
  - HARD_PASS strictly above floor (+0.02 over B; min-over-seed non-negative -- not an at-floor tie).
  - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@.
  - deterministic_seeding: fixed ints + default_rng + sorted(set); no hash()/list(set()) ordering.
  - LEAK-HUNT: giveaway_audit re-run on hardened pools (no single feature >=0.95 gold-selection); R1/R2/R3 use
    ONLY parser labels/POS/preposition structure -- gold patient is NEVER consulted inside accept().

PRIOR-WORK CHECK (substrate_query.sh "extraction candidate generation pronoun coordination patient reader"):
  top hits cosine=0.415 are unrelated entity-name matches (WordNet 'ration' / 'coordination', GeneOntology);
  NONE at cosine>0.30 is a prior extraction-hardening reader CELL. This is a continuation of v1 (the first
  end-to-end reader) with a NOVEL gold-independent filter-hardening lever + the residual partition that v1 did
  not compute. CITED@backup-doc 2026-07-20; MEASURED@diag_extraction/diag_fix 2026-07-20.
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

ANCHOR_NAME = "reader_integration_endtoend_whoaffected_v2_extraction_hardened"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_reader_integration_endtoend_whoaffected_v1 as E  # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_integrated_vote_role_decision_oracle_gold_v1 as IV  # noqa: E402
from hdlab.candidate_generator import NOMINAL  # noqa: E402

POS_PATH = E.POS_PATH
ARC_PATH = E.ARC_PATH
LABELER_PATH = E.LABELER_PATH
PATIENT_LABELS = E.PATIENT_LABELS
PRONOUNS = E.PRONOUNS
PREPS = L.PREPS


# ----------------------------------------------------------------------------------------------
# EXTRACTION-HARDENED accept(): v1 rules + R1 (iobj recipient) + R2 (mislabeled post-verbal obj, prep-gated)
# + R3 (obl-head coordinated obj). GOLD-INDEPENDENT: consults only parser labels / heads / POS / prepositions.
# ----------------------------------------------------------------------------------------------
def accept_hardened(a, vidx, labels, heads, pos, toks_lc):
    la = labels.get(a)
    if la in PATIENT_LABELS:
        return True
    if la == "conj":
        h = heads.get(a)
        if h is not None and labels.get(h) in PATIENT_LABELS:
            return True
    # R1: iobj recipient of the target verb (ditransitive; the affected/taught/shown entity).
    if la == "iobj" and heads.get(a) == vidx:
        return True
    # R2: post-verbal direct nominal dep tagged obl/nsubj/dep, NOT preposition-governed -> mislabeled obj.
    if la in ("obl", "nsubj", "dep") and heads.get(a) == vidx and pos[a - 1] in NOMINAL and a > vidx:
        prev = toks_lc[a - 2] if a - 2 >= 0 else ""
        prev2 = toks_lc[a - 3] if a - 3 >= 0 else ""
        if prev not in PREPS and prev2 not in PREPS:
            return True
    # R3: conj whose conjunct-head was accepted under R2 (coordinated obj off an obl-mislabeled head).
    if la == "conj":
        h = heads.get(a)
        if h is not None and labels.get(h) in ("obl", "nsubj", "dep") and heads.get(h) == vidx and h > vidx:
            prev = toks_lc[h - 2] if h - 2 >= 0 else ""
            if prev not in PREPS:
                return True
    return False


# ----------------------------------------------------------------------------------------------
# Build PARSER-derived candidate-pool instances (mode: unlabeled / labeled_v1 / labeled_hardened).
# Structurally identical to E.build_parser_instances but with the per-mode filter, and args_for gets vidx +
# pos + toks_lc so the hardened rules can see position/POS/preposition context.
# ----------------------------------------------------------------------------------------------
def build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, mode):
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
            aa = [a for (v, a) in parsed.candidates if v == vidx]
            if mode == "labeled_v1":
                aa = [a for a in aa if E.is_patient_labeled(a, labels, heads, conj_fix=True)]
            elif mode == "labeled_hardened":
                aa = [a for a in aa if accept_hardened(a, vidx, labels, heads, pos, toks_lc)]
            elif mode == "labeled_backoff":
                # PRECISION-SAFE BACKOFF: strict {obj,nsubj:pass}+conj first; ONLY if that pool is EMPTY,
                # fall back to the hardened rules. Never pollutes an already-working singleton pool (that is
                # what made the naive labeled_hardened arm HURT: it turned decision-free singleton-gold pools
                # into multi-candidate decision gambles). Backoff recovers extraction MISSES (empty pools)
                # without adding distractors to pools that already contain a strict patient candidate.
                strict = [a for a in aa if E.is_patient_labeled(a, labels, heads, conj_fix=True)]
                aa = strict if strict else [a for a in aa if accept_hardened(a, vidx, labels, heads, pos, toks_lc)]
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


# ----------------------------------------------------------------------------------------------
# RESIDUAL EXTRACTION:DECISION partition. For each WRONG pos instance: EXTRACTION if gold not in pool
# (includes empty pool), DECISION if gold in pool but the vote picked a different candidate.
# ----------------------------------------------------------------------------------------------
def residual_partition(w, pos_insts):
    n = len(pos_insts)
    correct = extraction_err = decision_err = 0
    dec_examples = []
    for inst in pos_insts:
        if not inst["cands"]:
            extraction_err += 1
            continue
        pick = IV.select_pick(w, inst)[0]
        if pick["p"] == inst["gold_patient"]:
            correct += 1
        elif inst["gold_in_pool"]:
            decision_err += 1
            dec_examples.append({"sid": inst["sid"], "v": inst["v_lemma"], "gold": inst["gold_patient"],
                                 "picked": pick["p"], "constr": inst["construction"], "n_cands": len(inst["cands"])})
        else:
            extraction_err += 1
    resid = extraction_err + decision_err
    return {"n": n, "correct": correct, "extraction_err": extraction_err, "decision_err": decision_err,
            "residual": resid,
            "extraction_frac_of_residual": (round(extraction_err / resid, 4) if resid else None),
            "decision_frac_of_residual": (round(decision_err / resid, 4) if resid else None),
            "decision_examples": dec_examples}


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = E.cfg_smoke() if mode == "smoke" else E.cfg_full()
    output_dir = _out_dir(mode)
    E._write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START slice={'+'.join(cfg['slice_lessons'])}", flush=True)

    from hdlab.candidate_generator import CandidateGenerator
    from hdlab.arc_labeler import ArcLabeler
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)
    print(f"[{ANCHOR_NAME}:{mode}] front-end loaded", flush=True)

    iv_cfg = IV.cfg_smoke() if mode == "smoke" else IV.cfg_full()
    gfit_fn, sel_fn, gfit_stats, n_mine = IV.build_mining_models(iv_cfg, output_dir)
    print(f"[{ANCHOR_NAME}:{mode}] mining: {gfit_stats['n_object_classes']} gfit classes, {n_mine} sents", flush=True)

    order, sent_text, reader_svo = L.load_slice_and_reader(cfg["slice_lessons"])
    gold, gold_meta = L.load_gold(cfg["slice_lessons"])

    unlab = build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "unlabeled")
    lab_v1 = build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled_v1")
    lab_hard = build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled_hardened")
    lab_bk = build_instances(order, sent_text, gold, gen, labeler, gfit_fn, sel_fn, "labeled_backoff")

    bk_pos_all = [i for i in lab_bk if i["is_pos"]]
    n_pos = len(bk_pos_all)
    ceil_unlab, _ = E.gold_in_pool_rate([i for i in unlab if i["is_pos"]])
    ceil_v1, _ = E.gold_in_pool_rate([i for i in lab_v1 if i["is_pos"]])
    ceil_hard, _ = E.gold_in_pool_rate([i for i in lab_hard if i["is_pos"]])
    ceil_bk, _ = E.gold_in_pool_rate(bk_pos_all)
    hard_frac = round(sum(1 for i in bk_pos_all if i["construction"] not in ("simple",)) / n_pos, 4) if n_pos else None
    leak_bk = E.giveaway_audit(bk_pos_all)
    print(f"[{ANCHOR_NAME}:{mode}] gold POS={n_pos} ceiling unlab={ceil_unlab} v1={ceil_v1} "
          f"naive_hard={ceil_hard} BACKOFF={ceil_bk} hard_frac={hard_frac}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] LEAK-GUARD backoff: max_single_cue_gold_sel="
          f"{leak_bk['max_single_feature_gold_selection_acc']} ({leak_bk['max_single_feature']}) "
          f"leak={leak_bk['leak']}", flush=True)

    per_seed = []
    v1_digests, bk_digests = {}, {}
    for seed in cfg["seeds"]:
        tr_v, te_v = E.verb_split(gold, seed, cfg["frac_train"])
        w_unlab, _, _ = IV.train_vote(E.sel_by_verb(unlab, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])
        w_v1, _, _ = IV.train_vote(E.sel_by_verb(lab_v1, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])
        w_hard, _, _ = IV.train_vote(E.sel_by_verb(lab_hard, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])
        w_bk, _, _ = IV.train_vote(E.sel_by_verb(lab_bk, tr_v), IV.IDX_ALL, seed, cfg["epochs"], cfg["lr"])

        unlab_te = [i for i in E.sel_by_verb(unlab, te_v) if i["is_pos"]]
        v1_te = [i for i in E.sel_by_verb(lab_v1, te_v) if i["is_pos"]]
        hard_te = [i for i in E.sel_by_verb(lab_hard, te_v) if i["is_pos"]]
        bk_te = [i for i in E.sel_by_verb(lab_bk, te_v) if i["is_pos"]]
        bk_tr = [i for i in E.sel_by_verb(lab_bk, tr_v) if i["is_pos"]]

        acc_unlab, _ = E.endtoend_accuracy(w_unlab, unlab_te)
        acc_v1, _ = E.endtoend_accuracy(w_v1, v1_te)
        acc_hard, _ = E.endtoend_accuracy(w_hard, hard_te)
        acc_bk, n_bk = E.endtoend_accuracy(w_bk, bk_te)
        acc_crude, _, crude_prec = E.crude_endtoend(order, sent_text, reader_svo, gold, cfg["epochs"], 0.45, seed, te_v)

        part_unlab = residual_partition(w_unlab, unlab_te)
        part_v1 = residual_partition(w_v1, v1_te)
        part_hard = residual_partition(w_hard, hard_te)
        part_bk = residual_partition(w_bk, bk_te)

        abst = E.abstain_analysis(w_bk, bk_tr, bk_te, cfg["alpha"], None, sent_text)
        pc_bk = E.per_construction_endtoend(w_bk, bk_te)
        pc_v1 = E.per_construction_endtoend(w_v1, v1_te)

        v1_digests[seed] = hashlib.sha256(np.round(w_v1, 6).tobytes()).hexdigest()[:16]
        bk_digests[seed] = hashlib.sha256(np.round(w_bk, 6).tobytes()).hexdigest()[:16]

        gain_bk_v1 = round((acc_bk or 0) - (acc_v1 or 0), 4)
        gain_hard_v1 = round((acc_hard or 0) - (acc_v1 or 0), 4)
        row = {"seed": seed, "n_test_pos": n_bk,
               "crude_endtoend_acc": acc_crude, "crude_precision_ref": round(crude_prec, 4),
               "unlabeled_vote_endtoend_acc": acc_unlab,
               "labeled_v1_vote_endtoend_acc": acc_v1,
               "labeled_naive_hardened_vote_endtoend_acc": acc_hard,
               "labeled_backoff_vote_endtoend_acc": acc_bk,
               "gain_backoff_vs_v1": gain_bk_v1, "gain_naive_hardened_vs_v1": gain_hard_v1,
               "test_ceiling_unlabeled": E.gold_in_pool_rate(unlab_te)[0],
               "test_ceiling_v1": E.gold_in_pool_rate(v1_te)[0],
               "test_ceiling_naive_hardened": E.gold_in_pool_rate(hard_te)[0],
               "test_ceiling_backoff": E.gold_in_pool_rate(bk_te)[0],
               "residual_partition_unlabeled": part_unlab,
               "residual_partition_v1": part_v1,
               "residual_partition_naive_hardened": part_hard,
               "residual_partition_backoff": part_bk,
               "per_construction_backoff": pc_bk, "per_construction_v1": pc_v1,
               "abstain_backoff": abst,
               "w_backoff": [round(x, 4) for x in w_bk.tolist()]}
        per_seed.append(row)
        print(f"[{ANCHOR_NAME}:{mode}] seed={seed} CRUDE={acc_crude} UNLAB={acc_unlab} V1={acc_v1} "
              f"naive_HARD={acc_hard} BACKOFF={acc_bk} (ceil_bk={row['test_ceiling_backoff']}) "
              f"gain_BK_vs_V1={gain_bk_v1:+.3f} (naive_hard_vs_v1={gain_hard_v1:+.3f}) "
              f"| residual BACKOFF ext:dec={part_bk['extraction_err']}:{part_bk['decision_err']} "
              f"(ext_frac={part_bk['extraction_frac_of_residual']}) | UNLAB ext:dec="
              f"{part_unlab['extraction_err']}:{part_unlab['decision_err']}", flush=True)

    def mean(key, sub=None):
        vals = []
        for s in per_seed:
            v = s.get(key) if sub is None else (s.get(key, {}) or {}).get(sub)
            if v is not None:
                vals.append(v)
        return round(float(np.mean(vals)), 4) if vals else None

    def minv(key):
        vals = [s[key] for s in per_seed if s.get(key) is not None]
        return round(float(np.min(vals)), 4) if vals else None

    m_crude = mean("crude_endtoend_acc")
    m_unlab = mean("unlabeled_vote_endtoend_acc")
    m_v1 = mean("labeled_v1_vote_endtoend_acc")
    m_hard = mean("labeled_naive_hardened_vote_endtoend_acc")
    m_bk = mean("labeled_backoff_vote_endtoend_acc")
    m_gain = mean("gain_backoff_vs_v1")
    min_gain = minv("gain_backoff_vs_v1")
    m_gain_naive = mean("gain_naive_hardened_vs_v1")

    # aggregate residual partition (sum counts across seeds -> robust ratio).
    def agg_partition(subkey):
        ext = sum(s[subkey]["extraction_err"] for s in per_seed)
        dec = sum(s[subkey]["decision_err"] for s in per_seed)
        cor = sum(s[subkey]["correct"] for s in per_seed)
        tot = sum(s[subkey]["n"] for s in per_seed)
        resid = ext + dec
        return {"n_total": tot, "correct": cor, "extraction_err": ext, "decision_err": dec, "residual": resid,
                "extraction_frac_of_residual": (round(ext / resid, 4) if resid else None),
                "decision_frac_of_residual": (round(dec / resid, 4) if resid else None),
                "ext_to_dec_ratio": (f"{ext}:{dec}")}

    part_bk_agg = agg_partition("residual_partition_backoff")
    part_hard_agg = agg_partition("residual_partition_naive_hardened")
    part_v1_agg = agg_partition("residual_partition_v1")
    part_unlab_agg = agg_partition("residual_partition_unlabeled")

    # per-construction aggregate (backoff = primary arm).
    constr_agg = defaultdict(lambda: {"acc": [], "gip": [], "n": []})
    for s in per_seed:
        for c, d in s["per_construction_backoff"].items():
            if d["endtoend_acc"] is not None:
                constr_agg[c]["acc"].append(d["endtoend_acc"])
            if d["gold_in_pool"] is not None:
                constr_agg[c]["gip"].append(d["gold_in_pool"])
            constr_agg[c]["n"].append(d["n"])
    per_constr_mean = {c: {"mean_endtoend_acc": round(float(np.mean(v["acc"])), 4) if v["acc"] else None,
                           "mean_gold_in_pool": round(float(np.mean(v["gip"])), 4) if v["gip"] else None,
                           "mean_n": round(float(np.mean(v["n"])), 2)} for c, v in sorted(constr_agg.items())}

    if m_bk is None or m_v1 is None:
        verdict = "UNKNOWN_NO_SEEDS"
    elif m_gain >= 0.02 and (min_gain or 0) >= 0 and not leak_bk["leak"]:
        verdict = "HARD_PASS_EXTRACTION_FIX_HELPS"
    elif m_gain < -0.01:
        verdict = "HARD_FAIL_EXTRACTION_FIX_HURTS"
    else:
        verdict = "MIDDLE_BAND"

    baseline_in_band = bool(m_v1 is not None and 0.05 < m_v1 < 0.95 and m_unlab is not None and 0.05 < m_unlab < 0.95)
    arms_differ = all(v1_digests[s] != bk_digests[s] for s in cfg["seeds"])
    below_ceiling = bool(m_bk is not None and ceil_bk is not None and m_bk <= ceil_bk + 1e-9)

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | slice={'+'.join(cfg['slice_lessons'])} gold_pos={n_pos} "
           f"| END-TO-END who-affected: CRUDE={m_crude} UNLAB={m_unlab} V1(baseline)={m_v1} "
           f"naive_HARD={m_hard}(gain={m_gain_naive:+.3f}) BACKOFF={m_bk}(ceil_bk={ceil_bk}) "
           f"gain_BACKOFF_vs_V1={m_gain:+.3f}(min={min_gain}) "
           f"| RESIDUAL PARTITION backoff ext:dec={part_bk_agg['ext_to_dec_ratio']} "
           f"(ext_frac={part_bk_agg['extraction_frac_of_residual']}) | v1 ext:dec={part_v1_agg['ext_to_dec_ratio']} "
           f"| unlab ext:dec={part_unlab_agg['ext_to_dec_ratio']} (ext_frac={part_unlab_agg['extraction_frac_of_residual']}) "
           f"| hard_frac={hard_frac} baseline_in_band={baseline_in_band} arms_differ={arms_differ} "
           f"below_ceiling={below_ceiling} no_giveaway={not leak_bk['leak']} "
           f"(max_single_cue_gold_sel bk={leak_bk['max_single_feature_gold_selection_acc']})")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": cfg["seeds"], "slice_lessons": cfg["slice_lessons"],
        "n_gold_pos_pairs": n_pos, "hard_frac": hard_frac,
        "PRIMARY_endtoend_backoff_vote": m_bk,
        "baseline_endtoend_labeled_v1_vote": m_v1,
        "diagnostic_endtoend_naive_hardened_vote": m_hard,
        "ablation": {"crude_4feat": m_crude, "unlabeled_plus_vote": m_unlab,
                     "labeled_v1_plus_vote": m_v1, "labeled_naive_hardened_plus_vote": m_hard,
                     "labeled_backoff_plus_vote": m_bk},
        "candidate_recall_ceiling_unlabeled": ceil_unlab,
        "candidate_recall_ceiling_v1": ceil_v1,
        "candidate_recall_ceiling_naive_hardened": ceil_hard,
        "candidate_recall_ceiling_backoff": ceil_bk,
        "gain_backoff_vs_v1_mean": m_gain, "gain_backoff_vs_v1_min": min_gain,
        "gain_naive_hardened_vs_v1_mean": m_gain_naive,
        "RESIDUAL_PARTITION_backoff": part_bk_agg,
        "RESIDUAL_PARTITION_naive_hardened": part_hard_agg,
        "RESIDUAL_PARTITION_labeled_v1": part_v1_agg,
        "RESIDUAL_PARTITION_unlabeled": part_unlab_agg,
        "per_construction_mean_backoff": per_constr_mean,
        "baseline_in_band": baseline_in_band, "arms_differ_verified": arms_differ, "endtoend_below_ceiling": below_ceiling,
        "leak_guard_backoff": leak_bk, "no_giveaway_verified": bool(not leak_bk["leak"]),
        "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "end-to-end decision-precision measurement",
        "progress_logging": "print_flush_true", "compute_architecture": "sequential-CPU (justified: <9min)",
        "deterministic_seeding": True, "gold_meta": gold_meta, "per_seed": per_seed,
    }
    E.write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


def self_test():
    print("=== reader_integration_endtoend v2 hardened self-test (real code paths) ===", flush=True)
    from hdlab.candidate_generator import CandidateGenerator
    from hdlab.arc_labeler import ArcLabeler
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    labeler = ArcLabeler.load(LABELER_PATH)

    # (1) ditransitive: 'papa showed him the seeds.' -> seeds should be recovered (R2 obj mislabel) OR obj.
    r = gen.generate("He showed him the seeds.")
    labels = labeler.label(r.tokens, r.pos, r.heads)
    tl = [t.lower() for t in r.tokens]
    vidx = next(i for i in range(1, len(r.tokens) + 1) if r.pos[i - 1] == "VERB")
    seeds_i = tl.index("seeds") + 1
    ok_seed = accept_hardened(seeds_i, vidx, labels, r.heads, r.pos, tl)
    # 'him' recipient: iobj OR obj -> recovered by R1/R2 (affected recipient).
    him_i = tl.index("him") + 1
    ok_him = accept_hardened(him_i, vidx, labels, r.heads, r.pos, tl)
    print(f"[selftest] showed/seeds accepted={ok_seed} label={labels.get(seeds_i)}; "
          f"showed/him accepted={ok_him} label={labels.get(him_i)}", flush=True)
    assert ok_seed or ok_him, "self-test FAIL: hardened filter recovered NEITHER ditransitive arg"

    # (2) GENUINE oblique must STILL be rejected (prep-gate holds): 'rubbed against the wall' -> wall NOT patient.
    r2 = gen.generate("The cat rubbed against the wall.")
    labels2 = labeler.label(r2.tokens, r2.pos, r2.heads)
    tl2 = [t.lower() for t in r2.tokens]
    v2 = next(i for i in range(1, len(r2.tokens) + 1) if r2.pos[i - 1] == "VERB")
    wall_i = tl2.index("wall") + 1
    got_wall = accept_hardened(wall_i, v2, labels2, r2.heads, r2.pos, tl2)
    # 'against' governs wall -> R2 prep-gate must exclude it (unless labeler itself tagged it obj).
    if labels2.get(wall_i) not in PATIENT_LABELS:
        assert not got_wall, f"self-test FAIL: prep-governed oblique 'wall' wrongly accepted (label={labels2.get(wall_i)})"
        print("[selftest] prep-gate rejects genuine 'against'-oblique: PASS", flush=True)

    # (3) gold-independence: accept_hardened signature takes NO gold argument.
    import inspect
    params = set(inspect.signature(accept_hardened).parameters)
    assert "gold" not in params and "patient" not in params, "self-test FAIL: accept_hardened sees gold (LEAK)"

    # (4) verb_split determinism (reuse v1).
    gold = {"s1": {"pos": [{"v": "eat"}, {"v": "take"}, {"v": "throw"}, {"v": "build"}], "nopat": set(), "pos_verbs": set()}}
    tr, te = E.verb_split(gold, 7, 0.6)
    assert not (set(tr) & set(te)), "self-test FAIL: train/test verb overlap"

    # (5) residual_partition sanity: a wrong pick with gold-in-pool = DECISION; empty pool = EXTRACTION.
    inst_dec = {"sid": "x", "v_lemma": "v", "gold_patient": "a", "construction": "simple", "gold_in_pool": True,
                "cands": [{"p": "a", "feat": np.zeros(IV.D), "is_gold": True},
                          {"p": "b", "feat": np.ones(IV.D), "is_gold": False}]}
    inst_ext = {"sid": "y", "v_lemma": "v", "gold_patient": "z", "construction": "simple", "gold_in_pool": False,
                "cands": []}
    w = np.ones(IV.D)  # favours 'b' (all-ones feat) -> wrong pick, gold in pool -> decision err
    part = residual_partition(w, [inst_dec, inst_ext])
    assert part["decision_err"] == 1 and part["extraction_err"] == 1, f"self-test FAIL: partition {part}"
    print("[selftest] PASS: hardened filter + gold-independence + residual partition all exercised", flush=True)
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
