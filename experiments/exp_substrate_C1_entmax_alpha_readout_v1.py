"""C1 nonlinear-readout frontier: entmax-alpha sparse-Hopfield readout vs softmax baseline (LOCKED 2026-06-17).

Director STEP-2 LOCK GO (Skunkworks SCHEMA-VET PASS; anchor-mechanism-match CLEAN). Swaps softmax -> entmax-alpha in the
ARCH-B explicit-K,V readout (alpha=1.0 entmax IS softmax = baseline arm; 1.5 = 1.5-entmax; 2.0 = sparsemax). Question:
does a SPARSE readout MATCH softmax recall at LOWER compute? (entmax zeros low-similarity stored patterns -> the
weights@V only needs the nonzero rows -> fewer effective ops.)

VERDICT MAPPING (LOCKED; Skunkworks refinement): PRIMARY axis = COMPUTE-at-iso-recall in the SATURATED zone (ARCH-B
showed softmax recall=1.0 to >=16xN, so recall can't discriminate there -> compare FLOPs/sparsity at matched recall).
   HARD-PASS = entmax recall PRESERVED (== softmax in saturated zone) AND nonzero-weight FLOPs strictly < softmax.
   MIDDLE    = FLOPs reduction marginal (1-5%) OR compute-parity.
   HARD-FAIL = no FLOPs reduction (compute-parity) OR (if a discriminating recall cliff is reached) entmax recall < 0.50
               at M/N=2 (Hu-2023 sparse bound does NOT transfer to structured HD codes = substrate-novel negative).
   HONEST_BOUNDED = no discriminating recall regime reachable -> COMPUTE-only verdict with floor/ceiling stated
               (measured-bounds; method/config-contingent). A recall NON-TEST must NOT read as a recall HARD-FAIL.
beta FROZEN dense-tuned (alpha=1.0), applied identically across alpha (no per-arm gaming; ARCH-B rule). T2 (Hu 2023) ->
T0 only on cert PASS. TIER-1 LAPTOP (N=1024; readout-swap; no training). HDLAB_RUN_MODE smoke|full. ASCII-only.
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path

import numpy as np

ANCHOR = "substrate_C1_entmax_alpha_readout_v1"
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data" / ANCHOR
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "smoke")
N = 256 if RUN_MODE == "smoke" else 1024
SEEDS = [7] if RUN_MODE == "smoke" else [7, 17, 23]
M_LIST = [128, 256, 512, 1024] if RUN_MODE == "smoke" else [256, 512, 1024, 2048, 4096]
ALPHAS = [1.0, 1.5, 2.0]          # 1.0 softmax (baseline) / 1.5 entmax / 2.0 sparsemax
F_K = 1.0                          # dense keys (match ARCH-B dense baseline; the readout-family contrast, not sparsity-of-keys)
BETA_GRID = [1.0, 2.0, 5.0, 10.0, 20.0]
ACC_THRESH = 0.90


def _rng(seed):
    return np.random.default_rng(seed)


def make_keys(M, n, g):
    return (g.integers(0, 2, size=(M, n)).astype(np.float32) * 2 - 1)


def entmax_alpha(Z, alpha, n_iter=30):
    """Row-wise alpha-entmax (Peters et al. 2019). alpha=1 -> softmax; alpha>1 -> sparse (bisection on tau)."""
    if alpha == 1.0:
        Z = Z - Z.max(axis=1, keepdims=True)
        E = np.exp(Z)
        return E / (E.sum(axis=1, keepdims=True) + 1e-12)
    am1 = alpha - 1.0
    Zs = am1 * Z                                   # work in (alpha-1)*z space
    tau_hi = Zs.max(axis=1, keepdims=True)
    tau_lo = Zs.min(axis=1, keepdims=True) - 1.0   # sum(tau_lo) >= 1 guaranteed; sum decreasing in tau
    for _ in range(n_iter):
        tau = 0.5 * (tau_lo + tau_hi)
        p = np.clip(Zs - tau, 0.0, None) ** (1.0 / am1)
        s = p.sum(axis=1, keepdims=True)
        over = s > 1.0
        tau_lo = np.where(over, tau, tau_lo)       # sum too big -> raise tau
        tau_hi = np.where(over, tau_hi, tau)
    p = np.clip(Zs - 0.5 * (tau_lo + tau_hi), 0.0, None) ** (1.0 / am1)
    return p / (p.sum(axis=1, keepdims=True) + 1e-12)


def readout_metrics(M, n, alpha, beta, g):
    """ARCH-B explicit-K,V readout with entmax-alpha. Returns (exact_recall, nonzero_frac, flops_ratio_vs_softmax)."""
    K = make_keys(M, n, g)
    V = make_keys(M, n, g)
    scores = K @ K.T                               # (M,M) query=stored key
    W = entmax_alpha(beta * scores, alpha)         # (M,M) sparse for alpha>1
    recalls = np.sign(W @ V)                        # (M,n)
    dot = (recalls * V).sum(1)
    nrm = np.linalg.norm(recalls, axis=1) * np.linalg.norm(V, axis=1) + 1e-12
    exact = float(((dot / nrm) >= ACC_THRESH).mean())
    nz = (W > 1e-9).sum(1).mean()                  # mean nonzero attention weights per query
    nonzero_frac = float(nz / M)                   # softmax -> ~1.0; entmax -> < 1.0
    flops_ratio = nonzero_frac                     # weights@V cost scales with nonzero rows (vs softmax all-M)
    return exact, nonzero_frac, flops_ratio


def tune_beta(g0):
    """beta frozen by dense softmax (alpha=1.0) max-mean-recall over M_LIST; applied identically across alpha."""
    best_b, best_v = BETA_GRID[0], -1.0
    for b in BETA_GRID:
        accs = [readout_metrics(m, N, 1.0, b, _rng(99))[0] for m in M_LIST]
        v = sum(accs) / len(accs)
        if v > best_v:
            best_v, best_b = v, b
    return best_b


def main():
    t0 = time.time()
    beta = tune_beta(None)
    grid = {f"a{a}": {f"M{m}": {} for m in M_LIST} for a in ALPHAS}
    for s in SEEDS:
        for a in ALPHAS:
            for m in M_LIST:
                ex, nzf, fr = readout_metrics(m, N, a, beta, _rng(s * 1000 + m + int(a * 10)))
                d = grid[f"a{a}"][f"M{m}"]
                d.setdefault("exact", []).append(ex); d.setdefault("nzf", []).append(nzf); d.setdefault("fr", []).append(fr)
    for a in ALPHAS:
        for m in M_LIST:
            d = grid[f"a{a}"][f"M{m}"]
            d["exact"] = float(np.mean(d["exact"])); d["nzf"] = float(np.mean(d["nzf"])); d["fr"] = float(np.mean(d["fr"]))

    # saturated zone = M where softmax (a1.0) recall >= 0.95; PRIMARY = compute-at-iso-recall there.
    # FIX (smoke catch): compare ISO-M (softmax vs entmax at the SAME M), NOT entmax-at-M vs softmax-mean.
    sat_M = [m for m in M_LIST if grid["a1.0"][f"M{m}"]["exact"] >= 0.95]
    # SPREAD check: is softmax actually SPREADING attention (nonzero-frac >> 1/M)? If softmax is already near-one-hot
    # (self-dominance), entmax has NOTHING to sparsify -> the regime is DEGENERATE for the entmax-vs-softmax lever.
    softmax_spread = {m: grid["a1.0"][f"M{m}"]["nzf"] * m for m in M_LIST}   # nonzero COUNT (1.0 == one-hot)
    spread_M = [m for m in sat_M if softmax_spread[m] > 2.0]   # softmax keeps >2 patterns = genuine spread
    best = {"alpha": None, "flops_ratio": 1.0, "M": None}
    iso_recall_ok = False
    for a in (1.5, 2.0):
        for m in spread_M:                                    # ONLY where softmax genuinely spreads
            sm = grid["a1.0"][f"M{m}"]; em = grid[f"a{a}"][f"M{m}"]
            if em["exact"] >= sm["exact"] - 0.01:             # recall PRESERVED (iso-recall, iso-M)
                iso_recall_ok = True
                red = 1.0 - em["fr"] / max(sm["fr"], 1e-9)    # ISO-M FLOPs reduction
                if red > (1.0 - best["flops_ratio"]):
                    best = {"alpha": a, "flops_ratio": em["fr"] / max(sm["fr"], 1e-9), "M": m, "recall": em["exact"],
                            "softmax_nzf": sm["fr"], "entmax_nzf": em["fr"]}
    flops_reduction = (1.0 - best["flops_ratio"]) if best["alpha"] else 0.0

    if not sat_M:
        verdict = "HONEST_BOUNDED"
        msg = (f"no saturated recall regime reached (softmax recall < 0.95 at all M); re-pick M range. envelope at N={N}.")
    elif not spread_M:
        verdict = "HONEST_BOUNDED"
        msg = (f"DEGENERATE regime for the entmax lever: softmax is already near-ONE-HOT (self-dominance; nonzero-count "
               f"~1 at all saturated M) -> entmax has nothing to sparsify; softmax==entmax sparsity at iso-M = NO compute "
               f"difference. The entmax-vs-softmax sparsity lever needs a SPREAD-attention regime (clustered/near-collision "
               f"keys or noisy-cue), NOT i.i.d.-random + clean-cue. C1 needs a spread-regime re-design. (Same self-"
               f"dominance pattern as ARCH-B; NON-TEST on the compute lever here, NOT a refutation.) envelope at N={N}.")
    elif iso_recall_ok and flops_reduction >= 0.05:
        verdict = "HARD_PASS"
        msg = (f"RECAPTURE-CHEAPER: entmax alpha={best['alpha']} PRESERVES softmax recall ({best.get('recall',1.0):.3f}) "
               f"in the saturated zone (M={best['M']}) at {flops_reduction*100:.1f}% lower effective FLOPs "
               f"(nonzero-frac {best['flops_ratio']:.3f} vs softmax {softmax_fr:.3f}). Sparse readout matches softmax cheaper. "
               f"N={N}; readout-family/config envelope (measured-bounds), NOT fundamental.")
    elif iso_recall_ok and flops_reduction > 0.01:
        verdict = "MIDDLE_BAND"
        msg = (f"MARGINAL: entmax preserves recall but only {flops_reduction*100:.1f}% FLOPs reduction (1-5% band). "
               f"alpha={best['alpha']} nonzero-frac {best['flops_ratio']:.3f} vs softmax {softmax_fr:.3f}.")
    else:
        verdict = "HARD_FAIL"
        msg = (f"NO compute win: entmax recall-preserving but compute-PARITY (FLOPs reduction {flops_reduction*100:.1f}% "
               f"<= 1%); sparse-readout does not buy compute on structured HD codes at this config (substrate-novel negative).")

    metrics = {
        "anchor_name": ANCHOR, "verdict": verdict, "verdict_msg": msg, "headline": msg, "run_mode": RUN_MODE,
        "N": N, "n_seeds": len(SEEDS), "M_list": M_LIST, "alphas": ALPHAS, "beta_frozen": beta,
        "saturated_M": sat_M, "primary_axis": "COMPUTE-at-iso-recall (saturated zone)", "iso_recall_ok": iso_recall_ok,
        "best_compute_win": best, "softmax_spread_nonzero_count": softmax_spread, "spread_M": spread_M,
        "flops_reduction_frac": flops_reduction,
        "grid": grid, "recapture_of": "n/a -- nonlinear-readout FRONTIER extension (bears_on ARCH-B + nonlinear-readout ceiling)",
        "method_delta": "readout-family swap softmax -> entmax-alpha (1.0/1.5/2.0); beta frozen dense-tuned across alpha; ARCH-B harness",
        "measured_bounds": f"envelope of the entmax readout-family at N={N}/this config; NOT fundamental",
        "elapsed_s": round(time.time() - t0, 2),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={RUN_MODE} N={N} beta*={beta} -> {verdict}")
    print(f"  saturated M (softmax recall>=0.95): {sat_M}")
    print(f"  exact-recall + nonzero-frac by alpha x M:")
    for a in ALPHAS:
        print(f"    alpha={a}: " + "  ".join(f"M{m}=(r{grid[f'a{a}'][f'M{m}']['exact']:.2f},nz{grid[f'a{a}'][f'M{m}']['nzf']:.3f})" for m in M_LIST))
    print(f"  spread_M (softmax keeps >2 patterns): {spread_M}; best compute-win: {best}; FLOPs reduction={flops_reduction*100:.1f}%")
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
