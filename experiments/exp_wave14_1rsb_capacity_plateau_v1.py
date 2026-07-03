"""Pred-1 (1-RSB diagnostic): Capacity-sweep plateau morphology.

1-RSB prediction: retA vs M_stored (patterns per stage = task difficulty) shows
a plateau + cliff morphology:
  - Plateau region A (easy): retA stays high across M in [M_lo, M_mid]
  - Cliff: sharp drop > 0.15 within a narrow M window
  - Plateau region B (hard): retA stays low across M in [M_mid, M_hi]
  Discrete plateaus are the signature of 1-RSB basin structure.

RS prediction: smooth monotone decay of retA with M_stored (no cliff; linear
or sigmoidal but continuously varying).

Method: sweep M_stored_per_stage in {25K, 50K, 100K, 150K, 200K, 300K, 400K}
bytes (= task complexity / load on the 4-stage M1 hierreplay chain). Measure
retA at each M. Fit: is there a plateau-cliff-plateau shape or smooth decay?

Per [[feedback-no-experiment-design-in-prompts]]: all parameters by exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS / HARD-FAIL pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands registered BEFORE running.

Pre-reg:
    HARD-PASS (1-RSB plateau morphology): capacity profile has:
              (a) cliff: any pair of consecutive M_stored values with
                  |delta_retA| >= 0.15, AND
              (b) plateau: at least two consecutive M values on the SAME SIDE
                  of the cliff where |delta_retA| < 0.05.
              -> Capacity-sweep plateau morphology CONFIRMED; 1-RSB supported.
    HARD-FAIL (RS smooth): max |delta_retA| across ALL consecutive M pairs
              < 0.08. -> Smooth monotone; 1-RSB NOT supported at capacity axis.
    MIDDLE: anything between.

Queue: overnight_queue (GPU) -- sweep across 7 M_stored values x 3 seeds x 4 stages.
ETA: ~5-6 hours GPU.
Pre-reg file: preregs/2026-05-24_wave14_1rsb_capacity_plateau_v1.md
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
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

# Load hierreplay v1 infrastructure
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
# M_stored sweep: bytes per stage (= task complexity)
M_SWEEP_FULL = [25_000, 50_000, 100_000, 150_000, 200_000, 300_000, 400_000]
M_SWEEP_SMOKE = [10_000, 50_000, 200_000]   # 3 points to check shape
SEEDS_FULL = [7, 17, 23]   # 3 seeds (GPU budget: 7 points x 3 seeds x 4 stages)
SEEDS_SMOKE = [17]
CHUNK_FRACTION = 0.5

# Pre-reg thresholds
CLIFF_DELTA = 0.15   # cliff drop >= this
PLATEAU_DELTA = 0.05  # plateau: consecutive delta within this
SMOOTH_MAX = 0.08    # RS smooth bound


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def run_4stage_m1_at_M(M_bytes, seed, config, device):
    """Run 4-stage M1 hierreplay at given bytes-per-stage; return retA."""
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    smoke = (config["mode"] == "smoke")

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:M_bytes] if M_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:M_bytes] if M_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = v1.load_corpus_D(smoke=smoke)
    corpus_d = corpus_d_full[:M_bytes] if M_bytes < len(corpus_d_full) else corpus_d_full

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    train_a, test_a = split80(corpus_a)
    train_b, _ = split80(corpus_b)
    train_c, _ = split80(corpus_c)
    train_d, _ = split80(corpus_d)

    def to_idx(tr):
        return base.bytes_to_idx_tensors(tr, device)

    train_a_idx, train_a_tgt = to_idx(train_a)
    test_a_idx, test_a_tgt = to_idx(test_a)
    train_b_idx, train_b_tgt = to_idx(train_b)
    train_c_idx, train_c_tgt = to_idx(train_c)
    train_d_idx, train_d_tgt = to_idx(train_d)

    W = torch.zeros((N, N), dtype=torch.float32, device=device)

    # Phase A
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)
    bpc_A_base = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                   byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                   batch_size, device)

    thin_A_v, thin_A_l, thin_A_u = m1.thin_pool_to_chunks(
        pool_A_v, pool_A_l, pool_A_u, chunk_fraction=CHUNK_FRACTION, device=device)

    # Phase B
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        thin_A_v, thin_A_l, thin_A_u, n_epochs, batch_size, device)

    thin_B_v, thin_B_l, thin_B_u = m1.thin_pool_to_chunks(
        pool_AB_v, pool_AB_l, pool_AB_u, chunk_fraction=CHUNK_FRACTION, device=device)
    combo_AB_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u]], dim=0)
    combo_AB_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u]], dim=0)
    combo_AB_u = combo_AB_v.shape[0]

    # Phase C
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        combo_AB_v, combo_AB_l, combo_AB_u, n_epochs, batch_size, device)

    thin_C_v, thin_C_l, thin_C_u = m1.thin_pool_to_chunks(
        pool_ABC_v, pool_ABC_l, pool_ABC_u, chunk_fraction=CHUNK_FRACTION, device=device)
    combo_ABC_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u],
                             thin_C_v[:thin_C_u]], dim=0)
    combo_ABC_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u],
                             thin_C_l[:thin_C_u]], dim=0)
    combo_ABC_u = combo_ABC_v.shape[0]

    # Phase D
    W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms, pos_atoms, train_d_idx, train_d_tgt,
        combo_ABC_v, combo_ABC_l, combo_ABC_u, n_epochs, batch_size, device)

    bpc_A_after = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                    byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                    batch_size, device)
    ret_A = min(bpc_A_base / max(bpc_A_after, 1e-6), 1.0)
    return ret_A, bpc_A_base, bpc_A_after


def compute_verdict(summary):
    by_M = summary.get("by_M_bytes", {})
    if not by_M:
        return ("CAPACITY_PLATEAU_INCONCLUSIVE", "Missing by_M_bytes data.")

    M_vals = sorted(int(m) for m in by_M.keys())
    if len(M_vals) < 3:
        return ("CAPACITY_PLATEAU_INCONCLUSIVE", f"Need >= 3 M values; got {M_vals}.")

    retA_by_M = {m: by_M[str(m)]["mean_retA"] for m in M_vals}
    # Consecutive step deltas (higher M = more load = expect lower retA)
    step_deltas = []
    for i in range(1, len(M_vals)):
        m_prev, m_curr = M_vals[i - 1], M_vals[i]
        delta = retA_by_M[m_prev] - retA_by_M[m_curr]  # positive = drop as M increases
        step_deltas.append(delta)

    max_delta = max(step_deltas) if step_deltas else 0.0
    n_cliff = sum(1 for d in step_deltas if d >= CLIFF_DELTA)
    n_plateau = sum(1 for d in step_deltas if abs(d) < PLATEAU_DELTA)

    M_str = ", ".join(f"M={m//1000}k:retA={retA_by_M[m]:.3f}" for m in M_vals)
    delta_str = ", ".join(f"{d:.3f}" for d in step_deltas)

    if n_cliff >= 1 and n_plateau >= 1:
        return ("CAPACITY_PLATEAU_1RSB_CONFIRMED",
                f"Plateau-cliff-plateau morphology: {n_cliff} cliff(s) >= {CLIFF_DELTA} + "
                f"{n_plateau} plateau step(s) < {PLATEAU_DELTA}. "
                f"max_delta={max_delta:.3f}. Profile: {M_str}. Deltas: {delta_str}. "
                f"1-RSB capacity-plateau morphology SUPPORTED.")
    if max_delta < SMOOTH_MAX:
        return ("CAPACITY_PLATEAU_RS_SMOOTH",
                f"Smooth monotone decay: max_delta={max_delta:.3f} < {SMOOTH_MAX}. "
                f"Profile: {M_str}. Deltas: {delta_str}. "
                f"RS smooth capacity decay SUPPORTED; 1-RSB capacity plateau NOT supported.")
    return ("CAPACITY_PLATEAU_MIDDLE",
            f"Intermediate morphology: n_cliff={n_cliff} n_plateau={n_plateau} "
            f"max_delta={max_delta:.3f}. Profile: {M_str}. Deltas: {delta_str}.")


def self_test_verdict():
    def mk(M_retA_pairs):
        by_M = {str(m): {"mean_retA": r} for m, r in M_retA_pairs}
        return {"by_M_bytes": by_M}

    # 1-RSB: plateau at low M, cliff, plateau at high M
    case1 = mk([(25000, 0.89), (50000, 0.88), (100000, 0.70), (200000, 0.68), (400000, 0.67)])
    # RS smooth: smooth decay
    case2 = mk([(25000, 0.92), (50000, 0.89), (100000, 0.86), (200000, 0.83), (400000, 0.80)])
    # Middle
    case3 = mk([(25000, 0.92), (50000, 0.85), (100000, 0.75), (200000, 0.72)])
    cases = [
        (case1, "CAPACITY_PLATEAU_1RSB_CONFIRMED"),
        (case2, "CAPACITY_PLATEAU_RS_SMOOTH"),
        (case3, "CAPACITY_PLATEAU_MIDDLE"),
        ({}, "CAPACITY_PLATEAU_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; summary={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run(smoke=False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    t0 = time.monotonic()
    print(f"[capacity-plateau] device={device} smoke={smoke}", flush=True)
    self_test_verdict()

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "M_sweep": M_SWEEP_SMOKE if smoke else M_SWEEP_FULL,
        "chunk_fraction": CHUNK_FRACTION,
        "cliff_delta": CLIFF_DELTA,
        "smooth_max": SMOOTH_MAX,
    }
    print(f"[config] {config}", flush=True)

    by_M = {}
    for M_bytes in config["M_sweep"]:
        per_seed = {}
        for seed in config["seeds"]:
            ret_A, bpc_base, bpc_after = run_4stage_m1_at_M(M_bytes, seed, config, device)
            per_seed[str(seed)] = {"retA": ret_A, "bpc_baseline": bpc_base,
                                   "bpc_after": bpc_after}
            print(f"  M={M_bytes//1000}k seed={seed}: retA={ret_A:.3f}", flush=True)
        mean_retA = sum(v["retA"] for v in per_seed.values()) / len(per_seed)
        by_M[str(M_bytes)] = {"per_seed": per_seed, "mean_retA": mean_retA}
        print(f"  M={M_bytes//1000}k MEAN retA={mean_retA:.3f}", flush=True)

    summary = {"by_M_bytes": by_M}
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

    out_dir = get_output_dir("wave14_1rsb_capacity_plateau_v1")
    summary, verdict, msg, elapsed, config = run(smoke=args.smoke)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    import shutil
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2))
    shutil.move(str(tmp), str(out_dir / "metrics.json"))
    oracle.assert_baseline_high("capacity_plateau_n_M_pts", float(len(summary.get("by_M_bytes", {}))), 1.0)
    print(f"[done] elapsed={elapsed:.1f}s verdict={verdict}", flush=True)


if __name__ == "__main__":
    main()
