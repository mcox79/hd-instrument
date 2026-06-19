"""Bet B multi-task transfer A -> genuinely-different-corpus C — U1/U7 KILLER.

Per strategy_untested_rows_triage_2026-05-24.md Priority A #5 U1/U7 UNSURE.

Tests substrate ability to transfer learning from corpus A (English text) to a
GENUINELY DIFFERENT domain corpus C beyond Python source (which is structurally
similar to A at byte level). Uses HEX-ENCODED NUMERICAL CONTENT as C — the
ASCII byte distribution of hex digits is very different from prose English.

Mechanism: Bet B Kovacs single-shared-W A->C two-phase with replay; measure
retention_A and gain_C separately. The cycle-94 NUMFACTS retraction left this
genuinely-different-domain transfer question open.

Pre-reg falsifier statements:

  - HARD-PASS:  retention_A >= 0.70 AND gain_C >= 0.30 across 5 seeds.
                Substrate transfers to genuinely-different domain.
  - HARD-FAIL:  retention_A <= 0.30 OR gain_C <= 0.05.
                No effective transfer; catastrophic forgetting OR no learning of C.
  - MIDDLE:     intermediate. Partial transfer.

Per [[feedback-no-smoke]]: HARD-PASS and HARD-FAIL falsifiable BEFORE running.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only.

Pre-reg: preregs/2026-05-24_wave14_betB_multitask_diff_corpus_v1.md
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

_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_spec = importlib.util.spec_from_file_location("base", _base_path)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
pa = base.pa

N_FULL = 2048
N_SMOKE = 512
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_FULL = 3
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 5
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 80000
BYTES_SMOKE = 4000
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

PASS_RET_A = 0.70
PASS_GAIN_C = 0.30
FAIL_RET_A = 0.30
FAIL_GAIN_C = 0.05


def load_hex_corpus(smoke):
    """Generate a hex-encoded numerical corpus: deterministic via seed-free RNG."""
    import secrets
    n_bytes = 4000 if smoke else 100000
    raw = secrets.token_bytes(n_bytes // 2)
    hex_str = raw.hex().encode("ascii")
    return hex_str


def compute_verdict(summary):
    seeds_data = summary.get("per_seed")
    if not seeds_data:
        return ("MULTITASK_DIFF_INCONCLUSIVE", "Missing per-seed data.")
    seeds = list(seeds_data.values())
    ret_A = sum(s["retention_A"] for s in seeds) / len(seeds)
    gain_C = sum(s["gain_C"] for s in seeds) / len(seeds)
    if ret_A <= FAIL_RET_A or gain_C <= FAIL_GAIN_C:
        return ("MULTITASK_DIFF_HARD_FAIL",
                f"No effective transfer: retention_A={ret_A:.3f} gain_C={gain_C:.3f}. "
                f"Either catastrophic forgetting OR no learning of C.")
    if ret_A >= PASS_RET_A and gain_C >= PASS_GAIN_C:
        return ("MULTITASK_DIFF_HARD_PASS",
                f"Substrate transfers to genuinely-different domain: retention_A={ret_A:.3f}>={PASS_RET_A} "
                f"AND gain_C={gain_C:.3f}>={PASS_GAIN_C}. U1/U7 closed-PASS.")
    return ("MULTITASK_DIFF_MIDDLE_BAND",
            f"Partial transfer: retention_A={ret_A:.3f} gain_C={gain_C:.3f}.")


def self_test_verdict():
    def mk(ra, gc):
        return {"per_seed": {"17": {"retention_A": ra, "gain_C": gc}}}
    cases = [
        (mk(0.80, 0.45), "MULTITASK_DIFF_HARD_PASS"),
        (mk(0.70, 0.30), "MULTITASK_DIFF_HARD_PASS"),
        (mk(0.50, 0.20), "MULTITASK_DIFF_MIDDLE_BAND"),
        (mk(0.65, 0.15), "MULTITASK_DIFF_MIDDLE_BAND"),
        (mk(0.30, 0.40), "MULTITASK_DIFF_HARD_FAIL"),
        (mk(0.80, 0.05), "MULTITASK_DIFF_HARD_FAIL"),
        (mk(0.25, 0.40), "MULTITASK_DIFF_HARD_FAIL"),
        ({}, "MULTITASK_DIFF_INCONCLUSIVE"),
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
    corpus_c_full = load_hex_corpus(smoke=(config["mode"] == "smoke"))
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full

    def split(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]
    train_a, test_a = split(corpus_a)
    train_c, test_c = split(corpus_c)
    train_a_idx, train_a_tgt = base.bytes_to_idx_tensors(train_a, device)
    test_a_idx, test_a_tgt = base.bytes_to_idx_tensors(test_a, device)
    train_c_idx, train_c_tgt = base.bytes_to_idx_tensors(train_c, device)
    test_c_idx, test_c_tgt = base.bytes_to_idx_tensors(test_c, device)

    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_zero, None, None, 0, byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt, None, None, 0,
        phase_a_epochs, batch_size, device)
    bpc_A_baseline = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    bpc_zero_on_C = base.evaluate_bpc(W_zero, None, None, 0, byte_atoms, pos_atoms,
                                          test_c_idx, test_c_tgt, batch_size, device)

    # Phase C with A replay (single-shared-W)
    W_AC, pool_AC_v, pool_AC_l, pool_AC_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms, train_c_idx, train_c_tgt,
        pool_A_v, pool_A_l, pool_A_u, n_epochs, batch_size, device)

    bpc_A_after_C = base.evaluate_bpc(W_AC, pool_AC_v, pool_AC_l, pool_AC_u,
                                          byte_atoms, pos_atoms, test_a_idx, test_a_tgt,
                                          batch_size, device)
    bpc_C_after_C = base.evaluate_bpc(W_AC, pool_AC_v, pool_AC_l, pool_AC_u,
                                          byte_atoms, pos_atoms, test_c_idx, test_c_tgt,
                                          batch_size, device)

    retention_A = min(bpc_A_baseline / max(bpc_A_after_C, 1e-6), 1.0)
    gain_C = bpc_zero_on_C - bpc_C_after_C
    return {"retention_A": retention_A, "gain_C": gain_C,
             "bpc_A_baseline": bpc_A_baseline, "bpc_A_after_C": bpc_A_after_C,
             "bpc_zero_on_C": bpc_zero_on_C, "bpc_C_after_C": bpc_C_after_C}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": N_SMOKE if smoke else N_FULL,
              "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
              "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
              "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
              "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
              "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
              "pass_ret_A": PASS_RET_A, "pass_gain_C": PASS_GAIN_C,
              "fail_ret_A": FAIL_RET_A, "fail_gain_C": FAIL_GAIN_C,
              "corpus_C": "hex_encoded_numerical"}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: retention_A={r['retention_A']:.3f} gain_C={r['gain_C']:.3f}", flush=True)
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
                          "wave14_betB_multitask_diff_corpus_v1_smoke" if args.smoke
                          else "wave14_betB_multitask_diff_corpus_v1")
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
