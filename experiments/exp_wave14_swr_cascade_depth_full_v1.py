"""SWR Pred-1 + PT C2: Full cascade-depth sweep N in {1,2,3,4,5,6}.

Prior cascade_depth_v1 (just completed) swept depths 2-4 only, landed MIDDLE
(max_delta=0.058, non-monotone). This anchor extends to the full range N={1..6}
required by SWR Pred-1 (biology discrete knee at N=3) and PT-cascade C2
(sqrt(K_eff) range for the substrate).

Key competing hypotheses (pre-registered):
- H_biology: discrete knee at N=3 (N=3 within 5% of N=6; N=2 >12% behind N=3).
- H_physics: smooth monotone scaling (max_delta < 0.10; var < 0.003).
- H_nonmonotone: inversion pattern (higher depth outperforms lower at some point).
- H_null: depth has no effect (all deltas < 0.05).

Reuses exp_wave14_k2_m1_hierreplay_v1 infrastructure (run_chain_depth +
thin_pool_to_chunks). Adds depth=1 (flat no-cascade single-pool baseline) and
depths 5-6 on top of what cascade_depth_v1 already tested.

Per [[feedback-no-experiment-design-in-prompts]]: all parameters exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS / HARD-FAIL bands pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands committed before ship.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.
Per [[feedback-strategy-spec-formula-selftests]]: self-test cells run before smoke.
Per [[feedback-composition-classification]]: SCORE-level composition.

Pre-reg: prereqs/2026-05-24_wave14_swr_cascade_depth_full_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, importlib.util, json, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from verification import oracle  # noqa: E402

# Load M1 hierreplay for thin_pool_to_chunks
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)

# Load cascade_depth_v1 for run_chain_depth (depths 2+)
_cd_path = REPO / "experiments" / "exp_wave14_1rsb_cascade_depth_v1.py"
_cd_spec = importlib.util.spec_from_file_location("cd", _cd_path)
cd = importlib.util.module_from_spec(_cd_spec)
_cd_spec.loader.exec_module(cd)

base = m1.base
v1 = m1.v1
pa = m1.pa

# ---- design parameters (exp_dev autonomy) ----
N_FULL = 4096
N_SMOKE = 512
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 200_000
BYTES_SMOKE = 4_000
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
CHUNK_FRACTION = 0.5
DEPTHS_TO_TEST_FULL = [1, 2, 3, 4, 5, 6]  # full SWR Pred-1 range
DEPTHS_TO_TEST_SMOKE = [1, 2, 3]           # smoke covers 3 depths to exercise all code paths

# Pre-registered threshold bands (biology knee test)
BIOLOGY_KNEE_JUMP = 0.12   # N=3 must be >= N=2 + this to confirm biology knee
BIOLOGY_KNEE_SAT = 0.05    # N=6 must be <= N=3 + this to confirm saturation
SMOOTH_MAX_DELTA = 0.10    # max consecutive delta for physics-smooth verdict
SMOOTH_VAR = 0.003         # variance of per-step deltas for physics-smooth verdict
NONMONOTONE_INVERT = 0.05  # N+(k+1) beats N+k by this much = inversion evidence


def get_output_dir(name=None):
    n = name or os.environ.get("HDLAB_EXP_NAME", "wave14_swr_cascade_depth_full_v1")
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def run_depth_1(seed, config, device):
    """Depth=1: single-pool flat replay (no cascade, standard betB compound)."""
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    smoke = (config["mode"] == "smoke")

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    tr_a, te_a = split80(corpus_a)
    tr_b, te_b = split80(corpus_b)
    tr_c, te_c = split80(corpus_c)

    tr_a_idx, tr_a_tgt = base.bytes_to_idx_tensors(tr_a, device)
    te_a_idx, te_a_tgt = base.bytes_to_idx_tensors(te_a, device)
    tr_b_idx, tr_b_tgt = base.bytes_to_idx_tensors(tr_b, device)
    tr_c_idx, tr_c_tgt = base.bytes_to_idx_tensors(tr_c, device)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)

    # Phase A (no replay)
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        tr_a_idx, tr_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)
    bpc_A_baseline = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                        byte_atoms, pos_atoms,
                                        te_a_idx, te_a_tgt, batch_size, device)

    # Phase B: replay A as flat pool (single timescale, no cascade)
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, tr_b_idx, tr_b_tgt,
        pool_A_v, pool_A_l, pool_A_u, n_epochs, batch_size, device)

    # Phase C: replay A+B flat
    comb_v = torch.cat([pool_A_v[:pool_A_u], pool_AB_v[:pool_AB_u]], dim=0)
    comb_l = torch.cat([pool_A_l[:pool_A_u], pool_AB_l[:pool_AB_u]], dim=0)
    comb_u = comb_v.shape[0]
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, tr_c_idx, tr_c_tgt,
        comb_v, comb_l, comb_u, n_epochs, batch_size, device)

    bpc_A_after = base.evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                     byte_atoms, pos_atoms,
                                     te_a_idx, te_a_tgt, batch_size, device)
    ret_A = min(bpc_A_baseline / max(bpc_A_after, 1e-6), 1.0)
    return ret_A, bpc_A_baseline, bpc_A_after


def run_depth_n(depth, seed, config, device):
    """Depth >= 2: cascade replay using cascade_depth_v1 run_chain_depth."""
    return cd.run_chain_depth(depth, seed, config, device)


def compute_verdict(summary):
    by_depth = summary.get("by_depth", {})
    if not by_depth:
        return ("SWR_DEPTH_INCONCLUSIVE", "No by_depth data.")
    depths = sorted(int(d) for d in by_depth.keys())
    if len(depths) < 4:
        return ("SWR_DEPTH_INCONCLUSIVE",
                f"Need >= 4 depths to classify; got {depths}.")

    mean_ret = {d: by_depth[str(d)]["mean_retA"] for d in depths}

    # Step deltas (positive = drop as depth increases)
    step_deltas = []
    for i in range(1, len(depths)):
        d_prev, d_curr = depths[i - 1], depths[i]
        step_deltas.append(mean_ret[d_prev] - mean_ret[d_curr])

    max_delta = max(abs(d) for d in step_deltas) if step_deltas else 0.0
    n_steps = len(step_deltas)
    mean_d = sum(step_deltas) / n_steps if n_steps else 0.0
    var_delta = sum((d - mean_d) ** 2 for d in step_deltas) / max(n_steps, 1)

    depth_str = ", ".join(f"N={d}:retA={mean_ret[d]:.3f}" for d in depths)
    delta_str = ", ".join(f"{d:.3f}" for d in step_deltas)

    # Check biology knee (N=3 jump + post-N=3 saturation)
    biology_verdict = None
    if 2 in mean_ret and 3 in mean_ret and 6 in mean_ret:
        n3_jump = mean_ret[2] - mean_ret[3]   # positive = drop going 2->3 (BAD: we want improvement)
        # NOTE: higher retA = better; we want N=3 to IMPROVE over N=2
        # Reframe: improvement means retA(3) > retA(2), i.e., n3_jump < 0
        n3_improvement = mean_ret[3] - mean_ret[2]
        n6_vs_n3 = mean_ret[6] - mean_ret[3]  # positive = N=6 better than N=3
        if n3_improvement >= BIOLOGY_KNEE_JUMP and abs(n6_vs_n3) <= BIOLOGY_KNEE_SAT:
            biology_verdict = (
                "SWR_DEPTH_BIOLOGY_KNEE",
                f"Biology discrete knee confirmed: N=3 improves over N=2 by "
                f"{n3_improvement:.3f}>={BIOLOGY_KNEE_JUMP}, N=6 within "
                f"{abs(n6_vs_n3):.3f}<={BIOLOGY_KNEE_SAT} of N=3. "
                f"Profile: {depth_str}. Deltas: {delta_str}. "
                f"H_biology SUPPORTED; substrate follows discrete cascade-depth regime."
            )

    # Biology knee check first: it's a specific inversion pattern (N=3 jumps up from N=2
    # then saturates), so must be classified before the generic inversion check.
    if biology_verdict:
        return biology_verdict

    # Check non-monotone inversion (excluding the biology-knee case already handled above)
    n_inversions = sum(1 for d in step_deltas if d < -NONMONOTONE_INVERT)
    if n_inversions >= 1:
        return ("SWR_DEPTH_NONMONOTONE",
                f"Non-monotone: {n_inversions} inversions where deeper beats shallower "
                f"by >{NONMONOTONE_INVERT}. Profile: {depth_str}. Deltas: {delta_str}. "
                f"Spacing or other lever dominates over depth per PT framing.")

    # Check null effect (subset of smooth; check before smooth to give specific label)
    if max_delta < 0.05:
        return ("SWR_DEPTH_NULL",
                f"Null effect: max_delta={max_delta:.3f}<0.05 across all depth steps. "
                f"Profile: {depth_str}. Cascade depth not the active mechanism.")

    # Check physics-smooth (monotone, uniform deltas, no knee)
    if max_delta < SMOOTH_MAX_DELTA and var_delta < SMOOTH_VAR:
        return ("SWR_DEPTH_PHYSICS_SMOOTH",
                f"Smooth monotone scaling: max_delta={max_delta:.3f}<{SMOOTH_MAX_DELTA} "
                f"var_delta={var_delta:.4f}<{SMOOTH_VAR}. Profile: {depth_str}. "
                f"Deltas: {delta_str}. H_physics wins; no discrete knee.")

    return ("SWR_DEPTH_MIDDLE",
            f"Intermediate: max_delta={max_delta:.3f} var_delta={var_delta:.4f} "
            f"n_inversions={n_inversions}. Profile: {depth_str}. Deltas: {delta_str}.")


def self_test_verdict():
    """Self-test: (input -> expected verdict) pairs per feedback-strategy-spec-formula-selftests."""
    def mk(depth_ret_pairs):
        return {"by_depth": {str(d): {"mean_retA": r} for d, r in depth_ret_pairs}}

    cases = [
        # Biology knee: N=3 jumps +0.13 over N=2, N=6 within 0.03 of N=3
        (mk([(1, 0.95), (2, 0.80), (3, 0.93), (4, 0.94), (5, 0.93), (6, 0.92)]),
         "SWR_DEPTH_BIOLOGY_KNEE"),
        # Physics smooth: uniform monotone drops, each ~0.07 (> null threshold 0.05, < smooth threshold 0.10)
        # step_deltas = [0.07, 0.07, 0.07, 0.07, 0.07], var~0
        (mk([(1, 0.95), (2, 0.88), (3, 0.81), (4, 0.74), (5, 0.67), (6, 0.60)]),
         "SWR_DEPTH_PHYSICS_SMOOTH"),
        # Non-monotone inversion: depth=4 beats depth=3 by 0.08
        (mk([(1, 0.90), (2, 0.88), (3, 0.82), (4, 0.92), (5, 0.89), (6, 0.86)]),
         "SWR_DEPTH_NONMONOTONE"),
        # Null: all flat
        (mk([(1, 0.90), (2, 0.90), (3, 0.89), (4, 0.90), (5, 0.90), (6, 0.90)]),
         "SWR_DEPTH_NULL"),
        # Middle: max_delta=0.11 (> smooth threshold 0.10) but no biology knee, no inversion
        # step_deltas: 0.05, 0.11, 0.02, 0.02, 0.02 -> max_delta=0.11 > 0.10
        (mk([(1, 0.95), (2, 0.90), (3, 0.79), (4, 0.77), (5, 0.75), (6, 0.73)]),
         "SWR_DEPTH_MIDDLE"),
        # Inconclusive: no data
        ({}, "SWR_DEPTH_INCONCLUSIVE"),
        # Too few depths
        (mk([(1, 0.95), (2, 0.90)]), "SWR_DEPTH_INCONCLUSIVE"),
    ]
    for summary, expected in cases:
        actual, msg = compute_verdict(summary)
        if actual != expected:
            raise AssertionError(
                f"self_test FAIL: got {actual!r} expected {expected!r}; msg={msg!r}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run(smoke=False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    t0 = time.monotonic()
    print(f"[swr-cascade-depth] device={device} smoke={smoke}", flush=True)

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "depths": DEPTHS_TO_TEST_SMOKE if smoke else DEPTHS_TO_TEST_FULL,
        "chunk_fraction": CHUNK_FRACTION,
        "biology_knee_jump": BIOLOGY_KNEE_JUMP,
        "smooth_max_delta": SMOOTH_MAX_DELTA,
        "smooth_var": SMOOTH_VAR,
    }
    print(f"[config] {config}", flush=True)

    by_depth = {}
    for depth in config["depths"]:
        per_seed = {}
        for seed in config["seeds"]:
            if depth == 1:
                ret_A, bpc_base, bpc_after = run_depth_1(seed, config, device)
            else:
                ret_A, bpc_base, bpc_after = run_depth_n(depth, seed, config, device)
            per_seed[str(seed)] = {
                "retA": ret_A, "bpc_baseline": bpc_base, "bpc_after": bpc_after}
            print(f"  depth={depth} seed={seed}: retA={ret_A:.3f} "
                  f"bpc_base={bpc_base:.4f} bpc_after={bpc_after:.4f}", flush=True)
        mean_retA = sum(v["retA"] for v in per_seed.values()) / len(per_seed)
        by_depth[str(depth)] = {"per_seed": per_seed, "mean_retA": mean_retA}
        print(f"  depth={depth} MEAN retA={mean_retA:.3f}", flush=True)

    summary = {"by_depth": by_depth}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        self_test_verdict()
        return

    name = os.environ.get(
        "HDLAB_EXP_NAME",
        "wave14_swr_cascade_depth_full_v1_smoke" if args.smoke
        else "wave14_swr_cascade_depth_full_v1")
    out_dir = get_output_dir(name)

    summary, verdict, msg, elapsed, config = run(smoke=args.smoke)

    if args.smoke:
        # Smoke gate: at least 3 depths ran without error
        n_depths = len(summary.get("by_depth", {}))
        oracle.assert_baseline_high("swr_cascade_n_depths", float(n_depths), 2.5)

    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "elapsed_s": elapsed, "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"[done] elapsed={elapsed:.1f}s verdict={verdict}", flush=True)


if __name__ == "__main__":
    main()
