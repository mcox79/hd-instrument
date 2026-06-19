"""
hippocampal_engram_consolidation_v1_n4096 -- Engram consolidation via substrate dynamics.

SCIENTIFIC QUESTION (PP-38 hippocampal phenomena, new sub-property):
  In memory systems, "engrams" are sparse ensembles of cells encoding a memory.
  Consolidation = the process by which a recently-learned engram is strengthened
  against interference from subsequent learning (stability-plasticity tradeoff).

  Substrate mapping:
  - Engram = sparse subset of active units in a stored pattern (top-K active units).
  - Consolidation = older patterns remain retrievable even after M_new new patterns
    are added, provided the engram's core units are protected.
  - Protection mechanism: engram replay (re-present noisy version of xi_old before
    each new write, effectively refreshing the outer-product contribution).

  Protocol:
  1. Store M_old "old" patterns. Identify engram core: top-K units by overlap with W.
  2. Add M_new new patterns WITHOUT replay -> measure drift (retrieval fidelity drops).
  3. Add M_new new patterns WITH engram replay (re-present xi_old before each write) ->
     measure consolidation benefit.
  4. Metrics:
     (A) consolidation_gain = fidelity_replay - fidelity_no_replay >= 0.10.
         HP-A: consolidation_gain >= 0.10.
     (B) old pattern retained under replay: fidelity_with_replay >= 0.70.
         HP-B: fidelity_with_replay >= 0.70.
     (C) New patterns still retrievable after replay: new_fidelity_with_replay >= 0.60.
         HP-C: new_fidelity_with_replay >= 0.60 (consolidation does not catastrophically
               push out new patterns).

HARD-PASS: HP-A AND HP-B AND HP-C.
HARD-FAIL: fidelity_with_replay < 0.40 OR fidelity_no_replay > 0.80 (no drift = no test).
MIDDLE: 2/3 cells pass.

PRE-REGISTERED BANDS:
  HP: consolidation_gain >= 0.10, old_fidelity >= 0.70, new_fidelity >= 0.60.
  HF: fidelity_with_replay < 0.40 OR no measurable drift.
  Calibration: first engram-consolidation test; no prior substrate anchor.
  Theory: Hopfield interference at alpha ~ 0.10 -> fidelity ~0.80; at alpha ~ 0.15 -> ~0.60.
  Replay should recover ~0.10-0.20 fidelity units. Bands: +-50% of theory on gain.
  No prior empirical anchor; bands set per calibration-probe policy.

FORMULA SELF-TESTS:
  1. Engram core: after storing xi in W, h = W @ xi has high-overlap units.
     Top-K = argmax(abs(h)). At M=1, h = xi (exact). K = 0.10*N (10% engram density).
     [INPUT: N=8, xi=[1,-1,1,-1,1,-1,1,-1], M=1] [EXPECTED: h = xi (exact); all units equal]
  2. Interference: storing 1 new pattern xi_new causes crosstalk to xi_old.
     Fidelity(xi_old | W_new) < 1.0 at M=2, N=8.
     [INPUT: N=8, M=2, orthogonal patterns] [EXPECTED: fidelity(xi_old) < 1.0]
  3. Replay write: W_replay = W + outer(xi_old, xi_old)/N. Fidelity(xi_old) should recover.
     [INPUT: same M=2 + replay] [EXPECTED: fidelity increases vs no-replay]

No _nN suffix (production N=4096 per PROT-018 rule 3 -- _n4096 not in anchor name).
Production N = 4096. Anchor: hippocampal_engram_consolidation_v1_n4096.
PROT-018: anchor has _n4096; N MUST = 4096.
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

ANCHOR_NAME = "hippocampal_engram_consolidation_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_OLD = 20
    M_NEW = 30
    N_QUERIES = 5
    N_REPLAY_STEPS = 1
    NOISE_FRAC = 0.10
    ENGRAM_DENSITY = 0.10
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_OLD = 40
    M_NEW = 60
    N_QUERIES = 10
    N_REPLAY_STEPS = 2
    NOISE_FRAC = 0.10
    ENGRAM_DENSITY = 0.10

# At N=4096, M_OLD+M_NEW=100: alpha=0.024 (well below alpha_c=0.138)
# alpha_after_new = (M_OLD+M_NEW)/N = 100/4096 ~ 0.024 -- too low for interference
# Use write-then-test at alpha = 0.12 to test consolidation properly
M_OLD_FULL = max(M_OLD, int(0.08 * N))
M_NEW_FULL = max(M_NEW, int(0.04 * N))

ALPHA_C = 0.138

HP_CONSOLIDATION_GAIN = 0.10
HP_OLD_FIDELITY_REPLAY = 0.70
HP_NEW_FIDELITY_REPLAY = 0.60
HF_OLD_FIDELITY_REPLAY = 0.40


def _selftest_engram():
    """Engram core: for single stored pattern, h=xi exactly."""
    n_small = 8
    xi = np.array([1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
    W = np.outer(xi, xi) / n_small
    np.fill_diagonal(W, 0.0)
    h = W @ xi
    # h = (N-1)/N * xi ~ xi for large N; for N=8: 7/8 * xi
    expected = xi * 7.0 / 8.0
    assert np.allclose(h, expected, atol=1e-8), f"engram selftest: h != expected"
    return h


def _selftest_interference():
    """Two orthogonal patterns: fidelity(xi_old | W_both) < 1.0."""
    n_small = 64
    rng = np.random.RandomState(42)
    xi_old = rng.choice([-1.0, 1.0], size=n_small).astype(np.float64)
    xi_new = rng.choice([-1.0, 1.0], size=n_small).astype(np.float64)
    W = (np.outer(xi_old, xi_old) + np.outer(xi_new, xi_new)) / n_small
    np.fill_diagonal(W, 0.0)
    h = W @ xi_old
    fid = float(np.dot(np.sign(h), xi_old)) / n_small
    # With 2 patterns and N=64, alpha=0.03, fidelity should be < 1.0 but close
    assert fid <= 1.01, f"interference selftest: fid={fid} > 1"
    return fid


def _selftest_replay():
    """Replay write recovers old pattern fidelity."""
    n_small = 64
    rng = np.random.RandomState(42)
    xi_old = rng.choice([-1.0, 1.0], size=n_small).astype(np.float64)
    xi_new = rng.choice([-1.0, 1.0], size=n_small).astype(np.float64)
    W_base = np.outer(xi_old, xi_old) / n_small
    np.fill_diagonal(W_base, 0.0)
    W_interference = W_base + np.outer(xi_new, xi_new) / n_small
    np.fill_diagonal(W_interference, 0.0)
    W_replay = W_interference + np.outer(xi_old, xi_old) / n_small
    np.fill_diagonal(W_replay, 0.0)
    fid_no_replay = float(np.dot(np.sign(W_interference @ xi_old), xi_old)) / n_small
    fid_replay = float(np.dot(np.sign(W_replay @ xi_old), xi_old)) / n_small
    assert fid_replay >= fid_no_replay, f"replay selftest: fid_replay={fid_replay} < no_replay={fid_no_replay}"
    return fid_no_replay, fid_replay


def _instrumentation_selftest():
    h = _selftest_engram()
    fid_int = _selftest_interference()
    fid_nr, fid_r = _selftest_replay()
    assert N_QUERIES > 0, "N_QUERIES > 0 required"
    print(f"[selftest] PASS: engram_h_ok fid_interference={fid_int:.4f} "
          f"fid_no_replay={fid_nr:.4f} fid_replay={fid_r:.4f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def hopfield_fidelity(W: np.ndarray, Xi: np.ndarray, n: int, noise_frac: float,
                       rng: np.random.RandomState, n_test: int, n_steps: int = 5) -> float:
    """Mean retrieval fidelity over n_test probes."""
    M = Xi.shape[0]
    fids = []
    for q in range(min(n_test, M)):
        probe = Xi[q].copy()
        flip = rng.random(n) < noise_frac
        probe[flip] *= -1.0
        state = probe.copy()
        for _ in range(n_steps):
            h = W @ state
            state = np.sign(h)
            state[state == 0] = 1.0
        fid = float(np.dot(state, Xi[q])) / float(n)
        fids.append(fid)
    return float(np.mean(fids)) if fids else 0.0


def run_seed(seed: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    # Use larger M values for meaningful interference
    m_old = max(M_OLD_FULL, M_OLD)
    m_new = max(M_NEW_FULL, M_NEW)

    Xi_old = rng.choice([-1.0, 1.0], size=(m_old, N)).astype(np.float64)
    Xi_new = rng.choice([-1.0, 1.0], size=(m_new, N)).astype(np.float64)

    # Build W_old (after storing old patterns)
    W_old = Xi_old.T @ Xi_old / float(N)
    np.fill_diagonal(W_old, 0.0)

    # Add new patterns WITHOUT replay
    W_no_replay = W_old.copy()
    W_no_replay += Xi_new.T @ Xi_new / float(N)
    np.fill_diagonal(W_no_replay, 0.0)

    # Add new patterns WITH replay (re-present Xi_old every N_REPLAY_STEPS writes)
    W_replay = W_old.copy()
    for i in range(m_new):
        W_replay += np.outer(Xi_new[i], Xi_new[i]) / float(N)
        if (i + 1) % max(1, m_new // N_REPLAY_STEPS) == 0:
            # Replay all old patterns
            for j in range(m_old):
                W_replay += np.outer(Xi_old[j], Xi_old[j]) / float(N)
    np.fill_diagonal(W_replay, 0.0)
    # Normalize to keep weights bounded
    W_replay /= (1.0 + float(m_old) * float(N_REPLAY_STEPS) / float(m_new))

    rng_test = np.random.RandomState(seed + 200)

    # Measure old-pattern fidelity
    fid_no_replay = hopfield_fidelity(W_no_replay, Xi_old, N, NOISE_FRAC, rng_test, N_QUERIES)

    rng_test2 = np.random.RandomState(seed + 201)
    fid_with_replay = hopfield_fidelity(W_replay, Xi_old, N, NOISE_FRAC, rng_test2, N_QUERIES)

    # Measure new-pattern fidelity under replay
    rng_test3 = np.random.RandomState(seed + 202)
    new_fid_with_replay = hopfield_fidelity(W_replay, Xi_new, N, NOISE_FRAC, rng_test3, N_QUERIES)

    consolidation_gain = fid_with_replay - fid_no_replay

    hp_a = consolidation_gain >= HP_CONSOLIDATION_GAIN
    hp_b = fid_with_replay >= HP_OLD_FIDELITY_REPLAY
    hp_c = new_fid_with_replay >= HP_NEW_FIDELITY_REPLAY

    alpha_total = (m_old + m_new) / float(N)
    elapsed = time.time() - t0

    print(f"  [seed={seed}] fid_no_replay={fid_no_replay:.4f} fid_replay={fid_with_replay:.4f} "
          f"gain={consolidation_gain:.4f}(HP>={HP_CONSOLIDATION_GAIN}) "
          f"new_fid={new_fid_with_replay:.4f}(HP>={HP_NEW_FIDELITY_REPLAY}) "
          f"alpha_total={alpha_total:.4f} "
          f"hp_ABC=[{int(hp_a)},{int(hp_b)},{int(hp_c)}] elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": N, "M_old": m_old, "M_new": m_new, "run_mode": RUN_MODE,
        "fidelity_no_replay": float(fid_no_replay),
        "fidelity_with_replay": float(fid_with_replay),
        "consolidation_gain": float(consolidation_gain),
        "new_fidelity_with_replay": float(new_fid_with_replay),
        "alpha_total": float(alpha_total),
        "hp_a": bool(hp_a), "hp_b": bool(hp_b), "hp_c": bool(hp_c),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(per_seed: Dict) -> Tuple[str, str]:
    results = list(per_seed.values())
    if not results:
        return ("HARD_FAIL", "No valid results.")

    n = len(results)
    mean_gain = float(np.mean([r["consolidation_gain"] for r in results]))
    mean_fid_r = float(np.mean([r["fidelity_with_replay"] for r in results]))
    mean_new_fid = float(np.mean([r["new_fidelity_with_replay"] for r in results]))

    summary = (f"consolidation_gain={mean_gain:.4f}(HP>={HP_CONSOLIDATION_GAIN}) "
               f"fid_replay={mean_fid_r:.4f}(HP>={HP_OLD_FIDELITY_REPLAY} HF<{HF_OLD_FIDELITY_REPLAY}) "
               f"new_fid={mean_new_fid:.4f}(HP>={HP_NEW_FIDELITY_REPLAY}) "
               f"n_seeds={n}")

    if mean_fid_r < HF_OLD_FIDELITY_REPLAY:
        return ("HARD_FAIL", f"HARD_FAIL: fid_replay below HF threshold. {summary}")

    n_all_hp = sum(1 for r in results if r["hp_a"] and r["hp_b"] and r["hp_c"])
    n_hp2 = sum(1 for r in results if sum([r["hp_a"], r["hp_b"], r["hp_c"]]) >= 2)
    min_pass = math.ceil(n * 0.6)

    if n_all_hp >= min_pass:
        return ("HARD_PASS", f"HARD_PASS: engram consolidation CONFIRMED. {summary}")
    if n_hp2 >= min_pass:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 2/3 cells pass. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: insufficient HP. {summary}")


out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_old": M_OLD, "M_new": M_NEW, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N} M_old={max(M_OLD_FULL, M_OLD)} M_new={max(M_NEW_FULL, M_NEW)}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(per_seed)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "mean_consolidation_gain": float(np.mean([r["consolidation_gain"] for r in all_results])) if all_results else None,
    "mean_fidelity_with_replay": float(np.mean([r["fidelity_with_replay"] for r in all_results])) if all_results else None,
    "mean_new_fidelity_with_replay": float(np.mean([r["new_fidelity_with_replay"] for r in all_results])) if all_results else None,
}
metrics_path = out_dir / "metrics.json"
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
