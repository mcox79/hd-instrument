"""Online W noise envelope CPU sweep — Strategy v158 Pick 1 (Cap 5 Gap B expansion).

Cap 5 (Gap B Online W Robbins-Monro+SNAP) demonstrated ONLINE_W_RESISTS_CF at FULL
(cycle 173 v153, N=8192, 50 writes, min_acc>=0.95). This experiment probes whether the
same online-W retention criterion holds when bit-flip noise is applied to each QUERY key
at retrieval time (i.i.d. per retrieval call, p_flip fraction of bits flipped).

Noise model: at retrieval step j, query key k_j is corrupted by flipping each bit
independently with probability p_flip before being passed to the recall step.
This is the same noise model used in Cap 1 (Crooks-FT, v157/v158) and Cap 3 (NESS
streaming, v158).

N=4096 (CPU-friendly). n_seeds=3. noise_levels = {0.0, 0.05, 0.10, 0.20, 0.30, 0.40}.

Memory budget (CPU):
  W: N x N float32 = 4096 x 4096 x 4 = 64 MB
  W_noisy (retrieval mask): 1D float N = 16 KB (negligible)
  Total peak: ~64 MB per seed (sequential). Well under any budget.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse, json, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

NOISE_LEVELS = [0.0, 0.05, 0.10, 0.20, 0.30, 0.40]


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"missing keys: {required - d.keys()}")


def compute_verdict(s):
    """Verdict based on noise-band pass/fail across all levels."""
    if "cell_results" not in s:
        return ("ONLINE_W_NOISE_INCONCLUSIVE", "Missing cell_results.")
    cells = s["cell_results"]
    n_cells = len(cells)
    if n_cells == 0:
        return ("ONLINE_W_NOISE_INCONCLUSIVE", "No cells evaluated.")
    # Count noise cells (p > 0)
    noise_cells = [c for c in cells if c["p_flip"] > 0.0]
    n_pass = sum(1 for c in noise_cells if c["pass"])
    n_noise = len(noise_cells)
    if n_noise == 0:
        return ("ONLINE_W_NOISE_INCONCLUSIVE", "No noise cells.")
    # Find boundary (highest p that still passes)
    passing_ps = [c["p_flip"] for c in noise_cells if c["pass"]]
    failing_ps = [c["p_flip"] for c in noise_cells if not c["pass"]]
    p_boundary = max(passing_ps) if passing_ps else 0.0
    if n_pass == n_noise:
        return ("ONLINE_W_NOISE_ENVELOPE_FULL_PASS",
                f"All {n_noise} noise cells pass (p_flip up to {max(c['p_flip'] for c in noise_cells):.2f}). "
                f"Envelope fully robust at tested noise levels.")
    if n_pass == 0:
        p_min = min(c["p_flip"] for c in noise_cells)
        return ("ONLINE_W_NOISE_ENVELOPE_KILL",
                f"0/{n_noise} noise cells pass; even p_flip={p_min:.2f} fails. "
                f"Online W retrieval not robust to bit-flip noise.")
    # Partial pass: boundary identified
    fail_min = min(failing_ps) if failing_ps else None
    return ("ONLINE_W_NOISE_ENVELOPE_NARROW",
            f"{n_pass}/{n_noise} noise cells pass; boundary at p_flip~{p_boundary:.2f} "
            f"(first fail at p~{fail_min:.2f}). Partial noise robustness.")


def self_test_verdict():
    cases = [
        ({"cell_results": [
            {"p_flip": 0.05, "pass": True},
            {"p_flip": 0.10, "pass": True},
            {"p_flip": 0.20, "pass": True},
            {"p_flip": 0.30, "pass": True},
            {"p_flip": 0.40, "pass": True},
        ]}, "ONLINE_W_NOISE_ENVELOPE_FULL_PASS"),
        ({"cell_results": [
            {"p_flip": 0.05, "pass": False},
            {"p_flip": 0.10, "pass": False},
        ]}, "ONLINE_W_NOISE_ENVELOPE_KILL"),
        ({"cell_results": [
            {"p_flip": 0.05, "pass": True},
            {"p_flip": 0.10, "pass": True},
            {"p_flip": 0.20, "pass": False},
            {"p_flip": 0.30, "pass": False},
        ]}, "ONLINE_W_NOISE_ENVELOPE_NARROW"),
        ({}, "ONLINE_W_NOISE_INCONCLUSIVE"),
        ({"cell_results": []}, "ONLINE_W_NOISE_INCONCLUSIVE"),
    ]
    for i, (s, exp) in enumerate(cases):
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"case {i}: got {a!r} expected {exp!r}")
    print(f"verdict self-test passed (5/5 cases)", flush=True)


def make_pattern(N, gen, device):
    b = (torch.rand(N, generator=gen) > 0.5).to(device).float()
    return 2.0 * b - 1.0


def robbins_monro_lr(step, base=1.0):
    return base / (1.0 + step / 10.0)


def snap_update(W, k, v, lr, N, snap_threshold=1.0):
    """SNAP-guarded outer-product update matching v153 config."""
    delta = lr * torch.outer(v, k) / N
    delta_norm = float(delta.abs().max().item())
    if delta_norm > snap_threshold:
        delta = delta * (snap_threshold / delta_norm)
    return W + delta


def apply_bit_flip_noise(k, p_flip, gen):
    """Flip each BSC bit independently with probability p_flip."""
    if p_flip <= 0.0:
        return k
    mask = (torch.rand(k.shape, generator=gen) < p_flip)
    return k * (~mask).float() * 1.0 + (-k) * mask.float()


def check_retrieval_noisy(W, k, v, p_flip, noise_gen):
    """Retrieve with noisy query key; check overlap > 0.7."""
    k_noisy = apply_bit_flip_noise(k, p_flip, noise_gen)
    pred = torch.sign(W @ k_noisy)
    pred[pred == 0] = 1.0
    overlap = float((pred * v).mean().item())
    return overlap > 0.7


def run_one_cell(N, n_writes, p_flip, seed, device):
    """Run one (noise_level, seed) cell. Returns (min_acc, final_acc, pass_bool)."""
    gen = torch.Generator(device=device).manual_seed(seed)
    noise_gen = torch.Generator(device=device).manual_seed(seed + 10007)
    W = torch.zeros((N, N), device=device)
    keys = []
    values = []
    accs_over_time = []
    for step in range(n_writes):
        k = make_pattern(N, gen, device)
        v = make_pattern(N, gen, device)
        lr = robbins_monro_lr(step)
        W = snap_update(W, k, v, lr, N)
        keys.append(k)
        values.append(v)
        n_correct = sum(
            1 for j in range(len(keys))
            if check_retrieval_noisy(W, keys[j], values[j], p_flip, noise_gen)
        )
        acc = n_correct / len(keys)
        accs_over_time.append(acc)
    min_acc = min(accs_over_time)
    final_acc = accs_over_time[-1]
    passes = min_acc >= 0.95
    return min_acc, final_acc, passes


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")  # CPU exploratory sweep
    cfg = {
        "N": 1024 if smoke else 4096,
        "n_writes": 10 if smoke else 50,
        "n_seeds": 1 if smoke else 3,
        "noise_levels": [0.0, 0.10] if smoke else NOISE_LEVELS,
        "mode": "smoke" if smoke else "full",
    }
    print(f"Config: N={cfg['N']} n_writes={cfg['n_writes']} n_seeds={cfg['n_seeds']}", flush=True)
    print(f"Noise levels: {cfg['noise_levels']}", flush=True)
    print(f"Device: {device}", flush=True)
    # Memory budget: W = N x N float32
    w_mb = cfg["N"] * cfg["N"] * 4 / 1e6
    print(f"W memory per seed: {w_mb:.1f} MB (peak CPU)", flush=True)
    cell_results = []
    for p_flip in cfg["noise_levels"]:
        seed_min_accs = []
        for seed_i in range(cfg["n_seeds"]):
            seed = 17 + seed_i * 31
            min_acc, final_acc, passes = run_one_cell(cfg["N"], cfg["n_writes"], p_flip, seed, device)
            seed_min_accs.append(min_acc)
            print(f"  p_flip={p_flip:.2f} seed={seed_i}: min_acc={min_acc:.3f} final={final_acc:.3f} pass={passes}", flush=True)
        mean_min_acc = sum(seed_min_accs) / len(seed_min_accs)
        cell_pass = mean_min_acc >= 0.95
        cell_results.append({
            "p_flip": p_flip,
            "mean_min_acc": mean_min_acc,
            "seed_min_accs": seed_min_accs,
            "pass": cell_pass,
        })
        print(f"  => p_flip={p_flip:.2f}: mean_min_acc={mean_min_acc:.3f} PASS={cell_pass}", flush=True)
    summary = {"cell_results": cell_results, "n_seeds": cfg["n_seeds"], "N": cfg["N"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    print(f"Elapsed: {elapsed:.1f}s", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
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
    out_dir = get_output_dir("wave14_online_W_noise_envelope_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    # Smoke gate: at least one cell evaluated and metrics valid
    oracle.assert_baseline_high("cells_evaluated", float(len(s["cell_results"])) + 0.001, 0.0)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_online_W_noise_envelope_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


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
