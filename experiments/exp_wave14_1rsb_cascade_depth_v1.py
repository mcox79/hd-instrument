"""Pred-5 (1-RSB diagnostic): Cascade-depth sensitivity.

1-RSB prediction: retA vs depth shows discrete plateau cliff at a critical depth
(phase-transition-like: flat -> sharp drop -> flat). RS prediction: smooth near-
linear degradation with depth.

Method: run 2/3/4/5 stage chains at fixed per-stage load (same corpus bytes per
stage) using the M1 chunk-replay mechanism (which cleared smoke HARD_PASS at
retA=0.888 for 4 stages). Measure retention_A at each depth. Test if the profile
is discontinuous (>= 0.10 drop per depth step with flat plateaus) or smooth
(< 0.10 max variance across consecutive per-step deltas).

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS / HARD-FAIL bands pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands registered BEFORE running.

Pre-reg:
    HARD-PASS (1-RSB confirmed): depth profile shows discrete cliff: any
               two consecutive steps with |delta_retA| >= 0.15 AND at least
               one plateau (two steps where |delta_retA| < 0.05).
               -> Cascade-depth sensitivity is discontinuous; 1-RSB supported.
    HARD-FAIL (RS confirmed): smooth linear degradation: max |delta_retA|
               across consecutive depth steps < 0.08 AND variance of per-step
               deltas < 0.002. -> Cascade-depth continuous; 1-RSB NOT supported at this axis.
    MIDDLE: anything between.

Queue: overnight_queue (GPU) -- 5-stage chain is the longest run.
ETA: ~6-7 hours GPU (5 seeds x 5 depth configs).
Pre-reg file: preregs/2026-05-24_wave14_1rsb_cascade_depth_v1.md
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

# Load hierreplay v1 for infrastructure (chunk replay + base)
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)

base = m1.base
v1 = m1.v1
pa = m1.pa

# ---- design parameters (exp_dev autonomy) ----
N_FULL = 4096
N_SMOKE = 1024
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 200_000
BYTES_SMOKE = 5_000
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
CHUNK_FRACTION = 0.5
DEPTHS_TO_TEST = [2, 3, 4, 5]  # stages (chain depth)

# Pre-registered threshold bands
CLIFF_DELTA = 0.15   # discrete drop >= this = cliff evidence
PLATEAU_DELTA = 0.05  # consecutive delta <= this = plateau evidence
SMOOTH_MAX_DELTA = 0.08  # max consecutive delta for RS (smooth) verdict
SMOOTH_VAR = 0.002        # variance of per-step deltas for RS verdict


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def run_chain_depth(depth, seed, config, device):
    """Run a D-stage chain with M1 chunk replay; return retention_A after final stage."""
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    smoke = (config["mode"] == "smoke")

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    # Load corpora for each stage (up to 5 stages)
    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpora = [corpus_a]
    # Stages 2+: shuffled A, corpus C, corpus D, extra shuffle
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpora.append(corpus_b)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpora.append(corpus_c)
    corpus_d_full = v1.load_corpus_D(smoke=smoke)
    corpus_d = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full
    corpora.append(corpus_d)
    # Stage 5: another shuffle of b
    corpus_e = pa.shuffle_bytes(corpus_b, seed=seed + 5)
    corpora.append(corpus_e)

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    train_sets, test_sets = [], []
    for c in corpora[:depth]:
        tr, te = split80(c)
        tidx, ttgt = base.bytes_to_idx_tensors(tr, device)
        te_idx, te_tgt = base.bytes_to_idx_tensors(te, device)
        train_sets.append((tidx, ttgt))
        test_sets.append((te_idx, te_tgt))

    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    thin_pools = []   # thinned pool for each prior stage

    bpc_A_baseline = None
    W_final = None
    pool_final_v = pool_final_l = None
    pool_final_u = 0

    for stage_idx in range(depth):
        tr_idx, tr_tgt = train_sets[stage_idx]
        n_ep = phase_a_epochs if stage_idx == 0 else n_epochs

        # Build combined replay from all prior thinned pools
        if thin_pools:
            all_v = torch.cat([p[0][:p[2]] for p in thin_pools], dim=0)
            all_l = torch.cat([p[1][:p[2]] for p in thin_pools], dim=0)
            all_u = all_v.shape[0]
        else:
            all_v = all_l = None
            all_u = 0

        W_new, pool_v, pool_l, pool_u = base.train_w_with_replay(
            W, None, None, 0,
            byte_atoms, pos_atoms,
            tr_idx, tr_tgt,
            all_v, all_l, all_u,
            n_ep, batch_size, device)
        W = W_new

        # Record baseline bpc on stage A after training stage A
        if stage_idx == 0:
            bpc_A_baseline = base.evaluate_bpc(
                W, pool_v, pool_l, pool_u,
                byte_atoms, pos_atoms,
                test_sets[0][0], test_sets[0][1],
                batch_size, device)

        # Thin this stage's pool for future replay
        thin_v, thin_l, thin_u = m1.thin_pool_to_chunks(
            pool_v, pool_l, pool_u, chunk_fraction=CHUNK_FRACTION, device=device)
        thin_pools.append((thin_v, thin_l, thin_u))

        pool_final_v = pool_v
        pool_final_l = pool_l
        pool_final_u = pool_u

    # Measure retention_A after final stage
    bpc_A_after = base.evaluate_bpc(
        W, pool_final_v, pool_final_l, pool_final_u,
        byte_atoms, pos_atoms,
        test_sets[0][0], test_sets[0][1],
        batch_size, device)
    ret_A = min(bpc_A_baseline / max(bpc_A_after, 1e-6), 1.0) if bpc_A_baseline else 0.0
    return ret_A, bpc_A_baseline, bpc_A_after


def compute_verdict(summary):
    by_depth = summary.get("by_depth", {})
    if not by_depth:
        return ("CASCADE_DEPTH_INCONCLUSIVE", "Missing by_depth data.")
    depths = sorted(int(d) for d in by_depth.keys())
    if len(depths) < 3:
        return ("CASCADE_DEPTH_INCONCLUSIVE", f"Need >= 3 depths; got {depths}.")

    ret_A_by_depth = {d: by_depth[str(d)]["mean_retA"] for d in depths}
    # Consecutive step deltas
    step_deltas = []
    for i in range(1, len(depths)):
        d_prev, d_curr = depths[i - 1], depths[i]
        delta = ret_A_by_depth[d_prev] - ret_A_by_depth[d_curr]  # positive = drop
        step_deltas.append(delta)

    max_delta = max(step_deltas)
    min_delta = min(step_deltas)
    n_steps = len(step_deltas)
    var_delta = sum((d - sum(step_deltas) / n_steps) ** 2 for d in step_deltas) / max(n_steps, 1)

    # Count plateaus: consecutive steps where delta < PLATEAU_DELTA
    n_plateau = sum(1 for d in step_deltas if abs(d) < PLATEAU_DELTA)
    # Count cliffs: consecutive steps where delta >= CLIFF_DELTA
    n_cliff = sum(1 for d in step_deltas if d >= CLIFF_DELTA)

    depth_str = ", ".join(f"depth={d}:retA={ret_A_by_depth[d]:.3f}" for d in depths)
    delta_str = ", ".join(f"{d:.3f}" for d in step_deltas)

    if n_cliff >= 1 and n_plateau >= 1:
        return ("CASCADE_DEPTH_1RSB_CONFIRMED",
                f"Discrete cliff + plateau detected. max_delta={max_delta:.3f}>={CLIFF_DELTA} "
                f"n_cliffs={n_cliff} n_plateaus={n_plateau}. "
                f"Profile: {depth_str}. Deltas: {delta_str}. "
                f"1-RSB cascade-depth sensitivity SUPPORTED.")

    if max_delta < SMOOTH_MAX_DELTA and var_delta < SMOOTH_VAR:
        return ("CASCADE_DEPTH_RS_SMOOTH",
                f"Smooth monotone degradation. max_delta={max_delta:.3f}<{SMOOTH_MAX_DELTA} "
                f"var_delta={var_delta:.4f}<{SMOOTH_VAR}. "
                f"Profile: {depth_str}. Deltas: {delta_str}. "
                f"RS smooth-degradation SUPPORTED; 1-RSB cascade-depth NOT supported.")

    return ("CASCADE_DEPTH_MIDDLE",
            f"Intermediate profile. max_delta={max_delta:.3f} n_cliffs={n_cliff} "
            f"n_plateaus={n_plateau} var_delta={var_delta:.4f}. "
            f"Profile: {depth_str}. Deltas: {delta_str}.")


def self_test_verdict():
    def mk(depth_vals):
        """depth_vals: list of (depth, retA)."""
        by_d = {str(d): {"mean_retA": r} for d, r in depth_vals}
        return {"by_depth": by_d}

    # 1-RSB case: plateau at depths 2-3, cliff at 4, plateau at 5
    case1 = mk([(2, 0.94), (3, 0.93), (4, 0.74), (5, 0.73)])
    # RS smooth case: small even drops
    case2 = mk([(2, 0.94), (3, 0.91), (4, 0.88), (5, 0.85)])
    # Middle case: some variation but not clean cliff+plateau
    case3 = mk([(2, 0.94), (3, 0.88), (4, 0.74), (5, 0.70)])
    cases = [
        (case1, "CASCADE_DEPTH_1RSB_CONFIRMED"),
        (case2, "CASCADE_DEPTH_RS_SMOOTH"),
        (case3, "CASCADE_DEPTH_MIDDLE"),
        ({}, "CASCADE_DEPTH_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; summary={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run(smoke=False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    t0 = time.monotonic()
    print(f"[cascade-depth] device={device} smoke={smoke}", flush=True)
    self_test_verdict()

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "depths": [2, 3, 4] if smoke else DEPTHS_TO_TEST,
        "chunk_fraction": CHUNK_FRACTION,
        "cliff_delta": CLIFF_DELTA,
        "smooth_max_delta": SMOOTH_MAX_DELTA,
    }
    print(f"[config] {config}", flush=True)

    by_depth = {}
    for depth in config["depths"]:
        per_seed = {}
        for seed in config["seeds"]:
            ret_A, bpc_base, bpc_after = run_chain_depth(depth, seed, config, device)
            per_seed[str(seed)] = {"retA": ret_A, "bpc_baseline": bpc_base, "bpc_after": bpc_after}
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
        print("self-test passed", flush=True)
        return

    out_dir = get_output_dir("wave14_1rsb_cascade_depth_v1")
    summary, verdict, msg, elapsed, config = run(smoke=args.smoke)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2))
    import shutil; shutil.move(str(tmp), str(out_dir / "metrics.json"))
    oracle.assert_baseline_high("cascade_depth_n_depths", float(len(summary.get("by_depth", {}))), 1.0)
    print(f"[done] elapsed={elapsed:.1f}s verdict={verdict}", flush=True)


if __name__ == "__main__":
    main()
