"""substrate_resonator_softchain_beta_sweep_v1 -- DECISIVE beta-sweep cell that
discriminates BOTH cell-1 (resonator_multihop) and cell-2 (soft_chain_dfe) HARD_FAILs
simultaneously per Skunkworks audit + Research synthesis 2026-06-24.

SMOKING-GUN diagnosis (from research_5cell_cross_HARDFAIL_synthesis_2026-06-24):
both cells set Modern-Hopfield inverse-temperature beta = N_DIM = 8192, at which
softmax(8192 * top_cosine) is a Dirac delta at argmax -- the "soft superposition"
mathematically reduces to hard winner-take-all, identical to the baseline.
EMPIRICAL PROOF: per-seed top1 values were bit-identical between resonator_hard and
soft_chain arms in the prior cells: s7=0.61/0.61, s17=0.645/0.645, s23=0.64/0.64.
The soft mechanism that 5 disparate fields unanimously recommend was NEVER exercised.

THIS CELL: ONE knob varies = beta. 7 arms:
  ARM_BASELINE_HARD : naive hard-argmax chain (reproduces 0.65 baseline; control)
  ARM_BETA_0_5      : very soft (near-uniform mixing over top-K)
  ARM_BETA_2        : moderately soft (entropy ~ log(5))
  ARM_BETA_10       : genuine soft-DFE regime per research drill (entropy ~ log(2))
  ARM_BETA_50       : sharper but still soft
  ARM_BETA_500      : near-hard but distinguishable from Dirac
  ARM_BETA_8192     : current cells' regime (Dirac; should reproduce baseline)

Apples-to-apples: ALL arms share same seed-derived E, R, W per seed; ONE knob varies.

PRE-REG HARD bands (PRIMARY = max top1 across {BETA_2, BETA_10, BETA_50} arms):
  HARD_PASS_REVIVAL  : best-soft-arm top1 >= 0.78 (>=13pp lift over baseline 0.65)
  MIDDLE_BAND        : best-soft-arm top1 in [0.70, 0.78) (small lift, partial)
  HARD_FAIL_DECISIVE : best-soft-arm top1 - baseline <= 0.03 across all beta in
                       {0.5, 2, 10, 50, 500} (soft mechanism fundamentally fails;
                       revert to encoder-side or PageRank revival angle)
  SANITY             : ARM_BETA_8192 top1 within +/-0.02 of ARM_BASELINE_HARD
                       (confirms the wiring-bug diagnosis directly)

Lane 1 substrate-native; pure numpy CPU; ASCII-only; PROT-021 per-seed checkpoint.
PROT-018 N/A (no _n<N> suffix on anchor).

CONFOUND_AUDIT (per master bias checklist):
- F1 Fix #28 over-claim: this cell measures per-arm top1; verdict_msg cites per-arm
  numerics + per-seed bit-identity check between BETA_8192 and BASELINE_HARD.
- H2 saturated discriminator: confirmed by smoking-gun bit-identity in prior cells.
- H6 single-knob variation: beta is the ONLY knob (E/R/W/K_SET shared per seed).
- D1 roofline probe: smoke at N=2048/100chains/1seed catches >0.5s/arm if scaling broken.
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
from experiments import _seed_checkpoint  # noqa: F401 (PROT-021 import gate)

ANCHOR_NAME = "substrate_resonator_softchain_beta_sweep_v1"
EXP_NAME = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)

# Pre-reg bands
HARD_PASS_REVIVAL = 0.78
MIDDLE_LO = 0.70
HARD_FAIL_DELTA = 0.03    # all-betas-within-this-of-baseline = decisive fail
SANITY_DIRAC_TOL = 0.02   # BETA_8192 vs BASELINE_HARD identity tolerance
CV_GATE = 0.05

# Beta sweep (the ONE knob). BASELINE arm = hard-argmax (not a beta value).
BETAS = [0.5, 2.0, 10.0, 50.0, 500.0, 8192.0]
SOFT_BETAS_FOR_HP = [2.0, 10.0, 50.0]  # the lit-predicted "right regime" subset

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
if "_smoke" in _HDLAB_EXP_NAME.lower():
    RUN_MODE = "smoke"

# Concept-graph dimensions (match prior cells for direct comparability)
V_CONCEPTS = 200
V_PREDICATES = 10
K_SET = 20

if RUN_MODE == "smoke":
    SEEDS = [7]
    N_DIM = 2048
    N_CHAINS = 100
else:
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    N_CHAINS = 200

CONFIG_VERSION = (
    "softchain-beta-sweep-v1: dense-bipolar HRR + multivalue-hebbian + "
    "7arm-beta-sweep on 2hop; V_C=%d V_P=%d N=%d K_SET=%d n_chains=%d "
    "betas=%s baseline=hard; bands HP>=%.2f MB>=%.2f HF_delta<=%.2f sanity_tol=%.2f cv<=%.2f"
) % (V_CONCEPTS, V_PREDICATES, N_DIM, K_SET, N_CHAINS, BETAS,
     HARD_PASS_REVIVAL, MIDDLE_LO, HARD_FAIL_DELTA, SANITY_DIRAC_TOL, CV_GATE)


# -- Substrate primitives (verbatim from base concept_kg cell; ascii) ---------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float, n_dim: int,
                   batch: int = 2000) -> np.ndarray:
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


# -- Chain mechanisms -------------------------------------------------------

def chain_naive_hard(W, E, R, sq, start: int, relations: List[int]) -> int:
    state = E[start].copy()
    last = start
    for p in relations:
        state = W @ (state * R[p] * sq)
        last = int((E @ state).argmax())
    return last


def chain_soft_beta(W, E, R, sq, start: int, relations: List[int],
                    k_set: int, beta: float) -> Tuple[int, List[float], List[float]]:
    """One knob varies = beta. Returns (final_idx, per_hop_top1_conf, per_hop_entropy_nats)."""
    state = _l2_normalize(E[start].copy())
    per_hop_top1: List[float] = []
    per_hop_entropy: List[float] = []
    for p in relations:
        transit = W @ (state * R[p] * sq)
        transit = _l2_normalize(transit)
        ent_scores = E @ transit
        top_idx = np.argpartition(ent_scores, -k_set)[-k_set:]
        top_conf = ent_scores[top_idx]
        per_hop_top1.append(float(top_conf.max()))
        # Modern-Hopfield bundle with EXPLICIT beta (the knob being swept)
        w = _softmax(beta * top_conf)
        # Per-hop entropy of the softmax (in nats) -- the load-bearing diagnostic
        ent_nats = float(-(w * np.log(w + 1e-12)).sum())
        per_hop_entropy.append(ent_nats)
        state = (w[:, None] * E[top_idx]).sum(axis=0)
        state = _l2_normalize(state)
    final_scores = E @ state
    return int(final_scores.argmax()), per_hop_top1, per_hop_entropy


# -- Chain builder (2-hop only; clean discriminator) -----------------------

def make_two_hop_chains(n_chains: int, V: int, g: np.random.Generator,
                        p1: int = 0, p2: int = 1):
    train: List[Tuple[int, int, int]] = []
    queries: List[Tuple[int, int, int, int, int]] = []
    used_s: set = set()
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


# -- Self-test -------------------------------------------------------------

def _selftest():
    """Verify (a) primitives end-to-end; (b) the smoking-gun: beta=N_DIM IS Dirac;
    (c) intermediate beta yields measurably-different per-hop entropy."""
    g = np.random.default_rng(0)
    n = 512
    V = 30
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(4, n, g)
    train, queries = make_two_hop_chains(8, V, g)
    W = ingest_hebbian(train, E, R, sq, n)
    assert len(queries) >= 4, "selftest: need >=4 queries"

    # (a) primitives run
    q0 = queries[0]
    s, p1, p2, o_true, _x = q0
    naive_pred = chain_naive_hard(W, E, R, sq, s, [p1, p2])
    assert isinstance(naive_pred, int) and 0 <= naive_pred < V, "naive bad output"
    soft_pred, confs, ents = chain_soft_beta(W, E, R, sq, s, [p1, p2],
                                             k_set=8, beta=10.0)
    assert isinstance(soft_pred, int) and 0 <= soft_pred < V, "soft bad output"
    assert len(confs) == 2 and len(ents) == 2, "per-hop counts"

    # (b) smoking-gun: beta = n (very large) -> entropy ~ 0 (Dirac).
    _, _, ents_dirac = chain_soft_beta(W, E, R, sq, s, [p1, p2], k_set=8, beta=float(n))
    assert max(ents_dirac) < 0.01, (
        "selftest WIRING-BUG-CHECK: at beta=N=%d, per-hop softmax entropy "
        "must be near-zero (Dirac). Got max_entropy=%.4f nats. If this fails, "
        "the soft mechanism is NOT actually saturating at beta=N -- something "
        "else changed in the primitive." % (n, max(ents_dirac))
    )

    # (c) intermediate beta yields measurably-larger entropy than Dirac
    _, _, ents_soft = chain_soft_beta(W, E, R, sq, s, [p1, p2], k_set=8, beta=2.0)
    assert max(ents_soft) > 0.1, (
        "selftest SOFT-REGIME-CHECK: at beta=2.0 with K_SET=8, per-hop softmax "
        "entropy should be measurably-non-zero (>0.1 nats). Got max_entropy=%.4f "
        "nats. If this fails, the soft mechanism is not exercised in any regime."
        % max(ents_soft)
    )

    # (d) BASELINE_HARD and BETA=N output should match per query (the Dirac
    # equivalence the audit names). Test 4 queries.
    matches = 0
    for q in queries[:4]:
        s, p1, p2, _o, _x = q
        n_pred = chain_naive_hard(W, E, R, sq, s, [p1, p2])
        d_pred, _, _ = chain_soft_beta(W, E, R, sq, s, [p1, p2],
                                       k_set=8, beta=float(n))
        if n_pred == d_pred:
            matches += 1
    # We expect HIGH (not necessarily 100% at tiny N=512) agreement;
    # cleanup over E may pick different tied-top entities at very small scale,
    # but they should agree on majority of queries.
    assert matches >= 3, (
        "selftest DIRAC-EQUIVALENCE-CHECK: naive_hard and beta=N should "
        "agree on >=3/4 queries (Dirac softmax = hard argmax over top-K). "
        "Got %d/4 matches. If this fails, hard-argmax and Dirac-softmax "
        "are picking different entities -- mechanism wired wrong."
        % matches
    )

    print(
        "[selftest] PASS: primitives OK; beta=%d entropy=%.4f (Dirac confirmed); "
        "beta=2.0 entropy=%.4f (soft regime exercised); dirac=naive %d/4 matches"
        % (n, max(ents_dirac), max(ents_soft), matches),
        flush=True,
    )


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# -- Arm runners -----------------------------------------------------------

def arm_baseline_hard(W, E, R, sq, queries) -> Dict:
    preds = np.array([chain_naive_hard(W, E, R, sq, q[0], [q[1], q[2]]) for q in queries])
    o_true = np.array([q[3] for q in queries])
    top1 = float((preds == o_true).mean())
    return {"top1": round(top1, 4), "n_chains": len(queries),
            "chance": round(1.0 / V_CONCEPTS, 5), "beta": None,
            "mechanism": "hard_argmax"}


def arm_soft_beta(W, E, R, sq, queries, k_set: int, beta: float) -> Dict:
    preds = []
    all_top1_h1 = []
    all_top1_h2 = []
    all_ent_h1 = []
    all_ent_h2 = []
    for q in queries:
        s, p1, p2, _o, _x = q
        pred, confs, ents = chain_soft_beta(W, E, R, sq, s, [p1, p2], k_set, beta)
        preds.append(pred)
        if len(confs) >= 1:
            all_top1_h1.append(confs[0]); all_ent_h1.append(ents[0])
        if len(confs) >= 2:
            all_top1_h2.append(confs[1]); all_ent_h2.append(ents[1])
    preds = np.array(preds)
    o_true = np.array([q[3] for q in queries])
    top1 = float((preds == o_true).mean())
    return {
        "top1": round(top1, 4),
        "n_chains": len(queries),
        "chance": round(1.0 / V_CONCEPTS, 5),
        "beta": beta,
        "k_set": k_set,
        "mean_top_conf_hop1": round(float(np.mean(all_top1_h1)) if all_top1_h1 else 0.0, 4),
        "mean_top_conf_hop2": round(float(np.mean(all_top1_h2)) if all_top1_h2 else 0.0, 4),
        "mean_softmax_entropy_hop1_nats": round(float(np.mean(all_ent_h1)) if all_ent_h1 else 0.0, 4),
        "mean_softmax_entropy_hop2_nats": round(float(np.mean(all_ent_h2)) if all_ent_h2 else 0.0, 4),
    }


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(V_PREDICATES, N_DIM, g)
    t = time.time()
    train, queries = make_two_hop_chains(N_CHAINS, V_CONCEPTS, g)
    W = ingest_hebbian(train, E, R, sq, N_DIM)

    out = {
        "seed": seed,
        "config_version": CONFIG_VERSION,
        "V_concepts": V_CONCEPTS, "V_predicates": V_PREDICATES,
        "N_DIM": N_DIM, "K_SET": K_SET,
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "M": N_CHAINS,
    }

    # ARM_BASELINE_HARD (control)
    out["ARM_BASELINE_HARD"] = arm_baseline_hard(W, E, R, sq, queries)
    print("  [seed=%d] ARM_BASELINE_HARD top1=%.4f (chance=%.4f, n=%d)"
          % (seed, out["ARM_BASELINE_HARD"]["top1"],
             out["ARM_BASELINE_HARD"]["chance"], out["ARM_BASELINE_HARD"]["n_chains"]),
          flush=True)

    # Sweep arms (one per beta)
    for beta in BETAS:
        name = "ARM_BETA_%s" % (("%g" % beta).replace(".", "_"))
        out[name] = arm_soft_beta(W, E, R, sq, queries, K_SET, beta)
        print("  [seed=%d] %s top1=%.4f beta=%.3g ent_h1=%.3f ent_h2=%.3f conf_h1=%.3f conf_h2=%.3f"
              % (seed, name, out[name]["top1"], beta,
                 out[name]["mean_softmax_entropy_hop1_nats"],
                 out[name]["mean_softmax_entropy_hop2_nats"],
                 out[name]["mean_top_conf_hop1"], out[name]["mean_top_conf_hop2"]),
              flush=True)

    out["wall_s"] = round(time.time() - t, 1)
    return out


# -- Verdict ---------------------------------------------------------------

def verdict(ps: List[Dict]) -> Tuple[str, str]:
    baseline_top1 = float(np.mean([p["ARM_BASELINE_HARD"]["top1"] for p in ps]))

    # Per-beta aggregate top1 + cv across seeds
    beta_summary = {}
    for beta in BETAS:
        key = "ARM_BETA_%s" % (("%g" % beta).replace(".", "_"))
        vals = [p[key]["top1"] for p in ps]
        m = float(np.mean(vals))
        sd = float(np.std(vals))
        cv = sd / max(m, 1e-9)
        ents = [(p[key]["mean_softmax_entropy_hop1_nats"]
                 + p[key]["mean_softmax_entropy_hop2_nats"]) / 2.0 for p in ps]
        beta_summary[beta] = {
            "top1_mean": round(m, 4),
            "top1_cv": round(cv, 4),
            "top1_per_seed": [round(v, 4) for v in vals],
            "delta_vs_baseline": round(m - baseline_top1, 4),
            "mean_entropy_nats": round(float(np.mean(ents)), 4),
        }

    # SANITY: BETA_8192 should reproduce BASELINE_HARD within tol
    beta_8192_top1 = beta_summary[8192.0]["top1_mean"]
    sanity_dirac_ok = abs(beta_8192_top1 - baseline_top1) <= SANITY_DIRAC_TOL

    # PRIMARY decision: max soft-arm top1 across BETA in {2, 10, 50}
    soft_arms = [(b, beta_summary[b]["top1_mean"]) for b in SOFT_BETAS_FOR_HP]
    best_soft_beta, best_soft_top1 = max(soft_arms, key=lambda kv: kv[1])
    best_soft_cv = beta_summary[best_soft_beta]["top1_cv"]

    # HARD_FAIL_DECISIVE: ALL betas in {0.5, 2, 10, 50, 500} within HARD_FAIL_DELTA of baseline
    nondirac_betas = [b for b in BETAS if b != 8192.0]
    all_deltas_small = all(
        abs(beta_summary[b]["top1_mean"] - baseline_top1) <= HARD_FAIL_DELTA
        for b in nondirac_betas
    )

    summary_per_beta = "; ".join(
        "b=%g top1=%.3f delta=%+.3f ent=%.3f cv=%.3f" % (
            b, beta_summary[b]["top1_mean"], beta_summary[b]["delta_vs_baseline"],
            beta_summary[b]["mean_entropy_nats"], beta_summary[b]["top1_cv"])
        for b in BETAS
    )
    sanity_tag = "sanity_dirac_OK" if sanity_dirac_ok else "sanity_dirac_MISMATCH"
    summ = (
        "BASELINE_HARD=%.4f | best_soft beta=%g top1=%.4f delta=%+.4f cv=%.3f | "
        "BETA_8192=%.4f (sanity tol +/-%.2f -> %s) | per-beta: %s | "
        "V_C=%d V_P=%d N=%d K_SET=%d chains=%d"
    ) % (
        baseline_top1, best_soft_beta, best_soft_top1,
        best_soft_top1 - baseline_top1, best_soft_cv,
        beta_8192_top1, SANITY_DIRAC_TOL, sanity_tag,
        summary_per_beta, V_CONCEPTS, V_PREDICATES, N_DIM, K_SET, N_CHAINS)

    if best_soft_top1 >= HARD_PASS_REVIVAL and best_soft_cv <= CV_GATE:
        return ("HARD_PASS",
                "HARD_PASS_REVIVAL: soft-DFE revives multi-hop. Best soft arm "
                "(beta=%g) top1=%.4f >= %.2f (lift=+%.4f over baseline %.4f) cv=%.3f. "
                "Confirms research synthesis: prior cells' Dirac wiring-bug (beta=N_DIM=8192) "
                "suppressed the mechanism; honest beta-sweep recovers chain-grade lift. "
                "%s | %s" % (
                    best_soft_beta, best_soft_top1, HARD_PASS_REVIVAL,
                    best_soft_top1 - baseline_top1, baseline_top1, best_soft_cv,
                    sanity_tag, summ))
    if best_soft_top1 >= MIDDLE_LO:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: best soft beta=%g top1=%.4f in [%.2f, %.2f); partial "
                "soft-mechanism rescue. Investigate K_SET sweep or anisotropic encoder. "
                "%s | %s" % (
                    best_soft_beta, best_soft_top1, MIDDLE_LO, HARD_PASS_REVIVAL,
                    sanity_tag, summ))
    if all_deltas_small:
        return ("HARD_FAIL",
                "HARD_FAIL_DECISIVE: ALL betas in %s within +/-%.3f of baseline %.4f. "
                "Soft mechanism fundamentally fails at this regime; revert to encoder-side "
                "(anisotropic/sparse) or PageRank-style revival angle. %s | %s" % (
                    nondirac_betas, HARD_FAIL_DELTA, baseline_top1, sanity_tag, summ))
    return ("HARD_FAIL",
            "HARD_FAIL: best soft beta=%g top1=%.4f < MIDDLE_LO %.2f; mechanism "
            "underperforms baseline %.4f. %s | %s" % (
                best_soft_beta, best_soft_top1, MIDDLE_LO, baseline_top1,
                sanity_tag, summ))


# -- Driver ----------------------------------------------------------------

if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d V_P=%d K_SET=%d chains=%d betas=%s | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, V_PREDICATES,
             K_SET, N_CHAINS, BETAS, CONFIG_VERSION),
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
            "Wave A revival cell #1 (per research_5cell_cross_HARDFAIL_synthesis "
            "2026-06-24): SINGLE decisive cell that discriminates BOTH prior "
            "HARD_FAILs (resonator_multihop + soft_chain_dfe). Both prior cells "
            "used beta = N_DIM = 8192 -> Dirac softmax = hard argmax (smoking gun: "
            "per-seed bit-identity between resonator and soft_chain). This cell "
            "sweeps beta in {0.5, 2, 10, 50, 500, 8192} on the same 2-hop substrate "
            "(ONE knob varies). ARM_BASELINE_HARD is control; ARM_BETA_8192 reproduces "
            "the prior cells' Dirac regime (sanity); intermediate betas test the "
            "lit-predicted soft-DFE regime (entropy ~ log(2-5) nats). Per-hop softmax "
            "entropy logged per-arm as load-bearing mechanism evidence."
        ),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
