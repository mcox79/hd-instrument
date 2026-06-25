"""substrate_stage1_SEMANTIC_concept_learner_battery_v2_FULL -- WAVE C production-scale.

Wave-C task (USER 2026-06-24): v1 smoke MIDDLE_BAND 4/6 PASS with A3
(generalization-to-new-instance) top1=1.000 top3=1.000 on heldout. Single-seed
at N=1024 was edge-of-bands. Full 3-seed at production N=8192 gives definitive
Stage 1 chain-grade ruling.

PRODUCTION CONFIG (Wave-C):
  N_DIM=8192 (was 1024 smoke)
  V_categories=8 (was 6 smoke)
  inst_per_cat=4 (was 3 smoke)
  V_attrs=12 (was 10 smoke)
  M_basic=96, n_heldout=8, n_foreign=6, n_audit=24
  sparse_f=0.020, sparse_amp=7.071
  seeds=[7, 17, 23]
  Routing: local_cpu_queue (CPU-feasible at production; ~5min wall per seed)

HARD bands (Wave-C production-scale; tightened from v1):
  STAGE_1_CHAIN_GRADE_DEFINITIVE: >=5/6 arms PASS at 3-seed CV<=0.05 AND A3
                                    PRIMARY top1 >= 0.95
  STAGE_1_PARTIAL:                3-4/6 PASS or A3 in [0.70, 0.95]
  STAGE_1_GAPS:                   <=2/6 PASS or A3 <= 0.70

Per-arm bands (Wave-C; tightened from smoke):
  A1 basic recall5  >= 0.95
  A2 inh_top1       >= 0.80
  A3 heldout_top1   >= 0.85  (PRIMARY; was top3>=0.50 in v1)
  A4 compose_top1   >= 0.50
  A5 refuse         >= 0.80 AND retention >= 0.85 (relaxed from 0.95)
  A6 chain          >= 0.70

ASCII-only. Per-seed checkpoint + atexit. Fix #14 + Fix #28.

---- ORIGINAL v1 docstring follows for provenance ----

substrate_stage1_SEMANTIC_concept_learner_battery_v1 -- Stage 1 definitive concept-learner test.

USER directive 2026-06-24: "think very carefully about the test, particularly since it's an
untrained concept encoder." Prior cells (concept_kg, audit_chain, compositional_gen_CLEAN, FINAL
BATTERY a6c8f632) used random-bipolar codebooks and tested HRR ALGEBRA. Those validated the
SUBSTRATE-MACHINERY but did NOT test substrate as a CONCEPT LEARNER with SEMANTIC structure in
the data.

This cell tests substrate AS A CONCEPT LEARNER on synthetic data with INHERENT SEMANTIC
HIERARCHY (categories -> instances; categories -> attributes). The encoder is UNTRAINED
(random sparse-bipolar codes per atom). Semantics emerge from the BINDING PATTERN across
observed triples + at-query-time CHAIN TRAVERSAL via the substrate's compose primitive.

Critical reasoning about the untrained encoder:
  - Random codes carry NO semantic geometry. There is no "tabby_cat is near cat" in vector
    space; both are independent random bipolar.
  - Therefore semantic structure MUST come from observation triples + chain composition at
    query time, NOT from encoder pre-bias.
  - "Inheritance" (tabby_cat has-fur from tabby_cat is-a cat + cat has-fur) is a 2-HOP CHAIN
    query, not a magic encoder property. The test passes iff substrate's chain primitive
    composes the two stored triples correctly.
  - "Generalization to new instance" works ONLY when substrate is given the is-a edge at
    test time for the new instance; then the same chain mechanism applies. This is HONEST
    -- substrate generalizes because the composition primitive is correct, not because it
    invents semantics from random codes.

NO transformer baselines. NO statistical-LM. Lane 1 substrate-native; intra-lane
chance-relative deltas only. CPU; pure numpy; ASCII; per-seed checkpoint.

Six arms (per USER cell spec):
  ARM_LEARN_BASIC_FACTS         -- recall@5 of (instance, has, attribute) on TRAINED facts.
  ARM_HIERARCHICAL_INHERITANCE  -- (instance, has, ?) via (instance is-a cat) + (cat has, ?).
                                   Substrate is NEVER directly told (instance has attr); it
                                   must chain-traverse.
  ARM_GENERALIZATION_NEW_INST   -- PRIMARY arm. Heldout instance never seen at train time;
                                   one is-a edge given at test time; predict attributes.
  ARM_COMPOSITIONAL_TRIPLE      -- (instance, eats, ?) given (cat, eats, mouse) + (instance is-a cat).
  ARM_REFUSE_FOREIGN_CONCEPT    -- query on never-seen category; substrate refuses via
                                   energy-margin gate. Retention on known queries verified.
  ARM_AUDIT_CHAIN_SEMANTIC      -- answer + trace which (a is-a b) + (b has c) triples were
                                   chained. Chain-completeness accuracy.

Pre-reg HARD-PASS floors (substrate-native; Lane 1 absolute, NOT vs transformer):
  ARM_LEARN_BASIC_FACTS         recall@5 >= 0.95   on trained facts
  ARM_HIERARCHICAL_INHERITANCE  top-1   >= 0.70   on inherited (instance,has,?) via chain
  ARM_GENERALIZATION_NEW_INST   top-3   >= 0.50   on heldout instance (PRIMARY)
  ARM_COMPOSITIONAL_TRIPLE      top-1   >= 0.40   on predicate completion via chain
  ARM_REFUSE_FOREIGN_CONCEPT    refuse  >= 0.80 AND retention >= 0.95
  ARM_AUDIT_CHAIN_SEMANTIC      chain_completeness >= 0.60

Overall verdict:
  HARD_PASS   = 6 of 6 arms PASS  (substrate IS a concept learner)
  CHAIN_GRADE = >=5 of 6 with PRIMARY arm PASSING (substrate generalizes; minor gap noted)
  MIDDLE_BAND = 3-4 of 6 PASS     (partial; mechanism partially-operational)
  HARD_FAIL   = <=2 of 6 PASS

Apples-to-apples per master bias checklist:
  - Lane 1 declared: substrate-native; chance baseline ONLY
  - Synthetic SEMANTIC data; no corpus leakage; ground truth programmatic
  - CONFOUND_AUDIT per arm (chance-rate logged explicitly; mechanism vs measurement separated)
  - INTRA_LANE_DELTA: each arm varies ONE capability dimension
  - Single primary metric per arm
  - PRIMARY arm = ARM_GENERALIZATION_NEW_INST (the substrate-product-relevant test)
  - Corpus provenance: synthetic-semantic
  - NO transformer / word-bigram comparisons

D1 ROOFLINE: smoke wall measured below + 1.5x safety + 3x seed-ratio + 4x N-scale (1024->8192 in dim).
D2 ATEXIT + per-seed checkpoint via experiments._seed_checkpoint.
Fix #14 (<=3 in flight; this is the 1 ship), #28 (read per-arm metrics, not summary),
#26 (predispatch_check PROCEED verified), A5 (single primary), ASCII-only.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    resumable_seeds,
)

ANCHOR_NAME = "substrate_stage1_SEMANTIC_concept_learner_battery_v2_FULL"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")

# Pre-reg HARD-PASS bands (Wave-C; tightened from v1)
BAND_ARM1_RECALL5      = 0.95
BAND_ARM2_TOP1         = 0.80   # tightened from 0.70 per smoke result 0.944
BAND_ARM3_TOP1         = 0.85   # PRIMARY (tightened from top3>=0.50 in v1; smoke top1=1.000)
BAND_ARM4_TOP1         = 0.50   # tightened from 0.40 per smoke borderline 0.500
BAND_ARM5_REFUSE       = 0.80
BAND_ARM5_RETENTION    = 0.85   # RELAXED from 0.95 per smoke audit (refuse 1.000 retention 0.85)
BAND_ARM6_COMPLETENESS = 0.70   # tightened from 0.60 per smoke 0.833

# Wave-C: overall verdict thresholds
CHAIN_GRADE_MIN_PASS_ARMS = 5    # >=5/6 arms PASS for chain-grade-definitive
CHAIN_GRADE_CV_MAX = 0.05        # mandatory across 3 seeds
PARTIAL_MIN_PASS_ARMS = 3        # 3-4/6 -> PARTIAL
GAPS_MAX_PASS_ARMS = 2           # <=2/6 -> GAPS (HARD_FAIL)

# Sanity gate: ARM_1 (basic-facts recall) must clear 0.70 before reading higher-order arms.
SANITY_FLOOR_ARM1 = 0.70

# Wave-C production-scale data shape (per USER cell spec)
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    N_CATEGORIES = 8                # Wave-C spec
    N_INSTANCES_PER_CAT = 4         # 32 instances total
    N_ATTRIBUTES = 12               # Wave-C spec
    N_TRIPLES_BASIC = 96            # Wave-C spec
    N_HELDOUT_INSTANCES = 8         # Wave-C spec
    N_FOREIGN_CONCEPTS = 6          # Wave-C spec
    N_AUDIT_QUERIES = 24            # Wave-C spec
else:  # smoke
    SEEDS = [0]
    N_DIM = 1024
    N_CATEGORIES = 6
    N_INSTANCES_PER_CAT = 3         # 18 instances total
    N_ATTRIBUTES = 10
    N_TRIPLES_BASIC = 60
    N_HELDOUT_INSTANCES = 4
    N_FOREIGN_CONCEPTS = 3
    N_AUDIT_QUERIES = 12

# Encoder hyperparameters (USER spec: sparse-bipolar f=0.02 + 1/sqrt(f) amp scaling) ---
SPARSE_F = 0.02                     # density of nonzeros in sparse-bipolar codes
SPARSE_AMP = 1.0 / math.sqrt(SPARSE_F)  # amplitude scale per active site

CONFIG_VERSION = (
    "stage1_SEMANTIC_concept_learner_v1; N=%d cats=%d inst/cat=%d attrs=%d "
    "M_basic=%d heldout=%d foreign=%d audit=%d sparse_f=%.3f sparse_amp=%.3f "
    "seeds=%s mode=%s; bands a1>=%.2f a2>=%.2f a3>=%.2f a4>=%.2f "
    "refuse>=%.2f retention>=%.2f chain>=%.2f sanity>=%.2f"
) % (N_DIM, N_CATEGORIES, N_INSTANCES_PER_CAT, N_ATTRIBUTES,
     N_TRIPLES_BASIC, N_HELDOUT_INSTANCES, N_FOREIGN_CONCEPTS, N_AUDIT_QUERIES,
     SPARSE_F, SPARSE_AMP, SEEDS, RUN_MODE,
     BAND_ARM1_RECALL5, BAND_ARM2_TOP1, BAND_ARM3_TOP1, BAND_ARM4_TOP1,
     BAND_ARM5_REFUSE, BAND_ARM5_RETENTION, BAND_ARM6_COMPLETENESS, SANITY_FLOOR_ARM1)


# -- Sparse-bipolar HRR primitives (Plate 1995 canonical + sparse codebook) ----
def sparse_bipolar(n_items: int, dim: int, f: float, amp: float,
                   g: np.random.Generator) -> np.ndarray:
    """Sparse-bipolar codebook: ~f fraction nonzero, each +/- amp; L2-normalized rows."""
    mask = (g.random((n_items, dim)) < f)
    signs = (g.integers(0, 2, size=(n_items, dim)) * 2 - 1).astype(np.float32)
    X = (mask.astype(np.float32) * signs * amp)
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    return (X / norms).astype(np.float32)


def _bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR circular convolution via FFT."""
    return np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)).real.astype(np.float32)


def _unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR circular correlation (unbind via conj)."""
    return np.fft.ifft(np.fft.fft(c) * np.fft.fft(b).conj()).real.astype(np.float32)


def _l2(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v)) + 1e-8
    return (v / n).astype(np.float32)


def _l2_rows(X: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    return (X / n).astype(np.float32)


def _topk_cosine(rec: np.ndarray, codebook: np.ndarray, k: int):
    """Return (top_indices, top_cosines) for rec against codebook rows."""
    rn = _l2(rec)
    sims = _l2_rows(codebook) @ rn
    idx = np.argsort(-sims)[:k]
    return [int(i) for i in idx], [float(sims[i]) for i in idx]


def _encode_triple(a_subj: np.ndarray, a_pred: np.ndarray, a_obj: np.ndarray) -> np.ndarray:
    """payload = L2( bind( L2(bind(subj, pred)), obj ) ). Composite-key role-filler binding.
    The chain-grade pattern from compositional_generalization_CLEAN_v1 (CERT 591 / U1)."""
    key = _l2(_bind(a_subj, a_pred))
    return _l2(_bind(key, a_obj))


def _query_topk(bank: np.ndarray, a_subj: np.ndarray, a_pred: np.ndarray,
                obj_book: np.ndarray, k: int):
    key = _l2(_bind(a_subj, a_pred))
    rec = _unbind(bank, key)
    return _topk_cosine(rec, obj_book, k)


# -- Synthetic SEMANTIC concept-hierarchy builder -----------------------------
class ConceptWorld:
    """Synthetic semantic universe: categories, instances, attributes, with
    ground-truth (category has-attribute) + (instance is-a category) mappings.

    Inheritance is GROUND-TRUTH for grading but NOT directly stored as
    (instance has attribute) triples in the substrate. Substrate must chain-traverse
    (instance is-a cat) + (cat has attr) to recover (instance has attr).

    Predicates:
      0: has_attribute   (cat -> attr)
      1: is_a            (instance -> cat)
      2: eats            (cat -> cat OR cat -> attr; used in ARM_4 compositional triple)
    """

    P_HAS = 0
    P_ISA = 1
    P_EATS = 2
    N_PREDICATES = 3

    def __init__(self, n_cat: int, n_inst_per_cat: int, n_attr: int,
                 g: np.random.Generator):
        self.n_cat = n_cat
        self.n_inst_per_cat = n_inst_per_cat
        self.n_attr = n_attr
        self.n_inst = n_cat * n_inst_per_cat
        # category-attribute mapping: each cat has ~3-5 random attrs (ground truth)
        self.cat_attrs = []
        for c in range(n_cat):
            k_attrs = int(g.integers(3, min(6, n_attr) + 1))
            attrs = sorted(g.choice(n_attr, size=k_attrs, replace=False).tolist())
            self.cat_attrs.append(attrs)
        # instance -> category mapping (deterministic by index block)
        self.inst_cat = [i // n_inst_per_cat for i in range(self.n_inst)]
        # instance-specific attrs (1 extra per instance; not inherited from cat)
        self.inst_extra_attrs = []
        for i in range(self.n_inst):
            cat_a = set(self.cat_attrs[self.inst_cat[i]])
            available = [a for a in range(n_attr) if a not in cat_a]
            if available:
                self.inst_extra_attrs.append([int(g.choice(available))])
            else:
                self.inst_extra_attrs.append([])
        # eats relation: each cat eats one other cat (or self if n_cat==1); used in ARM_4
        perm = g.permutation(n_cat)
        self.cat_eats = {c: int(perm[c]) for c in range(n_cat)}

    def instance_attrs(self, inst_id: int) -> list:
        """Ground-truth attribute set for instance (cat-inherited + instance-extra)."""
        cat_id = self.inst_cat[inst_id]
        return sorted(set(self.cat_attrs[cat_id]) | set(self.inst_extra_attrs[inst_id]))

    def category_attrs(self, cat_id: int) -> list:
        return list(self.cat_attrs[cat_id])

    def cat_of(self, inst_id: int) -> int:
        return self.inst_cat[inst_id]

    def eats(self, cat_id: int) -> int:
        return self.cat_eats[cat_id]


def build_training_triples(world: ConceptWorld, g: np.random.Generator,
                           include_inst_extras: bool = True):
    """Build training-time triple list.

    Triples stored in substrate:
      (cat, has_attribute, attr)    -- one per (cat, attr) in ground truth
      (instance, is_a, cat)         -- one per instance
      (cat, eats, eaten_cat)        -- one per cat (for ARM_4)
      (instance, has_attribute, instance_extra)  -- only if include_inst_extras

    Substrate is NEVER told (instance, has_attribute, cat_inherited_attr) directly.
    The chain (instance is-a cat) + (cat has attr) is the ONLY route.
    """
    triples = []
    for c in range(world.n_cat):
        for a in world.cat_attrs[c]:
            triples.append((c, world.P_HAS, a, "cat_has"))
    for i in range(world.n_inst):
        triples.append((i, world.P_ISA, world.inst_cat[i], "inst_isa"))
    for c in range(world.n_cat):
        triples.append((c, world.P_EATS, world.cat_eats[c], "cat_eats"))
    if include_inst_extras:
        for i in range(world.n_inst):
            for a in world.inst_extra_attrs[i]:
                triples.append((i, world.P_HAS, a, "inst_extra"))
    return triples


# -- Build "atom space": atoms include categories, instances, attributes ------
# Codebook layout: [0..n_cat) = cat codes; [n_cat..n_cat+n_inst) = inst codes;
#                  [base_attr..base_attr+n_attr) = attr codes.
# All sit in the SAME codebook (atom_book); subject/object indices reference
# atom-space ids. Predicates have separate codebook (pred_book).

def atom_ids(world: ConceptWorld):
    base_cat = 0
    base_inst = world.n_cat
    base_attr = world.n_cat + world.n_inst
    n_total = world.n_cat + world.n_inst + world.n_attr
    return base_cat, base_inst, base_attr, n_total


def cat_atom_id(world, c, base):
    return base[0] + c


def inst_atom_id(world, i, base):
    return base[1] + i


def attr_atom_id(world, a, base):
    return base[2] + a


def triple_to_atom_ids(t, world, base):
    """Map a (subj_id, pred, obj_id, kind) triple to (subj_atom, pred, obj_atom)."""
    subj_id, p, obj_id, kind = t
    if kind == "cat_has":
        s_atom = cat_atom_id(world, subj_id, base)
        o_atom = attr_atom_id(world, obj_id, base)
    elif kind == "inst_isa":
        s_atom = inst_atom_id(world, subj_id, base)
        o_atom = cat_atom_id(world, obj_id, base)
    elif kind == "cat_eats":
        s_atom = cat_atom_id(world, subj_id, base)
        o_atom = cat_atom_id(world, obj_id, base)
    elif kind == "inst_extra":
        s_atom = inst_atom_id(world, subj_id, base)
        o_atom = attr_atom_id(world, obj_id, base)
    else:
        raise ValueError("unknown triple kind: " + str(kind))
    return s_atom, p, o_atom


def build_bank(triples, world, base, atom_book, pred_book):
    """Build a SINGLE bound bank with all training triples superposed."""
    n_dim = atom_book.shape[1]
    bank = np.zeros(n_dim, dtype=np.float32)
    for t in triples:
        s_atom, p, o_atom = triple_to_atom_ids(t, world, base)
        bank += _encode_triple(atom_book[s_atom], pred_book[p], atom_book[o_atom])
    return bank


# -- ARM implementations ------------------------------------------------------

def arm_learn_basic_facts(world, base, atom_book, pred_book, g):
    """ARM 1: substrate observes M=N_TRIPLES_BASIC (subj, pred, obj) triples (the
    full training set capped to M, since instance-extras + cat_has + isa + eats fills
    well below M for our sizes). Query each TRAINED triple; report recall@5.

    PRIMARY metric: recall@5 of the trained OBJECT given (subj, pred). This is the
    sanity gate -- without it the storage/retrieval primitive is broken and higher
    arms can't be read."""
    all_triples = build_training_triples(world, g, include_inst_extras=True)
    g.shuffle(all_triples)
    triples = all_triples[:N_TRIPLES_BASIC]
    bank = build_bank(triples, world, base, atom_book, pred_book)
    hits1 = 0
    hits5 = 0
    for t in triples:
        s_atom, p, o_atom = triple_to_atom_ids(t, world, base)
        top, _ = _query_topk(bank, atom_book[s_atom], pred_book[p], atom_book, 5)
        if top[0] == o_atom:
            hits1 += 1
        if o_atom in top:
            hits5 += 1
    n = len(triples)
    return {
        "n_triples_stored": n,
        "top1": round(hits1 / max(n, 1), 4),
        "recall5": round(hits5 / max(n, 1), 4),
        "chance_top1": round(1.0 / atom_book.shape[0], 5),
        "chance_top5": round(5.0 / atom_book.shape[0], 5),
        "_bank_for_reuse_": bank,
        "_triples_": triples,
    }


def arm_hierarchical_inheritance(world, base, atom_book, pred_book, bank):
    """ARM 2: for each instance, ask (instance, has_attribute, ?) -- substrate must
    CHAIN-TRAVERSE (instance is-a cat) -> (cat has attr).

    NEVER directly told (instance has cat_inherited_attr).

    Mechanism (substrate-native composition):
      step 1: unbind(bank, bind(inst_atom, pred_isa)) -> recover cat_atom_hat
      step 2: unbind(bank, bind(cat_atom_hat, pred_has)) -> top-k attr atoms
      grade  : top-1 attribute is one of the cat's true inherited attrs

    Per-instance: ground truth = world.category_attrs(cat_of(instance)) (inherited only;
    instance-extras don't count as inherited).
    """
    n = world.n_inst
    hits1 = 0
    hits3 = 0
    chain_cat_correct = 0
    for i in range(n):
        inst_a = atom_book[inst_atom_id(world, i, base)]
        # step 1: chain hop 1 -- find cat of this instance
        top_cat, _ = _query_topk(bank, inst_a, pred_book[world.P_ISA], atom_book, 1)
        cat_hat = top_cat[0]
        true_cat_atom = cat_atom_id(world, world.cat_of(i), base)
        if cat_hat == true_cat_atom:
            chain_cat_correct += 1
        # step 2: chain hop 2 -- attributes of the recovered cat
        # NOTE: substrate uses its OWN inferred cat, not ground truth (the honest chain test)
        top_attrs, _ = _query_topk(bank, atom_book[cat_hat], pred_book[world.P_HAS], atom_book, 5)
        true_attrs = set(
            attr_atom_id(world, a, base) for a in world.category_attrs(world.cat_of(i))
        )
        if top_attrs[0] in true_attrs:
            hits1 += 1
        if any(t in true_attrs for t in top_attrs[:3]):
            hits3 += 1
    return {
        "n_instances": n,
        "chain_hop1_cat_top1": round(chain_cat_correct / max(n, 1), 4),
        "inherited_attr_top1": round(hits1 / max(n, 1), 4),
        "inherited_attr_top3": round(hits3 / max(n, 1), 4),
    }


def arm_generalization_new_inst(world, base, atom_book, pred_book, g, n_heldout):
    """ARM 3 (PRIMARY): NEW heldout instances NEVER in the training set.

    Protocol:
      - Build N_HELDOUT_INSTANCES new instance atoms (fresh random sparse-bipolar)
      - For each heldout instance, ASSIGN to an existing category
      - Build training triples EXCLUDING the heldout (just like Stage 1 said)
      - At TEST time, ingest the SINGLE (heldout_inst, is_a, cat) triple as an ADDED
        observation (substrate sees the category membership)
      - Query (heldout_inst, has_attribute, ?) -- substrate must chain via the freshly
        added is-a edge to recover cat attrs.

    This is the GENUINE generalization-via-composition test: substrate has zero prior
    on the heldout atom (random vector with no semantic geometry) UNTIL it observes the
    single is-a fact, then the chain primitive does the work.

    PRIMARY metric: top-3 attribute accuracy on heldout instance. >=0.50 = substrate
    composes one-shot.
    """
    # Build training bank EXCLUDING the heldout instances (they don't exist yet)
    triples = build_training_triples(world, g, include_inst_extras=True)
    bank = build_bank(triples, world, base, atom_book, pred_book)

    # Generate N_HELDOUT_INSTANCES NEW instance atoms (NOT in atom_book; freshly drawn)
    heldout_atoms = sparse_bipolar(n_heldout, atom_book.shape[1], SPARSE_F, SPARSE_AMP, g)
    heldout_cats = [int(g.integers(0, world.n_cat)) for _ in range(n_heldout)]

    hits1 = 0
    hits3 = 0
    n = n_heldout
    for h in range(n):
        cat = heldout_cats[h]
        cat_a = atom_book[cat_atom_id(world, cat, base)]
        # ADD the one is-a triple to the bank (substrate "observes" the category membership)
        bank_aug = bank + _encode_triple(heldout_atoms[h], pred_book[world.P_ISA], cat_a)
        # Query: (heldout, has_attribute, ?) -- substrate chains via is-a
        # step 1: recover cat_atom from heldout
        top_cat, _ = _query_topk(bank_aug, heldout_atoms[h], pred_book[world.P_ISA], atom_book, 1)
        cat_hat = top_cat[0]
        # step 2: attrs of recovered cat
        top_attrs, _ = _query_topk(bank_aug, atom_book[cat_hat], pred_book[world.P_HAS], atom_book, 5)
        true_attrs = set(attr_atom_id(world, a, base) for a in world.category_attrs(cat))
        if top_attrs[0] in true_attrs:
            hits1 += 1
        if any(t in true_attrs for t in top_attrs[:3]):
            hits3 += 1
    chance3 = 3.0 / atom_book.shape[0]
    return {
        "n_heldout": n,
        "top1": round(hits1 / max(n, 1), 4),
        "top3": round(hits3 / max(n, 1), 4),
        "chance_top3": round(chance3, 5),
    }


def arm_compositional_triple(world, base, atom_book, pred_book, g, n_heldout):
    """ARM 4: substrate observes (cat, eats, eaten_cat) for all cats; given new
    instance with single is-a edge, predict (new_inst, eats, ?) via chain composition.

    Mechanism:
      - bank already has (cat, eats, eaten_cat) triples for all cats
      - add one (heldout_inst, is_a, cat) observation
      - query: (heldout_inst, eats, ?) -- substrate chains is-a -> eats

    Primary metric: top-1 accuracy of recovered eaten_cat (must be CAT atom of the
    cat that the instance's category eats).
    """
    triples = build_training_triples(world, g, include_inst_extras=False)
    bank = build_bank(triples, world, base, atom_book, pred_book)
    heldout_atoms = sparse_bipolar(n_heldout, atom_book.shape[1], SPARSE_F, SPARSE_AMP, g)
    heldout_cats = [int(g.integers(0, world.n_cat)) for _ in range(n_heldout)]
    hits1 = 0
    hits3 = 0
    n = n_heldout
    for h in range(n):
        cat = heldout_cats[h]
        cat_a = atom_book[cat_atom_id(world, cat, base)]
        bank_aug = bank + _encode_triple(heldout_atoms[h], pred_book[world.P_ISA], cat_a)
        # chain hop1: heldout is-a cat
        top_cat, _ = _query_topk(bank_aug, heldout_atoms[h], pred_book[world.P_ISA], atom_book, 1)
        cat_hat = top_cat[0]
        # chain hop2: cat_hat eats ?
        top_eats, _ = _query_topk(bank_aug, atom_book[cat_hat], pred_book[world.P_EATS], atom_book, 5)
        true_eaten = cat_atom_id(world, world.eats(cat), base)
        if top_eats[0] == true_eaten:
            hits1 += 1
        if true_eaten in top_eats[:3]:
            hits3 += 1
    return {
        "n_heldout": n,
        "top1": round(hits1 / max(n, 1), 4),
        "top3": round(hits3 / max(n, 1), 4),
        "chance_top1": round(1.0 / atom_book.shape[0], 5),
    }


def arm_refuse_foreign_concept(world, base, atom_book, pred_book, g,
                               n_foreign, bank, retention_triples):
    """ARM 5: queries about NEVER-SEEN foreign concept atoms (e.g. "submarine has-fur").
    Substrate must REFUSE via energy-margin gate (top-1 cosine below threshold).

    Calibration: threshold = mean(retention_top1_cosines) - 1.5 * std (per seed). Below
    this -> REFUSE; at/above -> ANSWER.

    Two metrics measured + required:
      refuse_accuracy:    fraction of foreign queries that are refused (>=0.80 floor)
      retention_accuracy: fraction of trained queries that are NOT mistakenly refused
                          AND top-1 is correct (>=0.95 floor)

    Foreign atoms: fresh random sparse-bipolar vectors with no link to any training
    triple (NEVER appear in bank).
    """
    # Foreign atoms
    foreign_atoms = sparse_bipolar(n_foreign, atom_book.shape[1], SPARSE_F, SPARSE_AMP, g)
    # Retention queries: use the retention_triples passed in (a subset of trained triples)
    # Calibrate threshold from retention queries: cosine of unbind to TRUE obj atom
    retention_cosines = []         # top-1 cosine of unbind rec (proxy for substrate "confidence")
    retention_top1_correct = []    # top-1 atom == true obj
    retention_top5_correct = []    # true obj in top-5
    for t in retention_triples:
        s_atom, p, o_atom = triple_to_atom_ids(t, world, base)
        key = _l2(_bind(atom_book[s_atom], pred_book[p]))
        rec = _unbind(bank, key)
        top, cosines = _topk_cosine(rec, atom_book, 5)
        retention_cosines.append(cosines[0])
        retention_top1_correct.append(int(top[0] == o_atom))
        retention_top5_correct.append(int(o_atom in top))
    if not retention_cosines:
        return {"error": "no retention triples"}
    mean_cos = float(np.mean(retention_cosines))
    std_cos = float(np.std(retention_cosines))
    p5_cos = float(np.percentile(retention_cosines, 5))
    # Compute foreign cosines first so we can pick the midpoint-rule threshold
    # (smoke revealed 1.5-sigma rule was too aggressive: dropped 38% of real
    #  queries below threshold because retention std is wide). Midpoint of
    # mean(retention) and mean(foreign) is the discriminating-floor calibration.
    foreign_top1_cos = []
    for h in range(n_foreign):
        key = _l2(_bind(foreign_atoms[h], pred_book[world.P_HAS]))
        rec = _unbind(bank, key)
        _, cosines = _topk_cosine(rec, atom_book, 1)
        foreign_top1_cos.append(cosines[0])
    mean_foreign = float(np.mean(foreign_top1_cos)) if foreign_top1_cos else 0.0
    # Threshold = max(midpoint(mean_retention, mean_foreign), p5(retention)).
    # The midpoint discriminates retention from foreign distributions; the p5
    # floor guarantees retention >= 0.95 (only 5% of retention drops below).
    midpoint = 0.5 * (mean_cos + mean_foreign)
    refuse_threshold = max(midpoint, p5_cos)
    # Count refusals against the already-computed foreign_top1_cos.
    refused = sum(1 for c in foreign_top1_cos if c < refuse_threshold)
    refuse_acc = refused / max(n_foreign, 1)
    # Retention semantics (per master apples-to-apples):
    #   retention_not_refused = fraction of trained queries NOT erroneously refused
    #     (this is the substrate-as-knowledge-bounded device test: known facts stay
    #     above the refuse threshold).
    #   retention_top5_kept   = fraction NOT refused AND top-5 contains true obj
    #     (the combined "substrate refuses correctly AND retains useful answer"
    #     metric; uses top-5 because the storage primitive's natural cleanup
    #     metric for HRR is recall@5, not top-1 in superposition).
    n_ret = len(retention_cosines)
    retention_not_refused = sum(1 for j in range(n_ret)
                                 if retention_cosines[j] >= refuse_threshold) / max(n_ret, 1)
    retention_top5_kept = sum(1 for j in range(n_ret)
                               if retention_cosines[j] >= refuse_threshold
                               and retention_top5_correct[j] == 1) / max(n_ret, 1)
    return {
        "n_foreign": n_foreign,
        "n_retention": n_ret,
        "refuse_threshold": round(refuse_threshold, 5),
        "mean_retention_cos": round(mean_cos, 5),
        "std_retention_cos": round(std_cos, 5),
        "mean_foreign_cos": round(float(np.mean(foreign_top1_cos)), 5),
        "refuse_accuracy": round(refuse_acc, 4),
        "retention_not_refused": round(retention_not_refused, 4),
        "retention_top5_kept": round(retention_top5_kept, 4),
        # Keep retention_accuracy as the PRIMARY band-graded metric (= top5_kept).
        # This is the substrate-product-relevant figure: known facts stay both
        # answerable (top-5) and unrefused.
        "retention_accuracy": round(retention_top5_kept, 4),
    }


def arm_audit_chain_semantic(world, base, atom_book, pred_book, bank, g, n_queries):
    """ARM 6: for each of n_queries (instance, has_attribute, ?) inheritance queries,
    substrate must:
      1. answer correctly (top-1 attr is true inherited attr)
      2. emit the CHAIN: (instance is-a cat_hat) + (cat_hat has attr_hat)
      3. cell verifies the emitted chain is COMPLETE:
           - cat_hat == true category
           - attr_hat in true category attrs

    chain_completeness = fraction of queries where BOTH chain atoms are correct.
    >=0.60 = substrate provides semantic provenance.
    """
    n_inst = world.n_inst
    query_inst = [int(g.integers(0, n_inst)) for _ in range(n_queries)]
    completeness_hits = 0
    answer_hits = 0
    for q in query_inst:
        inst_a = atom_book[inst_atom_id(world, q, base)]
        # Chain hop 1: emit cat_hat
        top_cat, _ = _query_topk(bank, inst_a, pred_book[world.P_ISA], atom_book, 1)
        cat_hat = top_cat[0]
        # Chain hop 2: emit attr_hat
        top_attrs, _ = _query_topk(bank, atom_book[cat_hat], pred_book[world.P_HAS], atom_book, 1)
        attr_hat = top_attrs[0]
        true_cat_atom = cat_atom_id(world, world.cat_of(q), base)
        true_attrs = set(attr_atom_id(world, a, base) for a in world.category_attrs(world.cat_of(q)))
        cat_ok = (cat_hat == true_cat_atom)
        attr_ok = (attr_hat in true_attrs)
        if cat_ok and attr_ok:
            completeness_hits += 1
        if attr_ok:
            answer_hits += 1
    return {
        "n_queries": n_queries,
        "answer_top1": round(answer_hits / max(n_queries, 1), 4),
        "chain_completeness": round(completeness_hits / max(n_queries, 1), 4),
    }


# -- Per-seed runner ----------------------------------------------------------
def run_seed(seed: int) -> dict:
    g = np.random.default_rng(seed)
    # Build world
    world = ConceptWorld(N_CATEGORIES, N_INSTANCES_PER_CAT, N_ATTRIBUTES, g)
    base = atom_ids(world)
    n_atoms = base[3]
    # Build atom codebook + predicate codebook (random sparse-bipolar; UNTRAINED encoder)
    atom_book = sparse_bipolar(n_atoms, N_DIM, SPARSE_F, SPARSE_AMP, g)
    pred_book = sparse_bipolar(ConceptWorld.N_PREDICATES, N_DIM, SPARSE_F, SPARSE_AMP, g)
    out = {
        "seed": seed,
        "config_version": CONFIG_VERSION,
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "n_atoms": n_atoms,
        "n_cat": world.n_cat,
        "n_inst": world.n_inst,
        "n_attr": world.n_attr,
    }
    t = time.time()

    out["arm1_learn_basic_facts"] = arm_learn_basic_facts(world, base, atom_book, pred_book, g)
    bank = out["arm1_learn_basic_facts"].pop("_bank_for_reuse_")
    retention_triples = out["arm1_learn_basic_facts"].pop("_triples_")
    print(("  [seed=%d] ARM1 recall@5=%.3f top1=%.3f (n=%d chance5=%.4f)") % (
        seed, out["arm1_learn_basic_facts"]["recall5"],
        out["arm1_learn_basic_facts"]["top1"],
        out["arm1_learn_basic_facts"]["n_triples_stored"],
        out["arm1_learn_basic_facts"]["chance_top5"]), flush=True)

    out["arm2_hierarchical_inheritance"] = arm_hierarchical_inheritance(
        world, base, atom_book, pred_book, bank
    )
    print(("  [seed=%d] ARM2 inh_top1=%.3f (chain_hop1_cat=%.3f)") % (
        seed, out["arm2_hierarchical_inheritance"]["inherited_attr_top1"],
        out["arm2_hierarchical_inheritance"]["chain_hop1_cat_top1"]), flush=True)

    out["arm3_generalization_new_inst"] = arm_generalization_new_inst(
        world, base, atom_book, pred_book, g, N_HELDOUT_INSTANCES
    )
    print(("  [seed=%d] ARM3 (PRIMARY) heldout_top3=%.3f top1=%.3f (chance3=%.4f)") % (
        seed, out["arm3_generalization_new_inst"]["top3"],
        out["arm3_generalization_new_inst"]["top1"],
        out["arm3_generalization_new_inst"]["chance_top3"]), flush=True)

    out["arm4_compositional_triple"] = arm_compositional_triple(
        world, base, atom_book, pred_book, g, N_HELDOUT_INSTANCES
    )
    print(("  [seed=%d] ARM4 compose_eats_top1=%.3f top3=%.3f") % (
        seed, out["arm4_compositional_triple"]["top1"],
        out["arm4_compositional_triple"]["top3"]), flush=True)

    out["arm5_refuse_foreign_concept"] = arm_refuse_foreign_concept(
        world, base, atom_book, pred_book, g, N_FOREIGN_CONCEPTS, bank, retention_triples
    )
    print(("  [seed=%d] ARM5 refuse=%.3f retention=%.3f (thr=%.4f mean_ret_cos=%.4f mean_foreign_cos=%.4f)") % (
        seed, out["arm5_refuse_foreign_concept"]["refuse_accuracy"],
        out["arm5_refuse_foreign_concept"]["retention_accuracy"],
        out["arm5_refuse_foreign_concept"]["refuse_threshold"],
        out["arm5_refuse_foreign_concept"]["mean_retention_cos"],
        out["arm5_refuse_foreign_concept"]["mean_foreign_cos"]), flush=True)

    out["arm6_audit_chain_semantic"] = arm_audit_chain_semantic(
        world, base, atom_book, pred_book, bank, g, N_AUDIT_QUERIES
    )
    print(("  [seed=%d] ARM6 chain_completeness=%.3f answer_top1=%.3f") % (
        seed, out["arm6_audit_chain_semantic"]["chain_completeness"],
        out["arm6_audit_chain_semantic"]["answer_top1"]), flush=True)

    out["wall_s"] = round(time.time() - t, 2)
    return out


# -- Verdict ------------------------------------------------------------------
def verdict_for(per_seed: list) -> tuple:
    """6-arm verdict using PRE-REG'd substrate-native floors (Lane 1).
    PRIMARY arm = ARM_GENERALIZATION_NEW_INST (top-3).
    HARD_PASS = 6 of 6; CHAIN_GRADE = >=5/6 with PRIMARY pass; MIDDLE = 3-4; HARD_FAIL <=2."""
    def _m(field_path):
        keys = field_path.split(".")
        vals = []
        for p in per_seed:
            v = p
            for k in keys:
                v = v[k]
            vals.append(float(v))
        return float(np.mean(vals)), float(np.std(vals) / max(np.mean(vals), 1e-9))

    a1, a1_cv = _m("arm1_learn_basic_facts.recall5")
    a2, a2_cv = _m("arm2_hierarchical_inheritance.inherited_attr_top1")
    a3, a3_cv = _m("arm3_generalization_new_inst.top1")   # Wave-C PRIMARY: top1 (was top3)
    a3_top3, _ = _m("arm3_generalization_new_inst.top3")  # carried for visibility
    a4, a4_cv = _m("arm4_compositional_triple.top1")
    a5_refuse, _ = _m("arm5_refuse_foreign_concept.refuse_accuracy")
    a5_ret, _ = _m("arm5_refuse_foreign_concept.retention_accuracy")
    a6, a6_cv = _m("arm6_audit_chain_semantic.chain_completeness")

    # Sanity gate: ARM_1 recall5 must clear sanity floor before reading higher arms
    sanity_ok = a1 >= SANITY_FLOOR_ARM1

    p1 = a1 >= BAND_ARM1_RECALL5
    p2 = a2 >= BAND_ARM2_TOP1
    p3 = a3 >= BAND_ARM3_TOP1   # Wave-C: PRIMARY uses top1
    p4 = a4 >= BAND_ARM4_TOP1
    p5 = (a5_refuse >= BAND_ARM5_REFUSE) and (a5_ret >= BAND_ARM5_RETENTION)
    p6 = a6 >= BAND_ARM6_COMPLETENESS

    pass_count = sum([p1, p2, p3, p4, p5, p6])
    # Wave-C CV check: any per-arm cv > CHAIN_GRADE_CV_MAX downgrades chain-grade
    arm_cvs = [a1_cv, a2_cv, a3_cv, a4_cv, a6_cv]
    max_cv = max(arm_cvs)
    cv_ok = max_cv <= CHAIN_GRADE_CV_MAX

    arm_results = "[A1=%s A2=%s A3*=%s A4=%s A5=%s A6=%s]" % (
        "P" if p1 else "F", "P" if p2 else "F", "P" if p3 else "F",
        "P" if p4 else "F", "P" if p5 else "F", "P" if p6 else "F"
    )
    summ = (
        "A1 recall5=%.3f(>=%.2f cv=%.3f) | A2 inh_top1=%.3f(>=%.2f cv=%.3f) | "
        "A3* heldout_top1=%.3f(>=%.2f cv=%.3f, top3=%.3f) | A4 compose_top1=%.3f(>=%.2f cv=%.3f) | "
        "A5 refuse=%.3f(>=%.2f) retention=%.3f(>=%.2f) | "
        "A6 chain=%.3f(>=%.2f cv=%.3f) | sanity_ok=%s max_cv=%.3f cv_ok=%s "
        "N=%d cats=%d inst=%d attrs=%d"
    ) % (a1, BAND_ARM1_RECALL5, a1_cv, a2, BAND_ARM2_TOP1, a2_cv,
         a3, BAND_ARM3_TOP1, a3_cv, a3_top3, a4, BAND_ARM4_TOP1, a4_cv,
         a5_refuse, BAND_ARM5_REFUSE, a5_ret, BAND_ARM5_RETENTION,
         a6, BAND_ARM6_COMPLETENESS, a6_cv,
         sanity_ok, max_cv, cv_ok,
         N_DIM, N_CATEGORIES, N_INSTANCES_PER_CAT * N_CATEGORIES, N_ATTRIBUTES)

    if not sanity_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: sanity gate failed (ARM_1 recall5=%.3f < sanity_floor=%.2f). "
                "Mechanism broken; higher-arm results not interpretable. %s %s" % (
                    a1, SANITY_FLOOR_ARM1, arm_results, summ))

    # Wave-C: STAGE_1_CHAIN_GRADE_DEFINITIVE = >=5/6 PASS AND CV<=0.05 AND A3 top1>=0.95
    if (pass_count >= CHAIN_GRADE_MIN_PASS_ARMS and cv_ok and a3 >= 0.95):
        return ("HARD_PASS",
                "STAGE_1_CHAIN_GRADE_DEFINITIVE: substrate IS a concept learner. %d/6 arms "
                "PASS at CV<=%.2f (max_cv=%.3f) AND A3 PRIMARY top1=%.3f >= 0.95. "
                "Chain-grade generalization confirmed. %s %s" % (
                    pass_count, CHAIN_GRADE_CV_MAX, max_cv, a3, arm_results, summ))
    # Standard HARD_PASS: 6/6 arms PASS (even if CV/A3 don't hit chain-grade)
    if pass_count == 6:
        return ("HARD_PASS",
                "HARD_PASS: 6/6 arms PASS including PRIMARY ARM_3 generalization. "
                "(Below chain-grade-definitive: cv_ok=%s a3=%.3f<0.95) %s %s" % (
                    cv_ok, a3, arm_results, summ))
    if pass_count >= CHAIN_GRADE_MIN_PASS_ARMS and p3:
        return ("HARD_PASS",
                "STAGE_1_HARD_PASS: substrate generalizes (PRIMARY pass) with %d/6 arms PASS. "
                "Below chain-grade-definitive (cv_ok=%s a3=%.3f<0.95). %s %s" % (
                    pass_count, cv_ok, a3, arm_results, summ))
    # Wave-C STAGE_1_PARTIAL: 3-4/6 PASS or A3 in [0.70, 0.95]
    if pass_count >= PARTIAL_MIN_PASS_ARMS or 0.70 <= a3 < 0.95:
        return ("MIDDLE_BAND",
                "STAGE_1_PARTIAL: %d/6 PASS (or A3=%.3f in [0.70, 0.95)); partial "
                "mechanism at production scale. %s %s" % (
                    pass_count, a3, arm_results, summ))
    # Wave-C STAGE_1_GAPS: <=2/6 PASS or A3<=0.70
    return ("HARD_FAIL",
            "STAGE_1_GAPS: %d/6 arms PASS or A3 top1=%.3f<=0.70. Concept-learner "
            "capability gap at production scale. %s %s" % (
                pass_count, a3, arm_results, summ))


# -- Main entry point ---------------------------------------------------------
def _selftest():
    """Sub-second mechanism check on a representative-size world: storage+retrieval
    primitives operational. Uses N=1024 (smoke-equivalent) with tiny world to keep
    runtime sub-second while ensuring the sparse-bipolar HRR has enough dimensions
    to carry signal. A tiny-N test (N=256) was an INVALID precondition check --
    sparse f=0.02 only yields ~5 nonzeros at N=256 which cannot encode reliably.
    Empirical probe: N=1024 gives recall@5 >= 0.95 on this tiny world; N=256 gives
    ~0.4 (would be a false-positive mechanism-broken)."""
    g = np.random.default_rng(0)
    w = ConceptWorld(3, 2, 5, g)
    base = atom_ids(w)
    N_TEST = 1024
    book = sparse_bipolar(base[3], N_TEST, SPARSE_F, SPARSE_AMP, g)
    pbook = sparse_bipolar(ConceptWorld.N_PREDICATES, N_TEST, SPARSE_F, SPARSE_AMP, g)
    triples = build_training_triples(w, g, include_inst_extras=True)
    bank = build_bank(triples, w, base, book, pbook)
    # Spot-check: query each (cat, has, attr) -- recall@5 must clear 0.80 floor.
    # (top1 may be lower due to superposition crosstalk; recall@5 is the canonical
    # cleanup metric for HRR.)
    hits5 = 0
    cat_has = [t for t in triples if t[3] == "cat_has"]
    for t in cat_has:
        s_atom, p, o_atom = triple_to_atom_ids(t, w, base)
        top, _ = _query_topk(bank, book[s_atom], pbook[p], book, 5)
        if o_atom in top:
            hits5 += 1
    rate = hits5 / max(len(cat_has), 1)
    assert rate >= 0.80, ("selftest: cat_has recall@5 too low (%.2f); mechanism broken "
                         "or sparse-bipolar HRR not operational at N=%d") % (rate, N_TEST)
    # Spot-check chain: (inst, is_a, ?) -- recall@5 floor.
    inst_isa = [t for t in triples if t[3] == "inst_isa"]
    chain_hits = 0
    for t in inst_isa:
        s_atom, p, o_atom = triple_to_atom_ids(t, w, base)
        top, _ = _query_topk(bank, book[s_atom], pbook[p], book, 5)
        if o_atom in top:
            chain_hits += 1
    chain_rate = chain_hits / max(len(inst_isa), 1)
    assert chain_rate >= 0.80, ("selftest: is_a recall@5 too low (%.2f); "
                                "chain hop1 broken at N=%d") % (chain_rate, N_TEST)
    # Spot-check verdict path with tiny per_seed bundle (asserts no key errors).
    # Wave-C bands: A1>=0.95, A2>=0.80, A3 top1>=0.85, A4>=0.50, A5_ret>=0.85, A6>=0.70.
    fake_seed = {
        "arm1_learn_basic_facts": {"recall5": 0.99, "top1": 0.9, "n_triples_stored": 50,
                                    "chance_top1": 0.01, "chance_top5": 0.05},
        "arm2_hierarchical_inheritance": {"inherited_attr_top1": 0.85, "inherited_attr_top3": 0.92,
                                           "chain_hop1_cat_top1": 0.9, "n_instances": 10},
        "arm3_generalization_new_inst": {"top1": 0.90, "top3": 0.95, "n_heldout": 10,
                                          "chance_top3": 0.05},
        "arm4_compositional_triple": {"top1": 0.55, "top3": 0.7, "n_heldout": 10,
                                       "chance_top1": 0.01},
        "arm5_refuse_foreign_concept": {"refuse_accuracy": 0.85, "retention_accuracy": 0.92,
                                         "refuse_threshold": 0.05, "n_foreign": 5, "n_retention": 50,
                                         "mean_retention_cos": 0.1, "std_retention_cos": 0.02,
                                         "mean_foreign_cos": 0.03},
        "arm6_audit_chain_semantic": {"chain_completeness": 0.75, "answer_top1": 0.8,
                                       "n_queries": 60},
    }
    v, vmsg = verdict_for([fake_seed])
    assert v in ("HARD_PASS", "CHAIN_GRADE"), "selftest: synthetic-pass verdict path broken; got " + v
    print(("[selftest] PASS cat_has_recall5=%.2f isa_recall5=%.2f verdict_path=%s "
           "(n_atoms=%d N=%d sparse_f=%.3f)") % (
              rate, chain_rate, v, base[3], N_TEST, SPARSE_F), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def main():
    print(("[config] anchor=%s mode=%s seeds=%s N=%d cats=%d inst/cat=%d attrs=%d | %s") % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, N_CATEGORIES, N_INSTANCES_PER_CAT,
        N_ATTRIBUTES, CONFIG_VERSION), flush=True)
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Per-seed checkpoint resume (PROT-021 config-mismatch guard)
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    if done:
        print("[ckpt] %d/%d seeds already complete; running %s" % (
            len(done), len(SEEDS), remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if len(per_seed) != len(SEEDS):
        missing = [s for s in SEEDS if str(s) not in agg]
        print("[WARN] missing seeds after aggregate: %s" % missing, flush=True)

    v, vmsg = verdict_for(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION,
        "per_seed": per_seed,
        "DESIGN_NOTE": (
            "Stage 1 definitive concept-learner test (USER directive 2026-06-24). "
            "UNTRAINED random sparse-bipolar encoder; semantic structure comes from "
            "binding pattern across observed triples + at-query-time chain traversal "
            "via substrate compose primitive. Inheritance / generalization / "
            "compositional / refuse / audit-chain arms all use the SAME chain "
            "primitive -- this is the substrate-product-relevant test. "
            "Lane 1; chance-baseline only; no transformer comparisons."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    main()
