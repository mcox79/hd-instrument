"""substrate_swr_v3_iterative_clean_replay_seed_13_v1_GPU.

SWR v3 (true biological SWR: iterative SEQUENCE replay; NOT parallel bundling)
single-seed chunk for SEED=13. Parent design spec:
  notes/director_SWR_v3_iterative_clean_replay_design_spec_2026-06-30.md

Lineage:
  v1 (bundled outer product)  HARD_FAIL@smoke (K^2 cross-terms; recall -> 0.001)
  v2 (parallel multipass)     HARD_PASS@full but suspected MM_BC_CEILING per
                              Skunkworks landed-VET (all N_REPLAY arms = 0.985)
  v3 (this cell)              iterative SEQUENCE replay at M = 4096 / 8192 / 16384
                              regime (well above v2's 2048 ceiling) to expose
                              n_replay benefit not visible at v2's small-M trap

Architecture:
  CHUNKED single-seed-per-cell (per
  feedback_runner_zombie_ssh_disconnect_root_cause_FIXED_2026-06-28.md).
  This file = SEED 13. Sibling files exist for seeds 7 and 19. Skunkworks
  aggregates the 3 single-seed metrics for chain-grade verdict.

  Shared mechanism lives in experiments/_substrate_swr_v3_iterative_clean_replay_core.py
  (~600 LoC). This wrapper is ~150 LoC: argparse, RUN_MODE detection,
  output_dir, scaffolding, and the per-seed main() driver.

Mechanism summary (full detail in core module):
  - Build (k, v) codebook of size M; choose seq_len-length sequence
  - Project keys/vals N_DIM -> N_CORTEX via fixed Gaussian
  - For each arm (NO_REPLAY / N_REPLAY in {1, 5, 20} / DIRECT_UPPER):
      * NO_REPLAY: single batched Hebbian write (no iterative refinement)
      * N_REPLAY=k: initial write + k iterative passes, each walking sequence
        sequentially with iterative_cleanup at every step on key AND value
      * DIRECT_UPPER: oracle ceiling (10x eta; clean signal; no cleanup)
  - Recall = fraction of sequence items where W @ k_clean's nearest neighbor
    in value codebook == correct sequence idx

Bands (per-seed):
  HARD_PASS:   recall(N_REPLAY=20) - recall(N_REPLAY=1) >= 0.20 AND monotonic
               AND not BC-ceiling (K=20 < DIRECT_UPPER - 0.03)
  MIDDLE_BAND: lift in [0.10, 0.20)
  HARD_FAIL:   no lift / drop / BC-ceiling / arm-error / cardinality breach

META rules enforced:
  AF: arms-must-differ SHA-256 (per-arm cortex state hash)
  AH: atomic tmp + os.replace metrics.json
  AX: per-n_replay mechanism_hash distinct (selftest + verdict)
  J:  no bare except; specific exception classes; failure_class field per arm
  AC: numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
  Q:  suspect-1.000 check (BC_CEILING gate catches it when both n_replay arms
      and DIRECT_UPPER are at ceiling)
  AG: smoke at M=4096 (= 1/2 of chain-grade M=8192) to verify
      discriminator-survives-scale near full-N

PROT-018: no _n<N> suffix (M is the swept axis, not vector dim).
PROT-020: imports torch (GPU queue routing justified for matmul + cleanup loop).

# KB_REFERENT: hdlab/iterative_attractor.py
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import os
import time
from pathlib import Path

import torch  # PROT-020 GPU-queue gate

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._substrate_swr_v3_iterative_clean_replay_core import (
    N_DIM, N_CORTEX, SEQ_LEN, SEQ_LEN_SMOKE,
    M_SMOKE, N_REPLAY_VALUES, N_REPLAY_VALUES_SMOKE,
    EXPECTED_ARMS_PER_SEED, DEVICE,
    run_seed, compute_seed_verdict, selftest_core,
    write_crash_metrics, write_start_marker, write_final_metrics,
)


ANCHOR_NAME = "substrate_swr_v3_iterative_clean_replay_seed_13_v1_GPU"
SEED_THIS_CHUNK = 13
_HARDENING_MARKER = "v3_iterative_seq_replay_seed_13"

# FULL config (this chunk runs at M=8192 = chain-grade scale per spec discriminator).
# Sibling seed 13/19 chunks share this M. M_VALUES_FULL = {4096, 8192, 16384} from
# the spec is implemented across THREE separate cells if Skunkworks decides chain-grade
# verdict needs sweep; this primary chunk targets the central discriminator-firing M.
M_FULL = 8192                          # MEASURED@spec target for HARD_PASS discriminator
SEQ_LEN_FULL = SEQ_LEN                 # 100 per spec
N_REPLAY_VALUES_FULL = N_REPLAY_VALUES # (0, 1, 5, 20)


_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")

RUN_MODE = (
    "smoke"
    if (_ARGS.smoke or _NAME_SAYS_SMOKE
        or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke")
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

if RUN_MODE == "smoke":
    M_THIS = M_SMOKE                  # 4096 per spec (near-full M; discriminator-fires gate)
    SEQ_LEN_THIS = SEQ_LEN_SMOKE      # 50 per spec
    N_REPLAY_VALUES_THIS = N_REPLAY_VALUES_SMOKE
else:
    M_THIS = M_FULL
    SEQ_LEN_THIS = SEQ_LEN_FULL
    N_REPLAY_VALUES_THIS = N_REPLAY_VALUES_FULL


CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},SEED={SEED_THIS_CHUNK},M={M_THIS},seq_len={SEQ_LEN_THIS},"
    f"N_DIM={N_DIM},N_CORTEX={N_CORTEX},n_replay={N_REPLAY_VALUES_THIS},"
    f"RUN_MODE={RUN_MODE},DEVICE={DEVICE.type},"
    f"hardening=METARULE_AF+AH+AX+J+AC+AG_Q+ARMS_5+CHUNKED_PER_SEED"
)


def _instrumentation_selftest() -> None:
    """Cell-level selftest: regime sanity + core selftest."""
    try:
        if not hasattr(torch, "sign"):
            raise AssertionError("torch.sign missing")
        # Regime sanity: M sweep includes capacity-stress (M/N_c > 1.0) at full.
        if M_FULL <= N_CORTEX:
            raise AssertionError(f"FULL M_FULL={M_FULL} <= N_CORTEX={N_CORTEX}; "
                                 f"capacity-stress regime invariant violated")
        # N_REPLAY_VALUES must include 0 (NO_REPLAY equivalent) and span 1->20
        if 0 not in N_REPLAY_VALUES_FULL:
            raise AssertionError("N_REPLAY=0 (NO_REPLAY) missing from full sweep")
        if 1 not in N_REPLAY_VALUES_FULL or 20 not in N_REPLAY_VALUES_FULL:
            raise AssertionError("N_REPLAY 1 or 20 missing from full sweep")
        # ARM count check
        if EXPECTED_ARMS_PER_SEED != 5:
            raise AssertionError(f"EXPECTED_ARMS_PER_SEED={EXPECTED_ARMS_PER_SEED}; "
                                 f"v3 spec is 5 arms (NO_REPLAY + 3 N_REPLAY + DIRECT)")
        # Smoke regime must be at near-full N (DISCRIMINATOR-MUST-SURVIVE-SCALE check):
        # smoke at M=4096 (= 1/2 full M=8192) -> close enough for discriminator preview
        if M_SMOKE < M_FULL // 2:
            raise AssertionError(
                f"smoke M={M_SMOKE} < FULL/2={M_FULL // 2}; DISCRIMINATOR-SURVIVES-SCALE rule"
            )
        # Core mechanism selftest (asserts mechanism RUNS + arms differ + sane recall)
        selftest_core()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)
    print(f"[selftest] PASS  SEED={SEED_THIS_CHUNK}  M={M_THIS}  seq_len={SEQ_LEN_THIS}  "
          f"n_replay={N_REPLAY_VALUES_THIS}  arms={EXPECTED_ARMS_PER_SEED}  "
          f"device={DEVICE.type}  mode={RUN_MODE}  marker={_HARDENING_MARKER}",
          flush=True)


def _get_output_dir() -> Path:
    """Output dir = data/exp_<HDLAB_EXP_NAME or ANCHOR_NAME>/."""
    name = os.environ.get("HDLAB_EXP_NAME") or ANCHOR_NAME
    return REPO / "data" / f"exp_{name}"


def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = _get_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_ARMS_PER_SEED)

    try:
        t_start = time.time()
        print(f"[start] {ANCHOR_NAME} run_mode={RUN_MODE} seed={SEED_THIS_CHUNK} "
              f"M={M_THIS} seq_len={SEQ_LEN_THIS} n_replay={N_REPLAY_VALUES_THIS}",
              flush=True)
        seed_result = run_seed(
            seed=SEED_THIS_CHUNK,
            M=M_THIS,
            seq_len=SEQ_LEN_THIS,
            n_replay_values=N_REPLAY_VALUES_THIS,
            out_dir=out_dir,
        )
        verdict, verdict_msg = compute_seed_verdict(seed_result)
        elapsed_s = time.time() - t_start
        print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
        print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

        metrics_path = write_final_metrics(
            out_dir, ANCHOR_NAME, seed_result, verdict, verdict_msg,
            elapsed_s, RUN_MODE, CONFIG_VERSION,
        )
        print(f"[metrics] written to {metrics_path}", flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        write_crash_metrics(out_dir, ANCHOR_NAME, exc, RUN_MODE)
        raise


if __name__ == "__main__":
    _main()
