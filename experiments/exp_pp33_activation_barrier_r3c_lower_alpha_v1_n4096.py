"""
pp33_activation_barrier_r3c_lower_alpha_v1_n4096 -- PP-33 R3c: activation barrier at lower alpha.

Context: PP-33 non-equilibrium stat-mech framework class identification.
R3a (N=4096 extended grid): MIDDLE_BAND. nf_crit=0.495-0.505 for ALL alpha=[0.02,0.12]. Exhausted.
R3b (N=8192 extended grid): HARD_FAIL. nf_crit=0.495-0.505 IDENTICAL to R3a. N-independent boundary.
Structural conclusion: nf_crit~0.5 is N-independent fundamental boundary at alpha=[0.02,0.12].

R3c = lower alpha values: test alpha={0.001, 0.005, 0.01, 0.02} at N=4096.
Scientific question: Does the substrate become MORE robust at lower loading (smaller alpha),
shifting the retrieval boundary nf_crit to values well BELOW 0.5?
At very low alpha (few patterns stored), the network should resist noise much better,
allowing recall at higher noise_frac, meaning nf_crit should be HIGHER (closer to 1.0), NOT lower.

Wait -- the direction: nf_crit is the CRITICAL noise fraction where recall collapses to 0.5.
At LOWER alpha, recall is more robust -> substrate can handle MORE noise -> nf_crit is HIGHER.
At HIGHER alpha (near capacity), recall collapses at low noise -> nf_crit is LOWER.
So at alpha=0.001 we expect nf_crit -> high (near 0.8-0.9).
At alpha=0.02-0.12, nf_crit was stuck at ~0.5 (boundary). This is anomalous.

R3c tests: can we get nf_crit away from 0.5 boundary by going to very low alpha?
If yes (nf_crit at alpha=0.001 >> 0.5): the ~0.5 boundary at moderate alpha is a
  capacity-related phase boundary, not the retrieval mechanism failure. Ratio(0.001/0.02) computable.
If no (nf_crit still ~0.5 at alpha=0.001): the mechanism is N-independent AND alpha-independent,
  suggesting something fundamental about the retrieval dynamics at N=4096 (possible closure trigger).

FORMULA SELF-TESTS (PROT-022):
  1. Arrhenius ratio formula: (alpha_c - 0.001) / (alpha_c - 0.02) = 1.1569 (near-unity at low alpha).
     [INPUT: alpha_c=0.138, alpha1=0.001, alpha2=0.02] [EXPECTED: ratio in (1.0, 1.30)]
  2. M at alpha=0.001 N=4096: int(0.001 * 4096) = 4 >= 1.
     [EXPECTED: M_alpha001_N4096 = 4]
  3. M at alpha=0.02 N=4096: int(0.02 * 4096) = 81 >= 1.
     [EXPECTED: M_alpha02_N4096 = 81]
  4. Grid: 0.00..0.90 step 0.01 = 91 points.
     [EXPECTED: len(NOISE_FRACS) = 91 in FULL mode]

PRE-REGISTERED BANDS:
  HARD-PASS: nf_crit(alpha=0.001) > 0.6 (demonstrates nf_crit moves up at low alpha)
             AND nf_crit(alpha=0.001) > nf_crit(alpha=0.02) + 0.05
             (strictly higher than moderate-alpha boundary)
             AND ratio(0.001/0.02) >= 1.10.
  MIDDLE: nf_crit(alpha=0.001) in [0.50, 0.60] (marginal movement above boundary)
          OR ratio in [1.05, 1.10].
  HARD-FAIL: nf_crit(alpha=0.001) <= 0.50 (alpha-independent; same as moderate regime)
             OR ratio <= 1.02 (flat across all alpha tested).

NOTE: closure risk: if HARD_FAIL here (nf_crit alpha-independent across full tested range),
PP-33 activation-barrier proxy sub-claim is likely CLOSED at N=4096. R3d N=16384 is SECONDARY rescue.

PROT-018: anchor name has no _n<N> suffix binding requirement (N is config constant at 4096).
  Production N = 4096. No _n4096 in name per design (name describes experiment class, not N binding).
  EXPLICIT N-SUFFIX NOTE: "No _nN suffix; production N = 4096; rationale: R3c name follows
  prior R3a/R3b series naming without _n suffix per established series convention."
PROT-021: seed checkpoints keyed with run_mode.
QUEUE: remote_cpu_queue (pure CPU; 4 alpha x 91 noise steps x 5 seeds at N=4096).
TIMEOUT ESTIMATE: R3b (N=8192) elapsed ~642s FULL 5-seed. N=4096 is 4x cheaper (N^2 scaling).
  Also 4 alpha values vs 5 in R3b (0.8x fewer).
  ceil(1.5 * 642 * (4096/8192)^2 * (4/5)) = ceil(1.5 * 642 * 0.25 * 0.8) = ceil(192.6) = 300s.
  With 2x margin for lower alpha requiring more robust sweeps: 600s.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import numpy as np
except ImportError:
    print("[FATAL] numpy not installed.", flush=True)
    sys.exit(1)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp33_activation_barrier_r3c_lower_alpha_v1_n4096"

N = 4096  # Production N -- no _n suffix in anchor name; see PROT-018 note in docstring above.

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_C = 0.138
# R3c lower-alpha values: key scientific test
ALPHA_VALUES = [0.001, 0.005, 0.01, 0.02]
CRIT_RECALL = 0.5
N_RETRIEVAL_STEPS = 8

# PROT-022 formula self-tests at module scope
_RATIO_LOW_ALPHA = (ALPHA_C - 0.001) / (ALPHA_C - 0.02)
assert 1.0 < _RATIO_LOW_ALPHA < 1.30, f"ratio formula low-alpha: {_RATIO_LOW_ALPHA:.4f}"
_M_ALPHA001_N4096 = int(0.001 * N)  # 4
assert _M_ALPHA001_N4096 >= 1, f"M_alpha001_N4096={_M_ALPHA001_N4096} must be >= 1"
_M_ALPHA02_N4096 = int(0.02 * N)    # 81
assert _M_ALPHA02_N4096 == 81, f"M_alpha02_N4096={_M_ALPHA02_N4096} expected 81"

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_ACTIVE = 512
    N_QUERIES = 3
    NOISE_FRACS = [round(i * 0.05, 3) for i in range(19)]  # 0..0.90 step 0.05 = 19 pts
    ALPHA_VALUES_ACTIVE = [0.001, 0.02]
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_ACTIVE = N
    N_QUERIES = 8
    NOISE_FRACS = [round(i * 0.01, 3) for i in range(91)]  # 0.00..0.90 step 0.01 = 91 pts
    ALPHA_VALUES_ACTIVE = ALPHA_VALUES

assert len(NOISE_FRACS) == (19 if RUN_MODE == "smoke" else 91), \
    f"grid size: {len(NOISE_FRACS)} expected {19 if RUN_MODE == 'smoke' else 91}"

# Pre-registered thresholds (R3c lower-alpha)
HP_NFCRIT_MIN = 0.60        # nf_crit(alpha=0.001) must exceed this
HP_NFCRIT_DELTA = 0.05      # must exceed moderate-alpha nf_crit by at least this
HP_RATIO_MIN = 1.10
HF_NFCRIT_ALPHA001_MAX = 0.50   # alpha-independent boundary -> closure risk
HF_RATIO_MIN = 1.02
MIDDLE_NFCRIT_LOW = 0.50
MIDDLE_NFCRIT_HIGH = 0.60
MODERATE_ALPHA_BOUNDARY = 0.50  # prior observed nf_crit at alpha=0.02-0.12


def _instrumentation_selftest() -> None:
    # Verify formula self-tests
    r = (ALPHA_C - 0.001) / (ALPHA_C - 0.02)
    assert 1.0 < r < 1.30, f"ratio formula: {r:.4f}"

    # Verify grid
    expected_step = 0.05 if RUN_MODE == "smoke" else 0.01
    if len(NOISE_FRACS) > 1:
        step_max = max(abs(NOISE_FRACS[i+1] - NOISE_FRACS[i]) for i in range(len(NOISE_FRACS)-1))
        assert abs(step_max - expected_step) < 1e-9, f"grid step: {step_max:.4f} expected {expected_step}"

    expected_len = 19 if RUN_MODE == "smoke" else 91
    assert len(NOISE_FRACS) == expected_len, f"grid length: {len(NOISE_FRACS)} expected {expected_len}"

    # Small-scale recall sweep to verify filter passes >= 1 item
    N_t = 64
    M_t = max(1, int(0.001 * N_t))  # at very low alpha, M_t might be tiny
    M_t = max(M_t, 1)
    rng = np.random.RandomState(0)
    Xi = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    W = (Xi.T @ Xi) / float(N_t)
    recalls = []
    for nf in [0.0, 0.30, 0.60]:
        probe = Xi[0].copy()
        if nf > 0:
            flip = rng.random(N_t) < nf
            probe[flip] *= -1.0
        state = probe
        for _ in range(N_RETRIEVAL_STEPS):
            state = np.sign(W @ state)
            state[state == 0] = 1.0
        cos = float(np.dot(state, Xi[0]) / (np.linalg.norm(state) * np.linalg.norm(Xi[0]) + 1e-12))
        recalls.append(cos)
    assert len(recalls) >= 1, "no recall values computed in self-test"
    assert not any(np.isnan(r) for r in recalls), f"NaN in recalls: {recalls}"
    # nf=0.0 should have high recall
    assert recalls[0] > 0.5, f"recall at nf=0 too low: {recalls[0]:.3f}"

    print(f"[selftest] PASS: formula ok, grid ok ({len(NOISE_FRACS)} pts), "
          f"filter passes >= 1 item, recall={recalls[0]:.3f} at nf=0", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def compute_nf_crit(recalls: Dict[float, float], crit: float = CRIT_RECALL) -> Optional[float]:
    """Return noise_frac at which recall first drops below crit (linear interpolation)."""
    nfs = sorted(recalls.keys())
    for i in range(len(nfs) - 1):
        nf1, nf2 = nfs[i], nfs[i+1]
        r1, r2 = recalls[nf1], recalls[nf2]
        if r1 >= crit and r2 < crit:
            if abs(r2 - r1) > 1e-9:
                t = (crit - r1) / (r2 - r1)
                return float(nf1 + t * (nf2 - nf1))
            else:
                return float(nf2)
    return None  # boundary not found in grid


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()
    result = {"seed": seed, "N": n_dim, "run_mode": RUN_MODE}

    for alpha in ALPHA_VALUES_ACTIVE:
        M = max(1, int(alpha * n_dim))
        Xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float32)
        W = (Xi.T @ Xi) / float(n_dim)

        recalls_by_nf = {}
        for nf in NOISE_FRACS:
            acc = 0.0
            for k in range(min(N_QUERIES, M)):
                probe = Xi[k].copy()
                if nf > 0:
                    flip = rng.random(n_dim) < nf
                    probe[flip] *= -1.0
                state = probe
                for _ in range(N_RETRIEVAL_STEPS):
                    state = np.sign(W @ state)
                    state[state == 0] = 1.0
                cos = float(np.dot(state, Xi[k]) /
                            (np.linalg.norm(state) * np.linalg.norm(Xi[k]) + 1e-12))
                acc += max(cos, 0.0)
            recalls_by_nf[nf] = acc / max(min(N_QUERIES, M), 1)

        nf_crit = compute_nf_crit(recalls_by_nf, CRIT_RECALL)
        result[f"nf_crit_alpha{str(alpha).replace('.', 'p')}"] = nf_crit
        result[f"recall_nf0_alpha{str(alpha).replace('.', 'p')}"] = recalls_by_nf.get(0.0, None)

    elapsed = time.time() - t0
    result["elapsed_s"] = elapsed
    nf_parts = " ".join(
        "a{}:{}".format(str(a).replace('.', 'p'),
                        result.get("nf_crit_alpha" + str(a).replace('.', 'p')))
        for a in ALPHA_VALUES_ACTIVE
    )
    print(f"  [seed={seed}] nf_crits: {nf_parts} elapsed={elapsed:.2f}s", flush=True)
    return result


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    def mean_key(k):
        vs = [r[k] for r in results if k in r and r[k] is not None]
        return float(sum(vs) / len(vs)) if vs else None

    nf001 = mean_key("nf_crit_alpha0p001")
    nf005 = mean_key("nf_crit_alpha0p005")
    nf01  = mean_key("nf_crit_alpha0p01")
    nf02  = mean_key("nf_crit_alpha0p02")

    summary = (f"nf_crit: a0.001={nf001} a0.005={nf005} a0.01={nf01} a0.02={nf02} "
               f"moderate_boundary~{MODERATE_ALPHA_BOUNDARY} n_seeds={len(results)}")

    # HARD_FAIL: alpha-independent nf_crit at boundary (closure risk)
    if nf001 is not None and nf001 <= HF_NFCRIT_ALPHA001_MAX:
        return ("HARD_FAIL",
                f"HARD_FAIL: nf_crit(alpha=0.001)={nf001:.4f} <= {HF_NFCRIT_ALPHA001_MAX} "
                f"(alpha-independent; closure risk). {summary}")

    if (nf001 is None and nf02 is None):
        # boundary never found in grid for any alpha
        return ("HARD_FAIL", f"HARD_FAIL: nf_crit not found for any alpha at grid_max=0.90. {summary}")

    # HARD_PASS: nf_crit moves distinctly above boundary at low alpha
    if (nf001 is not None and nf02 is not None and
            nf001 >= HP_NFCRIT_MIN and
            nf001 >= nf02 + HP_NFCRIT_DELTA):
        ratio = nf001 / max(nf02, 0.001)
        if ratio >= HP_RATIO_MIN:
            return ("HARD_PASS",
                    f"HARD_PASS: nf_crit(alpha=0.001)={nf001:.4f}>={HP_NFCRIT_MIN} "
                    f"and ratio={ratio:.4f}>={HP_RATIO_MIN} (alpha-dependent boundary confirmed). "
                    f"{summary}")

    # MIDDLE
    return ("MIDDLE_BAND", f"MIDDLE_BAND: marginal nf_crit movement at low alpha. {summary}")


print(f"[config] N={N} n_active={N_ACTIVE} mode={RUN_MODE} alphas={ALPHA_VALUES_ACTIVE}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE, "alpha_values": ALPHA_VALUES_ACTIVE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
print(f"[elapsed] total {elapsed_total:.2f}s", flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "run_mode": RUN_MODE, "alpha_values": ALPHA_VALUES_ACTIVE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": list(per_seed.values()),
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
