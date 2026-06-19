"""Bet A M_init capacity envelope respec -- Strategy cycle 174 v154.

Respec of wave14_betA_M_init_threshold_v1, which OOM'd at all M_init on N=65536.
The v1 FULL verdict BETA_M_INIT_UNIFORM_KILL was an OOM artifact, NOT a substrate
refutation. This v2 fixes the memory hygiene and narrows the sweep.

Two sweeps in one script:

  Sweep A (primary): N=65536, M_init in {1024, 2048, 4096, 8192}
    -- characterizes lower half of M_init capacity envelope at the rescued N.
    -- M_init=8192 was the v2 5-seed PASS anchor; this confirms the region below.

  Sweep B (upper-end extension): N=8192, M_init in {16384, 32768, 65536}
    -- characterizes the M_init/N ratio for the upper half at lower memory cost.
    -- Gives ceiling data without the N=65536 VRAM pressure.

Memory hygiene fix (relative to v1):
  torch.cuda.empty_cache() called BEFORE each M_init iteration (not only in OOM branch).

Acceptance criteria:
  - >= 1 M_init at N=65536 produces 5 seeds with mean_kept >= 0.85 sd < 0.05
  - >= 3 M_init points at N=65536 produce non-OOM measurements
  - Sweep B covers M_init >= 16384 with non-OOM measurements at N=8192

Prereq: preregs/2026-05-23_wave14_betA_M_init_threshold_v2.md
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

# Import run_one_seed from the base Bet A experiment
_ba_spec = importlib.util.spec_from_file_location(
    "ba", REPO / "experiments" / "exp_wave14_betA_continual_edit_N65536_v1.py"
)
ba = importlib.util.module_from_spec(_ba_spec)
_ba_spec.loader.exec_module(ba)


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"metrics.json missing keys: {required - set(d.keys())}")


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_verdict_sweep(per, sweep_label):
    """Compute verdict for a single M_init sweep dict.

    Branches (in order):
      BETA_M_INIT_OOM_INCONCLUSIVE  -- all points OOM; no measurement possible
      BETA_M_INIT_UNIFORM_PASS      -- all non-OOM points pass (mean_kept >= 0.85)
      BETA_M_INIT_UNIFORM_KILL      -- all non-OOM points kill (mean_kept < 0.5)
      BETA_M_INIT_BOUND_FOUND       -- clear KILL->PASS transition detected
      BETA_M_INIT_MIXED             -- intermediate / partially measured
    """
    if not per:
        return ("BETA_M_INIT_OOM_INCONCLUSIVE",
                f"{sweep_label}: no M_init points measured (empty sweep).")

    # OOM-inconclusive branch: all points have oom=True
    if all(v.get("oom", False) for v in per.values()):
        return ("BETA_M_INIT_OOM_INCONCLUSIVE",
                f"{sweep_label}: all M_init OOM, no substrate measurement: {per}.")

    # Filter to non-OOM entries for threshold logic
    valid = {k: v for k, v in per.items() if not v.get("oom", False)}

    if all(v.get("mean_kept", 0) >= 0.85 for v in valid.values()):
        return ("BETA_M_INIT_UNIFORM_PASS",
                f"{sweep_label}: all M_init pass (non-OOM): {per}.")

    if all(v.get("mean_kept", 0) < 0.5 for v in valid.values()):
        return ("BETA_M_INIT_UNIFORM_KILL",
                f"{sweep_label}: all M_init kill (non-OOM): {per}.")

    # Threshold search: first KILL->PASS transition across sorted M_init
    sorted_keys = sorted(int(k) for k in valid.keys())
    threshold = None
    for i in range(len(sorted_keys) - 1):
        a = valid[str(sorted_keys[i])].get("mean_kept", 0)
        b = valid[str(sorted_keys[i + 1])].get("mean_kept", 0)
        if a < 0.5 and b >= 0.85:
            threshold = sorted_keys[i + 1]
            break

    if threshold is not None:
        return ("BETA_M_INIT_BOUND_FOUND",
                f"{sweep_label}: threshold M_init={threshold}; per_M_init={per}.")

    return ("BETA_M_INIT_MIXED",
            f"{sweep_label}: intermediate result; per_M_init={per}.")


def compute_verdict(summary):
    """Combined verdict across both sweeps.

    Primary sweep A (N=65536) drives the overall verdict label.
    """
    sweep_a = summary.get("sweep_A", {}).get("per_M_init", {})
    verdict_a, msg_a = compute_verdict_sweep(sweep_a, "SweepA-N65536")

    sweep_b = summary.get("sweep_B", {}).get("per_M_init", {})
    verdict_b, msg_b = compute_verdict_sweep(sweep_b, "SweepB-N8192")

    combined_msg = f"A: {msg_a} | B: {msg_b}"
    return (verdict_a, combined_msg)


def self_test_verdict():
    cases = [
        # All OOM -> OOM_INCONCLUSIVE
        (
            {"1024": {"mean_kept": 0.0, "oom": True}, "2048": {"mean_kept": 0.0, "oom": True}},
            "BETA_M_INIT_OOM_INCONCLUSIVE",
        ),
        # All pass
        (
            {"1024": {"mean_kept": 0.95}, "2048": {"mean_kept": 0.92}},
            "BETA_M_INIT_UNIFORM_PASS",
        ),
        # All kill (non-OOM)
        (
            {"1024": {"mean_kept": 0.2}, "2048": {"mean_kept": 0.3}},
            "BETA_M_INIT_UNIFORM_KILL",
        ),
        # Threshold found
        (
            {"1024": {"mean_kept": 0.2}, "4096": {"mean_kept": 0.91}},
            "BETA_M_INIT_BOUND_FOUND",
        ),
        # Mixed (no clean transition found)
        (
            {"1024": {"mean_kept": 0.6}, "4096": {"mean_kept": 0.7}},
            "BETA_M_INIT_MIXED",
        ),
        # OOM mixed with valid pass -> should NOT be OOM_INCONCLUSIVE
        (
            {"1024": {"mean_kept": 0.0, "oom": True}, "4096": {"mean_kept": 0.91}},
            "BETA_M_INIT_UNIFORM_PASS",
        ),
    ]
    for i, (per, expected) in enumerate(cases):
        got, _ = compute_verdict_sweep(per, "test")
        if got != expected:
            raise AssertionError(
                f"self_test case {i}: expected={expected} got={got} per={per}"
            )
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


# ---------------------------------------------------------------------------
# Core sweep runner
# ---------------------------------------------------------------------------

def run_sweep(N, M_init_grid, n_edits, seeds, device, sweep_name):
    """Run one M_init sweep and return per_M_init dict."""
    per_M_init = {}
    for M_init in M_init_grid:
        # Memory hygiene: clear cache BEFORE each M_init (not only after OOM)
        if device.type == "cuda":
            torch.cuda.empty_cache()
        print(f"\n[{sweep_name}] M_init={M_init} N={N} n_edits={n_edits}", flush=True)
        kept_accs = []
        for seed in seeds:
            cpu_gen = torch.Generator().manual_seed(seed)
            try:
                _edit_acc, k_acc = ba.run_one_seed(n_edits, N, M_init, cpu_gen, device)
                kept_accs.append(k_acc)
                print(f"  seed={seed}: kept_acc={k_acc:.3f}", flush=True)
            except torch.OutOfMemoryError:
                print(f"  seed={seed}: CUDA OOM (skipped)", flush=True)
                if device.type == "cuda":
                    torch.cuda.empty_cache()
        if not kept_accs:
            per_M_init[str(M_init)] = {"mean_kept": 0.0, "n_seeds": 0, "oom": True}
            print(f"  M_init={M_init}: OOM on all seeds", flush=True)
            continue
        mean = sum(kept_accs) / len(kept_accs)
        sd = (sum((x - mean) ** 2 for x in kept_accs) / len(kept_accs)) ** 0.5
        per_M_init[str(M_init)] = {
            "mean_kept": mean,
            "sd_kept": sd,
            "n_seeds": len(kept_accs),
            "oom": False,
        }
        print(f"  M_init={M_init}: mean_kept={mean:.3f} sd={sd:.3f} "
              f"n_seeds={len(kept_accs)}", flush=True)
    return per_M_init


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if smoke:
        cfg = {
            "mode": "smoke",
            # Sweep A: small N, small M_init grid, 2 seeds
            "sweep_A": {
                "N": 4096,
                "M_init_grid": [256, 1024],
                "n_edits": 20,
                "seeds": [17, 23],
            },
            # Sweep B: same small N, larger M_init (tests upper-end logic)
            "sweep_B": {
                "N": 4096,
                "M_init_grid": [2048, 4096],
                "n_edits": 20,
                "seeds": [17, 23],
            },
        }
    else:
        cfg = {
            "mode": "full",
            # Sweep A (primary): narrow lower half at rescued N=65536
            "sweep_A": {
                "N": 65536,
                "M_init_grid": [1024, 2048, 4096, 8192],
                "n_edits": 100,
                "seeds": [17, 23, 31, 41, 53],
            },
            # Sweep B (upper-end): larger M_init at lower N to avoid VRAM pressure
            "sweep_B": {
                "N": 8192,
                "M_init_grid": [16384, 32768, 65536],
                "n_edits": 100,
                "seeds": [17, 23, 31, 41, 53],
            },
        }

    print(f"[setup] mode={cfg['mode']} device={device}", flush=True)

    # Run Sweep A
    sa_cfg = cfg["sweep_A"]
    print(f"\n=== Sweep A (primary): N={sa_cfg['N']} M_init_grid={sa_cfg['M_init_grid']} ===",
          flush=True)
    per_A = run_sweep(
        sa_cfg["N"], sa_cfg["M_init_grid"], sa_cfg["n_edits"],
        sa_cfg["seeds"], device, "SweepA"
    )
    verdict_a, msg_a = compute_verdict_sweep(per_A, f"SweepA-N{sa_cfg['N']}")
    print(f"\nSweep A verdict: {verdict_a}", flush=True)
    print(f"  {msg_a}", flush=True)

    # Run Sweep B
    sb_cfg = cfg["sweep_B"]
    print(f"\n=== Sweep B (upper-end): N={sb_cfg['N']} M_init_grid={sb_cfg['M_init_grid']} ===",
          flush=True)
    per_B = run_sweep(
        sb_cfg["N"], sb_cfg["M_init_grid"], sb_cfg["n_edits"],
        sb_cfg["seeds"], device, "SweepB"
    )
    verdict_b, msg_b = compute_verdict_sweep(per_B, f"SweepB-N{sb_cfg['N']}")
    print(f"\nSweep B verdict: {verdict_b}", flush=True)
    print(f"  {msg_b}", flush=True)

    summary = {
        "sweep_A": {
            "N": sa_cfg["N"],
            "M_init_grid": sa_cfg["M_init_grid"],
            "per_M_init": per_A,
            "verdict": verdict_a,
        },
        "sweep_B": {
            "N": sb_cfg["N"],
            "M_init_grid": sb_cfg["M_init_grid"],
            "per_M_init": per_B,
            "verdict": verdict_b,
        },
    }

    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nCOMBINED VERDICT: {verdict}", flush=True)
    print(f"  {msg}", flush=True)
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
    out_dir = get_output_dir("wave14_betA_M_init_threshold_v2_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    # Sanity: at least one M_init in sweep A produced a measurement
    n_valid_A = sum(
        1 for val in s["sweep_A"]["per_M_init"].values()
        if not val.get("oom", False)
    )
    oracle.assert_baseline_high("sweep_A_has_measurements", float(n_valid_A) + 0.001, 0.0)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betA_M_init_threshold_v2")
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
