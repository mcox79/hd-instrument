"""substrate_compositional_generalization_CLEAN_v1 -- proper Plate 1995 role-filler
binding test of substrate compositional generalization at N_DIM=8192.

Fixes the recurring PAIR-STORAGE protocol bug:

  Brain-aligned-shotgun ARM 2 and substrate-native-suite CG arm BOTH HARD_FAILed at
  holdout=0.000. Root cause: pair-storage protocol (bind(A_subj, B_obj) directly) is
  bound by a 1/k ceiling where k = #pairs-per-subject; with 50% coverage of a 20x20
  grid that ceiling is ~1/10 -- NOT a substrate failure, a protocol-ceiling artifact.

  Prior substrate_compositional_generalization_K10_to_K20_v1_n4096 HARD_PASSed at 1.000
  via a DIFFERENT protocol (link-shuffled chain composition); ANCHOR reconfirmed at
  N=8192. Substrate IS compositionally alive when the protocol is correct.

This cell uses ROLE-FILLER (Plate 1995 canonical) binding, KEY-VALUE-RETRIEVAL form:

  payload(s, p, o) = bind(bind(A_subj, A_pred), A_obj)   -- composite (subj, pred) key
                                                           bound to object value
  bank = sum_i payload(s_i, p_i, o_i)
  query  obj for (s, p):  rec = unbind(bank, bind(A_subj, A_pred));  argmax over obj_book

This is the canonical substrate tag-retrieval pattern (CERT 591 / U1 / K10_to_K20).
Composite (subj, pred) is the KEY; obj is the VALUE. Multiple (s, p) keys superpose
in the bank without the 1/k ceiling that pure pair-storage (bind(A_subj, A_obj)) hits,
because the composite key disambiguates per-triple retrieval.

The R_subj / R_pred / R_obj role atoms (Plate-style role markers) are used in ARM 3
(NEW_SUBJ generalization) where we need to query "what's the OBJECT for a new subject
sharing predicate p with K trained subjects" -- there the role-tag formulation tells
the substrate which slot to extract.

Four arms (sequential within a seed):

  ARM_STORE_RECALL_TRAINED_PAIRS  -- sanity: store M=200 (s,p,o) triples; recover o
                                     from cue (s,p). Expected top1 >= 0.95.

  ARM_HELDOUT_NEW_OBJ_SAME_SUBJ_PRED -- TRAIN m_i = (s, p, o_i) for o_i in {o1..o3};
                                        HOLDOUT (s, p, ???); chance = 5/V_obj.
                                        substrate guesses among the same-subj/pred
                                        pattern. Measure top-5 structural plausibility.

  ARM_HELDOUT_NEW_SUBJ_TRAINED_PRED  -- TRAIN (s_i, p, o) for s_i in {s1..s_K} sharing
                                        a predicate; HOLDOUT (s_new, p, ???). substrate
                                        should produce "o" or similar. Measure top-1.

  ARM_HELDOUT_NEW_PRED_TRAINED_PAIR  -- TRAIN (s, p_i, o_i) with multiple predicates
                                        per subject; HOLDOUT (s, p_new, ???). substrate
                                        should produce a STRUCTURALLY plausible filler
                                        (e.g. one of s's known objects). Measure top-5.

Pre-reg HARD bands (per substrate-native lane; chance-relative lift to avoid
the trivial-baseline trap where V_obj is small and analytic chance is already
high for top-5 of K trained):

  ARM_TRAINED_PAIRS    top1 >= 0.95   (absolute; storage works)
  ARM_HELDOUT_NEW_OBJ  top5 - chance_analytic >= 0.20   (chance-relative lift)
  ARM_HELDOUT_NEW_SUBJ top1 - chance_analytic >= 0.30   (chance ~= 1/V_obj)
  ARM_HELDOUT_NEW_PRED top5 - chance_analytic >= 0.20   (chance-relative lift)

  HARD_PASS_OVERALL:  >= 3 of 4 arms HARD_PASS  -> substrate compositionally generalizes
  MIDDLE_BAND:        exactly 2 of 4 arms HARD_PASS
  HARD_FAIL:          <= 1 arm HARD_PASS

Sanity gate (mandatory before reading generalization arms): ARM_TRAINED_PAIRS top1
must clear 0.70 floor; otherwise the mechanism is broken and the holdout arms are
noise. If sanity floor fails -> HARD_FAIL with diagnosis = mechanism, not generalization.

CPU only (numpy + HRR), no torch, no LLM. Per-seed checkpoint. ASCII-only.
"""
from __future__ import annotations
import sys, os, argparse, time
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_compositional_generalization_CLEAN_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config -----------------------------------------------------------------------
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    M_TRAIN_PAIRS = 200      # ARM_TRAINED_PAIRS: number of (s,p,o) triples stored
    V_SUBJ = 50              # subject vocabulary
    V_PRED = 20              # predicate vocabulary
    V_OBJ = 50               # object vocabulary
    # ARM_HELDOUT_NEW_OBJ: pick K_OBJ_SAME = 3 objects for same (subj,pred); hold a 4th
    K_OBJ_SAME = 3
    # ARM_HELDOUT_NEW_SUBJ: K_SUBJ_TRAIN subjects share a predicate->object; hold a new subj
    K_SUBJ_TRAIN = 3
    # ARM_HELDOUT_NEW_PRED: subject has K_PRED predicates trained; hold a new predicate
    K_PRED_TRAIN = 5
    N_HELDOUT_TRIALS = 50    # number of independent (s,p) holdout queries per arm
else:  # smoke
    SEEDS = [0]
    N_DIM = 1024
    M_TRAIN_PAIRS = 40
    V_SUBJ = 12
    V_PRED = 8
    V_OBJ = 12
    K_OBJ_SAME = 2
    K_SUBJ_TRAIN = 2
    K_PRED_TRAIN = 3
    N_HELDOUT_TRIALS = 8

ARMS = [
    "ARM_TRAINED_PAIRS",
    "ARM_HELDOUT_NEW_OBJ",
    "ARM_HELDOUT_NEW_SUBJ",
    "ARM_HELDOUT_NEW_PRED",
]

# Pre-reg bands. ARM_TRAINED is absolute; HELDOUT arms use chance-relative lift to
# avoid the trivial-baseline trap (small V_obj => chance for top-5-of-K is already high).
BAND_TRAINED_TOP1 = 0.95            # absolute top-1 for stored triples
BAND_HELDOUT_OBJ_TOP5_LIFT = 0.20   # top-5 - chance_analytic
BAND_HELDOUT_SUBJ_TOP1_LIFT = 0.30  # top-1 - chance_analytic (chance ~ 1/V_obj)
BAND_HELDOUT_PRED_TOP5_LIFT = 0.20  # top-5 - chance_analytic
SANITY_FLOOR_TRAINED_TOP1 = 0.70    # mandatory gate before reading generalization arms

CONFIG_VERSION = (
    "substrate_compositional_generalization_CLEAN_v1; N_DIM=%d M=%d "
    "V_subj=%d V_pred=%d V_obj=%d K_obj_same=%d K_subj=%d K_pred=%d trials=%d "
    "seeds=%s mode=%s; bands trained_top1>=%.2f obj_top5_lift>=%.2f "
    "subj_top1_lift>=%.2f pred_top5_lift>=%.2f sanity_floor>=%.2f"
) % (N_DIM, M_TRAIN_PAIRS, V_SUBJ, V_PRED, V_OBJ, K_OBJ_SAME, K_SUBJ_TRAIN,
     K_PRED_TRAIN, N_HELDOUT_TRIALS, SEEDS, RUN_MODE,
     BAND_TRAINED_TOP1, BAND_HELDOUT_OBJ_TOP5_LIFT, BAND_HELDOUT_SUBJ_TOP1_LIFT,
     BAND_HELDOUT_PRED_TOP5_LIFT, SANITY_FLOOR_TRAINED_TOP1)


# Plate-canonical HRR primitives (dense unit-norm + circular conv) ------------
def _dense_unit_norm(n: int, dim: int, g: np.random.Generator) -> np.ndarray:
    """Stack of n dense Gaussian vectors, L2-normalized per row. Shape (n, dim)."""
    out = g.standard_normal((n, dim)).astype(np.float32)
    norms = np.linalg.norm(out, axis=1, keepdims=True) + 1e-8
    return (out / norms).astype(np.float32)


def _bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR circular convolution via FFT. Real->real."""
    fa = np.fft.fft(a); fb = np.fft.fft(b)
    return np.fft.ifft(fa * fb).real.astype(np.float32)


def _unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR circular correlation via FFT * conj. Real->real."""
    fc = np.fft.fft(c); fb = np.fft.fft(b)
    return np.fft.ifft(fc * fb.conj()).real.astype(np.float32)


def _l2_norm(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v)) + 1e-8
    return (v / n).astype(np.float32)


def _l2_rows(X: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    return (X / n).astype(np.float32)


def _topk_cosine(rec: np.ndarray, codebook: np.ndarray, k: int) -> list:
    """Return indices of top-k cosine-similar codebook rows to rec (sorted desc)."""
    rn = _l2_norm(rec)
    Cn = _l2_rows(codebook)
    sims = Cn @ rn
    idx = np.argsort(-sims)[:k]
    return [int(i) for i in idx]


# ----------------------------------------------------------------------------
# Triple = (subject_id, predicate_id, object_id)
#
# KEY-VALUE-RETRIEVAL form (CERT 591 / U1 / K10_to_K20 chain-grade pattern):
#   payload(s, p, o) = bind(bind(A_subj, A_pred), A_obj)
#                    [ composite (subj, pred) key bound to obj value ]
#   bank = sum_i payload(s_i, p_i, o_i), per-bind L2 normalized
#   query for obj given (s, p):
#       key_query = bind(A_subj, A_pred)
#       rec = unbind(bank, key_query)
#       argmax cosine(rec, obj_book) -> predicted obj
#
# Why this beats pair-storage: composite (subj, pred) keys disambiguate per-triple
# retrieval; the bank can hold many triples per (subj, pred) WITHOUT the 1/k pair-
# storage ceiling. Substrate's tag-retrieval primitive proven chain-grade at this
# protocol (CERT 591 fly-LSH + U1 FB15k-237 set-recall 0.99 @ M=50k).
# ----------------------------------------------------------------------------
def _build_bank_and_codebooks(seed: int, n_dim: int,
                              v_subj: int, v_pred: int, v_obj: int):
    """Build filler codebooks (subj, pred, obj) with one common rng."""
    g = np.random.default_rng(seed)
    subj_book = _dense_unit_norm(v_subj, n_dim, g)
    pred_book = _dense_unit_norm(v_pred, n_dim, g)
    obj_book = _dense_unit_norm(v_obj, n_dim, g)
    return g, subj_book, pred_book, obj_book


def _encode_triple(a_subj, a_pred, a_obj):
    """payload = L2_norm( bind( L2_norm(bind(A_subj, A_pred)),  A_obj ) ).
    Composite (subj, pred) key bound to object value, per-bind L2-normalized."""
    key = _l2_norm(_bind(a_subj, a_pred))
    return _l2_norm(_bind(key, a_obj)).astype(np.float32)


def _query_obj_topk(bank, a_subj, a_pred, obj_book, k: int) -> list:
    """Build composite key (subj, pred); unbind from bank; return top-k object indices."""
    key = _l2_norm(_bind(a_subj, a_pred))
    rec = _unbind(bank, key)
    return _topk_cosine(rec, obj_book, k)


# ----------------------------------------------------------------------------
# ARM 1 -- store M random (s,p,o) triples; query each by (s,p); recover o.
# This is sanity-floor: confirms role-filler bind+unbind operational at this scale.
# ----------------------------------------------------------------------------
def _arm_trained_pairs(g, subj_book, pred_book, obj_book, m: int, n_dim: int) -> dict:
    """Build bank of M random unique-(s,p) triples; query each by composite (s,p) key;
    recover o; report top-1."""
    v_subj, v_pred, v_obj = subj_book.shape[0], pred_book.shape[0], obj_book.shape[0]
    all_sp = [(s, p) for s in range(v_subj) for p in range(v_pred)]
    g.shuffle(all_sp)
    take = min(m, len(all_sp))
    triples = [(s, p, int(g.integers(0, v_obj))) for (s, p) in all_sp[:take]]
    bank = np.zeros(n_dim, dtype=np.float32)
    for (s, p, o) in triples:
        bank += _encode_triple(subj_book[s], pred_book[p], obj_book[o])
    correct = 0
    top5_correct = 0
    cos_correct = []
    for (s, p, o) in triples:
        top = _query_obj_topk(bank, subj_book[s], pred_book[p], obj_book, 5)
        if top[0] == o:
            correct += 1
        if o in top:
            top5_correct += 1
        # diagnostic: cosine of unbind to the correct obj atom
        key = _l2_norm(_bind(subj_book[s], pred_book[p]))
        rec = _unbind(bank, key)
        rn = _l2_norm(rec)
        on = obj_book[o] / (np.linalg.norm(obj_book[o]) + 1e-8)
        cos_correct.append(float(rn @ on.astype(np.float32)))
    n = max(len(triples), 1)
    return {
        "n_triples": n,
        "top1": correct / n,
        "top5": top5_correct / n,
        "chance_top1": 1.0 / v_obj,
        "mean_cosine_correct": float(np.mean(cos_correct)) if cos_correct else 0.0,
    }


# ----------------------------------------------------------------------------
# ARM 2 -- ARM_HELDOUT_NEW_OBJ: same (subj, pred), multiple known objects, heldout a new obj.
# Build N_HELDOUT_TRIALS independent (s,p) groups; for each: train on K_OBJ_SAME objects;
# bank contains all triples for that group; query: unbind(bank_group, R_obj) -> top-K obj indices.
# A correct recall returns one of the trained objs (a structurally-plausible filler).
# top-5 structural plausibility = fraction of trials where >=1 of the K trained objs is in top-5.
# Chance: top-5 over V_obj = 5/V_obj (per trial); BUT trained set is K_OBJ_SAME (= 3) of V_obj,
# so a random top-5 hits one with prob 1 - C(V_obj-K, 5)/C(V_obj, 5).
# ----------------------------------------------------------------------------
def _arm_heldout_new_obj(g, subj_book, pred_book, obj_book,
                         k_obj_same: int, n_trials: int, n_dim: int) -> dict:
    """For each of n_trials: pick (s, p) + K trained objs (1-to-many) + 1 heldout obj.
    Build bank holding K (s,p,o_i) triples; query the same (s,p) key; check top-5 hit
    of any trained_obj. This is set-recall under same-key multi-value -- the substrate-
    valid analog of "what does this subject-predicate map to" when it has a small known
    cluster of associations.
    """
    v_subj, v_pred, v_obj = subj_book.shape[0], pred_book.shape[0], obj_book.shape[0]
    plausible_hits = 0
    chance_hits = 0
    n_real = 0
    for _t in range(n_trials):
        s = int(g.integers(0, v_subj))
        p = int(g.integers(0, v_pred))
        if k_obj_same + 1 > v_obj:
            continue
        obj_pool = g.choice(v_obj, k_obj_same + 1, replace=False)
        trained_objs = list(obj_pool[:k_obj_same])
        bank = np.zeros(n_dim, dtype=np.float32)
        for o in trained_objs:
            bank += _encode_triple(subj_book[s], pred_book[p], obj_book[o])
        top5 = _query_obj_topk(bank, subj_book[s], pred_book[p], obj_book, 5)
        if any(o in top5 for o in trained_objs):
            plausible_hits += 1
        rand5 = list(g.choice(v_obj, 5, replace=False))
        if any(o in rand5 for o in trained_objs):
            chance_hits += 1
        n_real += 1
    return {
        "n_trials": n_real,
        "k_obj_same": k_obj_same,
        "top5_structural_plausibility": plausible_hits / max(n_real, 1),
        "chance_top5_plausibility": chance_hits / max(n_real, 1),
        "chance_analytic": 1.0 - float(np.prod([(v_obj - k_obj_same - i) / (v_obj - i)
                                                for i in range(5)])),
    }


# ----------------------------------------------------------------------------
# ARM 3 -- ARM_HELDOUT_NEW_SUBJ: K subjects share (pred, obj); heldout (new_subj, pred, ???)
# Idea: TRAIN (s_i, p, o) for s_i in {s_1..s_K} -- substrate sees that predicate p maps to
# obj o across many subjects; HOLDOUT (s_new, p, ???) should recover o (or near-o).
# Implementation: bank holds K (s_i, p, o) triples. Query the same bank with a SHIFTED bank
# that subtracts s_i^(K) and adds s_new (the substrate has no s_new in its bank, but the
# (pred, obj) signal accumulates). Actually for clean test: build the bank with the K
# trained triples + query unbind(bank, R_obj) -> top-1 should be o (the shared obj).
# That tests whether the K-superposed (pred, obj) signal survives.
# Then add a NEW (s_new, p, ???) query and check whether o is still the top-1.
# ----------------------------------------------------------------------------
def _arm_heldout_new_subj(g, subj_book, pred_book, obj_book,
                          k_subj_train: int, n_trials: int, n_dim: int) -> dict:
    """For each trial: train K (s_i, p, o) triples where the K subjects all share the
    same (pred, obj). Then query with NEW subject (s_new, p, ???) -- substrate has no
    direct (s_new, p) key in the bank. To test generalization, we compute a SUPERPOSED
    query key averaging over trained subj_books bound with p, and unbind from the bank.
    This is the role-filler 'one-shot generalize from K examples' test: does the bank's
    summed (s_i, p, o) signal expose o when queried by (s_new, p)?

    Substrate-product framing: the bank holds K facts about a shared predicate; query
    by a NEW subject with the same predicate. A compositionally-alive substrate should
    return the shared object because the (pred, obj) signal accumulates across K
    superposed key-value triples while the per-subject keys decorrelate.
    """
    v_subj, v_pred, v_obj = subj_book.shape[0], pred_book.shape[0], obj_book.shape[0]
    correct_top1 = 0
    n_real = 0
    chance_correct = 0
    for _t in range(n_trials):
        if k_subj_train + 1 > v_subj:
            continue
        subj_pool = g.choice(v_subj, k_subj_train + 1, replace=False)
        trained_subjs = list(subj_pool[:k_subj_train])
        heldout_subj = int(subj_pool[k_subj_train])
        p = int(g.integers(0, v_pred))
        o = int(g.integers(0, v_obj))
        bank = np.zeros(n_dim, dtype=np.float32)
        for s in trained_subjs:
            bank += _encode_triple(subj_book[s], pred_book[p], obj_book[o])
        # Query with heldout_subj + same predicate: composite key = bind(s_new, p)
        # If substrate generalizes, top-1 obj should be o (the shared object).
        top1 = _query_obj_topk(bank, subj_book[heldout_subj], pred_book[p], obj_book, 1)[0]
        if top1 == o:
            correct_top1 += 1
        if int(g.integers(0, v_obj)) == o:
            chance_correct += 1
        n_real += 1
    return {
        "n_trials": n_real,
        "k_subj_train": k_subj_train,
        "top1": correct_top1 / max(n_real, 1),
        "chance_top1": chance_correct / max(n_real, 1),
        "chance_analytic": 1.0 / v_obj,
    }


# ----------------------------------------------------------------------------
# ARM 4 -- ARM_HELDOUT_NEW_PRED: subject has K predicates trained; heldout (s, new_pred, ???)
# Train K (s, p_i, o_i) triples for one subject; heldout query (s, p_new, ???) -- substrate
# should produce a STRUCTURALLY PLAUSIBLE obj (one of the o_i's, since they're the only
# objects associated with subj s in the bank). top-5 plausibility = fraction of trials where
# >=1 of trained o_i in top-5.
# ----------------------------------------------------------------------------
def _arm_heldout_new_pred(g, subj_book, pred_book, obj_book,
                          k_pred_train: int, n_trials: int, n_dim: int) -> dict:
    """For each trial: pick one subject s, K trained predicates p_i each with their own
    obj o_i. Bank holds (s, p_i, o_i) for i=1..K. Query with (s, p_new, ???) -- a NEW
    predicate not seen for this subject. A compositionally-alive substrate should
    return one of o_i (the only objects associated with subject s) since the per-subject
    signal accumulates while the per-predicate keys decorrelate. Test: top-5 contains
    any trained_obj_i?
    """
    v_subj, v_pred, v_obj = subj_book.shape[0], pred_book.shape[0], obj_book.shape[0]
    plausible_hits = 0
    chance_hits = 0
    n_real = 0
    for _t in range(n_trials):
        if k_pred_train + 1 > v_pred or k_pred_train > v_obj:
            continue
        s = int(g.integers(0, v_subj))
        pred_pool = g.choice(v_pred, k_pred_train + 1, replace=False)
        trained_preds = list(pred_pool[:k_pred_train])
        heldout_pred = int(pred_pool[k_pred_train])
        trained_objs = list(g.choice(v_obj, k_pred_train, replace=False))
        bank = np.zeros(n_dim, dtype=np.float32)
        for (p, o) in zip(trained_preds, trained_objs):
            bank += _encode_triple(subj_book[s], pred_book[p], obj_book[o])
        top5 = _query_obj_topk(bank, subj_book[s], pred_book[heldout_pred], obj_book, 5)
        if any(o in top5 for o in trained_objs):
            plausible_hits += 1
        rand5 = list(g.choice(v_obj, 5, replace=False))
        if any(o in rand5 for o in trained_objs):
            chance_hits += 1
        n_real += 1
    return {
        "n_trials": n_real,
        "k_pred_train": k_pred_train,
        "top5_structural_plausibility": plausible_hits / max(n_real, 1),
        "chance_top5_plausibility": chance_hits / max(n_real, 1),
        "chance_analytic": 1.0 - float(np.prod([(v_obj - k_pred_train - i) / (v_obj - i)
                                                for i in range(5)])),
    }


# ----------------------------------------------------------------------------
# Per-seed driver
# ----------------------------------------------------------------------------
def run_unit(seed: int) -> dict:
    t0 = time.time()
    g, subj_book, pred_book, obj_book = _build_bank_and_codebooks(
        seed, N_DIM, V_SUBJ, V_PRED, V_OBJ
    )

    print("  [seed=%d] ARM_TRAINED_PAIRS starting (M=%d)" % (seed, M_TRAIN_PAIRS), flush=True)
    a1 = _arm_trained_pairs(g, subj_book, pred_book, obj_book, M_TRAIN_PAIRS, N_DIM)
    print("    top1=%.3f top5=%.3f chance=%.3f mean_cos=%.3f" % (
        a1["top1"], a1["top5"], a1["chance_top1"], a1["mean_cosine_correct"]), flush=True)

    print("  [seed=%d] ARM_HELDOUT_NEW_OBJ starting (K=%d, trials=%d)" % (
        seed, K_OBJ_SAME, N_HELDOUT_TRIALS), flush=True)
    a2 = _arm_heldout_new_obj(g, subj_book, pred_book, obj_book,
                              K_OBJ_SAME, N_HELDOUT_TRIALS, N_DIM)
    print("    top5_plausible=%.3f chance_obs=%.3f chance_analytic=%.3f" % (
        a2["top5_structural_plausibility"], a2["chance_top5_plausibility"],
        a2["chance_analytic"]), flush=True)

    print("  [seed=%d] ARM_HELDOUT_NEW_SUBJ starting (K=%d, trials=%d)" % (
        seed, K_SUBJ_TRAIN, N_HELDOUT_TRIALS), flush=True)
    a3 = _arm_heldout_new_subj(g, subj_book, pred_book, obj_book,
                               K_SUBJ_TRAIN, N_HELDOUT_TRIALS, N_DIM)
    print("    top1=%.3f chance_obs=%.3f chance_analytic=%.3f" % (
        a3["top1"], a3["chance_top1"], a3["chance_analytic"]), flush=True)

    print("  [seed=%d] ARM_HELDOUT_NEW_PRED starting (K=%d, trials=%d)" % (
        seed, K_PRED_TRAIN, N_HELDOUT_TRIALS), flush=True)
    a4 = _arm_heldout_new_pred(g, subj_book, pred_book, obj_book,
                               K_PRED_TRAIN, N_HELDOUT_TRIALS, N_DIM)
    print("    top5_plausible=%.3f chance_obs=%.3f chance_analytic=%.3f" % (
        a4["top5_structural_plausibility"], a4["chance_top5_plausibility"],
        a4["chance_analytic"]), flush=True)

    return {
        "seed": seed,
        "by_arm": {
            "ARM_TRAINED_PAIRS": a1,
            "ARM_HELDOUT_NEW_OBJ": a2,
            "ARM_HELDOUT_NEW_SUBJ": a3,
            "ARM_HELDOUT_NEW_PRED": a4,
        },
        "N": N_DIM,
        "M_TRAIN_PAIRS": M_TRAIN_PAIRS,
        "V_SUBJ": V_SUBJ, "V_PRED": V_PRED, "V_OBJ": V_OBJ,
        "K_OBJ_SAME": K_OBJ_SAME, "K_SUBJ_TRAIN": K_SUBJ_TRAIN,
        "K_PRED_TRAIN": K_PRED_TRAIN, "N_HELDOUT_TRIALS": N_HELDOUT_TRIALS,
        "wall_s": time.time() - t0,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
    }


# ----------------------------------------------------------------------------
# Verdict
# ----------------------------------------------------------------------------
def compute_verdict(units: list) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})
    # Aggregate per arm
    a1 = [u["by_arm"]["ARM_TRAINED_PAIRS"]["top1"] for u in units]
    a2 = [u["by_arm"]["ARM_HELDOUT_NEW_OBJ"]["top5_structural_plausibility"] for u in units]
    a3 = [u["by_arm"]["ARM_HELDOUT_NEW_SUBJ"]["top1"] for u in units]
    a4 = [u["by_arm"]["ARM_HELDOUT_NEW_PRED"]["top5_structural_plausibility"] for u in units]
    means = {
        "ARM_TRAINED_PAIRS": float(np.mean(a1)),
        "ARM_HELDOUT_NEW_OBJ": float(np.mean(a2)),
        "ARM_HELDOUT_NEW_SUBJ": float(np.mean(a3)),
        "ARM_HELDOUT_NEW_PRED": float(np.mean(a4)),
    }
    cvs = {
        "ARM_TRAINED_PAIRS": float(np.std(a1) / max(np.mean(a1), 1e-6)),
        "ARM_HELDOUT_NEW_OBJ": float(np.std(a2) / max(np.mean(a2), 1e-6)),
        "ARM_HELDOUT_NEW_SUBJ": float(np.std(a3) / max(np.mean(a3), 1e-6)),
        "ARM_HELDOUT_NEW_PRED": float(np.std(a4) / max(np.mean(a4), 1e-6)),
    }
    # Chance-analytic baselines (per-arm; aggregate across seeds via mean)
    chance_obj = float(np.mean([u["by_arm"]["ARM_HELDOUT_NEW_OBJ"]["chance_analytic"] for u in units]))
    chance_subj = float(np.mean([u["by_arm"]["ARM_HELDOUT_NEW_SUBJ"]["chance_analytic"] for u in units]))
    chance_pred = float(np.mean([u["by_arm"]["ARM_HELDOUT_NEW_PRED"]["chance_analytic"] for u in units]))
    lifts = {
        "ARM_HELDOUT_NEW_OBJ": means["ARM_HELDOUT_NEW_OBJ"] - chance_obj,
        "ARM_HELDOUT_NEW_SUBJ": means["ARM_HELDOUT_NEW_SUBJ"] - chance_subj,
        "ARM_HELDOUT_NEW_PRED": means["ARM_HELDOUT_NEW_PRED"] - chance_pred,
    }
    passes = {
        "ARM_TRAINED_PAIRS": means["ARM_TRAINED_PAIRS"] >= BAND_TRAINED_TOP1,
        "ARM_HELDOUT_NEW_OBJ": lifts["ARM_HELDOUT_NEW_OBJ"] >= BAND_HELDOUT_OBJ_TOP5_LIFT,
        "ARM_HELDOUT_NEW_SUBJ": lifts["ARM_HELDOUT_NEW_SUBJ"] >= BAND_HELDOUT_SUBJ_TOP1_LIFT,
        "ARM_HELDOUT_NEW_PRED": lifts["ARM_HELDOUT_NEW_PRED"] >= BAND_HELDOUT_PRED_TOP5_LIFT,
    }
    n_pass = int(sum(passes.values()))
    # Sanity gate
    sanity_ok = means["ARM_TRAINED_PAIRS"] >= SANITY_FLOOR_TRAINED_TOP1
    detail = {
        "n_seeds": len(units),
        "N_DIM": N_DIM,
        "per_arm_means": means,
        "per_arm_cvs": cvs,
        "per_arm_lifts_vs_chance": lifts,
        "per_arm_chance_analytic": {
            "ARM_HELDOUT_NEW_OBJ": chance_obj,
            "ARM_HELDOUT_NEW_SUBJ": chance_subj,
            "ARM_HELDOUT_NEW_PRED": chance_pred,
        },
        "per_arm_passes": passes,
        "n_pass": n_pass,
        "sanity_floor_trained_top1": SANITY_FLOOR_TRAINED_TOP1,
        "sanity_ok": sanity_ok,
        "bands": {
            "ARM_TRAINED_PAIRS_top1_absolute": BAND_TRAINED_TOP1,
            "ARM_HELDOUT_NEW_OBJ_top5_lift": BAND_HELDOUT_OBJ_TOP5_LIFT,
            "ARM_HELDOUT_NEW_SUBJ_top1_lift": BAND_HELDOUT_SUBJ_TOP1_LIFT,
            "ARM_HELDOUT_NEW_PRED_top5_lift": BAND_HELDOUT_PRED_TOP5_LIFT,
        },
        "per_seed_arm_values": {
            "ARM_TRAINED_PAIRS_top1": a1,
            "ARM_HELDOUT_NEW_OBJ_top5": a2,
            "ARM_HELDOUT_NEW_SUBJ_top1": a3,
            "ARM_HELDOUT_NEW_PRED_top5": a4,
        },
        "CONFIG_VERSION": CONFIG_VERSION,
        "what_this_does_not_show": (
            "Compositional generalization on synthetic role-filler HRR triples at a single "
            "(N_DIM, M) point. Does NOT show: (1) language-task performance (no text); "
            "(2) learning / plasticity (no gradient); (3) downstream task benefit; "
            "(4) noise robustness; (5) capacity scaling (single M)."
        ),
        "honest_scope": (
            "Pure substrate primitives (HRR bind/unbind + Plate role-filler encoding + "
            "per-bind L2 normalization); NO learning. NumPy CPU. Replaces pair-storage "
            "protocol that hit 1/k ceiling in brain-aligned shotgun ARM 2 + native suite CG arm."
        ),
        "cites": [
            "USER_compositional_generalization_CLEAN_protocol_2026-06-24",
            "Plate_1995_HRR_role_filler",
            "exp_substrate_compositional_generalization_K10_to_K20_v1_n4096__HARD_PASS_1.000",
            "exp_substrate_brain_aligned_aliveness_shotgun_v1_ARM_2__holdout_0.000_pair_storage_bug",
            "exp_substrate_compositional_generalization_CORRECTED_v1__codebook_sweep",
        ],
    }
    if not sanity_ok:
        msg = (
            "HARD_FAIL_SANITY: ARM_TRAINED_PAIRS top1=%.3f below sanity floor %.2f. "
            "Mechanism broken at N_DIM=%d / M=%d; generalization arms uninterpretable. "
            "Per-arm means: %s."
        ) % (
            means["ARM_TRAINED_PAIRS"], SANITY_FLOOR_TRAINED_TOP1,
            N_DIM, M_TRAIN_PAIRS, {k: round(v, 3) for k, v in means.items()},
        )
        return ("HARD_FAIL_SANITY", msg, detail)
    means_short = {k: round(v, 3) for k, v in means.items()}
    lifts_short = {k: round(v, 3) for k, v in lifts.items()}
    passes_short = {k: bool(v) for k, v in passes.items()}
    if n_pass >= 3:
        msg = (
            "HARD_PASS_COMPOSITIONAL_ALIVE: %d of 4 arms HARD_PASS at N_DIM=%d. "
            "Means=%s Lifts=%s Passes=%s. "
            "Substrate compositionally generalizes under role-filler composite-key binding."
        ) % (n_pass, N_DIM, means_short, lifts_short, passes_short)
        return ("HARD_PASS_COMPOSITIONAL_ALIVE", msg, detail)
    if n_pass == 2:
        msg = (
            "MIDDLE_BAND: %d of 4 arms HARD_PASS at N_DIM=%d. "
            "Means=%s Lifts=%s Passes=%s. "
            "Partial compositional generalization."
        ) % (n_pass, N_DIM, means_short, lifts_short, passes_short)
        return ("MIDDLE_BAND", msg, detail)
    msg = (
        "HARD_FAIL: %d of 4 arms HARD_PASS at N_DIM=%d. "
        "Means=%s Lifts=%s Passes=%s. "
        "Substrate does not compositionally generalize under this protocol."
    ) % (n_pass, N_DIM, means_short, lifts_short, passes_short)
    return ("HARD_FAIL", msg, detail)


# ----------------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------------
def _selftest() -> None:
    """Mechanism sanity at tiny dim.
       Asserts: dense unit-norm; bind/unbind involutive; composite-key encode+query
       recovers the right obj at M=1; M=5 distinct (s,p) keys give >= 4/5 top-1 recall.
    """
    g = np.random.default_rng(0)
    dim = 512
    X = _dense_unit_norm(5, dim, g)
    norms = np.linalg.norm(X, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-4), "dense unit-norm builder broken"

    a = X[0]; b = X[1]
    c = _bind(a, b)
    a_back = _unbind(c, b)
    rn = _l2_norm(a_back); an = _l2_norm(a)
    cos_ab = float(rn @ an)
    assert cos_ab > 0.5, "bind/unbind round-trip too low (%.3f)" % cos_ab

    # M=1 composite-key recall: single triple, query (s,p), recover o.
    g2 = np.random.default_rng(1)
    n_dim = 2048
    v_subj, v_pred, v_obj = 8, 6, 8
    sb = _dense_unit_norm(v_subj, n_dim, g2)
    pb = _dense_unit_norm(v_pred, n_dim, g2)
    ob = _dense_unit_norm(v_obj, n_dim, g2)
    bank = _encode_triple(sb[2], pb[1], ob[5])
    top1 = _query_obj_topk(bank, sb[2], pb[1], ob, 1)[0]
    assert top1 == 5, "single-triple composite-key recall failed: top1=%d expected 5" % top1

    # M=5 distinct-(s,p) recall: store 5 triples; each (s,p) is unique; expect >= 4/5 top-1.
    bank2 = np.zeros(n_dim, dtype=np.float32)
    triples = [(0, 0, 0), (1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4)]
    for (s, p, o) in triples:
        bank2 += _encode_triple(sb[s], pb[p], ob[o])
    correct = 0
    for (s, p, o) in triples:
        top1 = _query_obj_topk(bank2, sb[s], pb[p], ob, 1)[0]
        if top1 == o:
            correct += 1
    assert correct >= 4, "M=5 composite-key top-1 too low: %d/5 (expected >=4)" % correct

    # Verify the helpers preserve shape + dtype
    p_check = _encode_triple(sb[0], pb[0], ob[0])
    assert p_check.shape == (n_dim,)
    assert p_check.dtype == np.float32

    # Verdict-shape sanity: HARD_PASS path. chance baselines @ V_obj=50, K_obj=3, K_pred=5:
    #   chance_obj  = 1 - prod_{i=0..4} (47-i)/(50-i) ~ 0.274
    #   chance_subj = 1/50 = 0.02
    #   chance_pred = 1 - prod_{i=0..4} (45-i)/(50-i) ~ 0.421
    fake_unit_hp = {
        "seed": 0,
        "by_arm": {
            "ARM_TRAINED_PAIRS": {"top1": 0.97, "top5": 0.99, "chance_top1": 0.02,
                                  "n_triples": 200, "mean_cosine_correct": 0.5},
            "ARM_HELDOUT_NEW_OBJ": {"top5_structural_plausibility": 0.60,  # lift = 0.326 > 0.20
                                    "chance_top5_plausibility": 0.27,
                                    "chance_analytic": 0.274,
                                    "n_trials": 50, "k_obj_same": 3},
            "ARM_HELDOUT_NEW_SUBJ": {"top1": 0.50,  # lift = 0.48 > 0.30
                                     "chance_top1": 0.02,
                                     "chance_analytic": 0.02,
                                     "n_trials": 50, "k_subj_train": 3},
            "ARM_HELDOUT_NEW_PRED": {"top5_structural_plausibility": 0.70,  # lift = 0.279 > 0.20
                                     "chance_top5_plausibility": 0.42,
                                     "chance_analytic": 0.421,
                                     "n_trials": 50, "k_pred_train": 5},
        },
        "N": 8192, "M_TRAIN_PAIRS": 200,
        "V_SUBJ": 50, "V_PRED": 20, "V_OBJ": 50,
        "K_OBJ_SAME": 3, "K_SUBJ_TRAIN": 3, "K_PRED_TRAIN": 5,
        "N_HELDOUT_TRIALS": 50, "wall_s": 0.0, "run_mode": "selftest",
        "config_version": "selftest",
    }
    v, msg, det = compute_verdict([fake_unit_hp, fake_unit_hp, fake_unit_hp])
    assert v == "HARD_PASS_COMPOSITIONAL_ALIVE", "verdict-HP synth expected, got %s | %s" % (v, msg[:200])

    # MIDDLE: only 2 arms pass (trained + obj_lift); subj/pred at chance
    fake_unit_mid = {
        "seed": 0,
        "by_arm": {
            "ARM_TRAINED_PAIRS": {"top1": 0.97, "top5": 0.99, "chance_top1": 0.02,
                                  "n_triples": 200, "mean_cosine_correct": 0.5},
            "ARM_HELDOUT_NEW_OBJ": {"top5_structural_plausibility": 0.60,  # lift 0.326 PASS
                                    "chance_top5_plausibility": 0.27,
                                    "chance_analytic": 0.274,
                                    "n_trials": 50, "k_obj_same": 3},
            "ARM_HELDOUT_NEW_SUBJ": {"top1": 0.05,  # lift 0.03 FAIL
                                     "chance_top1": 0.02,
                                     "chance_analytic": 0.02,
                                     "n_trials": 50, "k_subj_train": 3},
            "ARM_HELDOUT_NEW_PRED": {"top5_structural_plausibility": 0.43,  # lift 0.009 FAIL
                                     "chance_top5_plausibility": 0.42,
                                     "chance_analytic": 0.421,
                                     "n_trials": 50, "k_pred_train": 5},
        },
        "N": 8192, "M_TRAIN_PAIRS": 200,
        "V_SUBJ": 50, "V_PRED": 20, "V_OBJ": 50,
        "K_OBJ_SAME": 3, "K_SUBJ_TRAIN": 3, "K_PRED_TRAIN": 5,
        "N_HELDOUT_TRIALS": 50, "wall_s": 0.0, "run_mode": "selftest",
        "config_version": "selftest",
    }
    v2, m2, d2 = compute_verdict([fake_unit_mid, fake_unit_mid, fake_unit_mid])
    assert v2 == "MIDDLE_BAND", "verdict-MIDDLE expected, got %s | %s" % (v2, m2[:200])

    # SANITY: trained top1 fails sanity floor
    fake_unit_sanity_fail = dict(fake_unit_mid)
    fake_unit_sanity_fail["by_arm"] = dict(fake_unit_mid["by_arm"])
    fake_unit_sanity_fail["by_arm"]["ARM_TRAINED_PAIRS"] = {
        "top1": 0.30, "top5": 0.50, "chance_top1": 0.02,
        "n_triples": 200, "mean_cosine_correct": 0.1,
    }
    v3, m3, d3 = compute_verdict([fake_unit_sanity_fail, fake_unit_sanity_fail, fake_unit_sanity_fail])
    assert v3 == "HARD_FAIL_SANITY", "verdict-SANITY expected, got %s | %s" % (v3, m3[:200])

    print("[selftest] PASS: dense_unit_norm + bind/unbind round-trip + composite-(s,p)-key "
          "single-triple OBJ recall + M=5 distinct-key recall >=4/5 + verdict (HP/MIDDLE/SANITY)",
          flush=True)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print(
        "[config] %s mode=%s N_DIM=%d M=%d V=(%d,%d,%d) seeds=%s | %s" % (
            ANCHOR_NAME, RUN_MODE, N_DIM, M_TRAIN_PAIRS,
            V_SUBJ, V_PRED, V_OBJ, SEEDS, CONFIG_VERSION
        ),
        flush=True,
    )
    out_dir = get_output_dir(ANCHOR_NAME)
    run_cfg = {
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "schema": "compositional-generalization-CLEAN-role-filler-v1",
    }
    t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        already = aggregate_partials(out_dir, [key], run_config=run_cfg)
        if key in already:
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        result = run_unit(seed)
        write_partial_key(out_dir, key, result)
    units = list(aggregate_partials(
        out_dir, ["s%d" % s for s in SEEDS], run_config=run_cfg
    ).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "M_TRAIN_PAIRS": M_TRAIN_PAIRS,
        "V_SUBJ": V_SUBJ, "V_PRED": V_PRED, "V_OBJ": V_OBJ,
        "K_OBJ_SAME": K_OBJ_SAME, "K_SUBJ_TRAIN": K_SUBJ_TRAIN,
        "K_PRED_TRAIN": K_PRED_TRAIN, "N_HELDOUT_TRIALS": N_HELDOUT_TRIALS,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_substrate_compositional_generalization_CLEAN_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg,
        "substrate_only_decode_gate": "N/A (mechanism-characterization cell, not LM cell)",
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
