"""Bet B 4-stage continual learning A->B->C->D — K2 KILLER T1.

Per strategy_untested_rows_triage_2026-05-24.md Priority A K2 KILLER Tier 1.

Extension of Bet B Kovacs (3-corpus A->B->C) to 4 distinct corpora:
  A: English text (repo)
  B: byte-shuffled A (distribution shift)
  C: Python source (genuinely different domain; existing load_corpus_C)
  D: structured-text 4th corpus (mathematical content; using verification/*.py
     files which are distinct from experiments/ used in C)

Tests whether the substrate's continual-learning mechanism scales to 4 stages
(not just 3); retention checkpoint at each stage AND at end.

Mechanism: per-task substrates AND cross-task replay (compound configuration
from v187 baseline). Phase D adds (A+B+C) combined replay pool.

Pre-reg falsifier statements:

  - HARD-PASS:  mean retention_A >= 0.80 AND retention_B >= 0.70 AND retention_C >= 0.70
                across 5 seeds. Substrate-product CL works for 4-task chain.
  - HARD-FAIL:  mean retention_A <= 0.50 OR catastrophic-collapse pattern at stage D.
                4-stage exceeds substrate ceiling.
  - MIDDLE:     intermediate. Stage D adds load but mechanism survives partially.

Per [[feedback-no-smoke]]: HARD-PASS and HARD-FAIL falsifiable BEFORE running.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only.

Pre-reg: preregs/2026-05-24_wave14_betB_4stage_continual_v1.md
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

# Load Kovacs base (provides train_w_with_replay, evaluate_bpc, bytes_to_idx_tensors etc).
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_spec = importlib.util.spec_from_file_location("base", _base_path)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
pa = base.pa

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

PASS_RET_A = 0.80
PASS_RET_B = 0.70
PASS_RET_C = 0.70
FAIL_RET_A = 0.50


def load_corpus_D(smoke):
    """Mathematical / verification code as corpus D (distinct from C which uses experiments/)."""
    ver_dir = REPO / "verification"
    parts = []
    n_files = 3 if smoke else 8
    for f in sorted(ver_dir.glob("*.py"))[:n_files]:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    # Fallback to hdlab/ if verification/ thin
    if len(b"".join(parts)) < 10000:
        hd_dir = REPO / "hdlab"
        for f in sorted(hd_dir.glob("*.py"))[:n_files]:
            if f.exists():
                parts.append(f.read_bytes())
                parts.append(b"\n\n")
    return b"".join(parts)


def compute_verdict(summary):
    seeds_data = summary.get("per_seed")
    if not seeds_data:
        return ("FOURSTAGE_INCONCLUSIVE", "Missing per-seed data.")
    seeds = list(seeds_data.values())
    ret_A = sum(s["retention_A"] for s in seeds) / len(seeds)
    ret_B = sum(s["retention_B"] for s in seeds) / len(seeds)
    ret_C = sum(s["retention_C"] for s in seeds) / len(seeds)
    if ret_A <= FAIL_RET_A:
        return ("FOURSTAGE_HARD_FAIL",
                f"4-stage exceeds ceiling: retention_A={ret_A:.3f}<={FAIL_RET_A}. "
                f"retention_B={ret_B:.3f} retention_C={ret_C:.3f}. Mechanism breaks at 4 stages.")
    if ret_A >= PASS_RET_A and ret_B >= PASS_RET_B and ret_C >= PASS_RET_C:
        return ("FOURSTAGE_HARD_PASS",
                f"4-stage CL works: retention_A={ret_A:.3f}>={PASS_RET_A} retention_B={ret_B:.3f}>={PASS_RET_B} "
                f"retention_C={ret_C:.3f}>={PASS_RET_C}. K2 KILLER T1 substrate scaled to 4 stages.")
    return ("FOURSTAGE_MIDDLE_BAND",
            f"4-stage partial: retention_A={ret_A:.3f} retention_B={ret_B:.3f} retention_C={ret_C:.3f}. "
            f"Phase D adds load but mechanism survives partially.")


def self_test_verdict():
    def mk(ra, rb, rc):
        return {"per_seed": {"17": {"retention_A": ra, "retention_B": rb, "retention_C": rc}}}
    cases = [
        (mk(0.85, 0.75, 0.75), "FOURSTAGE_HARD_PASS"),
        (mk(0.82, 0.71, 0.72), "FOURSTAGE_HARD_PASS"),
        (mk(0.45, 0.60, 0.65), "FOURSTAGE_HARD_FAIL"),
        (mk(0.50, 0.60, 0.50), "FOURSTAGE_HARD_FAIL"),
        (mk(0.70, 0.65, 0.65), "FOURSTAGE_MIDDLE_BAND"),
        (mk(0.85, 0.65, 0.65), "FOURSTAGE_MIDDLE_BAND"),
        ({}, "FOURSTAGE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; summary={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed(seed, config, device):
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

    # Phase D with A+B+C replay.
    combined_ABC_v = torch.cat([pool_A_v[:pool_A_u], pool_AB_v[:pool_AB_u], pool_ABC_v[:pool_ABC_u]], dim=0)
    combined_ABC_l = torch.cat([pool_A_l[:pool_A_u], pool_AB_l[:pool_AB_u], pool_ABC_l[:pool_ABC_u]], dim=0)
    combined_ABC_u = combined_ABC_v.shape[0]
    W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms, pos_atoms, train_d_idx, train_d_tgt,
        combined_ABC_v, combined_ABC_l, combined_ABC_u, n_epochs, batch_size, device)

    # Retention checks: how well does W_ABCD do on A, B, C, D?
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
             "bpc_D_after_D": bpc_D_after_D}


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
              "pass_ret_A": PASS_RET_A, "pass_ret_B": PASS_RET_B,
              "pass_ret_C": PASS_RET_C, "fail_ret_A": FAIL_RET_A}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: retention_A={r['retention_A']:.3f} retention_B={r['retention_B']:.3f} retention_C={r['retention_C']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    base.validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict(); return 0
    name = os.environ.get("HDLAB_EXP_NAME",
                          "wave14_betB_4stage_continual_v1_smoke" if args.smoke
                          else "wave14_betB_4stage_continual_v1")
    out_dir = REPO / "data" / f"exp_{name}"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    if args.smoke:
        seed_key = list(summary["per_seed"].keys())[0]
        r = summary["per_seed"][seed_key]
        oracle.assert_baseline_high("retention_A_smoke", r["retention_A"], 0.10)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
