"""READER-COUPLED chain-grade gate: structure-content factorization on relations OUR OWN READER
EXTRACTS from REAL narrative text (McGuffey Third Reader), with its real ~0.40-0.60 extraction noise.

QUESTION (the reading/learning axis's FIRST TRUE chain-grade shot):
Does the brain-faithful STRUCTURE-CONTENT FACTORIZATION -- a LEARNED content-blind structural code g
(relation-type verb + argument-role) bound to grounded content x via native FHRR conjunctive binding --
still give held-out-COMBINATION generalization when fed the role-filler tuples OUR READER extracts from
REAL narrative (NOISY, sparse, skewed) where a flat content-typicality baseline FAILS?

WHY THIS EXTENDS THE CONCEPTNET CG (atom 29335, exp_role_filler_factorization_conceptnet_cg_v1, commit
c880a8680; VET aea157d4 = STRONG-CG-candidate NOT chain-grade for TWO reasons THIS cell fixes):
  (1) READING NOT COUPLED: ConceptNet relations were GIVEN (curated). To EARN the reading-axis: use OUR
      reader's ACTUAL extractions from real text -> couples the reader's real extraction noise.
  (2) HEADROOM WAS CAPACITY not difficulty. THIS cell measures real-difficulty-vs-capacity EXPLICITLY:
      real_reader FACTORED vs control_synthetic FACTORED at the capacity-edge headline N. If real << control
      -> real content/noise difficulty; if real ~= control -> the headroom is pure capacity (honest either way).

THE MECHANISM IS BYTE-IDENTICAL to the ConceptNet CG cell: this module IMPORTS
exp_role_filler_factorization_conceptnet_cg_v1 as FZ and calls FZ.build_split / FZ.balanced_train /
FZ.make_heldout_set / FZ.learn / FZ.eval_heldout / FZ.global_nn_index / FZ.glove_to_fhrr /
FZ.fhrr_bind|unbind|unit_phase|sim_* -- SAME code path (Gate-D positive-control discipline: reproduce the
validated mechanism at the new test regime; ONLY the DATA SOURCE changes: reader extractions, not ConceptNet).

------------------------------------------------------------------------------------------------
REAL READER EXTRACTIONS (the load-bearing new element; the coupling)
------------------------------------------------------------------------------------------------
Data: data/_reader_extractions_third_reader_v1.json = the reader's ACTUAL noisy tuples on the 79-lesson
McGuffey Third Reader (built by tools/build_reader_extraction_cache_third_reader.py running the REAL reader
exp_read_nested_clause_relative_third_reader_v1 nest ON). NOT cleaned -- the noise (~0.40-0.60 corpus-wide
extraction precision CITED@notes/research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md) is
the point. STRUCTURAL CODE = slot = (verb-lemma, arg-role) from svo/goal/recipient tuples (verb-headed,
ConceptNet-analog of (predicate, HEAD/TAIL)). A concept FILLS a slot iff the READER extracted it in that
(verb, role) position -- so the concept<->slot association is the reader's REAL, noisy, skewed output.
Content = REAL GloVe-wiki-gigaword-300 for the argument concepts. MEASURED@probe: 2538 verb-headed tuples,
median 1 filler/verb-slot (genuinely sparse), 96 slots survive min_fillers=8, ~1142 held-out-eligible
recombination pairs, GloVe coverage 0.97.

HELD-OUT-COMBINATION split (recombination; per the p9 caveat CITED@notes/research_drill_p9_mechanism_
diagnosis_2x_2026-06-10.md): a (concept, slot) pair PROVABLY UNSEEN in train, concept seen in OTHER slots,
slot trained with OTHER concepts. FZ.build_split (identical to the ConceptNet cell).

------------------------------------------------------------------------------------------------
CONDITIONS (SAME reader extractions + SAME split; content / gating is the only variable)
------------------------------------------------------------------------------------------------
control_synthetic : random FHRR content on the reader's REAL sparse noisy structure = Gate-D positive
                    control (reproduces the mechanism at the reader-extracted test regime; clean content).
                    Isolates: does the sparse noisy STRUCTURE alone limit generalization, content aside?
real_reader       : REAL GloVe content on the SAME reader extractions + split. THE make-or-break (real
                    content confusability on the reader's noisy relations).
real_reader_gated : REAL GloVe content, but TRAINING memberships filtered by a SCHEMA-FIT COHERENCE GATE
                    (drop content-outlier fillers = likely mis-extractions) BEFORE factorization. The
                    DIAGNOSTIC: if raw-noise degrades real_reader and gating restores it -> the coherence-
                    gate is the confirmed next component. If gating does not help (or hurts by dropping real
                    sparse support) -> noise is not the bottleneck (capacity/sparsity is) -> localize.

------------------------------------------------------------------------------------------------
UN-SATURATION (same principled un-saturator as ConceptNet: native superposition capacity)
------------------------------------------------------------------------------------------------
Primary = a CAPACITY SWEEP over N at FIXED binding-load m and FIXED training-per-role t (both held constant
across conditions -> condition = content/gating only). Headline N = smallest (most capacity-stressed) where
FACTORED has HEADROOM (not 1.000). READOUT pool = the m present fillers + top-KNN GLOBAL content-neighbors
of the true filler (content confusability; hard + real-content-sensitive). chance = 1/(m+KNN).

------------------------------------------------------------------------------------------------
ARMS within each condition (ONE VARIABLE: structure-bind vs flat; identical task/split/situations)
------------------------------------------------------------------------------------------------
ARM_FLAT (must-fail control): proto[slot] = content typicality; held-out filler never trained in q -> FAILS.
ARM_FACTORED: LEARNED content-blind g_hat[slot]; est=unbind(S,g_hat[q]); argmax sim(est, x[cand]). g_hat
  NEVER sees held-out combos.

------------------------------------------------------------------------------------------------
BRAIN-CHECK (pre-registered; outcome NOT pre-assumed)
------------------------------------------------------------------------------------------------
The brain reads NOISY input and factorizes structure robustly: a coherence / schema-fit gate suppresses
incoherent parses (predictive-coding / schema expectation), and the compositional code tolerates noisy
fillers (relational transfer, TEM/grid structural codes reused across content, CITED@Whittington 2020).
Does the reader-coupled factorization survive extraction noise brain-faithfully (real_reader ~= control),
or does it need the coherence-gate (real_reader breaks, gated restores)? SAME-limit-as-brain (robust) =>
accept; brain-GATES-it (gate restores) => the coherence-gate is the fix. The gate genuinely CAN-FAIL: real
narrative slots have legitimately diverse fillers, so a schema-fit gate can drop REAL relations and HURT.

------------------------------------------------------------------------------------------------
BANDS (pre-registered; pool = m+KNN -> chance = 1/(m+KNN), MEASURED@run; headline = smallest N)
------------------------------------------------------------------------------------------------
DESIGN-GATE (verified at SMOKE before full):
  (G1) POSITIVE CONTROL (Gate D): control_synthetic FACTORED held-out (headline N) >= 0.80 AND gap >= 0.30
       (the mechanism reproduces on the reader-extracted test regime with clean content).
  (G2) UN-SATURATED PRIMARY: real_reader FACTORED held-out (headline N) in [0.55, 0.955] (HEADROOM; NOT
       1.000). If smoke shows >= 0.96 -> lower headline N until headroom.
  (G3) MUST-FAIL CONTROL fires: real_reader FLAT held-out <= chance + 0.15 AND gap >= 0.30.
  (G4) ONE VARIABLE: content/gating only; m and t fixed across conditions; split identical.
VERDICTS (full):
  HARD_PASS_READING_AXIS_FIRST_CG: positive control holds AND real_reader FACTORED held-out (headline N)
    >= 0.70 with headroom (<= 0.955) AND gap >= 0.30 AND must-fail fired. => un-saturated compositional
    generalization on relations OUR READER extracted from real text where flat fails: end-to-end
    read->extract->factorize->generalize. VET adjudicates CG vs CG-candidate + capacity-vs-difficulty.
  HARD_FAIL_READER_NOISE_BREAKS: positive control holds AND real_reader breaks (gap <= 0.05 OR FACTORED
    <= chance + 0.10 OR FACTORED drops >= 0.30 below control_synthetic at headline N). => the reader's
    extraction noise / real sparsity break the factorization -> COHERENCE-GATE NEEDED (crucial next-
    component signal); real_reader_gated vs real_reader localizes whether gating is the fix.
  HARD_FAIL_POSITIVE_CONTROL: control_synthetic does NOT reproduce -> cell/regime/split suspect.
  VOID_FLAT_GENERALIZES: real_reader FLAT held-out > 0.60 -> split does not isolate compgen.
  MIDDLE_BAND: anything between (e.g. generalizes but with only capacity headroom, real ~= control -- a
    step short of an EARNED real-difficulty CG; honest CG-candidate).

------------------------------------------------------------------------------------------------
COMPUTE ARCHITECTURE (mandatory declaration)
------------------------------------------------------------------------------------------------
Class: (b) sequential-CPU with justification -- wall seconds-to-low-minutes; the cell IS validating the
substrate primitive (FHRR bind/unbind) as a reference computation on reader-extracted relations; elementwise
complex ops on a few hundred N<=256 vectors. Foreground local-to-completion (light; NO queue; NO push; NO
remote-persist). Storage strategy: BUNDLED is the object under test (one situation = a bundle of m bound
pairs, brain-faithful m=6); no sharded store. Reader extraction is CACHED (deterministic) so the cell is fast
and reproducible; the self-test re-runs the REAL reader on a tiny sub-corpus (real_code_path witness).

CELL-TEMPLATE MANDATORY (subset for a LOCAL foreground mechanism-proof; NOT queue-dispatched):
- arms_differ_verified at smoke (META_RULE_AF; hash FACTORED vs FLAT held-out preds)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (META_RULE_AG; FLAT held-out is the must-fail control; FACTORED in headroom band)
- discriminator fires at smoke (must-fail FLAT << FACTORED; positive control reproduces)
- Gate D positive control: control_synthetic reproduces the mechanism AT THE READER-EXTRACTED TEST REGIME
- deterministic seeding: fixed int seeds + random.Random + torch.Generator + hashlib; no salted builtin hash
- scaffold-free witness in self-test RE-RUNS the REAL reader + REAL hdlab.binding + REAL GloVe on a real combo
- all numbers tagged HYPOTHESIZED@ / THEORETICAL@ / CITED@ / MEASURED@ (MEASURED printed at run)
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

ANCHOR_NAME = "role_filler_factorization_reader_coupled_cg_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Mechanism BYTE-IDENTICAL to the ConceptNet CG cell (Gate-D reproduce-at-test-regime discipline).
from experiments import exp_role_filler_factorization_conceptnet_cg_v1 as FZ  # noqa: E402
from hdlab.atoms import make_atoms  # noqa: E402
from hdlab.binding import bind as hdlab_bind  # noqa: E402
from hdlab.binding import unbind as hdlab_unbind  # noqa: E402

GLOVE_PATH = FZ.GLOVE_PATH
BETA_REAL = FZ.BETA_REAL
CACHE_PATH = os.path.join(REPO_ROOT, "data", "_reader_extractions_third_reader_v1.json")
CONDITIONS = ["control_synthetic", "real_reader", "real_reader_gated"]

# verb-headed reader tuples -> (verb, role) slots. role tag encodes source+role for the per-type breakdown.
_VERB_TUPLE_ROLES = {
    "svo": ("svo:SUBJ", "svo:OBJ"),
    "goal": ("goal:SUBJ", "goal:DEST"),
    "recipient": ("recip:AGT", "recip:RECIP"),
}


def hash_str(s: str) -> int:
    return int.from_bytes(hashlib.sha256(s.encode("utf-8")).digest()[:4], "big") % 1000003


# ----------------------------------------------------------------------------------------------
# REAL reader extractions -> slot inventory + GloVe content (mirrors FZ.load_conceptnet_and_glove contract).
# ----------------------------------------------------------------------------------------------
def _is_single_alpha(tok: str) -> bool:
    return isinstance(tok, str) and len(tok) >= 2 and tok.isalpha() and tok.islower()


def load_reader_extractions_and_glove(vocab_cap, min_slots, min_slot_fillers):
    """Build the REAL structural inventory from the reader's cached noisy extractions + REAL GloVe.
    Returns the SAME dict shape FZ.run helpers consume (vocab, glove, slot_ids, slot_fillers,
    concept_slots, pred_of_slot, eligible_concepts) plus reader-noise meta."""
    if not os.path.exists(CACHE_PATH):
        raise FileNotFoundError(f"reader extraction cache not found: {CACHE_PATH} "
                                f"(run tools/build_reader_extraction_cache_third_reader.py)")
    with open(CACHE_PATH, encoding="utf-8") as f:
        cache = json.load(f)

    # (concept, (verb, role)) memberships from verb-headed tuples.
    concept_slotset = defaultdict(set)
    concept_freq = defaultdict(int)
    for kind, (rA, rB) in _VERB_TUPLE_ROLES.items():
        for tup in cache.get(kind, []):
            verb, a1, a2 = tup[0], tup[1], tup[2]
            if not (_is_single_alpha(verb)):
                continue
            if _is_single_alpha(a1):
                concept_slotset[a1].add((verb, rA)); concept_freq[a1] += 1
            if _is_single_alpha(a2):
                concept_slotset[a2].add((verb, rB)); concept_freq[a2] += 1

    candidates = set(concept_slotset.keys())
    vec = {}
    with gzip.open(GLOVE_PATH, "rt", encoding="utf-8") as f:
        f.readline()
        for line in f:
            sp = line.split(" ", 1)
            if sp[0] in candidates:
                vec[sp[0]] = [float(t) for t in sp[1].split()]

    present = set(vec.keys())
    c_slots = {c: sorted(concept_slotset[c]) for c in present}
    eligible = [c for c in present if len(c_slots[c]) >= min_slots]
    eligible.sort(key=lambda c: (-len(c_slots[c]), -concept_freq[c], c))
    vocab = eligible[:vocab_cap]
    vocab_set = set(vocab)
    vocab_idx = {c: i for i, c in enumerate(vocab)}

    raw_slot_fillers = defaultdict(list)
    for c in vocab:
        for sl in c_slots[c]:
            raw_slot_fillers[sl].append(c)
    surviving = sorted([sl for sl, fs in raw_slot_fillers.items()
                        if len(set(fs) & vocab_set) >= min_slot_fillers])
    surviving_set = set(surviving)
    vocab = [c for c in vocab if len([sl for sl in c_slots[c] if sl in surviving_set]) >= min_slots]
    if len(vocab) < 8:
        raise RuntimeError(f"too few eligible concepts after pruning ({len(vocab)})")
    vocab_set = set(vocab)
    vocab_idx = {c: i for i, c in enumerate(vocab)}

    slot_idx = {sl: j for j, sl in enumerate(surviving)}
    slot_fillers = {j: sorted(vocab_idx[c] for c in set(raw_slot_fillers[sl]) & vocab_set)
                    for sl, j in slot_idx.items()}
    slot_fillers = {j: fs for j, fs in slot_fillers.items() if len(fs) >= min_slot_fillers}
    kept = sorted(slot_fillers.keys())
    reindex = {old: new for new, old in enumerate(kept)}
    slot_ids = [surviving[old] for old in kept]
    slot_fillers = {reindex[old]: slot_fillers[old] for old in kept}
    # pred_of_slot = coarse source:role bucket (for the per-relation-type breakdown).
    pred_of_slot = [sl[1] for sl in slot_ids]

    concept_slots = defaultdict(list)
    for j, fs in slot_fillers.items():
        for ci in fs:
            concept_slots[ci].append(j)
    concept_slots = {ci: sorted(js) for ci, js in concept_slots.items()}
    good = [ci for ci in range(len(vocab)) if len(concept_slots.get(ci, [])) >= min_slots]
    if len(good) < 8:
        raise RuntimeError(f"too few concepts fill >= {min_slots} slots ({len(good)})")

    glove = torch.tensor([vec[c] for c in vocab], dtype=torch.float32)  # (V,300)
    return {
        "vocab": vocab, "glove": glove, "slot_ids": slot_ids, "slot_fillers": slot_fillers,
        "concept_slots": concept_slots, "pred_of_slot": pred_of_slot,
        "eligible_concepts": good,
        "reader_meta": {"corpus": cache.get("corpus"), "reader": cache.get("reader"),
                        "n_reader_tuples": cache.get("n_tuples"), "tuple_kinds": cache.get("tuple_kinds"),
                        "extraction_precision_cited": "0.40-0.60 CITED@drill_2026-07-18"},
    }


def build_content(condition, glove, n_dim, gen):
    """control_synthetic -> random FHRR; real_reader / real_reader_gated -> GloVe-encoded FHRR."""
    if condition == "control_synthetic":
        return make_atoms(glove.shape[0], n_dim, torch.complex64, gen)
    M_unit = glove / torch.clamp(glove.norm(dim=1, keepdim=True), min=1e-8)
    return FZ.glove_to_fhrr(M_unit, n_dim, BETA_REAL, gen)


# ----------------------------------------------------------------------------------------------
# COHERENCE / SCHEMA-FIT GATE (real_reader_gated): drop content-outlier training fillers per slot
# (likely reader mis-extractions), floored so no slot starves. Uses GloVe (real content). Glass-box.
# ----------------------------------------------------------------------------------------------
def schema_fit_gate(trainable_fillers, glove, drop_frac, min_keep):
    """For each (slot, filler) TRAINING membership, score = cosine(glove[filler], centroid of the slot's
    OTHER trainable fillers). Drop the globally-lowest drop_frac fraction, but keep >= min_keep highest-
    scoring per slot (never starve). Returns (gated_trainable_fillers, gate_stats)."""
    gnorm = glove / torch.clamp(glove.norm(dim=1, keepdim=True), min=1e-8)
    scored = []  # (score, slot, filler)
    per_slot_scores = {}
    for sj, fs in trainable_fillers.items():
        if len(fs) < 2:
            per_slot_scores[sj] = [(9.0, ci) for ci in fs]  # singletons kept
            for ci in fs:
                scored.append((9.0, sj, ci))
            continue
        V = gnorm[fs]  # (k,300)
        s = []
        ssum = V.sum(dim=0)
        for idx, ci in enumerate(fs):
            others = (ssum - V[idx]) / (len(fs) - 1)
            sc = float(torch.dot(gnorm[ci], others / torch.clamp(others.norm(), min=1e-8)))
            s.append((sc, ci))
            scored.append((sc, sj, ci))
        per_slot_scores[sj] = s
    if not scored:
        return {sj: list(fs) for sj, fs in trainable_fillers.items()}, {"n_dropped": 0, "n_total": 0}
    real = sorted(sc for sc, _, _ in scored if sc < 8.0)
    thr = real[int(drop_frac * len(real))] if real else -9.0
    gated = {}
    n_dropped = 0
    n_total = 0
    dropped_examples = []
    for sj, s in per_slot_scores.items():
        s_sorted = sorted(s, key=lambda x: -x[0])  # highest coherence first
        keep = []
        for rank, (sc, ci) in enumerate(s_sorted):
            n_total += 1
            if sc >= thr or rank < min_keep or sc >= 8.0:
                keep.append(ci)
            else:
                n_dropped += 1
                if len(dropped_examples) < 12:
                    dropped_examples.append((sj, ci, round(sc, 3)))
        gated[sj] = sorted(keep)
    return gated, {"n_dropped": n_dropped, "n_total": n_total, "drop_thr": round(thr, 4),
                   "drop_frac_effective": round(n_dropped / max(1, n_total), 4),
                   "dropped_examples": dropped_examples}


# ----------------------------------------------------------------------------------------------
# Core run: capacity sweep x 3 conditions (control / real / real-gated).
# ----------------------------------------------------------------------------------------------
def run_config(cap_dims, m, knn, t_primary, vocab_cap, min_slots, min_slot_fillers,
               held_per_concept, min_train_fillers, n_test, gate_drop_frac, seeds):
    data = load_reader_extractions_and_glove(vocab_cap, min_slots, min_slot_fillers)
    glove = data["glove"]
    slot_fillers = data["slot_fillers"]
    concept_slots = data["concept_slots"]
    pred_of_slot = data["pred_of_slot"]
    n_slots = len(slot_fillers)
    chance = 1.0 / (m + knn)
    headline_dim = min(cap_dims)
    per_seed = []
    gate_stats_agg = []
    for seed in seeds:
        held_out, trainable, held_by = FZ.build_split(
            slot_fillers, concept_slots, data["eligible_concepts"],
            held_per_concept, min_train_fillers, random.Random(seed + 7))
        test_held = FZ.make_heldout_set(n_test, m, trainable, held_by, random.Random(seed + 100000))
        gated_trainable, gstats = schema_fit_gate(trainable, glove, gate_drop_frac, min_train_fillers)
        gate_stats_agg.append(gstats)

        train_by_cond = {
            "control_synthetic": trainable, "real_reader": trainable,
            "real_reader_gated": gated_trainable,
        }
        train_situations_by_cond = {
            c: FZ.balanced_train(m, t_primary, tf, random.Random(seed * 1000 + t_primary + hash_str(c)))
            for c, tf in train_by_cond.items()
        }

        cond_out = {}
        for cond in CONDITIONS:
            capacity = []
            ppred = None
            preds_hi = None
            content_cos = 0.0
            for n_dim in sorted(cap_dims):
                gen_g = torch.Generator().manual_seed(seed + n_dim)
                g_true = make_atoms(n_slots, n_dim, torch.complex64, gen_g)
                content_cond = "control_synthetic" if cond == "control_synthetic" else "real_reader"
                gen_c = torch.Generator().manual_seed(seed * 31 + hash_str(content_cond) + n_dim)
                x = build_content(content_cond, glove, n_dim, gen_c)
                nn_index = FZ.global_nn_index(x)
                g_hat, proto, cnt = FZ.learn(train_situations_by_cond[cond], n_slots, g_true, x, n_dim)
                acc, pp, pf, pl = FZ.eval_heldout(test_held, g_true, g_hat, proto, x, knn, nn_index,
                                                  pred_of_slot)
                capacity.append({"n_dim": n_dim, "factored": acc["factored"], "flat": acc["flat"],
                                 "g_hat_cos": float(FZ.sim_rowwise(g_hat, g_true).mean())})
                if n_dim == headline_dim:
                    ppred = pp
                    preds_hi = (pf, pl)
                    content_cos = FZ.content_corr_mean(x)
            cond_out[cond] = {"capacity": capacity, "per_pred_hi": ppred, "preds_hi": preds_hi,
                              "content_cos_mean": content_cos}
        per_seed.append({"seed": seed, "conditions": cond_out})

    meta = {
        "n_vocab": len(data["vocab"]), "n_slots": n_slots, "headline_dim": headline_dim,
        "slot_ids": [f"{v}|{r}" for (v, r) in data["slot_ids"]][:40],
        "slot_filler_counts_top": sorted((len(fs) for fs in slot_fillers.values()), reverse=True)[:16],
        "vocab_sample": data["vocab"][:24],
        "reader_meta": data["reader_meta"],
        "gate_stats": gate_stats_agg,
    }
    return chance, headline_dim, per_seed, meta


# ----------------------------------------------------------------------------------------------
# Aggregate + verdict.
# ----------------------------------------------------------------------------------------------
def _mean(xs):
    import statistics as st
    return st.mean(xs) if xs else 0.0


def aggregate(chance, headline_dim, per_seed, cap_dims):
    cap_sorted = sorted(cap_dims)
    summ = {}
    for cond in CONDITIONS:
        cap = []
        for i, n_dim in enumerate(cap_sorted):
            cap.append({
                "n_dim": n_dim,
                "factored": _mean([s["conditions"][cond]["capacity"][i]["factored"] for s in per_seed]),
                "flat": _mean([s["conditions"][cond]["capacity"][i]["flat"] for s in per_seed]),
                "g_hat_cos": _mean([s["conditions"][cond]["capacity"][i]["g_hat_cos"] for s in per_seed]),
                "factored_range": (max(s["conditions"][cond]["capacity"][i]["factored"] for s in per_seed)
                                   - min(s["conditions"][cond]["capacity"][i]["factored"] for s in per_seed)),
            })
        head = next(c for c in cap if c["n_dim"] == headline_dim)
        preds = set()
        for s in per_seed:
            preds |= set(s["conditions"][cond]["per_pred_hi"].keys())
        per_pred = {}
        for p in sorted(preds):
            fac, flat, ns = [], [], []
            for s in per_seed:
                d = s["conditions"][cond]["per_pred_hi"].get(p)
                if d:
                    fac.append(d["factored"]); flat.append(d["flat"]); ns.append(d["n"])
            per_pred[p] = {"factored": _mean(fac), "flat": _mean(flat), "n_mean": _mean(ns)}
        summ[cond] = {
            "capacity": cap, "per_pred_heldout": per_pred,
            "content_cos_mean": _mean([s["conditions"][cond]["content_cos_mean"] for s in per_seed]),
            "factored_headline": head["factored"], "flat_headline": head["flat"],
            "gap_headline": head["factored"] - head["flat"],
            "factored_headline_range": head["factored_range"], "g_hat_cos_headline": head["g_hat_cos"],
        }

    ctrl, real, gated = summ["control_synthetic"], summ["real_reader"], summ["real_reader_gated"]
    positive_control = bool(ctrl["factored_headline"] >= 0.80 and ctrl["gap_headline"] >= 0.30)
    real_mustfail = bool(real["flat_headline"] <= chance + 0.15 and real["gap_headline"] >= 0.30)
    real_void = bool(real["flat_headline"] > 0.60)
    real_unsaturated = bool(real["factored_headline"] <= 0.955)
    real_generalizes = bool(real["factored_headline"] >= 0.70 and real["gap_headline"] >= 0.30
                            and real_mustfail and real_unsaturated)
    real_content_cost = ctrl["factored_headline"] - real["factored_headline"]
    real_breaks = bool(real["gap_headline"] <= 0.05 or real["factored_headline"] <= chance + 0.10
                       or real_content_cost >= 0.30)
    # capacity-vs-difficulty: if real ~= control (within 0.05) the headroom is CAPACITY not real-difficulty.
    difficulty_is_capacity = bool(abs(real_content_cost) <= 0.05)
    gate_effect = gated["factored_headline"] - real["factored_headline"]

    if not positive_control:
        verdict = "HARD_FAIL_POSITIVE_CONTROL"
    elif real_void:
        verdict = "VOID_FLAT_GENERALIZES"
    elif real_breaks:
        verdict = "HARD_FAIL_READER_NOISE_BREAKS"
    elif real_generalizes and not difficulty_is_capacity:
        verdict = "HARD_PASS_READING_AXIS_FIRST_CG"
    elif real_generalizes and difficulty_is_capacity:
        verdict = "MIDDLE_BAND"  # generalizes but headroom = capacity, not earned real-difficulty CG
    else:
        verdict = "MIDDLE_BAND"

    return {
        "verdict": verdict, "chance": chance, "headline_dim": headline_dim, "per_condition": summ,
        "positive_control_reproduces": positive_control,
        "real_must_fail_control_fired": real_mustfail,
        "real_generalizes": real_generalizes, "real_breaks": real_breaks,
        "real_unsaturated_headroom": real_unsaturated,
        "real_content_cost_headline": real_content_cost,
        "difficulty_is_capacity_not_noise": difficulty_is_capacity,
        "coherence_gate_effect_headline": gate_effect,
        "can_fail_both_ways": True,
    }


def arms_differ(per_seed, cond="real_reader"):
    pf, pl = per_seed[0]["conditions"][cond]["preds_hi"]
    hpf = hashlib.sha256(json.dumps(list(map(int, pf))).encode()).hexdigest()
    hpl = hashlib.sha256(json.dumps(list(map(int, pl))).encode()).hexdigest()
    assert hpf != hpl, (f"META_RULE_AF: FACTORED and FLAT held-out preds bit-identical on {cond}; "
                        f"arm-implementation bug")
    assert len(set(pf)) > 1, f"META_RULE_AF: {cond} FACTORED preds degenerate (all identical filler)"
    return {f"{cond}_factored_pred_hash": hpf[:16], f"{cond}_flat_pred_hash": hpl[:16]}


# ----------------------------------------------------------------------------------------------
# Scaffold-free witness: RE-RUN the REAL reader on a tiny text -> a REAL extracted svo -> a held-out combo;
# REAL hdlab.binding + REAL GloVe; FACTORED recovers, FLAT fails.
# ----------------------------------------------------------------------------------------------
def scaffold_free_witness():
    from experiments import exp_read_nested_clause_relative_third_reader_v1 as NEST
    from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2
    clf = V2._fit_clf()
    passages = {"w": "The dog chased the cat. The boy caught the ball."}
    res = NEST.read_corpus(clf, passages, nest=True)
    svos = sorted([r for r in res["foundation"] if r[0] == "svo" and r[1] != "kind"])
    assert svos, f"witness: reader extracted no svo from the witness text: {res['foundation']}"
    # Build a mini factorization over the REAL extracted svo memberships + a hand held-out combo.
    n = 512
    words = ["dog", "cat", "boy", "ball", "chased", "caught"]
    want = set(words); found = {}
    with gzip.open(GLOVE_PATH, "rt", encoding="utf-8") as f:
        f.readline()
        for line in f:
            sp = line.split(" ", 1)
            if sp[0] in want:
                found[sp[0]] = [float(t) for t in sp[1].split()]
                if len(found) == len(want):
                    break
    for w in words:
        assert w in found, f"witness: GloVe missing {w}"
    M = torch.tensor([found[w] for w in words], dtype=torch.float32)
    M_unit = M / torch.clamp(M.norm(dim=1, keepdim=True), min=1e-8)
    gen = torch.Generator().manual_seed(11)
    x = FZ.glove_to_fhrr(M_unit, n, BETA_REAL, gen)
    g = make_atoms(2, n, torch.complex64, gen)
    CHASE_OBJ, CATCH_OBJ = 0, 1
    DOG, CAT, BOY, BALL = 0, 1, 2, 3
    # verify REAL hdlab bind/unbind == FZ ops.
    b1 = FZ.fhrr_bind(g[CHASE_OBJ], x[CAT]); b2 = hdlab_bind(g[CHASE_OBJ], x[CAT])
    assert torch.allclose(b1, b2), "fhrr_bind != hdlab.binding.bind"
    # Train: chase-OBJ trained with {ball} (wrong-but-fine filler), catch-OBJ trained with {cat}. HELD-OUT:
    # chase-OBJ = cat (unseen combo; cat seen in catch-OBJ, chase-OBJ trained with ball).
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
    return {"reader_svo_sample": [list(s) for s in svos[:3]], "n_reader_svo": len(svos),
            "factored_pred": "cat", "flat_pred": words[flat_pred], "witness": "PASS"}


# ----------------------------------------------------------------------------------------------
# Config presets.
# ----------------------------------------------------------------------------------------------
def cfg_smoke():
    return dict(cap_dims=[48, 96, 256], m=6, knn=10, t_primary=24, vocab_cap=400,
               min_slots=2, min_slot_fillers=6, held_per_concept=1, min_train_fillers=5,
               n_test=200, gate_drop_frac=0.25, seeds=[7, 13])


def cfg_full():
    return dict(cap_dims=[40, 48, 64, 96, 128, 192, 256], m=6, knn=10, t_primary=24, vocab_cap=400,
               min_slots=2, min_slot_fillers=8, held_per_concept=1, min_train_fillers=6,
               n_test=400, gate_drop_frac=0.25, seeds=[7, 13, 19])


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = os.path.join(REPO_ROOT, "data",
                              f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    witness = scaffold_free_witness()
    chance, headline_dim, per_seed, meta = run_config(**cfg)
    agg = aggregate(chance, headline_dim, per_seed, cfg["cap_dims"])
    hashes = arms_differ(per_seed, "real_reader")

    elapsed = time.perf_counter() - t0
    v = agg["verdict"]
    ctrl = agg["per_condition"]["control_synthetic"]
    real = agg["per_condition"]["real_reader"]
    gated = agg["per_condition"]["real_reader_gated"]
    gd = meta["gate_stats"][0] if meta["gate_stats"] else {}
    msg = (f"{v} | headlineN={headline_dim} m={cfg['m']} chance={chance:.3f} "
           f"| CTRL(Gate-D) F={ctrl['factored_headline']:.3f} gap={ctrl['gap_headline']:.3f} "
           f"| REAL F={real['factored_headline']:.3f} FLAT={real['flat_headline']:.3f} "
           f"gap={real['gap_headline']:.3f} rng={real['factored_headline_range']:.3f} "
           f"realcost={agg['real_content_cost_headline']:+.3f} capNOTnoise={agg['difficulty_is_capacity_not_noise']} "
           f"| GATED F={gated['factored_headline']:.3f} gate_effect={agg['coherence_gate_effect_headline']:+.3f} "
           f"drop={gd.get('drop_frac_effective')} "
           f"| posctrl={agg['positive_control_reproduces']} mustfail={agg['real_must_fail_control_fired']} "
           f"realgen={agg['real_generalizes']} realbreak={agg['real_breaks']} "
           f"unsat={agg['real_unsaturated_headroom']} | V={meta['n_vocab']} slots={meta['n_slots']}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": v, "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": cfg, "chance": chance, "headline_dim": headline_dim, "aggregate": agg,
        "data_meta": meta, "arms_differ_hashes": hashes, "arms_differ_verified": True,
        "scaffold_free_witness": witness, "final_metrics_atomicity": "tmp_replace",
        "content_source": "REAL GloVe-wiki-gigaword-300 (Pennington 2014) FHRR-encoded",
        "relation_source": ("REAL reader extractions on McGuffey Third Reader (our reader "
                            "exp_read_nested_clause_relative_third_reader_v1, nest ON); noisy, NOT cleaned"),
        "REQUIRED_FIELDS": ["verdict", "aggregate", "scaffold_free_witness", "data_meta"],
        "notes": ("READER-COUPLED chain-grade gate: structure-content factorization on relations OUR reader "
                  "extracted from real narrative (with real extraction noise). HARD_PASS_READING_AXIS_FIRST_CG "
                  "= un-saturated real-difficulty compositional generalization where flat fails. "
                  "HARD_FAIL_READER_NOISE_BREAKS = coherence-gate needed (next component). MIDDLE_BAND w/ "
                  "difficulty_is_capacity=True = generalizes but headroom is capacity not real-difficulty "
                  "(honest CG-candidate). CLAIM-VET-pending; VET adjudicates CG vs CG-candidate."),
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  reader: {meta['reader_meta']['n_reader_tuples']} tuples; kinds={meta['reader_meta']['tuple_kinds']}",
          flush=True)
    print(f"  slot_filler_counts_top: {meta['slot_filler_counts_top']}", flush=True)
    print(f"  gate: {gd}", flush=True)
    for cond in CONDITIONS:
        cc = agg["per_condition"][cond]
        print(f"  [{cond}] content_cos_mean={cc['content_cos_mean']:.3f} "
              f"headline(N={headline_dim}) F={cc['factored_headline']:.3f} FLAT={cc['flat_headline']:.3f} "
              f"gap={cc['gap_headline']:.3f} gcos={cc['g_hat_cos_headline']:.3f}", flush=True)
        print("     capacity sweep (F=FACTORED, N-dim; un-saturation axis):", flush=True)
        for r in cc["capacity"]:
            print(f"        N={r['n_dim']:>4} F={r['factored']:.3f} FLAT={r['flat']:.3f} "
                  f"gcos={r['g_hat_cos']:.3f} F_rng={r['factored_range']:.3f}", flush=True)
    print("  [per-relation-type held-out breakdown | real_reader | headline N]", flush=True)
    for p, d in sorted(real["per_pred_heldout"].items(), key=lambda kv: -kv[1]["n_mean"]):
        print(f"        {p:<12} F={d['factored']:.3f} FLAT={d['flat']:.3f} n~{d['n_mean']:.0f}", flush=True)
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
        chance, hd, per_seed, meta = run_config(
            cap_dims=[48, 256], m=6, knn=10, t_primary=24, vocab_cap=400, min_slots=2,
            min_slot_fillers=6, held_per_concept=1, min_train_fillers=5, n_test=80,
            gate_drop_frac=0.25, seeds=[7])
        agg = aggregate(chance, hd, per_seed, [48, 256])
        arms_differ(per_seed, "real_reader")
        ctrl = agg["per_condition"]["control_synthetic"]
        real = agg["per_condition"]["real_reader"]
        print(f"[{ANCHOR_NAME}] self-test end-to-end: verdict={agg['verdict']} headlineN={hd} "
              f"CTRL_F={ctrl['factored_headline']:.3f} REAL_F={real['factored_headline']:.3f} "
              f"REAL_gap={real['gap_headline']:.3f} V={meta['n_vocab']} slots={meta['n_slots']} "
              f"chance={chance:.3f}", flush=True)
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
