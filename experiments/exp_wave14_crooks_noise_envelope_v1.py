"""Crooks forensic erase noise-envelope - Cap 1 envelope expansion under bit-flip noise.

Probes whether the Crooks-FT delta_S_emp < 0.05 criterion holds when the substrate
is perturbed by bit-flip noise AFTER insertion, BEFORE the anti-Hebbian erase step.

Noise model: each entry of W is independently flipped in sign with probability p
before the reverse (erase) step. This mimics realistic substrate perturbation.

Noise levels: p in {0.0 (clean baseline), 0.05, 0.10, 0.20}.
3 seeds x 50 trials each cell.

Verdict labels:
  CROOKS_NOISE_ENVELOPE_PASS    - 2 or 3 noisy cells (p>0) satisfy delta_S_emp < 0.05
  CROOKS_NOISE_ENVELOPE_PARTIAL - 1 noisy cell satisfies delta_S_emp < 0.05
  CROOKS_NOISE_ENVELOPE_KILL    - 0 noisy cells satisfy; envelope narrows to clean only
"""
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"metrics missing keys: {required - d.keys()}")


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_noise_verdict(per_noise_results):
    """per_noise_results: dict { p_str -> delta_S_emp_mean }.
    Count how many NOISY cells (p > 0.0) pass the < 0.05 threshold.
    """
    noisy_pass = 0
    for p_str, val in per_noise_results.items():
        p_float = float(p_str)
        if p_float > 0.0 and val < 0.05:
            noisy_pass += 1
    noisy_total = sum(1 for p_str in per_noise_results if float(p_str) > 0.0)
    if noisy_pass >= 2:
        verdict = "CROOKS_NOISE_ENVELOPE_PASS"
        msg = (f"Noise envelope PASS: {noisy_pass}/{noisy_total} noisy cells "
               f"satisfy delta_S_emp < 0.05. Cap 1 verified under bit-flip noise.")
    elif noisy_pass == 1:
        verdict = "CROOKS_NOISE_ENVELOPE_PARTIAL"
        msg = (f"Noise envelope PARTIAL: {noisy_pass}/{noisy_total} noisy cells "
               f"satisfy delta_S_emp < 0.05. Cap 1 partial noise robustness.")
    else:
        verdict = "CROOKS_NOISE_ENVELOPE_KILL"
        msg = (f"Noise envelope KILL: 0/{noisy_total} noisy cells satisfy delta_S_emp < 0.05. "
               f"Cap 1 envelope narrows to clean substrate only.")
    return verdict, msg


def self_test_verdict():
    cases = [
        # All 3 noisy levels pass -> PASS
        ({"0.05": 0.01, "0.10": 0.02, "0.20": 0.03}, "CROOKS_NOISE_ENVELOPE_PASS"),
        # 2 of 3 pass -> PASS
        ({"0.05": 0.01, "0.10": 0.02, "0.20": 0.30}, "CROOKS_NOISE_ENVELOPE_PASS"),
        # 1 of 3 pass -> PARTIAL
        ({"0.05": 0.01, "0.10": 0.20, "0.20": 0.30}, "CROOKS_NOISE_ENVELOPE_PARTIAL"),
        # 0 of 3 pass -> KILL
        ({"0.05": 0.10, "0.10": 0.20, "0.20": 0.30}, "CROOKS_NOISE_ENVELOPE_KILL"),
        # Baseline p=0.0 excluded from count; 2 noisy pass -> PASS
        ({"0.0": 0.001, "0.05": 0.01, "0.10": 0.02, "0.20": 0.30}, "CROOKS_NOISE_ENVELOPE_PASS"),
    ]
    for i, (results, expected) in enumerate(cases):
        got, _ = compute_noise_verdict(results)
        if got != expected:
            raise AssertionError(f"self_test case {i}: got {got} expected {expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


# ---------------------------------------------------------------------------
# Experiment primitives (match v1 Crooks base)
# ---------------------------------------------------------------------------

def make_pattern(N, gen, device):
    b = (torch.rand(N, generator=gen) > 0.5).to(device)
    return (2.0 * b.float() - 1.0).to(torch.bfloat16)


def retrieval_entropy(W, k, candidates):
    """Entropy of softmax over inner-product scores W@k vs candidate set."""
    pred = W @ k
    scores = candidates @ pred
    log_probs = torch.log_softmax(scores.float(), dim=0)
    probs = log_probs.exp()
    H = float(-(probs * log_probs).sum().item())
    return H


def apply_bit_flip_noise(W, p, gen):
    """Flip each entry of W in sign with probability p using generator gen.
    W is bfloat16; noise mask is bool. Returns new tensor (W unchanged)."""
    if p == 0.0:
        return W
    mask = torch.rand(W.shape, generator=gen, device=W.device) < p
    return torch.where(mask, -W, W)


def run_cell(N, M_base, n_trials, seed, p_noise, device):
    """Run one (seed, p_noise) cell. Returns dict of per-trial delta_S values."""
    gen = torch.Generator(device="cpu").manual_seed(seed)
    gpu_gen = torch.Generator(device=device).manual_seed(seed + 100000)

    # Build candidate set and base keys (M_base patterns)
    candidates = torch.stack(
        [make_pattern(N, gen, device) for _ in range(M_base)], dim=0
    )  # (M_base, N) bf16
    base_keys = torch.stack(
        [make_pattern(N, gen, device) for _ in range(M_base)], dim=0
    )  # (M_base, N) bf16

    # W_base via Hebbian outer-product sum (bf16 throughout; no float32 upcast)
    W_base = (candidates.T.float() @ base_keys.float() / N).to(torch.bfloat16)
    # ^ M_base <= 200, so (N x M_base) @ (M_base x N) float32 is only
    #   16384 x 200 x 4 bytes = ~13 MB intermediate; safe.

    deltas = []
    for trial in range(n_trials):
        k_new = make_pattern(N, gen, device)
        v_new = make_pattern(N, gen, device)

        H_baseline = retrieval_entropy(W_base, k_new, candidates)

        # Forward: Hebbian insert
        W_inserted = W_base + torch.outer(v_new, k_new).to(torch.bfloat16) / N

        # Noise perturbation on W_inserted
        W_noisy = apply_bit_flip_noise(W_inserted, p_noise, gpu_gen)

        # Reverse: anti-Hebbian erase
        W_erased = W_noisy - torch.outer(v_new, k_new).to(torch.bfloat16) / N

        H_erased = retrieval_entropy(W_erased, k_new, candidates)

        delta = abs(H_erased - H_baseline)
        deltas.append(delta)

        # Free intermediates explicitly
        del W_inserted, W_noisy, W_erased

    del W_base, candidates, base_keys
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return deltas


def aggregate_cell(deltas):
    n = len(deltas)
    mean = sum(deltas) / n
    mx = max(deltas)
    std = (sum((d - mean) ** 2 for d in deltas) / n) ** 0.5
    return {"mean": mean, "max": mx, "std": std, "n_trials": n}


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if smoke:
        N = 4096
        M_base = 50
        n_trials = 10
        seeds = [17]
        noise_levels = [0.10]  # single noise level for smoke
        noise_levels_baseline = [0.0, 0.10]  # include baseline for sanity
    else:
        N = 16384
        M_base = 200
        n_trials = 50
        seeds = [17, 18, 19]
        noise_levels_baseline = [0.0, 0.05, 0.10, 0.20]

    if smoke:
        noise_levels_to_run = noise_levels_baseline
    else:
        noise_levels_to_run = noise_levels_baseline

    cfg = {
        "N": N, "M_base": M_base, "n_trials": n_trials,
        "seeds": seeds, "noise_levels": noise_levels_to_run,
    }

    print(f"Config: N={N} M_base={M_base} n_trials={n_trials} "
          f"seeds={seeds} noise_levels={noise_levels_to_run}", flush=True)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    # cell_results[p_str][seed] = aggregate_cell dict
    cell_results = {}
    for p in noise_levels_to_run:
        p_str = str(p)
        cell_results[p_str] = {}
        for seed in seeds:
            print(f"\n  [p={p} seed={seed}] running {n_trials} trials...", flush=True)
            deltas = run_cell(N, M_base, n_trials, seed, p, device)
            agg = aggregate_cell(deltas)
            cell_results[p_str][seed] = agg
            print(f"    delta_S mean={agg['mean']:.4f} max={agg['max']:.4f} "
                  f"std={agg['std']:.4f}", flush=True)

    # Aggregate per noise level across seeds
    per_noise_summary = {}
    for p_str, seed_dict in cell_results.items():
        all_means = [v["mean"] for v in seed_dict.values()]
        per_noise_summary[p_str] = sum(all_means) / len(all_means)

    if device.type == "cuda":
        peak_mb = torch.cuda.max_memory_allocated(device) / (1024 ** 2)
        print(f"\n  Peak VRAM: {peak_mb:.1f} MB", flush=True)
    else:
        peak_mb = None

    print(f"\nPer-noise delta_S_emp (mean over seeds):", flush=True)
    for p_str, val in sorted(per_noise_summary.items(), key=lambda x: float(x[0])):
        print(f"  p={p_str}: delta_S_emp={val:.4f}", flush=True)

    verdict, msg = compute_noise_verdict(per_noise_summary)
    elapsed = time.monotonic() - t0

    summary = {
        "per_noise_delta_S": per_noise_summary,
        "per_noise_cell_details": cell_results,
        "peak_vram_mb": peak_mb,
        "N": N, "M_base": M_base, "n_trials": n_trials,
        "seeds": seeds,
    }

    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------

def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "elapsed_s": elapsed, "summary": summary, "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# Smoke
# ---------------------------------------------------------------------------

def run_smoke():
    out_dir = get_output_dir("wave14_crooks_noise_envelope_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    # Sanity: delta_S_emp at p=0.10 should be within [0.0, 0.5]
    p_010_delta = s["per_noise_delta_S"].get("0.1", s["per_noise_delta_S"].get("0.10", None))
    if p_010_delta is not None:
        oracle.assert_in_range("delta_S_emp_p010", p_010_delta, (0.0, 0.5))
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_crooks_noise_envelope_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
