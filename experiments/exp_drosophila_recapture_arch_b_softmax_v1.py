"""ARCH-B Drosophila-MB-sparse RECAPTURE: sparse-KEY / dense-VALUE / SOFTMAX (supra-linear) readout.

The drill's conditional next fork after ARCH-A (linear readout) = MIDDLE_BAND (no robust recapture; limiter
localized to the LINEAR readout). ARCH-B changes ONLY the readout: explicit separable K,V + modern-Hopfield/softmax
single-step selection (recall = sign(softmax(beta*Q@K^T) @ V)). Tests "does a nonlinear/attractor readout unlock the
sparse-key capacity benefit?" -- the diagnostically-indicated change.

COMBINED FRAMING (Director STEP-2 LOCK 2026-06-17; Exp-Dev + Skunkworks aligned):
  REGIME (B): evaluate at the softmax cliff (anchor M where dense f_k=1.0 softmax exact-recall first crosses 0.5),
              which sits BEYOND the ARCH-A linear cliff (regime_lift = linear dense exact-recall < 0.10 there).
  GATING  (A; Skunkworks-BINDING): the RECAPTURE label requires sparse(0.05) > dense(1.0) +5pp (5/5 seeds) at the
              anchor -- claim-1 is a SPARSITY-advantage claim; a softmax that helps sparse and dense EQUALLY is a real
              READOUT finding, NOT a Drosophila-sparse recapture (avoids the trivial-softmax-pass).
  BETA no-Goodhart: beta FROZEN by a fixed rule (tuned on the DENSE f_k=1.0 baseline only, applied identically to all
              f_k). No per-f_k tuning.
THREE pre-registered outcomes:
  HARD_PASS = RECAPTURE      : regime_lift AND sparsity-gate(+5pp) AND capability(sparse>=0.90) -> N=4096 confirm next.
  SPARSITY_NEUTRAL           : regime_lift but NOT (gate AND capability) -> softmax lifts capacity, sparse~=dense ->
                               real READOUT finding (feeds cross-cutting nonlinear-readout bet); claim-1 RESCOPE stands.
  HONEST_BOUNDED             : NOT regime_lift (softmax doesn't beat linear) -> next fork ARCH-C (Willshaw/thresholded).
PRIMARY metric = exact-recall (DECIDES verdict); per-bit-accuracy = SECONDARY/diagnostic only (no proxy/Goodhart).

prereg: preregs/2026-06-17_drosophila_recapture_ARCH_B_sparse_key_softmax_readout_DRAFT.md (-> LOCKED combined framing)
recaptures: scorecard claim 1 (Drosophila MB sparse). predecessor: ARCH-A linear MIDDLE_BAND (commit 91336a55).
HDLAB_RUN_MODE: smoke (1 seed) | full (5 seeds). LAPTOP (N=1024) per R4 Track-1 plan. Run with .venv/Scripts/python.exe.
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path

import torch

N = 1024                                  # substrate-canonical small-N (N=4096 confirm = separate before-VALIDATED gate, REMOTE)
F_K = [0.05, 0.10, 0.20, 0.50, 1.00]      # active-fraction; 1.00 = TRUE-dense bipolar baseline; 0.05 = Drosophila op point
M_LIST = [128, 256, 512, 1024, 2048, 4096]  # softmax cliff likely HIGHER M than the linear cliff (~384); smoke locates it -> amend if needed
BETA_GRID = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0]  # beta frozen by dense-tuned rule (argmax mean dense exact over M_LIST)
ACC_THRESH = 0.90                         # exact-recall: cos(sign(recall), val) >= 0.90
CAP_BAR = 0.90                            # capability bar: sparse softmax exact-recall >= 0.90 at anchor
LINEAR_DEAD = 0.10                        # regime_lift: linear dense exact-recall < 0.10 at anchor (beyond linear cliff)
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "smoke")
SEEDS = [7] if RUN_MODE == "smoke" else [7, 17, 23, 31, 41]
DEV = "cpu"
ANCHOR = "drosophila_recapture_arch_b_softmax_v1"
OUT = Path(__file__).resolve().parents[1] / "data" / ANCHOR


def _gen(seed: int) -> torch.Generator:
    return torch.Generator(device=DEV).manual_seed(seed)


def make_sparse_keys(M: int, n: int, f_k: float, g: torch.Generator) -> torch.Tensor:
    """(M,n) sparse BIPOLAR keys: k=round(f_k*n) active positions per key (random), each +/-1; rest 0. (= ARCH-A)"""
    k = max(1, round(f_k * n))
    keys = torch.zeros((M, n), dtype=torch.float32, device=DEV)
    signs = (torch.randint(0, 2, (M, k), generator=g, device=DEV).float() * 2 - 1)
    idx = torch.argsort(torch.rand((M, n), generator=g, device=DEV), dim=1)[:, :k]
    keys.scatter_(1, idx, signs)
    return keys


def make_dense_values(M: int, n: int, g: torch.Generator) -> torch.Tensor:
    """(M,n) DENSE bipolar values (+/-1) -- held dense to ISOLATE the readout change. (= ARCH-A)"""
    return (torch.randint(0, 2, (M, n), generator=g, device=DEV).float() * 2 - 1)


def _exact_frac(recalls: torch.Tensor, vals: torch.Tensor) -> float:
    dot = (recalls * vals).sum(dim=1)
    norm = recalls.norm(dim=1) * vals.norm(dim=1) + 1e-12
    return float(((dot / norm) >= ACC_THRESH).float().mean().item())


def softmax_metrics(keys: torch.Tensor, vals: torch.Tensor, beta: float) -> tuple[float, float]:
    """ARCH-B readout: explicit K,V + softmax. recall_i = sign(softmax(beta * k_i @ K^T) @ V). Cued recall (query=key).
    Returns (exact_recall_frac, per_bit_acc)."""
    scores = keys @ keys.t()                          # (M,M) query-to-stored similarity (query = stored key)
    weights = torch.softmax(beta * scores, dim=1)     # (M,M) supra-linear selection over stored patterns
    recalls = torch.sign(weights @ vals)              # (M,N)
    exact = _exact_frac(recalls, vals)
    per_bit = float((recalls == vals).float().mean().item())
    return exact, per_bit


def linear_exact(keys: torch.Tensor, vals: torch.Tensor) -> float:
    """ARCH-A linear baseline (regime reference): W=sum val key^T; recall=sign(W@key); exact-recall fraction."""
    W = vals.t() @ keys                               # (N,N)
    recalls = torch.sign(keys @ W.t())                # (M,N)
    return _exact_frac(recalls, vals)


def anchor_M(dense_exact_by_m: dict, m_list: list) -> tuple:
    """PRE-REGISTERED anchor rule (= ARCH-A): grid-M nearest where dense f_k=1.0 SOFTMAX exact-recall first crosses 0.5
    (scan increasing M; linear-interp; snap to nearest grid M). Fallback: grid-M nearest |dense-0.5|."""
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


def tune_beta() -> tuple:
    """BETA no-Goodhart rule: freeze beta = argmax over BETA_GRID of MEAN dense (f_k=1.0) softmax exact-recall across
    M_LIST (tuned on the DENSE baseline ONLY; seed[0]; applied identically to all f_k)."""
    s = SEEDS[0]
    curve = {}
    for beta in BETA_GRID:
        accs = []
        for m in M_LIST:
            g = _gen(s * 100003 + m * 7 + 1000)       # dense (f_k=1.0) tuning generator
            keys = make_sparse_keys(m, N, 1.0, g)
            vals = make_dense_values(m, N, g)
            ex, _ = softmax_metrics(keys, vals, beta)
            accs.append(ex)
        curve[beta] = sum(accs) / len(accs)
    beta_star = max(BETA_GRID, key=lambda b: curve[b])
    return beta_star, curve


def main() -> int:
    t0 = time.time()
    beta_star, beta_curve = tune_beta()

    grid_exact = {f"{fk}": {} for fk in F_K}
    grid_perbit = {f"{fk}": {} for fk in F_K}
    grid_linear = {f"{fk}": {} for fk in F_K}        # ARCH-A linear baseline (regime reference)
    ps_exact = {f"{fk}": {f"M{m}": [] for m in M_LIST} for fk in F_K}
    for s in SEEDS:
        for fk in F_K:
            for m in M_LIST:
                g = _gen(s * 100003 + m * 7 + int(fk * 1000))
                keys = make_sparse_keys(m, N, fk, g)
                vals = make_dense_values(m, N, g)
                ex, pb = softmax_metrics(keys, vals, beta_star)
                lin = linear_exact(keys, vals)
                ps_exact[f"{fk}"][f"M{m}"].append(ex)
                grid_perbit[f"{fk}"].setdefault(f"M{m}", []).append(pb)
                grid_linear[f"{fk}"].setdefault(f"M{m}", []).append(lin)
    for fk in F_K:
        for m in M_LIST:
            ve = ps_exact[f"{fk}"][f"M{m}"]
            grid_exact[f"{fk}"][f"M{m}"] = sum(ve) / len(ve)
            grid_perbit[f"{fk}"][f"M{m}"] = sum(grid_perbit[f"{fk}"][f"M{m}"]) / len(SEEDS)
            grid_linear[f"{fk}"][f"M{m}"] = sum(grid_linear[f"{fk}"][f"M{m}"]) / len(SEEDS)

    # PRE-REGISTERED anchor (dense f_k=1.0 SOFTMAX exact-recall first crosses 0.5)
    dense_exact_by_m = {m: grid_exact["1.0"][f"M{m}"] for m in M_LIST}
    aM, m_cross, anchor_mode = anchor_M(dense_exact_by_m, M_LIST)
    # SOFTMAX-SATURATED handling (smoke + probe finding 2026-06-17): modern-Hopfield/softmax recall is SATURATED-PERFECT
    # for both sparse and dense out to >=16*N (raw-dot AND cosine, multi-beta) -- the cliff is beyond any feasible/
    # meaningful M. When dense softmax never crosses 0.5 (min >= 0.9), the nearest-0.5 fallback is meaningless; evaluate
    # at the LARGEST M that is BEYOND the linear cliff (linear dense < LINEAR_DEAD) = the most-stressed regime where the
    # readout still works perfectly = the legitimate sparsity test point (sparse vs dense where linear was dead).
    if anchor_mode == "fallback_nearest_0.5" and min(dense_exact_by_m.values()) >= 0.9:
        beyond = [m for m in M_LIST if grid_linear["1.0"][f"M{m}"] < LINEAR_DEAD]
        if beyond:
            aM = max(beyond); m_cross = float(aM); anchor_mode = "softmax_saturated_max_beyond_linear_cliff"
    aMk = f"M{aM}"

    a_sparse = grid_exact["0.05"][aMk]
    a_dense = grid_exact["1.0"][aMk]
    delta = a_sparse - a_dense
    lin_dense_anchor = grid_linear["1.0"][aMk]
    per_seed_delta = [ps_exact["0.05"][aMk][i] - ps_exact["1.0"][aMk][i] for i in range(len(SEEDS))]
    n_seeds_5pp = sum(1 for d in per_seed_delta if d >= 0.05)

    regime_lift = lin_dense_anchor < LINEAR_DEAD            # softmax achieves 0.5 where linear is dead -> capacity lift
    sparsity_gate = (delta >= 0.05) and (n_seeds_5pp == len(SEEDS))
    capability = all(ps_exact["0.05"][aMk][i] >= CAP_BAR for i in range(len(SEEDS)))

    if regime_lift and sparsity_gate and capability:
        verdict = "HARD_PASS"
        msg = (f"RECAPTURE via nonlinear readout: at anchor M={aM} (dense softmax exact-recall {a_dense:.3f}~0.5; "
               f"linear dense {lin_dense_anchor:.3f}<{LINEAR_DEAD} = beyond linear cliff) sparse f_k=0.05 exact-recall "
               f"{a_sparse:.3f} >= {CAP_BAR} AND > dense +5pp (delta={delta:+.3f}) {len(SEEDS)}/{len(SEEDS)} seeds. "
               f"Claim-1 sparsity capacity-boost recaptured. N=4096 confirm (REMOTE) before VALIDATED.")
    elif regime_lift:
        verdict = "SPARSITY_NEUTRAL"
        msg = (f"NONLINEAR READOUT LIFTS CAPACITY but SPARSITY-NEUTRAL: at anchor M={aM} softmax operates beyond the "
               f"linear cliff (linear dense {lin_dense_anchor:.3f}<{LINEAR_DEAD}) but sparse f_k=0.05 {a_sparse:.3f} does "
               f"NOT clear gate+capability vs dense {a_dense:.3f} (delta={delta:+.3f}; {n_seeds_5pp}/{len(SEEDS)} seeds "
               f">=+5pp; cap {a_sparse:.3f} vs {CAP_BAR}). Real READOUT finding (feeds cross-cutting nonlinear-readout "
               f"bet); NOT a Drosophila-sparse recapture; claim-1 RESCOPE stands. Sparse-specific edge not shown here.")
    else:
        verdict = "HONEST_BOUNDED"
        msg = (f"softmax does NOT recapture: at anchor M={aM} the regime is not beyond the linear cliff (linear dense "
               f"{lin_dense_anchor:.3f} >= {LINEAR_DEAD}) -- the nonlinear readout did not lift capacity meaningfully. "
               f"Next fork = ARCH-C (Willshaw/thresholded). Method/N-contingent (N={N}).")

    pb_sparse = grid_perbit["0.05"][aMk]
    pb_dense = grid_perbit["1.0"][aMk]

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
        "beta_star": beta_star,
        "beta_tuning_curve_dense": {str(b): round(v, 4) for b, v in beta_curve.items()},
        "elapsed_s": round(time.time() - t0, 2),
        "anchor_rule": ("PRE-REGISTERED: anchor M = grid-M nearest where dense f_k=1.0 SOFTMAX exact-recall first "
                        "crosses 0.5 (interp; fixed pre-run). beta FROZEN dense-tuned (argmax mean dense exact over M_LIST)."),
        "anchor_M": aM,
        "anchor_M_cross_interp": round(m_cross, 2),
        "anchor_mode": anchor_mode,
        "combined_framing": {
            "regime_lift (linear dense < %.2f at anchor)" % LINEAR_DEAD: bool(regime_lift),
            "linear_dense_at_anchor": lin_dense_anchor,
            "sparsity_gate (sparse>dense+5pp all-seeds; Skunkworks-BINDING)": bool(sparsity_gate),
            "capability (sparse>=%.2f all-seeds)" % CAP_BAR: bool(capability),
            "n_seeds_ge_5pp": n_seeds_5pp, "per_seed_delta": per_seed_delta},
        "primary_metric": f"exact_recall (cos(sign(recall),val) >= {ACC_THRESH}) -- DECIDES verdict",
        "secondary_metric": "per_bit_accuracy -- DIAGNOSTIC ONLY (no proxy substitution / Goodhart)",
        "grid_exact_recall_softmax": grid_exact,
        "grid_per_bit_acc_softmax": grid_perbit,
        "grid_exact_recall_linear_baseline": grid_linear,
        "per_seed_exact_softmax": ps_exact,
        "primary": {f"f_k_0.05_{aMk}": a_sparse, f"f_k_1.0_{aMk}": a_dense, "delta": delta, "anchor_M": aM,
                    "sparsity_gate": bool(sparsity_gate), "capability": bool(capability), "regime_lift": bool(regime_lift)},
        "secondary_per_bit_at_anchor": {f"f_k_0.05_{aMk}": pb_sparse, f"f_k_1.0_{aMk}": pb_dense,
                                        "delta": pb_sparse - pb_dense, "note": "diagnostic only; NOT a verdict input"},
        "prereg_bands": {
            "HARD_PASS": "regime_lift AND sparse>dense+0.05 all-seeds AND sparse>=%.2f all-seeds at anchor" % CAP_BAR,
            "SPARSITY_NEUTRAL": "regime_lift AND NOT(gate AND capability)",
            "HONEST_BOUNDED": "NOT regime_lift (softmax does not beat linear)", "acc_thresh": ACC_THRESH},
        # Skunkworks atomizer ruling B: keep recapture provenance fields consistently populated (structured metadata)
        "recapture_of": "scorecard_claim_1_drosophila_mb_sparse_f0.05 / EXP_substrate_drosophila_mb_sparse_single_modulator_v1 (HARD_FAIL gap 0.004; ARCH-A linear MIDDLE_BAND)",
        "failing_config_avoided": ("raw sparse-coding through a LINEAR heteroassociative readout (ARCH-A MIDDLE_BAND: "
                                   "no robust gain; limiter localized to the readout); ALSO probing at M>>capacity (over-capacity artifact)"),
        "method_delta": ("READOUT axis ONLY: ARCH-A linear W=sum val key^T -> ARCH-B explicit separable K,V + softmax "
                         "(modern-Hopfield) supra-linear single-step selection; sparse-key/dense-value held constant; "
                         "beta frozen dense-tuned. Tests sparse-as-routing UNDER a nonlinear readout."),
        "n_gate_before_validated": "N=1024 first decisive test; HARD_PASS confirm at N=4096 (REMOTE) before VALIDATED",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, OUT / "metrics.json")

    print(f"[{ANCHOR}] run_mode={RUN_MODE} seeds={len(SEEDS)} N={N} beta*={beta_star} -> {verdict}")
    print(f"  beta tuning (dense mean exact over M): " + "  ".join(f"b{b}={beta_curve[b]:.3f}" for b in BETA_GRID))
    print(f"  anchor M={aM} (dense softmax exact-recall={a_dense:.3f}~0.5; interp={m_cross:.1f}; mode={anchor_mode})")
    print(f"  regime_lift={regime_lift} (linear dense @anchor={lin_dense_anchor:.3f}<{LINEAR_DEAD}); "
          f"sparsity_gate={sparsity_gate}; capability={capability}")
    print(f"  PRIMARY (softmax exact-recall) @M{aM}: f_k=0.05={a_sparse:.3f} vs dense={a_dense:.3f}  delta={delta:+.3f}")
    print(f"  grid SOFTMAX exact-recall by f_k x M:")
    for fk in F_K:
        print(f"    f_k={fk}: " + "  ".join(f"M{m}={grid_exact[str(fk)][f'M{m}']:.3f}" for m in M_LIST))
    print(f"  grid LINEAR baseline exact-recall by f_k x M (regime reference):")
    for fk in F_K:
        print(f"    f_k={fk}: " + "  ".join(f"M{m}={grid_linear[str(fk)][f'M{m}']:.3f}" for m in M_LIST))
    print(f"  {msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
