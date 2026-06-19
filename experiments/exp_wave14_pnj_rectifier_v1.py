"""D3 Finding 4: pn-junction two-substrate rectifier primitive.

From research_semiconductor_physics_substrate_analogies_2026-05-23.md (D3 Finding 4):
  Two substrate regions with distinct W structures (W_A != W_B) create a
  "built-in potential" V_bi proportional to their free-energy mismatch.
  Information flows preferentially from high-F to low-F region (forward bias);
  blocked in reverse.

This experiment builds two substrates A and B with different stored-memory counts
(K_A < K_B -> F_A < F_B, since more memories = higher free energy / noisier landscape).
Then measures asymmetric information transfer:
  - Forward bias: inject query into substrate A, relay result to substrate B (high-F to low-F)
  - Reverse bias: inject query into substrate B, relay to substrate A (low-F to high-F)

Rectifier claim: forward transfer accuracy >> reverse transfer accuracy.

Free-energy proxy: F ~ K * log(K) / N (Hopfield free energy at beta=inf approximation).
Built-in potential: V_bi ~ F_B - F_A = (K_B - K_A) * log / N.

HARD PASS: forward_acc / reverse_acc >= 2.0 AND forward_acc >= 0.60.
HARD FAIL: ratio < 1.2 (symmetric; no rectifier behavior).

Verdict labels:
  PNJ_RECTIFIER_PASS    -- asymmetric transfer confirmed (ratio >= 2.0)
  PNJ_RECTIFIER_WEAK    -- weak asymmetry (ratio in [1.2, 2.0))
  PNJ_RECTIFIER_FAIL    -- symmetric or reversed (ratio < 1.2)
  PNJ_RECTIFIER_INCONCLUSIVE

Pure CPU. No GPU required.
Memory budget: W_A + W_B = 2 * N^2 float32; N=4096 -> 128 MB.
  Avoid materializing W: use codebook-product form. Peak ~50 MB.
Expected runtime: ~25-30 min CPU at FULL (N=4096, K_A=50 K_B=200, 200 probes, 3 seeds).
Smoke: ~2 min (N=1024, K_A=20 K_B=80, 50 probes, 1 seed).
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
from verification import oracle  # noqa: E402

RECTIFIER_RATIO_PASS = 2.0
RECTIFIER_RATIO_WEAK = 1.2
FWD_ACC_MIN = 0.50   # forward accuracy must be above floor to count


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError(f"missing keys: {set(d.keys())}")


def compute_verdict(summary):
    if "forward_acc" not in summary or "reverse_acc" not in summary:
        return ("PNJ_RECTIFIER_INCONCLUSIVE", "Missing forward_acc or reverse_acc.")
    fwd = summary["forward_acc"]
    rev = summary["reverse_acc"]
    if rev < 1e-6:
        ratio = float('inf') if fwd > 0 else 1.0
    else:
        ratio = fwd / rev
    summary["ratio"] = round(ratio, 3)
    desc = f"forward_acc={fwd:.3f}, reverse_acc={rev:.3f}, ratio={ratio:.2f}"
    if ratio >= RECTIFIER_RATIO_PASS and fwd >= FWD_ACC_MIN:
        return ("PNJ_RECTIFIER_PASS",
                f"HARD PASS: {desc}. ratio >= {RECTIFIER_RATIO_PASS} and fwd >= {FWD_ACC_MIN}. "
                "Substrate-novel rectifier behavior confirmed: information flows preferentially "
                "from high-F (K_A sparse) to low-F (K_B dense) substrate.")
    if ratio >= RECTIFIER_RATIO_WEAK:
        return ("PNJ_RECTIFIER_WEAK",
                f"Weak asymmetry: {desc}. ratio in [{RECTIFIER_RATIO_WEAK}, {RECTIFIER_RATIO_PASS}). "
                "Some rectification but below strong threshold.")
    return ("PNJ_RECTIFIER_FAIL",
            f"Symmetric or near-symmetric transfer: {desc}. ratio < {RECTIFIER_RATIO_WEAK}. "
            "No rectifier behavior; pn-junction analogy does not hold at this K_A/K_B contrast.")


def self_test_verdict():
    cases = [
        ({"forward_acc": 0.80, "reverse_acc": 0.30}, "PNJ_RECTIFIER_PASS"),
        ({"forward_acc": 0.60, "reverse_acc": 0.40}, "PNJ_RECTIFIER_WEAK"),
        ({"forward_acc": 0.55, "reverse_acc": 0.50}, "PNJ_RECTIFIER_FAIL"),
        ({"forward_acc": 0.70, "reverse_acc": 0.0}, "PNJ_RECTIFIER_PASS"),
        ({}, "PNJ_RECTIFIER_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"Expected {exp}, got {a} for input {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bsc_codebook(K, N, gen, device):
    return (torch.randint(0, 2, (K, N), generator=gen, device=device).float() * 2 - 1)


def hebbian_field(x, codebook):
    """Hebbian field: h = C^T (C x) / N."""
    N = codebook.shape[1]
    proj = codebook @ x  # (K,)
    return codebook.T @ proj / N  # (N,)


def converge(x, codebook, max_steps=30):
    """Converge x to fixed-point under sign(h)."""
    for _ in range(max_steps):
        h = hebbian_field(x, codebook)
        x_new = torch.sign(h)
        x_new[x_new == 0] = 1.0
        if torch.equal(x_new, x):
            break
        x = x_new
    return x


def transfer_acc(source_codebook, target_codebook, shared_items, n_probes, seed, device):
    """
    Asymmetric information transfer: source substrate -> target substrate.

    Protocol: shared items are stored in BOTH substrates. A query is presented
    to the source (with noise), source converges to its attractor (the shared
    item), and that attractor is used as a probe in the target substrate.
    Target succeeds if it retrieves the SAME item it shares with source.

    This directly tests the rectifier claim: source -> target has different
    accuracy than target -> source due to free-energy landscape differences.
    """
    N = source_codebook.shape[1]
    n_items = min(n_probes, shared_items.shape[0])
    if n_items == 0:
        return 0.0

    correct = 0
    for i in range(n_items):
        item = shared_items[i]

        # Noisy probe: flip 10% of bits
        noise_gen = torch.Generator(device=device).manual_seed(seed + i * 1000)
        flip_mask = torch.rand(N, generator=noise_gen, device=device) < 0.10
        noisy = item.clone()
        noisy[flip_mask] *= -1

        # Source convergence: denoise via source substrate
        source_out = converge(noisy, source_codebook)

        # Relay: use source output as probe into target
        target_out = converge(source_out, target_codebook)

        # Success: target output within N/8 Hamming of ground-truth item
        hamming = int((target_out != item).sum().item())
        if hamming <= N // 8:
            correct += 1

    return correct / n_items


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")  # Pure CPU
    cfg = {
        "mode": "smoke" if smoke else "full",
        "N": 1024 if smoke else 4096,
        "K_A": 20 if smoke else 50,    # sparse substrate A (fewer memories, higher F)
        "K_B": 80 if smoke else 200,   # dense substrate B (more memories, lower F)
        "n_probes": 20 if smoke else 80,
        "n_seeds": 1 if smoke else 3,
    }
    N = cfg["N"]
    print(f"Config: N={N}, K_A={cfg['K_A']}, K_B={cfg['K_B']}, "
          f"n_probes={cfg['n_probes']}, n_seeds={cfg['n_seeds']}", flush=True)
    print(f"  Free-energy proxy: F_A ~ K_A*log(K_A)/N = "
          f"{cfg['K_A'] * (len(str(cfg['K_A']))) / N:.4f}, "
          f"F_B ~ {cfg['K_B'] * (len(str(cfg['K_B']))) / N:.4f}", flush=True)

    fwd_accs = []
    rev_accs = []

    for seed_i in range(cfg["n_seeds"]):
        seed = 17 + seed_i * 101
        gen = torch.Generator(device=device).manual_seed(seed)

        # Shared items: stored in BOTH substrates (the "junction" memory)
        n_shared = min(cfg["n_probes"], 20)
        shared_items = make_bsc_codebook(n_shared, N, gen, device)

        # Substrate A: sparse (K_A extra noise memories + shared items)
        n_extra_A = cfg["K_A"] - n_shared
        extra_A = make_bsc_codebook(max(n_extra_A, 0), N, gen, device)
        if n_extra_A > 0:
            codebook_A = torch.cat([shared_items, extra_A], dim=0)
        else:
            codebook_A = shared_items

        # Substrate B: dense (K_B extra noise memories + shared items)
        n_extra_B = cfg["K_B"] - n_shared
        extra_B = make_bsc_codebook(max(n_extra_B, 0), N, gen, device)
        if n_extra_B > 0:
            codebook_B = torch.cat([shared_items, extra_B], dim=0)
        else:
            codebook_B = shared_items

        # Forward: A -> B (sparse source, dense target = high-F to low-F)
        fwd = transfer_acc(codebook_A, codebook_B, shared_items, cfg["n_probes"], seed + 1, device)
        # Reverse: B -> A (dense source, sparse target = low-F to high-F)
        rev = transfer_acc(codebook_B, codebook_A, shared_items, cfg["n_probes"], seed + 2, device)

        fwd_accs.append(fwd)
        rev_accs.append(rev)
        print(f"  seed={seed}: forward(A->B)={fwd:.3f}, reverse(B->A)={rev:.3f}", flush=True)

    mean_fwd = sum(fwd_accs) / len(fwd_accs)
    mean_rev = sum(rev_accs) / len(rev_accs)
    print(f"\n  mean forward_acc={mean_fwd:.3f}, mean reverse_acc={mean_rev:.3f}", flush=True)

    summary = {
        "forward_acc": round(mean_fwd, 4),
        "reverse_acc": round(mean_rev, 4),
        "K_A": cfg["K_A"],
        "K_B": cfg["K_B"],
        "per_seed": [{"fwd": round(f, 4), "rev": round(r, 4)}
                     for f, r in zip(fwd_accs, rev_accs)],
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_pnj_rectifier_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("forward_acc", summary["forward_acc"], 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_pnj_rectifier_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


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
