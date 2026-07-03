"""Bet B 4-stage continual learning A->B->C->D -- v190 K2 rehab axis 3.

Per v190 K2 4-stage rehab promotion gate (cap_map):
  - v1 result + axes 1 & 2 saturated at retention_A ~ 0.74 (below HARD-PASS 0.80)
  - Axis 3 (the last remaining axis from the v189 3-axis rehab list):
    Phase-D-specific replay weighting -- heavier weight on stage A in Phase D
    replay buffer (oldest stage gets up-weighted to counter capacity-bound
    load accumulation).

Mechanism: during Phase D, the combined (A+B+C) replay pool is rebalanced so
that stage-A samples appear with k-times multiplicity (k=4 default). All other
machinery is identical to v1 base. Tests whether biasing replay toward the
EARLIEST stage at the LATEST phase closes the retention_A degradation seen
across v1/axis-1/axis-2 (uniform / N-scaled / consolidation-extended runs).

Pre-reg falsifier statements:
  - HARD-PASS:  mean retention_A >= 0.80 AND retention_B >= 0.70 AND retention_C >= 0.70
                across 5 seeds. K2 4-stage CL clears HARD-PASS via Phase-D A-weighted
                replay rehab; K2 KILLER T1 row promotes 🟡 -> 🟢 ✅ track.
  - HARD-FAIL:  mean retention_A <= 0.50 OR catastrophic-collapse at stage D.
                A-weighted replay actively hurts (oversample of A crowds out
                B/C info; K2 axis 3 closed-failed).
  - MIDDLE:     intermediate. Rehab axis adds partial benefit but does not
                close the retention_A gap (joins axes 1+2 as third saturation
                point; K2 intrinsic-ceiling pattern confirmed across all 3
                rehab axes; product-spec rescoping recommendation).

Per [[feedback-no-smoke]]: HARD-PASS and HARD-FAIL falsifiable BEFORE running.
Per [[feedback-envelope-expansion-fail-bands]]: envelope-expansion drill on
K2 row; both bands carry forward + MIDDLE-band rehab-fail outcome pre-specified.
Per [[feedback-rehabilitation-after-rejection]]: this is rehab axis 3 of the
v189 3-axis rehab list; v190 axes 1+2 closed-failed; axis 3 is the final
decision point on K2 ❌ PROVISIONAL vs product-spec rescoping.

Pre-reg: preregs/2026-05-24_wave14_betB_4stage_continual_v2_rehab_phaseD_a_weighted_v1.md
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

# Load v1 base for the helper plumbing (run_one_seed -> we override).
_v1_path = REPO / "experiments" / "exp_wave14_betB_4stage_continual_v1.py"
_spec = importlib.util.spec_from_file_location("v1base", _v1_path)
v1base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1base)

# Load the Kovacs base module v1base loads internally so we can build the
# Phase-D replay buffer ourselves.
base = v1base.base
pa = v1base.pa
load_corpus_D = v1base.load_corpus_D

N_FULL = 4096
N_SMOKE = 1024
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 200000
BYTES_SMOKE = 5000
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Up-weighting factor for stage-A samples in Phase D replay. k=4 means stage A
# appears 4x in the Phase-D replay buffer relative to B and C.
A_WEIGHT = 4


def run_one_seed_axis3(seed, config, device):
    """Same as v1 base.run_one_seed but the Phase-D replay buffer up-weights A."""
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=(config["mode"] == "smoke"))
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = load_corpus_D(smoke=(config["mode"] == "smoke"))
    corpus_d = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full

    def split(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]
    train_a, test_a = split(corpus_a)
    train_b, test_b = split(corpus_b)
    train_c, test_c = split(corpus_c)
    train_d, test_d = split(corpus_d)

    train_a_idx, train_a_tgt = base.bytes_to_idx_tensors(train_a, device)
    test_a_idx, test_a_tgt = base.bytes_to_idx_tensors(test_a, device)
    train_b_idx, train_b_tgt = base.bytes_to_idx_tensors(train_b, device)
    test_b_idx, test_b_tgt = base.bytes_to_idx_tensors(test_b, device)
    train_c_idx, train_c_tgt = base.bytes_to_idx_tensors(train_c, device)
    test_c_idx, test_c_tgt = base.bytes_to_idx_tensors(test_c, device)
    train_d_idx, train_d_tgt = base.bytes_to_idx_tensors(train_d, device)
    test_d_idx, test_d_tgt = base.bytes_to_idx_tensors(test_d, device)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)

    # Phase A: no replay.
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)
    bpc_A_baseline = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                       byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                       batch_size, device)

    # Phase B with A replay.
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        pool_A_v, pool_A_l, pool_A_u, n_epochs, batch_size, device)
    bpc_B_baseline = base.evaluate_bpc(W_AB, pool_AB_v, pool_AB_l, pool_AB_u,
                                       byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                       batch_size, device)

    # Phase C with A+B replay.
    combined_AB_v = torch.cat([pool_A_v[:pool_A_u], pool_AB_v[:pool_AB_u]], dim=0)
    combined_AB_l = torch.cat([pool_A_l[:pool_A_u], pool_AB_l[:pool_AB_u]], dim=0)
    combined_AB_u = combined_AB_v.shape[0]
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        combined_AB_v, combined_AB_l, combined_AB_u, n_epochs, batch_size, device)
    bpc_C_baseline = base.evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                       byte_atoms, pos_atoms, test_c_idx, test_c_tgt,
                                       batch_size, device)

    # Phase D with A-WEIGHTED replay: A gets A_WEIGHT copies, B and C 1x each.
    a_slice_v = pool_A_v[:pool_A_u]
    a_slice_l = pool_A_l[:pool_A_u]
    a_weighted_v = a_slice_v.repeat(A_WEIGHT, 1)
    a_weighted_l = a_slice_l.repeat(A_WEIGHT)
    combined_ABC_v = torch.cat([a_weighted_v, pool_AB_v[:pool_AB_u], pool_ABC_v[:pool_ABC_u]], dim=0)
    combined_ABC_l = torch.cat([a_weighted_l, pool_AB_l[:pool_AB_u], pool_ABC_l[:pool_ABC_u]], dim=0)
    combined_ABC_u = combined_ABC_v.shape[0]
    W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms, pos_atoms, train_d_idx, train_d_tgt,
        combined_ABC_v, combined_ABC_l, combined_ABC_u, n_epochs, batch_size, device)

    bpc_A_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                      byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                      batch_size, device)
    bpc_B_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                      byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                      batch_size, device)
    bpc_C_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                      byte_atoms, pos_atoms, test_c_idx, test_c_tgt,
                                      batch_size, device)
    bpc_D_after_D = base.evaluate_bpc(W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u,
                                      byte_atoms, pos_atoms, test_d_idx, test_d_tgt,
                                      batch_size, device)

    retention_A = min(bpc_A_baseline / max(bpc_A_after_D, 1e-6), 1.0)
    retention_B = min(bpc_B_baseline / max(bpc_B_after_D, 1e-6), 1.0)
    retention_C = min(bpc_C_baseline / max(bpc_C_after_D, 1e-6), 1.0)
    return {"retention_A": retention_A, "retention_B": retention_B, "retention_C": retention_C,
            "bpc_A_baseline": bpc_A_baseline, "bpc_A_after_D": bpc_A_after_D,
            "bpc_B_baseline": bpc_B_baseline, "bpc_B_after_D": bpc_B_after_D,
            "bpc_C_baseline": bpc_C_baseline, "bpc_C_after_D": bpc_C_after_D,
            "bpc_D_after_D": bpc_D_after_D, "a_weight": A_WEIGHT}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
              "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "pass_ret_A": v1base.PASS_RET_A, "pass_ret_B": v1base.PASS_RET_B,
              "pass_ret_C": v1base.PASS_RET_C, "fail_ret_A": v1base.FAIL_RET_A,
              "rehab_axis": f"Phase-D A-weighted replay (k={A_WEIGHT})"}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed_axis3(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: retention_A={r['retention_A']:.3f} "
              f"retention_B={r['retention_B']:.3f} retention_C={r['retention_C']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = v1base.compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        v1base.self_test_verdict(); return 0
    name = os.environ.get("HDLAB_EXP_NAME",
                          "wave14_betB_4stage_continual_v2_rehab_phaseD_a_weighted_v1_smoke" if args.smoke
                          else "wave14_betB_4stage_continual_v2_rehab_phaseD_a_weighted_v1")
    out_dir = _canonical_get_output_dir(name)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    if args.smoke:
        seed_key = list(summary["per_seed"].keys())[0]
        r = summary["per_seed"][seed_key]
        oracle.assert_baseline_high("retention_A_smoke", r["retention_A"], 0.10)
    v1base.write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
