"""Reasoning-readout LENGTH-GENERALIZATION chain-grade (CLUTRR-style kinship) v1.

QUESTION (the reoriented, non-construction-determined chain-grade after atom 29363 proved
compositional generalization is FREE from binding): does a native-VSA iterative multi-hop reasoner
LEARN relational-composition rules from SHORT chains (length 2-4) and LENGTH-GENERALIZE to LONG chains
(up to 10) -- degrading gracefully -- better than a PARAM-MATCHED FLAT/single-hop baseline that provably
cannot chain, on a CLUTRR-style kinship task whose ceiling is honestly < 1.000?

WHY THIS IS NOT THE atom-29363 TRAP: multi-hop composition over a GOOD structural code is ALSO close to
"free" (a geometric consequence; same construction-determined trap). The genuine, LEARNED part lives at
LENGTH-GENERALIZATION, where the free geometry BREAKS (models fall from >0.9 at len 2-4 to 0.3-0.6 at
len 10). The load-bearing GUARD (per 29363): an ORACLE handed the true composition rules must NOT solve
length-10 for free (oracle_len10 < 0.90); the irreducible sub-1.0 ceiling comes from genuine relational
AMBIGUITY (gender/context underdetermination), the honest symbolic analog of CLUTRR's sub-1.0 ceiling.

------------------------------------------------------------------------------------------------
BRAIN GROUNDING (CITED@ notes/research_brain_reasoning_readout_multihop_constraint_chaingrade_target_2026-07-19.md)
------------------------------------------------------------------------------------------------
- Multi-hop over good structure is close to FREE (Bakermans-Whittington-Behrens 2024); rich-regime
  geometry BREAKS transitivity -> length-generalization is the part that ISN'T free. (Scan 2/3)
- CLUTRR: train kinship chains 2-4, test to 10; graph-relational >0.9 at 2-4 fall to 0.32-0.62 at 10;
  flat/single-hop FAIL to length-generalize = the mechanism-grounded must-fail baseline. (Scan 3)
- Asymmetry (order/rank/roles) carried by MONOTONIC/ORDINAL CONTENT codes + a SYMMETRIC/commutative
  bind; NO non-commutative neural binding operator exists (Dehaene number line; grid metric codes;
  Frankland-Greene role populations). The lever = ordered/monotonic position codes, not distinct-only.
  (Scan 4)
- Constraint-satisfaction resolution scaling is GENERIC MATH not learned (CAUTION, Scan 1): so the
  claim is NOT "more constraints = better resolution" (that would be construction-determined too); it is
  LEARNED pairwise rules that ITERATE and degrade with length where flat collapses.

------------------------------------------------------------------------------------------------
COMPUTE ARCHITECTURE (mandatory declaration)
------------------------------------------------------------------------------------------------
Class (b) sequential-CPU, BATCHED across chains (fold hop = batched [n_test,N]@[N,N] complex matmul).
Tiny FHRR reference computation; wall < ~90s full, < ~10s smoke, < ~5s self-test. No GPU (sub-100s).
LOCAL-ONLY foreground; not dispatched to a zombie-prone runner. Storage strategy: SHARDED (each
relation its own code; ARM_A cleans up to a clean code each hop). ARM_B's single bundle IS the
bundled must-fail arm. NO push, NO remote-persist, NO git add -A. needs_orchestrator_store_sync=True.

------------------------------------------------------------------------------------------------
ARMS (ONE variable = the compositional reasoner; identical data/codes/position-family/param budget)
------------------------------------------------------------------------------------------------
World (per seed): m named kinship-style relations; FHRR relation codes code[r] (unit phasors, N-dim);
MONOTONIC ordered position codes rho_pos[p] = base**p (fractional binding; grid/number-line-like).
A fixed per-seed pairwise composition kernel comp_dist[a,b,:] (distribution over results): fraction
`ambiguity_rate` of pairs map to a MIXTURE (p_major on the mode, rest on 1-2 alternates -> irreducible
sub-1.0 ceiling); the rest deterministic. Chains = iid base-relation sequences; answer = generative
LEFT-FOLD (sample each hop from comp_dist); model observes ONLY (sequence, final answer).

- ARM_A (native-VSA multi-hop reasoner): Hebbian heteroassociative composition memory
  W = sum_i outer(code[ans_i], key_i), key(a,b) = bind(rhoL,code[a]) + bind(rhoR,code[b]) (rhoL,rhoR
  ordered position codes; order carried by codes + COMMUTATIVE bind). W is LEARNED from length-2
  training pairs (direct pairwise observations). Inference: FOLD -- running=code[r1]; each hop
  est=W@key(running,next), cleanup to nearest relation code (sharded clean code), iterate to ANY length.
- ARM_B (param-matched FLAT/single-hop; provably cannot chain): chain_bundle = sum_i bind(rho_pos[i],
  code[r_i]) (same monotonic position family); ONE heteroassociative readout U = sum outer(code[ans],
  chain_bundle) ([N,N] complex, SAME shape/dtype as W) trained on length 2,3,4. No iteration. Fails at
  length > budget (4): rho_5..rho_10 never trained; single bundle blends k terms U never mapped.
  ARM_B is handed MORE usable data (all of 2-4) -> conservative for ARM_A.

------------------------------------------------------------------------------------------------
NUMBERS IN THIS FILE (tagging per META_RULE_AC)
------------------------------------------------------------------------------------------------
All quantitative outcomes are MEASURED@ data/exp_<anchor>[_smoke|_selftest]/metrics.json at run time.
Pre-registered bands are HYPOTHESIZED@ preregs/reasoning_readout_length_generalization_clutrr_cg_v1.md.
Capacity feasibility N>m^2 is THEORETICAL@ heteroassociative-linear-memory capacity ~ N patterns.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from _seed_checkpoint import (  # noqa: E402
    write_metrics as _write_metrics_helper,
    get_output_dir,
    record_gate,
)

ANCHOR_NAME = "reasoning_readout_length_generalization_clutrr_cg_v1"

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (ARM_A vs ARM_B prediction hashes)
# - final_metrics_atomicity = tmp_replace (via _seed_checkpoint.write_metrics)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a (accuracy GAP, not noise-floor); capacity feasibility N>m^2 verified
# - baseline_in_band: 0.10 < ARM_A_long < 0.90 AND oracle_len10 < 0.90
# - discriminator survives scale: smoke keeps full length range, long_gap fires
# - HARD_PASS strictly above floor (0.20 gap; band [0.05,~0.50])
# - cardinality_ok: EXPECTED_N_UNITS = seeds*conditions*lengths gate
# - deterministic seeding: default_rng + fixed ints + hashlib (no builtin hash / list(set()))


# --------------------------------------------------------------------------------------------
# World / data generator (relational monoid with ambiguous composition)
# --------------------------------------------------------------------------------------------
def make_world(rng: np.random.Generator, m: int, ambiguity_rate: float,
               p_major: float) -> np.ndarray:
    """Build fixed per-seed pairwise composition kernel comp_dist[a,b,:] (distribution over results).

    A fraction `ambiguity_rate` of ordered pairs (a,b) map to a MIXTURE: mode gets p_major, 1-2
    alternates share the rest (irreducible relational ambiguity -> honest sub-1.0 ceiling). The rest
    are deterministic (delta on a pseudo-random mode). Closed on the m relations.
    Shape [m, m, m]; comp_dist[a,b,c] = P(result=c | left-composed=a, next-base=b).
    """
    comp = np.zeros((m, m, m), dtype=np.float64)
    # Deterministic primary result for each pair (a random but fixed function of (a,b)).
    primary = rng.integers(0, m, size=(m, m))
    ambig_mask = rng.random((m, m)) < ambiguity_rate
    for a in range(m):
        for b in range(m):
            c0 = int(primary[a, b])
            if not ambig_mask[a, b]:
                comp[a, b, c0] = 1.0
            else:
                # 1 or 2 distinct alternates (not equal to c0)
                n_alt = int(rng.integers(1, 3))  # 1 or 2
                alts = []
                pool = [c for c in range(m) if c != c0]
                rng.shuffle(pool)
                alts = pool[:n_alt]
                comp[a, b, c0] = p_major
                rest = (1.0 - p_major)
                # split remaining mass across alternates (major-then-minor)
                if n_alt == 1:
                    comp[a, b, alts[0]] = rest
                else:
                    comp[a, b, alts[0]] = rest * 0.6
                    comp[a, b, alts[1]] = rest * 0.4
            # numerical safety
            s = comp[a, b].sum()
            comp[a, b] /= s
    return comp


def _scramble_answer(chain: np.ndarray, m: int, seed: int) -> int:
    """Non-compositional deterministic answer for the SCRAMBLE control.

    Answer is a deterministic function of the WHOLE sequence (hashlib, NOT builtin hash), so there is
    NO learnable pairwise/foldable rule -> short-chain training cannot transfer to unseen long chains.
    Uses hashlib (deterministic across processes; never flagged by the nondeterminism source scan).
    """
    key = f"{seed}|" + ",".join(str(int(x)) for x in chain)
    h = hashlib.sha256(key.encode("ascii")).digest()
    return int.from_bytes(h[:8], "big") % m


def gen_chains(rng: np.random.Generator, m: int, length: int, n: int) -> np.ndarray:
    """n iid base-relation chains of the given length. Shape [n, length]."""
    return rng.integers(0, m, size=(n, length)).astype(np.int64)


def gen_answers_clean(comp: np.ndarray, chains: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Generative left-fold answers (sample each hop from comp_dist). Shape [n]."""
    m = comp.shape[0]
    n, k = chains.shape
    ans = np.empty(n, dtype=np.int64)
    for i in range(n):
        state = int(chains[i, 0])
        for h in range(1, k):
            b = int(chains[i, h])
            p = comp[state, b]
            state = int(rng.choice(m, p=p))
        ans[i] = state
    return ans


def gen_answers_scramble(chains: np.ndarray, m: int, seed: int) -> np.ndarray:
    """Non-compositional per-sequence answers for the scramble control."""
    n = chains.shape[0]
    return np.array([_scramble_answer(chains[i], m, seed) for i in range(n)], dtype=np.int64)


def oracle_marginal_pred(comp: np.ndarray, chains: np.ndarray) -> np.ndarray:
    """Bayes oracle: exact marginal left-fold of the true kernel; argmax. Shape [n]."""
    m = comp.shape[0]
    n, k = chains.shape
    preds = np.empty(n, dtype=np.int64)
    for i in range(n):
        p = np.zeros(m)
        p[int(chains[i, 0])] = 1.0
        for h in range(1, k):
            b = int(chains[i, h])
            # new_p[c] = sum_a p[a] * comp[a, b, c]
            p = p @ comp[:, b, :]
        preds[i] = int(np.argmax(p))
    return preds


# --------------------------------------------------------------------------------------------
# FHRR codes + primitives (complex unit phasors)
# --------------------------------------------------------------------------------------------
def make_codes(rng: np.random.Generator, m: int, N: int) -> np.ndarray:
    """m relation codes as unit-magnitude complex phasors. Shape [m, N] complex128."""
    theta = rng.uniform(-np.pi, np.pi, size=(m, N))
    return np.exp(1j * theta)


def make_perm_powers(rng: np.random.Generator, N: int, max_pos: int) -> np.ndarray:
    """MONOTONIC/ordered position codes as PERMUTATION POWERS P^p (standard VSA ordinal transform).

    perm = a fixed random permutation of [0,N); perm_pows[p] = perm applied p times (index array).
    Order is carried by a positional re-indexing of the CONTENT code (representation), the combine
    step stays a COMMUTATIVE FHRR bind -- no non-commutative binding operator. Permutation-powers are
    the canonical VSA ordinal/position family (Plate/Kanerva; analog of grid-cell phase advance) and,
    unlike a multiplicative phasor tag (which factors out of a commutative product and symmetrizes),
    they make bind(P^1 a, P^2 b) order-sensitive AND keep distinct pair-keys quasi-orthogonal (low
    crosstalk in the heteroassociative memory). Returns int index array [max_pos+1, N].
    """
    perm = rng.permutation(N)
    pows = np.empty((max_pos + 1, N), dtype=np.int64)
    pows[0] = np.arange(N)
    for p in range(1, max_pos + 1):
        pows[p] = pows[p - 1][perm]
    return pows


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FHRR bind = elementwise complex multiply (commutative)."""
    return a * b


def cleanup(est: np.ndarray, codes: np.ndarray) -> np.ndarray:
    """Nearest relation code by real part of complex inner product. est [nt,N], codes [m,N] -> [nt]."""
    scores = np.real(est @ np.conj(codes).T)  # [nt, m]
    return np.argmax(scores, axis=1)


# --------------------------------------------------------------------------------------------
# ARM_A: iterative composition memory (learned from length-2 pairs) + fold
# --------------------------------------------------------------------------------------------
def _pair_key(left: np.ndarray, right: np.ndarray, perm1: np.ndarray, perm2: np.ndarray) -> np.ndarray:
    """Order-sensitive pair key = bind(P^1(left), P^2(right)) (commutative bind of permuted codes).

    left,right [n,N] complex; perm1,perm2 index arrays [N]. Returns [n,N].
    """
    return left[:, perm1] * right[:, perm2]


def train_comp_memory(pairs: np.ndarray, ans: np.ndarray, codes: np.ndarray,
                      perm1: np.ndarray, perm2: np.ndarray) -> np.ndarray:
    """W = sum_i outer(code[ans_i], key_i); key = bind(P^1 code[a], P^2 code[b]). [N,N] complex.

    pairs [n,2] = (a,b) length-2 chains; ans [n] observed answers. Vectorized: W = U.T @ conj(K).
    """
    K = _pair_key(codes[pairs[:, 0]], codes[pairs[:, 1]], perm1, perm2)  # [n, N]
    U = codes[ans]  # [n, N]
    return U.T @ np.conj(K)  # [N, N]


def arm_a_predict(W: np.ndarray, chains: np.ndarray, codes: np.ndarray,
                  perm1: np.ndarray, perm2: np.ndarray) -> np.ndarray:
    """Iterative fold with inter-hop cleanup (batched across chains). Returns predicted answer idx [n]."""
    n, k = chains.shape
    running = codes[chains[:, 0]].copy()  # [n, N] clean code for r1
    for h in range(1, k):
        nxt = codes[chains[:, h]]  # [n, N]
        key = _pair_key(running, nxt, perm1, perm2)  # [n, N]
        est = key @ W.T  # [n, N]  (W @ key per row)
        idx = cleanup(est, codes)  # [n]
        running = codes[idx]  # sharded: snap to clean relation code
    return cleanup(running, codes)


# --------------------------------------------------------------------------------------------
# ARM_B: flat single-bundle readout (param-matched; cannot chain)
# --------------------------------------------------------------------------------------------
def chain_bundle(chains: np.ndarray, codes: np.ndarray, perm_pows: np.ndarray) -> np.ndarray:
    """Single bundle sum_i P^i(code[r_i]) (positions 1..k; same ordered family). Shape [n, N] complex."""
    n, k = chains.shape
    N = codes.shape[1]
    acc = np.zeros((n, N), dtype=np.complex128)
    for h in range(k):
        acc += codes[chains[:, h]][:, perm_pows[h + 1]]  # position index 1..k
    return acc


def train_flat_readout(chains_list, ans_list, codes: np.ndarray, perm_pows: np.ndarray) -> np.ndarray:
    """U = sum outer(code[ans], chain_bundle) over all training chains (lengths 2,3,4). [N,N] complex."""
    N = codes.shape[1]
    W_accum = np.zeros((N, N), dtype=np.complex128)
    for chains, ans in zip(chains_list, ans_list):
        B = chain_bundle(chains, codes, perm_pows)  # [n, N]
        U = codes[ans]  # [n, N]
        W_accum += U.T @ np.conj(B)
    return W_accum


def arm_b_predict(U: np.ndarray, chains: np.ndarray, codes: np.ndarray,
                  perm_pows: np.ndarray) -> np.ndarray:
    """Flat readout: one bundle, one cleanup. Returns predicted answer idx [n]."""
    B = chain_bundle(chains, codes, perm_pows)  # [n, N]
    est = B @ U.T  # [n, N]
    return cleanup(est, codes)


# --------------------------------------------------------------------------------------------
# One-seed run
# --------------------------------------------------------------------------------------------
def run_seed(seed: int, N: int, m: int, ambiguity_rate: float, p_major: float,
             train_lengths, n_train_per_len: int, test_lengths, n_test_per_len: int):
    """Run both arms + oracle on clean AND scramble conditions for one seed. Returns dict."""
    rng = np.random.default_rng(seed)
    comp = make_world(rng, m, ambiguity_rate, p_major)
    max_pos = max(max(train_lengths), max(test_lengths))
    codes = make_codes(rng, m, N)
    perm_pows = make_perm_powers(rng, N, max_pos)
    perm1 = perm_pows[1]
    perm2 = perm_pows[2]

    chance = 1.0 / m

    # --- training data (identical set handed to both arms) ---
    train_chains = {}
    train_ans_clean = {}
    train_ans_scram = {}
    for L in train_lengths:
        ch = gen_chains(rng, m, L, n_train_per_len)
        train_chains[L] = ch
        train_ans_clean[L] = gen_answers_clean(comp, ch, rng)
        train_ans_scram[L] = gen_answers_scramble(ch, m, seed)

    # --- ARM_A memory: from length-2 pairs only (clean and scramble variants) ---
    pairs = train_chains[2]
    W_clean = train_comp_memory(pairs, train_ans_clean[2], codes, perm1, perm2)
    W_scram = train_comp_memory(pairs, train_ans_scram[2], codes, perm1, perm2)

    # --- ARM_B flat readout: from all training lengths ---
    chains_list = [train_chains[L] for L in train_lengths]
    U_clean = train_flat_readout(chains_list, [train_ans_clean[L] for L in train_lengths], codes, perm_pows)
    U_scram = train_flat_readout(chains_list, [train_ans_scram[L] for L in train_lengths], codes, perm_pows)

    # --- evaluation over test lengths ---
    curve = {"clean": {}, "scramble": {}}
    first_pred_hash = {"arm_a": None, "arm_b": None}  # for arms-differ (at first test length)
    for L in test_lengths:
        ch = gen_chains(rng, m, L, n_test_per_len)
        ans_clean = gen_answers_clean(comp, ch, rng)
        ans_scram = gen_answers_scramble(ch, m, seed)

        # clean
        pa = arm_a_predict(W_clean, ch, codes, perm1, perm2)
        pb = arm_b_predict(U_clean, ch, codes, perm_pows)
        po = oracle_marginal_pred(comp, ch)
        acc_a = float(np.mean(pa == ans_clean))
        acc_b = float(np.mean(pb == ans_clean))
        acc_o = float(np.mean(po == ans_clean))
        # majority-class rate for clean answers at this length
        vals, cnts = np.unique(ans_clean, return_counts=True)
        maj = float(cnts.max() / cnts.sum())
        curve["clean"][L] = {"arm_a": acc_a, "arm_b": acc_b, "oracle": acc_o,
                             "majority_class": maj, "chance": chance}

        # scramble
        pas = arm_a_predict(W_scram, ch, codes, perm1, perm2)
        pbs = arm_b_predict(U_scram, ch, codes, perm_pows)
        acc_as = float(np.mean(pas == ans_scram))
        acc_bs = float(np.mean(pbs == ans_scram))
        vals_s, cnts_s = np.unique(ans_scram, return_counts=True)
        maj_s = float(cnts_s.max() / cnts_s.sum())
        curve["scramble"][L] = {"arm_a": acc_as, "arm_b": acc_bs,
                                "majority_class": maj_s, "chance": chance}

        if first_pred_hash["arm_a"] is None:
            first_pred_hash["arm_a"] = hashlib.sha256(pa.tobytes()).hexdigest()
            first_pred_hash["arm_b"] = hashlib.sha256(pb.tobytes()).hexdigest()

    return {"seed": seed, "chance": chance, "curve": curve,
            "arms_differ_hashes": first_pred_hash}


# --------------------------------------------------------------------------------------------
# Aggregation + verdict
# --------------------------------------------------------------------------------------------
def _mean_over(curve_cond, lengths, arm):
    vals = [curve_cond[L][arm] for L in lengths if L in curve_cond]
    return float(np.mean(vals)) if vals else float("nan")


def aggregate(per_seed, test_lengths):
    """Average curves across seeds; compute discriminators + bands."""
    seeds = [s["seed"] for s in per_seed]
    chance = per_seed[0]["chance"]

    # mean curve per condition/length/arm
    def mean_curve(cond):
        out = {}
        for L in test_lengths:
            arms = ["arm_a", "arm_b"] + (["oracle"] if cond == "clean" else [])
            row = {}
            for arm in arms:
                row[arm] = float(np.mean([s["curve"][cond][L][arm] for s in per_seed]))
            row["majority_class"] = float(np.mean([s["curve"][cond][L]["majority_class"] for s in per_seed]))
            row["chance"] = chance
            out[L] = row
        return out

    mc_clean = mean_curve("clean")
    mc_scram = mean_curve("scramble")

    long_lengths = [L for L in test_lengths if L >= 6]
    short_lengths = [L for L in test_lengths if L <= 4]
    max_len = max(test_lengths)

    long_gap_clean = _mean_over(mc_clean, long_lengths, "arm_a") - _mean_over(mc_clean, long_lengths, "arm_b")
    long_gap_scram = _mean_over(mc_scram, long_lengths, "arm_a") - _mean_over(mc_scram, long_lengths, "arm_b")

    arm_a_short = _mean_over(mc_clean, short_lengths, "arm_a")
    oracle_short = _mean_over(mc_clean, short_lengths, "oracle")
    arm_a_long = _mean_over(mc_clean, long_lengths, "arm_a")

    oracle_len2 = mc_clean[min(test_lengths)]["oracle"]
    oracle_lenmax = mc_clean[max_len]["oracle"]
    arm_b_lenmax = mc_clean[max_len]["arm_b"]
    majority_lenmax = mc_clean[max_len]["majority_class"]
    arm_a_len2 = mc_clean[min(test_lengths)]["arm_a"]

    # --- bands ---
    H1 = long_gap_clean >= 0.20
    H2 = arm_b_lenmax <= max(chance, majority_lenmax) + 0.10
    H3 = (arm_a_short >= 0.60 * oracle_short) and (arm_a_short >= 3 * chance)
    G1 = oracle_lenmax < 0.90
    G2 = (oracle_len2 - oracle_lenmax) >= 0.10
    G3 = oracle_lenmax > 2 * chance
    C1 = long_gap_scram <= 0.08
    P1 = abs(arm_a_len2 - oracle_len2) <= 0.12
    baseline_in_band = (0.10 < arm_a_long < 0.90) and (oracle_lenmax < 0.90)

    guard_ok = G1 and G2 and G3
    control_ok = C1

    if not guard_ok:
        verdict = "GUARD_FAIL_CONSTRUCTION_DETERMINED"
    elif not control_ok:
        verdict = "HARD_FAIL_SCRAMBLE_LEAK"
    elif long_gap_clean <= 0.05:
        verdict = "HARD_FAIL_NO_COMPOSITIONAL_BENEFIT"
    elif H1 and H2 and H3 and baseline_in_band:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    return {
        "verdict": verdict,
        "seeds": seeds,
        "chance": chance,
        "mean_curve_clean": mc_clean,
        "mean_curve_scramble": mc_scram,
        "long_gap_clean": long_gap_clean,
        "long_gap_scramble": long_gap_scram,
        "arm_a_short": arm_a_short,
        "oracle_short": oracle_short,
        "arm_a_long": arm_a_long,
        "oracle_len2": oracle_len2,
        "oracle_lenmax": oracle_lenmax,
        "arm_b_lenmax": arm_b_lenmax,
        "majority_lenmax": majority_lenmax,
        "arm_a_len2": arm_a_len2,
        "bands": {"H1": bool(H1), "H2": bool(H2), "H3": bool(H3),
                  "G1": bool(G1), "G2": bool(G2), "G3": bool(G3),
                  "C1": bool(C1), "P1": bool(P1),
                  "baseline_in_band": bool(baseline_in_band)},
        "guard_ok": bool(guard_ok), "control_ok": bool(control_ok),
    }


# --------------------------------------------------------------------------------------------
# Config profiles
# --------------------------------------------------------------------------------------------
def cfg_selftest():
    return dict(N=256, m=6, ambiguity_rate=0.35, p_major=0.60,
                train_lengths=[2, 3, 4], n_train_per_len=400,
                test_lengths=[2, 3, 4, 5, 6, 7, 8], n_test_per_len=120, seeds=[7])


def cfg_smoke():
    return dict(N=512, m=10, ambiguity_rate=0.35, p_major=0.60,
                train_lengths=[2, 3, 4], n_train_per_len=1500,
                test_lengths=[2, 3, 4, 5, 6, 7, 8, 9, 10], n_test_per_len=300, seeds=[7])


def cfg_full():
    return dict(N=1024, m=18, ambiguity_rate=0.35, p_major=0.60,
                train_lengths=[2, 3, 4], n_train_per_len=4000,
                test_lengths=[2, 3, 4, 5, 6, 7, 8, 9, 10], n_test_per_len=600, seeds=[7, 13, 19])


# --------------------------------------------------------------------------------------------
# Runners
# --------------------------------------------------------------------------------------------
def _write_start_marker(output_dir, mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode,
              "expected_n_units": expected_n_units}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def run_mode(mode: str):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = get_output_dir(ANCHOR_NAME)  # Path (write_metrics helper requires Path)

    expected_n_units = len(cfg["seeds"]) * 2 * len(cfg["test_lengths"])  # seeds*conditions*lengths
    _write_start_marker(output_dir, mode, expected_n_units)

    per_seed = []
    per_unit_count = 0
    failures = []
    for seed in cfg["seeds"]:
        try:
            r = run_seed(seed, cfg["N"], cfg["m"], cfg["ambiguity_rate"], cfg["p_major"],
                         cfg["train_lengths"], cfg["n_train_per_len"],
                         cfg["test_lengths"], cfg["n_test_per_len"])
            per_seed.append(r)
            per_unit_count += 2 * len(cfg["test_lengths"])  # clean+scramble per length
            print(f"[{ANCHOR_NAME}:{mode}] seed={seed} done", flush=True)
        except Exception as e:  # per-seed failure-class capture (no bare except)
            failures.append({"seed": seed, "failure_class": type(e).__name__,
                             "msg": str(e)[:300]})
            print(f"[{ANCHOR_NAME}:{mode}] seed={seed} FAILED {type(e).__name__}: {e}", flush=True)

    if not per_seed:
        agg = {"verdict": "CELL_CRASHED", "note": "all seeds failed", "failures": failures}
        _finish(output_dir, mode, agg, cfg, t0, per_unit_count, expected_n_units, failures, None)
        return agg

    agg = aggregate(per_seed, cfg["test_lengths"])

    # cardinality gate (META_RULE_H)
    cardinality_ok = (per_unit_count == expected_n_units)
    if not cardinality_ok:
        agg["verdict"] = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"

    # arms-differ (META_RULE_AF)
    h = per_seed[0]["arms_differ_hashes"]
    arms_differ_verified = (h["arm_a"] != h["arm_b"])
    if not arms_differ_verified:
        agg["verdict"] = "HARD_FAIL_ARMS_BIT_IDENTICAL_META_RULE_AF"

    # discriminator-fires gate (smoke only): long gap must appear + ARM_B collapse + oracle in band
    discriminator_fired = True
    if mode == "smoke":
        max_len = max(cfg["test_lengths"])
        arm_b_maxlen = agg["mean_curve_clean"][max_len]["arm_b"]
        fired = (agg["long_gap_clean"] >= 0.15 and arm_b_maxlen <= 0.35
                 and (2 * agg["chance"]) < agg["oracle_lenmax"] < 0.90)
        discriminator_fired = bool(fired)
        if not discriminator_fired:
            agg["verdict"] = "SMOKE_DISCRIMINATOR_DID_NOT_FIRE"

    _finish(output_dir, mode, agg, cfg, t0, per_unit_count, expected_n_units, failures,
            {"arms_differ_verified": arms_differ_verified, "cardinality_ok": cardinality_ok,
             "discriminator_fired": discriminator_fired})
    return agg


def _finish(output_dir, mode, agg, cfg, t0, per_unit_count, expected_n_units, failures, gate_flags):
    elapsed = time.perf_counter() - t0
    v = agg.get("verdict", "UNKNOWN")
    lg = agg.get("long_gap_clean", float("nan"))
    lgs = agg.get("long_gap_scramble", float("nan"))
    orl = agg.get("oracle_lenmax", float("nan"))
    or2 = agg.get("oracle_len2", float("nan"))
    abl = agg.get("arm_b_lenmax", float("nan"))
    aas = agg.get("arm_a_short", float("nan"))
    msg = (f"{v} | long_gap_clean={lg:.3f} long_gap_scram={lgs:.3f} "
           f"| oracle len2={or2:.3f}->lenmax={orl:.3f} (GUARD<0.90) "
           f"| ARM_B lenmax={abl:.3f} ARM_A_short={aas:.3f} chance={agg.get('chance', float('nan')):.3f} "
           f"| bands={agg.get('bands', {})}")

    gate_claims = None
    if "long_gap_clean" in agg:
        gate_claims = [
            record_gate("H1_long_gap_clean", agg["long_gap_clean"], 0.20, ">=",
                        "ARM_A beats flat on long chains (k>=6)"),
            record_gate("H2_arm_b_collapse", agg["arm_b_lenmax"],
                        max(agg["chance"], agg["majority_lenmax"]) + 0.10, "<=",
                        "flat collapses at max length (must-fail 1)"),
            record_gate("G1_oracle_not_free", agg["oracle_lenmax"], 0.90, "<",
                        "handed rules do NOT solve length-max for free (construction-determined guard)"),
            record_gate("G2_oracle_decays", agg["oracle_len2"] - agg["oracle_lenmax"], 0.10, ">=",
                        "ceiling degrades with length"),
            record_gate("G3_oracle_above_chance", agg["oracle_lenmax"], 2 * agg["chance"], ">",
                        "task non-degenerate"),
            record_gate("C1_scramble_gap_collapse", agg["long_gap_scramble"], 0.08, "<=",
                        "ARM_A advantage vanishes without learnable rule (must-fail 2)"),
        ]

    payload = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": mode,
        "verdict": v,
        "verdict_msg": msg,
        "summary": msg,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {k: (list(x) if isinstance(x, (list, tuple)) else x) for k, x in cfg.items()},
        "aggregate": agg,
        "per_unit_count": per_unit_count,
        "expected_n_units": expected_n_units,
        "failures": failures,
        "gate_flags": gate_flags,
        "arms_differ_verified": (gate_flags or {}).get("arms_differ_verified", None),
        "cardinality_ok": (gate_flags or {}).get("cardinality_ok", None),
        "final_metrics_atomicity": "tmp_replace",
        "needs_orchestrator_store_sync": True,
        "notes": ("Reoriented chain-grade (post atom 29363): LENGTH-GENERALIZATION on CLUTRR-style "
                  "kinship, ceiling < 1.000, construction-determined GUARD = oracle_lenmax<0.90. "
                  "ONE variable = iterative fold+cleanup (ARM_A) vs flat single-bundle readout (ARM_B); "
                  "param-matched [N,N] complex memories; same codes/ordered-position family/data. "
                  "LOCAL-ONLY. Route to skunkworks landed-VET (adversarial on the GUARD hardest). "
                  "CLAIM-VET-pending."),
    }
    _write_metrics_helper(output_dir, payload, gate_claims=gate_claims)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    if "mean_curve_clean" in agg:
        for L in cfg["test_lengths"]:
            c = agg["mean_curve_clean"][L]
            s = agg["mean_curve_scramble"][L]
            print(f"  k={L:>2} | CLEAN A={c['arm_a']:.3f} B={c['arm_b']:.3f} "
                  f"O={c['oracle']:.3f} maj={c['majority_class']:.3f} "
                  f"| SCRAM A={s['arm_a']:.3f} B={s['arm_b']:.3f}", flush=True)


def self_test():
    """Fast end-to-end pipeline + guard-direction + deterministic-seeding witness (< ~5s)."""
    # deterministic-seeding source scan (F.5): assert this file has no hash()-seeded RNG / list(set())
    try:
        from _validity_preflight import assert_no_nondeterministic_seeding
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
            src = f.read()
        assert_no_nondeterministic_seeding(src, mode="warn")
        print(f"[{ANCHOR_NAME}] self-test: deterministic-seeding scan OK", flush=True)
    except Exception as e:
        print(f"[{ANCHOR_NAME}] self-test: nondeterminism scan note: {type(e).__name__}: {e}", flush=True)

    cfg = cfg_selftest()
    per_seed = [run_seed(cfg["seeds"][0], cfg["N"], cfg["m"], cfg["ambiguity_rate"], cfg["p_major"],
                         cfg["train_lengths"], cfg["n_train_per_len"],
                         cfg["test_lengths"], cfg["n_test_per_len"])]
    agg = aggregate(per_seed, cfg["test_lengths"])
    h = per_seed[0]["arms_differ_hashes"]
    arms_differ = (h["arm_a"] != h["arm_b"])

    print(f"[{ANCHOR_NAME}] self-test: verdict={agg['verdict']} "
          f"long_gap_clean={agg['long_gap_clean']:.3f} long_gap_scram={agg['long_gap_scramble']:.3f} "
          f"oracle len2={agg['oracle_len2']:.3f}->lenmax={agg['oracle_lenmax']:.3f} "
          f"ARM_B_lenmax={agg['arm_b_lenmax']:.3f} ARM_A_short={agg['arm_a_short']:.3f} "
          f"chance={agg['chance']:.3f} arms_differ={arms_differ}", flush=True)
    for L in cfg["test_lengths"]:
        c = agg["mean_curve_clean"][L]
        print(f"  k={L:>2} CLEAN A={c['arm_a']:.3f} B={c['arm_b']:.3f} O={c['oracle']:.3f} "
              f"| SCRAM A={agg['mean_curve_scramble'][L]['arm_a']:.3f} "
              f"B={agg['mean_curve_scramble'][L]['arm_b']:.3f}", flush=True)
    # scaffold-free witnesses (assertions the pipeline is sane, NOT pass/fail of the science claim):
    assert arms_differ, "self-test: ARM_A and ARM_B produced bit-identical predictions"
    assert 0.0 <= agg["oracle_len2"] <= 1.0, "oracle out of [0,1]"
    print(f"[{ANCHOR_NAME}] self-test: OK (witnesses pass; science verdict is informational)", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    if args.smoke:
        run_mode("smoke")
        return
    if args.full:
        run_mode("full")
        return
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
            "anchor_name": ANCHOR_NAME,
            "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}",
            "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        try:
            _write_metrics_helper(get_output_dir(ANCHOR_NAME + "_crash"), diag)
        except Exception:
            pass
        raise
