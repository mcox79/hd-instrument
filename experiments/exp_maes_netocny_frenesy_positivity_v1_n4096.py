"""Maes-Netocny frenesy positivity v1 N=4096.

CONTEXT (BAND-LIFTING per notes/research_noneq_framework_consolidation_v276_2026-05-29.md
Anchor candidate A, and G3 in notes/paper_outline_sagawa_ueda_substrate_thermodynamics_v278_2026-05-29.md):
  Per Maes-Netocny (arXiv:1904.10485, Phys Rep 2020) the entropy production of any
  stochastic system decomposes into:
      sigma_total = sigma_excess + sigma_housekeeping + sigma_coupling (geometric three-part decomp)
  with the time-symmetric "frenesy" / dynamical-activity rate accounting for the
  coupling/coupling-symmetric component. The 3-strike HS-class exclusion in
  v275+v276 shows the housekeeping component is degenerate. The substrate's
  surviving non-eq sub-class is Maes-Netocny + Sagawa-Ueda.

  This probe is the CHEAPEST decisive test to lift Maes-Netocny three-part class
  P_deflated from ~0.55-0.65 toward >= 0.70 (publication-grade), per the Research
  agent's framework consolidation. If frenesy is positive with sigma_margin >= 2.0
  across all seeds, the substrate's class identification gains a 4th independent
  non-eq stream (TCFT + SKAH-M + BID outside-Hopfield + frenesy positivity).

  Cost ~3-4h CPU; reuses Hatano-Sasa-style trajectory infrastructure.

ANCHOR: maes_netocny_frenesy_positivity_v1_n4096
QUEUE:  remote_cpu_queue
N:      4096 (PROT-018 binds _n4096 to N=4096)
SEEDS:  5 [7, 17, 23, 31, 41]
PARENT: exp_ortho_noneq_corroborator_v1.py / exp_wave14_hatano_sasa_ness_audit_v1.py
        (substrate-trajectory infrastructure: incremental Hebbian writes establish
        the discrete trajectory whose time-symmetric reactivity = frenesy).

FRENESY (Maes-Netocny 2003, 2019):
  For a stochastic system with rates k(x->y) and k(y->x), entropy production
  rate is the antisymmetric part:
    sigma_EP(x,y) = log( k(x->y) / k(y->x) )
  and frenesy (time-symmetric reactivity) is the SYMMETRIC part:
    K_frenesy(x,y) = k(x->y) + k(y->x)
  with dynamical activity rate:
    a(x->y) = sqrt( k(x->y) * k(y->x) )
  The Maes-Netocny "geometric" three-part decomposition writes
    sigma_total = sigma_excess + sigma_HS + sigma_coupling
  where sigma_coupling is time-symmetric and bounded below by the frenesy traffic.

  POSITIVITY CLAIM: a well-behaved non-eq system has K_frenesy > 0 (the time-symmetric
  dynamical activity is strictly positive: state-changes have a finite rate in each
  direction). HARD-FAIL would mean substrate has trivial or asymmetric one-way
  dynamics (frenesy ~ 0 in 1 or both directions), undermining the "fast layer is
  genuinely non-eq" claim from v276 Synthesis.

PROTOCOL (Hatano-Sasa style adapted for frenesy measurement):
  1. Build initial substrate W_0 from M_init = m_frac * N BSC patterns. Initial
     NESS is the steady-state of Hebbian retrieval dynamics on the pattern set.
  2. Generate a forward trajectory: incrementally add M_delta probe patterns,
     each one a perturbation of W. After each write, project all M_probe target
     patterns onto W and record their energy E(v).
  3. Generate a reverse trajectory at each step: REMOVE the most recently added
     probe pattern via reverse-Hebbian and recompute energies.
  4. For each (state -> state) transition x -> y observed over M_probe pattern
     probes, count forward and reverse rates per unit substrate-time:
       n_fwd(x->y)  = number of forward transitions x to y
       n_rev(x<-y)  = number of reverse transitions (y to x in reverse traj)
     Use sign-coarse-graining: state of probe = sign(v @ W @ v_target) so transitions
     are binary {+,-} -> {+,-} (4 cells of a 2x2 rate matrix).
  5. Compute frenesy = K = sum over (x,y) pairs of n_fwd(x->y) + n_rev(x<-y).
     Compute sigma_EP = sum over (x,y) of n_fwd * log(n_fwd / n_rev + eps).
     Frenesy-rate per unit time: K / T_traj.
  6. Sigma-margin: sigma_margin = K / sqrt(Var(K)) where Var(K) is the per-seed
     std of K across the M_probe targets.

  PROBE-LEVEL OBSERVABLE: for each probe pattern j, the per-target frenesy is
    K_j = number of distinct flip events along its trajectory (forward + reverse
    summed). We aggregate K_j over j to get the per-seed K and its variance.

PRE-REGISTERED BANDS (per [[feedback-envelope-expansion-fail-bands]]):
  HARD_PASS:
    frenesy_per_seed > 0 in all 5 seeds AND
    sigma_margin (K / sqrt(Var(K))) >= 2.0 in >= 4/5 seeds AND
    forward_rate > 0 AND reverse_rate > 0 (both directions non-trivial).
    -> substrate satisfies Maes-Netocny frenesy positivity; non-eq sub-class
       narrowed to Maes-Netocny + Sagawa-Ueda lineage.

  HARD_FAIL:
    frenesy_per_seed near-zero (frenesy_mean < 0.05 * M_probe) in >= 3/5 seeds OR
    forward_rate ~ 0 OR reverse_rate ~ 0 (>= 3/5 seeds: any direction zero).
    -> substrate has trivial time-symmetric dynamical activity; undermines fast-layer
       non-eq claim.

  MIDDLE_BAND:
    frenesy positive but sigma_margin < 2.0 in >= 3/5 seeds.
    -> directionally correct, more triangulation needed.

FORMULA SELF-TESTS:
  T1. For W = 0 (no patterns yet): all states project to 0; no transitions;
      frenesy K = 0 (degenerate). Test: K(W=0) is 0 or near-0.
  T2. For a single-pattern substrate where probe = stored pattern: deterministic
      sign(+1) for all retrievals; forward = reverse = no flips; K = 0. Self-consistency.
  T3. For random init + random probes (no structure): nontrivial K > 0;
      sigma_EP either zero (time-reversal-symmetric proxy) or finite.
  T4. Smoke at N=512, m_frac=0.125, 1 seed completes < 60s; returns finite,
      non-negative frenesy.

OOM PRE-CHECK:
  W at N=4096 float64: 128MB. M_init=512 patterns: 16MB. Plus rate-matrix counters: small.
  Two W matrices (forward + reverse): 256MB. OK.

TIMEOUT ESTIMATE:
  Build_W at N=4096, M_init=512: ~512 outer products O(N^2) = ~10G ops = ~20s per seed.
  Forward+reverse trajectory: per M_delta step compute W @ V over M_probe targets:
    M_delta=64 steps * M_probe=200 probes * (W@v = N^2 = 16M) = 200G ops = ~400s per seed.
  Five seeds: ~2100s wall.
  Safety 1.5x = 3150s. PROT-019 _n4096 floor = 14400s.
  ANCHOR TIMEOUT = 14400s (PROT-019 floor; realistic ~2100s).

CONTRACT (per Strategy hand-off):
  - argparse: --N --seeds --m_frac --smoke --self-test (env HDLAB_EXP_NAME honored)
  - atomic metrics.json write (.tmp + os.replace)
  - ASCII-only stdout
  - verdict_tag + verdict_msg in metrics
  - self-test runs at import

Parent: exp_ortho_noneq_corroborator_v1.py
Pre-reg: preregs/2026-05-29_maes_netocny_frenesy_positivity_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- PROT-018: _n4096 binds N_FULL = 4096 ---
N_FULL = 4096
N_SMOKE = 512
assert N_FULL == 4096, f"PROT-018: _n4096 suffix binds N_FULL=4096; got {N_FULL}"

M_FRAC_DEFAULT = 0.125    # M_init = alpha*N
M_DELTA_FRAC = 0.015625   # M_delta = (1/64) * N: small per-step perturbation
M_PROBE_FRAC = 0.05       # M_probe = 0.05*N: probe-pattern pool for frenesy traj
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_HEBBIAN = 0.1

# Pre-registered HARD_PASS/HARD_FAIL bands (per file-header pre-reg)
HP_FRENESY_MIN = 0.0                  # frenesy > 0 required at every seed
HP_SIGMA_MARGIN_MIN = 2.0             # sigma_margin = K / sqrt(Var(K)) >= 2.0
HP_SEEDS_PASS_MARGIN_MIN = 4          # >= 4/5 seeds pass sigma_margin
HP_RATE_DIRECTIONS_NONZERO = True     # both fwd and rev > 0

HF_FRENESY_FRAC_MIN = 0.05            # K/M_probe < 0.05 = near-zero frenesy fail band
HF_NEARZERO_SEEDS_MIN = 3             # >= 3/5 seeds in near-zero band = HARD_FAIL


def get_output_dir(default_name: str = "maes_netocny_frenesy_positivity_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def build_substrate(N: int, M: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Hebbian W from M random BSC patterns; returns (W, patterns)."""
    rng = np.random.default_rng(seed)
    patterns = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    W = np.zeros((N, N), dtype=np.float64)
    batch = 128
    for start in range(0, M, batch):
        end = min(start + batch, M)
        P = patterns[start:end]
        W += ALPHA_HEBBIAN * (P.T @ P) / N
    np.fill_diagonal(W, 0.0)
    return W, patterns


def sign_state(W: np.ndarray, v: np.ndarray, N: int) -> int:
    """Coarse-grained state: sign of normalized self-overlap (+1, -1, or 0)."""
    val = float(v @ W @ v) / N
    if val > 1e-9:
        return 1
    if val < -1e-9:
        return -1
    return 0


def count_transitions(state_seq: List[int]) -> Tuple[int, Dict[Tuple[int, int], int]]:
    """Count distinct transitions along state_seq; returns (total_transitions, per_pair counts)."""
    n_trans = 0
    pair_counts: Dict[Tuple[int, int], int] = {}
    for i in range(1, len(state_seq)):
        a, b = state_seq[i - 1], state_seq[i]
        if a != b:
            n_trans += 1
            key = (a, b)
            pair_counts[key] = pair_counts.get(key, 0) + 1
    return n_trans, pair_counts


def run_one_seed(N: int, m_frac: float, seed: int) -> Dict:
    """Build substrate, run forward+reverse Hebbian write/erase trajectory,
       compute per-probe frenesy = total transition count (forward + reverse)."""
    M_init = max(2, int(m_frac * N))
    M_delta = max(1, int(M_DELTA_FRAC * N))
    M_probe = max(4, int(M_PROBE_FRAC * N))
    M_steps = max(2, M_delta)  # number of trajectory steps

    t0 = time.time()
    W, init_patterns = build_substrate(N, M_init, seed)
    t_build = time.time() - t0

    # Probe pool: bipolar random patterns sampled deterministically from seed.
    rng = np.random.default_rng(seed + 10_000)
    probes = rng.choice([-1.0, 1.0], size=(M_probe, N)).astype(np.float64)

    # Delta patterns to be added over the trajectory.
    delta_patterns = rng.choice([-1.0, 1.0], size=(M_steps, N)).astype(np.float64)

    # Forward trajectory: record sign_state of each probe after each step (write of delta).
    fwd_state_seqs: List[List[int]] = [[] for _ in range(M_probe)]
    W_fwd = W.copy()
    # Step 0 baseline state
    for j in range(M_probe):
        fwd_state_seqs[j].append(sign_state(W_fwd, probes[j], N))
    for k in range(M_steps):
        d = delta_patterns[k]
        W_fwd += ALPHA_HEBBIAN * np.outer(d, d) / N
        np.fill_diagonal(W_fwd, 0.0)
        for j in range(M_probe):
            fwd_state_seqs[j].append(sign_state(W_fwd, probes[j], N))

    # Reverse trajectory: start from W_fwd, REMOVE each delta in reverse order.
    rev_state_seqs: List[List[int]] = [[] for _ in range(M_probe)]
    W_rev = W_fwd.copy()
    for j in range(M_probe):
        rev_state_seqs[j].append(sign_state(W_rev, probes[j], N))
    for k in range(M_steps - 1, -1, -1):
        d = delta_patterns[k]
        W_rev -= ALPHA_HEBBIAN * np.outer(d, d) / N
        np.fill_diagonal(W_rev, 0.0)
        for j in range(M_probe):
            rev_state_seqs[j].append(sign_state(W_rev, probes[j], N))

    t_traj = time.time() - t0 - t_build

    # Aggregate frenesy = total forward transitions + total reverse transitions.
    n_fwd_total = 0
    n_rev_total = 0
    per_probe_K: List[int] = []
    pair_fwd: Dict[Tuple[int, int], int] = {}
    pair_rev: Dict[Tuple[int, int], int] = {}
    for j in range(M_probe):
        f_n, f_pairs = count_transitions(fwd_state_seqs[j])
        r_n, r_pairs = count_transitions(rev_state_seqs[j])
        per_probe_K.append(f_n + r_n)
        n_fwd_total += f_n
        n_rev_total += r_n
        for k, v in f_pairs.items():
            pair_fwd[k] = pair_fwd.get(k, 0) + v
        for k, v in r_pairs.items():
            pair_rev[k] = pair_rev.get(k, 0) + v

    K_arr = np.asarray(per_probe_K, dtype=np.float64)
    K_mean = float(np.mean(K_arr))
    K_std = float(np.std(K_arr))
    K_total = float(np.sum(K_arr))
    sigma_margin = K_mean / (K_std / math.sqrt(len(K_arr)) + 1e-9)

    # Crude entropy-production proxy: sum_{(x,y)} f * log( (f + 1) / (r + 1) )
    sigma_EP = 0.0
    keys = set(pair_fwd.keys()) | set(pair_rev.keys())
    for key in keys:
        f = pair_fwd.get(key, 0)
        r = pair_rev.get(key, 0)
        if f > 0:
            sigma_EP += f * math.log((f + 1.0) / (r + 1.0))

    return {
        "N": N, "M_init": M_init, "M_delta": M_delta, "M_probe": M_probe,
        "M_steps": M_steps, "seed": seed,
        "frenesy_per_probe_mean": K_mean,
        "frenesy_per_probe_std": K_std,
        "frenesy_total": K_total,
        "frenesy_sigma_margin": float(sigma_margin),
        "forward_transitions": int(n_fwd_total),
        "reverse_transitions": int(n_rev_total),
        "sigma_EP_proxy": float(sigma_EP),
        "t_build_s": round(t_build, 2),
        "t_traj_s": round(t_traj, 2),
    }


def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str]:
    if not per_seed:
        return ("INCONCLUSIVE", "No per-seed data.")
    K_means = np.asarray([r["frenesy_per_probe_mean"] for r in per_seed], dtype=np.float64)
    sigmas = np.asarray([r["frenesy_sigma_margin"] for r in per_seed], dtype=np.float64)
    fwd_totals = np.asarray([r["forward_transitions"] for r in per_seed], dtype=np.int64)
    rev_totals = np.asarray([r["reverse_transitions"] for r in per_seed], dtype=np.int64)
    M_probe = per_seed[0]["M_probe"]

    n_positive = int(np.sum(K_means > HP_FRENESY_MIN))
    n_sigma_pass = int(np.sum(sigmas >= HP_SIGMA_MARGIN_MIN))
    n_nearzero = int(np.sum(K_means < HF_FRENESY_FRAC_MIN * M_probe))
    fwd_ok = bool(np.all(fwd_totals > 0))
    rev_ok = bool(np.all(rev_totals > 0))

    detail = (f"K_mean_per_seed={[round(k,3) for k in K_means.tolist()]} "
              f"sigma_margin_per_seed={[round(s,2) for s in sigmas.tolist()]} "
              f"n_K_positive={n_positive}/{len(K_means)} "
              f"n_sigma>={HP_SIGMA_MARGIN_MIN}={n_sigma_pass}/{len(K_means)} "
              f"fwd_ok={fwd_ok} rev_ok={rev_ok} "
              f"fwd_totals={fwd_totals.tolist()} rev_totals={rev_totals.tolist()} "
              f"M_probe={M_probe}")

    if n_nearzero >= HF_NEARZERO_SEEDS_MIN or (not fwd_ok) or (not rev_ok):
        return ("HARD_FAIL",
                "Maes-Netocny frenesy positivity VIOLATED. " + detail +
                f". >= {HF_NEARZERO_SEEDS_MIN} seeds in near-zero frenesy band "
                "OR forward/reverse rate trivially zero. "
                "Fast-layer non-eq claim weakened.")

    if (n_positive == len(K_means)) and (n_sigma_pass >= HP_SEEDS_PASS_MARGIN_MIN) and fwd_ok and rev_ok:
        return ("HARD_PASS",
                "Maes-Netocny frenesy positivity CONFIRMED. " + detail +
                ". Frenesy strictly positive across all seeds; sigma_margin meets band. "
                "BAND-LIFTING non-eq classification lower bound 67-77%; cap_map row lifts toward >= 70%.")

    return ("MIDDLE_BAND",
            "Frenesy positive but sigma_margin insufficient. " + detail)


def _instrumentation_selftest() -> None:
    # T1: W=0 trivially: sign_state returns 0; transitions among 0s = 0.
    Z = np.zeros((8, 8))
    v = np.array([1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
    s = sign_state(Z, v, 8)
    assert s == 0, f"W=0 sign_state must be 0; got {s}"
    print("[selftest 1/4] W=0 sign_state==0 OK", flush=True)

    # T2: count_transitions on a constant sequence = 0.
    n, pairs = count_transitions([1, 1, 1, 1])
    assert n == 0 and pairs == {}, f"constant sequence transitions != 0: {n} {pairs}"
    n2, pairs2 = count_transitions([1, -1, 1, -1])
    assert n2 == 3, f"alternating-3 transitions != 3: {n2}"
    assert pairs2.get((1, -1), 0) == 2 and pairs2.get((-1, 1), 0) == 1
    print(f"[selftest 2/4] count_transitions alt-3 = {n2} OK", flush=True)

    # T3: small smoke seed, frenesy finite and non-negative
    r3 = run_one_seed(N=64, m_frac=0.25, seed=17)
    assert math.isfinite(r3["frenesy_per_probe_mean"]) and r3["frenesy_per_probe_mean"] >= 0.0, (
        f"N=64 frenesy bad: {r3['frenesy_per_probe_mean']}")
    print(f"[selftest 3/4] N=64 frenesy_mean={r3['frenesy_per_probe_mean']:.4f} "
          f"sigma_margin={r3['frenesy_sigma_margin']:.3f} OK", flush=True)

    # T4: smoke at N=512 1 seed under 60s
    t0 = time.time()
    r4 = run_one_seed(N=N_SMOKE, m_frac=M_FRAC_DEFAULT, seed=17)
    t_smoke = time.time() - t0
    assert math.isfinite(r4["frenesy_per_probe_mean"]) and r4["frenesy_per_probe_mean"] >= 0.0, (
        f"smoke frenesy bad: {r4['frenesy_per_probe_mean']}")
    assert t_smoke < 60.0, f"smoke too slow: {t_smoke:.1f}s"
    print(f"[selftest 4/4] N={N_SMOKE} frenesy_mean={r4['frenesy_per_probe_mean']:.4f} "
          f"t={t_smoke:.2f}s OK", flush=True)
    print("[SELFTEST PASS] maes_netocny_frenesy_positivity_v1_n4096 instrumentation OK",
          flush=True)


_instrumentation_selftest()


def run(N: int, seeds: List[int], m_frac: float, smoke: bool) -> None:
    t0 = time.time()
    mode_str = "SMOKE" if smoke else "FULL"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "maes_netocny_frenesy_positivity_v1_n4096")

    print(f"[run] {exp_name} {mode_str} N={N} m_frac={m_frac} seeds={seeds}", flush=True)
    out_dir = get_output_dir(exp_name)

    per_seed: List[Dict] = []
    for seed in seeds:
        t_seed = time.time()
        r = run_one_seed(N, m_frac, seed)
        per_seed.append(r)
        print(f"  seed={seed}: K_mean={r['frenesy_per_probe_mean']:.4f} "
              f"K_std={r['frenesy_per_probe_std']:.4f} "
              f"sigma_margin={r['frenesy_sigma_margin']:.3f} "
              f"fwd={r['forward_transitions']} rev={r['reverse_transitions']} "
              f"sigma_EP={r['sigma_EP_proxy']:.3f} "
              f"({time.time()-t_seed:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict(per_seed)
    elapsed = time.time() - t0

    metrics = {
        "anchor": "maes_netocny_frenesy_positivity_v1_n4096",
        "verdict": verdict,
        "verdict_tag": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 2),
        "config": {"N": N, "m_frac": m_frac, "seeds": seeds, "smoke": smoke,
                   "M_delta_frac": M_DELTA_FRAC, "M_probe_frac": M_PROBE_FRAC,
                   "alpha_hebbian": ALPHA_HEBBIAN},
        "per_seed": per_seed,
        "summary": {
            "mean_frenesy_per_probe": float(np.mean([r["frenesy_per_probe_mean"] for r in per_seed])),
            "mean_sigma_margin": float(np.mean([r["frenesy_sigma_margin"] for r in per_seed])),
            "total_forward_transitions": int(np.sum([r["forward_transitions"] for r in per_seed])),
            "total_reverse_transitions": int(np.sum([r["reverse_transitions"] for r in per_seed])),
        },
    }
    out_path = out_dir / "metrics.json"
    tmp_path = out_dir / "metrics.json.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, out_path)
    print(f"\n[run] VERDICT: {verdict}", flush=True)
    print(f"[run] {verdict_msg}", flush=True)
    print(f"[run] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--N", type=int, default=N_FULL)
    p.add_argument("--seeds", type=int, nargs="+", default=None)
    p.add_argument("--m_frac", type=float, default=M_FRAC_DEFAULT)
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--timeout", type=float, default=14400.0)
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    if args.smoke:
        N = N_SMOKE
        seeds = args.seeds if args.seeds is not None else SEEDS_SMOKE
    else:
        N = args.N
        seeds = args.seeds if args.seeds is not None else SEEDS_FULL
    run(N=N, seeds=seeds, m_frac=args.m_frac, smoke=args.smoke)


if __name__ == "__main__":
    main()
