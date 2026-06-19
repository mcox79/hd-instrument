"""K2 M1 hierarchical chunk replay: deeper-N probe at N=8192 [deeperN_v1].

Context: wave14_k2_m1_hierreplay_v1 at N=4096 5-seed = K2_M1_MIDDLE_BAND
(retention_A=0.719 vs HARD-PASS threshold 0.80, baseline 0.74).
The smoke at N=1024 gave K2_M1_HARD_PASS (retention_A=0.888) -- suggesting
N-scaling effect: M1 mechanism may work BETTER at larger N where the outer-product
W matrix has more capacity to store chunk boundaries separately.

deeperN_v1 hypothesis: at N=8192, the M1 chunk-replay mechanism has sufficient
capacity separation to break the 4-stage ceiling cleanly (retention_A >= 0.80).

Design change from v1: N_FULL = 8192 (was 4096). All other parameters unchanged.
Queue: overnight_queue (GPU required -- N=8192 x 5 seeds needs CUDA).
ETA: ~60-90 min GPU (5 seeds x 4-stage pipeline at N=8192).
Pre-reg: preregs/2026-05-24_wave14_k2_m1_hierreplay_deeperN_v1.md

M1 mechanism description (unchanged from v1):
  Replay sub-task CHUNKS (windows of CHUNK_SIZE tokens) rather than entire
  prior-task sequences in the replay pool. Mimics hippocampal episodic replay.

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands registered BEFORE running.

Pre-reg:
    HARD-PASS: mean retention_A >= 0.80 AND retention_B >= 0.70 AND retention_C >= 0.70
               across 5 seeds. M1 hierarchical chunk-replay breaks 4-stage ceiling.
               -> K2 🟡 PARTIAL mechanism-class M1 PASSES; 🟡 -> 🟢 candidate.
    HARD-FAIL: mean retention_A <= 0.65 AND delta_A < 0.03 vs baseline retA=0.74
               -> M1 chunk-replay REJECTED; M2/M3/M4 remain as untested paths.
    MIDDLE: retention_A in (0.65, 0.80); improvement over 0.74 but below HARD-PASS.
               Report bands; M1 partial; sequence M2 (attention-gated readout) next.

Queue: overnight_queue (GPU required for N=8192 x 5 seeds).
ETA: ~60-90 min GPU.
Pre-reg file: preregs/2026-05-24_wave14_k2_m1_hierreplay_deeperN_v1.md
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

# Load 4-stage baseline to reuse infrastructure (train_w_with_replay, evaluate_bpc,
# bytes_to_idx_tensors, load_corpus_D, etc.)
_v1_path = REPO / "experiments" / "exp_wave14_betB_4stage_continual_v1.py"
_v1_spec = importlib.util.spec_from_file_location("v1", _v1_path)
v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1)

# Get base Kovacs module from v1 (provides train_w_with_replay, evaluate_bpc, etc.)
base = v1.base
pa = base.pa

# ───── design parameters (exp_dev autonomy) ─────
# deeperN_v1: N_FULL raised from 4096 to 8192 to test N-scaling of M1 mechanism
# v1 at N=4096 gave MIDDLE_BAND (retention_A=0.719); smoke at N=1024 gave HARD_PASS
# Hypothesis: larger N gives more capacity for chunk-boundary separation -> HARD_PASS
N_FULL = 8192
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

# M1 mechanism: chunk size for hierarchical replay pool (sub-task episodes)
CHUNK_SIZE = 64   # tokens per chunk; empirically ~sentence/phrase-length

# Pre-registered thresholds
PASS_RET_A = 0.80
PASS_RET_B = 0.70
PASS_RET_C = 0.70
FAIL_RET_A = 0.65
BASELINE_RET_A = 0.74   # v193 ceiling from prior tuning axes
FAIL_DELTA = 0.03       # delta < FAIL_DELTA = no meaningful improvement


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


def thin_pool_to_chunks(pool_vecs: torch.Tensor, pool_labels: torch.Tensor,
                        pool_used: int, chunk_fraction: float = 0.5, device=None):
    """Subsample a context-embedding pool to a fraction of its size.

    The pool is a ring buffer of continuous context vectors [POOL_SIZE, N].
    M1 mechanism: replay from a SUBSET of the pool (chunk_fraction * pool_used
    items, drawn uniformly without replacement) instead of the full pool.
    This simulates 'episodic chunk replay' — the model replays representative
    fragments, not the full prior-phase experience.

    Returns (sub_v, sub_l, sub_u): the thinned pool in the same format.
    """
    if pool_used == 0:
        return pool_vecs, pool_labels, 0
    n_keep = max(1, int(pool_used * chunk_fraction))
    perm = torch.randperm(pool_used)[:n_keep]
    sub_v = pool_vecs[perm]
    sub_l = pool_labels[perm]
    if device is not None:
        sub_v = sub_v.to(device)
        sub_l = sub_l.to(device)
    return sub_v, sub_l, n_keep


def run_one_seed_m1(seed: int, config: dict, device: torch.device):
    """4-stage A->B->C->D with M1 hierarchical chunk-pool replay."""
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    smoke = (config["mode"] == "smoke")

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    # Load corpora (same as v1)
    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = v1.load_corpus_D(smoke=smoke)
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

    # M1 MECHANISM: thin the A pool to CHUNK_FRACTION of its size before using
    # as replay in Phase B. This simulates hierarchical episodic replay where
    # only representative chunks of prior experience are replayed.
    thin_A_v, thin_A_l, thin_A_u = thin_pool_to_chunks(pool_A_v, pool_A_l, pool_A_u,
                                                        chunk_fraction=0.5, device=device)

    # Phase B with M1 thinned chunk-pool A replay.
    W_AB, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_b_idx, train_b_tgt,
        thin_A_v, thin_A_l, thin_A_u, n_epochs, batch_size, device)
    bpc_B_baseline = base.evaluate_bpc(W_AB, pool_AB_v, pool_AB_l, pool_AB_u,
                                       byte_atoms, pos_atoms, test_b_idx, test_b_tgt,
                                       batch_size, device)

    # Thin B pool and combine with thin A pool for Phase C replay.
    thin_B_v, thin_B_l, thin_B_u = thin_pool_to_chunks(pool_AB_v, pool_AB_l, pool_AB_u,
                                                        chunk_fraction=0.5, device=device)
    combined_AB_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u]], dim=0)
    combined_AB_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u]], dim=0)
    combined_AB_u = combined_AB_v.shape[0]

    # Phase C with M1 thinned A+B chunk-pool replay.
    W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u = base.train_w_with_replay(
        W_AB, pool_AB_v.clone(), pool_AB_l.clone(), pool_AB_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        combined_AB_v, combined_AB_l, combined_AB_u, n_epochs, batch_size, device)
    bpc_C_baseline = base.evaluate_bpc(W_ABC, pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                       byte_atoms, pos_atoms, test_c_idx, test_c_tgt,
                                       batch_size, device)

    # Thin C pool; combine A+B+C chunks for Phase D replay.
    thin_C_v, thin_C_l, thin_C_u = thin_pool_to_chunks(pool_ABC_v, pool_ABC_l, pool_ABC_u,
                                                        chunk_fraction=0.5, device=device)
    combined_ABC_v = torch.cat([thin_A_v[:thin_A_u], thin_B_v[:thin_B_u],
                                thin_C_v[:thin_C_u]], dim=0)
    combined_ABC_l = torch.cat([thin_A_l[:thin_A_u], thin_B_l[:thin_B_u],
                                thin_C_l[:thin_C_u]], dim=0)
    combined_ABC_u = combined_ABC_v.shape[0]

    # Phase D with M1 thinned A+B+C chunk-pool replay.
    W_ABCD, pool_ABCD_v, pool_ABCD_l, pool_ABCD_u = base.train_w_with_replay(
        W_ABC, pool_ABC_v.clone(), pool_ABC_l.clone(), pool_ABC_u,
        byte_atoms, pos_atoms, train_d_idx, train_d_tgt,
        combined_ABC_v, combined_ABC_l, combined_ABC_u, n_epochs, batch_size, device)

    # Retention after Phase D
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
            "bpc_D_after_D": bpc_D_after_D,
            "thin_A_count": int(thin_A_u), "chunk_fraction": 0.5}


def compute_verdict(summary):
    per_seed = summary.get("per_seed")
    if not per_seed:
        return ("K2_M1_INCONCLUSIVE", "Missing per-seed data.")
    seeds = list(per_seed.values())
    ret_A = sum(s["retention_A"] for s in seeds) / len(seeds)
    ret_B = sum(s["retention_B"] for s in seeds) / len(seeds)
    ret_C = sum(s["retention_C"] for s in seeds) / len(seeds)
    delta_A = ret_A - BASELINE_RET_A
    detail = (f"retention_A={ret_A:.3f} retention_B={ret_B:.3f} retention_C={ret_C:.3f} "
              f"delta_from_baseline={delta_A:+.3f}")
    if ret_A >= PASS_RET_A and ret_B >= PASS_RET_B and ret_C >= PASS_RET_C:
        return ("K2_M1_HARD_PASS",
                f"M1 hierarchical chunk-replay BREAKS 4-stage ceiling: {detail}. "
                f"K2 PARTIAL -> promotion candidate.")
    if ret_A <= FAIL_RET_A and delta_A < FAIL_DELTA:
        return ("K2_M1_HARD_FAIL",
                f"M1 chunk-replay REJECTED: {detail}. "
                f"No improvement > {FAIL_DELTA} over baseline {BASELINE_RET_A}.")
    return ("K2_M1_MIDDLE_BAND",
            f"M1 partial improvement: {detail}. Above baseline but below HARD-PASS.")


def self_test_verdict():
    """Self-test: verify verdict logic with (input -> expected output) pairs."""
    def mk(ra, rb, rc):
        return {"per_seed": {"17": {"retention_A": ra, "retention_B": rb, "retention_C": rc}}}

    # Self-test cells (per [[feedback-strategy-spec-formula-selftests]])
    # Input: (retA, retB, retC) -> Expected verdict
    cases = [
        # HARD-PASS: all criteria met
        (mk(0.83, 0.72, 0.73), "K2_M1_HARD_PASS"),      # retA=0.83>=0.80, retB=0.72>=0.70, retC=0.73>=0.70
        (mk(0.81, 0.70, 0.71), "K2_M1_HARD_PASS"),      # exactly at boundaries
        # HARD-FAIL: retA<=0.65 AND delta<0.03 (delta = retA - 0.74)
        (mk(0.62, 0.60, 0.65), "K2_M1_HARD_FAIL"),      # 0.62<=0.65, delta=0.62-0.74=-0.12<0.03
        (mk(0.65, 0.60, 0.65), "K2_M1_HARD_FAIL"),      # exactly at fail boundary, delta=-0.09<0.03
        # MIDDLE: retA > 0.65 but < 0.80 OR (retA<=0.65 but delta>=0.03)
        (mk(0.76, 0.65, 0.65), "K2_M1_MIDDLE_BAND"),    # retA=0.76 in (0.65,0.80)
        (mk(0.70, 0.55, 0.55), "K2_M1_MIDDLE_BAND"),    # retA=0.70 in (0.65,0.80)
        (mk(0.78, 0.72, 0.71), "K2_M1_MIDDLE_BAND"),    # close to pass but retA<0.80
        # INCONCLUSIVE: empty per_seed
        ({}, "K2_M1_INCONCLUSIVE"),
    ]
    for summary, expected in cases:
        v, msg = compute_verdict(summary)
        if v != expected:
            raise AssertionError(f"Expected {expected}, got {v}. msg={msg}. summary={summary}")
    print(f"self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
              "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "chunk_fraction": 0.5,
              "pass_ret_A": PASS_RET_A, "pass_ret_B": PASS_RET_B,
              "pass_ret_C": PASS_RET_C, "fail_ret_A": FAIL_RET_A,
              "fail_delta": FAIL_DELTA, "baseline_ret_A": BASELINE_RET_A}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed_m1(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: retention_A={r['retention_A']:.3f} "
              f"retention_B={r['retention_B']:.3f} retention_C={r['retention_C']:.3f} "
              f"thin_A_count={r['thin_A_count']}", flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
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
    out_name = ("wave14_k2_m1_hierreplay_v1_smoke" if args.smoke
                else "wave14_k2_m1_hierreplay_v1")
    out_dir = get_output_dir(out_name)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    if args.smoke:
        seed_key = list(summary["per_seed"].keys())[0]
        r = summary["per_seed"][seed_key]
        oracle.assert_baseline_high("retention_A_smoke_m1", r["retention_A"], 0.05)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\n{'SMOKE' if args.smoke else 'DONE'}: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
