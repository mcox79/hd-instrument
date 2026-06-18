"""A4: ARCH-B replicate at N=2048 (Bucket A; Director GO; Skunkworks GATE-0 + single-config-caveat check from E1).

UNCHANGED DESIGN from exp_drosophila_recapture_arch_b_softmax_v1 (N=1024 -> SPARSITY_NEUTRAL). A4 re-runs the SAME 2x2
(sparse-KEY/dense-VALUE x softmax readout, beta frozen dense-tuned, exact-recall primary) at N=2048 to test the
config-contingency of the ARCH-B finding (does nonlinear-readout-lifts-capacity + sparsity-neutral hold at 2x dimension?).
Skunkworks E1: guards the single-config caveat -- a cert that collapses at a 2nd N is config-contingent, reported honestly.

Readiness (remote-dispatch checklist): default run_mode=full (autonomous runner does not export it); --smoke/--self-test/--full;
--self-test writes NO metrics; structured provenance via the shared helper; import torch (q_f5 + CUDA); DEV=cuda-if-available
(GPU run) else cpu; no nested same-quote f-strings. HDLAB_RUN_MODE / --smoke / --self-test / --full. ASCII-only.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _cell_provenance import provenance_fields, now_utc

ANCHOR = "substrate_arch_b_replicate_n2048_v1"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)

N = 2048                                   # A4 replicate dimension (ARCH-B original = 1024)
F_K = [0.05, 0.10, 0.20, 0.50, 1.00]
M_LIST = [128, 256, 512, 1024, 2048, 4096]
BETA_GRID = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
ACC_THRESH = 0.90
CAP_BAR = 0.90
LINEAR_DEAD = 0.10
DEV = "cuda" if torch.cuda.is_available() else "cpu"


def _gen(seed: int):
    return torch.Generator(device=DEV).manual_seed(seed)


def make_sparse_keys(M, n, f_k, g):
    k = max(1, round(f_k * n))
    keys = torch.zeros((M, n), dtype=torch.float32, device=DEV)
    signs = (torch.randint(0, 2, (M, k), generator=g, device=DEV).float() * 2 - 1)
    idx = torch.argsort(torch.rand((M, n), generator=g, device=DEV), dim=1)[:, :k]
    keys.scatter_(1, idx, signs)
    return keys


def make_dense_values(M, n, g):
    return (torch.randint(0, 2, (M, n), generator=g, device=DEV).float() * 2 - 1)


def _exact_frac(recalls, vals):
    dot = (recalls * vals).sum(dim=1)
    norm = recalls.norm(dim=1) * vals.norm(dim=1) + 1e-12
    return float(((dot / norm) >= ACC_THRESH).float().mean().item())


def softmax_metrics(keys, vals, beta):
    scores = keys @ keys.t()
    weights = torch.softmax(beta * scores, dim=1)
    recalls = torch.sign(weights @ vals)
    return _exact_frac(recalls, vals), float((recalls == vals).float().mean().item())


def linear_exact(keys, vals):
    W = vals.t() @ keys
    recalls = torch.sign(keys @ W.t())
    return _exact_frac(recalls, vals)


def anchor_M(dense_exact_by_m, m_list):
    for i in range(len(m_list) - 1):
        lo, hi = m_list[i], m_list[i + 1]
        r_lo, r_hi = dense_exact_by_m[lo], dense_exact_by_m[hi]
        if r_lo >= 0.5 and r_hi < 0.5:
            frac = (r_lo - 0.5) / (r_lo - r_hi) if r_lo != r_hi else 0.0
            m_cross = lo + frac * (hi - lo)
            return (lo if abs(m_cross - lo) <= abs(m_cross - hi) else hi), m_cross, "interp_crossing"
    anchor = min(m_list, key=lambda m: abs(dense_exact_by_m[m] - 0.5))
    return anchor, float(anchor), "fallback_nearest_0.5"


def tune_beta(seeds):
    s = seeds[0]; curve = {}
    for beta in BETA_GRID:
        accs = []
        for m in M_LIST:
            g = _gen(s * 100003 + m * 7 + 1000)
            keys = make_sparse_keys(m, N, 1.0, g); vals = make_dense_values(m, N, g)
            ex, _ = softmax_metrics(keys, vals, beta); accs.append(ex)
        curve[beta] = sum(accs) / len(accs)
    return max(BETA_GRID, key=lambda b: curve[b]), curve


def run(seeds):
    beta_star, beta_curve = tune_beta(seeds)
    grid_exact = {f"{fk}": {} for fk in F_K}; grid_perbit = {f"{fk}": {} for fk in F_K}; grid_linear = {f"{fk}": {} for fk in F_K}
    ps_exact = {f"{fk}": {f"M{m}": [] for m in M_LIST} for fk in F_K}
    for s in seeds:
        for fk in F_K:
            for m in M_LIST:
                g = _gen(s * 100003 + m * 7 + int(fk * 1000))
                keys = make_sparse_keys(m, N, fk, g); vals = make_dense_values(m, N, g)
                ex, pb = softmax_metrics(keys, vals, beta_star); lin = linear_exact(keys, vals)
                ps_exact[f"{fk}"][f"M{m}"].append(ex)
                grid_perbit[f"{fk}"].setdefault(f"M{m}", []).append(pb)
                grid_linear[f"{fk}"].setdefault(f"M{m}", []).append(lin)
    for fk in F_K:
        for m in M_LIST:
            grid_exact[f"{fk}"][f"M{m}"] = sum(ps_exact[f"{fk}"][f"M{m}"]) / len(seeds)
            grid_perbit[f"{fk}"][f"M{m}"] = sum(grid_perbit[f"{fk}"][f"M{m}"]) / len(seeds)
            grid_linear[f"{fk}"][f"M{m}"] = sum(grid_linear[f"{fk}"][f"M{m}"]) / len(seeds)

    dense_exact_by_m = {m: grid_exact["1.0"][f"M{m}"] for m in M_LIST}
    aM, m_cross, anchor_mode = anchor_M(dense_exact_by_m, M_LIST)
    if anchor_mode == "fallback_nearest_0.5" and min(dense_exact_by_m.values()) >= 0.9:
        beyond = [m for m in M_LIST if grid_linear["1.0"][f"M{m}"] < LINEAR_DEAD]
        if beyond:
            aM = max(beyond); m_cross = float(aM); anchor_mode = "softmax_saturated_max_beyond_linear_cliff"
    aMk = f"M{aM}"

    a_sparse = grid_exact["0.05"][aMk]; a_dense = grid_exact["1.0"][aMk]; delta = a_sparse - a_dense
    lin_dense_anchor = grid_linear["1.0"][aMk]
    per_seed_delta = [ps_exact["0.05"][aMk][i] - ps_exact["1.0"][aMk][i] for i in range(len(seeds))]
    n_seeds_5pp = sum(1 for d in per_seed_delta if d >= 0.05)
    regime_lift = lin_dense_anchor < LINEAR_DEAD
    sparsity_gate = (delta >= 0.05) and (n_seeds_5pp == len(seeds))
    capability = all(ps_exact["0.05"][aMk][i] >= CAP_BAR for i in range(len(seeds)))

    if regime_lift and sparsity_gate and capability:
        verdict = "HARD_PASS"
        msg = (f"RECAPTURE via nonlinear readout at N={N} (replicate): anchor M={aM}, linear dense {lin_dense_anchor:.3f}<{LINEAR_DEAD}, "
               f"sparse f_k=0.05 {a_sparse:.3f}>={CAP_BAR} AND >dense +5pp (delta={delta:+.3f}) {len(seeds)}/{len(seeds)} seeds. ARCH-B holds + sparsity at N=2048.")
    elif regime_lift:
        verdict = "SPARSITY_NEUTRAL"
        msg = (f"NONLINEAR READOUT LIFTS CAPACITY, SPARSITY-NEUTRAL at N={N} (replicate of the N=1024 finding): anchor M={aM}, "
               f"linear dense {lin_dense_anchor:.3f}<{LINEAR_DEAD} (beyond linear cliff) but sparse f_k=0.05 {a_sparse:.3f} vs dense {a_dense:.3f} "
               f"(delta={delta:+.3f}; {n_seeds_5pp}/{len(seeds)} seeds>=+5pp) does NOT clear gate+capability. CONFIG-CONTINGENCY: the ARCH-B "
               f"readout-lever finding REPLICATES at N=2048 (E1 single-config caveat addressed). measured-bounds: N={N}.")
    else:
        verdict = "HONEST_BOUNDED"
        msg = (f"softmax does NOT beat linear at N={N}: anchor M={aM}, linear dense {lin_dense_anchor:.3f}>={LINEAR_DEAD} (not beyond linear cliff) "
               f"-> the readout lift did NOT replicate at N=2048 -> the ARCH-B finding is N=1024-CONTINGENT (honest config-contingency; E1 caveat materializes).")

    return {"verdict": verdict, "verdict_msg": msg, "N": N, "n_seeds": len(seeds), "seeds": seeds, "beta_star": beta_star,
            "dev": DEV, "anchor_M": aM, "anchor_mode": anchor_mode, "regime_lift": bool(regime_lift),
            "sparsity_gate": bool(sparsity_gate), "capability": bool(capability), "n_seeds_ge_5pp": n_seeds_5pp,
            "per_seed_delta": per_seed_delta, "linear_dense_at_anchor": lin_dense_anchor,
            "primary": {f"f_k_0.05_{aMk}": a_sparse, f"f_k_1.0_{aMk}": a_dense, "delta": delta},
            "grid_exact_recall_softmax": grid_exact, "grid_exact_recall_linear_baseline": grid_linear,
            "grid_per_bit_acc_softmax": grid_perbit, "per_seed_exact_softmax": ps_exact,
            "beta_tuning_curve_dense": {str(b): round(v, 4) for b, v in beta_curve.items()},
            "recapture_of": "ARCH-B SPARSITY_NEUTRAL @N=1024 (exp_drosophila_recapture_arch_b_softmax_v1); A4 config-contingency replicate @N=2048",
            "method_delta": "UNCHANGED ARCH-B design (sparse-key/dense-value x softmax readout, frozen dense-tuned beta, exact-recall primary) at N=2048 (was 1024); tests single-config caveat (E1)",
            "measured_bounds": f"ARCH-B 2x2 at N={N}/M_LIST/beta-dense-tuned; config-contingency check vs N=1024; NOT fundamental",
            "branch_path": "smoke_arch_b_n2048" if len(seeds) == 1 else "full_arch_b_n2048"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args, _ = ap.parse_known_args()
    run_mode = os.environ.get("HDLAB_RUN_MODE", "full").lower()
    self_test = getattr(args, "self_test", False)
    is_smoke = (args.smoke or self_test or run_mode == "smoke") and not getattr(args, "full", False)
    seeds = [7] if is_smoke else [7, 17, 23, 31, 41]
    t0 = time.time(); run_started_utc = now_utc()

    if self_test:
        run([7])  # wiring check at 1 seed
        print(f"[{ANCHOR}] --self-test wiring OK (ARCH-B 2x2 at N={N} runs on {DEV}); NO metrics written.")
        return 0

    r = run(seeds)
    metrics = {"anchor_name": ANCHOR, "verdict": r["verdict"], "verdict_msg": r["verdict_msg"], "summary": r["verdict_msg"],
               "headline": r["verdict_msg"], "n_seeds": r["n_seeds"],
               **provenance_fields("smoke" if is_smoke else "full", r["branch_path"],
                                   "measured_torch" + ("_gpu" if DEV == "cuda" else "_cpu"), run_started_utc),
               "result": r, "elapsed_s": round(time.time() - t0, 2), **{k: r[k] for k in ("N", "beta_star", "dev", "anchor_M",
               "regime_lift", "sparsity_gate", "capability", "primary", "recapture_of", "method_delta", "measured_bounds")}}
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={'smoke' if is_smoke else 'full'} N={N} dev={DEV} beta*={r['beta_star']} -> {r['verdict']}")
    print(f"  regime_lift={r['regime_lift']} sparsity_gate={r['sparsity_gate']} capability={r['capability']} anchor_M={r['anchor_M']}")
    print(f"  {r['verdict_msg']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
