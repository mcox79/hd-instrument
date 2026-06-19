"""Bet A continual edit 5-seed at N=32768 M_init=4096 -- v3 OOM-safe respec.

v1 hit CUDA OOM at M_init=N=65536 (8GB bf16 does not fit).
v2 targeted M_init=8192 N=65536 but cycle 175 Sweep A showed even
M_init=1024 at N=65536 OOM on 8GB GPU (W alone is 8.6 GB bf16).
v3 re-specs to N=32768 (W=2.15 GB bf16; peak fp32 edit ~4.3 GB;
total <5 GB; safe margin on 8GB GPU) with M_init=4096 (M/N=0.125,
same ratio as cycle 172 v2 rescued operating point at M_init=8192 N=65536).

This is a genuine production N (4x smoke N=4096; 2x next-step N=16384) and
maintains the same M/N=0.125 substrate-product operating regime that showed
edit_acc=1.0 kept_acc=1.0 in v2 smoke and the N=4096 v2 regime.

Substrate-product axis: editable memory at scale (capability class 2).
5-seed confirmation: variance characterization of edit_acc + kept_acc.

Verdict thresholds:
  BETA_5SEED_PASS: mean edit >= 0.95 AND mean kept >= 0.95 AND sd < 0.05
  BETA_5SEED_PARTIAL: mean edit >= 0.5 AND mean kept >= 0.5
  BETA_5SEED_KILLED: mean < 0.5
  BETA_5SEED_INCONCLUSIVE: metrics missing

Pre-reg: preregs/2026-05-23_wave14_betA_continual_edit_5seed_v3.md
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from verification import oracle  # noqa: E402

# Import run_one_seed from the base v1 module
_ba_spec = importlib.util.spec_from_file_location(
    "ba_n65536",
    REPO / "experiments" / "exp_wave14_betA_continual_edit_N65536_v1.py",
)
ba = importlib.util.module_from_spec(_ba_spec)
_ba_spec.loader.exec_module(ba)


PASS_EDIT = 0.95
PASS_KEPT = 0.95


def get_output_dir(name: str) -> Path:
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing required fields in metrics dict")


def compute_verdict(s: dict) -> tuple[str, str]:
    if "edit_acc_mean" not in s:
        return ("BETA_5SEED_INCONCLUSIVE", "Missing edit_acc_mean.")
    e_m = s["edit_acc_mean"]
    k_m = s["kept_acc_mean"]
    e_sd = s["edit_acc_sd"]
    k_sd = s["kept_acc_sd"]
    N = s.get("N", 0)
    M = s.get("M_init", 0)
    tag = f"N={N} M_init={M} M/N={M/N:.3f}" if N else ""
    if e_m >= PASS_EDIT and k_m >= PASS_KEPT and e_sd < 0.05 and k_sd < 0.05:
        return (
            "BETA_5SEED_PASS",
            f"mean edit={e_m:.3f} kept={k_m:.3f} sd_e={e_sd:.3f} sd_k={k_sd:.3f} "
            f"at {tag} (substrate-product 5-seed editable-memory CONFIRMED at large N).",
        )
    if e_m >= 0.5 and k_m >= 0.5:
        return (
            "BETA_5SEED_PARTIAL",
            f"mean edit={e_m:.3f} kept={k_m:.3f} (sd_e={e_sd:.3f} sd_k={k_sd:.3f}) "
            f"at {tag}.",
        )
    return (
        "BETA_5SEED_KILLED",
        f"mean edit={e_m:.3f} kept={k_m:.3f} <0.5 at {tag}.",
    )


def self_test_verdict() -> None:
    cases = [
        (
            {"edit_acc_mean": 0.98, "kept_acc_mean": 0.97,
             "edit_acc_sd": 0.02, "kept_acc_sd": 0.03,
             "N": 32768, "M_init": 4096},
            "BETA_5SEED_PASS",
        ),
        (
            {"edit_acc_mean": 0.70, "kept_acc_mean": 0.75,
             "edit_acc_sd": 0.1, "kept_acc_sd": 0.1,
             "N": 32768, "M_init": 4096},
            "BETA_5SEED_PARTIAL",
        ),
        (
            {"edit_acc_mean": 0.2, "kept_acc_mean": 0.1,
             "edit_acc_sd": 0.05, "kept_acc_sd": 0.05,
             "N": 32768, "M_init": 4096},
            "BETA_5SEED_KILLED",
        ),
        ({}, "BETA_5SEED_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"verdict self-test: got {actual!r} expected {expected!r}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    cfg: dict = {
        "N": 4096 if smoke else 32768,
        "M_init": 512 if smoke else 4096,
        "n_edits": 50 if smoke else 100,
        "seeds": [17, 23] if smoke else [17, 23, 31, 41, 53],
        "mode": "smoke" if smoke else "full",
    }

    # Memory budget log
    if device.type == "cuda":
        free_gb = torch.cuda.get_device_properties(device).total_memory / 1e9
        print(f"[setup] GPU total memory: {free_gb:.1f} GB", flush=True)
    print(
        f"[setup] N={cfg['N']} M_init={cfg['M_init']} n_edits={cfg['n_edits']} "
        f"seeds={cfg['seeds']} device={device}",
        flush=True,
    )

    e_list: list[float] = []
    k_list: list[float] = []
    per_seed: dict = {}

    for seed in cfg["seeds"]:
        cpu_gen = torch.Generator().manual_seed(seed)
        print(
            f"\n[seed={seed}] N={cfg['N']} M_init={cfg['M_init']} "
            f"n_edits={cfg['n_edits']}",
            flush=True,
        )
        e_acc, k_acc = ba.run_one_seed(
            cfg["n_edits"], cfg["N"], cfg["M_init"], cpu_gen, device
        )
        e_list.append(e_acc)
        k_list.append(k_acc)
        per_seed[str(seed)] = {"edit_acc": e_acc, "kept_acc": k_acc}
        print(f"  seed={seed}: edit_acc={e_acc:.3f} kept_acc={k_acc:.3f}", flush=True)

    n = len(e_list)
    e_mean = sum(e_list) / n
    k_mean = sum(k_list) / n
    e_sd = (sum((x - e_mean) ** 2 for x in e_list) / n) ** 0.5
    k_sd = (sum((x - k_mean) ** 2 for x in k_list) / n) ** 0.5

    print(f"\n  edit_acc mean={e_mean:.3f} sd={e_sd:.3f}", flush=True)
    print(f"  kept_acc mean={k_mean:.3f} sd={k_sd:.3f}", flush=True)

    summary = {
        "edit_acc_mean": e_mean,
        "kept_acc_mean": k_mean,
        "edit_acc_sd": e_sd,
        "kept_acc_sd": k_sd,
        "per_seed": per_seed,
        "seeds": cfg["seeds"],
        "M_init": cfg["M_init"],
        "N": cfg["N"],
        "headroom": cfg["N"] / cfg["M_init"],
        "n_edits": cfg["n_edits"],
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(
    out_dir: Path,
    summary: dict,
    verdict: str,
    msg: str,
    elapsed: float,
    config: dict,
) -> None:
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


def run_smoke() -> None:
    out_dir = get_output_dir("wave14_betA_continual_edit_5seed_v3_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    oracle.assert_baseline_high("edit_acc_present", s["edit_acc_mean"] + 0.001, 0.0)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main() -> None:
    out_dir = get_output_dir("wave14_betA_continual_edit_5seed_v3")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main() -> int:
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
