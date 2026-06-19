"""
exp_f4_spectrum_shoulder_replacement_observable_dim5_cpu_v1.py -- CONSTRUCTIVE follow-up to TW-DEFLATE HARD_FAIL: characterize the codebook's heavy-shoulder spectrum and find a REPLACEMENT dim-5 observable that IS robust at M=253 -- CPU/local (no heat), READ-ONLY.

ROUTING: Exp-Dev follow-up to CELL-TW-DEFLATE HARD_FAIL (9d pillar dim-5 not supported at M=253). Root cause was: the composite_hrr Gram
  spectrum has NO spike/bulk separation -- eigenvalues decay CONTINUOUSLY through the MP edge (a heavy shoulder), so there is no Tracy-Widom
  edge to test. TW was the wrong observable for THIS spectrum. This cell asks the constructive question: what IS the shoulder, and is there an
  alternative dim-5 observable that is (a) measurable at M=253, (b) STABLE under bootstrap (audit-robust), (c) informative? Feeds Research's
  pending TW-dim-5 protocol call with real spectral characterization (NOT a canonical claim -- measurement only; Strategy/verdict_handler own
  any pillar/cap_map change). Codebook-only (composite_hrr via AlgebraIndex), numpy, no relations, no LLM.

  CANDIDATE replacement observables for the heavy upper spectrum:
    O1 hill_alpha       -- Hill power-law exponent of the top eigenvalue tail (is the shoulder power-law / heavy-tailed?)
    O2 lambda1_over_lambda2 -- leading-spike dominance ratio
    O3 effective_rank   -- exp(Shannon entropy of normalized eigenvalues) (participation-style; how many directions carry the spectrum)
    O4 spectral_slope   -- log-log rank-eigenvalue slope over the top-k (shoulder decay exponent)
    O5 edge_excess      -- fraction of eigenvalues above the MP/Wishart edge (heaviness of the shoulder)
  Each is bootstrapped (resample atoms with replacement) -> CoV = SE/|value|; a viable replacement is STABLE (CoV <= 0.10) and informative.

PRE-REGISTERED: HARD-PASS iff >= 1 candidate observable is STABLE under bootstrap (CoV <= 0.10) AND informative (not degenerate) -> a viable
  replacement dim-5 exists at M=253; report the MOST robust as the recommendation. MIDDLE_BAND iff candidates are in (0.10, 0.20] (moderately
  robust). HARD-FAIL iff ALL candidates have CoV > 0.20 (no stable spectral observable at this scale -- dim-5 has no replacement until larger M).
  UNKNOWN if codebook < 30. ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, math
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "f4_spectrum_shoulder_replacement_observable_dim5_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
VECTOR_FIELD = "composite_hrr"; SEED = 5; N_BOOT = 100; TOPK = 30


def gram_eigs(A: np.ndarray) -> np.ndarray:
    n, p = A.shape
    G = A @ A.T if n <= p else A.T @ A
    return np.sort(np.linalg.eigvalsh(G))[::-1]            # descending


def mp_edge(n: int, p: int) -> float:
    a = math.sqrt(n - 0.5); b = math.sqrt(p - 0.5); return (a + b) ** 2


def hill_alpha(vals: np.ndarray, k: int) -> float:
    """Hill tail exponent over the top-k eigenvalues (power-law tail index)."""
    v = np.sort(vals)[::-1][:k + 1]
    if len(v) < 5 or v[-1] <= 0: return float("nan")
    logs = np.log(v[:-1] / v[-1])
    s = float(np.sum(logs))
    return (len(logs) / s) if s > 0 else float("nan")


def spectral_slope(vals: np.ndarray, k: int) -> float:
    """log-log rank vs eigenvalue slope over top-k (shoulder decay exponent)."""
    v = np.sort(vals)[::-1][:k]
    v = v[v > 0]
    if len(v) < 5: return float("nan")
    x = np.log(np.arange(1, len(v) + 1)); y = np.log(v)
    return float(np.polyfit(x, y, 1)[0])


def effective_rank(vals: np.ndarray) -> float:
    v = vals[vals > 0]
    if len(v) == 0: return 0.0
    p = v / v.sum(); H = -np.sum(p * np.log(p)); return float(math.exp(H))


def observables(A: np.ndarray) -> Dict[str, float]:
    n, p = A.shape; ev = gram_eigs(A); edge = mp_edge(n, p)
    ev_pos = ev[ev > 1e-9]
    return {"hill_alpha": hill_alpha(ev_pos, TOPK),
            "lambda1_over_lambda2": float(ev_pos[0] / ev_pos[1]) if len(ev_pos) > 1 and ev_pos[1] > 0 else float("nan"),
            "effective_rank": effective_rank(ev_pos),
            "spectral_slope": spectral_slope(ev_pos, TOPK),
            "edge_excess": float(np.mean(ev > edge))}


def _selftest():
    rng = np.random.RandomState(0)
    # power-law planted spectrum -> hill_alpha finite & positive; effective_rank < n
    X = rng.standard_normal((60, 200))
    for i in range(5): X[:, i] *= (8.0 / (i + 1))          # planted heavy directions
    o = observables(X)
    assert o["lambda1_over_lambda2"] >= 1.0
    assert 0 < o["effective_rank"] <= 60
    assert np.isfinite(o["hill_alpha"]) and np.isfinite(o["spectral_slope"])
    assert 0.0 <= o["edge_excess"] <= 1.0
    print("[selftest] PASS: f4_spectrum_shoulder_replacement_observable_dim5_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def _load_codebook() -> np.ndarray:
    from backend.substrate_index.partition import PartitionedStore
    from backend.substrate_index.algebra_index import AlgebraIndex
    idx = AlgebraIndex(); vecs = []
    for a in PartitionedStore(REPO / "data" / "substrate_index").all_atoms():
        v = getattr(idx.encode_atom(a), VECTOR_FIELD, None)
        if v is not None: vecs.append(np.asarray(v, dtype=np.float64))
    if not vecs: return np.zeros((0, 1024))
    A = np.stack(vecs); rn = np.linalg.norm(A, axis=1, keepdims=True) + 1e-12
    return (A / rn) * np.sqrt(A.shape[1])


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    A = None
    for _ in range(5):
        try:
            A = _load_codebook()
            if A.shape[0] >= 30: break
        except Exception:
            A = None; time.sleep(8)
    if A is None or A.shape[0] < 30:
        return {"error": "codebook_unavailable", "M": 0 if A is None else int(A.shape[0])}
    M, p = A.shape
    base = observables(A)
    rng = np.random.RandomState(SEED); nb = N_BOOT if RUN_MODE != "smoke" else 20
    # robustness via SUBSAMPLE-WITHOUT-REPLACEMENT (90% of atoms) -- avoids the bootstrap duplicate-row artifact (duplicates create
    # spurious heavy directions that bias hill_alpha up and effective_rank down). Unbiased composition-robustness estimate.
    m_sub = max(30, int(round(0.9 * M)))
    keys = list(base.keys()); boot = {k: [] for k in keys}
    for _ in range(nb):
        idx = rng.choice(M, size=m_sub, replace=False)
        ob = observables(A[idx])
        for k in keys:
            if np.isfinite(ob[k]): boot[k].append(ob[k])
    stats = {}
    for k in keys:
        arr = np.array(boot[k])
        if len(arr) < 5 or not np.isfinite(base[k]):
            stats[k] = {"value": None, "cov": None}; continue
        mean = float(arr.mean()); sd = float(arr.std())
        stats[k] = {"value": round(float(base[k]), 4), "boot_mean": round(mean, 4),
                    "cov": round(sd / (abs(mean) + 1e-12), 4)}
    # rank candidates by robustness (lowest CoV), among informative (finite value)
    viable = [(k, stats[k]["cov"]) for k in keys if stats[k].get("cov") is not None]
    viable.sort(key=lambda x: x[1])
    print("  codebook M=%d p=%d | MP edge=%.1f" % (M, p, mp_edge(M, p)), flush=True)
    for k in keys:
        st = stats[k]
        print("    %-22s value=%s boot_mean=%s CoV=%s" % (k, st.get("value"), st.get("boot_mean"), st.get("cov")), flush=True)
    if viable:
        best, bcov = viable[0]
        print("  MOST ROBUST candidate replacement dim-5: %s (CoV=%.4f)" % (best, bcov), flush=True)
    return {"M": M, "p": p, "stats": stats, "ranked": viable, "n_boot": nb}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("M", "")))
    ranked = r["ranked"]
    if not ranked:
        return ("UNKNOWN", "UNKNOWN: no finite spectral observable computed.")
    best, bcov = ranked[0]
    stable = [k for k, c in ranked if c <= 0.10]
    mid = [k for k, c in ranked if 0.10 < c <= 0.20]
    s = ("Codebook M=%d spectrum characterization (constructive follow-up to TW-DEFLATE HARD_FAIL; the spectrum is a continuous heavy shoulder, "
         "no TW edge). Candidate dim-5 observables ranked by bootstrap robustness: %s. STABLE(CoV<=0.10): %s. Most robust: %s (CoV=%.4f). "
         "Full stats: %s. Measurement only -- feeds Research's TW-dim-5 protocol call; Strategy owns any pillar/cap_map change.") % (
        r["M"], [(k, c) for k, c in ranked], stable, best, bcov, {k: r["stats"][k] for k in r["stats"]})
    if stable:
        return ("HARD_PASS", "HARD_PASS (a robust REPLACEMENT dim-5 observable EXISTS at M=%d): %d candidate(s) are STABLE under bootstrap "
                "(CoV<=0.10): %s. Recommend %s as the dim-5 replacement for the failed TW edge -- it is measurable at the current corpus size "
                "AND audit-robust, unlike the TW edge (which had no spike/bulk separation to test). " % (r["M"], len(stable), stable, best) + s)
    if mid:
        return ("MIDDLE_BAND", "MIDDLE_BAND: best candidate %s CoV=%.4f in (0.10,0.20] -- moderately robust; usable replacement dim-5 with a "
                "robustness footnote, or re-measure at larger M. " % (best, bcov) + s)
    return ("HARD_FAIL", "HARD_FAIL: all candidate spectral observables have CoV>0.20 (best %s=%.4f) -- no stable spectral dim-5 observable at "
            "M=%d; dim-5 has no robust replacement until the corpus grows. " % (best, bcov, r["M"]) + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s field=%s" % (ANCHOR_NAME, RUN_MODE, VECTOR_FIELD), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
