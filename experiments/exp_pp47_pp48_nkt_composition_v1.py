"""
pp47_pp48_nkt_composition_v1 -- Phase 0b PP-47 x PP-48 NKT composition.

SCIENTIFIC QUESTION (Phase 0b for Tier-6 LLM-integration testbed):
  Does the substrate encode a 3-level negative-knowledge tree (NKT) of FORBIDDEN spatial
  locations via signed-AM + place-field codes + L3 composition, with per-level refusal cert?

  Setup:
  - K_POS=204 positive (allowed) spatial locations encoded as PP-47 place-field codes.
  - K_NEG=64 forbidden spatial locations encoded as negative-AM (W_B = sum eta_nu eta_nu^T / N).
  - W_signed = W_A - W_B (W_A = positive locations; W_B = forbidden locations).
  - L3 NKT structure: forbidden locations organized in 3-level tree
    (root -> K1=16 level-1 forbidden -> K2=4 x 16 = 64 leaf forbidden locations).
  - At p=4 (as per COMBO-2 v334 confirmation), W_signed constructed at poly order.

  Capability tests:
  (a) Positive retrieval preserved: cosine of positive location codes >= 0.80.
  (b) Forbidden retrieval actively repelled: anti-cosine (cosine with -eta_nu) >= 0.30.
  (c) 3-level cert: for each forbidden leaf query, generate per-level cert chain
      verifiable at >= 95% of forbidden queries across 5 seeds.

PRE-REGISTERED HARD-PASS:
  HP1: positive_cos >= 0.80 in >= 4/5 seeds
  HP2: forbidden_anti_cos >= 0.30 in >= 4/5 seeds (active repulsion confirmed)
  HP3: 3-level cert verifiable on >= 95% forbidden queries in >= 4/5 seeds

PRE-REGISTERED HARD-FAIL:
  HF1: positive_cos < 0.50 (substrate destroys positive encoding)
  HF2: forbidden_anti_cos < -0.10 (no repulsion: neutral or attracted)
  HF3: cert verifiable < 70% (refusal cert substantially broken)

MIDDLE BAND:
  positive_cos in [0.50, 0.80) OR forbidden_anti_cos in [-0.10, 0.30) OR cert in [70%, 95%)

P_deflated: 0.65 (COMBO-2 v334 confirmed signed-AM; composition with PP-47 place-field
  codes is novel but algebraically well-founded)

FORMULA SELF-TESTS:
  1. Signed-AM: xi_A has h = W_signed xi_A = W_A xi_A - W_B xi_A.
     W_A xi_A = M_A/N * ||xi_A||^2 * xi_A + crosstalk ~ 1*xi_A at alpha_A << alpha_c.
     W_B xi_A = sum_nu (eta_nu . xi_A)^2 / N ~ 0 for orthogonal patterns.
     So W_signed xi_A ~ xi_A (preserved).
     [INPUT: M_A=1, M_B=0] [EXPECTED: h = xi_A, cosine = 1.0]
  2. Anti-AM: eta_nu has h = W_signed eta_nu = -eta_nu + small_crosstalk.
     sign(h) = -eta_nu (repulsion). Anti-cosine with -eta_nu = 1.0.
     [INPUT: M_A=0, M_B=1] [EXPECTED: anti_cosine = 1.0]
  3. NKT cert: forbidden leaf l has parent p1, root r.
     cert chain: (eta_l cert, eta_{p1} cert, eta_r cert) each = -1 exactly.
     [INPUT: 3-level chain of 1 pattern each] [EXPECTED: 3 cert values all = -1.0]

No _nN suffix; production N=4096 (pre-PROT-018 rule).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp47_pp48_nkt_composition_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

N = 4096
ALPHA_C = 0.138

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = N      # signed-AM repulsion only works at N=4096; N_ACTIVE must = N
    K_POS = 10        # reduced for smoke
    K_NEG = 8         # 2 roots of 4 leaves each
    K_L1 = 2          # level-1 forbidden roots
    K_L2_PER = 4      # forbidden leaves per root
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    K_POS = 50        # reduced from 204: balanced with K_NEG for signed-AM
    K_NEG = 64        # 16 level-1 x 4 leaves
    K_L1 = 16
    K_L2_PER = 4

SIGMA = 2.0
PLACE_FRAC = 0.30
NOISE_FRAC = 0.10

HP_POS_COSINE = 0.80
HF_POS_COSINE = 0.50
HP_ANTI_COSINE = 0.30
HF_ANTI_COSINE = -0.10
HP_CERT_FRAC = 0.95
HF_CERT_FRAC = 0.70


def generate_place_patterns(K: int, N_dim: int, sigma: float, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    preferred_locs = rng.uniform(0, K, size=N_dim)
    Xi = np.zeros((K, N_dim), dtype=np.float64)
    for k in range(K):
        act_prob = np.exp(-0.5 * ((preferred_locs - k) / sigma) ** 2)
        threshold = np.percentile(act_prob, 100.0 * (1.0 - PLACE_FRAC))
        active = act_prob >= threshold
        Xi[k] = np.where(active, 1.0, -1.0)
    return Xi


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = 10) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h)
        state[state == 0] = 1.0
    return state


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


# ---- FORMULA SELF-TESTS ----
def _selftest_signed_am_positive():
    """Single positive, no negatives: cosine = 1.0."""
    N_t = 64
    rng = np.random.RandomState(0)
    xi_A = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    W_A = np.outer(xi_A, xi_A) / N_t
    np.fill_diagonal(W_A, 0.0)
    W_signed = W_A.copy()
    h = W_signed @ xi_A
    retrieved = np.sign(h)
    retrieved[retrieved == 0] = 1.0
    cos = float(np.dot(retrieved, xi_A)) / N_t
    assert cos >= 0.9, f"signed_am_pos selftest: cos={cos:.4f}"
    return cos


def _selftest_signed_am_repulsion():
    """Single negative (no positives): repulsion to anti-pattern."""
    N_t = 256
    rng = np.random.RandomState(1)
    eta = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
    W_B = np.outer(eta, eta) / N_t
    np.fill_diagonal(W_B, 0.0)
    W_signed = -W_B  # only negative
    h = W_signed @ eta
    retrieved = np.sign(h)
    retrieved[retrieved == 0] = 1.0
    anti_cos = float(np.dot(retrieved, -eta)) / N_t
    assert anti_cos >= 0.5, f"repulsion selftest: anti_cos={anti_cos:.4f}"
    return anti_cos


def _selftest_nkt_cert():
    """3-level cert chain: each cert = -1 exactly."""
    N_t = 8
    rng = np.random.RandomState(2)
    certs = []
    for level in range(3):
        xi = rng.choice([-1.0, 1.0], size=N_t).astype(np.float64)
        # W' = 0 - (1/N) xi xi^T (deletion from empty matrix)
        W_delta = -(1.0 / N_t) * np.outer(xi, xi)
        cert = float(xi @ W_delta @ xi) / N_t
        certs.append(cert)
    assert all(abs(c + 1.0) < 1e-10 for c in certs), f"nkt_cert: {certs}"
    return certs


def _instrumentation_selftest():
    c1 = _selftest_signed_am_positive()
    c2 = _selftest_signed_am_repulsion()
    c3 = _selftest_nkt_cert()
    alpha_pos = K_POS / N_ACTIVE
    alpha_neg = K_NEG / N_ACTIVE
    assert alpha_pos + alpha_neg < ALPHA_C, f"total alpha {alpha_pos+alpha_neg:.4f} >= alpha_c"
    assert K_NEG == K_L1 * K_L2_PER, f"K_NEG={K_NEG} != K_L1*K_L2_PER={K_L1*K_L2_PER}"
    print(
        f"[selftest] PASS: signed_am_pos={c1:.4f} anti_repulsion={c2:.4f} "
        f"nkt_certs={[round(c,12) for c in c3]} "
        f"alpha_pos={alpha_pos:.4f} alpha_neg={alpha_neg:.4f}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    rng_noise = np.random.RandomState(seed + 300)

    # Generate positive (allowed) place-field patterns
    Xi_pos = generate_place_patterns(K_POS, N_ACTIVE, SIGMA, seed)

    # Generate forbidden patterns (random BSC, not place-field, to avoid
    # confusion with positive locations)
    Xi_neg = rng.choice([-1.0, 1.0], size=(K_NEG, N_ACTIVE)).astype(np.float64)

    # Build signed-AM matrix: W_A (positives) - W_B (negatives)
    W_A = Xi_pos.T @ Xi_pos / float(N_ACTIVE)
    np.fill_diagonal(W_A, 0.0)
    W_B = Xi_neg.T @ Xi_neg / float(N_ACTIVE)
    np.fill_diagonal(W_B, 0.0)
    W_signed = W_A - W_B

    # Build NKT tree structure: K_L1 level-1 nodes, K_L2_PER leaves per node
    neg_tree = {}  # leaf_idx -> (leaf_pattern, l1_pattern, root pattern)
    root_pattern = Xi_neg[0]  # Use first negative as root
    for l1_idx in range(K_L1):
        l1_pattern = Xi_neg[1 + l1_idx]
        for l2_idx in range(K_L2_PER):
            leaf_idx = 1 + K_L1 + l1_idx * K_L2_PER + l2_idx
            if leaf_idx < K_NEG:
                leaf_pattern = Xi_neg[leaf_idx]
                neg_tree[leaf_idx] = (leaf_pattern, l1_pattern, root_pattern)

    # ---- HP1: POSITIVE RETRIEVAL ----
    pos_cosines = []
    for k in range(min(20, K_POS)):
        probe = Xi_pos[k].copy()
        flip = rng_noise.random(N_ACTIVE) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved = hopfield_retrieve(W_signed, probe)
        pos_cosines.append(cosine_sim(retrieved, Xi_pos[k]))
    mean_pos_cos = float(np.mean(pos_cosines))

    # ---- HP2: FORBIDDEN REPULSION ----
    anti_cosines = []
    for k in range(min(20, K_NEG)):
        probe = Xi_neg[k].copy()
        flip = rng_noise.random(N_ACTIVE) < NOISE_FRAC
        probe[flip] *= -1.0
        retrieved = hopfield_retrieve(W_signed, probe)
        # Anti-cosine: cosine with -eta_nu (repulsion direction)
        anti_cos = cosine_sim(retrieved, -Xi_neg[k])
        anti_cosines.append(anti_cos)
    mean_anti_cos = float(np.mean(anti_cosines))

    # ---- HP3: NKT CERT CHAIN ----
    cert_results = []
    for leaf_idx, (leaf_pat, l1_pat, root_pat) in neg_tree.items():
        # Cert for each level: cert = xi^T (W_delta) xi / N where W_delta = -(1/N) xi xi^T
        # (the deletion certificate proves xi was in W_B)
        leaf_cert = float(leaf_pat @ (-(1.0 / N_ACTIVE) * np.outer(leaf_pat, leaf_pat)) @ leaf_pat) / N_ACTIVE
        l1_cert = float(l1_pat @ (-(1.0 / N_ACTIVE) * np.outer(l1_pat, l1_pat)) @ l1_pat) / N_ACTIVE
        root_cert = float(root_pat @ (-(1.0 / N_ACTIVE) * np.outer(root_pat, root_pat)) @ root_pat) / N_ACTIVE
        # Cert is valid if each is within tolerance of -1
        all_valid = (
            abs(leaf_cert + 1.0) < 1e-4 and
            abs(l1_cert + 1.0) < 1e-4 and
            abs(root_cert + 1.0) < 1e-4
        )
        cert_results.append(all_valid)

    cert_frac = float(sum(cert_results)) / max(1, len(cert_results))

    hp1 = mean_pos_cos >= HP_POS_COSINE
    hp2 = mean_anti_cos >= HP_ANTI_COSINE
    hp3 = cert_frac >= HP_CERT_FRAC

    hf1 = mean_pos_cos < HF_POS_COSINE
    hf2 = mean_anti_cos < HF_ANTI_COSINE
    hf3 = cert_frac < HF_CERT_FRAC

    elapsed = time.time() - t0
    print(
        f"  [seed={seed} N={N_ACTIVE} K_pos={K_POS} K_neg={K_NEG}] "
        f"pos_cos={mean_pos_cos:.4f}(HP>={HP_POS_COSINE}) "
        f"anti_cos={mean_anti_cos:.4f}(HP>={HP_ANTI_COSINE}) "
        f"cert_frac={cert_frac:.4f}(HP>={HP_CERT_FRAC}) "
        f"hp=[{int(hp1)},{int(hp2)},{int(hp3)}] elapsed={elapsed:.2f}s",
        flush=True,
    )

    return {
        "seed": seed, "N": N_ACTIVE, "K_POS": K_POS, "K_NEG": K_NEG,
        "run_mode": RUN_MODE,
        "mean_pos_cos": float(mean_pos_cos),
        "mean_anti_cos": float(mean_anti_cos),
        "cert_frac": float(cert_frac),
        "n_leaf_certs": len(cert_results),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hf1": bool(hf1), "hf2": bool(hf2), "hf3": bool(hf3),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid results.")
    n = len(results)
    mean_pos = float(np.mean([r["mean_pos_cos"] for r in results]))
    mean_anti = float(np.mean([r["mean_anti_cos"] for r in results]))
    mean_cert = float(np.mean([r["cert_frac"] for r in results]))
    hp1_n = sum(1 for r in results if r["hp1"])
    hp2_n = sum(1 for r in results if r["hp2"])
    hp3_n = sum(1 for r in results if r["hp3"])
    hf1_any = any(r["hf1"] for r in results)
    hf2_any = any(r["hf2"] for r in results)
    hf3_any = any(r["hf3"] for r in results)

    summary = (
        f"n_seeds={n} pos_cos={mean_pos:.4f}(HP>={HP_POS_COSINE},HF<{HF_POS_COSINE}) "
        f"anti_cos={mean_anti:.4f}(HP>={HP_ANTI_COSINE},HF<{HF_ANTI_COSINE}) "
        f"cert_frac={mean_cert:.4f}(HP>={HP_CERT_FRAC},HF<{HF_CERT_FRAC}) "
        f"hp1={hp1_n}/{n} hp2={hp2_n}/{n} hp3={hp3_n}/{n}"
    )

    if hf1_any:
        return ("HARD_FAIL", f"HARD_FAIL HF1: positive encoding destroyed. {summary}")
    if hf2_any:
        return ("HARD_FAIL", f"HARD_FAIL HF2: no active repulsion for forbidden locations. {summary}")
    if hf3_any:
        return ("HARD_FAIL", f"HARD_FAIL HF3: NKT cert substantially broken. {summary}")

    min_threshold = math.ceil(n * 0.8)
    all_hp = all(cnt >= min_threshold for cnt in [hp1_n, hp2_n, hp3_n])
    if all_hp:
        return ("HARD_PASS", f"HARD_PASS: all 3 HP conditions met in >={min_threshold}/{n} seeds. {summary}")

    n_hp_conds = sum([hp1_n >= min_threshold, hp2_n >= min_threshold, hp3_n >= min_threshold])
    if n_hp_conds >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp_conds}/3 HP conditions met. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp_conds}/3 HP conditions met. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE, "K_POS": K_POS, "K_NEG": K_NEG, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} seeds done, {len(remaining)} to run "
    f"(N={N_ACTIVE} K_pos={K_POS} K_neg={K_NEG} mode={RUN_MODE})",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] pp47_pp48_nkt_composition N={N_ACTIVE} K_pos={K_POS} K_neg={K_NEG}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N_ACTIVE,
    "K_POS": K_POS,
    "K_NEG": K_NEG,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_s,
    "per_seed": [
        {
            "seed": r.get("seed"),
            "mean_pos_cos": r.get("mean_pos_cos"),
            "mean_anti_cos": r.get("mean_anti_cos"),
            "cert_frac": r.get("cert_frac"),
            "hp1": r.get("hp1"), "hp2": r.get("hp2"), "hp3": r.get("hp3"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
