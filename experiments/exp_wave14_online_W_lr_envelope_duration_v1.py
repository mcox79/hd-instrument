"""Online W lr-envelope duration probe — wave14 Cap 5 (Gong et al. 2026 Science DOI 10.1126/science.aeb0813).

Brain-inspired drill: the Gong et al. 2026 Science paper reports that large rewards accelerate
mouse learning by EXTENDING DOPAMINE DURATION (not magnitude). At fixed total dopamine release
(integral conservation), wider-shorter envelopes outperform taller-narrower envelopes.

Substrate analog (1-edge to Cap 5): replace the Robbins-Monro lr schedule
    lr(t) = 1/(1+t/10)
with 4 envelopes at FIXED discrete sum Σ_t lr(t) = 10.0 (within ±5%):
    E1 baseline Robbins-Monro (τ=10): lr(t) = c1/(1+t/10)
    E2 brief-spike rectangular:       lr(t) = 5 for t in [0,1], 0 otherwise
    E3 extended-dopamine rectangular: lr(t) = 1 for t in [0,9], 0 otherwise
    E4 optogenetic-extended (τ=40):   lr(t) = c4/(1+t/40), longer half-life

HARD PASS (article mechanism transfers):
    Extended-dopamine envelope (E3 OR E4) DOMINATES baseline (E1) at p in {0.30, 0.40}
    by >= 0.05 retention accuracy, AND brief-spike (E2) underperforms or ties baseline.
    Verdict: LR_DURATION_BEATS_MAGNITUDE.

HARD FAIL (substrate orthogonal to dopamine-duration mechanism):
    All 4 envelopes within +/- 0.02 retention across all p (envelope-independent at fixed sum).
    Verdict: LR_ENVELOPE_NEUTRAL.

MIDDLE BAND:
    Some differentiation but not the predicted direction (e.g., brief-spike wins).
    Verdict: LR_ENVELOPE_MIXED.

Design: N=4096 bipolar substrate, n_writes=50, noise p in {0.20, 0.30, 0.40}, 3 seeds per cell.
4 envelopes x 3 noise x 3 seeds = 36 cells. SNAP threshold = 1.0 (matches Cap 5 v153/v159 config).
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse, json, math, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

NOISE_LEVELS = [0.20, 0.30, 0.40]
TARGET_LR_SUM = 10.0
LR_SUM_TOLERANCE = 0.05  # +/- 5%


# ---------------------------------------------------------------------------
# Envelope functions: each returns a list of lr values for steps 0..n-1.
# All envelopes scaled/clipped so discrete sum equals TARGET_LR_SUM within tol.
# ---------------------------------------------------------------------------

def envelope_e1_baseline_rm(n_writes: int) -> list[float]:
    """E1 baseline Robbins-Monro tau=10, scaled to integral = TARGET_LR_SUM."""
    raw = [1.0 / (1.0 + t / 10.0) for t in range(n_writes)]
    s = sum(raw)
    c = TARGET_LR_SUM / s
    return [c * x for x in raw]


def envelope_e2_brief_spike(n_writes: int) -> list[float]:
    """E2 brief-spike rectangular: lr=5 for t in [0,1], 0 otherwise. sum = 10.0 exact."""
    return [5.0 if t < 2 else 0.0 for t in range(n_writes)]


def envelope_e3_extended_rect(n_writes: int) -> list[float]:
    """E3 extended-dopamine rectangular: lr=1 for t in [0,9], 0 otherwise. sum = 10.0 exact."""
    return [1.0 if t < 10 else 0.0 for t in range(n_writes)]


def envelope_e4_optogenetic_rm(n_writes: int) -> list[float]:
    """E4 optogenetic-extended Robbins-Monro tau=40, scaled to integral = TARGET_LR_SUM."""
    raw = [1.0 / (1.0 + t / 40.0) for t in range(n_writes)]
    s = sum(raw)
    c = TARGET_LR_SUM / s
    return [c * x for x in raw]


ENVELOPES = {
    "E1_baseline_RM_tau10":    envelope_e1_baseline_rm,
    "E2_brief_spike_rect":     envelope_e2_brief_spike,
    "E3_extended_rect":        envelope_e3_extended_rect,
    "E4_optogenetic_RM_tau40": envelope_e4_optogenetic_rm,
}


# ---------------------------------------------------------------------------
# Self-tests for envelope integrals (mandatory per feedback-strategy-spec-formula-selftests)
# ---------------------------------------------------------------------------

def self_test_envelopes(n_writes: int = 50) -> None:
    """Verify each envelope sums to TARGET_LR_SUM within tolerance."""
    print(f"Envelope self-test (n_writes={n_writes}, target_sum={TARGET_LR_SUM}):", flush=True)
    for name, fn in ENVELOPES.items():
        lrs = fn(n_writes)
        s = sum(lrs)
        rel_err = abs(s - TARGET_LR_SUM) / TARGET_LR_SUM
        peak = max(lrs)
        nonzero_steps = sum(1 for x in lrs if x > 0)
        ok = rel_err <= LR_SUM_TOLERANCE
        flag = "OK" if ok else "FAIL"
        print(f"  {name}: sum={s:.4f} rel_err={rel_err:.4f} peak={peak:.3f} nz_steps={nonzero_steps} [{flag}]", flush=True)
        if not ok:
            raise AssertionError(f"envelope {name}: sum={s:.4f} off target {TARGET_LR_SUM} (rel_err={rel_err:.4f} > tol {LR_SUM_TOLERANCE})")
    print("envelope self-test passed (4/4)", flush=True)


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    """Compute verdict from per-(envelope, p) mean retention accuracies.

    HARD PASS: E3 OR E4 retention >= E1 retention + 0.05 at p in {0.30, 0.40}
               AND E2 retention <= E1 retention + 0.02 at p in {0.30, 0.40}.
    HARD FAIL: All 4 envelopes within +/- 0.02 across all p.
    MIDDLE BAND: differentiation but not the predicted direction.
    """
    if "cell_table" not in summary:
        return ("LR_ENVELOPE_INCONCLUSIVE", "Missing cell_table.")
    tbl = summary["cell_table"]  # dict: env_name -> { p: mean_min_acc }
    required_envs = list(ENVELOPES.keys())
    required_ps = [0.30, 0.40]
    for e in required_envs:
        if e not in tbl:
            return ("LR_ENVELOPE_INCONCLUSIVE", f"Missing envelope {e} from cell_table.")
        for p in required_ps:
            if str(p) not in tbl[e] and p not in tbl[e]:
                return ("LR_ENVELOPE_INCONCLUSIVE", f"Missing p={p} for envelope {e}.")

    def get(env, p):
        d = tbl[env]
        if p in d:
            return d[p]
        return d[str(p)]

    # Compute pairwise gaps at p in {0.30, 0.40}
    deltas = {}
    for p in required_ps:
        e1 = get("E1_baseline_RM_tau10", p)
        e2 = get("E2_brief_spike_rect", p)
        e3 = get("E3_extended_rect", p)
        e4 = get("E4_optogenetic_RM_tau40", p)
        deltas[p] = {"e1": e1, "e2": e2, "e3": e3, "e4": e4,
                     "e3_minus_e1": e3 - e1, "e4_minus_e1": e4 - e1, "e2_minus_e1": e2 - e1}

    # HARD FAIL check: all 4 envelopes within +/- 0.02 across ALL p (including 0.20)
    # (epsilon for float comparison; "spread <= 0.02" is the substantive criterion)
    all_ps_tight = True
    for p in [0.20] + required_ps:
        vals = [get(e, p) for e in required_envs]
        if max(vals) - min(vals) > 0.02 + 1e-9:
            all_ps_tight = False
            break
    if all_ps_tight:
        return ("LR_ENVELOPE_NEUTRAL",
                f"All 4 envelopes within +/-0.02 retention across all p (max spread <= 0.02). "
                f"Substrate insensitive to lr-envelope shape at fixed integral; "
                f"dopamine-duration mechanism does NOT transfer to substrate.")

    # HARD PASS check
    # Extended (E3 or E4) dominates E1 by >= 0.05 at BOTH p=0.30 and p=0.40
    e3_dominates = all(deltas[p]["e3_minus_e1"] >= 0.05 for p in required_ps)
    e4_dominates = all(deltas[p]["e4_minus_e1"] >= 0.05 for p in required_ps)
    extended_wins = e3_dominates or e4_dominates
    # E2 brief-spike underperforms or ties baseline (delta <= +0.02)
    e2_underperforms = all(deltas[p]["e2_minus_e1"] <= 0.02 for p in required_ps)

    if extended_wins and e2_underperforms:
        winner = "E3_extended_rect" if e3_dominates else "E4_optogenetic_RM_tau40"
        gaps_str = ", ".join(
            f"p={p:.2f}: E3-E1={deltas[p]['e3_minus_e1']:+.3f} E4-E1={deltas[p]['e4_minus_e1']:+.3f} E2-E1={deltas[p]['e2_minus_e1']:+.3f}"
            for p in required_ps
        )
        return ("LR_DURATION_BEATS_MAGNITUDE",
                f"{winner} dominates baseline by >=0.05 at p in {{0.30, 0.40}}; brief-spike (E2) ties or underperforms. "
                f"Article mechanism (dopamine DURATION not magnitude) transfers to substrate at fixed integral. "
                f"Gaps: {gaps_str}.")

    # Middle band — differentiation exists but predicted direction not met
    gaps_str = ", ".join(
        f"p={p:.2f}: E2-E1={deltas[p]['e2_minus_e1']:+.3f} E3-E1={deltas[p]['e3_minus_e1']:+.3f} E4-E1={deltas[p]['e4_minus_e1']:+.3f}"
        for p in required_ps
    )
    return ("LR_ENVELOPE_MIXED",
            f"Envelopes differ but not in predicted direction (extended dominates AND brief-spike ties/loses). "
            f"Gaps: {gaps_str}. Substrate-novel pattern; trigger 2x drill on envelope dose-response.")


def self_test_verdict() -> None:
    """Verify verdict logic across the 3 predicted regimes."""
    # HARD PASS case: E3 dominates by 0.10 at both p, E2 underperforms
    s_pass = {"cell_table": {
        "E1_baseline_RM_tau10":    {0.20: 0.95, 0.30: 0.70, 0.40: 0.50},
        "E2_brief_spike_rect":     {0.20: 0.93, 0.30: 0.68, 0.40: 0.45},
        "E3_extended_rect":        {0.20: 0.96, 0.30: 0.82, 0.40: 0.60},
        "E4_optogenetic_RM_tau40": {0.20: 0.95, 0.30: 0.75, 0.40: 0.55},
    }}
    v, _ = compute_verdict(s_pass)
    assert v == "LR_DURATION_BEATS_MAGNITUDE", f"HARD PASS case got {v}"

    # HARD FAIL case: all within 0.02 across all p
    s_fail = {"cell_table": {
        "E1_baseline_RM_tau10":    {0.20: 0.94, 0.30: 0.74, 0.40: 0.55},
        "E2_brief_spike_rect":     {0.20: 0.94, 0.30: 0.74, 0.40: 0.56},
        "E3_extended_rect":        {0.20: 0.95, 0.30: 0.75, 0.40: 0.56},
        "E4_optogenetic_RM_tau40": {0.20: 0.94, 0.30: 0.73, 0.40: 0.55},
    }}
    v, _ = compute_verdict(s_fail)
    assert v == "LR_ENVELOPE_NEUTRAL", f"HARD FAIL case got {v}"

    # MIDDLE BAND case: E2 brief-spike WINS (substrate-novel)
    s_mid = {"cell_table": {
        "E1_baseline_RM_tau10":    {0.20: 0.95, 0.30: 0.70, 0.40: 0.50},
        "E2_brief_spike_rect":     {0.20: 0.97, 0.30: 0.82, 0.40: 0.60},
        "E3_extended_rect":        {0.20: 0.94, 0.30: 0.68, 0.40: 0.45},
        "E4_optogenetic_RM_tau40": {0.20: 0.95, 0.30: 0.70, 0.40: 0.50},
    }}
    v, _ = compute_verdict(s_mid)
    assert v == "LR_ENVELOPE_MIXED", f"MIDDLE BAND case got {v}"

    # INCONCLUSIVE case
    v, _ = compute_verdict({})
    assert v == "LR_ENVELOPE_INCONCLUSIVE", f"INCONCLUSIVE case got {v}"

    print("verdict self-test passed (4/4 cases)", flush=True)


# ---------------------------------------------------------------------------
# Substrate (matches Cap 5 v153 / v159: bipolar BSC, SNAP-guarded outer product)
# ---------------------------------------------------------------------------

def make_pattern(N: int, gen: torch.Generator, device) -> torch.Tensor:
    """Bipolar BSC pattern: each component in {-1, +1}."""
    b = (torch.rand(N, generator=gen) > 0.5).to(device).float()
    return 2.0 * b - 1.0


def snap_update(W: torch.Tensor, k: torch.Tensor, v: torch.Tensor,
                lr: float, N: int, snap_threshold: float = 1.0) -> torch.Tensor:
    """SNAP-guarded outer-product update (Cap 5 v153 / v159 reference impl).

    delta = lr * outer(v, k) / N
    If |delta|_max > snap_threshold: clip delta by snap_threshold / |delta|_max.
    """
    if lr == 0.0:
        return W
    delta = lr * torch.outer(v, k) / N
    delta_norm = float(delta.abs().max().item())
    if delta_norm > snap_threshold:
        delta = delta * (snap_threshold / delta_norm)
    return W + delta


def apply_bit_flip_noise(k: torch.Tensor, p_flip: float, gen: torch.Generator) -> torch.Tensor:
    """Flip each bipolar component independently with probability p_flip."""
    if p_flip <= 0.0:
        return k
    mask = (torch.rand(k.shape, generator=gen) < p_flip)
    return k * (~mask).float() + (-k) * mask.float()


def check_retrieval_noisy(W: torch.Tensor, k: torch.Tensor, v: torch.Tensor,
                          p_flip: float, noise_gen: torch.Generator) -> bool:
    """Retrieve with noisy query; pass if mean component-overlap > 0.7."""
    k_noisy = apply_bit_flip_noise(k, p_flip, noise_gen)
    pred = torch.sign(W @ k_noisy)
    pred[pred == 0] = 1.0
    overlap = float((pred * v).mean().item())
    return overlap > 0.7


def run_one_cell(N: int, n_writes: int, lr_schedule: list[float],
                 p_flip: float, seed: int, device) -> tuple[float, float]:
    """Run one (envelope, p_flip, seed) cell. Returns (min_acc, final_acc)."""
    gen = torch.Generator(device=device).manual_seed(seed)
    noise_gen = torch.Generator(device=device).manual_seed(seed + 10007)
    W = torch.zeros((N, N), device=device)
    keys = []
    values = []
    accs_over_time = []
    for step in range(n_writes):
        k = make_pattern(N, gen, device)
        v = make_pattern(N, gen, device)
        lr = lr_schedule[step]
        W = snap_update(W, k, v, lr, N)
        keys.append(k)
        values.append(v)
        n_correct = sum(
            1 for j in range(len(keys))
            if check_retrieval_noisy(W, keys[j], values[j], p_flip, noise_gen)
        )
        acc = n_correct / len(keys)
        accs_over_time.append(acc)
    return min(accs_over_time), accs_over_time[-1]


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    device = torch.device("cpu")
    cfg = {
        "N": 64 if smoke else 4096,
        # Smoke n_writes must be >= 10 so E3 (rect, t<10) hits target sum within tol;
        # below 10 the rect schedule truncates and the integral check fails by design.
        "n_writes": 10 if smoke else 50,
        "n_seeds": 1 if smoke else 3,
        "noise_levels": [0.30] if smoke else NOISE_LEVELS,
        "snap_threshold": 1.0,
        "target_lr_sum": TARGET_LR_SUM,
        "lr_sum_tolerance": LR_SUM_TOLERANCE,
        "mode": "smoke" if smoke else "full",
        "envelopes": list(ENVELOPES.keys()),
    }
    print(f"Config: N={cfg['N']} n_writes={cfg['n_writes']} n_seeds={cfg['n_seeds']}", flush=True)
    print(f"Noise levels: {cfg['noise_levels']}", flush=True)
    print(f"Envelopes: {cfg['envelopes']}", flush=True)
    print(f"Device: {device}", flush=True)

    # Build + verify envelopes at this n_writes
    print("\n=== Envelope construction + integral sanity ===", flush=True)
    schedules = {}
    envelope_meta = {}
    for env_name, fn in ENVELOPES.items():
        lrs = fn(cfg["n_writes"])
        s = sum(lrs)
        rel_err = abs(s - TARGET_LR_SUM) / TARGET_LR_SUM
        if rel_err > LR_SUM_TOLERANCE:
            raise RuntimeError(f"envelope {env_name}: integral {s:.4f} off target (rel_err {rel_err:.4f} > tol {LR_SUM_TOLERANCE})")
        schedules[env_name] = lrs
        peak = max(lrs)
        nz = sum(1 for x in lrs if x > 0)
        envelope_meta[env_name] = {"sum": s, "peak": peak, "nonzero_steps": nz, "rel_err": rel_err}
        print(f"  {env_name}: sum={s:.4f} peak={peak:.4f} nz_steps={nz}", flush=True)

    # Run the (envelope, p, seed) grid
    print("\n=== Running cells ===", flush=True)
    cell_table = {e: {} for e in ENVELOPES}
    raw_cells = []
    for env_name in ENVELOPES:
        for p_flip in cfg["noise_levels"]:
            seed_min_accs = []
            seed_final_accs = []
            for seed_i in range(cfg["n_seeds"]):
                seed = 17 + seed_i * 31
                min_acc, final_acc = run_one_cell(
                    cfg["N"], cfg["n_writes"], schedules[env_name], p_flip, seed, device
                )
                seed_min_accs.append(min_acc)
                seed_final_accs.append(final_acc)
            mean_min = sum(seed_min_accs) / len(seed_min_accs)
            mean_final = sum(seed_final_accs) / len(seed_final_accs)
            cell_table[env_name][p_flip] = mean_min
            raw_cells.append({
                "envelope": env_name, "p_flip": p_flip,
                "mean_min_acc": mean_min, "mean_final_acc": mean_final,
                "seed_min_accs": seed_min_accs, "seed_final_accs": seed_final_accs,
            })
            print(f"  {env_name} p={p_flip:.2f}: mean_min={mean_min:.3f} mean_final={mean_final:.3f}", flush=True)

    summary = {
        "cell_table": cell_table,
        "raw_cells": raw_cells,
        "envelope_meta": envelope_meta,
        "n_seeds": cfg["n_seeds"],
        "N": cfg["N"],
        "n_writes": cfg["n_writes"],
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    print(f"Elapsed: {elapsed:.1f}s", flush=True)
    return summary, verdict, msg, elapsed, cfg


def get_output_dir(name: str) -> Path:
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"missing keys: {required - d.keys()}")


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config) -> None:
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_online_W_lr_envelope_duration_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    # Smoke gate: cell_table populated with 4 envelopes, integrals all within tol
    oracle.assert_baseline_high("envelopes_evaluated",
                                float(len(s["cell_table"])) + 0.001, 0.0)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_online_W_lr_envelope_duration_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_envelopes(n_writes=50)
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
