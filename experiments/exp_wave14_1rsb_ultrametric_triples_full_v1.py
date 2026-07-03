"""Pred-3 (1-RSB diagnostic): Ultrametric inequality on retained-task triples -- FULL config.

Pre-registered open item from v199 cap_map: ultrametric_triples FULL at N=2048, 12 seeds.
The smoke version (N=512, 3 seeds) returned trivially CONFIRMED because at N=512 all W-vector
overlaps are near-zero (q_EA~0) and any 3 near-zero overlaps trivially satisfy the isosceles
condition. FULL at N=2048 with 12 seeds is the discriminating run.

Uses GPU for Phase-A/B/C/D training (same 4-stage M1 hierreplay as existing ultrametric_triples_v1
but with device=cuda). Overlap computation stays on CPU (12x12 overlap matrix is trivial).

Design change from v1 smoke: runs 4-stage M1 hierreplay at N=2048 (was N=512 smoke).
The W vectors from 12 seeds are compared pairwise. If 1-RSB basin trapping occurs,
W-vectors from different seeds should share a common basin (q_EA >> 0), making overlaps
non-trivial and the ultrametric test meaningful.

Pre-reg (unchanged from v1):
    HARD-PASS: ultrametric fraction >= 0.50 -> 1-RSB ultrametric inequality SUPPORTED.
    HARD-FAIL: ultrametric fraction <= 0.36 (near 0.33 random baseline).
    MIDDLE: fraction in (0.36, 0.50).

Additional diagnostic: q_EA_estimate = mean pairwise overlap.
If q_EA << 0.01 -> overlaps still trivial (UV-problem persists at N=2048);
log this as diagnostic note, not a closure.

Queue: overnight_queue (GPU, 4-stage M1 hierreplay x12 seeds at N=2048 -> ~1-2h).
ETA: ~1-2h on GPU.
Pre-reg: preregs/2026-05-24_wave14_1rsb_ultrametric_triples_full_v1.md

Per [[feedback-no-experiment-design-in-prompts]]: all parameters by exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL/MIDDLE pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands registered BEFORE running.
Per [[feedback-ascii-only-in-scripts]]: stdout.reconfigure at top.
Per [[feedback-strategy-spec-formula-selftests]]: 4 self-test cells.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, importlib.util, json, math, os, random, shutil, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

# Load hierreplay infrastructure (M1 4-stage)
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)
base = m1.base
v1 = m1.v1
pa = m1.pa

# Load pq_retained helper (provides run_4stage_m1_get_W)
_pq_path = REPO / "experiments" / "exp_wave14_1rsb_pq_retained_v1.py"
_pq_spec = importlib.util.spec_from_file_location("pq_ret", _pq_path)
pq_ret = importlib.util.module_from_spec(_pq_spec)
_pq_spec.loader.exec_module(pq_ret)

# ───── design parameters (exp_dev autonomy) ─────
N_FULL = 2048
N_SMOKE = 512
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 100_000
BYTES_SMOKE = 3_000
SEEDS_FULL = list(range(12))   # 12 seeds -> C(12,3) = 220 possible triples
SEEDS_SMOKE = [7, 17, 23]
N_TRIPLES_FULL = 1000
N_TRIPLES_SMOKE = 50
EPS_ULTRAMETRIC = 0.10   # tolerance for isosceles condition (pre-registered in v1)

# Pre-registered thresholds (same as v1)
PASS_ULTRA_FRAC = 0.50
FAIL_ULTRA_FRAC = 0.36


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def ultrametric_fraction_W(W_stack: torch.Tensor, n_triples: int, eps: float, rng_seed: int):
    """Fraction of triples satisfying ultrametric inequality on W-overlaps.
    Ultrametric: for (i,j,k), min of {q_ij, q_ik, q_jk} equals second-smallest within eps.
    """
    S = W_stack.shape[0]
    N2 = W_stack.shape[1]
    Q_tensor = W_stack @ W_stack.T / N2   # (S x S)
    Q = Q_tensor.tolist()

    rng = random.Random(rng_seed)
    sat = 0
    isosceles_gaps = []
    for _ in range(n_triples):
        i, j, k = rng.sample(range(S), 3)
        q_ij = Q[i][j]
        q_ik = Q[i][k]
        q_jk = Q[j][k]
        vals = sorted([q_ij, q_ik, q_jk])  # ascending
        # Ultrametric (isosceles): two smallest equal within eps
        gap = abs(vals[1] - vals[0])
        isosceles_gaps.append(gap)
        if gap <= eps:
            sat += 1
    frac = sat / n_triples
    mean_gap = sum(isosceles_gaps) / len(isosceles_gaps)
    return frac, mean_gap


def compute_verdict(summary: dict):
    ultra_frac = summary.get("ultrametric_fraction", 0.0)
    mean_gap = summary.get("mean_isosceles_gap", 1.0)
    q_ea = summary.get("mean_overlap_q", 0.0)

    if ultra_frac >= PASS_ULTRA_FRAC:
        return (
            "ULTRAMETRIC_1RSB_CONFIRMED",
            f"Ultrametric fraction={ultra_frac:.3f} >= {PASS_ULTRA_FRAC}. "
            f"mean_isosceles_gap={mean_gap:.4f} q_EA={q_ea:.6f}. "
            f"Retained-task W triples satisfy isosceles condition >> random baseline. "
            f"1-RSB ultrametric inequality SUPPORTED at N=2048 12-seed."
        )
    if ultra_frac <= FAIL_ULTRA_FRAC:
        return (
            "ULTRAMETRIC_RS_FLAT",
            f"Ultrametric fraction={ultra_frac:.3f} <= {FAIL_ULTRA_FRAC} "
            f"(near 0.33 random baseline). mean_gap={mean_gap:.4f} q_EA={q_ea:.6f}. "
            f"W triples do NOT satisfy ultrametric; 1-RSB NOT supported at ultrametric axis."
        )
    return (
        "ULTRAMETRIC_MIDDLE",
        f"Intermediate ultrametric fraction={ultra_frac:.3f} in ({FAIL_ULTRA_FRAC},{PASS_ULTRA_FRAC}). "
        f"mean_gap={mean_gap:.4f} q_EA={q_ea:.6f}. Inconclusive 1-RSB vs RS."
    )


def self_test():
    """4 self-test cells verifying verdict logic."""
    errors = []

    # Cell 1: HARD-PASS condition
    s = {"ultrametric_fraction": 0.55, "mean_isosceles_gap": 0.02, "mean_overlap_q": 0.05}
    v, _ = compute_verdict(s)
    if v != "ULTRAMETRIC_1RSB_CONFIRMED":
        errors.append(f"Cell 1: expected CONFIRMED, got {v}")

    # Cell 2: HARD-FAIL condition
    s = {"ultrametric_fraction": 0.34, "mean_isosceles_gap": 0.15, "mean_overlap_q": 0.001}
    v, _ = compute_verdict(s)
    if v != "ULTRAMETRIC_RS_FLAT":
        errors.append(f"Cell 2: expected RS_FLAT, got {v}")

    # Cell 3: MIDDLE condition
    s = {"ultrametric_fraction": 0.43, "mean_isosceles_gap": 0.08, "mean_overlap_q": 0.01}
    v, _ = compute_verdict(s)
    if v != "ULTRAMETRIC_MIDDLE":
        errors.append(f"Cell 3: expected MIDDLE, got {v}")

    # Cell 4: ultrametric_fraction_W correctness on trivial case
    # If all W-vectors identical, all pairwise overlaps equal => every triple is isosceles
    S = 4
    N2 = 10
    W_ident = torch.ones(S, N2) / math.sqrt(N2)  # all rows identical
    frac, gap = ultrametric_fraction_W(W_ident, n_triples=100, eps=1e-6, rng_seed=42)
    if frac < 0.99:  # should be 1.0 (all gaps=0)
        errors.append(f"Cell 4: identical W -> frac should be ~1.0, got {frac:.3f}")

    if errors:
        print(f"[SELF-TEST FAIL] {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("[SELF-TEST PASS] 4/4 cells pass")
        sys.exit(0)


def run(smoke: bool) -> tuple:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    t0 = time.monotonic()
    print(f"[ultrametric-triples-full] device={device} smoke={smoke}", flush=True)

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "n_triples": N_TRIPLES_SMOKE if smoke else N_TRIPLES_FULL,
        "eps_ultrametric": EPS_ULTRAMETRIC,
        "pass_frac": PASS_ULTRA_FRAC,
        "fail_frac": FAIL_ULTRA_FRAC,
    }
    print(f"[config] N={config['N']} seeds={len(config['seeds'])} triples={config['n_triples']}", flush=True)

    W_flat_list = []
    for seed in config["seeds"]:
        print(f"  running M1 4-stage seed={seed}...", flush=True)
        W_flat = pq_ret.run_4stage_m1_get_W(seed, config, device)
        W_flat_list.append(W_flat.cpu())  # collect on CPU for overlap computation
        norm = float(W_flat.norm())
        print(f"  seed={seed}: norm={norm:.3f}", flush=True)

    W_stack = torch.stack(W_flat_list, dim=0)  # (S, N^2) on CPU
    S = W_stack.shape[0]
    print(f"  W_stack shape={W_stack.shape} S={S}", flush=True)

    ultra_frac, mean_gap = ultrametric_fraction_W(
        W_stack, config["n_triples"], EPS_ULTRAMETRIC, rng_seed=2026
    )
    print(f"  ultrametric_fraction={ultra_frac:.4f} mean_isosceles_gap={mean_gap:.4f}", flush=True)

    # Pairwise overlap statistics
    N2 = W_stack.shape[1]
    Q = W_stack @ W_stack.T / N2
    triu_mask = torch.triu(torch.ones(S, S, dtype=torch.bool), diagonal=1)
    overlaps = Q[triu_mask]
    mean_q = float(overlaps.mean())
    std_q = float(overlaps.std()) if overlaps.shape[0] > 1 else 0.0

    # Diagnostic note for UV-problem (trivial overlaps)
    uv_note = ""
    if abs(mean_q) < 0.01:
        uv_note = (
            f"DIAGNOSTIC: mean_q={mean_q:.6f} near zero -- W-vectors from different seeds "
            f"are nearly orthogonal (UV-problem persists at N={config['N']}). "
            f"Ultrametric test is on near-zero overlaps; trivial satisfaction expected. "
            f"Pool-level RSB (wave14e2_parisi_ultrametricity) unaffected."
        )

    summary = {
        "ultrametric_fraction": ultra_frac,
        "mean_isosceles_gap": mean_gap,
        "n_triples_tested": config["n_triples"],
        "n_seeds": S,
        "mean_overlap_q": mean_q,
        "std_overlap_q": std_q,
        "eps_used": EPS_ULTRAMETRIC,
        "uv_diagnostic": uv_note,
    }
    verdict, msg = compute_verdict(summary)
    if uv_note:
        msg = msg + " | " + uv_note
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    out_dir = get_output_dir("wave14_1rsb_ultrametric_triples_full_v1")
    summary, verdict, msg, elapsed, config = run(smoke=args.smoke)
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2))
    shutil.move(str(tmp), out_dir / "metrics.json")
    oracle.assert_baseline_high("ultrametric_n_triples", float(summary.get("n_triples_tested", 0)), 1.0)
    print(f"[done] elapsed={elapsed:.1f}s verdict={verdict}", flush=True)


if __name__ == "__main__":
    main()
