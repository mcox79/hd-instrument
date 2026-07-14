"""CONJUNCTION_NATIVE_BIND_VS_HOMOPHILY: the DECISIVE conjunction-mechanism experiment, the redesign after the
single-relation held-out approach was cleanly REFUTED (structured codes TIE/LOSE to homophily on real CSKG:
MEASURED@data/exp_relational_inference_neighbor_vs_unbind_structured_cskg_memsmoke_v3/metrics.json:gates.mrr.SN=0.1533
< HOM=0.1742 => verdict NEIGHBOR_INFERS_BUT_STRUCTURE_TIES_HOMOPHILY_REFUTED).

WHY THE REFRAME (chain, honest): single-relation held-out prediction is HOMOPHILY-SOLVABLE (sharing values ~= same
kind ~= shares the held-out value), so no structured code beats a value-overlap/frequency null. A real-CSKG feasibility
audit showed CSKG has ~NO native conjunction structure (one constraint already narrows a held-out relation to ~1.5
candidates), so conjunctions must be SUPPLIED (planted). Inline toys established the REFRAME: a CONJUNCTION target that
depends on a COMBINATION of >=2 constraints (NOT any single one) DISCRIMINATES structure from frequency where
single-relation did not -- on y=(a+b) mod L, HOMOPHILY collapses to chance, MEMORIZE fails NOVEL pairs, and the
substrate's NATIVE FHRR bind (matched to the additive composition) recovers y EXACTLY and GENERALIZES to novel pairs.
Lesson from the toy: use the substrate's NATIVE VSA ALGEBRA matched to the conjunction type, NOT SGD-learned codes
(learned-from-scratch was WEAK, 0.11 vs native 1.0).

WHAT THIS CELL IS: a conjunction-inference benchmark on REAL CSKG VOCABULARY (real entities/relations supply scale +
value-diversity + REAL value-frequency skew) with a PLANTED conjunction target y(e)=h(coord_A(v_A(e)), coord_B(v_B(e)))
that depends on a COMBINATION of an entity's two constituent constraints. The mechanism arm is the substrate's ACTUAL
FHRR bind (hdlab.binding.bind on complex64 phasor codes = the substrate's native compositional representation), NO SGD
fit. The decisive measured quantity is NOT "can FHRR add" (that is the mechanism definition, ~1.0 by construction on
CLEAN) -- it is whether, at REAL SCALE with REAL value distributions, the FREQUENCY/HOMOPHILY null stays near chance on
NOVEL compositional conjunctions (=> conjunctions are homophily-UNSOLVABLE => the reframe holds and gates the foundation
build) OR whether real vocab skew gives the null a backdoor (=> reframe weakens). The controls (ARBITRARY, SHUFFLE)
prove the native-bind win requires GENUINE compositional structure and is not leakage.

## COMPOSITIONAL-STRUCTURE SWEEP (the discriminating axis; all regimes scored PAIRED on the same held-out entities)
  CLEAN         : y = (coord_A + coord_B) mod L  (additive group; FHRR bind = phase addition = the MATCHED algebra)
  NOISY         : y = (coord_A + coord_B) mod L with prob (1-NOISE_P), else a uniform-random class (label noise)
  ARBITRARY     : y = Pi[coord_A, coord_B], Pi a FIXED RANDOM table Z_L x Z_L -> Z_L (NON-compositional; MUST-FAIL:
                  nothing generalizes to novel pairs; native-bind's additive readout is unrelated => ~chance)
  CLEAN_SHUFFLE : CLEAN labels PERMUTED across entities (freq-preserving) => the (v_A,v_B)->y link is destroyed while
                  the y-marginal is preserved (MUST-FAIL: native-bind must collapse to the frequency floor POP)

## ARMS (per regime, PAIRED on the SAME held-out query entities; top-1 acc + MRR over the L target classes)
  NATIVE_BIND  = substrate native FHRR bind (hdlab.binding.bind) of the two constituent phasor codes, cleanup to
                 nearest target-class phasor. NO training. THE headline mechanism. Novel-combo generalization by
                 construction of the algebra (bind is defined for all pairs).
  MEMORIZE     = exact (coord_A, coord_B)->majority-y train lookup; NOVEL pair (unseen combo) -> POP backoff.
  HOMOPHILY    = strongest fair FREQUENCY/HOMOPHILY null: conditional-match vote score(y)=count_train(a'==a,y)+
                 count_train(b'==b,y) (subsumes the factorized conditional-frequency predictor P(y|a),P(y|b)).
  HOMOPHILY_JAC= broader homophily: neighbor-vote over the entity's FULL real CSKG value-set (Jaccard over (rel,val)
                 tokens) -> vote neighbors' y. Guards against real correlated-vocab giving a broad-homophily backdoor.
  POP          = marginal floor: predict the most-frequent train y (frequency baseline, NOT popularity of entities).
  UNIFORM      = ~1/L chance reference.
  ORACLE       = info-ceiling: KNOWS the planted rule h -> applies it. CLEAN/ARBITRARY ceiling=1.0; NOISY ceiling=
                 irreducible-noise bound ~ (1-NOISE_P)+NOISE_P/L. Bounds every arm; the verdict never celebrates
                 sub-ceiling.
  FREQ_NULL    = max(HOMOPHILY, HOMOPHILY_JAC, POP) per stratum = the strongest frequency/homophily baseline the
                 native-bind mechanism must beat. THE decisive contrast is NATIVE_BIND vs FREQ_NULL on NOVEL.

## PRE-REGISTERED BANDS (NOVEL stratum, top-1 accuracy; chance = 1/L; NOT tuned on real data)
HARD_PASS (reframe SUPPORTED: native-bind composition beats frequency on compositional conjunctions) -- require ALL:
  P1 CLEAN     NATIVE_BIND novel-acc >= HP_BIND_CLEAN (0.85; feasible ~1.0, strict above cleanup-collision floor)
  P2 CLEAN     NATIVE_BIND novel-acc - FREQ_NULL novel-acc >= HP_DISSOCIATION (0.50) [the dissociation]
  P3 CLEAN     FREQ_NULL   novel-acc <= HP_NULL_FAILS (0.15) [null genuinely fails => conjunction homophily-UNSOLVABLE]
  P4 NOISY     NATIVE_BIND novel-acc - FREQ_NULL novel-acc >= HP_NOISY_MARGIN (0.20) [robust under realistic noise]
  P5 ARBITRARY NATIVE_BIND novel-acc - FREQ_NULL novel-acc <= MUSTFAIL_TOL (0.05) [no lift without compositional struct]
  P6 SHUFFLE   NATIVE_BIND novel-acc - POP novel-acc <= MUSTFAIL_TOL (0.05) [collapses to the frequency floor]
HARD_FAIL (reframe REFUTED -- report STRAIGHT; the most valuable negative) -- ANY of:
  F1 CLEAN     NATIVE_BIND novel-acc - FREQ_NULL novel-acc <= REFUTE_TOL (0.05) [native-bind does NOT beat freq clean]
  F2 CLEAN     FREQ_NULL   novel-acc >= REFUTE_NULL_SOLVES (0.40) [homophily SOLVES conjunctions => not unsolvable]
  F3 INTEGRITY ARBITRARY (NATIVE_BIND - FREQ_NULL) >= INTEGRITY_BREACH (0.20) OR SHUFFLE (NATIVE_BIND - POP) >=
               INTEGRITY_BREACH (0.20) [a must-fail did NOT fire => native-bind is leaking/cheating => the CLEAN win is
               an ARTIFACT and the whole result is INVALID -- integrity guard, dominates PASS]
MIDDLE_BAND: anything else (e.g. native-bind beats freq but modestly, or bands not cleanly separated).

## Compute architecture
class (b) sequential-CPU, JUSTIFIED: NO SGD fit (the mechanism is the substrate's NATIVE algebra, pure phasor
construction + one batched complex cleanup matmul (nq x d) @ (d x L) per regime + cheap graph/dict votes). Total wall
is seconds-to-a-few-minutes on CPU; the cleanup is batched (NOT a python matmul loop) per the GPU-batching rule but is
tiny enough that CPU is the proportionate resource. Storage strategy: no_storage / no_composition-chain (single-shot
compositional readout, no multi-item store, no chained retrieval). Route: remote_cpu_queue.

## CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor)
# - arms_differ_verified at self-test (META_RULE_AF): >=6 distinct arm prediction signatures per regime.
# - final_metrics_atomicity: tmp_replace (write_metrics uses os.replace; crash-metrics atomic).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: cleanup reachability THEORETICAL@ max off-diagonal FPE cosine ~ sqrt(2 ln L / d): at d=1024,
#   L=128 -> ~0.097 << 1.0 (true class) => NATIVE_BIND CLEAN survives scale; ORACLE bounds every arm; discriminator
#   reachability OK by construction. HP_BIND_CLEAN=0.85 is BELOW the ~1.0 native ceiling (feasible, strict).
# - baseline_in_band: FREQ_NULL is the honest frequency floor (structurally near chance on NOVEL, NOT saturated);
#   verified at self-test on the planted synthetic arena; the REAL run measures whether real skew moves it.
# - discriminator survives scale: (A) self-test runs the FULL regime machinery at synthetic scale AND fires the
#   discriminator + both must-fails; (B) analytical FPE-cleanup bound above; (C) a MEMSMOKE on reduced real CSKG core
#   confirms on real data before FULL.
# - HARD bands strictly separated: HP_DISSOCIATION=0.50 vs REFUTE_TOL=0.05; MUSTFAIL_TOL=0.05 vs INTEGRITY_BREACH=0.20.
# - HP_SCOPE: P1/P2/P3 gate NATIVE_BIND vs FREQ_NULL on CLEAN-novel; P4 on NOISY-novel; P5 ARBITRARY must-fail; P6
#   SHUFFLE must-fail. ORACLE/UNIFORM = ceiling/floor references (no HP gate). MEMORIZE = diagnostic (no HP gate).
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed must produce all 4 regimes x all arms + non-empty novel & seen.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: default_ok_for_this_regime -- all bands pre-registered from the mechanism's construction +
#   chance=1/L, NOT tuned on real data.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the docstring/prereg.
# - real_code_path (F.1): self-test calls the REAL substrate bind hdlab.binding.bind on complex64 phasor codes (the
#   FULL native-bind path); substrate_signature (F.2) binds hdlab.binding.bind against its live signature.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-regime flush prints + heartbeat).

ASCII-only. No bare except; except SystemExit before except Exception.
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from hdlab.binding import bind as hd_bind  # noqa: E402  # the REAL substrate FHRR bind (complex64 elementwise mul)

ANCHOR_NAME = "conjunction_native_bind_vs_homophily_cskg_v1"

# ---- regimes ----
CLEAN = "CLEAN"
NOISY = "NOISY"
ARBITRARY = "ARBITRARY"
SHUFFLE = "CLEAN_SHUFFLE"
REGIMES = [CLEAN, NOISY, ARBITRARY, SHUFFLE]

# ---- arms ----
NBIND = "NATIVE_BIND"
MEMO = "MEMORIZE"
HOM = "HOMOPHILY"
HOMJ = "HOMOPHILY_JAC"
POP = "POP"
UNIF = "UNIFORM"
ORC = "ORACLE"
ARMS = [NBIND, MEMO, HOM, HOMJ, POP, UNIF, ORC]
FREQ_NULL_ARMS = [HOM, HOMJ, POP]   # FREQ_NULL = max of these per stratum (strongest frequency/homophily baseline)

# ---- CITED reference (the single-relation refutation this reframes) ----
CITED_SN = 0.1533  # MEASURED@data/exp_relational_inference_neighbor_vs_unbind_structured_cskg_memsmoke_v3/metrics.json:gates.mrr.SN
CITED_HOM = 0.1742  # MEASURED@ same file :gates.mrr.HOM (structure TIED/LOST to homophily on single-relation)

# ---- PRE-REGISTERED bands (NOVEL stratum, top-1 accuracy; chance=1/L; NOT tuned on real data) ----
HP_BIND_CLEAN = 0.85       # P1
HP_DISSOCIATION = 0.50     # P2
HP_NULL_FAILS = 0.15       # P3
HP_NOISY_MARGIN = 0.20     # P4
MUSTFAIL_TOL = 0.05        # P5, P6
REFUTE_TOL = 0.05          # F1
REFUTE_NULL_SOLVES = 0.40  # F2
INTEGRITY_BREACH = 0.20    # F3

# ---- self-test planted thresholds (calibrated on synthetic, NOT real data) ----
ST_BIND_CLEAN = 0.90       # native-bind CLEAN novel-acc >= this (near-exact on planted additive arena)
ST_DISSOCIATION = 0.50     # native-bind - FREQ_NULL on CLEAN novel >= this (the discriminator FIRES)
ST_NULL_FAILS = 0.20       # FREQ_NULL CLEAN novel-acc <= this (null genuinely fails on the synthetic conjunction)
ST_ARB_MUSTFAIL = 0.10     # ARBITRARY: native-bind - FREQ_NULL novel-acc <= this (must-fail fires)
ST_SHUF_MUSTFAIL = 0.10    # SHUFFLE: native-bind - POP novel-acc <= this (must-fail fires)

# Config profiles. SELFTEST/MEMSMOKE/FULL exercise the SAME plant->split->arms->verdict path.
SELFTEST_CFG = dict(mode="synthetic", n_dim=256, L=32, noise_p=0.35, m_nn=25, query_frac=0.45,
                    n_ent=800, n_val_a=40, n_val_b=40, min_query=40, min_novel=8, seeds=[7])
MEMSMOKE_CFG = dict(mode="cskg", n_dim=512, L=64, noise_p=0.35, m_nn=25, query_frac=0.45,
                    cskg_max_lines=600000, k_core=4, cskg_max_nodes=0, min_query=100, min_novel=20, seeds=[7])
FULL_CFG = dict(mode="cskg", n_dim=1024, L=128, noise_p=0.35, m_nn=25, query_frac=0.45,
                cskg_max_lines=0, k_core=4, cskg_max_nodes=0, min_query=200, min_novel=40, seeds=[7, 13, 17])

CLEANUP_CHUNK = 1024


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.asarray(arr, dtype=np.int64)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _coord(value, seed, L):
    """Deterministic latent integer coordinate in Z_L for a real value string (seed-varying, spreads values)."""
    h = hashlib.sha256(("%d|%s" % (seed, value)).encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") % L


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# FPE phasor codebook (the substrate's native modular value manifold). Ycode[j] = exp(i 2pi m j / L), m random ints in
# [1,L) per dim => bind(Ycode[a], Ycode[b]) = Ycode[(a+b) mod L] EXACTLY (FHRR bind = elementwise complex mul).
# ---------------------------------------------------------------------------

def build_fpe_codebook(L, n_dim, seed):
    """Returns Ycode (L, n_dim) complex64 unit-modulus phasors, a group homomorphism over Z_L under FHRR bind."""
    g = np.random.default_rng(seed * 100003 + 17)
    m = g.integers(1, L, size=n_dim).astype(np.float64)          # per-dim integer frequency in [1, L)
    j = np.arange(L, dtype=np.float64)[:, None]                  # (L, 1)
    phase = (2.0 * np.pi / L) * (j * m[None, :])                 # (L, n_dim)
    code = np.exp(1j * phase).astype(np.complex64)
    return torch.from_numpy(code)                                # (L, n_dim) complex64


def cleanup_scores(pred, Ycode):
    """pred (nq, d) complex64, Ycode (L, d) complex64 unit-modulus. Returns real cosine-like scores (nq, L)."""
    nq = pred.shape[0]
    L = Ycode.shape[0]
    Yc = Ycode.conj().T.contiguous()                            # (d, L)
    out = torch.empty(nq, L, dtype=torch.float32)
    for s in range(0, nq, CLEANUP_CHUNK):
        e = min(s + CLEANUP_CHUNK, nq)
        out[s:e] = (pred[s:e] @ Yc).real.to(torch.float32)
    return out


# ---------------------------------------------------------------------------
# Rank metrics over L target classes (single gold class per query).
# ---------------------------------------------------------------------------

def acc_mrr_from_scores(scores, gold):
    """scores (nq, L) higher=better; gold (nq,) int class. Returns (top1_acc, mrr)."""
    nq = scores.shape[0]
    if nq == 0:
        return float("nan"), float("nan")
    gold_t = torch.as_tensor(gold, dtype=torch.long)
    gold_score = scores.gather(1, gold_t.view(-1, 1)).squeeze(1)          # (nq,)
    greater = (scores > gold_score.view(-1, 1)).sum(dim=1)                # strictly better classes
    equal = (scores == gold_score.view(-1, 1)).sum(dim=1)                 # ties incl. gold
    rank = greater.to(torch.float64) + (equal.to(torch.float64) + 1.0) / 2.0  # avg-rank over ties (1-indexed)
    top1 = float((rank <= 1.0).to(torch.float64).mean().item())
    mrr = float((1.0 / rank).mean().item())
    return top1, mrr


def acc_mrr_from_labels(pred_labels, gold, L):
    """Discrete-label arms (argmax already taken; ties broken to a single label). Rank = 1 if match else ~mid (L+1)/2
    for a random tie-broken guess is not modeled; we score top-1 acc exactly and set MRR = acc + (1-acc)/L (a guessing
    arm gets 1/L residual credit). Honest lower bound for discrete arms."""
    nq = len(pred_labels)
    if nq == 0:
        return float("nan"), float("nan")
    hit = np.asarray(pred_labels, dtype=np.int64) == np.asarray(gold, dtype=np.int64)
    acc = float(hit.mean())
    mrr = acc + (1.0 - acc) * (1.0 / L)
    return acc, mrr


# ---------------------------------------------------------------------------
# Arms.
# ---------------------------------------------------------------------------

def arm_native_bind(a_q, b_q, Ycode):
    """Substrate NATIVE FHRR bind of the two constituent phasor codes, cleanup to nearest target class. NO training."""
    cA = Ycode[torch.as_tensor(a_q, dtype=torch.long)]           # (nq, d) complex64
    cB = Ycode[torch.as_tensor(b_q, dtype=torch.long)]
    pred = hd_bind(cA, cB)                                       # REAL substrate bind (elementwise complex mul)
    return cleanup_scores(pred, Ycode)                          # (nq, L) real


def arm_memorize(a_q, b_q, a_tr, b_tr, y_tr, L, pop_label):
    """Exact (a,b)->majority-y train lookup; novel (unseen) pair -> POP backoff. Returns label predictions."""
    combo = defaultdict(lambda: defaultdict(int))
    for a, b, y in zip(a_tr, b_tr, y_tr):
        combo[(int(a), int(b))][int(y)] += 1
    preds = []
    for a, b in zip(a_q, b_q):
        d = combo.get((int(a), int(b)))
        if d:
            preds.append(max(d.items(), key=lambda kv: kv[1])[0])
        else:
            preds.append(pop_label)
    return np.asarray(preds, dtype=np.int64)


def arm_homophily_cond(a_q, b_q, a_tr, b_tr, y_tr, L, pop_label):
    """Strongest fair FREQUENCY/HOMOPHILY null: score(y)=count_train(a'==a,y)+count_train(b'==b,y) (subsumes the
    factorized conditional-frequency predictor). Returns (nq, L) score tensor (POP fallback baked in for empty)."""
    ay = defaultdict(lambda: np.zeros(L, dtype=np.float64))
    by = defaultdict(lambda: np.zeros(L, dtype=np.float64))
    for a, b, y in zip(a_tr, b_tr, y_tr):
        ay[int(a)][int(y)] += 1.0
        by[int(b)][int(y)] += 1.0
    marg = np.zeros(L, dtype=np.float64)
    for y in y_tr:
        marg[int(y)] += 1.0
    nq = len(a_q)
    out = np.zeros((nq, L), dtype=np.float32)
    for i, (a, b) in enumerate(zip(a_q, b_q)):
        sc = ay.get(int(a), np.zeros(L)) + by.get(int(b), np.zeros(L))
        if sc.sum() <= 0.0:
            sc = marg                                            # backoff to marginal (POP) when no conditional support
        out[i] = sc.astype(np.float32)
    return torch.from_numpy(out)


def arm_homophily_jaccard(q_idx, tr_idx, val_sets, y_all, m_nn, L):
    """Broad homophily: neighbor-vote over the entity's FULL real value-set (Jaccard over (rel,val) tokens). Retrieve
    top-m Jaccard-similar TRAIN entities via an inverted index; each votes its y weighted by Jaccard. Returns (nq, L)."""
    inv = defaultdict(list)                                      # token -> train positions
    tr_sets = [val_sets[e] for e in tr_idx]
    tr_sz = np.array([len(s) for s in tr_sets], dtype=np.float64)
    for j, s in enumerate(tr_sets):
        for tok in s:
            inv[tok].append(j)
    nq = len(q_idx)
    out = np.zeros((nq, L), dtype=np.float32)
    for i, e in enumerate(q_idx):
        Sc = val_sets[e]
        if not Sc:
            continue
        inter = defaultdict(int)
        for tok in Sc:
            for j in inv.get(tok, ()):
                inter[j] += 1
        csz = float(len(Sc))
        cand = []
        for j, ic in inter.items():
            if int(tr_idx[j]) == int(e):
                continue
            denom = csz + tr_sz[j] - ic
            if denom <= 0.0:
                continue
            cand.append((ic / denom, j))
        if not cand:
            continue
        cand.sort(reverse=True)
        for jac, j in cand[:m_nn]:
            if jac <= 0.0:
                continue
            out[i, int(y_all[int(tr_idx[j])])] += float(jac)
    return torch.from_numpy(out)


# ---------------------------------------------------------------------------
# Plant a regime's labels + oracle.
# ---------------------------------------------------------------------------

def plant_labels(coord_a, coord_b, regime, L, seed):
    """coord_a, coord_b: (n_ent,) int arrays. Returns (y (n_ent,), oracle_pred (n_ent,)) for the regime."""
    n = coord_a.shape[0]
    add = (coord_a + coord_b) % L
    rng = np.random.default_rng(seed * 100057 + hash(regime) % 100000)
    if regime == CLEAN:
        y = add.copy()
        oracle = add.copy()
    elif regime == NOISY:
        y = add.copy()
        flip = rng.random(n) < FULL_CFG_placeholder_noise()          # replaced below; see plant_labels_cfg
        y[flip] = rng.integers(0, L, size=int(flip.sum()))
        oracle = add.copy()                                          # rule-knower predicts the deterministic part
    elif regime == ARBITRARY:
        Pi = rng.integers(0, L, size=(L, L))
        y = Pi[coord_a, coord_b]
        oracle = Pi[coord_a, coord_b].copy()                        # oracle knows the table (ceiling=1.0)
    elif regime == SHUFFLE:
        base = add.copy()
        perm = rng.permutation(n)
        y = base[perm]                                              # freq-preserving label permutation
        oracle = base.copy()                                       # rule-knower predicts (a+b); uncorrelated w/ y
    else:
        raise ValueError("unknown regime %s" % regime)
    return y.astype(np.int64), oracle.astype(np.int64)


def FULL_CFG_placeholder_noise():
    # noise_p is threaded via a module global set per-run (avoids a signature change to plant_labels callers)
    return _ACTIVE_NOISE_P[0]


_ACTIVE_NOISE_P = [0.35]


# ---------------------------------------------------------------------------
# Build a corpus: entities with two constituent constraints (real CSKG vocab OR synthetic), planted targets, split.
# ---------------------------------------------------------------------------

def build_entity_constraints_cskg(pool_lbl, seed):
    """From CSKG triples pick the 2 relations with max DUAL-coverage; restrict to entities having both; one
    deterministic value per relation. Returns (ent_ids, v_a, v_b, val_sets, relA, relB, prov)."""
    rel_ents = defaultdict(set)
    rel_val = defaultdict(lambda: defaultdict(list))            # rel -> head -> [tails]
    full_sets = defaultdict(set)                                # head -> {(rel, tail)} for Jaccard homophily
    for (h, r, t) in pool_lbl:
        rel_ents[r].add(h)
        rel_val[r][h].append(t)
        full_sets[h].add((r, t))
    top_rels = sorted(rel_ents.keys(), key=lambda r: len(rel_ents[r]), reverse=True)
    # choose the pair (among the top-K by coverage) with MAX dual-coverage
    K = min(8, len(top_rels))
    best = None
    for i in range(K):
        for j in range(i + 1, K):
            rA, rB = top_rels[i], top_rels[j]
            dual = rel_ents[rA] & rel_ents[rB]
            if best is None or len(dual) > best[0]:
                best = (len(dual), rA, rB, dual)
    if best is None:
        return [], None, None, None, None, None, dict(dual=0)
    _, relA, relB, dual = best
    ents = sorted(dual)
    v_a = {}
    v_b = {}
    for e in ents:
        v_a[e] = min(rel_val[relA][e])                          # deterministic representative value
        v_b[e] = min(rel_val[relB][e])
    prov = dict(relA=relA, relB=relB, dual_coverage=len(ents),
                n_val_a=len({v_a[e] for e in ents}), n_val_b=len({v_b[e] for e in ents}),
                covA=len(rel_ents[relA]), covB=len(rel_ents[relB]), n_rel=len(rel_ents))
    return ents, v_a, v_b, full_sets, relA, relB, prov


def build_entity_constraints_synthetic(cfg, seed):
    """Synthetic arena mirroring the real structure: n_ent entities, each with a value on relation A and B drawn from
    n_val_a / n_val_b vocabs, plus a few extra (rel,val) tokens for Jaccard homophily. Returns same shape as CSKG."""
    rng = np.random.default_rng(seed * 100069 + 5)
    n = cfg["n_ent"]
    ents = ["e%d" % i for i in range(n)]
    v_a = {}
    v_b = {}
    full_sets = defaultdict(set)
    for e in ents:
        va = "A_v%d" % int(rng.integers(cfg["n_val_a"]))
        vb = "B_v%d" % int(rng.integers(cfg["n_val_b"]))
        v_a[e] = va
        v_b[e] = vb
        full_sets[e].add(("relA", va))
        full_sets[e].add(("relB", vb))
        for _ in range(int(rng.integers(0, 3))):               # a few extra tokens (real-like value-set noise)
            full_sets[e].add(("relX%d" % int(rng.integers(4)), "xv%d" % int(rng.integers(20))))
    prov = dict(relA="relA", relB="relB", dual_coverage=n,
                n_val_a=cfg["n_val_a"], n_val_b=cfg["n_val_b"], covA=n, covB=n, n_rel=6)
    return ents, v_a, v_b, full_sets, "relA", "relB", prov


def prepare_corpus(pool_lbl, cfg, seed):
    if cfg["mode"] == "cskg":
        ents, v_a, v_b, full_sets, relA, relB, prov = build_entity_constraints_cskg(pool_lbl, seed)
    else:
        ents, v_a, v_b, full_sets, relA, relB, prov = build_entity_constraints_synthetic(cfg, seed)
    if not ents or len(ents) < cfg["min_query"]:
        return None, prov
    L = cfg["L"]
    n = len(ents)
    ent_index = {e: i for i, e in enumerate(ents)}
    coord_a = np.array([_coord(v_a[e], seed, L) for e in ents], dtype=np.int64)
    coord_b = np.array([_coord(v_b[e], seed, L) for e in ents], dtype=np.int64)
    # split entities into train / query (held-out) deterministically
    rng = np.random.default_rng(seed * 100081 + 9)
    perm = rng.permutation(n)
    n_query = int(round(cfg["query_frac"] * n))
    q_pos = np.sort(perm[:n_query])
    tr_pos = np.sort(perm[n_query:])
    # NOVEL: query entity whose (coord_a, coord_b) pair is unseen among TRAIN entities
    train_pairs = set((int(coord_a[i]), int(coord_b[i])) for i in tr_pos)
    novel_mask = np.array([(int(coord_a[i]), int(coord_b[i])) not in train_pairs for i in q_pos], dtype=bool)
    # value-set tokens for Jaccard homophily, indexed by entity position
    val_sets = [full_sets[e] for e in ents]
    return dict(ents=ents, ent_index=ent_index, coord_a=coord_a, coord_b=coord_b, L=L, n=n,
                q_pos=q_pos, tr_pos=tr_pos, novel_mask=novel_mask, val_sets=val_sets,
                relA=relA, relB=relB, prov=prov), prov


# ---------------------------------------------------------------------------
# Score all arms for one regime, PAIRED on the same query entities. Returns per-stratum acc/mrr + signatures.
# ---------------------------------------------------------------------------

def score_regime(prep, cfg, regime, seed, Ycode):
    L = prep["L"]
    coord_a = prep["coord_a"]
    coord_b = prep["coord_b"]
    q_pos = prep["q_pos"]
    tr_pos = prep["tr_pos"]
    novel = prep["novel_mask"]
    y_all, oracle_all = plant_labels(coord_a, coord_b, regime, L, seed)

    a_q = coord_a[q_pos]
    b_q = coord_b[q_pos]
    gold = y_all[q_pos]
    a_tr = coord_a[tr_pos]
    b_tr = coord_b[tr_pos]
    y_tr = y_all[tr_pos]

    # POP label (most-frequent train y)
    counts = np.bincount(y_tr, minlength=L)
    pop_label = int(np.argmax(counts))

    # ---- arm scores (continuous score arms) ----
    nb_scores = arm_native_bind(a_q, b_q, Ycode)                 # (nq, L) REAL substrate bind path
    hom_scores = arm_homophily_cond(a_q, b_q, a_tr, b_tr, y_tr, L, pop_label)
    homj_scores = arm_homophily_jaccard(q_pos, tr_pos, prep["val_sets"], y_all, cfg["m_nn"], L)

    # ---- discrete-label arms ----
    memo_pred = arm_memorize(a_q, b_q, a_tr, b_tr, y_tr, L, pop_label)
    orc_pred = oracle_all[q_pos]
    pop_pred = np.full(a_q.shape[0], pop_label, dtype=np.int64)
    grng = np.random.default_rng(seed * 7 + 1)
    unif_pred = grng.integers(0, L, size=a_q.shape[0]).astype(np.int64)

    # ---- per-stratum metrics ----
    def strat(fn_scores_or_labels, is_scores):
        res = {}
        for name, msk in (("all", np.ones(len(gold), dtype=bool)), ("novel", novel), ("seen", ~novel)):
            if msk.sum() == 0:
                res[name] = dict(acc=float("nan"), mrr=float("nan"), n=0)
                continue
            if is_scores:
                acc, mrr = acc_mrr_from_scores(fn_scores_or_labels[torch.as_tensor(msk)], gold[msk])
            else:
                acc, mrr = acc_mrr_from_labels(np.asarray(fn_scores_or_labels)[msk], gold[msk], L)
            res[name] = dict(acc=round(acc, 6), mrr=round(mrr, 6), n=int(msk.sum()))
        return res

    arm_res = {
        NBIND: strat(nb_scores, True),
        HOM: strat(hom_scores, True),
        HOMJ: strat(homj_scores, True),
        MEMO: strat(memo_pred, False),
        ORC: strat(orc_pred, False),
        POP: strat(pop_pred, False),
        UNIF: strat(unif_pred, False),
    }

    # ---- arms-must-differ signatures (top-1 argmax label per arm) ----
    sigs = {}
    sigs[NBIND] = _sig(torch.argmax(nb_scores, dim=1).numpy())
    sigs[HOM] = _sig(torch.argmax(hom_scores, dim=1).numpy())
    sigs[HOMJ] = _sig(torch.argmax(homj_scores, dim=1).numpy())
    sigs[MEMO] = _sig(memo_pred)
    sigs[ORC] = _sig(orc_pred)
    sigs[POP] = _sig(pop_pred)
    sigs[UNIF] = _sig(unif_pred)

    return dict(regime=regime, arms=arm_res, sigs=sigs, pop_label=pop_label,
                n_query=int(len(gold)), n_novel=int(novel.sum()), n_seen=int((~novel).sum()))


def _freq_null(regime_res, stratum, metric="acc"):
    """FREQ_NULL = max over {HOMOPHILY, HOMOPHILY_JAC, POP} of the stratum metric = strongest frequency/homophily null."""
    vals = [regime_res["arms"][a][stratum][metric] for a in FREQ_NULL_ARMS]
    vals = [v for v in vals if v == v]
    return max(vals) if vals else float("nan")


def run_seed(pool_lbl, cfg, seed):
    prep, prov = prepare_corpus(pool_lbl, cfg, seed)
    if prep is None:
        return dict(seed=seed, invalid="insufficient_dual_coverage", prov=prov), None
    Ycode = build_fpe_codebook(cfg["L"], cfg["n_dim"], seed)
    _ACTIVE_NOISE_P[0] = cfg["noise_p"]
    regimes_res = {}
    for reg in REGIMES:
        regimes_res[reg] = score_regime(prep, cfg, reg, seed, Ycode)
    n_novel = regimes_res[CLEAN]["n_novel"]
    n_seen = regimes_res[CLEAN]["n_seen"]
    n_query = regimes_res[CLEAN]["n_query"]
    res = dict(seed=seed, n_query=n_query, n_novel=n_novel, n_seen=n_seen, L=cfg["L"], n_dim=cfg["n_dim"],
               n_entities=prep["n"], relA=prep["relA"], relB=prep["relB"], prov=prep["prov"], regimes=regimes_res)
    return res, prep


# ---------------------------------------------------------------------------
# Decisive verdict over per-seed results.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def _arm_novel_acc(per_seed, regime, arm):
    return _nm([ps["regimes"][regime]["arms"][arm]["novel"]["acc"] for ps in per_seed])


def _freqnull_novel_acc(per_seed, regime):
    return _nm([_freq_null(ps["regimes"][regime], "novel", "acc") for ps in per_seed])


def decisive_verdict(per_seed):
    L = per_seed[0]["L"]
    chance = 1.0 / L
    bind_clean = _arm_novel_acc(per_seed, CLEAN, NBIND)
    fn_clean = _freqnull_novel_acc(per_seed, CLEAN)
    bind_noisy = _arm_novel_acc(per_seed, NOISY, NBIND)
    fn_noisy = _freqnull_novel_acc(per_seed, NOISY)
    bind_arb = _arm_novel_acc(per_seed, ARBITRARY, NBIND)
    fn_arb = _freqnull_novel_acc(per_seed, ARBITRARY)
    bind_shuf = _arm_novel_acc(per_seed, SHUFFLE, NBIND)
    pop_shuf = _arm_novel_acc(per_seed, SHUFFLE, POP)
    orc_clean = _arm_novel_acc(per_seed, CLEAN, ORC)
    memo_clean = _arm_novel_acc(per_seed, CLEAN, MEMO)

    diss_clean = bind_clean - fn_clean
    diss_noisy = bind_noisy - fn_noisy
    arb_gap = bind_arb - fn_arb
    shuf_gap = bind_shuf - pop_shuf

    # ---- integrity guard (dominates): a must-fail that did NOT fire => native-bind leaking => CLEAN win is artifact ----
    integrity_breached = bool((arb_gap == arb_gap and arb_gap >= INTEGRITY_BREACH)
                              or (shuf_gap == shuf_gap and shuf_gap >= INTEGRITY_BREACH))
    # ceiling sanity: ORACLE >= NATIVE_BIND on CLEAN novel (info-ceiling well-formed)
    ceiling_ok = bool(orc_clean == orc_clean and bind_clean == bind_clean and orc_clean >= bind_clean - 1e-6)

    # ---- HARD_PASS gates ----
    p1 = bool(bind_clean == bind_clean and bind_clean >= HP_BIND_CLEAN)
    p2 = bool(diss_clean == diss_clean and diss_clean >= HP_DISSOCIATION)
    p3 = bool(fn_clean == fn_clean and fn_clean <= HP_NULL_FAILS)
    p4 = bool(diss_noisy == diss_noisy and diss_noisy >= HP_NOISY_MARGIN)
    p5 = bool(arb_gap == arb_gap and arb_gap <= MUSTFAIL_TOL)
    p6 = bool(shuf_gap == shuf_gap and shuf_gap <= MUSTFAIL_TOL)
    hard_pass = bool(p1 and p2 and p3 and p4 and p5 and p6 and (not integrity_breached) and ceiling_ok)

    # ---- HARD_FAIL gates ----
    f1 = bool(diss_clean == diss_clean and diss_clean <= REFUTE_TOL)
    f2 = bool(fn_clean == fn_clean and fn_clean >= REFUTE_NULL_SOLVES)
    f3 = integrity_breached
    hard_fail = bool(f1 or f2 or f3)

    if not ceiling_ok:
        verdict = "INCONCLUSIVE_CEILING_MALFORMED"
    elif integrity_breached:
        verdict = "INVALID_MUSTFAIL_DID_NOT_FIRE_NATIVE_BIND_LEAKS"
    elif hard_pass:
        verdict = "NATIVE_BIND_COMPOSITION_BEATS_FREQUENCY_ON_CONJUNCTIONS"
    elif hard_fail:
        verdict = "CONJUNCTION_REFRAME_REFUTED_NATIVE_BIND_TIES_FREQUENCY"
    else:
        verdict = "MIDDLE_BAND_INCONCLUSIVE"

    msg = ("%s || chance=1/L=%.4f | CLEAN: NBIND=%s FREQ_NULL=%s diss=%s(HP>=%.2f=%s null<=%.2f=%s bind>=%.2f=%s) | "
           "NOISY: NBIND=%s FREQ_NULL=%s diss=%s(HP>=%.2f=%s) | ARBITRARY(must-fail): NBIND=%s FREQ_NULL=%s gap=%s"
           "(<=%.2f=%s breach>=%.2f=%s) | SHUFFLE(must-fail): NBIND=%s POP=%s gap=%s(<=%.2f=%s breach>=%.2f=%s) | "
           "ORACLE_clean=%s MEMO_clean=%s ceiling_ok=%s || F1(tie)=%s F2(null-solves)=%s F3(integrity)=%s"
           % (verdict, chance, _fmt(bind_clean), _fmt(fn_clean), _fmt(diss_clean), HP_DISSOCIATION, p2,
              HP_NULL_FAILS, p3, HP_BIND_CLEAN, p1, _fmt(bind_noisy), _fmt(fn_noisy), _fmt(diss_noisy),
              HP_NOISY_MARGIN, p4, _fmt(bind_arb), _fmt(fn_arb), _fmt(arb_gap), MUSTFAIL_TOL, p5,
              INTEGRITY_BREACH, bool(arb_gap == arb_gap and arb_gap >= INTEGRITY_BREACH), _fmt(bind_shuf),
              _fmt(pop_shuf), _fmt(shuf_gap), MUSTFAIL_TOL, p6, INTEGRITY_BREACH,
              bool(shuf_gap == shuf_gap and shuf_gap >= INTEGRITY_BREACH), _fmt(orc_clean), _fmt(memo_clean),
              ceiling_ok, f1, f2, f3))

    def _r(x):
        return round(x, 6) if (x == x) else None

    gates = dict(
        verdict=verdict, chance=_r(chance),
        clean=dict(native_bind=_r(bind_clean), freq_null=_r(fn_clean), dissociation=_r(diss_clean),
                   oracle=_r(orc_clean), memorize=_r(memo_clean)),
        noisy=dict(native_bind=_r(bind_noisy), freq_null=_r(fn_noisy), dissociation=_r(diss_noisy)),
        arbitrary=dict(native_bind=_r(bind_arb), freq_null=_r(fn_arb), gap=_r(arb_gap)),
        shuffle=dict(native_bind=_r(bind_shuf), pop=_r(pop_shuf), gap=_r(shuf_gap)),
        hard_pass_gates=dict(P1_bind_clean=p1, P2_dissociation=p2, P3_null_fails=p3, P4_noisy_margin=p4,
                             P5_arb_mustfail=p5, P6_shuf_mustfail=p6),
        hard_fail_gates=dict(F1_tie=f1, F2_null_solves=f2, F3_integrity_breach=f3),
        integrity_breached=integrity_breached, ceiling_ok=ceiling_ok,
        bands=dict(HP_BIND_CLEAN=HP_BIND_CLEAN, HP_DISSOCIATION=HP_DISSOCIATION, HP_NULL_FAILS=HP_NULL_FAILS,
                   HP_NOISY_MARGIN=HP_NOISY_MARGIN, MUSTFAIL_TOL=MUSTFAIL_TOL, REFUTE_TOL=REFUTE_TOL,
                   REFUTE_NULL_SOLVES=REFUTE_NULL_SOLVES, INTEGRITY_BREACH=INTEGRITY_BREACH),
    )
    return verdict, msg, gates


# ---------------------------------------------------------------------------
# Self-test: apparatus validity on a synthetic conjunction arena (real bind code path) + validity-preflight.
# ---------------------------------------------------------------------------

def mechanism_selftest():
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _mechanism_selftest_body()
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body():
    cfg = dict(SELFTEST_CFG)
    out = {}

    # F.1/F.2 real bind path: bind two FPE codes and assert the homomorphism holds (native bind = modular add).
    Yc = build_fpe_codebook(cfg["L"], cfg["n_dim"], 7)
    a_idx = torch.tensor([3, 10, 20], dtype=torch.long)
    b_idx = torch.tensor([5, 7, 15], dtype=torch.long)
    bound = hd_bind(Yc[a_idx], Yc[b_idx])                        # REAL substrate bind
    sc = cleanup_scores(bound, Yc)
    pred = torch.argmax(sc, dim=1).tolist()
    expect = [((int(a) + int(b)) % cfg["L"]) for a, b in zip(a_idx.tolist(), b_idx.tolist())]
    homomorphism_ok = bool(pred == expect)

    res, prep = run_seed([], cfg, 7)
    if res.get("invalid"):
        return False, {"fail": "synthetic corpus invalid: %s" % res.get("invalid")}

    rc = res["regimes"]
    bind_clean = rc[CLEAN]["arms"][NBIND]["novel"]["acc"]
    fn_clean = _freq_null(rc[CLEAN], "novel", "acc")
    bind_arb = rc[ARBITRARY]["arms"][NBIND]["novel"]["acc"]
    fn_arb = _freq_null(rc[ARBITRARY], "novel", "acc")
    bind_shuf = rc[SHUFFLE]["arms"][NBIND]["novel"]["acc"]
    pop_shuf = rc[SHUFFLE]["arms"][POP]["novel"]["acc"]
    orc_clean = rc[CLEAN]["arms"][ORC]["novel"]["acc"]

    bind_beats = bool(bind_clean >= ST_BIND_CLEAN)
    dissociates = bool((bind_clean - fn_clean) >= ST_DISSOCIATION)
    null_fails = bool(fn_clean <= ST_NULL_FAILS)
    arb_mustfail = bool((bind_arb - fn_arb) <= ST_ARB_MUSTFAIL)
    shuf_mustfail = bool((bind_shuf - pop_shuf) <= ST_SHUF_MUSTFAIL)
    ceiling_ok = bool(orc_clean >= bind_clean - 1e-6)
    # arms differ per regime (>= 6 distinct top-1 signatures on CLEAN where arms genuinely diverge)
    n_sigs_clean = len(set(rc[CLEAN]["sigs"].values()))
    arms_differ = bool(n_sigs_clean >= 6)
    novel_seen_ok = bool(res["n_novel"] >= cfg["min_novel"] and res["n_seen"] >= 3)

    # VACUOUS-SMOKE / DISCRIMINATOR-FIRES guard: native-bind MUST separate from FREQ_NULL on CLEAN novel.
    disc_frozen = bool((bind_clean - fn_clean) < ST_DISSOCIATION)
    assert_discriminator_fires(disc_frozen, control_name="FREQ_NULL",
                               headline_name="native_bind_beats_freq_null_clean_novel", run_mode="self_test",
                               extra="on the synthetic additive-conjunction arena NATIVE_BIND did NOT dissociate from "
                                     "the frequency/homophily null on the NOVEL stratum -> arena not answerable / "
                                     "discriminator frozen (the conjunction reframe is not testable here)")

    v_verdict, _vm, _vg = decisive_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["hdlab.binding.bind", "build_fpe_codebook", "cleanup_scores"],
         "exercised_entrypoints": ["hdlab.binding.bind", "build_fpe_codebook", "cleanup_scores"],
         "extra": "self-test calls the REAL substrate FHRR bind (hdlab.binding.bind) on complex64 FPE phasor codes -- "
                  "the EXACT native-bind path the FULL run uses; build_cskg_core_triples is the FULL-only data source "
                  "(exercised remote via _ensure_cskg), intentionally not in self-test (no-local-smokes)"},
        {"kind": "substrate_signature", "callable_obj": hd_bind, "callable_name": "hdlab.binding.bind",
         "kwargs": {"a": Yc[a_idx], "b": Yc[b_idx]}},
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(bind_beats and dissociates and null_fails and homomorphism_ok),
         "control_name": "SYNTHETIC_ADDITIVE_CONJUNCTION",
         "headline_name": "native_bind_solves_conjunction_and_freq_null_fails_on_novel",
         "extra": "synthetic additive arena: FHRR bind is the group homomorphism (bind(a,b)=code[(a+b)%L]); NATIVE_BIND "
                  "solves novel combos, the frequency/homophily null fails on novel (conjunction is homophily-unsolvable "
                  "by construction here) -> apparatus CAN detect native-bind-beats-frequency when present"},
        {"kind": "metric_moves", "metric_name": "clean_novel_acc",
         "values": [bind_clean, fn_clean, rc[CLEAN]["arms"][MEMO]["novel"]["acc"], pop_shuf, bind_arb, bind_shuf],
         "extra": "arms MOVE: NBIND_clean=%.3f FREQ_NULL_clean=%.3f MEMO_clean=%.3f POP=%.3f NBIND_arb=%.3f NBIND_shuf=%.3f"
                  % (bind_clean, fn_clean, rc[CLEAN]["arms"][MEMO]["novel"]["acc"], pop_shuf, bind_arb, bind_shuf)},
        {"kind": "negative_control_margin",
         "control_scores": [fn_arb, pop_shuf],
         "headline_threshold": bind_clean, "higher_is_pass": True, "margin": ST_DISSOCIATION, "n_repeats_min": 2,
         "control_name": "arb_and_shuffle_nulls_below_clean_bind",
         "extra": "the ARBITRARY freq-null and the SHUFFLE POP floor sit far below NATIVE_BIND-clean; the must-fails "
                  "(ARBITRARY/SHUFFLE) confirm the CLEAN win requires genuine compositional structure, not leakage"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["bind_beats", "dissociates", "null_fails", "arb_mustfail", "shuf_mustfail",
                                    "ceiling_ok", "arms_differ", "homomorphism_ok", "decisive_verdict"],
         "exercised_gates": ["bind_beats", "dissociates", "null_fails", "arb_mustfail", "shuf_mustfail",
                             "ceiling_ok", "arms_differ", "homomorphism_ok", "decisive_verdict"],
         "extra": "decisive_verdict=%s at self-test scale" % v_verdict},
    ], run_mode="self_test")

    out.update(
        homomorphism_ok=homomorphism_ok, homomorphism_pred=pred, homomorphism_expect=expect,
        clean_native_bind_novel=round(bind_clean, 5), clean_freq_null_novel=round(fn_clean, 5),
        clean_dissociation=round(bind_clean - fn_clean, 5),
        arb_native_bind_novel=round(bind_arb, 5), arb_freq_null_novel=round(fn_arb, 5),
        arb_gap=round(bind_arb - fn_arb, 5),
        shuf_native_bind_novel=round(bind_shuf, 5), shuf_pop_novel=round(pop_shuf, 5),
        shuf_gap=round(bind_shuf - pop_shuf, 5), oracle_clean_novel=round(orc_clean, 5),
        n_distinct_sigs_clean=n_sigs_clean, n_novel=res["n_novel"], n_seen=res["n_seen"],
        bind_beats=bind_beats, dissociates=dissociates, null_fails=null_fails, arb_mustfail=arb_mustfail,
        shuf_mustfail=shuf_mustfail, ceiling_ok=ceiling_ok, arms_differ=arms_differ, novel_seen_ok=novel_seen_ok,
        decisive_selftest_verdict=v_verdict, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["real_code_path", "substrate_signature", "positive_control", "metric_moves",
                                     "negative_control_margin", "full_gates_exercised"],
    )
    ok = bool(homomorphism_ok and bind_beats and dissociates and null_fails and arb_mustfail and shuf_mustfail
              and ceiling_ok and arms_differ and novel_seen_ok)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def core_main(run_mode):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode])
    seeds = cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("run_mode=%s seeds=%s n_dim=%s L=%s noise_p=%s mode=%s"
         % (run_mode, seeds, cfg["n_dim"], cfg["L"], cfg["noise_p"], cfg["mode"]))

    st_ok, st_res = mechanism_selftest()
    _log("mechanism_selftest ok=%s | clean_bind=%s clean_freqnull=%s diss=%s arb_gap=%s shuf_gap=%s homo_ok=%s vp_ok=%s"
         % (st_ok, st_res.get("clean_native_bind_novel"), st_res.get("clean_freq_null_novel"),
            st_res.get("clean_dissociation"), st_res.get("arb_gap"), st_res.get("shuf_gap"),
            st_res.get("homomorphism_ok"), st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED: %s"
                        % {kk: st_res.get(kk) for kk in ("homomorphism_ok", "bind_beats", "dissociates", "null_fails",
                           "arb_mustfail", "shuf_mustfail", "ceiling_ok", "arms_differ", "novel_seen_ok")},
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS CONJUNCTION_NATIVE_BIND_VS_HOMOPHILY: FHRR bind is the group homomorphism "
                        "(bind(a,b)=code[(a+b)%L]); on the synthetic additive-conjunction arena NATIVE_BIND solves "
                        "NOVEL combos while the frequency/homophily null fails; the ARBITRARY + SHUFFLE must-fails fire; "
                        "6 validity-preflight checks declared. REAL CSKG FULL measures whether real value-skew lets the "
                        "frequency null climb (reframe weakens) or it stays near chance (reframe holds).",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_seed = []
    unit_failures = []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d rels=%d pool_edges=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["n_rel_tokens"], len(pool)))
            res, _prep = run_seed(pool, cfg, seed)
            if res.get("invalid"):
                raise RuntimeError("invalid corpus: %s (prov=%s)" % (res["invalid"], res.get("prov")))
            if int(res["n_query"]) < cfg["min_query"]:
                raise RuntimeError("held-out query entities too few (%d < %d)" % (int(res["n_query"]), cfg["min_query"]))
            if int(res["n_novel"]) < cfg["min_novel"]:
                raise RuntimeError("novel stratum too small (%d < %d)" % (int(res["n_novel"]), cfg["min_novel"]))
            if int(res["n_seen"]) < 3:
                raise RuntimeError("seen stratum too small (%d)" % int(res["n_seen"]))
            n_sigs = len(set(res["regimes"][CLEAN]["sigs"].values()))
            if n_sigs < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d n_sigs_clean=%d" % (seed, n_sigs))
            res["cskg_provenance"] = prov
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            rc = res["regimes"]
            _log("seed=%d nq=%d novel=%d seen=%d relA=%s relB=%s | CLEAN NBIND=%s FREQNULL=%s | ARB gap=%s | SHUF NBIND=%s POP=%s | (%.1fs)"
                 % (seed, res["n_query"], res["n_novel"], res["n_seen"], res["relA"], res["relB"],
                    _fmt(rc[CLEAN]["arms"][NBIND]["novel"]["acc"]), _fmt(_freq_null(rc[CLEAN], "novel", "acc")),
                    _fmt(rc[ARBITRARY]["arms"][NBIND]["novel"]["acc"] - _freq_null(rc[ARBITRARY], "novel", "acc")),
                    _fmt(rc[SHUFFLE]["arms"][NBIND]["novel"]["acc"]), _fmt(rc[SHUFFLE]["arms"][POP]["novel"]["acc"]),
                    time.time() - ts))
            _hb("cskg", si + 1)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            unit_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), unit_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            unit_failures=unit_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = decisive_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), n_seeds=len(seeds), seeds=seeds,
                   config=cfg, gates=gates, mechanism_selftest=st_res, unit_failures=unit_failures,
                   per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "memsmoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")  # CPU-only cell (no SGD)
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else args.run_mode
    if not args.self_test and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "memsmoke", "full"):
            run_mode = _env_mode
        if "memsmoke" in os.environ.get("HDLAB_EXP_NAME", "").lower():
            run_mode = "memsmoke"
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
