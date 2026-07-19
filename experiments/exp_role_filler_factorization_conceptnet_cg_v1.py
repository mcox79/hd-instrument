"""FULL-CHAIN-GRADE gate: structure-content factorization on REAL EXTRACTED ConceptNet relations.

QUESTION (the FULL-CG shot; the reading/learning axis's FIRST chain-grade):
Does the brain-faithful STRUCTURE-CONTENT FACTORIZATION -- a LEARNED content-blind structural
code g (relation-type + argument-role) bound to content x via native FHRR conjunctive binding --
give held-out-COMBINATION generalization on REAL EXTRACTED RELATIONS (ConceptNet: real concepts,
real relation-types, noisy, many-typed, skewed) where a flat content-typicality baseline FAILS,
in an UN-SATURATED primary (FACTORED sits ~0.85-0.95 WITH HEADROOM, not 1.000)?

WHY THIS EXTENDS THE CG-CANDIDATE (atom 29334, exp_role_filler_factorization_realcontent_cg_v1,
commit 8751c22d8): that cell VET-confirmed the mechanism on REAL GloVe content but with CURATED
abstract roles (random g_true, uniform role<->filler assignment) and a present-pool readout that
SATURATED at FACTORED=1.000 (MEASURED@data/exp_role_filler_factorization_realcontent_cg_v1/
metrics.json, both smoke and full). The VET (a288bd2f) named THIS as the full-CG promotion:
(1) REAL relations extracted from ConceptNet (real relation-types as the structural code; real,
skewed, semantically-loaded concept<->slot co-occurrence); (2) UN-SATURATED primary so real-relation
degradation is visible IN-primary; (3) keep binding-load m and training-per-role SEPARATE from the
realness knob.

------------------------------------------------------------------------------------------------
REAL EXTRACTED RELATIONS (the load-bearing new element)
------------------------------------------------------------------------------------------------
Data: data/datasets/conceptnet5_en_100k.jsonl (100k triples {subject, predicate, object}). 8 real
relation-types present (MEASURED@run: AtLocation, CapableOf, Antonym, Causes, DerivedFrom,
CausesDesire, DefinedAs, CreatedBy), heavily skewed (~28k down to ~260). The STRUCTURAL CODE = a
slot = (predicate, argument-role in {HEAD, TAIL}) -> up to 16 real structural slots. A concept
FILLS a slot iff it actually occurs in that (predicate, role) position in ConceptNet -- so the
concept<->slot association is REAL, skewed, semantically clustered. Content = REAL GloVe-wiki-
gigaword-300 vectors for the concept vocab (single-token, GloVe-present, appears in >=2 distinct
slots so held-out-eligible).

HELD-OUT-COMBINATION split (systematic-generalization probe; RECOMBINATION not arbitrary-unseen,
per the caveat CITED@notes/research_drill_p9_mechanism_diagnosis_2x_2026-06-10.md): a (concept,
slot) pair PROVABLY UNSEEN in train, where the concept IS seen in OTHER slots (grounded + trained)
and the slot IS trained with OTHER concepts.

------------------------------------------------------------------------------------------------
CONDITIONS (SAME real relations + SAME held-out split; content is the ONLY thing that varies)
------------------------------------------------------------------------------------------------
control_synthetic : random FHRR content (near-orthogonal) on the REAL relations + REAL split =
                    Gate-D positive control (reproduces the mechanism at the exact real-relation
                    test regime with clean content). Isolates the plumbing.
real_conceptnet   : REAL GloVe content on the SAME real relations + split. THE make-or-break.

------------------------------------------------------------------------------------------------
UN-SATURATION (design fix; knobs SEPARATE from realness, per VET caveat)
------------------------------------------------------------------------------------------------
This mechanism is EXTREMELY robust: at N>=256 the held-out FACTORED readout saturates at ~1.000
across the whole difficulty landscape (MEASURED@calibration 2026-07-19: even g_hat->g_true cos as
low as 0.50, hard global-semantic-neighbor readout pools at chance 0.04, and real skewed relations
leave FACTORED at ceiling; the FHRR unbind signal dominates all content confusability). The ONLY
principled un-saturator is the substrate's native SUPERPOSITION CAPACITY (Plate 1995: a bundle of
m bound pairs in N dims); the primary is therefore a CAPACITY SWEEP over N at FIXED brain-faithful
binding-load m and FIXED training-per-role t (both held constant across conditions -> realness =
content is the only variable, VET caveat honored). At the low-N capacity edge FACTORED has HEADROOM
(MEASURED@calibration N=48/m=6/gcos=0.92: real FACTORED ~0.88, control ~0.955, FLAT ~0.006) so any
real-relation cost is VISIBLE in-primary; as N grows both climb to ceiling.
READOUT: pool = the m PRESENT fillers + the top-KNN GLOBAL content-nearest-neighbors of the true
filler (semantic confusability; hard, and REAL-content-sensitive -- neighbors are ~random for the
synthetic control so the control stays clean). chance = 1/(m+KNN).
LEARNING CURVE: a separate exposure sweep over training-per-role t at the primary N shows g_hat->
g_true cos (the learned structural code quality) improving with exposure (the "g improves with
exposure" axis).

------------------------------------------------------------------------------------------------
ARMS within each condition (ONE VARIABLE: structure-bind vs flat; identical task/split/situations)
------------------------------------------------------------------------------------------------
World: g_true[slot] random FHRR per real (predicate, role) slot. Situation S = sum_i bind(g_true
[slot_i], x[filler_i]) over m distinct slots with distinct fillers (FHRR superposition).
ARM_FLAT (must-fail control): proto[slot] = unit(mean training x[filler-in-slot]); readout argmax
  sim(x[cand], proto[q]). Pure content typicality; held-out filler never trained in q -> FAILS.
ARM_FACTORED (structure-content factorization, LEARNED content-blind g): g_hat[slot] = unit(mean
  over slot occurrences of unbind(S, x[filler])); readout est=unbind(S,g_hat[q]); argmax
  sim(est, x[cand]). g_hat NEVER sees held-out combos.

------------------------------------------------------------------------------------------------
BRAIN-CHECK (pre-registered; outcome NOT pre-assumed)
------------------------------------------------------------------------------------------------
The brain generalizes relational knowledge to NOVEL concept-relation combinations (relational /
schema transfer; TEM/grid structural codes reused across content; CITED@Whittington et al. 2020).
Real relation-types are the structural scaffold. So real-relation compgen SHOULD factorize brain-
faithfully. Where might the substrate hit a REAL bound? FHRR superposition crosstalk grows with
binding-load m and shrinks with N (capacity); real correlated content adds a small extra cost that
appears at the capacity edge (MEASURED real FACTORED < control by ~0.03-0.10 at low N). If many-
types/noise/skew broke it AT FIXED m,t while the synthetic control held, that LOCALIZES the real-
relation barrier. Same-limit-as-brain => accept; brain-handles-it (relational transfer) => the fix.

------------------------------------------------------------------------------------------------
BANDS (pre-registered; pool = m+KNN -> chance = 1/(m+KNN), MEASURED@run; headline = smallest N)
------------------------------------------------------------------------------------------------
DESIGN-GATE (verified at SMOKE before full):
  (G1) POSITIVE CONTROL (Gate D): control_synthetic FACTORED held-out (headline N) >= 0.80 AND
       (FACTORED-FLAT) gap >= 0.30 (mechanism reproduces at the real-relation test regime).
  (G2) UN-SATURATED PRIMARY: real_conceptnet FACTORED held-out (headline N) in [0.70, 0.955]
       (HEADROOM; NOT 1.000). If smoke shows >= 0.96 -> saturated -> lower headline N until headroom.
  (G3) MUST-FAIL CONTROL fires: real_conceptnet FLAT held-out <= chance + 0.15 AND gap >= 0.30.
  (G4) ONE VARIABLE: structure-bind vs flat on identical real data/split; m and t fixed across conds.
VERDICTS (full):
  HARD_PASS_READING_AXIS_FIRST_CG: positive control holds AND real_conceptnet FACTORED held-out
    (headline N) >= 0.75 with headroom (<= 0.955, genuinely un-saturated) AND gap >= 0.30 AND
    must-fail fired. => un-saturated compositional generalization on REAL extracted relations where
    flat fails, brain-faithful native bind: the reading/learning axis's first chain-grade (VET
    adjudicates CG vs CG-candidate).
  HARD_FAIL_REAL_RELATIONS_BREAK: positive control holds AND real_conceptnet breaks (gap <= 0.05
    OR FACTORED <= chance + 0.10 OR FACTORED drops >= 0.30 below control_synthetic at headline N).
    => real relation structure/noise/skew break the factorization; per-relation-type breakdown localizes.
  HARD_FAIL_POSITIVE_CONTROL: control_synthetic does NOT reproduce -> cell/regime/split suspect.
  VOID_FLAT_GENERALIZES: real_conceptnet FLAT held-out > 0.60 -> split does not isolate compgen.
  MIDDLE_BAND: anything between.

------------------------------------------------------------------------------------------------
COMPUTE ARCHITECTURE (mandatory declaration)
------------------------------------------------------------------------------------------------
Class: (b) sequential-CPU with justification -- wall seconds-to-low-minutes; the cell IS validating
the substrate primitive (FHRR bind/unbind) as a reference computation on real extracted relations;
elementwise complex ops on a few hundred N<=256 vectors. Foreground local-to-completion (light; no
queue; no push; no remote-persist). Storage strategy: BUNDLED is the object under test (one
situation = one bundle of m bound pairs, brain-faithful m=6); no sharded store.

CELL-TEMPLATE MANDATORY (subset for a LOCAL foreground mechanism-proof; NOT queue-dispatched):
- arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test on prediction arrays)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (META_RULE_AG; FLAT held-out is the must-fail control; FACTORED in headroom band)
- discriminator fires at smoke (must-fail: FLAT << FACTORED; positive control reproduces at real regime)
- Gate D positive control: control_synthetic reproduces the mechanism AT THE REAL-RELATION TEST REGIME
- deterministic seeding: fixed int seeds + random.Random + torch.Generator + sorted()/hashlib; no salted-builtin hash, no set-order dedupe
- scaffold-free witness in self-test EXERCISES the REAL hdlab.binding.bind/unbind + REAL GloVe + a REAL ConceptNet held-out combo
- all numbers in comments tagged HYPOTHESIZED@ / THEORETICAL@ / CITED@ / MEASURED@ (MEASURED printed at run)
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

ANCHOR_NAME = "role_filler_factorization_conceptnet_cg_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Real substrate primitives (scaffold-free witness in self-test binds against these directly).
from hdlab.atoms import make_atoms  # noqa: E402
from hdlab.binding import bind as hdlab_bind  # noqa: E402
from hdlab.binding import unbind as hdlab_unbind  # noqa: E402

GLOVE_PATH = os.path.join(REPO_ROOT, "data", "gensim_cache",
                          "glove-wiki-gigaword-300", "glove-wiki-gigaword-300.gz")
CONCEPTNET_PATH = os.path.join(REPO_ROOT, "data", "datasets", "conceptnet5_en_100k.jsonl")

# THEORETICAL@ content_cos(u,v) = exp(-beta^2 (1 - cos_glove(u,v))); BETA_REAL matches the CG-candidate
# (MEASURED content_cos mean ~0.17 ~= GloVe native). CITED@GloVe (Pennington 2014), ConceptNet5 (Speer 2017).
BETA_REAL = 1.5
CONDITIONS = ["control_synthetic", "real_conceptnet"]


# ----------------------------------------------------------------------------------------------
# Native FHRR ops (elementwise complex; identical to hdlab.binding for complex dtype).
# ----------------------------------------------------------------------------------------------
def fhrr_bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """FHRR bind = elementwise complex mul. Broadcasts (..., N)."""
    return a * b


def fhrr_unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """FHRR unbind = elementwise mul by conjugate. Broadcasts (..., N)."""
    return c * b.conj()


def unit_phase(v: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """Project each complex component to unit magnitude (FHRR cleanup / phasor normalize)."""
    return v / torch.clamp(v.abs(), min=eps)


def sim_to_codebook(q: torch.Tensor, cb: torch.Tensor) -> torch.Tensor:
    """Normalized real inner product of q (N,) vs codebook cb (K,N). Returns (K,). FHRR sim."""
    n = q.shape[-1]
    return (cb * q.conj()).sum(dim=-1).real / n


def sim_rowwise(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Row-wise FHRR similarity between two (K,N) codebooks. Returns (K,)."""
    n = a.shape[-1]
    return (a * b.conj()).sum(dim=-1).real / n


def hash_str(s: str) -> int:
    """Deterministic (NOT salted-builtin) small int from a string; hashlib -> F.5-compliant."""
    return int.from_bytes(hashlib.sha256(s.encode("utf-8")).digest()[:4], "big") % 1000003


# ----------------------------------------------------------------------------------------------
# REAL data: ConceptNet slot inventory + GloVe content, filtered to GloVe-single-token concepts.
# ----------------------------------------------------------------------------------------------
def _is_single_alpha(tok: str) -> bool:
    return len(tok) >= 2 and tok.isalpha() and tok.islower()


def load_conceptnet_and_glove(vocab_cap: int, min_slots: int, min_slot_fillers: int):
    """Build the REAL structural inventory from ConceptNet + REAL GloVe vectors (deterministic)."""
    if not os.path.exists(CONCEPTNET_PATH):
        raise FileNotFoundError(f"ConceptNet file not found: {CONCEPTNET_PATH}")
    if not os.path.exists(GLOVE_PATH):
        raise FileNotFoundError(f"GloVe file not found: {GLOVE_PATH}")

    concept_slotset = defaultdict(set)
    concept_freq = defaultdict(int)
    rel_type_counts = defaultdict(int)
    with open(CONCEPTNET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            s, p, o = d["subject"], d["predicate"], d["object"]
            rel_type_counts[p] += 1
            if _is_single_alpha(s):
                concept_slotset[s].add((p, "H")); concept_freq[s] += 1
            if _is_single_alpha(o):
                concept_slotset[o].add((p, "T")); concept_freq[o] += 1

    candidates = set(concept_slotset.keys())
    vec = {}
    with gzip.open(GLOVE_PATH, "rt", encoding="utf-8") as f:
        f.readline()  # header
        for line in f:
            sp = line.rstrip().split(" ")
            if sp[0] in candidates:
                vec[sp[0]] = [float(t) for t in sp[1:]]

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
    pred_of_slot = [sl[0] for sl in slot_ids]

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
        "rel_type_counts": dict(rel_type_counts), "eligible_concepts": good,
    }


def glove_to_fhrr(M_unit: torch.Tensor, n_dim: int, beta: float, gen: torch.Generator) -> torch.Tensor:
    """Encode unit vectors (V,300) into FHRR unit phasors (V,N): x_j = exp(i*beta*(R_j . v_unit))."""
    R = torch.randn((n_dim, M_unit.shape[1]), generator=gen, dtype=torch.float32) * beta
    phase = M_unit @ R.t()
    return torch.complex(torch.cos(phase), torch.sin(phase)).to(torch.complex64)


def build_content(condition: str, glove: torch.Tensor, n_dim: int, gen: torch.Generator) -> torch.Tensor:
    """Content codes x (V,N) complex64 unit phasors (real relations identical across conditions)."""
    if condition == "control_synthetic":
        return make_atoms(glove.shape[0], n_dim, torch.complex64, gen)
    if condition == "real_conceptnet":
        M_unit = glove / torch.clamp(glove.norm(dim=1, keepdim=True), min=1e-8)
        return glove_to_fhrr(M_unit, n_dim, BETA_REAL, gen)
    raise ValueError(f"unknown condition {condition}")


def content_corr_mean(x: torch.Tensor) -> float:
    v, n = x.shape[0], x.shape[-1]
    g = (x @ x.conj().t()).real / n
    iu = torch.triu_indices(v, v, offset=1)
    return float(g[iu[0], iu[1]].mean())


def global_nn_index(x: torch.Tensor):
    """For each concept, content-nearest-neighbor order (excl self). Returns list[list[int]]."""
    n = x.shape[-1]
    G = (x @ x.conj().t()).real / n
    G.fill_diagonal_(-9.0)
    return [torch.argsort(G[i], descending=True).tolist() for i in range(x.shape[0])]


# ----------------------------------------------------------------------------------------------
# Held-out (concept, slot) split over REAL memberships (provably-unseen recombination).
# ----------------------------------------------------------------------------------------------
def build_split(slot_fillers, concept_slots, eligible, held_per_concept, min_train_fillers, rng):
    slots = sorted(slot_fillers.keys())
    train_fillers = {sj: set(slot_fillers[sj]) for sj in slots}
    held_out = set()
    order = sorted(eligible, key=lambda ci: (-len(concept_slots[ci]), ci))
    rng.shuffle(order)
    for ci in order:
        cs = [sj for sj in concept_slots[ci] if sj in train_fillers]
        if len(cs) < 2:
            continue
        rng.shuffle(cs)
        n_hold = min(held_per_concept, len(cs) - 1)
        held_here = 0
        for sj in cs:
            if held_here >= n_hold:
                break
            if len(train_fillers[sj]) - 1 < min_train_fillers or ci not in train_fillers[sj]:
                continue
            train_fillers[sj].discard(ci)
            held_out.add((ci, sj))
            held_here += 1
    trainable_fillers = {sj: sorted(train_fillers[sj]) for sj in slots}
    held_by_slot = defaultdict(list)
    for (ci, sj) in held_out:
        held_by_slot[sj].append(ci)
    for sj in slots:
        assert len(trainable_fillers[sj]) >= min_train_fillers, f"slot {sj} starved"
    if len(held_out) < 10:
        raise RuntimeError(f"too few held-out pairs ({len(held_out)})")
    return held_out, trainable_fillers, {sj: sorted(v) for sj, v in held_by_slot.items()}


def balanced_train(m, t, trainable_fillers, rng):
    """Each slot appears EXACTLY t times (fixed training-per-role; no starvation). Each situation =
    m distinct slots with distinct fillers. Returns list of assign dicts."""
    slots = [sj for sj, fs in trainable_fillers.items() if fs]
    bag = []
    for _ in range(t):
        order = slots[:]
        rng.shuffle(order)
        bag.extend(order)
    situations = []
    remaining = bag[:]
    while len(remaining) >= m:
        chosen, used, leftover = [], set(), []
        for sj in remaining:
            if sj not in used and len(chosen) < m:
                chosen.append(sj); used.add(sj)
            else:
                leftover.append(sj)
        if len(chosen) < m:
            break
        assign, usedf, ok = {}, set(), True
        for sj in chosen:
            cands = [c for c in trainable_fillers[sj] if c not in usedf]
            if not cands:
                ok = False
                break
            c = rng.choice(cands)
            assign[sj] = c
            usedf.add(c)
        if ok and len(assign) == m:
            situations.append(assign)
        remaining = leftover
    return situations


def sample_heldout_situation(m, trainable_fillers, held_by_slot, rng):
    hslots = [sj for sj, cs in held_by_slot.items() if cs]
    others_all = [sj for sj, fs in trainable_fillers.items() if fs]
    for _ in range(500):
        s_star = rng.choice(hslots)
        c_star = rng.choice(held_by_slot[s_star])
        others = [sj for sj in others_all if sj != s_star]
        if len(others) < m - 1:
            continue
        chosen = rng.sample(others, m - 1)
        assign, used, ok = {s_star: c_star}, {c_star}, True
        for sj in chosen:
            cands = [c for c in trainable_fillers[sj] if c not in used]
            if not cands:
                ok = False
                break
            c = rng.choice(cands)
            assign[sj] = c
            used.add(c)
        if ok and len(assign) == m:
            return assign, s_star
    raise RuntimeError("could not sample a valid held-out situation")


def make_heldout_set(n, m, trainable_fillers, held_by_slot, rng):
    out = []
    for _ in range(n):
        assign, s_star = sample_heldout_situation(m, trainable_fillers, held_by_slot, rng)
        out.append((assign, s_star, assign[s_star]))
    return out


def encode_situation(assign, g_true, x):
    """S = sum_i bind(g_true[slot_i], x[filler_i]) (FHRR superposition)."""
    parts = [fhrr_bind(g_true[sj], x[ci]) for sj, ci in sorted(assign.items())]
    return torch.stack(parts, dim=0).sum(dim=0)


def learn(train_situations, n_slots, g_true, x, n_dim):
    g_acc = torch.zeros((n_slots, n_dim), dtype=torch.complex64)
    p_acc = torch.zeros((n_slots, n_dim), dtype=torch.complex64)
    cnt = torch.zeros(n_slots)
    for assign in train_situations:
        S = encode_situation(assign, g_true, x)
        for sj, ci in assign.items():
            g_acc[sj] += fhrr_unbind(S, x[ci])
            p_acc[sj] += x[ci]
            cnt[sj] += 1
    cnt = torch.clamp(cnt, min=1.0)
    return unit_phase(g_acc / cnt.unsqueeze(1)), unit_phase(p_acc / cnt.unsqueeze(1)), cnt


def eval_heldout(test_set, g_true, g_hat, proto, x, knn, nn_index, pred_of_slot):
    """Readout pool = present fillers + top-knn global content-neighbors of the true filler.
    Both arms use the same pool (fair). Returns overall + per-relation-type accuracy + preds."""
    correct = {"factored": 0, "flat": 0}
    per_pred = defaultdict(lambda: {"factored": 0, "flat": 0, "n": 0})
    preds_fac, preds_flat = [], []
    for assign, q, true_f in test_set:
        S = encode_situation(assign, g_true, x)
        present = sorted(assign.values())
        pool = list(present)
        for d in nn_index[true_f]:
            if len(pool) >= len(present) + knn:
                break
            if d not in present:
                pool.append(d)
        pool = sorted(set(pool))
        cb = torch.stack([x[c] for c in pool], dim=0)
        est = fhrr_unbind(S, g_hat[q])
        fac = pool[int(torch.argmax(sim_to_codebook(est, cb)))]
        flat = pool[int(torch.argmax(sim_to_codebook(proto[q], cb)))]
        preds_fac.append(fac); preds_flat.append(flat)
        correct["factored"] += int(fac == true_f)
        correct["flat"] += int(flat == true_f)
        p = pred_of_slot[q]
        per_pred[p]["factored"] += int(fac == true_f)
        per_pred[p]["flat"] += int(flat == true_f)
        per_pred[p]["n"] += 1
    n = len(test_set)
    acc = {k: c / n for k, c in correct.items()}
    per_pred_acc = {p: {"factored": d["factored"] / d["n"], "flat": d["flat"] / d["n"], "n": d["n"]}
                    for p, d in per_pred.items()}
    return acc, per_pred_acc, preds_fac, preds_flat


# ----------------------------------------------------------------------------------------------
# Core run: capacity sweep (un-saturation) + exposure sweep (learning curve) x 2 conditions.
# ----------------------------------------------------------------------------------------------
def run_config(cap_dims, m, knn, t_primary, t_curve, vocab_cap, min_slots, min_slot_fillers,
               held_per_concept, min_train_fillers, n_test, seeds):
    data = load_conceptnet_and_glove(vocab_cap, min_slots, min_slot_fillers)
    glove = data["glove"]
    slot_fillers = data["slot_fillers"]
    concept_slots = data["concept_slots"]
    pred_of_slot = data["pred_of_slot"]
    n_slots = len(slot_fillers)
    chance = 1.0 / (m + knn)
    headline_dim = min(cap_dims)
    per_seed = []
    for seed in seeds:
        held_out, trainable, held_by = build_split(
            slot_fillers, concept_slots, data["eligible_concepts"],
            held_per_concept, min_train_fillers, random.Random(seed + 7))
        test_held = make_heldout_set(n_test, m, trainable, held_by, random.Random(seed + 100000))
        # Balanced training-per-role situations (assignment fixed per (t,seed); content-independent).
        train_by_t = {t: balanced_train(m, t, trainable, random.Random(seed * 1000 + t))
                      for t in sorted(set(t_curve) | {t_primary})}

        cond_out = {}
        for cond in CONDITIONS:
            capacity = []   # FACTORED/FLAT held-out vs N (fixed m, t_primary)
            curve = []      # FACTORED held-out + g_hat cos vs t (at headline N)
            ppred = None
            preds_hi = None
            for n_dim in sorted(cap_dims):
                gen_g = torch.Generator().manual_seed(seed + n_dim)  # slot scaffold per (seed,N)
                g_true = make_atoms(n_slots, n_dim, torch.complex64, gen_g)
                gen_c = torch.Generator().manual_seed(seed * 31 + hash_str(cond) + n_dim)
                x = build_content(cond, glove, n_dim, gen_c)
                nn_index = global_nn_index(x)
                g_hat, proto, cnt = learn(train_by_t[t_primary], n_slots, g_true, x, n_dim)
                acc, pp, pf, pl = eval_heldout(test_held, g_true, g_hat, proto, x, knn, nn_index,
                                               pred_of_slot)
                capacity.append({"n_dim": n_dim, "factored": acc["factored"], "flat": acc["flat"],
                                 "g_hat_cos": float(sim_rowwise(g_hat, g_true).mean())})
                if n_dim == headline_dim:
                    ppred = pp
                    preds_hi = (pf, pl)
                    content_cos = content_corr_mean(x)
            # Learning curve at headline N.
            gen_g = torch.Generator().manual_seed(seed + headline_dim)
            g_true = make_atoms(n_slots, headline_dim, torch.complex64, gen_g)
            gen_c = torch.Generator().manual_seed(seed * 31 + hash_str(cond) + headline_dim)
            x = build_content(cond, glove, headline_dim, gen_c)
            nn_index = global_nn_index(x)
            for t in sorted(t_curve):
                g_hat, proto, cnt = learn(train_by_t[t], n_slots, g_true, x, headline_dim)
                acc, _, _, _ = eval_heldout(test_held, g_true, g_hat, proto, x, knn, nn_index,
                                            pred_of_slot)
                curve.append({"t": t, "n_train_situations": len(train_by_t[t]),
                              "factored": acc["factored"], "flat": acc["flat"],
                              "g_hat_cos": float(sim_rowwise(g_hat, g_true).mean())})
            cond_out[cond] = {"capacity": capacity, "curve": curve, "per_pred_hi": ppred,
                              "preds_hi": preds_hi, "content_cos_mean": content_cos}
        per_seed.append({"seed": seed, "conditions": cond_out})

    meta = {
        "n_vocab": len(data["vocab"]), "n_slots": n_slots, "headline_dim": headline_dim,
        "slot_ids": [f"{p}:{r}" for (p, r) in data["slot_ids"]],
        "rel_type_counts": data["rel_type_counts"],
        "slot_filler_counts": {f"{data['slot_ids'][j][0]}:{data['slot_ids'][j][1]}": len(fs)
                               for j, fs in slot_fillers.items()},
        "vocab_sample": data["vocab"][:24],
    }
    return chance, headline_dim, per_seed, meta


# ----------------------------------------------------------------------------------------------
# Aggregate + verdict.
# ----------------------------------------------------------------------------------------------
def _mean(xs):
    import statistics as st
    return st.mean(xs)


def aggregate(chance, headline_dim, per_seed, cap_dims, t_curve):
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
        curve = []
        for j, t in enumerate(sorted(t_curve)):
            curve.append({
                "t": t,
                "factored": _mean([s["conditions"][cond]["curve"][j]["factored"] for s in per_seed]),
                "flat": _mean([s["conditions"][cond]["curve"][j]["flat"] for s in per_seed]),
                "g_hat_cos": _mean([s["conditions"][cond]["curve"][j]["g_hat_cos"] for s in per_seed]),
            })
        head = next(c for c in cap if c["n_dim"] == headline_dim)
        # per-relation-type at headline (mean over seeds).
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
            "capacity": cap, "curve": curve, "per_pred_heldout": per_pred,
            "content_cos_mean": _mean([s["conditions"][cond]["content_cos_mean"] for s in per_seed]),
            "factored_headline": head["factored"], "flat_headline": head["flat"],
            "gap_headline": head["factored"] - head["flat"],
            "factored_headline_range": head["factored_range"], "g_hat_cos_headline": head["g_hat_cos"],
        }

    ctrl, real = summ["control_synthetic"], summ["real_conceptnet"]
    positive_control = bool(ctrl["factored_headline"] >= 0.80 and ctrl["gap_headline"] >= 0.30)
    real_mustfail = bool(real["flat_headline"] <= chance + 0.15 and real["gap_headline"] >= 0.30)
    real_void = bool(real["flat_headline"] > 0.60)
    real_unsaturated = bool(real["factored_headline"] <= 0.955)
    real_generalizes = bool(real["factored_headline"] >= 0.75 and real["gap_headline"] >= 0.30
                            and real_mustfail and real_unsaturated)
    real_breaks = bool(real["gap_headline"] <= 0.05 or real["factored_headline"] <= chance + 0.10
                       or (ctrl["factored_headline"] - real["factored_headline"]) >= 0.30)

    if not positive_control:
        verdict = "HARD_FAIL_POSITIVE_CONTROL"
    elif real_void:
        verdict = "VOID_FLAT_GENERALIZES"
    elif real_generalizes:
        verdict = "HARD_PASS_READING_AXIS_FIRST_CG"
    elif real_breaks:
        verdict = "HARD_FAIL_REAL_RELATIONS_BREAK"
    else:
        verdict = "MIDDLE_BAND"

    return {
        "verdict": verdict, "chance": chance, "headline_dim": headline_dim, "per_condition": summ,
        "positive_control_reproduces": positive_control,
        "real_must_fail_control_fired": real_mustfail,
        "real_generalizes": real_generalizes, "real_breaks": real_breaks,
        "real_unsaturated_headroom": real_unsaturated,
        "real_content_cost_headline": ctrl["factored_headline"] - real["factored_headline"],
        "can_fail_both_ways": True,
    }


def arms_differ(per_seed, cond="real_conceptnet"):
    pf, pl = per_seed[0]["conditions"][cond]["preds_hi"]
    hpf = hashlib.sha256(json.dumps(list(map(int, pf))).encode()).hexdigest()
    hpl = hashlib.sha256(json.dumps(list(map(int, pl))).encode()).hexdigest()
    assert hpf != hpl, (f"META_RULE_AF: FACTORED and FLAT held-out preds bit-identical on {cond}; "
                        f"arm-implementation bug")
    assert len(set(pf)) > 1, f"META_RULE_AF: {cond} FACTORED preds degenerate (all identical filler)"
    return {f"{cond}_factored_pred_hash": hpf[:16], f"{cond}_flat_pred_hash": hpl[:16]}


# ----------------------------------------------------------------------------------------------
# Scaffold-free witness (self-test): REAL hdlab.binding + REAL GloVe + a REAL ConceptNet held-out combo.
# ----------------------------------------------------------------------------------------------
def scaffold_free_witness():
    n = 512
    words = ["dog", "cat", "car", "apple"]
    want = set(words); found = {}
    with gzip.open(GLOVE_PATH, "rt", encoding="utf-8") as f:
        f.readline()
        for line in f:
            sp = line.rstrip().split(" ")
            if sp[0] in want:
                found[sp[0]] = [float(t) for t in sp[1:]]
                if len(found) == len(want):
                    break
    M = torch.tensor([found[w] for w in words], dtype=torch.float32)
    M_unit = M / torch.clamp(M.norm(dim=1, keepdim=True), min=1e-8)
    gen = torch.Generator().manual_seed(11)
    x = glove_to_fhrr(M_unit, n, BETA_REAL, gen)
    g = make_atoms(3, n, torch.complex64, gen)
    ATLOC_H, CAUSES_H, CAPABLE_H = 0, 1, 2
    DOG, CAT, CAR, APPLE = 0, 1, 2, 3

    b_bulk = fhrr_bind(g[ATLOC_H], x[DOG]); b_real = hdlab_bind(g[ATLOC_H], x[DOG])
    assert torch.allclose(b_bulk, b_real), "fhrr_bind != hdlab.binding.bind"
    u_bulk = fhrr_unbind(b_bulk, x[DOG]); u_real = hdlab_unbind(b_real, x[DOG])
    assert torch.allclose(u_bulk, u_real), "fhrr_unbind != hdlab.binding.unbind"

    dc = float(sim_to_codebook(x[DOG], x[CAT].unsqueeze(0))[0])
    dcar = float(sim_to_codebook(x[DOG], x[CAR].unsqueeze(0))[0])
    assert dc > dcar, f"witness: real content not correlated (dog-cat {dc:.3f} !> dog-car {dcar:.3f})"

    # DOG never as CAUSES-HEAD (held-out); DOG trained in AtLocation-HEAD; Causes-HEAD trained w/ CAR,APPLE.
    train = [{ATLOC_H: DOG, CAUSES_H: CAT}, {ATLOC_H: CAT, CAPABLE_H: CAR},
             {CAUSES_H: CAR, CAPABLE_H: APPLE}, {CAUSES_H: APPLE, ATLOC_H: CAT}]
    g_hat = torch.zeros((3, n), dtype=torch.complex64)
    proto = torch.zeros((3, n), dtype=torch.complex64)
    cnt = torch.zeros(3)
    for assign in train:
        S = torch.stack([hdlab_bind(g[sj], x[ci]) for sj, ci in sorted(assign.items())], 0).sum(0)
        for sj, ci in assign.items():
            g_hat[sj] += hdlab_unbind(S, x[ci]); proto[sj] += x[ci]; cnt[sj] += 1
    g_hat = unit_phase(g_hat / torch.clamp(cnt, min=1.0).unsqueeze(1))
    proto = unit_phase(proto / torch.clamp(cnt, min=1.0).unsqueeze(1))

    S = torch.stack([hdlab_bind(g[CAUSES_H], x[DOG]), hdlab_bind(g[CAPABLE_H], x[CAT])], 0).sum(0)
    pool = [DOG, CAT]
    cb = torch.stack([x[c] for c in pool], 0)
    est = hdlab_unbind(S, g_hat[CAUSES_H])
    fac_pred = pool[int(torch.argmax(sim_to_codebook(est, cb)))]
    flat_pred = pool[int(torch.argmax(sim_to_codebook(proto[CAUSES_H], cb)))]
    assert fac_pred == DOG, f"witness: FACTORED failed held-out Causes-HEAD=DOG (got {fac_pred})"
    assert flat_pred != DOG, f"witness: FLAT unexpectedly recovered held-out combo (got {flat_pred})"
    return {"factored_pred": "dog", "flat_pred": words[flat_pred], "dog_cat_cos": round(dc, 3),
            "dog_car_cos": round(dcar, 3), "witness": "PASS"}


# ----------------------------------------------------------------------------------------------
# Config presets.
# ----------------------------------------------------------------------------------------------
def cfg_smoke():
    return dict(cap_dims=[48, 96, 256], m=6, knn=10, t_primary=24, t_curve=[6, 24],
                vocab_cap=300, min_slots=2, min_slot_fillers=8, held_per_concept=1,
                min_train_fillers=6, n_test=200, seeds=[7, 13])


def cfg_full():
    return dict(cap_dims=[48, 64, 96, 128, 192, 256], m=6, knn=10, t_primary=24,
                t_curve=[3, 6, 12, 24, 48], vocab_cap=300, min_slots=2, min_slot_fillers=8,
                held_per_concept=1, min_train_fillers=6, n_test=400, seeds=[7, 13, 19])


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
    agg = aggregate(chance, headline_dim, per_seed, cfg["cap_dims"], cfg["t_curve"])
    hashes = arms_differ(per_seed, "real_conceptnet")

    elapsed = time.perf_counter() - t0
    v = agg["verdict"]
    ctrl = agg["per_condition"]["control_synthetic"]
    real = agg["per_condition"]["real_conceptnet"]
    msg = (f"{v} | headlineN={headline_dim} m={cfg['m']} chance={chance:.3f} "
           f"| CTRL(Gate-D) F={ctrl['factored_headline']:.3f} gap={ctrl['gap_headline']:.3f} "
           f"| REAL F={real['factored_headline']:.3f} FLAT={real['flat_headline']:.3f} "
           f"gap={real['gap_headline']:.3f} rng={real['factored_headline_range']:.3f} "
           f"corr={real['content_cos_mean']:.3f} gcos={real['g_hat_cos_headline']:.3f} "
           f"realcost={agg['real_content_cost_headline']:+.3f} | posctrl={agg['positive_control_reproduces']} "
           f"mustfail={agg['real_must_fail_control_fired']} realgen={agg['real_generalizes']} "
           f"realbreak={agg['real_breaks']} unsat={agg['real_unsaturated_headroom']} "
           f"| V={meta['n_vocab']} slots={meta['n_slots']}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": v, "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": cfg, "chance": chance, "headline_dim": headline_dim, "aggregate": agg,
        "data_meta": meta, "arms_differ_hashes": hashes, "arms_differ_verified": True,
        "scaffold_free_witness": witness, "final_metrics_atomicity": "tmp_replace",
        "content_source": "REAL GloVe-wiki-gigaword-300 (Pennington 2014) FHRR-encoded",
        "relation_source": "REAL ConceptNet5 en-100k (Speer 2017); slot=(predicate,arg-role)",
        "notes": ("FULL-CHAIN-GRADE gate: structure-content factorization on REAL EXTRACTED ConceptNet "
                  "relations. HARD_PASS_READING_AXIS_FIRST_CG = un-saturated (capacity-edge) compositional "
                  "generalization on real extracted relations where flat fails (brain-faithful native bind). "
                  "Remaining step: relations extracted by OUR reader on real narrative (couples reader "
                  "extraction noise). CLAIM-VET-pending; VET adjudicates CG vs CG-candidate."),
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  rel_type_counts (real ConceptNet skew): {meta['rel_type_counts']}", flush=True)
    print(f"  slot_filler_counts: {meta['slot_filler_counts']}", flush=True)
    for cond in CONDITIONS:
        cc = agg["per_condition"][cond]
        print(f"  [{cond}] content_cos_mean={cc['content_cos_mean']:.3f} "
              f"headline(N={headline_dim}) F={cc['factored_headline']:.3f} FLAT={cc['flat_headline']:.3f} "
              f"gap={cc['gap_headline']:.3f} gcos={cc['g_hat_cos_headline']:.3f}", flush=True)
        print("     capacity sweep (F=FACTORED, N-dim; un-saturation axis):", flush=True)
        for r in cc["capacity"]:
            print(f"        N={r['n_dim']:>4} F={r['factored']:.3f} FLAT={r['flat']:.3f} "
                  f"gcos={r['g_hat_cos']:.3f} F_rng={r['factored_range']:.3f}", flush=True)
        print("     learning curve (training-per-role t; g improves with exposure):", flush=True)
        for r in cc["curve"]:
            print(f"        t={r['t']:>3} F={r['factored']:.3f} FLAT={r['flat']:.3f} "
                  f"gcos={r['g_hat_cos']:.3f}", flush=True)
    print("  [per-relation-type held-out breakdown | real_conceptnet | headline N]", flush=True)
    for p, d in sorted(real["per_pred_heldout"].items(), key=lambda kv: -kv[1]["n_mean"]):
        print(f"        {p:<14} F={d['factored']:.3f} FLAT={d['flat']:.3f} n~{d['n_mean']:.0f}", flush=True)
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
            cap_dims=[48, 256], m=6, knn=10, t_primary=24, t_curve=[6, 24], vocab_cap=300,
            min_slots=2, min_slot_fillers=8, held_per_concept=1, min_train_fillers=6,
            n_test=80, seeds=[7])
        agg = aggregate(chance, hd, per_seed, [48, 256], [6, 24])
        arms_differ(per_seed, "real_conceptnet")
        ctrl = agg["per_condition"]["control_synthetic"]
        real = agg["per_condition"]["real_conceptnet"]
        print(f"[{ANCHOR_NAME}] self-test end-to-end: verdict={agg['verdict']} headlineN={hd} "
              f"CTRL_F={ctrl['factored_headline']:.3f} REAL_F={real['factored_headline']:.3f} "
              f"REAL_corr={real['content_cos_mean']:.3f} REAL_gap={real['gap_headline']:.3f} "
              f"V={meta['n_vocab']} slots={meta['n_slots']} chance={chance:.3f}", flush=True)
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
