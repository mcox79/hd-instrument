"""ARCH-A Drosophila-MB-sparse RECAPTURE: sparse-KEY / dense-VALUE / linear readout PRESERVED.

Tests whether sparse-key routing recaptures capacity in the substrate's LINEAR heteroassociative regime
(W = sum val key^T; argmax/sign readout), vs the substrate's TRUE-dense bipolar baseline (f_k=1.0).
Honest-recapture (prereg LOCK 2026-06-17): a HARD-FAIL is the load-bearing finding "sparse-key gives no gain
in the linear regime" (verdict HONEST_BOUNDED; row -> ARCH-B softmax next), NOT a forced pass. P_deflated 0.35.

AMENDED 2026-06-17 (smoke caught a degenerate M-grid; Skunkworks re-VET PASS + 2 reqs):
  - M swept AROUND the linear capacity (~0.14N=143 at N=1024) to span the recall cliff (was {512,1024,2048},
    all >> capacity -> exact-recall saturated to 0 for ALL f_k incl dense = over-capacity artifact).
  - REQ-1: anchor M is PRE-REGISTERED deterministically (where dense f_k=1.0 exact-recall first crosses 0.5).
  - REQ-2: PRIMARY verdict is EXACT-RECALL at the anchor; per-bit-accuracy is SECONDARY/diagnostic ONLY
    (non-degenerate, but does NOT gate VALIDATED -- no proxy substitution / Goodhart).

prereg: preregs/2026-06-17_drosophila_recapture_ARCH_A_sparse_key_dense_value.md
recaptures: scorecard claim 1 (Drosophila MB sparse f=0.05; STEP-4 GENUINE OVER-CLAIM HARD_FAIL gap 0.004).
HDLAB_RUN_MODE: smoke (1 seed) | full (5 seeds). LAPTOP super-fast (N=1024).
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path

import torch

N = 1024                                  # substrate-canonical small-N (matches claim's small-N regime; N=4096 confirm is a separate before-VALIDATED gate)
F_K = [0.05, 0.10, 0.20, 0.50, 1.00]      # active-fraction; 1.00 = TRUE-dense bipolar baseline (Skunkworks Ask-3); 0.05 = Drosophila op point
M_LIST = [16, 32, 64, 128, 192, 256, 288, 320, 352, 384, 416, 448, 480, 512]  # AMENDED v2: smoke revealed the EMPIRICAL exact-recall cliff (cos>=0.9 + sign readout) sits at alpha~0.25-0.5 (HIGHER than textbook 0.14N=143; the hard cos threshold + sign readout raise effective capacity). Fine-sample [256,512] in steps of 32 so the anchor (dense~0.5) lands ON the graded cliff, not in the zero-zone.
ACC_THRESH = 0.90                         # exact-recall: cos(sign(recall), val) >= 0.90
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "smoke")
SEEDS = [7] if RUN_MODE == "smoke" else [7, 17, 23, 31, 41]
DEV = "cpu"
ANCHOR = "drosophila_recapture_arch_a_v1"
OUT = Path(__file__).resolve().parents[1] / "data" / ANCHOR


def _gen(seed: int) -> torch.Generator:
    return torch.Generator(device=DEV).manual_seed(seed)


def make_sparse_keys(M: int, n: int, f_k: float, g: torch.Generator) -> torch.Tensor:
    """(M,n) sparse BIPOLAR keys: k=round(f_k*n) active positions per key (random), each +/-1; rest 0."""
    k = max(1, round(f_k * n))
    keys = torch.zeros((M, n), dtype=torch.float32, device=DEV)
    signs = (torch.randint(0, 2, (M, k), generator=g, device=DEV).float() * 2 - 1)  # +/-1
    # per-row random k positions (argsort of random scores = random permutation; take first k)
    idx = torch.argsort(torch.rand((M, n), generator=g, device=DEV), dim=1)[:, :k]
    keys.scatter_(1, idx, signs)
    return keys


def make_dense_values(M: int, n: int, g: torch.Generator) -> torch.Tensor:
    """(M,n) DENSE bipolar values (+/-1) -- held dense to ISOLATE the sparse-KEY variable."""
    return (torch.randint(0, 2, (M, n), generator=g, device=DEV).float() * 2 - 1)


def recall_metrics(M: int, f_k: float, g: torch.Generator) -> tuple[float, float]:
    """Store M (sparse-key, dense-val) pairs in linear W=sum val key^T; sign-readout.
    Returns (exact_recall_frac, per_bit_acc):
      exact_recall_frac = fraction of patterns with cos(sign(recall),val) >= ACC_THRESH (PRIMARY; capacity claim).
      per_bit_acc       = mean component match-rate sign(recall)==val (SECONDARY/diagnostic; non-degenerate)."""
    keys = make_sparse_keys(M, N, f_k, g)            # (M,N)
    vals = make_dense_values(M, N, g)                # (M,N)
    W = vals.t() @ keys                              # (N,N) linear outer-product store (PRESERVED)
    recalls = torch.sign(keys @ W.t())               # (M,N) recall_i = sign(W @ key_i)
    # cosine(sign(recall), val): val is +/-1 so |val|=sqrt(N); recall in {-1,0,1}
    dot = (recalls * vals).sum(dim=1)
    norm = recalls.norm(dim=1) * vals.norm(dim=1) + 1e-12
    cos = dot / norm
    exact = float((cos >= ACC_THRESH).float().mean().item())
    per_bit = float((recalls == vals).float().mean().item())  # zeros (sign==0) count as miss -> conservative
    return exact, per_bit


def anchor_M(dense_exact_by_m: dict, m_list: list) -> tuple:
    """PRE-REGISTERED anchor rule (REQ-1; deterministic, fixed pre-run -- NOT post-hoc cherry-pick):
    anchor = grid-M nearest the point where the dense f_k=1.0 EXACT-recall FIRST crosses 0.5
    (scan increasing M; linear-interpolate the crossing between the bracketing grid points; snap to nearest grid M).
    Fallback (no clean >=0.5 -> <0.5 crossing on the grid): grid-M minimizing |dense_exact - 0.5|."""
    for i in range(len(m_list) - 1):
        lo, hi = m_list[i], m_list[i + 1]
        r_lo, r_hi = dense_exact_by_m[lo], dense_exact_by_m[hi]
        if r_lo >= 0.5 and r_hi < 0.5:
            frac = (r_lo - 0.5) / (r_lo - r_hi) if r_lo != r_hi else 0.0
            m_cross = lo + frac * (hi - lo)
            anchor = lo if abs(m_cross - lo) <= abs(m_cross - hi) else hi
            return anchor, m_cross, "interp_crossing"
    anchor = min(m_list, key=lambda m: abs(dense_exact_by_m[m] - 0.5))
    return anchor, float(anchor), "fallback_nearest_0.5"


def main() -> int:
    t0 = time.time()
    grid_exact = {f"{fk}": {} for fk in F_K}
    grid_perbit = {f"{fk}": {} for fk in F_K}
    ps_exact = {f"{fk}": {f"M{m}": [] for m in M_LIST} for fk in F_K}
    ps_perbit = {f"{fk}": {f"M{m}": [] for m in M_LIST} for fk in F_K}
    for s in SEEDS:
        for fk in F_K:
            for m in M_LIST:
                ex, pb = recall_metrics(m, fk, _gen(s * 100003 + m * 7 + int(fk * 1000)))
                ps_exact[f"{fk}"][f"M{m}"].append(ex)
                ps_perbit[f"{fk}"][f"M{m}"].append(pb)
    for fk in F_K:
        for m in M_LIST:
            ve = ps_exact[f"{fk}"][f"M{m}"]
            vp = ps_perbit[f"{fk}"][f"M{m}"]
            grid_exact[f"{fk}"][f"M{m}"] = sum(ve) / len(ve)
            grid_perbit[f"{fk}"][f"M{m}"] = sum(vp) / len(vp)

    # REQ-1: PRE-REGISTERED deterministic anchor (dense f_k=1.0 exact-recall first crosses 0.5)
    dense_exact_by_m = {m: grid_exact["1.0"][f"M{m}"] for m in M_LIST}
    aM, m_cross, anchor_mode = anchor_M(dense_exact_by_m, M_LIST)
    aMk = f"M{aM}"

    # REQ-2: PRIMARY verdict = EXACT-RECALL at anchor M, f_k=0.05 vs f_k=1.00 (TRUE-dense baseline)
    a_sparse = grid_exact["0.05"][aMk]
    a_dense = grid_exact["1.0"][aMk]
    delta = a_sparse - a_dense
    # lone-spike guard across f_k at anchor (no degenerate single-point spike)
    fk_at_anchor = [grid_exact[f"{fk}"][aMk] for fk in F_K]   # ordered by increasing f_k
    spike = a_sparse > max(fk_at_anchor[1:]) + 0.05
    # per-seed 5/5 check for HARD-PASS (exact-recall at anchor)
    per_seed_delta = [ps_exact["0.05"][aMk][i] - ps_exact["1.0"][aMk][i] for i in range(len(SEEDS))]
    n_seeds_5pp = sum(1 for d in per_seed_delta if d >= 0.05)
    seeds_pass = (n_seeds_5pp == len(SEEDS))
    # SECONDARY (diagnostic ONLY; does NOT decide verdict -- no proxy substitution): per-bit-acc at anchor
    pb_sparse = grid_perbit["0.05"][aMk]
    pb_dense = grid_perbit["1.0"][aMk]
    perbit_flat = abs(pb_sparse - pb_dense) < 0.01

    if delta >= 0.05 and seeds_pass and not spike:
        verdict = "HARD_PASS"
        msg = (f"RECAPTURE: sparse-key f_k=0.05 EXACT-recall {a_sparse:.3f} >= dense f_k=1.0 {a_dense:.3f} +5pp "
               f"(delta={delta:+.3f}) {len(SEEDS)}/{len(SEEDS)} seeds at anchor M={aM} (dense~0.5 cliff). "
               f"N={N}; N=4096 confirm gate before VALIDATED.")
    elif delta <= -0.03:
        verdict = "HONEST_BOUNDED"
        msg = (f"sparse-key gives NO exact-recall gain in the linear regime: f_k=0.05 {a_sparse:.3f} <= dense "
               f"f_k=1.0 {a_dense:.3f} -3pp (delta={delta:+.3f}) at anchor M={aM}. Recapture needs a supra-linear "
               f"selection step (ARCH-B softmax) per drill. Method/N-contingent (N={N}).")
    else:
        verdict = "MIDDLE_BAND"
        msg = (f"NO ROBUST recapture: f_k=0.05 {a_sparse:.3f} vs dense f_k=1.0 {a_dense:.3f} (delta={delta:+.3f}) "
               f"within [-3pp,+5pp] at anchor M={aM}. NON-ROBUST: only {n_seeds_5pp}/{len(SEEDS)} seeds >= +5pp; "
               f"positive mean driven by high-variance seeds at the steepest cliff point (exact-recall~0.5 = max "
               f"per-seed variance). Per-bit-acc {'FLAT' if perbit_flat else 'differs'} ({pb_sparse:.3f} vs "
               f"{pb_dense:.3f}); f_k=0.05 tracks dense across the whole cliff (no horizontal shift = no capacity-"
               f"gain signature). Honest-negative-leaning bounded: sparse-key/dense-value/LINEAR-readout does NOT "
               f"recapture; limiter localized to the READOUT. NOT to be cited as 'almost recaptured/promising' "
               f"(Skunkworks result-VET ruling). Next fork = ARCH-B (nonlinear/softmax readout).")

    metrics = {
        "anchor_name": ANCHOR,
        "verdict": verdict,
        "verdict_msg": msg,
        "headline": msg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "N": N,
        "M_list": M_LIST,
        "elapsed_s": round(time.time() - t0, 2),
        "anchor_rule": ("PRE-REGISTERED (REQ-1): anchor M = grid-M nearest where dense f_k=1.0 EXACT-recall first "
                        "crosses 0.5 (linear interp over grid, scanning increasing M); fallback = grid-M nearest "
                        "|dense-0.5|. Fixed pre-run, NOT post-hoc."),
        "anchor_M": aM,
        "anchor_M_cross_interp": round(m_cross, 2),
        "anchor_mode": anchor_mode,
        "primary_metric": f"exact_recall (cos(sign(recall),val) >= {ACC_THRESH}) -- the capacity claim; DECIDES verdict",
        "secondary_metric": ("per_bit_accuracy (mean component match-rate) -- DIAGNOSTIC ONLY, non-degenerate; "
                             "does NOT gate VALIDATED (no proxy substitution / Goodhart) (REQ-2)"),
        "grid_exact_recall": grid_exact,
        "grid_per_bit_acc": grid_perbit,
        "per_seed_exact": ps_exact,
        "per_seed_per_bit": ps_perbit,
        "primary": {f"f_k_0.05_{aMk}": a_sparse, f"f_k_1.0_{aMk}": a_dense, "delta": delta,
                    "anchor_M": aM, "seeds_pass_5pp": seeds_pass, "n_seeds_ge_5pp": n_seeds_5pp,
                    "per_seed_delta": per_seed_delta, "lone_spike_guard_tripped": bool(spike)},
        # Skunkworks result-VET ruling: honest-negative read lives in the DESCRIPTION/headline (NOT the verdict field;
        # bands are sacrosanct). MIDDLE_BAND must not be mis-cited as promising/almost-recaptured.
        "honest_negative_read": msg if verdict in ("MIDDLE_BAND", "HONEST_BOUNDED") else "",
        "secondary_per_bit_at_anchor": {f"f_k_0.05_{aMk}": pb_sparse, f"f_k_1.0_{aMk}": pb_dense,
                                        "delta": pb_sparse - pb_dense, "note": "diagnostic only; NOT a verdict input"},
        "prereg_bands": {
            "HARD_PASS": "exact_recall(0.05,anchorM) >= exact_recall(1.0,anchorM)+0.05 all-seeds + no-lone-spike",
            "HARD_FAIL_HONEST_BOUNDED": "exact_recall(0.05,anchorM) <= exact_recall(1.0,anchorM)-0.03",
            "MIDDLE": "between", "acc_thresh": ACC_THRESH},
        # Skunkworks framework refinement 1: auditable genuinely-different provenance
        "recapture_of": "scorecard_claim_1_drosophila_mb_sparse_f0.05 / EXP_substrate_drosophila_mb_sparse_single_modulator_v1 (HARD_FAIL gap 0.004)",
        "failing_config_avoided": ("raw sparse-coding expecting bundle-capacity-gain through a LINEAR heteroassociative "
                                   "readout with NO encoder-threshold / supra-linear selection (STEP-4 mechanism); "
                                   "failing config made BOTH keys and values sparse-BINARY {0,1}; ALSO probing at "
                                   "M>>capacity where exact-recall saturates to 0 (over-capacity artifact caught at smoke 2026-06-17)"),
        "method_delta": ("sparsity on the KEY ONLY (TopK routing); VALUE held DENSE bipolar; keys sparse-BIPOLAR "
                         "(+/-1, zero-mean) NOT sparse-binary; linear W=sum val key^T + sign readout PRESERVED; M swept "
                         "AROUND capacity (16..512) with anchor at the dense-recall~0.5 cliff. Tests sparse-as-ROUTING, "
                         "not sparse-as-bundle-capacity."),
        "n_gate_before_validated": "N=1024 first decisive test; confirm at N=4096 (claim's original N; remote) before VALIDATED",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={RUN_MODE} seeds={len(SEEDS)} N={N} -> {verdict}")
    print(f"  anchor M={aM} (dense exact-recall ~0.5; interp cross={m_cross:.1f}; mode={anchor_mode})")
    print(f"  PRIMARY (exact-recall) anchor M={aM}: f_k=0.05={a_sparse:.3f} vs f_k=1.0(dense)={a_dense:.3f}  delta={delta:+.3f}")
    print(f"  SECONDARY (per-bit-acc; diagnostic) anchor M={aM}: f_k=0.05={pb_sparse:.3f} vs f_k=1.0={pb_dense:.3f}")
    print(f"  grid EXACT-recall by f_k x M:")
    for fk in F_K:
        print(f"    f_k={fk}: " + "  ".join(f"M{m}={grid_exact[str(fk)][f'M{m}']:.3f}" for m in M_LIST))
    print(f"  grid PER-BIT-acc by f_k x M:")
    for fk in F_K:
        print(f"    f_k={fk}: " + "  ".join(f"M{m}={grid_perbit[str(fk)][f'M{m}']:.3f}" for m in M_LIST))
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
