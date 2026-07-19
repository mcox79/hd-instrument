"""ASSEMBLED READING-AXIS compgen milestone: the CG-target test done RIGHT (INDEPENDENT gold).

QUESTION (the assembled end-to-end reading-axis shot):
  Feed the LCCP parser's output on REAL McGuffey narrative (the cleaner 0.50-precision front-end,
  exp_learned_argstruct_parser_lccp_independent_gold_v1 arm-C) -> the validated structure-content
  FACTORIZATION (exp_role_filler_factorization_conceptnet_cg_v1: LEARNED content-blind g bound to
  GloVe content via native FHRR) -> does the pipeline generalize COMPOSITIONALLY to held-out
  (concept, role) combinations, scored against INDEPENDENT gold (data/gold_mcguffey_lccp_argstruct_
  v1.json -- the CORRECT relations, NOT the reader's/LCCP's own output)?

WHY THIS FIXES THE READER-COUPLED CELL'S FATAL FLAW (a92fab1d / atom 29336,
  exp_role_filler_factorization_reader_coupled_cg_v1): that cell scored the compgen readout against
  the READER'S OWN memberships (self-consistent) -> extraction-CORRECTNESS was INVISIBLE; the algebra
  "absorbs error by construction" (recovering a WRONG extracted filler counted as success). THE FIX =
  INDEPENDENT gold: a held-out (slot, filler) query is END-TO-END correct iff the factorization
  recovers the parser's filler (algebra) AND that (v, role, filler) is TRUE per the independent gold.
  Because gold-truth is fixed per query (arm-independent), the end-to-end correctness CEILING = the
  parser's precision (~0.50) -- the honest cap the reader-coupled framing hid.

FEASIBILITY-FIRST (per the contract; the reader-coupled cell used the DENSE 79-lesson reader cache,
  2538 tuples, 96 surviving slots, ~1142 held-out-eligible pairs). Independent gold is GOLD-BOUND to
  the 7 annotated lessons (100 pos relations); the LCCP arm-C output on that slice is ~68 tuples.
  MEASURED@probe 2026-07-19: at min_train_fillers>=2 (a GENUINE "slot trained with >=2 OTHER concepts"
  recombination claim) a fair FZ split yields only 5 held-out pairs -- BELOW the machinery's floor of
  10. Only min_train_fillers=1 (donor slot retains a SINGLE trainable filler = a compromised, near-
  vacuous recombination) reaches ~12 held-out pairs. => the 280-item / 7-lesson gold is TOO SPARSE for
  a FAIR dense recombination compgen split. This is a REAL finding: the milestone's real requirement
  is a LARGER / DENSER independent gold. Per the contract we do NOT force a vacuous split; we report
  the blocker AND the largest fair measure possible.

WHAT THIS CELL MEASURES (two well-scoped things):
  (A) WELL-POWERED, INDEPENDENT-GOLD PARSER-CEILING DECOMPOSITION (the robust result): over ALL LCCP
      arm-C content memberships (n~=few dozen), what fraction is GOLD-TRUE? = the assembled pipeline's
      end-to-end correctness ceiling (~parser precision 0.50). This quantifies the magnitude of the
      reader-coupled self-consistency flaw: ~half the memberships feeding the factorization are
      gold-WRONG, so a self-consistent compgen score of s implies at most ~s * ceiling gold-correct.
  (B) EXPLORATORY, UNDERPOWERED compgen on the LARGEST split the sparse gold supports (min_train_
      fillers=1, ~12 held-out queries): ARM_FACTORED vs ARM_FLAT, scored BOTH self-consistently
      (algebra: recovers parser filler) AND against INDEPENDENT gold (end-to-end). Reports algebra-
      accuracy, the parser ceiling on the held-out queries, end-to-end (gold) accuracy, and the
      conditional P(algebra correct | gold-true) = does the factorization PRESERVE correctness on the
      CORRECT tuples (integration works, parser-bottlenecked) or DEGRADE it under noise. DIRECTIONAL
      only (n_heldout ~12, high variance, donor-slot retention thin) -- NOT a verdict.

ARMS (ONE VARIABLE: factorization vs flat on IDENTICAL LCCP-parsed data + split):
  ARM_FLAT (must-fail control): proto[slot] = mean training content; held-out filler never trained in
    the query slot -> structurally cannot recover held-out combos -> FAILS on algebra.
  ARM_FACTORED: LEARNED content-blind g_hat[slot]; est=unbind(S,g_hat[q]); argmax sim(est, x[cand]).
  Positive control (Gate-D): control_synthetic random FHRR content on the SAME parser relations +
    split -> reproduces the validated mechanism at THIS test regime (distinguishes "mechanism broken
    here" from "real content hard / data too sparse").

DESIGN-GATE (pre-registered; verified at smoke):
  (G1) REAL baseline = FLAT, must FAIL on held-out combos (algebra <= chance + 0.15, gap >= 0.30).
  (G2) CAN-FAIL-BOTH-WAYS: the pre-registered outcomes are (i) HARD_PASS = fair split feasible AND
       factorization generalizes at ~parser ceiling where flat fails; (ii) DEGRADE = factorization
       loses correctness below ceiling on noisy input; (iii) FEASIBILITY_BLOCKED = gold lacks held-out
       structure for a fair split. All reachable; (iii) is the realized branch here (reported, not forced).
  (G3) DIFFICULTY-ON: real LCCP-parsed relations on real narrative vs INDEPENDENT gold + genuine
       held-out (concept, role) combinations (not by-construction).
  (G4) ONE VARIABLE: FACTORED vs FLAT on identical LCCP-parsed data + identical split.

VERDICT BANDS (pre-registered):
  HARD_PASS_ASSEMBLED_READING_AXIS_CG: fair_split_feasible (min_train_fillers>=2, held_out>=10) AND
    real FACTORED end-to-end (gold) >= parser_ceiling - 0.10 AND (FACTORED - FLAT) algebra gap >= 0.30
    AND must-fail fired AND positive control reproduces. => the assembled pipeline generalizes
    compositionally on CORRECT (independently-verified) relations at the parser ceiling. (VET adjudicates
    CG vs CG-candidate; parser-capped + single-annotator gold caveated -- NOT a full CG.)
  HARD_FAIL_FACTORIZATION_DEGRADES: fair_split_feasible AND FACTORED end-to-end < parser_ceiling - 0.15
    OR conditional P(algebra|gold-true) < 0.70. => factorization loses correctness on the correct
    tuples under real noise (a real integration finding).
  FEASIBILITY_BLOCKED_GOLD_TOO_SPARSE: NO fair split (min_train_fillers>=2 gives < 10 held-out).
    => the independent gold lacks recombination density for a FAIR compgen split; milestone requirement
    = larger / denser independent gold. Largest-fair EXPLORATORY partial reported (directional only).
  MIDDLE_BAND: fair split feasible but between the bars.

BRAIN-CHECK (pre-registered; outcome NOT pre-assumed): the assembled pipeline (learned parse ->
  glass-box factorized readout) is the NS-CL learned-parse -> structured-reason pattern, brain-faithful.
  The honest cap = parser precision (0.50; the brain's comprehension is likewise bounded by its parse).
  Q: does the factorization PRESERVE the parser's correctness under held-out generalization (brain-
  faithful compositional readout, relational transfer TEM/grid CITED@Whittington 2020) or DEGRADE it
  on noisy fillers? Where's the real bound -- parser precision (front-end), or factorization robustness
  to noise (back-end), or (as realized here) GOLD COVERAGE (a fair-test design bound, not a substrate
  bound)? The realized bound is gold coverage: the substrate mechanism is validated dense; the missing
  piece is a denser independent gold to score it fairly.

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- the cell validates the
  FHRR bind/unbind substrate primitive as a reference computation on LCCP-parsed relations; a live LCCP
  recompute (~15s) + elementwise complex ops on a few dozen N<=256 vectors; wall < ~60s. Foreground
  local-to-completion (NO queue; NO push; NO remote-persist). Storage: BUNDLED is the object under test
  (one situation = a bundle of m bound pairs); no sharded store. Determinism: OMP/MKL/OPENBLAS=1, fixed
  int seeds + random.Random + torch.Generator + hashlib; no salted builtin hash / list(set) dedupe.

CELL-TEMPLATE MANDATORY (LOCAL foreground mechanism-proof; NOT queue-dispatched):
- arms_differ_verified at smoke (FACTORED vs FLAT held-out preds hashes differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (FLAT is the must-fail control; FACTORED has headroom)
- discriminator fires at smoke (FLAT << FACTORED algebra; positive control reproduces)
- scaffold-free witness: re-runs the REAL LCCP parser live -> REAL arm-C tuples -> REAL hdlab bind/
  unbind + REAL GloVe on a held-out combo; FACTORED recovers, FLAT fails; some memberships gold-true
  AND some gold-false (the independent-gold fix is visibly live).
- all numbers tagged HYPOTHESIZED@/THEORETICAL@/CITED@/MEASURED@ (MEASURED printed at run).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import gzip
import hashlib
import json
import random
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "role_filler_factorization_assembled_reading_axis_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Front-end (LCCP parser) + back-end (validated factorization) reused byte-identically.
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as LCCP  # noqa: E402
from experiments import exp_role_filler_factorization_conceptnet_cg_v1 as FZ  # noqa: E402
from hdlab.atoms import make_atoms  # noqa: E402
from hdlab.binding import bind as hdlab_bind  # noqa: E402
from hdlab.binding import unbind as hdlab_unbind  # noqa: E402

GLOVE_PATH = FZ.GLOVE_PATH
BETA_REAL = FZ.BETA_REAL
CONDITIONS = ["control_synthetic", "real_parser"]
# argument roles for the structural code slot = (verb_lemma, role).
_ROLE_OBJ, _ROLE_SUBJ = "OBJ", "SUBJ"
_FUNC = LCCP.FUNCWORD | LCCP.PRONOUN


def hash_str(s: str) -> int:
    return int.from_bytes(hashlib.sha256(s.encode("utf-8")).digest()[:4], "big") % 1000003


def _okc(tok: str) -> bool:
    """Content-word filler: >=2 alpha lowercase, not a funcword/pronoun."""
    return isinstance(tok, str) and len(tok) >= 2 and tok.isalpha() and tok.islower() and tok not in _FUNC


# ----------------------------------------------------------------------------------------------
# Get the LCCP arm-C parser output + independent gold LIVE (self-contained; non-stale).
# ----------------------------------------------------------------------------------------------
def get_parser_output_and_gold(lccp_cfg):
    """Run the REAL LCCP parser live; return (keptC tuples, gold dict, lccp_arm_metrics)."""
    am, tn, lc, p3, meta, dec, ho, sn = LCCP.run_config(lccp_cfg)
    keptC = [(sid, tuple(t)) for sid, t in dec["C_lccp"]]
    gold, _gmeta = LCCP.load_gold(lccp_cfg["slice_lessons"])
    lccp_summary = {"A_precision": am["A_handrule"]["all"]["precision"],
                    "C_precision": am["C_lccp"]["all"]["precision"],
                    "C_recall": am["C_lccp"]["all"]["recall"],
                    "n_reader_svo": meta["n_reader_svo"], "n_gold_pos": meta["n_gold_pos"],
                    "n_keptC": len(keptC)}
    return keptC, gold, lccp_summary


def build_gold_membership_sets(gold):
    """Type-level INDEPENDENT-gold membership sets: (v_lemma, patient) for OBJ; (v_lemma, agent|ref)
    for SUBJ. These are the CORRECT relations, independent of parser output."""
    gold_obj = set()
    gold_subj = set()
    for sid, rec in gold.items():
        for g in rec["pos"]:
            v = g["v"]
            gold_obj.add((v, g["patient"]))
            for r in ({g["agent"]} | set(g.get("refs", []))):
                gold_subj.add((v, r))
    return gold_obj, gold_subj


def parser_content_memberships(keptC):
    """concept -> set of (verb_lemma, role) slots, from LCCP arm-C tuples (content-word fillers only)."""
    concept_slotset = defaultdict(set)
    for sid, t in keptC:
        v = LCCP.lemma_verb(t[0]); a = t[1]; p = t[2]
        if _okc(p):
            concept_slotset[p].add((v, _ROLE_OBJ))
        if _okc(a):
            concept_slotset[a].add((v, _ROLE_SUBJ))
    return concept_slotset


def load_glove_for(concepts):
    want = set(concepts)
    vec = {}
    with gzip.open(GLOVE_PATH, "rt", encoding="utf-8") as f:
        f.readline()
        for line in f:
            sp = line.split(" ", 1)
            if sp[0] in want:
                vec[sp[0]] = [float(t) for t in sp[1].split()]
                if len(vec) == len(want):
                    break
    return vec


def slot_gold_true(slot_id, concept, gold_obj, gold_subj):
    """Is (verb, role, concept) TRUE per the independent gold? slot_id = (verb, role)."""
    v, role = slot_id
    if role == _ROLE_OBJ:
        return (v, concept) in gold_obj
    return (v, concept) in gold_subj


# ----------------------------------------------------------------------------------------------
# Build FZ-shaped membership views + independent-gold-true pair set, for a given density floor.
# ----------------------------------------------------------------------------------------------
def build_views(concept_slotset, vec, gold_obj, gold_subj, min_slot_fillers, min_slots):
    """Return FZ-shaped dict (vocab, glove, slot_fillers, concept_slots, pred_of_slot, slot_ids,
    eligible) + gold_true_pairs {(slot_idx, concept_idx)} + parser-ceiling counts. GloVe-covered only.
    NOTE: ALL glove-covered concepts are kept as potential fillers (single-slot concepts serve as
    valid co-fillers / grounding support for donor slots); only the ELIGIBLE (held-out-donor) list is
    restricted to concepts in >= min_slots slots. Pruning vocab by min_slots would strip co-fillers and
    collapse the (already sparse) recombination structure."""
    present = {c for c in concept_slotset if c in vec}
    c_slots = {c: sorted(concept_slotset[c]) for c in present}
    vocab = sorted(present)
    vidx = {c: i for i, c in enumerate(vocab)}

    raw_slot_fillers = defaultdict(list)
    for c in vocab:
        for sl in c_slots[c]:
            raw_slot_fillers[sl].append(c)
    surviving = sorted([sl for sl, fs in raw_slot_fillers.items()
                        if len(set(fs)) >= min_slot_fillers])
    slot_idx = {sl: j for j, sl in enumerate(surviving)}
    slot_fillers = {j: sorted(vidx[c] for c in set(raw_slot_fillers[sl])) for sl, j in slot_idx.items()}
    kept = sorted(slot_fillers.keys())
    reindex = {old: new for new, old in enumerate(kept)}
    slot_ids = [surviving[old] for old in kept]
    slot_fillers = {reindex[old]: slot_fillers[old] for old in kept}

    concept_slots = defaultdict(list)
    for j, fs in slot_fillers.items():
        for ci in fs:
            concept_slots[ci].append(j)
    concept_slots = {ci: sorted(js) for ci, js in concept_slots.items()}
    eligible = [ci for ci in concept_slots if len(concept_slots[ci]) >= min_slots]
    pred_of_slot = [sl[1] for sl in slot_ids]  # role (OBJ/SUBJ) for the breakdown

    # independent-gold-true membership pairs among the surviving views
    gold_true_pairs = set()
    n_mem = 0
    n_gold_mem = 0
    for j, fs in slot_fillers.items():
        for ci in fs:
            n_mem += 1
            if slot_gold_true(slot_ids[j], vocab[ci], gold_obj, gold_subj):
                gold_true_pairs.add((j, ci))
                n_gold_mem += 1

    glove = torch.tensor([vec[c] for c in vocab], dtype=torch.float32) if vocab else torch.zeros((0, 300))
    return {
        "vocab": vocab, "glove": glove, "slot_fillers": slot_fillers, "concept_slots": concept_slots,
        "pred_of_slot": pred_of_slot, "slot_ids": slot_ids, "eligible": eligible,
        "gold_true_pairs": gold_true_pairs, "n_mem": n_mem, "n_gold_mem": n_gold_mem,
    }


def try_split(views, min_train_fillers, seed):
    """Attempt FZ.build_split at a given fairness floor; return (held_out, trainable, held_by) or None."""
    try:
        return FZ.build_split(views["slot_fillers"], views["concept_slots"], views["eligible"],
                              1, min_train_fillers, random.Random(seed + 7))
    except Exception:
        return None


# ----------------------------------------------------------------------------------------------
# Content build + independent-gold-scored eval.
# ----------------------------------------------------------------------------------------------
def build_content(condition, glove, n_dim, gen):
    if condition == "control_synthetic":
        return make_atoms(glove.shape[0], n_dim, torch.complex64, gen)
    M_unit = glove / torch.clamp(glove.norm(dim=1, keepdim=True), min=1e-8)
    return FZ.glove_to_fhrr(M_unit, n_dim, BETA_REAL, gen)


def gold_score(test_held, preds_fac, preds_flat, gold_true_pairs):
    """Decompose against INDEPENDENT gold. test_held[i]=(assign,s_star,true_f); preds in test order.
    Returns algebra (self-consistent), parser-ceiling, end-to-end (gold), conditional P(alg|gold-true)."""
    n = len(test_held)
    alg_fac = alg_flat = 0
    n_gold_true = 0
    e2e_fac = e2e_flat = 0
    cond_num = cond_den = 0
    for i, (assign, s_star, true_f) in enumerate(test_held):
        af = int(preds_fac[i] == true_f)
        al = int(preds_flat[i] == true_f)
        gt = int((s_star, true_f) in gold_true_pairs)
        alg_fac += af; alg_flat += al; n_gold_true += gt
        e2e_fac += af * gt; e2e_flat += al * gt
        if gt:
            cond_den += 1; cond_num += af
    return {
        "algebra_factored": alg_fac / n, "algebra_flat": alg_flat / n,
        "parser_ceiling_heldout": n_gold_true / n,
        "endtoend_factored_gold": e2e_fac / n, "endtoend_flat_gold": e2e_flat / n,
        "conditional_algebra_given_goldtrue": (cond_num / cond_den) if cond_den else 0.0,
        "n_heldout_queries": n, "n_gold_true_queries": n_gold_true,
    }


# ----------------------------------------------------------------------------------------------
# Core run.
# ----------------------------------------------------------------------------------------------
def run_config(mode):
    # Gold coverage is fixed at the 7 annotated lessons, so the split only exists on the FULL LCCP
    # slice; mode controls ONLY the factorization seeds / N-sweep / n_test (the 2-lesson LCCP smoke
    # slice has no recombination structure). This keeps the discriminator alive at the cell's smoke.
    lccp_cfg = LCCP.cfg_full()
    keptC, gold, lccp_summary = get_parser_output_and_gold(lccp_cfg)
    gold_obj, gold_subj = build_gold_membership_sets(gold)
    concept_slotset = parser_content_memberships(keptC)
    vec = load_glove_for(list(concept_slotset.keys()))

    # (A) WELL-POWERED parser-ceiling decomposition over ALL parser content memberships (any density).
    full_views = build_views(concept_slotset, vec, gold_obj, gold_subj, min_slot_fillers=1, min_slots=1)
    parser_ceiling_all = full_views["n_gold_mem"] / max(1, full_views["n_mem"])

    # FEASIBILITY: fair split needs min_train_fillers>=2 (slot trained with >=2 OTHER concepts).
    fair_views = build_views(concept_slotset, vec, gold_obj, gold_subj, min_slot_fillers=2, min_slots=2)
    fair_split = try_split(fair_views, min_train_fillers=2, seed=7)
    fair_split_feasible = fair_split is not None and len(fair_split[0]) >= 10

    # LARGEST split the sparse gold supports (exploratory; min_train_fillers=1 -> donor retains 1).
    expl_views = build_views(concept_slotset, vec, gold_obj, gold_subj, min_slot_fillers=1, min_slots=2)
    expl_split = try_split(expl_views, min_train_fillers=1, seed=7)

    if fair_split_feasible:
        views, mtf, split_kind = fair_views, 2, "fair"
    elif expl_split is not None and len(expl_split[0]) >= 10:
        views, mtf, split_kind = expl_views, 1, "exploratory_underpowered"
    else:
        views, mtf, split_kind = None, None, "none"

    m, knn = 6, 10
    chance = 1.0 / (m + knn)
    cap_dims = [64, 128, 256]
    headline_dim = min(cap_dims)
    seeds = [7, 13, 19] if mode == "full" else [7, 13]
    n_test = 120

    compgen = None
    per_seed_preds = None
    if views is not None:
        slot_fillers = views["slot_fillers"]
        concept_slots = views["concept_slots"]
        pred_of_slot = views["pred_of_slot"]
        glove = views["glove"]
        gold_true_pairs = views["gold_true_pairs"]
        n_slots = len(slot_fillers)

        per_seed = []
        preds_capture = None
        for seed in seeds:
            held_out, trainable, held_by = FZ.build_split(
                slot_fillers, concept_slots, views["eligible"], 1, mtf, random.Random(seed + 7))
            test_held = FZ.make_heldout_set(n_test, m, trainable, held_by, random.Random(seed + 100000))
            train_sit = FZ.balanced_train(m, 24, trainable, random.Random(seed * 1000 + 24))
            cond_out = {}
            for cond in CONDITIONS:
                caps = []
                fac_hi = flat_hi = None
                score_hi = None
                for n_dim in cap_dims:
                    gen_g = torch.Generator().manual_seed(seed + n_dim)
                    g_true = make_atoms(n_slots, n_dim, torch.complex64, gen_g)
                    gen_c = torch.Generator().manual_seed(seed * 31 + hash_str(cond) + n_dim)
                    x = build_content(cond, glove, n_dim, gen_c)
                    nn_index = FZ.global_nn_index(x)
                    g_hat, proto, cnt = FZ.learn(train_sit, n_slots, g_true, x, n_dim)
                    acc, pp, pf, pl = FZ.eval_heldout(test_held, g_true, g_hat, proto, x, knn,
                                                      nn_index, pred_of_slot)
                    caps.append({"n_dim": n_dim, "factored": acc["factored"], "flat": acc["flat"],
                                 "g_hat_cos": float(FZ.sim_rowwise(g_hat, g_true).mean())})
                    if n_dim == headline_dim:
                        fac_hi, flat_hi = pf, pl
                        score_hi = gold_score(test_held, pf, pl, gold_true_pairs)
                cond_out[cond] = {"capacity": caps, "score_headline": score_hi}
                if cond == "real_parser" and preds_capture is None:
                    preds_capture = (fac_hi, flat_hi)
            per_seed.append({"seed": seed, "conditions": cond_out})
        per_seed_preds = preds_capture

        # aggregate
        def mean(xs):
            return sum(xs) / len(xs) if xs else 0.0
        agg = {}
        for cond in CONDITIONS:
            keys = per_seed[0]["conditions"][cond]["score_headline"].keys()
            agg[cond] = {k: mean([s["conditions"][cond]["score_headline"][k] for s in per_seed])
                         for k in keys}
            agg[cond]["capacity"] = [
                {"n_dim": cap_dims[i],
                 "factored": mean([s["conditions"][cond]["capacity"][i]["factored"] for s in per_seed]),
                 "flat": mean([s["conditions"][cond]["capacity"][i]["flat"] for s in per_seed]),
                 "g_hat_cos": mean([s["conditions"][cond]["capacity"][i]["g_hat_cos"] for s in per_seed])}
                for i in range(len(cap_dims))]
        compgen = {"split_kind": split_kind, "min_train_fillers": mtf, "chance": chance,
                   "m": m, "knn": knn, "headline_dim": headline_dim, "aggregate": agg,
                   "n_slots": n_slots, "n_eligible_concepts": len(views["eligible"]),
                   "donor_retention_note": ("min_train_fillers=1 -> donor slots may retain a SINGLE "
                                            "trainable filler = compromised recombination"
                                            if mtf == 1 else "fair (>=2 trainable fillers per donor)")}

    meta = {
        "lccp_slice": lccp_cfg["slice_lessons"], "lccp_summary": lccp_summary,
        "parser_ceiling_all_memberships": parser_ceiling_all,
        "n_parser_content_memberships": full_views["n_mem"],
        "n_gold_true_memberships": full_views["n_gold_mem"],
        "feasibility": {
            "fair_split_feasible": fair_split_feasible,
            "fair_split_min_train_fillers": 2,
            "fair_split_held_out": (len(fair_split[0]) if fair_split is not None else 0),
            "fair_views_n_slots": len(fair_views["slot_fillers"]),
            "fair_views_n_eligible": len(fair_views["eligible"]),
            "exploratory_split_held_out": (len(expl_split[0]) if expl_split is not None else 0),
            "exploratory_views_n_slots": len(expl_views["slot_fillers"]),
            "exploratory_views_n_eligible": len(expl_views["eligible"]),
            "fz_floor_held_out": 10,
            "note": ("gold-bound to the annotated lessons; a FAIR recombination split (donor slot "
                     "trained with >=2 OTHER concepts) needs a denser gold than 280 items / 7 lessons"),
        },
        "gold_membership_counts": {"n_gold_obj_pairs": len(gold_obj), "n_gold_subj_pairs": len(gold_subj)},
        "vocab_sample": full_views["vocab"][:24],
    }
    return meta, compgen, per_seed_preds, chance


# ----------------------------------------------------------------------------------------------
# Verdict.
# ----------------------------------------------------------------------------------------------
def build_verdict(meta, compgen, chance):
    feas = meta["feasibility"]
    parser_ceiling = meta["parser_ceiling_all_memberships"]
    must_fail = False
    real_gap = 0.0
    real_e2e = 0.0
    real_alg = 0.0
    conditional = 0.0
    pos_ctrl = False
    if compgen is not None:
        real = compgen["aggregate"]["real_parser"]
        ctrl = compgen["aggregate"]["control_synthetic"]
        real_alg = real["algebra_factored"]
        real_e2e = real["endtoend_factored_gold"]
        conditional = real["conditional_algebra_given_goldtrue"]
        real_gap = real["algebra_factored"] - real["algebra_flat"]
        must_fail = bool(real["algebra_flat"] <= chance + 0.15 and real_gap >= 0.30)
        pos_ctrl = bool(ctrl["algebra_factored"] >= 0.70 and
                        (ctrl["algebra_factored"] - ctrl["algebra_flat"]) >= 0.30)
        ceil_ref = real["parser_ceiling_heldout"]
    else:
        ceil_ref = parser_ceiling

    if feas["fair_split_feasible"]:
        if real_e2e >= ceil_ref - 0.10 and real_gap >= 0.30 and must_fail and pos_ctrl:
            verdict = "HARD_PASS_ASSEMBLED_READING_AXIS_CG"
        elif real_e2e < ceil_ref - 0.15 or conditional < 0.70:
            verdict = "HARD_FAIL_FACTORIZATION_DEGRADES"
        else:
            verdict = "MIDDLE_BAND"
    else:
        verdict = "FEASIBILITY_BLOCKED_GOLD_TOO_SPARSE"

    return {
        "verdict": verdict, "fair_split_feasible": feas["fair_split_feasible"],
        "parser_ceiling_all_memberships": round(parser_ceiling, 4),
        "exploratory_real_algebra_factored": round(real_alg, 4),
        "exploratory_real_endtoend_gold": round(real_e2e, 4),
        "exploratory_parser_ceiling_heldout": round(ceil_ref, 4),
        "exploratory_conditional_algebra_given_goldtrue": round(conditional, 4),
        "exploratory_must_fail_fired": must_fail, "exploratory_positive_control": pos_ctrl,
        "exploratory_gap_factored_minus_flat": round(real_gap, 4),
        "milestone_requirement": ("a LARGER / DENSER independent gold (more annotated lessons) is "
                                  "required for a FAIR independent-gold-scored recombination compgen; "
                                  "the substrate factorization is validated dense (atoms 29334-36), the "
                                  "binding bound here is GOLD COVERAGE (a fair-test design bound)."),
        "can_fail_both_ways": True,
    }


def arms_differ(per_seed_preds):
    if per_seed_preds is None:
        return {"note": "no split ran; arms-differ N/A"}
    pf, pl = per_seed_preds
    hpf = hashlib.sha256(json.dumps(list(map(int, pf))).encode()).hexdigest()
    hpl = hashlib.sha256(json.dumps(list(map(int, pl))).encode()).hexdigest()
    assert hpf != hpl, "META_RULE_AF: FACTORED and FLAT held-out preds bit-identical; arm bug"
    assert len(set(pf)) > 1, "META_RULE_AF: FACTORED preds degenerate (all identical filler)"
    return {"factored_pred_hash": hpf[:16], "flat_pred_hash": hpl[:16]}


# ----------------------------------------------------------------------------------------------
# Scaffold-free witness: re-run REAL LCCP -> REAL arm-C tuples -> REAL hdlab bind on a held-out combo.
# ----------------------------------------------------------------------------------------------
def scaffold_free_witness():
    keptC, gold, _ = get_parser_output_and_gold(LCCP.cfg_smoke())
    assert keptC, "witness: LCCP produced no arm-C tuples"
    gold_obj, gold_subj = build_gold_membership_sets(gold)
    css = parser_content_memberships(keptC)
    vec = load_glove_for(list(css.keys()))
    views = build_views(css, vec, gold_obj, gold_subj, min_slot_fillers=1, min_slots=1)
    # the independent-gold fix must be VISIBLE: some memberships gold-true, some gold-false.
    n_true = views["n_gold_mem"]; n_all = views["n_mem"]
    assert 0 < n_true < n_all, (f"witness: independent-gold not discriminating (true={n_true} all={n_all})"
                                f" -- self-consistency flaw would be invisible")

    # REAL hdlab bind/unbind held-out-combo micro-factorization (mirrors validated back-end).
    n = 512
    words = ["dog", "cat", "boy", "ball"]
    found = load_glove_for(words)
    for w in words:
        assert w in found, f"witness: GloVe missing {w}"
    M = torch.tensor([found[w] for w in words], dtype=torch.float32)
    M_unit = M / torch.clamp(M.norm(dim=1, keepdim=True), min=1e-8)
    gen = torch.Generator().manual_seed(11)
    x = FZ.glove_to_fhrr(M_unit, n, BETA_REAL, gen)
    g = make_atoms(2, n, torch.complex64, gen)
    CHASE_OBJ, CATCH_OBJ = 0, 1
    DOG, CAT, BOY, BALL = 0, 1, 2, 3
    b1 = FZ.fhrr_bind(g[CHASE_OBJ], x[CAT]); b2 = hdlab_bind(g[CHASE_OBJ], x[CAT])
    assert torch.allclose(b1, b2), "fhrr_bind != hdlab.binding.bind"
    train = [{CHASE_OBJ: BALL, CATCH_OBJ: CAT}, {CHASE_OBJ: BOY, CATCH_OBJ: BALL}]
    g_hat = torch.zeros((2, n), dtype=torch.complex64)
    proto = torch.zeros((2, n), dtype=torch.complex64)
    cnt = torch.zeros(2)
    for assign in train:
        S = torch.stack([hdlab_bind(g[sj], x[ci]) for sj, ci in sorted(assign.items())], 0).sum(0)
        for sj, ci in assign.items():
            g_hat[sj] += hdlab_unbind(S, x[ci]); proto[sj] += x[ci]; cnt[sj] += 1
    g_hat = FZ.unit_phase(g_hat / torch.clamp(cnt, min=1.0).unsqueeze(1))
    proto = FZ.unit_phase(proto / torch.clamp(cnt, min=1.0).unsqueeze(1))
    S = torch.stack([hdlab_bind(g[CHASE_OBJ], x[CAT]), hdlab_bind(g[CATCH_OBJ], x[BOY])], 0).sum(0)
    pool = [CAT, BOY]
    cb = torch.stack([x[c] for c in pool], 0)
    est = hdlab_unbind(S, g_hat[CHASE_OBJ])
    fac_pred = pool[int(torch.argmax(FZ.sim_to_codebook(est, cb)))]
    flat_pred = pool[int(torch.argmax(FZ.sim_to_codebook(proto[CHASE_OBJ], cb)))]
    assert fac_pred == CAT, f"witness: FACTORED failed held-out chase-OBJ=cat (got {fac_pred})"
    assert flat_pred != CAT, f"witness: FLAT unexpectedly recovered held-out combo (got {flat_pred})"
    return {"n_arm_c_tuples": len(keptC), "n_parser_memberships": n_all,
            "n_gold_true_memberships": n_true, "gold_discriminates": True,
            "factored_pred": "cat", "flat_pred": words[flat_pred], "witness": "PASS"}


# ----------------------------------------------------------------------------------------------
def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    output_dir = os.path.join(REPO_ROOT, "data",
                              f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    witness = scaffold_free_witness()
    meta, compgen, per_seed_preds, chance = run_config(mode)
    vd = build_verdict(meta, compgen, chance)
    hashes = arms_differ(per_seed_preds)

    elapsed = time.perf_counter() - t0
    v = vd["verdict"]
    feas = meta["feasibility"]
    msg = (f"{v} | slice={'+'.join(meta['lccp_slice'])} "
           f"| LCCP A_P={meta['lccp_summary']['A_precision']:.3f} C_P={meta['lccp_summary']['C_precision']:.3f} "
           f"n_keptC={meta['lccp_summary']['n_keptC']} "
           f"| parser_ceiling(all mem)={vd['parser_ceiling_all_memberships']:.3f} "
           f"({meta['n_gold_true_memberships']}/{meta['n_parser_content_memberships']}) "
           f"| FEAS fair={feas['fair_split_feasible']} fair_held={feas['fair_split_held_out']} "
           f"(floor={feas['fz_floor_held_out']}) expl_held={feas['exploratory_split_held_out']} "
           f"| EXPL real_alg={vd['exploratory_real_algebra_factored']:.3f} "
           f"e2e_gold={vd['exploratory_real_endtoend_gold']:.3f} "
           f"ceil_held={vd['exploratory_parser_ceiling_heldout']:.3f} "
           f"cond(alg|gold)={vd['exploratory_conditional_algebra_given_goldtrue']:.3f} "
           f"gap={vd['exploratory_gap_factored_minus_flat']:+.3f} "
           f"mustfail={vd['exploratory_must_fail_fired']} posctrl={vd['exploratory_positive_control']}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": v, "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "verdict_detail": vd, "data_meta": meta, "compgen_exploratory": compgen,
        "arms_differ_hashes": hashes, "arms_differ_verified": (per_seed_preds is not None),
        "scaffold_free_witness": witness, "final_metrics_atomicity": "tmp_replace",
        "content_source": "REAL GloVe-wiki-gigaword-300 (Pennington 2014) FHRR-encoded",
        "relation_source": ("LCCP arm-C parser output on McGuffey Third Reader (live recompute of "
                            "exp_learned_argstruct_parser_lccp_independent_gold_v1)"),
        "gold_source": ("data/gold_mcguffey_lccp_argstruct_v1.json -- INDEPENDENT single-annotator gold "
                        "(the CORRECT relations, NOT the parser's own output; fixes the reader-coupled "
                        "self-consistency flaw)"),
        "REQUIRED_FIELDS": ["verdict", "verdict_detail", "data_meta", "scaffold_free_witness"],
        "notes": ("ASSEMBLED reading-axis compgen with INDEPENDENT gold. FEASIBILITY_BLOCKED_GOLD_TOO_"
                  "SPARSE = the 280-item / 7-lesson gold lacks recombination density for a FAIR compgen "
                  "split (a genuine min_train_fillers>=2 split gives <10 held-out; below the machinery "
                  "floor). Well-powered result that DOES stand: the assembled pipeline's end-to-end "
                  "correctness ceiling = parser precision ~0.50, and ~half the memberships feeding the "
                  "reader-coupled factorization were gold-WRONG (quantifies the self-consistency flaw). "
                  "Exploratory underpowered partial (min_train_fillers=1, ~dozen held-out) reported "
                  "DIRECTIONAL only. Milestone requirement = a denser independent gold. CLAIM-VET-pending."),
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  LCCP: A_P={meta['lccp_summary']['A_precision']:.3f} C_P={meta['lccp_summary']['C_precision']:.3f} "
          f"C_R={meta['lccp_summary']['C_recall']:.3f} n_reader_svo={meta['lccp_summary']['n_reader_svo']} "
          f"n_keptC={meta['lccp_summary']['n_keptC']} n_gold_pos={meta['lccp_summary']['n_gold_pos']}", flush=True)
    print(f"  PARSER CEILING (independent gold, ALL memberships): "
          f"{vd['parser_ceiling_all_memberships']:.3f} = {meta['n_gold_true_memberships']}/"
          f"{meta['n_parser_content_memberships']} gold-true", flush=True)
    print(f"  FEASIBILITY: fair_split(min_train>=2) feasible={feas['fair_split_feasible']} "
          f"held_out={feas['fair_split_held_out']} (floor={feas['fz_floor_held_out']}) "
          f"| fair_views slots={feas['fair_views_n_slots']} elig={feas['fair_views_n_eligible']} "
          f"| exploratory(min_train=1) held_out={feas['exploratory_split_held_out']} "
          f"slots={feas['exploratory_views_n_slots']} elig={feas['exploratory_views_n_eligible']}", flush=True)
    if compgen is not None:
        print(f"  EXPLORATORY compgen [{compgen['split_kind']} min_train_fillers={compgen['min_train_fillers']} "
              f"n_slots={compgen['n_slots']} chance={chance:.3f}]:", flush=True)
        print(f"    {compgen['donor_retention_note']}", flush=True)
        for cond in CONDITIONS:
            a = compgen["aggregate"][cond]
            print(f"    [{cond}] alg_F={a['algebra_factored']:.3f} alg_FLAT={a['algebra_flat']:.3f} "
                  f"| ceil_held={a['parser_ceiling_heldout']:.3f} e2e_gold_F={a['endtoend_factored_gold']:.3f} "
                  f"e2e_gold_FLAT={a['endtoend_flat_gold']:.3f} "
                  f"cond(alg|gold)={a['conditional_algebra_given_goldtrue']:.3f} "
                  f"n_held={a['n_heldout_queries']:.0f} n_goldT={a['n_gold_true_queries']:.0f}", flush=True)
            for r in a["capacity"]:
                print(f"       N={r['n_dim']:>4} alg_F={r['factored']:.3f} alg_FLAT={r['flat']:.3f} "
                      f"gcos={r['g_hat_cos']:.3f}", flush=True)
    else:
        print("  EXPLORATORY compgen: NO split ran (even min_train_fillers=1 below floor).", flush=True)
    print(f"  MILESTONE REQUIREMENT: {vd['milestone_requirement']}", flush=True)
    print(f"  [witness] {witness}", flush=True)
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        w = scaffold_free_witness()
        print(f"[{ANCHOR_NAME}] self-test scaffold-free witness: {w}", flush=True)
        meta, compgen, preds, chance = run_config("smoke")
        vd = build_verdict(meta, compgen, chance)
        arms_differ(preds)
        print(f"[{ANCHOR_NAME}] self-test end-to-end: verdict={vd['verdict']} "
              f"parser_ceiling={vd['parser_ceiling_all_memberships']:.3f} "
              f"fair_feasible={vd['fair_split_feasible']} "
              f"expl_e2e_gold={vd['exploratory_real_endtoend_gold']:.3f} "
              f"expl_alg={vd['exploratory_real_algebra_factored']:.3f}", flush=True)
        return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {
            "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
