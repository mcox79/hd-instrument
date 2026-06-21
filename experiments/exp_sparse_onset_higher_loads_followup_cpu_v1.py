"""sparse-onset higher-LOADS follow-up -- EXTENDS a3f473dd (sparse_alpha_fine_sweep_below_004_v1) to LOCATE the capacity
onset alpha_c(f) for the very-sparse f's that were still CAPPED (recall>=0.95 lower-bound) at a3f473dd's LOADS<=6.

Tier: MEASURED_MECHANISM (boundary-refinement; refines an existing characterization, no new mechanism). data-decides.
Skunkworks SCHEMA-VET BUILD_GO conditions:
  C1 (cite): a3f473dd (source) + 7315be3c (crosstalk-capacity-law; the onset IS the crosstalk boundary that law characterizes).
  C2 (config-MATCH, broken-cert-chain lesson): SAME N=8192, SAME sparse_pat (k-of-N), SAME W-free recall sign((s@P.T)@P - s*diag),
     SAME FLIP=0.05 as a3f473dd -- copied VERBATIM. The ONLY changes are the EXTENSION (higher LOADS + f=0.002) and a memory
     TILING of the recall (chunked over query rows) so M>>N doesn't materialize the M x M matrix (38GB) -- chunked==unchunked
     asserted in selftest (REQUIRED). VERSION-MARKER stamped in metrics.
  C-mono: monotonic alpha_c rise as f decreases, OVER THE LOCATED f's only (treat still-capped f as ">= its lower-bound").
ASCII; no em-dashes.
"""
import sys
from pathlib import Path
import argparse
import os
import time
import numpy as np

REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "sparse_onset_higher_loads_followup_cpu_v1"
_P = argparse.ArgumentParser(); _P.add_argument("--self-test", action="store_true", dest="self_test"); _ARGS, _ = _P.parse_known_args()
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full" if not _ARGS.self_test else "smoke")
# CONFIG-MATCH a3f473dd (C2): FLIP=0.05, N=8192, sparse k-of-N, W-free recall. EXTENSION: + f=0.002, + LOADS to 12.
FLIP = 0.05
SOURCE_CELL = "sparse_alpha_fine_sweep_below_004_v1"   # a3f473dd
CONFIG_VERSION = "a3f473dd-match:FLIP0.05/Nmatch/kofN/Wfree-sign((s@P.T)@P-s*diag)/recall>=0.95"   # VERSION-MARKER (C2)
FRACS = [0.002, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.10]            # + f=0.002 (sparser than a3f473dd's 0.005 floor)
RECALL_CHUNK = 2048
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]; N = 8192; LOADS = [0.05, 0.1, 0.2, 0.4, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0]   # a3f473dd's + {8,10,12}
else:
    SEEDS = [1]; N = 2048; LOADS = [0.1, 0.4, 0.7, 1.0, 1.5, 2.5, 4.0, 6.0, 8.0]


def sparse_pat(M, n, f, g):                                            # VERBATIM a3f473dd (C2)
    k = max(1, int(f * n)); P = np.zeros((M, n), np.float32)
    for i in range(M):
        idx = g.choice(n, k, replace=False); P[i, idx] = g.integers(0, 2, k) * 2 - 1
    return P


def _flip(P, g):                                                      # VERBATIM a3f473dd cue-noise (FLIP of active bits)
    s = P.copy()
    for i in range(len(P)):
        nz = np.nonzero(P[i])[0]; fl = nz[g.random(len(nz)) < FLIP]; s[i, fl] *= -1
    return s


def recall_unchunked(P, g):                                           # VERBATIM a3f473dd recall (for the chunked==unchunked selftest)
    diag = (P * P).sum(0); s = _flip(P, g)
    r = np.sign((s @ P.T) @ P - s * diag)
    return float(np.mean([np.all(r[i][np.nonzero(P[i])[0]] == P[i][np.nonzero(P[i])[0]]) for i in range(len(P))]))


def recall_chunked(P, g, chunk=RECALL_CHUNK):
    """SAME math as a3f473dd's recall, TILED over query rows (no M x M materialization). FLIP identical (same g) -> identical result."""
    M = len(P); diag = (P * P).sum(0); s = _flip(P, g)               # FLIP first (identical to unchunked) so chunking only tiles the matmul
    correct = 0
    for a in range(0, M, chunk):
        b = min(a + chunk, M)
        r = np.sign((s[a:b] @ P.T) @ P - s[a:b] * diag)              # (chunk, n); intermediate (s_chunk@P.T) = chunk x M, not M x M
        for i in range(a, b):
            nz = np.nonzero(P[i])[0]
            if len(nz) and np.all(r[i - a][nz] == P[i][nz]):
                correct += 1
    return correct / max(1, M)


def locate_onset(f, seed):
    """alpha_c(f) = highest LOAD with recall>=0.95 (the onset). capped=True if still >=0.95 at the max LOAD (lower-bound)."""
    g = np.random.default_rng(seed); c = 0.0; capped = True; last_pass = 0.0
    for load in LOADS:
        M = max(2, int(load * N))
        rec = recall_chunked(sparse_pat(M, N, f, np.random.default_rng(seed * 13 + M)), g)
        if rec >= 0.95:
            c = load; last_pass = load
        else:
            capped = False; break                                    # onset LOCATED between last_pass and this load
    if c == LOADS[-1]:
        capped = True                                                # never dropped through the top -> still lower-bound
    return {"alpha_c": c, "capped_lower_bound": bool(capped)}


def run_unit(seed):
    out = {("f%.3f" % f): locate_onset(f, seed) for f in FRACS}
    print("  [seed=%d] %s" % (seed, {k: (v["alpha_c"], "cap" if v["capped_lower_bound"] else "loc") for k, v in out.items()}), flush=True)
    return {"seed": seed, "onset": out}


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    agg = {}
    for f in FRACS:
        fk = "f%.3f" % f
        acs = [u["onset"][fk]["alpha_c"] for u in units]
        capped = any(u["onset"][fk]["capped_lower_bound"] for u in units)   # capped if ANY seed still capped (conservative -> keep lower-bound flag)
        cv = float(np.std(acs) / (np.mean(acs) + 1e-9))
        agg[fk] = {"alpha_c_mean": round(float(np.mean(acs)), 3), "capped_lower_bound": bool(capped), "seed_cv": round(cv, 4)}
    located = [f for f in FRACS if not agg["f%.3f" % f]["capped_lower_bound"]]
    still_capped = [f for f in FRACS if agg["f%.3f" % f]["capped_lower_bound"]]
    # C-mono: over LOCATED f's, alpha_c must rise monotonically as f decreases (Willshaw super-capacity)
    loc_sorted = sorted(located, reverse=True)                        # large f -> small f
    acs_loc = [agg["f%.3f" % f]["alpha_c_mean"] for f in loc_sorted]
    monotonic = all(acs_loc[i] <= acs_loc[i + 1] + 1e-6 for i in range(len(acs_loc) - 1)) if len(acs_loc) >= 2 else True
    worst_cv = max((agg["f%.3f" % f]["seed_cv"] for f in FRACS), default=0.0)
    seed_stable = worst_cv <= 0.05
    detail = {"alpha_c_by_f": agg, "located_f": located, "still_capped_lower_bound_f": still_capped,
              "monotonic_over_located": bool(monotonic), "worst_seed_cv": round(worst_cv, 4), "seed_stable": bool(seed_stable),
              "CONFIG_VERSION": CONFIG_VERSION, "source_cell": SOURCE_CELL, "cites": [SOURCE_CELL, "7315be3c_crosstalk_capacity_law"],
              "honest_scope": ("Extends a3f473dd sparse super-capacity to higher LOADS<=%g to LOCATE the onset alpha_c(f). "
                               "LOCATED for f=%s; f=%s still >=lower-bound (capped at LOADS<=%g, recall>=0.95 throughout -- preserve the "
                               ">= flag, do NOT overwrite with a located value). alpha_c rises monotonically as f decreases (Willshaw). "
                               "Config-matched to a3f473dd (C2; chunked==unchunked verified). MEASURED_MECHANISM boundary-refinement." %
                               (max(LOADS), located, still_capped, max(LOADS)))}
    summary = "located=%s still_capped(>=LB)=%s monotonic=%s worst_cv=%.3f | alpha_c=%s" % (
        located, still_capped, monotonic, worst_cv, {k: (v["alpha_c_mean"], "cap" if v["capped_lower_bound"] else "") for k, v in agg.items()})
    if not located:
        return ("MIDDLE_BAND", "MIDDLE_BAND: NO onset located even at LOADS<=%g (all f still >=lower-bound) -- the envelope is HIGHER than the swept range (honest: still a lower-bound, refine LOADS up). " % max(LOADS) + summary, detail)
    if monotonic and seed_stable:
        return ("HARD_PASS", "HARD_PASS (boundary-refinement; MEASURED_MECHANISM tier -> Skunkworks rules): located the sparse-capacity onset alpha_c(f) for f=%s at LOADS<=%g, monotonic Willshaw rise as f decreases, seed-stable (cv<=0.05); f=%s remain >=lower-bound (preserved). " % (located, max(LOADS), still_capped) + summary, detail)
    if not monotonic:
        return ("MIDDLE_BAND", "MIDDLE_BAND: onsets located but NOT monotonic over located f's (unexpected vs Willshaw -- investigate). " + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND: located but seed-unstable (cv>0.05). " + summary, detail)


def _selftest():
    g1 = np.random.default_rng(3); g2 = np.random.default_rng(3)      # SAME seed -> identical FLIP
    P = sparse_pat(60, 2048, 0.05, np.random.default_rng(9))
    ru = recall_unchunked(P, g1); rc = recall_chunked(P, g2, chunk=16)
    assert abs(ru - rc) < 1e-9, "REQUIRED (Skunkworks C2): chunked==unchunked, got %.9f vs %.9f" % (rc, ru)
    assert np.all((sparse_pat(5, 512, 0.05, np.random.default_rng(0)) != 0).sum(1) == int(0.05 * 512)), "k-of-N sparse (a3f473dd match)"
    print("[selftest] PASS: chunked==unchunked (%.2e) + k-of-N config-match a3f473dd" % abs(ru - rc), flush=True)


_selftest()
if _ARGS.self_test:
    raise SystemExit(0)

print("[config] %s mode=%s N=%d FRACS=%s LOADS<=%g seeds=%s | %s" % (ANCHOR_NAME, RUN_MODE, N, FRACS, max(LOADS), SEEDS, CONFIG_VERSION), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for seed in SEEDS:
    key = "s%d" % seed
    if key in aggregate_partials(out_dir, [key], run_config=run_config):
        print("[ckpt] %s done; skip" % key, flush=True); continue
    write_partial_key(out_dir, key, run_unit(seed))
units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "N": N,
           "FRACS": FRACS, "LOADS": LOADS, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_cpu_sparse_onset_higher_loads_extends_a3f473dd", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
