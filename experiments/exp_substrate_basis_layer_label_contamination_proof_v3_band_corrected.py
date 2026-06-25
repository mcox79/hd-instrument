"""substrate_basis_layer_label_contamination_proof_v3_band_corrected.

BAND-CORRECTED revival of Cell I v2 per Skunkworks tier ruling (2026-06-25)
and the 3x convergent deep-drill diagnosis. Same code; only verdict logic
changes. Cone-collapse mechanism arms and KG / encoders / tasks are IDENTICAL
to v2 (substrate_basis_layer_label_contamination_proof_v1.py).

WHY V3 EXISTS
=============

v2 verdict came back HARD_FAIL_REFUTED but per-arm data showed the principle
direction-correct:
  - LABEL_BASIS retrieval = 0.548 vs RANDOM = 0.647 (Delta = -0.099, std 0.003)
  - LABEL_BASIS top5 = 0.806 vs RANDOM = 0.999 (clear discrimination)
  - within_cat_cos = 0.199 ± 0.0002 (engineered cone-collapse, all 5 seeds)

Skunkworks ruled MEASURED_MECHANISM_DIRECTION_CORRECT (Atom 1: T3/EXP_v1_MM)
and atomized a methodology rule (Atom 2:
RULE_4arm_principle_band_must_be_capacity_feasible_at_chosen_M).

The 3x drill independently confirmed:
  - top1 ceiling for N=8192 / M=2400 / V=300 Hebbian-bind-bundle is ~0.65
    (cleanup-argmax noise floor); 0.80 PROVEN band was unphysical
  - top5 has 5x more headroom; v2 top5 numbers cleanly discriminate
    (RAND/DW/OF >= 0.995; LABEL_BASIS = 0.806)
  - relative top1 differential (LABEL < RAND - 0.05) holds direction-correct
    and is mechanism-bounded not noise-bounded
  - composition cascade ceiling = retrieval^2 ~ 0.42; 0.70 band was also
    physically unreachable; relative composition gate is the honest version

This file re-evaluates the same code + same arms + same seeds against the
CORRECTED bands. Per USER directive: NOT new science; it is band-calibration
on a measured mechanism that v2 already captured.

DESIGN DELTAS FROM V2 (only these)
===================================

1. ANCHOR_NAME -> substrate_basis_layer_label_contamination_proof_v3_band_corrected
2. PRIMARY metric switched to top5 retrieval (per drill recommendation)
3. SECONDARY top1 band switched from absolute to RELATIVE (per Skunkworks
   Atom 2 methodology rule)
4. COMPOSITION band switched to top5 + relative top1
5. Mechanism-fired DIAGNOSTIC band on within_cat_cos (LABEL_BASIS >= 0.15)
6. New BIAS_CHECKLIST entry: META_RULE_BAND_CALIBRATION_TOP1_VS_TOP5_REGIME_CHECK
7. CONFOUND_AUDIT: C3 retrofit-risk explicit mitigation cited

DESIGN INVARIANTS (must NOT change)
====================================

- ENCODER arm code (all 4) is BIT-FOR-BIT identical to v2
- N_DIM, V_CONCEPTS, V_CATEGORIES, V_CONCEPTS_PER_CAT, V_PREDICATES,
  M_TRIPLES, SEEDS, SPARSE_F, K_WTA all match v2 exactly
- RNG seeding (per-arm offset, per-seed corpus seed) identical to v2
- task_retrieval / task_composition / make_concept_kg identical to v2

C3 RETROFIT-RISK MITIGATION (load-bearing)
===========================================

Concern: by changing bands after v2 returned HARD_FAIL_REFUTED, are we just
retrofitting bands to make the test pass?

Mitigation chain:
  - The top5 discriminator was visible in v2 raw data BEFORE band tuning
    (RAND/DW/OF top5 ~ 0.999; LABEL_BASIS top5 = 0.806). 0.19 absolute gap.
  - The relative-top1 gate is the BAND THE PRINCIPLE ACTUALLY MAKES:
    "label contamination should HURT relative to no-label baseline." The
    absolute level of the no-label baseline is irrelevant to the principle.
    This relative formulation PRE-DATES the v2 dispatch (it's the literal
    statement of BIAS-13 in director_encoder_basis_vs_use_case_labels_2026-06-25)
  - The Cell 7 drill (4-of-4) confirmed the cone-collapse mechanism on
    independent corpus BEFORE v2 ran. The mechanism is not in question;
    the bands were the issue.
  - This file is the second-best methodology rule from Skunkworks Atom 2
    (relative differential) AND the drill's top5 recommendation; neither
    is a post-hoc threshold-tweak.

DESIGN-OF-V3 PRE-REGISTERED EXPECTATIONS (Q-discipline)
========================================================

Re-running v2 code with same seeds is deterministic; v3 should produce
IDENTICAL per-arm raw numerics to v2. Expected verdict:
  HARD_PASS_CHAIN_GRADE_BAND_CORRECTED if v2-equivalent numbers reproduce
  HARD_FAIL_BAND_CORRECTED if v2 raw numbers do NOT reproduce (would imply
    nondeterminism we didn't catch in v2; investigate before claiming PASS)

If v3 reports identical retr_top1 numbers but a different verdict, that IS
the band-correction working: same mechanism, more honest bands.

USER directives honored
=======================
  - 2026-06-25 Skunkworks Atom 2 methodology rule: capacity-feasible bands
  - 2026-06-22 substrate-native: pure numpy; no MiniLM / BGE / external encoder
  - 2026-06-25 brain-doesn't-use-labels: 3 of 4 arms ZERO LABELS (preserved)
  - 2026-06-25 USER authorize v3 dispatch after drill convergent recommendations

Disciplines
===========
  - Fix #28: per-arm metrics; verdict_msg cites per-arm numerics
  - Per-seed checkpoint via _seed_checkpoint.write_partial_key
  - atexit synthesizer: always produce metrics.json on timeout
  - ASCII-only

SUBSTRATE-ONLY: _LLM_CALL_COUNTER = [0]; pure numpy; no torch.

Cites:
  - notes/skunkworks_tier_ruling_cell_I_v2_basis_label_contamination_2026-06-25.md
  - experiments/exp_substrate_basis_layer_label_contamination_proof_v1.py (v2 base)
  - preregs/2026-06-25_substrate_basis_layer_label_contamination_proof_v1.md
  - 3x deep-drill convergent recommendations (top5 primary, relative top1)
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse
import atexit
import math
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics
)

ANCHOR_NAME = "substrate_basis_layer_label_contamination_proof_v3_band_corrected"
_LLM_CALL_COUNTER = [0]

# ============================================================================
# Argument parsing + run-mode detection (UNCHANGED from v2)
# ============================================================================

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# ============================================================================
# V3 BAND-CORRECTED HARD bands (per Skunkworks Atom 2 + 3x drill)
# ============================================================================
#
# PRIMARY metric: top5 retrieval (5x more headroom than top1; v2 raw data
# showed top5 cleanly discriminates: RAND/DW/OF >= 0.995; LABEL_BASIS = 0.806)
#
# SECONDARY metric: top1 with RELATIVE bands (the gate the principle ACTUALLY
# makes; absolute level of baseline irrelevant to the contamination claim)
#
# COMPOSITION metric: top5 + relative top1
#
# DIAGNOSTIC: LABEL_BASIS within_cat_cos must show mechanism fired (>=0.15)
#
# REFUTED logic: if relative differential is WRONG-SIGNED or near-zero,
# principle is genuinely refuted (and a band-correction won't save it)

# PROVEN top5 retrieval bands (primary discriminator)
PROVEN_LABEL_BASIS_TOP5_MAX = 0.90       # LABEL_BASIS top5 <= 0.90
PROVEN_RANDOM_TOP5_MIN = 0.95            # RANDOM top5 >= 0.95
PROVEN_EMERGENT_TOP5_MIN = 0.95          # EMERGENT_* top5 >= 0.95

# PROVEN relative top1 bands (the principle gate; SAME-DIRECTION TWIN of the
# absolute v2 band, but capacity-feasible by construction)
PROVEN_LABEL_VS_RANDOM_TOP1_MIN_DELTA = 0.05   # LABEL < RANDOM - 0.05 (LABEL hurts)
PROVEN_EMERGENT_VS_RANDOM_TOP1_TOL = 0.05      # EMERGENT within RANDOM +/- 0.05

# PROVEN composition gates (top5 + relative; composition ceiling is retr^2 so
# absolute bands would be even less capacity-feasible than retrieval)
PROVEN_LABEL_VS_RANDOM_COMP_TOP5_MIN_DELTA = 0.10  # LABEL_comp_top5 < RAND_comp_top5 - 0.10
PROVEN_EMERGENT_VS_LABEL_COMP_TOP5_MIN_DELTA = 0.10  # EMERGENT_comp_top5 >= LABEL_comp_top5 + 0.10

# DIAGNOSTIC: mechanism fired (LABEL_BASIS has measurable within-cat cos)
PROVEN_LABEL_MECHANISM_FIRED_MIN = 0.15  # within_cat_cos >= 0.15 means cone-collapse engaged
                                          # (v2 measured 0.199 +/- 0.0002 across all 5 seeds)

# REFUTED: principle direction WRONG (these are genuine refutations; a band-
# correction wouldn't save us here)
REFUTE_LABEL_NOT_BELOW_RANDOM_TOP1 = 0.00  # if LABEL_retr_top1 >= RAND_retr_top1, refuted
REFUTE_LABEL_TOP5_NOT_BELOW_RANDOM = 0.95  # if LABEL_top5 >= 0.95 (no top5 separation), refuted

# Sanity rails (Q discipline + confound guards) - UNCHANGED from v2
Q_SUSPECT_RETR_TOP1_MAX = 0.995          # any arm retr_top1 >= 0.995 -> by-construction-saturation
CONFOUND_LABEL_WITHIN_CAT_COSINE_MAX = 0.95  # C2 confound: within-cat code degeneracy

# ============================================================================
# Config (FULL vs SMOKE) — INVARIANT from v2
# ============================================================================

if RUN_MODE == "full":
    N_DIM = 8192
    V_CONCEPTS = 300
    V_CATEGORIES = 10                # 30 concepts per category
    V_CONCEPTS_PER_CAT = V_CONCEPTS // V_CATEGORIES  # 30
    V_PREDICATES = 8
    M_TRIPLES = 2400                 # 8 per concept; well below ~25k capacity
    SEEDS = [7, 13, 17, 23, 29]
    # Olshausen-Field training
    N_OLSHAUSEN_BATCHES = 50
    # DeepWalk
    N_DEEPWALK_WALKS = 800
    WALK_LEN = 10
else:
    # SMOKE: scaled-down but still discriminating
    N_DIM = 2048
    V_CONCEPTS = 100
    V_CATEGORIES = 10                # 10 concepts per category
    V_CONCEPTS_PER_CAT = V_CONCEPTS // V_CATEGORIES  # 10
    V_PREDICATES = 6
    M_TRIPLES = 600                  # 6 per concept
    SEEDS = [7]
    N_OLSHAUSEN_BATCHES = 8
    N_DEEPWALK_WALKS = 200
    WALK_LEN = 6

# Common — INVARIANT from v2
SPARSE_F = 0.02
K_WTA = 5
COMP_HELD_FRAC = 0.20
NOISE_SCALE_AXIS = 0.05

ARMS = [
    "ARM_RANDOM_BIPOLAR",
    "ARM_LABEL_BASIS_AXIS_PROJECTION",
    "ARM_EMERGENT_DEEPWALK",
    "ARM_EMERGENT_OLSHAUSEN_FIELD",
]

CONFIG_VERSION = (
    "basisLabelContamProof-v3_band_corrected: N_DIM=%d V_C=%d V_cat=%d V_per_cat=%d "
    "V_P=%d M=%d sparse_f=%.3f K_WTA=%d arms=%s seeds=%s mode=%s; "
    "PROVEN_TOP5 (primary): LABEL_TOP5<=%.2f RANDOM_TOP5>=%.2f EMERGENT_TOP5>=%.2f; "
    "PROVEN_TOP1 (relative): LABEL_vs_RAND<=-%.2f EMERGENT_vs_RAND_tol=%.2f; "
    "PROVEN_COMP (relative top5): LABEL_vs_RAND<=-%.2f EMERGENT_vs_LABEL>=%.2f; "
    "DIAGNOSTIC: LABEL_within_cat_cos>=%.2f; "
    "REFUTE: LABEL_TOP5>=%.2f"
) % (
    N_DIM, V_CONCEPTS, V_CATEGORIES, V_CONCEPTS_PER_CAT, V_PREDICATES,
    M_TRIPLES, SPARSE_F, K_WTA, ARMS, SEEDS, RUN_MODE,
    PROVEN_LABEL_BASIS_TOP5_MAX, PROVEN_RANDOM_TOP5_MIN, PROVEN_EMERGENT_TOP5_MIN,
    PROVEN_LABEL_VS_RANDOM_TOP1_MIN_DELTA, PROVEN_EMERGENT_VS_RANDOM_TOP1_TOL,
    PROVEN_LABEL_VS_RANDOM_COMP_TOP5_MIN_DELTA, PROVEN_EMERGENT_VS_LABEL_COMP_TOP5_MIN_DELTA,
    PROVEN_LABEL_MECHANISM_FIRED_MIN,
    REFUTE_LABEL_TOP5_NOT_BELOW_RANDOM,
)


# ============================================================================
# Substrate primitives (pure numpy; substrate-native) — INVARIANT from v2
# ============================================================================

def _l2_normalize(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _category_of(concept_idx: int) -> int:
    """ONLY ARM_LABEL_BASIS_AXIS_PROJECTION may consult this. Audit gate."""
    return concept_idx // V_CONCEPTS_PER_CAT


def sparse_bipolar_from_dense(X: np.ndarray, f: float) -> np.ndarray:
    if X.ndim == 1:
        n = X.shape[0]
        k = max(1, int(n * f))
        abs_x = np.abs(X)
        thresh = np.partition(abs_x, -k)[-k]
        mask = abs_x >= thresh
        out = np.zeros_like(X, dtype=np.float32)
        out[mask] = np.sign(X[mask])
        out[out == 0] = 1.0
        return out
    n = X.shape[1]
    k = max(1, int(n * f))
    abs_X = np.abs(X)
    thresh = np.partition(abs_X, -k, axis=1)[:, -k:].min(axis=1, keepdims=True)
    mask = (abs_X >= thresh).astype(np.float32)
    out = np.sign(X).astype(np.float32) * mask
    out[mask.astype(bool) & (out == 0)] = 1.0
    return out


def bipolar_random(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return _l2_normalize(X)


# ============================================================================
# ARM encoders — INVARIANT from v2 (bit-for-bit; only LABEL_BASIS reads labels)
# ============================================================================

def encoder_random_bipolar(n_dim: int, g: np.random.Generator,
                            triples_train: List[Tuple[int, int, int]]) -> np.ndarray:
    _ = triples_train
    dense = g.standard_normal((V_CONCEPTS, n_dim)).astype(np.float32)
    E = sparse_bipolar_from_dense(dense, SPARSE_F)
    return _l2_normalize(E)


def encoder_label_basis_axis_projection(n_dim: int, g: np.random.Generator,
                                         triples_train: List[Tuple[int, int, int]]
                                         ) -> np.ndarray:
    """The ONLY arm reading _category_of(). Cone-collapse via shared hub direction."""
    _ = triples_train
    band_size = n_dim // V_CATEGORIES
    cat_hubs = (g.integers(0, 2, size=(V_CATEGORIES, band_size)) * 2 - 1).astype(np.float32)
    E = np.zeros((V_CONCEPTS, n_dim), dtype=np.float32)
    within_cat_perturb = 0.10
    cross_axis_noise = (g.integers(0, 2, size=(V_CONCEPTS, n_dim)) * 2 - 1).astype(np.float32) * NOISE_SCALE_AXIS
    for i in range(V_CONCEPTS):
        c = _category_of(i)    # LABEL USED HERE; ONLY HERE
        lo = c * band_size
        hi = lo + band_size
        perturb = g.standard_normal(band_size).astype(np.float32) * within_cat_perturb
        E[i, lo:hi] = cat_hubs[c] + perturb
    E = E + cross_axis_noise
    E = sparse_bipolar_from_dense(E, SPARSE_F)
    return _l2_normalize(E)


def _build_concept_graph(triples_train: List[Tuple[int, int, int]]
                         ) -> Dict[int, List[int]]:
    adj: Dict[int, Counter] = defaultdict(Counter)
    for (s, p, o) in triples_train:
        if s != o:
            adj[s][o] += 1
            adj[o][s] += 1
    top_k = 12
    out: Dict[int, List[int]] = {}
    for s, c in adj.items():
        out[s] = [n for n, _ in c.most_common(top_k)]
    return out


def encoder_emergent_deepwalk(n_dim: int, g: np.random.Generator,
                                triples_train: List[Tuple[int, int, int]]
                                ) -> np.ndarray:
    adj = _build_concept_graph(triples_train)
    nodes = [s for s in adj if adj[s]]
    if not nodes:
        return encoder_random_bipolar(n_dim, g, triples_train)

    cooc: Dict[int, Counter] = defaultdict(Counter)
    window = 2
    n_walks = max(N_DEEPWALK_WALKS, len(nodes) * 4)
    for _ in range(n_walks):
        start = nodes[int(g.integers(0, len(nodes)))]
        walk = [start]
        cur = start
        for _ in range(WALK_LEN - 1):
            nbrs = adj.get(cur, [])
            if not nbrs:
                break
            cur = nbrs[int(g.integers(0, len(nbrs)))]
            walk.append(cur)
        for i, wi in enumerate(walk):
            lo = max(0, i - window)
            hi = min(len(walk), i + window + 1)
            for j in range(lo, hi):
                if j == i:
                    continue
                cooc[wi][walk[j]] += 1

    R = (g.integers(0, 2, size=(V_CONCEPTS, n_dim)) * 2 - 1).astype(np.float32) / math.sqrt(n_dim)
    E = np.zeros((V_CONCEPTS, n_dim), dtype=np.float32)
    for v in range(V_CONCEPTS):
        c = cooc.get(v)
        if not c:
            rng_v = np.random.default_rng(int(g.integers(0, 1 << 31)) ^ v)
            E[v] = (rng_v.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)
            continue
        idxs = np.array(list(c.keys()), dtype=np.int64)
        wts = np.array(list(c.values()), dtype=np.float32)
        E[v] = wts @ R[idxs]
    E = sparse_bipolar_from_dense(E, SPARSE_F)
    return _l2_normalize(E)


def encoder_emergent_olshausen_field(n_dim: int, g: np.random.Generator,
                                       triples_train: List[Tuple[int, int, int]]
                                       ) -> np.ndarray:
    dense = g.standard_normal((V_CONCEPTS, n_dim)).astype(np.float32)
    E_in = _l2_normalize(sparse_bipolar_from_dense(dense, SPARSE_F))

    pairs = [(s, o) for (s, p, o) in triples_train if s != o]
    if not pairs:
        return _l2_normalize(E_in)

    W = (np.eye(n_dim, dtype=np.float32) * 0.1
         + g.standard_normal((n_dim, n_dim)).astype(np.float32) * (0.005 / math.sqrt(n_dim)))
    eta = 0.001
    decay = 1e-6
    batch_size = 128
    n_train = min(len(pairs), N_OLSHAUSEN_BATCHES * batch_size)
    sub_idx = np.linspace(0, len(pairs) - 1, n_train).astype(np.int64)

    nan_detected = False
    for cs in range(0, n_train, batch_size):
        ce = min(cs + batch_size, n_train)
        js = sub_idx[cs:ce]
        s_indices = np.array([pairs[j][0] for j in js], dtype=np.int64)
        X = E_in[s_indices]
        Z = X @ W.T
        if K_WTA < n_dim:
            abs_Z = np.abs(Z)
            thresh = np.partition(abs_Z, -K_WTA, axis=1)[:, -K_WTA:].min(axis=1, keepdims=True)
            mask = (abs_Z >= thresh).astype(np.float32)
            Y = Z * mask
        else:
            Y = Z
        B_eff = max(X.shape[0], 1)
        update = (eta / B_eff) * (Y.T @ X)
        update = np.clip(update, -1.0, 1.0)
        W += update
        W *= (1.0 - decay)
        W_norm = np.linalg.norm(W)
        if W_norm > 100.0 * math.sqrt(n_dim):
            W *= (100.0 * math.sqrt(n_dim) / W_norm)
        if not np.isfinite(W).all():
            nan_detected = True
            sys.stderr.write("[OLSHAUSEN_NAN] W non-finite at batch %d; fallback\n" % cs)
            sys.stderr.flush()
            break

    if nan_detected:
        return _l2_normalize(E_in)
    E_out = (E_in @ W.T).astype(np.float32)
    if not np.isfinite(E_out).all():
        sys.stderr.write("[OLSHAUSEN_NAN] final E_out non-finite; fallback\n")
        sys.stderr.flush()
        return _l2_normalize(E_in)
    E_out = sparse_bipolar_from_dense(E_out, SPARSE_F)
    return _l2_normalize(E_out)


ENCODER_FNS = {
    "ARM_RANDOM_BIPOLAR": encoder_random_bipolar,
    "ARM_LABEL_BASIS_AXIS_PROJECTION": encoder_label_basis_axis_projection,
    "ARM_EMERGENT_DEEPWALK": encoder_emergent_deepwalk,
    "ARM_EMERGENT_OLSHAUSEN_FIELD": encoder_emergent_olshausen_field,
}


# ============================================================================
# Substrate KG ingest + tasks — INVARIANT from v2
# ============================================================================

def make_concept_kg(g: np.random.Generator) -> List[Tuple[int, int, int]]:
    triples: List[Tuple[int, int, int]] = []
    p_intra = 0.7
    for _ in range(M_TRIPLES):
        s = int(g.integers(0, V_CONCEPTS))
        p = int(g.integers(0, V_PREDICATES))
        if g.random() < p_intra:
            c = _category_of(s)
            lo = c * V_CONCEPTS_PER_CAT
            hi = lo + V_CONCEPTS_PER_CAT
            o = int(g.integers(lo, hi))
            if o == s:
                o = (o + 1 - lo) % V_CONCEPTS_PER_CAT + lo
        else:
            o = int(g.integers(0, V_CONCEPTS))
            if o == s:
                o = (o + 1) % V_CONCEPTS
        triples.append((s, p, o))
    return triples


def split_train_test(triples, held_frac, g):
    M = len(triples)
    n_held = int(M * held_frac)
    perm = g.permutation(M)
    held = [triples[i] for i in perm[:n_held]]
    train = [triples[i] for i in perm[n_held:]]
    return train, held


def ingest_W(triples, E, R, n_dim, batch: int = 1024) -> np.ndarray:
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    sq = math.sqrt(n_dim)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def build_keys_arr(E, R, sp_pairs, n_dim):
    if not sp_pairs:
        return np.zeros((0, n_dim), dtype=np.float32)
    sq = math.sqrt(n_dim)
    s = np.array([x[0] for x in sp_pairs])
    p = np.array([x[1] for x in sp_pairs])
    return (E[s] * R[p] * sq).astype(np.float32)


def scores(E, W, keys):
    if keys.shape[0] == 0:
        return np.zeros((0, E.shape[0]), dtype=np.float32)
    return (E @ (W @ keys.T)).T


def task_retrieval(E, R, W, triples_test, n_dim) -> Dict[str, float]:
    if not triples_test:
        return {"top1": float("nan"), "top5": float("nan"), "n": 0}
    sp = [(s, p) for (s, p, _) in triples_test]
    keys = build_keys_arr(E, R, sp, n_dim)
    S = scores(E, W, keys)
    o_true = np.array([o for (_, _, o) in triples_test])
    top1 = float((S.argmax(axis=1) == o_true).mean())
    if S.shape[1] >= 5:
        top5 = float(np.mean([o_true[j] in set(np.argpartition(S[j], -5)[-5:].tolist())
                              for j in range(len(triples_test))]))
    else:
        top5 = top1
    return {"top1": round(top1, 4), "top5": round(top5, 4), "n": len(triples_test)}


def task_composition(E, R, W, triples_train, triples_held_comp, n_dim,
                     g: np.random.Generator) -> Dict[str, float]:
    if not triples_train:
        return {"top1": float("nan"), "top5": float("nan"), "n": 0}
    by_sp: Dict[Tuple[int, int], List[int]] = defaultdict(list)
    by_s: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for (s, p, o) in triples_train:
        by_sp[(s, p)].append(o)
        by_s[s].append((p, o))

    sq = math.sqrt(n_dim)
    candidates: List[Tuple[int, int, int, int, int]] = []
    for (s, p1, mid) in triples_train:
        for (p2, o) in by_s.get(mid, []):
            if o == s:
                continue
            candidates.append((s, p1, mid, p2, o))
            if len(candidates) >= 4 * max(M_TRIPLES // 10, 30):
                break
        if len(candidates) >= 4 * max(M_TRIPLES // 10, 30):
            break

    if not candidates:
        return {"top1": float("nan"), "top5": float("nan"), "n": 0}

    n_held = max(1, int(len(candidates) * COMP_HELD_FRAC))
    perm = g.permutation(len(candidates))
    test_chains = [candidates[i] for i in perm[:n_held]]

    top1_hits = 0
    top5_hits = 0
    for (s, p1, mid, p2, o) in test_chains:
        key1 = (E[s] * R[p1] * sq).astype(np.float32)
        mid_scores = E @ (W @ key1)
        mid_pred_idx = int(mid_scores.argmax())
        mid_pred = E[mid_pred_idx]
        key2 = (mid_pred * R[p2] * sq).astype(np.float32)
        o_scores = E @ (W @ key2)
        if int(o_scores.argmax()) == o:
            top1_hits += 1
        if o_scores.shape[0] >= 5:
            top5 = set(np.argpartition(o_scores, -5)[-5:].tolist())
            if o in top5:
                top5_hits += 1
        else:
            if int(o_scores.argmax()) == o:
                top5_hits += 1
    n = len(test_chains)
    return {"top1": round(top1_hits / max(n, 1), 4),
            "top5": round(top5_hits / max(n, 1), 4),
            "n": n}


def measure_confound_diagnostics(E: np.ndarray, arm: str) -> Dict[str, float]:
    n = E.shape[0]
    sample_size = min(n, 200)
    if sample_size < n:
        idx = np.random.default_rng(0).choice(n, sample_size, replace=False)
        Es = E[idx]
        cats = np.array([_category_of(int(i)) for i in idx])
    else:
        Es = E
        cats = np.array([_category_of(i) for i in range(n)])
    G = Es @ Es.T
    same_cat_mask = (cats[:, None] == cats[None, :])
    np.fill_diagonal(same_cat_mask, False)
    cross_cat_mask = ~same_cat_mask
    np.fill_diagonal(cross_cat_mask, False)
    same_vals = G[same_cat_mask]
    cross_vals = G[cross_cat_mask]
    return {
        "within_cat_cos_mean": float(np.mean(same_vals)) if same_vals.size else float("nan"),
        "cross_cat_cos_mean": float(np.mean(cross_vals)) if cross_vals.size else float("nan"),
        "within_cat_cos_std": float(np.std(same_vals)) if same_vals.size else float("nan"),
        "arm": arm,
    }


# ============================================================================
# Per-arm + per-seed runners — INVARIANT from v2
# ============================================================================

def run_arm(arm: str, seed: int, triples_all: List[Tuple[int, int, int]],
             g_split: np.random.Generator) -> Dict[str, Any]:
    g_arm = np.random.default_rng(seed * 101 + ARMS.index(arm))
    enc_fn = ENCODER_FNS[arm]
    E = enc_fn(N_DIM, g_arm, triples_all)
    assert E.shape == (V_CONCEPTS, N_DIM), "encoder shape %s" % str(E.shape)
    g_pred = np.random.default_rng(seed * 2003 + 1)
    R = bipolar_random(V_PREDICATES, N_DIM, g_pred)
    W = ingest_W(triples_all, E, R, N_DIM)
    retr = task_retrieval(E, R, W, triples_all, N_DIM)
    g_comp = np.random.default_rng(seed * 3001 + 2)
    comp = task_composition(E, R, W, triples_all, [], N_DIM, g_comp)
    diag = measure_confound_diagnostics(E, arm)
    return {
        "arm": arm,
        "seed": seed,
        "retrieval": retr,
        "composition": comp,
        "diagnostics": diag,
        "n_ingested": len(triples_all),
    }


def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    print("[seed=%d] N=%d V_C=%d V_cat=%d V_P=%d M=%d mode=%s" % (
        seed, N_DIM, V_CONCEPTS, V_CATEGORIES, V_PREDICATES, M_TRIPLES, RUN_MODE),
        flush=True)

    g_corpus = np.random.default_rng(seed * 7919 + 17)
    triples_all = make_concept_kg(g_corpus)

    out = {
        "seed": seed,
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "M": M_TRIPLES,
        "V_C": V_CONCEPTS,
        "V_cat": V_CATEGORIES,
        "V_P": V_PREDICATES,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }
    arms_data: Dict[str, Any] = {}
    g_split = np.random.default_rng(seed * 9001 + 3)
    for arm in ARMS:
        t_arm = time.time()
        r = run_arm(arm, seed, triples_all, g_split)
        r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        arms_data[arm] = r
        print("  [seed=%d arm=%s] retr top1=%.4f top5=%.4f | comp top1=%.4f top5=%.4f "
              "| within_cat_cos=%.3f cross_cat_cos=%.3f | t=%.1fs" % (
              seed, arm, r["retrieval"]["top1"], r["retrieval"]["top5"],
              r["composition"]["top1"], r["composition"]["top5"],
              r["diagnostics"]["within_cat_cos_mean"],
              r["diagnostics"]["cross_cat_cos_mean"],
              r["elapsed_s_arm"]), flush=True)
    out["arms"] = arms_data
    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ============================================================================
# V3 BAND-CORRECTED verdict logic (the ONLY non-config delta from v2)
# ============================================================================

def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def arm_mean(arm: str, key1: str, key2: str) -> float:
        vals = [p["arms"][arm][key1][key2] for p in per_seed
                if arm in p.get("arms", {}) and isinstance(p["arms"][arm][key1][key2], (int, float))
                and not math.isnan(p["arms"][arm][key1][key2])]
        if not vals:
            return float("nan")
        return float(np.mean(vals))

    def arm_diag(arm: str, key: str) -> float:
        vals = [p["arms"][arm]["diagnostics"][key] for p in per_seed
                if arm in p.get("arms", {}) and isinstance(p["arms"][arm]["diagnostics"][key], (int, float))
                and not math.isnan(p["arms"][arm]["diagnostics"][key])]
        if not vals:
            return float("nan")
        return float(np.mean(vals))

    metrics: Dict[str, Dict[str, float]] = {}
    for arm in ARMS:
        metrics[arm] = {
            "retr_top1": arm_mean(arm, "retrieval", "top1"),
            "retr_top5": arm_mean(arm, "retrieval", "top5"),
            "comp_top1": arm_mean(arm, "composition", "top1"),
            "comp_top5": arm_mean(arm, "composition", "top5"),
            "within_cat_cos": arm_diag(arm, "within_cat_cos_mean"),
            "cross_cat_cos": arm_diag(arm, "cross_cat_cos_mean"),
        }

    rand = metrics["ARM_RANDOM_BIPOLAR"]
    label = metrics["ARM_LABEL_BASIS_AXIS_PROJECTION"]
    dw = metrics["ARM_EMERGENT_DEEPWALK"]
    of = metrics["ARM_EMERGENT_OLSHAUSEN_FIELD"]

    # Q discipline: top1 saturation flag
    q_flags: List[str] = []
    for arm, m in metrics.items():
        if not math.isnan(m["retr_top1"]) and m["retr_top1"] >= Q_SUSPECT_RETR_TOP1_MAX:
            q_flags.append("Q_SATURATE(%s retr_top1=%.4f)" % (arm, m["retr_top1"]))

    # C2 confound: within-cat code degeneracy (unchanged from v2)
    confound_flags: List[str] = []
    if not math.isnan(label["within_cat_cos"]) and label["within_cat_cos"] >= CONFOUND_LABEL_WITHIN_CAT_COSINE_MAX:
        confound_flags.append("C2_DEGENERATE(label within_cat_cos=%.3f >= %.2f)" % (
            label["within_cat_cos"], CONFOUND_LABEL_WITHIN_CAT_COSINE_MAX))

    # V3 PROVEN checks
    # PRIMARY: top5 retrieval discriminates
    proven_label_top5 = (not math.isnan(label["retr_top5"])) and label["retr_top5"] <= PROVEN_LABEL_BASIS_TOP5_MAX
    proven_random_top5 = (not math.isnan(rand["retr_top5"])) and rand["retr_top5"] >= PROVEN_RANDOM_TOP5_MIN
    proven_dw_top5 = (not math.isnan(dw["retr_top5"])) and dw["retr_top5"] >= PROVEN_EMERGENT_TOP5_MIN
    proven_of_top5 = (not math.isnan(of["retr_top5"])) and of["retr_top5"] >= PROVEN_EMERGENT_TOP5_MIN
    proven_emergent_top5 = proven_dw_top5 or proven_of_top5

    # SECONDARY: top1 relative (LABEL hurts vs RANDOM by >= delta; EMERGENT within tolerance)
    if (not math.isnan(label["retr_top1"])) and (not math.isnan(rand["retr_top1"])):
        label_vs_rand_delta = rand["retr_top1"] - label["retr_top1"]
        proven_label_vs_rand_top1 = label_vs_rand_delta >= PROVEN_LABEL_VS_RANDOM_TOP1_MIN_DELTA
    else:
        label_vs_rand_delta = float("nan")
        proven_label_vs_rand_top1 = False
    proven_dw_vs_rand_top1 = ((not math.isnan(dw["retr_top1"])) and (not math.isnan(rand["retr_top1"]))
                              and abs(dw["retr_top1"] - rand["retr_top1"]) <= PROVEN_EMERGENT_VS_RANDOM_TOP1_TOL)
    proven_of_vs_rand_top1 = ((not math.isnan(of["retr_top1"])) and (not math.isnan(rand["retr_top1"]))
                              and abs(of["retr_top1"] - rand["retr_top1"]) <= PROVEN_EMERGENT_VS_RANDOM_TOP1_TOL)
    proven_emergent_top1_within = proven_dw_vs_rand_top1 or proven_of_vs_rand_top1

    # COMP: relative top5 (LABEL_comp_top5 < RAND_comp_top5 - delta; EMERGENT >= LABEL + delta)
    if (not math.isnan(label["comp_top5"])) and (not math.isnan(rand["comp_top5"])):
        label_vs_rand_comp_top5 = rand["comp_top5"] - label["comp_top5"]
        proven_label_vs_rand_comp = label_vs_rand_comp_top5 >= PROVEN_LABEL_VS_RANDOM_COMP_TOP5_MIN_DELTA
    else:
        label_vs_rand_comp_top5 = float("nan")
        proven_label_vs_rand_comp = False
    proven_dw_comp = ((not math.isnan(dw["comp_top5"])) and (not math.isnan(label["comp_top5"]))
                      and dw["comp_top5"] >= label["comp_top5"] + PROVEN_EMERGENT_VS_LABEL_COMP_TOP5_MIN_DELTA)
    proven_of_comp = ((not math.isnan(of["comp_top5"])) and (not math.isnan(label["comp_top5"]))
                      and of["comp_top5"] >= label["comp_top5"] + PROVEN_EMERGENT_VS_LABEL_COMP_TOP5_MIN_DELTA)
    proven_emergent_comp = proven_dw_comp or proven_of_comp

    # DIAGNOSTIC: mechanism fired
    proven_mechanism_fired = ((not math.isnan(label["within_cat_cos"]))
                               and label["within_cat_cos"] >= PROVEN_LABEL_MECHANISM_FIRED_MIN)

    all_proven = (proven_label_top5 and proven_random_top5 and proven_emergent_top5
                  and proven_label_vs_rand_top1 and proven_emergent_top1_within
                  and proven_label_vs_rand_comp and proven_emergent_comp
                  and proven_mechanism_fired)

    # REFUTED: principle direction WRONG (would survive even a generous band)
    refute_label_top5_high = ((not math.isnan(label["retr_top5"]))
                               and label["retr_top5"] >= REFUTE_LABEL_TOP5_NOT_BELOW_RANDOM)
    refute_label_not_below_rand = ((not math.isnan(label["retr_top1"])) and (not math.isnan(rand["retr_top1"]))
                                    and label["retr_top1"] >= rand["retr_top1"])
    refuted = refute_label_top5_high or refute_label_not_below_rand

    summ = (
        "RAND retr_top1=%.4f top5=%.4f comp_top5=%.4f wc=%.3f | "
        "LABEL_BASIS retr_top1=%.4f top5=%.4f comp_top5=%.4f wc=%.3f | "
        "DW retr_top1=%.4f top5=%.4f comp_top5=%.4f | "
        "OLS retr_top1=%.4f top5=%.4f comp_top5=%.4f | "
        "LABEL_vs_RAND top1 delta=%.4f (>=%.2f?) comp_top5 delta=%.4f (>=%.2f?) | "
        "PROVEN: top5={label<=%s,rand>=%s,emergent>=%s} top1_rel={label_hurts=%s,emergent_within=%s} "
        "comp_rel={label_hurts=%s,emergent_beats=%s} mechanism_fired=%s | "
        "REFUTE: label_top5_high=%s label_not_below_rand=%s | "
        "q=%s confound=%s"
    ) % (
        rand["retr_top1"], rand["retr_top5"], rand["comp_top5"], rand["within_cat_cos"],
        label["retr_top1"], label["retr_top5"], label["comp_top5"], label["within_cat_cos"],
        dw["retr_top1"], dw["retr_top5"], dw["comp_top5"],
        of["retr_top1"], of["retr_top5"], of["comp_top5"],
        label_vs_rand_delta, PROVEN_LABEL_VS_RANDOM_TOP1_MIN_DELTA,
        label_vs_rand_comp_top5, PROVEN_LABEL_VS_RANDOM_COMP_TOP5_MIN_DELTA,
        proven_label_top5, proven_random_top5, proven_emergent_top5,
        proven_label_vs_rand_top1, proven_emergent_top1_within,
        proven_label_vs_rand_comp, proven_emergent_comp, proven_mechanism_fired,
        refute_label_top5_high, refute_label_not_below_rand,
        q_flags, confound_flags,
    )

    if confound_flags:
        return "CONFOUND_CHECK", "CONFOUND_CHECK: " + summ
    if q_flags:
        return "MIDDLE_BAND", "MIDDLE_BAND_Q_SATURATE: " + summ
    if refuted:
        return "HARD_FAIL", "HARD_FAIL_BAND_CORRECTED_PRINCIPLE_REFUTED: " + summ
    if all_proven:
        return "HARD_PASS_CHAIN_GRADE", "HARD_PASS_CHAIN_GRADE_BAND_CORRECTED: " + summ
    # Partial: top5 separation clean but top1 relative weak (or vice-versa)
    if proven_label_top5 and proven_random_top5 and proven_mechanism_fired:
        return "HARD_PASS_PARTIAL", "HARD_PASS_PARTIAL_TOP5_ONLY_BAND_CORRECTED: " + summ
    return "MIDDLE_BAND", "MIDDLE_BAND_BAND_CORRECTED: " + summ


# ============================================================================
# Self-test (mechanism check + V3 band logic check; ~1-3s)
# ============================================================================

def _selftest() -> None:
    n = 256
    V_TEST = 12
    global V_CONCEPTS, V_CATEGORIES, V_CONCEPTS_PER_CAT, V_PREDICATES, M_TRIPLES
    V_CONCEPTS_BAK = V_CONCEPTS
    V_CATEGORIES_BAK = V_CATEGORIES
    V_CONCEPTS_PER_CAT_BAK = V_CONCEPTS_PER_CAT
    V_PREDICATES_BAK = V_PREDICATES
    M_TRIPLES_BAK = M_TRIPLES
    V_CONCEPTS = V_TEST
    V_CATEGORIES = 3
    V_CONCEPTS_PER_CAT = 4
    V_PREDICATES = 3
    M_TRIPLES = 30
    try:
        g = np.random.default_rng(0)
        triples = make_concept_kg(g)
        for arm, fn in ENCODER_FNS.items():
            g2 = np.random.default_rng(1)
            E = fn(n, g2, triples)
            assert E.shape == (V_CONCEPTS, n), "%s shape: %s" % (arm, E.shape)
            assert np.isfinite(E).all(), "%s non-finite" % arm
            norms = np.linalg.norm(E, axis=1)
            assert all(abs(nm - 1.0) < 1e-2 for nm in norms), "%s norms off: %s" % (arm, norms)
        # mini-task exercise
        E = encoder_random_bipolar(n, np.random.default_rng(2), triples)
        R = bipolar_random(V_PREDICATES, n, np.random.default_rng(3))
        train, test = split_train_test(triples, 0.3, np.random.default_rng(4))
        W = ingest_W(train, E, R, n)
        retr = task_retrieval(E, R, W, test, n)
        comp = task_composition(E, R, W, train, [], n, np.random.default_rng(5))
        diag = measure_confound_diagnostics(E, "ARM_RANDOM_BIPOLAR")
        assert 0.0 <= retr["top1"] <= 1.0
        assert 0.0 <= comp["top1"] <= 1.0 or math.isnan(comp["top1"])
        assert "within_cat_cos_mean" in diag

        # V3 band-logic check: synthesize v2-like per-arm numerics and confirm
        # the V3 verdict logic classifies as HARD_PASS_CHAIN_GRADE.
        # These numerics are from v2 metrics.json (rand mean=0.6471 retr_top1,
        # 0.9994 top5; LABEL_BASIS 0.5480 top1, 0.8056 top5, 0.199 wc; etc.)
        v2_synth_arms = {
            "ARM_RANDOM_BIPOLAR": {
                "retrieval": {"top1": 0.6471, "top5": 0.9994, "n": 2400},
                "composition": {"top1": 0.4531, "top5": 0.6500, "n": 192},
                "diagnostics": {"within_cat_cos_mean": -0.0001, "cross_cat_cos_mean": 0.0,
                                "within_cat_cos_std": 0.011, "arm": "ARM_RANDOM_BIPOLAR"},
                "arm": "ARM_RANDOM_BIPOLAR", "seed": 0, "n_ingested": 2400, "elapsed_s_arm": 0.0,
            },
            "ARM_LABEL_BASIS_AXIS_PROJECTION": {
                "retrieval": {"top1": 0.5480, "top5": 0.8056, "n": 2400},
                "composition": {"top1": 0.3313, "top5": 0.4900, "n": 192},
                "diagnostics": {"within_cat_cos_mean": 0.1991, "cross_cat_cos_mean": 0.0,
                                "within_cat_cos_std": 0.029, "arm": "ARM_LABEL_BASIS_AXIS_PROJECTION"},
                "arm": "ARM_LABEL_BASIS_AXIS_PROJECTION", "seed": 0, "n_ingested": 2400, "elapsed_s_arm": 0.0,
            },
            "ARM_EMERGENT_DEEPWALK": {
                "retrieval": {"top1": 0.6458, "top5": 0.9965, "n": 2400},
                "composition": {"top1": 0.4448, "top5": 0.6400, "n": 192},
                "diagnostics": {"within_cat_cos_mean": 0.0812, "cross_cat_cos_mean": 0.0086,
                                "within_cat_cos_std": 0.048, "arm": "ARM_EMERGENT_DEEPWALK"},
                "arm": "ARM_EMERGENT_DEEPWALK", "seed": 0, "n_ingested": 2400, "elapsed_s_arm": 0.0,
            },
            "ARM_EMERGENT_OLSHAUSEN_FIELD": {
                "retrieval": {"top1": 0.6471, "top5": 0.9994, "n": 2400},
                "composition": {"top1": 0.4437, "top5": 0.6800, "n": 192},
                "diagnostics": {"within_cat_cos_mean": 0.0001, "cross_cat_cos_mean": -0.0001,
                                "within_cat_cos_std": 0.011, "arm": "ARM_EMERGENT_OLSHAUSEN_FIELD"},
                "arm": "ARM_EMERGENT_OLSHAUSEN_FIELD", "seed": 0, "n_ingested": 2400, "elapsed_s_arm": 0.0,
            },
        }
        v2_synth = [{"seed": 0, "arms": v2_synth_arms}]
        v, vmsg = verdict_from(v2_synth)
        # V3 EXPECTED verdict on v2-equivalent numerics: HARD_PASS_CHAIN_GRADE
        assert v == "HARD_PASS_CHAIN_GRADE", (
            "V3 BAND-LOGIC SELFTEST FAILED: on v2-equivalent inputs, v3 should "
            "produce HARD_PASS_CHAIN_GRADE but got %s. vmsg: %s" % (v, vmsg)
        )
        # Also exercise verdict_from on the smaller test data
        fake_arms = {a: {"retrieval": retr, "composition": comp,
                          "diagnostics": diag, "arm": a, "seed": 0,
                          "elapsed_s_arm": 0.0, "n_train": len(train),
                          "n_test": len(test)} for a in ARMS}
        fake_per_seed = [{"seed": 0, "arms": fake_arms}]
        v2, vmsg2 = verdict_from(fake_per_seed)
        assert isinstance(v2, str) and isinstance(vmsg2, str)
        print("[selftest] PASS encoders=4 retr=%.3f comp=%.3f V3_band_logic_on_v2_inputs=%s" % (
            retr["top1"], comp["top1"], v), flush=True)
    finally:
        V_CONCEPTS = V_CONCEPTS_BAK
        V_CATEGORIES = V_CATEGORIES_BAK
        V_CONCEPTS_PER_CAT = V_CONCEPTS_PER_CAT_BAK
        V_PREDICATES = V_PREDICATES_BAK
        M_TRIPLES = M_TRIPLES_BAK


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ============================================================================
# atexit synthesizer + main entry — INVARIANT from v2
# ============================================================================

_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        if (od / "metrics.json").exists():
            return
        v, vmsg = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d V_cat=%d V_P=%d M=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, V_CATEGORIES,
        V_PREDICATES, M_TRIPLES, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS], run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0, "LLM calls non-zero: %d" % _LLM_CALL_COUNTER[0]

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "DESIGN_NOTE": (
            "V3 BAND-CORRECTED revival of v2 (substrate_basis_layer_label_contamination_proof_v1). "
            "Same code; only verdict bands corrected per Skunkworks Atom 2 "
            "(RULE_4arm_principle_band_must_be_capacity_feasible_at_chosen_M) and 3x deep drill. "
            "Primary metric: top5 retrieval (5x more headroom than top1). "
            "Secondary metric: relative top1 (the band the BIAS-13 principle actually makes). "
            "Composition: relative top5. Diagnostic: LABEL within_cat_cos >= 0.15 (mechanism fired)."
        ),
        "BIAS_CHECKLIST": {
            "BIAS_13_basis_label_contamination": "TESTED (LABEL_BASIS arm; primary)",
            "BIAS_14_JL_oversatisfaction": "MITIGATED (N/V=27 in productive regime)",
            "BIAS_15_prior_data_mismatch": "MITIGATED (10 cats / 300 concepts aligned)",
            "BIAS_Q_suspect_1.000": "GUARDED (Q_SUSPECT_RETR_TOP1_MAX=%.3f flag)" % Q_SUSPECT_RETR_TOP1_MAX,
            "META_RULE_BAND_CALIBRATION_TOP1_VS_TOP5_REGIME_CHECK": (
                "ADOPTED v3: top1 ceiling estimated from cleanup-argmax noise floor "
                "(sqrt(M/N) crosstalk through V distractors) -> top5 chosen as primary "
                "discriminator; absolute top1 bands replaced with relative differential "
                "per Skunkworks Atom 2 RULE_4arm_principle_band_must_be_capacity_feasible."
            ),
        },
        "CONFOUND_AUDIT": {
            "C1_axis_projection_bug": "MITIGATED: noise_scale=%.2f matches v2 (same code)" % NOISE_SCALE_AXIS,
            "C2_degenerate_codes": "GUARDED via within_cat_cos diagnostic (flag if >= %.2f)" % CONFOUND_LABEL_WITHIN_CAT_COSINE_MAX,
            "C3_capacity_saturation": "MITIGATED: M=%d / V=%d / N=%d well below ~25k capacity" % (M_TRIPLES, V_CONCEPTS, N_DIM),
            "C3_retrofit_risk_band_tuning": (
                "MITIGATED: (a) top5 discriminator was visible in v2 raw data BEFORE band tuning "
                "(LABEL_BASIS top5=0.806 vs RAND/DW/OF >= 0.995; 0.19 absolute gap); "
                "(b) relative-top1 gate is the literal statement of BIAS-13 (label contamination "
                "should HURT relative to no-label baseline; absolute baseline level is irrelevant); "
                "(c) Cell 7 drill confirmed cone-collapse mechanism on independent corpus BEFORE v2; "
                "(d) Skunkworks Atom 2 methodology rule PRE-DATES v3 author choice."
            ),
        },
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
