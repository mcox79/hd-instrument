"""substrate_swr_v3_1_noisy_cue_replay_seed_19_v1_GPU.

SWR v3.1 (v3 mechanism + NOISY-CUE retrieval protocol per Director Option A
2026-06-30) single-seed chunk for SEED=19. Parent prereg:
  preregs/2026-06-30_substrate_swr_v3_1_noisy_cue_replay.md

Lineage:
  v3 (commit 48be1bd7)        honest-abort at smoke; clean-cue retrieval made
                              iterative cleanup vacuous; ALL arms 1.000 BC-ceiling
  v3.1 (this cell)            v3 mechanism + noisy-cue retrieval (sigma_query=0.5)
                              recall test injects noise on retrieval cue, so
                              NO_REPLAY ~0.34 (sanity-probed) and N_REPLAY arms
                              can lift toward DIRECT_UPPER as iterative cleanup
                              actually fires

CHUNKED single-seed-per-cell. This file = SEED 19. Sibling files exist for
seeds 7 and 13. Skunkworks aggregates the 3 per-seed metrics for chain-grade.

Bands (v3.1 retuned):
  HARD_PASS:   NO_REPLAY <= 0.40 AND R(N_REPLAY_20) - R(NO_REPLAY) >= 0.30
               AND monotonic AND not BC-ceiling
  MIDDLE_BAND: lift_20_vs_no in [0.10, 0.30)
  HARD_FAIL:   no lift / BC-ceiling / replay HURTS / arm-error / cardinality

META rules: AF + AH + AX + J + AC + AG + Q + AY (verdict auto-demote on distinctness=False).

PROT-018: no _n<N> suffix.
PROT-020: imports torch (GPU queue routing justified).

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

from experiments._substrate_swr_v3_1_noisy_cue_replay_core import (
    N_DIM, N_CORTEX, SEQ_LEN, SEQ_LEN_SMOKE,
    M_SMOKE, N_REPLAY_VALUES, N_REPLAY_VALUES_SMOKE,
    SIGMA_QUERY,
    EXPECTED_ARMS_PER_SEED, DEVICE,
    run_seed, compute_seed_verdict, selftest_core,
    write_crash_metrics, write_start_marker, write_final_metrics,
)


ANCHOR_NAME = "substrate_swr_v3_1_noisy_cue_replay_seed_19_v1_GPU"
SEED_THIS_CHUNK = 19
_HARDENING_MARKER = "v3_1_noisy_cue_seq_replay_seed_19"

M_FULL = 8192
SEQ_LEN_FULL = SEQ_LEN
N_REPLAY_VALUES_FULL = N_REPLAY_VALUES
SIGMA_QUERY_FULL = SIGMA_QUERY


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
    M_THIS = M_SMOKE
    SEQ_LEN_THIS = SEQ_LEN_SMOKE
    N_REPLAY_VALUES_THIS = N_REPLAY_VALUES_SMOKE
    SIGMA_QUERY_THIS = SIGMA_QUERY  # smoke uses same sigma as full (key discriminator)
else:
    M_THIS = M_FULL
    SEQ_LEN_THIS = SEQ_LEN_FULL
    N_REPLAY_VALUES_THIS = N_REPLAY_VALUES_FULL
    SIGMA_QUERY_THIS = SIGMA_QUERY_FULL


CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},SEED={SEED_THIS_CHUNK},M={M_THIS},seq_len={SEQ_LEN_THIS},"
    f"sigma_query={SIGMA_QUERY_THIS},N_DIM={N_DIM},N_CORTEX={N_CORTEX},"
    f"n_replay={N_REPLAY_VALUES_THIS},RUN_MODE={RUN_MODE},DEVICE={DEVICE.type},"
    f"hardening=METARULE_AF+AH+AX+J+AC+AG+Q+AY+NOISY_CUE+ARMS_5+CHUNKED_PER_SEED"
)


def _instrumentation_selftest() -> None:
    try:
        if not hasattr(torch, "sign"):
            raise AssertionError("torch.sign missing")
        if M_FULL <= N_CORTEX:
            raise AssertionError(f"FULL M_FULL={M_FULL} <= N_CORTEX={N_CORTEX}")
        if 0 not in N_REPLAY_VALUES_FULL:
            raise AssertionError("N_REPLAY=0 missing")
        if 1 not in N_REPLAY_VALUES_FULL or 20 not in N_REPLAY_VALUES_FULL:
            raise AssertionError("N_REPLAY 1 or 20 missing")
        if EXPECTED_ARMS_PER_SEED != 5:
            raise AssertionError(f"EXPECTED_ARMS_PER_SEED={EXPECTED_ARMS_PER_SEED}")
        if M_SMOKE < M_FULL // 2:
            raise AssertionError(
                f"smoke M={M_SMOKE} < FULL/2={M_FULL // 2}; SCALE rule"
            )
        if not (0.0 < SIGMA_QUERY < 3.0):
            raise AssertionError(f"SIGMA_QUERY={SIGMA_QUERY} out of plausible (0, 3)")
        # v3.1 KEY discriminator check: smoke must use SAME sigma_query as full
        # (the noisy-cue protocol IS the discriminator; smoke at sigma=0 = v3 BC trap)
        if abs(SIGMA_QUERY_FULL - SIGMA_QUERY) > 1e-6:
            raise AssertionError(
                "Smoke sigma_query MUST equal full sigma_query (the noisy-cue "
                "protocol IS the discriminator)"
            )
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
          f"sigma_query={SIGMA_QUERY_THIS}  n_replay={N_REPLAY_VALUES_THIS}  "
          f"arms={EXPECTED_ARMS_PER_SEED}  device={DEVICE.type}  mode={RUN_MODE}  "
          f"marker={_HARDENING_MARKER}", flush=True)


def _get_output_dir() -> Path:
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
              f"M={M_THIS} seq_len={SEQ_LEN_THIS} sigma_query={SIGMA_QUERY_THIS} "
              f"n_replay={N_REPLAY_VALUES_THIS}", flush=True)
        seed_result = run_seed(
            seed=SEED_THIS_CHUNK,
            M=M_THIS,
            seq_len=SEQ_LEN_THIS,
            n_replay_values=N_REPLAY_VALUES_THIS,
            sigma_query=SIGMA_QUERY_THIS,
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
