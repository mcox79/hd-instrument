"""substrate_resonator_multihop_integration_v1 -- INTEGRATE existing chain-grade
Resonator + confidence-tier gating into the concept_kg apples-to-apples harness.

USER pre-authored DISPATCH 1 (2026-06-24): today's concept_kg cell showed 2-hop
chained recovery = 0.638 (target >= 0.80). Per gap-mapping drill: existing
Store solution = Resonator (wave14_multihop_resonator + hdlab.multi_hop.iter_cleanup_chain;
CERT 585 K=2 chain-grade) + confidence-tier gating (substrate_72b_R0R1R2). This cell
INTEGRATES those existing chain-grade mechanisms, not novel research.

Three arms (all share same E/R/W per seed; ONE knob varies = composition mechanism):
  ARM_NAIVE_HEBBIAN_2HOP : control; reproduces 0.638 baseline (matches naive_chain)
  ARM_RESONATOR_2HOP     : PRIMARY; Modern-Hopfield beta-scaled softmax bundle per hop
                           (matches hdlab.multi_hop.iter_cleanup_chain semantics)
  ARM_RESONATOR_3HOP     : extends to 3-hop chained retrieval (chain-grade bonus)

Pre-reg HARD bands (PRIMARY = ARM_RESONATOR_2HOP top1):
  HARD_PASS  : top1 >= 0.85 AND cv across seeds <= 0.05
  MIDDLE_BAND: top1 in [0.70, 0.85)
  HARD_FAIL  : top1 < 0.70
  Sanity     : ARM_NAIVE_HEBBIAN_2HOP top1 in [0.59, 0.69] (reproduces 0.638)
  Bonus      : ARM_RESONATOR_3HOP top1 >= 0.70 (3-hop chain-grade)

Lane 1 substrate-native; pure numpy; CPU; ASCII; per-seed CONFIG_VERSION checkpoint.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
# PROT-021 defensive import (well below 4h floor, but kept for resume hygiene).
from experiments import _seed_checkpoint  # noqa: F401

ANCHOR_NAME = "substrate_resonator_multihop_integration_v1"
EXP_NAME = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)

# Pre-reg bands (PRIMARY = ARM_RESONATOR_2HOP top1)
SANITY_2HOP_LO = 0.59
SANITY_2HOP_HI = 0.69
RESONATOR_HARD_PASS = 0.85
RESONATOR_MIDDLE_LO = 0.70
RESONATOR_3HOP_BONUS = 0.70
CV_GATE = 0.05

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Concept graph dimensions (match base cell for direct comparability)
V_CONCEPTS = 200
V_PREDICATES = 10
K_SET = 20            # top-K bundle size for Modern-Hopfield cleanup (matches r1)
TAU_TERMINATE = None  # no early refuse for PRIMARY measurement (separate tau-sweep cell)

if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 1024
    N_CHAINS_2HOP = 80
    N_CHAINS_3HOP = 60
else:
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    N_CHAINS_2HOP = 300
    N_CHAINS_3HOP = 200

CONFIG_VERSION = (
    "resmh-v1: dense-bipolar HRR + multivalue-hebbian + 3arm-2/2/3hop; "
    "V_C=%d V_P=%d N=%d K_SET=%d tau=%s n2=%d n3=%d; "
    "bands sanity[%.2f,%.2f] resHP=%.2f resMB=%.2f r3=%.2f cv<=%.2f"
) % (V_CONCEPTS, V_PREDICATES, N_DIM, K_SET, str(TAU_TERMINATE),
     N_CHAINS_2HOP, N_CHAINS_3HOP,
     SANITY_2HOP_LO, SANITY_2HOP_HI, RESONATOR_HARD_PASS, RESONATOR_MIDDLE_LO,
     RESONATOR_3HOP_BONUS, CV_GATE)


# -- Substrate primitives (verbatim from base concept_kg cell) --------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Dense unit-norm bipolar vectors (M, n). The proven U1 primitive."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float, n_dim: int,
                   batch: int = 2000) -> np.ndarray:
    """Multi-value Hebbian-accumulate: W = sum_i outer(E[o_i], key_i)/N.
    key = E[s] * R[p] * sqrt(N). The U1 / n8 / concept_kg primitive."""
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def _l2_normalize(v: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    nrm = np.linalg.norm(v)
    return v / (nrm + eps)


def _softmax(x: np.ndarray) -> np.ndarray:
    z = x - x.max()
    ez = np.exp(z)
    return ez / ez.sum()


# -- Chain mechanisms (ARM 1 naive; ARM 2/3 resonator) ----------------------

def chain_naive(W: np.ndarray, E: np.ndarray, R: np.ndarray, sq: float,
                start: int, relations: List[int]) -> int:
    """ARM_NAIVE_HEBBIAN_2HOP/3HOP composition: per-hop W @ (state * R[p] * sq) + argmax(E @ state).
    Matches hdlab.multi_hop.naive_chain semantics. Final = last hop argmax."""
    state = E[start].copy()
    last = start
    for p in relations:
        state = W @ (state * R[p] * sq)
        last = int((E @ state).argmax())
    return last


def chain_resonator(W: np.ndarray, E: np.ndarray, R: np.ndarray, sq: float,
                    start: int, relations: List[int], k_set: int,
                    beta: float, tau_terminate: float | None) -> tuple[int | None, list[float]]:
    """ARM_RESONATOR composition: per-hop Modern-Hopfield beta-scaled softmax bundle
    over top-K_set entities, then L2-renormalize. Matches
    hdlab.multi_hop.iter_cleanup_chain semantics (k_inner=1; standard one-step Hopfield).

    tau_terminate: if not None, early-refuse (return None) when per-hop top1 < tau.
                   Set None for primary measurement (measure pure cleanup gain).
    Returns (final_entity_or_None, per_hop_top1_confs)."""
    state = _l2_normalize(E[start].copy())
    per_hop_conf: list[float] = []
    for p in relations:
        transit = W @ (state * R[p] * sq)
        transit = _l2_normalize(transit)
        # Ramsauer 2021 Modern-Hopfield: scores = E @ transit (cosine since both unit-norm).
        # beta = N is the substrate-appropriate sharpening (per hdlab.multi_hop.iter_cleanup_chain).
        ent_scores = E @ transit
        # top-K_set indices + scores
        top_idx = np.argpartition(ent_scores, -k_set)[-k_set:]
        top_conf = ent_scores[top_idx]
        top1 = float(top_conf.max())
        per_hop_conf.append(top1)
        if tau_terminate is not None and top1 < tau_terminate:
            return None, per_hop_conf
        # Modern-Hopfield bundle: softmax(beta * scores) weighted sum of top-K entity vectors.
        w = _softmax(beta * top_conf)
        state = (w[:, None] * E[top_idx]).sum(axis=0)
        state = _l2_normalize(state)
    final_scores = E @ state
    return int(final_scores.argmax()), per_hop_conf


# -- Synthetic chain builders ----------------------------------------------

def make_two_hop_chains(n_chains: int, V: int, P: int, g: np.random.Generator,
                        p1: int = 0, p2: int = 1):
    """Make 2-hop chains: (s,p1,x) + (x,p2,o). Distinct s,x,o; p1 != p2.
    Returns (train_triples, chain_queries=[(s,p1,p2,o,x_gt),...])."""
    train: list[tuple[int, int, int]] = []
    queries: list[tuple[int, int, int, int, int]] = []
    used_s: set[int] = set()
    tries = 0
    while len(queries) < n_chains and tries < n_chains * 100:
        tries += 1
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        x = int(g.integers(0, V))
        while x == s:
            x = int(g.integers(0, V))
        o = int(g.integers(0, V))
        while o == s or o == x:
            o = int(g.integers(0, V))
        train.append((s, p1, x))
        train.append((x, p2, o))
        queries.append((s, p1, p2, o, x))
        used_s.add(s)
    return train, queries


def make_three_hop_chains(n_chains: int, V: int, P: int, g: np.random.Generator,
                          p1: int = 0, p2: int = 1, p3: int = 2):
    """Make 3-hop chains: (s,p1,x) + (x,p2,y) + (y,p3,o). All distinct.
    Returns (train_triples, queries=[(s,p1,p2,p3,o,x_gt,y_gt),...])."""
    train: list[tuple[int, int, int]] = []
    queries: list[tuple[int, int, int, int, int, int, int]] = []
    used_s: set[int] = set()
    tries = 0
    while len(queries) < n_chains and tries < n_chains * 100:
        tries += 1
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        x = int(g.integers(0, V))
        while x == s:
            x = int(g.integers(0, V))
        y = int(g.integers(0, V))
        while y in (s, x):
            y = int(g.integers(0, V))
        o = int(g.integers(0, V))
        while o in (s, x, y):
            o = int(g.integers(0, V))
        train.append((s, p1, x))
        train.append((x, p2, y))
        train.append((y, p3, o))
        queries.append((s, p1, p2, p3, o, x, y))
        used_s.add(s)
    return train, queries


# -- Self-test -------------------------------------------------------------

def _selftest():
    """1-second mechanism check: storage + resonator + naive both end-to-end on tiny graph."""
    g = np.random.default_rng(0)
    n = 256
    V = 40
    P = 4
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)
    # tiny 2-hop set
    train, queries = make_two_hop_chains(10, V, P, g)
    W = ingest_hebbian(train, E, R, sq, n)
    # 1-hop sanity (build keys directly; ensure ingest learned something)
    s_p_o = train[:8]
    keys = np.stack([E[s] * R[p] * sq for (s, p, _o) in s_p_o]).astype(np.float32)
    scores = (E @ (W @ keys.T)).T
    hop1_top1 = float((scores.argmax(axis=1) == np.array([o for (_s, _p, o) in s_p_o])).mean())
    assert hop1_top1 >= 0.5, f"selftest 1-hop weak (got {hop1_top1:.2f})"
    # 2-hop chain primitives both produce finite outputs
    if len(queries) >= 4:
        naive_hits = 0
        res_hits = 0
        for (s, p1, p2, o_true, _x) in queries[:4]:
            n_pred = chain_naive(W, E, R, sq, s, [p1, p2])
            r_pred, _confs = chain_resonator(W, E, R, sq, s, [p1, p2],
                                             k_set=10, beta=float(n), tau_terminate=None)
            assert isinstance(n_pred, int) and 0 <= n_pred < V, "naive chain bad output"
            assert r_pred is not None and 0 <= r_pred < V, "resonator chain bad output"
            naive_hits += int(n_pred == o_true)
            res_hits += int(r_pred == o_true)
        # accept any finite output; smoke-scale signal is not the gate
        assert math.isfinite(naive_hits / 4), "naive chain finite-output check"
        assert math.isfinite(res_hits / 4), "resonator chain finite-output check"
    # 3-hop primitive runs end-to-end
    train3, q3 = make_three_hop_chains(4, V, P, g)
    W3 = ingest_hebbian(train3, E, R, sq, n)
    if q3:
        (s, p1, p2, p3, _o, _x, _y) = q3[0]
        r_pred3, confs3 = chain_resonator(W3, E, R, sq, s, [p1, p2, p3],
                                          k_set=10, beta=float(n), tau_terminate=None)
        assert r_pred3 is not None and 0 <= r_pred3 < V, "3-hop resonator bad output"
        assert len(confs3) == 3, "3-hop conf count"
    print("[selftest] PASS: resonator-multihop V=%d P=%d N=%d hop1_top1=%.2f"
          % (V, P, n, hop1_top1), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# -- Arm runners ------------------------------------------------------------

def arm_naive_hebbian_2hop(W, E, R, sq, queries) -> Dict:
    """Reproduces concept_kg ARM_2 chained baseline (~0.638)."""
    preds = np.array([chain_naive(W, E, R, sq, q[0], [q[1], q[2]]) for q in queries])
    o_true = np.array([q[3] for q in queries])
    top1 = float((preds == o_true).mean())
    return {"top1": round(top1, 4), "n_chains": len(queries),
            "chance": round(1.0 / V_CONCEPTS, 5)}


def arm_resonator_2hop(W, E, R, sq, queries, k_set: int, tau: float | None) -> Dict:
    """PRIMARY: Modern-Hopfield top-K bundle per hop."""
    beta = float(N_DIM)
    preds = []
    confs_top1_hop1 = []
    confs_top1_hop2 = []
    refused = 0
    for q in queries:
        s, p1, p2, o_true, _x_gt = q
        pred, confs = chain_resonator(W, E, R, sq, s, [p1, p2], k_set, beta, tau)
        if pred is None:
            refused += 1
            preds.append(-1)
        else:
            preds.append(pred)
        if len(confs) >= 1:
            confs_top1_hop1.append(confs[0])
        if len(confs) >= 2:
            confs_top1_hop2.append(confs[1])
    preds = np.array(preds)
    o_true = np.array([q[3] for q in queries])
    accepted = preds >= 0
    if accepted.any():
        top1_accepted = float((preds[accepted] == o_true[accepted]).mean())
    else:
        top1_accepted = 0.0
    top1_overall = float((preds == o_true).mean())  # refused count as wrong
    return {"top1": round(top1_overall, 4),
            "top1_accepted": round(top1_accepted, 4),
            "refused_frac": round(refused / max(len(queries), 1), 4),
            "k_set": k_set, "tau_terminate": tau, "beta": beta,
            "mean_conf_hop1": round(float(np.mean(confs_top1_hop1)) if confs_top1_hop1 else 0.0, 4),
            "mean_conf_hop2": round(float(np.mean(confs_top1_hop2)) if confs_top1_hop2 else 0.0, 4),
            "n_chains": len(queries),
            "chance": round(1.0 / V_CONCEPTS, 5)}


def arm_resonator_3hop(W, E, R, sq, queries, k_set: int, tau: float | None) -> Dict:
    """Bonus chain-grade probe at 3 hops."""
    beta = float(N_DIM)
    preds = []
    refused = 0
    for q in queries:
        s, p1, p2, p3, o_true, _x_gt, _y_gt = q
        pred, _confs = chain_resonator(W, E, R, sq, s, [p1, p2, p3], k_set, beta, tau)
        if pred is None:
            refused += 1
            preds.append(-1)
        else:
            preds.append(pred)
    preds = np.array(preds)
    o_true = np.array([q[4] for q in queries])
    accepted = preds >= 0
    if accepted.any():
        top1_accepted = float((preds[accepted] == o_true[accepted]).mean())
    else:
        top1_accepted = 0.0
    top1_overall = float((preds == o_true).mean())
    return {"top1": round(top1_overall, 4),
            "top1_accepted": round(top1_accepted, 4),
            "refused_frac": round(refused / max(len(queries), 1), 4),
            "k_set": k_set, "tau_terminate": tau, "beta": beta,
            "n_chains": len(queries),
            "chance": round(1.0 / V_CONCEPTS, 5)}


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(V_PREDICATES, N_DIM, g)
    t = time.time()

    # Build 2-hop train + chain queries (shared by ARM 1 + ARM 2)
    train2, q2 = make_two_hop_chains(N_CHAINS_2HOP, V_CONCEPTS, V_PREDICATES, g)
    W2 = ingest_hebbian(train2, E, R, sq, N_DIM)

    # Build SEPARATE 3-hop train + queries (different KB; clean Lane-1 measure)
    train3, q3 = make_three_hop_chains(N_CHAINS_3HOP, V_CONCEPTS, V_PREDICATES, g)
    W3 = ingest_hebbian(train3, E, R, sq, N_DIM)

    out = {"seed": seed,
           "config_version": CONFIG_VERSION,
           "V_concepts": V_CONCEPTS, "V_predicates": V_PREDICATES,
           "N_DIM": N_DIM, "K_SET": K_SET, "tau_terminate": TAU_TERMINATE,
           "run_mode": RUN_MODE}

    out["arm_naive_hebbian_2hop"] = arm_naive_hebbian_2hop(W2, E, R, sq, q2)
    print("  [seed=%d] ARM_NAIVE_HEBBIAN_2HOP top1=%.4f (n=%d chance=%.4f)"
          % (seed, out["arm_naive_hebbian_2hop"]["top1"],
             out["arm_naive_hebbian_2hop"]["n_chains"],
             out["arm_naive_hebbian_2hop"]["chance"]), flush=True)

    out["arm_resonator_2hop"] = arm_resonator_2hop(W2, E, R, sq, q2, K_SET, TAU_TERMINATE)
    print("  [seed=%d] ARM_RESONATOR_2HOP top1=%.4f (top1_accepted=%.4f refused=%.3f "
          "K_SET=%d beta=%.1f mean_conf=[h1=%.3f h2=%.3f])"
          % (seed, out["arm_resonator_2hop"]["top1"],
             out["arm_resonator_2hop"]["top1_accepted"],
             out["arm_resonator_2hop"]["refused_frac"],
             out["arm_resonator_2hop"]["k_set"],
             out["arm_resonator_2hop"]["beta"],
             out["arm_resonator_2hop"]["mean_conf_hop1"],
             out["arm_resonator_2hop"]["mean_conf_hop2"]), flush=True)

    out["arm_resonator_3hop"] = arm_resonator_3hop(W3, E, R, sq, q3, K_SET, TAU_TERMINATE)
    print("  [seed=%d] ARM_RESONATOR_3HOP top1=%.4f (top1_accepted=%.4f refused=%.3f)"
          % (seed, out["arm_resonator_3hop"]["top1"],
             out["arm_resonator_3hop"]["top1_accepted"],
             out["arm_resonator_3hop"]["refused_frac"]), flush=True)

    out["wall_s"] = round(time.time() - t, 1)
    return out


# -- Verdict ---------------------------------------------------------------

def verdict(ps: List[Dict]) -> Tuple[str, str]:
    """PRIMARY = ARM_RESONATOR_2HOP top1; sanity = ARM_NAIVE_HEBBIAN_2HOP top1 in [0.59, 0.69]."""
    naive_top1 = float(np.mean([p["arm_naive_hebbian_2hop"]["top1"] for p in ps]))
    naive_cv = float(np.std([p["arm_naive_hebbian_2hop"]["top1"] for p in ps]) / max(naive_top1, 1e-9))
    res2_top1 = float(np.mean([p["arm_resonator_2hop"]["top1"] for p in ps]))
    res2_cv = float(np.std([p["arm_resonator_2hop"]["top1"] for p in ps]) / max(res2_top1, 1e-9))
    res3_top1 = float(np.mean([p["arm_resonator_3hop"]["top1"] for p in ps]))
    res3_cv = float(np.std([p["arm_resonator_3hop"]["top1"] for p in ps]) / max(res3_top1, 1e-9))
    chance = 1.0 / V_CONCEPTS

    # Sanity: naive must reproduce baseline +- 0.05 (the gap-claim provenance).
    sanity_ok = (SANITY_2HOP_LO <= naive_top1 <= SANITY_2HOP_HI)
    # PRIMARY HARD_PASS conditions
    primary_pass = (res2_top1 >= RESONATOR_HARD_PASS) and (res2_cv <= CV_GATE)
    primary_middle = (res2_top1 >= RESONATOR_MIDDLE_LO) and (res2_top1 < RESONATOR_HARD_PASS)
    bonus_3hop_chain_grade = (res3_top1 >= RESONATOR_3HOP_BONUS)

    summ = ("NAIVE_2HOP top1=%.4f cv=%.3f (sanity=[%.2f,%.2f]) | "
            "RESONATOR_2HOP top1=%.4f cv=%.3f (HP>=%.2f cv<=%.2f) | "
            "RESONATOR_3HOP top1=%.4f cv=%.3f (bonus>=%.2f) | "
            "chance=%.4f V_C=%d V_P=%d N=%d K_SET=%d") % (
        naive_top1, naive_cv, SANITY_2HOP_LO, SANITY_2HOP_HI,
        res2_top1, res2_cv, RESONATOR_HARD_PASS, CV_GATE,
        res3_top1, res3_cv, RESONATOR_3HOP_BONUS,
        chance, V_CONCEPTS, V_PREDICATES, N_DIM, K_SET)
    sanity_tag = "sanity_ok" if sanity_ok else "sanity_MISMATCH"
    bonus_tag = " | BONUS_3HOP_CHAIN_GRADE" if bonus_3hop_chain_grade else ""

    if primary_pass and sanity_ok:
        return ("HARD_PASS",
                "HARD_PASS: Resonator integration closes 2-hop gap (top1=%.4f >= %.2f, cv=%.3f <= %.2f). "
                "Validates gap-map approach: existing chain-grade Resonator + confidence-tier gating "
                "PLUMBED into concept_kg apples-to-apples harness. %s%s | %s"
                % (res2_top1, RESONATOR_HARD_PASS, res2_cv, CV_GATE, sanity_tag, bonus_tag, summ))
    if primary_pass and not sanity_ok:
        # Resonator passes but baseline drifted -- still chain-grade but flag provenance.
        return ("HARD_PASS",
                "HARD_PASS_with_sanity_drift: Resonator top1=%.4f >= %.2f cv=%.3f, "
                "BUT naive baseline %.4f outside sanity [%.2f, %.2f] -- provenance for "
                "concept_kg 0.638 baseline did NOT cleanly reproduce; verdict honest "
                "but framing should NOT cite 0.638 as the prior measurement.%s | %s"
                % (res2_top1, RESONATOR_HARD_PASS, res2_cv, naive_top1,
                   SANITY_2HOP_LO, SANITY_2HOP_HI, bonus_tag, summ))
    if primary_middle:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: Resonator partial gain (top1=%.4f in [%.2f, %.2f), cv=%.3f); "
                "tune K_SET / beta / tau. %s%s | %s"
                % (res2_top1, RESONATOR_MIDDLE_LO, RESONATOR_HARD_PASS, res2_cv,
                   sanity_tag, bonus_tag, summ))
    return ("HARD_FAIL",
            "HARD_FAIL: Resonator integration does NOT close 2-hop gap (top1=%.4f < %.2f); "
            "gap-map approach needs revisit OR mechanism wired incorrectly. %s%s | %s"
            % (res2_top1, RESONATOR_MIDDLE_LO, sanity_tag, bonus_tag, summ))


# -- Driver ----------------------------------------------------------------

if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d V_P=%d K_SET=%d | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, V_PREDICATES, K_SET, CONFIG_VERSION),
          flush=True)
    t0 = time.time()
    out_dir = REPO / "data" / ("exp_%s" % EXP_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    ps: List[Dict] = []
    for s in SEEDS:
        pf = out_dir / ("partial_seed%d_%s.json" % (s, RUN_MODE))
        if pf.exists():
            try:
                rec = json.loads(pf.read_text(encoding="utf-8"))
                if rec.get("config_version") == CONFIG_VERSION:
                    print("  [seed=%d] RESUME from checkpoint (config match)" % s, flush=True)
                    ps.append(rec); continue
            except Exception:
                pass
        rec = run_seed(s)
        pf.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        ps.append(rec)
    v, vmsg = verdict(ps)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "config_version": CONFIG_VERSION,
        "per_seed": ps,
        "elapsed_s": round(time.time() - t0, 1),
        "summary": vmsg,
        "DESIGN_NOTE": (
            "USER pre-authored DISPATCH 1 (2026-06-24): integrates existing chain-grade "
            "Resonator (hdlab.multi_hop.iter_cleanup_chain; CERT 585 K=2) + confidence-tier "
            "gating (substrate_72b_R0R1R2) into the concept_kg apples-to-apples harness. "
            "Lane 1 substrate-native; ALL arms share same E/R/W per seed; ONE knob varies "
            "(composition mechanism: naive vs Modern-Hopfield top-K bundle). PRIMARY = "
            "ARM_RESONATOR_2HOP top1. Sanity = ARM_NAIVE_HEBBIAN_2HOP reproduces concept_kg "
            "0.638 baseline +- 0.05. Bonus = ARM_RESONATOR_3HOP >= 0.70 chain-grade.")
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
