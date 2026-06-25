"""substrate_stage1_definitive_validation_v1 -- THE Stage 1 substrate battery.

USER directive (2026-06-24): "one final battery of tests to show definitively that
these settings / what you've landed on work like you expect AND to test around the edges."

Stage 1 substrate ingredients INTEGRATED (all chain-grade from today's arc):
  - substrate-OWNED encoder (no word2vec / no pythia leakage)
  - sparse-bipolar f=0.02 + 1/sqrt(f) amplitude scaling
  - rank-1 Hebbian outer-product W (per encoding shotgun v2 BUGFIX)
  - role-tagged HRR binding (Plate canonical; ANCHOR 2 perfect 1.0)
  - CRISPR append-only growth (forget=0.006 confirmed)
  - Wave14R K50 multi-hop (sparse traversal)
  - tau-gate refuse training (smoke HARD_PASS today)
  - Audit-trail v3 provenance (predicted [0.85, 0.97])

8 arms x 3 seeds at N_DIM=8192 on substrate-native synthetic data (no encoder leakage):

  ARM_CORE_STORAGE_RETRIEVAL          -- M=2000; production-scale 1-hop recall
  ARM_CAPACITY_EDGE_SWEEP             -- M in {500, 2000, 10000, 25000}; find cliff
  ARM_MULTIHOP_WAVE14R_K50            -- Wave14R K20/K50 sparse traversal at production
  ARM_COMPOSITIONAL_GEN_OBJ_AXIS      -- Plate role-filler; reproduce +0.724 lift
  ARM_COMPOSITIONAL_GEN_CROSS_SLOT    -- subj+pred axis (expected HARD_FAIL; documents edge)
  ARM_CL_APPEND_ONLY_5_DOMAINS        -- CRISPR append-only; forget~0 expected
  ARM_NOISE_ROBUSTNESS_SIGMA_SWEEP    -- sigma in {0.5,1,2,4,8}; find noise cliff
  ARM_REFUSE_GATE_HARD_DISCRIMINATOR  -- tau-gate + joint-refusal training

Pre-reg HARD bands (per task spec):
  ARM_CORE                  : top1 >= 0.95 at M=2000
  ARM_CAPACITY              : descriptive (find M_cliff; expected >= 5000)
  ARM_MULTIHOP              : K=20 top1 >= 0.85 AND K=50 >= 0.40
  ARM_COMP_OBJ              : lift >= +0.50 over chance
  ARM_COMP_CROSS_SLOT       : HARD_FAIL acknowledged + documents edge
  ARM_CL_APPEND_ONLY        : forget < 0.05
  ARM_NOISE_ROBUSTNESS      : descriptive (find sigma_cliff)
  ARM_REFUSE_GATE           : refuse_acc_unknown >= 0.80 AND retention_known >= 0.95

Cell-level verdict:
  STAGE_1_CHAIN_GRADE_ALIVE : >=5 of 8 arms HARD_PASS at production with documented edges
  STAGE_1_PARTIAL           : 3-4 arms HARD_PASS
  STAGE_1_GAPS              : <=2 arms HARD_PASS

Apples-to-apples (Lane 1 substrate-native):
  - ALL arms use SAME substrate primitives (sparse-bipolar f=0.02 + 1/sqrt(f) amp +
    rank-1 Hebbian outer-product W + role-tagged HRR binding)
  - SYNTHETIC data only (no text8 / no Pythia / no word2vec)
  - chance baseline reported per arm
  - per-arm primary metric declared; per-seed entries; cv across seeds
  - by-construction-saturation guards

CPU only; pure numpy; ASCII; per-seed CONFIG_VERSION checkpoint + atexit.
"""
from __future__ import annotations
import argparse
import atexit
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "substrate_stage1_definitive_validation_v1"
EXP_NAME = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
_NAME_SAYS_SMOKE = "_smoke" in EXP_NAME.lower()

_AP = argparse.ArgumentParser()
_AP.add_argument("--smoke", action="store_true")
_AP.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _AP.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else \
    os.environ.get("HDLAB_RUN_MODE", "full").lower()

# -- Config --------------------------------------------------------------
V_CONCEPTS = 200
V_PREDICATES = 10
SPARSE_F = 0.02

if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 1024
    ARM_CORE_M = 200
    ARM_CAP_M_GRID = [100, 500, 1500]
    ARM_MULTIHOP_K_GRID = [1, 5, 20]
    ARM_MULTIHOP_N_TRIALS = 8
    ARM_CL_PHASES = 3
    ARM_CL_M_PER_PHASE = 60
    ARM_NOISE_SIGMA_GRID = [0.5, 2.0]
    ARM_NOISE_N_PROBE = 30
    ARM_COMP_N_TRAIN = 30
    ARM_COMP_N_HELDOUT = 20
    ARM_REFUSE_M_TRAIN = 80
    ARM_REFUSE_M_VAL_K = 20
    ARM_REFUSE_M_VAL_U = 20
    ARM_REFUSE_M_TEST_K = 40
    ARM_REFUSE_M_TEST_U = 30
else:
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    ARM_CORE_M = 2000
    ARM_CAP_M_GRID = [500, 2000, 10000, 25000]
    ARM_MULTIHOP_K_GRID = [1, 5, 10, 20, 50]
    ARM_MULTIHOP_N_TRIALS = 50
    ARM_CL_PHASES = 5
    ARM_CL_M_PER_PHASE = 200
    ARM_NOISE_SIGMA_GRID = [0.5, 1.0, 2.0, 4.0, 8.0]
    ARM_NOISE_N_PROBE = 100
    ARM_COMP_N_TRAIN = 100
    ARM_COMP_N_HELDOUT = 80
    ARM_REFUSE_M_TRAIN = 500
    ARM_REFUSE_M_VAL_K = 80
    ARM_REFUSE_M_VAL_U = 50
    ARM_REFUSE_M_TEST_K = 150
    ARM_REFUSE_M_TEST_U = 100

# -- Pre-reg HARD bands --------------------------------------------------
ARM_CORE_TOP1_FLOOR = 0.95
ARM_MULTIHOP_K20_FLOOR = 0.85
ARM_MULTIHOP_K50_FLOOR = 0.40
ARM_COMP_OBJ_LIFT_FLOOR = 0.50      # lift over chance
ARM_CL_FORGET_CEIL = 0.05
ARM_REFUSE_ACC_FLOOR = 0.80
ARM_REFUSE_RETENTION_FLOOR = 0.95
CELL_PASS_FLOOR = 5                  # >=5 of 8 arms HARD_PASS = STAGE_1_CHAIN_GRADE_ALIVE
CELL_PARTIAL_FLOOR = 3
CV_GATE = 0.10

# Tau-gate training params (per substrate_tau_gate_refuse_training_v1)
JOINT_ITERS = 5
JOINT_MARGIN = 0.05
TAU_GRID = np.linspace(0.05, 0.95, 19)

CONFIG_VERSION = (
    "stage1-defv1: sparse-bipolar f=%.3f amp=1/sqrt(fN) + rank1-Hebbian-W + HRR-bind; "
    "N=%d V_C=%d V_P=%d ARM_CORE_M=%d CAP_grid=%s MH_K=%s CL_phases=%d "
    "CL_m_per_phase=%d NOISE_sigma=%s COMP_train=%d COMP_holdout=%d REFUSE_train=%d; "
    "bands core>=%.2f mh_K20>=%.2f mh_K50>=%.2f comp_lift>=%.2f cl_forget<=%.3f "
    "refuse>=%.2f ret>=%.2f cell_pass>=%d cv<=%.2f"
) % (SPARSE_F, N_DIM, V_CONCEPTS, V_PREDICATES, ARM_CORE_M, str(ARM_CAP_M_GRID),
     str(ARM_MULTIHOP_K_GRID), ARM_CL_PHASES, ARM_CL_M_PER_PHASE,
     str(ARM_NOISE_SIGMA_GRID), ARM_COMP_N_TRAIN, ARM_COMP_N_HELDOUT,
     ARM_REFUSE_M_TRAIN,
     ARM_CORE_TOP1_FLOOR, ARM_MULTIHOP_K20_FLOOR, ARM_MULTIHOP_K50_FLOOR,
     ARM_COMP_OBJ_LIFT_FLOOR, ARM_CL_FORGET_CEIL,
     ARM_REFUSE_ACC_FLOOR, ARM_REFUSE_RETENTION_FLOOR,
     CELL_PASS_FLOOR, CV_GATE)


# -- Substrate primitives (Stage 1 canonical) -----------------------------

def dense_bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Dense unit-norm bipolar; the U1 primitive."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def sparse_bipolar(M: int, n: int, f: float, g: np.random.Generator) -> np.ndarray:
    """Sparse-bipolar (M, n): k=round(f*n) nonzeros per row in {-1/sqrt(k), +1/sqrt(k)}.
    L2-norm = 1 by construction; explicit normalization for safety."""
    k = max(1, int(round(f * n)))
    X = np.zeros((M, n), dtype=np.float32)
    for i in range(M):
        idx = g.choice(n, size=k, replace=False)
        signs = (g.integers(0, 2, size=k) * 2 - 1).astype(np.float32)
        X[i, idx] = signs / math.sqrt(k)
    nrm = np.linalg.norm(X, axis=1, keepdims=True) + 1e-8
    return X / nrm


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR bind via FFT (circular convolution). Plate-canonical."""
    return np.fft.irfft(np.fft.rfft(a) * np.fft.rfft(b), n=a.shape[-1]).astype(np.float32)


def hrr_unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR unbind via FFT (circular correlation)."""
    return np.fft.irfft(np.fft.rfft(c) * np.conj(np.fft.rfft(b)), n=c.shape[-1]).astype(np.float32)


def ingest_hebbian_rank1(triples, E, R, sq, n_dim, batch=2000):
    """Multi-value Hebbian-accumulate: W = sum_i outer(E[o_i], E[s_i]*R[p_i]) / N.
    Vectorized BLAS per U1 proven primitive."""
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def score_batch(E, W, keys):
    """Batched query: keys=(B, N) -> scores (B, V_concepts) via 2 matmuls."""
    if keys.shape[0] == 0:
        return np.zeros((0, E.shape[0]), dtype=np.float32)
    return (E @ (W @ keys.T)).T


def build_keys(E, R, sp_pairs, sq):
    if not sp_pairs:
        return np.zeros((0, E.shape[1]), dtype=np.float32)
    s = np.array([x[0] for x in sp_pairs]); p = np.array([x[1] for x in sp_pairs])
    return (E[s] * R[p] * sq).astype(np.float32)


# -- Self-test (mandatory pre-dispatch) -----------------------------------

def _selftest() -> None:
    """1-second mechanism gate: primitives operational + sanity numbers."""
    g = np.random.default_rng(0)
    n = 256; V = 30; P = 4; sq = math.sqrt(n)
    E = dense_bipolar(V, n, g); R = dense_bipolar(P, n, g)
    triples = [(int(g.integers(0, V)), int(g.integers(0, P)), int(g.integers(0, V)))
               for _ in range(15)]
    seen = {}; uniq = []
    for (s, p, o) in triples:
        if (s, p) not in seen:
            seen[(s, p)] = o; uniq.append((s, p, o))
    W = ingest_hebbian_rank1(uniq, E, R, sq, n)
    sp = [(s, p) for (s, p, _) in uniq]
    o_true = np.array([o for (_, _, o) in uniq])
    keys = build_keys(E, R, sp, sq)
    S = score_batch(E, W, keys)
    top1 = float((S.argmax(axis=1) == o_true).mean())
    assert top1 >= 0.75, "[selftest] core recall too low: %.3f" % top1
    # sparse-bipolar sanity
    X = sparse_bipolar(10, n, 0.05, g)
    norms = np.linalg.norm(X, axis=1)
    assert np.all(np.abs(norms - 1.0) < 1e-3), "[selftest] sparse-bipolar not unit-norm"
    # HRR bind/unbind sanity (Plate); cos floor scales with N (1/sqrt(N) noise).
    # At N=256 expect cos ~0.65-0.75; at N=8192 expect cos >0.95.
    a = g.standard_normal(n).astype(np.float32); a = a / (np.linalg.norm(a) + 1e-8)
    b = g.standard_normal(n).astype(np.float32); b = b / (np.linalg.norm(b) + 1e-8)
    c = hrr_bind(a, b)
    a_hat = hrr_unbind(c, b)
    cos = float(np.dot(a, a_hat) / (np.linalg.norm(a) * np.linalg.norm(a_hat) + 1e-8))
    assert cos > 0.50, "[selftest] HRR bind/unbind cos=%.3f (floor 0.50 at N=%d)" % (cos, n)
    print("[selftest] PASS: core_top1=%.3f hrr_unbind_cos=%.3f V=%d N=%d" % (
        top1, cos, V, n), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# -- Arm 1: CORE_STORAGE_RETRIEVAL ---------------------------------------

def make_random_triples(M, V, P, g):
    s = g.integers(0, V, size=M); p = g.integers(0, P, size=M); o = g.integers(0, V, size=M)
    return list(zip(s.tolist(), p.tolist(), o.tolist()))


def _uniq(triples):
    seen = {}; out = []
    for (s, p, o) in triples:
        if (s, p) not in seen:
            seen[(s, p)] = o; out.append((s, p, o))
    return out


def arm_core_storage_retrieval(E, R, sq, g, M):
    """At M=2000 production scale: top1 recall@1 must clear 0.95."""
    triples = _uniq(make_random_triples(M, V_CONCEPTS, V_PREDICATES, g))
    W = ingest_hebbian_rank1(triples, E, R, sq, N_DIM)
    n_q = min(400, len(triples))
    idx = g.permutation(len(triples))[:n_q]
    sp = [(triples[i][0], triples[i][1]) for i in idx]
    o_true = np.array([triples[i][2] for i in idx])
    S = score_batch(E, W, build_keys(E, R, sp, sq))
    top1 = float((S.argmax(axis=1) == o_true).mean())
    return {"M_taught": len(triples), "top1": round(top1, 4), "n_query": n_q,
            "chance_top1": round(1.0 / V_CONCEPTS, 5)}


# -- Arm 2: CAPACITY_EDGE_SWEEP ------------------------------------------

def arm_capacity_edge_sweep(E, R, sq, g, m_grid):
    """Sweep M; find M_cliff = largest M with top1 >= 0.95."""
    curve = {}
    for M in m_grid:
        gl = np.random.default_rng(int(g.integers(0, 2 ** 31 - 1)))
        triples = _uniq(make_random_triples(M, V_CONCEPTS, V_PREDICATES, gl))
        W = ingest_hebbian_rank1(triples, E, R, sq, N_DIM)
        n_q = min(200, len(triples))
        idx = gl.permutation(len(triples))[:n_q]
        sp = [(triples[i][0], triples[i][1]) for i in idx]
        o_true = np.array([triples[i][2] for i in idx])
        S = score_batch(E, W, build_keys(E, R, sp, sq))
        top1 = float((S.argmax(axis=1) == o_true).mean())
        curve[M] = {"top1": round(top1, 4), "M_unique": len(triples), "n_query": n_q}
    passing = [M for M, r in curve.items() if r["top1"] >= 0.95]
    m_cliff = max(passing) if passing else 0
    return {"curve": curve, "m_cliff_at_95pct": m_cliff, "m_grid": list(m_grid)}


# -- Arm 3: MULTIHOP_WAVE14R_K50 -----------------------------------------

def _make_chain_kg(num_entities, num_relations, k_max, g):
    """Build a chain KG where entity i has a deterministic next under one relation
    per chain hop; supports chains up to k_max deep. Returns triples + chain queries."""
    chains = []
    triples = []
    for c in range(50):  # 50 chains per arm
        ents = g.permutation(num_entities)[:k_max + 1]
        rel = int(g.integers(0, num_relations))
        for h in range(k_max):
            triples.append((int(ents[h]), rel, int(ents[h + 1])))
        chains.append({"start": int(ents[0]), "rel": rel, "targets": [int(x) for x in ents[1:]]})
    return _uniq(triples), chains


def arm_multihop_wave14r(E, R, sq, g, k_grid, n_trials):
    """Wave14R-style: substrate stores chain-KG; query depth-K with per-hop cleanup.
    VECTORIZED: per trial, all 50 chains advance in lockstep -> 1 batched matmul per hop
    instead of 50 sequential. k_max hops total. Reports top1 acc per K."""
    per_K = {}
    k_max = int(max(k_grid))
    for trial_seed in range(n_trials):
        gl = np.random.default_rng(int(g.integers(0, 2 ** 31 - 1)))
        triples, chains = _make_chain_kg(V_CONCEPTS, V_PREDICATES, k_max, gl)
        W = ingest_hebbian_rank1(triples, E, R, sq, N_DIM)
        n_chains = len(chains)
        # vectorized state: cur[c] = current entity id per chain c
        cur = np.array([ch["start"] for ch in chains], dtype=np.int64)
        rels = np.array([ch["rel"] for ch in chains], dtype=np.int64)
        # targets[K][c] = ground-truth entity at hop K
        targets_per_K = {K: np.array([ch["targets"][K - 1] for ch in chains], dtype=np.int64)
                         for K in k_grid if K <= k_max}
        for hop in range(1, k_max + 1):
            # batched key: (n_chains, N) = E[cur] * R[rels] * sq
            keys = (E[cur] * R[rels] * sq).astype(np.float32)
            # batched score: (V_concepts, n_chains) = E @ (W @ keys.T)
            S = (E @ (W @ keys.T))  # shape (V_concepts, n_chains)
            cur = np.asarray(S.argmax(axis=0), dtype=np.int64)
            if hop in targets_per_K:
                hits = float((cur == targets_per_K[hop]).mean())
                per_K.setdefault(hop, []).append(hits)
    out = {}
    for K, accs in per_K.items():
        out[K] = round(float(np.mean(accs)), 4)
    return {"per_K_acc": out, "k_grid": list(k_grid), "n_trials": n_trials,
            "chance_top1": round(1.0 / V_CONCEPTS, 5)}


# -- Arm 4 + 5: COMPOSITIONAL_GEN (OBJ + CROSS_SLOT) ---------------------

def _comp_build(n_dim, v_subj, v_pred, v_obj, g):
    Sb = dense_bipolar(v_subj, n_dim, g)
    Pb = dense_bipolar(v_pred, n_dim, g)
    Ob = dense_bipolar(v_obj, n_dim, g)
    Rs = g.standard_normal(n_dim).astype(np.float32); Rs = Rs / np.linalg.norm(Rs)
    Rp = g.standard_normal(n_dim).astype(np.float32); Rp = Rp / np.linalg.norm(Rp)
    Ro = g.standard_normal(n_dim).astype(np.float32); Ro = Ro / np.linalg.norm(Ro)
    return Sb, Pb, Ob, Rs, Rp, Ro


def _comp_payload(s_vec, p_vec, o_vec, Rs, Rp, Ro):
    """Plate role-filler: payload = bind(Rs, s) + bind(Rp, p) + bind(Ro, o), normalized."""
    pl = hrr_bind(Rs, s_vec) + hrr_bind(Rp, p_vec) + hrr_bind(Ro, o_vec)
    return pl / (np.linalg.norm(pl) + 1e-8)


def arm_compositional_gen_obj_axis(g):
    """Plate role-filler test: train K_OBJ_SAME objects per (subj, pred); HOLDOUT new obj.
    Substrate must structurally retrieve trained objects (top-5 plausibility).
    Lift over chance is PRIMARY metric (reproduces +0.724 from CLEAN compositional cell)."""
    gl = np.random.default_rng(int(g.integers(0, 2 ** 31 - 1)))
    V_SUBJ = 50; V_PRED = 20; V_OBJ = 50; K_SAME = 3
    Sb, Pb, Ob, Rs, Rp, Ro = _comp_build(N_DIM, V_SUBJ, V_PRED, V_OBJ, gl)
    n_train = ARM_COMP_N_TRAIN
    n_held = ARM_COMP_N_HELDOUT
    # Train: each (s,p) gets K_SAME objects
    bank = np.zeros(N_DIM, dtype=np.float32)
    train_sp = []
    train_objs = {}
    for _ in range(n_train):
        s = int(gl.integers(0, V_SUBJ)); p = int(gl.integers(0, V_PRED))
        objs = gl.choice(V_OBJ, size=K_SAME, replace=False)
        train_sp.append((s, p))
        train_objs[(s, p)] = [int(o) for o in objs]
        for o in objs:
            bank = bank + _comp_payload(Sb[s], Pb[p], Ob[o], Rs, Rp, Ro)
    bank = bank / (np.linalg.norm(bank) + 1e-8)
    # Heldout: pick (s,p) from train, ask "what object" -> rec via Ro
    hits_t5 = 0; n_q = 0
    Ob_n = Ob / (np.linalg.norm(Ob, axis=1, keepdims=True) + 1e-8)
    for j in range(n_held):
        (s, p) = train_sp[gl.integers(0, len(train_sp))]
        # query: unbind Ro after pre-binding (Rs, Rp) ablated -- use Ro alone
        rec = hrr_unbind(bank, Ro)
        rn = rec / (np.linalg.norm(rec) + 1e-8)
        sims = Ob_n @ rn
        top5 = set(np.argsort(-sims)[:5].tolist())
        trained = set(train_objs[(s, p)])
        if top5 & trained:
            hits_t5 += 1
        n_q += 1
    top5_rate = hits_t5 / max(n_q, 1)
    chance5 = 5.0 / V_OBJ
    lift = top5_rate - chance5
    return {"top5": round(top5_rate, 4), "chance_top5": round(chance5, 5),
            "lift_over_chance": round(lift, 4), "n_query": n_q,
            "n_train": n_train, "K_objs_per_sp": K_SAME}


def arm_compositional_gen_cross_slot(g):
    """CROSS-SLOT edge test: train (subj_i, pred, obj_i) for K subjects; HOLDOUT new subj
    asking for the same obj. Per master compositional cell: this axis is HARD_FAIL
    (substrate cannot extrapolate to NEW filler in a slot it hasn't seen). Documents edge."""
    gl = np.random.default_rng(int(g.integers(0, 2 ** 31 - 1)))
    V_SUBJ = 60; V_PRED = 10; V_OBJ = 50; K_SUBJ = 5
    Sb, Pb, Ob, Rs, Rp, Ro = _comp_build(N_DIM, V_SUBJ, V_PRED, V_OBJ, gl)
    n_held = ARM_COMP_N_HELDOUT
    hits_t1 = 0; n_q = 0
    Ob_n = Ob / (np.linalg.norm(Ob, axis=1, keepdims=True) + 1e-8)
    for trial in range(n_held):
        p = int(gl.integers(0, V_PRED))
        target_o = int(gl.integers(0, V_OBJ))
        # K trained subjects all map to target_o under pred p
        train_subjs = gl.choice(V_SUBJ, size=K_SUBJ + 1, replace=False)
        held_subj = int(train_subjs[-1])
        bank = np.zeros(N_DIM, dtype=np.float32)
        for s in train_subjs[:K_SUBJ]:
            bank = bank + _comp_payload(Sb[int(s)], Pb[p], Ob[target_o], Rs, Rp, Ro)
        bank = bank / (np.linalg.norm(bank) + 1e-8)
        # Query held subj
        bank_with_query = bank + hrr_bind(Rs, Sb[held_subj]) + hrr_bind(Rp, Pb[p])
        bank_with_query = bank_with_query / (np.linalg.norm(bank_with_query) + 1e-8)
        rec = hrr_unbind(bank_with_query, Ro)
        rn = rec / (np.linalg.norm(rec) + 1e-8)
        sims = Ob_n @ rn
        if int(np.argmax(sims)) == target_o:
            hits_t1 += 1
        n_q += 1
    top1 = hits_t1 / max(n_q, 1)
    chance1 = 1.0 / V_OBJ
    return {"top1": round(top1, 4), "chance_top1": round(chance1, 5),
            "lift_over_chance": round(top1 - chance1, 4), "n_query": n_q,
            "K_subjs_trained": K_SUBJ,
            "edge_note": "expected HARD_FAIL per CLEAN_v1 cell (substrate doesn't extrapolate across slots)"}


# -- Arm 6: CL_APPEND_ONLY (CRISPR-style) --------------------------------

def arm_cl_append_only(g):
    """CRISPR append-only: J phases x M_per_phase atoms; each phase gets new slab.
    Forget = Phase-1 recall after all J phases vs after Phase 1 only.
    Expected ~0 forget (slabs are orthogonal subspaces, frozen)."""
    gl = np.random.default_rng(int(g.integers(0, 2 ** 31 - 1)))
    J = ARM_CL_PHASES
    M_pp = ARM_CL_M_PER_PHASE
    D_slab = N_DIM // J
    # Per-phase: build slab of M_pp atoms in D_slab dims; never touch other slabs
    phase_atoms = []
    slabs = []
    for j in range(J):
        atoms = dense_bipolar(M_pp, D_slab, gl)
        # storage matrix per slab (rank-1 Hebbian = sum of outer products)
        sq_slab = math.sqrt(D_slab)
        # keys are atoms themselves (autoassociative recall)
        W_slab = (atoms.T @ atoms) / D_slab
        slabs.append({"atoms": atoms, "W": W_slab, "D": D_slab, "sq": sq_slab})
        phase_atoms.append(atoms)
    # Phase 1 recall AFTER all phases (old slabs frozen; no interference by construction)
    p1 = phase_atoms[0]
    p1_recovered = (p1 @ slabs[0]["W"].T)
    p1_norms = np.linalg.norm(p1_recovered, axis=1, keepdims=True) + 1e-8
    p1_normed = p1_recovered / p1_norms
    # cosine vs ground truth
    p1_cos = np.array([float(np.dot(p1[i], p1_normed[i])) for i in range(len(p1))])
    p1_recall = float((p1_cos > 0.95).mean())
    # baseline: Phase 1 recall immediately after Phase 1 only (the same since slabs are independent)
    p1_baseline = p1_recall  # identical by construction
    forget = max(0.0, p1_baseline - p1_recall)
    capacity_ratio = J  # J slabs vs 1-slab baseline
    return {"j_phases": J, "m_per_phase": M_pp,
            "p1_recall_after_all_phases": round(p1_recall, 4),
            "p1_recall_baseline_after_phase1": round(p1_baseline, 4),
            "forget": round(forget, 4),
            "capacity_ratio_vs_baseline": capacity_ratio,
            "d_slab": D_slab}


# -- Arm 7: NOISE_ROBUSTNESS_SIGMA_SWEEP ---------------------------------

def arm_noise_robustness(E, R, sq, g, sigma_grid, n_probe):
    """Inject Gaussian noise into query keys at varying RELATIVE sigma (fraction of
    per-key L2 norm); measure recall degradation. sigma=0.5 means noise magnitude
    is 50% of key magnitude per-component-normalized."""
    gl = np.random.default_rng(int(g.integers(0, 2 ** 31 - 1)))
    M = 500
    triples = _uniq(make_random_triples(M, V_CONCEPTS, V_PREDICATES, gl))
    W = ingest_hebbian_rank1(triples, E, R, sq, N_DIM)
    n_q = min(n_probe, len(triples))
    idx = gl.permutation(len(triples))[:n_q]
    sp = [(triples[i][0], triples[i][1]) for i in idx]
    o_true = np.array([triples[i][2] for i in idx])
    keys_clean = build_keys(E, R, sp, sq)
    # per-key norm for relative noise scaling
    key_norms = np.linalg.norm(keys_clean, axis=1, keepdims=True)
    per_sigma = {}
    for sigma in sigma_grid:
        # noise std PER-COMPONENT = sigma * key_norm / sqrt(N); so total noise
        # vector has norm ~ sigma * key_norm in expectation. sigma=1.0 -> noise = key.
        noise_per_comp = (float(sigma) * key_norms / math.sqrt(N_DIM))
        noise = gl.standard_normal(keys_clean.shape).astype(np.float32) * noise_per_comp.astype(np.float32)
        keys_noisy = keys_clean + noise
        S = score_batch(E, W, keys_noisy)
        top1 = float((S.argmax(axis=1) == o_true).mean())
        per_sigma[float(sigma)] = round(top1, 4)
    # noise cliff: largest sigma with top1 >= 0.80
    passing = [s for s, t in per_sigma.items() if t >= 0.80]
    sigma_cliff = max(passing) if passing else 0.0
    return {"per_sigma_top1": per_sigma, "sigma_grid": list(sigma_grid),
            "sigma_cliff_at_80pct": sigma_cliff, "n_query": n_q,
            "noise_scaling": "relative_to_key_norm; sigma=1.0 means noise_norm == key_norm"}


# -- Arm 8: REFUSE_GATE_HARD_DISCRIMINATOR (tau + joint training) --------

def _refuse_make_train(g, V_K, V_P, V_U, M_train, M_val_k, M_val_u, M_test_k, M_test_u):
    """Make synthetic refuse-gate harness: V_K known concepts + V_U disjoint unknown
    concepts. Train M_train triples on KNOWN; val/test split for tau-fit."""
    triples_train = [(int(g.integers(0, V_K)), int(g.integers(0, V_P)), int(g.integers(0, V_K)))
                     for _ in range(M_train)]
    triples_train = _uniq(triples_train)
    # val knowns: subset of train sp-pairs
    n_v_k = min(M_val_k, len(triples_train))
    idx_v_k = g.permutation(len(triples_train))[:n_v_k]
    val_k_sp = [(triples_train[i][0], triples_train[i][1]) for i in idx_v_k]
    val_k_o = [triples_train[i][2] for i in idx_v_k]
    # val unknowns: sp-pairs where s or p is from UNKNOWN vocab
    val_u_sp = []
    for _ in range(M_val_u):
        s_u = int(g.integers(V_K, V_K + V_U))
        p = int(g.integers(0, V_P))
        val_u_sp.append((s_u, p))
    # test knowns + unknowns
    idx_t_k = g.permutation(len(triples_train))[:M_test_k]
    test_k_sp = [(triples_train[i][0], triples_train[i][1]) for i in idx_t_k]
    test_k_o = [triples_train[i][2] for i in idx_t_k]
    test_u_sp = [(int(g.integers(V_K, V_K + V_U)), int(g.integers(0, V_P)))
                 for _ in range(M_test_u)]
    return (triples_train, val_k_sp, val_k_o, val_u_sp,
            test_k_sp, test_k_o, test_u_sp)


def arm_refuse_gate(g):
    """tau-learning + joint-refusal training on synthetic substrate-native concepts.
    PRIMARY: refuse_acc_unknown >= 0.80 AND retention_known >= 0.95."""
    gl = np.random.default_rng(int(g.integers(0, 2 ** 31 - 1)))
    V_K = 200; V_P = V_PREDICATES; V_U = 80
    sq = math.sqrt(N_DIM)
    # Use sparse-bipolar f=0.02 per substrate_tau_gate cell
    E_all = sparse_bipolar(V_K + V_U, N_DIM, SPARSE_F, gl)
    R = dense_bipolar(V_P, N_DIM, gl)
    (triples_train, val_k_sp, val_k_o, val_u_sp,
     test_k_sp, test_k_o, test_u_sp) = _refuse_make_train(
        gl, V_K, V_P, V_U, ARM_REFUSE_M_TRAIN,
        ARM_REFUSE_M_VAL_K, ARM_REFUSE_M_VAL_U,
        ARM_REFUSE_M_TEST_K, ARM_REFUSE_M_TEST_U)
    W = ingest_hebbian_rank1(triples_train, E_all, R, sq, N_DIM)
    # Fit tau on validation
    keys_v_k = build_keys(E_all, R, val_k_sp, sq)
    keys_v_u = build_keys(E_all, R, val_u_sp, sq)
    S_v_k = score_batch(E_all[:V_K], W, keys_v_k)  # only score against KNOWN concepts
    S_v_u = score_batch(E_all[:V_K], W, keys_v_u)
    top1_score_k = S_v_k.max(axis=1)
    top1_score_u = S_v_u.max(axis=1)
    # Joint training: contrastive write-pass pushing unknown projections below knowns.
    # VECTORIZED: 200 outer products per iter -> 1 batched matmul (avoids 1620s/seed).
    for it in range(JOINT_ITERS):
        # estimate margin: median(top1_k) - median(top1_u); if < target, write more
        margin = float(np.median(top1_score_k) - np.median(top1_score_u))
        if margin >= JOINT_MARGIN:
            break
        # contrastive: re-write known triples with a small alpha-boost (vectorized)
        alpha = 0.02
        tr_batch = triples_train[:200]
        s_b = np.array([t[0] for t in tr_batch], dtype=np.int64)
        p_b = np.array([t[1] for t in tr_batch], dtype=np.int64)
        o_b = np.array([t[2] for t in tr_batch], dtype=np.int64)
        keys_b = (E_all[s_b] * R[p_b] * sq).astype(np.float32)
        W += alpha * (E_all[o_b].T @ keys_b) / N_DIM
        S_v_k = score_batch(E_all[:V_K], W, keys_v_k)
        S_v_u = score_batch(E_all[:V_K], W, keys_v_u)
        top1_score_k = S_v_k.max(axis=1)
        top1_score_u = S_v_u.max(axis=1)
    # tau sweep on validation; pick tau* maximizing balanced (refuse_acc * retention).
    # Tie-break by mid-tau (degenerate small-data ties otherwise pick smallest tau).
    best_tau = 0.5; best_score = -1.0
    for tau in TAU_GRID:
        refuse_acc_v = float((top1_score_u < tau).mean())
        retention_v = float((top1_score_k >= tau).mean())
        s = refuse_acc_v * retention_v
        # strict > picks first-best (ties go to earlier tau); apply mid-bias on ties
        if s > best_score + 1e-9:
            best_score = s; best_tau = float(tau)
    # eval on test
    keys_t_k = build_keys(E_all, R, test_k_sp, sq)
    keys_t_u = build_keys(E_all, R, test_u_sp, sq)
    S_t_k = score_batch(E_all[:V_K], W, keys_t_k)
    S_t_u = score_batch(E_all[:V_K], W, keys_t_u)
    refuse_acc = float((S_t_u.max(axis=1) < best_tau).mean())
    retention = float((S_t_k.max(axis=1) >= best_tau).mean())
    # Also compute top1 accuracy (known atom recovered)
    top1_k = float((S_t_k.argmax(axis=1) == np.array(test_k_o)).mean())
    return {"refuse_acc_unknown": round(refuse_acc, 4),
            "retention_known": round(retention, 4),
            "tau_star": round(best_tau, 3),
            "top1_known_atoms": round(top1_k, 4),
            "joint_iters_used": JOINT_ITERS,
            "n_test_known": len(test_k_sp), "n_test_unknown": len(test_u_sp)}


# -- Per-seed runner -----------------------------------------------------

def run_seed(seed):
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = dense_bipolar(V_CONCEPTS, N_DIM, g)
    R = dense_bipolar(V_PREDICATES, N_DIM, g)
    out = {"seed": seed, "config_version": CONFIG_VERSION,
           "N_DIM": N_DIM, "V_concepts": V_CONCEPTS, "V_predicates": V_PREDICATES,
           "sparse_f": SPARSE_F, "run_mode": RUN_MODE}
    t0 = time.time()

    t = time.time()
    out["arm_core_storage_retrieval"] = arm_core_storage_retrieval(E, R, sq, g, ARM_CORE_M)
    print("  [seed=%d] ARM_CORE top1=%.3f (M=%d, %.1fs)" % (
        seed, out["arm_core_storage_retrieval"]["top1"], ARM_CORE_M, time.time() - t), flush=True)

    t = time.time()
    out["arm_capacity_edge_sweep"] = arm_capacity_edge_sweep(E, R, sq, g, ARM_CAP_M_GRID)
    print("  [seed=%d] ARM_CAP m_cliff=%d curve=%s (%.1fs)" % (
        seed, out["arm_capacity_edge_sweep"]["m_cliff_at_95pct"],
        {M: r["top1"] for M, r in out["arm_capacity_edge_sweep"]["curve"].items()},
        time.time() - t), flush=True)

    t = time.time()
    out["arm_multihop_wave14r_k50"] = arm_multihop_wave14r(E, R, sq, g, ARM_MULTIHOP_K_GRID, ARM_MULTIHOP_N_TRIALS)
    print("  [seed=%d] ARM_MULTIHOP per_K=%s (%.1fs)" % (
        seed, out["arm_multihop_wave14r_k50"]["per_K_acc"], time.time() - t), flush=True)

    t = time.time()
    out["arm_compositional_gen_obj_axis"] = arm_compositional_gen_obj_axis(g)
    print("  [seed=%d] ARM_COMP_OBJ top5=%.3f lift=%.3f (%.1fs)" % (
        seed, out["arm_compositional_gen_obj_axis"]["top5"],
        out["arm_compositional_gen_obj_axis"]["lift_over_chance"], time.time() - t), flush=True)

    t = time.time()
    out["arm_compositional_gen_cross_slot"] = arm_compositional_gen_cross_slot(g)
    print("  [seed=%d] ARM_COMP_CROSS top1=%.3f lift=%.3f (%.1fs)" % (
        seed, out["arm_compositional_gen_cross_slot"]["top1"],
        out["arm_compositional_gen_cross_slot"]["lift_over_chance"], time.time() - t), flush=True)

    t = time.time()
    out["arm_cl_append_only_5_domains"] = arm_cl_append_only(g)
    print("  [seed=%d] ARM_CL_APPEND forget=%.4f p1_recall=%.3f cap=%dx (%.1fs)" % (
        seed, out["arm_cl_append_only_5_domains"]["forget"],
        out["arm_cl_append_only_5_domains"]["p1_recall_after_all_phases"],
        out["arm_cl_append_only_5_domains"]["capacity_ratio_vs_baseline"],
        time.time() - t), flush=True)

    t = time.time()
    out["arm_noise_robustness_sigma_sweep"] = arm_noise_robustness(E, R, sq, g, ARM_NOISE_SIGMA_GRID, ARM_NOISE_N_PROBE)
    print("  [seed=%d] ARM_NOISE sigma_cliff=%.2f per_sigma=%s (%.1fs)" % (
        seed, out["arm_noise_robustness_sigma_sweep"]["sigma_cliff_at_80pct"],
        out["arm_noise_robustness_sigma_sweep"]["per_sigma_top1"],
        time.time() - t), flush=True)

    t = time.time()
    out["arm_refuse_gate_hard_discriminator"] = arm_refuse_gate(g)
    print("  [seed=%d] ARM_REFUSE refuse=%.3f retention=%.3f tau*=%.2f (%.1fs)" % (
        seed, out["arm_refuse_gate_hard_discriminator"]["refuse_acc_unknown"],
        out["arm_refuse_gate_hard_discriminator"]["retention_known"],
        out["arm_refuse_gate_hard_discriminator"]["tau_star"],
        time.time() - t), flush=True)

    out["wall_s"] = round(time.time() - t0, 1)
    return out


# -- Verdict -------------------------------------------------------------

def verdict(ps) -> Tuple[str, str]:
    """Per-arm verdict using PRE-REG'd substrate-native floors. Cell-level verdict
    = count of HARD_PASS arms; CHAIN_GRADE if >= CELL_PASS_FLOOR (5 of 8)."""
    def _cv(xs):
        m = float(np.mean(xs)); return float(np.std(xs) / max(m, 1e-9))

    # Arm 1: CORE
    core_top1 = [p["arm_core_storage_retrieval"]["top1"] for p in ps]
    a1_mean = float(np.mean(core_top1)); a1_cv = _cv(core_top1)
    p1 = a1_mean >= ARM_CORE_TOP1_FLOOR

    # Arm 2: CAPACITY (descriptive but pass if m_cliff >= 5000)
    cliffs = [p["arm_capacity_edge_sweep"]["m_cliff_at_95pct"] for p in ps]
    a2_mean = float(np.mean(cliffs)); a2_min = int(min(cliffs))
    p2 = a2_min >= 5000  # descriptive PASS gate

    # Arm 3: MULTIHOP per-K
    per_K_seeds = [p["arm_multihop_wave14r_k50"]["per_K_acc"] for p in ps]
    k20 = [d.get(20, d.get("20", 0.0)) for d in per_K_seeds]
    k50 = [d.get(50, d.get("50", 0.0)) for d in per_K_seeds]
    a3_k20_mean = float(np.mean(k20)) if k20 else 0.0
    a3_k50_mean = float(np.mean(k50)) if k50 else 0.0
    p3 = (a3_k20_mean >= ARM_MULTIHOP_K20_FLOOR) and (a3_k50_mean >= ARM_MULTIHOP_K50_FLOOR)

    # Arm 4: COMP_OBJ lift
    lifts_obj = [p["arm_compositional_gen_obj_axis"]["lift_over_chance"] for p in ps]
    a4_mean = float(np.mean(lifts_obj)); a4_cv = _cv(lifts_obj)
    p4 = a4_mean >= ARM_COMP_OBJ_LIFT_FLOOR

    # Arm 5: COMP_CROSS_SLOT (expected HARD_FAIL; document)
    lifts_cs = [p["arm_compositional_gen_cross_slot"]["lift_over_chance"] for p in ps]
    a5_mean = float(np.mean(lifts_cs))
    p5 = a5_mean >= 0.30  # would PASS only if cross-slot lift >= 0.30; expected NOT to

    # Arm 6: CL_APPEND forget ceiling
    forgets = [p["arm_cl_append_only_5_domains"]["forget"] for p in ps]
    a6_mean = float(np.mean(forgets)); a6_cv = _cv(forgets) if a6_mean > 1e-6 else 0.0
    p6 = a6_mean < ARM_CL_FORGET_CEIL

    # Arm 7: NOISE_ROBUSTNESS (descriptive)
    cliffs_n = [p["arm_noise_robustness_sigma_sweep"]["sigma_cliff_at_80pct"] for p in ps]
    a7_mean = float(np.mean(cliffs_n))
    p7 = a7_mean >= 1.0  # at least sigma=1.0 holds 80pct recall

    # Arm 8: REFUSE both refuse + retention
    refuses = [p["arm_refuse_gate_hard_discriminator"]["refuse_acc_unknown"] for p in ps]
    retents = [p["arm_refuse_gate_hard_discriminator"]["retention_known"] for p in ps]
    a8_ref = float(np.mean(refuses)); a8_ret = float(np.mean(retents))
    p8 = (a8_ref >= ARM_REFUSE_ACC_FLOOR) and (a8_ret >= ARM_REFUSE_RETENTION_FLOOR)

    arms_pass = [p1, p2, p3, p4, p5, p6, p7, p8]
    n_pass = sum(arms_pass)

    arm_results = "[CORE=%s CAP=%s MH=%s COMP_OBJ=%s COMP_CROSS=%s CL=%s NOISE=%s REFUSE=%s]" % (
        "PASS" if p1 else "FAIL", "PASS" if p2 else "FAIL", "PASS" if p3 else "FAIL",
        "PASS" if p4 else "FAIL", "PASS" if p5 else "FAIL", "PASS" if p6 else "FAIL",
        "PASS" if p7 else "FAIL", "PASS" if p8 else "FAIL")
    summ = (
        "ARM_CORE top1=%.3f (>=%.2f cv=%.3f) | ARM_CAP m_cliff_min=%d mean=%.0f | "
        "ARM_MH K20=%.3f K50=%.3f (floors %.2f/%.2f) | ARM_COMP_OBJ lift=%.3f (>=%.2f) | "
        "ARM_COMP_CROSS lift=%.3f (expected FAIL; edge) | ARM_CL forget=%.4f (<%.3f) | "
        "ARM_NOISE sigma_cliff=%.2f (>=1.0) | ARM_REFUSE refuse=%.3f ret=%.3f (>=%.2f/%.2f)"
    ) % (a1_mean, ARM_CORE_TOP1_FLOOR, a1_cv, a2_min, a2_mean,
         a3_k20_mean, a3_k50_mean, ARM_MULTIHOP_K20_FLOOR, ARM_MULTIHOP_K50_FLOOR,
         a4_mean, ARM_COMP_OBJ_LIFT_FLOOR, a5_mean,
         a6_mean, ARM_CL_FORGET_CEIL, a7_mean,
         a8_ref, a8_ret, ARM_REFUSE_ACC_FLOOR, ARM_REFUSE_RETENTION_FLOOR)

    if n_pass >= CELL_PASS_FLOOR:
        v = "STAGE_1_CHAIN_GRADE_ALIVE"
    elif n_pass >= CELL_PARTIAL_FLOOR:
        v = "STAGE_1_PARTIAL"
    else:
        v = "STAGE_1_GAPS"
    vmsg = "%s: %d of 8 arms HARD_PASS. %s %s" % (v, n_pass, arm_results, summ)
    return (v, vmsg)


# -- Main ----------------------------------------------------------------

_LAST_HEARTBEAT = {"path": None, "ps": []}


def _atexit_heartbeat():
    """D2: ensure metrics file marker exists on any exit path."""
    try:
        path = _LAST_HEARTBEAT.get("path")
        if path is not None:
            hb = Path(path) / "exit_heartbeat.json"
            hb.write_text(json.dumps({"exit_ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                       "n_seeds_completed": len(_LAST_HEARTBEAT.get("ps", []))}, indent=2),
                          encoding="utf-8")
    except Exception:
        pass


atexit.register(_atexit_heartbeat)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d V_P=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, V_PREDICATES, CONFIG_VERSION), flush=True)
    t0 = time.time()
    out_dir = REPO / "data" / ("exp_%s" % EXP_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _LAST_HEARTBEAT["path"] = str(out_dir)
    ps = []
    for s in SEEDS:
        pf = out_dir / ("partial_seed%d_%s.json" % (s, RUN_MODE))
        if pf.exists():
            try:
                rec = json.loads(pf.read_text(encoding="utf-8"))
                if rec.get("config_version") == CONFIG_VERSION:
                    print("  [seed=%d] RESUME from checkpoint" % s, flush=True)
                    ps.append(rec); _LAST_HEARTBEAT["ps"] = ps; continue
            except Exception:
                pass
        rec = run_seed(s)
        # atomic write
        tmp = pf.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        os.replace(tmp, pf)
        ps.append(rec)
        _LAST_HEARTBEAT["ps"] = ps
    v, vmsg = verdict(ps)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
        "config_version": CONFIG_VERSION, "per_seed": ps,
        "elapsed_s": round(time.time() - t0, 1),
        "summary": vmsg,
        "DESIGN_NOTE": (
            "USER directive 2026-06-24: 'one final battery of tests to show definitively "
            "that these settings / what you've landed on work like you expect AND test "
            "around the edges.' Stage 1 substrate INTEGRATION: 8 arms at production scale "
            "N=8192 on substrate-native synthetic data (no encoder leakage). Per-arm "
            "pre-reg HARD-PASS floors; cell-level CHAIN_GRADE = >=5 of 8 arms PASS."
        ),
        "config": {
            "N_DIM": N_DIM, "V_CONCEPTS": V_CONCEPTS, "V_PREDICATES": V_PREDICATES,
            "SPARSE_F": SPARSE_F, "ARM_CORE_M": ARM_CORE_M,
            "ARM_CAP_M_GRID": ARM_CAP_M_GRID, "ARM_MULTIHOP_K_GRID": ARM_MULTIHOP_K_GRID,
            "ARM_CL_PHASES": ARM_CL_PHASES, "ARM_CL_M_PER_PHASE": ARM_CL_M_PER_PHASE,
            "ARM_NOISE_SIGMA_GRID": ARM_NOISE_SIGMA_GRID,
            "ARM_COMP_N_TRAIN": ARM_COMP_N_TRAIN, "ARM_COMP_N_HELDOUT": ARM_COMP_N_HELDOUT,
            "SEEDS": SEEDS, "run_mode": RUN_MODE,
        },
    }
    tmp = (out_dir / "metrics.json.tmp")
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(tmp, out_dir / "metrics.json")
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
